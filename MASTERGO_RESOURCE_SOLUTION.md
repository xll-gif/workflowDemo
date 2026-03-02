# MasterGo 静态资源存储解决方案

## 概述

相比 Figma，使用 MasterGo 有以下优势：

1. ✅ **API 访问更稳定** - 没有海外 API 限流问题
2. ✅ **访问速度更快** - 国内服务器，延迟低
3. ✅ **中文文档完善** - 更容易理解和集成
4. ✅ **符合国内规范** - 遵守国内数据存储法规

## 方案对比

### 方案 1：对象存储公共读（推荐 ⭐⭐⭐⭐⭐）

**原理**：配置对象存储 Bucket 为公共读权限，所有资源通过永久 URL 访问

**优点**：
- ✅ 永久可访问，无签名过期问题
- ✅ 支持 CDN 加速
- ✅ 便于前端直接引用
- ✅ 成本低（只有流量费）

**缺点**：
- ⚠️ 需要配置 Bucket 权限
- ⚠️ 任何人都可以访问（如果需要私密访问，不建议）

**适用场景**：
- 公开的前端项目
- 需要快速加载的静态资源
- H5、小程序等前端项目

#### 实现步骤

##### 1. 配置对象存储 Bucket

```bash
# 创建 Bucket（如果还没有）
# 设置访问权限为公共读
```

```json
{
  "Bucket": "h5-demo-assets",
  "Region": "cn-beijing",
  "ACL": "public-read"
}
```

##### 2. 上传资源到对象存储

```python
import oss2

# 配置 Bucket
auth = oss2.Auth('your-access-key-id', 'your-access-key-secret')
bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'h5-demo-assets')

# 上传文件
def upload_to_oss(file_path: str, object_key: str) -> str:
    """
    上传文件到 OSS 并生成公共 URL

    Args:
        file_path: 本地文件路径
        object_key: OSS 对象键（如：images/logo.png）

    Returns:
        公共访问 URL
    """
    # 上传文件
    bucket.put_object_from_file(object_key, file_path)

    # 生成公共 URL（永久可访问）
    public_url = f"https://h5-demo-assets.oss-cn-beijing.aliyuncs.com/{object_key}"

    return public_url

# 示例：上传 MasterGo 导出的图片
logo_url = upload_to_oss("/tmp/logo.png", "images/logo.png")
icon_email_url = upload_to_oss("/tmp/email-icon.png", "images/icon-email.png")
```

##### 3. 在代码中使用

```tsx
// 直接使用公共 URL
<img src="https://h5-demo-assets.oss-cn-beijing.aliyuncs.com/images/logo.png" alt="Logo" />
<img src="https://h5-demo-assets.oss-cn-beijing.aliyuncs.com/images/icon-email.png" alt="Email" />
```

---

### 方案 2：本地资源（当前使用 ⭐⭐⭐⭐）

**原理**：将资源文件放在项目的 `public/` 目录，直接访问

**优点**：
- ✅ 简单直接，无需配置
- ✅ 不依赖外部服务
- ✅ 开发和部署一致

**缺点**：
- ⚠️ 增加项目体积
- ⚠️ 无法利用 CDN 加速
- ⚠️ 多个项目无法共享资源

**适用场景**：
- 小型项目
- 静态资源较少
- 不需要 CDN 加速

---

### 方案 3：CDN + 对象存储签名 URL（需要轮换 ⭐⭐⭐）

**原理**：使用对象存储的签名 URL，定期更新

**优点**：
- ✅ 安全性高
- ✅ 支持 CDN 加速

**缺点**：
- ⚠️ 签名会过期
- ⚠️ 需要定期更新
- ⚠️ 实现复杂

**适用场景**：
- 需要控制访问权限的项目
- 私有项目

---

### 方案 4：MasterGo 云存储（最佳方案 ⭐⭐⭐⭐⭐）

**原理**：使用 MasterGo 提供的资源导出 API，直接获取永久 URL

**优点**：
- ✅ 无需自己配置存储
- ✅ 资源与设计稿绑定
- ✅ 自动更新
- ✅ 支持版本管理

**缺点**：
- ⚠️ 依赖 MasterGo 服务
- ⚠️ 需要集成 MasterGo API

**适用场景**：
- 使用 MasterGo 进行设计
- 需要资源自动更新
- 中大型项目

---

## MasterGo API 集成方案

### 1. 获取 MasterGo API Token

1. 登录 [MasterGo 控制台](https://mastergo.com/)
2. 进入"设置" → "API 管理"
3. 创建新的 API Token
4. 复制 Token（妥善保管）

### 2. 创建 MasterGo API 客户端

```python
"""
MasterGo API 工具
用于读取 MasterGo 设计稿、提取组件信息、导出静态资源
"""
import os
import requests
import json
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class MasterGoAPI(BaseModel):
    """MasterGo API 客户端"""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("MASTERGO_TOKEN")
        self.base_url = "https://api.mastergo.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """获取 MasterGo 文件"""
        url = f"{self.base_url}/files/{file_id}"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取 MasterGo 文件失败: {e}")
            return None

    def export_image(self, file_id: str, node_id: str,
                    format: str = "png", scale: int = 2) -> Optional[str]:
        """
        导出图片并获取永久 URL

        Args:
            file_id: 文件 ID
            node_id: 节点 ID
            format: 导出格式（png, svg, jpg）
            scale: 缩放比例（1, 2, 3）

        Returns:
            图片永久 URL
        """
        url = f"{self.base_url}/files/{file_id}/nodes/{node_id}/export"

        params = {
            "format": format,
            "scale": scale
        }

        try:
            response = requests.post(url, headers=self.headers, json=params, timeout=30)
            response.raise_for_status()
            result = response.json()

            # MasterGo 返回永久 URL
            return result.get("url")

        except requests.exceptions.RequestException as e:
            print(f"导出图片失败: {e}")
            return None

    def get_all_images(self, file_id: str) -> List[Dict[str, str]]:
        """
        获取文件中所有图片资源的永久 URL

        Args:
            file_id: 文件 ID

        Returns:
            图片资源列表 [{id, name, url}, ...]
        """
        file_data = self.get_file(file_id)

        if not file_data:
            return []

        images = []

        # 递归查找所有 IMAGE 类型的节点
        def find_images(node: Dict[str, Any]):
            if node.get("type") == "IMAGE":
                node_id = node.get("id")
                node_name = node.get("name", "unnamed")

                # 导出图片
                url = self.export_image(file_id, node_id, format="png", scale=2)

                if url:
                    images.append({
                        "id": node_id,
                        "name": node_name,
                        "url": url
                    })

            # 递归处理子节点
            if "children" in node:
                for child in node["children"]:
                    find_images(child)

        find_images(file_data.get("document", {}))

        return images
```

### 3. 使用 MasterGo API 提取资源

```python
# 初始化 MasterGo API
api = MasterGoAPI()

# 获取所有图片资源
images = api.get_all_images("file_id_123")

# 输出图片资源
for img in images:
    print(f"名称: {img['name']}")
    print(f"ID: {img['id']}")
    print(f"URL: {img['url']}")
    print("---")
```

### 4. 生成资源映射文件

```python
# 生成资源映射 JSON
resource_map = {
    "logo": {
        "url": "https://static.mastergo.com/xxx/logo.png",
        "type": "image",
        "size": {"width": 120, "height": 40}
    },
    "icon-email": {
        "url": "https://static.mastergo.com/xxx/email.png",
        "type": "icon",
        "size": {"width": 24, "height": 24}
    }
}

# 保存到项目中
with open("src/resources/images.json", "w") as f:
    json.dump(resource_map, f, indent=2)
```

---

## 推荐方案：对象存储公共读 + MasterGo API

**组合方案**：

1. **使用 MasterGo API** 导出设计稿中的静态资源
2. **下载到本地临时目录**
3. **上传到对象存储**（公共读权限）
4. **生成永久 URL**
5. **在代码中引用**

### 实现代码

```python
import os
import requests
import oss2
from pathlib import Path

class MasterGoResourceUploader:
    """MasterGo 资源上传器"""

    def __init__(self, mastergo_token: str, oss_config: dict):
        # MasterGo API
        self.mastergo_token = mastergo_token

        # OSS 配置
        auth = oss2.Auth(oss_config['access_key_id'], oss_config['access_key_secret'])
        self.bucket = oss2.Bucket(
            auth,
            oss_config['endpoint'],
            oss_config['bucket_name']
        )

    def extract_resources(self, file_id: str) -> List[Dict]:
        """从 MasterGo 提取所有资源"""
        api = MasterGoAPI(self.mastergo_token)
        return api.get_all_images(file_id)

    def download_resource(self, url: str, local_path: str) -> bool:
        """下载资源到本地"""
        try:
            response = requests.get(url, timeout=30)
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            print(f"下载失败: {e}")
            return False

    def upload_to_oss(self, local_path: str, object_key: str) -> str:
        """上传到 OSS 并返回公共 URL"""
        self.bucket.put_object_from_file(object_key, local_path)

        # 生成公共 URL（永久可访问）
        return f"https://{self.bucket.bucket_name}.{self.bucket.endpoint.split('//')[1]}/{object_key}"

    def process_all_resources(self, file_id: str) -> Dict[str, str]:
        """处理所有资源：提取 → 下载 → 上传 → 生成 URL"""
        # 1. 提取资源
        resources = self.extract_resources(file_id)

        result = {}

        # 临时目录
        temp_dir = Path("/tmp/mastergo_assets")
        temp_dir.mkdir(exist_ok=True)

        for resource in resources:
            # 生成文件名
            filename = f"{resource['name']}.png"
            local_path = temp_dir / filename
            object_key = f"images/{filename}"

            # 2. 下载
            if not self.download_resource(resource['url'], str(local_path)):
                continue

            # 3. 上传
            url = self.upload_to_oss(str(local_path), object_key)

            # 4. 保存结果
            result[resource['name']] = url

            # 5. 清理临时文件
            local_path.unlink()

        return result

# 使用示例
uploader = MasterGoResourceUploader(
    mastergo_token="your_mastergo_token",
    oss_config={
        'access_key_id': 'your_oss_access_key',
        'access_key_secret': 'your_oss_secret',
        'endpoint': 'https://oss-cn-beijing.aliyuncs.com',
        'bucket_name': 'h5-demo-assets'
    }
)

# 处理所有资源
resources = uploader.process_all_resources("file_id_123")

# 输出结果
print(json.dumps(resources, indent=2))
```

---

## 配置文件

### config/mastergo_config.json

```json
{
  "token": "your_mastergo_token",
  "oss": {
    "access_key_id": "your_oss_access_key",
    "access_key_secret": "your_oss_secret",
    "endpoint": "https://oss-cn-beijing.aliyuncs.com",
    "bucket_name": "h5-demo-assets",
    "region": "cn-beijing"
  },
  "export": {
    "format": "png",
    "scale": 2,
    "quality": 90
  }
}
```

### config/resource_mapping.json

```json
{
  "logo": "https://h5-demo-assets.oss-cn-beijing.aliyuncs.com/images/logo.png",
  "icon-email": "https://h5-demo-assets.oss-cn-beijing.aliyuncs.com/images/email.png",
  "icon-lock": "https://h5-demo-assets.oss-cn-beijing.aliyuncs.com/images/lock.png",
  "icon-eye": "https://h5-demo-assets.oss-cn-beijing.aliyuncs.com/images/eye.png",
  "icon-eye-closed": "https://h5-demo-assets.oss-cn-beijing.aliyuncs.com/images/eye-closed.png"
}
```

---

## 总结

### 推荐方案选择

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 小型项目 | 方案 2：本地资源 | 简单直接 |
| 中型项目 | 方案 1：对象存储公共读 | 永久可访问，支持 CDN |
| 大型项目 | 方案 4：MasterGo 云存储 | 自动更新，版本管理 |
| 私有项目 | 方案 3：CDN + 签名 URL | 安全性高 |

### 最佳实践

1. **使用对象存储公共读** - 配置简单，永久可访问
2. **集成 MasterGo API** - 自动提取和导出资源
3. **生成资源映射文件** - 便于管理和引用
4. **使用 CDN 加速** - 提升加载速度

### 下一步

1. 配置对象存储 Bucket（公共读权限）
2. 获取 MasterGo API Token
3. 创建资源上传工具
4. 集成到工作流中
5. 自动生成资源映射文件

---

## 相关文档

- [MasterGo API 文档](https://mastergo.com/api)
- [阿里云 OSS 文档](https://help.aliyun.com/product/31815.html)
- [对象存储公共读配置指南](https://help.aliyun.com/document_detail/100676.html)
