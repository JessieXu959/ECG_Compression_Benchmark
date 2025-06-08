"""
Evaluation module for ECG Compression Challenge
Handles file extraction, processing, and scoring using Codabench ingestion/scoring logic
"""

import os
import sys
import json
import shutil
import tempfile
import zipfile
import logging
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import subprocess
import time

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def evaluate_submission_async(zip_path: str, submission_id: str) -> Dict[str, Any]:
    """
    Simplified evaluation function that returns a mock score for now
    In a full implementation, this would extract and run the user's algorithm
    """
    eval_start_time = time.time()

    try:
        logger.info(f"Starting evaluation for submission {submission_id}")

        # For now, return a mock successful result
        # In the future, this would:
        # 1. Extract the ZIP file
        # 2. Validate the submission structure
        # 3. Run the ingestion process
        # 4. Run the scoring process
        # 5. Return the actual results

        # Simulate some processing time
        time.sleep(2)

        # Generate mock scores
        import random
        mock_cr = round(random.uniform(30, 50), 1)
        mock_prd = round(random.uniform(0.001, 0.01), 4)
        mock_score = round(100 - (mock_prd * 1000) + (mock_cr * 0.5), 1)

        logger.info(f"Evaluation completed for {submission_id}. Score: {mock_score}")

        return {
            'status': 'completed',
            'score': mock_score,
            'metrics': {
                'CR': mock_cr,
                'PRD': mock_prd,
                'Score': mock_score
            },
            'evaluation_time': time.time() - eval_start_time
        }

    except Exception as e:
        logger.error(f"Evaluation failed for {submission_id}: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e),
            'score': 0.0,
            'metrics': {},
            'evaluation_time': time.time() - eval_start_time
        }


# Test function for development
def main():
    """Test function for development"""
    if len(sys.argv) != 3:
        print("Usage: python evaluate.py <zip_path> <submission_id>")
        sys.exit(1)

    zip_path = sys.argv[1]
    submission_id = sys.argv[2]

    result = evaluate_submission_async(zip_path, submission_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()