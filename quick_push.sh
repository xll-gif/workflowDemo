#!/bin/bash

# 快速推送脚本 - 需要配置 GitHub Token

echo "========================================="
echo "🚀 推送到 GitHub"
echo "========================================="
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  警告：未检测到 GITHUB_TOKEN 环境变量"
    echo ""
    echo "请选择以下方式之一："
    echo ""
    echo "方式 1：设置环境变量后运行此脚本"
    echo "  export GITHUB_TOKEN=your_token_here"
    echo "  ./quick_push.sh"
    echo ""
    echo "方式 2：直接使用命令推送"
    echo "  git push -u origin master"
    echo "  (输入用户名和 token 作为密码)"
    echo ""
    echo "方式 3：使用 SSH"
    echo "  git remote set-url origin git@github.com:xll-gif/workflowDemo.git"
    echo "  git push -u origin master"
    echo ""
    echo "详细说明请查看: PUSH_GUIDE.md"
    exit 1
fi

echo "✅ 检测到 GitHub Token"
echo "📦 正在推送到 https://github.com/xll-gif/workflowDemo.git"
echo ""

# 使用 token 推送
git push -u origin master https://xll-gif:$GITHUB_TOKEN@github.com/xll-gif/workflowDemo.git

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 推送成功！"
    echo "🔗 访问: https://github.com/xll-gif/workflowDemo"
else
    echo ""
    echo "❌ 推送失败"
    echo "请检查 token 是否正确或网络连接"
    exit 1
fi
