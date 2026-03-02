

# ==================== 代码审查和测试节点定义 ====================

class CodeReviewInput(BaseModel):
    """代码审查节点输入"""
    platform: str = Field(..., description="目标平台（h5/ios/android/harmonyos/miniprogram）")
    all_generated_files: List[Dict[str, Any]] = Field(..., description="所有生成的文件列表")
    platform_files: Dict[str, List[Dict[str, str]]] = Field(default={}, description="按平台分组的文件列表")

class CodeReviewOutput(BaseModel):
    """代码审查节点输出"""
    overall_score: float = Field(..., description="整体评分（0-10）")
    issues: List[Dict[str, Any]] = Field(default=[], description="发现的问题列表")
    suggestions: List[Dict[str, Any]] = Field(default=[], description="改进建议列表")
    summary: str = Field(..., description="审查摘要")


class AutoTestInput(BaseModel):
    """自动化测试节点输入"""
    platform: str = Field(..., description="目标平台（h5/ios/android/harmonyos/miniprogram）")
    all_generated_files: List[Dict[str, Any]] = Field(..., description="所有生成的文件列表")
    platform_files: Dict[str, List[Dict[str, str]]] = Field(default={}, description="按平台分组的文件列表")

class AutoTestOutput(BaseModel):
    """自动化测试节点输出"""
    test_files: List[Dict[str, str]] = Field(..., description="测试文件列表")
    test_results: Dict[str, Any] = Field(..., description="测试结果")
    summary: str = Field(..., description="测试摘要")
