"""
ECG Compression Challenge - Algorithm Template
==============================================

这是您的主要算法实现文件。请在ECGCompressor类中实现您的压缩算法。

重要提示:
1. 必须保持ECGCompressor类名和compress_and_reconstruct方法名不变
2. 输入是一维numpy数组(ECG信号)
3. 输出必须是(重建信号, 压缩比)的元组格式
4. 重建信号长度必须与原始信号相同
5. 压缩比必须大于1.0

作者: [您的团队名称]
日期: [提交日期]
算法描述: [简要描述您的算法原理]
"""

import numpy as np
from scipy import signal
# 添加您需要的其他导入


class ECGCompressor:
    """
    ECG信号压缩器类

    实现您的ECG压缩和重建算法
    """

    def __init__(self):
        """
        初始化压缩器

        在这里设置算法参数、预训练模型等
        """
        # 示例: 设置算法参数
        self.compression_factor = 2  # 压缩因子
        self.filter_order = 4        # 滤波器阶数

        # 您可以在这里添加更多初始化代码
        pass

    def compress_and_reconstruct(self, ecg_signal):
        """
        ECG信号压缩和重建的主要接口

        这是平台调用的主要方法，请在此实现您的算法逻辑

        参数:
            ecg_signal (numpy.ndarray): 输入的一维ECG信号

        返回:
            tuple: (reconstructed_signal, compression_ratio)
            - reconstructed_signal (numpy.ndarray): 重建的ECG信号，长度与输入相同
            - compression_ratio (float): 压缩比，必须 > 1.0

        评分公式:
            最终得分 = compression_ratio / (PRD + 1e-6)
            其中 PRD = ||original - reconstructed|| / ||original - mean(original)|| * 100
        """

        # 第一步: 输入验证
        if not isinstance(ecg_signal, np.ndarray):
            ecg_signal = np.array(ecg_signal)

        if len(ecg_signal.shape) != 1:
            raise ValueError("输入必须是一维数组")

        original_length = len(ecg_signal)

        # 第二步: 实现您的压缩算法
        # =================================

        # 示例算法1: 简单降采样压缩 (请替换为您的算法)
        compressed_signal = self._simple_downsample_compress(ecg_signal)

        # 示例算法2: 小波压缩 (注释掉，您可以选择使用)
        # compressed_signal = self._wavelet_compress(ecg_signal)

        # 示例算法3: 频域压缩 (注释掉，您可以选择使用)
        # compressed_signal = self._frequency_domain_compress(ecg_signal)

        # 第三步: 重建信号
        # =================
        reconstructed_signal = self._reconstruct_signal(compressed_signal, original_length)

        # 第四步: 计算压缩比
        # ==================
        original_size = len(ecg_signal) * 8  # 假设每个样本8字节
        compressed_size = len(compressed_signal) * 8  # 压缩后大小

        if compressed_size == 0:
            compression_ratio = 1.0
        else:
            compression_ratio = original_size / compressed_size

        # 确保压缩比大于1
        compression_ratio = max(compression_ratio, 1.0)

        # 第五步: 验证输出格式
        # ====================
        if len(reconstructed_signal) != original_length:
            # 如果长度不匹配，进行调整
            if len(reconstructed_signal) > original_length:
                reconstructed_signal = reconstructed_signal[:original_length]
            else:
                # 零填充或重复填充
                padding = original_length - len(reconstructed_signal)
                reconstructed_signal = np.pad(reconstructed_signal, (0, padding), mode='constant')

        return reconstructed_signal, float(compression_ratio)

    def _simple_downsample_compress(self, ecg_signal):
        """
        示例方法1: 简单降采样压缩

        这是一个基础示例，您应该实现更先进的算法
        """
        # 简单降采样: 每隔compression_factor取一个样本
        compressed = ecg_signal[::self.compression_factor]
        return compressed

    def _wavelet_compress(self, ecg_signal):
        """
        示例方法2: 小波压缩 (需要安装pywt)

        取消注释以使用此方法
        """
        # import pywt
        #
        # # 小波分解
        # coeffs = pywt.wavedec(ecg_signal, 'db4', level=4)
        #
        # # 阈值处理 (简单压缩)
        # threshold = 0.1 * np.max(np.abs(coeffs[0]))
        # coeffs_thresh = [pywt.threshold(c, threshold, mode='soft') for c in coeffs]
        #
        # return coeffs_thresh

        # 暂时返回简单压缩结果
        return self._simple_downsample_compress(ecg_signal)

    def _frequency_domain_compress(self, ecg_signal):
        """
        示例方法3: 频域压缩

        基于FFT的频域压缩方法
        """
        # FFT变换
        fft_signal = np.fft.fft(ecg_signal)

        # 保留主要频率成分 (简单截断)
        n_keep = len(fft_signal) // self.compression_factor
        compressed_fft = np.zeros_like(fft_signal)
        compressed_fft[:n_keep] = fft_signal[:n_keep]
        compressed_fft[-n_keep:] = fft_signal[-n_keep:]

        return compressed_fft

    def _reconstruct_signal(self, compressed_signal, target_length):
        """
        重建信号到原始长度

        参数:
            compressed_signal: 压缩后的信号
            target_length: 目标长度
        """

        # 方法1: 简单重复插值 (对应降采样)
        if isinstance(compressed_signal, np.ndarray) and len(compressed_signal.shape) == 1:
            # 线性插值重建
            x_compressed = np.arange(len(compressed_signal))
            x_target = np.linspace(0, len(compressed_signal)-1, target_length)
            reconstructed = np.interp(x_target, x_compressed, compressed_signal)
            return reconstructed

        # 方法2: 小波重建 (如果使用小波压缩)
        # if isinstance(compressed_signal, list):  # 小波系数
        #     import pywt
        #     reconstructed = pywt.waverec(compressed_signal, 'db4')
        #     return reconstructed[:target_length]

        # 方法3: 频域重建 (如果使用频域压缩)
        if np.iscomplexobj(compressed_signal):
            reconstructed = np.fft.ifft(compressed_signal).real
            return reconstructed[:target_length]

        # 默认: 重复填充
        if len(compressed_signal) == 0:
            return np.zeros(target_length)

        repeat_times = target_length // len(compressed_signal) + 1
        extended = np.tile(compressed_signal, repeat_times)
        return extended[:target_length]


# 用于测试的辅助函数 (可选)
def test_compressor():
    """
    本地测试函数
    """
    # 生成测试ECG信号
    t = np.linspace(0, 10, 3600)  # 10秒, 360Hz采样
    ecg_test = np.sin(2 * np.pi * 1.2 * t) + 0.5 * np.sin(2 * np.pi * 2.4 * t)
    ecg_test += 0.1 * np.random.randn(len(t))  # 添加噪声

    # 测试压缩器
    compressor = ECGCompressor()
    reconstructed, cr = compressor.compress_and_reconstruct(ecg_test)

    # 计算PRD
    prd = np.linalg.norm(ecg_test - reconstructed) / np.linalg.norm(ecg_test - np.mean(ecg_test)) * 100
    score = cr / (prd + 1e-6)

    print(f"测试结果:")
    print(f"  原始信号长度: {len(ecg_test)}")
    print(f"  重建信号长度: {len(reconstructed)}")
    print(f"  压缩比: {cr:.2f}")
    print(f"  PRD: {prd:.4f}%")
    print(f"  最终得分: {score:.2f}")

    return reconstructed, cr


if __name__ == "__main__":
    # 运行本地测试
    test_compressor()