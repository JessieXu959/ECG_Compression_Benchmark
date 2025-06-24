"""
ECG Compression Challenge - Backup Interface
============================================

这是备用的命令行接口文件。
主要用于兼容旧版本提交格式和本地测试。

推荐使用: ecg_model.py (标准接口)
备用选项: solve.py (此文件)

使用方法:
    python solve.py --input ecg_data.npy --output result.npy

作者: [您的团队名称]
"""

import sys
import argparse
import numpy as np
from pathlib import Path

# 尝试导入主算法模块
try:
    from ecg_model import ECGCompressor
    print("✓ 成功导入 ecg_model.ECGCompressor")
except ImportError:
    print("⚠ 无法导入 ecg_model.py，使用备用实现")
    ECGCompressor = None


def simple_compress_reconstruct(ecg_signal):
    """
    简单的备用压缩算法

    如果无法导入主算法，使用此备用实现
    """
    # 简单降采样压缩
    compression_factor = 2
    compressed = ecg_signal[::compression_factor]

    # 线性插值重建
    x_compressed = np.arange(len(compressed))
    x_target = np.linspace(0, len(compressed)-1, len(ecg_signal))
    reconstructed = np.interp(x_target, x_compressed, compressed)

    # 计算压缩比
    compression_ratio = len(ecg_signal) / len(compressed)

    return reconstructed, compression_ratio


def main():
    """
    主函数 - 命令行接口
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='ECG压缩算法')
    parser.add_argument('--input', '-i', required=True, help='输入ECG数据文件(.npy)')
    parser.add_argument('--output', '-o', required=True, help='输出重建信号文件(.npy)')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')

    args = parser.parse_args()

    try:
        # 读取输入数据
        if args.verbose:
            print(f"正在读取: {args.input}")

        ecg_data = np.load(args.input)

        if args.verbose:
            print(f"输入数据形状: {ecg_data.shape}")
            print(f"数据类型: {ecg_data.dtype}")

        # 确保是一维数组
        if len(ecg_data.shape) > 1:
            ecg_data = ecg_data.flatten()

        # 运行压缩算法
        if ECGCompressor is not None:
            # 使用主算法
            compressor = ECGCompressor()
            reconstructed, compression_ratio = compressor.compress_and_reconstruct(ecg_data)
            algorithm_used = "ECGCompressor (主算法)"
        else:
            # 使用备用算法
            reconstructed, compression_ratio = simple_compress_reconstruct(ecg_data)
            algorithm_used = "SimpleCompressor (备用算法)"

        # 计算评估指标
        prd = np.linalg.norm(ecg_data - reconstructed) / np.linalg.norm(ecg_data - np.mean(ecg_data)) * 100
        score = compression_ratio / (prd + 1e-6)

        # 保存结果
        np.save(args.output, reconstructed)

        # 输出结果
        print(f"\n=== ECG压缩结果 ===")
        print(f"使用算法: {algorithm_used}")
        print(f"原始信号长度: {len(ecg_data)}")
        print(f"重建信号长度: {len(reconstructed)}")
        print(f"压缩比 (CR): {compression_ratio:.4f}")
        print(f"PRD: {prd:.4f}%")
        print(f"最终得分: {score:.4f}")
        print(f"输出文件: {args.output}")

        if args.verbose:
            print(f"\n=== 详细统计 ===")
            print(f"原始信号范围: [{np.min(ecg_data):.4f}, {np.max(ecg_data):.4f}]")
            print(f"重建信号范围: [{np.min(reconstructed):.4f}, {np.max(reconstructed):.4f}]")
            print(f"信号均值差异: {abs(np.mean(ecg_data) - np.mean(reconstructed)):.6f}")
            print(f"信号标准差差异: {abs(np.std(ecg_data) - np.std(reconstructed)):.6f}")

        return 0

    except FileNotFoundError:
        print(f"错误: 无法找到输入文件 {args.input}")
        return 1

    except Exception as e:
        print(f"错误: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def validate_submission():
    """
    验证提交格式的辅助函数
    """
    print("=== 提交格式验证 ===")

    # 检查必需文件
    required_files = ['ecg_model.py']
    optional_files = ['solve.py', 'requirements.txt']

    current_dir = Path('.')

    print("检查必需文件:")
    for file in required_files:
        if (current_dir / file).exists():
            print(f"  ✓ {file} - 存在")
        else:
            print(f"  ✗ {file} - 缺失 (必需)")

    print("\n检查可选文件:")
    for file in optional_files:
        if (current_dir / file).exists():
            print(f"  ✓ {file} - 存在")
        else:
            print(f"  - {file} - 不存在 (可选)")

    # 测试算法接口
    print("\n测试算法接口:")
    try:
        if ECGCompressor is not None:
            compressor = ECGCompressor()

            # 生成测试数据
            test_signal = np.sin(np.linspace(0, 10, 1000))

            # 测试接口
            result = compressor.compress_and_reconstruct(test_signal)

            if isinstance(result, tuple) and len(result) == 2:
                reconstructed, cr = result
                if isinstance(reconstructed, np.ndarray) and isinstance(cr, (int, float)):
                    if len(reconstructed) == len(test_signal) and cr >= 1.0:
                        print(f"  ✓ 接口测试通过 (CR: {cr:.2f})")
                    else:
                        print(f"  ✗ 接口测试失败: 长度或压缩比不正确")
                else:
                    print(f"  ✗ 接口测试失败: 返回类型错误")
            else:
                print(f"  ✗ 接口测试失败: 返回格式错误")
        else:
            print(f"  - 无法导入ECGCompressor，跳过接口测试")

    except Exception as e:
        print(f"  ✗ 接口测试失败: {str(e)}")


if __name__ == "__main__":
    # 如果没有命令行参数，运行验证
    if len(sys.argv) == 1:
        validate_submission()
    else:
        sys.exit(main())