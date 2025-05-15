# app/routes/dashboard.py
from flask import Blueprint, render_template #, session, redirect, url_for, flash
# from ..utils.decorators import login_required # Assuming a decorator for staff login

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
# @login_required
def index():
    # return render_template('dashboard/index.html', title='Staff Dashboard')
    return "Staff Dashboard - Dashboard Blueprint - Functional"

@dashboard.route('/login', methods=['GET', 'POST'])
def login():
    # form = LoginForm()
    # if form.validate_on_submit():
    #    # Check password, set session
    #    return redirect(url_for('.index'))
    # return render_template('dashboard/login.html', title='Staff Login', form=form)
    return "Staff Login Page - Dashboard Blueprint - Functional"

@dashboard.route('/logout')
def logout():
    # session.pop('staff_logged_in', None)
    # flash('You have been logged out.')
    # return redirect(url_for('main.index'))
    return "Staff Logout - Dashboard Blueprint - Functional"

# Placeholder for other dashboard routes like job_detail, job actions etc.

# print("Dashboard blueprint defined (functional).") # Debug 