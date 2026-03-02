# 工作流快速开始指南

## 概述

本指南帮助你快速开始使用前端自动化工作流。

## 前置条件

1. ✅ GitHub 仓库已创建（workflowDemo）
2. ✅ React 项目已初始化
3. ✅ GitHub Token 已配置
4. ✅ Figma Token 已配置（如需使用设计稿解析功能）

## 快速开始

### 步骤 1：配置 Figma（新增）

**方式 A：使用快速配置脚本（最简单）**
```bash
bash setup_figma_config.sh
```
输入你的 Figma Token，脚本会自动创建配置文件。

**方式 B：手动配置文件**
```bash
# 1. 创建配置文件
vim config/figma_config.json

# 2. 填入 Token
{
  "token": "figd_your_token_here"
}
```

**方式 C：使用环境变量**
```bash
export FIGMA_TOKEN=figd_your_token_here
```

**验证配置：**
```bash
python3 check_figma_config.py
```

### 步骤 2：创建 Figma 设计稿（可选）

如果你有设计稿，工作流可以解析设计稿并生成更准确的代码。

#### 2.1 使用 Figma AI 快速创建（推荐新手）

**在 Figma 中使用 AI：**
1. 访问 https://www.figma.com 并登录
2. 创建新文件，按下 `/` 键
3. 输入以下提示词：
```
Create a simple mobile login page with:
- A centered title "Welcome Back" at y=100
- An email input field with placeholder "Enter your email" at y=200
- A password input field with placeholder "Enter your password" at y=264
- A blue login button (#007AFF) at y=340
- Clean and modern design
- iPhone 11 size (375x812)
```
4. 等待 Figma AI 生成设计稿
5. 复制 Figma URL

**详细指南：** 查看 `FIGMA_QUICK_START.md`（5分钟快速入门）或 `FIGMA_DESIGN_GUIDE.md`（完整指南）

#### 2.2 验证你的设计

运行验证脚本检查设计是否符合规范：

```bash
python3 validate_design.py
```

输入你的 Figma URL，查看验证报告和改进建议。

#### 2.3 测试设计稿解析

```bash
python3 test_figma_quick.py
# 选择 2 - 完整测试
# 输入你的 Figma URL
```

### 步骤 3：创建一个需求 Issue

有三种方式创建需求：

#### 方式 A：使用自动化脚本（推荐）

创建一个示例需求（用户登录功能）：

```bash
cd /workspace/projects
python3 create_workflow_issue.py
```

#### 方式 B：交互式创建

根据提示输入需求信息：

```bash
python3 create_issue_interactive.py
```

#### 方式 C：手动在 GitHub 创建

1. 访问: https://github.com/xll-gif/workflowDemo/issues/new
2. 按照需求格式填写内容
3. **如果有 Figma 设计稿，添加 Figma URL**
4. 点击 "Submit new issue"

**需求格式示例（包含 Figma URL）：**

```markdown
## 需求描述

开发一个用户登录功能...

## 功能列表

1. 实现登录页面 UI
2. 实现表单验证功能
3. 实现登录接口调用

## API 定义

API: POST /api/auth/login
说明: 用户登录接口

## Figma 设计稿
Figma URL: https://www.figma.com/file/YOUR_FILE_KEY/Login-Design
```

**注意：** 添加 Figma URL 后，工作流会自动解析设计稿，提取 UI 组件和布局信息，生成更准确的代码。

### 步骤 2：测试需求分析

测试工作流是否能正确解析你的需求：

```bash
python3 test_requirement_analysis.py
```

输入 Issue URL，例如：
```
https://github.com/xll-gif/workflowDemo/issues/1
```

查看输出，确认功能列表和 API 定义是否正确提取。

### 步骤 3：查看工作流能力

了解当前工作流支持的功能：

```bash
python3 show_capabilities.sh
```

或查看能力文档：

```bash
cat CURRENT_CAPABILITIES.md
```

### 步骤 4：（TODO）运行完整工作流

```bash
# TODO: 实现主工作流运行脚本
```

## 示例需求

我们已经为你创建了一个示例需求：

- **Issue #1**: [实现用户登录功能](https://github.com/xll-gif/workflowDemo/issues/1)
  - 功能列表: 8 项
  - API 定义: 4 个

你可以基于这个 Issue 测试工作流。

## 工作流处理流程

```
GitHub Issue
    ↓
需求分析（提取功能列表、API 定义）
    ↓
设计稿解析（提取 UI 组件、布局、资源）← 新增
    ↓
代码库分析（分析现有代码结构）
    ↓
代码生成（生成前端代码）
    ↓
代码推送（推送到 GitHub，可选创建 PR）
```

## Figma 集成测试（新功能）

### 步骤 1：获取 Figma Token

1. 登录 [Figma](https://www.figma.com/)
2. 进入 Settings → Personal Access Tokens
3. 创建新 Token，复制保存

### 步骤 2：配置 Token

```bash
export FIGMA_TOKEN=your_figma_token_here
```

### 步骤 3：运行测试

**方式 1：一键启动（推荐）**
```bash
bash test_figma.sh
```

**方式 2：快速测试（不需要设计稿）**
```bash
python3 test_figma_quick.py
# 选择 1 - 快速测试
```

**方式 3：完整测试（需要设计稿）**
```bash
python3 test_figma_quick.py
# 选择 2 - 完整测试
# 输入 Figma URL 和页面名称
```

**方式 4：详细功能测试**
```bash
python3 test_figma_api.py
# 选择测试项目
```

### 步骤 4：查看测试结果

测试会显示：
- ✅ 组件数量和类型
- ✅ 布局信息
- ✅ 静态资源列表
- ✅ 设计稿摘要

### 详细文档

- 📖 [Figma 集成指南](FIGMA_INTEGRATION_GUIDE.md) - 完整的集成文档
- 📖 [Figma 测试指南](FIGMA_TESTING_GUIDE.md) - 详细的测试步骤
- 📖 [Figma 测试检查清单](FIGMA_TEST_CHECKLIST.md) - 测试检查清单

## 常用命令

### GitHub 相关

```bash
# 测试 GitHub 连接
python3 test_github_connection.py

# 测试 GitHub API
python3 test_github_api_guide.py

# 查看仓库信息
python3 test_github_repo.py
```

### 需求管理

```bash
# 创建示例需求
python3 create_workflow_issue.py

# 交互式创建需求
python3 create_issue_interactive.py

# 测试需求分析
python3 test_requirement_analysis.py
```

### Figma 集成

```bash
# Figma 快速测试
python3 test_figma_quick.py

# Figma 详细测试
python3 test_figma_api.py

# 一键启动测试
bash test_figma.sh
```

### 项目管理

```bash
# 初始化 React 项目
python3 init_react_vite.py

# 连接用户仓库
python3 connect_user_repo.py

# 运行 GitHub 连接设置
bash setup_github_connection.sh
```

## 文档导航

| 文档 | 描述 |
|-----|------|
| [需求创建指南](REQUIREMENT_CREATE_GUIDE.md) | 如何创建符合格式的要求 |
| [GitHub 仓库使用指南](GITHUB_REPO_USAGE.md) | GitHub 集成使用说明 |
| [代码推送指南](GITHUB_CODE_PUSH_GUIDE.md) | 如何推送代码到 GitHub |
| [工作流能力清单](CURRENT_CAPABILITIES.md) | 当前支持的功能 |
| [AGENTS.md](AGENTS.md) | 工作流节点清单 |

## 常见问题

### Q: 如何创建一个新的需求？

A: 使用以下任一方式：
1. 运行 `python3 create_workflow_issue.py` 创建示例需求
2. 运行 `python3 create_issue_interactive.py` 交互式创建
3. 直接在 GitHub 上手动创建

### Q: 需求格式有什么要求？

A: 需求必须包含三个部分：
1. **需求描述**: 简要描述需求背景
2. **功能列表**: 编号列表，每项一个具体功能
3. **API 定义**: 格式为 `API: 方法 URL 说明`

详见 [需求创建指南](REQUIREMENT_CREATE_GUIDE.md)

### Q: 如何测试工作流？

A:
1. 创建一个需求 Issue
2. 运行 `python3 test_requirement_analysis.py` 测试需求解析
3. 查看输出确认解析结果

### Q: 工作流支持哪些功能？

A: 查看 [工作流能力清单](CURRENT_CAPABILITIES.md) 或运行 `python3 show_capabilities.sh`

### Q: 如何配置 GitHub Token？

A: 查看 [GitHub 账号设置指南](GITHUB_ACCOUNT_SETUP_GUIDE.md)

## 下一步

1. 创建一个需求 Issue
2. 测试需求分析功能
3. 查看 AGENTS.md 了解工作流结构
4. 探索源码，理解工作流实现

## 获取帮助

如果遇到问题：
1. 查看本文档和相关指南
2. 运行 `python3 show_capabilities.sh` 查看当前状态
3. 查看日志: `/app/work/logs/bypass/app.log`
