import os
import sys
import json
import time
import numpy as np
import scipy.io as sio



# 这些路径是在 Codabench 容器里的“惯例”：
INPUT_DIR       = "/app/input_data"       # 放公共的输入 ECG 信号(有时也写 /app/input)
OUTPUT_DIR = "/app/output"        # 要把选手的预测/重建结果放在这里
PROGRAM_DIR     = "/app/program"          # 自己的 ingestion 程序所在位置
SUBMISSION_DIR  = "/app/ingested_program" # 选手提交的代码会解压到这里
sys.path.append(PROGRAM_DIR)
sys.path.append(SUBMISSION_DIR)

METADATA_FILE   = os.path.join(OUTPUT_DIR, "metadata.json")

def print_bar():
    print("-"*30)

def get_ecg_datasets():
    """
    返回本次要压缩/重建的 ECG 数据文件列表（不含后缀）。
    比如你在 /app/input_data/ 下放了两个 .mat 文件：
      - PhysioNet_MITBIH_rec117_5min.mat
      - PhysioNet_MITBIH_rec119_5min.mat
    这里就返回 ["PhysioNet_MITBIH_rec117_5min", "PhysioNet_MITBIH_rec119_5min"]。
    """
    return [
        "PhysioNet_MITBIH_rec117_5min",
        "PhysioNet_MITBIH_rec119_5min"
    ]

def load_mat_file(filepath):
    """读取 .mat 文件并返回其中的字典结构。"""
    return sio.loadmat(filepath)

def save_mat_file(filepath, data_dict):
    """把 data_dict 存到 .mat 文件里。"""
    sio.savemat(filepath, data_dict)

def main():
    print_bar()
    print("Starting ECG ingestion...")

    # 1. 记录开始时间
    start_time = time.time()

    # 2. 从选手提交包引入选手的函数 / 类
    #    假设参赛者提交了 "ecg_model.py"，其中有一个 "ECGCompressor" 类
    try:
        from ecg_model import ECGCompressor
    except ImportError:
        print("ERROR: Could not find `ecg_model.py` with `ECGCompressor` class in submission.")
        # 出错也可以考虑写一个 metadata.json 做提示，然后退出
        with open(METADATA_FILE, 'w') as f:
            json.dump({"error": "No ecg_model found."}, f)
        return

    # 3. 初始化选手的压缩器(或重建器)
    compressor = ECGCompressor()

    # 4. 获取数据集文件名列表
    datasets = get_ecg_datasets()

    # 5. 依次读取数据 -> 调用选手函数 -> 写出重建结果
    for ds_name in datasets:
        print_bar()
        print(f"Ingesting dataset: {ds_name}")

        # 4.1 读取原始ECG
        ecg_path = os.path.join(INPUT_DIR, ds_name + ".mat")
        if not os.path.exists(ecg_path):
            print(f"File {ecg_path} not found, skip.")
            continue
        
        ecg_dict = load_mat_file(ecg_path)
        if "ecg" not in ecg_dict:
            print(f"`ecg` variable not found in {ecg_path}, skip.")
            continue
        ecg_signal = ecg_dict["ecg"]  # 假设原始信号保存在 `ecg`

        # 4.2 调用选手代码进行压缩 & 重建
        #     这里就看你如何定义接口：可能 compressor.fit_transform(ecg_signal) 返回 (f_recon, CR_val)
        #     或者先 compressor.compress(...), 再 compressor.decompress(...)，等等。
        try:
            f_recon, cr_val = compressor.compress_and_reconstruct(ecg_signal)
        except Exception as e:
            print(f"Error during compression: {e}")
            f_recon = np.zeros_like(ecg_signal)
            cr_val = 1.0
        
        # 4.3 把结果写到 /app/input/res 下，文件命名与 scoring.py 相匹配
        #假设 scoring.py 期望 ds_name+"_pred.mat" 里有 `f_recon` 和 `CR_val`
        pred_mat_name = ds_name + "_pred.mat"
        pred_dict = {
            "f_recon": f_recon,
            "CR_val":  cr_val
        }
        save_mat_file(os.path.join(OUTPUT_DIR, pred_mat_name), pred_dict)
        print(f"Saved predictions to {pred_mat_name}")

    # 6. 记录总耗时
    duration = time.time() - start_time
    print(f"Ingestion finished. Total time: {duration:.2f} seconds.")

    # 7. 写出 metadata.json
    with open(METADATA_FILE, 'w') as f:
        json.dump({"duration": duration}, f)

    print_bar()

if __name__ == "__main__":
    main()
