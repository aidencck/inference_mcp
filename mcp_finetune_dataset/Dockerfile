# MCP微调项目Docker镜像
FROM nvidia/cuda:12.6.0-devel-ubuntu20.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# 设置工作目录
WORKDIR /app

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

# 创建Python软链接
RUN ln -sf /usr/bin/python3.9 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.9 /usr/bin/python

# 升级pip
RUN pip install --upgrade pip

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装PyTorch GPU版本
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p /app/.cache/models \
    /app/.temp \
    /app/models \
    /app/downloads \
    /app/logs \
    /app/outputs

# 设置权限
RUN chmod +x run_training.sh

# 暴露端口（用于Jupyter或Web服务）
EXPOSE 8888 8000

# 默认命令
CMD ["/bin/bash"]