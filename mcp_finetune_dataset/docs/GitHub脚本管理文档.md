# GitHub 脚本管理文档

## 概述

本文档提供了一套完整的GitHub仓库管理脚本和工作流程，帮助开发团队统一管理代码仓库，提高开发效率。

## 目录

- [快速开始](#快速开始)
- [脚本工具](#脚本工具)
- [分支管理](#分支管理)
- [发布流程](#发布流程)
- [代码质量](#代码质量)
- [自动化工作流](#自动化工作流)
- [常见问题](#常见问题)

## 快速开始

### 1. 环境准备

```bash
# 安装Git
sudo apt-get install git

# 配置Git用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 配置SSH密钥
ssh-keygen -t rsa -b 4096 -C "your.email@example.com"
cat ~/.ssh/id_rsa.pub  # 复制到GitHub SSH Keys

# 安装GitHub CLI（可选）
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

### 2. 仓库初始化脚本

创建 `scripts/init_repo.sh`：

```bash
#!/bin/bash

# GitHub仓库初始化脚本
# 用法: ./init_repo.sh <repo_name> [description]

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

# 检查参数
if [ $# -lt 1 ]; then
    log_error "用法: $0 <repo_name> [description]"
    exit 1
fi

REPO_NAME=$1
DESCRIPTION=${2:-"A new repository"}

log_info "初始化仓库: $REPO_NAME"

# 创建本地仓库
if [ ! -d "$REPO_NAME" ]; then
    mkdir "$REPO_NAME"
fi

cd "$REPO_NAME"

# 初始化Git仓库
if [ ! -d ".git" ]; then
    git init
    log_success "Git仓库初始化完成"
fi

# 创建基础文件
if [ ! -f "README.md" ]; then
    cat > README.md << EOF
# $REPO_NAME

$DESCRIPTION

## 安装

\`\`\`bash
git clone https://github.com/username/$REPO_NAME.git
cd $REPO_NAME
\`\`\`

## 使用

TODO: 添加使用说明

## 贡献

1. Fork 项目
2. 创建功能分支 (\`git checkout -b feature/AmazingFeature\`)
3. 提交更改 (\`git commit -m 'Add some AmazingFeature'\`)
4. 推送到分支 (\`git push origin feature/AmazingFeature\`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情
EOF
    log_success "README.md 创建完成"
fi

if [ ! -f ".gitignore" ]; then
    cat > .gitignore << EOF
# 依赖
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 环境变量
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 系统文件
.DS_Store
Thumbs.db

# 日志
*.log
logs/

# 临时文件
*.tmp
*.temp
EOF
    log_success ".gitignore 创建完成"
fi

if [ ! -f "LICENSE" ]; then
    cat > LICENSE << EOF
MIT License

Copyright (c) $(date +%Y) Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
    log_success "LICENSE 创建完成"
fi

# 添加文件到Git
git add .
git commit -m "Initial commit: Add basic project structure"

log_success "本地仓库设置完成"
log_info "下一步: 在GitHub上创建仓库并推送代码"
log_info "命令: gh repo create $REPO_NAME --public --description \"$DESCRIPTION\""
log_info "推送: git remote add origin https://github.com/username/$REPO_NAME.git && git push -u origin main"
```

## 脚本工具

### 1. 快速提交脚本

创建 `scripts/quick_commit.sh`：

```bash
#!/bin/bash

# 快速提交脚本
# 用法: ./quick_commit.sh "commit message" [branch]

set -e

COMMIT_MSG=${1:-"Update: $(date '+%Y-%m-%d %H:%M:%S')"}
BRANCH=${2:-$(git branch --show-current)}

echo "🚀 快速提交到分支: $BRANCH"
echo "📝 提交信息: $COMMIT_MSG"

# 检查工作区状态
if [ -z "$(git status --porcelain)" ]; then
    echo "⚠️  没有需要提交的更改"
    exit 0
fi

# 显示更改
echo "📋 更改文件:"
git status --short

read -p "确认提交? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add .
    git commit -m "$COMMIT_MSG"
    
    read -p "是否推送到远程? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin "$BRANCH"
        echo "✅ 提交并推送完成"
    else
        echo "✅ 本地提交完成"
    fi
else
    echo "❌ 取消提交"
fi
```

### 2. 分支管理脚本

创建 `scripts/branch_manager.sh`：

```bash
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
```

### 3. 发布管理脚本

创建 `scripts/release_manager.sh`：

```bash
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
    echo "  $0 "" minor          # 自动增加minor版本"
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
```

## 分支管理

### 分支命名规范

```
主分支:
- main/master: 主分支，稳定版本
- develop: 开发分支，集成最新功能

功能分支:
- feature/功能名称: 新功能开发
- bugfix/问题描述: 问题修复
- hotfix/紧急修复: 紧急修复
- release/版本号: 发布准备

示例:
- feature/user-authentication
- bugfix/login-error
- hotfix/security-patch
- release/v1.2.0
```

### Git Flow 工作流

```bash
# 1. 开始新功能
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. 开发完成后
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# 3. 创建Pull Request
gh pr create --title "Add new feature" --body "Description of the feature"

# 4. 合并到develop
git checkout develop
git pull origin develop
git merge feature/new-feature
git push origin develop

# 5. 删除功能分支
git branch -d feature/new-feature
git push origin --delete feature/new-feature
```

## 发布流程

### 1. 语义化版本控制

```
版本格式: MAJOR.MINOR.PATCH

- MAJOR: 不兼容的API更改
- MINOR: 向后兼容的功能添加
- PATCH: 向后兼容的问题修复

示例:
- 1.0.0 -> 1.0.1 (patch)
- 1.0.1 -> 1.1.0 (minor)
- 1.1.0 -> 2.0.0 (major)
```

### 2. 发布检查清单

```markdown
## 发布前检查

- [ ] 所有测试通过
- [ ] 代码审查完成
- [ ] 文档更新
- [ ] 变更日志更新
- [ ] 版本号更新
- [ ] 依赖项检查
- [ ] 安全扫描通过

## 发布后检查

- [ ] 标签创建
- [ ] 发布说明发布
- [ ] 部署到生产环境
- [ ] 监控检查
- [ ] 用户通知
```

## 代码质量

### 1. 提交信息规范

```
格式: <type>(<scope>): <subject>

type类型:
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建过程或辅助工具的变动

示例:
- feat(auth): add user login functionality
- fix(api): resolve data validation issue
- docs(readme): update installation instructions
```

### 2. 代码检查脚本

创建 `scripts/code_check.sh`：

```bash
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
```

## 自动化工作流

### 1. GitHub Actions 配置

创建 `.github/workflows/ci.yml`：

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest flake8 safety
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest
      run: |
        pytest
    
    - name: Security check
      run: |
        safety check

  release:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0
    
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.run_number }}
        release_name: Release ${{ github.run_number }}
        draft: false
        prerelease: false
```

### 2. 预提交钩子

创建 `.pre-commit-config.yaml`：

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
  
  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/flake8
    rev: 5.0.4
    hooks:
      - id: flake8
```

安装预提交钩子：

```bash
pip install pre-commit
pre-commit install
```

## 常见问题

### 1. 合并冲突解决

```bash
# 1. 拉取最新代码
git fetch origin
git checkout main
git pull origin main

# 2. 合并或变基
git checkout feature-branch
git rebase main  # 或 git merge main

# 3. 解决冲突
# 编辑冲突文件，解决冲突标记
git add .
git rebase --continue  # 或 git commit

# 4. 推送更新
git push origin feature-branch --force-with-lease
```

### 2. 撤销操作

```bash
# 撤销最后一次提交（保留更改）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃更改）
git reset --hard HEAD~1

# 撤销特定文件的更改
git checkout -- filename

# 撤销已推送的提交
git revert <commit-hash>
git push origin branch-name
```

### 3. 清理仓库

```bash
# 清理未跟踪的文件
git clean -fd

# 清理远程分支引用
git remote prune origin

# 压缩Git历史
git gc --aggressive --prune=now

# 查看仓库大小
du -sh .git
```

## 最佳实践

### 1. 提交频率
- 小而频繁的提交
- 每个提交只做一件事
- 提交前确保代码可运行

### 2. 分支策略
- 使用功能分支开发
- 定期同步主分支
- 及时删除已合并的分支

### 3. 代码审查
- 所有代码都要经过审查
- 审查关注功能、性能、安全
- 提供建设性反馈

### 4. 文档维护
- 保持README更新
- 记录API变更
- 维护变更日志

## 工具推荐

### 1. 命令行工具
- [GitHub CLI](https://cli.github.com/): GitHub官方命令行工具
- [hub](https://hub.github.com/): GitHub命令行包装器
- [git-flow](https://github.com/nvie/gitflow): Git Flow工作流工具

### 2. GUI工具
- [GitKraken](https://www.gitkraken.com/): 跨平台Git GUI
- [SourceTree](https://www.sourcetreeapp.com/): Atlassian的Git GUI
- [GitHub Desktop](https://desktop.github.com/): GitHub官方桌面应用

### 3. 集成工具
- [Conventional Commits](https://www.conventionalcommits.org/): 提交信息规范
- [Semantic Release](https://semantic-release.gitbook.io/): 自动化发布
- [Dependabot](https://dependabot.com/): 依赖更新自动化

---

**注意**: 请根据项目实际情况调整脚本和工作流程。定期更新脚本以适应新的需求和最佳实践。