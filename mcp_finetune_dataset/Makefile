# MCP微调项目Docker管理Makefile
# 使用方法: make [target]
# Docker Makefile Introduction
# A Makefile for managing Docker containers and images
# Key features:
# - Build and manage Docker images
# - Control container lifecycle (start/stop/restart)
# - Handle Docker volumes and networks
# - Provide development and production environments
# - Automate common Docker operations
# # 一键设置开发环境
#   make dev-setup

# 或分步执行
# 	./docker-start.sh build
# 	./docker-start.sh start
# 	./docker-start.sh jupyter

# 训练模型
# 	make train              # 运行训练
# 	make tensorboard        # 监控训练
# 	make health            # 健康检查
# 生产部署
# 	make prod-build        # 构建生产镜像
# 	make prod-up          # 启动生产环境
# 	make prod-status      # 查看状态
# 项目配置
PROJECT_NAME := mcp-finetune
IMAGE_NAME := $(PROJECT_NAME):latest
CONTAINER_NAME := mcp-training-container
DOCKER_COMPOSE := docker-compose
DOCKER_COMPOSE_PROD := docker-compose -f docker-compose.prod.yml

# 颜色定义
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# 默认目标
.DEFAULT_GOAL := help

# 帮助信息
.PHONY: help
help: ## 显示帮助信息
	@echo "$(BLUE)MCP微调项目Docker管理命令$(NC)"
	@echo ""
	@echo "$(YELLOW)构建相关:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "build|image"
	@echo ""
	@echo "$(YELLOW)容器管理:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "start|stop|restart|up|down"
	@echo ""
	@echo "$(YELLOW)开发工具:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "shell|logs|jupyter|tensorboard"
	@echo ""
	@echo "$(YELLOW)训练和测试:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "train|test|health"
	@echo ""
	@echo "$(YELLOW)维护清理:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "clean|prune|status"
	@echo ""
	@echo "$(YELLOW)生产部署:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "prod"

# 检查Docker环境
.PHONY: check-docker
check-docker:
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)错误: Docker未安装$(NC)"; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "$(YELLOW)警告: docker-compose未安装$(NC)"; }
	@docker info >/dev/null 2>&1 || { echo "$(RED)错误: Docker服务未运行$(NC)"; exit 1; }

# 检查NVIDIA Docker支持
.PHONY: check-gpu
check-gpu:
	@docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi >/dev/null 2>&1 || { echo "$(YELLOW)警告: NVIDIA Docker支持未配置$(NC)"; }

# =============================================================================
# 构建相关
# =============================================================================

.PHONY: build
build: check-docker ## 构建Docker镜像
	@echo "$(BLUE)构建Docker镜像...$(NC)"
	docker build -t $(IMAGE_NAME) .
	@echo "$(GREEN)镜像构建完成$(NC)"

.PHONY: build-no-cache
build-no-cache: check-docker ## 无缓存构建Docker镜像
	@echo "$(BLUE)无缓存构建Docker镜像...$(NC)"
	docker build --no-cache -t $(IMAGE_NAME) .
	@echo "$(GREEN)镜像构建完成$(NC)"

.PHONY: build-jupyter
build-jupyter: check-docker ## 构建Jupyter镜像
	@echo "$(BLUE)构建Jupyter镜像...$(NC)"
	docker build -f Dockerfile.jupyter -t $(PROJECT_NAME)-jupyter:latest .
	@echo "$(GREEN)Jupyter镜像构建完成$(NC)"

# =============================================================================
# 容器管理
# =============================================================================

.PHONY: up
up: check-docker ## 启动所有服务
	@echo "$(BLUE)启动所有服务...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)服务启动完成$(NC)"

.PHONY: down
down: ## 停止所有服务
	@echo "$(BLUE)停止所有服务...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)服务已停止$(NC)"

.PHONY: start
start: check-docker check-gpu ## 启动训练容器
	@echo "$(BLUE)启动训练容器...$(NC)"
	./docker-start.sh start

.PHONY: stop
stop: ## 停止训练容器
	@echo "$(BLUE)停止训练容器...$(NC)"
	./docker-start.sh stop

.PHONY: restart
restart: ## 重启训练容器
	@echo "$(BLUE)重启训练容器...$(NC)"
	./docker-start.sh restart

# =============================================================================
# 开发工具
# =============================================================================

.PHONY: shell
shell: ## 进入容器Shell
	@echo "$(BLUE)进入容器Shell...$(NC)"
	docker exec -it $(CONTAINER_NAME) /bin/bash

.PHONY: logs
logs: ## 查看容器日志
	@echo "$(BLUE)查看容器日志...$(NC)"
	docker logs -f $(CONTAINER_NAME)

.PHONY: jupyter
jupyter: ## 启动Jupyter服务
	@echo "$(BLUE)启动Jupyter服务...$(NC)"
	./docker-start.sh jupyter
	@echo "$(GREEN)Jupyter已启动: http://localhost:8889$(NC)"
	@echo "$(YELLOW)Token: mcp-training-2024$(NC)"

.PHONY: tensorboard
tensorboard: ## 启动TensorBoard服务
	@echo "$(BLUE)启动TensorBoard服务...$(NC)"
	./docker-start.sh tensorboard
	@echo "$(GREEN)TensorBoard已启动: http://localhost:6007$(NC)"

# =============================================================================
# 训练和测试
# =============================================================================

.PHONY: train
train: ## 运行训练脚本
	@echo "$(BLUE)运行训练脚本...$(NC)"
	docker exec -it $(CONTAINER_NAME) bash -c "cd /app && ./run_training.sh"

.PHONY: test
test: ## 运行测试
	@echo "$(BLUE)运行测试...$(NC)"
	docker exec -it $(CONTAINER_NAME) bash -c "cd /app && python -m pytest tests/ -v"

.PHONY: health
health: ## 运行健康检查
	@echo "$(BLUE)运行健康检查...$(NC)"
	docker exec -it $(CONTAINER_NAME) python /app/scripts/health_check.py

.PHONY: inference
inference: ## 运行推理测试
	@echo "$(BLUE)运行推理测试...$(NC)"
	docker exec -it $(CONTAINER_NAME) bash -c "cd /app && python inference.py --interactive"

# =============================================================================
# 维护清理
# =============================================================================

.PHONY: status
status: ## 查看容器状态
	@echo "$(BLUE)容器状态:$(NC)"
	@docker ps -a --filter "name=$(CONTAINER_NAME)" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo "\n$(BLUE)镜像信息:$(NC)"
	@docker images --filter "reference=$(IMAGE_NAME)" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
	@echo "\n$(BLUE)数据卷:$(NC)"
	@docker volume ls --filter "name=$(PROJECT_NAME)"

.PHONY: clean
clean: ## 清理容器和镜像
	@echo "$(YELLOW)警告: 这将删除所有相关容器和镜像$(NC)"
	@read -p "确认继续? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(BLUE)清理容器和镜像...$(NC)"
	$(DOCKER_COMPOSE) down --rmi all --volumes --remove-orphans
	@echo "$(GREEN)清理完成$(NC)"

.PHONY: clean-volumes
clean-volumes: ## 清理数据卷
	@echo "$(YELLOW)警告: 这将删除所有数据卷$(NC)"
	@read -p "确认继续? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(BLUE)清理数据卷...$(NC)"
	docker volume prune -f
	@echo "$(GREEN)数据卷清理完成$(NC)"

.PHONY: prune
prune: ## 清理未使用的Docker资源
	@echo "$(BLUE)清理未使用的Docker资源...$(NC)"
	docker system prune -f
	docker image prune -f
	docker volume prune -f
	@echo "$(GREEN)清理完成$(NC)"

# =============================================================================
# 生产部署
# =============================================================================

.PHONY: prod-build
prod-build: check-docker ## 构建生产环境镜像
	@echo "$(BLUE)构建生产环境镜像...$(NC)"
	$(DOCKER_COMPOSE_PROD) build
	@echo "$(GREEN)生产环境镜像构建完成$(NC)"

.PHONY: prod-up
prod-up: check-docker ## 启动生产环境
	@echo "$(BLUE)启动生产环境...$(NC)"
	$(DOCKER_COMPOSE_PROD) up -d
	@echo "$(GREEN)生产环境启动完成$(NC)"

.PHONY: prod-down
prod-down: ## 停止生产环境
	@echo "$(BLUE)停止生产环境...$(NC)"
	$(DOCKER_COMPOSE_PROD) down
	@echo "$(GREEN)生产环境已停止$(NC)"

.PHONY: prod-logs
prod-logs: ## 查看生产环境日志
	@echo "$(BLUE)查看生产环境日志...$(NC)"
	$(DOCKER_COMPOSE_PROD) logs -f

.PHONY: prod-status
prod-status: ## 查看生产环境状态
	@echo "$(BLUE)生产环境状态:$(NC)"
	$(DOCKER_COMPOSE_PROD) ps

# =============================================================================
# 开发辅助
# =============================================================================

.PHONY: dev-setup
dev-setup: build up jupyter ## 开发环境一键设置
	@echo "$(GREEN)开发环境设置完成$(NC)"
	@echo "$(BLUE)可用服务:$(NC)"
	@echo "  - Jupyter Lab: http://localhost:8889 (Token: mcp-training-2024)"
	@echo "  - 容器Shell: make shell"
	@echo "  - 训练: make train"

.PHONY: backup
backup: ## 备份重要数据
	@echo "$(BLUE)备份重要数据...$(NC)"
	@mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	@docker run --rm -v $(PROJECT_NAME)_models:/data -v $(PWD)/backups/$(shell date +%Y%m%d_%H%M%S):/backup alpine tar czf /backup/models.tar.gz -C /data .
	@cp -r configs/ backups/$(shell date +%Y%m%d_%H%M%S)/
	@echo "$(GREEN)备份完成: backups/$(shell date +%Y%m%d_%H%M%S)$(NC)"

.PHONY: update
update: ## 更新项目依赖
	@echo "$(BLUE)更新项目依赖...$(NC)"
	git pull
	docker pull nvidia/cuda:11.8-devel-ubuntu20.04
	make build-no-cache
	@echo "$(GREEN)更新完成$(NC)"

# =============================================================================
# 监控和调试
# =============================================================================

.PHONY: monitor
monitor: ## 监控容器资源使用
	@echo "$(BLUE)监控容器资源使用...$(NC)"
	docker stats $(CONTAINER_NAME)

.PHONY: gpu-status
gpu-status: ## 查看GPU状态
	@echo "$(BLUE)GPU状态:$(NC)"
	@if command -v nvidia-smi >/dev/null 2>&1; then \
		nvidia-smi; \
	else \
		docker exec $(CONTAINER_NAME) nvidia-smi 2>/dev/null || echo "$(YELLOW)GPU不可用$(NC)"; \
	fi

.PHONY: debug
debug: ## 调试模式启动容器
	@echo "$(BLUE)调试模式启动容器...$(NC)"
	docker run -it --rm --gpus all \
		-v $(PWD):/app \
		-p 8888:8888 \
		--name $(CONTAINER_NAME)-debug \
		$(IMAGE_NAME) /bin/bash

# 确保目录存在
$(shell mkdir -p logs outputs models .cache .temp)

# 防止文件名冲突
.PHONY: all clean build start stop restart shell logs status help