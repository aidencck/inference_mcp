# Makefile使用指南

本文档详细介绍MCP微调项目中Makefile的使用方法和管理命令。

## 📋 目录

- [概述](#概述)
- [前置要求](#前置要求)
- [命令分类](#命令分类)
- [详细命令说明](#详细命令说明)
- [使用场景](#使用场景)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 概述

Makefile提供了一套完整的Docker容器管理命令，简化了开发、测试、部署的工作流程。通过标准化的命令接口，开发者可以快速执行常见操作。

### 核心优势

- **统一接口**: 所有操作通过`make`命令执行
- **自动化**: 复杂操作一键完成
- **可扩展**: 易于添加新的管理命令
- **跨平台**: 在支持Make的系统上通用

## 前置要求

### 系统要求

- **Make工具**: GNU Make 3.81+
- **Docker**: Docker Engine 20.10+
- **Docker Compose**: 2.0+
- **操作系统**: Linux, macOS, Windows (WSL2)

### 安装验证

```bash
# 检查Make版本
make --version

# 检查Docker版本
docker --version
docker-compose --version

# 验证GPU支持（可选）
nvidia-smi
```

## 命令分类

### 🏗️ 构建相关

| 命令 | 描述 | 使用场景 |
|------|------|----------|
| `make build` | 构建Docker镜像 | 首次部署或代码更新后 |
| `make build-no-cache` | 无缓存构建镜像 | 依赖更新或构建问题 |
| `make build-jupyter` | 构建Jupyter镜像 | 开发环境需要 |

### 🚀 容器管理

| 命令 | 描述 | 使用场景 |
|------|------|----------|
| `make up` | 启动所有服务 | 完整环境启动 |
| `make down` | 停止所有服务 | 环境清理 |
| `make start` | 启动训练容器 | 单独启动主容器 |
| `make stop` | 停止训练容器 | 单独停止主容器 |
| `make restart` | 重启训练容器 | 配置更新后 |

### 🛠️ 开发工具

| 命令 | 描述 | 访问地址 |
|------|------|----------|
| `make shell` | 进入容器Shell | 命令行交互 |
| `make logs` | 查看容器日志 | 调试和监控 |
| `make jupyter` | 启动Jupyter服务 | http://localhost:8889 |
| `make tensorboard` | 启动TensorBoard | http://localhost:6007 |

### 🎯 训练和测试

| 命令 | 描述 | 使用场景 |
|------|------|----------|
| `make train` | 运行训练脚本 | 模型训练 |
| `make test` | 运行测试套件 | 代码验证 |
| `make health` | 健康检查 | 系统诊断 |
| `make inference` | 推理测试 | 模型验证 |

### 🔧 维护清理

| 命令 | 描述 | 注意事项 |
|------|------|----------|
| `make status` | 查看容器状态 | 无风险 |
| `make clean` | 清理容器和镜像 | ⚠️ 会删除数据 |
| `make clean-volumes` | 清理数据卷 | ⚠️ 会删除持久数据 |
| `make prune` | 清理未使用资源 | 释放磁盘空间 |

### 🏭 生产部署

| 命令 | 描述 | 环境 |
|------|------|------|
| `make prod-build` | 构建生产镜像 | 生产环境 |
| `make prod-up` | 启动生产环境 | 生产环境 |
| `make prod-down` | 停止生产环境 | 生产环境 |
| `make prod-logs` | 查看生产日志 | 生产环境 |
| `make prod-status` | 生产环境状态 | 生产环境 |

### 🔍 监控调试

| 命令 | 描述 | 用途 |
|------|------|------|
| `make monitor` | 资源监控 | 性能分析 |
| `make gpu-status` | GPU状态 | GPU监控 |
| `make debug` | 调试模式 | 问题诊断 |

### 🎁 便捷功能

| 命令 | 描述 | 功能 |
|------|------|------|
| `make dev-setup` | 一键开发环境 | 快速开始 |
| `make backup` | 数据备份 | 数据保护 |
| `make update` | 项目更新 | 版本升级 |

## 详细命令说明

### 构建相关命令

#### `make build`

**功能**: 构建主要的Docker镜像

```bash
make build
```

**执行流程**:
1. 检查Docker环境
2. 使用Dockerfile构建镜像
3. 标记为`mcp-finetune:latest`

**适用场景**:
- 首次部署项目
- 代码或依赖更新后
- 镜像损坏需要重建

#### `make build-no-cache`

**功能**: 无缓存构建，强制重新下载所有依赖

```bash
make build-no-cache
```

**适用场景**:
- 依赖包更新
- 构建缓存问题
- 基础镜像更新

#### `make build-jupyter`

**功能**: 构建Jupyter开发环境镜像

```bash
make build-jupyter
```

**特点**:
- 轻量级镜像
- 专门用于交互式开发
- 包含Jupyter Lab和常用扩展

### 容器管理命令

#### `make up`

**功能**: 启动完整的服务栈

```bash
make up
```

**启动的服务**:
- 主训练容器
- Jupyter服务
- TensorBoard服务

**等效命令**:
```bash
docker-compose up -d
```

#### `make start`

**功能**: 仅启动主训练容器

```bash
make start
```

**特点**:
- 包含GPU支持检查
- 自动创建必要目录
- 支持数据卷挂载

#### `make restart`

**功能**: 重启训练容器

```bash
make restart
```

**使用场景**:
- 配置文件更新后
- 容器状态异常
- 内存泄漏清理

### 开发工具命令

#### `make shell`

**功能**: 进入容器的交互式Shell

```bash
make shell
```

**特点**:
- 直接访问容器环境
- 完整的开发工具链
- 实时代码调试

**常用操作**:
```bash
# 进入容器后可以执行
python train.py
pip install new_package
vim config.yaml
```

#### `make jupyter`

**功能**: 启动Jupyter Lab服务

```bash
make jupyter
```

**访问信息**:
- **URL**: http://localhost:8889
- **Token**: mcp-training-2024

**功能特性**:
- 代码编辑和执行
- 数据可视化
- 交互式开发
- 实时结果展示

#### `make tensorboard`

**功能**: 启动TensorBoard监控服务

```bash
make tensorboard
```

**访问信息**:
- **URL**: http://localhost:6007

**监控内容**:
- 训练损失曲线
- 模型结构图
- 参数分布
- 性能指标

### 训练和测试命令

#### `make train`

**功能**: 执行模型训练

```bash
make train
```

**执行流程**:
1. 检查容器状态
2. 进入容器环境
3. 执行`./run_training.sh`
4. 实时显示训练日志

**监控方法**:
```bash
# 另开终端监控
make logs
make tensorboard
```

#### `make test`

**功能**: 运行测试套件

```bash
make test
```

**测试内容**:
- 单元测试
- 集成测试
- 模型验证
- 性能测试

#### `make health`

**功能**: 系统健康检查

```bash
make health
```

**检查项目**:
- Python环境
- GPU可用性
- 磁盘空间
- 内存使用
- 网络连接
- 文件权限
- 配置文件
- 进程状态

#### `make inference`

**功能**: 模型推理测试

```bash
make inference
```

**特点**:
- 交互式推理
- 模型性能验证
- 结果质量评估

### 维护清理命令

#### `make status`

**功能**: 查看系统状态

```bash
make status
```

**显示信息**:
- 容器运行状态
- 镜像信息
- 数据卷使用
- GPU状态

#### `make clean`

**功能**: 清理容器和镜像

```bash
make clean
```

**⚠️ 警告**: 此操作会删除:
- 所有相关容器
- 项目镜像
- 未命名数据卷

**确认流程**:
```bash
警告: 这将删除所有相关容器和镜像
确认继续? (y/N): y
```

#### `make prune`

**功能**: 清理未使用的Docker资源

```bash
make prune
```

**清理内容**:
- 停止的容器
- 未使用的镜像
- 未使用的数据卷
- 未使用的网络

### 生产部署命令

#### `make prod-build`

**功能**: 构建生产环境镜像

```bash
make prod-build
```

**特点**:
- 优化的镜像大小
- 安全配置
- 性能优化
- 监控集成

#### `make prod-up`

**功能**: 启动生产环境

```bash
make prod-up
```

**包含服务**:
- 训练容器
- Prometheus监控
- Fluentd日志聚合
- Nginx反向代理

#### `make prod-status`

**功能**: 查看生产环境状态

```bash
make prod-status
```

**监控指标**:
- 服务健康状态
- 资源使用情况
- 性能指标
- 错误日志

### 便捷功能命令

#### `make dev-setup`

**功能**: 一键设置完整开发环境

```bash
make dev-setup
```

**执行步骤**:
1. 构建所有镜像
2. 启动服务栈
3. 启动Jupyter Lab
4. 显示访问信息

**完成后提示**:
```
开发环境设置完成
可用服务:
  - Jupyter Lab: http://localhost:8889 (Token: mcp-training-2024)
  - 容器Shell: make shell
  - 训练: make train
```

#### `make backup`

**功能**: 备份重要数据

```bash
make backup
```

**备份内容**:
- 模型文件
- 配置文件
- 训练日志
- 数据集

**备份位置**: `backups/YYYYMMDD_HHMMSS/`

#### `make update`

**功能**: 更新项目到最新版本

```bash
make update
```

**更新步骤**:
1. 拉取最新代码
2. 更新基础镜像
3. 重新构建镜像
4. 重启服务

## 使用场景

### 🚀 新项目开始

```bash
# 1. 一键设置开发环境
make dev-setup

# 2. 验证环境
make health

# 3. 开始开发
make shell
# 或
open http://localhost:8889
```

### 🔄 日常开发流程

```bash
# 1. 启动环境
make start

# 2. 开发调试
make jupyter
make shell

# 3. 运行训练
make train

# 4. 监控训练
make tensorboard
make logs

# 5. 测试验证
make test
make inference

# 6. 停止环境
make stop
```

### 🏭 生产部署流程

```bash
# 1. 构建生产镜像
make prod-build

# 2. 启动生产环境
make prod-up

# 3. 验证部署
make prod-status
make health

# 4. 监控运行
make prod-logs
make monitor
```

### 🔧 维护和故障排除

```bash
# 1. 检查状态
make status
make health

# 2. 查看日志
make logs

# 3. 重启服务
make restart

# 4. 清理资源
make prune

# 5. 完全重建
make clean
make build-no-cache
make start
```

### 📊 性能监控

```bash
# 1. 资源监控
make monitor

# 2. GPU状态
make gpu-status

# 3. 训练监控
make tensorboard

# 4. 系统健康
make health
```

## 最佳实践

### 🎯 开发阶段

1. **环境隔离**
   ```bash
   # 使用独立的开发环境
   make dev-setup
   ```

2. **增量构建**
   ```bash
   # 优先使用缓存构建
   make build
   
   # 仅在必要时无缓存构建
   make build-no-cache
   ```

3. **实时监控**
   ```bash
   # 开启多个终端
   # 终端1: 训练
   make train
   
   # 终端2: 监控
   make logs
   
   # 终端3: TensorBoard
   make tensorboard
   ```

### 🏭 生产阶段

1. **资源管理**
   ```bash
   # 定期清理
   make prune
   
   # 监控资源
   make monitor
   ```

2. **数据备份**
   ```bash
   # 定期备份
   make backup
   
   # 验证备份
   ls -la backups/
   ```

3. **健康检查**
   ```bash
   # 定期健康检查
   make health
   
   # 监控生产状态
   make prod-status
   ```

### 🔒 安全考虑

1. **权限管理**
   ```bash
   # 检查文件权限
   make health
   
   # 使用非root用户
   # 在.env中配置
   USER_ID=1000
   GROUP_ID=1000
   ```

2. **网络安全**
   ```bash
   # 限制端口访问
   # 在docker-compose.yml中配置
   ports:
     - "127.0.0.1:8888:8888"
   ```

3. **数据保护**
   ```bash
   # 定期备份
   make backup
   
   # 使用加密存储
   # 配置Docker secrets
   ```

## 故障排除

### 🚨 常见问题

#### 1. Docker服务未运行

**错误信息**:
```
Cannot connect to the Docker daemon
```

**解决方案**:
```bash
# 启动Docker服务
sudo systemctl start docker

# 验证Docker状态
docker info
```

#### 2. GPU不可用

**错误信息**:
```
GPU不可用，将使用CPU
```

**解决方案**:
```bash
# 检查NVIDIA驱动
nvidia-smi

# 检查Docker GPU支持
docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi

# 重启Docker服务
sudo systemctl restart docker
```

#### 3. 端口冲突

**错误信息**:
```
Port 8888 is already in use
```

**解决方案**:
```bash
# 查看端口占用
sudo netstat -tlnp | grep :8888

# 修改端口配置
echo "JUPYTER_PORT=8889" >> .env

# 重启服务
make restart
```

#### 4. 内存不足

**错误信息**:
```
OOMKilled
```

**解决方案**:
```bash
# 增加共享内存
echo "SHM_SIZE=4g" >> .env

# 设置内存限制
echo "MEM_LIMIT=32g" >> .env

# 重启容器
make restart
```

#### 5. 磁盘空间不足

**错误信息**:
```
No space left on device
```

**解决方案**:
```bash
# 清理Docker资源
make prune

# 清理系统缓存
sudo apt-get clean

# 检查磁盘使用
df -h
```

### 🔍 调试技巧

#### 1. 详细日志

```bash
# 查看详细日志
make logs

# 查看特定服务日志
docker-compose logs jupyter
docker-compose logs tensorboard
```

#### 2. 交互式调试

```bash
# 进入容器调试
make shell

# 调试模式启动
make debug
```

#### 3. 健康检查

```bash
# 全面健康检查
make health

# 检查容器状态
make status

# 监控资源使用
make monitor
```

#### 4. 网络诊断

```bash
# 检查网络连接
docker exec mcp-training-container ping google.com

# 检查端口监听
docker exec mcp-training-container netstat -tlnp
```

### 📞 获取帮助

1. **查看帮助信息**
   ```bash
   make help
   ```

2. **检查系统状态**
   ```bash
   make status
   make health
   ```

3. **查看日志**
   ```bash
   make logs
   ```

4. **社区支持**
   - 提交Issue到项目仓库
   - 查看项目文档
   - 参考Docker官方文档

## 📚 相关文档

- [Docker部署指南](Docker部署指南.md)
- [README-Docker](../README-Docker.md)
- [配置参考文档](配置参考文档.md)
- [阿里云部署教程](阿里云部署教程.md)

## 🔄 版本更新

当项目更新时，使用以下命令同步：

```bash
# 更新项目
make update

# 或手动更新
git pull
make build-no-cache
make restart
```

---

**快速参考**:

```bash
# 开发环境一键启动
make dev-setup

# 查看所有命令
make help

# 运行训练
make train

# 查看状态
make status

# 清理资源
make prune
```