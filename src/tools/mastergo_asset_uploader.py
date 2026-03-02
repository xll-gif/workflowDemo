#!/usr/bin/env python3
"""
MasterGo 静态资源上传工具

功能：
1. 从 MasterGo 设计稿中提取图片/图标
2. 下载到本地临时目录
3. 上传到对象存储（CDN）
4. 生成签名 URL
5. 返回 CDN URL 列表
"""

import os
import sys
import json
import requests
import tempfile
from typing import List, Dict, Optional
from dataclasses import dataclass

from tools.mastergo_api import MasterGoAPI


@dataclass
class MasterGoAsset:
    """MasterGo 资产"""
    node_id: str
    node_name: str
    node_type: str
    image_url: str
    local_path: str
    cdn_url: str = ""


@dataclass
class AssetUploadResult:
    """资产上传结果"""
    total_count: int
    success_count: int
    failed_count: int
    assets: List[MasterGoAsset]
    errors: List[str]


class MasterGoAssetUploader:
    """MasterGo 资产上传器"""

    def __init__(self, mastergo_api: Optional[MasterGoAPI] = None):
        """
        初始化上传器

        Args:
            mastergo_api: MasterGo API 客户端
        """
        self.mastergo_api = mastergo_api or MasterGoAPI()
        self.temp_dir = tempfile.mkdtemp(prefix="mastergo_assets_")

        # 导入对象存储
        try:
            from coze_coding_dev_sdk.s3 import S3SyncStorage
            self.storage = S3SyncStorage(
                endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
                access_key="",
                secret_key="",
                bucket_name=os.getenv("COZE_BUCKET_NAME"),
                region="cn-beijing",
            )
            self.storage_enabled = True
        except Exception as e:
            print(f"⚠️  对象存储初始化失败: {e}")
            self.storage_enabled = False

    def extract_assets_from_design(self, file_id: str, node_id: Optional[str] = None) -> List[MasterGoAsset]:
        """
        从设计稿中提取所有图片资产

        Args:
            file_id: MasterGo 文件 ID
            node_id: 节点 ID（可选，默认提取整个文件）

        Returns:
            资产列表
        """
        print(f"\n📋 步骤 1: 从设计稿中提取资产")
        print(f"   File ID: {file_id}")
        print(f"   Node ID: {node_id or '提取整个文件'}")

        assets = []

        try:
            # 获取所有图片资源
            images = self.mastergo_api.get_all_images(file_id)

            for img in images:
                asset = MasterGoAsset(
                    node_id=img["id"],
                    node_name=img["name"],
                    node_type="IMAGE",
                    image_url=img["url"],
                    local_path=""
                )
                assets.append(asset)
                print(f"   ✅ 发现图片: {img['name']}")

            print(f"\n   📊 提取完成，共 {len(assets)} 个资产")

        except Exception as e:
            print(f"   ❌ 提取资产失败: {e}")

        return assets

    def download_assets(self, assets: List[MasterGoAsset]) -> List[MasterGoAsset]:
        """
        下载资产到本地临时目录

        Args:
            assets: 资产列表

        Returns:
            更新后的资产列表（包含本地路径）
        """
        print(f"\n📋 步骤 2: 下载资产到本地")

        for i, asset in enumerate(assets, 1):
            try:
                # 生成本地文件名
                file_ext = ".png"
                safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in asset.node_name)
                local_filename = f"{safe_name}_{asset.node_id.replace(':', '_')}{file_ext}"
                local_path = os.path.join(self.temp_dir, local_filename)

                # 下载图片
                response = requests.get(asset.image_url, timeout=30)
                response.raise_for_status()

                # 保存到本地
                with open(local_path, "wb") as f:
                    f.write(response.content)

                # 更新资产信息
                asset.local_path = local_path
                print(f"   ✅ [{i}/{len(assets)}] 下载: {asset.node_name}")

            except Exception as e:
                print(f"   ❌ [{i}/{len(assets)}] 下载失败 {asset.node_name}: {e}")

        downloaded_count = sum(1 for a in assets if a.local_path)
        print(f"\n   📊 下载完成: {downloaded_count}/{len(assets)}")

        return assets

    def upload_to_cdn(self, assets: List[MasterGoAsset], prefix: str = "mastergo/assets/") -> List[MasterGoAsset]:
        """
        上传资产到 CDN

        Args:
            assets: 资产列表
            prefix: 对象存储前缀

        Returns:
            更新后的资产列表（包含 CDN URL）
        """
        print(f"\n📋 步骤 3: 上传到 CDN")
        print(f"   存储前缀: {prefix}")

        if not self.storage_enabled:
            print(f"   ⚠️  对象存储未启用，跳过上传")
            return assets

        for i, asset in enumerate(assets, 1):
            if not asset.local_path:
                print(f"   ⚠️  [{i}/{len(assets)}] 跳过 {asset.node_name}（本地文件不存在）")
                continue

            try:
                # 读取本地文件
                with open(asset.local_path, "rb") as f:
                    file_content = f.read()

                # 生成本地文件名
                safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in asset.node_name)
                file_ext = ".png"
                filename = f"{safe_name}_{asset.node_id.replace(':', '_')}{file_ext}"

                # 上传到对象存储
                file_key = self.storage.upload_file(
                    file_content=file_content,
                    file_name=f"{prefix}{filename}",
                    content_type="image/png",
                )

                # 生成签名 URL
                asset.cdn_url = self.storage.generate_presigned_url(
                    key=file_key,
                    expire_time=86400 * 30  # 30 天有效期
                )

                print(f"   ✅ [{i}/{len(assets)}] 上传: {asset.node_name}")
                print(f"      Key: {file_key}")
                print(f"      URL: {asset.cdn_url[:80]}...")

            except Exception as e:
                print(f"   ❌ [{i}/{len(assets)}] 上传失败 {asset.node_name}: {e}")

        uploaded_count = sum(1 for a in assets if a.cdn_url)
        print(f"\n   📊 上传完成: {uploaded_count}/{len(assets)}")

        return assets

    def process_assets(self, file_id: str, node_id: Optional[str] = None, prefix: str = "mastergo/assets/") -> AssetUploadResult:
        """
        完整处理流程：提取、下载、上传

        Args:
            file_id: MasterGo 文件 ID
            node_id: 节点 ID（可选）
            prefix: 对象存储前缀

        Returns:
            AssetUploadResult 处理结果对象
        """
        print("="*80)
        print("🚀 开始处理 MasterGo 资产")
        print("="*80)

        try:
            # 1. 提取资产
            assets = self.extract_assets_from_design(file_id, node_id)

            if not assets:
                print("\n⚠️  未找到任何资产")
                return AssetUploadResult(
                    total_count=0,
                    success_count=0,
                    failed_count=0,
                    assets=[],
                    errors=["未找到任何资产"]
                )

            # 2. 下载资产
            assets = self.download_assets(assets)

            # 3. 上传到 CDN
            assets = self.upload_to_cdn(assets, prefix)

            # 4. 生成结果
            successful_assets = [a for a in assets if a.cdn_url]
            failed_assets = [a for a in assets if not a.cdn_url]

            return AssetUploadResult(
                total_count=len(assets),
                success_count=len(successful_assets),
                failed_count=len(failed_assets),
                assets=successful_assets,
                errors=[f"上传失败: {a.node_name}" for a in failed_assets]
            )

        except Exception as e:
            print(f"\n❌ 处理资产失败: {e}")
            import traceback
            traceback.print_exc()

            return AssetUploadResult(
                total_count=0,
                success_count=0,
                failed_count=0,
                assets=[],
                errors=[f"处理失败: {str(e)}"]
            )

    def cleanup(self):
        """清理临时文件"""
        import shutil
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"\n🧹 已清理临时目录: {self.temp_dir}")
        except Exception as e:
            print(f"\n⚠️  清理临时目录失败: {e}")


def main():
    """主函数"""
    import sys

    # 测试配置
    file_id = "7120216615013610"  # 替换为实际的 MasterGo 文件 ID
    node_id = None  # 可选

    print("MasterGo 资产上传工具")
    print("="*80)
    print(f"File ID: {file_id}")
    print(f"Node ID: {node_id}")
    print()

    # 创建上传器
    uploader = MasterGoAssetUploader()

    try:
        # 处理资产
        result = uploader.process_assets(
            file_id=file_id,
            node_id=node_id,
            prefix="mastergo/login/"
        )

        # 保存结果
        if result.success_count > 0:
            result_dict = {
                "success": result.success_count > 0,
                "total": result.total_count,
                "successful": result.success_count,
                "failed": result.failed_count,
                "assets": [
                    {
                        "node_id": a.node_id,
                        "node_name": a.node_name,
                        "cdn_url": a.cdn_url
                    }
                    for a in result.assets
                ]
            }
            with open("mastergo_assets_result.json", "w", encoding="utf-8") as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            print(f"\n💾 结果已保存到: mastergo_assets_result.json")

    finally:
        # 清理临时文件
        uploader.cleanup()


if __name__ == "__main__":
    main()
