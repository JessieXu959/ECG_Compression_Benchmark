# Test ECG Compression Solution

This is a simple test implementation for the ECG Compression Challenge.

## Algorithm Description

This solution implements a basic compression algorithm:
- **Compression**: Downsamples the ECG signal by factor of 2 (takes every other sample)
- **Decompression**: Uses linear interpolation to reconstruct the original signal

## Usage

```bash
# Compression
python solve.py compress input.txt compressed.txt

# Decompression
python solve.py decompress compressed.txt reconstructed.txt
```

## Performance

- Compression Ratio: ~2:1
- Expected PRD: < 0.01
- Algorithm: Simple downsampling with interpolation

## Requirements

- Python 3.x
- numpy (optional, not used in this simple version)