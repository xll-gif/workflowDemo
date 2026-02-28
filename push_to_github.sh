#!/bin/bash

# H5 项目推送到 GitHub 的脚本

echo "========================================="
echo "H5 登录页面 - GitHub 推送脚本"
echo "========================================="
echo ""

# 检查是否提供了 GitHub 仓库 URL
if [ -z "$1" ]; then
    echo "❌ 错误：请提供 GitHub 仓库 URL"
    echo ""
    echo "使用方法："
    echo "  ./push_to_github.sh <your-github-repo-url>"
    echo ""
    echo "示例："
    echo "  ./push_to_github.sh https://github.com/username/h5-login-app.git"
    echo ""
    echo "或者先设置远程仓库："
    echo "  git remote add origin <your-github-repo-url>"
    echo "  git push -u origin master"
    exit 1
fi

GITHUB_REPO_URL=$1

echo "📦 正在推送到 GitHub..."
echo "仓库 URL: $GITHUB_REPO_URL"
echo ""

# 添加远程仓库
git remote add origin $GITHUB_REPO_URL 2>/dev/null || git remote set-url origin $GITHUB_REPO_URL

# 推送到 GitHub
git push -u origin master

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 推送成功！"
    echo ""
    echo "🔗 你可以在以下地址查看你的项目："
    echo "   $GITHUB_REPO_URL"
    echo ""
    echo "📝 后续步骤："
    echo "   1. 克隆或访问你的 GitHub 仓库"
    echo "   2. 使用 GitHub Pages 或 Vercel 部署应用"
    echo ""
else
    echo ""
    echo "❌ 推送失败！"
    echo ""
    echo "可能的原因："
    echo "   1. GitHub Token 未配置或无效"
    echo "   2. 仓库 URL 错误"
    echo "   3. 网络连接问题"
    echo ""
    echo "请检查后重试。"
    exit 1
fi
