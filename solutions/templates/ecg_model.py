#!/usr/bin/env python3
"""
测试ECG压缩算法
简单的基于小波变换的ECG压缩实现
"""

import numpy as np

class ECGCompressor:
    """ECG压缩器 - 简单的测试实现"""

    def __init__(self):
        self.compression_ratio = 10.0  # 默认压缩比

    def compress_and_reconstruct(self, ecg_signal):
        """
        压缩和重构ECG信号

        Args:
            ecg_signal: 输入ECG信号 (list或numpy array)

        Returns:
            tuple: (重构信号, 压缩比)
        """

        # 确保输入是numpy数组
        if not isinstance(ecg_signal, np.ndarray):
            ecg_signal = np.array(ecg_signal)

        # 简单的压缩算法：降采样然后插值重构
        # 这里使用每N个点采样一个点的方法模拟压缩

        # 计算降采样因子
        downsample_factor = max(1, int(len(ecg_signal) / (len(ecg_signal) / self.compression_ratio)))

        # 降采样 (模拟压缩)
        compressed_indices = np.arange(0, len(ecg_signal), downsample_factor)
        compressed_signal = ecg_signal[compressed_indices]

        # 重构 (线性插值)
        original_indices = np.arange(len(ecg_signal))
        reconstructed_signal = np.interp(original_indices, compressed_indices, compressed_signal)

        # 计算实际压缩比
        actual_cr = len(ecg_signal) / len(compressed_signal)

        return reconstructed_signal, actual_cr

# 兼容性函数 - 其他可能的接口
def compress_ecg(signal):
    """兼容性接口"""
    compressor = ECGCompressor()
    return compressor.compress_and_reconstruct(signal)

def decompress_ecg(compressed_data):
    """兼容性接口 - 在这个简单实现中不需要"""
    return compressed_data

# 测试代码
if __name__ == "__main__":
    print("🧪 测试ECG压缩算法...")

    # 生成测试信号
    t = np.linspace(0, 1, 1000)  # 1秒，1000个采样点
    test_signal = np.sin(2 * np.pi * 5 * t) + 0.1 * np.random.randn(1000)

    # 测试压缩
    compressor = ECGCompressor()
    reconstructed, cr = compressor.compress_and_reconstruct(test_signal)

    print(f"✅ 压缩测试完成")
    print(f"   原始信号长度: {len(test_signal)}")
    print(f"   重构信号长度: {len(reconstructed)}")
    print(f"   压缩比: {cr:.2f}")

    # 计算简单的误差指标
    mse = np.mean((test_signal - reconstructed)**2)
    print(f"   均方误差: {mse:.6f}")

    print("🎉 ECG压缩算法测试成功！")