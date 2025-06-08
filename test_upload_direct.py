#!/usr/bin/env python3
"""
Direct API test - bypassing Swagger UI issues
"""

import requests

def test_direct_upload():
    """Test file upload directly with requests"""

    print("🧪 Testing Direct File Upload")
    print("=" * 50)

    # Your exact token from the API response
    token = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ0ZWFtTmFtZSI6ICJzdHJpbmciLCAiZW1haWwiOiAic3RyaW5nIiwgImlhdCI6IDE3NDk0MTYzNDUsICJleHAiOiAxNzQ5NTAyNzQ1fQ.signature"

    # API URL
    url = "http://localhost:8000/api/submit-to-codabench"

    # Headers
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Prepare the file and data
    try:
        with open('test_ecg_algorithm.zip', 'rb') as f:
            files = {
                'file': ('test_ecg_algorithm.zip', f, 'application/zip')
            }

            data = {
                'algorithm_name': 'TestAlgorithm_Direct',
                'paper_title': 'Direct Upload Test Paper',
                'paper_authors': 'Test Author',
                'paper_type': 'conference',
                'paper_doi': '10.1000/direct-test'
            }

            print(f"📤 Uploading to: {url}")
            print(f"🔑 Using token: {token[:50]}...")
            print(f"📄 Algorithm name: {data['algorithm_name']}")

            # Make the request
            response = requests.post(url, files=files, data=data, headers=headers)

            print(f"\n📊 Response Status: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")

            if response.status_code == 200:
                result = response.json()
                print("✅ Upload successful!")
                print(f"📄 Response: {result}")
                return True
            else:
                print("❌ Upload failed!")
                print(f"📄 Error Response: {response.text}")
                return False

    except FileNotFoundError:
        print("❌ test_ecg_algorithm.zip not found. Please run create_test_zip.py first")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health_check():
    """Test if backend is responding"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Checking backend health...")
    if not test_health_check():
        print("\n⚠️ Backend is not running. Please start it with:")
        print("   cd mini-backend && python main.py")
        exit(1)

    print("\n🚀 Starting direct upload test...")
    success = test_direct_upload()

    print("\n" + "=" * 50)
    if success:
        print("🎉 Direct upload test PASSED!")
        print("✅ The issue is with Swagger UI, not your authentication")
        print("\n💡 Recommendations:")
        print("   1. Use the frontend at http://localhost:3000")
        print("   2. Or use curl/requests directly")
        print("   3. Avoid using Swagger UI for file uploads")
    else:
        print("❌ Direct upload test FAILED!")
        print("⚠️ There may be a real authentication issue")