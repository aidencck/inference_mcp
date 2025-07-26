# MCP微调项目Docker部署指南

本指南详细介绍如何使用Docker部署和运行MCP微调项目。

## 目录

- [前置要求](#前置要求)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [常用操作](#常用操作)
- [故障排除](#故障排除)
- [性能优化](#性能优化)
- [安全注意事项](#安全注意事项)

## 前置要求

### 系统要求

- **操作系统**: Linux (推荐 Ubuntu 20.04+), macOS, Windows 10/11
- **内存**: 最低 8GB，推荐 16GB+
- **存储**: 最低 50GB 可用空间
- **GPU**: NVIDIA GPU (可选，用于加速训练)

### 软件依赖

1. **Docker Engine** (版本 20.10+)
   ```bash
   # Ubuntu安装Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

2. **Docker Compose** (版本 2.0+)
   ```bash
   # 安装Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **NVIDIA Container Toolkit** (GPU支持)
   ```bash
   # 安装NVIDIA Container Toolkit
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

### 验证安装

```bash
# 验证Docker
docker --version
docker-compose --version

# 验证GPU支持（如果有GPU）
docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi
```

## 快速开始

### 1. 克隆项目

```bash
git clone <项目地址>
cd mcp_finetune_dataset
```

### 2. 配置环境

```bash
# 复制环境配置文件
cp .env.docker .env

# 根据需要编辑配置
vim .env
```

### 3. 构建和启动

```bash
# 使用便捷脚本
./docker-start.sh build    # 构建镜像
./docker-start.sh start    # 启动容器

# 或使用docker-compose
docker-compose up -d
```

### 4. 验证部署

```bash
# 查看容器状态
./docker-start.sh status

# 进入容器
./docker-start.sh shell
```

## 详细配置

### 环境变量配置

编辑 `.env` 文件来自定义配置：

```bash
# 基础配置
PROJECT_NAME=mcp-finetune
CONTAINER_NAME=mcp-training-container

# GPU配置
NVIDIA_VISIBLE_DEVICES=all  # 或指定GPU: 0,1

# 端口配置
JUPYTER_PORT=8888
WEB_PORT=8000
TENSORBOARD_PORT=6006

# 资源限制
SHM_SIZE=2g
MEM_LIMIT=16g
CPUS=8.0
```

### 数据卷挂载

项目使用以下数据卷挂载：

```yaml
volumes:
  - ./data:/app/data              # 训练数据
  - ./models:/app/models          # 模型文件
  - ./logs:/app/logs              # 日志文件
  - ./outputs:/app/outputs        # 输出结果
  - ./configs:/app/configs        # 配置文件
  - ./.cache:/app/.cache          # 缓存目录
```

### 网络配置

默认端口映射：

- **8888**: Jupyter Lab
- **8000**: Web服务
- **6006**: TensorBoard
- **8889**: Jupyter (独立服务)
- **6007**: TensorBoard (独立服务)

## 常用操作

### 容器管理

```bash
# 启动所有服务
./docker-start.sh start

# 停止所有服务
./docker-start.sh stop

# 重启服务
./docker-start.sh restart

# 查看日志
./docker-start.sh logs

# 查看状态
./docker-start.sh status
```

### 开发环境

```bash
# 启动Jupyter Lab
./docker-start.sh jupyter
# 访问: http://localhost:8889
# Token: mcp-training-2024

# 启动TensorBoard
./docker-start.sh tensorboard
# 访问: http://localhost:6007

# 进入容器Shell
./docker-start.sh shell
```

### 训练和测试

```bash
# 运行训练
./docker-start.sh train

# 运行测试
./docker-start.sh test

# 手动执行命令
docker exec -it mcp-training-container bash -c "cd /app && python train.py"
```

### 数据管理

```bash
# 复制文件到容器
docker cp local_file.txt mcp-training-container:/app/data/

# 从容器复制文件
docker cp mcp-training-container:/app/outputs/model.bin ./

# 查看容器内文件
docker exec mcp-training-container ls -la /app/
```

## 故障排除

### 常见问题

#### 1. GPU不可用

**问题**: 容器内无法使用GPU

**解决方案**:
```bash
# 检查NVIDIA驱动
nvidia-smi

# 检查Docker GPU支持
docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi

# 重启Docker服务
sudo systemctl restart docker
```

#### 2. 端口冲突

**问题**: 端口已被占用

**解决方案**:
```bash
# 查看端口占用
sudo netstat -tlnp | grep :8888

# 修改.env文件中的端口配置
JUPYTER_PORT=8889
```

#### 3. 内存不足

**问题**: 容器内存不足

**解决方案**:
```bash
# 增加共享内存
SHM_SIZE=4g

# 设置内存限制
MEM_LIMIT=32g

# 或在docker-compose.yml中调整
```

#### 4. 权限问题

**问题**: 文件权限错误

**解决方案**:
```bash
# 修改文件权限
sudo chown -R $USER:$USER ./data ./models ./outputs

# 或在容器内修改
docker exec -it mcp-training-container chown -R root:root /app/
```

### 日志调试

```bash
# 查看容器日志
docker logs mcp-training-container

# 实时查看日志
docker logs -f mcp-training-container

# 查看特定服务日志
docker-compose logs jupyter
docker-compose logs tensorboard
```

### 性能监控

```bash
# 查看容器资源使用
docker stats mcp-training-container

# 查看GPU使用情况
docker exec mcp-training-container nvidia-smi

# 查看磁盘使用
docker exec mcp-training-container df -h
```

## 性能优化

### 1. 资源配置优化

```yaml
# docker-compose.yml
services:
  mcp-training:
    deploy:
      resources:
        limits:
          memory: 32G
          cpus: '16.0'
        reservations:
          memory: 16G
          cpus: '8.0'
    shm_size: '4gb'
```

### 2. 缓存优化

```bash
# 使用本地缓存卷
docker volume create mcp-cache
docker volume create mcp-models

# 在docker-compose.yml中使用
volumes:
  - mcp-cache:/app/.cache
  - mcp-models:/app/models
```

### 3. 网络优化

```yaml
# 使用host网络模式（Linux）
network_mode: host

# 或优化bridge网络
networks:
  mcp-network:
    driver: bridge
    driver_opts:
      com.docker.network.driver.mtu: 1500
```

### 4. 存储优化

```bash
# 使用SSD存储
# 配置Docker数据目录到SSD
sudo systemctl stop docker
sudo mv /var/lib/docker /ssd/docker
sudo ln -s /ssd/docker /var/lib/docker
sudo systemctl start docker
```

## 安全注意事项

### 1. 网络安全

```bash
# 限制端口访问
# 仅绑定到本地接口
ports:
  - "127.0.0.1:8888:8888"

# 使用防火墙
sudo ufw allow from 192.168.1.0/24 to any port 8888
```

### 2. 数据安全

```bash
# 加密敏感数据
# 使用Docker secrets
echo "your_token" | docker secret create huggingface_token -

# 在compose文件中使用
secrets:
  - huggingface_token
```

### 3. 容器安全

```yaml
# 非root用户运行
user: "1000:1000"

# 只读根文件系统
read_only: true

# 删除不必要的能力
cap_drop:
  - ALL
cap_add:
  - CHOWN
  - SETUID
  - SETGID
```

### 4. 镜像安全

```bash
# 扫描镜像漏洞
docker scan mcp-finetune:latest

# 使用多阶段构建减少攻击面
# 定期更新基础镜像
docker pull nvidia/cuda:11.8-devel-ubuntu20.04
```

## 生产部署建议

### 1. 使用编排工具

```bash
# Kubernetes部署
kubectl apply -f k8s/

# Docker Swarm部署
docker stack deploy -c docker-compose.prod.yml mcp-stack
```

### 2. 监控和日志

```yaml
# 添加监控服务
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

### 3. 备份策略

```bash
# 定期备份数据卷
docker run --rm -v mcp-models:/data -v $(pwd):/backup alpine tar czf /backup/models-backup.tar.gz -C /data .

# 备份配置
cp -r configs/ backups/configs-$(date +%Y%m%d)/
```

### 4. 自动化部署

```bash
# 使用CI/CD管道
# .github/workflows/deploy.yml
# 自动构建、测试、部署
```

## 总结

通过Docker部署MCP微调项目具有以下优势：

- **环境一致性**: 确保开发、测试、生产环境一致
- **快速部署**: 一键启动完整的训练环境
- **资源隔离**: 避免依赖冲突和环境污染
- **可扩展性**: 支持多GPU、分布式训练
- **可维护性**: 简化环境管理和版本控制

建议在生产环境中结合Kubernetes等编排工具，实现更高级的容器管理和自动化运维。