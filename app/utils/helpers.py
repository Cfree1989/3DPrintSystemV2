# app/utils/helpers.py
"""
Utility functions for display formatting and other helper functions.
"""

from datetime import datetime
import pytz
import math

def get_display_name(value, field_type=None):
    """
    Convert database/form values to proper display names.
    
    Args:
        value: The raw value from database/form
        field_type: Optional field type for specific formatting
    
    Returns:
        Properly formatted display string
    """
    if not value:
        return "N/A"
    
    # Handle specific field types
    if field_type == 'printer':
        return get_printer_display_name(value)
    elif field_type == 'color':
        return get_color_display_name(value)
    elif field_type == 'discipline':
        return get_discipline_display_name(value)
    
    # Default formatting: replace underscores with spaces and title case
    return value.replace('_', ' ').title()

def get_printer_display_name(printer_key):
    """Get proper display name for printer keys."""
    printer_names = {
        'prusa_mk4s': 'Prusa MK4S',
        'prusa_xl': 'Prusa XL', 
        'raise3d_pro2plus': 'Raise3D Pro 2 Plus',
        'formlabs_form3': 'Form 3'
    }
    return printer_names.get(printer_key, printer_key.replace('_', ' ').title())

def get_color_display_name(color_key):
    """Get proper display name for color keys."""
    color_names = {
        'true_red': 'True Red',
        'true_orange': 'True Orange',
        'light_orange': 'Light Orange',
        'true_yellow': 'True Yellow',
        'dark_yellow': 'Dark Yellow',
        'lime_green': 'Lime Green',
        'green': 'Green',
        'forest_green': 'Forest Green',
        'blue': 'Blue',
        'electric_blue': 'Electric Blue',
        'midnight_purple': 'Midnight Purple',
        'light_purple': 'Light Purple',
        'clear': 'Clear',
        'true_white': 'True White',
        'gray': 'Gray',
        'true_black': 'True Black',
        'brown': 'Brown',
        'copper': 'Copper',
        'bronze': 'Bronze',
        'true_silver': 'True Silver',
        'true_gold': 'True Gold',
        'glow_in_dark': 'Glow in the Dark',
        'color_changing': 'Color Changing',
        'black': 'Black',
        'white': 'White'
    }
    return color_names.get(color_key, color_key.replace('_', ' ').title())

def get_discipline_display_name(discipline_key):
    """Get proper display name for discipline keys."""
    discipline_names = {
        'art': 'Art',
        'architecture': 'Architecture',
        'landscape_architecture': 'Landscape Architecture',
        'interior_design': 'Interior Design',
        'engineering': 'Engineering',
        'hobby_personal': 'Hobby/Personal',
        'other': 'Other'
    }
    return discipline_names.get(discipline_key, discipline_key.replace('_', ' ').title())

def get_status_display_name(status_key):
    """Get proper display name for job status keys."""
    status_names = {
        'UPLOADED': 'Uploaded',
        'PENDING': 'Pending',
        'READYTOPRINT': 'Ready to Print',
        'PRINTING': 'Printing',
        'COMPLETED': 'Completed',
        'PAIDPICKEDUP': 'Paid/Picked Up',
        'REJECTED': 'Rejected'
    }
    return status_names.get(status_key, status_key.replace('_', ' ').title())

def format_datetime_local(dt):
    """
    Convert UTC datetime to Central Time and format for display.
    
    Args:
        dt: datetime object (assumed to be UTC)
    
    Returns:
        Formatted string in Central Time
    """
    if not dt:
        return "N/A"
    
    # Define timezones
    utc = pytz.UTC
    central = pytz.timezone('America/Chicago')  # Baton Rouge is in Central Time
    
    # If datetime is naive, assume it's UTC
    if dt.tzinfo is None:
        dt = utc.localize(dt)
    
    # Convert to Central Time
    local_dt = dt.astimezone(central)
    
    return local_dt.strftime('%m/%d/%Y at %I:%M %p %Z')

def format_datetime_detailed(dt):
    """
    Convert UTC datetime to Central Time and format for detailed display.
    
    Args:
        dt: datetime object (assumed to be UTC)
    
    Returns:
        Formatted string in Central Time with full month name
    """
    if not dt:
        return "N/A"
    
    # Define timezones
    utc = pytz.UTC
    central = pytz.timezone('America/Chicago')  # Baton Rouge is in Central Time
    
    # If datetime is naive, assume it's UTC
    if dt.tzinfo is None:
        dt = utc.localize(dt)
    
    # Convert to Central Time
    local_dt = dt.astimezone(central)
    
    return local_dt.strftime('%B %d, %Y at %I:%M %p %Z')

def round_time_conservative(time_hours):
    """
    Round time to nearest 0.5 hours, always rounding UP for conservative estimates.
    
    Args:
        time_hours: Time in hours (float)
    
    Returns:
        Time rounded up to nearest 0.5 hours (float)
    
    Examples:
        1.2 hours → 1.5 hours
        1.6 hours → 2.0 hours
        2.1 hours → 2.5 hours
        2.5 hours → 2.5 hours (no change)
        2.0 hours → 2.0 hours (no change)
    """
    if not time_hours or time_hours <= 0:
        return 0.5  # Minimum realistic print time
    
    # Calculate how many 0.5-hour increments we need
    increments = math.ceil(time_hours / 0.5)
    
    # Convert back to hours
    return increments * 0.5

# Placeholder for general helper functions
pass 