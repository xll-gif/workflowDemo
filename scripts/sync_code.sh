#!/bin/bash

# 快速同步代码脚本
# 使用方法: bash scripts/sync_code.sh

set -e  # 遇到错误立即退出

echo "=========================================="
echo "🔄 代码同步脚本"
echo "=========================================="
echo ""

# 1. 检查是否在 Git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ 错误：当前目录不是 Git 仓库"
    exit 1
fi

echo "✅ 当前在 Git 仓库中"

# 2. 查看当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 当前分支: $CURRENT_BRANCH"
echo ""

# 3. 查看未提交的修改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  警告：检测到未提交的修改"
    echo ""
    git status --short
    echo ""
    read -p "是否先暂存这些修改？(y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "💾 暂存修改中..."
        git stash push -m "同步前的临时暂存 $(date)"
        echo "✅ 修改已暂存"
        echo ""
    else
        echo "❌ 取消同步"
        exit 1
    fi
fi

# 4. 获取远程更新
echo "📥 获取远程更新..."
git fetch origin

# 5. 检查是否有更新
if [ $(git rev-list HEAD..origin/$CURRENT_BRANCH --count) -eq 0 ]; then
    echo "✅ 已经是最新版本，无需更新"
    echo ""
    # 恢复暂存
    if [ -n "$(git stash list)" ]; then
        echo "📤 恢复暂存的修改..."
        git stash pop
        echo "✅ 修改已恢复"
    fi
    exit 0
fi

# 6. 显示更新内容
echo ""
echo "📋 更新内容预览："
echo ""
git log HEAD..origin/$CURRENT_BRANCH --oneline
echo ""

# 7. 确认是否更新
read -p "是否确认更新到最新版本？(y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 取消更新"
    # 恢复暂存
    if [ -n "$(git stash list)" ]; then
        echo "📤 恢复暂存的修改..."
        git stash pop
        echo "✅ 修改已恢复"
    fi
    exit 0
fi

# 8. 执行合并
echo "🔄 正在合并更新..."
git merge origin/$CURRENT_BRANCH

# 9. 检查是否有冲突
if [ -n "$(git status --porcelain | grep '^UU')" ]; then
    echo ""
    echo "❌ 检测到合并冲突！"
    echo ""
    echo "请手动解决冲突后，运行以下命令："
    echo "  git add <冲突文件>"
    echo "  git commit -m '解决合并冲突'"
    echo ""
    exit 1
fi

echo "✅ 更新成功！"

# 10. 恢复暂存
if [ -n "$(git stash list)" ]; then
    echo ""
    echo "📤 恢复暂存的修改..."
    git stash pop
    if [ $? -eq 0 ]; then
        echo "✅ 修改已恢复"
    else
        echo "⚠️  恢复修改时遇到冲突，请手动解决"
    fi
fi

echo ""
echo "=========================================="
echo "✨ 同步完成！"
echo "=========================================="
echo ""
echo "当前版本:"
git log --oneline -1
echo ""
