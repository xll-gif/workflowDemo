# Mock 服务使用指南

## 📋 概述

Mock 服务生成工具可以根据 API 定义自动生成 Mock 服务代码，支持 MSW 和 Mock.js 两种格式。

### 功能特性
- ✅ 自动生成 Mock 服务代码
- ✅ 支持 MSW (Mock Service Worker)
- ✅ 支持 Mock.js
- ✅ 真实数据模拟
- ✅ 自动延迟响应
- ✅ 支持多种数据类型

---

## 🚀 快速开始

### 1. 运行测试

```bash
# 运行所有测试
python3 test_mock_generation.py

# 测试结果会保存在当前目录：
# - test_msw_output.js (MSW 格式)
# - test_mockjs_output.js (Mock.js 格式)
# - test_realistic_output.js (真实数据模拟)
```

### 2. 在工作流中使用

```python
from graphs.nodes.mock_service_generator_node import mock_service_generator_node
from graphs.state import MockServiceGeneratorInput, ApiDefinition

# 准备输入
input_data = MockServiceGeneratorInput(
    api_definitions=[
        ApiDefinition(
            name="登录",
            method="POST",
            path="/api/v1/login",
            description="用户登录",
            request_body={
                "email": "user@example.com",
                "password": "123456"
            },
            response_example={
                "code": 0,
                "message": "登录成功",
                "data": {
                    "token": "xxx",
                    "user": {...}
                }
            },
            status_code=200
        )
    ],
    mock_type="msw",
    use_realistic_data=True
)

# 调用节点
result = mock_service_generator_node(
    state=input_data,
    config=RunnableConfig(...),
    runtime=Runtime[Context]()
)

# 获取生成的 Mock 代码
mock_code = result.mock_code
mock_file_name = result.mock_file_name
```

---

## 📝 API 定义格式

### ApiDefinition 数据结构

```python
class ApiDefinition(BaseModel):
    name: str                    # API 名称
    method: str                  # HTTP 方法（GET/POST/PUT/DELETE）
    path: str                    # API 路径
    description: str             # API 描述（可选）
    request_params: dict         # 请求参数（可选）
    request_body: dict           # 请求体（可选）
    response_example: dict       # 响应示例
    status_code: int             # HTTP 状态码
```

### 示例

```python
ApiDefinition(
    name="登录",
    method="POST",
    path="/api/v1/login",
    description="用户登录",
    request_body={
        "email": "user@example.com",
        "password": "123456"
    },
    response_example={
        "code": 0,
        "message": "登录成功",
        "data": {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example",
            "user": {
                "id": "123",
                "name": "张三",
                "email": "user@example.com",
                "avatar": "https://example.com/avatar.png"
            }
        }
    },
    status_code=200
)
```

---

## 🎯 Mock 类型

### 1. MSW (Mock Service Worker) - 推荐

**优点**：
- ✅ 现代化，功能强大
- ✅ 支持所有 HTTP 方法
- ✅ 易于调试
- ✅ 社区活跃

**生成的代码示例**：

```javascript
// Mock Service Worker - 生成于: 自动化工作流
import { rest } from 'msw'

// Mock 数据生成工具
const generateId = () => Math.random().toString(36).substr(2, 9)
const generateToken = () => 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.' + Math.random().toString(36).substr(2)


// 导出 handlers
export const handlers = [
  // 登录
rest.post('/api/v1/login', (delay(500), req, res, ctx) => {
  return res(
    ctx.status(200),
    ctx.json({
            "code": 0,
            "message": "登录成功",
            "data": {
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example",
                        "user": {
                                    "id": "123",
                                    "name": "张三",
                                    "email": "user@example.com",
                                    "avatar": "https://example.com/avatar.png"
                        }
            }
        }
    )
  )
),

  // 获取用户信息
rest.get('/api/v1/user/info', (delay(500), req, res, ctx) => {
  return res(
    ctx.status(200),
    ctx.json({
            "code": 0,
            "message": "获取成功",
            "data": {
                        "id": "123",
                        "name": "张三",
                        "email": "user@example.com",
                        "phone": "13800138000",
                        "avatar": "https://example.com/avatar.png"
            }
        }
    )
  )
})
]
```

**在前端项目中使用**：

```javascript
// src/mocks/browser.js
import { setupWorker } from 'msw/browser'
import { handlers } from './mockHandlers'

// 设置 Mock Service Worker
const worker = setupWorker(...handlers)
worker.start()

export default worker
```

```javascript
// src/main.js
// 仅在开发环境启用 Mock
if (import.meta.env.DEV) {
  import('./mocks/browser')
}
```

---

### 2. Mock.js

**优点**：
- ✅ 简单易用
- ✅ 支持丰富的数据模板
- ✅ 轻量级

**生成的代码示例**：

```javascript
// Mock.js - 生成于: 自动化工作流
import Mock from 'mockjs'

// Mock 数据生成工具
const Random = Mock.Random


// 导出 mocks
export default {
  // 登录
'/api/v1/login post': {
  'method': 'post',
  'url': '/api/v1/login',
  'response': {
  "code": 0,
  "message": '登录成功',
  "data": {
  "token": 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example',
  "user": {
  "id": '123',
  "name": '张三',
  "email": 'user@example.com',
  "avatar": 'https://example.com/avatar.png'
  }
  }
  }
},

  // 获取用户信息
'/api/v1/user/info get': {
  'method': 'get',
  'url': '/api/v1/user/info',
  'response': {
  "code": 0,
  "message": '获取成功',
  "data": {
  "id": '123',
  "name": '张三',
  "email": 'user@example.com',
  "phone": '13800138000',
  "avatar": 'https://example.com/avatar.png'
  }
  }
}
}
```

**在前端项目中使用**：

```javascript
// src/mocks/index.js
import Mock from 'mockjs'
import mocks from './mockConfig'

// 启用 Mock
Mock.setup({
  timeout: '500-1000'  // 延迟 500-1000 毫秒
})

// 注册 Mock
Object.values(mocks).forEach(mock => {
  Mock.mock(new RegExp(mock.url), mock.method, mock.response)
})

export default Mock
```

```javascript
// src/main.js
// 仅在开发环境启用 Mock
if (import.meta.env.DEV) {
  import('./mocks')
}
```

---

## 🎨 真实数据模拟

### 自动识别字段类型

Mock 服务生成工具会自动根据字段名生成合适的模拟数据：

| 字段名 | Mock.js 表达式 | 示例值 |
|--------|---------------|--------|
| `token` | `@string('lower', 32)` | `a1b2c3d4e5f6...` |
| `email` | `@email()` | `user@example.com` |
| `name` | `@cname()` | `张三` |
| `phone` | 手机号格式 | `13800138000` |
| `avatar` / `image` | `@image('100x100')` | 随机图片 URL |
| `url` | `@url()` | `https://example.com/...` |
| `id` | `@id()` | `123456789` |
| `date` / `time` | `@datetime()` | `2024-01-01 10:30:00` |
| `price` / `money` | `@float(0, 1000, 2, 2)` | `999.99` |

### 示例：真实数据模拟

**输入 API 定义**：
```python
ApiDefinition(
    name="获取用户详细信息",
    method="GET",
    path="/api/v1/user/detail",
    response_example={
        "code": 0,
        "message": "获取成功",
        "data": {
            "id": "123456",
            "name": "李四",
            "email": "lisi@example.com",
            "phone": "13900139000",
            "avatar": "https://example.com/avatar.png",
            "age": 28,
            "balance": 999.99,
            "register_time": "2024-01-15 10:30:00"
        }
    }
)
```

**生成的 Mock.js 代码**：
```javascript
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "id": @id(),
    "name": @cname(),
    "email": @email(),
    "phone": '1' + @pick('3','5','7','8','9') + @string('number', 9),
    "avatar": @image('100x100'),
    "age": 28,
    "balance": @float(0, 1000, 2, 2),
    "register_time": @datetime()
  }
}
```

**每次请求返回不同的数据**：
```javascript
// 第一次请求
{
  "data": {
    "id": "abc123",
    "name": "王五",
    "email": "wangwu@example.com",
    ...
  }
}

// 第二次请求
{
  "data": {
    "id": "def456",
    "name": "赵六",
    "email": "zhaoliu@example.com",
    ...
  }
}
```

---

## 🔧 配置选项

### MockGeneratorConfig

```python
@dataclass
class MockGeneratorConfig:
    use_realistic_data: bool = True   # 是否使用真实模拟数据
    use_delay: bool = True            # 是否添加延迟
    delay_time: int = 500            # 延迟时间（毫秒）
```

### 使用自定义配置

```python
from tools.mock_service_generator import MockServiceGenerator, MockGeneratorConfig

# 自定义配置
config = MockGeneratorConfig(
    use_realistic_data=True,
    use_delay=False,  # 关闭延迟
    delay_time=200    # 200ms 延迟
)

# 创建生成器
generator = MockServiceGenerator(config)

# 生成 Mock 代码
mock_code = generator.generate(api_definitions, "msw")
```

---

## 📊 工作流集成

### 在 LangGraph 工作流中使用

```python
from langgraph.graph import StateGraph, END
from graphs.nodes.mock_service_generator_node import mock_service_generator_node

# 创建状态图
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 添加节点
builder.add_node("mock_generator", mock_service_generator_node, metadata={"type": "task"})

# 添加边
builder.add_edge("api_parser", "mock_generator")
builder.add_edge("mock_generator", "frontend_generator")

# 编译图
main_graph = builder.compile()
```

### 完整数据流

```
GitHub Issues (需求描述)
    ↓
[需求分析节点]
    ↓
API 定义列表
    ↓
[Mock 服务生成节点] ✅
    ↓
Mock 服务代码
    ↓
[前端代码生成节点]
    ↓
集成 Mock 的前端代码
    ↓
部署到 CDN
    ↓
Demo 展示
```

---

## 🎯 使用场景

### 1. Demo 展示

生成 Mock 服务，用于前端 Demo 展示：

```python
# 生成 Mock 代码
result = mock_service_generator_node(
    state=MockServiceGeneratorInput(
        api_definitions=api_list,
        mock_type="msw"
    ),
    ...
)

# 保存 Mock 代码
with open("mockHandlers.js", "w") as f:
    f.write(result.mock_code)
```

### 2. 前后端并行开发

后端定义 API，前端使用 Mock 开发：

```python
# 后端提供 API 定义（Postman Collection）
api_definitions = parse_postman_collection(collection_url)

# 生成 Mock 服务
mock_code = generate_mock_service(api_definitions, "msw")

# 前端使用 Mock 开发
# 后端实现真实 API
```

### 3. 测试数据生成

生成测试用例的 Mock 数据：

```python
# 生成测试数据
test_data = generate_mock_service(test_apis, "mockjs")

# 在测试中使用
```

---

## 📦 生成的文件

### MSW 格式
- **文件名**: `mockHandlers.js`
- **内容**: MSW handlers 数组
- **用途**: 在前端项目中引入并启动 MSW

### Mock.js 格式
- **文件名**: `mockConfig.js`
- **内容**: Mock 配置对象
- **用途**: 在前端项目中注册 Mock

---

## 🚨 注意事项

### 1. Token 处理

对于固定的 token（如 JWT），工具会保持原样：

```python
# 输入
response_example = {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example"
}

# 输出（保持原样）
"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example"
```

### 2. 延迟设置

默认添加 500ms 延迟，模拟真实网络环境：

```javascript
// MSW
rest.post('/api/v1/login', (delay(500), req, res, ctx) => { ... })

// Mock.js
Mock.setup({ timeout: '500-1000' })
```

### 3. 仅在开发环境使用

确保只在开发环境启用 Mock：

```javascript
// 仅在开发环境
if (import.meta.env.DEV) {
  import('./mocks')
}
```

---

## 🔍 故障排除

### 问题 1: Mock 不生效

**原因**: MSW 未正确启动

**解决方案**:
```javascript
// 确保在主入口文件中启动
import { setupWorker } from 'msw/browser'
import { handlers } from './mockHandlers'

const worker = setupWorker(...handlers)
worker.start()
```

### 问题 2: 跨域问题

**原因**: Mock 服务与 API 域名不匹配

**解决方案**: 使用 `setupServer` (Node.js) 或 `setupWorker` (Browser)

```javascript
// Browser 环境
import { setupWorker } from 'msw/browser'

// Node.js 环境
import { setupServer } from 'msw/node'
```

### 问题 3: 延迟太长

**原因**: 默认延迟 500ms

**解决方案**: 自定义配置

```python
config = MockGeneratorConfig(
    use_delay=False  # 关闭延迟
)
```

---

## 📚 相关资源

- [MSW 文档](https://mswjs.io/)
- [Mock.js 文档](http://mockjs.com/)
- [Postman Collection](https://www.postman.com/)
- [OpenAPI 规范](https://swagger.io/specification/)

---

**更新时间**: 2026-02-26
**版本**: v1.0.0
