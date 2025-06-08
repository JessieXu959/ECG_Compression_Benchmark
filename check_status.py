#!/usr/bin/env python3
"""
Check submission status
"""

import requests
import json

def check_submission_status():
    token = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ0ZWFtTmFtZSI6ICJzdHJpbmciLCAiZW1haWwiOiAic3RyaW5nIiwgImlhdCI6IDE3NDk0MTYzNDUsICJleHAiOiAxNzQ5NTAyNzQ1fQ.signature"
    submission_id = "816c956e-505e-49af-b25c-cd8a3634ceb5"

    headers = {
        'Authorization': f'Bearer {token}'
    }

    url = f"http://localhost:8000/api/submission-status/{submission_id}"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            print("📊 Submission Status:")
            print(json.dumps(result, indent=2))

            # Check if it's completed
            if result.get('status') == 'completed':
                print(f"\n🎉 Submission completed!")
                print(f"📊 Score: {result.get('score', 'N/A')}")
                print(f"📏 Metrics: {result.get('metrics', {})}")
            else:
                print(f"\n⏳ Status: {result.get('status', 'Unknown')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

def check_leaderboard():
    """Check the leaderboard"""
    try:
        response = requests.get("http://localhost:8000/api/leaderboard")

        if response.status_code == 200:
            result = response.json()
            print("\n🏆 Current Leaderboard:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Leaderboard error: {response.status_code}")

    except Exception as e:
        print(f"❌ Leaderboard error: {e}")

if __name__ == "__main__":
    print("🔍 Checking submission status...")
    check_submission_status()

    print("\n" + "="*50)
    check_leaderboard()