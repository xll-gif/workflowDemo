"""
MasterGo 设计解析节点

使用 MasterGo Magic MCP 解析 MasterGo 设计稿
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入 MCP 客户端
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from tools.mastergo_mcp_client import create_mastergo_client

# 导入状态定义
from graphs.state import (
    DesignParseInput,
    DesignParseOutput
)


def design_parse_node(state: DesignParseInput, config: RunnableConfig, runtime: Runtime[Context]) -> DesignParseOutput:
    """
    title: MasterGo 设计解析
    desc: 使用 MasterGo Magic MCP 解析 MasterGo 设计稿，提取组件和资源信息
    integrations: MasterGo Magic MCP
    """
    # 获取环境变量
    use_mock = os.getenv("USE_MOCK_MCP", "true").lower() == "true"

    try:
        # 创建 MCP 客户端
        logger.info(f"正在创建 MasterGo MCP 客户端（Mock: {use_mock}）")
        client = create_mastergo_client(use_mock=use_mock)

        # 启动客户端（如果不是 Mock）
        if not use_mock:
            if not client.start():
                raise RuntimeError("无法启动 MasterGo MCP 服务器")
            logger.info("MasterGo MCP 服务器已启动")

        # 获取设计数据
        logger.info(f"正在解析设计: {state.mastergo_url}")
        design_data = client.get_design(state.mastergo_url)

        # 提取组件
        components = design_data.get("components", [])
        logger.info(f"找到 {len(components)} 个组件")

        # 提取资源
        assets = design_data.get("assets", [])
        logger.info(f"找到 {len(assets)} 个资源")

        # 提取样式
        styles = design_data.get("styles", {})
        logger.info(f"找到样式定义: {list(styles.keys())}")

        # 停止客户端（如果不是 Mock）
        if not use_mock:
            client.stop()
            logger.info("MasterGo MCP 服务器已停止")

        # 生成摘要
        summary = f"设计解析完成：包含 {len(components)} 个组件和 {len(assets)} 个资源"

        # 返回结果（匹配状态定义）
        return DesignParseOutput(
            components=components,
            layout=styles,  # 将样式信息作为布局信息
            static_assets=assets,  # 使用 static_assets 字段
            mastergo_summary=summary
        )

    except Exception as e:
        logger.error(f"设计解析失败: {e}")
        raise RuntimeError(f"MasterGo 设计解析失败: {e}")


def parse_design_details(design_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    解析设计详细信息

    Args:
        design_data: 原始设计数据

    Returns:
        解析后的详细信息
    """
    details = {
        "total_components": len(design_data.get("components", [])),
        "total_assets": len(design_data.get("assets", [])),
        "component_types": {},
        "asset_types": {},
    }

    # 统计组件类型
    for component in design_data.get("components", []):
        comp_type = component.get("type", "UNKNOWN")
        details["component_types"][comp_type] = details["component_types"].get(comp_type, 0) + 1

    # 统计资源类型
    for asset in design_data.get("assets", []):
        asset_type = asset.get("type", "UNKNOWN")
        details["asset_types"][asset_type] = details["asset_types"].get(asset_type, 0) + 1

    return details


# 测试代码
if __name__ == "__main__":
    # 测试节点
    print("测试 MasterGo 设计解析节点")
    print("=" * 80)

    # 创建测试输入
    test_input = DesignParseInput(
        mastergo_url="https://mastergo.com/design/login"
    )

    # 创建模拟的 Runtime 和 Context
    from unittest.mock import MagicMock

    mock_config = {}
    mock_runtime = MagicMock()
    mock_runtime.context = MagicMock()
    mock_runtime.context.logger = MagicMock()

    # 执行节点
    try:
        result = design_parse_node(test_input, mock_config, mock_runtime)

        print("\n✅ 节点执行成功！")
        print("\n组件列表:")
        for comp in result.components:
            print(f"  - {comp['name']} ({comp['type']})")

        print("\n资源列表:")
        for asset in result.static_assets:
            print(f"  - {asset['name']} ({asset['type']})")

        print("\n布局信息（样式）:")
        print(f"  颜色: {list(result.layout.get('colors', {}).keys())}")
        print(f"  字体: {list(result.layout.get('fonts', {}).keys())}")
        print(f"  间距: {list(result.layout.get('spacing', {}).keys())}")

        print("\n设计摘要:")
        print(f"  {result.mastergo_summary}")

    except Exception as e:
        print(f"\n❌ 节点执行失败: {e}")
        import traceback
        traceback.print_exc()
