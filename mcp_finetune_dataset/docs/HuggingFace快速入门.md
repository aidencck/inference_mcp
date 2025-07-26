# HuggingFace集成快速入门

本指南帮助您在5分钟内快速上手HuggingFace集成功能。

## 🚀 快速开始

### 第一步：环境准备

```bash
# 1. 安装依赖
cd <项目根目录>
pip install -r requirements.txt

# 2. 登录HuggingFace
huggingface-cli login
# 输入您的Token
```

### 第二步：基础配置

编辑 `config.yaml`，添加以下配置：

```yaml
# 在config.yaml中添加
huggingface:
  enabled: true
  auto_sync: true
  repository:
    model_name: "your-username/mcp-model"  # 替换为您的用户名
    private: true
```

### 第三步：运行训练

```bash
# 一键训练并自动上传到HuggingFace
./run_training.sh
```

就这么简单！训练完成后，您的模型会自动上传到HuggingFace Hub。

## 📋 配置检查清单

在开始之前，请确认以下项目：

- [ ] 已安装所有依赖包
- [ ] 已获取HuggingFace Token
- [ ] 已完成HuggingFace登录
- [ ] 已在config.yaml中配置用户名
- [ ] 已设置仓库名称

## 🔧 常用命令

```bash
# 检查HuggingFace认证状态
huggingface-cli whoami

# 手动上传模型
python scripts/huggingface_manager.py upload-model \
    --model-path ./mcp_finetuned_model \
    --version-tag v1.0.0

# 下载模型
python scripts/huggingface_manager.py download-model \
    --version-tag v1.0.0 \
    --local-dir ./downloaded_model

# 查看所有版本
python scripts/huggingface_manager.py list-versions
```

## 🎯 使用场景

### 场景1：自动训练和上传

```bash
# 完全自动化
./run_training.sh
```

### 场景2：只上传已有模型

```bash
# 跳过训练，只上传
python scripts/huggingface_manager.py sync \
    --model-path ./existing_model \
    --experiment-name my_experiment
```

### 场景3：下载和使用模型

```python
from scripts.huggingface_manager import HuggingFaceManager

manager = HuggingFaceManager("config.yaml")
model_path = manager.download_model(
    version_tag="v1.0.0",
    local_dir="./downloaded_model"
)

# 使用下载的模型
from transformers import AutoModel, AutoTokenizer
model = AutoModel.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)
```

## ⚠️ 常见问题

### Q: 认证失败怎么办？

```bash
# 重新登录
huggingface-cli logout
huggingface-cli login
```

### Q: 仓库名称冲突？

在 `config.yaml` 中修改仓库名称：

```yaml
huggingface:
  repository:
    model_name: "your-username/mcp-model-v2"  # 使用新名称
```

### Q: 上传失败？

检查网络连接和文件权限：

```bash
# 检查文件
ls -la ./mcp_finetuned_model/

# 检查网络
curl -I https://huggingface.co
```

## 📚 进阶学习

- 📖 [完整使用教程](./HuggingFace集成使用教程.md)
- 💻 [代码示例](../examples/huggingface_usage.py)
- 🔧 [配置参考](../configs/huggingface_config.yaml)

## 🆘 获取帮助

如果遇到问题：

1. 查看详细教程：`docs/HuggingFace集成使用教程.md`
2. 运行示例代码：`python examples/huggingface_usage.py --interactive`
3. 检查日志文件：`logs/training_*.log`

---

🎉 **恭喜！** 您已经掌握了HuggingFace集成的基本用法。现在可以开始您的模型训练和版本管理之旅了！