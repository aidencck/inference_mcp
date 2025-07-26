# HuggingFace集成使用教程

本教程详细介绍如何使用项目中的HuggingFace集成功能，实现模型和配置的自动版本管理。

## 目录

1. [功能概述](#功能概述)
2. [环境准备](#环境准备)
3. [配置设置](#配置设置)
4. [使用方法](#使用方法)
5. [高级功能](#高级功能)
6. [故障排除](#故障排除)
7. [最佳实践](#最佳实践)

## 功能概述

HuggingFace集成模块提供以下核心功能：

- 🤖 **自动模型上传**: 训练完成后自动上传模型到HuggingFace Hub
- 📋 **配置版本管理**: 保存和同步训练配置文件
- 🔬 **实验跟踪**: 记录训练结果和元数据
- 🏷️ **版本标签**: 支持语义化版本和时间戳版本
- 📄 **模型卡片**: 自动生成详细的模型文档
- 🔄 **工作流同步**: 一键同步完整训练工作流

## 环境准备

### 1. 安装依赖

确保已安装所有必要的依赖包：

```bash
cd <项目根目录>
pip install -r requirements.txt
```

### 2. HuggingFace认证

#### 方法一：使用CLI登录（推荐）

```bash
huggingface-cli login
```

按提示输入您的HuggingFace Token。

#### 方法二：环境变量

```bash
export HUGGINGFACE_TOKEN="your_token_here"
```

#### 方法三：在代码中设置

```python
from huggingface_hub import login
login(token="your_token_here")
```

### 3. 获取HuggingFace Token

1. 访问 [HuggingFace Settings](https://huggingface.co/settings/tokens)
2. 点击 "New token"
3. 选择 "Write" 权限
4. 复制生成的Token

## 配置设置

### 1. 主配置文件 (config.yaml)

在项目根目录的 `config.yaml` 中添加HuggingFace配置：

```yaml
# 其他配置...

# HuggingFace集成配置
huggingface:
  enabled: true                    # 启用HuggingFace集成
  config_file: "configs/huggingface_config.yaml"  # HF配置文件路径
  
  # 仓库设置
  repository:
    model_name: "your-username/mcp-finetuned-model"  # 模型仓库名
    private: true                  # 是否创建私有仓库
    auto_create: true             # 自动创建仓库
  
  # 自动同步设置
  auto_sync: true                 # 训练后自动同步
  upload_items:                   # 要上传的项目
    - model                       # 模型文件
    - config                      # 配置文件
    - results                     # 训练结果
  
  # 版本控制
  versioning:
    auto_tag: true                # 自动生成版本标签
    tag_format: "v{timestamp}"    # 标签格式
  
  # 实验跟踪
  experiment_tracking:
    enabled: true                 # 启用实验跟踪
    include_metrics: true         # 包含训练指标
```

### 2. HuggingFace专用配置 (configs/huggingface_config.yaml)

创建详细的HuggingFace配置文件：

```yaml
# 用户信息
user:
  username: "your-username"       # HuggingFace用户名
  email: "your-email@example.com" # 邮箱地址

# 仓库模板
repository:
  model_repo_template: "{username}/{model_name}"           # 模型仓库模板
  config_repo_template: "{username}/{model_name}-configs"  # 配置仓库模板

# 上传/下载设置
settings:
  auto_create_repos: true         # 自动创建仓库
  default_private: true           # 默认私有仓库
  auto_versioning: true           # 自动版本管理
  commit_message_template: "Upload {item_type} for {experiment_name}"  # 提交信息模板
  default_branch: "main"          # 默认分支
  
  # 上传设置
  upload:
    chunk_size: 10485760          # 上传块大小 (10MB)
    max_retries: 3                # 最大重试次数
    retry_delay: 5                # 重试延迟 (秒)
  
  # 下载设置
  download:
    cache_dir: "./.cache/huggingface"  # 缓存目录
    resume_download: true         # 断点续传

# 同步选项
sync:
  include_git_info: true          # 包含Git信息
  include_system_info: true       # 包含系统信息
  backup_before_upload: false     # 上传前备份

# 模型卡片元数据
model_card:
  language: "zh"                  # 语言
  license: "mit"                  # 许可证
  tags:                           # 标签
    - "mcp"
    - "fine-tuning"
    - "tool-calling"
  
  # 作者信息
  authors:
    - name: "Your Name"
      email: "your-email@example.com"
  
  # 数据集信息
  datasets:
    - name: "MCP Tool Calls Dataset"
      description: "Dataset for training MCP tool calling capabilities"

# 版本控制规则
versioning:
  semantic_versioning: true       # 使用语义化版本
  auto_increment: "patch"         # 自动递增级别
  tag_prefix: "v"                 # 标签前缀
  
  # 版本格式
  formats:
    timestamp: "v{year}{month:02d}{day:02d}-{hour:02d}{minute:02d}{second:02d}"
    semantic: "v{major}.{minor}.{patch}"

# 实验跟踪
experiment_tracking:
  fields:                         # 要跟踪的字段
    - "model_name"
    - "base_model"
    - "training_params"
    - "eval_results"
    - "timestamp"
    - "git_commit"
  
  metadata_file: "experiment_metadata.json"  # 元数据文件名

# 备份设置
backup:
  enabled: false                 # 启用备份
  local_backup_dir: "./backups"   # 本地备份目录
  keep_backups: 5                 # 保留备份数量

# 通知设置
notifications:
  enabled: false                 # 启用通知
  webhook_url: ""                 # Webhook URL
  email_notifications: false     # 邮件通知
```

## 使用方法

### 1. 自动模式（推荐）

这是最简单的使用方式，只需在配置中启用自动同步：

```bash
# 运行完整训练流程
./run_training.sh

# 或者分步执行
python scripts/generate_dataset.py --config config.yaml
python scripts/train_mcp_model.py --config config.yaml
# 训练完成后会自动同步到HuggingFace
```

### 2. 手动模式

#### 使用Python API

```python
from scripts.huggingface_manager import HuggingFaceManager

# 创建管理器
manager = HuggingFaceManager("config.yaml")

# 方法1: 同步完整工作流（推荐）
results = manager.sync_training_workflow(
    model_path="./mcp_finetuned_model",
    experiment_name="baseline_experiment",
    version_tag="v1.0.0",
    private=True
)

print("同步结果:")
for key, url in results.items():
    print(f"  {key}: {url}")

# 方法2: 分步操作
# 创建仓库
manager.create_repositories(private=True)

# 上传模型
model_url = manager.upload_model(
    model_path="./mcp_finetuned_model",
    version_tag="v1.0.0",
    commit_message="Upload fine-tuned MCP model"
)

# 上传配置
config_url = manager.upload_training_config(
    config_data=manager.config,
    experiment_name="baseline_experiment"
)

# 上传训练结果
results_url = manager.upload_training_results(
    results_path="./mcp_finetuned_model/eval_results.json",
    experiment_name="baseline_experiment"
)
```

#### 使用命令行工具

```bash
# 同步完整工作流
python scripts/huggingface_manager.py sync \
    --model-path ./mcp_finetuned_model \
    --experiment-name baseline_experiment \
    --version-tag v1.0.0 \
    --private

# 上传模型
python scripts/huggingface_manager.py upload-model \
    --model-path ./mcp_finetuned_model \
    --version-tag v1.0.0 \
    --commit-message "Upload fine-tuned model"

# 上传配置
python scripts/huggingface_manager.py upload-config \
    --config-file config.yaml \
    --experiment-name baseline_experiment

# 下载模型
python scripts/huggingface_manager.py download-model \
    --version-tag v1.0.0 \
    --local-dir ./downloaded_model

# 列出版本
python scripts/huggingface_manager.py list-versions

# 列出实验
python scripts/huggingface_manager.py list-experiments
```

### 3. 训练脚本集成

训练脚本支持HuggingFace相关的命令行参数：

```bash
# 跳过HuggingFace同步
./run_training.sh --skip-hf-sync

# 强制执行HuggingFace同步（即使配置中未启用）
./run_training.sh --force-hf-sync

# 使用自定义配置并强制同步
./run_training.sh --config custom_config.yaml --force-hf-sync
```

## 高级功能

### 1. 版本管理策略

#### 语义化版本

```python
# 手动指定语义化版本
manager.upload_model(
    model_path="./model",
    version_tag="v1.2.3",  # major.minor.patch
    commit_message="Fix training stability issues"
)
```

#### 时间戳版本

```python
# 自动生成时间戳版本
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
version_tag = f"v{timestamp}"

manager.upload_model(
    model_path="./model",
    version_tag=version_tag
)
```

#### 实验版本

```python
# 实验相关的版本标签
manager.upload_model(
    model_path="./model",
    version_tag="exp-baseline-001",
    commit_message="Baseline experiment with default parameters"
)
```

### 2. 模型卡片自定义

```python
# 生成自定义模型卡片
model_card = manager.generate_model_card(
    model_path="./model",
    version_tag="v1.0.0",
    custom_sections={
        "limitations": "This model may have biases...",
        "ethical_considerations": "Please use responsibly...",
        "training_data": "Trained on MCP tool calling dataset..."
    }
)

# 保存模型卡片
with open("MODEL_CARD.md", "w", encoding="utf-8") as f:
    f.write(model_card)
```

### 3. 批量操作

```python
# 批量上传多个实验
experiments = [
    {"path": "./exp1", "name": "baseline", "tag": "v1.0.0"},
    {"path": "./exp2", "name": "optimized", "tag": "v1.1.0"},
    {"path": "./exp3", "name": "final", "tag": "v2.0.0"}
]

for exp in experiments:
    results = manager.sync_training_workflow(
        model_path=exp["path"],
        experiment_name=exp["name"],
        version_tag=exp["tag"]
    )
    print(f"Uploaded {exp['name']}: {results['model_url']}")
```

### 4. 条件同步

```python
# 只在满足条件时同步
def should_sync(eval_results):
    return eval_results.get("accuracy", 0) > 0.8

# 在训练脚本中
if should_sync(eval_results):
    manager.sync_training_workflow(
        model_path=output_dir,
        experiment_name="high_accuracy_model",
        version_tag="v1.0.0"
    )
```

## 故障排除

### 常见问题及解决方案

#### 1. 认证失败

**问题**: `HTTPError: 401 Client Error: Unauthorized`

**解决方案**:
```bash
# 重新登录
huggingface-cli logout
huggingface-cli login

# 或检查Token
echo $HUGGINGFACE_TOKEN

# 验证认证状态
python -c "from huggingface_hub import HfApi; print(HfApi().whoami())"
```

#### 2. 仓库创建失败

**问题**: `Repository already exists` 或权限错误

**解决方案**:
```python
# 检查仓库是否存在
from huggingface_hub import HfApi
api = HfApi()
try:
    repo_info = api.repo_info("username/repo-name")
    print("仓库已存在")
except:
    print("仓库不存在，可以创建")

# 手动创建仓库
api.create_repo(
    repo_id="username/repo-name",
    private=True,
    repo_type="model"
)
```

#### 3. 上传失败

**问题**: 网络错误或文件过大

**解决方案**:
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 分块上传大文件
manager.upload_model(
    model_path="./large_model",
    version_tag="v1.0.0",
    chunk_size=5*1024*1024  # 5MB chunks
)

# 重试机制
for attempt in range(3):
    try:
        result = manager.upload_model(...)
        break
    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt == 2:
            raise
```

#### 4. 配置文件错误

**问题**: YAML语法错误或配置项缺失

**解决方案**:
```bash
# 验证YAML语法
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# 检查配置完整性
python scripts/huggingface_manager.py validate-config --config config.yaml
```

#### 5. 模型文件损坏

**问题**: 上传的模型无法加载

**解决方案**:
```python
# 验证模型文件
from transformers import AutoModel, AutoTokenizer

try:
    model = AutoModel.from_pretrained("./model_path")
    tokenizer = AutoTokenizer.from_pretrained("./model_path")
    print("模型文件正常")
except Exception as e:
    print(f"模型文件有问题: {e}")
```

### 调试技巧

#### 1. 启用详细日志

```bash
# 设置日志级别
export LOG_LEVEL=DEBUG

# 运行脚本
python scripts/huggingface_manager.py sync --model-path ./model
```

#### 2. 检查网络连接

```bash
# 测试HuggingFace连接
curl -I https://huggingface.co

# 测试API访问
python -c "from huggingface_hub import HfApi; print(HfApi().whoami())"
```

#### 3. 验证文件完整性

```python
# 检查模型文件
import os
model_files = ['pytorch_model.bin', 'config.json', 'tokenizer.json']
for file in model_files:
    path = os.path.join('./model', file)
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"{file}: {size} bytes")
    else:
        print(f"{file}: 缺失")
```

## 最佳实践

### 1. 版本管理策略

- **开发阶段**: 使用时间戳版本 (`v20240101-120000`)
- **实验阶段**: 使用实验标签 (`exp-baseline-001`)
- **发布阶段**: 使用语义化版本 (`v1.0.0`)

### 2. 仓库组织

```
your-username/
├── mcp-model-v1/          # 主要模型仓库
├── mcp-model-v1-configs/  # 配置仓库
├── mcp-experiments/       # 实验记录仓库
└── mcp-datasets/          # 数据集仓库
```

### 3. 提交信息规范

```python
# 好的提交信息
commit_messages = [
    "feat: Add support for new MCP tools",
    "fix: Improve model stability on edge cases",
    "perf: Optimize inference speed by 20%",
    "docs: Update model card with usage examples"
]
```

### 4. 安全考虑

- 使用私有仓库存储敏感模型
- 定期轮换HuggingFace Token
- 不在代码中硬编码Token
- 使用环境变量或安全的配置管理

### 5. 性能优化

```python
# 并行上传多个文件
import concurrent.futures

def upload_file(file_path):
    # 上传逻辑
    pass

files = ['model.bin', 'config.json', 'tokenizer.json']
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(upload_file, f) for f in files]
    concurrent.futures.wait(futures)
```

### 6. 监控和告警

```python
# 添加监控
import time
import psutil

def monitor_upload(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
            
        end_time = time.time()
        end_memory = psutil.virtual_memory().used
        
        print(f"上传耗时: {end_time - start_time:.2f}秒")
        print(f"内存使用: {(end_memory - start_memory) / 1024 / 1024:.2f}MB")
        print(f"上传状态: {'成功' if success else '失败'}")
        
        return result
    return wrapper

# 使用装饰器
@monitor_upload
def upload_with_monitoring():
    return manager.upload_model(...)
```

## 总结

HuggingFace集成功能为MCP微调项目提供了完整的MLOps解决方案，支持：

- ✅ 自动化的模型版本管理
- ✅ 配置和实验跟踪
- ✅ 灵活的部署选项
- ✅ 完整的文档生成
- ✅ 强大的故障恢复机制

通过合理配置和使用这些功能，您可以建立一个高效、可靠的机器学习工作流，确保模型开发过程的可追溯性和可重现性。

如有问题，请参考项目的 `examples/huggingface_usage.py` 文件获取更多使用示例，或查看项目的GitHub Issues页面。