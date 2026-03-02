# 腾讯云 COS 上传 API 服务部署指南

## 概述

本指南详细介绍如何部署和运行腾讯云 COS 上传 API 服务，该服务为前端工作流提供 STS 临时凭证，实现安全的文件上传功能。

## 📋 前置条件

### 1. 腾讯云账号

1. 访问 [腾讯云官网](https://cloud.tencent.com/)
2. 注册并登录账号
3. 开通 COS 服务

### 2. Python 环境

- Python 3.9 或更高版本
- pip 包管理器

### 3. 腾讯云 COS 配置

#### 创建存储桶（Bucket）

1. 进入 COS 控制台
2. 点击"创建存储桶"
3. 填写配置：
   - **名称**：例如 `frontend-automation-assets`
   - **所属地域**：选择合适的区域（如上海）
   - **访问权限**：私有读写（推荐）或 公共读
4. 点击确定

#### 获取访问密钥

1. 进入"访问管理" → "API密钥管理"
2. 点击"新建密钥"
3. 复制 SecretId 和 SecretKey（**请妥善保管，不要泄露**）

#### 创建子账号和角色（可选，推荐）

**方式一：使用主账号密钥（简单但不推荐）**

直接使用主账号的 SecretId 和 SecretKey

**方式二：使用子账号和 STS（推荐，更安全）**

1. 进入"访问管理" → "用户" → "新建用户"
2. 用户类型：子用户
3. 访问方式：编程访问
4. 创建后，复制 AccessKeyId 和 SecretKey

## 🚀 快速开始

### 1. 克隆或下载项目代码

```bash
cd /path/to/your/project
```

### 2. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements-api.txt

# 或手动安装
pip install Flask flask-cors python-dotenv tencentcloud-sdk-python
```

### 3. 配置环境变量

#### 方法一：使用 .env 文件（推荐）

```bash
# 复制配置模板
cp .env.api.example .env

# 编辑 .env 文件
nano .env  # 或使用 vim / vscode
```

#### 方法二：使用系统环境变量

```bash
export TENCENT_SECRET_ID=your_secret_id
export TENCENT_SECRET_KEY=your_secret_key
export TENCENT_BUCKET=your-bucket-name
export TENCENT_REGION=ap-shanghai
```

### 4. 配置说明

编辑 `.env` 文件，填入实际配置：

```bash
# ==================== API 服务配置 ====================
PORT=5000
DEBUG=false
API_SECRET_KEY=your-api-secret-key  # 可选，用于 API 安全验证

# ==================== 腾讯云 COS 配置 ====================
TENCENT_SECRET_ID=AKIDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TENCENT_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TENCENT_BUCKET=frontend-automation-assets
TENCENT_REGION=ap-shanghai
TENCENT_DURATION_SECONDS=900
TENCENT_ALLOW_PREFIX=frontend-automation/*
TENCENT_CUSDOMAIN=https://your-cdn-domain.com  # 可选

# ==================== 工作流配置（客户端） ====================
STORAGE_BACKEND=cos
TENCENT_API_BASE_URL=http://localhost:5000
TENCENT_SCENE_NAME=frontend-automation
TENCENT_BUSINESS_NAME=workflow
TENCENT_MODE=dev
```

**重要配置说明**：

- `TENCENT_SECRET_ID`: 腾讯云 SecretId
- `TENCENT_SECRET_KEY`: 腾讯云 SecretKey
- `TENCENT_BUCKET`: COS 存储桶名称
- `TENCENT_REGION`: COS 区域（如 ap-shanghai, ap-beijing）
- `TENCENT_DURATION_SECONDS`: STS 临时凭证有效期（秒），默认 900（15 分钟）
- `TENCENT_ALLOW_PREFIX`: 允许上传的路径前缀，支持通配符 `*`
- `TENCENT_CUSDOMAIN`: 自定义 CDN 域名（可选）
- `API_SECRET_KEY`: API 安全密钥（可选），如果设置了则客户端必须提供 `X-Secret-Key`

### 5. 启动服务

#### 开发环境

```bash
python api_server.py
```

#### 生产环境（使用 Gunicorn）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

#### 使用 systemd（Linux）

创建服务文件 `/etc/systemd/system/tencent-cos-api.service`：

```ini
[Unit]
Description=Tencent COS Upload API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/venv/bin"
ExecStart=/path/to/your/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start tencent-cos-api

# 设置开机自启
sudo systemctl enable tencent-cos-api

# 查看状态
sudo systemctl status tencent-cos-api

# 查看日志
sudo journalctl -u tencent-cos-api -f
```

### 6. 验证服务

#### 健康检查

```bash
curl http://localhost:5000/health
```

预期响应：

```json
{
  "status": "ok",
  "service": "tencent-cos-upload-api",
  "version": "1.0.0"
}
```

#### 测试获取上传凭证

```bash
curl -X POST http://localhost:5000/api/v1/upload-token \
  -H "Content-Type: application/json" \
  -H "X-Secret-Key: your-api-secret-key" \
  -d '{
    "mediaType": "image",
    "sceneName": "frontend-automation",
    "businessName": "workflow",
    "source": "test"
  }'
```

预期响应：

```json
{
  "code": 0,
  "data": {
    "bucket": "frontend-automation-assets",
    "region": "ap-shanghai",
    "cusdomain": "",
    "tencent": {
      "tmpSecretId": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "tmpSecretKey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "sessionToken": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    },
    "expiredTime": 900
  }
}
```

#### 使用测试脚本

```bash
# 确保已配置环境变量
export TENCENT_API_BASE_URL=http://localhost:5000

# 运行测试脚本
python test_api_server.py
```

## 🔧 API 接口说明

### 1. 健康检查

**接口**: `GET /health`

**描述**: 检查服务状态

**请求**:

```bash
curl http://localhost:5000/health
```

**响应**:

```json
{
  "status": "ok",
  "service": "tencent-cos-upload-api",
  "version": "1.0.0"
}
```

### 2. 获取上传凭证

**接口**: `POST /api/v1/upload-token`

**描述**: 获取 STS 临时凭证

**Headers**:
- `Content-Type`: `application/json`
- `X-Secret-Key`: API 安全密钥（可选）
- `Authorization`: `Bearer <token>`（可选）

**请求体**:

```json
{
  "mediaType": "image",
  "sceneName": "frontend-automation",
  "businessName": "workflow",
  "source": "web"
}
```

**参数说明**:
- `mediaType`: 媒体类型（image/video/file）
- `sceneName`: 场景名称（必需）
- `businessName`: 业务名称（必需）
- `source`: 来源（web/app）

**响应**:

```json
{
  "code": 0,
  "data": {
    "bucket": "frontend-automation-assets",
    "region": "ap-shanghai",
    "cusdomain": "https://your-cdn-domain.com",
    "tencent": {
      "tmpSecretId": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "tmpSecretKey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "sessionToken": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    },
    "expiredTime": 900
  }
}
```

**错误响应**:

```json
{
  "code": -1,
  "msg": "TENCENT_SECRET_ID is not configured"
}
```

### 3. 上报上传结果

**接口**: `POST /api/v1/upload-result`

**描述**: 上报文件上传结果

**Headers**:
- `Content-Type`: `application/json`
- `X-Secret-Key`: API 安全密钥（可选）
- `Authorization`: `Bearer <token>`（可选）

**请求体**:

```json
{
  "filename": "test-image.png",
  "tempVisit": "https://example.com/test-image.png",
  "size": 1024,
  "success": true
}
```

**参数说明**:
- `filename`: 文件名（必需）
- `tempVisit`: 临时访问 URL
- `size`: 文件大小（字节）
- `success`: 是否成功

**响应**:

```json
{
  "code": 0,
  "msg": "Upload result reported successfully"
}
```

## 🔐 安全最佳实践

### 1. 使用子账号和最小权限

**推荐**：使用子账号，仅授予必要的 COS 权限

**策略示例**:

```json
{
  "version": "2.0",
  "statement": [
    {
      "action": [
        "name/cos:PutObject",
        "name/cos:PostObject",
        "name/cos:HeadObject",
        "name/cos:GetObject"
      ],
      "effect": "allow",
      "resource": [
        "qcs::cos:ap-shanghai:uid/*:frontend-automation-assets/frontend-automation/*"
      ]
    }
  ]
}
```

### 2. 使用 API 安全密钥

**推荐**：设置 `API_SECRET_KEY`，客户端必须提供 `X-Secret-Key`

```bash
# .env 文件
API_SECRET_KEY=your-secure-random-key
```

### 3. 使用 HTTPS

**推荐**：在生产环境使用 HTTPS

- 使用 Nginx 反向代理配置 HTTPS
- 使用 Let's Encrypt 免费证书

### 4. 短期凭证有效期

**推荐**：设置较短的凭证有效期（如 15 分钟）

```bash
TENCENT_DURATION_SECONDS=900
```

### 5. 环境变量管理

**推荐**：
- 使用 `.env` 文件管理配置
- 将 `.env` 添加到 `.gitignore`
- 不要在代码中硬编码密钥

```bash
# .gitignore
.env
*.pyc
__pycache__/
```

## 🐛 故障排查

### 问题 1: 服务启动失败

**错误**: `ModuleNotFoundError: No module named 'flask'`

**解决方案**:

```bash
pip install -r requirements-api.txt
```

### 问题 2: 获取上传凭证失败

**错误**: `TENCENT_SECRET_ID is not configured`

**解决方案**:
检查 `.env` 文件，确保 `TENCENT_SECRET_ID` 和 `TENCENT_SECRET_KEY` 已正确配置

### 问题 3: 调用腾讯云 STS 失败

**错误**: `AuthFailure: SecretId is disabled`

**解决方案**:
检查腾讯云密钥是否已禁用或过期，重新生成密钥

### 问题 4: 上传失败：权限不足

**错误**: `AccessDenied`

**解决方案**:
检查 STS 策略是否包含必要的权限，确保 `TENCENT_ALLOW_PREFIX` 配置正确

### 问题 5: 客户端无法连接

**错误**: `Connection refused`

**解决方案**:
检查服务是否正常启动，防火墙是否开放端口 5000

```bash
# 检查服务状态
curl http://localhost:5000/health

# 检查端口是否监听
netstat -tuln | grep 5000
```

## 📊 监控和日志

### 查看服务日志

```bash
# 开发环境（直接运行）
python api_server.py  # 日志直接输出到控制台

# 生产环境（systemd）
sudo journalctl -u tencent-cos-api -f
```

### 日志级别配置

修改 `api_server.py` 中的日志级别：

```python
# 开发环境
logging.basicConfig(level=logging.DEBUG)

# 生产环境
logging.basicConfig(level=logging.INFO)
```

## 🚀 性能优化

### 1. 使用 Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

参数说明：
- `-w 4`: 4 个工作进程
- `-b 0.0.0.0:5000`: 监听所有网络接口的 5000 端口

### 2. 使用 Nginx 反向代理

配置 `/etc/nginx/sites-available/tencent-cos-api`:

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 3. 使用缓存（可选）

对于频繁的相同请求，可以使用 Redis 缓存 STS 临时凭证

## 📝 生产环境检查清单

在部署到生产环境前，请确认以下事项：

- [ ] 使用子账号而非主账号密钥
- [ ] 配置最小权限策略
- [ ] 设置 API_SECRET_KEY
- [ ] 使用 HTTPS
- [ ] 设置合理的凭证有效期（≤ 15 分钟）
- [ ] 配置 TENCENT_ALLOW_PREFIX 限制上传路径
- [ ] 使用 Gunicorn 或 uWSGI 部署
- [ ] 使用 Nginx 反向代理
- [ ] 配置日志轮转
- [ ] 设置监控告警
- [ ] 配置防火墙规则
- [ ] 定期更新依赖包

## 📚 相关文档

- [腾讯云 COS 官方文档](https://cloud.tencent.com/document/product/436)
- [腾讯云 STS 官方文档](https://cloud.tencent.com/document/product/598)
- [TENCENT_COS_INTEGRATION_GUIDE.md](TENCENT_COS_INTEGRATION_GUIDE.md) - 腾讯云 COS 集成详细指南
- [STATIC_ASSET_PROCESSING_GUIDE.md](STATIC_ASSET_PROCESSING_GUIDE.md) - 静态资源处理完整指南

## 💡 示例代码

### 使用 Python 客户端调用 API

```python
import requests

def get_upload_token():
    url = "http://localhost:5000/api/v1/upload-token"
    headers = {
        "Content-Type": "application/json",
        "X-Secret-Key": "your-api-secret-key"
    }
    data = {
        "mediaType": "image",
        "sceneName": "frontend-automation",
        "businessName": "workflow",
        "source": "web"
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()

# 使用
result = get_upload_token()
print(result)
```

### 使用 JavaScript 客户端调用 API

```javascript
async function getUploadToken() {
  const url = "http://localhost:5000/api/v1/upload-token";
  const headers = {
    "Content-Type": "application/json",
    "X-Secret-Key": "your-api-secret-key"
  };
  const data = {
    mediaType: "image",
    sceneName: "frontend-automation",
    businessName: "workflow",
    source: "web"
  };

  const response = await fetch(url, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(data)
  });

  return await response.json();
}

// 使用
getUploadToken().then(result => console.log(result));
```

## 🎯 总结

本指南涵盖了腾讯云 COS 上传 API 服务的完整部署流程，包括：

1. 前置条件准备
2. 依赖安装
3. 环境配置
4. 服务启动
5. 接口测试
6. 安全配置
7. 故障排查
8. 性能优化

按照本指南操作，您应该能够成功部署并运行腾讯云 COS 上传 API 服务。
