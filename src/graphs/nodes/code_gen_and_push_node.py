"""
代码生成与推送节点
拉取仓库代码、生成新代码、提交并推送到远程
"""
import os
import json
from typing import List, Dict, Any, Optional
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from pydantic import BaseModel, Field

# 导入 GitHub API 工具
from tools.github_api import GitHubAPI
from graphs.state import GlobalState


# ==================== 状态定义 ====================

class CodeGenAndPushInput(BaseModel):
    """代码生成与推送节点输入"""
    repo_owner: str = Field(..., description="GitHub 仓库所有者")
    repo_name: str = Field(..., description="GitHub 仓库名称")
    repo_dir: str = Field(..., description="仓库本地路径")
    base_branch: str = Field(default="main", description="基础分支名")
    feature_branch: str = Field(..., description="特性分支名")
    github_token: str = Field(..., description="GitHub Token（必须）")
    
    # 代码生成配置
    files_to_generate: List[Dict[str, str]] = Field(
        default=[],
        description="要生成的文件列表，每个包含 path 和 content"
    )
    commit_message: str = Field(..., description="提交消息")
    
    # PR 配置
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


# ==================== 节点实现 ====================

def code_gen_and_push_node(
    state: CodeGenAndPushInput, 
    config: RunnableConfig, 
    runtime: Runtime[Context]
) -> CodeGenAndPushOutput:
    """
    title: 代码生成与推送
    desc: 拉取仓库代码、生成新文件、提交并推送到远程，可选创建 Pull Request
    integrations: GitHub API
    """
    ctx = runtime.context
    
    print("="*70)
    print("🚀 代码生成与推送工作流")
    print("="*70)
    print(f"仓库: {state.repo_owner}/{state.repo_name}")
    print(f"本地路径: {state.repo_dir}")
    print(f"基础分支: {state.base_branch}")
    print(f"特性分支: {state.feature_branch}")
    print(f"待生成文件数: {len(state.files_to_generate)}")
    print(f"创建 PR: {'是' if state.create_pr else '否'}")
    print()
    
    # 初始化 GitHub API
    github = GitHubAPI(token=state.github_token)
    
    # 结果对象
    result = CodeGenAndPushOutput(
        success=False,
        branch_created=False,
        files_generated=[],
        commit_created=False,
        push_successful=False,
        pr_url="",
        error_message=""
    )
    
    # 步骤 1: 克隆或拉取仓库
    print("📥 步骤 1: 拉取仓库代码...")
    
    if os.path.exists(state.repo_dir):
        # 仓库已存在，执行拉取
        print(f"  仓库已存在，执行拉取...")
        pull_success = github.pull_repository(state.repo_dir, state.base_branch)
        if not pull_success:
            result.error_message = "拉取仓库失败"
            print("  ❌ 拉取失败")
            return result
        print("  ✅ 拉取成功")
    else:
        # 仓库不存在，执行克隆
        print(f"  仓库不存在，执行克隆...")
        clone_success = github.clone_repository(
            state.repo_owner,
            state.repo_name,
            state.repo_dir,
            state.base_branch,
            state.github_token
        )
        if not clone_success:
            result.error_message = "克隆仓库失败"
            print("  ❌ 克隆失败")
            return result
        print("  ✅ 克隆成功")
    
    print()
    
    # 步骤 2: 创建特性分支
    print("🌿 步骤 2: 创建特性分支...")
    branch_success = github.create_branch(
        state.repo_dir,
        state.feature_branch,
        state.base_branch
    )
    
    if not branch_success:
        result.error_message = "创建分支失败"
        print("  ❌ 创建分支失败")
        return result
    
    result.branch_created = True
    print(f"  ✅ 成功创建分支: {state.feature_branch}")
    print()
    
    # 步骤 3: 生成代码文件
    print("📝 步骤 3: 生成代码文件...")
    
    for file_info in state.files_to_generate:
        file_path = file_info.get("path")
        file_content = file_info.get("content")
        
        if not file_path or file_content is None:
            print(f"  ⚠️  跳过无效文件配置: {file_info}")
            continue
        
        # 构建完整文件路径
        full_path = os.path.join(state.repo_dir, file_path)
        
        # 创建目录（如果不存在）
        dir_path = os.path.dirname(full_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # 写入文件
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            result.files_generated.append(file_path)
            print(f"  ✅ 生成文件: {file_path}")
        except Exception as e:
            print(f"  ❌ 生成文件失败 {file_path}: {e}")
            result.error_message = f"生成文件失败: {str(e)}"
            return result
    
    if not result.files_generated:
        result.error_message = "没有生成任何文件"
        print("  ❌ 没有生成任何文件")
        return result
    
    print(f"  总共生成了 {len(result.files_generated)} 个文件")
    print()
    
    # 步骤 4: 提交修改
    print("💾 步骤 4: 提交修改...")
    commit_success = github.commit_changes(
        state.repo_dir,
        state.commit_message,
        result.files_generated  # 只提交生成的文件
    )
    
    if not commit_success:
        result.error_message = "提交修改失败"
        print("  ❌ 提交失败")
        return result
    
    result.commit_created = True
    print(f"  ✅ 提交成功: {state.commit_message}")
    print()
    
    # 步骤 5: 推送到远程
    print("📤 步骤 5: 推送到远程仓库...")
    push_success = github.push_repository(
        state.repo_dir,
        state.feature_branch,
        force=False,
        token=state.github_token
    )
    
    if not push_success:
        result.error_message = "推送到远程失败"
        print("  ❌ 推送失败")
        return result
    
    result.push_successful = True
    print(f"  ✅ 推送成功: {state.feature_branch}")
    print()
    
    # 步骤 6: 创建 Pull Request（可选）
    if state.create_pr:
        print("🔀 步骤 6: 创建 Pull Request...")
        
        pr_info = github.create_pull_request(
            state.repo_owner,
            state.repo_name,
            state.pr_title or state.commit_message,
            state.feature_branch,
            state.base_branch,
            state.pr_body or state.commit_message
        )
        
        if pr_info:
            result.pr_url = pr_info.get("url", "")
            print(f"  ✅ PR 创建成功: {result.pr_url}")
        else:
            print(f"  ⚠️  PR 创建失败（可能是已存在）")
    
    print()
    
    # 全部成功
    result.success = True
    
    print("="*70)
    print("✅ 代码生成与推送完成")
    print("="*70)
    print(f"分支: {state.feature_branch}")
    print(f"生成文件: {len(result.files_generated)} 个")
    print(f"推送状态: {'成功' if result.push_successful else '失败'}")
    if result.pr_url:
        print(f"PR 链接: {result.pr_url}")
    print()
    
    return result


# ==================== 测试代码 ====================

if __name__ == "__main__":
    """测试节点"""
    import sys
    sys.path.insert(0, os.path.join(os.getenv("COZE_WORKSPACE_PATH", "."), "src"))
    
    # 创建测试输入
    test_input = CodeGenAndPushInput(
        repo_owner="your-username",  # 替换为你的用户名
        repo_name="test-repo",       # 替换为你的仓库名
        repo_dir="/tmp/test-repo",
        base_branch="main",
        feature_branch="feature/auto-generated-code",
        github_token="your_github_token_here",  # 替换为你的 Token
        files_to_generate=[
            {
                "path": "src/generated/hello.js",
                "content": "// 自动生成的文件\nconsole.log('Hello from automated workflow!');"
            },
            {
                "path": "src/generated/utils.js",
                "content": "// 工具函数\nexport function greet(name) {\n  return `Hello, ${name}!`;\n}"
            },
            {
                "path": "README_AUTO.md",
                "content": "# 自动生成说明\n\n本文件由自动化工作流生成。"
            }
        ],
        commit_message="feat: 添加自动生成的代码文件",
        create_pr=False,  # 测试时先不创建 PR
        pr_title="自动生成的代码",
        pr_body="此 PR 由自动化工作流创建"
    )
    
    # 模拟运行
    from unittest.mock import Mock
    mock_config = {}
    mock_runtime = Mock()
    mock_runtime.context = Mock()
    
    try:
        result = code_gen_and_push_node(test_input, mock_config, mock_runtime)
        print("\n测试结果:")
        print(f"成功: {result.success}")
        print(f"生成的文件: {result.files_generated}")
        print(f"错误信息: {result.error_message}")
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
