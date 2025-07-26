# 🚀 GitHub 脚本管理工具

一套完整的GitHub仓库管理脚本工具集，帮助开发团队统一管理代码仓库，提高开发效率和代码质量。

## ✨ 特性

- 🎯 **统一管理**: 一个命令行工具管理所有Git操作
- 🔄 **标准化工作流**: 支持Git Flow和GitHub Flow
- 📋 **代码质量**: 集成代码检查、测试和安全扫描
- 🏷️ **版本管理**: 自动化语义版本控制和发布流程
- 🔧 **预提交钩子**: 自动代码格式化和质量检查
- 📊 **CI/CD集成**: GitHub Actions自动化工作流
- 📚 **详细文档**: 完整的使用指南和最佳实践

## 📁 项目结构

```
.
├── scripts/                          # 核心脚本目录
│   ├── github_manager.sh             # 统一管理入口
│   ├── init_repo.sh                  # 仓库初始化
│   ├── quick_commit.sh               # 快速提交
│   ├── branch_manager.sh             # 分支管理
│   ├── release_manager.sh            # 发布管理
│   └── code_check.sh                 # 代码质量检查
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions工作流
├── docs/                             # 文档目录
│   ├── GitHub脚本管理文档.md          # 详细文档
│   └── 快速使用指南.md               # 快速上手指南
├── .pre-commit-config.yaml          # 预提交钩子配置
└── GitHub脚本管理工具README.md       # 本文件
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装Git（如果还没有）
sudo apt-get install git

# 配置Git用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 安装GitHub CLI（推荐）
sudo apt update
sudo apt install gh
gh auth login
```

### 2. 设置脚本权限

```bash
# 设置执行权限
chmod +x scripts/*.sh

# 或使用自动设置
./scripts/github_manager.sh setup
```

### 3. 开始使用

```bash
# 查看帮助信息
./scripts/github_manager.sh help

# 初始化新项目
./scripts/github_manager.sh init my-project "项目描述"

# 快速提交
./scripts/github_manager.sh commit "feat: add new feature"

# 创建发布版本
./scripts/github_manager.sh release patch
```

## 🛠️ 核心功能

### 仓库管理
- ✅ 自动初始化Git仓库
- ✅ 创建标准项目结构（README、LICENSE、.gitignore）
- ✅ 配置远程仓库
- ✅ 显示仓库状态和信息

### 分支管理
- ✅ 创建、切换、删除分支
- ✅ 合并分支和解决冲突
- ✅ 同步远程分支
- ✅ 清理已合并分支
- ✅ 可视化分支关系

### 提交管理
- ✅ 快速提交和推送
- ✅ 规范化提交信息
- ✅ 交互式确认
- ✅ 自动添加所有更改

### 版本发布
- ✅ 语义化版本控制
- ✅ 自动生成变更日志
- ✅ 创建Git标签
- ✅ GitHub发布集成
- ✅ 版本文件自动更新

### 代码质量
- ✅ 代码风格检查（flake8、black、isort）
- ✅ 类型检查（mypy）
- ✅ 安全扫描（bandit、safety）
- ✅ 测试运行（pytest）
- ✅ 提交信息格式检查

### 自动化工作流
- ✅ GitHub Actions CI/CD
- ✅ 预提交钩子
- ✅ 自动化测试和部署
- ✅ 代码覆盖率报告

## 📋 使用示例

### 日常开发工作流

```bash
# 1. 查看当前状态
./scripts/github_manager.sh status

# 2. 创建功能分支
./scripts/github_manager.sh branch create feature/user-auth

# 3. 开发完成后提交
./scripts/github_manager.sh commit "feat(auth): implement user authentication"

# 4. 推送到远程
./scripts/github_manager.sh push

# 5. 切换回主分支并合并
./scripts/github_manager.sh branch switch main
./scripts/github_manager.sh branch merge feature/user-auth

# 6. 清理分支
./scripts/github_manager.sh branch delete feature/user-auth
```

### 发布流程

```bash
# 1. 运行代码质量检查
./scripts/github_manager.sh check

# 2. 创建发布版本
./scripts/github_manager.sh release minor

# 3. 推送标签和更改
git push origin main --tags
```

### 团队协作

```bash
# 1. 同步远程分支
./scripts/github_manager.sh branch sync

# 2. 清理已合并分支
./scripts/github_manager.sh branch clean

# 3. 备份当前状态
./scripts/github_manager.sh backup
```

## 🔧 配置选项

### 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

类型:
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建/工具
```

### 分支命名规范

```
- feature/功能名称: 新功能开发
- bugfix/问题描述: 问题修复
- hotfix/紧急修复: 紧急修复
- release/版本号: 发布准备
```

### 预提交钩子

```bash
# 安装预提交钩子
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg

# 手动运行检查
pre-commit run --all-files
```

## 📊 GitHub Actions

自动化工作流包括：

- 🔍 **代码质量检查**: flake8、black、isort、mypy
- 🛡️ **安全扫描**: bandit、safety
- 🧪 **测试运行**: pytest（多Python版本）
- 📦 **构建检查**: 包构建和验证
- 🐳 **Docker构建**: 容器镜像构建
- 🚀 **自动发布**: 标签创建和GitHub发布
- 📢 **通知**: 成功/失败通知

## 📚 文档

- 📖 [详细文档](docs/GitHub脚本管理文档.md) - 完整的功能说明和配置指南
- 🚀 [快速使用指南](docs/快速使用指南.md) - 快速上手和常用操作
- 🔧 [API使用指南](docs/API使用指南.md) - FastAPI服务使用说明

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`./scripts/github_manager.sh branch create feature/amazing-feature`)
3. 提交更改 (`./scripts/github_manager.sh commit "feat: add amazing feature"`)
4. 推送到分支 (`./scripts/github_manager.sh push`)
5. 创建 Pull Request

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/username/repo.git
cd repo

# 设置开发环境
./scripts/github_manager.sh setup

# 安装预提交钩子
pip install pre-commit
pre-commit install

# 运行测试
./scripts/github_manager.sh test
```

## 🐛 故障排除

### 常见问题

1. **权限错误**
   ```bash
   chmod +x scripts/*.sh
   ```

2. **Git配置问题**
   ```bash
   ./scripts/github_manager.sh setup
   ```

3. **预提交钩子失败**
   ```bash
   pre-commit run --all-files
   ```

4. **合并冲突**
   ```bash
   # 查看冲突文件
   git status
   # 手动解决冲突后
   git add .
   git commit
   ```

### 获取帮助

- 📖 查看文档: `docs/` 目录
- 💬 运行帮助: `./scripts/github_manager.sh help`
- 🐛 报告问题: 创建GitHub Issue
- 💡 功能建议: 创建Feature Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目的启发和支持：

- [Git](https://git-scm.com/) - 版本控制系统
- [GitHub CLI](https://cli.github.com/) - GitHub命令行工具
- [pre-commit](https://pre-commit.com/) - Git钩子框架
- [Conventional Commits](https://www.conventionalcommits.org/) - 提交信息规范
- [Semantic Versioning](https://semver.org/) - 语义化版本控制

## 📈 项目状态

![GitHub last commit](https://img.shields.io/github/last-commit/username/repo)
![GitHub issues](https://img.shields.io/github/issues/username/repo)
![GitHub pull requests](https://img.shields.io/github/issues-pr/username/repo)
![GitHub](https://img.shields.io/github/license/username/repo)

---

**🎯 目标**: 让GitHub仓库管理变得简单、高效、标准化！

**💡 理念**: 通过自动化和标准化，让开发者专注于代码本身，而不是繁琐的仓库管理工作。