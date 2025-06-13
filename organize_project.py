#!/usr/bin/env python3
"""
项目文件整理脚本 - ECG压缩算法评估系统
按功能和用途重新组织项目文件结构
"""

import os
import shutil
from pathlib import Path
import json

def create_directory_structure():
    """创建新的目录结构"""
    directories = {
        # 核心系统目录
        "core": "核心系统文件",
        "core/backend": "后端服务",
        "core/frontend": "前端界面",
        "core/evaluation": "评估系统",

        # 算法和解决方案
        "solutions": "算法解决方案",
        "solutions/examples": "示例算法",
        "solutions/templates": "算法模板",

        # 数据目录
        "data": "数据文件",
        "data/datasets": "数据集",
        "data/output": "输出结果",
        "data/cache": "缓存文件",

        # 测试目录
        "tests": "测试文件",
        "tests/unit": "单元测试",
        "tests/integration": "集成测试",
        "tests/performance": "性能测试",

        # 文档目录
        "docs": "文档说明",
        "docs/api": "API文档",
        "docs/guides": "使用指南",
        "docs/examples": "示例文档",

        # 配置目录
        "config": "配置文件",

        # 工具目录
        "tools": "工具脚本",
        "tools/analysis": "分析工具",
        "tools/deployment": "部署工具",

        # 临时文件
        "temp": "临时文件",

        # 备份目录
        "backup": "备份文件"
    }

    print("📁 创建目录结构...")
    for dir_path, description in directories.items():
        os.makedirs(dir_path, exist_ok=True)
        print(f"   ✅ {dir_path}/ - {description}")

    return directories

def organize_files():
    """整理文件到新的目录结构"""

    # 文件分类映射
    file_organization = {
        # 核心系统文件
        "core/evaluation/": [
            "real_evaluation_system.py",
            "real_evaluation_requirements.txt",
        ],

        "core/backend/": [
            "mini-backend/main.py",
            "mini-backend/storage.py",
            "mini-backend/evaluate.py",
            "mini-backend/requirements.txt",
            "mini-backend/README.md",
            "mini-backend/start_backend.py",
        ],

        "core/frontend/": [
            "ecg-compression/index.html",
            "ecg-compression/scripts.js",
            "ecg-compression/styles.css",
            "ecg-compression/images/",
        ],

        # 算法解决方案
        "solutions/examples/": [
            "solution/solve.py",
            "solution/ecg_model.py",
            "solution/requirements.txt",
            "solution/README.md",
            "solution/__init__.py",
            "solution/run_test.py",
        ],

        "solutions/templates/": [
            "ecg_model.py",  # 根目录的模板文件
        ],

        # 数据文件
        "data/datasets/": [
            "evaluation_data/",
            "demo_evaluation_data/",
            "simple_test_data/",
            "test_data/",
        ],

        "data/output/": [
            "output_test/",
        ],

        "data/cache/": [
            "mini-backend/data/",
        ],

        # 测试文件
        "tests/unit/": [
            "test_algorithm.py",
            "simple_ecg_test.py",
        ],

        "tests/integration/": [
            "test_real_evaluation.py",
            "test_api.py",
            "test_new_features.py",
            "test_data_persistence.py",
        ],

        "tests/performance/": [
            "test_concurrent_submissions.py",
            "monitor_system_performance.py",
            "compare_solutions.py",
        ],

        # 文档
        "docs/guides/": [
            "README.md",
            "COMPLETE_TESTING_GUIDE.md",
            "REAL_ECG_EVALUATION_GUIDE.md",
            "SCORING_SYSTEM_INTEGRATION.md",
            "SCORE_LOGIC_VERIFICATION.md",
            "scoring_system_analysis.md",
        ],

        "docs/examples/": [
            "verify_frontend.html",
        ],

        # 配置文件
        "config/": [
            "requirements.txt",
            "competition.yaml",
        ],

        # 工具脚本
        "tools/analysis/": [
            "cleanup_project.py",
            "file_analysis_report.json",
        ],

        "tools/deployment/": [
            "setup_complete_system.py",
            "restart_system.py",
            "fix_windows_setup.py",
            "start_backend.py",
            "copy_bundle_files.py",
        ],

        "tools/": [
            "quick_system_check.py",
            "check_frontend_cache.py",
            "check_status.py",
            "clear_frontend_cache.js",
        ],

        # 备份文件
        "backup/": [
            "ecg_compression_bundle.zip",
            "solutions_comparison.png",
            "ModelingLab.png",
        ]
    }

    print("\n📦 开始整理文件...")
    moved_files = 0

    for target_dir, files in file_organization.items():
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        for file_item in files:
            if os.path.exists(file_item):
                try:
                    if os.path.isdir(file_item):
                        # 移动目录
                        target_path = os.path.join(target_dir, os.path.basename(file_item))
                        if not os.path.exists(target_path):
                            shutil.move(file_item, target_path)
                            print(f"   📁 {file_item} → {target_path}")
                            moved_files += 1
                    else:
                        # 移动文件
                        target_path = os.path.join(target_dir, os.path.basename(file_item))
                        if not os.path.exists(target_path):
                            shutil.move(file_item, target_path)
                            print(f"   📄 {file_item} → {target_path}")
                            moved_files += 1
                except Exception as e:
                    print(f"   ❌ 移动 {file_item} 失败: {e}")

    return moved_files

def create_project_structure_doc():
    """创建项目结构说明文档"""
    structure_doc = """# ECG压缩算法评估系统 - 项目结构

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
"""

    with open("PROJECT_STRUCTURE.md", "w", encoding="utf-8") as f:
        f.write(structure_doc)

    print("📋 项目结构文档已生成: PROJECT_STRUCTURE.md")

def main():
    """主函数"""
    print("🗂️  ECG压缩算法评估系统 - 项目文件整理")
    print("="*60)

    # 询问用户确认
    print("此操作将:")
    print("• 创建新的目录结构")
    print("• 按功能分类移动文件")
    print("• 生成项目结构说明文档")
    print("• 保持所有文件完整性")

    response = input("\n继续整理项目文件? (y/N): ").strip().lower()
    if response not in ['y', 'yes', '是']:
        print("❌ 文件整理已取消")
        return

    # 创建目录结构
    directories = create_directory_structure()

    # 整理文件
    moved_files = organize_files()

    # 创建项目结构文档
    create_project_structure_doc()

    # 清理空目录
    empty_dirs = []
    for root, dirs, files in os.walk('.'):
        if not dirs and not files and root != '.':
            empty_dirs.append(root)

    for empty_dir in empty_dirs:
        try:
            os.rmdir(empty_dir)
            print(f"   🗑️  删除空目录: {empty_dir}")
        except:
            pass

    print("\n" + "="*60)
    print("✨ 项目整理完成!")
    print("="*60)
    print(f"📁 创建目录: {len(directories)} 个")
    print(f"📄 移动文件: {moved_files} 个")
    print(f"📋 生成文档: PROJECT_STRUCTURE.md")

    print(f"\n🎯 新的项目结构:")
    print(f"   core/          - 核心系统文件")
    print(f"   solutions/     - 算法解决方案")
    print(f"   data/          - 数据文件")
    print(f"   tests/         - 测试文件")
    print(f"   docs/          - 文档说明")
    print(f"   config/        - 配置文件")
    print(f"   tools/         - 工具脚本")
    print(f"   backup/        - 备份文件")

    print(f"\n💡 下一步建议:")
    print(f"   1. 查看 PROJECT_STRUCTURE.md 了解新结构")
    print(f"   2. 运行 python tools/quick_system_check.py 验证系统")
    print(f"   3. 测试核心功能是否正常工作")
    print(f"   4. 删除不需要的测试文件节省空间")

if __name__ == "__main__":
    main()