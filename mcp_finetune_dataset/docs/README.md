
## 数据集特点

### 1. 工具覆盖
- **web_search**: 网络搜索功能
- **get_weather**: 天气查询
- **list_files**: 文件列表
- **write_file**: 文件写入
- **read_file**: 文件读取
- **calculate**: 数学计算
- **get_current_time**: 时间获取

### 2. 数据格式
采用标准的对话格式，包含：
- System prompt（系统提示）
- User message（用户消息）
- Assistant response with tool calls（助手响应和工具调用）
- Tool results（工具执行结果）
- Final assistant response（最终助手响应）

### 3. 训练目标
- 正确识别用户意图
- 选择合适的MCP工具
- 构造正确的工具调用参数
- 处理工具返回结果
- 生成用户友好的最终响应

## 使用方法

### 1. 生成数据集
```bash
cd scripts
python generate_dataset.py
```

### 2. 训练模型
```bash
cd scripts
python train_mcp_model.py
```

### 3. 自定义配置
可以修改 `train_mcp_model.py` 中的参数：
- `model_name`: 基础模型名称
- `num_epochs`: 训练轮数
- `batch_size`: 批次大小
- `learning_rate`: 学习率

## 模型评估

### 评估指标
1. **工具选择准确率**: 模型选择正确工具的比例
2. **参数构造准确率**: 工具参数构造的正确性
3. **响应质量**: 最终响应的质量和用户友好性

### 测试用例
```python
# 测试工具调用能力
test_cases = [
    "请搜索Python机器学习的最新信息",
    "查看北京的天气情况",
    "列出当前目录的文件",
    "创建一个hello.txt文件",
    "计算125乘以37的结果"
]
```

## 扩展指南

### 添加新工具
1. 在 `examples/mcp_tools.py` 中定义新工具函数
2. 在 `MCPToolRegistry` 中注册工具
3. 更新工具schema定义
4. 在数据生成器中添加相应模板

### 数据增强
- 增加更多样化的用户请求表达
- 添加多轮对话场景
- 包含错误处理和异常情况
- 支持工具链式调用

## 最佳实践

1. **数据质量**: 确保训练数据的多样性和准确性
2. **模型选择**: 选择支持function calling的基础模型
3. **超参数调优**: 根据具体任务调整学习率和训练轮数
4. **评估验证**: 使用独立的验证集评估模型性能
5. **持续改进**: 根据实际使用反馈不断优化数据集

## 注意事项

- 确保有足够的GPU内存进行训练
- 建议使用支持function calling的模型作为基础
- 训练过程中监控loss变化，避免过拟合
- 定期保存检查点，防止训练中断

## HuggingFace集成功能

### 🌟 核心特性

- **🤖 自动模型上传**: 训练完成后自动上传到HuggingFace Hub
- **📋 配置版本管理**: 保存和同步训练配置文件
- **🔬 实验跟踪**: 记录训练结果和元数据
- **🏷️ 版本标签**: 支持语义化版本和时间戳版本
- **📄 模型卡片**: 自动生成详细的模型文档
- **🔄 工作流同步**: 一键同步完整训练工作流

### 🚀 快速使用

1. **配置HuggingFace**:
   ```yaml
   # 在config.yaml中添加
   huggingface:
     enabled: true
     auto_sync: true
     repository:
       model_name: "your-username/mcp-model"
   ```

2. **运行训练**:
   ```bash
   ./run_training.sh
   ```

3. **手动同步**:
   ```bash
   python scripts/huggingface_manager.py sync \
     --model-path ./mcp_finetuned_model \
     --experiment-name my_experiment
   ```

### 📖 相关文档

- [HuggingFace快速入门](./HuggingFace快速入门.md) - 快速上手指南
- [HuggingFace集成使用教程](./HuggingFace集成使用教程.md) - 详细使用教程
- [配置参考文档](./配置参考文档.md) - 完整配置说明

## 模型训练指南

### 训练流程

1. **环境准备**: 安装依赖和配置HuggingFace
2. **数据生成**: 自动生成MCP工具调用数据集
3. **模型训练**: 使用生成的数据集微调模型
4. **自动同步**: 训练完成后自动上传到HuggingFace
5. **模型测试**: 验证模型的工具调用能力

### 支持的功能

- ✅ 多种基础模型支持
- ✅ 自动数据集生成
- ✅ 分布式训练支持
- ✅ 实验跟踪和监控
- ✅ 自动版本管理
- ✅ 模型性能评估

## 获取帮助

### 📞 联系方式

- **GitHub Issues**: 报告问题和功能请求
- **文档**: 查看详细的使用教程和配置说明
- **示例代码**: 参考 `examples/` 目录中的示例

### 🔍 故障排除

1. **查看日志**: `logs/training_*.log`
2. **验证配置**: `python scripts/huggingface_manager.py validate-config`
3. **检查环境**: `huggingface-cli whoami`
4. **运行示例**: `python examples/huggingface_usage.py --interactive`

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

---

**🎉 感谢使用MCP微调项目！** 如果您觉得这个项目有用，请给我们一个⭐️星标支持！# MCP微调项目文档中心

欢迎来到MCP（Model Context Protocol）微调项目的文档中心。本项目提供了完整的工具调用微调解决方案，包括数据生成、模型训练、版本管理和HuggingFace集成。

## 📚 文档导航

### 🚀 快速开始
- [HuggingFace快速入门](./HuggingFace快速入门.md) - 5分钟快速上手HuggingFace集成
- [项目版本管理](./项目版本管理.md) - 了解项目的版本控制策略

### 📖 详细教程
- [HuggingFace集成使用教程](./HuggingFace集成使用教程.md) - 完整的HuggingFace集成功能指南
- [配置参考文档](./配置参考文档.md) - 所有配置选项的详细说明

### 🔧 技术文档
- [MCP工具调用数据集](#mcp工具调用数据集) - 数据集生成和使用说明
- [模型训练指南](#模型训练指南) - 训练流程和最佳实践

---

## MCP工具调用数据集

本项目的核心是一个完整的MCP工具调用微调数据集，用于训练大语言模型正确调用MCP工具。

### 项目结构