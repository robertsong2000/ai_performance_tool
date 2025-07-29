#!/usr/bin/env python3
"""
可视化性能测试结果的工具
生成图表和可视化报告
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import argparse
import os
from typing import List, Dict, Any


class PerformanceVisualizer:
    """性能数据可视化器"""
    
    def __init__(self, data_file: str):
        """
        初始化可视化器
        
        Args:
            data_file: 性能数据JSON文件路径
        """
        self.data_file = data_file
        self.data = self.load_data()
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def load_data(self) -> Dict[str, Any]:
        """
        加载性能数据
        
        Returns:
            Dict[str, Any]: 性能数据
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到数据文件: {self.data_file}")
        except json.JSONDecodeError:
            raise ValueError(f"数据文件格式错误: {self.data_file}")
    
    def create_response_time_chart(self) -> None:
        """创建响应时间图表"""
        metrics = self.data.get('detailed_metrics', [])
        if not metrics:
            print("❌ 没有详细指标数据")
            return
        
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in metrics]
        response_times = [m['response_time'] for m in metrics]
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, response_times, 'b-', marker='o', markersize=4, linewidth=2)
        plt.title('响应时间趋势', fontsize=16, fontweight='bold')
        plt.xlabel('时间', fontsize=12)
        plt.ylabel('响应时间 (秒)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 添加统计信息
        avg_time = np.mean(response_times)
        plt.axhline(y=avg_time, color='r', linestyle='--', alpha=0.7, 
                   label=f'平均值: {avg_time:.3f}s')
        plt.legend()
        
        plt.savefig('response_time_trend.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("📊 响应时间图表已保存: response_time_trend.png")
    
    def create_throughput_chart(self) -> None:
        """创建吞吐量图表"""
        metrics = self.data.get('detailed_metrics', [])
        if not metrics:
            print("❌ 没有详细指标数据")
            return
        
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in metrics]
        tps_values = [m['tokens_per_second'] for m in metrics]
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, tps_values, 'g-', marker='s', markersize=4, linewidth=2)
        plt.title('吞吐量趋势 (Tokens per Second)', fontsize=16, fontweight='bold')
        plt.xlabel('时间', fontsize=12)
        plt.ylabel('Tokens/秒', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 添加统计信息
        avg_tps = np.mean(tps_values)
        plt.axhline(y=avg_tps, color='r', linestyle='--', alpha=0.7, 
                   label=f'平均值: {avg_tps:.2f} tokens/s')
        plt.legend()
        
        plt.savefig('throughput_trend.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("📊 吞吐量图表已保存: throughput_trend.png")
    
    def create_resource_usage_chart(self) -> None:
        """创建资源使用图表"""
        metrics = self.data.get('detailed_metrics', [])
        if not metrics:
            print("❌ 没有详细指标数据")
            return
        
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in metrics]
        memory_usage = [m['memory_usage'] for m in metrics]
        cpu_usage = [m['cpu_usage'] for m in metrics]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # 内存使用图
        ax1.plot(timestamps, memory_usage, 'purple', marker='o', markersize=3, linewidth=2)
        ax1.set_title('内存使用趋势', fontsize=14, fontweight='bold')
        ax1.set_ylabel('内存使用 (MB)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # CPU使用图
        ax2.plot(timestamps, cpu_usage, 'orange', marker='^', markersize=3, linewidth=2)
        ax2.set_title('CPU使用率趋势', fontsize=14, fontweight='bold')
        ax2.set_xlabel('时间', fontsize=12)
        ax2.set_ylabel('CPU使用率 (%)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('resource_usage.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("📊 资源使用图表已保存: resource_usage.png")
    
    def create_performance_distribution(self) -> None:
        """创建性能分布图"""
        metrics = self.data.get('detailed_metrics', [])
        if not metrics:
            print("❌ 没有详细指标数据")
            return
        
        response_times = [m['response_time'] for m in metrics]
        tps_values = [m['tokens_per_second'] for m in metrics]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 响应时间分布
        ax1.hist(response_times, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_title('响应时间分布', fontsize=14, fontweight='bold')
        ax1.set_xlabel('响应时间 (秒)', fontsize=12)
        ax1.set_ylabel('频次', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # 吞吐量分布
        ax2.hist(tps_values, bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
        ax2.set_title('吞吐量分布', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Tokens/秒', fontsize=12)
        ax2.set_ylabel('频次', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('performance_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("📊 性能分布图表已保存: performance_distribution.png")
    
    def create_summary_dashboard(self) -> None:
        """创建综合仪表板"""
        metrics = self.data.get('detailed_metrics', [])
        summary = self.data.get('test_summary', {})
        
        if not metrics:
            print("❌ 没有详细指标数据")
            return
        
        fig = plt.figure(figsize=(16, 12))
        
        # 创建网格布局
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in metrics]
        response_times = [m['response_time'] for m in metrics]
        tps_values = [m['tokens_per_second'] for m in metrics]
        memory_usage = [m['memory_usage'] for m in metrics]
        cpu_usage = [m['cpu_usage'] for m in metrics]
        
        # 1. 响应时间趋势
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.plot(timestamps, response_times, 'b-', marker='o', markersize=3)
        ax1.set_title('响应时间趋势', fontweight='bold')
        ax1.set_ylabel('响应时间 (秒)')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. 关键指标摘要
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.axis('off')
        summary_text = f"""
关键指标摘要

总请求数: {len(metrics)}
平均响应时间: {np.mean(response_times):.3f}s
平均吞吐量: {np.mean(tps_values):.2f} t/s
最大响应时间: {max(response_times):.3f}s
最小响应时间: {min(response_times):.3f}s
        """
        ax2.text(0.1, 0.9, summary_text, transform=ax2.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        # 3. 吞吐量趋势
        ax3 = fig.add_subplot(gs[1, :2])
        ax3.plot(timestamps, tps_values, 'g-', marker='s', markersize=3)
        ax3.set_title('吞吐量趋势', fontweight='bold')
        ax3.set_ylabel('Tokens/秒')
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. 响应时间分布
        ax4 = fig.add_subplot(gs[1, 2])
        ax4.hist(response_times, bins=15, alpha=0.7, color='skyblue', edgecolor='black')
        ax4.set_title('响应时间分布', fontweight='bold')
        ax4.set_xlabel('响应时间 (秒)')
        ax4.set_ylabel('频次')
        
        # 5. 内存使用
        ax5 = fig.add_subplot(gs[2, 0])
        ax5.plot(timestamps, memory_usage, 'purple', marker='o', markersize=2)
        ax5.set_title('内存使用', fontweight='bold')
        ax5.set_ylabel('内存 (MB)')
        ax5.tick_params(axis='x', rotation=45)
        ax5.grid(True, alpha=0.3)
        
        # 6. CPU使用
        ax6 = fig.add_subplot(gs[2, 1])
        ax6.plot(timestamps, cpu_usage, 'orange', marker='^', markersize=2)
        ax6.set_title('CPU使用率', fontweight='bold')
        ax6.set_ylabel('CPU (%)')
        ax6.tick_params(axis='x', rotation=45)
        ax6.grid(True, alpha=0.3)
        
        # 7. 吞吐量分布
        ax7 = fig.add_subplot(gs[2, 2])
        ax7.hist(tps_values, bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
        ax7.set_title('吞吐量分布', fontweight='bold')
        ax7.set_xlabel('Tokens/秒')
        ax7.set_ylabel('频次')
        
        plt.suptitle('LM Studio 性能测试综合仪表板', fontsize=16, fontweight='bold')
        plt.savefig('performance_dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("📊 综合仪表板已保存: performance_dashboard.png")
    
    def generate_all_charts(self) -> None:
        """生成所有图表"""
        print("🎨 开始生成性能可视化图表...")
        
        try:
            self.create_response_time_chart()
            self.create_throughput_chart()
            self.create_resource_usage_chart()
            self.create_performance_distribution()
            self.create_summary_dashboard()
            
            print("\n✅ 所有图表生成完成!")
            print("📁 生成的文件:")
            print("   - response_time_trend.png")
            print("   - throughput_trend.png")
            print("   - resource_usage.png")
            print("   - performance_distribution.png")
            print("   - performance_dashboard.png")
            
        except Exception as e:
            print(f"❌ 生成图表时发生错误: {e}")


def find_latest_result_file() -> str:
    """
    查找最新的测试结果文件
    
    Returns:
        str: 最新结果文件路径
    """
    result_files = [f for f in os.listdir('.') if f.startswith('lm_studio_performance_') and f.endswith('.json')]
    
    if not result_files:
        raise FileNotFoundError("当前目录下没有找到测试结果文件")
    
    # 按修改时间排序，返回最新的
    result_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return result_files[0]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="LM Studio性能测试结果可视化工具")
    parser.add_argument("--file", "-f", help="指定测试结果JSON文件路径")
    parser.add_argument("--chart", "-c", 
                       choices=["response", "throughput", "resource", "distribution", "dashboard", "all"],
                       default="all", help="指定要生成的图表类型")
    
    args = parser.parse_args()
    
    # 确定数据文件
    if args.file:
        data_file = args.file
    else:
        try:
            data_file = find_latest_result_file()
            print(f"🔍 使用最新的测试结果文件: {data_file}")
        except FileNotFoundError as e:
            print(f"❌ {e}")
            print("💡 请先运行性能测试或使用 --file 参数指定结果文件")
            return
    
    # 创建可视化器
    try:
        visualizer = PerformanceVisualizer(data_file)
        
        # 根据参数生成相应图表
        if args.chart == "response":
            visualizer.create_response_time_chart()
        elif args.chart == "throughput":
            visualizer.create_throughput_chart()
        elif args.chart == "resource":
            visualizer.create_resource_usage_chart()
        elif args.chart == "distribution":
            visualizer.create_performance_distribution()
        elif args.chart == "dashboard":
            visualizer.create_summary_dashboard()
        elif args.chart == "all":
            visualizer.generate_all_charts()
            
    except Exception as e:
        print(f"❌ 可视化过程中发生错误: {e}")


if __name__ == "__main__":
    main()