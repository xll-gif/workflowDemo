"""
GitHub API 工具
用于读取 GitHub Issues、Pull Requests 等信息
"""
import os
import requests
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class GitHubIssue(BaseModel):
    """GitHub Issue 数据模型"""
    id: int = Field(..., description="Issue ID")
    number: int = Field(..., description="Issue 编号")
    title: str = Field(..., description="Issue 标题")
    body: str = Field(default="", description="Issue 内容")
    state: str = Field(default="open", description="Issue 状态")
    created_at: str = Field(default="", description="创建时间")
    updated_at: str = Field(default="", description="更新时间")
    user: Dict[str, Any] = Field(default={}, description="创建者信息")
    labels: List[Dict[str, Any]] = Field(default=[], description="标签列表")
    url: str = Field(default="", description="Issue URL")


class GitHubFile(BaseModel):
    """GitHub 文件数据模型"""
    name: str = Field(..., description="文件名")
    path: str = Field(..., description="文件路径")
    type: str = Field(..., description="类型：file/directory/symlink")
    size: int = Field(default=0, description="文件大小（字节）")
    url: str = Field(default="", description="API URL")
    download_url: str = Field(default="", description="下载 URL")
    content: str = Field(default="", description="文件内容（Base64 编码）")
    sha: str = Field(default="", description="文件 SHA")


class GitHubRepository(BaseModel):
    """GitHub 仓库数据模型"""
    id: int = Field(..., description="仓库 ID")
    name: str = Field(..., description="仓库名称")
    full_name: str = Field(..., description="完整名称（owner/repo）")
    description: str = Field(default="", description="仓库描述")
    language: str = Field(default="", description="主要编程语言")
    stars: int = Field(default=0, description="星标数")
    forks: int = Field(default=0, description="Fork 数")
    open_issues: int = Field(default=0, description="Open Issue 数")
    clone_url: str = Field(default="", description="克隆 URL")
    default_branch: str = Field(default="main", description="默认分支")


class GitHubAPI:
    """GitHub API 客户端"""
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化 GitHub API 客户端
        
        Args:
            token: GitHub Personal Access Token（可选）
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Frontend-Automation-Workflow"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def get_issue(self, owner: str, repo: str, issue_number: int) -> Optional[GitHubIssue]:
        """
        获取单个 Issue
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            issue_number: Issue 编号
            
        Returns:
            GitHubIssue 对象，失败返回 None
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            issue = GitHubIssue(
                id=data.get("id"),
                number=data.get("number"),
                title=data.get("title", ""),
                body=data.get("body", ""),
                state=data.get("state", "open"),
                created_at=data.get("created_at", ""),
                updated_at=data.get("updated_at", ""),
                user=data.get("user", {}),
                labels=data.get("labels", []),
                url=data.get("html_url", "")
            )
            
            return issue
            
        except requests.exceptions.RequestException as e:
            print(f"获取 GitHub Issue 失败: {e}")
            return None
    
    def create_issue(self, owner: str, repo: str, title: str, body: str,
                    labels: Optional[List[str]] = None) -> Optional[GitHubIssue]:
        """
        创建 Issue
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            title: Issue 标题
            body: Issue 内容
            labels: 标签列表（可选）
            
        Returns:
            GitHubIssue 对象，失败返回 None
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        
        data = {
            "title": title,
            "body": body
        }
        
        if labels:
            data["labels"] = labels
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            issue = GitHubIssue(
                id=data.get("id"),
                number=data.get("number"),
                title=data.get("title", ""),
                body=data.get("body", ""),
                state=data.get("state", "open"),
                created_at=data.get("created_at", ""),
                updated_at=data.get("updated_at", ""),
                user=data.get("user", {}),
                labels=data.get("labels", []),
                url=data.get("html_url", "")
            )
            
            return issue
            
        except requests.exceptions.RequestException as e:
            print(f"创建 GitHub Issue 失败: {e}")
            if hasattr(e, "response") and e.response:
                print(f"   {e.response.text}")
            return None
    
    def get_file_content(self, owner: str, repo: str, file_path: str, 
                        branch: Optional[str] = None) -> Optional[str]:
        """
        获取文件内容
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            file_path: 文件路径
            branch: 分支名（可选，默认使用默认分支）
            
        Returns:
            文件内容字符串，失败返回 None
        """
        if branch is None:
            branch = self.get_default_branch(owner, repo)
            if branch is None:
                return None
        
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
        params = {"ref": branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            import base64
            content = base64.b64decode(data.get("content", "")).decode("utf-8")
            return content
            
        except requests.exceptions.RequestException as e:
            print(f"获取文件内容失败: {e}")
            return None
    
    def get_directory_contents(self, owner: str, repo: str, directory_path: str = "",
                              branch: Optional[str] = None) -> List[GitHubFile]:
        """
        获取目录内容
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            directory_path: 目录路径（空字符串表示根目录）
            branch: 分支名（可选）
            
        Returns:
            GitHubFile 对象列表
        """
        if branch is None:
            branch = self.get_default_branch(owner, repo)
            if branch is None:
                return []
        
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{directory_path}"
        params = {"ref": branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            files = []
            for item in data if isinstance(data, list) else [data]:
                github_file = GitHubFile(
                    name=item.get("name", ""),
                    path=item.get("path", ""),
                    type=item.get("type", "file"),
                    size=item.get("size", 0),
                    url=item.get("url", ""),
                    download_url=item.get("download_url", ""),
                    sha=item.get("sha", "")
                )
                files.append(github_file)
            
            return files
            
        except requests.exceptions.RequestException as e:
            print(f"获取目录内容失败: {e}")
            return []
    
    def get_repository_info(self, owner: str, repo: str) -> Optional[GitHubRepository]:
        """
        获取仓库信息
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            GitHubRepository 对象，失败返回 None
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            repo_info = GitHubRepository(
                id=data.get("id"),
                name=data.get("name", ""),
                full_name=data.get("full_name", ""),
                description=data.get("description", ""),
                language=data.get("language", ""),
                stars=data.get("stargazers_count", 0),
                forks=data.get("forks_count", 0),
                open_issues=data.get("open_issues_count", 0),
                clone_url=data.get("clone_url", ""),
                default_branch=data.get("default_branch", "main")
            )
            
            return repo_info
            
        except requests.exceptions.RequestException as e:
            print(f"获取仓库信息失败: {e}")
            return None
    
    def get_branch_list(self, owner: str, repo: str) -> List[Dict[str, str]]:
        """
        获取分支列表
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            分支列表，每个分支包含 name 和 sha
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/branches"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            branches = []
            for item in data:
                branches.append({
                    "name": item.get("name", ""),
                    "sha": item.get("commit", {}).get("sha", "")
                })
            
            return branches
            
        except requests.exceptions.RequestException as e:
            print(f"获取分支列表失败: {e}")
            return []
    
    def get_default_branch(self, owner: str, repo: str) -> Optional[str]:
        """
        获取默认分支
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            默认分支名，失败返回 None
        """
        repo_info = self.get_repository_info(owner, repo)
        if repo_info:
            return repo_info.default_branch
        return None
    
    def clone_repository(self, owner: str, repo: str, target_dir: str,
                        branch: Optional[str] = None, token: Optional[str] = None) -> bool:
        """
        克隆仓库到本地（使用 git 命令）
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            target_dir: 目标目录
            branch: 分支名（可选）
            token: GitHub Token（可选，用于私有仓库）
            
        Returns:
            成功返回 True，失败返回 False
        """
        import subprocess
        import os
        
        # 构建 URL（如果有 token，使用带认证的 URL）
        if token or self.token:
            auth_token = token or self.token
            clone_url = f"https://{auth_token}@github.com/{owner}/{repo}.git"
        else:
            clone_url = f"https://github.com/{owner}/{repo}.git"
        
        # 构建克隆命令
        cmd = ["git", "clone", clone_url, target_dir]
        if branch:
            cmd.extend(["--branch", branch, "--single-branch"])
        
        try:
            # 创建目标目录（如果不存在）
            os.makedirs(os.path.dirname(target_dir) or ".", exist_ok=True)
            
            # 执行克隆
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print(f"克隆失败: {result.stderr}")
                return False
            
            print(f"✅ 成功克隆仓库到: {target_dir}")
            return True
            
        except subprocess.TimeoutExpired:
            print("克隆超时")
            return False
        except Exception as e:
            print(f"克隆仓库失败: {e}")
            return False
    
    def pull_repository(self, repo_dir: str, branch: Optional[str] = None) -> bool:
        """
        拉取仓库最新代码
        
        Args:
            repo_dir: 仓库本地路径
            branch: 分支名（可选，默认当前分支）
            
        Returns:
            成功返回 True，失败返回 False
        """
        import subprocess
        
        if not os.path.exists(repo_dir):
            print(f"❌ 仓库目录不存在: {repo_dir}")
            return False
        
        try:
            # 切换到仓库目录
            original_dir = os.getcwd()
            os.chdir(repo_dir)
            
            # 拉取命令
            cmd = ["git", "pull", "origin"]
            if branch:
                cmd.append(branch)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            os.chdir(original_dir)
            
            if result.returncode != 0:
                print(f"❌ 拉取失败: {result.stderr}")
                return False
            
            print(f"✅ 成功拉取最新代码")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ 拉取超时")
            return False
        except Exception as e:
            print(f"❌ 拉取失败: {e}")
            return False
    
    def create_branch(self, repo_dir: str, branch_name: str, 
                     from_branch: Optional[str] = None) -> bool:
        """
        创建新分支
        
        Args:
            repo_dir: 仓库本地路径
            branch_name: 新分支名称
            from_branch: 基于哪个分支创建（可选，默认当前分支）
            
        Returns:
            成功返回 True，失败返回 False
        """
        import subprocess
        
        if not os.path.exists(repo_dir):
            print(f"❌ 仓库目录不存在: {repo_dir}")
            return False
        
        try:
            # 切换到仓库目录
            original_dir = os.getcwd()
            os.chdir(repo_dir)
            
            # 如果指定了源分支，先切换过去
            if from_branch:
                result = subprocess.run(
                    ["git", "checkout", from_branch],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    print(f"❌ 切换到分支 {from_branch} 失败: {result.stderr}")
                    os.chdir(original_dir)
                    return False
            
            # 创建并切换到新分支
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.chdir(original_dir)
            
            if result.returncode != 0:
                print(f"❌ 创建分支失败: {result.stderr}")
                return False
            
            print(f"✅ 成功创建分支: {branch_name}")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ 创建分支超时")
            return False
        except Exception as e:
            print(f"❌ 创建分支失败: {e}")
            return False
    
    def commit_changes(self, repo_dir: str, message: str, 
                      files: Optional[List[str]] = None) -> bool:
        """
        提交修改
        
        Args:
            repo_dir: 仓库本地路径
            message: 提交消息
            files: 要提交的文件列表（可选，None 表示提交所有修改）
            
        Returns:
            成功返回 True，失败返回 False
        """
        import subprocess
        
        if not os.path.exists(repo_dir):
            print(f"❌ 仓库目录不存在: {repo_dir}")
            return False
        
        try:
            # 切换到仓库目录
            original_dir = os.getcwd()
            os.chdir(repo_dir)
            
            # 添加文件
            if files:
                for file_path in files:
                    result = subprocess.run(
                        ["git", "add", file_path],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode != 0:
                        print(f"⚠️  添加文件 {file_path} 失败: {result.stderr}")
            else:
                # 添加所有修改
                result = subprocess.run(
                    ["git", "add", "."],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    print(f"⚠️  添加文件失败: {result.stderr}")
            
            # 提交
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.chdir(original_dir)
            
            if result.returncode != 0:
                # 可能是没有任何修改
                if "nothing to commit" in result.stdout:
                    print("⚠️  没有需要提交的修改")
                    return True
                print(f"❌ 提交失败: {result.stderr}")
                return False
            
            print(f"✅ 成功提交修改: {message}")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ 提交超时")
            return False
        except Exception as e:
            print(f"❌ 提交失败: {e}")
            return False
    
    def push_repository(self, repo_dir: str, branch: Optional[str] = None, 
                       force: bool = False, token: Optional[str] = None) -> bool:
        """
        推送代码到远程仓库
        
        Args:
            repo_dir: 仓库本地路径
            branch: 分支名（可选，默认当前分支）
            force: 是否强制推送
            token: GitHub Token（可选，用于私有仓库）
            
        Returns:
            成功返回 True，失败返回 False
        """
        import subprocess
        
        if not os.path.exists(repo_dir):
            print(f"❌ 仓库目录不存在: {repo_dir}")
            return False
        
        try:
            # 切换到仓库目录
            original_dir = os.getcwd()
            os.chdir(repo_dir)
            
            # 如果没有指定分支，获取当前分支
            if branch is None:
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0:
                    print(f"❌ 获取当前分支失败: {result.stderr}")
                    os.chdir(original_dir)
                    return False
                branch = result.stdout.strip()
            
            # 配置认证
            auth_token = token or self.token
            if auth_token:
                # 设置远程 URL 为带认证的 URL
                remote_url_result = subprocess.run(
                    ["git", "config", "--get", "remote.origin.url"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if remote_url_result.returncode == 0:
                    current_url = remote_url_result.stdout.strip()
                    if "github.com" in current_url and "@" not in current_url:
                        # 转换为带认证的 URL
                        parts = current_url.split("github.com/")
                        if len(parts) == 2:
                            new_url = f"https://{auth_token}@github.com/{parts[1]}"
                            subprocess.run(
                                ["git", "remote", "set-url", "origin", new_url],
                                capture_output=True,
                                timeout=10
                            )
            
            # 推送命令
            cmd = ["git", "push", "origin", branch]
            if force:
                cmd.append("--force")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            os.chdir(original_dir)
            
            if result.returncode != 0:
                print(f"❌ 推送失败: {result.stderr}")
                return False
            
            print(f"✅ 成功推送到远程: {branch}")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ 推送超时")
            return False
        except Exception as e:
            print(f"❌ 推送失败: {e}")
            return False
    
    def create_pull_request(self, owner: str, repo: str, title: str, 
                           head: str, base: str, body: str = "") -> Optional[Dict[str, Any]]:
        """
        创建 Pull Request
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            title: PR 标题
            head: 源分支（如：feature-branch）
            base: 目标分支（如：main）
            body: PR 描述
            
        Returns:
            PR 信息字典，失败返回 None
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            pr_data = response.json()
            
            pr_info = {
                "number": pr_data.get("number"),
                "title": pr_data.get("title"),
                "url": pr_data.get("html_url"),
                "state": pr_data.get("state"),
                "created_at": pr_data.get("created_at")
            }
            
            print(f"✅ 成功创建 PR: #{pr_info['number']} - {pr_info['title']}")
            print(f"🔗 链接: {pr_info['url']}")
            
            return pr_info
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 创建 PR 失败: {e}")
            return None
    
    def get_issues(self, owner: str, repo: str, state: str = "open", 
                   per_page: int = 10, page: int = 1) -> List[GitHubIssue]:
        """
        获取 Issue 列表
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            state: Issue 状态（open/closed/all）
            per_page: 每页数量
            page: 页码
            
        Returns:
            GitHubIssue 对象列表
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {
            "state": state,
            "per_page": per_page,
            "page": page
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            issues = []
            for item in data:
                issue = GitHubIssue(
                    id=item.get("id"),
                    number=item.get("number"),
                    title=item.get("title", ""),
                    body=item.get("body", ""),
                    state=item.get("state", "open"),
                    created_at=item.get("created_at", ""),
                    updated_at=item.get("updated_at", ""),
                    user=item.get("user", {}),
                    labels=item.get("labels", []),
                    url=item.get("html_url", "")
                )
                issues.append(issue)
            
            return issues
            
        except requests.exceptions.RequestException as e:
            print(f"获取 GitHub Issue 列表失败: {e}")
            return []
    
    def parse_issue_url(self, issue_url: str) -> Optional[Dict[str, str]]:
        """
        解析 GitHub Issue URL
        
        Args:
            issue_url: GitHub Issue URL，例如：https://github.com/owner/repo/issues/123
            
        Returns:
            包含 owner, repo, issue_number 的字典，失败返回 None
        """
        # 支持两种格式：
        # 1. https://github.com/owner/repo/issues/123
        # 2. owner/repo#123
        try:
            if "github.com" in issue_url:
                # 格式1: https://github.com/owner/repo/issues/123
                parts = issue_url.rstrip("/").split("/")
                issue_number = int(parts[-1])
                repo = parts[-3]
                owner = parts[-4]
            else:
                # 格式2: owner/repo#123
                repo_part, issue_part = issue_url.split("#")
                owner, repo = repo_part.split("/")
                issue_number = int(issue_part)
            
            return {
                "owner": owner,
                "repo": repo,
                "issue_number": issue_number
            }
        except Exception as e:
            print(f"解析 GitHub Issue URL 失败: {e}")
            return None


# 便捷函数
def get_github_issue(issue_url: str, token: Optional[str] = None) -> Optional[GitHubIssue]:
    """
    通过 URL 获取 GitHub Issue
    
    Args:
        issue_url: GitHub Issue URL
        token: GitHub Personal Access Token（可选）
        
    Returns:
        GitHubIssue 对象，失败返回 None
    """
    github = GitHubAPI(token)
    parsed = github.parse_issue_url(issue_url)
    
    if not parsed:
        return None
    
    return github.get_issue(
        owner=parsed["owner"],
        repo=parsed["repo"],
        issue_number=parsed["issue_number"]
    )


def get_file_from_repo(owner: str, repo: str, file_path: str, 
                      branch: Optional[str] = None, token: Optional[str] = None) -> Optional[str]:
    """
    从 GitHub 仓库获取文件内容
    
    Args:
        owner: 仓库所有者
        repo: 仓库名称
        file_path: 文件路径
        branch: 分支名（可选）
        token: GitHub Token（可选）
        
    Returns:
        文件内容字符串，失败返回 None
    """
    github = GitHubAPI(token)
    return github.get_file_content(owner, repo, file_path, branch)


def get_repo_directory(owner: str, repo: str, directory_path: str = "",
                      branch: Optional[str] = None, token: Optional[str] = None) -> List[GitHubFile]:
    """
    获取 GitHub 仓库目录内容
    
    Args:
        owner: 仓库所有者
        repo: 仓库名称
        directory_path: 目录路径（空字符串表示根目录）
        branch: 分支名（可选）
        token: GitHub Token（可选）
        
    Returns:
        GitHubFile 对象列表
    """
    github = GitHubAPI(token)
    return github.get_directory_contents(owner, repo, directory_path, branch)


def clone_github_repo(owner: str, repo: str, target_dir: str,
                     branch: Optional[str] = None, token: Optional[str] = None) -> bool:
    """
    克隆 GitHub 仓库到本地
    
    Args:
        owner: 仓库所有者
        repo: 仓库名称
        target_dir: 目标目录
        branch: 分支名（可选）
        token: GitHub Token（可选）
        
    Returns:
        成功返回 True，失败返回 False
    """
    github = GitHubAPI(token)
    return github.clone_repository(owner, repo, target_dir, branch)


def get_repo_info(owner: str, repo: str, token: Optional[str] = None) -> Optional[GitHubRepository]:
    """
    获取 GitHub 仓库信息
    
    Args:
        owner: 仓库所有者
        repo: 仓库名称
        token: GitHub Token（可选）
        
    Returns:
        GitHubRepository 对象，失败返回 None
    """
    github = GitHubAPI(token)
    return github.get_repository_info(owner, repo)


def pull_github_repo(repo_dir: str, branch: Optional[str] = None, 
                    token: Optional[str] = None) -> bool:
    """
    拉取 GitHub 仓库最新代码
    
    Args:
        repo_dir: 仓库本地路径
        branch: 分支名（可选）
        token: GitHub Token（可选）
        
    Returns:
        成功返回 True，失败返回 False
    """
    github = GitHubAPI(token)
    return github.pull_repository(repo_dir, branch)


def create_github_branch(repo_dir: str, branch_name: str, 
                        from_branch: Optional[str] = None, 
                        token: Optional[str] = None) -> bool:
    """
    创建 GitHub 仓库新分支
    
    Args:
        repo_dir: 仓库本地路径
        branch_name: 新分支名称
        from_branch: 基于哪个分支创建（可选）
        token: GitHub Token（可选）
        
    Returns:
        成功返回 True，失败返回 False
    """
    github = GitHubAPI(token)
    return github.create_branch(repo_dir, branch_name, from_branch)


def commit_github_changes(repo_dir: str, message: str, 
                         files: Optional[List[str]] = None,
                         token: Optional[str] = None) -> bool:
    """
    提交 GitHub 仓库修改
    
    Args:
        repo_dir: 仓库本地路径
        message: 提交消息
        files: 要提交的文件列表（可选）
        token: GitHub Token（可选）
        
    Returns:
        成功返回 True，失败返回 False
    """
    github = GitHubAPI(token)
    return github.commit_changes(repo_dir, message, files)


def push_github_repo(repo_dir: str, branch: Optional[str] = None, 
                    force: bool = False, token: Optional[str] = None) -> bool:
    """
    推送 GitHub 仓库代码到远程
    
    Args:
        repo_dir: 仓库本地路径
        branch: 分支名（可选）
        force: 是否强制推送
        token: GitHub Token（可选）
        
    Returns:
        成功返回 True，失败返回 False
    """
    github = GitHubAPI(token)
    return github.push_repository(repo_dir, branch, force, token)


def create_github_pull_request(owner: str, repo: str, title: str, 
                               head: str, base: str, body: str = "",
                               token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    创建 GitHub Pull Request
    
    Args:
        owner: 仓库所有者
        repo: 仓库名称
        title: PR 标题
        head: 源分支
        base: 目标分支
        body: PR 描述
        token: GitHub Token（可选）

    Returns:
        PR 信息字典，失败返回 None
    """
    github = GitHubAPI(token)
    return github.create_pull_request(owner, repo, title, head, base, body)

