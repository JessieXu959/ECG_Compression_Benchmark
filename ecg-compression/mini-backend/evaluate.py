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

# Paths to the scoring components
CODABENCH_DIR = current_dir.parent / "codabench_bundle"
INGESTION_SCRIPT = CODABENCH_DIR / "ingestion.py"
SCORING_SCRIPT = CODABENCH_DIR / "scoring.py"

def setup_evaluation_environment(submission_dir: Path, work_dir: Path) -> Dict[str, Path]:
    """
    Set up the directory structure needed for evaluation
    Similar to Codabench container structure
    """
    # Create directory structure
    input_data_dir = work_dir / "input_data"
    output_dir = work_dir / "output"
    program_dir = work_dir / "program"
    ingested_program_dir = work_dir / "ingested_program"
    ref_dir = work_dir / "input" / "ref"
    res_dir = work_dir / "input" / "res"

    for dir_path in [input_data_dir, output_dir, program_dir, ingested_program_dir, ref_dir, res_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # Copy scoring scripts to program directory
    shutil.copy2(INGESTION_SCRIPT, program_dir / "ingestion.py")
    shutil.copy2(SCORING_SCRIPT, program_dir / "scoring.py")

    # Copy the sample ECG data files (you'll need to provide these)
    sample_data_dir = current_dir / "data"  # Assume sample data is here
    if sample_data_dir.exists():
        for mat_file in sample_data_dir.glob("*.mat"):
            shutil.copy2(mat_file, input_data_dir)
            shutil.copy2(mat_file, ref_dir)  # Reference data for scoring

    # Copy submitted files to ingested_program directory
    for file_path in submission_dir.iterdir():
        if file_path.is_file():
            shutil.copy2(file_path, ingested_program_dir)

    return {
        "input_data": input_data_dir,
        "output": output_dir,
        "program": program_dir,
        "ingested_program": ingested_program_dir,
        "ref": ref_dir,
        "res": res_dir
    }

def run_ingestion(dirs: Dict[str, Path], work_dir: Path) -> Dict[str, Any]:
    """Run the ingestion process"""
    try:
        # Set environment variables for the ingestion script
        env = os.environ.copy()
        env.update({
            "INPUT_DIR": str(dirs["input_data"]),
            "OUTPUT_DIR": str(dirs["output"]),
            "PROGRAM_DIR": str(dirs["program"]),
            "SUBMISSION_DIR": str(dirs["ingested_program"])
        })

        # Update the ingestion script paths dynamically
        ingestion_script_content = (dirs["program"] / "ingestion.py").read_text()
        ingestion_script_content = ingestion_script_content.replace(
            'INPUT_DIR       = "/app/input_data"',
            f'INPUT_DIR       = "{dirs["input_data"]}"'
        ).replace(
            'OUTPUT_DIR = "/app/output"',
            f'OUTPUT_DIR = "{dirs["output"]}"'
        ).replace(
            'PROGRAM_DIR     = "/app/program"',
            f'PROGRAM_DIR     = "{dirs["program"]}"'
        ).replace(
            'SUBMISSION_DIR  = "/app/ingested_program"',
            f'SUBMISSION_DIR  = "{dirs["ingested_program"]}"'
        )

        (dirs["program"] / "ingestion.py").write_text(ingestion_script_content)

        # Run ingestion
        result = subprocess.run(
            [sys.executable, str(dirs["program"] / "ingestion.py")],
            cwd=str(work_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            logger.error(f"Ingestion failed: {result.stderr}")
            return {"success": False, "error": result.stderr}

        # Move output files to res directory for scoring
        output_files = list(dirs["output"].glob("*_pred.mat"))
        for output_file in output_files:
            shutil.copy2(output_file, dirs["res"])

        return {"success": True, "stdout": result.stdout}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Ingestion timed out after 5 minutes"}
    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}")
        return {"success": False, "error": str(e)}

def run_scoring(dirs: Dict[str, Path], work_dir: Path) -> Dict[str, Any]:
    """Run the scoring process"""
    try:
        # Set environment variables for the scoring script
        env = os.environ.copy()
        env.update({
            "INPUT_DIR": str(work_dir / "input"),
            "OUTPUT_DIR": str(dirs["output"])
        })

        # Update the scoring script paths dynamically
        scoring_script_content = (dirs["program"] / "scoring.py").read_text()
        scoring_script_content = scoring_script_content.replace(
            'INPUT_DIR = "/app/input"',
            f'INPUT_DIR = "{work_dir / "input"}"'
        ).replace(
            'OUTPUT_DIR = "/app/output"',
            f'OUTPUT_DIR = "{dirs["output"]}"'
        )

        (dirs["program"] / "scoring.py").write_text(scoring_script_content)

        # Run scoring
        result = subprocess.run(
            [sys.executable, str(dirs["program"] / "scoring.py")],
            cwd=str(work_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            logger.error(f"Scoring failed: {result.stderr}")
            return {"success": False, "error": result.stderr}

        # Read the scores.json file
        scores_file = dirs["output"] / "scores.json"
        if scores_file.exists():
            scores = json.loads(scores_file.read_text())
            return {"success": True, "scores": scores, "stdout": result.stdout}
        else:
            return {"success": False, "error": "scores.json not found"}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Scoring timed out after 5 minutes"}
    except Exception as e:
        logger.error(f"Scoring error: {str(e)}")
        return {"success": False, "error": str(e)}

def extract_zip_file(zip_path: str, extract_to: Path) -> bool:
    """Extract ZIP file to specified directory"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except Exception as e:
        logger.error(f"Failed to extract ZIP file: {str(e)}")
        return False

def evaluate_submission_async(zip_path: str, submission_id: str) -> Dict[str, Any]:
    """
    Full evaluation function that runs the actual ingestion and scoring pipeline
    """
    eval_start_time = time.time()

    try:
        logger.info(f"Starting evaluation for submission {submission_id}")

        # Create temporary working directory
        with tempfile.TemporaryDirectory() as temp_dir:
            work_dir = Path(temp_dir)
            submission_dir = work_dir / "submission"
            submission_dir.mkdir()

            # Extract the submitted ZIP file
            if not extract_zip_file(zip_path, submission_dir):
                return {
                    'status': 'failed',
                    'error': 'Failed to extract submission ZIP file',
                    'score': 0.0,
                    'metrics': {},
                    'evaluation_time': time.time() - eval_start_time
                }

            # Check if required files exist
            required_files = ["ecg_model.py"]  # As specified in ingestion.py
            missing_files = []
            for req_file in required_files:
                if not (submission_dir / req_file).exists():
                    missing_files.append(req_file)

            if missing_files:
                return {
                    'status': 'failed',
                    'error': f'Missing required files: {", ".join(missing_files)}',
                    'score': 0.0,
                    'metrics': {},
                    'evaluation_time': time.time() - eval_start_time
                }

            # Set up evaluation environment
            dirs = setup_evaluation_environment(submission_dir, work_dir)

            # Run ingestion (participant code execution)
            logger.info(f"Running ingestion for {submission_id}")
            ingestion_result = run_ingestion(dirs, work_dir)

            if not ingestion_result["success"]:
                return {
                    'status': 'failed',
                    'error': f'Ingestion failed: {ingestion_result["error"]}',
                    'score': 0.0,
                    'metrics': {},
                    'evaluation_time': time.time() - eval_start_time
                }

            # Run scoring
            logger.info(f"Running scoring for {submission_id}")
            scoring_result = run_scoring(dirs, work_dir)

            if not scoring_result["success"]:
                return {
                    'status': 'failed',
                    'error': f'Scoring failed: {scoring_result["error"]}',
                    'score': 0.0,
                    'metrics': {},
                    'evaluation_time': time.time() - eval_start_time
                }

            # Extract results
            scores = scoring_result["scores"]
            overall_score = scores.get("overall_score", 0.0)

            # Prepare metrics (excluding overall_score from individual metrics)
            metrics = {k: v for k, v in scores.items() if k != "overall_score"}

            logger.info(f"Evaluation completed for {submission_id}. Score: {overall_score}")

            return {
                'status': 'completed',
                'score': float(overall_score),
                'metrics': metrics,
                'evaluation_time': time.time() - eval_start_time
            }

    except Exception as e:
        logger.error(f"Evaluation failed for {submission_id}: {str(e)}")
        logger.error(traceback.format_exc())
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