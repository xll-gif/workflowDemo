# MasterGo API 连接问题解决方案

## 问题现状

**当前问题**：无法连接到 MasterGo API (`api.mastergo.cn`)

**测试结果**：
- ❌ `api.mastergo.cn` - 连接超时
- ❌ `openapi.mastergo.cn` - 连接超时
- ✅ `www.mastergo.com` - 可访问

## 解决方案（按优先级排序）

---

## 方案 1：使用浏览器开发者工具抓包（最推荐，成功率最高）

### 步骤

#### 1.1 打开浏览器开发者工具
1. 使用 Chrome 或 Edge 浏览器
2. 访问您的设计稿链接：https://mastergo.com/file/185219791981799?fileOpenFrom=home&page_id=M
3. 按 `F12` 键打开开发者工具
4. 切换到 **Network（网络）** 标签

#### 1.2 清空并重新加载
1. 点击 "Clear（清空）" 按钮（禁止图标）
2. 刷新页面（F5）

#### 1.3 查找 API 请求
1. 在 Network 列表中，查找以下类型的请求：
   - 域名包含 `api` 的请求
   - 域名包含 `openapi` 的请求
   - 请求类型为 `XHR` 或 `fetch` 的请求
   - 返回 JSON 数据的请求

2. 点击找到的请求，查看以下信息：
   - **请求 URL**：完整的 API 地址
   - **请求方法**：GET、POST 等
   - **请求头**：特别是 `Authorization` 或 `token` 相关的
   - **请求参数**：URL 参数或请求体

#### 1.4 记录关键信息

请记录以下信息（复制给我）：

```
API 端点: https://xxxxx.com/xxxxx/xxxxx
请求方法: GET/POST
请求头示例:
  Authorization: Bearer xxxxxx
  Content-Type: application/json
```

#### 1.5 测试获取到的端点

1. 将找到的 API 端点复制给我
2. 我将更新代码并测试

---

## 方案 2：配置网络代理

### 步骤

#### 2.1 检查是否有可用代理

如果您公司或网络环境有代理服务器，请询问网络管理员获取代理地址。

代理地址格式：
```
http://proxy.example.com:8080
或
https://proxy.example.com:8080
```

#### 2.2 配置代理

**方式 1：环境变量（推荐）**

在命令行中执行：

```bash
# Linux/Mac
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# Windows PowerShell
$env:HTTP_PROXY="http://proxy.example.com:8080"
$env:HTTPS_PROXY="http://proxy.example.com:8080"
```

**方式 2：在代码中配置**

我需要更新 `src/tools/mastergo_api.py`，添加代理配置。

#### 2.3 提供代理信息

如果您有代理，请提供：
- 代理地址
- 端口号
- 是否需要用户名和密码

我将立即更新代码。

---

## 方案 3：查找官方 API 文档

### 步骤

#### 3.1 访问 MasterGo 官方文档

尝试访问以下页面：
- https://www.mastergo.com/docs
- https://www.mastergo.com/developer
- https://www.mastergo.com/api

#### 3.2 搜索 API 信息

在文档中搜索：
- "API"
- "Open API"
- "开发者"
- "接口"

#### 3.3 查找关键信息

请查找并告诉我：
- API 基础 URL
- 认证方式（Token 的使用方法）
- 示例代码

---

## 方案 4：联系 MasterGo 技术支持

### 步骤

#### 4.1 准备问题信息

准备以下信息：

```
问题：无法访问 MasterGo API
File ID: 185219791981799
Token: mg_03992ef8773c4a75902b337bf0e2c208
测试结果：api.mastergo.cn 连接超时
```

#### 4.2 联系方式

- MasterGo 官网客服
- 官方论坛
- 技术支持邮箱

#### 4.3 询问要点

1. 正确的 API 端点是什么？
2. 当前 Token 是否有效？
3. 是否需要特殊的网络配置？
4. 是否有 API 使用示例？

---

## 方案 5：暂时使用 Mock 数据（立即可用）

### 步骤

#### 5.1 使用现有 Mock 数据

我已经创建了完整的 Mock 数据，可以立即使用：

```bash
python mock_mastergo_parse.py
```

这会生成 `assets/mastergo_parse_mock.json`，包含完整的设计稿数据。

#### 5.2 在开发中使用 Mock 数据

您可以直接使用 Mock 数据进行：
- 功能开发
- 代码测试
- 工作流演示

#### 5.3 后续切换到真实 API

当网络问题解决后，只需：
1. 更新 API 端点配置
2. 删除 Mock 数据代码
3. 使用真实 API

---

## 推荐行动方案

### 短期方案（今天）

✅ **方案 5：使用 Mock 数据**

**原因**：
- 立即可用
- 不依赖网络
- 可以继续开发

**操作**：
```bash
python mock_mastergo_parse.py
```

---

### 中期方案（1-2天）

✅ **方案 1：浏览器抓包**

**原因**：
- 成功率最高
- 可以找到真实的 API 端点
- 无需询问任何人

**操作**：
1. 打开 https://mastergo.com/file/185219791981799?fileOpenFrom=home&page_id=M
2. 按 F12 → Network 标签
3. 查找 API 请求
4. 将找到的 API 端点复制给我

---

### 长期方案（1周内）

✅ **方案 2：配置代理** 或 **方案 3：查找文档**

**原因**：
- 根本解决问题
- 稳定可靠
- 适合生产环境

---

## 我需要您的帮助

请从以下选项中选择一个或多个：

### 选项 A：提供浏览器抓包结果（最推荐）
1. 按照方案 1 的步骤操作
2. 找到 API 请求
3. 复制以下信息给我：
   - 请求 URL
   - 请求头（特别是 Authorization）

### 选项 B：提供代理配置
1. 询问网络管理员获取代理地址
2. 将代理信息告诉我

### 选项 C：查找 API 文档
1. 访问 MasterGo 官方文档
2. 找到 API 相关信息
3. 分享给我

### 选项 D：继续使用 Mock 数据
1. 确认使用 Mock 数据
2. 我将继续完善功能

---

## 快速决策指南

| 情况 | 推荐方案 | 耗时 |
|------|---------|------|
| 想立即继续开发 | 方案 5（Mock 数据） | 0 分钟 |
| 有浏览器访问权限 | 方案 1（抓包） | 5-10 分钟 |
| 知道代理地址 | 方案 2（配置代理） | 2-3 分钟 |
| 可以查找文档 | 方案 3（查找文档） | 10-20 分钟 |
| 想彻底解决 | 联系 MasterGo 支持 | 1-3 天 |

---

## 我的建议

**立即执行**（5分钟）：
1. 尝试方案 1（浏览器抓包）- 只需要 5 分钟
2. 如果失败，使用方案 5（Mock 数据）继续开发

**今天完成**：
1. 确定最终的 API 端点
2. 更新代码配置
3. 测试真实 API 连接

---

## 等待您的回复

请告诉我：
1. 您选择哪个方案？
2. 或者您有其他想法？

我将根据您的选择，立即提供下一步的详细指导。
