# 更新日志

所有重要的项目变更都会记录在此文件中。

## [Unreleased]

### 计划中
- 添加部署节点（将代码部署到测试/生产环境）
- 添加监控节点（监控线上应用状态）
- 添加通知节点（发送执行报告到团队）
- 优化性能（缓存、增量生成等）

## [5.0.0] - 2026-03-02

### 新增功能

#### 静态资源处理流程（v5.0）
- **静态资源提取节点（extract_assets_node）**：
  - 从 MasterGo 设计稿中提取所有图片、图标、背景等静态资源
  - 支持多种资源类型：IMAGE、ICON、BACKGROUND、COMPONENT_IMAGE、LOGO
  - 智能识别布局中的背景图

- **资源分类和优化节点（optimize_assets_node）**：
  - 智能分类资源：图标、背景图、插图、Logo、头像、其他
  - 自动优化资源格式：图标优先 SVG，背景图转 WebP
  - 生成多倍图：@1x、@2x、@3x（用于 iOS）
  - 生成响应式版本：375px、768px、1024px、1440px（用于 H5）

- **资源上传节点（upload_assets_node）**：
  - 上传资源到对象存储（OSS）
  - 生成资源映射表（组件名 → OSS URL）
  - 支持 Mock 模式（未配置 OSS 时）
  - 自动处理下载失败情况

- **资源映射表生成节点（generate_asset_mapping_node）**：
  - 为五平台生成资源映射文件
  - H5: TypeScript 类型定义 + 资源常量
  - iOS: Assets.xcassets 配置 + ResourceManager
  - Android: resources.xml + ResourceManager
  - 鸿蒙: ResourceConstants.ets
  - 小程序: resource-constants.js

### 优化

- **H5 代码生成节点**：
  - 集成资源映射表，使用 OSS URL 生成代码
  - 支持多种资源引用方式（常量、索引、直接 URL）
  - 优化静态资源处理逻辑

- **工作流编排**：
  - 更新工作流，集成静态资源处理流程
  - 新流程：design_parse → extract_assets → optimize_assets → upload_assets → generate_asset_mapping → component_identify → h5_code_generation
  - 移除旧的 mastergo_asset_upload_node（功能被新流程替代）

### 修复

- 修复 HarmonyOS 映射生成中的语法错误（括号问题）
- 修复资源下载失败时的 Mock 处理逻辑
- 优化资源映射表生成逻辑

### 文档

- 新增 [STATIC_ASSET_PROCESSING_GUIDE.md](STATIC_ASSET_PROCESSING_GUIDE.md) - 静态资源处理流程完整指南
- 更新 AGENTS.md，添加新的静态资源处理节点信息
- 更新 GlobalState，添加静态资源处理流程相关字段

## [4.1.0] - 2026-02-28

### 新增功能

#### 远程代码拉取和同步
- **pull_remote_code_node**：通用远程代码拉取节点
  - 支持 Git clone 拉取完整代码
  - 支持项目规则提取
  - 支持 5 个平台（H5、iOS、Android、鸿蒙、小程序）

- **pull_h5_remote_code_node**：H5 专用拉取节点
  - 分析 package.json
  - 分析 tsconfig.json
  - 分析 ESLint、Prettier 配置

### 文档

- 新增 [PULL_REMOTE_CODE_GUIDE.md](PULL_REMOTE_CODE_GUIDE.md) - 远程代码拉取和同步指南

## [4.0.0] - 2026-02-27

### 新增功能

#### 项目规则解析
- **analyze_h5_project_rules_node**：H5 项目规则解析
- **analyze_ios_project_rules_node**：iOS 项目规则解析
- **analyze_android_project_rules_node**：Android 项目规则解析
- **analyze_harmonyos_project_rules_node**：鸿蒙项目规则解析
- **analyze_miniprogram_project_rules_node**：小程序项目规则解析

- 支持 8 个维度的项目规则分析：
  1. 项目结构
  2. 代码规范
  3. 组件使用
  4. API 集成
  5. 样式规范
  6. 测试规范
  7. 依赖管理
  8. 构建配置

### 优化

- 工作流在代码生成前先分析各平台项目规则
- 基于项目规则生成符合规范的代码

## [3.0.0] - 2026-02-26

### 新增功能

#### 多端代码生成
- **ios_code_generation_node**：iOS 代码生成（SwiftUI）
- **android_code_generation_node**：Android 代码生成（Jetpack Compose）
- **harmonyos_code_rules_node**：鸿蒙代码生成（ArkTS）
- **miniprogram_code_generation_node**：小程序代码生成

#### 并行代码生成
- 实现五端代码生成并行执行
- 提升效率约 4.3 倍

#### 代码审查和测试
- **code_review_node**：代码审查节点
- **automated_testing_node**：自动化测试节点
- 支持并行执行，提升效率约 1.7 倍

### 优化

- 工作流支持完整的前后端并行开发流程
- 支持联调和测试

## [2.0.0] - 2026-02-25

### 新增功能

#### MasterGo 集成
- **design_parse_node**：设计稿解析节点
- **mastergo_asset_upload_node**：资源上传节点
- **component_identify_node**：组件识别节点
- 使用 MasterGo Magic MCP 进行设计稿解析

#### Mock 服务
- **mock_service_generator_node**：Mock 服务生成节点
- 使用 MSW（Mock Service Worker）
- 支持前后端并行开发

### 优化

- 工作流支持从设计稿生成代码
- 支持静态资源管理

## [1.0.0] - 2026-02-24

### 新增功能

#### 基础工作流
- **requirement_analysis_node**：需求分析节点
- **h5_code_generation_node**：H5 代码生成节点（React + TypeScript + Vite）
- **github_commit_node**：GitHub 提交节点

#### 核心功能
- 支持从 GitHub Issues 读取需求
- 支持生成完整的 H5 应用
- 支持提交代码到 GitHub

---

## 版本规范

本项目使用 [语义化版本控制](https://semver.org/lang/zh-CN/)。

- **主版本号（Major）**：不兼容的 API 修改
- **次版本号（Minor）**：向下兼容的功能性新增
- **修订号（Patch）**：向下兼容的问题修正
