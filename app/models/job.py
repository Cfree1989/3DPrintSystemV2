# app/models/job.py
from ..extensions import db # Assuming extensions.py defines db = SQLAlchemy()
from datetime import datetime
import uuid

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())) # uuid4 hex
    student_name = db.Column(db.String(100), nullable=False)
    student_email = db.Column(db.String(100), nullable=False)
    original_filename = db.Column(db.String(256), nullable=False) # Original name from student upload
    display_name = db.Column(db.String(256), nullable=False)      # Standardized name or slicer output name
    file_path = db.Column(db.String(512), nullable=False)         # Full network path to the authoritative file
    status = db.Column(db.String(50), default='UPLOADED', nullable=False) # Enum: UPLOADED, PENDING, REJECTED, READYTOPRINT, PRINTING, COMPLETED, PAIDPICKEDUP
    printer = db.Column(db.String(64), nullable=True)      # Selected printer type/method
    color = db.Column(db.String(32), nullable=True)
    material = db.Column(db.String(32), nullable=True)     # Entered by staff
    weight_g = db.Column(db.Float, nullable=True)          # Entered by staff
    time_min = db.Column(db.Integer, nullable=True)        # Entered by staff
    cost_usd = db.Column(db.Numeric(6, 2), nullable=True)  # Calculated
    student_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    student_confirmed_at = db.Column(db.DateTime, nullable=True)
    confirm_token = db.Column(db.String(128), nullable=True, unique=True)
    confirm_token_expires = db.Column(db.DateTime, nullable=True)
    reject_reasons = db.Column(db.JSON, nullable=True) # List of strings or structured reasons
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_updated_by = db.Column(db.String(50), nullable=True) # "student" or "staff"

    # Added from masterplan (missed in initial placeholder)
    discipline = db.Column(db.String(100), nullable=True) # From student submission form
    class_number = db.Column(db.String(50), nullable=True) # From student submission form
    scaled_correctly = db.Column(db.Boolean, nullable=True) # From student submission form
    acknowledged_minimum_charge = db.Column(db.Boolean, nullable=True) # From student submission form


    def __repr__(self):
        return f'<Job {self.id} - {self.student_name} - {self.status}>'

# print("Job model defined.") # Debug
# pass 