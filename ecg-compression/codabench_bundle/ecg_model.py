"""
示例: ecg_model.py

说明：
- 这里定义一个类 ECGCompressor，提供 compress_and_reconstruct 方法。
- 评测时，ingestion.py 会通过 "from ecg_model import ECGCompressor" 来调用此类。
- 你可以在这里使用任意算法完成对ECG信号的压缩与重建。
"""

# ecg_model.py
import numpy as np

class ECGCompressor:
    def __init__(self):
        pass

    def compress_and_reconstruct(self, ecg_signal):
        # 压缩逻辑（示例：降采样）
        compressed_data = ecg_signal[::2]  # 取偶数索引

        # 计算压缩比（CR）
        original_length = ecg_signal.size
        compressed_length = compressed_data.size
        if compressed_length == 0:
            raise ValueError("Compressed signal is empty.")
        cr_val = original_length / compressed_length

        # 重建信号（示例：简单插值）
        f_recon = np.repeat(compressed_data, 2)
        if f_recon.size > original_length:
            f_recon = f_recon[:original_length]
        elif f_recon.size < original_length:
            f_recon = np.pad(f_recon, (0, original_length - f_recon.size), mode='constant')

        return f_recon, cr_val