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


def validate_file_security(file_path, debug=False):
    """
    Validate that the file path is within authorized storage directories.
    
    This function prevents path traversal attacks and ensures only files
    within the designated storage structure can be accessed.
    
    Args:
        file_path (str): The file path to validate
        debug (bool): Enable debug output
        
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
            raise SecurityError(
                f"File path not within authorized storage directories. "
                f"Path: {abs_path_str}"
            )
        
        # Additional security checks
        
        # Block network paths
        if abs_path_str.startswith('\\\\') or abs_path_str.startswith('//'):
            raise SecurityError("Network paths are not allowed for security reasons")
        
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
                raise SecurityError(f"Access to system directory '{sys_dir}' is not allowed")
        
        # Block parent directory traversal patterns in the original path
        if '..' in file_path:
            # This is an additional check - the resolve() should handle most cases
            # but we want to be extra cautious
            if debug:
                print("Debug: Warning - parent directory traversal pattern detected in original path")
        
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


def launch_slicer(slicer_path, file_path, debug=False):
    """
    Launch the slicer software with the specified file.
    
    Args:
        slicer_path (str): Path to the slicer executable
        file_path (str): Path to the 3D file to open
        debug (bool): Enable debug output
        
    Raises:
        SlicerError: If the slicer fails to launch
    """
    import subprocess
    
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
        
        # Don't wait for the process to complete - let it run independently
        
    except FileNotFoundError:
        raise SlicerError(f"Slicer executable not found: {slicer_path}")
    except PermissionError:
        raise SlicerError(f"Permission denied launching slicer: {slicer_path}")
    except Exception as e:
        raise SlicerError(f"Failed to launch slicer: {str(e)}")


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


def main():
    """Main entry point for the SlicerOpener script."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Show help if no URL provided
        if not args.url:
            print("SlicerOpener.py - 3D Print File Protocol Handler")
            print("Usage: python SlicerOpener.py \"3dprint://open?file=<encoded_path>\"")
            print("Use --help for more information")
            return 0
        
        # Enable debug output if requested
        debug = args.debug
        
        if debug:
            print(f"Debug: Received URL: {args.url}")
        
        # Parse the protocol URL
        try:
            file_path = parse_protocol_url(args.url)
            print(f"Parsed file path: {file_path}")
            
            if debug:
                print(f"Debug: Successfully parsed file path: {file_path}")
            
        except ValueError as e:
            print(f"ERROR: {str(e)}")
            return 1
        
        # Security validation (Step 1.2)
        try:
            validated_path = validate_file_security(file_path, debug)
            if debug:
                print(f"Debug: Security validation passed for: {validated_path}")
        except SecurityError as e:
            print(f"SECURITY ERROR: {str(e)}")
            return 1
        
        # File existence check (Step 1.3)
        if not os.path.exists(validated_path):
            print(f"ERROR: File not found: {validated_path}")
            return 1
        
        if debug:
            print(f"Debug: File exists: {validated_path}")
        
        # Slicer detection and launch (Step 1.3)
        try:
            slicer_path = detect_slicer_for_file(validated_path, debug)
            if debug:
                print(f"Debug: Selected slicer: {slicer_path}")
            
            launch_slicer(slicer_path, validated_path, debug)
            print(f"SUCCESS: File opened in slicer: {os.path.basename(validated_path)}")
            
        except SlicerError as e:
            print(f"SLICER ERROR: {str(e)}")
            return 1
        
        # TODO: Add logging (Step 1.4)
        
        print("SUCCESS: URL parsing completed")
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"UNEXPECTED ERROR: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 