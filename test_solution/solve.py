#!/usr/bin/env python3
"""
Test ECG Compression Solution
This is a simple test implementation for the ECG Compression Challenge
"""

import os

def compress_ecg(input_path, output_path):
    """
    Simple ECG compression function for testing

    Args:
        input_path: Path to input ECG data
        output_path: Path to save compressed data
    """
    try:
        # Load ECG data (assuming it's in a text format)
        if os.path.exists(input_path):
            # Simple compression: downsample by factor of 2
            with open(input_path, 'r') as f:
                data = [float(line.strip()) for line in f if line.strip()]

            # Compress by taking every other sample
            compressed = data[::2]

            # Save compressed data
            with open(output_path, 'w') as f:
                for value in compressed:
                    f.write(f"{value}\n")

            print(f"Compressed {len(data)} samples to {len(compressed)} samples")
            return True
        else:
            print(f"Input file not found: {input_path}")
            return False

    except Exception as e:
        print(f"Compression failed: {e}")
        return False

def decompress_ecg(input_path, output_path):
    """
    Simple ECG decompression function for testing

    Args:
        input_path: Path to compressed ECG data
        output_path: Path to save reconstructed data
    """
    try:
        # Load compressed data
        if os.path.exists(input_path):
            with open(input_path, 'r') as f:
                compressed = [float(line.strip()) for line in f if line.strip()]

            # Simple decompression: linear interpolation
            reconstructed = []
            for i in range(len(compressed)):
                reconstructed.append(compressed[i])
                if i < len(compressed) - 1:
                    # Add interpolated value
                    interpolated = (compressed[i] + compressed[i + 1]) / 2
                    reconstructed.append(interpolated)

            # Save reconstructed data
            with open(output_path, 'w') as f:
                for value in reconstructed:
                    f.write(f"{value}\n")

            print(f"Decompressed {len(compressed)} samples to {len(reconstructed)} samples")
            return True
        else:
            print(f"Input file not found: {input_path}")
            return False

    except Exception as e:
        print(f"Decompression failed: {e}")
        return False

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python solve.py <mode> <input_path> <output_path>")
        print("mode: 'compress' or 'decompress'")
        sys.exit(1)

    mode = sys.argv[1]
    input_path = sys.argv[2]
    output_path = sys.argv[3]

    if mode == "compress":
        success = compress_ecg(input_path, output_path)
    elif mode == "decompress":
        success = decompress_ecg(input_path, output_path)
    else:
        print(f"Unknown mode: {mode}")
        success = False

    sys.exit(0 if success else 1)