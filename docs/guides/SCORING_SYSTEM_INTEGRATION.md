# 🧬 ECG评分系统集成设计文档

## 📋 原有系统 vs 新设计对比

### 🏗️ 架构对比

| 方面 | 您的原有系统 | 我的实时系统 |
|------|-------------|-------------|
| **部署方式** | Codabench容器化 | FastAPI + Web界面 |
| **执行模式** | 批处理 (ingestion → scoring) | 实时集成评估 |
| **数据格式** | .mat文件存储 | JSON动态传输 |
| **用户交互** | 文件上传等待 | 实时Web界面 |
| **结果展示** | HTML静态报告 | 动态排行榜 |

### 🔧 核心评分逻辑保持一致

#### 1. PRD计算公式 (完全保留您的逻辑)

**您的原始代码:**
```python
def compute_PRD(f, f_recon):
    f_mean = np.mean(f)
    numerator = np.linalg.norm(f - f_recon, 2)
    denominator = np.linalg.norm(f - f_mean, 2)

    if denominator < EPSILON:
        return float('inf')

    prd = (numerator / denominator) * 100
    return prd
```

**我的集成版本:**
```python
@staticmethod
def calculate_prd(original: np.ndarray, reconstructed: np.ndarray) -> float:
    # User's original PRD calculation logic
    f_mean = np.mean(original)
    numerator = np.linalg.norm(original - reconstructed, 2)
    denominator = np.linalg.norm(original - f_mean, 2)

    if denominator < ECGMetricsCalculator.EPSILON:
        return float('inf')

    prd = (numerator / denominator) * 100
    return float(prd)
```

#### 2. 最终评分公式 (保持您的评分标准)

**您的原始公式:**
```python
score = cr_val / (prd_val + EPSILON)
```

**我的集成版本:**
```python
@staticmethod
def calculate_final_score(cr: float, prd: float) -> float:
    """Score = CR / (PRD + epsilon)"""
    return cr / (prd + ECGMetricsCalculator.EPSILON)
```

## 🚀 系统集成架构

### 📤 数据流程对比

#### 您的原有流程:
```
1. 用户上传ZIP → Codabench容器
2. ingestion.py 解压 → 导入ECGCompressor
3. 读取.mat文件 → 调用compress_and_reconstruct()
4. 保存结果到.mat → 等待scoring阶段
5. scoring.py 读取结果 → 计算PRD和CR
6. 生成最终评分 → 输出HTML报告
```

#### 我的实时流程:
```
1. 用户通过Web界面上传ZIP
2. RealECGEvaluationSystem 实时处理:
   ├── 解压ZIP文件
   ├── 动态生成ECG数据集 (JSON格式)
   ├── 安全执行用户算法
   ├── 立即计算所有指标 (PRD, CR, RMSE, SNR)
   ├── 应用您的评分公式
   └── 返回JSON结果
3. FastAPI后端格式化响应
4. 前端实时显示结果和更新排行榜
```

### 🔗 API接口设计

#### 评估结果格式 (兼容您的评分系统):
```json
{
  "success": true,
  "evaluation_method": "real_ecg_compression",

  // 核心指标 (使用您的计算公式)
  "compression_ratio": 3.0,
  "prd_percent": 12.5,
  "rmse": 0.087,
  "snr_db": 18.2,
  "final_score": 0.24,  // CR / (PRD + epsilon)
  "score": 0.24,        // 主要排名指标

  // 评分系统信息
  "scoring_formula": "FinalScore = CR / (PRD + epsilon)",
  "epsilon_value": 1e-6,

  // 性能信息
  "execution_time": 0.85,
  "datasets_processed": 3,
  "total_datasets": 3
}
```

## 🎯 关键设计决策

### 1. **保持评分标准一致性**
- 完全保留您的PRD计算公式
- 使用相同的最终评分 `CR/(PRD+ε)`
- 相同的epsilon值处理

### 2. **提升用户体验**
- 从批处理改为实时评估
- Web界面替代容器上传
- 即时结果反馈

### 3. **简化部署要求**
- 无需Codabench环境
- 本地运行FastAPI服务
- 浏览器直接访问

### 4. **增强安全性**
- 沙盒化算法执行
- 资源限制 (内存、时间)
- 错误隔离和恢复

## 🧪 算法执行方式对比

### 您的ingestion方式:
```python
# 在容器环境中直接导入
from ecg_model import ECGCompressor
compressor = ECGCompressor()

# 逐个处理数据集
for ds_name in datasets:
    ecg_signal = load_mat_file(ecg_path)["ecg"]
    f_recon, cr_val = compressor.compress_and_reconstruct(ecg_signal)
    save_mat_file(output_path, {"f_recon": f_recon, "CR_val": cr_val})
```

### 我的安全执行方式:
```python
# 创建安全的执行脚本
script_content = f'''
import sys
sys.path.insert(0, r"{algorithm_dir}")

from ecg_model import ECGCompressor
input_data = {json.dumps(input_data)}

results = {{}}
for dataset_name, dataset_info in input_data.items():
    ecg_signal = dataset_info["signal"]
    compressor = ECGCompressor()
    f_recon, cr_val = compressor.compress_and_reconstruct(ecg_signal)

    results[dataset_name] = {{
        "reconstructed": f_recon.tolist(),
        "compression_ratio": float(cr_val)
    }}

print(json.dumps(results))
'''

# 在子进程中安全执行
process = subprocess.Popen([sys.executable, script_path], ...)
stdout, stderr = process.communicate(timeout=self.timeout)
```

## 📊 评估结果展示

### 您的HTML报告:
```python
def make_figure(scores_dict):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(dataset_names, scores, color='blue', alpha=0.7)
    # 生成静态图表
```

### 我的动态Web界面:
```javascript
// 实时更新排行榜
function updateLeaderboard(results) {
    const leaderboard = document.getElementById('leaderboard');
    // 动态添加结果行
    // 支持排序、筛选、实时更新
}

// 实时显示评估进度
function showEvaluationProgress(status) {
    // 显示处理状态、进度条、预估时间
}
```

## 🔄 从您的系统迁移到新系统

### 迁移优势:
1. **保持相同的评分标准** - 算法排名不变
2. **改善用户体验** - 即时反馈替代长时间等待
3. **降低部署复杂度** - 无需容器化环境
4. **增强交互性** - Web界面替代静态报告
5. **提高安全性** - 沙盒执行替代直接导入

### 兼容性保证:
- ECGCompressor接口完全相同
- 评分公式完全一致
- 数据集格式概念保持 (转换为JSON)
- 结果精度保持一致

## 🎉 总结

我的设计**完全保留了您原有的评分逻辑和标准**，同时通过以下方式提升了系统:

1. **实时Web化** - 从批处理变为实时交互
2. **安全增强** - 沙盒执行用户代码
3. **用户友好** - 直观的Web界面和即时反馈
4. **部署简化** - 无需复杂的容器化环境

**核心评分逻辑保持100%一致**，确保算法评估结果的准确性和公平性。