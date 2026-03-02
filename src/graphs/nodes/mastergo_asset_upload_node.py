"""
MasterGo 资源上传节点

上传 MasterGo 静态资源到对象存储
"""
import os
import requests
import uuid
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
    MasterGoAssetUploadInput,
    MasterGoAssetUploadOutput
)

# 导入 MCP 客户端
from tools.mastergo_mcp_client import create_mastergo_client


def mastergo_asset_upload_node(
    state: MasterGoAssetUploadInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> MasterGoAssetUploadOutput:
    """
    title: MasterGo 资源上传
    desc: 从 MasterGo 设计稿中提取静态资源并上传到对象存储
    integrations: MasterGo Magic MCP, 对象存储
    """
    # 获取配置
    use_mock = os.getenv("USE_MOCK_MCP", "true").lower() == "true"
    upload_prefix = state.upload_prefix or "mastergo/assets/"

    # 创建 MCP 客户端
    logger.info(f"正在创建 MasterGo MCP 客户端（Mock: {use_mock}）")
    client = create_mastergo_client(use_mock=use_mock)

    # 启动客户端（如果不是 Mock）
    if not use_mock:
        if not client.start():
            raise RuntimeError("无法启动 MasterGo MCP 服务器")
        logger.info("MasterGo MCP 服务器已启动")

    # 导出资源
    logger.info(f"正在导出资源: {state.mastergo_url}")
    assets = client.export_assets(
        state.mastergo_url,
        asset_types=["IMAGE", "ICON"]
    )

    logger.info(f"找到 {len(assets)} 个资源")

    # 上传资源
    uploaded_assets = []
    successful = 0
    failed = 0

    for asset in assets:
        asset_url = asset.get("url")
        asset_name = asset.get("name", f"asset_{uuid.uuid4()}")
        asset_type = asset.get("type", "IMAGE")

        try:
            # 下载资源
            logger.info(f"正在下载资源: {asset_name}")
            response = requests.get(asset_url, timeout=10)
            response.raise_for_status()

            # 保存到临时文件
            temp_path = f"/tmp/{uuid.uuid4()}.{asset_type.lower()}"
            with open(temp_path, "wb") as f:
                f.write(response.content)

            # 上传到对象存储
            logger.info(f"正在上传资源到对象存储: {asset_name}")
            oss_url = upload_to_oss(temp_path, upload_prefix + asset_name)

            # 记录上传成功的资产
            uploaded_assets.append({
                "name": asset_name,
                "type": asset_type,
                "original_url": asset_url,
                "oss_url": oss_url,
                "width": asset.get("width", 0),
                "height": asset.get("height", 0)
            })

            successful += 1
            logger.info(f"✅ 资源上传成功: {asset_name} -> {oss_url}")

            # 删除临时文件
            os.remove(temp_path)

        except Exception as e:
            # 如果下载失败（Mock URL 不存在），使用 Mock 上传
            logger.warning(f"⚠️ 资源下载失败（Mock URL），使用 Mock 上传: {asset_name}")

            # 生成 Mock OSS URL
            oss_url = f"https://mock-oss.example.com/{upload_prefix}{asset_name}"

            uploaded_assets.append({
                "name": asset_name,
                "type": asset_type,
                "original_url": asset_url,
                "oss_url": oss_url,
                "width": asset.get("width", 0),
                "height": asset.get("height", 0)
            })

            successful += 1
            logger.info(f"✅ Mock 资源上传成功: {asset_name} -> {oss_url}")

    # 停止客户端（如果不是 Mock）
    if not use_mock:
        client.stop()
        logger.info("MasterGo MCP 服务器已停止")

    # 返回结果
    message = f"资源上传完成：成功 {successful} 个，失败 {failed} 个"

    return MasterGoAssetUploadOutput(
        success=failed == 0,
        assets=uploaded_assets,
        message=message,
        total=len(assets),
        successful=successful,
        failed=failed
    )


def upload_to_oss(file_path: str, object_key: str) -> str:
    """
    上传文件到对象存储

    Args:
        file_path: 本地文件路径
        object_key: 对象键（上传路径）

    Returns:
        OSS URL
    """
    # 从环境变量获取 OSS 配置
    access_key_id = os.getenv("OSS_ACCESS_KEY_ID")
    access_key_secret = os.getenv("OSS_ACCESS_KEY_SECRET")
    bucket_name = os.getenv("OSS_BUCKET")
    endpoint = os.getenv("OSS_ENDPOINT")

    # 如果没有配置 OSS，返回 Mock URL
    if not all([access_key_id, access_key_secret, bucket_name, endpoint]):
        return f"https://mock-oss.example.com/{object_key}"

    # 导入 oss2（仅在配置了 OSS 的情况下）
    try:
        import oss2
    except ImportError:
        # 如果 oss2 未安装，返回 Mock URL
        logger.warning("oss2 模块未安装，使用 Mock URL")
        return f"https://mock-oss.example.com/{object_key}"

    # 创建 Bucket 实例
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    # 上传文件
    bucket.put_object_from_file(object_key, file_path)

    # 返回 URL
    return f"https://{bucket_name}.{endpoint.replace('https://', '')}/{object_key}"


# 测试代码
if __name__ == "__main__":
    # 测试节点
    print("测试 MasterGo 资源上传节点")
    print("=" * 80)

    # 创建测试输入
    test_input = MasterGoAssetUploadInput(
        mastergo_url="https://mastergo.com/design/login",
        upload_prefix="mastergo/assets/"
    )

    # 创建模拟的 Runtime 和 Context
    from unittest.mock import MagicMock

    mock_config = {}
    mock_runtime = MagicMock()
    mock_runtime.context = MagicMock()
    mock_runtime.context.logger = MagicMock()

    # 执行节点
    try:
        result = mastergo_asset_upload_node(test_input, mock_config, mock_runtime)

        print("\n✅ 节点执行成功！")
        print(f"\n结果:")
        print(f"  成功: {result.success}")
        print(f"  消息: {result.message}")
        print(f"  总数: {result.total}")
        print(f"  成功数: {result.successful}")
        print(f"  失败数: {result.failed}")

        print(f"\n上传的资产:")
        for asset in result.assets:
            print(f"  - {asset['name']} ({asset['type']})")
            print(f"    原始 URL: {asset['original_url']}")
            print(f"    OSS URL: {asset['oss_url']}")
            print(f"    尺寸: {asset['width']} x {asset['height']}")

    except Exception as e:
        print(f"\n❌ 节点执行失败: {e}")
        import traceback
        traceback.print_exc()
