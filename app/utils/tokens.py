# app/utils/tokens.py

from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from datetime import datetime, timedelta

def generate_confirmation_token(job_id: str, expires_hours: int = 168) -> tuple[str, datetime]:
    """
    Generate a secure confirmation token for a job.
    
    Args:
        job_id: The job ID to encode in the token
        expires_hours: Token expiration time in hours (default: 168 = 7 days)
    
    Returns:
        Tuple of (token_string, expiration_datetime)
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(job_id, salt='job-confirmation')
    
    # Calculate expiration datetime
    expiration = datetime.utcnow() + timedelta(hours=expires_hours)
    
    return token, expiration

def confirm_token(token: str, max_age_hours: int = 168) -> str:
    """
    Validate and decode a confirmation token.
    
    Args:
        token: The token string to validate
        max_age_hours: Maximum age in hours (default: 168 = 7 days)
    
    Returns:
        job_id if token is valid, None if invalid/expired
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        job_id = serializer.loads(
            token,
            salt='job-confirmation',
            max_age=max_age_hours * 3600  # Convert hours to seconds
        )
        return job_id
    except Exception:
        return None

def is_token_expired(token_expires: datetime) -> bool:
    """
    Check if a token has expired.
    
    Args:
        token_expires: DateTime when token expires
    
    Returns:
        True if expired, False if still valid
    """
    return datetime.utcnow() > token_expires if token_expires else True

# print("tokens.py loaded (placeholder).") # Debug
pass 