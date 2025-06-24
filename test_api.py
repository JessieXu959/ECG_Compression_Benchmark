#!/usr/bin/env python3
"""
简单的API测试脚本
"""
import requests
import json

def test_api():
    base_url = "http://localhost:8000"

    print("🔍 Testing ECG Compression Challenge API")
    print("=" * 50)

    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health Check: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Users: {health_data.get('active_users')}")
            print(f"   Submissions: {health_data.get('total_submissions')}")
    except Exception as e:
        print(f"❌ Health Check failed: {e}")

    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root Endpoint: {response.status_code}")
        if response.status_code == 200:
            root_data = response.json()
            print(f"   Name: {root_data.get('name')}")
            print(f"   Version: {root_data.get('version')}")
    except Exception as e:
        print(f"❌ Root Endpoint failed: {e}")

    # Test leaderboard endpoint
    try:
        response = requests.get(f"{base_url}/api/leaderboard")
        print(f"✅ Leaderboard: {response.status_code}")
        if response.status_code == 200:
            leaderboard_data = response.json()
            print(f"   Results: {len(leaderboard_data.get('results', []))} entries")
    except Exception as e:
        print(f"❌ Leaderboard failed: {e}")

    # Test global stats
    try:
        response = requests.get(f"{base_url}/api/global-stats")
        print(f"✅ Global Stats: {response.status_code}")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"   Total Users: {stats_data.get('global_metrics', {}).get('total_users', 0)}")
            print(f"   Total Submissions: {stats_data.get('global_metrics', {}).get('total_submissions', 0)}")
    except Exception as e:
        print(f"❌ Global Stats failed: {e}")

    # Test docs endpoint
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"✅ Documentation: {response.status_code}")
    except Exception as e:
        print(f"❌ Documentation failed: {e}")

    print("=" * 50)
    print("🎯 API Test Complete")

if __name__ == "__main__":
    test_api()