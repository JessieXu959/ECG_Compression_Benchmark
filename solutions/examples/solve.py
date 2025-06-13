# solve.py
import os
import sys
import numpy as np
import scipy.io as sio
from ecg_model import ECGCompressor

def main():
    # 1) 解析命令行参数
    if len(sys.argv) < 3:
        print("Usage: python solve.py <input_data_dir> <output_dir>")
        sys.exit(1)
    input_data_dir = sys.argv[1]  # /input_data
    output_dir = sys.argv[2]

    print(f"输入目录: {input_data_dir}")
    print(f"输出目录: {output_dir}")

    # 2) 遍历所有数据集（假设数据集名称已知）
    dataset_names = [
        "PhysioNet_MITBIH_rec117_5min",
        "PhysioNet_MITBIH_rec119_5min",
        "PhysioNet_MITBIH_rec201_10min"  # 添加了第三个数据集
    ]

    print(f"将处理 {len(dataset_names)} 个数据集")

    for ds_name in dataset_names:
        print(f"\n===== 处理数据集: {ds_name} =====")
        # 2.1) 读取输入数据
        input_path = os.path.join(input_data_dir, f"{ds_name}.mat")
        try:
            print(f"尝试读取: {input_path}")
            mat_data = sio.loadmat(input_path)
            print(f"数据键: {[k for k in mat_data.keys() if not k.startswith('__')]}")

            if "ecg" in mat_data:
                ecg_signal = mat_data["ecg"].flatten()
                print(f"读取ECG信号成功，形状: {ecg_signal.shape}, 类型: {ecg_signal.dtype}")
            else:
                print(f"错误: 文件中没有'ecg'键")
                continue
        except (FileNotFoundError, KeyError) as e:
            print(f"错误加载 {input_path}: {e}")
            continue

        # 2.2) 调用压缩算法
        print("开始压缩和重建...")
        compressor = ECGCompressor()
        f_recon, cr_val = compressor.compress_and_reconstruct(ecg_signal)

        # 2.3) 确保重建信号形状匹配原始信号
        print(f"重建前信号形状: {f_recon.shape}")
        f_recon = f_recon.reshape(ecg_signal.shape)
        print(f"重建后信号形状: {f_recon.shape}")

        # 2.4) 保存预测结果（必须为 .mat 文件，包含 f_recon 和 CR_val）
        output_path = os.path.join(output_dir, f"{ds_name}_pred.mat")
        print(f"保存结果到: {output_path}")

        # 确保数据类型正确
        result_dict = {
            "f_recon": f_recon.astype(np.float64),
            "CR_val": float(cr_val),

            # 尝试其他可能的键名
            "reconstructed": f_recon.astype(np.float64),
            "compression_ratio": float(cr_val),
            "cr": float(cr_val)
        }

        sio.savemat(output_path, result_dict)
        print(f"已保存结果文件: {output_path}")
        print(f"包含键: {list(result_dict.keys())}")

        # 验证保存的文件
        try:
            check = sio.loadmat(output_path)
            print(f"验证文件内容: {[k for k in check.keys() if not k.startswith('__')]}")
        except Exception as e:
            print(f"验证文件失败: {e}")

        print(f"完成处理 {ds_name}: CR={cr_val:.2f}")

    print("\n所有数据集处理完成!")

if __name__ == "__main__":
    try:
        print("===== ECG压缩处理开始 =====")
        main()
        print("===== ECG压缩处理成功完成 =====")
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)