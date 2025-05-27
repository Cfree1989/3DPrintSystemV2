#!/usr/bin/env python3
"""
Test script for SlicerOpener URL parsing functionality
"""

from SlicerOpener import parse_protocol_url

def test_url_parsing():
    """Test various URL parsing scenarios."""
    
    test_cases = [
        # Valid URLs
        ("3dprint://open?file=C%3A%5Cstorage%5CUploaded%5Ctest.stl", "C:\\storage\\Uploaded\\test.stl", True),
        ("3dprint://open?file=test%20with%20spaces.stl", "test with spaces.stl", True),
        ("3dprint://open?file=simple.3mf", "simple.3mf", True),
        
        # Invalid URLs
        ("invalid://wrong?file=test.stl", None, False),
        ("3dprint://wrong?file=test.stl", None, False),
        ("3dprint://open?nofile=test.stl", None, False),
        ("3dprint://open", None, False),
        ("", None, False),
    ]
    
    print("Testing URL parsing functionality...")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for url, expected_path, should_succeed in test_cases:
        try:
            result = parse_protocol_url(url)
            if should_succeed:
                if result == expected_path:
                    print(f"✅ PASS: {url[:40]}...")
                    print(f"   Expected: {expected_path}")
                    print(f"   Got:      {result}")
                    passed += 1
                else:
                    print(f"❌ FAIL: {url[:40]}...")
                    print(f"   Expected: {expected_path}")
                    print(f"   Got:      {result}")
                    failed += 1
            else:
                print(f"❌ FAIL: {url[:40]}... (should have failed but didn't)")
                print(f"   Got: {result}")
                failed += 1
        except Exception as e:
            if not should_succeed:
                print(f"✅ PASS: {url[:40]}... (correctly failed)")
                print(f"   Error: {str(e)}")
                passed += 1
            else:
                print(f"❌ FAIL: {url[:40]}... (should have succeeded)")
                print(f"   Error: {str(e)}")
                failed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! URL parsing is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False

if __name__ == '__main__':
    test_url_parsing() 