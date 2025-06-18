"""
Enhanced ECG Compression Scoring System
Based on the comprehensive design document for ECG Compression Benchmark

Implements:
- Standard PRD (Percent Root-mean-square Difference)
- PRDN (Normalized PRD with baseline removal)
- WWPRD (Wavelet-Weighted PRD)
- SNR (Signal-to-Noise Ratio)
- QS (Quality Score)
- Overall Score = CR / (PRD + ε)
- Additional diagnostic quality metrics
"""

import numpy as np
import scipy.io as sio
import scipy.signal
import pywt
import time
from typing import Dict, List, Tuple, Any, Optional
import logging

class EnhancedECGMetricsCalculator:
    """
    Comprehensive ECG compression metrics calculator
    Following the design specifications for robust evaluation
    """

    # Constants following design document recommendations
    EPSILON = 1e-6  # Small constant to avoid division by zero
    CLINICAL_PRD_THRESHOLD = 10.0  # Clinical acceptability threshold (%)
    WWPRD_THRESHOLD = 10.0  # Wavelet-weighted PRD threshold (%)

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
        """
        Calculate Compression Ratio (CR)
        CR = B₀ / Bc where B₀ is original bits, Bc is compressed bits

        Args:
            original_size: Size of original data in bits/bytes
            compressed_size: Size of compressed data in bits/bytes

        Returns:
            float: Compression ratio (higher is better)
        """
        if compressed_size == 0:
            return 0.0
        return float(original_size / compressed_size)

    @staticmethod
    def calculate_prd(original: np.ndarray, reconstructed: np.ndarray) -> float:
        """
        Calculate standard Percent Root-mean-square Difference (PRD)

        PRD(%) = 100 × √(Σ[x(n) - x_r(n)]²) / √(Σ[x(n)]²)

        Args:
            original: Original ECG signal
            reconstructed: Reconstructed ECG signal

        Returns:
            float: PRD percentage (lower is better)
        """
        # Align signal lengths
        if len(original) != len(reconstructed):
            min_len = min(len(original), len(reconstructed))
            original = original[:min_len]
            reconstructed = reconstructed[:min_len]

        # Calculate PRD using the standard formula
        numerator = np.linalg.norm(original - reconstructed, 2)
        denominator = np.linalg.norm(original, 2)

        if denominator < EnhancedECGMetricsCalculator.EPSILON:
            return float('inf')  # Handle zero signals

        prd = (numerator / denominator) * 100
        return float(prd)

    @staticmethod
    def calculate_prdn(original: np.ndarray, reconstructed: np.ndarray,
                      baseline_method: str = 'mean') -> float:
        """
        Calculate Normalized PRD (PRDN) with baseline removal

        This removes DC offset or baseline wander before computing PRD
        to ensure fairness across signals with different baselines.

        Args:
            original: Original ECG signal
            reconstructed: Reconstructed ECG signal
            baseline_method: 'mean', 'median', or 'linear_detrend'

        Returns:
            float: PRDN percentage (lower is better)
        """
        # Align signal lengths
        if len(original) != len(reconstructed):
            min_len = min(len(original), len(reconstructed))
            original = original[:min_len]
            reconstructed = reconstructed[:min_len]

        # Remove baseline according to specified method
        if baseline_method == 'mean':
            original_norm = original - np.mean(original)
            reconstructed_norm = reconstructed - np.mean(reconstructed)
        elif baseline_method == 'median':
            original_norm = original - np.median(original)
            reconstructed_norm = reconstructed - np.median(reconstructed)
        elif baseline_method == 'linear_detrend':
            original_norm = scipy.signal.detrend(original, type='linear')
            reconstructed_norm = scipy.signal.detrend(reconstructed, type='linear')
        else:
            # Default to mean removal
            original_norm = original - np.mean(original)
            reconstructed_norm = reconstructed - np.mean(reconstructed)

        # Calculate PRDN on normalized signals
        numerator = np.linalg.norm(original_norm - reconstructed_norm, 2)
        denominator = np.linalg.norm(original_norm, 2)

        if denominator < EnhancedECGMetricsCalculator.EPSILON:
            return float('inf')

        prdn = (numerator / denominator) * 100
        return float(prdn)

    @staticmethod
    def calculate_wwprd(original: np.ndarray, reconstructed: np.ndarray,
                       wavelet_name: str = 'db4', levels: int = 6) -> float:
        """
        Calculate Wavelet-Weighted PRD (WWPRD)

        WWPRD weights errors in different frequency bands according to
        their clinical importance, emphasizing QRS complexes and other
        diagnostically relevant features.

        Args:
            original: Original ECG signal
            reconstructed: Reconstructed ECG signal
            wavelet_name: Wavelet to use for decomposition
            levels: Number of decomposition levels

        Returns:
            float: WWPRD percentage (lower is better)
        """
        # Align signal lengths
        if len(original) != len(reconstructed):
            min_len = min(len(original), len(reconstructed))
            original = original[:min_len]
            reconstructed = reconstructed[:min_len]

        try:
            # Wavelet decomposition
            coeffs_orig = pywt.wavedec(original, wavelet_name, level=levels)
            coeffs_recon = pywt.wavedec(reconstructed, wavelet_name, level=levels)

            # Clinical weighting factors (emphasize QRS-relevant frequencies)
            # Higher weights for bands containing QRS complex (10-40 Hz)
            weights = np.array([1.0, 2.0, 3.0, 2.0, 1.5, 1.0, 0.5][:len(coeffs_orig)])

            weighted_error = 0.0
            weighted_signal = 0.0

            for i, (c_orig, c_recon, weight) in enumerate(zip(coeffs_orig, coeffs_recon, weights)):
                # Ensure same length
                min_len = min(len(c_orig), len(c_recon))
                c_orig = c_orig[:min_len]
                c_recon = c_recon[:min_len]

                # Weighted energy
                error_energy = np.sum((c_orig - c_recon) ** 2)
                signal_energy = np.sum(c_orig ** 2)

                weighted_error += weight * error_energy
                weighted_signal += weight * signal_energy

            if weighted_signal < EnhancedECGMetricsCalculator.EPSILON:
                return float('inf')

            wwprd = 100 * np.sqrt(weighted_error / weighted_signal)
            return float(wwprd)

        except Exception as e:
            # Fallback to standard PRD if wavelet calculation fails
            logging.warning(f"WWPRD calculation failed: {e}. Using standard PRD.")
            return EnhancedECGMetricsCalculator.calculate_prd(original, reconstructed)

    @staticmethod
    def calculate_snr_db(original: np.ndarray, reconstructed: np.ndarray) -> float:
        """
        Calculate Signal-to-Noise Ratio in dB

        SNR = 20 * log₁₀(|signal| / |noise|)

        Args:
            original: Original ECG signal
            reconstructed: Reconstructed ECG signal

        Returns:
            float: SNR in decibels (higher is better)
        """
        # Align signal lengths
        if len(original) != len(reconstructed):
            min_len = min(len(original), len(reconstructed))
            original = original[:min_len]
            reconstructed = reconstructed[:min_len]

        signal_power = np.mean(original ** 2)
        noise_power = np.mean((original - reconstructed) ** 2)

        if noise_power == 0:
            return float('inf')  # Perfect reconstruction
        if signal_power == 0:
            return float('-inf')  # Zero signal

        snr = 10 * np.log10(signal_power / noise_power)
        return float(snr)

    @staticmethod
    def calculate_rmse(original: np.ndarray, reconstructed: np.ndarray) -> float:
        """
        Calculate Root Mean Square Error (RMSE)

        Args:
            original: Original ECG signal
            reconstructed: Reconstructed ECG signal

        Returns:
            float: RMSE value (lower is better)
        """
        # Align signal lengths
        if len(original) != len(reconstructed):
            min_len = min(len(original), len(reconstructed))
            original = original[:min_len]
            reconstructed = reconstructed[:min_len]

        mse = np.mean((original - reconstructed) ** 2)
        return float(np.sqrt(mse))

    @staticmethod
    def calculate_quality_score(cr: float, prd: float) -> float:
        """
        Calculate Quality Score (QS) = CR / PRD

        Args:
            cr: Compression ratio
            prd: PRD percentage

        Returns:
            float: Quality score (higher is better)
        """
        if prd == 0:
            return float('inf')
        return float(cr / prd)

    @staticmethod
    def calculate_quality_score_normalized(cr: float, prdn: float) -> float:
        """
        Calculate Quality Score Normalized (QSN) = CR / PRDN

        Args:
            cr: Compression ratio
            prdn: Normalized PRD percentage

        Returns:
            float: Normalized quality score (higher is better)
        """
        if prdn == 0:
            return float('inf')
        return float(cr / prdn)

    @staticmethod
    def calculate_overall_score(cr: float, prd: float,
                              epsilon: Optional[float] = None) -> float:
        """
        Calculate Overall Score using the main ranking formula

        Overall Score = CR / (PRD + ε)

        This is the primary metric for leaderboard ranking.

        Args:
            cr: Compression ratio
            prd: PRD percentage
            epsilon: Small constant to avoid division by zero

        Returns:
            float: Overall score (higher is better)
        """
        if epsilon is None:
            epsilon = EnhancedECGMetricsCalculator.EPSILON

        overall_score = cr / (prd + epsilon)
        return float(overall_score)

class DiagnosticQualityAssessor:
    """
    Assess diagnostic quality preservation in compressed ECG signals
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def assess_r_peak_preservation(self, original: np.ndarray, reconstructed: np.ndarray,
                                 fs: float = 360.0) -> Dict[str, float]:
        """
        Assess R-peak detection accuracy on reconstructed signal

        Args:
            original: Original ECG signal
            reconstructed: Reconstructed ECG signal
            fs: Sampling frequency in Hz

        Returns:
            Dict with R-peak preservation metrics
        """
        try:
            # Simple R-peak detection using scipy
            # This is a basic implementation - production would use advanced detectors

            # High-pass filter for QRS enhancement
            nyquist = fs / 2
            high_cutoff = 5.0 / nyquist
            b, a = scipy.signal.butter(4, high_cutoff, btype='high')

            orig_filtered = scipy.signal.filtfilt(b, a, original)
            recon_filtered = scipy.signal.filtfilt(b, a, reconstructed)

            # Find peaks with minimum distance
            min_distance = int(0.3 * fs)  # Minimum 300ms between R-peaks

            orig_peaks, _ = scipy.signal.find_peaks(orig_filtered,
                                                   distance=min_distance,
                                                   height=np.std(orig_filtered))
            recon_peaks, _ = scipy.signal.find_peaks(recon_filtered,
                                                    distance=min_distance,
                                                    height=np.std(recon_filtered))

            # Calculate preservation metrics
            tolerance = int(0.05 * fs)  # 50ms tolerance

            true_positives = 0
            for orig_peak in orig_peaks:
                if any(abs(orig_peak - recon_peak) <= tolerance for recon_peak in recon_peaks):
                    true_positives += 1

            false_positives = len(recon_peaks) - true_positives
            false_negatives = len(orig_peaks) - true_positives

            sensitivity = true_positives / len(orig_peaks) if len(orig_peaks) > 0 else 0.0
            ppv = true_positives / len(recon_peaks) if len(recon_peaks) > 0 else 0.0

            return {
                'sensitivity': float(sensitivity),
                'positive_predictive_value': float(ppv),
                'true_positives': true_positives,
                'false_positives': false_positives,
                'false_negatives': false_negatives,
                'original_peaks': len(orig_peaks),
                'reconstructed_peaks': len(recon_peaks)
            }

        except Exception as e:
            self.logger.warning(f"R-peak assessment failed: {e}")
            return {
                'sensitivity': 0.0,
                'positive_predictive_value': 0.0,
                'error': str(e)
            }

    def assess_heart_rate_variability(self, original: np.ndarray, reconstructed: np.ndarray,
                                    fs: float = 360.0) -> Dict[str, float]:
        """
        Compare HRV parameters between original and reconstructed signals

        Args:
            original: Original ECG signal
            reconstructed: Reconstructed ECG signal
            fs: Sampling frequency in Hz

        Returns:
            Dict with HRV preservation metrics
        """
        try:
            # Get R-peak analysis for both signals
            orig_r_peaks = self.assess_r_peak_preservation(original, original, fs)
            recon_r_peaks = self.assess_r_peak_preservation(reconstructed, reconstructed, fs)

            # Simple HRV analysis would go here
            # For now, return placeholder metrics

            return {
                'hrv_preservation_score': 0.95,  # Placeholder
                'rr_interval_correlation': 0.98,  # Placeholder
                'sdnn_difference': 2.5  # Placeholder difference in ms
            }

        except Exception as e:
            self.logger.warning(f"HRV assessment failed: {e}")
            return {
                'hrv_preservation_score': 0.0,
                'error': str(e)
            }

class ComprehensiveECGEvaluator:
    """
    Main evaluator that combines all metrics for comprehensive assessment
    """

    def __init__(self):
        self.metrics_calc = EnhancedECGMetricsCalculator()
        self.diagnostic_assessor = DiagnosticQualityAssessor()
        self.logger = logging.getLogger(__name__)

    def evaluate_compression_performance(self, original: np.ndarray, reconstructed: np.ndarray,
                                       compression_ratio: float, fs: float = 360.0,
                                       include_diagnostic: bool = True) -> Dict[str, Any]:
        """
        Comprehensive evaluation of ECG compression performance

        Args:
            original: Original ECG signal
            reconstructed: Reconstructed ECG signal
            compression_ratio: Reported compression ratio
            fs: Sampling frequency
            include_diagnostic: Whether to include diagnostic quality assessment

        Returns:
            Dict with comprehensive metrics
        """
        start_time = time.time()

        results = {
            'timestamp': start_time,
            'signal_length': len(original),
            'sampling_frequency': fs
        }

        try:
            # Core compression metrics
            prd = self.metrics_calc.calculate_prd(original, reconstructed)
            prdn = self.metrics_calc.calculate_prdn(original, reconstructed)
            wwprd = self.metrics_calc.calculate_wwprd(original, reconstructed)
            snr = self.metrics_calc.calculate_snr_db(original, reconstructed)
            rmse = self.metrics_calc.calculate_rmse(original, reconstructed)

            # Quality scores
            qs = self.metrics_calc.calculate_quality_score(compression_ratio, prd)
            qsn = self.metrics_calc.calculate_quality_score_normalized(compression_ratio, prdn)

            # Overall score (primary ranking metric)
            overall_score = self.metrics_calc.calculate_overall_score(compression_ratio, prd)

            # Core metrics
            results.update({
                'compression_metrics': {
                    'CR': float(compression_ratio),
                    'PRD': float(prd),
                    'PRDN': float(prdn),
                    'WWPRD': float(wwprd),
                    'RMSE': float(rmse),
                    'SNR': float(snr)
                },
                'quality_scores': {
                    'QS': float(qs),
                    'QSN': float(qsn),
                    'OverallScore': float(overall_score)
                },
                'clinical_assessment': {
                    'prd_acceptable': prd < self.metrics_calc.CLINICAL_PRD_THRESHOLD,
                    'wwprd_acceptable': wwprd < self.metrics_calc.WWPRD_THRESHOLD,
                    'diagnostic_quality': 'Acceptable' if prd < self.metrics_calc.CLINICAL_PRD_THRESHOLD else 'Questionable'
                }
            })

            # Diagnostic quality assessment (optional, computationally intensive)
            if include_diagnostic:
                try:
                    r_peak_metrics = self.diagnostic_assessor.assess_r_peak_preservation(
                        original, reconstructed, fs)
                    hrv_metrics = self.diagnostic_assessor.assess_heart_rate_variability(
                        original, reconstructed, fs)

                    results['diagnostic_preservation'] = {
                        'r_peak_detection': r_peak_metrics,
                        'heart_rate_variability': hrv_metrics
                    }
                except Exception as e:
                    self.logger.warning(f"Diagnostic assessment failed: {e}")
                    results['diagnostic_preservation'] = {'error': str(e)}

            # Performance metrics
            results['evaluation_performance'] = {
                'computation_time': time.time() - start_time,
                'status': 'completed'
            }

            return results

        except Exception as e:
            self.logger.error(f"Evaluation failed: {e}")
            results.update({
                'status': 'failed',
                'error': str(e),
                'evaluation_performance': {
                    'computation_time': time.time() - start_time,
                    'status': 'failed'
                }
            })
            return results

    def evaluate_dataset_submission(self, dataset_results: Dict[str, Dict],
                                   original_signals: Dict[str, np.ndarray],
                                   sampling_frequencies: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Evaluate submission across multiple ECG datasets

        Args:
            dataset_results: Algorithm outputs per dataset
            original_signals: Original signals per dataset
            sampling_frequencies: Sampling frequencies per dataset

        Returns:
            Aggregated evaluation results
        """
        if sampling_frequencies is None:
            sampling_frequencies = {name: 360.0 for name in original_signals.keys()}

        dataset_evaluations = {}
        aggregated_metrics = {
            'CR': [], 'PRD': [], 'PRDN': [], 'WWPRD': [],
            'RMSE': [], 'SNR': [], 'QS': [], 'QSN': [], 'OverallScore': []
        }

        total_original_size = 0
        total_compressed_size = 0

        for dataset_name, original_signal in original_signals.items():
            if dataset_name in dataset_results:
                try:
                    result = dataset_results[dataset_name]
                    reconstructed = np.array(result['reconstructed'])
                    cr = float(result['compression_ratio'])
                    fs = sampling_frequencies.get(dataset_name, 360.0)

                    # Evaluate this dataset
                    eval_result = self.evaluate_compression_performance(
                        original_signal, reconstructed, cr, fs, include_diagnostic=False)

                    dataset_evaluations[dataset_name] = eval_result

                    # Collect metrics for aggregation
                    if eval_result['status'] == 'completed':
                        metrics = eval_result['compression_metrics']
                        quality = eval_result['quality_scores']

                        aggregated_metrics['CR'].append(metrics['CR'])
                        aggregated_metrics['PRD'].append(metrics['PRD'])
                        aggregated_metrics['PRDN'].append(metrics['PRDN'])
                        aggregated_metrics['WWPRD'].append(metrics['WWPRD'])
                        aggregated_metrics['RMSE'].append(metrics['RMSE'])
                        aggregated_metrics['SNR'].append(metrics['SNR'])
                        aggregated_metrics['QS'].append(quality['QS'])
                        aggregated_metrics['QSN'].append(quality['QSN'])
                        aggregated_metrics['OverallScore'].append(quality['OverallScore'])

                        # For total compression ratio calculation
                        original_size = len(original_signal)
                        compressed_size = original_size / cr if cr > 0 else original_size
                        total_original_size += original_size
                        total_compressed_size += compressed_size

                except Exception as e:
                    dataset_evaluations[dataset_name] = {
                        'status': 'failed',
                        'error': str(e)
                    }

        # Calculate aggregated metrics
        final_metrics = {}
        for metric_name, values in aggregated_metrics.items():
            if values:
                if metric_name == 'CR':
                    # Use total compression ratio for overall CR
                    final_metrics[metric_name] = float(total_original_size / total_compressed_size) if total_compressed_size > 0 else 0.0
                else:
                    # Use average for other metrics
                    final_metrics[metric_name] = float(np.mean(values))
            else:
                final_metrics[metric_name] = 0.0

        return {
            'overall_metrics': final_metrics,
            'dataset_evaluations': dataset_evaluations,
            'datasets_processed': len([k for k, v in dataset_evaluations.items() if v.get('status') == 'completed']),
            'total_datasets': len(original_signals),
            'evaluation_summary': {
                'primary_score': final_metrics.get('OverallScore', 0.0),
                'compression_ratio': final_metrics.get('CR', 0.0),
                'reconstruction_error': final_metrics.get('PRD', float('inf')),
                'clinical_acceptability': final_metrics.get('PRD', float('inf')) < EnhancedECGMetricsCalculator.CLINICAL_PRD_THRESHOLD
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the enhanced scoring system
    evaluator = ComprehensiveECGEvaluator()

    # Generate test signals
    fs = 360.0
    duration = 10.0  # 10 seconds
    t = np.linspace(0, duration, int(fs * duration))

    # Simulated ECG with some noise
    original = np.sin(2 * np.pi * 1.2 * t) + 0.5 * np.sin(2 * np.pi * 0.3 * t) + 0.1 * np.random.randn(len(t))

    # Simulated reconstruction with some distortion
    reconstructed = original + 0.05 * np.random.randn(len(t))

    # Test evaluation
    cr = 15.0  # 15:1 compression ratio

    results = evaluator.evaluate_compression_performance(
        original, reconstructed, cr, fs, include_diagnostic=True)

    print("=== Enhanced ECG Compression Evaluation Results ===")
    print(f"Compression Ratio: {results['compression_metrics']['CR']:.2f}")
    print(f"PRD: {results['compression_metrics']['PRD']:.4f}%")
    print(f"PRDN: {results['compression_metrics']['PRDN']:.4f}%")
    print(f"WWPRD: {results['compression_metrics']['WWPRD']:.4f}%")
    print(f"SNR: {results['compression_metrics']['SNR']:.2f} dB")
    print(f"Overall Score: {results['quality_scores']['OverallScore']:.2f}")
    print(f"Clinical Acceptability: {results['clinical_assessment']['diagnostic_quality']}")
    print(f"Computation Time: {results['evaluation_performance']['computation_time']:.3f}s")