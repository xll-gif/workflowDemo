"""
静态资源提取节点

从 MasterGo 设计稿中提取所有静态资源（图片、图标、背景等）
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# 导入状态定义
from graphs.state import (
    ExtractAssetsInput,
    ExtractAssetsOutput
)

# 导入 MCP 客户端
from tools.mastergo_mcp_client import create_mastergo_client


def extract_assets_node(
    state: ExtractAssetsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ExtractAssetsOutput:
    """
    title: 静态资源提取
    desc: 从 MasterGo 设计稿中提取所有图片、图标等静态资源
    integrations: MasterGo Magic MCP
    """
    ctx = runtime.context

    # 获取配置
    use_mock = os.getenv("USE_MOCK_MCP", "true").lower() == "true"

    logger.info(f"开始提取静态资源")
    logger.info(f"  MasterGo URL: {state.mastergo_url}")
    logger.info(f"  使用 Mock: {use_mock}")

    # 创建 MCP 客户端
    client = create_mastergo_client(use_mock=use_mock)

    # 启动客户端（如果不是 Mock）
    if not use_mock:
        if not client.start():
            raise RuntimeError("无法启动 MasterGo MCP 服务器")
        logger.info("MasterGo MCP 服务器已启动")

    # 获取设计数据
    logger.info("正在获取设计数据...")
    try:
        design_data = client.get_design(state.mastergo_url)
        logger.info(f"设计数据获取成功，文件名: {design_data.get('name', 'Unknown')}")
    except Exception as e:
        logger.error(f"获取设计数据失败: {e}")
        raise

    # 提取所有资源
    raw_assets = []

    # 1. 从设计数据中提取图片资源
    logger.info("正在提取图片资源...")
    try:
        assets = client.export_assets(
            state.mastergo_url,
            asset_types=["IMAGE", "ICON"]
        )

        for asset in assets:
            asset_data = {
                "id": asset.get("id", ""),
                "name": asset.get("name", ""),
                "type": asset.get("type", "IMAGE"),
                "url": asset.get("url", ""),
                "width": asset.get("width", 0),
                "height": asset.get("height", 0),
                "format": asset.get("format", "png"),
                "source": "mastergo",
                "parent_node": asset.get("parent_node", ""),
                "usage_hint": asset.get("usage_hint", "unknown")
            }
            raw_assets.append(asset_data)
            logger.debug(f"  - {asset_data['name']} ({asset_data['type']}): {asset_data['url']}")

        logger.info(f"✅ 提取到 {len(raw_assets)} 个资源")

    except Exception as e:
        logger.error(f"提取资源失败: {e}")
        # 即使失败也返回空列表，不中断流程
        raw_assets = []

    # 2. 从布局信息中提取背景图
    logger.info("正在提取背景图...")
    if state.layout and "background" in state.layout:
        background = state.layout["background"]
        if background and isinstance(background, dict):
            bg_image = background.get("image")
            if bg_image:
                bg_asset = {
                    "id": f"bg_{raw_assets}",
                    "name": "page_background",
                    "type": "BACKGROUND",
                    "url": bg_image,
                    "width": background.get("width", 0),
                    "height": background.get("height", 0),
                    "format": "png",
                    "source": "layout",
                    "parent_node": "root",
                    "usage_hint": "background"
                }
                raw_assets.insert(0, bg_asset)  # 背景图放在最前面
                logger.info(f"✅ 提取到背景图: {bg_image}")

    # 3. 从组件中提取资源
    logger.info("正在从组件中提取资源...")
    if state.components:
        for component in state.components:
            component_name = component.get("name", "unknown")

            # 检查组件中的图片
            if "image" in component:
                image = component["image"]
                if isinstance(image, str) and image.startswith("http"):
                    asset_data = {
                        "id": f"component_{component_name}_{len(raw_assets)}",
                        "name": f"{component_name}_image",
                        "type": "COMPONENT_IMAGE",
                        "url": image,
                        "width": component.get("width", 0),
                        "height": component.get("height", 0),
                        "format": "png",
                        "source": "component",
                        "parent_node": component_name,
                        "usage_hint": "component_image"
                    }
                    raw_assets.append(asset_data)
                    logger.debug(f"  - 组件 {component_name} 中的图片: {image}")

    # 停止客户端（如果不是 Mock）
    if not use_mock:
        client.stop()
        logger.info("MasterGo MCP 服务器已停止")

    # 生成摘要
    summary = f"从设计稿中提取到 {len(raw_assets)} 个静态资源"
    logger.info(f"✅ {summary}")

    # 按类型统计
    type_stats = {}
    for asset in raw_assets:
        asset_type = asset["type"]
        type_stats[asset_type] = type_stats.get(asset_type, 0) + 1

    if type_stats:
        logger.info("资源类型分布:")
        for asset_type, count in type_stats.items():
            logger.info(f"  - {asset_type}: {count}")

    return ExtractAssetsOutput(
        raw_assets=raw_assets,
        asset_count=len(raw_assets),
        summary=summary
    )


# 测试代码
if __name__ == "__main__":
    print("测试静态资源提取节点")
    print("=" * 80)

    # 创建测试输入
    test_input = ExtractAssetsInput(
        mastergo_url="https://mastergo.com/design/login",
        components=[
            {"name": "login_form", "image": "https://example.com/bg.jpg", "width": 375, "height": 667}
        ],
        layout={"background": {"image": "https://example.com/page_bg.png", "width": 375, "height": 667}}
    )

    # 创建模拟的 Runtime 和 Context
    from unittest.mock import MagicMock

    mock_config = {}
    mock_runtime = MagicMock()
    mock_context = MagicMock()
    mock_runtime.context = mock_context

    # 运行节点
    result = extract_assets_node(test_input, mock_config, mock_runtime)

    print("\n结果:")
    print(f"  资源总数: {result.asset_count}")
    print(f"  摘要: {result.summary}")
    print(f"  资源列表:")
    for asset in result.raw_assets:
        print(f"    - {asset['name']} ({asset['type']}): {asset['url']}")
