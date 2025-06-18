#!/usr/bin/env python3
"""
测试全局统计API的脚本
"""
import requests
import json

def test_global_stats_api():
    """测试全局统计API端点"""
    try:
        print("🔍 测试全局统计API...")

        # 测试API端点
        response = requests.get("http://localhost:8000/api/global-stats")

        if response.status_code == 200:
            data = response.json()
            print("✅ API响应成功!")
            print("\n📊 全局统计数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # 检查关键字段
            global_metrics = data.get('global_metrics', {})
            score_statistics = data.get('score_statistics', {})
            performance_metrics = data.get('performance_metrics', {})

            print(f"\n📈 关键指标:")
            print(f"  总用户数: {global_metrics.get('total_users', 0)}")
            print(f"  活跃团队: {global_metrics.get('active_teams', 0)}")
            print(f"  总提交数: {global_metrics.get('total_submissions', 0)}")
            print(f"  平均分数: {score_statistics.get('average_score', 'N/A')}")
            print(f"  最佳压缩比: {performance_metrics.get('best_compression_ratio', 'N/A')}")
            print(f"  最佳PRD: {performance_metrics.get('best_prd', 'N/A')}")

        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"   响应: {response.text}")

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_leaderboard_api():
    """测试排行榜API以确认数据完整性"""
    try:
        print("\n🏆 测试排行榜API...")

        response = requests.get("http://localhost:8000/api/leaderboard")

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✅ 排行榜API响应成功! 共有 {len(results)} 个条目")

            if results:
                print("\n前3名:")
                for i, entry in enumerate(results[:3]):
                    print(f"  {i+1}. {entry.get('participant_name', 'Unknown')} - 分数: {entry.get('score', 0)}")
            else:
                print("  没有排行榜数据")

        else:
            print(f"❌ 排行榜API请求失败: {response.status_code}")

    except Exception as e:
        print(f"❌ 排行榜测试失败: {str(e)}")

if __name__ == "__main__":
    print("🧪 开始测试全局统计功能...")
    test_global_stats_api()
    test_leaderboard_api()
    print("\n✨ 测试完成!")