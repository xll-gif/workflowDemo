import time
import json
import re
import os
import logging
from typing import List, Dict, Any, Optional
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import RequirementAnalysisInput, RequirementAnalysisOutput
from tools.github_api import get_github_issue, GitHubAPI, GitHubIssue

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_github_issue_with_retry(issue_url: str, token: Optional[str] = None, 
                                  max_retries: int = 3, initial_delay: float = 1.0) -> Optional[GitHubIssue]:
    """
    带重试机制的 GitHub Issue 获取
    
    Args:
        issue_url: GitHub Issue URL
        token: GitHub Token（可选）
        max_retries: 最大重试次数
        initial_delay: 初始延迟（秒）
        
    Returns:
        GitHubIssue 对象，失败返回 None
    """
    import requests
    
    for attempt in range(max_retries):
        try:
            logger.info(f"尝试获取 GitHub Issue（第 {attempt + 1}/{max_retries} 次）")
            
            issue = get_github_issue(issue_url, token)
            
            if issue:
                logger.info("成功获取 GitHub Issue")
                return issue
            else:
                logger.warning(f"第 {attempt + 1} 次尝试失败，返回 None")
                
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') and e.response else None
            
            if status_code == 403:
                # API 限流
                logger.warning(f"遇到 API 限流（403），等待后重试...")
                wait_time = initial_delay * (2 ** attempt)  # 指数退避
                logger.info(f"等待 {wait_time:.1f} 秒...")
                time.sleep(wait_time)
            elif status_code == 404:
                logger.error(f"Issue 不存在（404）: {issue_url}")
                return None
            else:
                logger.error(f"HTTP 错误 {status_code}: {e}")
                if attempt < max_retries - 1:
                    wait_time = initial_delay * (2 ** attempt)
                    time.sleep(wait_time)
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {e}")
            if attempt < max_retries - 1:
                wait_time = initial_delay * (2 ** attempt)
                time.sleep(wait_time)
                
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return None
    
    logger.error(f"经过 {max_retries} 次尝试后仍然失败")
    return None


def requirement_analysis_node(state: RequirementAnalysisInput, config: RunnableConfig, runtime: Runtime[Context]) -> RequirementAnalysisOutput:
    """
    title: 需求分析
    desc: 从 GitHub Issue 读取需求信息，提取功能列表和 API 定义
    integrations: GitHub API
    """
    logger.info("开始需求分析节点")
    
    # 如果没有提供 issue_body，从 GitHub 读取
    if not state.issue_body and state.github_issue_url:
        logger.info(f"正在从 GitHub 读取 Issue: {state.github_issue_url}")
        
        # 获取 GitHub Token
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            logger.info("使用 GitHub Token 进行认证")
        else:
            logger.warning("未设置 GITHUB_TOKEN 环境变量，将使用匿名访问（可能受到限流限制）")
        
        # 尝试读取 Issue（带重试机制）
        issue = fetch_github_issue_with_retry(state.github_issue_url, github_token)
        
        if issue:
            issue_title = issue.title
            issue_body = issue.body
            logger.info(f"✅ 成功读取 Issue: #{issue.number} - {issue_title}")
        else:
            logger.warning(f"⚠️ 读取 GitHub Issue 失败，使用提供的标题和内容")
            issue_title = state.issue_title or ""
            issue_body = state.issue_body or ""
    else:
        issue_title = state.issue_title or ""
        issue_body = state.issue_body or ""
        logger.info("使用提供的标题和内容")
    
    # 分析需求，提取功能列表
    feature_list = extract_features(issue_title, issue_body)
    logger.info(f"提取到 {len(feature_list)} 个功能")
    
    # 分析需求，提取 API 定义
    api_definitions = extract_api_definitions(issue_title, issue_body)
    logger.info(f"提取到 {len(api_definitions)} 个 API 定义")
    
    # 生成需求摘要
    summary = generate_summary(issue_title, issue_body, feature_list, api_definitions)

    # 提取 MasterGo URL
    mastergo_url = extract_mastergo_url(issue_title, issue_body)
    if mastergo_url:
        logger.info(f"提取到 MasterGo URL: {mastergo_url}")

    # 打印分析结果
    print("\n" + "="*60)
    print("需求分析结果")
    print("="*60)
    print(f"需求标题: {issue_title}")
    if mastergo_url:
        print(f"MasterGo URL: {mastergo_url}")
    print(f"\n功能列表 ({len(feature_list)} 项):")
    for i, feature in enumerate(feature_list, 1):
        print(f"  {i}. {feature}")

    print(f"\nAPI 定义 ({len(api_definitions)} 项):")
    for i, api in enumerate(api_definitions, 1):
        print(f"  {i}. {api.get('method', 'GET')} {api.get('url', 'N/A')}")

    print(f"\n需求摘要:\n{summary}")
    print("="*60 + "\n")

    return RequirementAnalysisOutput(
        feature_list=feature_list,
        api_definitions=api_definitions,
        summary=summary,
        mastergo_url=mastergo_url
    )


def extract_features(title: str, body: str) -> List[str]:
    """
    从 Issue 标题和内容中提取功能列表
    
    Args:
        title: Issue 标题
        body: Issue 内容
        
    Returns:
        功能列表
    """
    features = []
    
    # 合并标题和内容
    content = f"{title}\n{body}"
    
    # 先尝试匹配功能列表的标题（支持中文和英文冒号）
    feature_list_match = re.search(r'功能[列表]?\s*[:：]\s*\n', content)
    
    if feature_list_match:
        # 提取功能列表后的内容（最多20行）
        start_pos = feature_list_match.end()
        feature_section = content[start_pos:start_pos+1000]
        
        # 匹配列表项（支持 - * • 以及数字）
        list_items = re.findall(r'(?:[-*•]|\d+\.)\s*(.+)', feature_section)
        
        for item in list_items:
            item = item.strip()
            # 过滤掉空项和太短的项
            if item and len(item) > 2 and item not in features and '\n' not in item:
                features.append(item)
    
    # 如果仍然没有找到功能列表，尝试更简单的方法
    if not features:
        # 直接在内容中搜索所有以 - 开头的行
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # 匹配 - 功能、* 功能、1. 功能
            match = re.match(r'^[-*•\d+.]\s*(.+)', line)
            if match:
                item = match.group(1).strip()
                if item and len(item) > 2 and item not in features and '\n' not in item:
                    features.append(item)
    
    # 如果仍然没有找到功能列表，尝试从标题推断
    if not features and title:
        features.append(f"实现 {title}")
    
    # 从内容中提取句子级别的功能描述
    if not features and body:
        sentences = re.split(r'[。\n]', body)
        for sentence in sentences:
            sentence = sentence.strip()
            # 匹配包含"实现"、"添加"、"支持"等关键词的句子
            if any(keyword in sentence for keyword in ['实现', '添加', '支持', '需要', '包含']):
                if len(sentence) > 5 and sentence not in features:
                    features.append(sentence)
    
    return features


def extract_mastergo_url(title: str, body: str) -> str:
    """
    从 Issue 标题和内容中提取 MasterGo URL

    Args:
        title: Issue 标题
        body: Issue 内容

    Returns:
        MasterGo URL，未找到返回空字符串
    """
    content = f"{title}\n{body}"

    # 匹配 MasterGo URL 格式
    patterns = [
        r'https://mastergo\.com/design/[a-zA-Z0-9]+',
        r'https://mastergo\.com/file/[a-zA-Z0-9]+',
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(0)

    return ""


def extract_api_definitions(title: str, body: str) -> List[Dict[str, Any]]:
    """
    从 Issue 内容中提取 API 定义
    
    Args:
        title: Issue 标题
        body: Issue 内容
        
    Returns:
        API 定义列表
    """
    api_list = []
    
    # 合并标题和内容
    content = f"{title}\n{body}"
    
    # 匹配 API 格式
    patterns = [
        r'API[：:]\s*([A-Z]+)\s+(/[\w/]+)',  # API: POST /api/login
        r'/api/[^\s,]+',  # /api/xxx
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                method = match[0]
                url = match[1]
            else:
                method = "GET"
                url = match
            
            # 检查是否已存在
            existing = False
            for api in api_list:
                if api.get("url") == url:
                    existing = True
                    break
            
            if not existing:
                api_list.append({
                    "method": method,
                    "url": url,
                    "params": [],
                    "description": f"{method} {url}"
                })
    
    return api_list


def generate_summary(title: str, body: str, feature_list: List[str], api_definitions: List[Dict[str, Any]]) -> str:
    """
    生成需求摘要
    
    Args:
        title: Issue 标题
        body: Issue 内容
        feature_list: 功能列表
        api_definitions: API 定义
        
    Returns:
        需求摘要
    """
    summary_parts = []
    
    summary_parts.append(f"需求标题: {title}")
    summary_parts.append(f"功能数量: {len(feature_list)}")
    summary_parts.append(f"API 数量: {len(api_definitions)}")
    
    if feature_list:
        summary_parts.append("\n主要功能:")
        for i, feature in enumerate(feature_list[:3], 1):
            summary_parts.append(f"  {i}. {feature}")
        if len(feature_list) > 3:
            summary_parts.append(f"  ... 还有 {len(feature_list) - 3} 项功能")
    
    if api_definitions:
        summary_parts.append("\n相关 API:")
        for api in api_definitions[:3]:
            summary_parts.append(f"  - {api.get('method', 'GET')} {api.get('url')}")
        if len(api_definitions) > 3:
            summary_parts.append(f"  ... 还有 {len(api_definitions) - 3} 个 API")
    
    return "\n".join(summary_parts)
