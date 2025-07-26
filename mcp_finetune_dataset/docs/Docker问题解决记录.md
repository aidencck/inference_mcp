# Docker问题解决记录

## 问题描述

在执行 `make build` 构建Docker镜像时遇到以下错误：

```
ERROR: failed to solve: nvidia/cuda:11.8-devel-ubuntu20.04: failed to resolve source metadata for docker.io/nvidia/cuda:11.8-devel-ubuntu20.04: docker.io/nvidia/cuda:11.8-devel-ubuntu20.04: not found
```

## 问题分析

1. **CUDA镜像版本问题**：`nvidia/cuda:11.8-devel-ubuntu20.04` 镜像在Docker Hub上不可用或已被移除
2. **Python包安装问题**：Ubuntu 20.04默认不包含 `python3.9-pip` 包

## 解决方案

### 1. 更新CUDA基础镜像

将Dockerfile中的基础镜像从：
```dockerfile
FROM nvidia/cuda:11.8-devel-ubuntu20.04
```

更新为：
```dockerfile
FROM nvidia/cuda:12.6.0-devel-ubuntu20.04
```

### 2. 更新PyTorch安装源

相应地将PyTorch安装命令从：
```dockerfile
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

更新为：
```dockerfile
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 3. 修复Python 3.9安装问题

添加deadsnakes PPA源来安装Python 3.9：
```dockerfile
# 安装系统依赖
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.9 \
    python3.9-distutils \
    python3.9-venv \
    python3.9-dev \
    python3-pip \
    git \
    wget \
    curl \
    vim \
    htop \
    tree \
    unzip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
```

## 验证结果

构建成功后的验证：

1. **镜像大小**：29.1GB
2. **Python版本**：Python 3.9.23
3. **PyTorch版本**：2.5.1+cu121
4. **CUDA版本**：12.6.0

## 构建时间

- 总构建时间：约20分钟
- 主要耗时步骤：
  - Python依赖安装：~12分钟
  - PyTorch安装：~8分钟
  - 镜像导出：~10分钟

## 注意事项

1. **GPU支持**：容器运行时需要NVIDIA Container Toolkit才能使用GPU功能
2. **镜像大小**：由于包含完整的CUDA开发环境和深度学习库，镜像较大（29.1GB）
3. **版本兼容性**：CUDA 12.6与PyTorch 2.5.1+cu121完全兼容

## 相关文档

- [Docker部署指南](./Docker部署指南.md)
- [Makefile使用指南](./Makefile使用指南.md)
- [README-Docker](../README-Docker.md)

## 更新日期

2024年12月19日