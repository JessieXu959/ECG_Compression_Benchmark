
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
