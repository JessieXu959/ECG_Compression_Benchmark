# 🧪 完整系统测试指南

## 📋 系统概览

您的ECG压缩评估系统由以下几个部分组成：

```
系统架构:
┌─────────────────┐    HTTP     ┌─────────────────┐    Python     ┌─────────────────┐
│    前端Web界面   │ ←────────→ │   FastAPI后端    │ ←────────→ │  实时评估系统    │
│  (index.html)   │   端口3000   │  (main.py)      │            │ (real_eval.py)  │
└─────────────────┘            └─────────────────┘            └─────────────────┘
```

## 🚀 方法一：一键启动测试 (推荐)

### 使用自动化设置脚本
```bash
# 在项目根目录执行
python setup_complete_system.py
```

这个脚本会：
- ✅ 自动安装所有依赖
- ✅ 启动后端API服务器 (http://localhost:8000)
- ✅ 启动前端Web服务器 (http://localhost:3000)
- ✅ 自动打开浏览器到应用界面

## 🔧 方法二：手动分步测试

### 第1步：测试实时评估系统

```bash
# 测试核心评估系统是否正常工作
python quick_test.py
```

**预期输出:**
```
🚀 Initializing Real ECG Evaluation System...
✅ Real ECG evaluation system loaded
🎯 Real evaluator initialized with 3 datasets
✅ System initialized with 3 datasets
📝 Test file test_ecg_algorithm.zip not found. System ready for evaluation.
✅ Real ECG Evaluation System is ready!
```

### 第2步：启动后端服务器

#### 方法2A: 使用启动脚本
```bash
cd mini-backend
python start_backend.py
```

#### 方法2B: 直接启动
```bash
cd mini-backend
python main.py
```

**预期输出:**
```
✅ Real ECG evaluation system loaded
🎯 Real evaluator initialized with 3 datasets
🚀 Starting ECG Compression Challenge Backend...
📍 Server will be available at: http://localhost:8000
📖 API documentation at: http://localhost:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 第3步：测试后端API

**在新终端窗口执行:**
```bash
# 测试健康检查
curl http://localhost:8000/health

# 或使用Python测试脚本
python test_api.py
```

**预期响应:**
```json
{
  "status": "healthy",
  "message": "ECG Compression Challenge Backend is running",
  "total_submissions": 0,
  "active_users": 0
}
```

### 第4步：启动前端服务器

**在新终端窗口执行:**
```bash
# 从项目根目录启动前端
python -m http.server 3000
```

**或者从ecg-compression目录:**
```bash
cd ecg-compression
python -m http.server 3000
```

**预期输出:**
```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

### 第5步：访问Web界面

打开浏览器访问：
- **前端界面**: http://localhost:3000
- **后端API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 🧪 第三步：完整功能测试

### 测试1：用户注册和登录

1. **注册新用户**:
   - 打开 http://localhost:3000
   - 点击"注册"
   - 填写队伍名称、邮箱、密码
   - 提交注册

2. **登录测试**:
   - 使用注册的账号登录
   - 验证是否成功进入主界面

### 测试2：算法提交

1. **创建测试算法**:
   ```bash
   python create_test_zip.py
   ```

   这会生成 `test_ecg_algorithm.zip` 文件

2. **通过Web界面提交**:
   - 登录后点击"提交算法"
   - 上传 `test_ecg_algorithm.zip`
   - 填写算法名称等信息
   - 提交并观察处理过程

3. **观察评估过程**:
   - 提交后状态显示"处理中"
   - 等待5-10秒后刷新页面
   - 查看评估结果和得分

### 测试3：排行榜功能

1. **查看排行榜**:
   - 点击"排行榜"选项卡
   - 验证您的提交出现在排行榜中
   - 检查得分和排名

2. **提交历史**:
   - 点击"我的提交"
   - 查看提交历史和详细结果

## 🔍 第四步：深度评估系统测试

### 运行综合评估演示

```bash
# 运行完整的评估系统演示
python demo_real_evaluation.py
```

**这个演示会:**
- ✅ 创建多个测试算法 (DCT压缩、下采样、多项式拟合)
- ✅ 运行完整评估流程
- ✅ 展示详细的评估指标
- ✅ 验证后端集成

**预期输出示例:**
```
🎯 ECG压缩算法评估演示

✅ 算法创建完成:
   - dct_compression.zip (DCT-based压缩)
   - simple_downsampling.zip (简单下采样)
   - polynomial_fitting.zip (多项式拟合)

🚀 开始评估系统测试...

📊 算法对比结果:
┌─────────────────────┬─────┬──────┬───────┬──────┬───────┐
│ 算法名称             │ CR  │ PRD  │ RMSE  │ SNR  │ 得分  │
├─────────────────────┼─────┼──────┼───────┼──────┼───────┤
│ dct_compression     │ 8.2 │ 2.45 │ 0.023 │ 24.5 │ 3.35  │
│ simple_downsampling │ 2.0 │ 8.91 │ 0.089 │ 15.2 │ 0.22  │
│ polynomial_fitting  │ 6.1 │ 4.12 │ 0.041 │ 19.8 │ 1.48  │
└─────────────────────┴─────┴──────┴───────┴──────┴───────┘

🏆 最佳算法: dct_compression (得分: 3.35)
```

## 📊 第五步：性能和压力测试

### 并发提交测试

```bash
# 测试多个并发提交
python test_concurrent_submissions.py
```

### 大文件上传测试

```bash
# 测试大文件处理
python test_large_file_upload.py
```

### 内存和性能监控

```bash
# 监控系统资源使用
python monitor_system_performance.py
```

## 🐛 故障排除指南

### 常见问题和解决方案

#### 1. 端口占用问题
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

#### 2. 依赖包问题
```bash
# 升级pip和重新安装
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r real_evaluation_requirements.txt
```

#### 3. 前端无法连接后端
```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查防火墙设置
# 确保端口8000和3000未被阻止
```

#### 4. 评估系统错误
```bash
# 检查评估系统状态
python -c "from real_evaluation_system import RealECGEvaluationSystem; print('✅ 评估系统正常')"

# 查看详细错误日志
python debug_evaluation_system.py
```

#### 5. 文件权限问题
```bash
# 确保上传目录有写权限
chmod 755 mini-backend/uploads
chmod 755 mini-backend/data
chmod 755 mini-backend/temp
```

## 📈 测试检查清单

### ✅ 系统启动检查
- [ ] 实时评估系统初始化成功
- [ ] 后端API服务器启动 (端口8000)
- [ ] 前端Web服务器启动 (端口3000)
- [ ] 健康检查API响应正常

### ✅ 功能测试检查
- [ ] 用户注册功能正常
- [ ] 用户登录功能正常
- [ ] 算法文件上传正常
- [ ] 算法评估处理正常
- [ ] 评估结果显示正确
- [ ] 排行榜更新正常

### ✅ 评分系统检查
- [ ] PRD计算使用原始公式
- [ ] 最终得分使用 CR/(PRD+ε) 公式
- [ ] EPSILON值为1e-6
- [ ] 评估指标完整 (CR, PRD, RMSE, SNR)

### ✅ 性能检查
- [ ] 文件上传速度合理
- [ ] 算法评估时间在预期范围
- [ ] 系统内存使用正常
- [ ] 并发处理能力正常

## 🎯 测试成功标准

系统测试通过的标准：

1. **启动成功**: 前后端都能正常启动并监听对应端口
2. **API正常**: 所有API端点都能正确响应
3. **评估准确**: 使用您的原始评分公式，结果准确
4. **用户体验**: Web界面响应流畅，提交流程顺畅
5. **数据持久**: 用户数据和提交记录正确保存
6. **错误处理**: 异常情况能正确处理和提示

## 🚀 下一步

测试完成后，您可以：

1. **邀请用户**: 将http://localhost:3000分享给参赛者
2. **监控系统**: 使用提供的监控工具跟踪系统状态
3. **数据导出**: 定期备份用户数据和提交记录
4. **性能优化**: 根据使用情况调整系统配置

---

**需要帮助？** 如果遇到任何问题，请查看：
- 后端日志输出
- 浏览器开发者控制台 (F12)
- 各个测试脚本的输出结果