#!/usr/bin/env python3
"""
Create a test ZIP file for ECG compression algorithm submission
"""

import zipfile
from pathlib import Path

def create_test_algorithm_zip():
    """Create a test ZIP file with sample algorithm"""

    # Algorithm code
    algorithm_code = '''#!/usr/bin/env python3
"""
Simple ECG Compression Algorithm - Test Submission
"""

import numpy as np

def compress_ecg(signal):
    """
    Simple compression: downsample by factor of 2
    In practice, you would implement more sophisticated compression
    """
    if len(signal) % 2 != 0:
        signal = signal[:-1]  # Make even length

    compressed = signal[::2]  # Take every other sample
    return compressed

def decompress_ecg(compressed_signal):
    """
    Simple decompression: upsample by repeating samples
    In practice, you would implement interpolation or reconstruction
    """
    decompressed = np.repeat(compressed_signal, 2)
    return decompressed

def evaluate_compression(original, compressed):
    """
    Calculate compression metrics
    """
    # Decompress
    reconstructed = decompress_ecg(compressed)

    # Ensure same length
    min_len = min(len(original), len(reconstructed))
    original = original[:min_len]
    reconstructed = reconstructed[:min_len]

    # Calculate metrics
    mse = np.mean((original - reconstructed) ** 2)
    prd = np.sqrt(mse) / np.std(original) * 100  # PRD in percentage
    cr = len(original) / len(compressed)  # Compression ratio

    return {
        'CR': cr,
        'PRD': prd,
        'MSE': mse
    }

# Example usage
if __name__ == "__main__":
    # Generate sample ECG signal
    t = np.linspace(0, 10, 1000)  # 10 seconds, 100 Hz
    ecg_signal = np.sin(2 * np.pi * 1.2 * t) + 0.3 * np.sin(2 * np.pi * 2.4 * t)
    ecg_signal += 0.1 * np.random.randn(len(t))  # Add noise

    # Test compression
    compressed = compress_ecg(ecg_signal)
    metrics = evaluate_compression(ecg_signal, compressed)

    print(f"Compression Ratio: {metrics['CR']:.2f}")
    print(f"PRD: {metrics['PRD']:.4f}%")
    print(f"MSE: {metrics['MSE']:.6f}")
'''

    # README file
    readme_content = '''# Test ECG Compression Algorithm

## Overview
This is a simple test algorithm for ECG compression challenge.

## Algorithm Description
- **Method**: Simple downsampling compression
- **Compression**: Takes every other sample (2:1 compression)
- **Decompression**: Repeats each sample twice

## Files
- `algorithm.py`: Main algorithm implementation
- `requirements.txt`: Dependencies
- `README.md`: This file

## Usage
```python
from algorithm import compress_ecg, decompress_ecg

# Compress ECG signal
compressed = compress_ecg(ecg_signal)

# Decompress
reconstructed = decompress_ecg(compressed)
```

## Performance
- Compression Ratio: ~2.0
- Expected PRD: 5-15%
- Processing Speed: Very fast

## Author
Test Team - ECG Compression Challenge
'''

    # Requirements file
    requirements_content = '''numpy>=1.20.0
scipy>=1.7.0
'''

    # Create ZIP file
    zip_filename = "test_ecg_algorithm.zip"

    print(f"🔨 Creating test algorithm ZIP file: {zip_filename}")

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("algorithm.py", algorithm_code)
        zf.writestr("README.md", readme_content)
        zf.writestr("requirements.txt", requirements_content)

    file_size = Path(zip_filename).stat().st_size
    print(f"✅ Created {zip_filename} ({file_size} bytes)")
    print(f"📁 File location: {Path(zip_filename).absolute()}")

    return zip_filename

if __name__ == "__main__":
    create_test_algorithm_zip()
    print("\n🎯 Use this ZIP file for testing the submission API!")
    print("📋 Algorithm name suggestion: TestAlgorithm_Downsampling")