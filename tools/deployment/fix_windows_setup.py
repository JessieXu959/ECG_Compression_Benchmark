#!/usr/bin/env python3
"""
Windows专用修复安装脚本 - ECG压缩挑战系统
解决Python 3.13在Windows环境下的依赖安装问题
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - 失败")
        print(f"错误输出: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("🏥 ECG压缩挑战系统 - Windows修复安装")
    print("=" * 60)

    # 检查Python版本
    python_version = sys.version
    print(f"🐍 当前Python版本: {python_version}")

    if sys.version_info >= (3, 13):
        print("⚠️  检测到Python 3.13+，将使用兼容性安装方案")

    # 1. 升级pip和基础工具
    print("\n📦 第一步：升级pip和基础安装工具...")
    commands = [
        "python -m pip install --upgrade pip",
        "pip install --upgrade setuptools wheel",
        "pip install --upgrade build"
    ]

    for cmd in commands:
        run_command(cmd, f"执行: {cmd}")

    # 2. 先安装预编译的科学计算包
    print("\n🧮 第二步：安装预编译的科学计算包...")
    scientific_packages = [
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "scikit-learn"
    ]

    for package in scientific_packages:
        run_command(f"pip install --only-binary=all {package}", f"安装预编译版本的 {package}")

    # 3. 安装其他依赖
    print("\n📋 第三步：安装其他依赖包...")
    other_packages = [
        "fastapi",
        "uvicorn",
        "python-multipart",
        "aiofiles",
        "pydantic",
        "pydantic-settings",
        "python-dotenv",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "tinydb",
        "sqlalchemy",
        "pytest",
        "pytest-asyncio",
        "httpx"
    ]

    for package in other_packages:
        run_command(f"pip install {package}", f"安装 {package}")

    # 4. 验证安装
    print("\n✅ 第四步：验证关键包安装...")
    verification_packages = ["fastapi", "numpy", "pandas", "uvicorn"]
    all_verified = True

    for package in verification_packages:
        try:
            __import__(package)
            print(f"✅ {package} - 安装成功")
        except ImportError:
            print(f"❌ {package} - 安装失败")
            all_verified = False

    if all_verified:
        print("\n🎉 所有依赖安装成功！")

        # 5. 启动系统
        print("\n🚀 第五步：启动ECG压缩挑战系统...")

        # 启动后端
        backend_path = Path("mini-backend")
        if backend_path.exists():
            print("启动后端API服务器...")
            subprocess.Popen([
                sys.executable, "start_backend.py"
            ], cwd=backend_path)

        # 启动前端
        frontend_path = Path("ecg-compression")
        if frontend_path.exists():
            print("启动前端Web服务器...")
            subprocess.Popen([
                sys.executable, "-m", "http.server", "3000"
            ], cwd=frontend_path)
        elif Path("index.html").exists():
            print("启动前端Web服务器...")
            subprocess.Popen([
                sys.executable, "-m", "http.server", "3000"
            ])

        print("\n" + "=" * 60)
        print("🎯 系统启动成功！")
        print("🌐 前端地址: http://localhost:3000")
        print("⚡ 后端API: http://localhost:8000")
        print("📖 API文档: http://localhost:8000/docs")
        print("=" * 60)

        # 尝试打开浏览器
        try:
            import webbrowser
            webbrowser.open("http://localhost:3000")
            print("🚀 浏览器已自动打开")
        except:
            print("请手动打开浏览器访问: http://localhost:3000")

    else:
        print("\n❌ 部分依赖安装失败，请检查错误信息")
        print("💡 建议尝试以下解决方案：")
        print("   1. 安装 Visual Studio Build Tools")
        print("   2. 或者降级到 Python 3.11")
        print("   3. 或者使用 Anaconda/Miniconda")

if __name__ == "__main__":
    main()