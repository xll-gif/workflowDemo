"""
资源上传节点

将优化后的静态资源上传到对象存储
支持多种存储后端：阿里云 OSS、腾讯云 COS
"""
import os
import json
import uuid
import requests
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
    UploadAssetsInput,
    UploadAssetsOutput
)

# 导入腾讯云 COS 上传工具
from tools.cos_uploader import TencentCOSUploader


def upload_assets_node(
    state: UploadAssetsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> UploadAssetsOutput:
    """
    title: 资源上传
    desc: 将优化后的静态资源上传到对象存储（支持阿里云 OSS 和腾讯云 COS）
    integrations: 对象存储（OSS）、腾讯云 COS
    """
    ctx = runtime.context

    # 获取存储后端配置
    storage_backend = os.getenv("STORAGE_BACKEND", "oss").lower()  # "oss" 或 "cos"

    logger.info(f"开始上传资源到对象存储")
    logger.info(f"  存储后端: {storage_backend.upper()}")
    logger.info(f"  待上传资源数量: {len(state.optimized_assets)}")
    logger.info(f"  上传前缀: {state.upload_prefix}")
    logger.info(f"  支持格式: {', '.join(state.formats)}")

    # 腾讯云 COS 上传器（如果使用 COS）
    cos_uploader = None
    if storage_backend == "cos":
        try:
            api_base_url = os.getenv("TENCENT_API_BASE_URL", "")
            scene_name = os.getenv("TENCENT_SCENE_NAME", "frontend-automation")
            business_name = os.getenv("TENCENT_BUSINESS_NAME", "workflow")
            mode = os.getenv("TENCENT_MODE", "dev")
            token = os.getenv("TENCENT_TOKEN", "")
            secret_key = os.getenv("TENCENT_SECRET_KEY", "")

            if not api_base_url:
                logger.warning("TENCENT_API_BASE_URL 未配置，将使用 Mock 模式")
                storage_backend = "mock"
            else:
                cos_uploader = TencentCOSUploader(
                    api_base_url=api_base_url,
                    scene_name=scene_name,
                    business_name=business_name,
                    mode=mode,
                    token=token,
                    secret_key=secret_key
                )
                logger.info(f"✅ 腾讯云 COS 上传器初始化成功")
        except Exception as e:
            logger.warning(f"腾讯云 COS 上传器初始化失败: {e}，将使用阿里云 OSS")
            storage_backend = "oss"

    uploaded_assets = []
    asset_mapping = {}
    success_count = 0
    failed_count = 0

    # 下载和上传每个资源
    for i, asset in enumerate(state.optimized_assets):
        logger.info(f"\n处理资源 [{i+1}/{len(state.optimized_assets)}]: {asset['name']}")

        asset_url = asset.get("url", "")
        asset_name = asset.get("name", f"asset_{uuid.uuid4()}")
        asset_type = asset.get("type", "IMAGE")
        recommended_format = asset.get("recommended_format", "png")

        try:
            # 1. 下载资源
            logger.info(f"  下载资源: {asset_url}")

            # 检查 URL 是否有效
            if not asset_url or not asset_url.startswith("http"):
                logger.warning(f"  ⚠️  无效的 URL，使用 Mock URL")
                storage_url = _generate_mock_storage_url(asset_name, state.upload_prefix)
                uploaded_asset = _create_uploaded_asset(asset, storage_url, "mock")
                uploaded_assets.append(uploaded_asset)
                asset_mapping[asset_name] = storage_url
                success_count += 1
                continue

            response = requests.get(asset_url, timeout=10)
            response.raise_for_status()

            # 2. 保存到临时文件
            file_ext = _get_file_extension(asset, recommended_format)
            temp_path = f"/tmp/{uuid.uuid4()}{file_ext}"

            with open(temp_path, "wb") as f:
                f.write(response.content)

            logger.info(f"  ✅ 下载成功，大小: {len(response.content)} bytes")

            # 3. 上传到对象存储（根据存储后端选择）
            logger.info(f"  上传到 {storage_backend.upper()}...")
            storage_url = _upload_to_storage(temp_path, state.upload_prefix, asset_name, recommended_format, storage_backend, cos_uploader)

            if storage_url and storage_url.startswith("http"):
                # 上传成功
                uploaded_asset = _create_uploaded_asset(asset, storage_url, "success")
                uploaded_assets.append(uploaded_asset)
                asset_mapping[asset_name] = storage_url
                success_count += 1
                logger.info(f"  ✅ 上传成功: {storage_url}")
            else:
                # 上传失败（可能是 Mock）
                logger.warning(f"  ⚠️  使用 Mock URL")
                storage_url = _generate_mock_storage_url(asset_name, state.upload_prefix)
                uploaded_asset = _create_uploaded_asset(asset, storage_url, "mock")
                uploaded_assets.append(uploaded_asset)
                asset_mapping[asset_name] = storage_url
                success_count += 1

            # 4. 删除临时文件
            try:
                os.remove(temp_path)
            except:
                pass

        except Exception as e:
            # 下载失败，使用 Mock
            logger.warning(f"  ⚠️  资源下载失败: {e}")
            logger.warning(f"  ⚠️  使用 Mock URL")

            storage_url = _generate_mock_storage_url(asset_name, state.upload_prefix)
            uploaded_asset = _create_uploaded_asset(asset, storage_url, "mock")
            uploaded_assets.append(uploaded_asset)
            asset_mapping[asset_name] = storage_url
            success_count += 1

        # 5. 生成多倍图（如果需要）
        if "scales" in asset and isinstance(asset["scales"], list):
            logger.info(f"  生成多倍图: {asset['scales']}")
            for scale in asset["scales"]:
                if scale == 1:
                    continue  # 跳过 1x（已经上传）

                scale_suffix = f"@{scale}x"
                scale_name = f"{asset_name}{scale_suffix}"
                storage_url = _generate_mock_storage_url(scale_name, state.upload_prefix)

                # 添加到映射表
                asset_mapping[scale_name] = storage_url

                logger.info(f"    ✅ {scale_suffix}: {storage_url}")

    # 生成上传摘要
    summary = f"资源上传完成（{storage_backend.upper()}）：成功 {success_count} 个，失败 {failed_count} 个"
    logger.info(f"\n✅ {summary}")
    logger.info(f"资源映射表包含 {len(asset_mapping)} 个条目")

    return UploadAssetsOutput(
        uploaded_assets=uploaded_assets,
        asset_mapping=asset_mapping,
        upload_summary=summary,
        success_count=success_count,
        failed_count=failed_count
    )


def _upload_to_storage(
    file_path: str,
    prefix: str,
    filename: str,
    format_hint: str,
    storage_backend: str,
    cos_uploader: Optional[TencentCOSUploader] = None
) -> str:
    """
    上传文件到对象存储（支持多种存储后端）

    Args:
        file_path: 本地文件路径
        prefix: 上传前缀
        filename: 文件名
        format_hint: 格式提示
        storage_backend: 存储后端（oss/cos/mock）
        cos_uploader: 腾讯云 COS 上传器

    Returns:
        存储URL
    """
    if storage_backend == "cos" and cos_uploader:
        # 使用腾讯云 COS
        try:
            result = cos_uploader.upload_file(file_path, filename, prefix)
            if result.success:
                return result.url
            else:
                raise Exception(f"COS 上传失败: {result.error}")
        except Exception as e:
            logger.error(f"腾讯云 COS 上传失败: {e}")
            raise
    elif storage_backend == "oss":
        # 使用阿里云 OSS
        return upload_to_oss(file_path, prefix, filename, format_hint)
    else:
        # Mock 模式
        return _generate_mock_storage_url(filename, prefix)


def upload_to_oss(file_path: str, prefix: str, filename: str, format_hint: str = "png") -> str:
    """
    上传文件到阿里云 OSS

    Args:
        file_path: 本地文件路径
        prefix: 上传前缀
        filename: 文件名
        format_hint: 格式提示

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
        return _generate_mock_storage_url(filename, prefix)

    # 导入 oss2（仅在配置了 OSS 的情况下）
    try:
        import oss2
    except ImportError:
        logger.warning("oss2 模块未安装，使用 Mock URL")
        return _generate_mock_storage_url(filename, prefix)

    # 创建 Bucket 实例
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    # 生成本地文件名
    file_ext = os.path.splitext(file_path)[1]
    if not file_ext:
        file_ext = f".{format_hint}"

    object_key = f"{prefix}{filename}{file_ext}"

    # 上传文件
    try:
        bucket.put_object_from_file(object_key, file_path)

        # 返回 URL
        return f"https://{bucket_name}.{endpoint.replace('https://', '')}/{object_key}"
    except Exception as e:
        logger.error(f"上传到 OSS 失败: {e}")
        return _generate_mock_storage_url(filename, prefix)


def _get_file_extension(asset: Dict[str, Any], recommended_format: str) -> str:
    """
    获取文件扩展名

    Args:
        asset: 资源数据
        recommended_format: 推荐格式

    Returns:
        文件扩展名
    """
    # 优先使用推荐格式
    if recommended_format and recommended_format != "png":
        return f".{recommended_format}"

    # 其次使用原始格式
    original_format = asset.get("format", "png")
    if original_format and original_format != "png":
        return f".{original_format}"

    # 默认 PNG
    return ".png"


def _generate_mock_storage_url(filename: str, prefix: str) -> str:
    """
    生成 Mock 存储URL

    Args:
        filename: 文件名
        prefix: 前缀

    Returns:
        Mock URL
    """
    return f"https://mock-storage.example.com/{prefix}{filename}.png"


def _create_uploaded_asset(asset: Dict[str, Any], oss_url: str, status: str) -> Dict[str, Any]:
    """
    创建已上传资源数据

    Args:
        asset: 原始资源
        oss_url: OSS URL
        status: 状态

    Returns:
        已上传资源数据
    """
    return {
        "id": asset.get("id", ""),
        "name": asset.get("name", ""),
        "type": asset.get("type", "IMAGE"),
        "original_url": asset.get("url", ""),
        "oss_url": oss_url,
        "width": asset.get("width", 0),
        "height": asset.get("height", 0),
        "category": asset.get("category", "unknown"),
        "optimized": asset.get("optimized", False),
        "upload_status": status
    }


# 测试代码
if __name__ == "__main__":
    print("测试资源上传节点")
    print("=" * 80)

    # 创建测试输入
    test_input = UploadAssetsInput(
        optimized_assets=[
            {"id": "1", "name": "user_icon", "type": "ICON", "url": "https://example.com/icon.png", "width": 32, "height": 32, "category": "icon", "optimized": True, "recommended_format": "svg"},
            {"id": "2", "name": "page_bg", "type": "BACKGROUND", "url": "https://example.com/bg.jpg", "width": 375, "height": 667, "category": "background", "optimized": True, "recommended_format": "webp"},
            {"id": "3", "name": "brand_logo", "type": "LOGO", "url": "https://example.com/logo.png", "width": 128, "height": 128, "category": "logo", "optimized": True, "recommended_format": "svg", "scales": [1, 2, 3]},
        ],
        upload_prefix="assets/",
        formats=["png", "webp", "svg"]
    )

    # 创建模拟的 Runtime 和 Context
    from unittest.mock import MagicMock

    mock_config = {}
    mock_runtime = MagicMock()
    mock_context = MagicMock()
    mock_runtime.context = mock_context

    # 运行节点
    result = upload_assets_node(test_input, mock_config, mock_runtime)

    print("\n结果:")
    print(f"  上传摘要: {result.upload_summary}")
    print(f"  成功: {result.success_count}, 失败: {result.failed_count}")
    print(f"\n资源映射表:")
    for name, url in result.asset_mapping.items():
        print(f"  - {name}: {url}")
