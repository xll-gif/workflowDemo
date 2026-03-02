# 多端登录应用

## 项目概述
这是一个多平台登录应用的代码仓库集合，包含 iOS、Android、鸿蒙、H5 和微信小程序五个独立仓库。所有项目均由自动化工作流生成，支持前后端并行开发与联调。

## 仓库列表

### 1. iOS 登录应用
- **仓库地址**: https://github.com/xll-gif/ios-login-app
- **技术栈**: Swift 5.9+ + SwiftUI
- **最低版本**: iOS 15.0+
- **架构**: MVVM

### 2. Android 登录应用
- **仓库地址**: https://github.com/xll-gif/android-login-app
- **技术栈**: Kotlin 1.9+ + Jetpack Compose
- **最低 SDK**: API 24 (Android 7.0)
- **架构**: MVVM

### 3. 鸿蒙登录应用
- **仓库地址**: https://github.com/xll-gif/harmonyos-login-app
- **技术栈**: ArkTS + ArkUI
- **最低版本**: API 9 (HarmonyOS 3.0)
- **架构**: MVVM

### 4. H5 登录应用
- **仓库地址**: https://github.com/xll-gif/h5-login-app
- **技术栈**: React 18 + TypeScript + Vite
- **浏览器支持**: Chrome 90+, Safari 14+, iOS 14+
- **架构**: MVC

### 5. 微信小程序登录应用
- **仓库地址**: https://github.com/xll-gif/miniprogram-login-app
- **技术栈**: JavaScript + WXML + WXSS
- **最低基础库**: 2.20.0
- **架构**: MVP

## 功能特性

所有平台均实现以下功能：
- 用户登录（用户名/密码）
- 表单验证
- 加载状态提示
- 错误处理
- Mock 数据联调支持

## 组件映射规则

| 抽象组件 | iOS (SwiftUI) | Android (Compose) | 鸿蒙 (ArkUI) | H5 (React) | 小程序 (WXML) |
|---------|--------------|------------------|-------------|------------|---------------|
| 通用按钮 | Button | Button | Button | \<Button\> | \<button\> |
| 通用输入框 | TextField | TextField | TextInput | \<Input\> | \<input\> |
| 通用图片 | Image | AsyncImage | Image | \<img\> | \<image\> |

## 开发流程

### 自动化生成流程
1. **需求输入**: 在 GitHub Issue 中描述需求
2. **设计输入**: 在 MasterGo 中创建设计稿
3. **API 定义**: 在 Postman 中定义 API 接口
4. **工作流运行**: 触发自动化工作流
5. **代码生成**: 自动生成各平台代码
6. **代码提交**: 自动提交到各平台仓库
7. **联调测试**: 基于 Mock 数据进行联调

### 人工介入点
- 组件识别确认（本地控制台）
- 代码审查（GitHub PR）
- 测试验收（各平台真机）

## 技术选型理由

### 代码仓库组织
- **选择**: 5个独立仓库
- **理由**:
  - 每个平台有独立的构建系统和依赖管理
  - 降低代码耦合度，提高维护效率
  - 支持独立发布和版本管理
  - 便于不同团队并行开发

### 联调模式
- **选择**: 前后端并行开发（基于 Mock 数据）
- **理由**:
  - 提高开发效率，减少等待时间
  - 降低沟通成本
  - 便于前端独立开发与测试

### 静态资源处理
- **选择**: 暂存本地 assets/ 目录
- **理由**:
  - 快速原型开发
  - 待 CDN 接通后迁移到对象存储
  - 便于本地调试

## 依赖服务

### 外部服务
- GitHub: 代码托管和需求管理
- MasterGo: 设计稿管理（通过 Magic MCP 集成）
- Postman: API 定义和测试
- OSS/S3: 对象存储（待接通）

### 内部服务
- LLM 服务: 代码生成和设计稿识别
- Git: 版本控制

## 测试策略

### 单元测试
- 各平台独立运行单元测试
- 覆盖核心业务逻辑

### 集成测试
- 基于 Mock 数据的 API 集成测试
- 验证各平台与后端接口的兼容性

### 端到端测试
- 登录流程端到端测试
- 跨平台功能一致性测试

## 贡献指南

### 开发环境准备
1. 克隆对应平台的仓库
2. 按照各平台 README 配置开发环境
3. 运行项目确保环境正常

### 代码规范
- iOS: 遵循 Swift 官方代码规范
- Android: 遵循 Kotlin 官方代码规范
- 鸿蒙: 遵循 ArkTS 官方代码规范
- H5: 遵循 TypeScript + React 官方代码规范
- 小程序: 遵循微信小程序官方代码规范

### 提交规范
- 使用 Conventional Commits 规范
- 提交信息格式：`type(scope): description`
- 类型包括：feat, fix, docs, style, refactor, test, chore

## 时间线

- **2026年2月26日**: 项目启动，初始化 5 个仓库
- **2026年2月27日-28日**: 基础设施搭建
- **2026年3月2日-3日**: 组件映射表配置
- **2026年3月4日**: 代码生成节点实现
- **2026年3月5日**: 集成测试和演示

## 联系方式

- GitHub: https://github.com/xll-gif
- Issues: 在各平台仓库提交 Issue

## 许可证

MIT License
