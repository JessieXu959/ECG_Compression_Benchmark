#!/usr/bin/env python3
"""
系统性能监控脚本
监控ECG评估系统的资源使用情况
"""

import psutil
import time
import requests
import json
from datetime import datetime
import threading
import signal
import sys

class SystemPerformanceMonitor:
    def __init__(self, backend_url="http://localhost:8000"):
        self.backend_url = backend_url
        self.monitoring = False
        self.metrics = []
        self.start_time = None

    def get_system_metrics(self):
        """获取系统指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # 获取网络统计
            net_io = psutil.net_io_counters()

            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / (1024 * 1024),
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_used_gb": disk.used / (1024 * 1024 * 1024),
                "disk_free_gb": disk.free / (1024 * 1024 * 1024),
                "network_bytes_sent": net_io.bytes_sent,
                "network_bytes_recv": net_io.bytes_recv
            }

            return metrics
        except Exception as e:
            print(f"❌ 获取系统指标时出错: {e}")
            return None

    def check_backend_status(self):
        """检查后端状态"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "backend_online": True,
                    "total_submissions": data.get("total_submissions", 0),
                    "active_users": data.get("active_users", 0),
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                }
            else:
                return {
                    "backend_online": False,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "backend_online": False,
                "error": str(e)
            }

    def get_process_metrics(self):
        """获取Python进程指标"""
        try:
            current_process = psutil.Process()

            # 查找可能的backend进程
            backend_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('main.py' in cmd or 'uvicorn' in cmd for cmd in cmdline):
                        backend_processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu_percent": proc.cpu_percent(),
                            "memory_mb": proc.info['memory_info'].rss / (1024 * 1024),
                            "cmdline": ' '.join(cmdline[:3])  # 只显示前3个参数
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return {
                "current_process": {
                    "pid": current_process.pid,
                    "cpu_percent": current_process.cpu_percent(),
                    "memory_mb": current_process.memory_info().rss / (1024 * 1024)
                },
                "backend_processes": backend_processes
            }
        except Exception as e:
            print(f"⚠️ 获取进程指标时出错: {e}")
            return {"error": str(e)}

    def monitor_loop(self, interval=5):
        """监控循环"""
        print(f"🔍 开始系统监控 (间隔: {interval}秒)")
        print("按 Ctrl+C 停止监控")
        print("=" * 60)

        self.start_time = time.time()
        self.monitoring = True

        try:
            while self.monitoring:
                # 获取各种指标
                system_metrics = self.get_system_metrics()
                backend_status = self.check_backend_status()
                process_metrics = self.get_process_metrics()

                if system_metrics:
                    # 合并所有指标
                    combined_metrics = {
                        **system_metrics,
                        "backend": backend_status,
                        "processes": process_metrics,
                        "uptime_seconds": time.time() - self.start_time
                    }

                    self.metrics.append(combined_metrics)

                    # 实时显示
                    self.display_current_metrics(combined_metrics)

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n⏹️  监控已停止")
            self.monitoring = False
            self.generate_report()

    def display_current_metrics(self, metrics):
        """显示当前指标"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # 清屏并显示当前状态
        print(f"\r🕒 {timestamp} | CPU: {metrics['cpu_percent']:.1f}% | "
              f"内存: {metrics['memory_percent']:.1f}% ({metrics['memory_used_mb']:.0f}MB) | "
              f"后端: {'🟢' if metrics['backend']['backend_online'] else '🔴'}", end="")

        # 每30秒显示详细信息
        if len(self.metrics) % 6 == 0:  # 30秒 / 5秒间隔 = 6次
            print()  # 换行
            self.display_detailed_metrics(metrics)

    def display_detailed_metrics(self, metrics):
        """显示详细指标"""
        print("\n" + "=" * 60)
        print(f"📊 详细监控报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 系统资源
        print("🖥️  系统资源:")
        print(f"   CPU使用率: {metrics['cpu_percent']:.1f}%")
        print(f"   内存使用率: {metrics['memory_percent']:.1f}% ({metrics['memory_used_mb']:.0f}MB / {metrics['memory_used_mb'] + metrics['memory_available_mb']:.0f}MB)")
        print(f"   磁盘使用率: {metrics['disk_percent']:.1f}% ({metrics['disk_used_gb']:.1f}GB / {metrics['disk_used_gb'] + metrics['disk_free_gb']:.1f}GB)")

        # 后端状态
        backend = metrics['backend']
        print(f"\n🌐 后端状态:")
        if backend['backend_online']:
            print(f"   状态: 🟢 在线")
            print(f"   响应时间: {backend.get('response_time_ms', 0):.1f}ms")
            print(f"   总提交数: {backend.get('total_submissions', 0)}")
            print(f"   活跃用户: {backend.get('active_users', 0)}")
        else:
            print(f"   状态: 🔴 离线")
            if 'error' in backend:
                print(f"   错误: {backend['error']}")

        # 进程信息
        processes = metrics['processes']
        if 'backend_processes' in processes and processes['backend_processes']:
            print(f"\n🔧 后端进程:")
            for proc in processes['backend_processes']:
                print(f"   PID {proc['pid']}: CPU {proc['cpu_percent']:.1f}%, 内存 {proc['memory_mb']:.0f}MB - {proc['cmdline']}")

        print(f"\n⏱️  运行时间: {metrics['uptime_seconds']:.0f}秒")
        print("=" * 60)

    def generate_report(self):
        """生成最终报告"""
        if not self.metrics:
            print("❌ 没有收集到监控数据")
            return

        print("\n📋 监控总结报告")
        print("=" * 60)

        # 计算统计数据
        cpu_values = [m['cpu_percent'] for m in self.metrics]
        memory_values = [m['memory_percent'] for m in self.metrics]

        print(f"📊 统计数据 (基于 {len(self.metrics)} 个样本):")
        print(f"   CPU使用率: 平均 {sum(cpu_values)/len(cpu_values):.1f}%, "
              f"最高 {max(cpu_values):.1f}%, 最低 {min(cpu_values):.1f}%")
        print(f"   内存使用率: 平均 {sum(memory_values)/len(memory_values):.1f}%, "
              f"最高 {max(memory_values):.1f}%, 最低 {min(memory_values):.1f}%")

        # 后端可用性
        backend_online_count = sum(1 for m in self.metrics if m['backend']['backend_online'])
        availability = (backend_online_count / len(self.metrics)) * 100
        print(f"   后端可用性: {availability:.1f}% ({backend_online_count}/{len(self.metrics)})")

        # 响应时间统计
        response_times = [m['backend'].get('response_time_ms', 0)
                         for m in self.metrics if m['backend']['backend_online']]
        if response_times:
            print(f"   后端响应时间: 平均 {sum(response_times)/len(response_times):.1f}ms, "
                  f"最快 {min(response_times):.1f}ms, 最慢 {max(response_times):.1f}ms")

        # 保存详细数据
        report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2, ensure_ascii=False)
            print(f"\n💾 详细数据已保存到: {report_file}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")

        print("=" * 60)

def signal_handler(sig, frame):
    """信号处理器"""
    print('\n\n⏹️  收到停止信号，正在生成报告...')
    sys.exit(0)

def main():
    """主函数"""
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)

    print("🔍 ECG评估系统性能监控工具")
    print("=" * 60)

    monitor = SystemPerformanceMonitor()

    # 初始检查
    print("🔧 初始系统检查...")
    initial_metrics = monitor.get_system_metrics()
    initial_backend = monitor.check_backend_status()

    if initial_metrics:
        print(f"✅ CPU: {initial_metrics['cpu_percent']:.1f}%, "
              f"内存: {initial_metrics['memory_percent']:.1f}%, "
              f"后端: {'🟢 在线' if initial_backend['backend_online'] else '🔴 离线'}")

    # 开始监控
    try:
        monitor.monitor_loop(interval=5)
    except Exception as e:
        print(f"❌ 监控过程中出错: {e}")
    finally:
        if monitor.metrics:
            monitor.generate_report()

if __name__ == "__main__":
    main()