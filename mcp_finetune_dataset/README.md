# MCP Fine-tuning Dataset Project

这是一个用于微调大语言模型以支持MCP (Model Context Protocol) 工具调用的项目。项目提供了完整的数据生成、模型训练、版本管理和HuggingFace集成功能。

## 功能特性

- 🤖 **自动数据生成**: 基于MCP工具自动生成训练数据集
- 🚀 **模型微调**: 支持多种预训练模型的微调
- 📊 **实验跟踪**: 集成Weights & Biases进行实验管理
- 🔄 **版本控制**: 完整的配置、模型和实验版本管理
- ☁️ **HuggingFace集成**: 自动同步模型和配置到HuggingFace Hub
- 🛠️ **灵活配置**: 支持YAML配置文件和命令行参数

## 项目结构

```
mcp_finetune_dataset/
├── config.yaml                    # 主配置文件
├── configs/
│   └── huggingface_config.yaml    # HuggingFace配置
├── scripts/
│   ├── generate_dataset.py        # 数据集生成
│   ├── train_mcp_model.py         # 模型训练
│   ├── model_manager.py           # 模型管理
│   └── huggingface_manager.py     # HuggingFace管理
├── examples/
│   └── huggingface_usage.py       # 使用示例
├── mcp_tools/                     # MCP工具定义
├── run_training.sh               # 训练脚本
└── requirements.txt              # 依赖包
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd mcp_finetune_dataset

# 安装依赖
pip install -r requirements.txt

# 配置HuggingFace Token (可选)
export HUGGINGFACE_TOKEN="your_token_here"
```

### 2. 配置设置

编辑 `config.yaml` 文件，设置模型、训练参数等：

```yaml
model:
  name: "microsoft/DialoGPT-medium"
  max_length: 512

training:
  epochs: 3
  batch_size: 4
  learning_rate: 5e-5

# HuggingFace集成 (可选)
huggingface:
  enabled: true
  auto_sync: true
  repository:
    model_name: "your-username/mcp-finetuned-model"
```

### 3. 运行训练

```bash
# 完整训练流程
./run_training.sh

# 或分步执行
python scripts/generate_dataset.py --config config.yaml
python scripts/train_mcp_model.py --config config.yaml
```

## HuggingFace集成

### 功能概述

项目提供了完整的HuggingFace Hub集成，支持：

- **自动模型上传**: 训练完成后自动上传模型到HuggingFace
- **配置版本管理**: 保存和同步训练配置
- **实验跟踪**: 记录训练结果和元数据
- **版本标签**: 支持语义化版本管理
- **模型卡片**: 自动生成详细的模型文档

### 配置HuggingFace

1. **设置Token**:
```bash
export HUGGINGFACE_TOKEN="your_token_here"
# 或在代码中设置
huggingface-cli login
```

2. **配置仓库信息** (`configs/huggingface_config.yaml`):
```yaml
user:
  username: "your-username"
  email: "your-email@example.com"

repository:
  model_repo_template: "{username}/{model_name}"
  config_repo_template: "{username}/{model_name}-configs"

settings:
  auto_create_repos: true
  default_private: true
  auto_versioning: true
```

### 使用方法

#### 1. 自动同步 (推荐)

在 `config.yaml` 中启用自动同步：

```yaml
huggingface:
  enabled: true
  auto_sync: true
  upload_items:
    - model
    - config
    - results
```

训练完成后会自动上传所有内容到HuggingFace。

#### 2. 手动管理

```python
from scripts.huggingface_manager import HuggingFaceManager

# 创建管理器
manager = HuggingFaceManager("config.yaml")

# 上传模型
model_url = manager.upload_model(
    model_path="./mcp_finetuned_model",
    version_tag="v1.0.0",
    commit_message="Initial model release"
)

# 同步完整工作流
results = manager.sync_training_workflow(
    model_path="./mcp_finetuned_model",
    experiment_name="baseline_experiment",
    version_tag="v1.0.0"
)
```

#### 3. 命令行工具

```bash
# 上传模型
python scripts/huggingface_manager.py upload-model \
    --model-path ./mcp_finetuned_model \
    --version-tag v1.0.0

# 下载模型
python scripts/huggingface_manager.py download-model \
    --version-tag v1.0.0 \
    --local-dir ./downloaded_model

# 列出版本
python scripts/huggingface_manager.py list-versions

# 同步工作流
python scripts/huggingface_manager.py sync \
    --model-path ./mcp_finetuned_model \
    --experiment-name my_experiment
```

### 版本管理

项目支持多层次的版本管理：

1. **Git版本控制**: 代码和配置文件
2. **模型版本**: HuggingFace仓库中的标签和分支
3. **实验版本**: 配置快照和结果记录
4. **数据版本**: 数据集生成参数和文件

#### 版本标签规则

- **语义化版本**: `v1.0.0`, `v1.1.0`, `v2.0.0`
- **时间戳版本**: `v20240101-120000`
- **实验版本**: `exp-baseline-001`, `exp-optimized-002`

### 使用示例

查看 `examples/huggingface_usage.py` 获取详细的使用示例：

```bash
# 交互式演示
python examples/huggingface_usage.py --interactive

# 运行特定示例
python examples/huggingface_usage.py --example 1  # 上传模型
python examples/huggingface_usage.py --example 3  # 同步工作流
```

## 高级功能

### 1. 实验跟踪

项目集成了多种实验跟踪工具：

- **Weights & Biases**: 训练过程监控
- **HuggingFace Hub**: 模型和配置版本管理
- **本地日志**: 详细的训练日志

### 2. 模型卡片生成

自动生成包含以下信息的模型卡片：

- 模型架构和参数
- 训练数据和过程
- 性能指标
- 使用示例
- 限制和偏见说明

### 3. 配置管理

支持多种配置方式：

- **YAML文件**: 主要配置方式
- **命令行参数**: 覆盖配置文件
- **环境变量**: 敏感信息配置

### 4. 错误处理和恢复

- **断点续训**: 支持从检查点恢复训练
- **网络重试**: 自动重试失败的上传/下载
- **配置验证**: 启动前验证配置正确性

## 故障排除

### 常见问题

1. **HuggingFace认证失败**:
   ```bash
   # 重新登录
   huggingface-cli login
   # 或设置环境变量
   export HUGGINGFACE_TOKEN="your_token"
   ```

2. **模型上传失败**:
   - 检查网络连接
   - 确认仓库权限
   - 验证模型文件完整性

3. **配置文件错误**:
   ```bash
   # 验证YAML语法
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

4. **内存不足**:
   - 减小batch_size
   - 启用梯度累积
   - 使用fp16训练

### 日志和调试

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
python scripts/train_mcp_model.py --config config.yaml

# 查看训练日志
tail -f logs/training.log

# 检查HuggingFace同步状态
python scripts/huggingface_manager.py list-experiments
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

[MIT License](LICENSE)

## 联系方式

如有问题或建议，请创建Issue或联系维护者。