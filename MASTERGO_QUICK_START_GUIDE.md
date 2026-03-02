# MasterGo 集成快速实施指南

## 🎯 目标
将工作流中的 Figma 替换为 MasterGo，解决静态资源存储和 API 限流问题。

## 📋 当前状态

### ✅ 已完成
1. **网络诊断报告**：确认 `api.mastergo.cn` 无法连接
2. **解决方案文档**：创建了 6 份详细指南文档
3. **Mock 数据方案**：提供了开发阶段的 Mock 数据
4. **官方 MCP 发现**：找到 MasterGo 官方 Magic MCP 服务器

### 🔍 关键发现

#### 1. MasterGo 官方 Magic MCP
- **名称**: MasterGo Magic MCP
- **包名**: `@mastergo/magic-mcp`
- **功能**: 从 MasterGo 设计文件中检索 DSL 数据
- **官方文档**: https://github.com/mastergo-design/mastergo-magic-mcp

#### 2. MasterGo API 基础 URL
- **正确**: `https://api.mastergo.com`（注意是 .com 不是 .cn）
- **错误**: `api.mastergo.cn`（连接超时）

#### 3. MCP Token 获取方式
1. 访问 https://mastergo.com
2. 进入个人设置
3. 点击安全设置
4. 找到个人访问令牌
5. 生成并复制 MG_MCP_TOKEN

## 🚀 实施步骤

### 步骤 1：获取 MasterGo MCP Token（用户操作）

```bash
# 1. 访问 MasterGo
https://mastergo.com

# 2. 登录后进入个人设置
# 路径：个人设置 → 安全设置 → 个人访问令牌

# 3. 生成令牌并复制
```

### 步骤 2：配置环境变量

```bash
# 创建 .env 文件
cat > .env << 'EOF'
# MasterGo MCP 配置
MASTERGO_API_URL=https://mastergo.com
MASTERGO_MCP_TOKEN=YOUR_TOKEN_HERE

# 对象存储配置
OSS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
OSS_ACCESS_KEY_SECRET=YOUR_SECRET_KEY
OSS_BUCKET=your-bucket-name
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com

# GitHub 配置
GITHUB_TOKEN=YOUR_GITHUB_TOKEN
GITHUB_USERNAME=your-username
EOF
```

### 步骤 3：测试 MCP 连接

```bash
# 测试 MasterGo MCP 服务器
npx @mastergo/magic-mcp --token=YOUR_TOKEN --url=https://mastergo.com --debug

# 或者运行示例代码
python examples/mastergo_mcp_integration_example.py
```

### 步骤 4：集成到工作流（开发任务）

#### 4.1 更新 design_parse_node.py

```python
# src/graphs/nodes/design_parse_node.py

from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context

def design_parse_node(state: DesignParseInput, config: RunnableConfig, runtime: Runtime[Context]) -> DesignParseOutput:
    """
    title: MasterGo 设计解析
    desc: 使用 MasterGo Magic MCP 解析设计稿
    integrations: MasterGo Magic MCP
    """
    ctx = runtime.context

    # 创建 MCP 客户端
    mcp_client = SearchClient(ctx=new_context(method="mastergo"))

    # 通过 MCP 获取设计数据
    # 注意：这里需要根据实际的 MCP 客户端实现调整
    result = mcp_client.web_search_with_summary(
        query=f"mastergo design parse {state.mastergo_url}",
        count=1
    )

    # 解析结果
    design_data = parse_mcp_result(result)

    return DesignParseOutput(
        design_data=design_data,
        components=extract_components(design_data),
        assets=extract_assets(design_data)
    )
```

#### 4.2 更新 mastergo_asset_upload_node.py

```python
# src/graphs/nodes/mastergo_asset_upload_node.py

def mastergo_asset_upload_node(state: AssetUploadInput, config: RunnableConfig, runtime: Runtime[Context]) -> AssetUploadOutput:
    """
    title: MasterGo 资源上传
    desc: 上传 MasterGo 静态资源到对象存储
    integrations: 对象存储
    """
    ctx = runtime.context

    # 从 MasterGo 获取资源 URL
    asset_urls = [asset["url"] for asset in state.assets]

    # 上传到对象存储
    uploaded_urls = []
    for asset_url in asset_urls:
        # 下载资源
        response = requests.get(asset_url)
        temp_path = f"/tmp/{uuid.uuid4()}.png"
        with open(temp_path, "wb") as f:
            f.write(response.content)

        # 上传到对象存储
        oss_url = upload_to_oss(temp_path)
        uploaded_urls.append(oss_url)

    return AssetUploadOutput(
        uploaded_urls=uploaded_urls
    )
```

### 步骤 5：更新状态定义

```python
# src/graphs/state.py

class DesignParseInput(BaseModel):
    """设计解析节点输入"""
    mastergo_url: str = Field(..., description="MasterGo 设计稿 URL")

class DesignParseOutput(BaseModel):
    """设计解析节点输出"""
    design_data: Dict[str, Any] = Field(..., description="解析后的设计数据")
    components: List[Dict[str, Any]] = Field(default=[], description="识别出的组件")
    assets: List[Dict[str, Any]] = Field(default=[], description="静态资源列表")
```

### 步骤 6：测试工作流

```bash
# 运行测试
python -m pytest src/tests/ -v

# 或者使用 test_run 工具
```

## 📊 数据流转

```
用户输入 MasterGo URL
    ↓
通过 MCP 调用 MasterGo Magic MCP
    ↓
获取设计 DSL 数据
    ↓
解析组件和资源
    ↓
上传资源到对象存储
    ↓
生成代码
    ↓
输出结果
```

## 🔧 配置文件

### config/mastergo_config.json

```json
{
  "api_url": "https://mastergo.com",
  "mcp_token": "${MASTERGO_MCP_TOKEN}",
  "mcp_command": "npx @mastergo/magic-mcp",
  "timeout": 30
}
```

## ⚠️ 注意事项

1. **Token 安全**：
   - 不要将 MG_MCP_TOKEN 提交到版本控制系统
   - 使用环境变量存储敏感信息

2. **网络问题**：
   - 如果无法连接 `mastergo.com`，需要配置网络代理
   - 参考 `assets/PROXY_EXPLANATION.md`

3. **MCP 客户端**：
   - 需要安装 Node.js 环境
   - 需要配置 MCP 客户端

4. **开发阶段**：
   - 可以使用 Mock 数据进行开发
   - 参考 `mock_mastergo_parse.py`

## 📚 相关文档

- **主文档**: `MASTERGO_INTEGRATION_GUIDE.md`
- **MCP 集成**: `MASTERGO_MCP_INTEGRATION_GUIDE.md`
- **官方方案**: `assets/MASTERGO_OFFICIAL_MCP_SOLUTION.md`
- **环境变量**: `ENVIRONMENT_VARIABLES.md`
- **代理说明**: `assets/PROXY_EXPLANATION.md`
- **API 问题**: `assets/MASTERGO_API_SOLUTION_GUIDE.md`

## 🎯 下一步行动

### 立即行动（用户）
1. [ ] 获取 MasterGo MCP Token
2. [ ] 配置环境变量
3. [ ] 测试 MCP 连接

### 开发任务（开发者）
1. [ ] 更新 `design_parse_node.py`
2. [ ] 更新 `mastergo_asset_upload_node.py`
3. [ ] 更新 `state.py`
4. [ ] 测试工作流
5. [ ] 更新文档

## 💡 常见问题

### Q1: 如何获取 MG_MCP_TOKEN？
A: 访问 https://mastergo.com → 个人设置 → 安全设置 → 个人访问令牌 → 生成令牌

### Q2: MCP 服务器在哪里？
A: 官方 MCP 服务器包名是 `@mastergo/magic-mcp`，通过 npx 运行

### Q3: 为什么之前的 API 连接失败？
A: 之前使用的 `api.mastergo.cn` 是错误的域名，正确的应该是 `api.mastergo.com`

### Q4: 开发阶段如何测试？
A: 使用 `mock_mastergo_parse.py` 提供的 Mock 数据

### Q5: 如何配置网络代理？
A: 参考 `assets/PROXY_EXPLANATION.md` 文档

## 📞 技术支持

- MasterGo 官方文档: https://developers.mastergo.com/guide/
- MCP 官方文档: https://modelcontextprotocol.io/
- MasterGo GitHub: https://github.com/mastergo-design/mastergo-magic-mcp

---

*版本：1.0*
*更新日期：2026-02-28*
