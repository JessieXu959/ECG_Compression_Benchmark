#!/usr/bin/env python3
"""
Simple ECG Evaluation Test - Windows Compatible
===============================================

This script tests the ECG evaluation system without using problematic
multiprocessing features, making it compatible with Windows.
"""

import os
import sys
import json
import time
import zipfile
import tempfile
import numpy as np
from pathlib import Path

def create_simple_test_algorithm():
    """Create a simple test algorithm that works reliably"""

    algorithm_code = '''#!/usr/bin/env python3
import numpy as np

class ECGCompressor:
    def __init__(self):
        self.compression_factor = 2

    def compress_and_reconstruct(self, ecg_signal):
        """Simple ECG compression using downsampling"""
        # Convert to numpy array
        ecg_signal = np.array(ecg_signal, dtype=np.float64)

        # Simple downsampling compression
        compressed = ecg_signal[::self.compression_factor]

        # Reconstruct with linear interpolation
        indices = np.arange(0, len(ecg_signal), self.compression_factor)
        full_indices = np.arange(len(ecg_signal))
        reconstructed = np.interp(full_indices, indices, compressed)

        # Calculate compression ratio
        cr_val = len(ecg_signal) / len(compressed) if len(compressed) > 0 else 1.0

        return reconstructed, cr_val
'''

    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="simple_ecg_test_")

    # Write algorithm file
    algorithm_path = os.path.join(temp_dir, "ecg_model.py")
    with open(algorithm_path, 'w') as f:
        f.write(algorithm_code)

    # Create ZIP file
    zip_path = "simple_test_algorithm.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(algorithm_path, "ecg_model.py")

    # Cleanup temp directory
    import shutil
    shutil.rmtree(temp_dir)

    print(f"✅ Created simple test algorithm: {zip_path}")
    return zip_path

def test_algorithm_directly():
    """Test algorithm execution directly without multiprocessing"""

    print("\n🧪 Testing Algorithm Execution (Direct Method)")
    print("-" * 50)

    try:
        # Create test ECG data
        fs = 360  # Sampling frequency
        duration = 10  # 10 seconds
        t = np.arange(0, duration, 1/fs)

        # Generate simple ECG-like signal
        heart_rate = 72
        ecg_signal = np.sin(2 * np.pi * heart_rate/60 * t) + 0.1 * np.random.randn(len(t))

        print(f"📊 Test ECG signal: {len(ecg_signal)} samples, {duration}s @ {fs}Hz")

        # Create and test algorithm ZIP
        zip_path = create_simple_test_algorithm()

        # Extract algorithm
        temp_dir = tempfile.mkdtemp(prefix="test_extract_")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Import algorithm directly
        sys.path.insert(0, temp_dir)
        from ecg_model import ECGCompressor

        # Test algorithm
        print("🔧 Testing algorithm...")
        start_time = time.time()

        compressor = ECGCompressor()
        reconstructed, cr = compressor.compress_and_reconstruct(ecg_signal)

        execution_time = time.time() - start_time

        # Calculate metrics
        original = np.array(ecg_signal)
        reconstructed = np.array(reconstructed)

        # Ensure same length
        min_len = min(len(original), len(reconstructed))
        original = original[:min_len]
        reconstructed = reconstructed[:min_len]

        # Calculate PRD
        prd = np.sqrt(np.mean((original - reconstructed) ** 2)) / np.sqrt(np.mean(original ** 2)) * 100

        # Calculate RMSE
        rmse = np.sqrt(np.mean((original - reconstructed) ** 2))

        # Calculate SNR
        signal_power = np.mean(original ** 2)
        noise_power = np.mean((original - reconstructed) ** 2)
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else float('inf')

        print(f"\n📈 Results:")
        print(f"   Compression Ratio: {cr:.2f}")
        print(f"   PRD: {prd:.4f}%")
        print(f"   RMSE: {rmse:.6f}")
        print(f"   SNR: {snr:.2f} dB")
        print(f"   Execution time: {execution_time:.3f}s")

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        if os.path.exists(zip_path):
            os.remove(zip_path)

        print("✅ Direct algorithm test PASSED")
        return True

    except Exception as e:
        print(f"❌ Direct algorithm test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_evaluation_system_simple():
    """Test evaluation system with simplified approach"""

    print("\n🚀 Testing ECG Evaluation System (Simplified)")
    print("-" * 50)

    try:
        from real_evaluation_system import ECGDatasetManager, ECGMetricsCalculator

        print("✅ Imported evaluation system components")

        # Test dataset generation
        print("\n📊 Testing dataset generation...")
        dataset_manager = ECGDatasetManager("simple_test_data")
        datasets = dataset_manager.create_standard_datasets()

        print(f"✅ Created {len(datasets)} datasets")
        for name, dataset in datasets.items():
            size_kb = dataset["size_bytes"] / 1024
            duration = len(dataset["signal"]) / dataset["fs"]
            print(f"   - {name}: {len(dataset['signal'])} samples, {duration:.1f}s, {size_kb:.1f}KB")

        # Test metrics calculation
        print("\n🧮 Testing metrics calculation...")
        metrics_calc = ECGMetricsCalculator()

        # Use first dataset for testing
        dataset_name = list(datasets.keys())[0]
        original_signal = datasets[dataset_name]["signal"]

        # Create a simple "compressed" version (every other sample)
        compressed_indices = np.arange(0, len(original_signal), 2)
        compressed_signal = original_signal[compressed_indices]
        reconstructed = np.interp(np.arange(len(original_signal)), compressed_indices, compressed_signal)

        # Calculate metrics
        cr = len(original_signal) / len(compressed_signal)
        prd = metrics_calc.calculate_prd(original_signal, reconstructed)
        rmse = metrics_calc.calculate_rmse(original_signal, reconstructed)
        snr = metrics_calc.calculate_snr(original_signal, reconstructed)
        qs = metrics_calc.calculate_qs_score(cr, prd)

        print(f"   Compression Ratio: {cr:.2f}")
        print(f"   PRD: {prd:.4f}%")
        print(f"   RMSE: {rmse:.6f}")
        print(f"   SNR: {snr:.2f} dB")
        print(f"   Quality Score: {qs:.2f}")

        print("✅ Metrics calculation test PASSED")
        return True

    except Exception as e:
        print(f"❌ Evaluation system test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""

    print("🧬 Simple ECG Evaluation Test - Windows Compatible")
    print("=" * 60)

    # Test 1: Direct algorithm execution
    success1 = test_algorithm_directly()

    # Test 2: Evaluation system components
    success2 = test_evaluation_system_simple()

    # Summary
    print("\n" + "="*60)
    print("🎯 Test Summary:")
    print(f"   Direct Algorithm Test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"   Evaluation System Test: {'✅ PASSED' if success2 else '❌ FAILED'}")

    if success1 and success2:
        print("\n🎉 Basic ECG evaluation functionality is working!")
        print("\n💡 Core components verified:")
        print("   ✓ ECG signal generation")
        print("   ✓ Algorithm execution (direct)")
        print("   ✓ Metric calculations")
        print("   ✓ Dataset management")

        print("\n⚠️ Note: Advanced features (safe execution with multiprocessing)")
        print("   may need additional fixes for Windows compatibility.")
    else:
        print("\n❌ Some tests failed. Check error messages above.")

    print("\n💡 To run the full system:")
    print("   1. Fix multiprocessing issues for production use")
    print("   2. Start backend: cd mini-backend && python main.py")
    print("   3. Open frontend: ecg-compression/index.html")

if __name__ == "__main__":
    main()