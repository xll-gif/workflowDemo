"""
组件识别节点

使用大模型智能识别设计稿中的组件
"""
import os
import json
import logging
from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from jinja2 import Template

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入状态定义
from graphs.state import ComponentIdentifyInput, ComponentIdentifyOutput


def get_text_content(content) -> str:
    """
    安全地从 AIMessage content 中提取文本
    
    Args:
        content: AIMessage.content（可能是 str 或 list）
    
    Returns:
        提取的文本字符串
    """
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        if content and isinstance(content[0], str):
            # List of strings
            return " ".join(content)
        else:
            # List of dicts (multimodal response)
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            return " ".join(text_parts)
    else:
        return str(content)


def component_identify_node(
    state: ComponentIdentifyInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ComponentIdentifyOutput:
    """
    title: 组件识别
    desc: 使用大模型智能识别设计稿中的组件，生成层次结构和设计建议
    integrations: 大语言模型
    """
    logger.info("开始组件识别节点")
    logger.info(f"收到 {len(state.components)} 个组件")

    # 从配置文件中读取大模型配置
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r') as fd:
        _cfg = json.load(fd)

    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    # 使用 jinja2 模板渲染用户提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        "components": json.dumps(state.components, ensure_ascii=False),
        "layout": json.dumps(state.layout, ensure_ascii=False),
        "static_assets": json.dumps(state.static_assets, ensure_ascii=False),
        "mastergo_url": state.mastergo_url
    })

    logger.info(f"渲染后的用户提示词长度: {len(user_prompt_content)}")

    # 初始化 LLM 客户端
    ctx = runtime.context
    client = LLMClient(ctx=ctx)

    # 构建消息
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt_content)
    ]

    # 调用大模型
    logger.info(f"调用大模型: {llm_config.get('model', 'unknown')}")
    
    try:
        response = client.invoke(
            messages=messages,
            model=llm_config.get("model", "doubao-seed-1-8-251228"),
            temperature=llm_config.get("temperature", 0.3),
            top_p=llm_config.get("top_p", 0.7),
            max_completion_tokens=llm_config.get("max_completion_tokens", 2000),
            thinking=llm_config.get("thinking", "disabled")
        )
        
        # 提取响应内容
        response_text = get_text_content(response.content)
        logger.info(f"大模型响应长度: {len(response_text)}")
        
        # 解析 JSON 响应
        try:
            result = json.loads(response_text)
            
            identified_components = result.get("identified_components", [])
            component_hierarchy = result.get("component_hierarchy", {})
            design_summary = result.get("design_summary", "")
            suggestions = result.get("suggestions", [])
            
            logger.info(f"识别完成: {len(identified_components)} 个组件")
            logger.info(f"生成建议: {len(suggestions)} 条")
            
            return ComponentIdentifyOutput(
                identified_components=identified_components,
                component_hierarchy=component_hierarchy,
                design_summary=design_summary,
                suggestions=suggestions
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"解析大模型响应 JSON 失败: {e}")
            logger.error(f"原始响应: {response_text[:500]}")
            raise Exception(f"大模型返回的不是有效的 JSON 格式: {e}")
        
    except Exception as e:
        logger.error(f"调用大模型失败: {e}")
        raise Exception(f"组件识别失败: {e}")


# 测试代码
if __name__ == "__main__":
    # 测试节点
    print("测试组件识别节点")
    print("=" * 80)

    # 创建测试输入
    test_input = ComponentIdentifyInput(
        components=[
            {
                "id": "btn_login",
                "name": "LoginButton",
                "type": "BUTTON",
                "props": {
                    "text": "登录",
                    "backgroundColor": "#1890ff",
                    "borderRadius": 4
                }
            },
            {
                "id": "input_username",
                "name": "UsernameInput",
                "type": "INPUT",
                "props": {
                    "placeholder": "请输入用户名",
                    "borderRadius": 4
                }
            }
        ],
        layout={
            "colors": {
                "primary": "#1890ff",
                "background": "#ffffff"
            }
        },
        static_assets=[],
        mastergo_url="https://mastergo.com/design/login"
    )

    # 创建模拟的 Runtime 和 Context
    from unittest.mock import MagicMock

    mock_config = {
        "metadata": {
            "llm_cfg": "config/component_identify_cfg.json"
        }
    }
    mock_runtime = MagicMock()
    mock_runtime.context = MagicMock()

    # 执行节点
    try:
        result = component_identify_node(test_input, mock_config, mock_runtime)

        print("\n✅ 节点执行成功！")
        print("\n识别后的组件:")
        for comp in result.identified_components:
            print(f"  - {comp['name']} ({comp['type']}) - {comp.get('purpose', 'N/A')}")

        print("\n组件层次结构:")
        print(json.dumps(result.component_hierarchy, indent=2, ensure_ascii=False))

        print("\n设计摘要:")
        print(result.design_summary)

        print("\n设计建议:")
        for i, suggestion in enumerate(result.suggestions, 1):
            print(f"  {i}. {suggestion}")

    except Exception as e:
        print(f"\n❌ 节点执行失败: {e}")
        import traceback
        traceback.print_exc()
