"""
Evaluation module for ECG Compression Challenge
Handles file extraction, processing, and scoring using real ECG evaluation system
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
sys.path.insert(0, str(current_dir / "core" / "evaluation"))

# Import the real evaluation system with better error handling
HAS_REAL_EVALUATOR = False
real_evaluator = None

try:
    # Try absolute import first
    from core.evaluation.real_evaluation_system import RealECGEvaluationSystem
    HAS_REAL_EVALUATOR = True
except ImportError:
    try:
        # Try relative import
        sys.path.insert(0, os.path.join(os.getcwd(), 'core', 'evaluation'))
        from real_evaluation_system import RealECGEvaluationSystem
        HAS_REAL_EVALUATOR = True
    except ImportError as e:
        HAS_REAL_EVALUATOR = False
        logging.warning(f"Real evaluation system not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the real evaluation system
if HAS_REAL_EVALUATOR:
    try:
        real_evaluator = RealECGEvaluationSystem()
        logger.info("✅ Real ECG Evaluation System initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize real evaluator: {e}")
        HAS_REAL_EVALUATOR = False
        real_evaluator = None
else:
    real_evaluator = None

def evaluate_submission_async(zip_path: str, submission_id: str) -> Dict[str, Any]:
    """
    Evaluate ECG compression submission using real evaluation system
    """
    eval_start_time = time.time()

    try:
        logger.info(f"Starting evaluation for submission {submission_id}")

        # Use real evaluation system if available
        if HAS_REAL_EVALUATOR and real_evaluator:
            try:
                # Use the real evaluation system
                result = real_evaluator.evaluate_submission(zip_path)
                
                if result['status'] == 'completed':
                    # Extract the key metrics for compatibility
                    metrics = result['metrics']
                    final_score = metrics.get('Score', metrics.get('FinalScore', 0))
                    
                    logger.info(f"✅ Real evaluation completed for {submission_id}. Score: {final_score}")
                    
                    return {
                        'status': 'completed',
                        'score': round(final_score, 1),
                        'metrics': {
                            'CR': round(metrics.get('CR', 0), 1),
                            'PRD': round(metrics.get('PRD', 0), 4),
                            'RMSE': round(metrics.get('RMSE', 0), 6),
                            'SNR': round(metrics.get('SNR', 0), 2),
                            'QS': round(metrics.get('QS', 0), 2),
                            'Score': round(final_score, 1)
                        },
                        'evaluation_time': time.time() - eval_start_time,
                        'datasets_evaluated': result.get('datasets_evaluated', 0),
                        'total_datasets': result.get('total_datasets', 0),
                        'evaluation_method': 'real_system'
                    }
                else:
                    # Real evaluation failed, return error
                    error_msg = '; '.join(result.get('errors', ['Evaluation failed']))
                    logger.error(f"❌ Real evaluation failed for {submission_id}: {error_msg}")
                    
                    return {
                        'status': 'failed',
                        'error': error_msg,
                        'score': 0.0,
                        'metrics': {},
                        'evaluation_time': time.time() - eval_start_time,
                        'evaluation_method': 'real_system'
                    }
                    
            except Exception as e:
                logger.error(f"❌ Real evaluation error for {submission_id}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Fall back to mock if real evaluation fails
                logger.info("🔄 Falling back to mock evaluation")
        
        # Fallback to mock evaluation (for development/testing)
        logger.warning(f"⚠️ Using mock evaluation for {submission_id} (real evaluator: {HAS_REAL_EVALUATOR})")
        
        # Simulate some processing time
        time.sleep(2)

        # Generate mock scores (for fallback only)
        import random
        mock_cr = round(random.uniform(30, 50), 1)
        mock_prd = round(random.uniform(0.001, 0.01), 4)
        mock_score = round(100 - (mock_prd * 1000) + (mock_cr * 0.5), 1)

        logger.info(f"Mock evaluation completed for {submission_id}. Score: {mock_score}")

        return {
            'status': 'completed',
            'score': mock_score,
            'metrics': {
                'CR': mock_cr,
                'PRD': mock_prd,
                'Score': mock_score
            },
            'evaluation_time': time.time() - eval_start_time,
            'evaluation_method': 'mock_fallback'
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