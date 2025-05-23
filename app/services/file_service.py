# app/services/file_service.py

"""
File service for handling 3D print job file operations.
Handles standardized naming, file saving, and file movements between status directories.
"""
import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app

class FileService:
    """Service for handling file operations in the 3D print system."""
    
    @staticmethod
    def generate_standardized_filename(student_name: str, print_method: str, color: str, job_id: str, original_filename: str) -> str:
        """
        Generate standardized filename following the convention:
        FirstAndLastName_PrintMethod_Color_SimpleJobID.original_extension
        
        Args:
            student_name: Full name from form (e.g., "Jane Doe")
            print_method: Print method (e.g., "Filament", "Resin") 
            color: Selected color (e.g., "Blue", "Red")
            job_id: UUID job ID (will be shortened for filename)
            original_filename: Original uploaded filename for extension
            
        Returns:
            Standardized filename (e.g., "JaneDoe_Filament_Blue_123.stl")
        """
        # Clean and format student name (remove spaces, keep only letters)
        name_parts = student_name.strip().split()
        if len(name_parts) >= 2:
            # Take first and last name, remove non-alphanumeric characters
            first_name = ''.join(c for c in name_parts[0] if c.isalnum())
            last_name = ''.join(c for c in name_parts[-1] if c.isalnum())
            formatted_name = f"{first_name}{last_name}"
        else:
            # Single name case
            formatted_name = ''.join(c for c in name_parts[0] if c.isalnum()) if name_parts else "Unknown"
        
        # Clean print method and color (remove spaces, keep alphanumeric)
        clean_method = ''.join(c for c in print_method if c.isalnum())
        clean_color = ''.join(c for c in color if c.isalnum())
        
        # Create simple job ID from UUID (first 8 characters)
        simple_job_id = job_id.replace('-', '')[:8]
        
        # Extract original extension
        original_ext = Path(original_filename).suffix.lower()
        
        # Construct standardized filename
        standardized_name = f"{formatted_name}_{clean_method}_{clean_color}_{simple_job_id}{original_ext}"
        
        return standardized_name
    
    @staticmethod
    def save_uploaded_file(uploaded_file, student_name: str, print_method: str, color: str, job_id: str) -> tuple[str, str, str]:
        """
        Save uploaded file to the Uploaded directory with standardized naming.
        
        Args:
            uploaded_file: FileStorage object from form
            student_name: Student's full name
            print_method: Selected print method
            color: Selected color
            job_id: UUID job ID
            
        Returns:
            Tuple of (original_filename, display_name, file_path)
            
        Raises:
            OSError: If file saving fails
            ValueError: If storage directory is not configured
        """
        if not uploaded_file or not uploaded_file.filename:
            raise ValueError("No file provided")
        
        # Get storage root from config
        storage_root = current_app.config.get('APP_STORAGE_ROOT')
        if not storage_root:
            raise ValueError("APP_STORAGE_ROOT not configured")
        
        uploaded_dir = os.path.join(storage_root, 'Uploaded')
        
        # Ensure directory exists
        os.makedirs(uploaded_dir, exist_ok=True)
        
        # Store original filename
        original_filename = uploaded_file.filename
        
        # Generate standardized filename
        display_name = FileService.generate_standardized_filename(
            student_name, print_method, color, job_id, original_filename
        )
        
        # Create full file path
        file_path = os.path.join(uploaded_dir, display_name)
        
        # Save the file
        try:
            uploaded_file.save(file_path)
        except Exception as e:
            raise OSError(f"Failed to save file: {str(e)}")
        
        return original_filename, display_name, file_path
    
    @staticmethod
    def move_file(current_path: str, from_status: str, to_status: str, display_name: str) -> str:
        """
        Move file between status directories.
        
        Args:
            current_path: Current full path to the file
            from_status: Current status directory name (e.g., "Uploaded")
            to_status: Target status directory name (e.g., "Pending")
            display_name: Current display name of the file
            
        Returns:
            New file path after moving
            
        Raises:
            OSError: If file move fails
            ValueError: If paths are invalid
        """
        storage_root = current_app.config.get('APP_STORAGE_ROOT')
        if not storage_root:
            raise ValueError("APP_STORAGE_ROOT not configured")
        
        # Construct new path
        new_dir = os.path.join(storage_root, to_status)
        new_path = os.path.join(new_dir, display_name)
        
        # Ensure target directory exists
        os.makedirs(new_dir, exist_ok=True)
        
        # Move file
        try:
            if os.path.exists(current_path):
                os.rename(current_path, new_path)
            else:
                raise FileNotFoundError(f"Source file not found: {current_path}")
        except Exception as e:
            raise OSError(f"Failed to move file from {current_path} to {new_path}: {str(e)}")
        
        return new_path
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Check if a file exists at the given path."""
        return os.path.exists(file_path) if file_path else False
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes. Returns 0 if file doesn't exist."""
        try:
            return os.path.getsize(file_path) if os.path.exists(file_path) else 0
        except OSError:
            return 0

# print("file_service.py loaded (placeholder).") # Debug
pass 