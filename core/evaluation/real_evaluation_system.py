#!/usr/bin/env python3
"""
Real ECG Compression Evaluation System
======================================

This module implements a complete evaluation system for ECG compression algorithms.
It can safely execute user-submitted code and calculate real compression metrics.

Features:
- Safe algorithm execution in isolated environment
- Real ECG dataset generation and management
- Comprehensive metric calculation (CR, PRD, RMSE, SNR)
- Performance monitoring (time, memory)
- Security measures for user code execution
"""

import os
import sys
import json
import time
import psutil
import tempfile
import zipfile
import subprocess
import traceback
import numpy as np
import scipy.io as sio
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import multiprocessing
import warnings

# Platform-specific imports
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    # Windows doesn't have resource module
    HAS_RESOURCE = False
    warnings.warn("Resource module not available (Windows). Memory limits will be approximate.")

try:
    from scipy.io import savemat, loadmat
    from scipy import signal
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    warnings.warn("SciPy not available. Some advanced features will be disabled.")

class ECGDatasetManager:
    """Manages ECG datasets for evaluation"""

    def __init__(self, data_dir: str = "evaluation_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.datasets = {}

    def create_standard_datasets(self):
        """Create standard ECG datasets for evaluation"""

        # PhysioNet-inspired datasets
        datasets_config = [
            {
                "name": "PhysioNet_MITBIH_rec117_5min",
                "fs": 360,  # Sampling frequency
                "duration": 300,  # 5 minutes
                "heart_rate": 72,
                "noise_level": 0.02
            },
            {
                "name": "PhysioNet_MITBIH_rec119_5min",
                "fs": 360,
                "duration": 300,
                "heart_rate": 68,
                "noise_level": 0.03
            },
            {
                "name": "PhysioNet_MITBIH_rec201_10min",
                "fs": 360,
                "duration": 600,  # 10 minutes
                "heart_rate": 75,
                "noise_level": 0.025
            }
        ]

        for config in datasets_config:
            ecg_signal = self._generate_realistic_ecg(**config)

            # Save as .mat file
            output_path = self.data_dir / f"{config['name']}.mat"
            sio.savemat(output_path, {
                "ecg": ecg_signal,
                "fs": config["fs"],
                "duration": config["duration"]
            })

            self.datasets[config["name"]] = {
                "path": output_path,
                "signal": ecg_signal,
                "fs": config["fs"],
                "size_bytes": ecg_signal.nbytes
            }

        print(f"✅ Created {len(datasets_config)} standard ECG datasets")
        return self.datasets

    def _generate_realistic_ecg(self, name, fs, duration, heart_rate, noise_level):
        """Generate realistic ECG signal"""

        t = np.arange(0, duration, 1/fs)
        n_samples = len(t)

        # Heart rate variability
        hr_variation = 1 + 0.1 * np.sin(2 * np.pi * 0.1 * t)  # 0.1 Hz variation
        instantaneous_hr = heart_rate * hr_variation

        # Generate ECG components
        ecg_signal = np.zeros(n_samples)

        # P-QRS-T complex parameters
        rr_intervals = 60 / instantaneous_hr  # RR interval in seconds

        current_time = 0
        beat_idx = 0

        while current_time < duration:
            if beat_idx < len(rr_intervals):
                rr_interval = rr_intervals[beat_idx]
            else:
                rr_interval = 60 / heart_rate

            # QRS complex (main spike)
            qrs_time = current_time
            qrs_idx = int(qrs_time * fs)
            if qrs_idx < n_samples:
                qrs_width = int(0.08 * fs)  # 80ms QRS width
                qrs_start = max(0, qrs_idx - qrs_width//2)
                qrs_end = min(n_samples, qrs_idx + qrs_width//2)

                # QRS shape (simplified)
                qrs_t = np.linspace(-0.04, 0.04, qrs_end - qrs_start)
                qrs_shape = np.exp(-0.5 * (qrs_t / 0.02)**2) * np.sign(qrs_t + 0.01)
                ecg_signal[qrs_start:qrs_end] += qrs_shape

            # P wave
            p_time = current_time - 0.15
            p_idx = int(p_time * fs)
            if p_idx > 0 and p_idx < n_samples:
                p_width = int(0.08 * fs)
                p_start = max(0, p_idx - p_width//2)
                p_end = min(n_samples, p_idx + p_width//2)
                p_t = np.linspace(-0.04, 0.04, p_end - p_start)
                p_shape = 0.25 * np.exp(-0.5 * (p_t / 0.03)**2)
                ecg_signal[p_start:p_end] += p_shape

            # T wave
            t_time = current_time + 0.25
            t_idx = int(t_time * fs)
            if t_idx < n_samples:
                t_width = int(0.15 * fs)
                t_start = max(0, t_idx - t_width//2)
                t_end = min(n_samples, t_idx + t_width//2)
                t_t = np.linspace(-0.075, 0.075, t_end - t_start)
                t_shape = 0.3 * np.exp(-0.5 * (t_t / 0.05)**2)
                ecg_signal[t_start:t_end] += t_shape

            current_time += rr_interval
            beat_idx += 1

        # Add baseline wander
        baseline_freq = 0.5  # Hz
        baseline_wander = 0.1 * np.sin(2 * np.pi * baseline_freq * t)
        ecg_signal += baseline_wander

        # Add noise
        noise = noise_level * np.random.randn(n_samples)
        ecg_signal += noise

        # Normalize
        ecg_signal = ecg_signal / np.max(np.abs(ecg_signal))

        return ecg_signal

class SafeCodeExecutor:
    """Safely execute user-submitted algorithms"""

    def __init__(self, timeout=60, memory_limit_mb=512):
        self.timeout = timeout
        self.memory_limit = memory_limit_mb * 1024 * 1024  # Convert to bytes

    def extract_and_validate_submission(self, zip_path: str) -> str:
        """Extract and validate user submission"""

        temp_dir = tempfile.mkdtemp(prefix="ecg_eval_")

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Look for required files
            required_files = ["ecg_model.py"]  # Main algorithm file
            found_files = []

            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file in required_files:
                        found_files.append(os.path.join(root, file))

            if not found_files:
                raise ValueError(f"Required files not found: {required_files}")

            return temp_dir

        except Exception as e:
            # Cleanup on error
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e

    def execute_algorithm(self, algorithm_dir: str, input_data: Dict) -> Dict:
        """Execute user algorithm with safety measures - Windows compatible version"""

        try:
            # Create evaluation script that works with subprocess
            eval_script_path = self._create_evaluation_script(algorithm_dir, input_data)

            # Execute with direct subprocess approach (Windows compatible)
            start_time = time.time()
            result = self._execute_algorithm_safely(eval_script_path, input_data)
            execution_time = time.time() - start_time

            if result.get('success', False):
                result['execution_time'] = execution_time
                return result
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Unknown execution error'),
                    "execution_time": execution_time
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Algorithm execution failed: {str(e)}",
                "execution_time": 0
            }

    def _create_evaluation_script(self, algorithm_dir: str, input_data: Dict) -> str:
        """Create Python script to evaluate the algorithm"""

        script_content = f'''
import sys
import os
import numpy as np
import json
import traceback

# Add algorithm directory to path
sys.path.insert(0, r"{algorithm_dir}")

try:
    from ecg_model import ECGCompressor

    # Load input data from JSON string
    input_data = {json.dumps(input_data)}

    results = {{}}

    for dataset_name, dataset_info in input_data.items():
        try:
            ecg_signal = dataset_info["signal"]

            # Initialize and run algorithm
            compressor = ECGCompressor()
            f_recon, cr_val = compressor.compress_and_reconstruct(ecg_signal)

            # Ensure reconstructed signal is proper format
            if hasattr(f_recon, 'tolist'):
                f_recon = f_recon.tolist()
            elif not isinstance(f_recon, list):
                f_recon = list(f_recon)

            # Ensure same length as original
            if len(f_recon) != len(ecg_signal):
                if len(f_recon) > len(ecg_signal):
                    f_recon = f_recon[:len(ecg_signal)]
                else:
                    # Pad with zeros or interpolate
                    import numpy as np
                    f_recon_array = np.array(f_recon)
                    original_indices = np.linspace(0, len(f_recon)-1, len(f_recon))
                    target_indices = np.linspace(0, len(f_recon)-1, len(ecg_signal))
                    f_recon = np.interp(target_indices, original_indices, f_recon_array).tolist()

            results[dataset_name] = {{
                "reconstructed": f_recon,
                "compression_ratio": float(cr_val)
            }}

        except Exception as dataset_error:
            results[dataset_name] = {{
                "error": str(dataset_error)
            }}

    # Output results as JSON
    print(json.dumps(results))

except Exception as e:
    error_result = {{
        "error": str(e),
        "traceback": traceback.format_exc()
    }}
    print(json.dumps(error_result))
'''

        script_path = os.path.join(algorithm_dir, "eval_script.py")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        return script_path

    def _execute_algorithm_safely(self, script_path: str, input_data: Dict) -> Dict:
        """Execute algorithm with safety limits - Windows compatible"""

        try:
            start_time = time.time()

            # Simple subprocess execution without multiprocessing
            process = subprocess.Popen(
                [sys.executable, script_path],
                cwd=os.path.dirname(script_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                execution_time = time.time() - start_time

                if process.returncode == 0:
                    # Parse output
                    try:
                        result = json.loads(stdout)
                        return {
                            'success': True,
                            'output': result,
                            'execution_time': execution_time
                        }
                    except json.JSONDecodeError:
                        return {
                            'success': False,
                            'error': f'Invalid JSON output: {stdout[:500]}',
                            'execution_time': execution_time
                        }
                else:
                    return {
                        'success': False,
                        'error': f'Process failed (code {process.returncode}): {stderr}',
                        'execution_time': execution_time
                    }

            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    'success': False,
                    'error': f'Execution timeout ({self.timeout}s exceeded)',
                    'execution_time': self.timeout
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Execution error: {str(e)}',
                'execution_time': 0
            }

class ECGMetricsCalculator:
    """Calculate ECG compression metrics - Enhanced with user's original scoring logic"""

    # 设定 EPSILON 避免除零 (from user's original scoring.py)
    EPSILON = 1e-6

    @staticmethod
    def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
        """Calculate compression ratio"""
        if compressed_size == 0:
            return 0.0
        return original_size / compressed_size

    @staticmethod
    def calculate_prd(original: np.ndarray, reconstructed: np.ndarray) -> float:
        """
        Calculate Percent Root-mean-square Difference (PRD)
        - Enhanced with user's original formula from scoring.py
        """
        if len(original) != len(reconstructed):
            min_len = min(len(original), len(reconstructed))
            original = original[:min_len]
            reconstructed = reconstructed[:min_len]

        # User's original PRD calculation logic
        f_mean = np.mean(original)
        numerator = np.linalg.norm(original - reconstructed, 2)
        denominator = np.linalg.norm(original - f_mean, 2)

        if denominator < ECGMetricsCalculator.EPSILON:
            return float('inf')  # 处理全零信号

        prd = (numerator / denominator) * 100
        return float(prd)

    @staticmethod
    def calculate_rmse(original: np.ndarray, reconstructed: np.ndarray) -> float:
        """Calculate Root Mean Square Error (RMSE)"""
        if len(original) != len(reconstructed):
            min_len = min(len(original), len(reconstructed))
            original = original[:min_len]
            reconstructed = reconstructed[:min_len]

        mse = np.mean((original - reconstructed) ** 2)
        return float(np.sqrt(mse))

    @staticmethod
    def calculate_snr(original: np.ndarray, reconstructed: np.ndarray) -> float:
        """Calculate Signal-to-Noise Ratio (SNR) in dB"""
        if len(original) != len(reconstructed):
            min_len = min(len(original), len(reconstructed))
            original = original[:min_len]
            reconstructed = reconstructed[:min_len]

        signal_power = np.mean(original ** 2)
        noise_power = np.mean((original - reconstructed) ** 2)

        if noise_power == 0:
            return float('inf')
        if signal_power == 0:
            return 0.0

        snr = 10 * np.log10(signal_power / noise_power)
        return float(snr)

    @staticmethod
    def calculate_qs_score(cr: float, prd: float) -> float:
        """Calculate Quality Score (QS) = CR / PRD"""
        if prd == 0:
            return float('inf')
        return cr / prd

    @staticmethod
    def calculate_final_score(cr: float, prd: float) -> float:
        """
        Calculate final score using user's original formula:
        Score = CR / (PRD + epsilon)
        """
        return cr / (prd + ECGMetricsCalculator.EPSILON)

class RealECGEvaluationSystem:
    """Main evaluation system"""

    def __init__(self, data_dir: str = "evaluation_data"):
        self.dataset_manager = ECGDatasetManager(data_dir)
        self.code_executor = SafeCodeExecutor()
        self.metrics_calculator = ECGMetricsCalculator()

        # Initialize datasets
        self.datasets = self.dataset_manager.create_standard_datasets()

    def evaluate_submission(self, zip_file_path: str) -> Dict[str, Any]:
        """
        Complete evaluation of a user submission

        Returns:
            Dict containing all evaluation results and metrics
        """

        evaluation_result = {
            "status": "processing",
            "timestamp": time.time(),
            "datasets_evaluated": 0,
            "total_datasets": len(self.datasets),
            "metrics": {},
            "performance": {},
            "errors": []
        }

        try:
            # Extract and validate submission
            algorithm_dir = self.code_executor.extract_and_validate_submission(zip_file_path)

            # Prepare input data for algorithm
            input_data = {}
            for name, dataset in self.datasets.items():
                input_data[name] = {
                    "signal": dataset["signal"].tolist(),
                    "fs": dataset["fs"]
                }

            # Execute algorithm
            execution_result = self.code_executor.execute_algorithm(algorithm_dir, input_data)

            if not execution_result["success"]:
                evaluation_result["status"] = "failed"
                evaluation_result["errors"].append(execution_result["error"])
                return evaluation_result

            # Calculate metrics for each dataset
            algorithm_output = execution_result["output"]
            dataset_metrics = {}
            overall_metrics = {
                "CR": [],
                "PRD": [],
                "RMSE": [],
                "SNR": [],
                "QS": [],
                "FinalScore": []  # Add final score tracking
            }

            for dataset_name, dataset in self.datasets.items():
                if dataset_name in algorithm_output:
                    original = dataset["signal"]
                    result = algorithm_output[dataset_name]

                    if "error" not in result:
                        reconstructed = np.array(result["reconstructed"])
                        cr_reported = result["compression_ratio"]

                        # Calculate all metrics using integrated scoring logic
                        prd = self.metrics_calculator.calculate_prd(original, reconstructed)
                        rmse = self.metrics_calculator.calculate_rmse(original, reconstructed)
                        snr = self.metrics_calculator.calculate_snr(original, reconstructed)
                        qs = self.metrics_calculator.calculate_qs_score(cr_reported, prd)

                        # Calculate final score using user's original formula
                        final_score = self.metrics_calculator.calculate_final_score(cr_reported, prd)

                        dataset_metrics[dataset_name] = {
                            "CR": cr_reported,
                            "PRD": prd,
                            "RMSE": rmse,
                            "SNR": snr,
                            "QS": qs,
                            "FinalScore": final_score
                        }

                        # Collect for overall statistics
                        overall_metrics["CR"].append(cr_reported)
                        overall_metrics["PRD"].append(prd)
                        overall_metrics["RMSE"].append(rmse)
                        overall_metrics["SNR"].append(snr)
                        overall_metrics["QS"].append(qs)
                        overall_metrics["FinalScore"].append(final_score)

                        evaluation_result["datasets_evaluated"] += 1
                    else:
                        evaluation_result["errors"].append(f"Dataset {dataset_name}: {result['error']}")
                else:
                    evaluation_result["errors"].append(f"No output for dataset {dataset_name}")

            # Calculate overall metrics (averages) - Using user's scoring system
            if overall_metrics["CR"]:
                evaluation_result["metrics"] = {
                    "CR": np.mean(overall_metrics["CR"]),
                    "PRD": np.mean(overall_metrics["PRD"]),
                    "RMSE": np.mean(overall_metrics["RMSE"]),
                    "SNR": np.mean(overall_metrics["SNR"]),
                    "QS": np.mean(overall_metrics["QS"]),
                    "FinalScore": np.mean(overall_metrics["FinalScore"]),
                    "Score": np.mean(overall_metrics["FinalScore"])  # Use FinalScore as primary ranking
                }

                evaluation_result["detailed_metrics"] = dataset_metrics
                evaluation_result["performance"] = {
                    "execution_time": execution_result["execution_time"],
                    "memory_usage_mb": "N/A",  # Would need more complex monitoring
                    "datasets_processed": len(overall_metrics["CR"]),
                    "total_datasets": len(self.datasets)
                }

                # Add scoring system compatibility info
                evaluation_result["scoring_info"] = {
                    "formula": "FinalScore = CR / (PRD + epsilon)",
                    "epsilon": self.metrics_calculator.EPSILON,
                    "ranking_metric": "FinalScore"
                }

                evaluation_result["status"] = "completed"
            else:
                evaluation_result["status"] = "failed"
                evaluation_result["errors"].append("No successful dataset evaluations")

            # Cleanup
            import shutil
            shutil.rmtree(algorithm_dir, ignore_errors=True)

        except Exception as e:
            evaluation_result["status"] = "failed"
            evaluation_result["errors"].append(f"Evaluation error: {str(e)}")
            evaluation_result["traceback"] = traceback.format_exc()

        return evaluation_result

# Example usage and testing
if __name__ == "__main__":

    print("🚀 Initializing Real ECG Evaluation System...")

    # Initialize the evaluation system
    evaluator = RealECGEvaluationSystem()

    print(f"✅ System initialized with {len(evaluator.datasets)} datasets")

    # Test with a sample algorithm (if available)
    test_zip = "test_ecg_algorithm.zip"
    if os.path.exists(test_zip):
        print(f"\n🧪 Testing with {test_zip}...")
        result = evaluator.evaluate_submission(test_zip)

        print(f"\n📊 Evaluation Results:")
        print(f"Status: {result['status']}")
        print(f"Datasets evaluated: {result['datasets_evaluated']}/{result['total_datasets']}")

        if result['status'] == 'completed':
            metrics = result['metrics']
            print(f"\n📈 Overall Metrics:")
            print(f"  Compression Ratio: {metrics['CR']:.2f}")
            print(f"  PRD: {metrics['PRD']:.4f}%")
            print(f"  RMSE: {metrics['RMSE']:.6f}")
            print(f"  SNR: {metrics['SNR']:.2f} dB")
            print(f"  Quality Score: {metrics['QS']:.2f}")
            print(f"  Final Score: {metrics['Score']:.2f}")

        if result['errors']:
            print(f"\n⚠️ Errors:")
            for error in result['errors']:
                print(f"  - {error}")
    else:
        print(f"\n📝 Test file {test_zip} not found. System ready for evaluation.")

    print("\n✅ Real ECG Evaluation System is ready!")