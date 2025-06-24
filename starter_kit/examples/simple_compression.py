"""
ECG Compression Challenge - Example 1: Simple Compression
=========================================================

这是一个简单的ECG压缩算法示例，使用降采样方法。
适合初学者理解基础概念。

算法特点:
- 使用降采样进行压缩
- 线性插值进行重建
- 简单易懂，运行速度快
- 压缩比约2-4倍

作者: Starter Kit Team
"""

import numpy as np
from scipy import signal


class SimpleECGCompressor:
    """
    简单ECG压缩器

    使用降采样和插值的基础压缩方法
    """

    def __init__(self, compression_factor=2):
        """
        初始化压缩器

        参数:
            compression_factor (int): 压缩因子，建议2-4
        """
        self.compression_factor = compression_factor

    def compress_and_reconstruct(self, ecg_signal):
        """
        压缩和重建ECG信号

        参数:
            ecg_signal (numpy.ndarray): 输入ECG信号

        返回:
            tuple: (重建信号, 压缩比)
        """
        # 1. 预处理：去除噪声
        filtered_signal = self._preprocess(ecg_signal)

        # 2. 压缩：降采样
        compressed_indices = np.arange(0, len(filtered_signal), self.compression_factor)
        compressed_values = filtered_signal[compressed_indices]

        # 3. 重建：线性插值
        original_indices = np.arange(len(filtered_signal))
        reconstructed = np.interp(original_indices, compressed_indices, compressed_values)

        # 4. 计算压缩比
        compression_ratio = len(filtered_signal) / len(compressed_values)

        return reconstructed, compression_ratio

    def _preprocess(self, ecg_signal):
        """
        信号预处理：简单低通滤波
        """
        # 应用低通滤波器去除高频噪声
        nyquist = 0.5  # 归一化频率
        low_cutoff = 0.1  # 低通截止频率

        b, a = signal.butter(4, low_cutoff, btype='low')
        filtered = signal.filtfilt(b, a, ecg_signal)

        return filtered


# 测试代码
def demo_simple_compression():
    """
    演示简单压缩算法
    """
    print("=== 简单ECG压缩算法演示 ===\n")

    # 生成模拟ECG信号
    t = np.linspace(0, 10, 3600)  # 10秒, 360Hz
    ecg_signal = (
        np.sin(2 * np.pi * 1.2 * t) +           # 心率成分
        0.5 * np.sin(2 * np.pi * 2.4 * t) +     # 谐波
        0.1 * np.random.randn(len(t))           # 噪声
    )

    print(f"原始信号长度: {len(ecg_signal)}")
    print(f"采样频率: 360 Hz")
    print(f"信号时长: 10 秒\n")

    # 测试不同压缩因子
    factors = [2, 3, 4, 5]

    print("压缩因子\t压缩比\t\tPRD (%)\t\t得分")
    print("-" * 50)

    best_score = 0
    best_factor = 2

    for factor in factors:
        compressor = SimpleECGCompressor(compression_factor=factor)
        reconstructed, cr = compressor.compress_and_reconstruct(ecg_signal)

        # 计算PRD
        prd = (np.linalg.norm(ecg_signal - reconstructed) /
               np.linalg.norm(ecg_signal - np.mean(ecg_signal))) * 100

        # 计算得分
        score = cr / (prd + 1e-6)

        print(f"{factor}\t\t{cr:.2f}\t\t{prd:.4f}\t\t{score:.2f}")

        if score > best_score:
            best_score = score
            best_factor = factor

    print(f"\n最佳压缩因子: {best_factor}")
    print(f"最佳得分: {best_score:.2f}")

    # 详细分析最佳结果
    print(f"\n=== 最佳结果详细分析 ===")
    best_compressor = SimpleECGCompressor(compression_factor=best_factor)
    best_reconstructed, best_cr = best_compressor.compress_and_reconstruct(ecg_signal)

    best_prd = (np.linalg.norm(ecg_signal - best_reconstructed) /
                np.linalg.norm(ecg_signal - np.mean(ecg_signal))) * 100

    print(f"压缩比: {best_cr:.4f}")
    print(f"PRD: {best_prd:.4f}%")
    print(f"最终得分: {best_score:.4f}")
    print(f"重建误差 (RMSE): {np.sqrt(np.mean((ecg_signal - best_reconstructed)**2)):.6f}")
    print(f"信号保真度: {(1 - best_prd/100)*100:.2f}%")


if __name__ == "__main__":
    demo_simple_compression()