#!/usr/bin/env python3
"""
LM Studio AI推理性能测试主程序
支持多种测试模式：单次测试、批量测试、并发测试、压力测试
"""

import argparse
import sys
from lm_studio_tester import LMStudioPerformanceTester, get_test_prompts


def run_single_test(tester: LMStudioPerformanceTester):
    """运行单次推理测试"""
    print("\n🔍 单次推理测试")
    print("-" * 40)
    
    prompt = "请简单介绍一下人工智能的基本概念，不超过100字。"
    print(f"📝 测试提示词: {prompt}")
    
    metrics = tester.single_inference_test(prompt, max_tokens=150)
    if metrics:
        print(f"✅ 测试完成!")
        print(f"   响应时间: {metrics.response_time:.3f}秒")
        print(f"   生成速度: {metrics.tokens_per_second:.2f} tokens/秒")
        print(f"   生成Token数: {metrics.completion_tokens}")
        print(f"   内存使用: {metrics.memory_usage:.1f} MB")
        print(f"   CPU使用率: {metrics.cpu_usage:.1f}%")
    else:
        print("❌ 单次测试失败")


def run_batch_test(tester: LMStudioPerformanceTester):
    """运行批量推理测试"""
    print("\n📦 批量推理测试")
    print("-" * 40)
    
    prompts = get_test_prompts()[:5]  # 使用前5个测试提示词
    results = tester.batch_inference_test(prompts, max_tokens=100)
    
    if results:
        avg_response_time = sum(r.response_time for r in results) / len(results)
        avg_tps = sum(r.tokens_per_second for r in results) / len(results)
        print(f"\n📊 批量测试汇总:")
        print(f"   成功请求: {len(results)}/{len(prompts)}")
        print(f"   平均响应时间: {avg_response_time:.3f}秒")
        print(f"   平均生成速度: {avg_tps:.2f} tokens/秒")


def run_concurrent_test(tester: LMStudioPerformanceTester):
    """运行并发推理测试"""
    print("\n🔄 并发推理测试")
    print("-" * 40)
    
    prompt = "请用一句话解释什么是深度学习。"
    concurrent_count = 3  # 并发数量
    
    results = tester.concurrent_inference_test(prompt, num_concurrent=concurrent_count, max_tokens=80)
    
    if results:
        avg_response_time = sum(r.response_time for r in results) / len(results)
        total_tps = sum(r.tokens_per_second for r in results)
        print(f"\n📊 并发测试汇总:")
        print(f"   并发数: {concurrent_count}")
        print(f"   成功请求: {len(results)}")
        print(f"   平均响应时间: {avg_response_time:.3f}秒")
        print(f"   总吞吐量: {total_tps:.2f} tokens/秒")


def run_stress_test(tester: LMStudioPerformanceTester):
    """运行压力测试"""
    print("\n⚡ 压力测试")
    print("-" * 40)
    
    prompt = "简单回答：什么是AI？"
    duration = 30  # 测试30秒
    
    print(f"⏱️  将进行 {duration} 秒的压力测试...")
    results = tester.stress_test(prompt, duration_seconds=duration, max_tokens=50)
    
    if results:
        success_rate = len(results) / duration * 100  # 每秒成功请求数
        avg_tps = sum(r.tokens_per_second for r in results) / len(results)
        print(f"\n📊 压力测试汇总:")
        print(f"   测试时长: {duration}秒")
        print(f"   成功请求: {len(results)}")
        print(f"   平均每秒请求数: {len(results)/duration:.2f}")
        print(f"   平均生成速度: {avg_tps:.2f} tokens/秒")


def run_comprehensive_test(tester: LMStudioPerformanceTester):
    """运行综合测试"""
    print("\n🎯 综合性能测试")
    print("=" * 50)
    
    # 依次运行各种测试
    run_single_test(tester)
    run_batch_test(tester)
    run_concurrent_test(tester)
    run_stress_test(tester)
    
    # 生成最终报告
    print("\n" + "=" * 50)
    tester.print_report()
    
    # 保存详细结果
    tester.save_detailed_results()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="LM Studio AI推理性能测试工具")
    parser.add_argument("--url", default="http://localhost:1234", 
                       help="LM Studio服务器地址 (默认: http://localhost:1234)")
    parser.add_argument("--model", default=None, 
                       help="指定模型名称 (可选)")
    parser.add_argument("--test-type", choices=["single", "batch", "concurrent", "stress", "comprehensive"], 
                       default="comprehensive", help="测试类型 (默认: comprehensive)")
    parser.add_argument("--list", action="store_true",
                       help="列出所有可用模型")
    
    args = parser.parse_args()
    
    print("🚀 LM Studio AI推理性能测试工具")
    print("=" * 50)
    print(f"🌐 服务器地址: {args.url}")
    if args.model:
        print(f"🤖 指定模型: {args.model}")
    print(f"🧪 测试类型: {args.test_type}")
    print("=" * 50)
    
    # 创建测试器实例
    tester = LMStudioPerformanceTester(base_url=args.url, model_name=args.model)
    
    # 如果使用了--list选项，则只列出模型并退出
    if args.list:
        models = tester.get_available_models()
        if models:
            print("\n📋 可用模型列表:")
            for i, model in enumerate(models, 1):
                print(f"   {i}. {model}")
        else:
            print("\n❌ 无法获取模型列表，请确保LM Studio服务器正在运行且已加载模型。")
        sys.exit(0)
    
    # 检查服务器状态
    if not tester.check_server_status():
        print("\n❌ 无法连接到LM Studio服务器，请确保:")
        print("   1. LM Studio已启动")
        print("   2. 已加载模型")
        print("   3. 服务器地址正确")
        print("   4. 端口未被占用")
        sys.exit(1)
    
    # 根据参数运行相应测试
    try:
        if args.test_type == "single":
            run_single_test(tester)
        elif args.test_type == "batch":
            run_batch_test(tester)
        elif args.test_type == "concurrent":
            run_concurrent_test(tester)
        elif args.test_type == "stress":
            run_stress_test(tester)
        elif args.test_type == "comprehensive":
            run_comprehensive_test(tester)
        
        print("\n✅ 所有测试完成!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        if tester.metrics_history:
            print("📊 生成已完成测试的报告...")
            tester.print_report()
            tester.save_detailed_results()
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()