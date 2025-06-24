"""
ECG Compression Challenge - Test Data Generator
===============================================

生成模拟ECG数据用于本地测试和算法开发。
这些数据模拟真实ECG信号的特征，但不用于最终评估。

使用方法:
    python generate_test_data.py

输出文件:
    - test_ecg_simple.npy: 简单正弦波ECG
    - test_ecg_realistic.npy: 模拟真实ECG
    - test_ecg_noisy.npy: 含噪声ECG
    - test_ecg_arrhythmia.npy: 心律不齐ECG

作者: Starter Kit Team
"""

import numpy as np
import os
from pathlib import Path


def generate_simple_ecg(duration=10, sampling_rate=360):
    """
    生成简单的正弦波ECG信号

    参数:
        duration (float): 信号时长(秒)
        sampling_rate (int): 采样率(Hz)

    返回:
        numpy.ndarray: ECG信号
    """
    t = np.linspace(0, duration, int(duration * sampling_rate))

    # 基础心率信号 (约72 BPM)
    heart_rate = 1.2  # Hz
    ecg = np.sin(2 * np.pi * heart_rate * t)

    # 添加谐波成分
    ecg += 0.5 * np.sin(2 * np.pi * 2.4 * t)
    ecg += 0.3 * np.sin(2 * np.pi * 3.6 * t)

    # 归一化
    ecg = ecg / np.max(np.abs(ecg))

    return ecg


def generate_realistic_ecg(duration=10, sampling_rate=360, heart_rate=72):
    """
    生成模拟真实ECG信号

    包含P波、QRS波群、T波等特征

    参数:
        duration (float): 信号时长(秒)
        sampling_rate (int): 采样率(Hz)
        heart_rate (int): 心率(BPM)

    返回:
        numpy.ndarray: 真实ECG信号
    """
    t = np.linspace(0, duration, int(duration * sampling_rate))
    ecg = np.zeros_like(t)

    beat_interval = 60 / heart_rate  # 心跳间隔(秒)

    # 为每个心跳生成PQRST波形
    for beat_start in np.arange(0, duration, beat_interval):
        # P波 (心房除极)
        p_center = beat_start + 0.08
        p_width = 0.04
        p_amplitude = 0.15
        p_wave = p_amplitude * np.exp(-0.5 * ((t - p_center) / p_width)**2)

        # QRS波群 (心室除极)
        qrs_center = beat_start + 0.15

        # Q波 (小的负向波)
        q_center = qrs_center - 0.02
        q_width = 0.01
        q_amplitude = -0.1
        q_wave = q_amplitude * np.exp(-0.5 * ((t - q_center) / q_width)**2)

        # R波 (主要正向波)
        r_center = qrs_center
        r_width = 0.015
        r_amplitude = 1.0
        r_wave = r_amplitude * np.exp(-0.5 * ((t - r_center) / r_width)**2)

        # S波 (负向波)
        s_center = qrs_center + 0.025
        s_width = 0.02
        s_amplitude = -0.3
        s_wave = s_amplitude * np.exp(-0.5 * ((t - s_center) / s_width)**2)

        # T波 (心室复极)
        t_center = beat_start + 0.35
        t_width = 0.08
        t_amplitude = 0.25
        t_wave = t_amplitude * np.exp(-0.5 * ((t - t_center) / t_width)**2)

        # 组合所有波形
        ecg += p_wave + q_wave + r_wave + s_wave + t_wave

    return ecg


def generate_noisy_ecg(duration=10, sampling_rate=360, noise_level=0.1):
    """
    生成含噪声的ECG信号

    参数:
        duration (float): 信号时长(秒)
        sampling_rate (int): 采样率(Hz)
        noise_level (float): 噪声水平

    返回:
        numpy.ndarray: 含噪声ECG信号
    """
    # 基础ECG信号
    ecg_clean = generate_realistic_ecg(duration, sampling_rate)

    # 添加白噪声
    white_noise = noise_level * np.random.randn(len(ecg_clean))

    # 添加50Hz工频干扰
    t = np.linspace(0, duration, len(ecg_clean))
    powerline_noise = 0.05 * np.sin(2 * np.pi * 50 * t)

    # 添加基线漂移
    baseline_drift = 0.1 * np.sin(2 * np.pi * 0.5 * t)

    # 添加肌电干扰 (EMG)
    emg_noise = 0.03 * np.random.randn(len(ecg_clean))
    b, a = signal.butter(4, [20, 40], btype='band', fs=sampling_rate)
    emg_noise = signal.filtfilt(b, a, emg_noise)

    ecg_noisy = ecg_clean + white_noise + powerline_noise + baseline_drift + emg_noise

    return ecg_noisy


def generate_arrhythmia_ecg(duration=10, sampling_rate=360):
    """
    生成心律不齐ECG信号

    包含不规则心跳间隔和异常波形

    参数:
        duration (float): 信号时长(秒)
        sampling_rate (int): 采样率(Hz)

    返回:
        numpy.ndarray: 心律不齐ECG信号
    """
    t = np.linspace(0, duration, int(duration * sampling_rate))
    ecg = np.zeros_like(t)

    # 不规则心跳间隔
    base_interval = 60 / 75  # 基础心率 75 BPM
    current_time = 0
    beat_count = 0

    while current_time < duration:
        # 随机变化心跳间隔 (±20%)
        interval_variation = np.random.uniform(0.8, 1.2)
        beat_interval = base_interval * interval_variation

        # 偶尔插入早搏
        if np.random.random() < 0.1:  # 10%概率早搏
            beat_interval *= 0.7
            amplitude_factor = 0.8  # 早搏幅度稍小
        else:
            amplitude_factor = 1.0

        # 生成单个心跳
        beat_start = current_time

        # 正常PQRST波形 (简化版)
        # P波
        p_center = beat_start + 0.08
        p_wave = 0.15 * amplitude_factor * np.exp(-0.5 * ((t - p_center) / 0.04)**2)

        # QRS波群
        qrs_center = beat_start + 0.15
        r_wave = 1.0 * amplitude_factor * np.exp(-0.5 * ((t - qrs_center) / 0.015)**2)
        s_wave = -0.3 * amplitude_factor * np.exp(-0.5 * ((t - qrs_center + 0.025) / 0.02)**2)

        # T波
        t_center = beat_start + 0.35
        t_wave = 0.25 * amplitude_factor * np.exp(-0.5 * ((t - t_center) / 0.08)**2)

        ecg += p_wave + r_wave + s_wave + t_wave

        current_time += beat_interval
        beat_count += 1

    # 添加轻微噪声
    ecg += 0.05 * np.random.randn(len(ecg))

    return ecg


def save_test_data():
    """
    生成并保存所有测试数据
    """
    # 确保输出目录存在
    output_dir = Path(__file__).parent
    output_dir.mkdir(exist_ok=True)

    print("生成ECG测试数据...")

    # 生成不同类型的ECG数据
    datasets = {
        'test_ecg_simple.npy': generate_simple_ecg(),
        'test_ecg_realistic.npy': generate_realistic_ecg(),
        'test_ecg_noisy.npy': generate_noisy_ecg(),
        'test_ecg_arrhythmia.npy': generate_arrhythmia_ecg()
    }

    # 保存数据并显示统计信息
    for filename, data in datasets.items():
        filepath = output_dir / filename
        np.save(filepath, data)

        print(f"\n✓ 保存: {filename}")
        print(f"  长度: {len(data)} 样本")
        print(f"  时长: {len(data)/360:.1f} 秒")
        print(f"  范围: [{np.min(data):.4f}, {np.max(data):.4f}]")
        print(f"  均值: {np.mean(data):.4f}")
        print(f"  标准差: {np.std(data):.4f}")

    print(f"\n所有测试数据已保存到: {output_dir}")
    print("\n使用方法:")
    print("  import numpy as np")
    print("  ecg_data = np.load('test_ecg_realistic.npy')")
    print("  # 然后用您的算法处理 ecg_data")


def demonstrate_data():
    """
    演示生成的数据特征
    """
    print("=== ECG测试数据演示 ===\n")

    try:
        import matplotlib.pyplot as plt

        # 生成示例数据
        simple = generate_simple_ecg(duration=2)
        realistic = generate_realistic_ecg(duration=2)
        noisy = generate_noisy_ecg(duration=2)
        arrhythmia = generate_arrhythmia_ecg(duration=2)

        # 创建时间轴
        t = np.linspace(0, 2, len(simple))

        # 绘制图形
        fig, axes = plt.subplots(4, 1, figsize=(12, 10))

        axes[0].plot(t, simple)
        axes[0].set_title('Simple ECG (正弦波模拟)')
        axes[0].set_ylabel('振幅')

        axes[1].plot(t, realistic)
        axes[1].set_title('Realistic ECG (真实波形模拟)')
        axes[1].set_ylabel('振幅')

        axes[2].plot(t, noisy)
        axes[2].set_title('Noisy ECG (含噪声)')
        axes[2].set_ylabel('振幅')

        axes[3].plot(t, arrhythmia)
        axes[3].set_title('Arrhythmia ECG (心律不齐)')
        axes[3].set_ylabel('振幅')
        axes[3].set_xlabel('时间 (秒)')

        plt.tight_layout()
        plt.savefig('ecg_test_data_preview.png', dpi=150, bbox_inches='tight')
        plt.show()

        print("✓ 图形已保存为 'ecg_test_data_preview.png'")

    except ImportError:
        print("matplotlib未安装，跳过可视化演示")
        print("安装matplotlib查看图形: pip install matplotlib")


# 需要scipy.signal用于滤波
try:
    from scipy import signal
except ImportError:
    print("警告: scipy未安装，部分功能可能受限")
    print("建议安装: pip install scipy")


if __name__ == "__main__":
    # 保存测试数据
    save_test_data()

    # 演示数据 (可选)
    print("\n" + "="*50)
    demonstrate_data()