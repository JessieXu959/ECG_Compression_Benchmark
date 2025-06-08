import os
import json
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# 评测容器路径
INPUT_DIR = "/app/input"
REF_DIR = os.path.join(INPUT_DIR, "ref")  # Ground truth
# scoring.py

RES_DIR = os.path.join(INPUT_DIR, "res")  # 正确路径：/app/input/res
OUTPUT_DIR = "/app/output"  # 评分结果写入这里

SCORES_FILE = os.path.join(OUTPUT_DIR, "scores.json")
DETAIL_FILE = os.path.join(OUTPUT_DIR, "detailed_results.html")

# 设定 EPSILON 避免除零
EPSILON = 1e-6

def get_dataset_names():
    """ 返回要评测的数据集名称（不带后缀） """
    return [
        "PhysioNet_MITBIH_rec117_5min",
        "PhysioNet_MITBIH_rec119_5min"
    ]

def load_matlab_file(filepath, var_name=None):
    """ 读取 .mat 文件 """
    data_dict = sio.loadmat(filepath)
    if var_name is None:
        return data_dict
    elif var_name in data_dict:
        return data_dict[var_name]
    else:
        raise KeyError(f"Variable '{var_name}' not found in {filepath}")

def compute_PRD(f, f_recon):
    """ 计算 PRD(%) """
    f_mean = np.mean(f)
    numerator = np.linalg.norm(f - f_recon, 2)
    denominator = np.linalg.norm(f - f_mean, 2)
    
    if denominator < EPSILON:
        return float('inf')  # 处理全零信号
    
    prd = (numerator / denominator) * 100
    return prd

def make_figure(scores_dict):
    """ 生成评分可视化图表 """
    dataset_names = list(scores_dict.keys())
    scores = list(scores_dict.values())

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(dataset_names, scores, color='blue', alpha=0.7)
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Score")
    ax.set_title("ECG Compression Scores")
    ax.set_xticklabels(dataset_names, rotation=45, ha="right")

    plt.tight_layout()
    return fig

def fig_to_b64(fig):
    """ 把 Matplotlib 图表转换成 base64 """
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def write_file(filepath, content):
    """ 写入文件 """
    with open(filepath, "w") as f:
        f.write(content)

def print_bar():
    """ 打印分隔线 """
    print("=" * 40)

def main():
   
    print_bar()
    print("Starting ECG scoring...")
    
    # 打印关键路径
    print(f"Reference data directory: {REF_DIR}")
    print(f"Prediction files directory: {RES_DIR}")
    print(f"Files in RES_DIR: {os.listdir(RES_DIR)}")  # 检查文件列表

    # ...（原有代码）

    scores_dict = {}

    dataset_names = get_dataset_names()
    for ds_name in dataset_names:
        # 1) 读取原始 ECG 信号
        ref_path = os.path.join(REF_DIR, ds_name + ".mat")
        try:
            ref_dict = load_matlab_file(ref_path)
            f = ref_dict["ecg"]  # 你的 `ecg` 变量
        except (FileNotFoundError, KeyError) as e:
            print(f"Error loading reference file {ref_path}: {e}")
            scores_dict[ds_name] = 0
            continue

        # 2) 读取选手的预测（重建）文件
        pred_path = os.path.join(RES_DIR, f"{ds_name}_pred.mat")
        print(f"Checking: {pred_path}")
        if not os.path.exists(pred_path):
            print(f"Prediction file {pred_path} not found.")
            scores_dict[ds_name] = 0
            continue

        try:
            pred_dict = load_matlab_file(pred_path)
            f_recon = pred_dict["f_recon"]
        except (FileNotFoundError, KeyError) as e:
            print(f"Error loading prediction file {pred_path}: {e}")
            scores_dict[ds_name] = 0
            continue

        # 确保 `f_recon` 形状匹配 `f`
        if f_recon.shape != f.shape:
            print(f"Reshaping f_recon from {f_recon.shape} to {f.shape}")
            f_recon = np.reshape(f_recon, f.shape)

        # 3) 计算 PRD
        prd_val = compute_PRD(f, f_recon)

        # 4) 计算 CR
        if "CR_val" in pred_dict:
            cr_val = float(pred_dict["CR_val"])
        else:
            print(f"Warning: CR_val not found in {pred_path}, defaulting to 1.0")
            cr_val = 1.0

        # 5) 计算最终 score = CR / (PRD + eps)
        score = cr_val / (prd_val + EPSILON)
        scores_dict[ds_name] = float(score)

    # 计算总分
    overall_score = np.mean(list(scores_dict.values()))
    scores_dict["overall_score"] = float(overall_score)

    # 写入 scores.json
    print_bar()
    print("Scoring program finished. Writing scores.")
    print(scores_dict)
    write_file(SCORES_FILE, json.dumps(scores_dict, indent=4))

    # 生成并写入 HTML 可视化结果
    fig = make_figure(scores_dict)
    figure_b64 = fig_to_b64(fig)
    write_file(DETAIL_FILE, f'<img src="data:image/png;base64,{figure_b64}">')

    print("Scoring results saved.")

if __name__ == "__main__":
    main()
