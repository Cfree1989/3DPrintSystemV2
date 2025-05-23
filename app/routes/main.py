# app/routes/main.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from app.forms import SubmissionForm # Import the new form
from app.models.job import Job
from app.services.file_service import FileService
from app.extensions import db
import uuid

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # return render_template('main/index.html', title='Welcome')
    return "Hello, World! Main Blueprint - Functional - Index" # Updated for clarity

@main.route('/submit', methods=['GET', 'POST'])
def submit_form():
    form = SubmissionForm()
    if form.validate_on_submit():
        try:
            # Generate unique job ID
            job_id = str(uuid.uuid4())
            
            # Save uploaded file with standardized naming
            original_filename, display_name, file_path = FileService.save_uploaded_file(
                uploaded_file=form.file_upload.data,
                student_name=form.student_name.data,
                print_method=form.print_method.data,
                color=form.color_preference.data,
                job_id=job_id
            )
            
            # Create new job record
            new_job = Job(
                id=job_id,
                student_name=form.student_name.data,
                student_email=form.student_email.data,
                original_filename=original_filename,
                display_name=display_name,
                file_path=file_path,
                status='UPLOADED',
                printer=form.printer_selection.data,  # Use the new printer selection field
                color=form.color_preference.data,
                discipline=form.discipline.data,
                class_number=form.class_number.data,
                acknowledged_minimum_charge=(form.minimum_charge_consent.data == 'yes'),  # Convert dropdown to boolean
                last_updated_by='student'
            )
            
            # Save to database
            db.session.add(new_job)
            db.session.commit()
            
            # Success - redirect to success page with job ID
            flash(f'Job submitted successfully! Your Job ID is: {job_id[:8]}', 'success')
            return redirect(url_for('main.submit_success', job_id=job_id))
            
        except Exception as e:
            # Log error and show user-friendly message
            current_app.logger.error(f"Error processing job submission: {str(e)}")
            db.session.rollback()  # Rollback any partial database changes
            flash('An error occurred while processing your submission. Please try again.', 'error')
            return render_template('main/submit.html', title='Submit Job', form=form)
    
    # If GET request or form validation fails, render the form template.
    # Errors from form.validate_on_submit() will be automatically available in the template.
    return render_template('main/submit.html', title='Submit Job', form=form)

@main.route('/submit/success')
def submit_success():
    job_id = request.args.get('job_id')
    if not job_id:
        # If no job ID provided, redirect back to submit form
        flash('Invalid success page access.', 'error')
        return redirect(url_for('main.submit_form'))
    
    # Render the success template with job ID
    return render_template('main/success.html', title='Submission Successful', job_id=job_id)

@main.route('/confirm/<token>')
def confirm_job(token):
    """Display job confirmation page for students."""
    from app.utils.tokens import confirm_token
    from datetime import datetime
    
    # Validate the token and get job ID
    job_id = confirm_token(token)
    
    if not job_id:
        # Token is invalid or expired
        return render_template('main/confirm.html', title='Confirm Job', job=None, token=token)
    
    # Get the job from database
    job = Job.query.filter_by(id=job_id).first()
    
    if not job:
        # Job not found
        return render_template('main/confirm.html', title='Confirm Job', job=None, token=token)
    
    # Check if job is still in PENDING status
    if job.status != 'PENDING':
        # Job is no longer pending (already confirmed, rejected, etc.)
        flash(f'This job has already been processed. Current status: {job.status}', 'info')
        return render_template('main/confirm.html', title='Confirm Job', job=None, token=token)
    
    # Check if token matches the job's token (additional security)
    if job.confirm_token != token:
        return render_template('main/confirm.html', title='Confirm Job', job=None, token=token)
    
    # Check if token has expired (additional check)
    if job.confirm_token_expires and job.confirm_token_expires < datetime.utcnow():
        return render_template('main/confirm.html', title='Confirm Job', job=None, token=token)
    
    # Job is valid and pending - show confirmation page
    return render_template('main/confirm.html', title='Confirm Job', job=job, token=token)

@main.route('/confirm/<token>', methods=['POST'])
def confirm_job_post(token):
    """Process job confirmation from student."""
    from app.utils.tokens import confirm_token
    from app.services.file_service import FileService
    from datetime import datetime
    
    # Validate the token and get job ID
    job_id = confirm_token(token)
    
    if not job_id:
        flash('Invalid or expired confirmation link.', 'error')
        return redirect(url_for('main.index'))
    
    # Get the job from database
    job = Job.query.filter_by(id=job_id).first()
    
    if not job:
        flash('Job not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Verify job is in correct state for confirmation
    if job.status != 'PENDING':
        flash(f'This job cannot be confirmed. Current status: {job.status}', 'error')
        return redirect(url_for('main.index'))
    
    # Verify token matches and hasn't expired
    if job.confirm_token != token or (job.confirm_token_expires and job.confirm_token_expires < datetime.utcnow()):
        flash('Invalid or expired confirmation link.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Move file from Pending to ReadyToPrint
        new_file_path = FileService.move_file_between_status_dirs(
            current_path=job.file_path,
            from_status='PENDING',
            to_status='READYTOPRINT'
        )
        
        # Update job in database
        job.status = 'READYTOPRINT'
        job.student_confirmed = True
        job.student_confirmed_at = datetime.utcnow()
        job.file_path = new_file_path
        job.last_updated_by = 'student'
        # Keep the token for potential future reference, but it's no longer valid for confirmation
        
        db.session.commit()
        
        # Success message
        flash(f'Job confirmed successfully! Your print job (ID: {job.id[:8]}) is now in the queue.', 'success')
        current_app.logger.info(f"Job {job.id[:8]} confirmed by student {job.student_email}")
        
        # Render success page
        return render_template('main/confirm_success.html', title='Job Confirmed', job=job)
        
    except Exception as e:
        current_app.logger.error(f"Error confirming job {job.id[:8]}: {str(e)}")
        db.session.rollback()
        flash('An error occurred while confirming your job. Please contact us in person.', 'error')
        return redirect(url_for('main.confirm_job', token=token))

# print("Main blueprint defined (functional) with updated /submit route.") # Debug 