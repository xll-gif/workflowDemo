# Git 推送问题解决方案

## 问题描述

尝试推送工作流代码到远程时，GitHub 拒绝了推送，因为历史提交中包含了敏感信息（密钥）。

### 检测到的敏感信息

1. **Figma Personal Access Token**
   - 提交: 0d801fc, eb759a2, d132df2, 47738a3
   - 文件: config/figma_config.json

2. **GitHub Personal Access Token**
   - 提交: 1e6eafe
   - 文件: fix_issue_url.py
   - 提交: d132df2
   - 文件: WORKFLOW_COMPLETE_REPORT.md

## 解决方案

### 方案一：从 GitHub 允许这些密钥

访问以下链接，允许这些密钥：
- https://github.com/xll-gif/workflowDemo/security/secret-scanning/unblock-secret/3ANoYlC07nK3MI4853kryfQ47XL
- https://github.com/xll-gif/workflowDemo/security/secret-scanning/unblock-secret/3ANoYlmCfUl6afy6CzhWk7PkpS7
- https://github.com/xll-gif/workflowDemo/security/secret-scanning/unblock-secret/3ANoYnlKB8hXZc8SFWApi6MV4XK
- https://github.com/xll-gif/workflowDemo/security/secret-scanning/unblock-secret/3ANoYnRAQ42RylZKNcpfTsXgx5M
- https://github.com/xll-gif/workflowDemo/security/secret-scanning/unblock-secret/3ANoYpDPwzrxSNQrW2oBGi1xC2B

### 方案二：清理历史记录中的敏感信息（推荐）

使用 git filter-branch 或 git filter-repo 从历史记录中删除敏感信息。

```bash
# 创建备份分支
git branch backup-before-cleanup

# 删除包含敏感信息的文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config/figma_config.json fix_issue_url.py WORKFLOW_COMPLETE_REPORT.md" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送
git push origin main --force
```

### 方案三：创建新分支（最简单但会丢失历史）

```bash
# 创建一个全新的分支
git checkout --orphan new-main

# 添加所有文件
git add .

# 创建新的初始提交
git commit -m "Initial commit: Frontend Automation Workflow"

# 删除旧的 main 分支
git branch -D main

# 重命名新分支为 main
git branch -m main

# 强制推送
git push origin main --force
```

## 当前状态

- 本地 main 分支有 58 个提交
- 远程 main 分支有 1 个提交（被重置）
- 腾讯云 COS 集成代码已在本地完成并提交

## 建议操作

1. 先尝试方案一（从 GitHub 允许密钥）
2. 如果方案一不可行，使用方案二清理历史记录
3. 作为最后手段，使用方案三创建新分支

## 注意事项

- 强制推送会覆盖远程历史，请确保有备份
- 清理历史记录后，其他开发者需要重新克隆仓库
- 敏感信息应该使用环境变量或密钥管理系统，不应该提交到代码仓库
