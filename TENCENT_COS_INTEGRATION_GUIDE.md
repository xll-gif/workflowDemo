# 腾讯云 COS 集成指南

## 概述

本指南详细说明如何在工作流自动化系统中集成腾讯云 COS（Cloud Object Storage）进行文件上传。

## 🎯 功能特性

- ✅ 使用 STS 临时凭证（更安全）
- ✅ 支持多种存储后端（阿里云 OSS / 腾讯云 COS / Mock）
- ✅ 自动凭证管理（缓存 + 自动刷新）
- ✅ 上传结果上报
- ✅ 环境配置灵活（dev/gray/prod）

## 📋 前置条件

### 1. 腾讯云账号

1. 访问 [腾讯云官网](https://cloud.tencent.com/)
2. 注册并登录账号
3. 开通 COS 服务

### 2. 创建存储桶（Bucket）

1. 进入 COS 控制台
2. 点击"创建存储桶"
3. 填写配置：
   - **名称**：例如 `frontend-automation-assets`
   - **所属地域**：选择合适的区域（如上海）
   - **访问权限**：私有读写（推荐）或 公共读
4. 点击确定

### 3. 创建子账号并配置权限

**方式一：使用主账号 AccessKey（不推荐）**

1. 进入"访问管理" → "API密钥管理"
2. 创建密钥，复制 SecretId 和 SecretKey

**方式二：使用 STS 临时凭证（推荐）**

1. 进入"访问管理" → "角色" → "新建角色"
2. 角色类型：腾讯云服务
3. 受信实体：云服务器（CVM）或 自定义
4. 配置角色权限：
   ```json
   {
     "version": "2.0",
     "statement": [
       {
         "effect": "allow",
         "action": [
           "name/cos:PutObject",
           "name/cos:PostObject",
           "name/cos:HeadObject"
         ],
         "resource": [
           "qcs::cos:ap-shanghai:uid/xxx:bucket-name/*"
         ]
       }
     ]
   }
   ```

### 4. 安装 Python SDK

```bash
pip install cos-python-sdk-v5
```

## 🔧 配置步骤

### 1. 环境变量配置

创建 `.env` 文件：

```bash
# 存储后端选择
STORAGE_BACKEND=cos

# 腾讯云 COS 配置
TENCENT_API_BASE_URL=https://api.example.com
TENCENT_SCENE_NAME=frontend-automation
TENCENT_BUSINESS_NAME=workflow
TENCENT_MODE=dev
TENCENT_TOKEN=your_token_here
TENCENT_SECRET_KEY=your_secret_key_here
```

### 2. 后端 API 实现（必需）

腾讯云 COS 上传需要后端提供 `/api/v1/upload-token` API，用于获取 STS 临时凭证。

#### API 接口规范

**请求**：
```
POST /api/v1/upload-token
Headers: {
  "Content-Type": "application/json",
  "X-Secret-Key": "<secret-key>"  // 可选
}
Body: {
  "mediaType": "image",          // mediaType: image/video/file
  "sceneName": "imchat",        // 场景名称
  "businessName": "sale",       // 业务名称
  "source": "web"               // 来源
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "bucket": "your-bucket-name",
    "region": "ap-shanghai",
    "cusdomain": "https://your-cdn-domain.com",  // 可选：自定义加速域名
    "tencent": {
      "tmpSecretId": "<tmp-secret-id>",
      "tmpSecretKey": "<tmp-secret-key>",
      "sessionToken": "<session-token>"
    },
    "expiredTime": 900  // 有效期（秒）
  }
}
```

#### 后端实现示例（Node.js）

```javascript
const STS = require('qcloud-cos-sts');

// 配置腾讯云 STS
const stsConfig = {
  secretId: process.env.TENCENT_SECRET_ID,
  secretKey: process.env.TENCENT_SECRET_KEY,
  region: 'ap-shanghai',
  durationSeconds: 900,
  bucket: 'your-bucket-name',
  allowPrefix: 'frontend-automation/*',
  policy: {
    version: '2.0',
    statement: [{
      action: [
        'name/cos:PutObject',
        'name/cos:PostObject',
        'name/cos:HeadObject'
      ],
      effect: 'allow',
      resource: [
        `qcs::cos:ap-shanghai:uid/xxx:your-bucket-name/frontend-automation/*`
      ]
    }]
  }
};

// 获取临时凭证 API
app.post('/api/v1/upload-token', async (req, res) => {
  const { mediaType, sceneName, businessName, source } = req.body;

  try {
    // 调用腾讯云 STS 获取临时凭证
    const tempCreds = await new Promise((resolve, reject) => {
      STS.getCredential({
        secretId: stsConfig.secretId,
        secretKey: stsConfig.secretKey,
        policy: stsConfig.policy,
        durationSeconds: stsConfig.durationSeconds,
        region: stsConfig.region,
        bucket: stsConfig.bucket,
        allowPrefix: stsConfig.allowPrefix
      }, (err, data) => {
        if (err) reject(err);
        else resolve(data);
      });
    });

    res.json({
      code: 0,
      data: {
        bucket: stsConfig.bucket,
        region: stsConfig.region,
        cusdomain: 'https://your-cdn-domain.com',
        tencent: {
          tmpSecretId: tempCreds.credentials.tmpSecretId,
          tmpSecretKey: tempCreds.credentials.tmpSecretKey,
          sessionToken: tempCreds.credentials.sessionToken
        },
        expiredTime: stsConfig.durationSeconds
      }
    });
  } catch (error) {
    res.status(500).json({
      code: -1,
      msg: error.message
    });
  }
});
```

#### 后端实现示例（Python）

```python
from tencentcloud.sts.v20180813 import sts_client, models
from tencentcloud.common import credential
import json

# 配置腾讯云 STS
sts_config = {
    "secret_id": os.getenv("TENCENT_SECRET_ID"),
    "secret_key": os.getenv("TENCENT_SECRET_KEY"),
    "region": "ap-shanghai",
    "duration_seconds": 900,
    "bucket": "your-bucket-name",
    "allow_prefix": "frontend-automation/*"
}

# 获取临时凭证 API
@app.route('/api/v1/upload-token', methods=['POST'])
def get_upload_token():
    data = request.json
    media_type = data.get('mediaType', 'image')
    scene_name = data.get('sceneName', '')
    business_name = data.get('businessName', '')

    try:
        # 创建 STS 客户端
        cred = credential.Credential(
            sts_config["secret_id"],
            sts_config["secret_key"]
        )
        client = sts_client.StsClient(cred, sts_config["region"])

        # 构建策略
        policy = {
            "version": "2.0",
            "statement": [{
                "effect": "allow",
                "action": [
                    "name/cos:PutObject",
                    "name/cos:PostObject",
                    "name/cos:HeadObject"
                ],
                "resource": [
                    f"qcs::cos:{sts_config['region']}:uid/xxx:{sts_config['bucket']}/{scene_name}/{business_name}/*"
                ]
            }]
        }

        # 获取临时凭证
        req = models.GetFederationTokenRequest()
        req.Name = "frontend-automation"
        req.PolicyJson = json.dumps(policy)
        req.DurationSeconds = sts_config["duration_seconds"]

        resp = client.GetFederationToken(req)

        res.json({
            "code": 0,
            "data": {
                "bucket": sts_config["bucket"],
                "region": sts_config["region"],
                "cusdomain": "https://your-cdn-domain.com",
                "tencent": {
                    "tmpSecretId": resp.Credentials.TmpSecretId,
                    "tmpSecretKey": resp.Credentials.TmpSecretKey,
                    "sessionToken": resp.Credentials.SessionToken
                },
                "expiredTime": sts_config["duration_seconds"]
            }
        })

    except Exception as e:
        res.status(500).json({
            "code": -1,
            "msg": str(e)
        })
```

## 🚀 使用方法

### 方式一：使用环境变量（推荐）

```bash
# 设置环境变量
export STORAGE_BACKEND=cos
export TENCENT_API_BASE_URL=https://api.example.com
export TENCENT_SCENE_NAME=frontend-automation
export TENCENT_BUSINESS_NAME=workflow
export TENCENT_MODE=dev

# 运行工作流
python main.py
```

### 方式二：使用 .env 文件

1. 复制配置模板：
```bash
cp .env.tencentyun.example .env
```

2. 编辑 `.env` 文件，填入实际配置

3. 运行工作流

### 方式三：代码中使用

```python
from tools.cos_uploader import TencentCOSUploader

# 创建上传器
uploader = TencentCOSUploader(
    api_base_url="https://api.example.com",
    scene_name="frontend-automation",
    business_name="workflow",
    mode="dev"
)

# 上传文件
result = uploader.upload_file(
    file_path="/path/to/image.png",
    filename="user_avatar.png",
    prefix="assets/",
    on_progress=lambda percent: print(f"Progress: {percent}%")
)

if result.success:
    print(f"上传成功: {result.url}")
else:
    print(f"上传失败: {result.error}")
```

## 🔍 验证配置

运行以下测试代码验证配置是否正确：

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 检查配置
required_vars = [
    "STORAGE_BACKEND",
    "TENCENT_API_BASE_URL",
    "TENCENT_SCENE_NAME",
    "TENCENT_BUSINESS_NAME",
    "TENCENT_MODE"
]

missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
else:
    print("✅ 所有必需的环境变量已配置")
    
    # 测试上传
    from tools.cos_uploader import TencentCOSUploader
    try:
        uploader = TencentCOSUploader(
            api_base_url=os.getenv("TENCENT_API_BASE_URL"),
            scene_name=os.getenv("TENCENT_SCENE_NAME"),
            business_name=os.getenv("TENCENT_BUSINESS_NAME"),
            mode=os.getenv("TENCENT_MODE")
        )
        
        # 获取临时凭证
        credentials = uploader.get_credentials()
        
        print("✅ 腾讯云 COS 连接成功！")
        print(f"  Bucket: {credentials.bucket}")
        print(f"  Region: {credentials.region}")
        print(f"  过期时间: {credentials.expired_time} 秒")
        
    except Exception as e:
        print(f"❌ 腾讯云 COS 连接失败: {e}")
```

## 📊 存储后端对比

| 特性 | 阿里云 OSS | 腾讯云 COS |
|-----|-----------|-----------|
| **认证方式** | 长期密钥 | STS 临时凭证 |
| **安全性** | 中 | 高 |
| **环境配置** | dev/prod | dev/gray/prod |
| **上传凭证** | 无需后端 | 需要后端 API |
| **进度回调** | ❌ | ✅ |
| **自动刷新** | ❌ | ✅ |

## 🔐 安全最佳实践

### 1. 使用 STS 临时凭证

✅ **推荐**：
- 使用 STS 临时凭证，有效期为 15 分钟
- 凭证自动缓存和刷新
- 避免长期密钥泄露风险

❌ **不推荐**：
- 使用主账号 AccessKey
- 将密钥硬编码在代码中
- 将密钥提交到版本控制系统

### 2. 环境变量管理

✅ **推荐**：
- 使用 `.env` 文件管理环境变量
- 将 `.env` 添加到 `.gitignore`
- 为不同环境创建不同的配置文件

❌ **不推荐**：
- 在代码中硬编码配置
- 将敏感信息提交到 Git

### 3. 权限最小化

✅ **推荐**：
- 为不同的业务场景创建不同的角色
- 仅授予必要的权限（如 PutObject）
- 使用资源路径限制（如 `frontend-automation/*`）

❌ **不推荐**：
- 使用管理员权限
- 授予所有 COS 权限

## 🐛 故障排查

### 常见问题

**1. 获取上传凭证失败**

- 检查 `TENCENT_API_BASE_URL` 是否正确
- 检查后端 API 是否正常运行
- 检查网络连接

**2. COS SDK 未安装**

```bash
pip install cos-python-sdk-v5
```

**3. 上传失败：权限不足**

- 检查角色权限配置
- 检查存储桶访问权限
- 检查临时凭证有效期

**4. 环境变量未生效**

```bash
# 重新加载 .env
export $(cat .env | xargs)

# 或使用 python-dotenv
from dotenv import load_dotenv
load_dotenv()
```

## 📝 迁移指南

### 从阿里云 OSS 迁移到腾讯云 COS

1. **安装腾讯云 COS SDK**：
```bash
pip install cos-python-sdk-v5
```

2. **配置环境变量**：
```bash
STORAGE_BACKEND=cos
TENCENT_API_BASE_URL=https://api.example.com
TENCENT_SCENE_NAME=frontend-automation
TENCENT_BUSINESS_NAME=workflow
TENCENT_MODE=dev
```

3. **实现后端 API**：
   - 添加 `/api/v1/upload-token` API
   - 配置 STS 策略

4. **测试上传**：
```python
from tools.cos_uploader import TencentCOSUploader

uploader = TencentCOSUploader(...)
result = uploader.upload_file("test.png")
```

## 📚 相关文档

- [腾讯云 COS 官方文档](https://cloud.tencent.com/document/product/436)
- [COS Python SDK 文档](https://cloud.tencent.com/document/product/436/12269)
- [STS 临时凭证文档](https://cloud.tencent.com/document/product/598)
- [wptresource 仓库分析](WPTRESOURCE_ANALYSIS.md)

## 🎯 总结

腾讯云 COS 集成提供了：

- ✅ 更安全的 STS 临时凭证机制
- ✅ 更完善的功能（进度回调、自动刷新）
- ✅ 更灵活的配置（多环境、多场景）
- ✅ 与 wptresource 保持一致的设计

建议在生产环境中使用腾讯云 COS + STS 方案，以获得更好的安全性和功能性。
