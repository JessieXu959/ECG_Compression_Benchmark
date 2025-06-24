"""
ECG Compression Challenge - Example 2: Wavelet Compression
==========================================================

这是一个中等复杂度的ECG压缩算法示例，使用小波变换。
适合有一定信号处理基础的参赛者。

算法特点:
- 使用离散小波变换(DWT)
- 自适应阈值选择
- 较好的压缩效果
- 压缩比约5-20倍

依赖: pip install pywt

作者: Starter Kit Team
"""

import numpy as np
try:
    import pywt
    PYWT_AVAILABLE = True
except ImportError:
    PYWT_AVAILABLE = False
    print("警告: 请安装pywt库 -> pip install pywt")


class WaveletECGCompressor:
    """
    基于小波变换的ECG压缩器

    使用离散小波变换进行压缩和重建
    """

    def __init__(self, wavelet='db4', levels=4, threshold_mode='soft'):
        """
        初始化小波压缩器

        参数:
            wavelet (str): 小波基函数，推荐 'db4', 'haar', 'bior4.4'
            levels (int): 分解层数，建议3-6
            threshold_mode (str): 阈值模式 'soft' 或 'hard'
        """
        if not PYWT_AVAILABLE:
            raise ImportError("需要安装pywt库: pip install pywt")

        self.wavelet = wavelet
        self.levels = levels
        self.threshold_mode = threshold_mode

        # 压缩参数
        self.threshold_ratio = 0.1  # 阈值比例
        self.energy_retention = 0.95  # 能量保持比例

    def compress_and_reconstruct(self, ecg_signal):
        """
        小波压缩和重建ECG信号

        参数:
            ecg_signal (numpy.ndarray): 输入ECG信号

        返回:
            tuple: (重建信号, 压缩比)
        """
        if not PYWT_AVAILABLE:
            # 降级到简单压缩
            return self._simple_fallback(ecg_signal)

        # 1. 小波分解
        coeffs = pywt.wavedec(ecg_signal, self.wavelet, level=self.levels)

        # 2. 自适应阈值计算
        threshold = self._calculate_adaptive_threshold(coeffs)

        # 3. 系数阈值处理
        coeffs_thresh = self._apply_threshold(coeffs, threshold)

        # 4. 计算压缩比
        original_size = len(ecg_signal)
        compressed_size = self._estimate_compressed_size(coeffs_thresh)
        compression_ratio = original_size / max(compressed_size, 1)

        # 5. 小波重建
        reconstructed = pywt.waverec(coeffs_thresh, self.wavelet)

        # 6. 长度调整
        if len(reconstructed) != len(ecg_signal):
            reconstructed = reconstructed[:len(ecg_signal)]

        return reconstructed, compression_ratio

    def _calculate_adaptive_threshold(self, coeffs):
        """
        计算自适应阈值

        基于信号能量分布自动选择阈值
        """
        # 计算所有系数的能量
        all_coeffs = np.concatenate([c.flatten() for c in coeffs[1:]])  # 跳过近似系数

        # 方法1: 基于能量保持的阈值
        squared_coeffs = np.sort(np.abs(all_coeffs))**2
        total_energy = np.sum(squared_coeffs)
        target_energy = total_energy * (1 - self.energy_retention)

        cumulative_energy = np.cumsum(squared_coeffs)
        threshold_idx = np.searchsorted(cumulative_energy, target_energy)

        if threshold_idx < len(squared_coeffs):
            energy_threshold = np.sqrt(squared_coeffs[threshold_idx])
        else:
            energy_threshold = 0

        # 方法2: 基于统计的阈值
        sigma = np.median(np.abs(all_coeffs)) / 0.6745  # 稳健的噪声估计
        n = len(all_coeffs)
        stat_threshold = sigma * np.sqrt(2 * np.log(n))

        # 方法3: 基于比例的阈值
        ratio_threshold = self.threshold_ratio * np.max(np.abs(all_coeffs))

        # 选择合适的阈值
        threshold = max(min(energy_threshold, stat_threshold), ratio_threshold)

        return threshold

    def _apply_threshold(self, coeffs, threshold):
        """
        对小波系数应用阈值处理
        """
        coeffs_thresh = []

        # 保留近似系数(低频成分)
        coeffs_thresh.append(coeffs[0])

        # 对细节系数应用阈值
        for i in range(1, len(coeffs)):
            if self.threshold_mode == 'soft':
                thresh_coeffs = pywt.threshold(coeffs[i], threshold, mode='soft')
            else:
                thresh_coeffs = pywt.threshold(coeffs[i], threshold, mode='hard')

            coeffs_thresh.append(thresh_coeffs)

        return coeffs_thresh

    def _estimate_compressed_size(self, coeffs_thresh):
        """
        估计压缩后的大小
        """
        # 计算非零系数的数量
        non_zero_count = 0
        for c in coeffs_thresh:
            non_zero_count += np.count_nonzero(c)

        # 假设每个非零系数需要额外的位置信息
        # 这是一个简化的估计
        estimated_size = non_zero_count * 1.5  # 系数值 + 位置信息

        return max(estimated_size, 1)

    def _simple_fallback(self, ecg_signal):
        """
        如果没有pywt库，使用简单的降采样方法
        """
        factor = 4  # 压缩因子
        compressed = ecg_signal[::factor]

        # 线性插值重建
        x_old = np.arange(0, len(ecg_signal), factor)
        x_new = np.arange(len(ecg_signal))
        reconstructed = np.interp(x_new, x_old, compressed)

        compression_ratio = len(ecg_signal) / len(compressed)

        return reconstructed, compression_ratio


def demo_wavelet_compression():
    """
    演示小波压缩算法
    """
    print("=== 小波ECG压缩算法演示 ===\n")

    if not PYWT_AVAILABLE:
        print("警告: pywt库未安装，将使用简化演示")
        print("完整体验请运行: pip install pywt\n")

    # 生成更复杂的模拟ECG信号
    t = np.linspace(0, 10, 3600)  # 10秒, 360Hz

    # 模拟真实ECG信号：P波、QRS波、T波
    ecg_signal = np.zeros_like(t)
    heart_rate = 72  # 每分钟心跳数
    beat_interval = 60 / heart_rate  # 心跳间隔(秒)

    for beat_time in np.arange(0, 10, beat_interval):
        # P波
        p_wave = 0.2 * np.exp(-50 * (t - beat_time - 0.1)**2)
        # QRS波群
        qrs_wave = -1.5 * np.exp(-200 * (t - beat_time)**2) + 0.8 * np.exp(-100 * (t - beat_time - 0.02)**2)
        # T波
        t_wave = 0.3 * np.exp(-20 * (t - beat_time + 0.2)**2)

        ecg_signal += p_wave + qrs_wave + t_wave

    # 添加噪声
    ecg_signal += 0.05 * np.random.randn(len(t))

    print(f"原始信号长度: {len(ecg_signal)}")
    print(f"采样频率: 360 Hz")
    print(f"信号时长: 10 秒")
    print(f"心率: {heart_rate} BPM\n")

    # 测试不同小波基
    wavelets = ['db4', 'haar', 'bior4.4'] if PYWT_AVAILABLE else ['fallback']
    levels_list = [3, 4, 5] if PYWT_AVAILABLE else [4]

    print("小波基\t\t层数\t压缩比\t\tPRD (%)\t\t得分")
    print("-" * 65)

    best_score = 0
    best_config = None

    for wavelet in wavelets:
        for levels in levels_list:
            try:
                compressor = WaveletECGCompressor(
                    wavelet=wavelet,
                    levels=levels,
                    threshold_mode='soft'
                )

                reconstructed, cr = compressor.compress_and_reconstruct(ecg_signal)

                # 计算PRD
                prd = (np.linalg.norm(ecg_signal - reconstructed) /
                       np.linalg.norm(ecg_signal - np.mean(ecg_signal))) * 100

                # 计算得分
                score = cr / (prd + 1e-6)

                print(f"{wavelet}\t\t{levels}\t{cr:.2f}\t\t{prd:.4f}\t\t{score:.2f}")

                if score > best_score:
                    best_score = score
                    best_config = (wavelet, levels)

            except Exception as e:
                print(f"{wavelet}\t\t{levels}\t错误: {str(e)}")

    if best_config:
        print(f"\n最佳配置: 小波={best_config[0]}, 层数={best_config[1]}")
        print(f"最佳得分: {best_score:.2f}")

        # 详细分析最佳结果
        print(f"\n=== 最佳结果详细分析 ===")
        best_compressor = WaveletECGCompressor(
            wavelet=best_config[0],
            levels=best_config[1]
        )
        best_reconstructed, best_cr = best_compressor.compress_and_reconstruct(ecg_signal)

        best_prd = (np.linalg.norm(ecg_signal - best_reconstructed) /
                    np.linalg.norm(ecg_signal - np.mean(ecg_signal))) * 100

        print(f"压缩比: {best_cr:.4f}")
        print(f"PRD: {best_prd:.4f}%")
        print(f"最终得分: {best_score:.4f}")
        print(f"重建误差 (RMSE): {np.sqrt(np.mean((ecg_signal - best_reconstructed)**2)):.6f}")

        # 信号质量分析
        correlation = np.corrcoef(ecg_signal, best_reconstructed)[0, 1]
        print(f"信号相关性: {correlation:.6f}")
        print(f"信号保真度: {(1 - best_prd/100)*100:.2f}%")


if __name__ == "__main__":
    demo_wavelet_compression()