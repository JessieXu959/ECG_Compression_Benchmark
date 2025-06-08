# ECG压缩挑战赛 - 当前评分系统分析

## 📊 当前评分逻辑概述

### 🔍 **评分流程**
当前系统使用的是**模拟评分机制**，具体流程如下：

1. **文件上传阶段**
   - 参赛者上传ZIP格式的算法文件
   - 系统验证文件格式和大小（最大50MB）
   - 生成唯一的提交ID并保存文件

2. **评分处理阶段**
   - 后台任务异步处理提交
   - 模拟5秒的处理时间
   - 调用 `run_local_evaluation()` 函数进行评分

3. **结果生成阶段**
   - 更新提交状态为"已完成"
   - 计算并保存评分结果
   - 更新用户统计信息

---

## 🎯 **核心评分函数分析**

### `run_local_evaluation(file_path: str)` 函数详解

```python
async def run_local_evaluation(file_path: str) -> Dict[str, Any]:
    """Run local evaluation (simplified version)"""
    try:
        import random

        # 生成现实的随机分数
        cr = round(random.uniform(8.0, 50.0), 1)      # 压缩比 (8.0-50.0)
        prd = round(random.uniform(0.001, 0.1), 4)    # PRD越低越好 (0.001-0.1)

        # 计算综合分数 (简化公式)
        score = round(cr * (1.0 / (prd + 0.001)) * 0.1, 1)

        return {
            "status": "completed",
            "score": score,
            "metrics": {
                "CR": cr,           # 压缩比
                "PRD": prd,         # 百分比均方根差异
                "Score": score,     # 综合得分
                "RMSE": round(random.uniform(0.01, 0.1), 4),   # 均方根误差
                "SNR": round(random.uniform(15.0, 30.0), 1)    # 信噪比
            },
            "evaluation_time": round(random.uniform(2.0, 10.0), 2)
        }
    except Exception as e:
        return {"status": "failed", "score": 0.0, "error": str(e), "metrics": {}}
```

---

## 📈 **评分指标说明**

### 🔢 **主要指标**

| 指标 | 名称 | 范围 | 说明 |
|------|------|------|------|
| **CR** | 压缩比 | 8.0 - 50.0 | 压缩倍数，越高越好 |
| **PRD** | 百分比均方根差异 | 0.001 - 0.1 | 重建误差，越低越好 |
| **Score** | 综合得分 | 计算值 | 基于CR和PRD的综合评分 |
| **RMSE** | 均方根误差 | 0.01 - 0.1 | 重建精度指标 |
| **SNR** | 信噪比 | 15.0 - 30.0 dB | 信号质量指标 |

### 🧮 **得分计算公式**

```python
score = cr × (1.0 / (prd + 0.001)) × 0.1
```

**公式解释：**
- `cr`：压缩比，数值越大贡献越大
- `1.0 / (prd + 0.001)`：PRD的倒数，PRD越小这个值越大
- `0.001`：防止除零的小数
- `0.1`：缩放因子，调整最终得分范围

---

## ⚠️ **当前系统的限制**

### 🚨 **重要提醒**
目前的评分系统是**模拟系统**，具有以下特点：

1. **随机评分**：不实际运行参赛者的算法代码
2. **固定范围**：所有指标都在预设范围内随机生成
3. **无真实测试**：不使用真实的ECG数据进行测试

### 🛠️ **实际评分系统应该包含**

1. **算法执行**
   - 解压参赛者的ZIP文件
   - 运行算法代码
   - 使用标准ECG数据集进行测试

2. **真实指标计算**
   - 压缩比 = 原始文件大小 / 压缩文件大小
   - PRD = √(Σ(x-x')²) / √(Σx²) × 100%
   - RMSE = √(Σ(x-x')²/N)

3. **性能评估**
   - 运行时间测量
   - 内存使用量统计
   - 算法稳定性测试

---

## 🔄 **排行榜更新机制**

### 📊 **排名规则**
- 按照 `score` 降序排列（分数越高排名越前）
- 每个团队只显示**最佳成绩**
- 实时更新排行榜

### 🏆 **最佳成绩逻辑**
```python
# 只保留每个团队的最高分数
if team_name not in team_best or score > team_best[team_name]["score"]:
    team_best[team_name] = {
        "participant_name": team_name,
        "score": score,
        "scores": {"Score": score, "CR": cr, "PRD": prd},
        "submission_date": submitted_at,
        "algorithm_name": algorithm_name
    }
```

---

## 💡 **建议改进方向**

### 🎯 **短期改进**
1. 增加更现实的随机评分逻辑
2. 考虑算法名称影响评分
3. 添加评分详细日志

### 🚀 **长期改进**
1. 实现真实的ECG压缩算法评估
2. 集成Docker容器安全执行环境
3. 添加多种ECG数据集测试
4. 实现算法性能基准测试

---

## 📝 **总结**

当前系统提供了完整的**比赛框架**，包括：
- ✅ 用户注册和认证
- ✅ 文件上传和验证
- ✅ 异步评分处理
- ✅ 排行榜管理
- ✅ 提交历史跟踪

但评分部分是**模拟的**，在实际部署时需要替换为真实的ECG压缩算法评估系统。

---

*最后更新时间：2024年12月*