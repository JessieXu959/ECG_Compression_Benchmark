"""
Create sample ECG data files for evaluation
"""

import numpy as np
import scipy.io as sio
from pathlib import Path

def create_sample_ecg_data():
    """Create sample ECG data files for testing"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Sample ECG parameters
    fs = 360  # Sampling frequency (Hz)
    duration = 5 * 60  # 5 minutes in seconds
    t = np.arange(0, duration, 1/fs)

    # Create two different ECG-like signals
    datasets = [
        "PhysioNet_MITBIH_rec117_5min",
        "PhysioNet_MITBIH_rec119_5min"
    ]

    for i, dataset_name in enumerate(datasets):
        # Generate a simple ECG-like signal
        # Combine multiple frequencies to simulate an ECG
        heart_rate = 70 + i * 10  # Different heart rates

        # Main heartbeat frequency
        f_heart = heart_rate / 60  # Convert to Hz

        # Create ECG-like signal with multiple harmonics
        ecg_signal = (
            1.0 * np.sin(2 * np.pi * f_heart * t) +
            0.3 * np.sin(2 * np.pi * 2 * f_heart * t) +
            0.2 * np.sin(2 * np.pi * 3 * f_heart * t) +
            0.1 * np.sin(2 * np.pi * 5 * f_heart * t) +
            0.05 * np.sin(2 * np.pi * 50 * t) +  # Powerline interference
            0.02 * np.random.randn(len(t))  # Noise
        )

        # Add some QRS-like spikes
        spike_interval = int(fs * (60 / heart_rate))  # Samples between heartbeats
        for spike_idx in range(spike_interval, len(ecg_signal), spike_interval):
            if spike_idx < len(ecg_signal):
                # Add a sharp spike to simulate QRS complex
                spike_width = 5
                start_idx = max(0, spike_idx - spike_width)
                end_idx = min(len(ecg_signal), spike_idx + spike_width)
                ecg_signal[start_idx:end_idx] += 2.0 * np.exp(-0.5 * ((np.arange(start_idx, end_idx) - spike_idx) / 2) ** 2)

        # Normalize
        ecg_signal = ecg_signal / np.max(np.abs(ecg_signal))

        # Save as .mat file
        mat_file_path = data_dir / f"{dataset_name}.mat"
        sio.savemat(str(mat_file_path), {"ecg": ecg_signal})

        print(f"Created {mat_file_path} with {len(ecg_signal)} samples")

if __name__ == "__main__":
    create_sample_ecg_data()
    print("Sample ECG data files created successfully!")