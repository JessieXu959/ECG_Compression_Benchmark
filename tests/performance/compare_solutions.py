#!/usr/bin/env python3
"""
比较不同ECG压缩算法方案的表现
"""
from real_evaluation_system import RealECGEvaluationSystem
import matplotlib.pyplot as plt
import numpy as np

def evaluate_solution(zip_path, name):
    """评估指定的解决方案"""
    print(f"🧪 评估方案: {name}...")

    # 初始化评估系统
    evaluator = RealECGEvaluationSystem()

    # 评估解决方案
    result = evaluator.evaluate_submission(zip_path)

    if result.get("status") == "completed":
        metrics = result.get("metrics", {})
        print(f"✅ 评估成功")
        print(f"  CR: {metrics.get('CR', 'N/A'):.2f}")
        print(f"  PRD: {metrics.get('PRD', 'N/A'):.2f}%")
        print(f"  SNR: {metrics.get('SNR', 'N/A'):.2f} dB")
        print(f"  最终得分: {metrics.get('Score', 'N/A'):.4f}")
    else:
        print(f"❌ 评估失败: {result.get('errors', ['未知错误'])}")

    return result

def compare_solutions():
    """比较不同的解决方案"""
    print("📊 比较ECG压缩算法方案...")

    # 评估原始解决方案
    basic_result = evaluate_solution('solution/solution.zip', "原始方案")

    # 评估更新后的解决方案
    updated_result = evaluate_solution('solution/solution_updated.zip', "更新方案")

    # 评估优化后的解决方案
    optimized_result = evaluate_solution('solution/solution_optimized.zip', "优化方案")

    # 比较结果
    solutions = ["原始方案", "更新方案", "优化方案"]
    results = [basic_result, updated_result, optimized_result]

    # 提取指标
    cr_values = []
    prd_values = []
    snr_values = []
    scores = []

    for result in results:
        if result.get("status") == "completed":
            metrics = result.get("metrics", {})
            cr_values.append(metrics.get('CR', 0))
            prd_values.append(metrics.get('PRD', 0))
            snr_values.append(metrics.get('SNR', 0))
            scores.append(metrics.get('Score', 0))
        else:
            cr_values.append(0)
            prd_values.append(0)
            snr_values.append(0)
            scores.append(0)

    # 绘制比较图表
    plt.figure(figsize=(15, 10))

    # 压缩比比较
    plt.subplot(2, 2, 1)
    plt.bar(solutions, cr_values)
    plt.title('压缩比 (CR) 比较')
    plt.ylabel('压缩比')
    plt.grid(True, linestyle='--', alpha=0.7)

    # PRD比较
    plt.subplot(2, 2, 2)
    plt.bar(solutions, prd_values)
    plt.title('百分比均方根差 (PRD) 比较')
    plt.ylabel('PRD (%)')
    plt.grid(True, linestyle='--', alpha=0.7)

    # SNR比较
    plt.subplot(2, 2, 3)
    plt.bar(solutions, snr_values)
    plt.title('信噪比 (SNR) 比较')
    plt.ylabel('SNR (dB)')
    plt.grid(True, linestyle='--', alpha=0.7)

    # 最终得分比较
    plt.subplot(2, 2, 4)
    plt.bar(solutions, scores)
    plt.title('最终得分比较')
    plt.ylabel('得分')
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig('solutions_comparison.png')
    plt.close()

    print("\n📈 比较结果总结:")
    print(f"{'方案':<12} {'压缩比':<10} {'PRD %':<10} {'SNR (dB)':<10} {'得分':<10}")
    print("-" * 60)
    for i, solution in enumerate(solutions):
        print(f"{solution:<12} {cr_values[i]:<10.2f} {prd_values[i]:<10.2f} {snr_values[i]:<10.2f} {scores[i]:<10.4f}")

    # 找出最佳方案
    best_index = np.argmax(scores)
    print(f"\n🏆 最佳方案: {solutions[best_index]}")
    print(f"   得分: {scores[best_index]:.4f}")
    print(f"   相对原始方案提升: {(scores[best_index]/scores[0] - 1)*100:.2f}%")

    print("\n💾 比较图表已保存为 'solutions_comparison.png'")

if __name__ == "__main__":
    compare_solutions()