# app/routes/main.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.forms import SubmissionForm # Import the new form
# Potentially other imports later like db, Job model, file handling utils

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # return render_template('main/index.html', title='Welcome')
    return "Hello, World! Main Blueprint - Functional - Index" # Updated for clarity

@main.route('/submit', methods=['GET', 'POST'])
def submit_form():
    form = SubmissionForm()
    if form.validate_on_submit():
        # This is where file handling, db interaction, etc., will go in later sub-tasks.
        # For now, just flash a success message and redirect.
        # student_name = form.student_name.data
        # uploaded_file = form.file_upload.data
        # filename = uploaded_file.filename # Example: get filename
        
        flash(f'Form submitted successfully for {form.student_name.data}! (Placeholder - no data saved yet).', 'success')
        return redirect(url_for('main.submit_success')) # Redirect to a success page
    
    # If GET request or form validation fails, render the form template.
    # Errors from form.validate_on_submit() will be automatically available in the template.
    return render_template('main/submit.html', title='Submit Job', form=form)

@main.route('/submit/success')
def submit_success():
    # return render_template('main/success.html', title='Submission Successful')
    # For now, a simple message. A proper success page will be built later.
    return "Submission Successful Page - Main Blueprint - Thank you for your submission! (Placeholder)"

@main.route('/confirm/<token>')
def confirm_job(token):
    # return render_template('main/confirm.html', title='Confirm Job')
    return f"Confirm Job Page with token: {token} - Main Blueprint - Functional"

# print("Main blueprint defined (functional) with updated /submit route.") # Debug 