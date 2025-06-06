from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, InputRequired, ValidationError, Length

# Custom validator to ensure a selection is made for SelectFields with a default empty choice
def SelectRequired(message="Please make a selection."):
    def _validate(form, field):
        if not field.data: # Checks if the value is empty (like '')
            raise ValidationError(message)
    return _validate

# Custom validator for file size limit
def FileSizeLimit(max_size_mb=50, message=None):
    """
    Validates that uploaded file doesn't exceed size limit.
    max_size_mb: Maximum file size in megabytes
    """
    if not message:
        message = f"File size cannot exceed {max_size_mb}MB."
    
    def _validate(form, field):
        if field.data:
            # Get file size by seeking to end and back
            field.data.seek(0, 2)  # Seek to end
            file_size = field.data.tell()  # Get position (file size)
            field.data.seek(0)  # Reset to beginning
            
            max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
            if file_size > max_size_bytes:
                raise ValidationError(message)
    return _validate

class SubmissionForm(FlaskForm):
    student_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100, message="Name must be between 2 and 100 characters.")])
    student_email = StringField('Email Address', validators=[DataRequired(), Email(message="Please enter a valid email address."), Length(max=100)])
    
    # Updated discipline options to match actual academic programs
    discipline_choices = [
        ('', '-- Select Discipline --'),
        ('art', 'Art'),
        ('architecture', 'Architecture'),
        ('landscape_architecture', 'Landscape Architecture'),
        ('interior_design', 'Interior Design'),
        ('engineering', 'Engineering'),
        ('hobby_personal', 'Hobby/Personal'),
        ('other', 'Other')
    ]
    discipline = SelectField('Discipline/Major', choices=discipline_choices, validators=[SelectRequired(message="Please select a discipline.")])
    
    class_number = StringField('Class Number (e.g., ARCH 4000 or N/A)', validators=[DataRequired(message="Please enter a class number or N/A."), Length(max=50)])
    
    print_method_choices = [
        ('', '-- Select Print Method --'),
        ('Filament', 'Filament'),
        ('Resin', 'Resin')
    ]
    print_method = SelectField('Print Method', choices=print_method_choices, validators=[SelectRequired(message="Please select a print method.")])
    
    # Combined color choices for server-side validation (JavaScript will filter display)
    all_color_choices = [
        ('', '-- Select Color --'),
        # Filament colors
        ('true_red', 'True Red'),
        ('true_orange', 'True Orange'),
        ('light_orange', 'Light Orange'),
        ('true_yellow', 'True Yellow'),
        ('dark_yellow', 'Dark Yellow'),
        ('lime_green', 'Lime Green'),
        ('green', 'Green'),
        ('forest_green', 'Forest Green'),
        ('blue', 'Blue'),
        ('electric_blue', 'Electric Blue'),
        ('midnight_purple', 'Midnight Purple'),
        ('light_purple', 'Light Purple'),
        ('clear', 'Clear'),
        ('true_white', 'True White'),
        ('gray', 'Gray'),
        ('true_black', 'True Black'),
        ('brown', 'Brown'),
        ('copper', 'Copper'),
        ('bronze', 'Bronze'),
        ('true_silver', 'True Silver'),
        ('true_gold', 'True Gold'),
        ('glow_in_dark', 'Glow in the Dark'),
        ('color_changing', 'Color Changing'),
        # Resin colors (keeping separate 'black', 'white' for resin to avoid conflicts)
        ('black', 'Black'),
        ('white', 'White')
    ]
    color_preference = SelectField('Color Preference', choices=all_color_choices, validators=[SelectRequired(message="Please select a color preference.")])
    
    # New printer selection field
    printer_choices = [
        ('', '-- Select Printer --'),
        ('prusa_mk4s', 'Prusa MK4S'),
        ('prusa_xl', 'Prusa XL'),
        ('raise3d_pro2plus', 'Raise3D Pro 2 Plus'),
        ('formlabs_form3', 'Form 3')
    ]
    printer_selection = SelectField('Which printer do you think your model fits on?', choices=printer_choices, validators=[SelectRequired(message="Please select a printer.")])
    
    # Change minimum charge from checkbox to dropdown
    minimum_charge_choices = [
        ('', '-- Select --'),
        ('yes', 'Yes'),
        ('no', 'No')
    ]
    minimum_charge_consent = SelectField(
        'I understand there is a minimum $3.00 charge for all print jobs, and that the final cost may be higher based on material and time.',
        choices=minimum_charge_choices,
        validators=[SelectRequired(message="You must acknowledge the minimum charge and potential cost.")]
    )
    
    allowed_extensions = ['stl', 'obj', '3mf']
    file_upload = FileField(
        'Upload 3D Model File (.stl, .obj, .3mf)', 
        validators=[
            FileRequired(message="Please select a file to upload."),
            FileAllowed(allowed_extensions, f"File type not allowed. Please upload one of: {', '.join(allowed_extensions)}."),
            FileSizeLimit(max_size_mb=50, message="File size cannot exceed 50MB.")
        ]
    )
    
    submit = SubmitField('Submit Print Job') 