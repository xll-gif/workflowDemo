# 环境变量配置指南

## 概述

本文档描述前端自动化工作流所需的所有环境变量配置，包括 GitHub、MasterGo、对象存储等集成服务。

## 环境变量列表

### 1. GitHub

| 变量名 | 必填 | 说明 | 示例 |
|-------|------|------|------|
| `GITHUB_TOKEN` | 是 | GitHub Personal Access Token | `ghp_xxxxxxxxxxxx` |
| `GITHUB_REPO_OWNER` | 否 | 默认仓库所有者 | `xll-gif` |
| `GITHUB_REPO_NAME` | 否 | 默认仓库名称 | `h5-demo` |
| `GITHUB_DEFAULT_BRANCH` | 否 | 默认分支名 | `main` |

### 2. MasterGo（新）

| 变量名 | 必填 | 说明 | 示例 |
|-------|------|------|------|
| `MASTERGO_TOKEN` | 是 | MasterGo API Token | `your_mastergo_token_here` |
| `MASTERGO_BASE_URL` | 否 | MasterGo API 基础 URL | `https://api.mastergo.com/openapi` |

### 3. Figma（已弃用）

| 变量名 | 必填 | 说明 | 示例 |
|-------|------|------|------|
| `FIGMA_TOKEN` | 否 | Figma API Token（已弃用） | `figd_xxxxxxxxxxxx` |
| `FIGMA_BASE_URL` | 否 | Figma API 基础 URL（已弃用） | `https://api.figma.com/v1` |

### 4. 对象存储 (CDN)

| 变量名 | 必填 | 说明 | 示例 |
|-------|------|------|------|
| `COZE_BUCKET_ENDPOINT_URL` | 是 | 对象存储终端 URL | `https://s3.cn-beijing.amazonaws.com.cn` |
| `COZE_BUCKET_NAME` | 是 | 存储桶名称 | `my-bucket` |
| `COZE_BUCKET_REGION` | 否 | 存储桶区域 | `cn-beijing` |

### 5. 大语言模型

| 变量名 | 必填 | 说明 | 示例 |
|-------|------|------|------|
| `OPENAI_API_KEY` | 否 | OpenAI API Key | `sk-xxxxxxxxxxxxxxxx` |
| `OPENAI_BASE_URL` | 否 | OpenAI API 基础 URL | `https://api.openai.com/v1` |

## 配置方式

### 方式 1：.env 文件（推荐）

在项目根目录创建 `.env` 文件：

```bash
# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_REPO_OWNER=xll-gif
GITHUB_REPO_NAME=h5-demo
GITHUB_DEFAULT_BRANCH=main

# MasterGo（新）
MASTERGO_TOKEN=your_mastergo_token_here
MASTERGO_BASE_URL=https://api.mastergo.com/openapi

# Figma（已弃用，可以删除）
# FIGMA_TOKEN=figd_xxxxxxxxxxxx
# FIGMA_BASE_URL=https://api.figma.com/v1

# 对象存储
COZE_BUCKET_ENDPOINT_URL=https://s3.cn-beijing.amazonaws.com.cn
COZE_BUCKET_NAME=my-bucket
COZE_BUCKET_REGION=cn-beijing

# 大语言模型
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
```

**重要**：
- `.env` 文件包含敏感信息，**不要**提交到代码仓库
- 将 `.env` 添加到 `.gitignore`：
  ```bash
  echo ".env" >> .gitignore
  ```

### 方式 2：Shell 环境变量

在终端中设置：

```bash
# Linux / macOS
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
export MASTERGO_TOKEN=your_mastergo_token_here
export COZE_BUCKET_ENDPOINT_URL=https://s3.cn-beijing.amazonaws.com.cn
export COZE_BUCKET_NAME=my-bucket
export COZE_BUCKET_REGION=cn-beijing
```

**注意**：
- 环境变量只在当前会话有效
- 关闭终端后需要重新设置

### 方式 3：Python 代码中设置

```python
import os

os.environ["GITHUB_TOKEN"] = "ghp_xxxxxxxxxxxx"
os.environ["MASTERGO_TOKEN"] = "your_mastergo_token_here"
os.environ["COZE_BUCKET_ENDPOINT_URL"] = "https://s3.cn-beijing.amazonaws.com.cn"
os.environ["COZE_BUCKET_NAME"] = "my-bucket"
os.environ["COZE_BUCKET_REGION"] = "cn-beijing"
```

### 方式 4：docker-compose.yml

如果使用 Docker 部署：

```yaml
version: '3.8'

services:
  workflow:
    environment:
      - GITHUB_TOKEN=ghp_xxxxxxxxxxxx
      - MASTERGO_TOKEN=your_mastergo_token_here
      - COZE_BUCKET_ENDPOINT_URL=https://s3.cn-beijing.amazonaws.com.cn
      - COZE_BUCKET_NAME=my-bucket
      - COZE_BUCKET_REGION=cn-beijing
```

## 获取 Token

### GitHub Token

1. 登录 GitHub
2. 进入 Settings → Developer settings → Personal access tokens → Tokens (classic)
3. 点击 "Generate new token (classic)"
4. 选择权限：
   - `repo` - 完整仓库访问权限
   - `workflow` - GitHub Actions 访问权限
5. 复制生成的 Token（格式：`ghp_xxxxxxxxxxxx`）

### MasterGo Token

1. 登录 MasterGo (https://mastergo.com)
2. 进入个人设置
3. 选择 "API Tokens" 或 "个人访问令牌"
4. 点击 "Create new token"
5. 复制生成的 Token

### 对象存储配置

根据使用的对象存储服务（如 AWS S3、阿里云 OSS、腾讯云 COS）配置相应的端点 URL 和访问凭证。

## 迁移指南：从 Figma 到 MasterGo

### 1. 更新 .env 文件

```bash
# 删除 Figma 配置
# FIGMA_TOKEN=figd_xxxxxxxxxxxx
# FIGMA_BASE_URL=https://api.figma.com/v1

# 添加 MasterGo 配置
MASTERGO_TOKEN=your_mastergo_token_here
MASTERGO_BASE_URL=https://api.mastergo.com/openapi
```

### 2. 更新配置文件

将 `config/figma_config.json` 替换为 `config/mastergo_config.json`

### 3. 清理旧 Token（可选）

```bash
unset FIGMA_TOKEN
unset FIGMA_BASE_URL
```

## 验证配置

### 验证 GitHub Token

```python
from tools.github_api import GitHubAPI

api = GitHubAPI()
user_info = api.get_user_info()
print(f"GitHub 用户: {user_info['login']}")
```

### 验证 MasterGo Token

```python
from src.tools.mastergo_api import MasterGoAPI

api = MasterGoAPI()
# 尝试解析一个公开的设计稿 URL
file_id, node_id = api.parse_mastergo_url("https://mastergo.com/design/7120216615013610")
print(f"File ID: {file_id}")
```

### 验证对象存储

```python
from coze_coding_dev_sdk.s3 import S3SyncStorage

storage = S3SyncStorage(
    endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
    access_key="",
    secret_key="",
    bucket_name=os.getenv("COZE_BUCKET_NAME"),
    region=os.getenv("COZE_BUCKET_REGION"),
)

# 列出存储桶中的文件
objects = storage.list_objects(prefix="mastergo/")
print(f"文件数量: {len(objects)}")
```

## 故障排查

### 问题 1：环境变量未生效

**症状**：
```
Error: Environment variable not found
```

**解决方案**：
1. 确认 `.env` 文件存在
2. 确认 `.env` 文件不在 `.gitignore` 中（如果需要提交）
3. 使用 `python-dotenv` 加载 `.env`：
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### 问题 2：Token 无效

**症状**：
```
Error: 401 Unauthorized
```

**解决方案**：
1. 检查 Token 是否正确
2. 检查 Token 是否已过期
3. 重新生成 Token

### 问题 3：权限不足

**症状**：
```
Error: 403 Forbidden
```

**解决方案**：
1. 检查 Token 权限配置
2. 确认有访问指定资源的权限
3. 联系管理员授权

## 安全最佳实践

1. **不要提交敏感信息**
   - 将 `.env` 添加到 `.gitignore`
   - 不要在代码中硬编码 Token
   - 不要在 GitHub Issue 或 PR 中暴露 Token

2. **定期轮换 Token**
   - 每 90 天更换一次 Token
   - 记录 Token 更换日期
   - 及时更新部署环境

3. **使用最小权限原则**
   - Token 只授予必要的权限
   - 避免使用 `admin` 或 `full` 权限
   - 为不同环境使用不同的 Token

4. **监控 Token 使用**
   - 定期检查 Token 使用记录
   - 发现异常立即撤销 Token
   - 启用 Token 使用通知

## 相关文档

- [GitHub 账号设置指南](./GITHUB_ACCOUNT_SETUP_GUIDE.md)
- [MasterGo 集成指南](./MASTERGO_INTEGRATION_GUIDE.md)
- [GitHub 仓库连接流程](./GITHUB_REPO_CONNECTION_FLOW.md)
