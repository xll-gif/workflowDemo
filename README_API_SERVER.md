# 腾讯云 COS 上传 API 服务

为前端自动化工作流提供 STS 临时凭证，实现安全的文件上传功能。

## 📦 文件清单

```
.
├── api_server.py                    # Flask API 服务主程序
├── requirements-api.txt             # Python 依赖包
├── .env.api.example                 # 环境变量配置模板
├── start_api_server.sh              # 快速启动脚本
├── test_api_server.py               # API 测试脚本
├── API_SERVER_DEPLOYMENT_GUIDE.md   # 详细部署指南
└── README_API_SERVER.md             # 本文件
```

## 🚀 快速开始

### 1. 一键启动（推荐）

```bash
# 给启动脚本添加执行权限（首次运行）
chmod +x start_api_server.sh

# 运行启动脚本
./start_api_server.sh
```

脚本会自动完成以下操作：
- ✅ 检查 Python 版本
- ✅ 安装依赖包
- ✅ 创建配置文件
- ✅ 验证必需配置
- ✅ 启动 API 服务

### 2. 手动启动

#### 安装依赖

```bash
pip install -r requirements-api.txt
```

#### 配置环境变量

```bash
# 复制配置模板
cp .env.api.example .env

# 编辑配置文件
nano .env
```

必需配置项：

```bash
TENCENT_SECRET_ID=your_secret_id_here
TENCENT_SECRET_KEY=your_secret_key_here
TENCENT_BUCKET=your-bucket-name
TENCENT_REGION=ap-shanghai
```

#### 启动服务

```bash
python api_server.py
```

### 3. 测试服务

```bash
# 方式一：使用测试脚本
python test_api_server.py

# 方式二：使用 curl

# 健康检查
curl http://localhost:5000/health

# 获取上传凭证
curl -X POST http://localhost:5000/api/v1/upload-token \
  -H "Content-Type: application/json" \
  -d '{
    "mediaType": "image",
    "sceneName": "frontend-automation",
    "businessName": "workflow",
    "source": "test"
  }'
```

## 📡 API 接口

### 1. 健康检查

```
GET /health
```

**响应**：

```json
{
  "status": "ok",
  "service": "tencent-cos-upload-api",
  "version": "1.0.0"
}
```

### 2. 获取上传凭证

```
POST /api/v1/upload-token
Content-Type: application/json
```

**请求体**：

```json
{
  "mediaType": "image",
  "sceneName": "frontend-automation",
  "businessName": "workflow",
  "source": "web"
}
```

**响应**：

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

### 3. 上报上传结果

```
POST /api/v1/upload-result
Content-Type: application/json
```

**请求体**：

```json
{
  "filename": "test-image.png",
  "tempVisit": "https://example.com/test-image.png",
  "size": 1024,
  "success": true
}
```

**响应**：

```json
{
  "code": 0,
  "msg": "Upload result reported successfully"
}
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `PORT` | API 服务端口 | 否 | 5000 |
| `DEBUG` | 调试模式 | 否 | false |
| `API_SECRET_KEY` | API 安全密钥 | 否 | - |
| `TENCENT_SECRET_ID` | 腾讯云 SecretId | 是 | - |
| `TENCENT_SECRET_KEY` | 腾讯云 SecretKey | 是 | - |
| `TENCENT_BUCKET` | COS 存储桶名称 | 是 | - |
| `TENCENT_REGION` | COS 区域 | 是 | ap-shanghai |
| `TENCENT_DURATION_SECONDS` | 凭证有效期（秒） | 否 | 900 |
| `TENCENT_ALLOW_PREFIX` | 允许上传路径前缀 | 否 | frontend-automation/* |
| `TENCENT_CUSDOMAIN` | 自定义 CDN 域名 | 否 | - |

### 安全配置

**1. 使用子账号和最小权限**

创建子账号，仅授予必要的 COS 权限：

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
        "qcs::cos:ap-shanghai:uid/*:bucket-name/frontend-automation/*"
      ]
    }
  ]
}
```

**2. 使用 API 安全密钥**

设置 `API_SECRET_KEY`，客户端必须提供 `X-Secret-Key`：

```bash
API_SECRET_KEY=your-secure-random-key
```

**3. 短期凭证有效期**

设置较短的凭证有效期（建议 ≤ 15 分钟）：

```bash
TENCENT_DURATION_SECONDS=900
```

## 🐳 Docker 部署

### 1. 创建 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY api_server.py .

EXPOSE 5000

CMD ["python", "api_server.py"]
```

### 2. 构建 Docker 镜像

```bash
docker build -t tencent-cos-api .
```

### 3. 运行容器

```bash
docker run -d \
  --name tencent-cos-api \
  -p 5000:5000 \
  --env-file .env \
  tencent-cos-api
```

### 4. 使用 Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    restart: always
```

启动服务：

```bash
docker-compose up -d
```

## 🔧 生产环境部署

### 使用 Gunicorn

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### 使用 systemd

创建服务文件 `/etc/systemd/system/tencent-cos-api.service`：

```ini
[Unit]
Description=Tencent COS Upload API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 /path/to/project/api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start tencent-cos-api
sudo systemctl enable tencent-cos-api
sudo systemctl status tencent-cos-api
```

### 使用 Nginx 反向代理

配置 `/etc/nginx/sites-available/tencent-cos-api`：

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/tencent-cos-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📚 相关文档

- [API_SERVER_DEPLOYMENT_GUIDE.md](API_SERVER_DEPLOYMENT_GUIDE.md) - 详细部署指南
- [TENCENT_COS_INTEGRATION_GUIDE.md](TENCENT_COS_INTEGRATION_GUIDE.md) - 腾讯云 COS 集成指南
- [STATIC_ASSET_PROCESSING_GUIDE.md](STATIC_ASSET_PROCESSING_GUIDE.md) - 静态资源处理指南

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
检查 `.env` 文件，确保必需配置已填写。

### 问题 3: 调用腾讯云 STS 失败

**错误**: `AuthFailure: SecretId is disabled`

**解决方案**:
检查腾讯云密钥是否有效，重新生成密钥。

### 问题 4: 上传失败：权限不足

**错误**: `AccessDenied`

**解决方案**:
检查 STS 策略权限配置，确保 `TENCENT_ALLOW_PREFIX` 正确。

## 🔐 安全建议

1. ✅ 使用子账号而非主账号密钥
2. ✅ 配置最小权限策略
3. ✅ 设置 API_SECRET_KEY
4. ✅ 使用 HTTPS（生产环境）
5. ✅ 设置短期凭证有效期（≤ 15 分钟）
6. ✅ 配置 TENCENT_ALLOW_PREFIX 限制路径
7. ✅ 使用环境变量管理密钥
8. ✅ 定期更新依赖包
9. ✅ 启用日志监控
10. ✅ 配置防火墙规则

## 📝 生产环境检查清单

部署前请确认：

- [ ] 使用子账号而非主账号
- [ ] 配置最小权限策略
- [ ] 设置 API_SECRET_KEY
- [ ] 使用 HTTPS
- [ ] 设置合理的凭证有效期
- [ ] 配置 TENCENT_ALLOW_PREFIX
- [ ] 使用 Gunicorn 或 uWSGI
- [ ] 使用 Nginx 反向代理
- [ ] 配置日志轮转
- [ ] 设置监控告警
- [ ] 配置防火墙
- [ ] 定期更新依赖

## 📄 许可证

MIT License

## 💡 支持

如有问题，请查看：
- [API_SERVER_DEPLOYMENT_GUIDE.md](API_SERVER_DEPLOYMENT_GUIDE.md) - 详细部署指南
- [TENCENT_COS_INTEGRATION_GUIDE.md](TENCENT_COS_INTEGRATION_GUIDE.md) - 腾讯云 COS 集成指南

## 🎉 总结

本 API 服务为前端自动化工作流提供了安全、可靠的文件上传功能。通过 STS 临时凭证机制，实现了：

- ✅ 安全的文件上传（短期凭证）
- ✅ 灵活的配置（多环境、多场景）
- ✅ 简单的集成（REST API）
- ✅ 完善的文档（部署、使用、故障排查）

按照本指南操作，您应该能够快速部署并使用本 API 服务。
