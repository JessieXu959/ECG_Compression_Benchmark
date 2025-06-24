#!/usr/bin/env python3
"""
测试后端API所有可用路由
"""

import requests
import json

def test_routes():
    """测试各种端点"""
    base_url = "http://localhost:8000"

    # 要测试的端点列表
    endpoints = [
        "/",
        "/health",
        "/api/leaderboard",
        "/api/global-stats",
        "/api/download/starter-kit",
        "/docs",
        "/openapi.json"
    ]

    print("🔍 测试API端点...")
    print("=" * 60)

    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            status = response.status_code
            content_type = response.headers.get('content-type', 'unknown')

            if status == 200:
                status_icon = "✅"
            elif status == 404:
                status_icon = "❌"
            else:
                status_icon = "⚠️"

            print(f"{status_icon} {endpoint:<30} | {status} | {content_type}")

            # 如果是下载端点且成功，显示额外信息
            if endpoint == "/api/download/starter-kit" and status == 200:
                content_length = response.headers.get('content-length', 'unknown')
                print(f"   📦 文件大小: {content_length} bytes")

        except requests.exceptions.RequestException as e:
            print(f"💥 {endpoint:<30} | ERROR | {str(e)}")

    print("=" * 60)

def get_openapi_spec():
    """获取OpenAPI规范查看所有路由"""
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        if response.status_code == 200:
            spec = response.json()
            paths = spec.get('paths', {})

            print("\n📋 从OpenAPI规范获取的所有路由:")
            print("-" * 50)

            for path, methods in paths.items():
                for method, details in methods.items():
                    summary = details.get('summary', 'No summary')
                    print(f"{method.upper():<8} {path:<35} | {summary}")

            return True
        else:
            print(f"❌ 无法获取OpenAPI规范: {response.status_code}")
            return False
    except Exception as e:
        print(f"💥 获取OpenAPI规范失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ECG压缩挑战赛 - API路由测试")
    print()

    # 测试基础端点
    test_routes()

    # 获取OpenAPI规范
    get_openapi_spec()