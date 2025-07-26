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