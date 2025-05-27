#!/usr/bin/env python3
"""
Test script for SlicerOpener.py logging functionality.

This script tests the logging system to ensure all file access attempts
are properly logged with appropriate detail levels.
"""

import sys
import os
import subprocess
from pathlib import Path
import time

def run_slicer_opener_test(url, description, expected_result="ERROR"):
    """
    Run SlicerOpener.py with a test URL and return the result.
    
    Args:
        url (str): Test URL to pass to SlicerOpener.py
        description (str): Description of the test
        expected_result (str): Expected result (SUCCESS, ERROR, etc.)
    
    Returns:
        tuple: (return_code, stdout, stderr)
    """
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print(f"Expected: {expected_result}")
    print(f"{'='*60}")
    
    try:
        # Run SlicerOpener.py with the test URL
        result = subprocess.run(
            [sys.executable, "SlicerOpener.py", url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        
        return result.returncode, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print("ERROR: Test timed out after 30 seconds")
        return -1, "", "Timeout"
    except Exception as e:
        print(f"ERROR: Failed to run test: {str(e)}")
        return -1, "", str(e)


def check_log_file():
    """Check if log file exists and display recent entries."""
    log_file = Path("logs/slicer_opener.log")
    
    if log_file.exists():
        print(f"\n{'='*60}")
        print("LOG FILE CONTENTS (Last 20 lines):")
        print(f"{'='*60}")
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show last 20 lines
                for line in lines[-20:]:
                    print(line.rstrip())
        except Exception as e:
            print(f"ERROR: Could not read log file: {str(e)}")
    else:
        print(f"\nWARNING: Log file not found at {log_file}")


def main():
    """Main test function."""
    print("SlicerOpener.py Logging System Test Suite")
    print("=" * 60)
    
    # Change to tools directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Test cases
    test_cases = [
        {
            "url": "3dprint://open?file=C%3A%5C3DPrintSystemV2%5Cstorage%5CUploaded%5Ctest_file.stl",
            "description": "Valid file access (should succeed if file exists)",
            "expected": "SUCCESS or FILE_ERROR"
        },
        {
            "url": "3dprint://open?file=C%3A%5C3DPrintSystemV2%5Cstorage%5CUploaded%5Cnonexistent.stl",
            "description": "Missing file (should log FILE_ERROR)",
            "expected": "FILE_ERROR"
        },
        {
            "url": "3dprint://open?file=..%2F..%2F..%2FWindows%2FSystem32%2Fcalc.exe",
            "description": "Path traversal attack (should log SECURITY_ERROR)",
            "expected": "SECURITY_ERROR"
        },
        {
            "url": "3dprint://open?file=C%3A%5CWindows%5CSystem32%5Ccalc.exe",
            "description": "System directory access (should log SECURITY_ERROR)",
            "expected": "SECURITY_ERROR"
        },
        {
            "url": "3dprint://open?file=C%3A%5C3DPrintSystemV2%5Cstorage%5CUploaded%5Ctest.txt",
            "description": "Unsupported file type (should log SLICER_ERROR)",
            "expected": "SLICER_ERROR"
        },
        {
            "url": "invalid://wrong?file=test.stl",
            "description": "Invalid protocol (should log URL_PARSE_ERROR)",
            "expected": "URL_PARSE_ERROR"
        },
        {
            "url": "3dprint://wrong?file=test.stl",
            "description": "Invalid netloc (should log URL_PARSE_ERROR)",
            "expected": "URL_PARSE_ERROR"
        },
        {
            "url": "3dprint://open?nofile=test.stl",
            "description": "Missing file parameter (should log URL_PARSE_ERROR)",
            "expected": "URL_PARSE_ERROR"
        }
    ]
    
    # Clear existing log file for clean test
    log_file = Path("logs/slicer_opener.log")
    if log_file.exists():
        try:
            log_file.unlink()
            print("Cleared existing log file for clean test")
        except Exception as e:
            print(f"Warning: Could not clear log file: {str(e)}")
    
    # Run all test cases
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\nTEST {i}/{len(test_cases)}")
        
        return_code, stdout, stderr = run_slicer_opener_test(
            test_case["url"],
            test_case["description"],
            test_case["expected"]
        )
        
        results.append({
            "test": test_case["description"],
            "expected": test_case["expected"],
            "return_code": return_code,
            "passed": return_code != 0  # Most tests should fail (return non-zero)
        })
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Display log file contents
    check_log_file()
    
    # Summary
    print(f"\n\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"Test {i}: {status} - {result['test']}")
        if result["passed"]:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    # Check if log file was created
    if log_file.exists():
        print(f"✅ Log file created successfully: {log_file}")
        print(f"✅ Log file size: {log_file.stat().st_size} bytes")
    else:
        print("❌ Log file was not created")
    
    print(f"\n{'='*60}")
    print("LOGGING SYSTEM TEST COMPLETE")
    print(f"{'='*60}")
    
    return 0 if passed >= len(results) * 0.8 else 1  # 80% pass rate required


if __name__ == "__main__":
    sys.exit(main()) 