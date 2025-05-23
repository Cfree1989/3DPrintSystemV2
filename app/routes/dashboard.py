# app/routes/dashboard.py
"""
Dashboard routes for staff authentication and job management.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from app.models.job import Job
from app.extensions import db

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
    """Main dashboard showing uploaded jobs."""
    try:
        # Get all jobs with UPLOADED status, ordered by most recent first
        uploaded_jobs = Job.query.filter_by(status='UPLOADED').order_by(Job.created_at.desc()).all()
        
        # Count jobs by status for dashboard stats
        total_uploaded = len(uploaded_jobs)
        total_pending = Job.query.filter_by(status='PENDING').count()
        total_ready = Job.query.filter_by(status='READYTOPRINT').count()
        total_printing = Job.query.filter_by(status='PRINTING').count()
        total_completed = Job.query.filter_by(status='COMPLETED').count()
        
        stats = {
            'uploaded': total_uploaded,
            'pending': total_pending,
            'ready': total_ready,
            'printing': total_printing,
            'completed': total_completed
        }
        
        return render_template('dashboard/index.html', 
                             title='Staff Dashboard',
                             jobs=uploaded_jobs,
                             stats=stats)
    except Exception as e:
        current_app.logger.error(f"Error loading dashboard: {str(e)}")
        flash('Error loading dashboard data.', 'error')
        return render_template('dashboard/index.html', 
                             title='Staff Dashboard',
                             jobs=[],
                             stats={})

@dashboard.route('/job/<job_id>')
@login_required
def job_detail(job_id):
    """View detailed information about a specific job."""
    job = Job.query.get_or_404(job_id)
    return render_template('dashboard/job_detail.html', 
                         title=f'Job {job_id[:8]}',
                         job=job)

# Placeholder for other dashboard routes like job_detail, job actions etc.

# print("Dashboard blueprint defined (functional).") # Debug 