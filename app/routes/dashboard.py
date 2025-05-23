# app/routes/dashboard.py
"""
Dashboard routes for staff authentication and job management.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app, jsonify
from app.models.job import Job
from app.extensions import db
from app.services.cost_service import calculate_cost, get_printer_display_name
from app.services.email_service import send_approval_email, send_rejection_email
from app.services.file_service import FileService
from app.utils.tokens import generate_confirmation_token
from datetime import datetime

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def login_required(f):
    """Decorator to require staff login for dashboard routes."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('staff_logged_in'):
            return redirect(url_for('dashboard.login'))
        return f(*args, **kwargs)
    return decorated_function

@dashboard.route('/login', methods=['GET', 'POST'])
def login():
    """Staff login page with shared password authentication."""
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        staff_password = current_app.config.get('STAFF_PASSWORD', 'defaultstaffpassword')
        
        if password == staff_password:
            session['staff_logged_in'] = True
            session.permanent = True  # Remember login
            flash('Welcome to the staff dashboard!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid password. Please try again.', 'error')
    
    return render_template('dashboard/login.html', title='Staff Login')

@dashboard.route('/logout')
def logout():
    """Log out staff user."""
    session.pop('staff_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@dashboard.route('/')
@login_required
def index():
    """Main dashboard showing jobs by status."""
    status = request.args.get('status', 'UPLOADED').upper()
    valid_statuses = ['UPLOADED', 'PENDING', 'READYTOPRINT', 'PRINTING', 'COMPLETED', 'PAIDPICKEDUP', 'REJECTED']
    
    if status not in valid_statuses:
        status = 'UPLOADED'
    
    try:
        # Get jobs for the selected status
        jobs = Job.query.filter_by(status=status).order_by(Job.created_at.desc()).all()
        
        # Count jobs by status for dashboard stats
        stats = {
            'uploaded': Job.query.filter_by(status='UPLOADED').count(),
            'pending': Job.query.filter_by(status='PENDING').count(),
            'ready': Job.query.filter_by(status='READYTOPRINT').count(),
            'printing': Job.query.filter_by(status='PRINTING').count(),
            'completed': Job.query.filter_by(status='COMPLETED').count(),
            'paidpickedup': Job.query.filter_by(status='PAIDPICKEDUP').count(),
            'rejected': Job.query.filter_by(status='REJECTED').count()
        }
        
        return render_template('dashboard/index.html', 
                             title='Staff Dashboard',
                             jobs=jobs,
                             stats=stats,
                             current_status=status)
    except Exception as e:
        current_app.logger.error(f"Error loading dashboard: {str(e)}")
        flash('Error loading dashboard data.', 'error')
        return render_template('dashboard/index.html', 
                             title='Staff Dashboard',
                             jobs=[],
                             stats={},
                             current_status=status)

@dashboard.route('/api/jobs/<status>')
@login_required
def api_jobs_by_status(status):
    """API endpoint to get jobs by status (for AJAX tab switching)."""
    status = status.upper()
    valid_statuses = ['UPLOADED', 'PENDING', 'READYTOPRINT', 'PRINTING', 'COMPLETED', 'PAIDPICKEDUP', 'REJECTED']
    
    if status not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400
    
    try:
        jobs = Job.query.filter_by(status=status).order_by(Job.created_at.desc()).all()
        
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                'id': job.id,
                'display_name': job.display_name,
                'student_name': job.student_name,
                'student_email': job.student_email,
                'printer': job.printer,
                'color': job.color,
                'material': job.material or 'N/A',
                'status': job.status,
                'created_at': job.created_at.strftime('%m/%d/%Y at %I:%M %p'),
                'cost_usd': str(job.cost_usd) if job.cost_usd else 'N/A'
            })
        
        return jsonify({
            'status': 'success',
            'jobs': jobs_data,
            'count': len(jobs_data)
        })
    except Exception as e:
        current_app.logger.error(f"Error loading jobs for status {status}: {str(e)}")
        return jsonify({'error': 'Error loading jobs'}), 500

@dashboard.route('/job/<job_id>')
@login_required
def job_detail(job_id):
    """View detailed information about a specific job."""
    job = Job.query.get_or_404(job_id)
    return render_template('dashboard/job_detail.html', 
                         title=f'Job {job_id[:8]}',
                         job=job)

@dashboard.route('/job/<job_id>/approve', methods=['POST'])
@login_required
def approve_job(job_id):
    """Approve a job and move it to PENDING status."""
    try:
        job = Job.query.get_or_404(job_id)
        
        if job.status != 'UPLOADED':
            flash('Only uploaded jobs can be approved.', 'error')
            return redirect(url_for('dashboard.job_detail', job_id=job_id))
        
        # Get form data
        weight_g = float(request.form.get('weight_g', 0))
        time_hours_raw = float(request.form.get('time_hours', 0))
        material = request.form.get('material', '').strip()
        
        if weight_g <= 0 or time_hours_raw <= 0 or not material:
            flash('Please provide valid weight, time, and material.', 'error')
            return redirect(url_for('dashboard.job_detail', job_id=job_id))
        
        # Apply conservative time rounding (always round up to nearest 0.5 hours)
        from app.utils.helpers import round_time_conservative
        time_hours = round_time_conservative(time_hours_raw)
        
        # Calculate cost
        cost = calculate_cost(job.printer, weight_g, time_hours)
        
        # Generate confirmation token
        token, token_expires = generate_confirmation_token(job.id)
        
        # Update job record
        job.status = 'PENDING'
        job.weight_g = weight_g
        job.time_hours = time_hours
        job.material = material
        job.cost_usd = cost
        job.confirm_token = token
        job.confirm_token_expires = token_expires
        job.updated_at = datetime.utcnow()
        job.last_updated_by = 'staff'
        
        # Move file from Uploaded to Pending
        try:
            new_file_path = FileService.move_file(
                job.file_path, 'Uploaded', 'Pending', job.display_name
            )
            job.file_path = new_file_path
        except Exception as e:
            current_app.logger.error(f"Error moving file for job {job_id}: {str(e)}")
            flash('Error moving file. Please try again.', 'error')
            return redirect(url_for('dashboard.job_detail', job_id=job_id))
        
        # Save changes
        db.session.commit()
        
        # Send approval email
        email_sent = send_approval_email(job)
        if email_sent:
            flash(f'Job approved and confirmation email sent to {job.student_email}', 'success')
        else:
            flash('Job approved but email failed to send. Please contact student manually.', 'warning')
        
        return redirect(url_for('dashboard.index'))
        
    except ValueError as e:
        current_app.logger.error(f"Cost calculation error for job {job_id}: {str(e)}")
        flash('Error calculating cost. Please check printer selection.', 'error')
        return redirect(url_for('dashboard.job_detail', job_id=job_id))
    except Exception as e:
        current_app.logger.error(f"Error approving job {job_id}: {str(e)}")
        db.session.rollback()
        flash('Error approving job. Please try again.', 'error')
        return redirect(url_for('dashboard.job_detail', job_id=job_id))

@dashboard.route('/job/<job_id>/reject', methods=['POST'])
@login_required
def reject_job(job_id):
    """Reject a job and move it to REJECTED status."""
    try:
        job = Job.query.get_or_404(job_id)
        
        if job.status != 'UPLOADED':
            flash('Only uploaded jobs can be rejected.', 'error')
            return redirect(url_for('dashboard.job_detail', job_id=job_id))
        
        # Get rejection reasons
        rejection_reasons = request.form.getlist('rejection_reasons')
        custom_reason = request.form.get('custom_reason', '').strip()
        
        if custom_reason:
            rejection_reasons.append(custom_reason)
        
        if not rejection_reasons:
            flash('Please provide at least one rejection reason.', 'error')
            return redirect(url_for('dashboard.job_detail', job_id=job_id))
        
        # Update job record
        job.status = 'REJECTED'
        job.reject_reasons = rejection_reasons
        job.updated_at = datetime.utcnow()
        job.last_updated_by = 'staff'
        
        # Save changes
        db.session.commit()
        
        # Send rejection email
        email_sent = send_rejection_email(job, rejection_reasons)
        if email_sent:
            flash(f'Job rejected and notification email sent to {job.student_email}', 'success')
        else:
            flash('Job rejected but email failed to send. Please contact student manually.', 'warning')
        
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        current_app.logger.error(f"Error rejecting job {job_id}: {str(e)}")
        db.session.rollback()
        flash('Error rejecting job. Please try again.', 'error')
        return redirect(url_for('dashboard.job_detail', job_id=job_id))

# Placeholder for other dashboard routes like job_detail, job actions etc.

# print("Dashboard blueprint defined (functional).") # Debug 