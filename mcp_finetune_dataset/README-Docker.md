# MCP微调项目 - Docker版本

本项目已完全Docker化，提供开箱即用的容器化训练环境。

## 🚀 快速开始

### 前置要求

- Docker Engine 20.10+
- Docker Compose 2.0+
- NVIDIA Container Toolkit (GPU支持)
- 8GB+ 内存，50GB+ 存储空间

### 一键启动

```bash
# 克隆项目
git clone <项目地址>
cd mcp_finetune_dataset

# 构建并启动
make dev-setup

# 或使用脚本
./docker-start.sh build
./docker-start.sh start
```

## 📋 可用命令

### 使用Makefile（推荐）

```bash
# 查看所有可用命令
make help

# 开发环境
make dev-setup      # 一键设置开发环境
make build          # 构建镜像
make up             # 启动所有服务
make shell          # 进入容器
make jupyter        # 启动Jupyter Lab
make tensorboard    # 启动TensorBoard

# 训练和测试
make train          # 运行训练
make test           # 运行测试
make health         # 健康检查
make inference      # 推理测试

# 维护
make status         # 查看状态
make logs           # 查看日志
make clean          # 清理资源
```

### 使用启动脚本

```bash
# 查看帮助
./docker-start.sh help

# 基础操作
./docker-start.sh build        # 构建镜像
./docker-start.sh start        # 启动容器
./docker-start.sh stop         # 停止容器
./docker-start.sh restart      # 重启容器
./docker-start.sh shell        # 进入Shell
./docker-start.sh logs         # 查看日志
./docker-start.sh status       # 查看状态

# 开发工具
./docker-start.sh jupyter      # 启动Jupyter
./docker-start.sh tensorboard  # 启动TensorBoard

# 训练相关
./docker-start.sh train        # 运行训练
./docker-start.sh test         # 运行测试

# 清理
./docker-start.sh clean        # 清理所有
```

### 使用Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 生产环境
docker-compose -f docker-compose.prod.yml up -d
```

## 🌐 服务访问

启动后可通过以下地址访问服务：

- **Jupyter Lab**: http://localhost:8889
  - Token: `mcp-training-2024`
- **TensorBoard**: http://localhost:6007
- **主容器**: `make shell` 或 `./docker-start.sh shell`

## 📁 目录结构

```
mcp_finetune_dataset/
├── Dockerfile              # 主要镜像定义
├── Dockerfile.jupyter      # Jupyter镜像定义
├── docker-compose.yml      # 开发环境编排
├── docker-compose.prod.yml # 生产环境编排
├── docker-start.sh         # 启动脚本
├── .dockerignore           # Docker忽略文件
├── .env.docker             # 环境变量模板
├── Makefile                # 便捷命令
├── scripts/
│   └── health_check.py     # 健康检查脚本
└── docs/
    └── Docker部署指南.md    # 详细部署文档
```

## ⚙️ 配置说明

### 环境变量

复制并编辑环境配置：

```bash
cp .env.docker .env
vim .env
```

主要配置项：

```bash
# GPU配置
NVIDIA_VISIBLE_DEVICES=all  # 使用所有GPU

# 端口配置
JUPYTER_PORT=8888
WEB_PORT=8000
TENSORBOARD_PORT=6006

# 资源限制
SHM_SIZE=2g
MEM_LIMIT=16g
CPUS=8.0

# HuggingFace配置
HUGGINGFACE_TOKEN=your_token_here
```

### 数据卷挂载

项目使用以下数据卷：

- `./data` → `/app/data` (训练数据)
- `./models` → `/app/models` (模型文件)
- `./logs` → `/app/logs` (日志文件)
- `./outputs` → `/app/outputs` (输出结果)
- `./.cache` → `/app/.cache` (缓存目录)

## 🔧 开发工作流

### 1. 环境准备

```bash
# 一键设置开发环境
make dev-setup

# 或分步执行
make build
make up
make jupyter
```

### 2. 代码开发

```bash
# 进入容器开发
make shell

# 或使用Jupyter Lab
# 访问 http://localhost:8889
```

### 3. 训练模型

```bash
# 运行训练
make train

# 监控训练过程
make tensorboard  # 访问 http://localhost:6007
make logs         # 查看实时日志
```

### 4. 测试验证

```bash
# 运行测试
make test

# 健康检查
make health

# 推理测试
make inference
```

## 🚀 生产部署

### 生产环境启动

```bash
# 构建生产镜像
make prod-build

# 启动生产环境
make prod-up

# 查看状态
make prod-status

# 查看日志
make prod-logs
```

### 监控和维护

```bash
# 资源监控
make monitor

# GPU状态
make gpu-status

# 备份数据
make backup

# 更新项目
make update
```

## 🐛 故障排除

### 常见问题

#### GPU不可用

```bash
# 检查NVIDIA驱动
nvidia-smi

# 检查Docker GPU支持
docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi

# 重启Docker
sudo systemctl restart docker
```

#### 端口冲突

```bash
# 查看端口占用
sudo netstat -tlnp | grep :8888

# 修改.env文件中的端口
JUPYTER_PORT=8889
```

#### 内存不足

```bash
# 增加共享内存
echo "SHM_SIZE=4g" >> .env

# 设置内存限制
echo "MEM_LIMIT=32g" >> .env
```

#### 权限问题

```bash
# 修改文件权限
sudo chown -R $USER:$USER ./data ./models ./outputs

# 或在容器内修改
make shell
chown -R root:root /app/
```

### 调试模式

```bash
# 调试模式启动
make debug

# 查看详细日志
make logs

# 健康检查
make health
```

## 📊 性能优化

### 资源配置

```bash
# 编辑.env文件
SHM_SIZE=4g          # 增加共享内存
MEM_LIMIT=32g        # 设置内存限制
CPUS=16.0            # 设置CPU限制
```

### 缓存优化

```bash
# 使用本地缓存卷
docker volume create mcp-cache
docker volume create mcp-models
```

### 网络优化

```bash
# 使用host网络模式（Linux）
echo "network_mode: host" >> docker-compose.override.yml
```

## 🔒 安全注意事项

### 网络安全

```bash
# 限制端口访问（仅本地）
ports:
  - "127.0.0.1:8888:8888"
```

### 数据安全

```bash
# 使用Docker secrets
echo "your_token" | docker secret create huggingface_token -
```

### 容器安全

```bash
# 非root用户运行
user: "1000:1000"

# 只读根文件系统
read_only: true
```

## 📚 更多文档

- [详细部署指南](docs/Docker部署指南.md)
- [阿里云部署教程](docs/阿里云部署教程.md)
- [配置参考文档](docs/配置参考文档.md)
- [HuggingFace集成教程](docs/HuggingFace集成使用教程.md)

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 在Docker环境中开发测试
4. 提交Pull Request

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🆘 获取帮助

- 查看帮助：`make help` 或 `./docker-start.sh help`
- 健康检查：`make health`
- 查看日志：`make logs`
- 问题反馈：提交Issue

---

**快速开始命令总结：**

```bash
# 完整开发环境一键启动
make dev-setup

# 访问Jupyter Lab
open http://localhost:8889

# 运行训练
make train

# 查看状态
make status
```