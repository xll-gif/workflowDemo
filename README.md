# H5 登录页面应用

基于 AI 自动生成的前端登录页面应用，使用 React 18 + TypeScript + Vite 技术栈。

## ✨ 功能特性

- ✅ 完整的登录表单（邮箱、密码）
- ✅ 实时表单验证（邮箱格式、密码长度）
- ✅ 密码显示/隐藏切换
- ✅ 加载状态管理
- ✅ 错误提示展示
- ✅ 登录接口调用
- ✅ 忘记密码功能
- ✅ Token 本地存储
- ✅ 响应式设计（移动端优先）
- ✅ 符合现代 UI 规范

## 🚀 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

项目将在 http://localhost:3000 启动

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 📁 项目结构

```
h5-login-app/
├── src/
│   ├── components/
│   │   ├── pages/
│   │   │   └── LoginPage.tsx    # 登录页面
│   │   └── ui/
│   │       ├── Button.tsx       # 按钮组件
│   │       └── Input.tsx        # 输入框组件
│   ├── hooks/
│   │   └── useForm.ts           # 表单管理 Hook
│   ├── services/
│   │   └── api.ts               # API 服务层
│   ├── types/
│   │   └── index.ts             # TypeScript 类型定义
│   ├── assets/
│   │   └── logo.png             # 品牌 Logo
│   ├── App.tsx                  # 主应用组件
│   ├── main.tsx                 # 应用入口
│   └── index.css                # 全局样式
├── public/
│   └── vite.svg                 # Vite 图标
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── postcss.config.js
```

## 🎨 技术栈

- **框架**: React 18
- **语言**: TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **HTTP 客户端**: Axios
- **路由**: React Router
- **表单管理**: 自定义 Hooks

## 📡 API 接口

### 登录接口
```
POST /api/auth/login
```

**请求参数**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

### 忘记密码接口
```
POST /api/auth/forgot-password
```

**请求参数**:
```json
{
  "email": "user@example.com"
}
```

## 🔧 配置说明

### Mock 服务

项目使用 MSW (Mock Service Worker) 进行接口 Mock，配置文件在 `src/mock/handlers.ts`。

### 样式配置

Tailwind CSS 配置文件：`tailwind.config.js`

### 路径别名

- `@/*` → `src/*`
- `@assets/*` → `src/assets/*`

## 📝 开发说明

### 添加新页面

1. 在 `src/components/pages/` 创建新组件
2. 在 `src/App.tsx` 中添加路由

### 添加新组件

1. 在 `src/components/ui/` 创建 UI 组件
2. 导出并使用

### 添加新 API

1. 在 `src/types/index.ts` 添加类型定义
2. 在 `src/services/api.ts` 添加 API 方法

## 🎯 待实现功能

- [ ] 注册页面
- [ ] 用户个人中心
- [ ] 多语言支持
- [ ] 暗黑模式
- [ ] 单元测试

## 📄 License

MIT

## 🙏 致谢

本应用由 AI 自动生成，基于以下技术：
- React 18
- TypeScript
- Vite
- Tailwind CSS
