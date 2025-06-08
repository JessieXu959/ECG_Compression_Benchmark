#!/usr/bin/env python3
"""
Quick test script to verify token authentication fix
"""

import requests
import json
import zipfile
import tempfile
from pathlib import Path

BASE_URL = "http://localhost:8000/api"

def test_authentication_flow():
    """Test the complete authentication and submission flow"""

    print("🧪 Testing Authentication Fix")
    print("=" * 50)

    # Test 1: Register a new user
    print("\n1. Testing Registration...")
    register_data = {
        "teamName": "TestTeam_Fix",
        "email": "test@fix.com",
        "password": "TestPassword123!"
    }

    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        if response.status_code == 200:
            result = response.json()
            token = result["access_token"]
            print(f"✅ Registration successful!")
            print(f"📄 Token: {token[:50]}...")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            # Try login instead
            print("\n2. Trying Login...")
            login_data = {
                "teamName": "TestTeam_Fix",
                "password": "TestPassword123!"
            }
            response = requests.post(f"{BASE_URL}/login", json=login_data)
            if response.status_code == 200:
                result = response.json()
                token = result["access_token"]
                print(f"✅ Login successful!")
                print(f"📄 Token: {token[:50]}...")
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

    # Test 2: Create a test ZIP file
    print("\n3. Creating test ZIP file...")
    try:
        temp_dir = Path(tempfile.mkdtemp())
        zip_path = temp_dir / "test_algorithm.zip"

        # Create a simple test file
        test_content = """
import numpy as np

def compress_ecg(signal):
    return signal[::2]  # Simple compression

def decompress_ecg(compressed):
    return np.repeat(compressed, 2)  # Simple decompression
"""

        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("algorithm.py", test_content)
            zf.writestr("README.md", "# Test Algorithm")

        print(f"✅ Test ZIP created: {zip_path}")

    except Exception as e:
        print(f"❌ ZIP creation error: {e}")
        return False

    # Test 3: Submit the algorithm
    print("\n4. Testing Algorithm Submission...")
    try:
        files = {
            'file': ('test_algorithm.zip', open(zip_path, 'rb'), 'application/zip')
        }

        data = {
            'algorithm_name': 'TestAlgorithm_AuthFix',
            'paper_title': 'Test Paper for Auth Fix',
            'paper_authors': 'Test Author',
            'paper_type': 'conference',
            'paper_doi': '10.1000/test123'
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
            submission_id = result.get("submission_id")

            # Test 4: Check submission status
            if submission_id:
                print(f"\n5. Checking submission status...")
                status_response = requests.get(
                    f"{BASE_URL}/submission-status/{submission_id}",
                    headers=headers
                )

                if status_response.status_code == 200:
                    status_result = status_response.json()
                    print("✅ Status check successful!")
                    print(f"📄 Status: {json.dumps(status_result, indent=2)}")
                else:
                    print(f"⚠️ Status check failed: {status_response.status_code}")

            return True
        else:
            print(f"❌ Submission failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Submission error: {e}")
        return False

    finally:
        # Cleanup
        try:
            zip_path.unlink()
            temp_dir.rmdir()
        except:
            pass

def main():
    """Run the authentication test"""
    try:
        # First check if backend is running
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code != 200:
            print("❌ Backend not running. Please start the backend first:")
            print("   cd mini-backend && python main.py")
            return

        print("✅ Backend is running")

        # Run the authentication test
        success = test_authentication_flow()

        print("\n" + "=" * 50)
        if success:
            print("🎉 Authentication fix test PASSED!")
            print("✅ JWT token authentication is working correctly")
        else:
            print("❌ Authentication fix test FAILED!")
            print("⚠️ There are still issues with token authentication")

    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    main()