# app/routes/main.py
from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # return render_template('main/index.html', title='Welcome')
    return "Hello, World! Main Blueprint - Functional"

@main.route('/submit')
def submit_form():
    # return render_template('main/submit.html', title='Submit Job')
    return "Submit Job Page - Main Blueprint - Functional"

@main.route('/submit/success')
def submit_success():
    # return render_template('main/success.html', title='Submission Successful')
    return "Submission Successful Page - Main Blueprint - Functional"

@main.route('/confirm/<token>')
def confirm_job(token):
    # return render_template('main/confirm.html', title='Confirm Job')
    return f"Confirm Job Page with token: {token} - Main Blueprint - Functional"

# print("Main blueprint defined (functional).") # Debug 