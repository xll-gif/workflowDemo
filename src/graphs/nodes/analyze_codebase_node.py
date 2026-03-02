"""
代码仓库分析节点
从 GitHub 仓库拉取代码并分析项目结构
"""
import os
import json
from typing import List, Dict, Any, Optional
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from pydantic import BaseModel, Field

# 导入 GitHub API 工具
from tools.github_api import GitHubAPI, get_repo_info, get_file_from_repo, get_repo_directory
from graphs.state import GlobalState


# ==================== 状态定义 ====================

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


# ==================== 节点实现 ====================

def analyze_codebase_node(
    state: AnalyzeCodebaseInput, 
    config: RunnableConfig, 
    runtime: Runtime[Context]
) -> AnalyzeCodebaseOutput:
    """
    title: 代码库分析
    desc: 从 GitHub 仓库拉取代码并分析项目结构、技术栈和关键文件
    integrations: GitHub API
    """
    ctx = runtime.context
    
    print("="*60)
    print("🔍 开始分析代码库")
    print("="*60)
    print(f"仓库: {state.repo_owner}/{state.repo_name}")
    print(f"分支: {state.repo_branch}")
    print(f"分析深度: {state.analyze_depth}")
    print()
    
    # 初始化 GitHub API
    github = GitHubAPI(token=state.github_token)
    
    # 1. 获取仓库基本信息
    print("📋 步骤 1: 获取仓库信息...")
    repo_info_dict = {}
    
    repo_info = github.get_repository_info(state.repo_owner, state.repo_name)
    if repo_info:
        repo_info_dict = {
            "full_name": repo_info.full_name,
            "description": repo_info.description,
            "language": repo_info.language,
            "stars": repo_info.stars,
            "forks": repo_info.forks,
            "default_branch": repo_info.default_branch,
            "clone_url": repo_info.clone_url
        }
        print(f"  ✅ {repo_info.full_name}")
        print(f"  📝 {repo_info.description}")
        print(f"  🌿 语言: {repo_info.language}")
        print(f"  ⭐ 星标: {repo_info.stars}")
    else:
        print("  ❌ 获取仓库信息失败")
    
    print()
    
    # 2. 分析项目结构
    print("📁 步骤 2: 分析项目结构...")
    project_structure = []
    
    def analyze_directory(path: str, depth: int = 0) -> List[Dict[str, Any]]:
        """递归分析目录结构"""
        if depth > state.analyze_depth:
            return []
        
        items = []
        contents = github.get_directory_contents(
            state.repo_owner,
            state.repo_name,
            path,
            state.repo_branch
        )
        
        for item in contents:
            item_info = {
                "name": item.name,
                "path": item.path,
                "type": item.type,
                "size": item.size,
                "depth": depth
            }
            items.append(item_info)
            
            # 如果是目录且深度未达上限，递归分析
            if item.type == "directory" and depth < state.analyze_depth:
                sub_items = analyze_directory(item.path, depth + 1)
                items.extend(sub_items)
        
        return items
    
    if repo_info:
        structure = analyze_directory("", 0)
        project_structure = structure
        print(f"  ✅ 找到 {len(structure)} 个文件/目录")
        
        # 显示前10个
        for item in structure[:10]:
            icon = "📁" if item["type"] == "directory" else "📄"
            indent = "  " * item["depth"]
            print(f"  {indent}{icon} {item['name']}")
        
        if len(structure) > 10:
            print(f"  ... 还有 {len(structure) - 10} 个文件")
    
    print()
    
    # 3. 分析技术栈
    print("🛠️  步骤 3: 分析技术栈...")
    tech_stack = {}
    
    # 尝试读取 package.json（JavaScript/TypeScript 项目）
    package_content = get_file_from_repo(
        state.repo_owner,
        state.repo_name,
        "package.json",
        state.repo_branch,
        state.github_token
    )
    
    if package_content:
        try:
            package_data = json.loads(package_content)
            tech_stack["name"] = package_data.get("name")
            tech_stack["version"] = package_data.get("version")
            tech_stack["type"] = "JavaScript/TypeScript"
            tech_stack["frameworks"] = []
            tech_stack["dependencies"] = list(package_data.get("dependencies", {}).keys())
            tech_stack["dev_dependencies"] = list(package_data.get("devDependencies", {}).keys())
            
            # 识别常见框架
            deps = set(tech_stack["dependencies"] + tech_stack["dev_dependencies"])
            if "react" in deps:
                tech_stack["frameworks"].append("React")
            if "vue" in deps:
                tech_stack["frameworks"].append("Vue")
            if "angular" in deps:
                tech_stack["frameworks"].append("Angular")
            if "next" in deps:
                tech_stack["frameworks"].append("Next.js")
            
            print(f"  ✅ 检测到 JavaScript/TypeScript 项目")
            print(f"  📦 框架: {', '.join(tech_stack['frameworks']) or '未检测到'}")
            print(f"  🔗 依赖数: {len(tech_stack['dependencies'])}")
            
        except json.JSONDecodeError:
            print("  ⚠️  package.json 解析失败")
    
    # 尝试读取 requirements.txt（Python 项目）
    if not tech_stack:
        requirements_content = get_file_from_repo(
            state.repo_owner,
            state.repo_name,
            "requirements.txt",
            state.repo_branch,
            state.github_token
        )
        
        if requirements_content:
            tech_stack["type"] = "Python"
            tech_stack["dependencies"] = [
                line.strip().split("==")[0].split(">=")[0].split("<=")[0]
                for line in requirements_content.split("\n")
                if line.strip() and not line.startswith("#")
            ]
            print(f"  ✅ 检测到 Python 项目")
            print(f"  🔗 依赖数: {len(tech_stack['dependencies'])}")
    
    # 尝试读取 go.mod（Go 项目）
    if not tech_stack:
        go_mod_content = get_file_from_repo(
            state.repo_owner,
            state.repo_name,
            "go.mod",
            state.repo_branch,
            state.github_token
        )
        
        if go_mod_content:
            tech_stack["type"] = "Go"
            tech_stack["dependencies"] = []
            for line in go_mod_content.split("\n"):
                if line.strip().startswith("require"):
                    deps = line.split()[1:]
                    if deps:
                        tech_stack["dependencies"].append(deps[0])
            print(f"  ✅ 检测到 Go 项目")
            print(f"  🔗 依赖数: {len(tech_stack['dependencies'])}")
    
    if not tech_stack:
        print(f"  ⚠️  无法自动识别技术栈")
        tech_stack["type"] = "Unknown"
        tech_stack["dependencies"] = []
    
    print()
    
    # 4. 识别关键文件
    print("🔑 步骤 4: 识别关键文件...")
    key_files = []
    
    # 常见关键文件列表
    key_file_patterns = [
        "README.md",
        "package.json",
        "tsconfig.json",
        ".gitignore",
        ".env.example",
        "LICENSE",
        "Dockerfile",
        "docker-compose.yml",
        "webpack.config.js",
        "vite.config.js",
        "next.config.js"
    ]
    
    root_files = github.get_directory_contents(
        state.repo_owner,
        state.repo_name,
        "",
        state.repo_branch
    )
    
    for pattern in key_file_patterns:
        for file in root_files:
            if file.name.lower() == pattern.lower():
                key_files.append(file.path)
                print(f"  ✅ {file.name}")
    
    print()
    
    print("="*60)
    print("✅ 代码库分析完成")
    print("="*60)
    print()
    
    return AnalyzeCodebaseOutput(
        repo_info=repo_info_dict,
        project_structure=project_structure,
        tech_stack=tech_stack,
        key_files=key_files
    )


# ==================== 测试代码 ====================

if __name__ == "__main__":
    """测试节点"""
    import sys
    sys.path.insert(0, os.path.join(os.getenv("COZE_WORKSPACE_PATH", "."), "src"))
    
    # 创建测试输入
    test_input = AnalyzeCodebaseInput(
        repo_owner="vuejs",
        repo_name="core",
        repo_branch="main",
        analyze_depth=1
    )
    
    # 模拟运行
    from unittest.mock import Mock
    mock_config = {}
    mock_runtime = Mock()
    mock_runtime.context = Mock()
    
    try:
        result = analyze_codebase_node(test_input, mock_config, mock_runtime)
        print("\n测试结果:")
        print(f"仓库信息: {result.repo_info}")
        print(f"技术栈: {result.tech_stack}")
        print(f"关键文件: {result.key_files}")
    except Exception as e:
        print(f"测试失败: {e}")
        print("提示: 如遇到速率限制，请配置 GITHUB_TOKEN 环境变量")
