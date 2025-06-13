# ECG 压缩算法解决方案

这是一个基于小波变换的ECG信号压缩算法实现。

## 算法特点

- 使用小波变换（Wavelet Transform）进行信号压缩
- 自适应阈值处理，保留重要信号特征
- 高压缩比（15:1以上）
- 确保重建信号质量

## 目录结构

```
solution/
├── README.md              # 本文档
├── requirements.txt       # 依赖库列表
├── __init__.py            # 包初始化文件
├── ecg_model.py           # 压缩算法实现
├── solve.py               # 主入口脚本
└── run_test.py            # 测试脚本
```

## 依赖

- Python 3.6+
- NumPy
- SciPy
- PyWavelets

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python solve.py <输入数据目录> <输出目录>
```

例如:

```bash
python solve.py /input_data /output
```

## 评估方法

算法将被评估以下指标:

1. **压缩比 (CR)**: 原始信号大小与压缩后信号大小的比值
2. **百分比均方根差异 (PRD)**: 测量原始信号与重建信号的差异程度
3. **最终得分**: 使用公式 `Score = CR / (PRD + ε)` 计算，其中 `ε` 是一个小常数

## 开发者

- 作者: 系统用户