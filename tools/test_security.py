#!/usr/bin/env python3
"""
Security test script for SlicerOpener path validation
"""

import os
import sys
from pathlib import Path
from SlicerOpener import validate_file_security, SecurityError, get_authorized_storage_paths

def test_security_validation():
    """Test security validation with various attack scenarios."""
    
    # Get the project root and storage paths for testing
    project_root = Path(__file__).parent.parent
    storage_base = project_root / "storage"
    
    test_cases = [
        # ALLOWED paths (should pass validation)
        (str(storage_base / "Uploaded" / "test.stl"), True, "Valid uploaded file"),
        (str(storage_base / "ReadyToPrint" / "file.3mf"), True, "Valid ready to print file"),
        (str(storage_base / "Pending" / "model.obj"), True, "Valid pending file"),
        (str(storage_base / "thumbnails" / "thumb.png"), True, "Valid thumbnail file"),
        
        # BLOCKED paths (should fail validation)
        ("C:\\Windows\\System32\\calc.exe", False, "System file access attempt"),
        ("C:\\Program Files\\test.exe", False, "Program Files access attempt"),
        (str(project_root / "app" / "config.py"), False, "Application config access"),
        (str(storage_base / ".." / "app" / "models" / "job.py"), False, "Parent directory traversal"),
        ("\\\\network\\share\\file.stl", False, "Network path access"),
        ("//network/share/file.stl", False, "Unix-style network path"),
        (str(storage_base / "Uploaded" / ".." / ".." / "app" / "config.py"), False, "Complex traversal attack"),
        ("C:\\Users\\Administrator\\Documents\\file.stl", False, "Admin user directory"),
        
        # Edge cases
        ("", False, "Empty path"),
        ("relative/path.stl", False, "Relative path outside storage"),
    ]
    
    print("Testing Security Validation System...")
    print("=" * 60)
    
    # First, show authorized paths
    auth_paths = get_authorized_storage_paths()
    print("Authorized Storage Paths:")
    for path in auth_paths:
        print(f"  ✅ {path}")
    print()
    
    passed = 0
    failed = 0
    
    for test_path, should_succeed, description in test_cases:
        print(f"Testing: {description}")
        print(f"Path: {test_path}")
        
        try:
            result = validate_file_security(test_path, debug=False)
            if should_succeed:
                print(f"✅ PASS: Security validation allowed access")
                print(f"   Validated path: {result}")
                passed += 1
            else:
                print(f"❌ FAIL: Security validation should have blocked this path")
                print(f"   Unexpectedly allowed: {result}")
                failed += 1
        except SecurityError as e:
            if not should_succeed:
                print(f"✅ PASS: Security validation correctly blocked access")
                print(f"   Reason: {str(e)}")
                passed += 1
            else:
                print(f"❌ FAIL: Security validation incorrectly blocked valid path")
                print(f"   Error: {str(e)}")
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: Unexpected error during validation")
            print(f"   Error: {str(e)}")
            failed += 1
        
        print("-" * 40)
    
    print("=" * 60)
    print(f"Security Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🔒 All security tests passed! Path validation is working correctly.")
        print("✅ System is protected against path traversal attacks")
        print("✅ System blocks access to unauthorized directories")
        print("✅ System allows access only to authorized storage paths")
        return True
    else:
        print("⚠️  Some security tests failed. SECURITY VULNERABILITY DETECTED!")
        print("🚨 DO NOT DEPLOY until all security tests pass!")
        return False

def test_path_traversal_attacks():
    """Test specific path traversal attack patterns."""
    
    print("\nTesting Path Traversal Attack Patterns...")
    print("=" * 50)
    
    # Common path traversal patterns
    attack_patterns = [
        "../../../Windows/System32/calc.exe",
        "..\\..\\..\\Windows\\System32\\calc.exe", 
        "....//....//....//Windows//System32//calc.exe",
        "..%2F..%2F..%2FWindows%2FSystem32%2Fcalc.exe",
        "..%5C..%5C..%5CWindows%5CSystem32%5Ccalc.exe",
        "..\\..\\..\\..\\..\\..\\..\\..\\..\\..\\..\\..\\..\\..\\..\\..",
        "storage/../app/config.py",
        "storage\\..\\app\\config.py",
    ]
    
    blocked_count = 0
    
    for pattern in attack_patterns:
        print(f"Testing attack pattern: {pattern}")
        try:
            result = validate_file_security(pattern)
            print(f"❌ VULNERABILITY: Attack pattern was not blocked!")
            print(f"   Allowed path: {result}")
        except SecurityError as e:
            print(f"✅ BLOCKED: {str(e)}")
            blocked_count += 1
        except Exception as e:
            print(f"✅ BLOCKED: Unexpected error (still secure): {str(e)}")
            blocked_count += 1
        print()
    
    print(f"Path Traversal Test Results: {blocked_count}/{len(attack_patterns)} attacks blocked")
    
    if blocked_count == len(attack_patterns):
        print("🔒 All path traversal attacks successfully blocked!")
        return True
    else:
        print("🚨 CRITICAL SECURITY VULNERABILITY: Some attacks were not blocked!")
        return False

if __name__ == '__main__':
    print("SlicerOpener Security Validation Test Suite")
    print("=" * 60)
    
    # Run main security tests
    security_passed = test_security_validation()
    
    # Run path traversal attack tests
    traversal_passed = test_path_traversal_attacks()
    
    print("\n" + "=" * 60)
    print("FINAL SECURITY ASSESSMENT")
    print("=" * 60)
    
    if security_passed and traversal_passed:
        print("🎉 ALL SECURITY TESTS PASSED!")
        print("✅ System is secure and ready for deployment")
        print("✅ Path traversal attacks are prevented")
        print("✅ Unauthorized file access is blocked")
        sys.exit(0)
    else:
        print("🚨 SECURITY TESTS FAILED!")
        print("❌ System has security vulnerabilities")
        print("❌ DO NOT DEPLOY until all tests pass")
        sys.exit(1) 