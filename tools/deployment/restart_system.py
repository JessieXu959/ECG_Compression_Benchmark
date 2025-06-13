#!/usr/bin/env python3
"""
ECG压缩挑战系统重启脚本
修复前后端连接问题
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def kill_process_on_port(port):
    """杀死占用指定端口的进程"""
    try:
        # Windows命令查找端口占用
        result = subprocess.run(f'netstat -ano | findstr :{port}', shell=True, capture_output=True, text=True)
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            subprocess.run(f'taskkill /PID {pid} /F', shell=True, check=True)
                            print(f"✅ 已终止端口 {port} 上的进程 (PID: {pid})")
                        except:
                            pass
    except Exception as e:
        print(f"⚠️ 清理端口 {port} 时出错: {e}")

def main():
    print("=" * 60)
    print("🔄 ECG压缩挑战系统 - 重启修复")
    print("=" * 60)

    # 1. 清理端口
    print("🧹 清理端口占用...")
    kill_process_on_port(3000)
    kill_process_on_port(8000)
    time.sleep(2)

    # 2. 检查目录结构
    backend_path = Path("mini-backend")
    frontend_path = Path("ecg-compression")

    if not backend_path.exists():
        print("❌ 后端目录不存在: mini-backend/")
        return

    if not frontend_path.exists():
        print("❌ 前端目录不存在: ecg-compression/")
        return

    print("✅ 目录结构检查通过")

    # 3. 启动后端服务器
    print("\n🚀 启动后端API服务器...")
    try:
        # 启动后端
        backend_process = subprocess.Popen([
            sys.executable, "main.py"
        ], cwd=backend_path, creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)

        print("✅ 后端服务器启动中...")
        time.sleep(3)  # 等待后端启动

    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        return

    # 4. 启动前端服务器
    print("🌐 启动前端Web服务器...")
    try:
        # 启动前端
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "http.server", "3000"
        ], cwd=frontend_path, creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)

        print("✅ 前端服务器启动中...")
        time.sleep(2)

    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
        return

    # 5. 验证服务
    print("\n🔍 验证服务状态...")

    # 测试后端
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端API服务器运行正常")
        else:
            print("⚠️ 后端API服务器响应异常")
    except Exception as e:
        print(f"⚠️ 后端连接测试失败: {e}")

    # 测试前端
    try:
        import requests
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ 前端Web服务器运行正常")
        else:
            print("⚠️ 前端Web服务器响应异常")
    except Exception as e:
        print(f"⚠️ 前端连接测试失败: {e}")

    print("\n" + "=" * 60)
    print("🎯 系统重启完成！")
    print("🌐 前端地址: http://localhost:3000")
    print("⚡ 后端API: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔍 健康检查: http://localhost:8000/health")
    print("=" * 60)

    # 打开浏览器
    try:
        import webbrowser
        time.sleep(2)
        webbrowser.open("http://localhost:3000")
        print("🚀 浏览器已自动打开")
    except:
        print("请手动打开浏览器访问: http://localhost:3000")

    print("\n💡 提示:")
    print("- 如果遇到API错误，请检查后端控制台输出")
    print("- 前端和后端都在新的控制台窗口中运行")
    print("- 按Ctrl+C可停止对应的服务")

if __name__ == "__main__":
    main()