#!/usr/bin/env python3
"""
Script to clear demo data from the ECG Compression Challenge backend
Only keeps legitimate user account: teamA
"""
import requests
import json

# Configuration
API_BASE = "http://localhost:8000"

# Teams to keep (real user accounts)
REAL_TEAMS = ["teamA"]

def clear_demo_data():
    """Clear demo data by directly accessing the backend API"""

    print("🧹 Starting demo data cleanup...")

    # First, get the current leaderboard to see what needs to be cleared
    response = requests.get(f"{API_BASE}/api/leaderboard")
    if response.status_code == 200:
        leaderboard = response.json()["results"]
        print(f"📊 Current leaderboard has {len(leaderboard)} entries:")
        for entry in leaderboard:
            team_name = entry["participant_name"]
            score = entry["score"]
            status = "✅ KEEP" if team_name in REAL_TEAMS else "❌ DELETE"
            print(f"   - {team_name}: {score} points [{status}]")

    # Since we can't directly delete from the in-memory database,
    # we'll create a new script to restart with clean data
    print("\n🔧 Creating clean backend script...")

    return leaderboard

def create_clean_backend():
    """Create a clean version of the backend without demo data"""

    # Read the current main.py
    with open("mini-backend/main.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Create a backup
    with open("mini-backend/main_backup.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Created backup: mini-backend/main_backup.py")

    # Add a data cleanup function to the backend
    cleanup_code = '''
# Data cleanup function (add this after the database definitions)
def clear_demo_data():
    """Clear demo data keeping only real user accounts"""
    real_teams = ["teamA"]

    # Clear demo submissions
    to_remove = []
    for sub_id, sub in submissions_db.items():
        if sub.get("teamName") not in real_teams:
            to_remove.append(sub_id)

    for sub_id in to_remove:
        del submissions_db[sub_id]

    # Clear demo users
    to_remove = []
    for team_name in users_db.keys():
        if team_name not in real_teams:
            to_remove.append(team_name)

    for team_name in to_remove:
        del users_db[team_name]

    print(f"🧹 Cleared demo data. Keeping {len(real_teams)} real teams.")
    return len(to_remove)

# Add cleanup endpoint
@app.post("/api/admin/clear-demo-data")
async def clear_demo_data_endpoint():
    """Admin endpoint to clear demo data"""
    removed_count = clear_demo_data()
    return {
        "status": "success",
        "message": f"Cleared {removed_count} demo entries",
        "real_teams_kept": ["teamA"]
    }
'''

    # Find where to insert the cleanup code (after database definitions)
    db_line = content.find("submissions_db = {}")
    if db_line != -1:
        # Find the end of that line
        next_line = content.find("\n", db_line) + 1
        # Insert cleanup code
        new_content = content[:next_line] + cleanup_code + content[next_line:]

        # Write the modified content
        with open("mini-backend/main_clean.py", "w", encoding="utf-8") as f:
            f.write(new_content)

        print("✅ Created clean backend: mini-backend/main_clean.py")
        print("📝 Added admin endpoint: POST /api/admin/clear-demo-data")
        return True

    return False

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy")
            print(f"   - Active users: {data.get('active_users', 0)}")
            print(f"   - Total submissions: {data.get('total_submissions', 0)}")
            return True
    except:
        print("❌ Backend is not running")
        return False

def main():
    """Main function"""
    print("🚀 ECG Compression Challenge - Demo Data Cleanup")
    print("=" * 50)

    # Test backend health
    if not test_backend_health():
        print("\n⚠️  Please start the backend first:")
        print("   cd mini-backend && python main.py")
        return

    # Show current data
    current_data = clear_demo_data()

    # Create clean backend
    if create_clean_backend():
        print("\n🎯 Next steps:")
        print("1. Stop the current backend (Ctrl+C)")
        print("2. Start the clean backend:")
        print("   cd mini-backend && python main_clean.py")
        print("3. Call the cleanup endpoint:")
        print("   curl -X POST http://localhost:8000/api/admin/clear-demo-data")
        print("4. Verify the leaderboard is clean")
    else:
        print("❌ Failed to create clean backend")

if __name__ == "__main__":
    main()