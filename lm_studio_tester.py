import requests
import time
import json
import statistics
import threading
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import psutil
import numpy as np


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    response_time: float  # 响应时间（秒）
    tokens_per_second: float  # 每秒生成的token数
    total_tokens: int  # 总token数
    prompt_tokens: int  # 提示词token数
    completion_tokens: int  # 完成token数
    memory_usage: float  # 内存使用量（MB）
    cpu_usage: float  # CPU使用率（%）
    timestamp: str  # 时间戳


class LMStudioPerformanceTester:
    """LM Studio性能测试器"""
    
    def __init__(self, base_url: str = "http://localhost:1234", model_name: str = None):
        """
        初始化性能测试器
        
        Args:
            base_url: LM Studio服务器地址
            model_name: 模型名称
        """
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.session = requests.Session()
        self.metrics_history: List[PerformanceMetrics] = []
        
    def check_server_status(self) -> bool:
        """
        检查LM Studio服务器状态
        
        Returns:
            bool: 服务器是否可用
        """
        try:
            response = self.session.get(f"{self.base_url}/v1/models", timeout=5)
            if response.status_code == 200:
                models = response.json()
                print(f"✅ LM Studio服务器连接成功")
                print(f"📋 可用模型: {[model['id'] for model in models.get('data', [])]}")
                return True
            else:
                print(f"❌ 服务器响应错误: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ 无法连接到LM Studio服务器: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """
        获取可用模型列表
        
        Returns:
            List[str]: 模型名称列表
        """
        try:
            response = self.session.get(f"{self.base_url}/v1/models", timeout=5)
            if response.status_code == 200:
                models = response.json()
                return [model['id'] for model in models.get('data', [])]
            else:
                print(f"❌ 服务器响应错误: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"❌ 无法连接到LM Studio服务器: {e}")
            return []
    
    def get_system_metrics(self) -> tuple:
        """
        获取系统资源使用情况
        
        Returns:
            tuple: (内存使用量MB, CPU使用率%)
        """
        memory_info = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_mb = memory_info.used / 1024 / 1024
        return memory_mb, cpu_percent
    
    def single_inference_test(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> Optional[PerformanceMetrics]:
        """
        执行单次推理测试
        
        Args:
            prompt: 输入提示词
            max_tokens: 最大生成token数
            temperature: 温度参数
            
        Returns:
            PerformanceMetrics: 性能指标，如果失败返回None
        """
        start_time = time.time()
        memory_before, cpu_before = self.get_system_metrics()
        
        payload = {
            "model": self.model_name or "local-model",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=60
            )
            
            end_time = time.time()
            memory_after, cpu_after = self.get_system_metrics()
            
            if response.status_code == 200:
                data = response.json()
                response_time = end_time - start_time
                
                # 提取token信息
                usage = data.get('usage', {})
                total_tokens = usage.get('total_tokens', 0)
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)
                
                # 计算tokens per second
                tokens_per_second = completion_tokens / response_time if response_time > 0 else 0
                
                metrics = PerformanceMetrics(
                    response_time=response_time,
                    tokens_per_second=tokens_per_second,
                    total_tokens=total_tokens,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    memory_usage=memory_after,
                    cpu_usage=cpu_after,
                    timestamp=datetime.now().isoformat()
                )
                
                self.metrics_history.append(metrics)
                return metrics
            else:
                print(f"❌ API请求失败: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return None
    
    def batch_inference_test(self, prompts: List[str], max_tokens: int = 100) -> List[PerformanceMetrics]:
        """
        批量推理测试
        
        Args:
            prompts: 提示词列表
            max_tokens: 最大生成token数
            
        Returns:
            List[PerformanceMetrics]: 性能指标列表
        """
        results = []
        print(f"🚀 开始批量测试，共 {len(prompts)} 个请求...")
        
        for i, prompt in enumerate(prompts, 1):
            print(f"📝 执行第 {i}/{len(prompts)} 个请求...")
            metrics = self.single_inference_test(prompt, max_tokens)
            if metrics:
                results.append(metrics)
                print(f"✅ 完成 - 响应时间: {metrics.response_time:.2f}s, TPS: {metrics.tokens_per_second:.2f}")
            else:
                print(f"❌ 第 {i} 个请求失败")
            
            # 短暂延迟避免过载
            time.sleep(0.5)
        
        return results
    
    def concurrent_inference_test(self, prompt: str, num_concurrent: int = 5, max_tokens: int = 100) -> List[PerformanceMetrics]:
        """
        并发推理测试
        
        Args:
            prompt: 测试提示词
            num_concurrent: 并发数量
            max_tokens: 最大生成token数
            
        Returns:
            List[PerformanceMetrics]: 性能指标列表
        """
        results = []
        threads = []
        
        def worker():
            metrics = self.single_inference_test(prompt, max_tokens)
            if metrics:
                results.append(metrics)
        
        print(f"🔄 开始并发测试，并发数: {num_concurrent}")
        start_time = time.time()
        
        # 创建并启动线程
        for i in range(num_concurrent):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"✅ 并发测试完成 - 总耗时: {total_time:.2f}s, 成功请求: {len(results)}/{num_concurrent}")
        
        return results
    
    def stress_test(self, prompt: str, duration_seconds: int = 60, max_tokens: int = 50) -> List[PerformanceMetrics]:
        """
        压力测试
        
        Args:
            prompt: 测试提示词
            duration_seconds: 测试持续时间（秒）
            max_tokens: 最大生成token数
            
        Returns:
            List[PerformanceMetrics]: 性能指标列表
        """
        results = []
        start_time = time.time()
        request_count = 0
        
        print(f"⚡ 开始压力测试，持续时间: {duration_seconds}秒")
        
        while time.time() - start_time < duration_seconds:
            request_count += 1
            print(f"📊 压力测试请求 #{request_count}")
            
            metrics = self.single_inference_test(prompt, max_tokens)
            if metrics:
                results.append(metrics)
            
            # 短暂延迟
            time.sleep(0.1)
        
        total_time = time.time() - start_time
        print(f"✅ 压力测试完成 - 总耗时: {total_time:.2f}s, 总请求: {request_count}, 成功: {len(results)}")
        
        return results
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        生成性能报告
        
        Returns:
            Dict[str, Any]: 性能报告数据
        """
        if not self.metrics_history:
            return {"error": "没有性能数据"}
        
        response_times = [m.response_time for m in self.metrics_history]
        tokens_per_second = [m.tokens_per_second for m in self.metrics_history]
        memory_usage = [m.memory_usage for m in self.metrics_history]
        cpu_usage = [m.cpu_usage for m in self.metrics_history]
        
        report = {
            "测试概览": {
                "总请求数": len(self.metrics_history),
                "测试时间范围": f"{self.metrics_history[0].timestamp} 到 {self.metrics_history[-1].timestamp}"
            },
            "响应时间统计": {
                "平均值": f"{statistics.mean(response_times):.3f}s",
                "中位数": f"{statistics.median(response_times):.3f}s",
                "最小值": f"{min(response_times):.3f}s",
                "最大值": f"{max(response_times):.3f}s",
                "标准差": f"{statistics.stdev(response_times) if len(response_times) > 1 else 0:.3f}s"
            },
            "吞吐量统计": {
                "平均TPS": f"{statistics.mean(tokens_per_second):.2f} tokens/s",
                "最大TPS": f"{max(tokens_per_second):.2f} tokens/s",
                "最小TPS": f"{min(tokens_per_second):.2f} tokens/s"
            },
            "系统资源": {
                "平均内存使用": f"{statistics.mean(memory_usage):.1f} MB",
                "平均CPU使用率": f"{statistics.mean(cpu_usage):.1f}%",
                "最大内存使用": f"{max(memory_usage):.1f} MB",
                "最大CPU使用率": f"{max(cpu_usage):.1f}%"
            },
            "Token统计": {
                "总生成Token数": sum(m.completion_tokens for m in self.metrics_history),
                "平均每次生成Token数": f"{statistics.mean([m.completion_tokens for m in self.metrics_history]):.1f}",
                "总处理Token数": sum(m.total_tokens for m in self.metrics_history)
            }
        }
        
        return report
    
    def print_report(self):
        """打印性能报告"""
        report = self.generate_performance_report()
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return
        
        print("\n" + "="*60)
        print("🎯 LM Studio 性能测试报告")
        print("="*60)
        
        for section, data in report.items():
            print(f"\n📊 {section}:")
            for key, value in data.items():
                print(f"   {key}: {value}")
        
        print("\n" + "="*60)
    
    def save_detailed_results(self, filename: str = None):
        """
        保存详细测试结果到JSON文件
        
        Args:
            filename: 文件名，如果为None则自动生成
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lm_studio_performance_{timestamp}.json"
        
        data = {
            "test_summary": self.generate_performance_report(),
            "detailed_metrics": [
                {
                    "timestamp": m.timestamp,
                    "response_time": m.response_time,
                    "tokens_per_second": m.tokens_per_second,
                    "total_tokens": m.total_tokens,
                    "prompt_tokens": m.prompt_tokens,
                    "completion_tokens": m.completion_tokens,
                    "memory_usage": m.memory_usage,
                    "cpu_usage": m.cpu_usage
                }
                for m in self.metrics_history
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 详细结果已保存到: {filename}")


def get_test_prompts() -> List[str]:
    """
    获取测试用的提示词列表
    
    Returns:
        List[str]: 测试提示词列表
    """
    return [
        "请简单介绍一下人工智能的发展历史。",
        "解释一下什么是机器学习？",
        "写一个Python函数来计算斐波那契数列。",
        "描述一下深度学习和传统机器学习的区别。",
        "请推荐几本关于数据科学的书籍。",
        "解释一下什么是自然语言处理？",
        "如何优化神经网络的训练速度？",
        "什么是Transformer架构？",
        "请介绍一下强化学习的基本概念。",
        "如何评估机器学习模型的性能？"
    ]


if __name__ == "__main__":
    # 这个文件作为模块导入时不会执行以下代码
    pass