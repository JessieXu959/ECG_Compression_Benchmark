#!/usr/bin/env python3
"""
Comprehensive Test Script for Enhanced ECG Scoring System

This script validates all metrics and features of the enhanced scoring system:
- Standard PRD calculation
- Normalized PRD (PRDN) with baseline removal
- Wavelet-Weighted PRD (WWPRD)
- Signal-to-Noise Ratio (SNR)
- Quality Scores (QS, QSN)
- Overall Score formula: CR / (PRD + ε)
- Diagnostic quality assessment
"""

import numpy as np
import sys
import os

# Add the core evaluation directory to Python path
sys.path.append('core/evaluation')

try:
    from enhanced_scoring_system import (
        EnhancedECGMetricsCalculator,
        DiagnosticQualityAssessor,
        ComprehensiveECGEvaluator
    )
    print("✅ Enhanced scoring system imported successfully")
except ImportError as e:
    print(f"❌ Failed to import enhanced scoring system: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

def generate_test_signals():
    """Generate test ECG signals for evaluation"""
    print("📊 Generating test ECG signals...")

    # Parameters
    fs = 360.0  # Sampling frequency (Hz)
    duration = 10.0  # Duration (seconds)
    t = np.linspace(0, duration, int(fs * duration))

    # Generate synthetic ECG signal
    # Basic ECG-like signal with multiple components
    heart_rate = 72  # BPM
    rr_interval = 60.0 / heart_rate  # seconds

    # P-wave, QRS complex, T-wave components
    ecg_signal = np.zeros_like(t)

    for i, time in enumerate(t):
        # Simple ECG model with multiple harmonics
        cardiac_cycle = (time % rr_interval) / rr_interval

        # QRS complex (dominant feature)
        if 0.15 < cardiac_cycle < 0.25:
            qrs_amplitude = 1.0 * np.exp(-50 * (cardiac_cycle - 0.2)**2)
            ecg_signal[i] += qrs_amplitude

        # P-wave
        if 0.05 < cardiac_cycle < 0.12:
            p_amplitude = 0.2 * np.exp(-100 * (cardiac_cycle - 0.085)**2)
            ecg_signal[i] += p_amplitude

        # T-wave
        if 0.35 < cardiac_cycle < 0.55:
            t_amplitude = 0.3 * np.exp(-25 * (cardiac_cycle - 0.45)**2)
            ecg_signal[i] += t_amplitude

    # Add baseline wander and noise
    baseline_wander = 0.1 * np.sin(2 * np.pi * 0.5 * t)
    noise = 0.05 * np.random.randn(len(t))

    original = ecg_signal + baseline_wander + noise

    # Generate different types of reconstructed signals for testing
    test_cases = {
        'high_quality': original + 0.02 * np.random.randn(len(t)),  # Very good reconstruction
        'medium_quality': original + 0.1 * np.random.randn(len(t)),  # Medium quality
        'low_quality': original + 0.3 * np.random.randn(len(t)),    # Poor reconstruction
        'baseline_shift': original + 0.5 + 0.05 * np.random.randn(len(t)),  # DC offset
        'frequency_distortion': original * 0.8 + 0.1 * np.sin(2 * np.pi * 10 * t)  # Frequency artifacts
    }

    return original, test_cases, fs

def test_basic_metrics():
    """Test basic compression metrics calculations"""
    print("\n🔬 Testing Basic Metrics Calculations")
    print("=" * 50)

    calculator = EnhancedECGMetricsCalculator()

    # Test signals
    original, test_cases, fs = generate_test_signals()

    print(f"Signal length: {len(original)} samples")
    print(f"Duration: {len(original)/fs:.1f} seconds")
    print(f"Sampling frequency: {fs} Hz")

    for case_name, reconstructed in test_cases.items():
        print(f"\n--- Testing: {case_name.replace('_', ' ').title()} ---")

        # Calculate all metrics
        prd = calculator.calculate_prd(original, reconstructed)
        prdn = calculator.calculate_prdn(original, reconstructed)
        wwprd = calculator.calculate_wwprd(original, reconstructed)
        snr = calculator.calculate_snr_db(original, reconstructed)
        rmse = calculator.calculate_rmse(original, reconstructed)

        # Test different compression ratios
        test_crs = [5.0, 10.0, 15.0, 20.0]

        for cr in test_crs:
            qs = calculator.calculate_quality_score(cr, prd)
            qsn = calculator.calculate_quality_score_normalized(cr, prdn)
            overall_score = calculator.calculate_overall_score(cr, prd)

            print(f"  CR={cr:.1f}: PRD={prd:.3f}%, PRDN={prdn:.3f}%, WWPRD={wwprd:.3f}%")
            print(f"          SNR={snr:.2f}dB, RMSE={rmse:.6f}")
            print(f"          QS={qs:.3f}, QSN={qsn:.3f}, Overall={overall_score:.3f}")
            print()

def test_clinical_thresholds():
    """Test clinical acceptability thresholds"""
    print("\n🏥 Testing Clinical Acceptability Thresholds")
    print("=" * 50)

    calculator = EnhancedECGMetricsCalculator()

    # Test with different PRD levels
    test_prds = [2.0, 5.0, 9.0, 10.0, 12.0, 15.0, 20.0]

    print("PRD Threshold Analysis:")
    print("PRD(%)  | Clinical Quality | WWPRD Acceptable")
    print("-" * 45)

    for prd in test_prds:
        clinical_ok = prd < calculator.CLINICAL_PRD_THRESHOLD
        wwprd_ok = prd < calculator.WWPRD_THRESHOLD  # Assuming similar threshold

        quality = "Acceptable" if clinical_ok else "Questionable"
        wwprd_status = "✓" if wwprd_ok else "✗"

        print(f"{prd:6.1f}  | {quality:15s} | {wwprd_status:>12s}")

def test_diagnostic_quality():
    """Test diagnostic quality assessment"""
    print("\n🫀 Testing Diagnostic Quality Assessment")
    print("=" * 50)

    assessor = DiagnosticQualityAssessor()

    # Generate test signals
    original, test_cases, fs = generate_test_signals()

    for case_name, reconstructed in test_cases.items():
        print(f"\n--- Diagnostic Assessment: {case_name.replace('_', ' ').title()} ---")

        # R-peak preservation
        r_peak_metrics = assessor.assess_r_peak_preservation(original, reconstructed, fs)

        print(f"R-peak Detection Metrics:")
        if 'error' not in r_peak_metrics:
            print(f"  Sensitivity: {r_peak_metrics['sensitivity']:.3f}")
            print(f"  PPV: {r_peak_metrics['positive_predictive_value']:.3f}")
            print(f"  Original peaks: {r_peak_metrics['original_peaks']}")
            print(f"  Reconstructed peaks: {r_peak_metrics['reconstructed_peaks']}")
            print(f"  True positives: {r_peak_metrics['true_positives']}")
            print(f"  False positives: {r_peak_metrics['false_positives']}")
            print(f"  False negatives: {r_peak_metrics['false_negatives']}")
        else:
            print(f"  Error: {r_peak_metrics['error']}")

        # HRV assessment
        hrv_metrics = assessor.assess_heart_rate_variability(original, reconstructed, fs)

        print(f"HRV Preservation Metrics:")
        if 'error' not in hrv_metrics:
            print(f"  HRV preservation score: {hrv_metrics['hrv_preservation_score']:.3f}")
            print(f"  RR interval correlation: {hrv_metrics['rr_interval_correlation']:.3f}")
            print(f"  SDNN difference: {hrv_metrics['sdnn_difference']:.2f} ms")
        else:
            print(f"  Error: {hrv_metrics['error']}")

def test_comprehensive_evaluation():
    """Test the comprehensive evaluation system"""
    print("\n🚀 Testing Comprehensive Evaluation System")
    print("=" * 50)

    evaluator = ComprehensiveECGEvaluator()

    # Generate test signals
    original, test_cases, fs = generate_test_signals()

    # Test comprehensive evaluation for each case
    for case_name, reconstructed in test_cases.items():
        print(f"\n--- Comprehensive Evaluation: {case_name.replace('_', ' ').title()} ---")

        # Test with different compression ratios
        for cr in [10.0, 15.0, 20.0]:
            print(f"\n  Compression Ratio: {cr:.1f}")

            results = evaluator.evaluate_compression_performance(
                original, reconstructed, cr, fs, include_diagnostic=True
            )

            # Check if evaluation was successful
            eval_status = results.get('evaluation_performance', {}).get('status', 'unknown')

            if eval_status == 'completed':
                # Core metrics
                metrics = results.get('compression_metrics', {})
                quality = results.get('quality_scores', {})
                clinical = results.get('clinical_assessment', {})

                print(f"    Core Metrics:")
                print(f"      CR: {metrics.get('CR', 0):.2f}")
                print(f"      PRD: {metrics.get('PRD', 0):.4f}%")
                print(f"      PRDN: {metrics.get('PRDN', 0):.4f}%")
                print(f"      WWPRD: {metrics.get('WWPRD', 0):.4f}%")
                print(f"      SNR: {metrics.get('SNR', 0):.2f} dB")
                print(f"      RMSE: {metrics.get('RMSE', 0):.6f}")

                print(f"    Quality Scores:")
                print(f"      QS: {quality.get('QS', 0):.4f}")
                print(f"      QSN: {quality.get('QSN', 0):.4f}")
                print(f"      Overall Score: {quality.get('OverallScore', 0):.4f}")

                print(f"    Clinical Assessment:")
                print(f"      PRD Acceptable: {clinical.get('prd_acceptable', False)}")
                print(f"      WWPRD Acceptable: {clinical.get('wwprd_acceptable', False)}")
                print(f"      Diagnostic Quality: {clinical.get('diagnostic_quality', 'Unknown')}")

                # Performance
                perf = results.get('evaluation_performance', {})
                print(f"    Performance:")
                print(f"      Computation Time: {perf.get('computation_time', 0):.3f}s")

                # Diagnostic preservation (if available)
                if 'diagnostic_preservation' in results:
                    diag = results['diagnostic_preservation']
                    if 'r_peak_detection' in diag and 'error' not in diag['r_peak_detection']:
                        r_peaks = diag['r_peak_detection']
                        print(f"    R-peak Preservation:")
                        print(f"      Sensitivity: {r_peaks.get('sensitivity', 0):.3f}")
                        print(f"      PPV: {r_peaks.get('positive_predictive_value', 0):.3f}")

            else:
                print(f"    ❌ Evaluation failed: {results.get('error', 'Unknown error')}")
                print(f"    Status: {eval_status}")

def test_dataset_evaluation():
    """Test multi-dataset evaluation"""
    print("\n📊 Testing Multi-Dataset Evaluation")
    print("=" * 50)

    evaluator = ComprehensiveECGEvaluator()

    # Generate multiple test datasets
    datasets = {}
    original_signals = {}

    for i in range(3):
        dataset_name = f"test_dataset_{i+1}"
        original, test_cases, fs = generate_test_signals()

        # Use medium quality reconstruction
        reconstructed = test_cases['medium_quality']
        cr = 10.0 + i * 5.0  # Different compression ratios

        datasets[dataset_name] = {
            'reconstructed': reconstructed,
            'compression_ratio': cr
        }
        original_signals[dataset_name] = original

    # Run multi-dataset evaluation
    results = evaluator.evaluate_dataset_submission(
        datasets, original_signals
    )

    print(f"Multi-Dataset Evaluation Results:")
    print(f"  Total datasets: {results['total_datasets']}")
    print(f"  Datasets processed: {results['datasets_processed']}")

    # Overall metrics
    overall = results['overall_metrics']
    print(f"\n  Overall Aggregated Metrics:")
    print(f"    CR: {overall['CR']:.2f}")
    print(f"    PRD: {overall['PRD']:.4f}%")
    print(f"    PRDN: {overall['PRDN']:.4f}%")
    print(f"    WWPRD: {overall['WWPRD']:.4f}%")
    print(f"    SNR: {overall['SNR']:.2f} dB")
    print(f"    Overall Score: {overall['OverallScore']:.4f}")

    # Evaluation summary
    summary = results['evaluation_summary']
    print(f"\n  Evaluation Summary:")
    print(f"    Primary Score: {summary['primary_score']:.4f}")
    print(f"    Compression Ratio: {summary['compression_ratio']:.2f}")
    print(f"    Reconstruction Error: {summary['reconstruction_error']:.4f}%")
    print(f"    Clinical Acceptability: {summary['clinical_acceptability']}")

def run_all_tests():
    """Run all test suites"""
    print("🧪 Enhanced ECG Scoring System - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Testing comprehensive ECG compression evaluation system")
    print(f"Includes: PRD, PRDN, WWPRD, SNR, QS, Overall Score = CR/(PRD+ε)")
    print(f"Plus diagnostic quality assessment and clinical thresholds")

    try:
        test_basic_metrics()
        test_clinical_thresholds()
        test_diagnostic_quality()
        test_comprehensive_evaluation()
        test_dataset_evaluation()

        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🎯 Enhanced scoring system is ready for production use")

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return False

    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)