#!/bin/bash

# MCP模型训练完整流程脚本
# 包含环境检查、模型下载、数据生成、训练和测试

set -e  # 遇到错误立即退出

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

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# 配置文件路径
CONFIG_FILE="$PROJECT_DIR/config.yaml"

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    log_error "配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 解析命令行参数
SKIP_INSTALL=false
SKIP_DOWNLOAD=false
SKIP_DATA_GEN=false
ONLY_TEST=false
INTERACTIVE=false
CUSTOM_CONFIG=""
SKIP_HF_SYNC=false
FORCE_HF_SYNC=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-install)
            SKIP_INSTALL=true
            shift
            ;;
        --skip-download)
            SKIP_DOWNLOAD=true
            shift
            ;;
        --skip-data-gen)
            SKIP_DATA_GEN=true
            shift
            ;;
        --only-test)
            ONLY_TEST=true
            shift
            ;;
        --interactive)
            INTERACTIVE=true
            shift
            ;;
        --config)
            CUSTOM_CONFIG="$2"
            shift 2
            ;;
        --skip-hf-sync)
            SKIP_HF_SYNC=true
            shift
            ;;
        --force-hf-sync)
            FORCE_HF_SYNC=true
            shift
            ;;
        --help|-h)
            echo "MCP模型训练脚本"
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --skip-install    跳过依赖安装"
            echo "  --skip-download   跳过模型下载"
            echo "  --skip-data-gen   跳过数据生成"
            echo "  --only-test       仅运行测试"
            echo "  --interactive     交互式测试模式"
            echo "  --config FILE     使用自定义配置文件"
            echo "  --skip-hf-sync    跳过HuggingFace同步"
            echo "  --force-hf-sync   强制执行HuggingFace同步"
            echo "  --help, -h        显示此帮助信息"
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            exit 1
            ;;
    esac
done

# 使用自定义配置文件
if [ -n "$CUSTOM_CONFIG" ]; then
    if [ -f "$CUSTOM_CONFIG" ]; then
        CONFIG_FILE="$CUSTOM_CONFIG"
        log_info "使用自定义配置文件: $CONFIG_FILE"
    else
        log_error "自定义配置文件不存在: $CUSTOM_CONFIG"
        exit 1
    fi
fi

# 检查Python环境
check_python() {
    log_info "检查Python环境..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    log_info "Python版本: $PYTHON_VERSION"
    
    # 检查是否满足最低版本要求 (3.8+)
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_success "Python版本满足要求"
    else
        log_error "Python版本过低，需要3.8或更高版本"
        exit 1
    fi
}

# 检查GPU环境
check_gpu() {
    log_info "检查GPU环境..."
    
    if command -v nvidia-smi &> /dev/null; then
        GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | head -1)
        log_success "检测到GPU: $GPU_INFO"
        
        # 检查CUDA
        if python3 -c "import torch; print('CUDA可用:', torch.cuda.is_available())" 2>/dev/null; then
            log_success "CUDA环境正常"
        else
            log_warning "CUDA不可用，将使用CPU训练（速度较慢）"
        fi
    else
        log_warning "未检测到GPU，将使用CPU训练"
    fi
}

# 检查HuggingFace环境
check_huggingface() {
    log_info "检查HuggingFace环境..."
    
    # 检查是否启用HuggingFace集成
    HF_ENABLED=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config.get('huggingface', {}).get('enabled', False))" 2>/dev/null || echo "False")
    
    if [ "$HF_ENABLED" = "True" ]; then
        log_info "HuggingFace集成已启用"
        
        # 检查Token
        if [ -n "$HUGGINGFACE_TOKEN" ]; then
            log_success "检测到HuggingFace Token (环境变量)"
        elif python3 -c "from huggingface_hub import HfApi; HfApi().whoami()" 2>/dev/null; then
            log_success "HuggingFace认证正常"
        else
            log_warning "HuggingFace Token未设置，请运行: huggingface-cli login"
            log_warning "或设置环境变量: export HUGGINGFACE_TOKEN=your_token"
        fi
        
        # 检查配置文件
        HF_CONFIG_FILE="$PROJECT_DIR/configs/huggingface_config.yaml"
        if [ -f "$HF_CONFIG_FILE" ]; then
            log_success "HuggingFace配置文件存在"
        else
            log_warning "HuggingFace配置文件不存在: $HF_CONFIG_FILE"
        fi
    else
        log_info "HuggingFace集成未启用"
    fi
}

# 安装依赖
install_dependencies() {
    if [ "$SKIP_INSTALL" = true ]; then
        log_info "跳过依赖安装"
        return
    fi
    
    log_info "安装Python依赖..."
    
    # 检查requirements.txt
    if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
        log_error "requirements.txt 文件不存在"
        exit 1
    fi
    
    # 安装依赖
    python3 -m pip install --upgrade pip
    python3 -m pip install -r "$PROJECT_DIR/requirements.txt"
    
    log_success "依赖安装完成"
}

# 下载模型
download_model() {
    if [ "$SKIP_DOWNLOAD" = true ]; then
        log_info "跳过模型下载"
        return
    fi
    
    log_info "检查并下载模型..."
    
    cd "$PROJECT_DIR"
    python3 -c "
import sys
sys.path.append('scripts')
from model_manager import ModelManager
import yaml

# 加载配置
with open('$CONFIG_FILE', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 创建模型管理器
manager = ModelManager(config)

# 下载模型
print('开始下载模型...')
manager.download_model()
print('模型下载完成')
"
    
    if [ $? -eq 0 ]; then
        log_success "模型下载完成"
    else
        log_error "模型下载失败"
        exit 1
    fi
}

# 生成训练数据
generate_data() {
    if [ "$SKIP_DATA_GEN" = true ]; then
        log_info "跳过数据生成"
        return
    fi
    
    log_info "生成训练数据..."
    
    cd "$PROJECT_DIR"
    
    # 检查数据文件是否已存在
    TRAIN_FILE=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['data']['train_file'])")
    VALIDATION_FILE=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['data']['validation_file'])")
    
    if [ -f "$TRAIN_FILE" ] && [ -f "$VALIDATION_FILE" ]; then
        log_warning "训练数据已存在，是否重新生成？(y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_info "跳过数据生成"
            return
        fi
    fi
    
    # 生成训练数据
    python3 scripts/generate_dataset.py --config "$CONFIG_FILE"
    
    if [ $? -eq 0 ]; then
        log_success "训练数据生成完成"
    else
        log_error "训练数据生成失败"
        exit 1
    fi
}

# 开始训练
start_training() {
    log_info "开始模型训练..."
    
    cd "$PROJECT_DIR"
    
    # 创建日志目录
    mkdir -p logs
    
    # 开始训练
    python3 scripts/train_mcp_model.py --config "$CONFIG_FILE" 2>&1 | tee "logs/training_$(date +%Y%m%d_%H%M%S).log"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "模型训练完成"
    else
        log_error "模型训练失败"
        exit 1
    fi
}

# 测试模型
test_model() {
    log_info "测试训练好的模型..."
    
    cd "$PROJECT_DIR"
    
    # 获取输出目录
    OUTPUT_DIR=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['output']['model_dir'])")
    
    # 处理相对路径
    if [[ ! "$OUTPUT_DIR" = /* ]]; then
        OUTPUT_DIR="$PROJECT_DIR/$OUTPUT_DIR"
    fi
    
    if [ ! -d "$OUTPUT_DIR" ]; then
        log_error "模型输出目录不存在: $OUTPUT_DIR"
        exit 1
    fi
    
    # 获取基础模型名称
    BASE_MODEL=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['model']['name'])")
    
    if [ "$INTERACTIVE" = true ]; then
        log_info "启动交互式测试模式..."
        python3 scripts/inference.py --model_path "$OUTPUT_DIR" --base_model "$BASE_MODEL" --interactive
    else
        log_info "运行批量测试..."
        python3 scripts/inference.py --model_path "$OUTPUT_DIR" --base_model "$BASE_MODEL"
    fi
    
    if [ $? -eq 0 ]; then
        log_success "模型测试完成"
    else
        log_error "模型测试失败"
        exit 1
    fi
}

# 同步到HuggingFace
sync_to_huggingface() {
    if [ "$SKIP_HF_SYNC" = true ]; then
        log_info "跳过HuggingFace同步"
        return
    fi
    
    # 检查是否启用HuggingFace集成
    HF_ENABLED=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config.get('huggingface', {}).get('enabled', False))" 2>/dev/null || echo "False")
    
    if [ "$HF_ENABLED" != "True" ] && [ "$FORCE_HF_SYNC" != true ]; then
        log_info "HuggingFace集成未启用，跳过同步"
        return
    fi
    
    log_info "开始同步到HuggingFace..."
    
    cd "$PROJECT_DIR"
    
    # 获取输出目录
    OUTPUT_DIR=$(python3 -c "import yaml; config=yaml.safe_load(open('$CONFIG_FILE')); print(config['output']['model_dir'])")
    
    # 处理相对路径
    if [[ ! "$OUTPUT_DIR" = /* ]]; then
        OUTPUT_DIR="$PROJECT_DIR/$OUTPUT_DIR"
    fi
    
    if [ ! -d "$OUTPUT_DIR" ]; then
        log_error "模型输出目录不存在: $OUTPUT_DIR"
        log_error "无法进行HuggingFace同步"
        return
    fi
    
    # 生成版本标签
    VERSION_TAG="v$(date +%Y%m%d-%H%M%S)"
    EXPERIMENT_NAME="training_$(date +%Y%m%d_%H%M%S)"
    
    # 执行同步
    python3 -c "
import sys
sys.path.append('scripts')
from huggingface_manager import HuggingFaceManager
import traceback

try:
    # 创建管理器
    manager = HuggingFaceManager('$CONFIG_FILE')
    
    # 同步工作流
    print('开始同步训练工作流到HuggingFace...')
    results = manager.sync_training_workflow(
        model_path='$OUTPUT_DIR',
        experiment_name='$EXPERIMENT_NAME',
        version_tag='$VERSION_TAG',
        private=True
    )
    
    print('同步完成:')
    for key, url in results.items():
        print(f'  {key}: {url}')
        
except Exception as e:
    print(f'同步失败: {e}')
    traceback.print_exc()
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        log_success "HuggingFace同步完成"
        log_info "版本标签: $VERSION_TAG"
        log_info "实验名称: $EXPERIMENT_NAME"
    else
        log_error "HuggingFace同步失败"
        log_warning "您可以稍后手动同步:"
        log_warning "python scripts/huggingface_manager.py sync --model-path $OUTPUT_DIR"
    fi
}

# 显示训练信息
show_training_info() {
    log_info "训练配置信息:"
    echo "  配置文件: $CONFIG_FILE"
    echo "  项目目录: $PROJECT_DIR"
    
    # 显示配置摘要
    python3 -c "
import yaml
with open('$CONFIG_FILE', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

print(f'  模型: {config[\"model\"][\"name\"]}')
print(f'  训练轮数: {config[\"training\"][\"num_epochs\"]}')
print(f'  批次大小: {config[\"training\"][\"batch_size\"]}')
print(f'  学习率: {config[\"training\"][\"learning_rate\"]}')
print(f'  输出目录: {config[\"output\"][\"model_dir\"]}')
"
}

# 主函数
main() {
    echo "="*60
    echo "MCP模型训练完整流程"
    echo "="*60
    
    # 显示训练信息
    show_training_info
    echo ""
    
    # 如果只是测试模式
    if [ "$ONLY_TEST" = true ]; then
        log_info "仅运行测试模式"
        test_model
        return
    fi
    
    # 环境检查
    check_python
    check_gpu
    check_huggingface
    echo ""
    
    # 安装依赖
    install_dependencies
    echo ""
    
    # 下载模型
    download_model
    echo ""
    
    # 生成数据
    generate_data
    echo ""
    
    # 开始训练
    start_training
    echo ""
    
    # 测试模型
    test_model
    
    # HuggingFace同步
    sync_to_huggingface
    
    echo ""
    log_success "所有流程完成！"
    echo "="*60
}

# 捕获中断信号
trap 'log_warning "训练被中断"; exit 1' INT TERM

# 运行主函数
main