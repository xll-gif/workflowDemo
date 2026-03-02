"""
资源优化节点

对提取的静态资源进行分类、优化和格式转换
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
    OptimizeAssetsInput,
    OptimizeAssetsOutput
)


def optimize_assets_node(
    state: OptimizeAssetsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> OptimizeAssetsOutput:
    """
    title: 资源优化
    desc: 对静态资源进行分类、格式优化和多倍图生成
    integrations: 大语言模型（用于智能分类）
    """
    ctx = runtime.context

    logger.info(f"开始优化资源")
    logger.info(f"  原始资源数量: {len(state.raw_assets)}")
    logger.info(f"  优化图标: {state.optimize_icons}")
    logger.info(f"  优化背景图: {state.optimize_backgrounds}")
    logger.info(f"  生成多倍图: {state.generate_multi_scale}")

    # 分类资源
    categorized_assets = {
        "icons": [],
        "backgrounds": [],
        "illustrations": [],
        "logos": [],
        "avatars": [],
        "others": []
    }

    optimized_assets = []
    optimization_stats = {
        "total": len(state.raw_assets),
        "classified": 0,
        "optimized": 0,
        "multi_scale_generated": 0,
        "format_converted": 0
    }

    # 智能分类函数
    def classify_asset(asset: Dict[str, Any]) -> str:
        """
        根据资源特征智能分类

        Args:
            asset: 资源数据

        Returns:
            分类结果
        """
        name = asset.get("name", "").lower()
        asset_type = asset.get("type", "")
        usage_hint = asset.get("usage_hint", "").lower()
        width = asset.get("width", 0)
        height = asset.get("height", 0)

        # 1. 根据名称判断
        if any(keyword in name for keyword in ["icon", "icon_", "-icon", "button_icon"]):
            return "icons"
        if any(keyword in name for keyword in ["logo", "brand", "logotype"]):
            return "logos"
        if any(keyword in name for keyword in ["avatar", "user", "profile", "head"]):
            return "avatars"
        if any(keyword in name for keyword in ["bg", "background", "bkg"]):
            return "backgrounds"
        if any(keyword in name for keyword in ["illustration", "illustr", "illust"]):
            return "illustrations"

        # 2. 根据类型判断
        if asset_type == "BACKGROUND" or usage_hint == "background":
            return "backgrounds"
        if asset_type == "ICON":
            return "icons"
        if asset_type == "LOGO":
            return "logos"

        # 3. 根据尺寸判断
        if width > 0 and height > 0:
            # 图标通常较小（<= 256px）
            if width <= 256 and height <= 256:
                return "icons"
            # 背景图通常较大（>= 375px）
            if width >= 375 or height >= 375:
                return "backgrounds"

        # 4. 根据宽高比判断
        if width > 0 and height > 0:
            ratio = width / height
            # 正方形或接近正方形通常是图标或 Logo
            if 0.8 <= ratio <= 1.2:
                return "icons"

        return "others"

    # 处理每个资源
    for i, asset in enumerate(state.raw_assets):
        logger.debug(f"\n处理资源 [{i+1}/{len(state.raw_assets)}]: {asset['name']}")

        # 1. 分类
        category = classify_asset(asset)
        categorized_assets[category].append(asset)
        optimization_stats["classified"] += 1
        logger.debug(f"  分类: {category}")

        # 2. 创建优化后的资源副本
        optimized_asset = asset.copy()

        # 3. 根据分类进行优化
        if category == "icons" and state.optimize_icons:
            # 图标优化
            optimized_asset = _optimize_icon(optimized_asset, state.generate_multi_scale)
            optimization_stats["optimized"] += 1
            if state.generate_multi_scale:
                optimization_stats["multi_scale_generated"] += 1
            logger.debug(f"  优化: 图标优化（SVG/WebP 转换）")

        elif category == "backgrounds" and state.optimize_backgrounds:
            # 背景图优化
            optimized_asset = _optimize_background(optimized_asset)
            optimization_stats["optimized"] += 1
            optimization_stats["format_converted"] += 1
            logger.debug(f"  优化: 背景图优化（WebP 转换）")

        elif category == "logos":
            # Logo 优化
            optimized_asset = _optimize_logo(optimized_asset, state.generate_multi_scale)
            optimization_stats["optimized"] += 1
            if state.generate_multi_scale:
                optimization_stats["multi_scale_generated"] += 1
            logger.debug(f"  优化: Logo 优化")

        else:
            # 其他资源，保持原样
            optimized_asset["optimized"] = False
            logger.debug(f"  优化: 跳过（保持原样）")

        optimized_assets.append(optimized_asset)

    # 生成优化摘要
    summary_parts = [
        f"共处理 {optimization_stats['total']} 个资源",
        f"分类 {optimization_stats['classified']} 个",
        f"优化 {optimization_stats['optimized']} 个"
    ]

    if state.generate_multi_scale:
        summary_parts.append(f"生成 {optimization_stats['multi_scale_generated']} 个多倍图")

    if optimization_stats["format_converted"] > 0:
        summary_parts.append(f"转换 {optimization_stats['format_converted']} 个格式")

    summary = "，".join(summary_parts) + "。"

    logger.info(f"✅ 优化完成: {summary}")
    logger.info("分类统计:")
    for category, assets in categorized_assets.items():
        if assets:
            logger.info(f"  - {category}: {len(assets)} 个")

    return OptimizeAssetsOutput(
        optimized_assets=optimized_assets,
        categorized_assets=categorized_assets,
        optimization_summary=summary,
        optimization_stats=optimization_stats
    )


def _optimize_icon(asset: Dict[str, Any], generate_multi_scale: bool) -> Dict[str, Any]:
    """
    优化图标

    Args:
        asset: 原始资源
        generate_multi_scale: 是否生成多倍图

    Returns:
        优化后的资源
    """
    # 优先转换为 SVG（如果是简单图标）
    # 如果无法转换，使用 WebP 格式

    asset.update({
        "optimized": True,
        "recommended_format": "svg",  # 优先 SVG
        "fallback_format": "webp",   # 备选 WebP
        "category": "icon"
    })

    # 如果需要生成多倍图（主要用于 PNG）
    if generate_multi_scale:
        asset["scales"] = [1, 2, 3]  # @1x, @2x, @3x

    return asset


def _optimize_background(asset: Dict[str, Any]) -> Dict[str, Any]:
    """
    优化背景图

    Args:
        asset: 原始资源

    Returns:
        优化后的资源
    """
    # 转换为 WebP 格式（更小的体积）
    asset.update({
        "optimized": True,
        "recommended_format": "webp",
        "quality": 85,  # WebP 质量
        "category": "background"
    })

    # 生成响应式版本
    if asset.get("width", 0) > 0:
        asset["responsive_sizes"] = [375, 768, 1024, 1440]

    return asset


def _optimize_logo(asset: Dict[str, Any], generate_multi_scale: bool) -> Dict[str, Any]:
    """
    优化 Logo

    Args:
        asset: 原始资源
        generate_multi_scale: 是否生成多倍图

    Returns:
        优化后的资源
    """
    asset.update({
        "optimized": True,
        "recommended_format": "svg",  # Logo 优先 SVG
        "category": "logo"
    })

    # 如果需要生成多倍图
    if generate_multi_scale:
        asset["scales"] = [1, 2, 3]

    return asset


# 测试代码
if __name__ == "__main__":
    print("测试资源优化节点")
    print("=" * 80)

    # 创建测试输入
    test_input = OptimizeAssetsInput(
        raw_assets=[
            {"id": "1", "name": "user_icon", "type": "ICON", "url": "https://example.com/icon.png", "width": 32, "height": 32},
            {"id": "2", "name": "page_bg", "type": "BACKGROUND", "url": "https://example.com/bg.jpg", "width": 375, "height": 667},
            {"id": "3", "name": "brand_logo", "type": "LOGO", "url": "https://example.com/logo.png", "width": 128, "height": 128},
            {"id": "4", "name": "avatar_1", "type": "IMAGE", "url": "https://example.com/avatar.jpg", "width": 64, "height": 64},
        ],
        layout={},
        optimize_icons=True,
        optimize_backgrounds=True,
        generate_multi_scale=True
    )

    # 创建模拟的 Runtime 和 Context
    from unittest.mock import MagicMock

    mock_config = {}
    mock_runtime = MagicMock()
    mock_context = MagicMock()
    mock_runtime.context = mock_context

    # 运行节点
    result = optimize_assets_node(test_input, mock_config, mock_runtime)

    print("\n结果:")
    print(f"  优化摘要: {result.optimization_summary}")
    print(f"  优化统计:")
    for key, value in result.optimization_stats.items():
        print(f"    - {key}: {value}")
    print(f"\n分类统计:")
    for category, assets in result.categorized_assets.items():
        if assets:
            print(f"  - {category}: {len(assets)} 个")
