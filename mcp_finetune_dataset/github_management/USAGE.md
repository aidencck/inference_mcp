# GitHub 管理工具使用说明

## 📍 当前位置

所有GitHub管理相关的脚本和文档已统一整理到 `github_management/` 目录下。

## 🚀 快速开始

### 1. 设置脚本权限

```bash
# 进入github_management目录
cd github_management

# 设置所有脚本的执行权限
chmod +x scripts/*.sh
```

### 2. 使用统一管理脚本

```bash
# 查看帮助信息
./scripts/github_manager.sh help

# 初始化新项目
./scripts/github_manager.sh init my-project "项目描述"

# 查看仓库状态
./scripts/github_manager.sh status

# 创建新分支
./scripts/github_manager.sh branch create feature/new-feature

# 快速提交
./scripts/github_manager.sh commit "feat: add new feature"

# 发布新版本
./scripts/github_manager.sh release patch
```

## 📁 目录结构说明

```
github_management/
├── scripts/                    # 核心脚本工具
│   ├── github_manager.sh       # 🎯 主入口脚本（推荐使用）
│   ├── init_repo.sh            # 仓库初始化
│   ├── quick_commit.sh         # 快速提交
│   ├── branch_manager.sh       # 分支管理
│   ├── release_manager.sh      # 发布管理
│   └── code_check.sh           # 代码检查
├── docs/                       # 📚 文档资料
│   ├── GitHub脚本管理文档.md    # 详细功能说明
│   └── 快速使用指南.md          # 快速上手指南
├── workflows/                  # ⚙️ GitHub Actions
│   └── ci.yml                  # CI/CD工作流
└── config/                     # 🔧 配置文件
    └── .pre-commit-config.yaml # 预提交钩子配置
```

## 🔧 配置文件部署

### GitHub Actions 工作流

```bash
# 创建.github/workflows目录（如果不存在）
mkdir -p .github/workflows

# 复制CI工作流文件
cp github_management/workflows/ci.yml .github/workflows/
```

### 预提交钩子配置

```bash
# 复制预提交配置到项目根目录
cp github_management/config/.pre-commit-config.yaml .

# 安装pre-commit（如果未安装）
pip install pre-commit

# 安装钩子
pre-commit install
```

## 💡 使用建议

### 推荐工作流程

1. **项目初始化**
   ```bash
   ./scripts/github_manager.sh init my-project "项目描述"
   ```

2. **日常开发**
   ```bash
   # 创建功能分支
   ./scripts/github_manager.sh branch create feature/new-feature
   
   # 开发完成后提交
   ./scripts/github_manager.sh commit "feat: implement new feature"
   
   # 合并到主分支
   ./scripts/github_manager.sh branch merge feature/new-feature
   ```

3. **版本发布**
   ```bash
   # 发布补丁版本
   ./scripts/github_manager.sh release patch
   
   # 发布次要版本
   ./scripts/github_manager.sh release minor
   
   # 发布主要版本
   ./scripts/github_manager.sh release major
   ```

4. **代码质量检查**
   ```bash
   # 运行完整检查
   ./scripts/github_manager.sh check
   
   # 只检查代码风格
   ./scripts/github_manager.sh lint
   
   # 只运行测试
   ./scripts/github_manager.sh test
   ```

### 团队协作建议

1. **统一使用路径**
   - 建议团队成员都使用相对路径调用脚本
   - 可以在项目根目录创建软链接方便使用

2. **配置文件同步**
   - 将 `github_management/config/` 下的配置文件复制到项目根目录
   - 确保团队成员使用相同的代码质量标准

3. **工作流标准化**
   - 使用 `github_management/workflows/ci.yml` 作为标准CI/CD流程
   - 根据项目需求适当调整工作流配置

## 🔗 便捷访问

### 创建软链接（可选）

```bash
# 在项目根目录创建软链接，方便直接调用
ln -s github_management/scripts/github_manager.sh gm

# 使用软链接
./gm help
./gm status
./gm commit "update feature"
```

### 添加到PATH（可选）

```bash
# 将脚本目录添加到PATH
export PATH="$PWD/github_management/scripts:$PATH"

# 直接使用脚本名
github_manager.sh help
```

## 📖 更多信息

- 📋 **详细功能说明**: `docs/GitHub脚本管理文档.md`
- 🚀 **快速上手指南**: `docs/快速使用指南.md`
- 📘 **项目总览**: `GitHub脚本管理工具README.md`

---

如有问题或建议，请查看相关文档或提交Issue。