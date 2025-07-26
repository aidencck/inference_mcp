# 多容器Docker部署管理方案

## 概述

本文档提供了一套完整的多容器Docker部署、通信和管理方案，适用于MCP微调项目的生产环境部署。

## 1. 架构设计

### 1.1 容器架构

```
┌─────────────────────────────────────────────────────────────┐
│                    负载均衡层                                │
│                   (Nginx/Traefik)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                   应用服务层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ MCP训练容器  │  │ MCP推理容器  │  │  Web API    │        │
│  │             │  │             │  │   容器      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                   数据服务层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Redis     │  │ PostgreSQL  │  │   MinIO     │        │
│  │   缓存      │  │   数据库    │  │  对象存储    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 容器分类

#### 核心服务容器
- **mcp-training**: 模型训练服务
- **mcp-inference**: 模型推理服务
- **mcp-api**: Web API服务
- **mcp-scheduler**: 任务调度服务

#### 基础设施容器
- **nginx**: 反向代理和负载均衡
- **redis**: 缓存和消息队列
- **postgresql**: 关系型数据库
- **minio**: 对象存储服务
- **prometheus**: 监控数据收集
- **grafana**: 监控数据可视化

## 2. Docker Compose配置

### 2.1 生产环境配置 (docker-compose.prod.yml)

```yaml
version: '3.8'

services:
  # 负载均衡
  nginx:
    image: nginx:alpine
    container_name: mcp-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - mcp-api
      - mcp-inference
    networks:
      - mcp-network
    restart: unless-stopped

  # 训练服务
  mcp-training:
    image: mcp-finetune:latest
    container_name: mcp-training
    command: python scripts/train_mcp_model.py
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
      - ./outputs:/app/outputs
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - TRAINING_MODE=production
    depends_on:
      - redis
      - postgresql
    networks:
      - mcp-network
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped

  # 推理服务
  mcp-inference:
    image: mcp-finetune:latest
    container_name: mcp-inference
    command: python scripts/inference.py --mode server
    ports:
      - "8001:8001"
    volumes:
      - ./models:/app/models:ro
      - ./logs:/app/logs
    environment:
      - CUDA_VISIBLE_DEVICES=1
      - INFERENCE_MODE=production
    depends_on:
      - redis
      - mcp-training
    networks:
      - mcp-network
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped

  # API服务
  mcp-api:
    image: mcp-finetune:latest
    container_name: mcp-api
    command: python scripts/api_server.py
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
    environment:
      - API_MODE=production
      - DATABASE_URL=postgresql://mcp_user:mcp_pass@postgresql:5432/mcp_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - postgresql
    networks:
      - mcp-network
    restart: unless-stopped

  # 任务调度
  mcp-scheduler:
    image: mcp-finetune:latest
    container_name: mcp-scheduler
    command: python scripts/scheduler.py
    volumes:
      - ./logs:/app/logs
    environment:
      - SCHEDULER_MODE=production
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    networks:
      - mcp-network
    restart: unless-stopped

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: mcp-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    networks:
      - mcp-network
    restart: unless-stopped

  # PostgreSQL数据库
  postgresql:
    image: postgres:15-alpine
    container_name: mcp-postgresql
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      - POSTGRES_DB=mcp_db
      - POSTGRES_USER=mcp_user
      - POSTGRES_PASSWORD=mcp_pass
    networks:
      - mcp-network
    restart: unless-stopped

  # MinIO对象存储
  minio:
    image: minio/minio:latest
    container_name: mcp-minio
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin123
    command: server /data --console-address ":9001"
    networks:
      - mcp-network
    restart: unless-stopped

  # Prometheus监控
  prometheus:
    image: prom/prometheus:latest
    container_name: mcp-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - mcp-network
    restart: unless-stopped

  # Grafana可视化
  grafana:
    image: grafana/grafana:latest
    container_name: mcp-grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    networks:
      - mcp-network
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
  minio_data:
  prometheus_data:
  grafana_data:

networks:
  mcp-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 2.2 开发环境配置 (docker-compose.dev.yml)

```yaml
version: '3.8'

services:
  # 开发环境训练服务
  mcp-training-dev:
    image: mcp-finetune:latest
    container_name: mcp-training-dev
    command: python scripts/train_mcp_model.py --debug
    volumes:
      - .:/app
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
    environment:
      - TRAINING_MODE=development
      - DEBUG=true
    ports:
      - "8888:8888"  # Jupyter端口
    networks:
      - mcp-dev-network
    stdin_open: true
    tty: true

  # 开发环境Redis
  redis-dev:
    image: redis:7-alpine
    container_name: mcp-redis-dev
    ports:
      - "6380:6379"
    networks:
      - mcp-dev-network

networks:
  mcp-dev-network:
    driver: bridge
```

## 3. 容器通信方案

### 3.1 网络通信

#### 内部通信
- 使用Docker自定义网络 `mcp-network`
- 容器间通过服务名进行通信
- 端口映射仅对外暴露必要服务

#### 外部通信
- Nginx作为反向代理处理外部请求
- SSL/TLS加密保证通信安全
- API网关统一管理接口访问

### 3.2 消息队列

```python
# Redis消息队列示例
import redis
import json

class MessageQueue:
    def __init__(self, host='redis', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
    
    def publish_training_task(self, task_data):
        """发布训练任务"""
        self.redis_client.lpush('training_queue', json.dumps(task_data))
    
    def consume_training_task(self):
        """消费训练任务"""
        task = self.redis_client.brpop('training_queue', timeout=30)
        if task:
            return json.loads(task[1])
        return None
    
    def publish_inference_request(self, request_data):
        """发布推理请求"""
        request_id = request_data['request_id']
        self.redis_client.setex(f'inference:{request_id}', 3600, json.dumps(request_data))
        self.redis_client.lpush('inference_queue', request_id)
    
    def get_inference_result(self, request_id):
        """获取推理结果"""
        result = self.redis_client.get(f'result:{request_id}')
        if result:
            return json.loads(result)
        return None
```

### 3.3 服务发现

```python
# 服务注册与发现
class ServiceRegistry:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def register_service(self, service_name, host, port, health_check_url):
        """注册服务"""
        service_info = {
            'host': host,
            'port': port,
            'health_check_url': health_check_url,
            'last_heartbeat': time.time()
        }
        self.redis.hset('services', service_name, json.dumps(service_info))
    
    def discover_service(self, service_name):
        """发现服务"""
        service_data = self.redis.hget('services', service_name)
        if service_data:
            return json.loads(service_data)
        return None
    
    def health_check(self):
        """健康检查"""
        services = self.redis.hgetall('services')
        for service_name, service_data in services.items():
            service_info = json.loads(service_data)
            # 执行健康检查逻辑
            if self._is_service_healthy(service_info):
                service_info['last_heartbeat'] = time.time()
                self.redis.hset('services', service_name, json.dumps(service_info))
            else:
                self.redis.hdel('services', service_name)
```

## 4. 数据管理

### 4.1 数据持久化策略

#### 数据卷映射
```bash
# 模型数据
./models:/app/models

# 训练数据
./data:/app/data

# 日志数据
./logs:/app/logs

# 输出结果
./outputs:/app/outputs

# 数据库数据
postgres_data:/var/lib/postgresql/data

# 缓存数据
redis_data:/data
```

#### 备份策略
```bash
#!/bin/bash
# backup.sh - 数据备份脚本

BACKUP_DIR="/backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# 备份数据库
docker exec mcp-postgresql pg_dump -U mcp_user mcp_db > $BACKUP_DIR/database.sql

# 备份模型文件
tar -czf $BACKUP_DIR/models.tar.gz ./models

# 备份配置文件
tar -czf $BACKUP_DIR/configs.tar.gz ./configs

# 清理旧备份（保留7天）
find /backup -type d -mtime +7 -exec rm -rf {} +
```

### 4.2 数据同步

```python
# 模型同步服务
class ModelSyncService:
    def __init__(self, minio_client, redis_client):
        self.minio = minio_client
        self.redis = redis_client
    
    def upload_model(self, model_path, model_name, version):
        """上传模型到对象存储"""
        bucket_name = 'mcp-models'
        object_name = f'{model_name}/{version}/model.tar.gz'
        
        # 压缩模型文件
        tar_path = f'/tmp/{model_name}_{version}.tar.gz'
        self._compress_model(model_path, tar_path)
        
        # 上传到MinIO
        self.minio.fput_object(bucket_name, object_name, tar_path)
        
        # 更新Redis中的模型信息
        model_info = {
            'name': model_name,
            'version': version,
            'path': object_name,
            'upload_time': time.time()
        }
        self.redis.hset('models', f'{model_name}:{version}', json.dumps(model_info))
    
    def download_model(self, model_name, version, local_path):
        """从对象存储下载模型"""
        bucket_name = 'mcp-models'
        object_name = f'{model_name}/{version}/model.tar.gz'
        
        # 从MinIO下载
        tar_path = f'/tmp/{model_name}_{version}.tar.gz'
        self.minio.fget_object(bucket_name, object_name, tar_path)
        
        # 解压到本地路径
        self._extract_model(tar_path, local_path)
```

## 5. 监控与日志

### 5.1 监控配置

#### Prometheus配置 (monitoring/prometheus.yml)
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'mcp-api'
    static_configs:
      - targets: ['mcp-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'mcp-inference'
    static_configs:
      - targets: ['mcp-inference:8001']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgresql:5432']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

#### Grafana仪表板配置
```json
{
  "dashboard": {
    "title": "MCP微调系统监控",
    "panels": [
      {
        "title": "API请求量",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{status}}"
          }
        ]
      },
      {
        "title": "GPU使用率",
        "type": "graph",
        "targets": [
          {
            "expr": "nvidia_gpu_utilization_percent",
            "legendFormat": "GPU {{gpu}}"
          }
        ]
      },
      {
        "title": "内存使用情况",
        "type": "graph",
        "targets": [
          {
            "expr": "container_memory_usage_bytes / container_spec_memory_limit_bytes * 100",
            "legendFormat": "{{name}}"
          }
        ]
      }
    ]
  }
}
```

### 5.2 日志管理

#### 日志配置 (logging.yml)
```yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
  json:
    format: '%(asctime)s %(name)s %(levelname)s %(message)s'
    class: pythonjsonlogger.jsonlogger.JsonFormatter

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout
  
  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: json
    filename: /app/logs/mcp.log
    maxBytes: 10485760  # 10MB
    backupCount: 5
  
  redis:
    class: redis_log_handler.RedisHandler
    level: ERROR
    formatter: json
    host: redis
    port: 6379
    db: 1
    key: mcp_errors

loggers:
  mcp:
    level: DEBUG
    handlers: [console, file, redis]
    propagate: false

root:
  level: INFO
  handlers: [console]
```

## 6. 部署脚本

### 6.1 一键部署脚本 (deploy.sh)

```bash
#!/bin/bash

set -e

# 配置变量
ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"

echo "开始部署MCP微调系统 - 环境: $ENVIRONMENT"

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装"
    exit 1
fi

# 检查NVIDIA Docker支持
if [ "$ENVIRONMENT" = "production" ]; then
    if ! docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu20.04 nvidia-smi &> /dev/null; then
        echo "警告: NVIDIA Docker支持未正确配置，GPU功能将不可用"
    fi
fi

# 创建必要的目录
mkdir -p {data,models,logs,outputs,backup}
mkdir -p {nginx,monitoring}

# 生成配置文件
echo "生成配置文件..."
./scripts/generate_configs.sh $ENVIRONMENT

# 构建镜像
echo "构建Docker镜像..."
docker build -t mcp-finetune:latest .

# 启动服务
echo "启动服务..."
docker-compose -f $COMPOSE_FILE up -d

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 健康检查
echo "执行健康检查..."
./scripts/health_check.sh

# 初始化数据库
if [ "$ENVIRONMENT" = "production" ]; then
    echo "初始化数据库..."
    docker exec mcp-postgresql psql -U mcp_user -d mcp_db -f /docker-entrypoint-initdb.d/init.sql
fi

echo "部署完成！"
echo "访问地址:"
echo "  - API服务: http://localhost:8000"
echo "  - 推理服务: http://localhost:8001"
echo "  - Grafana监控: http://localhost:3000 (admin/admin123)"
echo "  - MinIO控制台: http://localhost:9001 (minioadmin/minioadmin123)"
```

### 6.2 健康检查脚本 (scripts/health_check.sh)

```bash
#!/bin/bash

# 健康检查脚本

SERVICES=("mcp-api:8000" "mcp-inference:8001" "redis:6379" "postgresql:5432")
FAILED_SERVICES=()

echo "开始健康检查..."

for service in "${SERVICES[@]}"; do
    IFS=':' read -r name port <<< "$service"
    
    echo -n "检查 $name:$port ... "
    
    if timeout 10 bash -c "</dev/tcp/localhost/$port"; then
        echo "✓ 正常"
    else
        echo "✗ 失败"
        FAILED_SERVICES+=("$name:$port")
    fi
done

# API端点检查
echo -n "检查API端点 ... "
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "✓ 正常"
else
    echo "✗ 失败"
    FAILED_SERVICES+=("API端点")
fi

# 推理服务检查
echo -n "检查推理服务 ... "
if curl -f -s http://localhost:8001/health > /dev/null; then
    echo "✓ 正常"
else
    echo "✗ 失败"
    FAILED_SERVICES+=("推理服务")
fi

# 结果汇总
if [ ${#FAILED_SERVICES[@]} -eq 0 ]; then
    echo "\n✓ 所有服务运行正常"
    exit 0
else
    echo "\n✗ 以下服务存在问题:"
    printf '  - %s\n' "${FAILED_SERVICES[@]}"
    exit 1
fi
```

## 7. 运维管理

### 7.1 服务管理命令

```bash
# 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 停止所有服务
docker-compose -f docker-compose.prod.yml down

# 重启特定服务
docker-compose -f docker-compose.prod.yml restart mcp-api

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看服务日志
docker-compose -f docker-compose.prod.yml logs -f mcp-training

# 扩展服务实例
docker-compose -f docker-compose.prod.yml up -d --scale mcp-inference=3

# 更新服务
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### 7.2 故障排查

#### 常见问题及解决方案

1. **容器启动失败**
```bash
# 查看容器日志
docker logs mcp-training

# 检查容器状态
docker inspect mcp-training

# 进入容器调试
docker exec -it mcp-training bash
```

2. **网络连接问题**
```bash
# 检查网络配置
docker network ls
docker network inspect mcp-network

# 测试容器间连通性
docker exec mcp-api ping redis
```

3. **资源不足**
```bash
# 查看资源使用情况
docker stats

# 清理未使用的资源
docker system prune -a
```

### 7.3 性能优化

#### 容器资源限制
```yaml
services:
  mcp-training:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
```

#### 镜像优化
```dockerfile
# 多阶段构建减小镜像大小
FROM nvidia/cuda:12.6.0-devel-ubuntu20.04 as builder
# 构建阶段

FROM nvidia/cuda:12.6.0-runtime-ubuntu20.04 as runtime
# 运行阶段，只包含必要的运行时文件
```

## 8. 安全配置

### 8.1 网络安全

```yaml
# 网络隔离配置
networks:
  frontend:
    driver: bridge
    internal: false
  backend:
    driver: bridge
    internal: true
  database:
    driver: bridge
    internal: true
```

### 8.2 访问控制

```yaml
# 环境变量加密
services:
  mcp-api:
    environment:
      - DATABASE_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### 8.3 SSL/TLS配置

```nginx
# nginx SSL配置
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    location / {
        proxy_pass http://mcp-api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 9. 总结

本方案提供了一套完整的多容器Docker部署解决方案，包括：

- **架构设计**: 分层架构，职责清晰
- **容器编排**: Docker Compose统一管理
- **服务通信**: 网络隔离和消息队列
- **数据管理**: 持久化存储和备份策略
- **监控日志**: 全方位监控和日志收集
- **运维管理**: 自动化部署和故障排查
- **安全配置**: 网络安全和访问控制

通过这套方案，可以实现MCP微调系统的高可用、可扩展、易维护的生产环境部署。