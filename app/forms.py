from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, InputRequired, ValidationError

# Custom validator to ensure a selection is made for SelectFields with a default empty choice
def SelectRequired(message="Please make a selection."):
    def _validate(form, field):
        if not field.data: # Checks if the value is empty (like '')
            raise ValidationError(message)
    return _validate

class SubmissionForm(FlaskForm):
    student_name = StringField('Full Name', validators=[DataRequired()])
    student_email = StringField('Email Address', validators=[DataRequired(), Email()])
    
    discipline_choices = [
        ('', '-- Select Discipline --'),
        ('engineering', 'Engineering'),
        ('art_design', 'Art & Design'),
        ('architecture', 'Architecture'),
        ('hobby', 'Hobby/Personal'),
        ('other', 'Other')
    ]
    discipline = SelectField('Discipline/Major', choices=discipline_choices, validators=[SelectRequired(message="Please select a discipline.")])
    
    class_number = StringField('Class Number (e.g., ARCH-101, ME-203, or N/A)', validators=[DataRequired(message="Please enter a class number or N/A.")])
    
    print_method_choices = [
        ('', '-- Select Print Method --'),
        ('Filament', 'Filament (FDM/FFF)'),
        ('Resin', 'Resin (SLA/DLP)')
    ]
    print_method = SelectField('Print Method', choices=print_method_choices, validators=[SelectRequired(message="Please select a print method.")])
    
    color_preference_choices = [
        ('', '-- Select Color --'),
        ('black', 'Black'),
        ('white', 'White'),
        ('grey', 'Grey'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('clear_resin', 'Clear Resin (Resin only)'),
        ('grey_resin', 'Grey Resin (Resin only)'),
        ('other', 'Other (Staff will contact)') 
    ]
    color_preference = SelectField('Color Preference', choices=color_preference_choices, validators=[SelectRequired(message="Please select a color preference.")])
    
    model_scaled_correctly = RadioField(
        'Is your model scaled correctly for the printer?',
        choices=[('yes', 'Yes'), ('no', 'No'), ('unsure', 'Unsure')],
        default='unsure',
        validators=[DataRequired(message="Please answer the question about model scaling.")]
    )
    
    minimum_charge_consent = BooleanField(
        'I understand there is a minimum $3.00 charge for all print jobs, and that the final cost may be higher based on material and time.',
        validators=[InputRequired(message="You must acknowledge the minimum charge and potential cost.")]
    )
    
    allowed_extensions = ['stl', 'obj', '3mf']
    file_upload = FileField(
        'Upload 3D Model File (.stl, .obj, .3mf)', 
        validators=[
            FileRequired(message="Please select a file to upload."),
            FileAllowed(allowed_extensions, f"File type not allowed. Please upload one of: {', '.join(allowed_extensions)}.")
        ]
    )
    
    submit = SubmitField('Submit Print Job') 