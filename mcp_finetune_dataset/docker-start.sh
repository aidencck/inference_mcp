#!/bin/bash

# MCP微调项目Docker启动脚本
# 使用方法: ./docker-start.sh [命令]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="mcp-finetune"
CONTAINER_NAME="mcp-training-container"
IMAGE_NAME="mcp-finetune:latest"

# 函数：打印帮助信息
show_help() {
    echo -e "${BLUE}MCP微调项目Docker管理脚本${NC}"
    echo ""
    echo "使用方法: $0 [命令]"
    echo ""
    echo "可用命令:"
    echo "  build          构建Docker镜像"
    echo "  start          启动容器"
    echo "  stop           停止容器"
    echo "  restart        重启容器"
    echo "  logs           查看容器日志"
    echo "  shell          进入容器Shell"
    echo "  jupyter        启动Jupyter服务"
    echo "  tensorboard    启动TensorBoard服务"
    echo "  train          运行训练脚本"
    echo "  test           运行测试"
    echo "  clean          清理容器和镜像"
    echo "  status         查看容器状态"
    echo "  help           显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 build        # 构建镜像"
    echo "  $0 start        # 启动容器"
    echo "  $0 shell        # 进入容器"
    echo "  $0 train        # 运行训练"
}

# 函数：检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker未安装或不在PATH中${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}警告: docker-compose未安装，将使用docker命令${NC}"
    fi
}

# 函数：检查NVIDIA Docker支持
check_nvidia_docker() {
    if ! docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi &> /dev/null; then
        echo -e "${YELLOW}警告: NVIDIA Docker支持未正确配置，GPU功能可能不可用${NC}"
    fi
}

# 函数：构建镜像
build_image() {
    echo -e "${BLUE}构建Docker镜像...${NC}"
    docker build -t $IMAGE_NAME .
    echo -e "${GREEN}镜像构建完成${NC}"
}

# 函数：启动容器
start_container() {
    echo -e "${BLUE}启动容器...${NC}"
    
    # 检查容器是否已存在
    if docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${YELLOW}容器已存在，正在启动...${NC}"
        docker start $CONTAINER_NAME
    else
        echo -e "${BLUE}创建并启动新容器...${NC}"
        if command -v docker-compose &> /dev/null; then
            docker-compose up -d mcp-training
        else
            docker run -d \
                --name $CONTAINER_NAME \
                --gpus all \
                -v $(pwd)/data:/app/data \
                -v $(pwd)/models:/app/models \
                -v $(pwd)/logs:/app/logs \
                -v $(pwd)/outputs:/app/outputs \
                -v $(pwd)/.cache:/app/.cache \
                -p 8888:8888 \
                -p 8000:8000 \
                -p 6006:6006 \
                --shm-size=2g \
                $IMAGE_NAME
        fi
    fi
    
    echo -e "${GREEN}容器启动完成${NC}"
}

# 函数：停止容器
stop_container() {
    echo -e "${BLUE}停止容器...${NC}"
    if command -v docker-compose &> /dev/null; then
        docker-compose stop
    else
        docker stop $CONTAINER_NAME
    fi
    echo -e "${GREEN}容器已停止${NC}"
}

# 函数：重启容器
restart_container() {
    stop_container
    start_container
}

# 函数：查看日志
show_logs() {
    echo -e "${BLUE}查看容器日志...${NC}"
    docker logs -f $CONTAINER_NAME
}

# 函数：进入容器Shell
enter_shell() {
    echo -e "${BLUE}进入容器Shell...${NC}"
    docker exec -it $CONTAINER_NAME /bin/bash
}

# 函数：启动Jupyter
start_jupyter() {
    echo -e "${BLUE}启动Jupyter服务...${NC}"
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d jupyter
        echo -e "${GREEN}Jupyter已启动，访问地址: http://localhost:8889${NC}"
        echo -e "${YELLOW}Token: mcp-training-2024${NC}"
    else
        docker exec -d $CONTAINER_NAME jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
        echo -e "${GREEN}Jupyter已启动，访问地址: http://localhost:8888${NC}"
    fi
}

# 函数：启动TensorBoard
start_tensorboard() {
    echo -e "${BLUE}启动TensorBoard服务...${NC}"
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d tensorboard
        echo -e "${GREEN}TensorBoard已启动，访问地址: http://localhost:6007${NC}"
    else
        docker exec -d $CONTAINER_NAME tensorboard --logdir=/app/logs --host=0.0.0.0 --port=6006
        echo -e "${GREEN}TensorBoard已启动，访问地址: http://localhost:6006${NC}"
    fi
}

# 函数：运行训练
run_training() {
    echo -e "${BLUE}运行训练脚本...${NC}"
    docker exec -it $CONTAINER_NAME bash -c "cd /app && ./run_training.sh"
}

# 函数：运行测试
run_test() {
    echo -e "${BLUE}运行测试...${NC}"
    docker exec -it $CONTAINER_NAME bash -c "cd /app && python -m pytest tests/ -v"
}

# 函数：清理容器和镜像
clean_all() {
    echo -e "${YELLOW}警告: 这将删除所有相关容器和镜像${NC}"
    read -p "确认继续? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}清理容器和镜像...${NC}"
        
        # 停止并删除容器
        if command -v docker-compose &> /dev/null; then
            docker-compose down --rmi all --volumes
        else
            docker stop $CONTAINER_NAME 2>/dev/null || true
            docker rm $CONTAINER_NAME 2>/dev/null || true
            docker rmi $IMAGE_NAME 2>/dev/null || true
        fi
        
        echo -e "${GREEN}清理完成${NC}"
    else
        echo -e "${YELLOW}取消清理操作${NC}"
    fi
}

# 函数：查看状态
show_status() {
    echo -e "${BLUE}容器状态:${NC}"
    docker ps -a --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo -e "\n${BLUE}镜像信息:${NC}"
    docker images --filter "reference=$IMAGE_NAME" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    echo -e "\n${BLUE}GPU状态:${NC}"
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits
    else
        echo "NVIDIA驱动未安装或不可用"
    fi
}

# 主函数
main() {
    # 检查Docker
    check_docker
    
    # 解析命令
    case "${1:-help}" in
        build)
            build_image
            ;;
        start)
            check_nvidia_docker
            start_container
            ;;
        stop)
            stop_container
            ;;
        restart)
            restart_container
            ;;
        logs)
            show_logs
            ;;
        shell)
            enter_shell
            ;;
        jupyter)
            start_jupyter
            ;;
        tensorboard)
            start_tensorboard
            ;;
        train)
            run_training
            ;;
        test)
            run_test
            ;;
        clean)
            clean_all
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}未知命令: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"