from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# ==================== 全局状态 ====================
class GlobalState(BaseModel):
    """工作流全局状态"""
    input_message: str = Field(default="", description="输入消息")
    output_message: str = Field(default="", description="输出消息")
    processing_time: float = Field(default=0.0, description="处理耗时（秒）")

    # GitHub Issue 数据
    github_issue_url: str = Field(default="", description="GitHub Issue URL")
    issue_title: str = Field(default="", description="Issue 标题")
    issue_body: str = Field(default="", description="Issue 内容")

    # 需求分析结果
    feature_list: List[str] = Field(default=[], description="功能列表")
    api_definitions: List[Dict[str, Any]] = Field(default=[], description="API 定义列表")

    # MasterGo 设计稿数据
    mastergo_url: str = Field(default="", description="MasterGo 设计稿 URL")
    components: List[Dict[str, Any]] = Field(default=[], description="UI 组件列表")
    layout: Dict[str, Any] = Field(default={}, description="布局信息")
    static_assets: List[Dict[str, Any]] = Field(default=[], description="静态资源列表")
    mastergo_summary: str = Field(default="", description="设计稿摘要")

    # 静态资源处理流程（v5.0 新增）
    raw_assets: List[Dict[str, Any]] = Field(default=[], description="提取的原始资源列表")
    optimized_assets: List[Dict[str, Any]] = Field(default=[], description="优化后的资源列表")
    categorized_assets: Dict[str, List[Dict[str, Any]]] = Field(default={}, description="分类后的资源")
    uploaded_assets: List[Dict[str, Any]] = Field(default=[], description="上传成功的资源列表")
    asset_mapping: Dict[str, str] = Field(default={}, description="资源映射表（组件名 → OSS URL）")

    # 组件识别结果
    identified_components: List[Dict[str, Any]] = Field(default=[], description="识别后的组件列表")
    component_hierarchy: Dict[str, Any] = Field(default={}, description="组件层次结构")
    design_summary: str = Field(default="", description="设计摘要")
    suggestions: List[str] = Field(default=[], description="设计建议")

    # H5 代码生成结果
    h5_generated_files: List[Dict[str, str]] = Field(default=[], description="H5 生成的文件列表")
    h5_generation_summary: str = Field(default="", description="H5 代码生成摘要")

# ==================== 图输入输出 ====================
class GraphInput(BaseModel):
    """工作流输入"""
    input_message: str = Field(default="", description="输入消息")
    github_issue_url: str = Field(default="", description="GitHub Issue URL")
    issue_title: str = Field(default="", description="Issue 标题")
    issue_body: str = Field(default="", description="Issue 内容")

class GraphOutput(BaseModel):
    """工作流输出"""
    output_message: str = Field(default="", description="输出消息")
    processing_time: float = Field(default=0.0, description="处理耗时（秒）")
    feature_list: List[str] = Field(default=[], description="功能列表")
    api_definitions: List[Dict[str, Any]] = Field(default=[], description="API 定义列表")
    mastergo_url: str = Field(default="", description="MasterGo 设计稿 URL")
    components: List[Dict[str, Any]] = Field(default=[], description="UI 组件列表")
    layout: Dict[str, Any] = Field(default={}, description="布局信息")
    static_assets: List[Dict[str, Any]] = Field(default=[], description="静态资源列表")
    mastergo_summary: str = Field(default="", description="设计稿摘要")
    identified_components: List[Dict[str, Any]] = Field(default=[], description="识别后的组件列表")
    component_hierarchy: Dict[str, Any] = Field(default={}, description="组件层次结构")
    design_summary: str = Field(default="", description="设计摘要")
    suggestions: List[str] = Field(default=[], description="设计建议")
    h5_generated_files: List[Dict[str, str]] = Field(default=[], description="H5 生成的文件列表")
    h5_generation_summary: str = Field(default="", description="H5 代码生成摘要")

# ==================== 节点输入输出 ====================
class HelloWorldInput(BaseModel):
    """Hello World 节点输入"""
    input_message: str = Field(..., description="输入消息")

class HelloWorldOutput(BaseModel):
    """Hello World 节点输出"""
    output_message: str = Field(..., description="输出消息")
    processing_time: float = Field(..., description="处理耗时（秒）")


class RequirementAnalysisInput(BaseModel):
    """需求分析节点输入"""
    github_issue_url: str = Field(..., description="GitHub Issue URL")
    issue_title: str = Field(default="", description="Issue 标题")
    issue_body: str = Field(default="", description="Issue 内容")

class RequirementAnalysisOutput(BaseModel):
    """需求分析节点输出"""
    feature_list: List[str] = Field(..., description="功能列表")
    api_definitions: List[Dict[str, Any]] = Field(default=[], description="API 定义列表")
    summary: str = Field(..., description="需求摘要")
    mastergo_url: str = Field(default="", description="MasterGo 设计稿 URL（从 Issue 中提取）")


class AnalyzeCodebaseInput(BaseModel):
    """代码库分析节点输入"""
    repo_owner: str = Field(..., description="GitHub 仓库所有者")
    repo_name: str = Field(..., description="GitHub 仓库名称")
    repo_branch: Optional[str] = Field(default="main", description="分支名（可选）")
    github_token: Optional[str] = Field(default=None, description="GitHub Token（可选）")
    analyze_depth: int = Field(default=1, description="分析深度：0=仅根目录，1=一级子目录，2=二级子目录")


class AnalyzeCodebaseOutput(BaseModel):
    """代码库分析节点输出"""
    repo_info: Dict[str, Any] = Field(..., description="仓库基本信息")
    project_structure: List[Dict[str, Any]] = Field(default=[], description="项目结构")
    tech_stack: Dict[str, Any] = Field(default={}, description="技术栈信息")
    key_files: List[str] = Field(default=[], description="关键文件路径")


class CodeGenAndPushInput(BaseModel):
    """代码生成与推送节点输入"""
    repo_owner: str = Field(..., description="GitHub 仓库所有者")
    repo_name: str = Field(..., description="GitHub 仓库名称")
    repo_dir: str = Field(..., description="仓库本地路径")
    base_branch: str = Field(default="main", description="基础分支名")
    feature_branch: str = Field(..., description="特性分支名")
    github_token: str = Field(..., description="GitHub Token（必须）")
    files_to_generate: List[Dict[str, str]] = Field(
        default=[],
        description="要生成的文件列表，每个包含 path 和 content"
    )
    commit_message: str = Field(..., description="提交消息")
    create_pr: bool = Field(default=False, description="是否创建 Pull Request")
    pr_title: str = Field(default="", description="PR 标题")
    pr_body: str = Field(default="", description="PR 描述")


class CodeGenAndPushOutput(BaseModel):
    """代码生成与推送节点输出"""
    success: bool = Field(..., description="是否成功")
    branch_created: bool = Field(default=False, description="分支是否创建成功")
    files_generated: List[str] = Field(default=[], description="已生成的文件列表")
    commit_created: bool = Field(default=False, description="提交是否创建成功")
    push_successful: bool = Field(default=False, description="推送是否成功")
    pr_url: str = Field(default="", description="Pull Request URL")
    error_message: str = Field(default="", description="错误信息")


class DesignParseInput(BaseModel):
    """设计稿解析节点输入"""
    mastergo_url: str = Field(..., description="MasterGo 设计稿 URL")
    page_name: Optional[str] = Field(default="Page 1", description="页面名称（可选）")


class DesignParseOutput(BaseModel):
    """设计稿解析节点输出"""
    components: List[Dict[str, Any]] = Field(default=[], description="组件列表")
    layout: Dict[str, Any] = Field(default={}, description="布局信息")
    static_assets: List[Dict[str, Any]] = Field(default=[], description="静态资源列表")
    mastergo_summary: str = Field(..., description="设计稿摘要")


class MasterGoAssetUploadInput(BaseModel):
    """MasterGo 资产上传节点输入"""
    mastergo_url: str = Field(..., description="MasterGo 设计稿 URL")
    upload_prefix: Optional[str] = Field(default="mastergo/assets/", description="上传前缀（可选）")
    formats: Optional[List[str]] = Field(default=["png"], description="图片格式列表（可选）")
    scales: Optional[List[int]] = Field(default=[1, 2, 3], description="图片倍数列表（可选）")


class MasterGoAssetUploadOutput(BaseModel):
    """MasterGo 资产上传节点输出"""
    success: bool = Field(..., description="是否成功")
    assets: List[Dict[str, Any]] = Field(default=[], description="上传的资产列表")
    message: str = Field(..., description="处理消息")
    total: int = Field(default=0, description="总资产数")
    successful: int = Field(default=0, description="成功上传数")
    failed: int = Field(default=0, description="失败数")


# ==================== Mock 服务相关定义 ====================

class ApiDefinition(BaseModel):
    """API 定义"""
    name: str = Field(..., description="API 名称")
    method: str = Field(..., description="HTTP 方法（GET/POST/PUT/DELETE）")
    path: str = Field(..., description="API 路径")
    description: Optional[str] = Field(default="", description="API 描述")
    request_params: Optional[Dict[str, Any]] = Field(default={}, description="请求参数")
    request_body: Optional[Dict[str, Any]] = Field(default={}, description="请求体")
    response_example: Optional[Dict[str, Any]] = Field(default={}, description="响应示例")
    status_code: Optional[int] = Field(default=200, description="HTTP 状态码")


class MockServiceGeneratorInput(BaseModel):
    """Mock 服务生成节点输入"""
    api_definitions: List[ApiDefinition] = Field(..., description="API 定义列表")
    mock_type: Optional[str] = Field(default="msw", description="Mock 类型（msw/mockjs）")
    use_realistic_data: Optional[bool] = Field(default=True, description="是否使用真实模拟数据")


class MockServiceGeneratorOutput(BaseModel):
    """Mock 服务生成节点输出"""
    success: bool = Field(..., description="是否成功")
    mock_code: str = Field(..., description="生成的 Mock 代码")
    mock_file_name: str = Field(default="mockHandlers.js", description="Mock 文件名")
    message: str = Field(..., description="处理消息")
    api_count: int = Field(default=0, description="生成的 API 数量")


class ApiParserInput(BaseModel):
    """API 解析节点输入"""
    api_source: str = Field(..., description="API 来源（postman/swagger/manual）")
    api_content: str = Field(..., description="API 内容（URL/JSON/文本）")


class ApiParserOutput(BaseModel):
    """API 解析节点输出"""
    success: bool = Field(..., description="是否成功")
    api_definitions: List[ApiDefinition] = Field(default=[], description="解析后的 API 定义列表")
    message: str = Field(..., description="处理消息")
    source_type: str = Field(..., description="来源类型")


# ==================== 组件识别节点定义 ====================

class ComponentIdentifyInput(BaseModel):
    """组件识别节点输入"""
    components: List[Dict[str, Any]] = Field(..., description="原始组件列表")
    layout: Dict[str, Any] = Field(default={}, description="布局信息")
    static_assets: List[Dict[str, Any]] = Field(default=[], description="静态资源列表")
    mastergo_url: str = Field(default="", description="MasterGo 设计稿 URL")


class ComponentIdentifyOutput(BaseModel):
    """组件识别节点输出"""
    identified_components: List[Dict[str, Any]] = Field(default=[], description="识别后的组件列表")
    component_hierarchy: Dict[str, Any] = Field(default={}, description="组件层次结构")
    design_summary: str = Field(..., description="设计摘要")
    suggestions: List[str] = Field(default=[], description="设计建议")


# ==================== H5 代码生成节点定义 ====================

class H5CodeGenerationInput(BaseModel):
    """H5 代码生成节点输入"""
    feature_list: List[str] = Field(..., description="功能列表")
    identified_components: List[Dict[str, Any]] = Field(..., description="识别后的组件列表")
    component_hierarchy: Dict[str, Any] = Field(default={}, description="组件层次结构")
    layout: Dict[str, Any] = Field(default={}, description="布局信息")
    static_assets: List[Dict[str, Any]] = Field(default=[], description="静态资源列表")
    api_definitions: List[Dict[str, Any]] = Field(default=[], description="API 定义列表")
    asset_mapping: Dict[str, str] = Field(default={}, description="资源映射表（组件名 → OSS URL）")  # 新增


class H5CodeGenerationOutput(BaseModel):
    """H5 代码生成节点输出"""
    success: bool = Field(..., description="是否成功")
    h5_generated_files: List[Dict[str, str]] = Field(default=[], description="生成的文件列表（path, content）")
    h5_generation_summary: str = Field(..., description="代码生成摘要")
    file_count: int = Field(default=0, description="生成的文件数量")
    tech_stack: str = Field(default="React 18 + TypeScript + Vite", description="使用的技术栈")


# ==================== 静态资源处理节点定义 ====================

class ExtractAssetsInput(BaseModel):
    """静态资源提取节点输入"""
    mastergo_url: str = Field(..., description="MasterGo 设计稿 URL")
    components: List[Dict[str, Any]] = Field(default=[], description="组件列表")
    layout: Dict[str, Any] = Field(default={}, description="布局信息")


class ExtractAssetsOutput(BaseModel):
    """静态资源提取节点输出"""
    raw_assets: List[Dict[str, Any]] = Field(default=[], description="提取的原始资源列表")
    asset_count: int = Field(default=0, description="资源总数")
    summary: str = Field(..., description="资源提取摘要")


class OptimizeAssetsInput(BaseModel):
    """资源优化节点输入"""
    raw_assets: List[Dict[str, Any]] = Field(..., description="原始资源列表")
    layout: Dict[str, Any] = Field(default={}, description="布局信息")
    optimize_icons: bool = Field(default=True, description="是否优化图标")
    optimize_backgrounds: bool = Field(default=True, description="是否优化背景图")
    generate_multi_scale: bool = Field(default=True, description="是否生成多倍图（iOS @2x, @3x）")


class OptimizeAssetsOutput(BaseModel):
    """资源优化节点输出"""
    optimized_assets: List[Dict[str, Any]] = Field(default=[], description="优化后的资源列表")
    categorized_assets: Dict[str, List[Dict[str, Any]]] = Field(default={}, description="分类后的资源（icons, backgrounds, illustrations, logos）")
    optimization_summary: str = Field(..., description="优化摘要")
    optimization_stats: Dict[str, Any] = Field(default={}, description="优化统计信息")


class UploadAssetsInput(BaseModel):
    """资源上传节点输入"""
    optimized_assets: List[Dict[str, Any]] = Field(..., description="优化后的资源列表")
    upload_prefix: str = Field(default="assets/", description="上传前缀")
    formats: List[str] = Field(default=["png", "webp"], description="支持的格式列表")


class UploadAssetsOutput(BaseModel):
    """资源上传节点输出"""
    uploaded_assets: List[Dict[str, Any]] = Field(default=[], description="上传成功的资源列表")
    asset_mapping: Dict[str, str] = Field(default={}, description="资源映射表（组件名 → OSS URL）")
    upload_summary: str = Field(..., description="上传摘要")
    success_count: int = Field(default=0, description="成功上传数")
    failed_count: int = Field(default=0, description="失败上传数")


class GenerateAssetMappingInput(BaseModel):
    """资源映射表生成节点输入"""
    uploaded_assets: List[Dict[str, Any]] = Field(..., description="已上传的资源列表")
    categorized_assets: Dict[str, List[Dict[str, Any]]] = Field(default={}, description="分类后的资源")
    platforms: List[str] = Field(default=["h5", "ios", "android", "harmonyos", "miniprogram"], description="目标平台列表")


class GenerateAssetMappingOutput(BaseModel):
    """资源映射表生成节点输出"""
    asset_mapping_files: Dict[str, Dict[str, Any]] = Field(default={}, description="各平台的资源映射文件")
    asset_mapping_json: Dict[str, Any] = Field(default={}, description="完整的资源映射 JSON")
    mapping_summary: str = Field(..., description="映射表生成摘要")


# ==================== 项目规则解析节点定义（已存在，保留引用）====================


