# 在工作流中集成 MasterGo MCP 服务器

## 什么是 MCP (Model Context Protocol)？

**MCP** 是一个开放标准，用于让 AI 模型访问外部数据和服务。

**简单理解**：
- MCP 就像一个"翻译器"
- 把 MasterGo API 转换成 AI 模型能理解的格式
- 让 AI 可以直接调用 MasterGo 的功能

---

## 架构设计

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│             │  MCP    │  MasterGo   │  API    │  MasterGo   │
│  LangGraph  │ ←────→ │   MCP 服务器 │ ←────→ │    API      │
│   工作流    │         │             │         │  服务端     │
└─────────────┘         └─────────────┘         └─────────────┘
```

---

## 集成步骤

### 方案 A：使用官方 MasterGo MCP（如果有）

检查 MasterGo 是否提供官方 MCP 服务器：
1. 访问 https://mastergo.com/mcp
2. 查看 MCP 服务器地址
3. 配置到工作流中

### 方案 B：创建自定义 MasterGo MCP 服务器

如果 MasterGo 没有官方 MCP，我们可以创建一个。

---

## 实现方案 B：创建自定义 MCP 服务器

### 步骤 1：安装 MCP 依赖

```bash
pip install mcp
```

### 步骤 2：创建 MCP 服务器

创建 `src/mcp/mastergo_server.py`：

```python
"""
MasterGo MCP 服务器
将 MasterGo API 包装成 MCP 服务器
"""
from mcp.server import Server
from mcp.types import Tool, TextContent
import os
import json

# 导入现有的 MasterGo API 工具
from tools.mastergo_api import MasterGoAPI

# 创建 MCP 服务器
app = Server("mastergo-mcp-server")

# 初始化 MasterGo API
mastergo_api = MasterGoAPI()

@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的 MasterGo 工具"""
    return [
        Tool(
            name="parse_mastergo_url",
            description="解析 MasterGo URL，提取文件 ID 和节点 ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "MasterGo 设计稿 URL"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="get_mastergo_file",
            description="获取 MasterGo 文件信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "MasterGo 文件 ID"
                    },
                    "depth": {
                        "type": "integer",
                        "description": "遍历深度（可选）"
                    }
                },
                "required": ["file_id"]
            }
        ),
        Tool(
            name="get_mastergo_images",
            description="获取 MasterGo 文件中的所有图片资源",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "MasterGo 文件 ID"
                    }
                },
                "required": ["file_id"]
            }
        ),
        Tool(
            name="upload_assets_to_cdn",
            description="上传 MasterGo 资产到 CDN",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "MasterGo 文件 ID"
                    },
                    "prefix": {
                        "type": "string",
                        "description": "上传前缀"
                    }
                },
                "required": ["file_id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """调用 MasterGo 工具"""

    try:
        if name == "parse_mastergo_url":
            url = arguments["url"]
            file_id, node_id = mastergo_api.parse_mastergo_url(url)
            result = {
                "file_id": file_id,
                "node_id": node_id
            }
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False)
            )]

        elif name == "get_mastergo_file":
            file_id = arguments["file_id"]
            depth = arguments.get("depth")
            file_data = mastergo_api.get_file(file_id, depth=depth)
            return [TextContent(
                type="text",
                text=json.dumps(file_data, ensure_ascii=False, indent=2)
            )]

        elif name == "get_mastergo_images":
            file_id = arguments["file_id"]
            images = mastergo_api.get_all_images(file_id)
            return [TextContent(
                type="text",
                text=json.dumps(images, ensure_ascii=False, indent=2)
            )]

        elif name == "upload_assets_to_cdn":
            file_id = arguments["file_id"]
            prefix = arguments.get("prefix", "mastergo/assets/")
            from tools.mastergo_asset_uploader import MasterGoAssetUploader
            uploader = MasterGoAssetUploader(mastergo_api)
            result = uploader.process_assets(file_id, prefix=prefix)
            return [TextContent(
                type="text",
                text=json.dumps({
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
                }, ensure_ascii=False, indent=2)
            )]

        else:
            return [TextContent(
                type="text",
                text=f"未知工具: {name}"
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"错误: {str(e)}"
        )]

# 启动服务器
if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )

    asyncio.run(main())
```

### 步骤 3：创建 MCP 配置文件

创建 `.mcp/config.json`：

```json
{
  "mcpServers": {
    "mastergo": {
      "command": "python",
      "args": ["src/mcp/mastergo_server.py"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src",
        "MASTERGO_TOKEN": "mg_03992ef8773c4a75902b337bf0e2c208"
      }
    }
  }
}
```

### 步骤 4：在工作流中使用 MCP

更新 `src/graphs/nodes/design_parse_node.py`：

```python
"""
设计稿解析节点（使用 MCP）
"""
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

async def design_parse_with_mcp(mastergo_url: str):
    """使用 MCP 调用 MasterGo API"""

    # 创建 MCP 客户端
    server_params = StdioServerParameters(
        command="python",
        args=["src/mcp/mastergo_server.py"],
        env={
            "PYTHONPATH": "/workspace/projects/src",
            "MASTERGO_TOKEN": os.getenv("MASTERGO_TOKEN", "mg_03992ef8773c4a75902b337bf0e2c208")
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化会话
            await session.initialize()

            # 列出可用工具
            tools = await session.list_tools()
            print(f"可用工具: {[tool.name for tool in tools.tools]}")

            # 调用 MasterGo 工具
            # 1. 解析 URL
            result = await session.call_tool(
                "parse_mastergo_url",
                {"url": mastergo_url}
            )
            url_info = json.loads(result[0].text)
            file_id = url_info["file_id"]

            # 2. 获取文件信息
            file_result = await session.call_tool(
                "get_mastergo_file",
                {"file_id": file_id, "depth": None}
            )
            file_data = json.loads(file_result[0].text)

            # 3. 获取图片资源
            images_result = await session.call_tool(
                "get_mastergo_images",
                {"file_id": file_id}
            )
            images = json.loads(images_result[0].text)

            return {
                "file_id": file_id,
                "file_data": file_data,
                "images": images
            }

# 在节点中使用
def design_parse_node(state, config, runtime):
    """
    设计稿解析节点（MCP 版本）
    """
    mastergo_url = state.mastergo_url

    # 使用 MCP 调用
    import asyncio
    result = asyncio.run(design_parse_with_mcp(mastergo_url))

    # 处理结果
    components = extract_components(result["file_data"])
    static_assets = result["images"]

    return DesignParseOutput(
        components=components,
        layout={},
        static_assets=static_assets,
        mastergo_summary=f"文件 ID: {result['file_id']}"
    )
```

---

## 启动 MCP 服务器

### 方式 1：独立运行

```bash
python src/mcp/mastergo_server.py
```

### 方式 2：使用工作流启动

在工作流配置中自动启动 MCP 服务器。

---

## 测试 MCP 集成

创建 `test_mcp_integration.py`：

```python
"""
测试 MCP 集成
"""
import asyncio
import os
import json

async def test_mcp():
    """测试 MCP 连接"""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    server_params = StdioServerParameters(
        command="python",
        args=["src/mcp/mastergo_server.py"],
        env={
            "PYTHONPATH": "/workspace/projects/src",
            "MASTERGO_TOKEN": "mg_03992ef8773c4a75902b337bf0e2c208"
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()

            # 列出工具
            tools = await session.list_tools()
            print("可用工具:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # 测试解析 URL
            print("\n测试解析 URL...")
            result = await session.call_tool(
                "parse_mastergo_url",
                {"url": "https://mastergo.com/file/185219791981799"}
            )
            print("结果:", json.dumps(json.loads(result[0].text), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_mcp())
```

运行测试：
```bash
python test_mcp_integration.py
```

---

## 配置 LangGraph 使用 MCP

在 `src/graphs/graph.py` 中：

```python
from mcp import MCP

# 创建 MCP 客户端
mcp_client = MCP(config_path=".mcp/config.json")

# 在节点中使用
def design_parse_node(state, config, runtime):
    # 通过 MCP 调用 MasterGo
    result = mcp_client.call_tool(
        server="mastergo",
        tool="parse_mastergo_url",
        arguments={"url": state.mastergo_url}
    )

    # 处理结果...
```

---

## 优势

使用 MCP 的优势：

1. **标准化接口**：所有工具都遵循 MCP 标准
2. **易于集成**：可以在任何支持 MCP 的平台使用
3. **统一管理**：集中管理所有外部工具
4. **类型安全**：自动生成类型定义
5. **文档化**：自动生成工具文档

---

## 注意事项

1. **网络问题**：如果 MasterGo API 无法访问，MCP 也会失败
2. **Token 安全**：确保 Token 安全存储
3. **错误处理**：需要处理 MCP 调用失败的情况

---

## 替代方案

如果网络问题持续，可以使用：

### 方案 1：Mock MCP 服务器

创建返回模拟数据的 MCP 服务器，用于开发和测试。

### 方案 2：使用 Mock 数据

直接使用 Mock 数据，无需 MCP。

---

## 下一步

请告诉我：

1. **是否需要创建 MCP 服务器**？
   - 如果是，我会立即创建完整代码
   - 如果否，我们继续使用直接 API 调用或 Mock 数据

2. **是否需要使用官方 MCP（如果有）**？
   - 如果有，请提供 MasterGo MCP 服务器的配置信息
