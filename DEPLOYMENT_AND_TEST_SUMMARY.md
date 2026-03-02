# 腾讯云 COS 上传功能 - 完整部署和测试总结

## 📦 交付清单

### 1. 后端 API 服务（核心）

#### 文件清单

```
├── api_server.py                    # Flask API 服务主程序
├── requirements-api.txt             # Python 依赖包
├── .env.api.example                 # 环境变量配置模板
├── start_api_server.sh              # 快速启动脚本（可执行）
├── test_api_server.py               # API 测试脚本
├── API_SERVER_DEPLOYMENT_GUIDE.md   # 详细部署指南
└── README_API_SERVER.md             # API 服务说明文档
```

#### 功能特性

- ✅ 提供获取 STS 临时凭证 API
- ✅ 提供上报上传结果 API
- ✅ 健康检查接口
- ✅ 支持多种存储后端（腾讯云 COS）
- ✅ API 安全密钥验证（可选）
- ✅ 自动生成 STS 策略
- ✅ 支持自定义 CDN 域名
- ✅ 完善的错误处理和日志

#### API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/v1/upload-token` | POST | 获取上传凭证（STS 临时凭证） |
| `/api/v1/upload-result` | POST | 上报上传结果 |

### 2. 客户端上传工具

#### 文件清单

```
src/tools/cos_uploader.py             # 腾讯云 COS 上传工具类
src/graphs/nodes/upload_assets_node.py # 资源上传节点（已更新）
```

#### 功能特性

- ✅ 支持使用 STS 临时凭证进行安全上传
- ✅ 自动缓存和刷新凭证（提前 5 分钟过期）
- ✅ 支持自定义加速域名
- ✅ 支持上传结果上报到后端
- ✅ 支持多存储后端选择（oss/cos/mock）

### 3. 文档

#### 文件清单

```
├── TENCENT_COS_INTEGRATION_GUIDE.md  # 腾讯云 COS 集成详细指南
├── STATIC_ASSET_PROCESSING_GUIDE.md  # 静态资源处理完整指南
├── WPTRESOURCE_ANALYSIS.md           # wptresource 仓库代码分析报告
├── API_SERVER_DEPLOYMENT_GUIDE.md    # API 服务部署详细指南
├── README_API_SERVER.md              # API 服务说明文档
├── .env.api.example                  # API 服务配置文件示例
└── .env.tencentyun.example           # 客户端配置文件示例
```

## 🚀 快速开始

### 方式一：使用快速启动脚本（推荐）

```bash
# 1. 给启动脚本添加执行权限
chmod +x start_api_server.sh

# 2. 运行启动脚本
./start_api_server.sh
```

脚本会自动完成：
- ✅ 检查 Python 版本
- ✅ 安装依赖包
- ✅ 创建配置文件
- ✅ 验证必需配置
- ✅ 启动 API 服务

### 方式二：手动部署

#### 步骤 1: 安装依赖

```bash
pip install -r requirements-api.txt
```

#### 步骤 2: 配置环境变量

```bash
# 复制配置模板
cp .env.api.example .env

# 编辑配置文件
nano .env
```

必需配置：

```bash
TENCENT_SECRET_ID=your_secret_id_here
TENCENT_SECRET_KEY=your_secret_key_here
TENCENT_BUCKET=your-bucket-name
TENCENT_REGION=ap-shanghai
```

#### 步骤 3: 启动服务

```bash
python api_server.py
```

服务将启动在 `http://localhost:5000`

### 步骤 4: 测试服务

```bash
# 方式一：使用测试脚本
python test_api_server.py

# 方式二：使用 curl
curl http://localhost:5000/health

curl -X POST http://localhost:5000/api/v1/upload-token \
  -H "Content-Type: application/json" \
  -d '{
    "mediaType": "image",
    "sceneName": "frontend-automation",
    "businessName": "workflow",
    "source": "test"
  }'
```

## ⚙️ 配置说明

### API 服务配置（.env）

```bash
# ==================== API 服务配置 ====================
PORT=5000                    # API 服务端口
DEBUG=false                  # 调试模式
API_SECRET_KEY=              # API 安全密钥（可选）

# ==================== 腾讯云 COS 配置 ====================
TENCENT_SECRET_ID=           # 腾讯云 SecretId（必需）
TENCENT_SECRET_KEY=          # 腾讯云 SecretKey（必需）
TENCENT_BUCKET=              # COS 存储桶名称（必需）
TENCENT_REGION=ap-shanghai   # COS 区域（必需）
TENCENT_DURATION_SECONDS=900 # 凭证有效期（秒）
TENCENT_ALLOW_PREFIX=frontend-automation/*  # 允许上传路径
TENCENT_CUSDOMAIN=           # 自定义 CDN 域名（可选）

# ==================== 工作流配置（客户端） ====================
STORAGE_BACKEND=cos          # 存储后端选择
TENCENT_API_BASE_URL=http://localhost:5000  # API 服务地址
TENCENT_SCENE_NAME=frontend-automation      # 场景名称
TENCENT_BUSINESS_NAME=workflow             # 业务名称
TENCENT_MODE=dev              # 环境模式
```

### 客户端配置（工作流）

```bash
# 设置存储后端为腾讯云 COS
export STORAGE_BACKEND=cos

# 设置 API 服务地址
export TENCENT_API_BASE_URL=http://localhost:5000

# 设置场景和业务名称
export TENCENT_SCENE_NAME=frontend-automation
export TENCENT_BUSINESS_NAME=workflow
export TENCENT_MODE=dev

# 运行工作流
python main.py
```

## 🐳 Docker 部署

### 创建 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY api_server.py .

EXPOSE 5000

CMD ["python", "api_server.py"]
```

### 构建和运行

```bash
# 构建镜像
docker build -t tencent-cos-api .

# 运行容器
docker run -d \
  --name tencent-cos-api \
  -p 5000:5000 \
  --env-file .env \
  tencent-cos-api
```

### 使用 Docker Compose

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

## 📊 测试结果

### 测试脚本功能

`test_api_server.py` 提供以下测试：

1. ✅ 健康检查接口测试
2. ✅ 获取上传凭证接口测试
3. ✅ 上报上传结果接口测试
4. ✅ 无效安全密钥测试
5. ✅ 缺少必需参数测试

### 运行测试

```bash
# 设置 API 服务地址
export TENCENT_API_BASE_URL=http://localhost:5000

# 运行测试
python test_api_server.py
```

### 预期输出

```
============================================================
开始测试腾讯云 COS 上传 API 服务
============================================================

配置:
  API Base URL: http://localhost:5000
  API Secret Key: 已配置
  Scene Name: frontend-automation
  Business Name: workflow
  Source: test-script

等待服务启动...

============================================================
测试: 健康检查接口
============================================================
响应: {
  "status": "ok",
  "service": "tencent-cos-upload-api",
  "version": "1.0.0"
}
✅ 通过: 服务状态: ok

============================================================
测试: 获取上传凭证接口
============================================================
...

============================================================
测试结果汇总
============================================================
健康检查: ✅ 通过
获取上传凭证: ✅ 通过
上报上传结果: ✅ 通过
无效安全密钥: ✅ 通过
缺少必需参数: ✅ 通过

总计: 5/5 测试通过

🎉 所有测试通过！API 服务运行正常
```

## 🔐 安全建议

1. ✅ **使用子账号而非主账号密钥**
2. ✅ **配置最小权限策略**
3. ✅ **设置 API_SECRET_KEY**
4. ✅ **使用 HTTPS（生产环境）**
5. ✅ **设置短期凭证有效期（≤ 15 分钟）**
6. ✅ **配置 TENCENT_ALLOW_PREFIX 限制路径**
7. ✅ **使用环境变量管理密钥**
8. ✅ **定期更新依赖包**
9. ✅ **启用日志监控**
10. ✅ **配置防火墙规则**

## 📝 生产环境检查清单

部署前请确认：

- [ ] 使用子账号而非主账号
- [ ] 配置最小权限策略
- [ ] 设置 API_SECRET_KEY
- [ ] 使用 HTTPS
- [ ] 设置合理的凭证有效期（≤ 15 分钟）
- [ ] 配置 TENCENT_ALLOW_PREFIX
- [ ] 使用 Gunicorn 或 uWSGI
- [ ] 使用 Nginx 反向代理
- [ ] 配置日志轮转
- [ ] 设置监控告警
- [ ] 配置防火墙
- [ ] 定期更新依赖

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

### 问题 5: 客户端无法连接

**错误**: `Connection refused`

**解决方案**:
检查服务是否正常启动，防火墙是否开放端口 5000。

## 📚 相关文档

- [API_SERVER_DEPLOYMENT_GUIDE.md](API_SERVER_DEPLOYMENT_GUIDE.md) - 详细部署指南
- [TENCENT_COS_INTEGRATION_GUIDE.md](TENCENT_COS_INTEGRATION_GUIDE.md) - 腾讯云 COS 集成指南
- [STATIC_ASSET_PROCESSING_GUIDE.md](STATIC_ASSET_PROCESSING_GUIDE.md) - 静态资源处理指南
- [README_API_SERVER.md](README_API_SERVER.md) - API 服务说明文档

## 🎯 总结

### 完成的功能

1. ✅ **后端 API 服务**
   - Flask 框架实现
   - 提供获取 STS 临时凭证 API
   - 提供上报上传结果 API
   - 健康检查接口
   - API 安全密钥验证
   - 完善的错误处理和日志

2. ✅ **客户端上传工具**
   - 腾讯云 COS 上传工具类
   - 自动凭证管理（缓存 + 刷新）
   - 支持自定义加速域名
   - 支持多存储后端选择

3. ✅ **配置和部署**
   - 环境变量配置模板
   - 快速启动脚本
   - Docker 支持
   - 生产环境部署指南

4. ✅ **测试和文档**
   - 完整的测试脚本
   - 详细的部署指南
   - API 服务说明文档
   - 故障排查指南

### 下一步建议

1. **实际部署**：在真实的腾讯云环境中部署 API 服务
2. **集成测试**：与工作流集成，测试完整的上传流程
3. **性能优化**：根据实际使用情况优化性能
4. **监控告警**：配置监控和告警系统
5. **高可用部署**：使用负载均衡和多个实例实现高可用

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

### 使用工作流上传文件

```python
from tools.cos_uploader import TencentCOSUploader

# 创建上传器
uploader = TencentCOSUploader(
    api_base_url="http://localhost:5000",
    scene_name="frontend-automation",
    business_name="workflow",
    mode="dev"
)

# 上传文件
result = uploader.upload_file(
    file_path="/path/to/image.png",
    filename="user_avatar.png",
    prefix="assets/"
)

if result.success:
    print(f"✅ 上传成功: {result.url}")
else:
    print(f"❌ 上传失败: {result.error}")
```

## 🎉 结语

恭喜！您已完成腾讯云 COS 上传功能的完整部署和测试。

现在您可以在工作流中使用腾讯云 COS 进行安全的文件上传了。如有任何问题，请参考相关文档或联系技术支持。
