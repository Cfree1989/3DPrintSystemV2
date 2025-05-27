#!/usr/bin/env python3
"""
SlicerOpener.py - Custom Protocol Handler for 3D Print Files

This script handles 3dprint:// protocol URLs to open 3D files in appropriate slicer software.
Security is the top priority - only files within authorized storage directories are accessible.

Usage:
    python SlicerOpener.py "3dprint://open?file=<encoded_path>"
    python SlicerOpener.py --help

Author: 3D Print System V2
Version: 1.0.0
"""

import sys
import argparse
import urllib.parse
import os
import subprocess
from pathlib import Path
import configparser
import logging
import logging.handlers
from datetime import datetime
import threading

# GUI error dialog support
try:
    import tkinter as tk
    from tkinter import messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


def setup_logging(debug=False):
    """
    Set up logging system with file rotation and appropriate log levels.
    
    Args:
        debug (bool): Enable debug level logging
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    script_dir = Path(__file__).parent
    log_dir = script_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure log file path
    log_file = log_dir / "slicer_opener.log"
    
    # Create logger
    logger = logging.getLogger('SlicerOpener')
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create rotating file handler (max 5MB, keep 5 backup files)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, 
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # Create console handler for errors and debug output
    console_handler = logging.StreamHandler()
    
    # Set log levels
    file_handler.setLevel(logging.INFO)
    console_handler.setLevel(logging.ERROR if not debug else logging.DEBUG)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    # Add formatters to handlers
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_file_access_attempt(logger, url, file_path, result, details=None):
    """
    Log file access attempt with comprehensive details.
    
    Args:
        logger (logging.Logger): Logger instance
        url (str): Original URL received
        file_path (str): Requested file path
        result (str): Result of access attempt (SUCCESS, SECURITY_ERROR, FILE_ERROR, SLICER_ERROR)
        details (str): Additional details about the result
    """
    # Sanitize sensitive information from logs
    safe_url = url[:100] + "..." if len(url) > 100 else url
    safe_path = file_path[:200] + "..." if len(file_path) > 200 else file_path
    
    log_message = f"File access attempt - URL: {safe_url} | Path: {safe_path} | Result: {result}"
    if details:
        log_message += f" | Details: {details}"
    
    if result == "SUCCESS":
        logger.info(log_message)
    elif result == "SECURITY_ERROR":
        logger.warning(log_message)
    else:
        logger.error(log_message)


def log_slicer_launch(logger, slicer_name, slicer_path, file_path, success=True, error_details=None):
    """
    Log slicer launch attempt with details.
    
    Args:
        logger (logging.Logger): Logger instance
        slicer_name (str): Name of the slicer software
        slicer_path (str): Path to slicer executable
        file_path (str): File being opened
        success (bool): Whether launch was successful
        error_details (str): Error details if launch failed
    """
    safe_slicer_path = slicer_path[:100] + "..." if len(slicer_path) > 100 else slicer_path
    safe_file_path = file_path[:200] + "..." if len(file_path) > 200 else file_path
    
    if success:
        logger.info(f"Slicer launched successfully - {slicer_name} at {safe_slicer_path} | File: {safe_file_path}")
    else:
        logger.error(f"Slicer launch failed - {slicer_name} at {safe_slicer_path} | File: {safe_file_path} | Error: {error_details}")


def log_security_validation(logger, file_path, authorized_paths, result, blocked_reason=None):
    """
    Log security validation details for audit trail.
    
    Args:
        logger (logging.Logger): Logger instance
        file_path (str): File path being validated
        authorized_paths (list): List of authorized storage paths
        result (bool): Whether validation passed
        blocked_reason (str): Reason for blocking if validation failed
    """
    safe_path = file_path[:200] + "..." if len(file_path) > 200 else file_path
    auth_count = len(authorized_paths)
    
    if result:
        logger.info(f"Security validation PASSED - Path: {safe_path} | Authorized directories: {auth_count}")
    else:
        logger.warning(f"Security validation FAILED - Path: {safe_path} | Reason: {blocked_reason} | Authorized directories: {auth_count}")


class SecurityError(Exception):
    """Custom exception for security validation failures."""
    pass


class SlicerError(Exception):
    """Custom exception for slicer detection and launch failures."""
    pass


def get_authorized_storage_paths():
    """
    Get list of authorized storage base paths.
    
    Returns:
        list: List of authorized storage directory paths
    """
    # Default authorized paths - can be made configurable later
    script_dir = Path(__file__).parent.parent  # Go up to project root
    storage_base = script_dir / "storage"
    
    authorized_paths = [
        str(storage_base / "Uploaded"),
        str(storage_base / "Pending"), 
        str(storage_base / "ReadyToPrint"),
        str(storage_base / "Printing"),
        str(storage_base / "Completed"),
        str(storage_base / "PaidPickedUp"),
        str(storage_base / "thumbnails"),
    ]
    
    # Convert to absolute paths and normalize
    return [str(Path(p).resolve()) for p in authorized_paths]


def validate_file_security(file_path, debug=False, logger=None):
    """
    Validate that the file path is within authorized storage directories.
    
    This function prevents path traversal attacks and ensures only files
    within the designated storage structure can be accessed.
    
    Args:
        file_path (str): The file path to validate
        debug (bool): Enable debug output
        logger (logging.Logger): Logger instance for audit trail
        
    Returns:
        str: The validated absolute file path
        
    Raises:
        SecurityError: If the file path is not within authorized directories
    """
    if debug:
        print(f"Debug: Validating file path: {file_path}")
    
    try:
        # Convert to absolute path and resolve any symbolic links
        abs_path = Path(file_path).resolve()
        abs_path_str = str(abs_path)
        
        if debug:
            print(f"Debug: Resolved absolute path: {abs_path_str}")
        
        # Get authorized storage paths
        authorized_paths = get_authorized_storage_paths()
        
        if debug:
            print(f"Debug: Authorized paths: {authorized_paths}")
        
        # Check if the file path is within any authorized directory
        path_is_authorized = False
        for auth_path in authorized_paths:
            try:
                # Use Path.is_relative_to() equivalent check
                auth_path_obj = Path(auth_path)
                if abs_path.is_relative_to(auth_path_obj):
                    path_is_authorized = True
                    if debug:
                        print(f"Debug: Path authorized under: {auth_path}")
                    break
            except (ValueError, OSError):
                # Handle cases where paths can't be compared
                continue
        
        if not path_is_authorized:
            # Additional check using string comparison as fallback
            for auth_path in authorized_paths:
                if abs_path_str.startswith(auth_path + os.sep) or abs_path_str == auth_path:
                    path_is_authorized = True
                    if debug:
                        print(f"Debug: Path authorized under (fallback): {auth_path}")
                    break
        
        if not path_is_authorized:
            blocked_reason = f"File path not within authorized storage directories. Path: {abs_path_str}"
            if logger:
                log_security_validation(logger, file_path, authorized_paths, False, blocked_reason)
            raise SecurityError(blocked_reason)
        
        # Additional security checks
        
        # Block network paths
        if abs_path_str.startswith('\\\\') or abs_path_str.startswith('//'):
            blocked_reason = "Network paths are not allowed for security reasons"
            if logger:
                log_security_validation(logger, file_path, authorized_paths, False, blocked_reason)
            raise SecurityError(blocked_reason)
        
        # Block system directories (Windows)
        system_dirs = [
            'C:\\Windows',
            'C:\\Program Files',
            'C:\\Program Files (x86)',
            'C:\\Users\\Administrator',
            'C:\\System Volume Information'
        ]
        
        for sys_dir in system_dirs:
            if abs_path_str.lower().startswith(sys_dir.lower()):
                blocked_reason = f"Access to system directory '{sys_dir}' is not allowed"
                if logger:
                    log_security_validation(logger, file_path, authorized_paths, False, blocked_reason)
                raise SecurityError(blocked_reason)
        
        # Block parent directory traversal patterns in the original path
        if '..' in file_path:
            # This is an additional check - the resolve() should handle most cases
            # but we want to be extra cautious
            if debug:
                print("Debug: Warning - parent directory traversal pattern detected in original path")
        
        # Log successful validation
        if logger:
            log_security_validation(logger, file_path, authorized_paths, True)
        
        return abs_path_str
        
    except SecurityError:
        # Re-raise security errors
        raise
    except Exception as e:
        raise SecurityError(f"Failed to validate file path: {str(e)}")


def get_slicer_paths():
    """
    Get dictionary of known slicer software installation paths.
    
    Returns:
        dict: Dictionary mapping slicer names to possible installation paths
    """
    return {
        'PrusaSlicer': [
            r'C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer.exe',
            r'C:\Program Files (x86)\Prusa3D\PrusaSlicer\prusa-slicer.exe',
            r'C:\Users\{}\AppData\Local\PrusaSlicer\prusa-slicer.exe'.format(os.getenv('USERNAME', 'User')),
        ],
        'UltiMaker Cura': [
            r'C:\Program Files\Ultimaker Cura 5.0\UltiMaker-Cura.exe',
            r'C:\Program Files\Ultimaker Cura\UltiMaker-Cura.exe',
            r'C:\Program Files (x86)\Ultimaker Cura\UltiMaker-Cura.exe',
            r'C:\Program Files\UltiMaker Cura 5.8\UltiMaker-Cura.exe',
        ],
        'Bambu Studio': [
            r'C:\Program Files\Bambu Studio\bambu-studio.exe',
            r'C:\Program Files (x86)\Bambu Studio\bambu-studio.exe',
        ],
        'Orca Slicer': [
            r'C:\Program Files\OrcaSlicer\OrcaSlicer.exe',
            r'C:\Program Files (x86)\OrcaSlicer\OrcaSlicer.exe',
        ]
    }


def detect_installed_slicers(debug=False):
    """
    Detect which slicer software is installed on the system.
    
    Args:
        debug (bool): Enable debug output
        
    Returns:
        dict: Dictionary of installed slicers {name: path}
    """
    installed_slicers = {}
    slicer_paths = get_slicer_paths()
    
    if debug:
        print("Debug: Detecting installed slicer software...")
    
    for slicer_name, possible_paths in slicer_paths.items():
        for path in possible_paths:
            if os.path.exists(path):
                installed_slicers[slicer_name] = path
                if debug:
                    print(f"Debug: Found {slicer_name} at: {path}")
                break
        else:
            if debug:
                print(f"Debug: {slicer_name} not found")
    
    return installed_slicers


def get_file_extension(file_path):
    """
    Get the file extension from a file path.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File extension (lowercase, without dot)
    """
    return Path(file_path).suffix.lower().lstrip('.')


def detect_slicer_for_file(file_path, debug=False):
    """
    Detect the best slicer software for opening a specific file.
    
    Args:
        file_path (str): Path to the 3D file
        debug (bool): Enable debug output
        
    Returns:
        str: Path to the slicer executable
        
    Raises:
        SlicerError: If no suitable slicer is found
    """
    file_ext = get_file_extension(file_path)
    
    if debug:
        print(f"Debug: File extension: {file_ext}")
    
    # Define supported file extensions for each slicer type
    supported_extensions = {
        'stl', '3mf', 'obj', 'ply', 'amf', 'step', 'stp'
    }
    
    if file_ext not in supported_extensions:
        raise SlicerError(f"Unsupported file type: .{file_ext}")
    
    # Detect installed slicers
    installed_slicers = detect_installed_slicers(debug)
    
    if not installed_slicers:
        raise SlicerError(
            "No compatible 3D slicer software found. "
            "Please install PrusaSlicer, UltiMaker Cura, Bambu Studio, or Orca Slicer."
        )
    
    # Preference order for slicer selection
    slicer_preference = ['PrusaSlicer', 'UltiMaker Cura', 'Bambu Studio', 'Orca Slicer']
    
    # Select the best available slicer
    for preferred_slicer in slicer_preference:
        if preferred_slicer in installed_slicers:
            if debug:
                print(f"Debug: Selected {preferred_slicer} (preferred)")
            return installed_slicers[preferred_slicer]
    
    # If no preferred slicer found, use the first available
    slicer_name = list(installed_slicers.keys())[0]
    slicer_path = installed_slicers[slicer_name]
    
    if debug:
        print(f"Debug: Selected {slicer_name} (first available)")
    
    return slicer_path


def launch_slicer(slicer_path, file_path, debug=False, logger=None):
    """
    Launch the slicer software with the specified file.
    
    Args:
        slicer_path (str): Path to the slicer executable
        file_path (str): Path to the 3D file to open
        debug (bool): Enable debug output
        logger (logging.Logger): Logger instance for audit trail
        
    Raises:
        SlicerError: If the slicer fails to launch
    """
    import subprocess
    
    # Determine slicer name from path
    slicer_name = Path(slicer_path).stem
    
    try:
        if debug:
            print(f"Debug: Launching slicer: {slicer_path}")
            print(f"Debug: Opening file: {file_path}")
        
        # Launch the slicer with the file as an argument
        # Use subprocess.Popen to launch and detach
        process = subprocess.Popen(
            [slicer_path, file_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        if debug:
            print(f"Debug: Slicer launched with PID: {process.pid}")
        
        # Log successful launch
        if logger:
            log_slicer_launch(logger, slicer_name, slicer_path, file_path, success=True)
        
        # Don't wait for the process to complete - let it run independently
        
    except FileNotFoundError as e:
        error_msg = f"Slicer executable not found: {slicer_path}"
        if logger:
            log_slicer_launch(logger, slicer_name, slicer_path, file_path, success=False, error_details=str(e))
        raise SlicerError(error_msg)
    except PermissionError as e:
        error_msg = f"Permission denied launching slicer: {slicer_path}"
        if logger:
            log_slicer_launch(logger, slicer_name, slicer_path, file_path, success=False, error_details=str(e))
        raise SlicerError(error_msg)
    except Exception as e:
        error_msg = f"Failed to launch slicer: {str(e)}"
        if logger:
            log_slicer_launch(logger, slicer_name, slicer_path, file_path, success=False, error_details=str(e))
        raise SlicerError(error_msg)


def parse_arguments():
    """Parse command line arguments and return parsed args."""
    parser = argparse.ArgumentParser(
        description='3D Print File Protocol Handler - Opens 3D files in appropriate slicer software',
        epilog='Example: python SlicerOpener.py "3dprint://open?file=C%3A%5Cstorage%5CUploaded%5Ctest.stl"'
    )
    
    parser.add_argument(
        'url',
        nargs='?',
        help='3dprint:// protocol URL containing the file path to open'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='SlicerOpener 1.0.0'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output for troubleshooting'
    )
    
    return parser.parse_args()


def parse_protocol_url(url):
    """
    Parse 3dprint:// protocol URL and extract file path.
    
    Args:
        url (str): The 3dprint:// protocol URL
        
    Returns:
        str: Decoded file path, or None if parsing fails
        
    Raises:
        ValueError: If URL format is invalid
    """
    if not url:
        raise ValueError("No URL provided")
    
    if not url.startswith('3dprint://'):
        raise ValueError(f"Invalid protocol. Expected '3dprint://', got: {url[:20]}...")
    
    try:
        # Manual parsing since urllib.parse doesn't recognize custom schemes properly
        # Expected format: 3dprint://open?file=<encoded_path>
        
        # Remove the protocol prefix
        url_without_protocol = url[10:]  # Remove "3dprint://"
        
        # Split on '?' to separate netloc from query
        if '?' not in url_without_protocol:
            raise ValueError("Missing query parameters in URL")
        
        netloc_part, query_part = url_without_protocol.split('?', 1)
        
        # Validate netloc
        if netloc_part != 'open':
            raise ValueError(f"Invalid netloc. Expected 'open', got: {netloc_part}")
        
        # Parse query parameters
        query_params = urllib.parse.parse_qs(query_part)
        
        if 'file' not in query_params:
            raise ValueError("Missing 'file' parameter in URL")
        
        # Get the file path and decode it
        encoded_path = query_params['file'][0]
        decoded_path = urllib.parse.unquote(encoded_path)
        
        return decoded_path
        
    except Exception as e:
        raise ValueError(f"Failed to parse URL: {str(e)}")


def show_error_popup(title, message):
    """
    Show a user-friendly error popup using tkinter. Non-blocking.
    Falls back to console output if tkinter is unavailable.
    """
    def _popup():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    if TKINTER_AVAILABLE:
        # Run in a separate thread to avoid blocking
        t = threading.Thread(target=_popup)
        t.start()
    else:
        print(f"ERROR: {title} - {message}")


def main():
    """Main entry point for the SlicerOpener script."""
    logger = None
    
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Enable debug output if requested
        debug = args.debug
        
        # Set up logging system (Step 1.4)
        logger = setup_logging(debug)
        logger.info("SlicerOpener started")
        
        # Show help if no URL provided
        if not args.url:
            print("SlicerOpener.py - 3D Print File Protocol Handler")
            print("Usage: python SlicerOpener.py \"3dprint://open?file=<encoded_path>\"")
            print("Use --help for more information")
            logger.info("Help displayed - no URL provided")
            return 0
        
        if debug:
            print(f"Debug: Received URL: {args.url}")
        
        # Parse the protocol URL
        try:
            file_path = parse_protocol_url(args.url)
            print(f"Parsed file path: {file_path}")
            
            if debug:
                print(f"Debug: Successfully parsed file path: {file_path}")
            
        except ValueError as e:
            error_msg = str(e)
            show_error_popup("URL Error", error_msg)
            log_file_access_attempt(logger, args.url, "UNKNOWN", "URL_PARSE_ERROR", error_msg)
            return 1
        
        # Security validation (Step 1.2)
        try:
            validated_path = validate_file_security(file_path, debug, logger)
            if debug:
                print(f"Debug: Security validation passed for: {validated_path}")
        except SecurityError as e:
            error_msg = str(e)
            show_error_popup("Security Error", error_msg)
            log_file_access_attempt(logger, args.url, file_path, "SECURITY_ERROR", error_msg)
            return 1
        
        # File existence check (Step 1.3)
        if not os.path.exists(validated_path):
            error_msg = f"File not found: {validated_path}"
            show_error_popup("File Not Found", error_msg)
            log_file_access_attempt(logger, args.url, file_path, "FILE_ERROR", error_msg)
            return 1
        
        if debug:
            print(f"Debug: File exists: {validated_path}")
        
        # Slicer detection and launch (Step 1.3)
        try:
            slicer_path = detect_slicer_for_file(validated_path, debug)
            if debug:
                print(f"Debug: Selected slicer: {slicer_path}")
            
            launch_slicer(slicer_path, validated_path, debug, logger)
            print(f"SUCCESS: File opened in slicer: {os.path.basename(validated_path)}")
            
            # Log successful file access
            log_file_access_attempt(logger, args.url, file_path, "SUCCESS", f"Opened in {Path(slicer_path).stem}")
            
        except SlicerError as e:
            error_msg = str(e)
            show_error_popup("Slicer Error", error_msg)
            log_file_access_attempt(logger, args.url, file_path, "SLICER_ERROR", error_msg)
            return 1
        
        print("SUCCESS: URL parsing completed")
        logger.info("SlicerOpener completed successfully")
        return 0
        
    except KeyboardInterrupt:
        show_error_popup("Operation Cancelled", "Operation cancelled by user.")
        if logger:
            logger.info("Operation cancelled by user")
        return 1
    except Exception as e:
        error_msg = str(e)
        show_error_popup("Unexpected Error", error_msg)
        if logger:
            logger.error(f"Unexpected error: {error_msg}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 