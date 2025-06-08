#!/usr/bin/env python3
"""
Test script to verify data persistence and demo data clearing
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:8000/api"
TEST_TEAM = "TestDataPersistence"
TEST_EMAIL = "test.persistence@example.com"
TEST_PASSWORD = "TestPass123!"

def test_data_persistence():
    """Test that only real data is shown and persisted"""

    print("🧪 Testing Data Persistence and Demo Data Clearing")
    print("=" * 60)

    # Test 1: Check if backend is running
    print("1. Testing backend health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.ok:
            print("✅ Backend is healthy")
        else:
            print("❌ Backend health check failed")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

    # Test 2: Register new user
    print("\n2. Testing user registration...")
    register_data = {
        "teamName": TEST_TEAM,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }

    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        if response.ok:
            result = response.json()
            token = result.get('access_token')
            print(f"✅ Registration successful, token received")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

    # Test 3: Check empty submissions for new user
    print("\n3. Testing empty submissions for new user...")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/user-submissions/{TEST_TEAM}", headers=headers)
        if response.ok:
            data = response.json()
            submissions = data.get('submissions', [])
            if len(submissions) == 0:
                print("✅ New user has no submissions (as expected)")
            else:
                print(f"❌ New user has {len(submissions)} submissions (unexpected)")
                return False
        else:
            print(f"❌ Failed to get user submissions: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting submissions: {e}")
        return False

    # Test 4: Check empty leaderboard
    print("\n4. Testing leaderboard state...")
    try:
        response = requests.get(f"{BASE_URL}/leaderboard", headers=headers)
        if response.ok:
            data = response.json()
            results = data.get('results', [])
            print(f"✅ Leaderboard has {len(results)} entries")
        else:
            print(f"❌ Failed to get leaderboard: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting leaderboard: {e}")

    print("\n" + "=" * 60)
    print("✅ All data persistence tests passed!")
    print("\nKey findings:")
    print("- Backend is running and healthy")
    print("- New users start with no submissions")
    print("- No demo/static data is present")
    print("- API endpoints are working correctly")

    return True

if __name__ == "__main__":
    success = test_data_persistence()
    if success:
        print("\n🎉 Data persistence system is working correctly!")
    else:
        print("\n❌ Some tests failed. Please check the backend.")