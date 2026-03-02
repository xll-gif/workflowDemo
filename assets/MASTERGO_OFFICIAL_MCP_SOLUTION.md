# MasterGo 集成解决方案（基于官方 Magic MCP）

## 📋 问题诊断

### 当前问题
1. 原始代码尝试连接 `api.mastergo.cn`，连接超时
2. 缺少官方 API 文档和认证方式
3. 未找到合适的 MasterGo Python SDK

### 根本原因
1. **API 端点错误**：MasterGo 官方 API 基础 URL 应该是 `https://api.mastergo.com`，而非 `api.mastergo.cn`
2. **集成方式错误**：MasterGo 官方提供了 MCP (Model Context Protocol) 服务器，应该使用 MCP 而非直接调用 REST API
3. **缺少认证令牌**：需要从 MasterGo 个人设置中获取 MG_MCP_TOKEN

## ✅ 推荐解决方案：使用官方 MasterGo Magic MCP

### 方案概述
MasterGo 官方提供了 **MasterGo Magic MCP** 服务器，这是一个独立的 MCP 服务，专门用于将 MasterGo 设计工具与 AI 模型连接起来。

### 核心优势
- ✅ **官方支持**：MasterGo 官方提供和维护
- ✅ **开箱即用**：无需复杂的 API 集成，通过 MCP 协议直接访问
- ✅ **功能完整**：支持从 MasterGo 设计文件中检索 DSL 数据
- ✅ **简单配置**：只需要一个令牌即可使用

## 🔧 集成步骤

### 步骤 1：获取 MasterGo 访问令牌

1. 访问 [https://mastergo.com](https://mastergo.com)
2. 登录您的 MasterGo 账号
3. 进入 **个人设置**
4. 点击 **安全设置** 选项卡
5. 找到 **个人访问令牌**
6. 点击 **生成令牌**
7. 复制生成的令牌（MG_MCP_TOKEN）

### 步骤 2：安装 MasterGo Magic MCP

```bash
# 使用 npx 直接运行（推荐）
npx @mastergo/magic-mcp --token=YOUR_TOKEN --url=https://mastergo.com

# 或者全局安装
npm install -g @mastergo/magic-mcp
mastergo-magic-mcp --token=YOUR_TOKEN --url=https://mastergo.com
```

### 步骤 3：配置 MCP 服务器

在您的 MCP 客户端配置文件中（例如 Claude Desktop 的配置文件）：

```json
{
  "mcpServers": {
    "mastergo-magic-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "@mastergo/magic-mcp",
        "--token=YOUR_MG_MCP_TOKEN",
        "--url=https://mastergo.com"
      ],
      "env": {}
    }
  }
}
```

### 步骤 4：使用 MCP 工具

配置完成后，MCP 服务器会提供以下工具：

- **读取设计文件**：从 MasterGo 文件中检索 DSL 数据
- **解析设计元素**：解析设计稿中的图层、组件等
- **提取资源信息**：提取图片、图标等资源信息

## 📝 工作流集成方案

### 方案 A：直接使用 MCP（推荐）

```python
# src/graphs/nodes/design_parse_node.py

def design_parse_node(state: DesignParseInput, config: RunnableConfig, runtime: Runtime[Context]) -> DesignParseOutput:
    """
    title: MasterGo 设计解析
    desc: 使用 MasterGo Magic MCP 解析设计稿
    """
    ctx = runtime.context

    # 通过 MCP 调用 MasterGo 工具
    # （具体的 MCP 调用方式需要根据您的 MCP 客户端实现）
    result = ctx.mcp.call_tool("mastergo-magic-mcp", "parse_design", {
        "url": state.mastergo_url
    })

    # 解析结果
    design_data = parse_mcp_result(result)

    return DesignParseOutput(
        design_data=design_data,
        components=extract_components(design_data),
        assets=extract_assets(design_data)
    )
```

### 方案 B：使用 MCP 作为数据源 + 本地处理

```python
# 1. 通过 MCP 获取设计数据
def get_design_from_mastergo(url: str) -> dict:
    """从 MasterGo 获取设计数据"""
    # 调用 MCP 工具获取 DSL 数据
    return mcp_client.call("get_design", {"url": url})

# 2. 本地解析设计数据
def parse_mastergo_design(dsl_data: dict) -> dict:
    """解析 MasterGo DSL 数据"""
    # 解析组件、图层、样式等
    components = []
    assets = []

    for node in dsl_data.get("nodes", []):
        if node["type"] == "COMPONENT":
            components.append({
                "name": node["name"],
                "props": extract_props(node)
            })
        elif node["type"] in ["IMAGE", "ICON"]:
            assets.append({
                "type": node["type"],
                "url": node["url"]
            })

    return {
        "components": components,
        "assets": assets,
        "styles": extract_styles(dsl_data)
    }
```

## 🔍 MCP 工具列表

根据官方文档，MasterGo Magic MCP 提供以下工具：

| 工具名称 | 功能描述 | 参数 |
|---------|---------|------|
| `get_design` | 获取设计文件 DSL 数据 | `url`: 设计文件 URL |
| `list_components` | 列出设计中的所有组件 | `url`: 设计文件 URL |
| `get_component` | 获取特定组件的详细信息 | `url`: 设计文件 URL, `component_id`: 组件 ID |
| `export_assets` | 导出设计中的资源（图片、图标等） | `url`: 设计文件 URL, `asset_types`: 资源类型列表 |

## 📊 数据流转

```
用户输入（MasterGo URL）
    ↓
通过 MCP 调用 MasterGo Magic MCP
    ↓
获取设计 DSL 数据
    ↓
解析设计数据（组件、图层、资源）
    ↓
提取组件信息
    ↓
提取资源信息（图片、图标）
    ↓
上传资源到对象存储
    ↓
生成代码
```

## 🌐 网络配置

### 当前环境测试结果

根据之前的测试：
- ❌ `api.mastergo.cn` - 无法连接（可能是错误的域名）
- ✅ `mastergo.com` - 官方网站，可访问

### 建议配置

```bash
# 设置环境变量
export MASTERGO_API_URL="https://mastergo.com"
export MASTERGO_API_TOKEN="YOUR_MG_MCP_TOKEN"

# 或者在配置文件中
# config/mastergo_config.json
{
  "api_url": "https://mastergo.com",
  "mcp_token": "YOUR_MG_MCP_TOKEN",
  "mcp_command": "npx @mastergo/magic-mcp"
}
```

## 📚 官方资源

### 文档链接
- MasterGo 官网: https://mastergo.com
- MasterGo 开发者平台: https://developers.mastergo.com/guide/
- MasterGo Magic MCP GitHub: https://github.com/mastergo-design/mastergo-magic-mcp
- 腾讯云 MCP 市场: https://cloud.tencent.com/developer/mcp/server/10019
- 魔搭社区: https://modelscope.cn/mcp/servers/@mastergo-design/mastergo-magic-mcp

### 教程
- MasterGo 入门指南: https://mastergocn.com/guide.html
- 开发者教程: https://developers.mastergo.com/guide/tutorials.html
- MCP 使用示例: https://mastergo.com/file/155675508499265?page_id=158:0002

## 🚀 下一步行动

### 立即行动
1. **获取 MG_MCP_TOKEN**：按照步骤 1 获取访问令牌
2. **测试 MCP 连接**：使用 npx 命令测试 MCP 服务器
3. **集成到工作流**：更新 `design_parse_node.py` 使用 MCP

### 后续优化
1. **缓存设计数据**：避免重复获取相同的设计文件
2. **增量更新**：只更新发生变化的设计元素
3. **错误处理**：完善网络错误和认证错误的处理

## ⚠️ 注意事项

1. **令牌安全**：不要将 MG_MCP_TOKEN 提交到版本控制系统
2. **限流控制**：MasterGo API 可能有调用频率限制
3. **网络代理**：如果在网络受限的环境中，可能需要配置代理
4. **版本兼容**：确保 MCP 服务器版本与客户端兼容

## 📞 技术支持

如果遇到问题，可以参考：
- MasterGo 官方文档
- MCP 官方文档: https://modelcontextprotocol.io/
- MasterGo GitHub Issues: https://github.com/mastergo-design/mastergo-magic-mcp/issues

## 🔄 备选方案

如果 MCP 方案不可行，可以考虑：

### 方案 C：使用 MasterGo 插件 API

MasterGo 提供了插件开发 API，可以开发一个 MasterGo 插件来导出设计数据。

**优点**：
- 功能最完整
- 官方支持
- 可以访问所有设计数据

**缺点**：
- 需要安装 MasterGo 客户端
- 需要在 MasterGo 中运行插件
- 不适合自动化流程

### 方案 D：使用设计文件导出功能

MasterGo 支持导出设计文件（如 JSON 格式），然后解析导出的文件。

**优点**：
- 简单直接
- 不需要 API 调用
- 可以离线使用

**缺点**：
- 需要手动导出
- 不适合自动化流程
- 可能不是最新版本

## 📝 总结

**推荐方案**：使用官方 **MasterGo Magic MCP**

**原因**：
1. 官方支持，维护有保障
2. 开箱即用，配置简单
3. 功能完整，满足需求
4. 与 AI 模型集成度高

**实施步骤**：
1. 获取 MG_MCP_TOKEN
2. 安装 MCP 服务器
3. 配置 MCP 客户端
4. 集成到工作流
5. 测试验证

---

*文档版本：1.0*
*更新日期：2026-02-28*
