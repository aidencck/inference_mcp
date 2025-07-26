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