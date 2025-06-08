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

    # 2) 遍历所有数据集（假设数据集名称已知）
    dataset_names = [
        "PhysioNet_MITBIH_rec117_5min",
        "PhysioNet_MITBIH_rec119_5min"
    ]

    for ds_name in dataset_names:
        # 2.1) 读取输入数据
        input_path = os.path.join(input_data_dir, f"{ds_name}.mat")
        try:
            mat_data = sio.loadmat(input_path)
            ecg_signal = mat_data["ecg"].flatten()
        except (FileNotFoundError, KeyError) as e:
            print(f"Error loading {input_path}: {e}")
            continue

        # 2.2) 调用压缩算法
        compressor = ECGCompressor()
        f_recon, cr_val = compressor.compress_and_reconstruct(ecg_signal)

        # 2.3) 确保重建信号形状匹配原始信号
        f_recon = f_recon.reshape(ecg_signal.shape)

        # 2.4) 保存预测结果（必须为 .mat 文件，包含 f_recon 和 CR_val）
        output_path = os.path.join(output_dir, f"{ds_name}_pred.mat")
        sio.savemat(output_path, {"f_recon": f_recon, "CR_val": cr_val})

if __name__ == "__main__":
    main()