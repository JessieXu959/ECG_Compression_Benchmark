#!/usr/bin/env python3
"""
Script to check and clear frontend cache data
"""
import requests
import json

# Configuration
API_BASE = "http://localhost:8000"

def check_current_state():
    print("🔍 Checking current backend state...")

    # Check health
    health_response = requests.get(f"{API_BASE}/health")
    if health_response.status_code == 200:
        health_data = health_response.json()
        print(f"✅ Backend health:")
        print(f"   - Active users: {health_data.get('active_users', 0)}")
        print(f"   - Total submissions: {health_data.get('total_submissions', 0)}")

    # Check leaderboard
    leaderboard_response = requests.get(f"{API_BASE}/api/leaderboard")
    if leaderboard_response.status_code == 200:
        leaderboard_data = leaderboard_response.json()
        print(f"📊 Current leaderboard:")
        results = leaderboard_data.get("results", [])
        if results:
            for i, entry in enumerate(results, 1):
                print(f"   {i}. {entry['participant_name']}: {entry['score']} points")
        else:
            print("   - Empty (no submissions)")

    return len(results) if 'results' in locals() else 0

def generate_frontend_cache_clear():
    """Generate JavaScript code to clear frontend cache"""

    cache_clear_js = """
// Clear all localStorage data related to ECG Compression Challenge
console.log('🧹 Clearing ECG Compression Challenge cache...');

// Clear all keys that might contain cached data
const keysToRemove = [];
for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && (
        key.includes('personalSubmissions_') ||
        key.includes('leaderboardData') ||
        key.includes('submissionHistory') ||
        key.includes('userToken') ||
        key.includes('ecgCompression')
    )) {
        keysToRemove.push(key);
    }
}

keysToRemove.forEach(key => {
    localStorage.removeItem(key);
    console.log(`Removed: ${key}`);
});

console.log(`✅ Cleared ${keysToRemove.length} cache entries`);

// Also clear sessionStorage
sessionStorage.clear();
console.log('✅ Cleared session storage');

// Force refresh
location.reload();
"""

    with open("clear_frontend_cache.js", "w", encoding="utf-8") as f:
        f.write(cache_clear_js)

    print("📄 Created frontend cache clearing script: clear_frontend_cache.js")

def main():
    print("🔍 Frontend Cache Check & Clear")
    print("=" * 50)

    entry_count = check_current_state()

    if entry_count == 0:
        print("\n✅ Backend is clean (no leaderboard entries)")
        print("🤔 If you're still seeing demo data on the frontend, it's cached data.")

        generate_frontend_cache_clear()

        print("\n📝 To clear frontend cache:")
        print("1. Open the frontend in your browser (http://localhost:3000)")
        print("2. Open browser Developer Tools (F12)")
        print("3. Go to Console tab")
        print("4. Copy and paste the contents of 'clear_frontend_cache.js'")
        print("5. Press Enter to execute")
        print("6. The page will refresh with clean data")

        print("\n🔄 Alternative method:")
        print("1. In browser, press Ctrl+Shift+R (hard refresh)")
        print("2. Or go to Developer Tools > Application > Storage > Clear storage")

    else:
        print(f"\n⚠️  Backend still has {entry_count} entries")
        print("Running cleanup endpoint...")

        cleanup_response = requests.post(f"{API_BASE}/api/admin/clear-demo-data")
        if cleanup_response.status_code == 200:
            result = cleanup_response.json()
            print(f"✅ Cleanup result: {result['message']}")
            check_current_state()
        else:
            print("❌ Failed to clear backend data")

if __name__ == "__main__":
    main()