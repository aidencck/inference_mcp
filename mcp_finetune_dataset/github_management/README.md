# GitHub 管理工具集

这个目录包含了完整的GitHub仓库管理工具集，用于统一管理开发中的仓库。

## 📁 目录结构

```
github_management/
├── README.md                           # 本文件，工具集总览
├── GitHub脚本管理工具README.md          # 详细的项目介绍和使用说明
├── scripts/                            # 核心脚本工具
│   ├── github_manager.sh               # 统一管理入口脚本
│   ├── init_repo.sh                    # 仓库初始化脚本
│   ├── quick_commit.sh                 # 快速提交脚本
│   ├── branch_manager.sh               # 分支管理脚本
│   ├── release_manager.sh              # 发布管理脚本
│   └── code_check.sh                   # 代码质量检查脚本
├── docs/                               # 文档资料
│   ├── GitHub脚本管理文档.md            # 详细功能说明和配置指南
│   └── 快速使用指南.md                  # 快速上手指南
├── workflows/                          # GitHub Actions工作流
│   └── ci.yml                          # CI/CD自动化工作流
└── config/                             # 配置文件
    └── .pre-commit-config.yaml         # 预提交钩子配置
```

## 🚀 快速开始

### 1. 设置权限
```bash
chmod +x github_management/scripts/*.sh
```

### 2. 查看帮助
```bash
./github_management/scripts/github_manager.sh help
```

### 3. 初始化项目
```bash
./github_management/scripts/github_manager.sh init my-project "项目描述"
```

## 📋 主要功能

- **🏗️ 仓库管理** - 自动初始化、配置远程仓库、状态查看
- **🌿 分支管理** - 完整的分支操作，支持Git Flow工作流
- **📝 提交管理** - 规范化提交信息，快速提交和推送
- **🏷️ 版本发布** - 语义化版本控制，自动生成变更日志
- **🔍 代码质量** - 集成多种代码检查工具，确保代码质量
- **⚙️ 自动化工作流** - GitHub Actions和预提交钩子，全面自动化

## 📖 文档说明

- **GitHub脚本管理工具README.md** - 项目总览和完整使用说明
- **docs/GitHub脚本管理文档.md** - 详细的功能说明、配置指南和最佳实践
- **docs/快速使用指南.md** - 快速上手指南，包含常用操作和故障排除

## 🔧 配置文件说明

- **config/.pre-commit-config.yaml** - 预提交钩子配置，需要复制到项目根目录使用
- **workflows/ci.yml** - GitHub Actions工作流，需要复制到`.github/workflows/`目录使用

## 💡 使用建议

1. **首次使用** - 先阅读`docs/快速使用指南.md`
2. **详细配置** - 参考`docs/GitHub脚本管理文档.md`
3. **团队协作** - 根据团队需求定制化配置
4. **持续改进** - 根据使用反馈优化工具和流程

## 🎯 适用场景

- ✅ 个人项目管理
- ✅ 团队协作开发
- ✅ 开源项目维护
- ✅ 企业级代码仓库管理
- ✅ CI/CD流水线集成

---

更多详细信息请查看相关文档文件。