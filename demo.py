#!/usr/bin/env python3
"""
简单的演示脚本，展示如何使用LM Studio性能测试工具
"""

from lm_studio_tester import LMStudioPerformanceTester, get_test_prompts


def demo_basic_usage():
    """演示基本使用方法"""
    print("🎯 LM Studio性能测试工具演示")
    print("=" * 50)
    
    # 创建测试器实例
    tester = LMStudioPerformanceTester()
    
    # 检查服务器状态
    print("1️⃣ 检查服务器连接...")
    if not tester.check_server_status():
        print("❌ 无法连接到LM Studio，请确保服务已启动")
        return
    
    # 单次测试
    print("\n2️⃣ 执行单次推理测试...")
    prompt = "请用一句话解释什么是人工智能。"
    metrics = tester.single_inference_test(prompt, max_tokens=50)
    
    if metrics:
        print(f"✅ 测试成功!")
        print(f"   响应时间: {metrics.response_time:.3f}秒")
        print(f"   生成速度: {metrics.tokens_per_second:.2f} tokens/秒")
        print(f"   生成内容长度: {metrics.completion_tokens} tokens")
    
    # 批量测试
    print("\n3️⃣ 执行批量测试...")
    test_prompts = [
        "什么是机器学习？",
        "解释深度学习的概念。",
        "Python有什么优势？"
    ]
    
    batch_results = tester.batch_inference_test(test_prompts, max_tokens=80)
    print(f"✅ 批量测试完成，成功 {len(batch_results)}/{len(test_prompts)} 个请求")
    
    # 生成报告
    print("\n4️⃣ 生成性能报告...")
    tester.print_report()
    
    # 保存结果
    print("\n5️⃣ 保存测试结果...")
    tester.save_detailed_results("demo_results.json")
    
    print("\n🎉 演示完成!")
    print("💡 提示: 运行 'python visualizer.py --file demo_results.json' 查看可视化报告")


def demo_custom_test():
    """演示自定义测试"""
    print("\n🔧 自定义测试演示")
    print("-" * 30)
    
    # 使用自定义参数创建测试器
    tester = LMStudioPerformanceTester(
        base_url="http://localhost:1234",
        model_name="custom-model"  # 可以指定特定模型
    )
    
    if not tester.check_server_status():
        print("❌ 服务器连接失败")
        return
    
    # 自定义测试参数
    custom_prompt = "编写一个Python函数来计算两个数的最大公约数。"
    
    print("🧪 执行自定义参数测试...")
    metrics = tester.single_inference_test(
        prompt=custom_prompt,
        max_tokens=200,  # 更长的输出
        temperature=0.3  # 更确定性的输出
    )
    
    if metrics:
        print(f"✅ 自定义测试完成")
        print(f"   响应时间: {metrics.response_time:.3f}秒")
        print(f"   生成速度: {metrics.tokens_per_second:.2f} tokens/秒")


def demo_performance_comparison():
    """演示性能对比测试"""
    print("\n📊 性能对比演示")
    print("-" * 30)
    
    tester = LMStudioPerformanceTester()
    
    if not tester.check_server_status():
        print("❌ 服务器连接失败")
        return
    
    # 测试不同长度的输出
    test_cases = [
        {"name": "短回答", "max_tokens": 50, "prompt": "简单回答：什么是AI？"},
        {"name": "中等回答", "max_tokens": 150, "prompt": "详细解释什么是人工智能？"},
        {"name": "长回答", "max_tokens": 300, "prompt": "请详细介绍人工智能的发展历史和应用领域。"}
    ]
    
    results = {}
    
    for case in test_cases:
        print(f"🧪 测试 {case['name']} (max_tokens={case['max_tokens']})")
        metrics = tester.single_inference_test(case['prompt'], case['max_tokens'])
        
        if metrics:
            results[case['name']] = {
                'response_time': metrics.response_time,
                'tokens_per_second': metrics.tokens_per_second,
                'completion_tokens': metrics.completion_tokens
            }
            print(f"   ✅ 完成 - {metrics.response_time:.3f}s, {metrics.tokens_per_second:.2f} TPS")
        else:
            print(f"   ❌ 失败")
    
    # 显示对比结果
    print(f"\n📈 性能对比结果:")
    print(f"{'测试类型':<10} {'响应时间':<10} {'生成速度':<12} {'Token数':<8}")
    print("-" * 45)
    
    for name, data in results.items():
        print(f"{name:<10} {data['response_time']:<10.3f} {data['tokens_per_second']:<12.2f} {data['completion_tokens']:<8}")


if __name__ == "__main__":
    try:
        # 基本演示
        demo_basic_usage()
        
        # 自定义测试演示
        demo_custom_test()
        
        # 性能对比演示
        demo_performance_comparison()
        
        print("\n🎊 所有演示完成!")
        print("📚 更多功能请参考 README.md 或运行 'python main.py --help'")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        print("💡 请确保LM Studio已启动并加载了模型")