# 静态资源处理完整指南

## 概述

本指南详细说明在工作流自动化系统中如何处理静态资源（图片、视频等），包括从 MasterGo 下载、上传到对象存储、以及多平台适配的全流程。

## 📋 目录

1. [工作流程](#工作流程)
2. [存储后端](#存储后端)
3. [上传工具](#上传工具)
4. [使用示例](#使用示例)
5. [故障排查](#故障排查)

## 🔄 工作流程

```
MasterGo 设计稿
    ↓
download_file() 下载到本地
    ↓
格式转换/优化 (可选)
    ↓
上传到对象存储 (OSS/COS/Mock)
    ↓
返回 CDN URL
```

## 🗄️ 存储后端

系统支持三种存储后端，通过环境变量 `STORAGE_BACKEND` 切换：

### 1. 阿里云 OSS (Alibaba Cloud OSS)

**配置**：
```bash
STORAGE_BACKEND=oss
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET=your-bucket-name
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
```

**特点**：
- ✅ 使用长期密钥
- ✅ 配置简单
- ❌ 安全性相对较低

### 2. 腾讯云 COS (Tencent Cloud COS)

**配置**：
```bash
STORAGE_BACKEND=cos
TENCENT_API_BASE_URL=https://api.example.com
TENCENT_SCENE_NAME=frontend-automation
TENCENT_BUSINESS_NAME=workflow
TENCENT_MODE=dev
TENCENT_TOKEN=your_token_here
TENCENT_SECRET_KEY=your_secret_key_here
```

**特点**：
- ✅ 使用 STS 临时凭证（更安全）
- ✅ 支持进度回调
- ✅ 支持多环境（dev/gray/prod）
- ✅ 自动刷新凭证
- ⚠️ 需要后端 API 支持

**详细配置**：参见 [TENCENT_COS_INTEGRATION_GUIDE.md](TENCENT_COS_INTEGRATION_GUIDE.md)

### 3. Mock 模式（测试用）

**配置**：
```bash
STORAGE_BACKEND=mock
```

**特点**：
- ✅ 无需实际存储
- ✅ 生成模拟 URL
- ⚠️ 仅用于开发/测试

## 🛠️ 上传工具

### TencentCOSUploader（腾讯云 COS）

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

print(result.url)
```

### OSSUploader（阿里云 OSS）

```python
from tools.oss_uploader import OSSUploader

# 创建上传器
uploader = OSSUploader(
    access_key_id="your_access_key_id",
    access_key_secret="your_access_key_secret",
    bucket="your-bucket-name",
    endpoint="https://oss-cn-hangzhou.aliyuncs.com"
)

# 上传文件
result = uploader.upload_file(
    file_path="/path/to/image.png",
    key="assets/user_avatar.png"
)

print(result.url)
```

### MockUploader（测试用）

```python
from tools.mock_uploader import MockUploader

# 创建上传器
uploader = MockUploader()

# 上传文件
result = uploader.upload_file(
    file_path="/path/to/image.png",
    key="assets/user_avatar.png"
)

print(result.url)  # https://mock-oss.example.com/assets/user_avatar.png
```

## 💻 使用示例

### 示例 1：上传单个图片

```python
from tools.cos_uploader import TencentCOSUploader
import os

# 初始化上传器
uploader = TencentCOSUploader(
    api_base_url=os.getenv("TENCENT_API_BASE_URL"),
    scene_name=os.getenv("TENCENT_SCENE_NAME"),
    business_name=os.getenv("TENCENT_BUSINESS_NAME"),
    mode=os.getenv("TENCENT_MODE")
)

# 上传图片
result = uploader.upload_file(
    file_path="/tmp/design.png",
    filename="design.png",
    prefix="designs/",
    on_progress=lambda p: print(f"上传进度: {p}%")
)

if result.success:
    print(f"✅ 上传成功: {result.url}")
else:
    print(f"❌ 上传失败: {result.error}")
```

### 示例 2：批量上传多张图片

```python
from tools.cos_uploader import TencentCOSUploader
import os

uploader = TencentCOSUploader(...)

# 批量上传
image_files = [
    "/tmp/image1.png",
    "/tmp/image2.png",
    "/tmp/image3.png"
]

results = []
for i, file_path in enumerate(image_files):
    print(f"正在上传第 {i+1}/{len(image_files)} 张图片...")

    result = uploader.upload_file(
        file_path=file_path,
        filename=os.path.basename(file_path),
        prefix="batch/"
    )

    results.append(result)

    if result.success:
        print(f"✅ {os.path.basename(file_path)}: {result.url}")
    else:
        print(f"❌ {os.path.basename(file_path)}: {result.error}")

# 统计结果
success_count = sum(1 for r in results if r.success)
print(f"\n总计: {success_count}/{len(results)} 上传成功")
```

### 示例 3：根据环境选择存储后端

```python
import os

def get_uploader():
    """根据环境变量获取上传器"""
    backend = os.getenv("STORAGE_BACKEND", "mock")

    if backend == "cos":
        from tools.cos_uploader import TencentCOSUploader
        return TencentCOSUploader(
            api_base_url=os.getenv("TENCENT_API_BASE_URL"),
            scene_name=os.getenv("TENCENT_SCENE_NAME"),
            business_name=os.getenv("TENCENT_BUSINESS_NAME"),
            mode=os.getenv("TENCENT_MODE")
        )
    elif backend == "oss":
        from tools.oss_uploader import OSSUploader
        return OSSUploader(
            access_key_id=os.getenv("OSS_ACCESS_KEY_ID"),
            access_key_secret=os.getenv("OSS_ACCESS_KEY_SECRET"),
            bucket=os.getenv("OSS_BUCKET"),
            endpoint=os.getenv("OSS_ENDPOINT")
        )
    else:
        from tools.mock_uploader import MockUploader
        return MockUploader()

# 使用
uploader = get_uploader()
result = uploader.upload_file("test.png", "test.png")
print(result.url)
```

## 🧪 测试

### 测试工具安装

```bash
# 腾讯云 COS SDK
pip install cos-python-sdk-v5

# 阿里云 OSS SDK
pip install oss2
```

### 测试脚本

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_cos_upload():
    """测试腾讯云 COS 上传"""
    from tools.cos_uploader import TencentCOSUploader

    uploader = TencentCOSUploader(
        api_base_url=os.getenv("TENCENT_API_BASE_URL"),
        scene_name=os.getenv("TENCENT_SCENE_NAME"),
        business_name=os.getenv("TENCENT_BUSINESS_NAME"),
        mode=os.getenv("TENCENT_MODE")
    )

    # 创建测试文件
    test_file = "/tmp/test_cos_upload.txt"
    with open(test_file, "w") as f:
        f.write("Test file for COS upload")

    try:
        result = uploader.upload_file(
            file_path=test_file,
            filename="test_cos_upload.txt",
            prefix="test/"
        )

        if result.success:
            print(f"✅ COS 上传测试成功: {result.url}")
            return True
        else:
            print(f"❌ COS 上传测试失败: {result.error}")
            return False
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)

def test_oss_upload():
    """测试阿里云 OSS 上传"""
    from tools.oss_uploader import OSSUploader

    uploader = OSSUploader(
        access_key_id=os.getenv("OSS_ACCESS_KEY_ID"),
        access_key_secret=os.getenv("OSS_ACCESS_KEY_SECRET"),
        bucket=os.getenv("OSS_BUCKET"),
        endpoint=os.getenv("OSS_ENDPOINT")
    )

    # 创建测试文件
    test_file = "/tmp/test_oss_upload.txt"
    with open(test_file, "w") as f:
        f.write("Test file for OSS upload")

    try:
        result = uploader.upload_file(
            file_path=test_file,
            key="test/test_oss_upload.txt"
        )

        if result.success:
            print(f"✅ OSS 上传测试成功: {result.url}")
            return True
        else:
            print(f"❌ OSS 上传测试失败: {result.error}")
            return False
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)

def test_mock_upload():
    """测试 Mock 上传"""
    from tools.mock_uploader import MockUploader

    uploader = MockUploader()

    result = uploader.upload_file(
        file_path="/tmp/mock_file.txt",
        key="test/mock_file.txt"
    )

    if result.success:
        print(f"✅ Mock 上传测试成功: {result.url}")
        return True
    else:
        print(f"❌ Mock 上传测试失败: {result.error}")
        return False

# 运行测试
if __name__ == "__main__":
    backend = os.getenv("STORAGE_BACKEND", "mock")

    print(f"测试存储后端: {backend}")
    print("=" * 50)

    if backend == "cos":
        test_cos_upload()
    elif backend == "oss":
        test_oss_upload()
    else:
        test_mock_upload()
```

## 🔍 故障排查

### 常见问题

**1. ModuleNotFoundError: No module named 'cos'**

```bash
pip install cos-python-sdk-v5
```

**2. 获取上传凭证失败（COS）**

- 检查 `TENCENT_API_BASE_URL` 是否正确
- 检查后端 API 是否正常运行
- 检查网络连接
- 检查 `X-Secret-Key` 或 cookie 中的密钥

**3. OSS 认证失败**

- 检查 AccessKey ID 和 Secret 是否正确
- 检查 Bucket 名称是否正确
- 检查 Endpoint 是否正确

**4. 环境变量未生效**

```bash
# 重新加载 .env
export $(cat .env | xargs)

# 或使用 python-dotenv
from dotenv import load_dotenv
load_dotenv()
```

**5. 上传进度回调不触发**

- 确保文件大小大于 10KB（小文件上传太快，进度回调可能不触发）
- 使用大文件测试（>1MB）

## 📚 相关文档

- [TencentCOSUploader 详细配置](TENCENT_COS_INTEGRATION_GUIDE.md)
- [wptresource 仓库分析](WPTRESOURCE_ANALYSIS.md)
- [MasterGo MCP 集成](MASTERGO_MCP_INTEGRATION.md)

## 🎯 最佳实践

1. **生产环境使用腾讯云 COS + STS**：更安全，支持多环境
2. **开发环境使用 Mock 模式**：快速测试，无需实际存储
3. **使用进度回调**：提供更好的用户体验
4. **错误处理**：捕获并记录上传失败的情况
5. **批量上传**：使用循环或异步上传多个文件
6. **缓存凭证**：腾讯云 COS 会自动缓存和刷新临时凭证

## 📝 版本历史

- **v2.0** (2024-01): 新增腾讯云 COS 支持
- **v1.0** (2023-12): 初始版本，支持阿里云 OSS
