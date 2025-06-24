# ECG Compression Challenge - Starter Kit 🚀

## 🎯 **竞赛目标**

设计高效的ECG信号压缩算法，在保持信号诊断质量的同时实现最大压缩比。你的算法将通过以下指标进行评估：

- **压缩比 (CR)**: 原始数据大小 / 压缩后大小
- **重建误差 (PRD)**: 重建信号与原始信号的百分比差异
- **最终得分**: CR / (PRD + 1e-6) - **越高越好！**

## 📦 **提交要求**

### **文件结构**
```
your_algorithm.zip
├── ecg_model.py          # 主算法文件 (必需)
├── requirements.txt      # Python依赖列表 (可选)
├── solve.py             # 备用入口文件 (可选)
└── [其他文件]            # 辅助文件 (可选)
```

### **标准算法接口**
你的 `ecg_model.py` 必须包含以下类和方法：

```python
import numpy as np

class ECGCompressor:
    def __init__(self):
        """初始化压缩器"""
        pass

    def compress_and_reconstruct(self, ecg_signal):
        """
        主要算法接口 - 实现ECG信号的压缩和重建

        参数:
            ecg_signal (numpy.ndarray): 一维ECG信号数组

        返回:
            tuple: (reconstructed_signal, compression_ratio)
            - reconstructed_signal: 重建的ECG信号 (numpy.ndarray)
            - compression_ratio: 压缩比 (float, 必须 > 1.0)
        """
        # 在这里实现你的压缩算法
        pass
```

## 🚀 **快速开始**

### **步骤 1: 修改算法**
1. 打开 `ecg_model.py`
2. 在 `compress_and_reconstruct` 方法中实现你的算法
3. 确保返回格式正确: `(重建信号, 压缩比)`

### **步骤 2: 本地测试**
```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
python test/test_algorithm.py

# 验证算法性能
python utils/validation.py
```

### **步骤 3: 打包提交**
1. 将你的文件压缩为ZIP格式
2. 确保ZIP包含 `ecg_model.py`
3. 文件大小不超过50MB
4. 上传到竞赛平台

## 💡 **算法示例**

我们提供了三个不同复杂度的示例算法：

### **1. 简单压缩 (`examples/simple_compression.py`)**
- 基于降采样的简单方法
- 适合初学者理解基本流程
- 压缩比: ~2-4x

### **2. 小波压缩 (`examples/wavelet_compression.py`)**
- 使用小波变换进行压缩
- 平衡压缩比和信号质量
- 压缩比: ~5-15x

### **3. B样条压缩 (`examples/bspline_compression.py`)**
- 高级数学方法，基于样条拟合
- 高压缩比，低失真
- 压缩比: ~10-30x

## 📊 **评估数据**

平台使用多个合成ECG数据集进行评估：

- **数据集1**: 正常心律 (360Hz, 10秒)
- **数据集2**: 心动过速 (360Hz, 15秒)
- **数据集3**: 高噪声环境 (250Hz, 12秒)

你的算法将在所有数据集上测试，最终得分为平均值。

## 🛠 **开发工具**

### **本地验证工具 (`utils/validation.py`)**
```bash
python utils/validation.py --algorithm ecg_model.py --data test/sample_ecg.npy
```

### **指标计算 (`utils/metrics.py`)**
```python
from utils.metrics import calculate_prd, calculate_compression_ratio

# 计算重建误差
prd = calculate_prd(original_signal, reconstructed_signal)

# 计算压缩比
cr = calculate_compression_ratio(original_size, compressed_size)
```

## ❓ **常见问题**

### **Q: 我的算法返回错误的数据类型怎么办？**
A: 确保返回 `(numpy.ndarray, float)` 格式，重建信号长度与原始信号相同。

### **Q: 如何提高压缩比？**
A: 尝试频域压缩、稀疏表示、或机器学习方法。注意平衡压缩比和重建质量。

### **Q: 算法执行时间有限制吗？**
A: 是的，每个数据集最多60秒处理时间。优化算法效率很重要。

### **Q: 可以使用外部库吗？**
A: 可以！在 `requirements.txt` 中列出所有依赖。常用库如numpy, scipy, scikit-learn都支持。

## 🏆 **获胜策略**

1. **理解数据特征**: ECG信号有特定的频率特征和冗余性
2. **平衡权衡**: 不要过度追求压缩比而忽略信号质量
3. **算法优化**: 考虑计算效率和内存使用
4. **多样化测试**: 在不同类型的ECG数据上验证算法
5. **参考文献**: 学习已有的ECG压缩方法和技术

## 🔗 **有用资源**

- **ECG信号处理**: [PhysioNet](https://physionet.org/)
- **压缩算法理论**: [Data Compression Book](http://www.data-compression.com/)
- **Python科学计算**: [SciPy Documentation](https://docs.scipy.org/)

## 📞 **技术支持**

遇到问题？查看平台FAQ或联系技术支持团队。

---

**祝你在ECG压缩挑战中取得优异成绩！** 🎉

---

*最后更新: 2024年12月*