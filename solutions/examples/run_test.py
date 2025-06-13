#!/usr/bin/env python3
"""
测试脚本 - 用于验证ECG压缩算法的输出格式和评分指标
"""
import os
import sys
import numpy as np
import scipy.io as sio
from ecg_model import ECGCompressor

def calculate_prd(original, reconstructed):
    """计算PRD (Percent Root-mean-square Difference)"""
    f_mean = np.mean(original)
    numerator = np.linalg.norm(original - reconstructed, 2)
    denominator = np.linalg.norm(original - f_mean, 2)

    EPSILON = 1e-10
    if denominator < EPSILON:
        return float('inf')

    prd = (numerator / denominator) * 100
    return prd

def calculate_final_score(cr, prd):
    """使用评分公式计算最终得分: Score = CR / (PRD + epsilon)"""
    EPSILON = 1e-6
    return cr / (prd + EPSILON)

def test_on_sample_data():
    """在示例数据上测试算法并打印评分信息"""
    # 生成测试数据 - 简单的正弦波形
    fs = 360  # 采样率
    duration = 5  # 秒
    t = np.arange(0, duration, 1/fs)
    ecg_signal = np.sin(2 * np.pi * 1 * t)  # 1Hz的正弦波

    print(f"测试数据大小: {len(ecg_signal)} 样本")

    # 压缩和重建
    compressor = ECGCompressor()
    reconstructed, cr = compressor.compress_and_reconstruct(ecg_signal)

    # 计算评分指标
    prd = calculate_prd(ecg_signal, reconstructed)
    score = calculate_final_score(cr, prd)

    # 打印结果
    print(f"\n===== 测试结果 =====")
    print(f"压缩比 (CR): {cr:.2f}")
    print(f"百分比均方根差异 (PRD): {prd:.4f}%")
    print(f"最终得分 (Score): {score:.2f}")

    # 检查结果的有效性
    if cr <= 0 or np.isnan(cr):
        print("⚠️ 警告: CR无效或为零")
    if prd < 0 or np.isnan(prd):
        print("⚠️ 警告: PRD无效")
    if score <= 0 or np.isnan(score):
        print("⚠️ 警告: 得分无效")

    # 保存结果以检查格式
    output_path = "test_output.mat"
    sio.savemat(output_path, {"f_recon": reconstructed, "CR_val": cr})
    print(f"结果已保存至: {output_path}")

    # 检查保存的文件
    saved_data = sio.loadmat(output_path)
    print("\n保存的文件内容:")
    for key in saved_data:
        if key.startswith('__'):  # 跳过内部变量
            continue
        print(f"键: {key}, 形状: {saved_data[key].shape}")

def test_on_real_data():
    """在实际评测数据集上测试算法"""
    # 检查评测数据文件夹是否存在
    data_dir = "../evaluation_data"
    if not os.path.exists(data_dir):
        print(f"❌ 评测数据文件夹未找到: {data_dir}")
        return

    print("\n===== 在实际评测数据上测试 =====")
    # 查找所有.mat文件
    dataset_files = [f for f in os.listdir(data_dir) if f.endswith('.mat')]

    if not dataset_files:
        print("❌ 未找到评测数据文件")
        return

    for dataset_file in dataset_files:
        file_path = os.path.join(data_dir, dataset_file)
        try:
            # 读取数据
            mat_data = sio.loadmat(file_path)
            ecg_signal = mat_data["ecg"].flatten()

            print(f"\n处理数据集: {dataset_file}")
            print(f"信号大小: {len(ecg_signal)} 样本")

            # 压缩和重建
            compressor = ECGCompressor()
            reconstructed, cr = compressor.compress_and_reconstruct(ecg_signal)

            # 计算评分指标
            prd = calculate_prd(ecg_signal, reconstructed)
            score = calculate_final_score(cr, prd)

            # 打印结果
            print(f"压缩比 (CR): {cr:.2f}")
            print(f"百分比均方根差异 (PRD): {prd:.4f}%")
            print(f"最终得分 (Score): {score:.2f}")

        except Exception as e:
            print(f"❌ 处理数据集时出错: {dataset_file}")
            print(f"错误: {str(e)}")

if __name__ == "__main__":
    print("===== ECG压缩算法测试 =====\n")

    # 测试在样本数据上
    test_on_sample_data()

    # 测试在实际评测数据上
    test_on_real_data()

    print("\n测试完成")