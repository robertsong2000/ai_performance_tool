# LM Studio AI推理性能测试工具

这是一个专门用于测试LM Studio本地AI推理性能的Python工具包。支持多种测试模式，提供详细的性能指标分析和可视化报告。

## 功能特性

- 🚀 **多种测试模式**: 单次测试、批量测试、并发测试、压力测试
- 📊 **详细性能指标**: 响应时间、吞吐量、资源使用情况
- 📈 **可视化报告**: 自动生成图表和仪表板
- 💾 **数据导出**: 支持JSON格式的详细测试结果
- 🔧 **灵活配置**: 支持自定义服务器地址、模型等参数

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 启动LM Studio
确保LM Studio已启动并加载了模型，默认服务地址为 `http://localhost:1234`

### 2. 运行性能测试

#### 综合测试（推荐）
```bash
python main.py
```

#### 指定测试类型
```bash
# 单次推理测试
python main.py --test-type single

# 批量测试
python main.py --test-type batch

# 并发测试
python main.py --test-type concurrent

# 压力测试
python main.py --test-type stress
```

#### 自定义服务器地址
```bash
python main.py --url http://localhost:8080 --model your-model-name
```

### 3. 生成可视化报告

```bash
# 生成所有图表
python visualizer.py

# 生成特定图表
python visualizer.py --chart dashboard
python visualizer.py --chart response
python visualizer.py --chart throughput

# 指定结果文件
python visualizer.py --file lm_studio_performance_20231201_143022.json
```

## 测试模式说明

### 单次测试 (single)
- 执行一次推理请求
- 测试基本连接和响应性能
- 适合快速验证服务状态

### 批量测试 (batch)
- 顺序执行多个不同的推理请求
- 测试模型在不同任务上的表现
- 评估平均性能水平

### 并发测试 (concurrent)
- 同时发送多个推理请求
- 测试服务器的并发处理能力
- 评估多用户场景下的性能

### 压力测试 (stress)
- 在指定时间内持续发送请求
- 测试系统的稳定性和极限性能
- 发现性能瓶颈和资源限制

## 性能指标

### 响应时间指标
- **平均响应时间**: 所有请求的平均处理时间
- **中位数响应时间**: 50%请求的响应时间
- **最大/最小响应时间**: 极值情况
- **标准差**: 响应时间的稳定性

### 吞吐量指标
- **Tokens per Second (TPS)**: 每秒生成的token数量
- **平均TPS**: 所有请求的平均生成速度
- **峰值TPS**: 最高生成速度

### 资源使用指标
- **内存使用量**: 测试期间的内存占用
- **CPU使用率**: 测试期间的CPU占用
- **Token统计**: 输入/输出token的详细统计

## 输出文件

### 测试报告
- 控制台输出详细的性能报告
- 包含各项指标的统计分析

### JSON结果文件
- 格式: `lm_studio_performance_YYYYMMDD_HHMMSS.json`
- 包含完整的测试数据和汇总信息
- 可用于后续分析和可视化

### 可视化图表
- `response_time_trend.png`: 响应时间趋势图
- `throughput_trend.png`: 吞吐量趋势图
- `resource_usage.png`: 资源使用情况图
- `performance_distribution.png`: 性能分布图
- `performance_dashboard.png`: 综合仪表板

## 使用示例

### 基本性能测试
```bash
# 运行综合测试
python main.py

# 查看结果
python visualizer.py
```

### 自定义测试场景
```bash
# 测试特定模型的并发性能
python main.py --url http://localhost:1234 --model llama-2-7b --test-type concurrent

# 进行30秒压力测试
python main.py --test-type stress
```

### 比较不同配置
```bash
# 测试配置A
python main.py --model model-a --test-type comprehensive
mv lm_studio_performance_*.json results_model_a.json

# 测试配置B
python main.py --model model-b --test-type comprehensive
mv lm_studio_performance_*.json results_model_b.json

# 分别生成报告
python visualizer.py --file results_model_a.json
python visualizer.py --file results_model_b.json
```

## 故障排除

### 连接问题
- 确保LM Studio已启动
- 检查服务器地址和端口
- 验证模型已正确加载

### 性能问题
- 检查系统资源使用情况
- 调整并发数量和测试参数
- 监控网络延迟

### 图表生成问题
- 确保安装了matplotlib
- 检查测试结果文件是否存在
- 验证数据格式是否正确

## 注意事项

1. **资源监控**: 测试过程中会监控系统资源，确保有足够的内存和CPU
2. **网络延迟**: 本地测试通常延迟很低，远程测试需要考虑网络因素
3. **模型差异**: 不同模型的性能表现可能差异很大
4. **测试负载**: 压力测试可能会对系统造成较高负载，请谨慎使用

## 技术支持

如果遇到问题或需要功能建议，请检查：
1. LM Studio的官方文档
2. 确保所有依赖库已正确安装
3. 检查Python版本兼容性（推荐Python 3.8+）