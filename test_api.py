#!/usr/bin/env python3
"""
ECG Compression Challenge - API Test Script
Demonstrates how to test the API endpoints with proper parameters
"""

import requests
import json
from pathlib import Path

# API Configuration
BASE_URL = "http://localhost:8000/api"

def test_register():
    """Test user registration"""
    print("🔐 Testing user registration...")

    payload = {
        "teamName": "TestTeam123",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }

    response = requests.post(f"{BASE_URL}/register", json=payload)

    if response.status_code == 200:
        result = response.json()
        print("✅ Registration successful!")
        print(f"📄 Response: {json.dumps(result, indent=2)}")
        return result.get("access_token")
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"📄 Error: {response.text}")
        return None

def test_login():
    """Test user login"""
    print("\n🔑 Testing user login...")

    payload = {
        "teamName": "TestTeam123",
        "password": "TestPassword123!"
    }

    response = requests.post(f"{BASE_URL}/login", json=payload)

    if response.status_code == 200:
        result = response.json()
        print("✅ Login successful!")
        print(f"📄 Response: {json.dumps(result, indent=2)}")
        return result.get("access_token")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"📄 Error: {response.text}")
        return None

def create_test_zip():
    """Create a test ZIP file for submission"""
    import zipfile
    import tempfile

    # Create a temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    zip_path = temp_dir / "test_algorithm.zip"

    # Create some test files
    test_files = {
        "README.md": "# Test ECG Compression Algorithm\n\nThis is a test submission.",
        "algorithm.py": """
import numpy as np

def compress_ecg(signal):
    # Mock compression algorithm
    return signal[::2]  # Simple downsampling

def decompress_ecg(compressed_signal):
    # Mock decompression
    return np.repeat(compressed_signal, 2)  # Simple upsampling
""",
        "requirements.txt": "numpy>=1.20.0\nscipy>=1.7.0"
    }

    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for filename, content in test_files.items():
            zf.writestr(filename, content)

    print(f"📦 Created test ZIP file: {zip_path}")
    return zip_path

def test_submit_algorithm(token):
    """Test algorithm submission"""
    print("\n📤 Testing algorithm submission...")

    if not token:
        print("❌ No token provided, skipping submission test")
        return

    # Create test ZIP file
    zip_path = create_test_zip()

    try:
        # Prepare form data
        files = {
            'file': ('test_algorithm.zip', open(zip_path, 'rb'), 'application/zip')
        }

        data = {
            'algorithm_name': 'TestAlgorithm_v1.0',
            'paper_title': 'Novel ECG Compression Algorithm Using Deep Learning',
            'paper_authors': 'John Doe, Jane Smith',
            'paper_type': 'journal',
            'paper_doi': '10.1000/example123'
        }

        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = requests.post(f"{BASE_URL}/submit-to-codabench",
                               files=files, data=data, headers=headers)

        if response.status_code == 200:
            result = response.json()
            print("✅ Submission successful!")
            print(f"📄 Response: {json.dumps(result, indent=2)}")
            return result.get("submission_id")
        else:
            print(f"❌ Submission failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return None

    finally:
        # Clean up
        if zip_path.exists():
            zip_path.unlink()
        zip_path.parent.rmdir()

def test_submission_status(token, submission_id):
    """Test checking submission status"""
    print(f"\n📊 Testing submission status check for: {submission_id}")

    if not token or not submission_id:
        print("❌ Missing token or submission_id, skipping status test")
        return

    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(f"{BASE_URL}/submission-status/{submission_id}",
                           headers=headers)

    if response.status_code == 200:
        result = response.json()
        print("✅ Status check successful!")
        print(f"📄 Response: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Status check failed: {response.status_code}")
        print(f"📄 Error: {response.text}")

def test_leaderboard():
    """Test leaderboard endpoint"""
    print("\n🏆 Testing leaderboard...")

    response = requests.get(f"{BASE_URL}/leaderboard")

    if response.status_code == 200:
        result = response.json()
        print("✅ Leaderboard fetch successful!")
        print(f"📄 Response: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Leaderboard fetch failed: {response.status_code}")
        print(f"📄 Error: {response.text}")

def test_health_check():
    """Test health check endpoint"""
    print("\n🏥 Testing health check...")

    response = requests.get("http://localhost:8000/health")

    if response.status_code == 200:
        result = response.json()
        print("✅ Health check successful!")
        print(f"📄 Response: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
        print(f"📄 Error: {response.text}")

def main():
    """Run all API tests"""
    print("🚀 Starting ECG Compression Challenge API Tests")
    print("=" * 60)

    # Test health check first
    test_health_check()

    # Test registration (or login if user exists)
    token = test_register()
    if not token:
        # Try login if registration failed (user might exist)
        token = test_login()

    # Test submission
    submission_id = test_submit_algorithm(token)

    # Wait a moment for processing
    if submission_id:
        import time
        print("\n⏳ Waiting 10 seconds for processing...")
        time.sleep(10)
        test_submission_status(token, submission_id)

    # Test leaderboard
    test_leaderboard()

    print("\n" + "=" * 60)
    print("🎉 API tests completed!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test error: {e}")