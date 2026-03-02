# wptresource 仓库代码分析报告

## 📋 仓库概览

- **仓库名称**: `-`（特殊命名）
- **类型**: Monorepo（使用 Lerna 管理）
- **主要功能**: 多平台文件上传（图片、文件、视频）
- **云服务**: 腾讯云 COS (Cloud Object Storage)

## 📦 目录结构

```
wptresource/
├── lerna.json                          # Lerna 配置
├── package.json                        # 根 package.json
├── packages/
│   ├── uploadImg/                      # 图片上传包
│   │   ├── src/
│   │   │   ├── uploads/
│   │   │   │   ├── pcUploadImg.ts     # H5/PC 端上传
│   │   │   │   ├── wxUploadImg.ts     # 微信公众号上传
│   │   │   │   └── xcxUploadImg.ts    # 微信小程序上传
│   │   │   ├── core/
│   │   │   │   └── util.ts            # 工具函数
│   │   │   └── index.ts               # 主入口
│   │   ├── typings/
│   │   │   └── index.ts               # TypeScript 类型定义
│   │   └── package.json
│   ├── uploadFile/                     # 文件上传包
│   └── uploadVideo/                    # 视频上传包
```

## 🎯 核心功能分析

### 1. 图片上传功能 (uploadImg)

#### 支持的平台

| 平台 | 实现类 | 上传方式 | SDK |
|-----|--------|---------|-----|
| H5/PC | `pcUploadImg.ts` | 腾讯云 COS SDK | `cos-js-sdk-v5` |
| 微信公众号 | `wxUploadImg.ts` | 微信上传 API | 微信 JSSDK |
| 微信小程序 | `xcxUploadImg.ts` | 微信上传 API | 微信小程序 SDK |

#### 上传流程

```
1. 初始化 UploadImg
   ↓
2. 检测运行环境（H5/微信）
   ↓
3. 创建文件选择器（H5）或调用微信 API（微信）
   ↓
4. 从后端获取上传凭证
   API: POST /api/v1/upload-token
   ↓
5. 使用腾讯云 COS SDK 上传文件
   ↓
6. 上报上传结果
   API: POST /api/v1/upload-result
   ↓
7. 返回上传结果（filename, tempVisit）
```

#### 关键配置参数

```typescript
interface PropsOption {
  mediaType?: string;           // 媒体类型（image/video/file）
  sceneName: string;            // 场景名称（如 imchat）
  businessName: string;         // 业务名称（如 sale）
  mode?: 'dev' | 'gray' | 'prod'; // 环境模式
  token?: string;               // 认证 Token
  limit?: number;               // 单次上传数量限制（默认 9）
  maxSize?: number;             // 文件大小限制（默认 10MB）
  onProgress?: (percent, index) => void; // 上传进度回调
  secretKey?: string;           // X-Secret-Key（安全密钥）
}
```

### 2. 核心技术实现

#### H5/PC 端上传 (pcUploadImg.ts)

**关键代码片段**:

```typescript
// 1. 初始化腾讯云 COS
setCos = () => {
  return new Promise((resolve, reject) => {
    this.ajax({
      url: '/api/v1/upload-token',
      data: {
        mediaType: 'image',
        sceneName: this.option.sceneName,
        businessName: this.option.businessName,
        source: 'web',
      }
    }).then((res) => {
      // 使用后端返回的临时凭证初始化 COS
      this.cos = new COS({
        Domain: res.data.cusdomain,
        Protocol: 'https:',
        getAuthorization: (options, callback) => {
          callback({
            TmpSecretId: res.data.tencent.tmpSecretId,
            TmpSecretKey: res.data.tencent.tmpSecretKey,
            XCosSecurityToken: res.data.tencent.sessionToken,
            ExpiredTime: res.data.expiredTime,
          });
        },
      });

      this.state = {
        bucket: res.data.bucket,
        region: res.data.region,
      };
      resolve(res);
    });
  });
};

// 2. 上传文件
uploadFile = async (file: File) => {
  return new Promise((resolve, reject) => {
    const fileName = `${uuid()}.${file.name.split('.').pop()}`;
    const key = `${sceneName}/${businessName}/${fileName}`;

    this.cos.postObject({
      Bucket: this.state.bucket,
      Region: this.state.region,
      Key: key,
      Body: file,
      onProgress: (progressData) => {
        const percent = progressData.percent * 100;
        this.option.onProgress?.(percent, index);
      }
    }, (err, data) => {
      if (err) {
        reject(err);
      } else {
        resolve({
          filename: key,
          tempVisit: `https://${this.state.bucket}.cos.${this.state.region}.myqcloud.com/${key}`
        });
      }
    });
  });
};
```

#### 微信公众号上传 (wxUploadImg.ts)

**关键代码片段**:

```typescript
// 1. 选择图片
chooseImage = () => {
  window.wx.chooseImage({
    sourceType: ['album', 'camera'],
    count: Math.min(this.option.limit, 9),
    success: (res) => {
      this.localIds = res.localIds;
      setTimeout(this.startUpload, 200);
    }
  });
};

// 2. 上传图片到微信服务器
uploadImg = (localId: string) => {
  return new Promise((resolve, reject) => {
    window.wx.uploadImage({
      localId: localId,
      isShowProgressTips: 1,
      success: (res) => {
        // 上报第三方下载链接
        this.reportThirdUploadResult(res.serverId).then((uploadResult) => {
          this.serverIds.push(uploadResult.filename);
          this.tempVisits.push(uploadResult.tempVisit);
          resolve(uploadResult);
        });
      }
    });
  });
};

// 3. 上报上传结果
reportThirdUploadResult = (serverId: string) => {
  return this.ajax({
    url: '/api/v1/links',
    data: { serverId }
  });
};
```

### 3. 工具函数 (util.ts)

#### 核心工具函数

```typescript
// 1. 生成唯一 ID
export function uuid(len = 8): string {
  const S = 'qwertyuioopasdfghjklzxcvbnmQWERTYUIOOPASDFGHJKLZXCVBNM0123456789';
  const LEN = S.length - 1;
  return ' '.repeat(len).split('').map(() => S[Math.round(Math.random() * LEN)]).join('');
}

// 2. 获取 Cookie
export function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null;
  }
  return null;
}

// 3. 获取 X-Secret-Key
export function getSecretKey(paramSecretKey?: string): string | null {
  // 优先从 cookie 获取
  const cookieSecretKey = getCookie('X-Secret-Key');
  if (cookieSecretKey) {
    return cookieSecretKey;
  }
  // 如果 cookie 获取不到，从参数获取
  return paramSecretKey || null;
}

// 4. AJAX 封装
export const ajax = ({ method, token, mode, source }) => ({ url, data, headers }) => {
  const hostname = getHostname(mode, source);
  return request.post({
    url: url.startsWith('http') ? url : hostname + url,
    headers: {
      'content-type': 'application/json;charset=utf-8',
      ...headers,
    },
    data,
    withCredentials: true
  });
};

// 5. 环境配置
const HOST_CONFIG = {
  wpt: {
    dev: 'https://skt.weipaitang.com',
    gray: 'https://canary-sk.weipaitang.com',
    prod: 'https://sk.weipaitang.com',
  },
  baocui: {
    dev: 'https://w-skt.baocuicoin.com',
    gray: 'https://w-skt.baocuicoin.com',
    prod: 'https://w-sk.baocuicoin.com',
  },
};
```

## 🔑 关键 API

### 1. 获取上传凭证

```typescript
POST /api/v1/upload-token
Headers: {
  'Content-Type': 'application/json',
  'X-Secret-Key': '<secret-key>'  // 可选
}
Body: {
  mediaType: 'image',
  sceneName: 'imchat',
  businessName: 'sale',
  source: 'web'
}
Response: {
  code: 0,
  data: {
    bucket: 'appwpt-10002380',
    region: 'ap-shanghai',
    cusdomain: 'https://custom-domain.com',
    tencent: {
      tmpSecretId: '<tmp-secret-id>',
      tmpSecretKey: '<tmp-secret-key>',
      sessionToken: '<session-token>'
    },
    expiredTime: 900  // 秒
  }
}
```

### 2. 上报上传结果

```typescript
POST /api/v1/upload-result
Body: {
  filename: 'imchat/sale/abc123.png',
  tempVisit: 'https://...',
  size: 102400,
  ...
}
```

### 3. 微信公众号 - 上报第三方链接

```typescript
POST /api/v1/links
Body: {
  serverId: 'wx-server-id'
}
Response: {
  filename: 'xxx',
  tempVisit: 'https://...'
}
```

## 💡 设计亮点

### 1. 多平台适配

自动检测运行环境，选择合适的上传方式：

```typescript
const isPhone = window.navigator.userAgent.match(/phone|android|iphone|ios|ipad/i);
const weChatInfo = window.navigator.userAgent.match(/MicroMessenger\/([\d\.]+)/i);

if (isPhone && weChatInfo && weChatInfo[1] > '6.0.2') {
  this.uploader = new WxUploadImg(opt);  // 微信环境
} else {
  this.uploader = new H5UploadImg(opt);  // H5 环境
}
```

### 2. 安全性设计

- 使用临时凭证（STS），避免长期密钥泄露
- X-Secret-Key 机制，增强安全性
- Cookie + 参数双重获取 Secret Key

### 3. 可配置性

- 支持多环境（dev/gray/prod）
- 支持多业务场景（sceneName, businessName）
- 支持自定义上传参数

### 4. 用户体验

- 上传进度回调
- 批量上传支持
- 失败重试机制

## 📊 与现有方案的对比

| 特性 | wptresource | 我们的 upload_assets_node |
|-----|-------------|---------------------------|
| **云服务** | 腾讯云 COS | 阿里云 OSS |
| **认证方式** | STS 临时凭证 | 长期密钥 |
| **多平台支持** | H5 + 微信 | H5 |
| **进度回调** | ✅ | ❌ |
| **临时凭证** | ✅ | ❌ |
| **安全性** | 高（临时凭证） | 中（长期密钥） |
| **环境配置** | dev/gray/prod | Mock/真实 |
| **上报结果** | ✅ | ❌ |

## 🚀 集成建议

### 方案 1：完全替换（推荐）

**优势**：
- 更安全（STS 临时凭证）
- 更完善（进度回调、多平台）
- 更灵活（多环境配置）

**劣势**：
- 需要后端支持（获取临时凭证 API）
- 需要迁移到腾讯云 COS

### 方案 2：混合使用

**保留**：
- 阿里云 OSS 作为主要存储

**新增**：
- 腾讯云 COS 作为备用存储
- 或用于特定业务场景

### 方案 3：仅提取逻辑

**提取**：
- 文件选择逻辑
- 进度回调机制
- 环境配置方式

**保留**：
- 阿里云 OSS 上传
- 现有 Mock 模式

## 📝 迁移步骤（如果选择方案 1）

### 步骤 1：后端实现

```typescript
// 实现获取上传凭证 API
app.post('/api/v1/upload-token', async (req, res) => {
  const { mediaType, sceneName, businessName, source } = req.body;

  // 使用腾讯云 STS 生成临时凭证
  const stsConfig = {
    bucket: 'your-bucket-name',
    region: 'ap-shanghai',
    secretId: process.env.TENCENT_SECRET_ID,
    secretKey: process.env.TENCENT_SECRET_KEY,
    policy: {
      version: '2.0',
      statement: [{
        effect: 'allow',
        action: [
          'name/cos:PutObject',
          'name/cos:PostObject'
        ],
        resource: [`qcs::cos:ap-shanghai:uid/xxx:bucket-name/${sceneName}/${businessName}/*`]
      }]
    }
  };

  const tempCreds = await getSTSToken(stsConfig);

  res.json({
    code: 0,
    data: {
      bucket: 'your-bucket-name',
      region: 'ap-shanghai',
      cusdomain: 'https://your-cdn-domain.com',
      tencent: {
        tmpSecretId: tempCreds.tmpSecretId,
        tmpSecretKey: tempCreds.tmpSecretKey,
        sessionToken: tempCreds.sessionToken
      },
      expiredTime: tempCreds.expiredTime
    }
  });
});
```

### 步骤 2：前端集成

```python
# src/graphs/nodes/upload_assets_node.py

# 新增：腾讯云 COS 上传支持
def upload_to_cos(file_path: str, prefix: str, filename: str) -> str:
    """
    上传文件到腾讯云 COS

    Args:
        file_path: 本地文件路径
        prefix: 上传前缀
        filename: 文件名

    Returns:
        COS URL
    """
    # 获取上传凭证
    token_response = requests.post(
        "https://api.example.com/api/v1/upload-token",
        json={
            "mediaType": "image",
            "sceneName": "frontend-automation",
            "businessName": "workflow",
            "source": "web"
        }
    )

    if token_response.status_code != 200:
        raise Exception("获取上传凭证失败")

    token_data = token_response.json()

    # 初始化腾讯云 COS
    try:
        from cos_cos_python_sdk_v5 import CosS3Client
    except ImportError:
        raise Exception("需要安装 cos-python-sdk-v5")

    # 使用临时凭证初始化
    config = CosS3Config(
        Region=token_data["region"],
        Scheme='https'
    )
    client = CosS3Client(
        SecretId=token_data["tencent"]["tmpSecretId"],
        SecretKey=token_data["tencent"]["tmpSecretKey"],
        Token=token_data["tencent"]["sessionToken"],
        Region=token_data["region"]
    )

    # 上传文件
    file_key = f"{prefix}{filename}"
    response = client.put_object(
        Bucket=token_data["bucket"],
        Body=open(file_path, 'rb'),
        Key=file_key
    )

    # 生成 URL
    return f"https://{token_data['bucket']}.cos.{token_data['region']}.myqcloud.com/{file_key}"
```

### 步骤 3：环境配置

```bash
# .env
TENCENT_SECRET_ID=your_tencent_secret_id
TENCENT_SECRET_KEY=your_tencent_secret_key
TENCENT_BUCKET=your-bucket-name
TENCENT_REGION=ap-shanghai
```

## 🎯 总结

这个 `wptresource` 仓库是一个**成熟的企业级文件上传解决方案**，具有以下特点：

✅ **优点**：
- 多平台支持（H5、微信小程序、微信公众号）
- 安全性高（STS 临时凭证）
- 功能完善（进度回调、批量上传、重试机制）
- 可配置性强（多环境、多场景）

⚠️ **注意事项**：
- 需要后端支持（STS 临时凭证 API）
- 需要迁移到腾讯云 COS（如果当前使用阿里云 OSS）
- 依赖特定的业务 API（/api/v1/upload-token、/api/v1/links）

📌 **建议**：
1. 如果您的项目需要更高安全性和功能完善性，建议迁移到腾讯云 COS + STS 方案
2. 如果当前阿里云 OSS 方案已满足需求，可以仅提取工具函数和进度回调机制
3. 可以参考其设计思路，优化现有的 upload_assets_node

---

**生成时间**: 2026-03-02
**分析工具**: Coze Coding AI
