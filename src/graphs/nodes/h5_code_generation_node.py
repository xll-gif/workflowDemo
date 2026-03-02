"""
H5 代码生成节点

基于需求、设计稿和组件识别结果生成 H5 代码（React + TypeScript）
"""
import os
import json
import logging
import base64
from typing import List, Dict, Any
from pathlib import Path
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from jinja2 import Template
import requests

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入状态定义
from graphs.state import H5CodeGenerationInput, H5CodeGenerationOutput


def get_text_content(content) -> str:
    """
    安全地从 AIMessage content 中提取文本
    """
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        if content and isinstance(content[0], str):
            return " ".join(content)
        else:
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            return " ".join(text_parts)
    else:
        return str(content)


def download_static_asset(url: str, save_path: str) -> bool:
    """
    下载静态资源到本地
    
    Args:
        url: 资源 URL
        save_path: 保存路径
    
    Returns:
        是否下载成功
    """
    try:
        # 创建目录
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 下载文件
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 保存文件
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"静态资源下载成功: {url} -> {save_path}")
        return True
        
    except Exception as e:
        logger.error(f"静态资源下载失败: {url}, 错误: {e}")
        return False


def generate_mock_service(api_definitions: List[Dict[str, Any]]) -> str:
    """
    生成 Mock 服务代码（MSW）
    
    Args:
        api_definitions: API 定义列表
    
    Returns:
        Mock 服务代码
    """
    mock_code = """import { http, HttpResponse } from 'msw'

// Mock handlers for the application
export const handlers = [
"""

    for api in api_definitions:
        method = api.get("method", "GET").lower()
        path = api.get("url", api.get("path", ""))
        description = api.get("description", "")
        
        if method == "get":
            mock_code += f"""
  http.{method}('{path}', () => {{
    return HttpResponse.json({{
      success: true,
      data: {{}},
      message: '{description}'
    }})
  }}),
"""
        elif method == "post":
            mock_code += f"""
  http.{method}('{path}', async ({{ request }}) => {{
    const body = await request.json()
    return HttpResponse.json({{
      success: true,
      data: {{ token: 'mock-token-123', ...body }},
      message: '{description}'
    }})
  }}),
"""
        elif method == "put":
            mock_code += f"""
  http.{method}('{path}', async ({{ request }}) => {{
    const body = await request.json()
    return HttpResponse.json({{
      success: true,
      data: {{ ...body }},
      message: '{description}'
    }})
  }}),
"""
        elif method == "delete":
            mock_code += f"""
  http.{method}('{path}', () => {{
    return HttpResponse.json({{
      success: true,
      message: '{description}'
    }})
  }}),
"""
    
    mock_code += """]

// MSW setup for browser
if (typeof window !== 'undefined' && window.ServiceWorkerGlobalScope) {
  // Running in browser
}

export default handlers
"""
    
    return mock_code


def generate_package_json() -> str:
    """生成 package.json"""
    return json.dumps({
        "name": "frontend-automation-h5",
        "version": "1.0.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "tsc && vite build",
            "preview": "vite preview",
            "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
        },
        "dependencies": {
            "react": "^18.3.1",
            "react-dom": "^18.3.1",
            "react-router-dom": "^6.26.0",
            "axios": "^1.7.7",
            "msw": "^2.4.0"
        },
        "devDependencies": {
            "@types/react": "^18.3.3",
            "@types/react-dom": "^18.3.0",
            "@typescript-eslint/eslint-plugin": "^8.0.1",
            "@typescript-eslint/parser": "^8.0.1",
            "@vitejs/plugin-react": "^4.3.1",
            "eslint": "^9.9.0",
            "eslint-plugin-react-hooks": "^5.1.0",
            "eslint-plugin-react-refresh": "^0.4.9",
            "typescript": "^5.5.4",
            "vite": "^5.4.2"
        }
    }, indent=2)


def generate_vite_config() -> str:
    """生成 vite.config.ts"""
    return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@assets': path.resolve(__dirname, './assets')
    }
  },
  server: {
    port: 3000,
    open: true
  }
})
"""


def generate_tsconfig_json() -> str:
    """生成 tsconfig.json"""
    return """{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@assets/*": ["./assets/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}"""


def generate_index_html(title: str) -> str:
    """生成 index.html"""
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""


def h5_code_generation_node(
    state: H5CodeGenerationInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> H5CodeGenerationOutput:
    """
    title: H5 代码生成
    desc: 基于需求、设计稿和组件识别结果生成完整的 H5 代码（React + TypeScript）
    integrations: 大语言模型
    """
    logger.info("开始 H5 代码生成节点")
    logger.info(f"功能列表: {len(state.feature_list)} 项")
    logger.info(f"组件数量: {len(state.identified_components)} 个")
    logger.info(f"静态资源: {len(state.static_assets)} 个")
    logger.info(f"资源映射表: {len(state.asset_mapping)} 个条目")

    # 1. 准备静态资源数据（使用 OSS URL）
    # 优先使用资源映射表中的 OSS URL，如果没有映射则使用原始 URL
    prepared_assets = []
    for asset in state.static_assets:
        asset_name = asset.get("name", "")
        asset_type = asset.get("type", "")
        original_url = asset.get("url", "")

        # 查找映射表中的 OSS URL
        oss_url = state.asset_mapping.get(asset_name, original_url)

        if asset_name and asset_type == "IMAGE":
            prepared_assets.append({
                "name": asset_name,
                "type": asset_type,
                "url": oss_url,  # 使用 OSS URL
                "original_url": original_url,
                "local_import": f"@assets/{asset_name}",  # 用于 import 语句
                "remote_url": oss_url  # 用于直接引用
            })

    logger.info(f"准备 {len(prepared_assets)} 个静态资源（使用 OSS URL）")

    # 2. 生成资源映射文件（如果还没有生成）
    if not state.asset_mapping:
        logger.warning("资源映射表为空，将使用原始 URL")

    # 3. 生成 Mock 服务代码
    mock_service_code = generate_mock_service(state.api_definitions)
    
    # 3. 从配置文件中读取大模型配置
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r') as fd:
        _cfg = json.load(fd)

    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    # 4. 准备大模型输入数据
    prompt_data = {
        "feature_list": json.dumps(state.feature_list, ensure_ascii=False),
        "components": json.dumps(state.identified_components, ensure_ascii=False),
        "component_hierarchy": json.dumps(state.component_hierarchy, ensure_ascii=False),
        "layout": json.dumps(state.layout, ensure_ascii=False),
        "static_assets": json.dumps(prepared_assets, ensure_ascii=False),  # 使用 prepared_assets
        "asset_mapping": json.dumps(state.asset_mapping, ensure_ascii=False),  # 新增资源映射表
        "api_definitions": json.dumps(state.api_definitions, ensure_ascii=False)
    }

    # 使用 jinja2 模板渲染用户提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render(prompt_data)

    logger.info(f"渲染后的用户提示词长度: {len(user_prompt_content)}")

    # 5. 初始化 LLM 客户端并调用
    ctx = runtime.context
    client = LLMClient(ctx=ctx)

    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt_content)
    ]

    try:
        logger.info(f"调用大模型: {llm_config.get('model', 'unknown')}")
        
        response = client.invoke(
            messages=messages,
            model=llm_config.get("model", "doubao-seed-1-8-251228"),
            temperature=llm_config.get("temperature", 0.5),
            top_p=llm_config.get("top_p", 0.7),
            max_completion_tokens=llm_config.get("max_completion_tokens", 4000),
            thinking=llm_config.get("thinking", "disabled")
        )
        
        # 提取响应内容
        response_text = get_text_content(response.content)
        logger.info(f"大模型响应长度: {len(response_text)}")
        
        # 保存原始响应用于调试
        debug_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH", ""), "debug_llm_response.txt")
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(response_text)
        logger.info(f"已保存大模型响应到: {debug_file}")
        
        # 解析 JSON 响应
        try:
            # 尝试直接解析
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            # 如果直接解析失败，尝试提取 JSON 代码块
            logger.warning(f"直接解析 JSON 失败，尝试提取代码块: {e}")
            
            # 尝试提取 ```json ... ``` 中的内容
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
                logger.info(f"提取的 JSON 长度: {len(response_text)}")
                result = json.loads(response_text)
            else:
                # 尝试提取 ``` ... ``` 中的内容
                code_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
                if code_match:
                    response_text = code_match.group(1)
                    logger.info(f"提取的代码块长度: {len(response_text)}")
                    result = json.loads(response_text)
                else:
                    # 最后尝试：提取第一个 { ... } 对
                    brace_start = response_text.find('{')
                    brace_end = response_text.rfind('}')
                    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
                        response_text = response_text[brace_start:brace_end+1]
                        logger.info(f"提取的 brace 块长度: {len(response_text)}")
                        result = json.loads(response_text)
                    else:
                        raise Exception(f"无法从响应中提取有效的 JSON: {e}")
            generated_files = result.get("generated_files", [])
            summary = result.get("summary", "H5 代码生成完成")
            
            # 添加基础配置文件
            generated_files.extend([
                {
                    "path": "package.json",
                    "content": generate_package_json()
                },
                {
                    "path": "vite.config.ts",
                    "content": generate_vite_config()
                },
                {
                    "path": "tsconfig.json",
                    "content": generate_tsconfig_json()
                },
                {
                    "path": "index.html",
                    "content": generate_index_html(state.feature_list[0] if state.feature_list else "H5 Application")
                },
                {
                    "path": "src/mock/handlers.ts",
                    "content": mock_service_code
                }
            ])
            
            logger.info(f"代码生成完成: {len(generated_files)} 个文件")
            
            return H5CodeGenerationOutput(
                success=True,
                h5_generated_files=generated_files,
                h5_generation_summary=summary,
                file_count=len(generated_files),
                tech_stack="React 18 + TypeScript + Vite + MSW"
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"解析大模型响应 JSON 失败: {e}")
            logger.error(f"原始响应: {response_text[:500]}")
            raise Exception(f"大模型返回的不是有效的 JSON 格式: {e}")
        
    except Exception as e:
        logger.error(f"调用大模型失败: {e}")
        raise Exception(f"H5 代码生成失败: {e}")


# 测试代码
if __name__ == "__main__":
    # 测试节点
    print("测试 H5 代码生成节点")
    print("=" * 80)

    # 创建测试输入
    test_input = H5CodeGenerationInput(
        feature_list=["实现登录页面"],
        identified_components=[
            {
                "id": "btn_login",
                "name": "LoginButton",
                "type": "Button",
                "component_type": "interactive",
                "props": {
                    "text": "登录",
                    "backgroundColor": "#1890ff",
                    "borderRadius": 4
                },
                "purpose": "primary_action",
                "accessible": True,
                "responsiveness": "adaptive"
            },
            {
                "id": "input_username",
                "name": "UsernameInput",
                "type": "Input",
                "component_type": "form",
                "props": {
                    "placeholder": "请输入用户名",
                    "borderRadius": 4
                },
                "purpose": "user_input",
                "validation_required": True,
                "accessible": True
            }
        ],
        component_hierarchy={
            "root": {
                "type": "Container",
                "children": ["LoginButton", "UsernameInput"]
            },
            "total_components": 2,
            "depth": 2
        },
        layout={
            "colors": {
                "primary": "#1890ff",
                "background": "#ffffff"
            }
        },
        static_assets=[
            {
                "id": "img_logo",
                "name": "logo.png",
                "type": "IMAGE",
                "url": "https://via.placeholder.com/100x100"
            }
        ],
        api_definitions=[
            {
                "method": "POST",
                "url": "/api/auth/login",
                "description": "用户登录接口"
            }
        ]
    )

    # 创建模拟的 Runtime 和 Context
    from unittest.mock import MagicMock

    mock_config = {
        "metadata": {
            "llm_cfg": "config/h5_code_generation_cfg.json"
        }
    }
    mock_runtime = MagicMock()
    mock_runtime.context = MagicMock()

    # 执行节点
    try:
        result = h5_code_generation_node(test_input, mock_config, mock_runtime)

        print("\n✅ 节点执行成功！")
        print(f"\n生成文件数量: {result.file_count}")
        print(f"技术栈: {result.tech_stack}")
        print(f"\n摘要: {result.h5_generation_summary}")
        
        print("\n生成的文件列表:")
        for i, file_info in enumerate(result.h5_generated_files, 1):
            print(f"  {i}. {file_info['path']}")

    except Exception as e:
        print(f"\n❌ 节点执行失败: {e}")
        import traceback
        traceback.print_exc()
