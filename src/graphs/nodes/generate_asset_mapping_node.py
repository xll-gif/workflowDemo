"""
资源映射表生成节点

为各平台生成静态资源映射文件，用于代码生成时引用
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
    GenerateAssetMappingInput,
    GenerateAssetMappingOutput
)


def generate_asset_mapping_node(
    state: GenerateAssetMappingInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GenerateAssetMappingOutput:
    """
    title: 资源映射表生成
    desc: 为各平台生成静态资源映射文件，便于代码生成时引用
    integrations: -
    """
    ctx = runtime.context

    logger.info(f"开始生成资源映射表")
    logger.info(f"  已上传资源数量: {len(state.uploaded_assets)}")
    logger.info(f"  目标平台: {', '.join(state.platforms)}")

    asset_mapping_files = {}
    asset_mapping_json = {
        "version": "1.0",
        "total_assets": len(state.uploaded_assets),
        "platforms": {}
    }

    # 为每个平台生成映射文件
    for platform in state.platforms:
        logger.info(f"\n生成 {platform.upper()} 平台映射文件...")
        mapping_data = _generate_platform_mapping(
            platform,
            state.uploaded_assets,
            state.categorized_assets
        )
        asset_mapping_files[platform] = mapping_data
        asset_mapping_json["platforms"][platform] = mapping_data
        logger.info(f"  ✅ 生成成功: {mapping_data['file_count']} 个文件")

    # 生成完整摘要
    total_files = sum(m["file_count"] for m in asset_mapping_files.values())
    summary = f"为 {len(state.platforms)} 个平台生成资源映射表，共 {total_files} 个文件"

    logger.info(f"\n✅ {summary}")

    return GenerateAssetMappingOutput(
        asset_mapping_files=asset_mapping_files,
        asset_mapping_json=asset_mapping_json,
        mapping_summary=summary
    )


def _generate_platform_mapping(
    platform: str,
    uploaded_assets: List[Dict[str, Any]],
    categorized_assets: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """
    为指定平台生成映射数据

    Args:
        platform: 平台名称
        uploaded_assets: 已上传的资源列表
        categorized_assets: 分类后的资源

    Returns:
        映射数据
    """
    files = {}
    import_statements = {}

    if platform == "h5":
        # H5 平台映射（React + TypeScript）
        files = _generate_h5_mapping(uploaded_assets, categorized_assets)
        import_statements = _generate_h5_imports(uploaded_assets, categorized_assets)

    elif platform == "ios":
        # iOS 平台映射（SwiftUI）
        files = _generate_ios_mapping(uploaded_assets, categorized_assets)
        import_statements = _generate_ios_imports(uploaded_assets, categorized_assets)

    elif platform == "android":
        # Android 平台映射（Jetpack Compose）
        files = _generate_android_mapping(uploaded_assets, categorized_assets)
        import_statements = _generate_android_imports(uploaded_assets, categorized_assets)

    elif platform == "harmonyos":
        # 鸿蒙平台映射（ArkTS）
        files = _generate_harmonyos_mapping(uploaded_assets, categorized_assets)
        import_statements = _generate_harmonyos_imports(uploaded_assets, categorized_assets)

    elif platform == "miniprogram":
        # 小程序平台映射
        files = _generate_miniprogram_mapping(uploaded_assets, categorized_assets)
        import_statements = _generate_miniprogram_imports(uploaded_assets, categorized_assets)

    return {
        "platform": platform,
        "file_count": len(files),
        "files": files,
        "import_statements": import_statements,
        "asset_count": len(uploaded_assets)
    }


def _generate_h5_mapping(
    uploaded_assets: List[Dict[str, Any]],
    categorized_assets: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """生成 H5 平台映射文件"""
    files = {}

    # 生成资源索引文件
    resource_index = {
        "images": {},
        "icons": {},
        "backgrounds": {}
    }

    for asset in uploaded_assets:
        name = asset["name"]
        url = asset["oss_url"]
        category = asset.get("category", "unknown")

        if category == "icon":
            resource_index["icons"][name] = url
        elif category == "background":
            resource_index["backgrounds"][name] = url
        else:
            resource_index["images"][name] = url

    # 生成 TypeScript 类型定义
    ts_content = _generate_h5_types(resource_index)

    # 生成资源常量文件
    constants_content = _generate_h5_constants(resource_index)

    files["src/assets/resources.ts"] = {
        "path": "src/assets/resources.ts",
        "content": ts_content,
        "type": "typescript"
    }

    files["src/assets/resource-constants.ts"] = {
        "path": "src/assets/resource-constants.ts",
        "content": constants_content,
        "type": "typescript"
    }

    return files


def _generate_h5_imports(
    uploaded_assets: List[Dict[str, Any]],
    categorized_assets: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, str]:
    """生成 H5 导入语句"""
    imports = {}

    for asset in uploaded_assets:
        name = asset["name"]
        safe_name = name.replace("-", "_").replace(" ", "_")
        imports[f"{safe_name}_url"] = f"import {safe_name}Url from '@/assets/images/{name}.png';"

    return imports


def _generate_h5_types(resource_index: Dict[str, Any]) -> str:
    """生成 H5 TypeScript 类型定义"""
    return f"""/**
 * 静态资源类型定义
 * 自动生成，请勿手动修改
 */

export interface ResourceIndex {{
  images: Record<string, string>;
  icons: Record<string, string>;
  backgrounds: Record<string, string>;
}}

export const resourceIndex: ResourceIndex = {json.dumps(resource_index, indent=2)};

export type ImageKey = keyof typeof resourceIndex.images;
export type IconKey = keyof typeof resourceIndex.icons;
export type BackgroundKey = keyof typeof resourceIndex.backgrounds;
"""


def _generate_h5_constants(resource_index: Dict[str, Any]) -> str:
    """生成 H5 资源常量文件"""
    constants = []

    # 图标常量
    for name, url in resource_index["icons"].items():
        safe_name = name.replace("-", "_").replace(" ", "_")
        constants.append(f"export const {safe_name}_ICON = '{url}';")

    # 背景图常量
    for name, url in resource_index["backgrounds"].items():
        safe_name = name.replace("-", "_").replace(" ", "_")
        constants.append(f"export const {safe_name}_BG = '{url}';")

    # 图片常量
    for name, url in resource_index["images"].items():
        safe_name = name.replace("-", "_").replace(" ", "_")
        constants.append(f"export const {safe_name}_IMG = '{url}';")

    return f"""/**
 * 静态资源常量
 * 自动生成，请勿手动修改
 */

{chr(10).join(constants)}
"""


def _generate_ios_mapping(
    uploaded_assets: List[Dict[str, Any]],
    categorized_assets: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """生成 iOS 平台映射文件"""
    files = {}

    # 生成 Assets.xcassets 结构
    assets_catalog = {
        "images": [],
        "colors": []
    }

    for asset in uploaded_assets:
        name = asset["name"]
        safe_name = name.replace("-", "_").replace(" ", "_")
        assets_catalog["images"].append({
            "name": safe_name,
            "filename": f"{name}.imageset",
            "scales": asset.get("scales", [1])
        })

    # 生成资源管理器代码
    resource_manager_content = _generate_ios_resource_manager(assets_catalog)

    files["Assets.xcassets/Contents.json"] = {
        "path": "Assets.xcassets/Contents.json",
        "content": json.dumps({"info": {"version": 1, "author": "xcode"}}, indent=2),
        "type": "json"
    }

    files["Utils/ResourceManager.swift"] = {
        "path": "Utils/ResourceManager.swift",
        "content": resource_manager_content,
        "type": "swift"
    }

    return files


def _generate_ios_imports(
    uploaded_assets: List[Dict[str, Any]],
    categorized_assets: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, str]:
    """生成 iOS 导入语句"""
    imports = {}

    for asset in uploaded_assets:
        name = asset["name"]
        safe_name = name.replace("-", "_").replace(" ", "_")
        imports[f"{safe_name}_image"] = f"UIImage(named: \"{safe_name}\")"

    return imports


def _generate_ios_resource_manager(assets_catalog: Dict[str, Any]) -> str:
    """生成 iOS 资源管理器代码"""
    images = assets_catalog["images"]
    image_properties = []

    for img in images:
        name = img["name"]
        image_properties.append(f"    static let {name} = UIImage(named: \"{name}\")")

    return f"""//
//  ResourceManager.swift
//  自动生成的资源管理器
//

import UIKit

class ResourceManager {{
{chr(10).join(image_properties)}

    static let allImages: [String: UIImage?] = [
{chr(10).join([f"        \"{img['name']}\": {img['name']}," for img in images])}
    ]
}}
"""


def _generate_android_mapping(
    uploaded_assets: List[Dict[str, Any]],
    categorized_assets: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """生成 Android 平台映射文件"""
    files = {}

    # 生成资源索引 XML
    resources_xml = _generate_android_resources_xml(uploaded_assets)

    files["app/src/main/res/values/resources.xml"] = {
        "path": "app/src/main/res/values/resources.xml",
        "content": resources_xml,
        "type": "xml"
    }

    # 生成资源管理器代码
    resource_manager_content = _generate_android_resource_manager(uploaded_assets)

    files["app/src/main/java/com/example/app/utils/ResourceManager.kt"] = {
        "path": "app/src/main/java/com/example/app/utils/ResourceManager.kt",
        "content": resource_manager_content,
        "type": "kotlin"
    }

    return files


def _generate_android_imports(
    uploaded_assets: List[Dict[str, Any]],
    categorized_assets: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, str]:
    """生成 Android 导入语句"""
    imports = {}

    for asset in uploaded_assets:
        name = asset["name"]
        safe_name = name.replace("-", "_").replace(" ", "_")
        imports[f"{safe_name}_drawable"] = f"R.drawable.{safe_name}"

    return imports


def _generate_android_resources_xml(uploaded_assets: List[Dict[str, Any]]) -> str:
    """生成 Android resources.xml"""
    xml_lines = ["<resources>"]

    for asset in uploaded_assets:
        name = asset["name"]
        safe_name = name.replace("-", "_").replace(" ", "_")
        xml_lines.append(f'    <string name="img_{safe_name}">{asset["oss_url"]}</string>')

    xml_lines.append("</resources>")

    return "\n".join(xml_lines)


def _generate_android_resource_manager(uploaded_assets: List[Dict[str, Any]]) -> str:
    """生成 Android 资源管理器代码"""
    properties = []

    for asset in uploaded_assets:
        name = asset["name"]
        safe_name = name.replace("-", "_").replace(" ", "_")
        properties.append(f'    val {safe_name} = R.drawable.{safe_name}')

    return f"""package com.example.app.utils

import android.content.Context
import android.graphics.drawable.Drawable
import com.example.app.R

/**
 * 自动生成的资源管理器
 */
object ResourceManager {{
{chr(10).join(properties)}

    fun allResources(context: Context): Map<String, Drawable> {{
        return mapOf(
{chr(10).join([f'            "{asset["name"]}" to context.getDrawable({asset["name"].replace("-", "_").replace(" ", "_")})!!' for asset in uploaded_assets])}
        )
    }}
}}
"""


def _generate_harmonyos_mapping(
    uploaded_assets: List[Dict[str, Any]],
    categorized_assets: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """生成鸿蒙平台映射文件"""
    files = {}

    # 生成资源常量文件
    resource_constants_content = _generate_harmonyos_resource_constants(uploaded_assets)

    files["ets/common/resource/ResourceConstants.ets"] = {
        "path": "ets/common/resource/ResourceConstants.ets",
        "content": resource_constants_content,
        "type": "ets"
    }

    return files


def _generate_harmonyos_imports(
    uploaded_assets: List[Dict[str, Any]],
    categorized_assets: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, str]:
    """生成鸿蒙导入语句"""
    imports = {}

    for asset in uploaded_assets:
        name = asset["name"]
        safe_name = name.replace("-", "_").replace(" ", "_")
        imports[f"{safe_name}_resource"] = f"$r('app.media.{safe_name}')"

    return imports


def _generate_harmonyos_resource_constants(uploaded_assets: List[Dict[str, Any]]) -> str:
    """生成鸿蒙资源常量文件"""
    constants = []

    for asset in uploaded_assets:
        name = asset["name"]
        safe_name = name.replace("-", "_").replace(" ", "_")
        constants.append(f"  static readonly {safe_name}: Resource = $r('app.media.{safe_name}');")

    return f"""/**
 * 自动生成的资源常量
 */

export class ResourceConstants {{
{chr(10).join(constants)}

  static getAllResources(): Map<string, Resource> {{
    return new Map([
{chr(10).join([f'      ["{asset["name"]}", this.{asset["name"].replace("-", "_").replace(" ", "_")}],' for asset in uploaded_assets])}
    ]);
  }}
}}
"""


def _generate_miniprogram_mapping(
    uploaded_assets: List[Dict[str, Any]],
    categorized_assets: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """生成小程序平台映射文件"""
    files = {}

    # 生成资源常量文件
    resource_constants_content = _generate_miniprogram_resource_constants(uploaded_assets)

    files["utils/resource-constants.js"] = {
        "path": "utils/resource-constants.js",
        "content": resource_constants_content,
        "type": "javascript"
    }

    return files


def _generate_miniprogram_imports(
    uploaded_assets: List[Dict[str, Any]],
    categorized_assets: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, str]:
    """生成小程序导入语句"""
    imports = {}

    for asset in uploaded_assets:
        name = asset["name"]
        imports[f"{name}_path"] = f"/assets/images/{name}.png"

    return imports


def _generate_miniprogram_resource_constants(uploaded_assets: List[Dict[str, Any]]) -> str:
    """生成小程序资源常量文件"""
    constants = []

    for asset in uploaded_assets:
        name = asset["name"]
        constants.append(f'  {name}: "/assets/images/{name}.png",')

    return f"""/**
 * 自动生成的资源常量
 */

module.exports = {{
{chr(10).join(constants)}
}};
"""


# 测试代码
if __name__ == "__main__":
    print("测试资源映射表生成节点")
    print("=" * 80)

    # 创建测试输入
    test_input = GenerateAssetMappingInput(
        uploaded_assets=[
            {"id": "1", "name": "user_icon", "type": "ICON", "url": "https://example.com/icon.png", "oss_url": "https://oss.example.com/assets/user_icon.png", "category": "icon", "scales": [1, 2, 3]},
            {"id": "2", "name": "page_bg", "type": "BACKGROUND", "url": "https://example.com/bg.jpg", "oss_url": "https://oss.example.com/assets/page_bg.webp", "category": "background"},
            {"id": "3", "name": "brand_logo", "type": "LOGO", "url": "https://example.com/logo.png", "oss_url": "https://oss.example.com/assets/brand_logo.svg", "category": "logo"},
        ],
        categorized_assets={
            "icons": [],
            "backgrounds": [],
            "illustrations": [],
            "logos": [],
            "avatars": [],
            "others": []
        },
        platforms=["h5", "ios", "android", "harmonyos", "miniprogram"]
    )

    # 创建模拟的 Runtime 和 Context
    from unittest.mock import MagicMock

    mock_config = {}
    mock_runtime = MagicMock()
    mock_context = MagicMock()
    mock_runtime.context = mock_context

    # 运行节点
    result = generate_asset_mapping_node(test_input, mock_config, mock_runtime)

    print("\n结果:")
    print(f"  映射表生成摘要: {result.mapping_summary}")
    print(f"\n各平台文件数:")
    for platform, mapping in result.asset_mapping_files.items():
        print(f"  - {platform}: {mapping['file_count']} 个文件")
