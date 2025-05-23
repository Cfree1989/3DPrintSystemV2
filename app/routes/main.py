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
    # return render_template('main/confirm.html', title='Confirm Job')
    return f"Confirm Job Page with token: {token} - Main Blueprint - Functional"

# print("Main blueprint defined (functional) with updated /submit route.") # Debug 