# app/services/email_service.py

# Placeholder for email sending logic
# (e.g., sending confirmation, rejection, completion emails)

from flask_mail import Message
from app.extensions import mail
from flask import current_app, render_template_string
import logging

logger = logging.getLogger(__name__)

def _is_email_configured():
    """Check if email is properly configured."""
    mail_server = current_app.config.get('MAIL_SERVER', '')
    mail_username = current_app.config.get('MAIL_USERNAME', '')
    mail_default_sender = current_app.config.get('MAIL_DEFAULT_SENDER', '')
    
    # Check if we have real configuration (not placeholder values)
    if (mail_server in ['smtp.example.com', ''] or 
        mail_default_sender in ['noreply@example.com', ''] or
        not mail_username):
        return False
    
    return True

def get_email_status():
    """Get current email configuration status for admin display."""
    if _is_email_configured():
        return {
            'configured': True,
            'server': current_app.config.get('MAIL_SERVER'),
            'sender': current_app.config.get('MAIL_DEFAULT_SENDER')
        }
    else:
        return {
            'configured': False,
            'message': 'Email not configured. Set MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD, and MAIL_DEFAULT_SENDER in environment variables.'
        }

def send_email(to, subject, html_content, text_content=None):
    """
    Send an email using Flask-Mail.
    
    Args:
        to: Recipient email address
        subject: Email subject
        html_content: HTML content for email
        text_content: Plain text content (optional)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Check if email is properly configured
    if not _is_email_configured():
        logger.warning(f"Email not configured - cannot send email to {to}: {subject}")
        return False
    
    try:
        msg = Message(
            subject=subject, 
            sender=current_app.config['MAIL_DEFAULT_SENDER'], 
            recipients=[to]
        )
        msg.html = html_content
        if text_content:
            msg.body = text_content
        else:
            # Simple text fallback by stripping HTML
            msg.body = html_content.replace('<br>', '\n').replace('<p>', '').replace('</p>', '\n')
        
        mail.send(msg)
        logger.info(f"Email sent successfully to {to}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {str(e)}")
        return False

def send_approval_email(job):
    """
    Send approval email to student requesting confirmation.
    
    Args:
        job: Job model instance
    
    Returns:
        bool: True if email sent successfully
    """
    subject = f"3D Print Job Approved - Confirmation Required (Job #{job.id[:8]})"
    
    html_content = f"""
    <h2>Your 3D Print Job Has Been Approved!</h2>
    
    <p>Dear {job.student_name},</p>
    
    <p>Great news! Your 3D print job has been reviewed and approved by our staff. Here are the details:</p>
    
    <h3>Job Details:</h3>
    <ul>
        <li><strong>Job ID:</strong> {job.id[:8]}</li>
        <li><strong>File:</strong> {job.display_name}</li>
        <li><strong>Printer:</strong> {job.printer}</li>
        <li><strong>Color:</strong> {job.color}</li>
        <li><strong>Material:</strong> {job.material}</li>
        <li><strong>Estimated Weight:</strong> {job.weight_g}g</li>
        <li><strong>Estimated Print Time:</strong> {job.time_min} minutes</li>
        <li><strong>Estimated Cost:</strong> ${job.cost_usd:.2f}</li>
    </ul>
    
    <h3>CONFIRMATION REQUIRED</h3>
    <p><strong>Your print will NOT proceed without your confirmation.</strong></p>
    
    <p>Please review the cost estimate and confirm your job by clicking the link below:</p>
    <p><a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/confirm/{job.confirm_token}" 
          style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">
          CONFIRM PRINT JOB
    </a></p>
    
    <p><strong>Important:</strong> This confirmation link will expire in 7 days. If you don't confirm by then, your job will be removed from the queue.</p>
    
    <p>Questions? Contact us in person at the makerspace.</p>
    
    <p>Best regards,<br>3D Print Service Team</p>
    """
    
    return send_email(job.student_email, subject, html_content)

def send_rejection_email(job, rejection_reasons):
    """
    Send rejection email to student with reasons.
    
    Args:
        job: Job model instance
        rejection_reasons: List of rejection reason strings
    
    Returns:
        bool: True if email sent successfully
    """
    subject = f"3D Print Job Update - Action Required (Job #{job.id[:8]})"
    
    reasons_html = ""
    if rejection_reasons:
        reasons_html = "<ul>"
        for reason in rejection_reasons:
            reasons_html += f"<li>{reason}</li>"
        reasons_html += "</ul>"
    
    html_content = f"""
    <h2>3D Print Job Update Required</h2>
    
    <p>Dear {job.student_name},</p>
    
    <p>We've reviewed your 3D print job submission and found some issues that need to be addressed before we can proceed with printing.</p>
    
    <h3>Job Details:</h3>
    <ul>
        <li><strong>Job ID:</strong> {job.id[:8]}</li>
        <li><strong>File:</strong> {job.display_name}</li>
        <li><strong>Submitted:</strong> {job.created_at.strftime('%B %d, %Y')}</li>
    </ul>
    
    <h3>Issues Found:</h3>
    {reasons_html}
    
    <h3>Next Steps:</h3>
    <p>Please address these issues and submit a new print job when ready. You can submit a new job using the same submission form.</p>
    
    <p>If you have questions about any of these issues or need help fixing your model, please visit us in person at the makerspace. Our staff are happy to help!</p>
    
    <p>Best regards,<br>3D Print Service Team</p>
    """
    
    return send_email(job.student_email, subject, html_content)

def send_completion_email(job):
    """
    Send completion email when job is ready for pickup.
    
    Args:
        job: Job model instance
    
    Returns:
        bool: True if email sent successfully
    """
    subject = f"3D Print Ready for Pickup! (Job #{job.id[:8]})"
    
    html_content = f"""
    <h2>Your 3D Print is Ready!</h2>
    
    <p>Dear {job.student_name},</p>
    
    <p>Great news! Your 3D print job has been completed and is ready for pickup.</p>
    
    <h3>Job Details:</h3>
    <ul>
        <li><strong>Job ID:</strong> {job.id[:8]}</li>
        <li><strong>File:</strong> {job.display_name}</li>
        <li><strong>Final Cost:</strong> ${job.cost_usd:.2f}</li>
    </ul>
    
    <h3>Pickup Information:</h3>
    <p><strong>Location:</strong> Makerspace - 3D Print Pickup Area<br>
    <strong>Hours:</strong> Monday-Friday, 8:00 AM - 5:00 PM</p>
    
    <p>Please bring your student ID and be prepared to pay the final cost of ${job.cost_usd:.2f}.</p>
    
    <p><strong>Important:</strong> Please pick up your print within 30 days. Items not collected will be recycled.</p>
    
    <p>We hope you're pleased with your print!</p>
    
    <p>Best regards,<br>3D Print Service Team</p>
    """
    
    return send_email(job.student_email, subject, html_content)

# print("email_service.py loaded (placeholder).") # Debug
pass 