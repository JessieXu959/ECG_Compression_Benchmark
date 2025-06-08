#!/usr/bin/env python3
"""
Test script for new progress bar and personal performance features
"""

import requests
import json
import time

def test_backend_features():
    """Test all backend features"""
    print("🧪 Testing ECG Compression Challenge - Enhanced Features")
    print("=" * 60)

    # Test health check
    print("1. 🏥 Testing backend health...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Backend healthy: {health_data['message']}")
            print(f"   📊 Total submissions: {health_data['total_submissions']}")
            print(f"   👥 Active users: {health_data['active_users']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

    # Test user login
    print("\n2. 🔐 Testing user authentication...")
    login_data = {
        "teamName": "string",
        "password": "string"
    }

    try:
        response = requests.post("http://localhost:8000/api/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            print(f"   ✅ Login successful")
            print(f"   🎫 Token: {token[:50]}...")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False

    # Test user submissions endpoint
    print("\n3. 📋 Testing user submissions API...")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get("http://localhost:8000/api/user-submissions/string", headers=headers)
        if response.status_code == 200:
            data = response.json()
            submissions = data.get("submissions", [])
            print(f"   ✅ User submissions retrieved: {len(submissions)} submissions")

            for i, sub in enumerate(submissions[:3]):  # Show first 3
                print(f"   📄 Submission {i+1}:")
                print(f"      - Algorithm: {sub.get('algorithmName', 'N/A')}")
                print(f"      - Status: {sub.get('status', 'N/A')}")
                print(f"      - Score: {sub.get('score', 'N/A')}")
                print(f"      - Date: {sub.get('submitted_at', 'N/A')}")
        else:
            print(f"   ❌ User submissions failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ User submissions error: {e}")

    # Test leaderboard
    print("\n4. 🏆 Testing leaderboard...")
    try:
        response = requests.get("http://localhost:8000/api/leaderboard")
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            print(f"   ✅ Leaderboard retrieved: {len(results)} entries")

            for i, result in enumerate(results[:3]):  # Show top 3
                print(f"   🏅 Rank {i+1}: {result.get('participant_name', 'N/A')} - Score: {result.get('score', 'N/A')}")
        else:
            print(f"   ❌ Leaderboard failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Leaderboard error: {e}")

    print("\n5. 🎯 Testing submission workflow...")

    # Check if test file exists
    import os
    if os.path.exists('test_ecg_algorithm.zip'):
        print("   📦 Test ZIP file found")

        # Test file upload
        files = {'file': ('test_ecg_algorithm.zip', open('test_ecg_algorithm.zip', 'rb'), 'application/zip')}
        data = {
            'algorithm_name': 'ProgressBarTest_v1.0',
            'paper_title': 'Testing Progress Bar Feature',
            'paper_authors': 'Test Team',
            'paper_type': 'conference'
        }

        try:
            response = requests.post("http://localhost:8000/api/submit-to-codabench",
                                   files=files, data=data, headers=headers)

            if response.status_code == 200:
                result = response.json()
                submission_id = result.get("submission_id")
                print(f"   ✅ File upload successful")
                print(f"   🆔 Submission ID: {submission_id}")

                # Test progress tracking
                print(f"\n   ⏳ Testing progress tracking...")
                for i in range(6):  # Check 6 times over 30 seconds
                    time.sleep(5)

                    try:
                        status_response = requests.get(f"http://localhost:8000/api/submission-status/{submission_id}",
                                                     headers=headers)
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            status = status_data.get("status", "unknown")
                            score = status_data.get("score", "N/A")

                            print(f"   📊 Check {i+1}: Status = {status}, Score = {score}")

                            if status in ['completed', 'failed']:
                                if status == 'completed':
                                    print(f"   🎉 Submission completed successfully!")
                                    print(f"   📊 Final Score: {score}")
                                    print(f"   📏 Metrics: {status_data.get('metrics', {})}")
                                else:
                                    print(f"   ❌ Submission failed: {status_data.get('error', 'Unknown error')}")
                                break
                        else:
                            print(f"   ⚠️ Status check failed: {status_response.status_code}")
                    except Exception as e:
                        print(f"   ⚠️ Status check error: {e}")

            else:
                print(f"   ❌ File upload failed: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"   ❌ Upload error: {e}")
    else:
        print("   ⚠️ Test ZIP file not found - skipping upload test")

    print("\n" + "=" * 60)
    print("🎊 Testing completed!")
    print("\n💡 Frontend Features to Test:")
    print("   1. Open http://localhost:3000")
    print("   2. Login with team 'string', password 'string'")
    print("   3. Go to Submit section")
    print("   4. Check 'Your Current Performance' table")
    print("   5. Upload a file and watch the progress bar")
    print("   6. Verify that both tables show consistent data")

if __name__ == "__main__":
    test_backend_features()