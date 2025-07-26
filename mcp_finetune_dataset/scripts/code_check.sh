#!/bin/bash

# 代码质量检查脚本

set -e

log_info() { echo -e "\033[0;34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# 检查提交信息格式
check_commit_message() {
    local commit_msg=$(git log -1 --pretty=%B)
    local pattern="^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+"
    
    if [[ $commit_msg =~ $pattern ]]; then
        log_success "提交信息格式正确"
    else
        log_error "提交信息格式不符合规范"
        echo "当前提交信息: $commit_msg"
        echo "正确格式: <type>(<scope>): <subject>"
        return 1
    fi
}

# 检查代码风格
check_code_style() {
    log_info "检查代码风格..."
    
    # Python代码检查
    if find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" | head -1 | read; then
        if command -v flake8 &> /dev/null; then
            flake8 . --exclude=venv,.venv,__pycache__ --max-line-length=88
            log_success "Python代码风格检查通过"
        else
            log_info "flake8未安装，跳过Python代码检查"
        fi
    fi
    
    # JavaScript代码检查
    if [ -f "package.json" ] && command -v npm &> /dev/null; then
        if npm list eslint &> /dev/null; then
            npm run lint
            log_success "JavaScript代码风格检查通过"
        else
            log_info "ESLint未配置，跳过JavaScript代码检查"
        fi
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # Python测试
    if [ -f "pytest.ini" ] || [ -f "setup.cfg" ] || find . -name "test_*.py" | head -1 | read; then
        if command -v pytest &> /dev/null; then
            pytest
            log_success "Python测试通过"
        else
            log_info "pytest未安装，跳过Python测试"
        fi
    fi
    
    # JavaScript测试
    if [ -f "package.json" ] && command -v npm &> /dev/null; then
        if npm list jest &> /dev/null || npm list mocha &> /dev/null; then
            npm test
            log_success "JavaScript测试通过"
        else
            log_info "测试框架未配置，跳过JavaScript测试"
        fi
    fi
}

# 检查安全漏洞
check_security() {
    log_info "检查安全漏洞..."
    
    # Python安全检查
    if [ -f "requirements.txt" ] && command -v safety &> /dev/null; then
        safety check
        log_success "Python安全检查通过"
    fi
    
    # JavaScript安全检查
    if [ -f "package.json" ] && command -v npm &> /dev/null; then
        npm audit
        log_success "JavaScript安全检查通过"
    fi
}

# 主函数
main() {
    log_info "开始代码质量检查..."
    
    check_commit_message
    check_code_style
    run_tests
    check_security
    
    log_success "所有检查通过！"
}

main "$@"