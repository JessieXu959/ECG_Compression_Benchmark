# ECG压缩算法评估系统 - 项目结构

## 📁 目录结构说明

### 🎯 核心系统 (core/)
```
core/
├── evaluation/         # 评估系统核心
│   ├── real_evaluation_system.py    # 主评估引擎
│   └── real_evaluation_requirements.txt
├── backend/           # 后端API服务
│   ├── main.py        # FastAPI主服务
│   ├── storage.py     # 数据存储
│   ├── evaluate.py    # 评估接口
│   └── requirements.txt
└── frontend/          # 前端界面
    ├── index.html     # 主页面
    ├── scripts.js     # JavaScript逻辑
    ├── styles.css     # 样式表
    └── images/        # 图片资源
```

### 🧮 算法解决方案 (solutions/)
```
solutions/
├── examples/          # 示例算法
│   ├── solve.py       # 主求解脚本
│   ├── ecg_model.py   # ECG压缩模型
│   └── requirements.txt
└── templates/         # 算法模板
    └── ecg_model.py   # 基础模板
```

### 📊 数据管理 (data/)
```
data/
├── datasets/          # 数据集
│   ├── evaluation_data/      # 评估数据
│   ├── demo_evaluation_data/ # 演示数据
│   └── test_data/           # 测试数据
├── output/           # 输出结果
│   └── output_test/  # 测试输出
└── cache/            # 缓存文件
    └── data/         # 系统缓存
```

### 🧪 测试系统 (tests/)
```
tests/
├── unit/             # 单元测试
│   ├── test_algorithm.py    # 算法测试
│   └── simple_ecg_test.py   # 简单ECG测试
├── integration/      # 集成测试
│   ├── test_real_evaluation.py  # 评估系统测试
│   ├── test_api.py              # API测试
│   └── test_new_features.py     # 新功能测试
└── performance/      # 性能测试
    ├── test_concurrent_submissions.py  # 并发测试
    └── monitor_system_performance.py   # 性能监控
```

### 📚 文档系统 (docs/)
```
docs/
├── guides/           # 使用指南
│   ├── README.md                    # 主说明文档
│   ├── COMPLETE_TESTING_GUIDE.md    # 完整测试指南
│   └── REAL_ECG_EVALUATION_GUIDE.md # 评估指南
├── api/              # API文档
└── examples/         # 示例文档
    └── verify_frontend.html  # 前端验证示例
```

### ⚙️ 配置文件 (config/)
```
config/
├── requirements.txt   # Python依赖
└── competition.yaml  # 竞赛配置
```

### 🔧 工具脚本 (tools/)
```
tools/
├── analysis/         # 分析工具
│   └── cleanup_project.py    # 项目清理
├── deployment/       # 部署工具
│   ├── setup_complete_system.py  # 系统安装
│   └── restart_system.py         # 系统重启
└── quick_system_check.py      # 快速系统检查
```

### 💾 备份文件 (backup/)
```
backup/
├── ecg_compression_bundle.zip  # 项目备份包
├── solutions_comparison.png    # 解决方案对比图
└── ModelingLab.png            # 实验室logo
```

## 🚀 快速启动

1. **启动后端服务**:
   ```bash
   cd core/backend
   python main.py
   ```

2. **打开前端界面**:
   ```bash
   # 打开 core/frontend/index.html
   ```

3. **运行系统检查**:
   ```bash
   python tools/quick_system_check.py
   ```

4. **测试算法**:
   ```bash
   cd tests/unit
   python test_algorithm.py
   ```

## 📋 文件用途说明

### 必须保留的核心文件:
- `core/evaluation/real_evaluation_system.py` - 评估系统核心
- `core/backend/main.py` - 后端API服务
- `core/frontend/index.html` - 前端主页
- `solutions/examples/solve.py` - 算法求解器
- `solutions/examples/ecg_model.py` - ECG压缩模型

### 可选文件:
- `tests/` - 测试文件 (开发调试用)
- `docs/` - 文档文件 (说明参考)
- `tools/` - 工具脚本 (维护管理)
- `backup/` - 备份文件 (安全备份)

## 🔄 维护建议

1. 定期运行 `tools/quick_system_check.py` 检查系统状态
2. 使用 `tools/analysis/cleanup_project.py` 清理临时文件
3. 备份重要数据到 `backup/` 目录
4. 新算法放入 `solutions/examples/` 目录
5. 测试文件放入对应的 `tests/` 子目录
