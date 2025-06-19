"""
Storage layer for ECG Compression Backend
Supports multiple storage backends: CSV, TinyDB, SQLite
"""

import os
import json
import csv
import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

# Configuration
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "csv")  # "csv", "tinydb", or "sqlite"
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# File paths
USERS_FILE = DATA_DIR / "users.csv"
SUBMISSIONS_FILE = DATA_DIR / "submissions.csv"
LEADERBOARD_FILE = DATA_DIR / "leaderboard.csv"

class StorageManager:
    """Unified storage interface supporting multiple backends"""

    def __init__(self, storage_type: str = "csv"):
        self.storage_type = storage_type
        self._ensure_storage()

    def _ensure_storage(self):
        """Initialize storage files/tables"""
        if self.storage_type == "csv":
            self._ensure_csv_files()
        elif self.storage_type == "sqlite":
            self._ensure_sqlite_tables()
        elif self.storage_type == "tinydb":
            # TinyDB files are created automatically
            pass

    def _ensure_csv_files(self):
        """Create CSV files with headers if they don't exist"""
        # Users CSV
        if not USERS_FILE.exists():
            with open(USERS_FILE, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'teamName', 'email', 'password', 'registeredDate',
                    'totalSubmissions', 'bestScore'
                ])
                writer.writeheader()

        # Submissions CSV
        if not SUBMISSIONS_FILE.exists():
            with open(SUBMISSIONS_FILE, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'teamName', 'algorithmName', 'fileName', 'timestamp',
                    'status', 'score', 'metrics', 'filePath', 'fileHash',
                    'paperTitle', 'paperAuthors', 'paperType', 'paperDOI', 'evaluationTime'
                ])
                writer.writeheader()

# Storage functions for users
def save_user(team_name: str, user_data: Dict[str, Any]):
    """Save user data"""
    storage = StorageManager(STORAGE_TYPE)

    if storage.storage_type == "csv":
        # Read existing users to check for updates vs inserts
        users = []
        if USERS_FILE.exists():
            with open(USERS_FILE, 'r') as f:
                users = list(csv.DictReader(f))

        # Update existing or add new user
        user_exists = False
        for i, user in enumerate(users):
            if user['teamName'] == team_name:
                users[i] = user_data
                user_exists = True
                break

        if not user_exists:
            users.append(user_data)

        # Write back to file
        with open(USERS_FILE, 'w', newline='') as f:
            if users:
                writer = csv.DictWriter(f, fieldnames=users[0].keys())
                writer.writeheader()
                writer.writerows(users)

def get_user(team_name: str) -> Optional[Dict[str, Any]]:
    """Get user data by team name"""
    storage = StorageManager(STORAGE_TYPE)

    if storage.storage_type == "csv":
        if not USERS_FILE.exists():
            return None

        with open(USERS_FILE, 'r') as f:
            for user in csv.DictReader(f):
                if user['teamName'] == team_name:
                    return user
        return None

def get_all_users() -> List[Dict[str, Any]]:
    """Get all users data"""
    storage = StorageManager(STORAGE_TYPE)

    if storage.storage_type == "csv":
        if not USERS_FILE.exists():
            return []

        users = []
        with open(USERS_FILE, 'r') as f:
            for user in csv.DictReader(f):
                # Remove password for security
                user_safe = user.copy()
                if 'password' in user_safe:
                    del user_safe['password']
                users.append(user_safe)
        return users

    return []

# Storage functions for submissions
def save_submission(submission_id: str, submission_data: Dict[str, Any]):
    """Save submission data"""
    storage = StorageManager(STORAGE_TYPE)

    if storage.storage_type == "csv":
        # Convert metrics dict to JSON string for CSV storage
        submission_data_copy = submission_data.copy()
        if 'metrics' in submission_data_copy:
            submission_data_copy['metrics'] = json.dumps(submission_data_copy['metrics'])

        with open(SUBMISSIONS_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'teamName', 'algorithmName', 'fileName', 'timestamp',
                'status', 'score', 'metrics', 'filePath', 'fileHash',
                'paperTitle', 'paperAuthors', 'paperType', 'paperDOI', 'evaluationTime'
            ])
            writer.writerow(submission_data_copy)

def get_submissions() -> List[Dict[str, Any]]:
    """Get all submissions"""
    storage = StorageManager(STORAGE_TYPE)

    if storage.storage_type == "csv":
        if not SUBMISSIONS_FILE.exists():
            return []

        submissions = []
        with open(SUBMISSIONS_FILE, 'r') as f:
            for submission in csv.DictReader(f):
                # Parse JSON metrics back to dict
                if 'metrics' in submission and submission['metrics']:
                    try:
                        submission['metrics'] = json.loads(submission['metrics'])
                    except json.JSONDecodeError:
                        submission['metrics'] = {}
                submissions.append(submission)
        return submissions

def update_submission_status(submission_id: str, status: str, update_data: Dict[str, Any] = None):
    """Update submission status and optional additional data"""
    storage = StorageManager(STORAGE_TYPE)

    if storage.storage_type == "csv":
        # Read all submissions
        submissions = []
        if SUBMISSIONS_FILE.exists():
            with open(SUBMISSIONS_FILE, 'r') as f:
                submissions = list(csv.DictReader(f))

        # Update the specific submission
        for i, submission in enumerate(submissions):
            if submission['id'] == submission_id:
                submissions[i]['status'] = status
                if update_data:
                    for key, value in update_data.items():
                        if key == 'metrics':
                            submissions[i][key] = json.dumps(value)
                        else:
                            submissions[i][key] = value
                break

        # Write back to file
        if submissions:
            with open(SUBMISSIONS_FILE, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=submissions[0].keys())
                writer.writeheader()
                writer.writerows(submissions)

def get_user_submissions(team_name: str) -> List[Dict[str, Any]]:
    """Get submissions for a specific user"""
    all_submissions = get_submissions()
    return [s for s in all_submissions if s.get('teamName') == team_name]

def get_leaderboard(limit: int = 50) -> List[Dict[str, Any]]:
    """Get leaderboard data sorted by best score"""
    submissions = get_submissions()

    # Group by team and get best submission for each
    team_best = {}
    for submission in submissions:
        if submission.get('status') != 'completed':
            continue

        team_name = submission.get('teamName')
        score = float(submission.get('score', 0))

        if team_name not in team_best or score > team_best[team_name]['score']:
            team_best[team_name] = {
                'participant_name': team_name,
                'score': score,
                'scores': {
                    'Score': score,
                    'CR': submission.get('metrics', {}).get('CR', 0),
                    'PRD': submission.get('metrics', {}).get('PRD', 0)
                },
                'submission_date': submission.get('timestamp', ''),
                'algorithm_name': submission.get('algorithmName', '')
            }

    # Sort by score descending
    leaderboard = list(team_best.values())
    leaderboard.sort(key=lambda x: x['score'], reverse=True)

    return leaderboard[:limit]

def delete_user_data(team_name: str):
    """Delete all data for a user"""
    storage = StorageManager(STORAGE_TYPE)

    if storage.storage_type == "csv":
        # Remove user from users file
        users = []
        if USERS_FILE.exists():
            with open(USERS_FILE, 'r') as f:
                users = [user for user in csv.DictReader(f) if user['teamName'] != team_name]

            with open(USERS_FILE, 'w', newline='') as f:
                if users:
                    writer = csv.DictWriter(f, fieldnames=users[0].keys())
                    writer.writeheader()
                    writer.writerows(users)

        # Remove user submissions
        submissions = []
        if SUBMISSIONS_FILE.exists():
            with open(SUBMISSIONS_FILE, 'r') as f:
                submissions = [sub for sub in csv.DictReader(f) if sub['teamName'] != team_name]

            with open(SUBMISSIONS_FILE, 'w', newline='') as f:
                if submissions:
                    writer = csv.DictWriter(f, fieldnames=submissions[0].keys())
                    writer.writeheader()
                    writer.writerows(submissions)