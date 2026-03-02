# MasterGo 集成指南

## 概述

MasterGo 集成是前端自动化工作流的核心功能之一，用于解析 MasterGo 设计稿并提取 UI 组件、布局结构和静态资源信息，为代码生成提供基础数据。

**为什么选择 MasterGo 而不是 Figma？**

1. **API 限流问题**：Figma API 存在严格的限流机制（429 Too Many Requests），影响自动化流程的稳定性
2. **静态资源访问**：Figma 的图片 URL 存在签名过期问题（403 Forbidden），导致资源无法长期访问
3. **MasterGo 优势**：
   - 更宽松的 API 限流政策
   - 支持对象存储公共读配置
   - 更适合国内开发环境

## 功能特性

### 1. 设计稿解析
- ✅ 从 MasterGo URL 读取设计稿
- ✅ 支持特定节点解析（通过 node-id）
- ✅ 支持页面级解析
- ✅ 自动识别组件类型和属性

### 2. 组件识别
- ✅ 支持多种组件类型（Button、Input、Text、Image、Container 等）
- ✅ 提取组件属性（文字、颜色、尺寸、圆角、边框等）
- ✅ 递归处理嵌套组件
- ✅ 识别组件可见性

### 3. 布局分析
- ✅ 识别布局类型（垂直、水平、网格、绝对定位）
- ✅ 提取间距信息
- ✅ 提取内边距
- ✅ 识别对齐方式

### 4. 静态资源提取
- ✅ 识别图片资源
- ✅ 识别图标资源
- ✅ 提取资源信息（名称、格式、倍数）
- ✅ 支持多倍图导出（1x、2x、3x）
- ✅ 上传到对象存储（CDN）并生成签名 URL

### 5. 颜色处理
- ✅ 自动转换 MasterGo RGB 颜色到 Hex 格式
- ✅ 支持透明度处理

## 前置条件

### 1. 获取 MasterGo Token

1. 登录 MasterGo (https://mastergo.com)
2. 进入个人设置
3. 选择 "API Tokens" 或 "个人访问令牌"
4. 点击 "Create new token"
5. 复制生成的 Token

### 2. 配置环境变量

**方式 1：设置环境变量**
```bash
export MASTERGO_TOKEN=your_mastergo_token_here
```

**方式 2：在配置文件中设置**
编辑 `config/mastergo_config.json`：
```json
{
  "token": "your_mastergo_token_here",
  "base_url": "https://api.mastergo.com/openapi",
  "default_export_format": "png",
  "default_scales": [1, 2, 3],
  "timeout": 30
}
```

**方式 3：在代码中传递**
```python
from tools.mastergo_api import MasterGoAPI

mastergo = MasterGoAPI(token="your_mastergo_token_here")
```

## 使用方式

### 1. 基本用法

```python
from tools.mastergo_api import MasterGoAPI

# 初始化 API
api = MasterGoAPI()

# 解析设计稿 URL
file_id, node_id = api.parse_mastergo_url(
    "https://mastergo.com/design/7120216615013610"
)

# 获取文件数据
file_data = api.get_file(file_id, depth=None)

# 获取图片资源
images = api.get_all_images(file_id)

for img in images:
    print(f"图片: {img['name']}")
    print(f"URL: {img['url']}")
```

### 2. 在工作流中使用

设计稿解析节点会自动使用 MasterGo API：

```python
from graphs.state import DesignParseInput

# 创建输入
input_state = DesignParseInput(
    mastergo_url="https://mastergo.com/design/7120216615013610",
    page_name="Page 1"
)

# 调用节点
output = design_parse_node(input_state, config, runtime)

# 输出包含：
# - components: 组件列表
# - layout: 布局信息
# - static_assets: 静态资源列表
# - mastergo_summary: 摘要信息
```

### 3. 资产上传

```python
from src.tools.mastergo_asset_uploader import MasterGoAssetUploader

# 创建上传器
uploader = MasterGoAssetUploader()

# 处理资产
result = uploader.process_assets(
    file_id="7120216615013610",
    node_id=None,
    prefix="mastergo/assets/"
)

print(f"总计: {result.total_count}")
print(f"成功: {result.success_count}")
print(f"失败: {result.failed_count}")

# 保存结果
import json
with open("mastergo_assets_result.json", "w") as f:
    json.dump({
        "total": result.total_count,
        "success": result.success_count,
        "failed": result.failed_count,
        "assets": [
            {
                "node_id": a.node_id,
                "node_name": a.node_name,
                "cdn_url": a.cdn_url
            }
            for a in result.assets
        ]
    }, f, indent=2)

# 清理临时文件
uploader.cleanup()
```

## URL 格式

MasterGo 支持以下 URL 格式：

1. **设计稿链接**：
   ```
   https://mastergo.com/design/7120216615013610
   https://mastergo.com/file/7120216615013610
   ```

2. **特定节点链接**：
   ```
   https://mastergo.com/design/7120216615013610?node=xxx
   ```

## 配置文件说明

`config/mastergo_config.json` 包含以下配置：

```json
{
  "token": "your_mastergo_token_here",
  "base_url": "https://api.mastergo.com/openapi",
  "default_export_format": "png",
  "default_scales": [1, 2, 3],
  "timeout": 30,
  "component_mappings": {
    "button": {
      "keywords": ["button", "btn", "submit", "action"],
      "default_variant": "primary"
    },
    "input": {
      "keywords": ["input", "field", "textbox", "entry"],
      "default_placeholder": "Please enter text"
    }
  },
  "color_mappings": {
    "primary": "#007AFF",
    "secondary": "#5AC8FA"
  }
}
```

### 配置项说明

| 配置项 | 说明 |
|-------|------|
| `token` | MasterGo API 访问令牌 |
| `base_url` | API 基础 URL |
| `default_export_format` | 默认导出格式（png/svg） |
| `default_scales` | 默认导出倍数 |
| `timeout` | 请求超时时间（秒） |
| `component_mappings` | 组件识别规则 |
| `color_mappings` | 颜色映射规则 |

## 静态资源处理方案

### 方案 1：对象存储公共读（推荐）

1. 将 MasterGo 中的图片上传到对象存储
2. 设置存储桶为公共读
3. 直接使用公共 URL 访问资源

```python
# 上传到对象存储
storage.upload_file(
    file_content=image_data,
    file_name=f"mastergo/assets/{filename}",
    content_type="image/png",
    acl="public-read"
)

# 公共 URL
public_url = f"{storage.endpoint}/{bucket_name}/mastergo/assets/{filename}"
```

### 方案 2：签名 URL

1. 将 MasterGo 中的图片上传到对象存储
2. 生成带签名的临时 URL
3. 在签名有效期内访问资源

```python
# 生成签名 URL
signed_url = storage.generate_presigned_url(
    key="mastergo/assets/example.png",
    expire_time=86400 * 30  # 30 天
)
```

### 方案 3：MasterGo 云存储

MasterGo 本身提供云存储功能，可以直接使用 MasterGo 返回的 URL（如果支持公共访问）。

## 迁移指南：从 Figma 到 MasterGo

### 1. 更新环境变量

```bash
# 删除 Figma Token
unset FIGMA_TOKEN

# 设置 MasterGo Token
export MASTERGO_TOKEN=your_mastergo_token_here
```

### 2. 更新配置文件

- `config/figma_config.json` → `config/mastergo_config.json`

### 3. 更新节点引用

```python
# 旧的
from tools.figma_api import FigmaAPI
from graphs.state import FigmaAssetUploadInput

# 新的
from src.tools.mastergo_api import MasterGoAPI
from graphs.state import MasterGoAssetUploadInput
```

### 4. 更新工作流

在工作流配置中，将 `figma_asset_upload` 节点替换为 `mastergo_asset_upload` 节点。

### 5. 更新 GitHub Issue

如果 GitHub Issue 中包含 Figma URL，更新为 MasterGo URL：
```
# 设计稿链接
- Figma: https://www.figma.com/file/abc123/My-Design
+ MasterGo: https://mastergo.com/design/7120216615013610
```

## 故障排查

### 问题 1：API Token 无效

**症状**：
```
Error: 401 Unauthorized
```

**解决方案**：
1. 检查 Token 是否正确
2. 检查 Token 是否已过期
3. 重新生成 Token

### 问题 2：无法解析 URL

**症状**：
```
Error: Invalid MasterGo URL
```

**解决方案**：
1. 检查 URL 格式是否正确
2. 确保使用 `https://mastergo.com/design/` 或 `https://mastergo.com/file/`
3. 确保文件 ID 存在

### 问题 3：图片下载失败

**症状**：
```
Error: Failed to download image
```

**解决方案**：
1. 检查网络连接
2. 检查图片 URL 是否有效
3. 检查文件权限

### 问题 4：对象存储上传失败

**症状**：
```
Error: Failed to upload to CDN
```

**解决方案**：
1. 检查对象存储配置
2. 检查访问权限
3. 检查存储桶是否存在

## 最佳实践

1. **Token 安全**
   - 不要将 Token 提交到代码仓库
   - 使用环境变量或配置文件
   - 定期轮换 Token

2. **缓存策略**
   - 对设计稿数据进行缓存
   - 避免重复解析相同的设计稿
   - 使用文件修改时间判断是否需要重新解析

3. **错误处理**
   - 捕获并记录所有 API 错误
   - 实现重试机制
   - 提供友好的错误提示

4. **资源管理**
   - 上传完成后清理临时文件
   - 使用合理的 CDN URL 有效期
   - 定期清理未使用的资源

## 相关文档

- [MasterGo API 文档](https://mastergo.com/openapi)
- [对象存储集成指南](./STORAGE_INTEGRATION_GUIDE.md)
- [工作流配置指南](./WORKFLOW_CONFIG_GUIDE.md)
