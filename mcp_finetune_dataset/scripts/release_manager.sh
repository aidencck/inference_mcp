#!/bin/bash

# 发布管理脚本
# 用法: ./release_manager.sh [version] [type]

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

# 获取当前版本
get_current_version() {
    if [ -f "package.json" ]; then
        grep '"version"' package.json | sed 's/.*"version": "\(.*\)".*/\1/'
    elif [ -f "setup.py" ]; then
        grep 'version=' setup.py | sed "s/.*version='\(.*\)'.*/\1/"
    elif git tag --list | tail -1; then
        git tag --list | tail -1 | sed 's/v//'
    else
        echo "0.0.0"
    fi
}

# 增加版本号
bump_version() {
    local current_version=$1
    local bump_type=$2
    
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    local major=${VERSION_PARTS[0]}
    local minor=${VERSION_PARTS[1]}
    local patch=${VERSION_PARTS[2]}
    
    case $bump_type in
        "major")
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        "minor")
            minor=$((minor + 1))
            patch=0
            ;;
        "patch")
            patch=$((patch + 1))
            ;;
        *)
            log_error "未知的版本类型: $bump_type"
            exit 1
            ;;
    esac
    
    echo "$major.$minor.$patch"
}

# 更新版本文件
update_version_files() {
    local new_version=$1
    
    if [ -f "package.json" ]; then
        sed -i "s/\"version\": \".*\"/\"version\": \"$new_version\"/" package.json
        log_info "已更新 package.json"
    fi
    
    if [ -f "setup.py" ]; then
        sed -i "s/version='.*'/version='$new_version'/" setup.py
        log_info "已更新 setup.py"
    fi
    
    if [ -f "pyproject.toml" ]; then
        sed -i "s/version = \".*\"/version = \"$new_version\"/" pyproject.toml
        log_info "已更新 pyproject.toml"
    fi
}

# 生成变更日志
generate_changelog() {
    local version=$1
    local previous_tag=$(git tag --list | tail -1)
    
    log_info "生成变更日志..."
    
    if [ -z "$previous_tag" ]; then
        log_warning "没有找到之前的标签，生成完整日志"
        git log --pretty=format:'- %s (%h)' > CHANGELOG_TEMP.md
    else
        git log "$previous_tag"..HEAD --pretty=format:'- %s (%h)' > CHANGELOG_TEMP.md
    fi
    
    # 创建或更新CHANGELOG.md
    if [ -f "CHANGELOG.md" ]; then
        # 在现有文件前添加新内容
        {
            echo "# Changelog"
            echo
            echo "## [$version] - $(date +%Y-%m-%d)"
            echo
            cat CHANGELOG_TEMP.md
            echo
            tail -n +2 CHANGELOG.md
        } > CHANGELOG_NEW.md
        mv CHANGELOG_NEW.md CHANGELOG.md
    else
        # 创建新文件
        {
            echo "# Changelog"
            echo
            echo "## [$version] - $(date +%Y-%m-%d)"
            echo
            cat CHANGELOG_TEMP.md
        } > CHANGELOG.md
    fi
    
    rm CHANGELOG_TEMP.md
    log_success "变更日志已更新"
}

# 创建发布
create_release() {
    local version=$1
    local release_type=${2:-"patch"}
    
    # 检查工作区是否干净
    if [ -n "$(git status --porcelain)" ]; then
        log_error "工作区有未提交的更改，请先提交或暂存"
        exit 1
    fi
    
    # 确保在主分支
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
        log_warning "当前不在主分支，是否继续? (y/N)"
        read -p "" -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # 获取版本号
    if [ -z "$version" ]; then
        local current_version=$(get_current_version)
        version=$(bump_version "$current_version" "$release_type")
        log_info "自动生成版本号: $current_version -> $version"
    fi
    
    log_info "创建发布版本: $version"
    
    # 更新版本文件
    update_version_files "$version"
    
    # 生成变更日志
    generate_changelog "$version"
    
    # 提交更改
    git add .
    git commit -m "Release version $version"
    
    # 创建标签
    git tag -a "v$version" -m "Release version $version"
    
    log_success "发布 v$version 创建完成"
    
    # 推送到远程
    read -p "是否推送到远程仓库? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin "$current_branch"
        git push origin "v$version"
        log_success "已推送到远程仓库"
        
        # 使用GitHub CLI创建发布
        if command -v gh &> /dev/null; then
            read -p "是否在GitHub上创建发布? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                gh release create "v$version" --title "Release v$version" --notes-file CHANGELOG.md
                log_success "GitHub发布已创建"
            fi
        fi
    fi
}

# 显示帮助
show_help() {
    echo "发布管理脚本"
    echo
    echo "用法: $0 [version] [type]"
    echo
    echo "参数:"
    echo "  version              指定版本号 (可选)"
    echo "  type                 版本类型: major|minor|patch (默认: patch)"
    echo
    echo "示例:"
    echo "  $0                   # 自动增加patch版本"
    echo "  $0 1.2.3             # 指定版本号"
    echo "  $0 \"\" minor          # 自动增加minor版本"
    echo "  $0 2.0.0 major       # 指定版本号和类型"
}

# 主函数
main() {
    local version=$1
    local release_type=${2:-"patch"}
    
    if [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_help
        exit 0
    fi
    
    create_release "$version" "$release_type"
}

main "$@"