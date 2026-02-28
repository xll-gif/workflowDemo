# 登录功能 Demo

## 📋 项目概述

这是一个完整的用户登录功能 Demo，基于 GitHub Issue #2 实现。

## ✨ 功能特性

### UI 功能
- ✨ 完整的登录页面 UI
- 📧 邮箱输入框（带图标）
- 🔒 密码输入框（带图标和显示/隐藏切换）
- 🔘 醒目的登录按钮
- 🔗 忘记密码链接

### 交互功能
- ✅ 表单验证（邮箱格式、密码长度）
- 📡 登录接口调用
- 🔄 加载状态显示
- ⚠️ 错误提示
- ✅ 登录成功处理

## 🚀 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

## 🔌 API 接口

### 1. 用户登录
**接口：** POST /api/auth/login

**请求参数：**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**成功响应：**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "...",
    "refreshToken": "...",
    "user": {...},
    "expiresIn": 7200
  }
}
```

### 2. 忘记密码
**接口：** POST /api/auth/forgot-password

**请求参数：**
```json
{
  "email": "user@example.com"
}
```

**成功响应：**
```json
{
  "code": 200,
  "message": "重置密码邮件已发送",
  "data": {
    "email": "user@example.com"
  }
}
```

## 🧪 Mock 服务

项目使用 MSW (Mock Service Worker) 提供开发环境的 Mock 数据。

Mock 配置文件：`src/mockHandlers.ts`

## 📦 技术栈

- **框架**: React 18
- **语言**: TypeScript
- **构建工具**: Vite
- **HTTP 客户端**: Axios
- **Mock**: MSW (Mock Service Worker)

## 🎨 设计稿

- **Figma URL**: https://www.figma.com/design/KiEfynzOUX7NIjhzUAN3Jd/Untitled?node-id=0-1

## 📝 GitHub Issue

- **Issue**: https://github.com/xll-gif/workflowDemo/issues/2

## ✅ 验收标准

- [x] UI 与 Figma 设计稿一致
- [x] 邮箱输入框正常工作
- [x] 密码输入框支持隐藏/显示
- [x] 表单验证功能完整
- [x] 登录接口调用成功
- [x] 错误提示清晰友好
- [x] 加载状态显示正常
- [x] 登录成功后正确跳转
- [x] Token 正确存储

## 📁 项目结构

```
demo_project/
├── src/
│   ├── api.ts              # API 接口定义
│   ├── App.tsx             # App 组件
│   ├── App.css             # App 样式
│   ├── Login.tsx           # 登录页面组件
│   ├── Login.css           # 登录页面样式
│   ├── main.tsx            # 入口文件
│   └── mockHandlers.ts     # Mock 服务配置
├── index.html              # HTML 模板
├── package.json            # 项目依赖
├── tsconfig.json           # TypeScript 配置
├── vite.config.ts          # Vite 配置
└── README.md               # 项目说明
```

## 🎯 使用说明

### 登录流程

1. 打开登录页面
2. 输入邮箱和密码
3. 点击登录按钮
4. 系统验证输入
5. 调用登录接口
6. 登录成功后跳转

### 表单验证

- **邮箱格式**: 必须符合邮箱格式（如 user@example.com）
- **密码长度**: 至少 6 位字符

### 错误处理

- 网络错误提示
- 服务器错误提示
- 登录失败提示

---

**创建时间**: 2026-02-26
**创建工具**: Coze Coding 工作流
**状态**: ✅ 已完成
