#!/bin/bash

# MCP API服务部署脚本
# 用于快速部署和管理FastAPI服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 检查端口是否被占用
check_ports() {
    local ports=("8000" "80" "443" "6379" "9090" "3000")
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_warning "端口 $port 已被占用"
        fi
    done
}

# 创建必要的目录
setup_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p models data logs ssl monitoring/grafana/provisioning
    
    # 设置权限
    chmod 755 models data logs
    
    log_success "目录创建完成"
}

# 构建Docker镜像
build_image() {
    log_info "构建MCP API Docker镜像..."
    
    docker build -f Dockerfile.api -t mcp-api:latest .
    
    if [ $? -eq 0 ]; then
        log_success "Docker镜像构建成功"
    else
        log_error "Docker镜像构建失败"
        exit 1
    fi
}

# 启动服务
start_services() {
    local mode=${1:-"basic"}
    
    log_info "启动MCP API服务 (模式: $mode)..."
    
    case $mode in
        "basic")
            # 只启动API服务
            docker-compose -f docker-compose.api.yml up -d mcp-api
            ;;
        "full")
            # 启动所有服务
            docker-compose -f docker-compose.api.yml up -d
            ;;
        "api-redis")
            # 启动API和Redis
            docker-compose -f docker-compose.api.yml up -d mcp-api redis
            ;;
        "api-nginx")
            # 启动API和Nginx
            docker-compose -f docker-compose.api.yml up -d mcp-api nginx
            ;;
        *)
            log_error "未知的启动模式: $mode"
            log_info "可用模式: basic, full, api-redis, api-nginx"
            exit 1
            ;;
    esac
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    check_service_health
}

# 检查服务健康状态
check_service_health() {
    log_info "检查服务健康状态..."
    
    # 检查API服务
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            log_success "API服务健康检查通过"
            break
        else
            log_info "等待API服务启动... ($attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "API服务启动失败或健康检查超时"
        show_logs
        exit 1
    fi
}

# 停止服务
stop_services() {
    log_info "停止MCP API服务..."
    
    docker-compose -f docker-compose.api.yml down
    
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    local mode=${1:-"basic"}
    
    log_info "重启MCP API服务..."
    
    stop_services
    sleep 5
    start_services $mode
}

# 显示服务状态
show_status() {
    log_info "服务状态:"
    docker-compose -f docker-compose.api.yml ps
    
    echo
    log_info "服务访问地址:"
    echo "  - API文档: http://localhost:8000/docs"
    echo "  - API健康检查: http://localhost:8000/health"
    echo "  - Nginx (如果启用): http://localhost:80"
    echo "  - Grafana (如果启用): http://localhost:3000 (admin/admin123)"
    echo "  - Prometheus (如果启用): http://localhost:9090"
}

# 显示日志
show_logs() {
    local service=${1:-"mcp-api"}
    local lines=${2:-"50"}
    
    log_info "显示 $service 服务日志 (最近 $lines 行):"
    docker-compose -f docker-compose.api.yml logs --tail=$lines $service
}

# 进入容器
enter_container() {
    local service=${1:-"mcp-api"}
    
    log_info "进入 $service 容器..."
    docker-compose -f docker-compose.api.yml exec $service /bin/bash
}

# 清理资源
cleanup() {
    log_info "清理Docker资源..."
    
    # 停止并删除容器
    docker-compose -f docker-compose.api.yml down -v
    
    # 删除镜像（可选）
    read -p "是否删除Docker镜像? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rmi mcp-api:latest 2>/dev/null || true
        log_success "镜像已删除"
    fi
    
    # 清理未使用的资源
    docker system prune -f
    
    log_success "清理完成"
}

# 安装依赖（本地开发）
install_deps() {
    log_info "安装Python依赖..."
    
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt文件不存在"
        exit 1
    fi
    
    pip install -r requirements.txt
    
    log_success "依赖安装完成"
}

# 本地运行（开发模式）
run_local() {
    log_info "本地运行API服务（开发模式）..."
    
    # 检查依赖
    if ! python -c "import fastapi" 2>/dev/null; then
        log_warning "FastAPI未安装，正在安装依赖..."
        install_deps
    fi
    
    # 启动服务
    python start_api.py --reload
}

# 运行测试
run_tests() {
    log_info "运行API测试..."
    
    if [ ! -f "test_api.py" ]; then
        log_error "test_api.py文件不存在"
        exit 1
    fi
    
    python test_api.py --url http://localhost:8000
}

# 显示帮助信息
show_help() {
    echo "MCP API服务部署脚本"
    echo
    echo "用法: $0 [命令] [选项]"
    echo
    echo "命令:"
    echo "  build                构建Docker镜像"
    echo "  start [mode]         启动服务 (模式: basic|full|api-redis|api-nginx)"
    echo "  stop                 停止服务"
    echo "  restart [mode]       重启服务"
    echo "  status               显示服务状态"
    echo "  logs [service] [n]   显示日志 (默认: mcp-api, 50行)"
    echo "  shell [service]      进入容器 (默认: mcp-api)"
    echo "  cleanup              清理Docker资源"
    echo "  install              安装Python依赖"
    echo "  dev                  本地运行（开发模式）"
    echo "  test                 运行API测试"
    echo "  help                 显示帮助信息"
    echo
    echo "示例:"
    echo "  $0 build                    # 构建镜像"
    echo "  $0 start basic               # 启动基础服务"
    echo "  $0 start full                # 启动所有服务"
    echo "  $0 logs mcp-api 100          # 显示API服务最近100行日志"
    echo "  $0 shell                     # 进入API容器"
    echo "  $0 dev                       # 本地开发模式运行"
}

# 主函数
main() {
    local command=${1:-"help"}
    
    case $command in
        "build")
            check_docker
            setup_directories
            build_image
            ;;
        "start")
            check_docker
            check_ports
            setup_directories
            start_services ${2:-"basic"}
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services ${2:-"basic"}
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs $2 $3
            ;;
        "shell")
            enter_container $2
            ;;
        "cleanup")
            cleanup
            ;;
        "install")
            install_deps
            ;;
        "dev")
            run_local
            ;;
        "test")
            run_tests
            ;;
        "help")
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"