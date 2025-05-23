#!/usr/bin/env python3
"""
Test script for job confirmation workflow
"""
import requests

# Token from the pending job
token = "IjUzZGM1MzVhLTNmNWEtNGY4MS04M2Q2LWFmNmE2NTU4ZGYxOCI.aDC72g.i3oj5iu5aR9hshbKD1Ekr5GHVDY"
url = f"http://localhost:5000/confirm/{token}"

print("Testing job confirmation...")
print(f"URL: {url}")

# Test POST request to confirm the job
response = requests.post(url)

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response Content Length: {len(response.content)}")

if response.status_code == 200:
    print("SUCCESS: Job confirmation page loaded")
    if "Job Confirmed Successfully" in response.text:
        print("SUCCESS: Job was confirmed!")
    elif "Confirm Your 3D Print Job" in response.text:
        print("INFO: Still on confirmation page - may need CSRF token")
elif response.status_code == 302:
    print(f"REDIRECT: {response.headers.get('Location', 'Unknown location')}")
else:
    print(f"ERROR: Unexpected response - {response.status_code}")

print(f"Content sample: {response.text[:200]}...") 