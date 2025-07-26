# MCP模型微调快速开始指南

本指南将帮助您快速开始MCP工具调用模型的训练和使用。

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- CUDA 11.8+ (推荐，用于GPU训练)
- 至少16GB内存
- 至少50GB磁盘空间

### 2. 一键运行

```bash
# 给脚本执行权限
chmod +x run_training.sh

# 运行完整训练流程
./run_training.sh
```

这个命令将自动完成：
- ✅ 环境检查
- ✅ 依赖安装
- ✅ 模型下载
- ✅ 训练数据生成
- ✅ 模型训练
- ✅ 模型测试

### 3. 自定义选项

```bash
# 查看所有选项
./run_training.sh --help

# 跳过依赖安装（如果已安装）
./run_training.sh --skip-install

# 跳过模型下载（如果已下载）
./run_training.sh --skip-download

# 仅运行测试
./run_training.sh --only-test

# 交互式测试模式
./run_training.sh --only-test --interactive

# 使用自定义配置文件
./run_training.sh --config my_config.yaml
```

## 📋 分步执行

如果您想分步执行，可以按以下步骤：

### 步骤1: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤2: 下载模型

```bash
python3 -c "
import sys
sys.path.append('scripts')
from model_manager import ModelManager
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

manager = ModelManager(config)
manager.download_model()
"
```

### 步骤3: 生成训练数据

```bash
python3 scripts/generate_dataset.py --config config.yaml
```

### 步骤4: 开始训练

```bash
python3 scripts/train_mcp_model.py --config config.yaml
```

### 步骤5: 测试模型

```bash
# 批量测试
python3 scripts/inference.py --model_path outputs/mcp_model --base_model Qwen/Qwen2-7B-Instruct

# 交互式测试
python3 scripts/inference.py --model_path outputs/mcp_model --base_model Qwen/Qwen2-7B-Instruct --interactive
```

## ⚙️ 配置说明

主要配置文件是 `config.yaml`，包含以下关键设置：

```yaml
model:
  name: "Qwen/Qwen2-7B-Instruct"  # 基础模型
  max_length: 2048                 # 最大序列长度

training:
  num_epochs: 3                    # 训练轮数
  batch_size: 4                    # 批次大小
  learning_rate: 2e-5              # 学习率
  output_dir: "outputs/mcp_model"  # 输出目录

data:
  train_samples: 1000              # 训练样本数
  validation_samples: 200          # 验证样本数
```

## 🔧 常见问题

### Q: 内存不足怎么办？
A: 减少 `batch_size` 或使用梯度累积：
```yaml
training:
  batch_size: 2
  gradient_accumulation_steps: 2
```

### Q: 训练速度太慢？
A: 确保使用GPU，或减少训练数据量：
```yaml
data:
  train_samples: 500
  validation_samples: 100
```

### Q: 模型下载失败？
A: 设置HuggingFace镜像：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Q: 如何使用自己的工具？
A: 修改 `examples/mcp_tools.py`，添加新的工具定义。

## 📊 训练监控

训练过程中会生成以下日志：
- `logs/training_YYYYMMDD_HHMMSS.log` - 训练日志
- `training.log` - 实时训练日志
- Weights & Biases 面板（如果配置）

## 🎯 下一步

训练完成后，您可以：

1. **集成到应用**: 使用 `scripts/inference.py` 作为参考
2. **添加新工具**: 扩展 `examples/mcp_tools.py`
3. **优化模型**: 调整训练参数和数据
4. **部署服务**: 创建API服务包装模型

## 📚 更多资源

- [完整文档](docs/README.md)
- [工具开发指南](examples/mcp_tools.py)
- [配置参考](config.yaml)

---

🎉 **恭喜！** 您已经成功设置了MCP模型训练环境。开始您的AI工具调用之旅吧！