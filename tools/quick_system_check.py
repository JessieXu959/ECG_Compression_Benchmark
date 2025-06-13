#!/usr/bin/env python3
"""
快速系统检查脚本
检查ECG评估系统的各个组件是否准备就绪
"""

import os
import sys
import json
import requests
import subprocess
import time
from pathlib import Path

class SystemChecker:
    def __init__(self):
        self.root_path = Path(".")
        self.issues = []
        self.warnings = []

    def check_mark(self, condition):
        return "✅" if condition else "❌"

    def warning_mark(self, condition):
        return "⚠️" if not condition else "✅"

    def print_section(self, title):
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print("="*60)

    def check_file_structure(self):
        """检查项目文件结构"""
        self.print_section("项目文件结构检查")

        required_files = [
            "real_evaluation_system.py",
            "mini-backend/main.py",
            "mini-backend/requirements.txt",
            "test_solution.zip",
            "setup_complete_system.py"
        ]

        optional_files = [
            "ecg-compression/index.html",
            "ecg-compression/scripts.js",
            "ecg-compression/styles.css",
            "README.md",
            "demo_real_evaluation.py",
            "test_concurrent_submissions.py"
        ]

        print("📁 必需文件:")
        for file_path in required_files:
            exists = (self.root_path / file_path).exists()
            print(f"   {self.check_mark(exists)} {file_path}")
            if not exists:
                self.issues.append(f"缺少必需文件: {file_path}")

        print("\n📄 可选文件:")
        for file_path in optional_files:
            exists = (self.root_path / file_path).exists()
            print(f"   {self.warning_mark(exists)} {file_path}")
            if not exists:
                self.warnings.append(f"缺少可选文件: {file_path}")

    def check_dependencies(self):
        """检查Python依赖"""
        self.print_section("Python依赖检查")

        # 核心依赖
        core_dependencies = [
            ("numpy", "数值计算"),
            ("fastapi", "后端框架"),
            ("uvicorn", "ASGI服务器"),
            ("requests", "HTTP客户端"),
            ("aiofiles", "异步文件操作")
        ]

        # 可选依赖
        optional_dependencies = [
            ("psutil", "系统监控"),
            ("matplotlib", "图表绘制"),
            ("scipy", "科学计算"),
            ("pandas", "数据处理")
        ]

        print("🐍 核心Python依赖:")
        for package, description in core_dependencies:
            try:
                __import__(package)
                print(f"   ✅ {package:<15} - {description}")
            except ImportError:
                print(f"   ❌ {package:<15} - {description}")
                self.issues.append(f"缺少核心依赖: {package}")

        print("\n📦 可选Python依赖:")
        for package, description in optional_dependencies:
            try:
                __import__(package)
                print(f"   ✅ {package:<15} - {description}")
            except ImportError:
                print(f"   ⚠️ {package:<15} - {description}")
                self.warnings.append(f"缺少可选依赖: {package}")

    def check_backend_status(self):
        """检查后端状态"""
        self.print_section("后端服务检查")

        backend_url = "http://localhost:8000"

        # 检查端口是否可用
        print("🌐 后端连接测试:")

        try:
            response = requests.get(f"{backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 后端服务在线 ({backend_url})")
                print(f"   📊 状态: {data.get('status', 'unknown')}")
                print(f"   📈 总提交数: {data.get('total_submissions', 0)}")
                print(f"   👥 活跃用户: {data.get('active_users', 0)}")
                print(f"   ⏱️  响应时间: {response.elapsed.total_seconds()*1000:.1f}ms")

                # 测试其他端点
                endpoints_to_test = [
                    ("/docs", "API文档", "GET"),
                    ("/api/register", "用户注册", "POST"),
                    ("/api/leaderboard", "排行榜", "GET")
                ]

                print("\n🔌 API端点测试:")
                for endpoint, description, method in endpoints_to_test:
                    try:
                        if method == "GET":
                            test_response = requests.get(f"{backend_url}{endpoint}", timeout=3)
                        elif method == "POST":
                            # For POST endpoints, send minimal test data
                            test_response = requests.post(f"{backend_url}{endpoint}",
                                                        json={}, timeout=3)

                        # Accept 200 (success), 422 (validation error), or 400 (bad request) as valid responses
                        status = "✅" if test_response.status_code in [200, 422, 400] else "❌"
                        print(f"   {status} {endpoint:<25} - {description} (状态码: {test_response.status_code})")
                    except Exception as e:
                        print(f"   ❌ {endpoint:<25} - {description} (错误: {str(e)[:30]}...)")

            else:
                print(f"   ❌ 后端服务异常 (状态码: {response.status_code})")
                self.issues.append(f"后端服务状态码异常: {response.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"   ⚠️ 后端服务未运行 ({backend_url})")
            self.warnings.append("后端服务未运行，需要启动后端")
        except Exception as e:
            print(f"   ❌ 后端连接错误: {e}")
            self.issues.append(f"后端连接错误: {e}")

    def check_frontend_status(self):
        """检查前端状态"""
        self.print_section("前端服务检查")

        frontend_url = "http://localhost:3000"

        # 检查前端文件
        frontend_path = self.root_path / "ecg-compression"
        if frontend_path.exists():
            print("📂 前端文件结构:")
            frontend_files = ["index.html", "scripts.js", "styles.css"]
            for file in frontend_files:
                file_path = frontend_path / file
                exists = file_path.exists()
                print(f"   {self.check_mark(exists)} {file}")
                if not exists:
                    self.issues.append(f"前端文件缺失: {file}")
        else:
            print("   ❌ 前端目录不存在")
            self.issues.append("前端目录不存在")
            return

        # 检查前端服务
        print(f"\n🌐 前端连接测试:")
        try:
            response = requests.get(frontend_url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ 前端服务在线 ({frontend_url})")
                print(f"   📄 页面大小: {len(response.content)} bytes")
                print(f"   ⏱️  响应时间: {response.elapsed.total_seconds()*1000:.1f}ms")
            else:
                print(f"   ❌ 前端服务异常 (状态码: {response.status_code})")
                self.issues.append(f"前端服务状态码异常: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️ 前端服务未运行 ({frontend_url})")
            self.warnings.append("前端服务未运行，需要启动前端")
        except Exception as e:
            print(f"   ❌ 前端连接错误: {e}")
            self.issues.append(f"前端连接错误: {e}")

    def check_evaluation_system(self):
        """检查评估系统"""
        self.print_section("评估系统检查")

        try:
            # 尝试导入评估系统
            sys.path.append(str(self.root_path))
            from real_evaluation_system import RealECGEvaluationSystem

            print("🧪 评估系统组件:")
            print("   ✅ RealECGEvaluationSystem 导入成功")

            # 初始化评估系统
            evaluator = RealECGEvaluationSystem()
            print("   ✅ 评估系统初始化成功")

            # 检查数据集管理器
            if hasattr(evaluator, 'dataset_manager'):
                datasets = evaluator.dataset_manager.datasets
                print(f"   ✅ 可用数据集: {len(datasets)} 个")

                for dataset_name, info in list(datasets.items())[:3]:  # 只显示前3个
                    size_mb = info.get('size_bytes', 0) / (1024 * 1024)
                    print(f"      📊 {dataset_name}: {size_mb:.1f} MB")
            else:
                print("   ⚠️ 数据集管理器未初始化")

            # 检查测试算法
            test_zip = self.root_path / "test_solution.zip"
            if test_zip.exists():
                print("   ✅ 测试算法文件存在")
                print(f"      📦 文件大小: {test_zip.stat().st_size} bytes")
            else:
                print("   ❌ 测试算法文件不存在")
                self.issues.append("测试算法文件不存在")

        except ImportError as e:
            print(f"   ❌ 评估系统导入失败: {e}")
            self.issues.append(f"评估系统导入失败: {e}")
        except Exception as e:
            print(f"   ❌ 评估系统检查失败: {e}")
            self.issues.append(f"评估系统检查失败: {e}")

    def check_ports(self):
        """检查端口占用情况"""
        self.print_section("端口占用检查")

        ports_to_check = [
            (3000, "前端服务"),
            (8000, "后端API"),
            (8080, "备用端口"),
        ]

        print("🔌 端口状态:")
        for port, description in ports_to_check:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()

                if result == 0:
                    print(f"   🟢 端口 {port:<5} - {description} (已使用)")
                else:
                    print(f"   ⚪ 端口 {port:<5} - {description} (可用)")
            except Exception as e:
                print(f"   ❌ 端口 {port:<5} - {description} (检查失败: {e})")

    def generate_startup_guide(self):
        """生成启动指南"""
        self.print_section("启动指南")

        if self.issues:
            print("❌ 发现严重问题，需要先解决:")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
            print("\n🔧 建议的解决步骤:")
            print("   1. 运行 'pip install -r mini-backend/requirements.txt' 安装依赖")
            print("   2. 检查缺失的文件并确保项目结构完整")
            print("   3. 重新运行此检查脚本")
            return False

        print("🚀 系统启动顺序:")
        print("   1. 启动后端服务:")
        print("      cd mini-backend && python main.py")
        print("      或者: python mini-backend/start_backend.py")
        print()
        print("   2. 启动前端服务:")
        print("      cd ecg-compression && python -m http.server 3000")
        print()
        print("   3. 访问系统:")
        print("      前端界面: http://localhost:3000")
        print("      API文档: http://localhost:8000/docs")
        print()
        print("   4. 运行测试:")
        print("      python demo_real_evaluation.py")
        print("      python test_concurrent_submissions.py")
        print()

        if self.warnings:
            print("⚠️ 注意事项:")
            for warning in self.warnings:
                print(f"   • {warning}")

        return True

    def run_check(self):
        """运行完整检查"""
        print("🔍 ECG评估系统完整性检查")
        print("🕒 开始时间:", time.strftime("%Y-%m-%d %H:%M:%S"))

        # 执行各项检查
        self.check_file_structure()
        self.check_dependencies()
        self.check_evaluation_system()
        self.check_ports()
        self.check_backend_status()
        self.check_frontend_status()

        # 生成报告
        print(f"\n{'='*60}")
        print("📋 检查总结")
        print("="*60)

        total_issues = len(self.issues)
        total_warnings = len(self.warnings)

        if total_issues == 0 and total_warnings == 0:
            print("🎉 系统检查完全通过！所有组件都已准备就绪。")
            status = "READY"
        elif total_issues == 0:
            print(f"✅ 系统基本准备就绪，有 {total_warnings} 个警告。")
            status = "READY_WITH_WARNINGS"
        else:
            print(f"❌ 发现 {total_issues} 个严重问题和 {total_warnings} 个警告。")
            status = "NOT_READY"

        print(f"📊 检查结果: {status}")
        print(f"🕒 检查完成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))

        # 生成启动指南
        ready = self.generate_startup_guide()

        return status, ready

def main():
    """主函数"""
    checker = SystemChecker()
    status, ready = checker.run_check()

    # 返回适当的退出码
    if status == "READY":
        sys.exit(0)
    elif status == "READY_WITH_WARNINGS":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()