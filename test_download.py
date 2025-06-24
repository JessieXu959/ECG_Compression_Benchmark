#!/usr/bin/env python3
"""
测试Starter Kit下载功能
"""

import requests
import os
from pathlib import Path

def test_download_api():
    """测试下载API端点"""
    print("🧪 测试Starter Kit下载功能...")

    # API端点
    url = "http://localhost:8000/api/download/starter-kit"

    try:
        # 发送GET请求
        print(f"📡 请求: {url}")
        response = requests.get(url)

        print(f"📊 状态码: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")

        if response.status_code == 200:
            # 检查content-type
            content_type = response.headers.get('content-type', '')
            print(f"📦 内容类型: {content_type}")

            if 'application/zip' in content_type or 'application/octet-stream' in content_type:
                # 保存文件
                test_file = Path("test_download.zip")
                with open(test_file, 'wb') as f:
                    f.write(response.content)

                file_size = test_file.stat().st_size
                print(f"✅ 文件下载成功: {test_file}")
                print(f"📏 文件大小: {file_size} bytes")

                # 清理测试文件
                test_file.unlink()
                print("🧹 测试文件已清理")

                return True
            else:
                print(f"❌ 错误的内容类型: {content_type}")
                print(f"📄 响应内容: {response.text[:200]}...")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"📄 错误信息: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 后端服务器未运行")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def check_file_exists():
    """检查starter_kit.zip文件是否存在"""
    project_root = Path(__file__).parent
    starter_kit_path = project_root / "starter_kit.zip"

    print(f"🔍 检查文件: {starter_kit_path}")

    if starter_kit_path.exists():
        file_size = starter_kit_path.stat().st_size
        print(f"✅ 文件存在: {file_size} bytes")
        return True
    else:
        print("❌ 文件不存在")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 ECG压缩挑战赛 - Starter Kit下载测试")
    print("=" * 50)

    # 检查文件
    print("\n1️⃣ 检查starter_kit.zip文件...")
    file_exists = check_file_exists()

    if file_exists:
        print("\n2️⃣ 测试下载API...")
        api_works = test_download_api()

        if api_works:
            print("\n🎉 下载功能测试通过!")
        else:
            print("\n💔 下载功能测试失败!")
    else:
        print("\n💔 无法进行API测试，文件不存在!")

    print("\n" + "=" * 50)