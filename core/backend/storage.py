#!/usr/bin/env python3
"""
ECG Compression Challenge - Storage Module
Handles data persistence using JSON/CSV files
"""

import json
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import shutil

class StorageManager:
    """Manages data storage for the ECG Compression Challenge"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # File paths
        self.submissions_file = self.data_dir / "submissions.json"
        self.leaderboard_file = self.data_dir / "leaderboard.json"
        self.users_file = self.data_dir / "users.json"
        self.submissions_csv = self.data_dir / "submissions.csv"

        # Initialize files if they don't exist
        self._initialize_files()

    def _initialize_files(self):
        """Initialize storage files if they don't exist"""

        # Initialize submissions.json
        if not self.submissions_file.exists():
            with open(self.submissions_file, 'w') as f:
                json.dump([], f, indent=2)

        # Initialize leaderboard.json
        if not self.leaderboard_file.exists():
            with open(self.leaderboard_file, 'w') as f:
                json.dump([], f, indent=2)

        # Initialize users.json
        if not self.users_file.exists():
            with open(self.users_file, 'w') as f:
                json.dump({}, f, indent=2)

        # Initialize submissions.csv
        if not self.submissions_csv.exists():
            with open(self.submissions_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'submission_id', 'team_name', 'algorithm_name',
                    'submitted_at', 'status', 'score', 'compression_ratio',
                    'reconstruction_error', 'paper_title', 'paper_url'
                ])

    def save_submission(self, submission_data: Dict[str, Any]) -> bool:
        """
        Save submission data to storage

        Args:
            submission_data: Dictionary containing submission information

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing submissions
            submissions = self.load_submissions()

            # Update or add submission
            updated = False
            for i, sub in enumerate(submissions):
                if sub['submission_id'] == submission_data['submission_id']:
                    submissions[i] = submission_data
                    updated = True
                    break

            if not updated:
                submissions.append(submission_data)

            # Save to JSON
            with open(self.submissions_file, 'w') as f:
                json.dump(submissions, f, indent=2, default=str)

            # Save to CSV
            self._save_to_csv(submission_data)

            # Update leaderboard if submission is finished
            if submission_data.get('status') == 'finished' and 'results' in submission_data:
                self._update_leaderboard(submission_data)

            return True

        except Exception as e:
            print(f"Error saving submission: {e}")
            return False

    def _save_to_csv(self, submission_data: Dict[str, Any]):
        """Save submission to CSV file"""
        try:
            # Read existing CSV
            df = pd.read_csv(self.submissions_csv)

            # Prepare row data
            results = submission_data.get('results', {})
            row_data = {
                'submission_id': submission_data['submission_id'],
                'team_name': submission_data['team_name'],
                'algorithm_name': submission_data['algorithm_name'],
                'submitted_at': submission_data['submitted_at'],
                'status': submission_data['status'],
                'score': results.get('score', 0),
                'compression_ratio': results.get('compression_ratio', 0),
                'reconstruction_error': results.get('reconstruction_error', 0),
                'paper_title': submission_data.get('paper_title', ''),
                'paper_url': submission_data.get('paper_url', '')
            }

            # Update or append
            if submission_data['submission_id'] in df['submission_id'].values:
                df.loc[df['submission_id'] == submission_data['submission_id']] = pd.Series(row_data)
            else:
                df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)

            # Save CSV
            df.to_csv(self.submissions_csv, index=False)

        except Exception as e:
            print(f"Error saving to CSV: {e}")

    def load_submissions(self) -> List[Dict[str, Any]]:
        """Load all submissions from storage"""
        try:
            with open(self.submissions_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading submissions: {e}")
            return []

    def get_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific submission by ID"""
        submissions = self.load_submissions()
        for sub in submissions:
            if sub['submission_id'] == submission_id:
                return sub
        return None

    def get_user_submissions(self, team_name: str) -> List[Dict[str, Any]]:
        """Get all submissions for a specific team"""
        submissions = self.load_submissions()
        return [sub for sub in submissions if sub['team_name'] == team_name]

    def _update_leaderboard(self, submission_data: Dict[str, Any]):
        """Update leaderboard with new submission"""
        try:
            leaderboard = self.get_leaderboard()
            results = submission_data.get('results', {})

            # Create leaderboard entry
            entry = {
                'team_name': submission_data['team_name'],
                'algorithm_name': submission_data['algorithm_name'],
                'score': results.get('score', 0),
                'compression_ratio': results.get('compression_ratio', 0),
                'reconstruction_error': results.get('reconstruction_error', 0),
                'submitted_at': submission_data['submitted_at'],
                'submission_id': submission_data['submission_id'],
                'paper_title': submission_data.get('paper_title', ''),
                'paper_url': submission_data.get('paper_url', ''),
                'metrics': results.get('metrics', {})
            }

            # Update existing entry or add new one
            updated = False
            for i, lb_entry in enumerate(leaderboard):
                if lb_entry['team_name'] == submission_data['team_name']:
                    # Keep the best score for each team
                    if entry['score'] > lb_entry['score']:
                        leaderboard[i] = entry
                    updated = True
                    break

            if not updated:
                leaderboard.append(entry)

            # Sort by score (descending)
            leaderboard.sort(key=lambda x: x['score'], reverse=True)

            # Add rank
            for i, entry in enumerate(leaderboard):
                entry['rank'] = i + 1

            # Save leaderboard
            with open(self.leaderboard_file, 'w') as f:
                json.dump(leaderboard, f, indent=2, default=str)

        except Exception as e:
            print(f"Error updating leaderboard: {e}")

    def get_leaderboard(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get current leaderboard"""
        try:
            with open(self.leaderboard_file, 'r') as f:
                leaderboard = json.load(f)
            return leaderboard[:limit]
        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            return []

    def save_user(self, user_data: Dict[str, Any]) -> bool:
        """Save user data"""
        try:
            users = self.load_users()
            users[user_data['team_name']] = user_data

            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2, default=str)

            return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False

    def load_users(self) -> Dict[str, Any]:
        """Load all users"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}

    def get_user(self, team_name: str) -> Optional[Dict[str, Any]]:
        """Get specific user data"""
        users = self.load_users()
        return users.get(team_name)

    def export_data(self, export_dir: str = "export") -> Dict[str, str]:
        """Export all data to a directory"""
        try:
            export_path = Path(export_dir)
            export_path.mkdir(exist_ok=True)

            # Copy all data files
            files_exported = {}

            if self.submissions_file.exists():
                shutil.copy2(self.submissions_file, export_path / "submissions.json")
                files_exported['submissions_json'] = str(export_path / "submissions.json")

            if self.submissions_csv.exists():
                shutil.copy2(self.submissions_csv, export_path / "submissions.csv")
                files_exported['submissions_csv'] = str(export_path / "submissions.csv")

            if self.leaderboard_file.exists():
                shutil.copy2(self.leaderboard_file, export_path / "leaderboard.json")
                files_exported['leaderboard'] = str(export_path / "leaderboard.json")

            if self.users_file.exists():
                shutil.copy2(self.users_file, export_path / "users.json")
                files_exported['users'] = str(export_path / "users.json")

            # Create summary report
            summary = self.generate_summary()
            with open(export_path / "summary.json", 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            files_exported['summary'] = str(export_path / "summary.json")

            return files_exported

        except Exception as e:
            print(f"Error exporting data: {e}")
            return {}

    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        try:
            submissions = self.load_submissions()
            leaderboard = self.get_leaderboard()
            users = self.load_users()

            # Calculate statistics
            total_submissions = len(submissions)
            finished_submissions = len([s for s in submissions if s.get('status') == 'finished'])
            failed_submissions = len([s for s in submissions if s.get('status') == 'failed'])
            running_submissions = len([s for s in submissions if s.get('status') == 'running'])

            # Team statistics
            teams = set(s['team_name'] for s in submissions)
            total_teams = len(teams)

            # Score statistics
            scores = [s.get('results', {}).get('score', 0) for s in submissions
                     if s.get('status') == 'finished']

            summary = {
                'generated_at': datetime.now().isoformat(),
                'total_submissions': total_submissions,
                'finished_submissions': finished_submissions,
                'failed_submissions': failed_submissions,
                'running_submissions': running_submissions,
                'total_teams': total_teams,
                'total_users': len(users),
                'leaderboard_entries': len(leaderboard),
                'score_statistics': {
                    'count': len(scores),
                    'max': max(scores) if scores else 0,
                    'min': min(scores) if scores else 0,
                    'avg': sum(scores) / len(scores) if scores else 0
                }
            }

            return summary

        except Exception as e:
            print(f"Error generating summary: {e}")
            return {}

    def backup_data(self, backup_dir: str = None) -> str:
        """Create a backup of all data"""
        try:
            if backup_dir is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = f"backup_{timestamp}"

            backup_path = Path(backup_dir)
            backup_path.mkdir(exist_ok=True)

            # Copy entire data directory
            if self.data_dir.exists():
                shutil.copytree(self.data_dir, backup_path / "data", dirs_exist_ok=True)

            return str(backup_path)

        except Exception as e:
            print(f"Error creating backup: {e}")
            return ""

if __name__ == "__main__":
    # Test the storage manager
    storage = StorageManager()

    # Test submission
    test_submission = {
        'submission_id': 'test_123',
        'team_name': 'TestTeam',
        'algorithm_name': 'TestAlgorithm',
        'submitted_at': datetime.now().isoformat(),
        'status': 'finished',
        'results': {
            'score': 85.5,
            'compression_ratio': 12.3,
            'reconstruction_error': 0.05
        }
    }

    # Save and retrieve
    storage.save_submission(test_submission)
    retrieved = storage.get_submission('test_123')
    print("Retrieved submission:", retrieved)

    # Test leaderboard
    leaderboard = storage.get_leaderboard()
    print("Leaderboard:", leaderboard)

    # Generate summary
    summary = storage.generate_summary()
    print("Summary:", json.dumps(summary, indent=2))