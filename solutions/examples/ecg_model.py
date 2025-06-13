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
        self.compression_ratio = 10.0  # 目标压缩比

    def compress_and_reconstruct(self, ecg_signal):
        """
        使用简单下采样压缩ECG信号

        Args:
            ecg_signal: 输入ECG信号

        Returns:
            tuple: (重建信号, 压缩比)
        """
        # 确保输入是numpy数组
        if not isinstance(ecg_signal, np.ndarray):
            ecg_signal = np.array(ecg_signal)

        original_length = len(ecg_signal)
        print(f"原始信号长度: {original_length}")

        # 1. 简单的下采样压缩（每N个点取1个）
        step = 10  # 下采样步长
        indices = np.arange(0, original_length, step)
        compressed = ecg_signal[indices]

        print(f"压缩后长度: {len(compressed)}")

        # 2. 计算实际压缩比
        cr_val = float(original_length) / float(len(compressed))
        print(f"压缩比: {cr_val:.2f}")

        # 3. 重建信号 (线性插值)
        x_original = np.arange(original_length)
        reconstructed = np.interp(x_original, indices, compressed)

        # 4. 确保重建信号与原始信号长度一致
        if len(reconstructed) != original_length:
            if len(reconstructed) > original_length:
                reconstructed = reconstructed[:original_length]
            else:
                # 填充至原始长度
                padded = np.zeros(original_length)
                padded[:len(reconstructed)] = reconstructed
                reconstructed = padded

        # 5. 打印调试信息
        print(f"重建信号类型: {type(reconstructed)}, 形状: {reconstructed.shape}")
        print(f"压缩比类型: {type(cr_val)}, 值: {cr_val}")

        # 6. 计算PRD值 (仅用于参考)
        self._calculate_prd(ecg_signal, reconstructed)

        # 7. 返回重建信号和压缩比
        return reconstructed.astype(np.float64), float(cr_val)

    def _calculate_prd(self, original, reconstructed):
        """计算PRD (Percent Root-mean-square Difference)"""
        f_mean = np.mean(original)
        numerator = np.linalg.norm(original - reconstructed, 2)
        denominator = np.linalg.norm(original - f_mean, 2)

        EPSILON = 1e-10
        if denominator < EPSILON:
            prd = float('inf')
        else:
            prd = (numerator / denominator) * 100

        print(f"PRD: {prd:.4f}%")
        return prd