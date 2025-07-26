#!/bin/bash

# 分支管理脚本
# 用法: ./branch_manager.sh [command] [args]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 显示帮助信息
show_help() {
    echo "分支管理脚本"
    echo
    echo "用法: $0 [command] [args]"
    echo
    echo "命令:"
    echo "  list                 列出所有分支"
    echo "  create <name>        创建新分支"
    echo "  switch <name>        切换分支"
    echo "  delete <name>        删除分支"
    echo "  merge <name>         合并分支到当前分支"
    echo "  sync                 同步远程分支"
    echo "  clean                清理已合并的分支"
    echo "  status               显示分支状态"
    echo "  help                 显示帮助信息"
}

# 列出分支
list_branches() {
    log_info "本地分支:"
    git branch -v
    echo
    log_info "远程分支:"
    git branch -r -v
}

# 创建分支
create_branch() {
    local branch_name=$1
    if [ -z "$branch_name" ]; then
        log_error "请提供分支名称"
        exit 1
    fi
    
    log_info "创建分支: $branch_name"
    git checkout -b "$branch_name"
    log_success "分支 $branch_name 创建并切换成功"
}

# 切换分支
switch_branch() {
    local branch_name=$1
    if [ -z "$branch_name" ]; then
        log_error "请提供分支名称"
        exit 1
    fi
    
    log_info "切换到分支: $branch_name"
    git checkout "$branch_name"
    log_success "已切换到分支 $branch_name"
}

# 删除分支
delete_branch() {
    local branch_name=$1
    if [ -z "$branch_name" ]; then
        log_error "请提供分支名称"
        exit 1
    fi
    
    local current_branch=$(git branch --show-current)
    if [ "$branch_name" = "$current_branch" ]; then
        log_error "不能删除当前分支"
        exit 1
    fi
    
    log_warning "删除分支: $branch_name"
    read -p "确认删除? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git branch -d "$branch_name"
        log_success "分支 $branch_name 已删除"
        
        read -p "是否删除远程分支? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push origin --delete "$branch_name"
            log_success "远程分支 $branch_name 已删除"
        fi
    fi
}

# 合并分支
merge_branch() {
    local branch_name=$1
    if [ -z "$branch_name" ]; then
        log_error "请提供分支名称"
        exit 1
    fi
    
    local current_branch=$(git branch --show-current)
    log_info "将分支 $branch_name 合并到 $current_branch"
    
    git merge "$branch_name"
    log_success "分支合并完成"
}

# 同步远程分支
sync_remote() {
    log_info "同步远程分支..."
    git fetch --all --prune
    log_success "远程分支同步完成"
}

# 清理已合并的分支
clean_merged() {
    log_info "查找已合并的分支..."
    
    local merged_branches=$(git branch --merged | grep -v "\*\|main\|master\|develop")
    
    if [ -z "$merged_branches" ]; then
        log_info "没有需要清理的分支"
        return
    fi
    
    echo "已合并的分支:"
    echo "$merged_branches"
    
    read -p "是否删除这些分支? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$merged_branches" | xargs -n 1 git branch -d
        log_success "已合并的分支清理完成"
    fi
}

# 显示分支状态
show_status() {
    local current_branch=$(git branch --show-current)
    log_info "当前分支: $current_branch"
    
    echo
    log_info "工作区状态:"
    git status --short
    
    echo
    log_info "最近提交:"
    git log --oneline -5
    
    echo
    log_info "分支关系:"
    git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit -10
}

# 主函数
main() {
    local command=${1:-"help"}
    
    case $command in
        "list")
            list_branches
            ;;
        "create")
            create_branch $2
            ;;
        "switch")
            switch_branch $2
            ;;
        "delete")
            delete_branch $2
            ;;
        "merge")
            merge_branch $2
            ;;
        "sync")
            sync_remote
            ;;
        "clean")
            clean_merged
            ;;
        "status")
            show_status
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

main "$@"