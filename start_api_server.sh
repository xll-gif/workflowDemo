#!/bin/bash

# 腾讯云 COS 上传 API 服务快速启动脚本

set -e

echo "======================================================================"
echo "腾讯云 COS 上传 API 服务 - 快速启动"
echo "======================================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 版本
echo "1. 检查 Python 版本..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python 版本: $PYTHON_VERSION"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 未安装${NC}"
    echo "   请先安装 Python 3.9 或更高版本"
    exit 1
fi

echo -e "${GREEN}✅ Python 已安装${NC}"
echo ""

# 检查是否安装了依赖
echo "2. 检查依赖包..."
MISSING_DEPS=()

if ! python3 -c "import flask" 2>/dev/null; then
    MISSING_DEPS+=("Flask")
fi

if ! python3 -c "import flask_cors" 2>/dev/null; then
    MISSING_DEPS+=("flask-cors")
fi

if ! python3 -c "import dotenv" 2>/dev/null; then
    MISSING_DEPS+=("python-dotenv")
fi

if ! python3 -c "import tencentcloud" 2>/dev/null; then
    MISSING_DEPS+=("tencentcloud-sdk-python")
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo -e "${YELLOW}⚠️  缺少依赖包: ${MISSING_DEPS[*]}${NC}"
    echo "   正在安装依赖包..."

    if [ -f "requirements-api.txt" ]; then
        pip3 install -r requirements-api.txt
    else
        pip3 install Flask flask-cors python-dotenv tencentcloud-sdk-python
    fi

    echo -e "${GREEN}✅ 依赖包安装完成${NC}"
else
    echo -e "${GREEN}✅ 所有依赖包已安装${NC}"
fi

echo ""

# 检查配置文件
echo "3. 检查配置文件..."

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 文件不存在${NC}"
    echo "   正在创建 .env 文件..."

    if [ -f ".env.api.example" ]; then
        cp .env.api.example .env
        echo -e "${GREEN}✅ 已从 .env.api.example 创建 .env 文件${NC}"
    else
        cat > .env << EOF
# API 服务配置
PORT=5000
DEBUG=false
API_SECRET_KEY=

# 腾讯云 COS 配置
TENCENT_SECRET_ID=
TENCENT_SECRET_KEY=
TENCENT_BUCKET=
TENCENT_REGION=ap-shanghai
TENCENT_DURATION_SECONDS=900
TENCENT_ALLOW_PREFIX=frontend-automation/*
TENCENT_CUSDOMAIN=

# 工作流配置
STORAGE_BACKEND=cos
TENCENT_API_BASE_URL=http://localhost:5000
TENCENT_SCENE_NAME=frontend-automation
TENCENT_BUSINESS_NAME=workflow
TENCENT_MODE=dev
EOF
        echo -e "${GREEN}✅ 已创建 .env 文件${NC}"
    fi

    echo ""
    echo -e "${YELLOW}⚠️  请编辑 .env 文件，填入实际的腾讯云配置：${NC}"
    echo "   nano .env  # 或使用 vim / vscode"
    echo ""
    read -p "是否现在编辑 .env 文件？(y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        nano .env
    else
        echo -e "${RED}❌ 请先配置 .env 文件后再运行${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ 配置文件已就绪${NC}"
echo ""

# 验证必需配置
echo "4. 验证必需配置..."

source .env

REQUIRED_CONFIGS=(
    "TENCENT_SECRET_ID"
    "TENCENT_SECRET_KEY"
    "TENCENT_BUCKET"
)

MISSING_CONFIGS=()

for config in "${REQUIRED_CONFIGS[@]}"; do
    if [ -z "${!config}" ]; then
        MISSING_CONFIGS+=("$config")
    fi
done

if [ ${#MISSING_CONFIGS[@]} -ne 0 ]; then
    echo -e "${RED}❌ 缺少必需的配置: ${MISSING_CONFIGS[*]}${NC}"
    echo "   请编辑 .env 文件并填入上述配置"
    exit 1
fi

echo -e "${GREEN}✅ 所有必需配置已设置${NC}"
echo ""

# 显示配置摘要
echo "5. 配置摘要："
echo "   API 服务端口: $PORT"
echo "   COS 存储桶: $TENCENT_BUCKET"
echo "   COS 区域: $TENCENT_REGION"
echo "   凭证有效期: $TENCENT_DURATION_SECONDS 秒"
echo "   允许路径前缀: $TENCENT_ALLOW_PREFIX"
echo "   自定义域名: ${TENCENT_CUSDOMAIN:-N/A}"
echo ""

# 启动服务
echo "======================================================================"
echo "6. 启动 API 服务..."
echo "======================================================================"
echo ""

echo "服务将启动在: http://0.0.0.0:$PORT"
echo "健康检查: http://localhost:$PORT/health"
echo "获取凭证: POST http://localhost:$PORT/api/v1/upload-token"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动服务
python3 api_server.py
