#!/bin/bash

# GitHub统一管理脚本
# 用法: ./github_manager.sh [command] [args...]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_header() { echo -e "${PURPLE}[GITHUB MANAGER]${NC} $1"; }

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 显示欢迎信息
show_welcome() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    GitHub 仓库管理工具                        ║"
    echo "║                                                              ║"
    echo "║  统一管理开发中的GitHub仓库，提供快速、便捷的操作接口          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 显示帮助信息
show_help() {
    show_welcome
    echo
    log_header "可用命令:"
    echo
    echo -e "  ${GREEN}仓库管理:${NC}"
    echo "    init <name> [desc]     初始化新仓库"
    echo "    status                 显示仓库状态"
    echo "    info                   显示仓库信息"
    echo
    echo -e "  ${GREEN}分支操作:${NC}"
    echo "    branch list            列出所有分支"
    echo "    branch create <name>   创建新分支"
    echo "    branch switch <name>   切换分支"
    echo "    branch delete <name>   删除分支"
    echo "    branch merge <name>    合并分支"
    echo "    branch sync            同步远程分支"
    echo "    branch clean           清理已合并分支"
    echo "    branch status          显示分支状态"
    echo
    echo -e "  ${GREEN}提交操作:${NC}"
    echo "    commit [message]       快速提交"
    echo "    push [branch]          推送到远程"
    echo "    pull [branch]          拉取远程更新"
    echo
    echo -e "  ${GREEN}发布管理:${NC}"
    echo "    release [version]      创建发布版本"
    echo "    release major          创建主版本发布"
    echo "    release minor          创建次版本发布"
    echo "    release patch          创建补丁版本发布"
    echo
    echo -e "  ${GREEN}代码质量:${NC}"
    echo "    check                  运行代码质量检查"
    echo "    lint                   代码风格检查"
    echo "    test                   运行测试"
    echo "    security               安全检查"
    echo
    echo -e "  ${GREEN}工具命令:${NC}"
    echo "    setup                  设置开发环境"
    echo "    clean                  清理临时文件"
    echo "    backup                 备份当前状态"
    echo "    help                   显示帮助信息"
    echo
    echo -e "  ${YELLOW}示例:${NC}"
    echo "    $0 init my-project \"My awesome project\""
    echo "    $0 branch create feature/new-feature"
    echo "    $0 commit \"Add new feature\""
    echo "    $0 release minor"
    echo
}

# 检查Git仓库
check_git_repo() {
    if [ ! -d ".git" ]; then
        log_error "当前目录不是Git仓库"
        log_info "使用 '$0 init <name>' 初始化新仓库"
        exit 1
    fi
}

# 初始化仓库
init_repo() {
    local repo_name=$1
    local description=$2
    
    if [ -z "$repo_name" ]; then
        log_error "请提供仓库名称"
        echo "用法: $0 init <repo_name> [description]"
        exit 1
    fi
    
    log_header "初始化仓库: $repo_name"
    bash "$SCRIPT_DIR/init_repo.sh" "$repo_name" "$description"
}

# 分支管理
manage_branch() {
    check_git_repo
    local action=$1
    shift
    
    log_header "分支管理: $action"
    bash "$SCRIPT_DIR/branch_manager.sh" "$action" "$@"
}

# 快速提交
quick_commit() {
    check_git_repo
    local message=$1
    local branch=$2
    
    log_header "快速提交"
    bash "$SCRIPT_DIR/quick_commit.sh" "$message" "$branch"
}

# 发布管理
manage_release() {
    check_git_repo
    local version=$1
    local type=$2
    
    log_header "发布管理"
    bash "$SCRIPT_DIR/release_manager.sh" "$version" "$type"
}

# 代码检查
run_code_check() {
    check_git_repo
    log_header "代码质量检查"
    bash "$SCRIPT_DIR/code_check.sh"
}

# 显示仓库状态
show_status() {
    check_git_repo
    log_header "仓库状态"
    
    echo -e "${GREEN}当前分支:${NC}"
    git branch --show-current
    echo
    
    echo -e "${GREEN}工作区状态:${NC}"
    git status --short
    echo
    
    echo -e "${GREEN}最近提交:${NC}"
    git log --oneline -5
    echo
    
    echo -e "${GREEN}远程仓库:${NC}"
    git remote -v
}

# 显示仓库信息
show_info() {
    check_git_repo
    log_header "仓库信息"
    
    echo -e "${GREEN}仓库路径:${NC} $(pwd)"
    echo -e "${GREEN}当前分支:${NC} $(git branch --show-current)"
    echo -e "${GREEN}总提交数:${NC} $(git rev-list --all --count)"
    echo -e "${GREEN}贡献者数:${NC} $(git shortlog -sn | wc -l)"
    echo -e "${GREEN}文件总数:${NC} $(git ls-files | wc -l)"
    
    if git remote get-url origin &>/dev/null; then
        echo -e "${GREEN}远程地址:${NC} $(git remote get-url origin)"
    fi
    
    local last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "无标签")
    echo -e "${GREEN}最新标签:${NC} $last_tag"
    
    echo
    echo -e "${GREEN}分支列表:${NC}"
    git branch -a
}

# 推送到远程
push_to_remote() {
    check_git_repo
    local branch=${1:-$(git branch --show-current)}
    
    log_header "推送到远程: $branch"
    
    if git remote get-url origin &>/dev/null; then
        git push origin "$branch"
        log_success "推送完成"
    else
        log_error "未配置远程仓库"
        log_info "使用以下命令添加远程仓库:"
        echo "git remote add origin <repository_url>"
    fi
}

# 拉取远程更新
pull_from_remote() {
    check_git_repo
    local branch=${1:-$(git branch --show-current)}
    
    log_header "拉取远程更新: $branch"
    
    if git remote get-url origin &>/dev/null; then
        git pull origin "$branch"
        log_success "拉取完成"
    else
        log_error "未配置远程仓库"
    fi
}

# 设置开发环境
setup_environment() {
    log_header "设置开发环境"
    
    # 设置Git配置
    if [ -z "$(git config --global user.name)" ]; then
        read -p "请输入您的姓名: " user_name
        git config --global user.name "$user_name"
    fi
    
    if [ -z "$(git config --global user.email)" ]; then
        read -p "请输入您的邮箱: " user_email
        git config --global user.email "$user_email"
    fi
    
    # 设置常用别名
    git config --global alias.st status
    git config --global alias.co checkout
    git config --global alias.br branch
    git config --global alias.ci commit
    git config --global alias.lg "log --oneline --graph --decorate"
    
    # 设置脚本权限
    chmod +x "$SCRIPT_DIR"/*.sh
    
    log_success "开发环境设置完成"
}

# 清理临时文件
clean_temp_files() {
    check_git_repo
    log_header "清理临时文件"
    
    # 清理Git缓存
    git gc --prune=now
    
    # 清理未跟踪的文件（询问确认）
    if [ -n "$(git clean -n)" ]; then
        echo "将要删除的文件:"
        git clean -n
        read -p "确认删除这些文件? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git clean -fd
            log_success "临时文件清理完成"
        else
            log_info "取消清理操作"
        fi
    else
        log_info "没有需要清理的文件"
    fi
}

# 备份当前状态
backup_current_state() {
    check_git_repo
    log_header "备份当前状态"
    
    local backup_branch="backup-$(date +%Y%m%d-%H%M%S)"
    local current_branch=$(git branch --show-current)
    
    # 创建备份分支
    git checkout -b "$backup_branch"
    
    # 如果有未提交的更改，先提交
    if [ -n "$(git status --porcelain)" ]; then
        git add .
        git commit -m "Backup: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    # 切换回原分支
    git checkout "$current_branch"
    
    log_success "备份分支已创建: $backup_branch"
}

# 主函数
main() {
    local command=${1:-"help"}
    
    case $command in
        "init")
            init_repo "$2" "$3"
            ;;
        "status")
            show_status
            ;;
        "info")
            show_info
            ;;
        "branch")
            manage_branch "$2" "${@:3}"
            ;;
        "commit")
            quick_commit "$2" "$3"
            ;;
        "push")
            push_to_remote "$2"
            ;;
        "pull")
            pull_from_remote "$2"
            ;;
        "release")
            if [ "$2" = "major" ] || [ "$2" = "minor" ] || [ "$2" = "patch" ]; then
                manage_release "" "$2"
            else
                manage_release "$2" "$3"
            fi
            ;;
        "check")
            run_code_check
            ;;
        "lint")
            # 只运行代码风格检查
            check_git_repo
            log_header "代码风格检查"
            # 这里可以调用具体的lint工具
            ;;
        "test")
            # 只运行测试
            check_git_repo
            log_header "运行测试"
            # 这里可以调用具体的测试命令
            ;;
        "security")
            # 只运行安全检查
            check_git_repo
            log_header "安全检查"
            # 这里可以调用具体的安全检查工具
            ;;
        "setup")
            setup_environment
            ;;
        "clean")
            clean_temp_files
            ;;
        "backup")
            backup_current_state
            ;;
        "help")
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            echo
            show_help
            exit 1
            ;;
    esac
}

main "$@"