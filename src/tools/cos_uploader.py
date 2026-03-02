"""
腾讯云 COS 上传工具

使用腾讯云 COS SDK 进行文件上传，支持 STS 临时凭证
"""
import os
import logging
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class STSCredentials:
    """STS 临时凭证"""
    tmp_secret_id: str
    tmp_secret_key: str
    session_token: str
    expired_time: int  # 过期时间（秒）
    bucket: str
    region: str
    cusdomain: Optional[str] = None


@dataclass
class UploadResult:
    """上传结果"""
    filename: str
    temp_visit: str
    size: int
    url: str
    success: bool
    error: Optional[str] = None


class TencentCOSUploader:
    """腾讯云 COS 上传器"""

    def __init__(
        self,
        api_base_url: str,
        scene_name: str,
        business_name: str,
        mode: str = "dev",
        token: Optional[str] = None,
        secret_key: Optional[str] = None
    ):
        """
        初始化腾讯云 COS 上传器

        Args:
            api_base_url: API 基础 URL
            scene_name: 场景名称（如 imchat）
            business_name: 业务名称（如 sale）
            mode: 环境模式（dev/gray/prod）
            token: 认证 Token
            secret_key: X-Secret-Key（安全密钥）
        """
        self.api_base_url = api_base_url
        self.scene_name = scene_name
        self.business_name = business_name
        self.mode = mode
        self.token = token
        self.secret_key = secret_key

        # STS 凭证缓存
        self.sts_credentials: Optional[STSCredentials] = None
        self.credentials_expires_at: Optional[float] = None

        # COS 客户端
        self.cos_client = None

    def get_upload_token(self, media_type: str = "image") -> Dict[str, Any]:
        """
        获取上传凭证（STS 临时凭证）

        Args:
            media_type: 媒体类型（image/video/file）

        Returns:
            上传凭证数据
        """
        url = f"{self.api_base_url}/api/v1/upload-token"

        # 构建请求参数
        params = {
            "mediaType": media_type,
            "sceneName": self.scene_name,
            "businessName": self.business_name,
            "source": "web"
        }

        # 构建 Headers
        headers = {
            "Content-Type": "application/json"
        }

        # 添加 X-Secret-Key
        if self.secret_key:
            headers["X-Secret-Key"] = self.secret_key

        # 添加认证 Token
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            logger.info(f"正在获取上传凭证: {url}")
            response = requests.post(url, json=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get("code") != 0:
                raise Exception(f"获取上传凭证失败: {data.get('msg', 'Unknown error')}")

            logger.info(f"✅ 获取上传凭证成功: Bucket={data['data']['bucket']}, Region={data['data']['region']}")

            return data["data"]

        except Exception as e:
            logger.error(f"❌ 获取上传凭证失败: {e}")
            raise

    def initialize_cos_client(self, credentials: STSCredentials) -> None:
        """
        初始化腾讯云 COS 客户端

        Args:
            credentials: STS 临时凭证
        """
        try:
            # 检查是否安装了 cos-python-sdk-v5
            try:
                from cos_cos_python_sdk_v5 import CosS3Client, CosS3Config
            except ImportError:
                logger.warning("cos-python-sdk-v5 未安装，尝试使用 cos_python_sdk_v5")
                from cos_python_sdk_v5 import CosS3Client, CosS3Config

            # 创建配置
            config = CosS3Config(
                Region=credentials.region,
                Scheme='https'
            )

            # 使用临时凭证初始化客户端
            self.cos_client = CosS3Client(
                SecretId=credentials.tmp_secret_id,
                SecretKey=credentials.tmp_secret_key,
                Token=credentials.session_token,
                Region=credentials.region,
                Config=config
            )

            logger.info("✅ 腾讯云 COS 客户端初始化成功")

        except ImportError as e:
            logger.error(f"❌ 腾讯云 COS SDK 未安装: {e}")
            logger.error("请运行: pip install cos-python-sdk-v5")
            raise Exception("腾讯云 COS SDK 未安装")

    def get_credentials(self, media_type: str = "image") -> STSCredentials:
        """
        获取 STS 临时凭证（带缓存）

        Args:
            media_type: 媒体类型

        Returns:
            STS 临时凭证
        """
        import time

        # 检查凭证是否过期
        if self.sts_credentials and self.credentials_expires_at:
            if time.time() < self.credentials_expires_at:
                logger.debug("使用缓存的 STS 凭证")
                return self.sts_credentials

        # 获取新凭证
        logger.info("正在获取新的 STS 临时凭证...")
        token_data = self.get_upload_token(media_type)

        # 创建凭证对象
        credentials = STSCredentials(
            tmp_secret_id=token_data["tencent"]["tmpSecretId"],
            tmp_secret_key=token_data["tencent"]["tmpSecretKey"],
            session_token=token_data["tencent"]["sessionToken"],
            expired_time=token_data["expiredTime"],
            bucket=token_data["bucket"],
            region=token_data["region"],
            cusdomain=token_data.get("cusdomain")
        )

        # 缓存凭证（提前 5 分钟过期）
        import time
        self.credentials_expires_at = time.time() + credentials.expired_time - 300
        self.sts_credentials = credentials

        # 初始化 COS 客户端
        self.initialize_cos_client(credentials)

        return credentials

    def upload_file(
        self,
        file_path: str,
        filename: Optional[str] = None,
        prefix: str = "",
        on_progress: Optional[callable] = None
    ) -> UploadResult:
        """
        上传文件到腾讯云 COS

        Args:
            file_path: 本地文件路径
            filename: 文件名（可选，默认使用原文件名）
            prefix: 上传前缀
            on_progress: 上传进度回调

        Returns:
            上传结果
        """
        import os
        import time
        from typing import Dict, Any

        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")

            # 获取文件信息
            file_size = os.path.getsize(file_path)
            original_filename = os.path.basename(file_path)
            upload_filename = filename or original_filename

            # 获取 STS 凭证
            credentials = self.get_credentials()

            # 生成文件 Key
            file_key = f"{prefix}{upload_filename}".lstrip("/")

            logger.info(f"开始上传文件: {file_key} (大小: {file_size} bytes)")

            # 上传文件
            start_time = time.time()

            response = self.cos_client.put_object(
                Bucket=credentials.bucket,
                Body=open(file_path, 'rb'),
                Key=file_key,
                EnableMD5=True
            )

            upload_time = time.time() - start_time

            # 生成访问 URL
            if credentials.cusdomain:
                # 使用自定义加速域名
                url = f"{credentials.cusdomain}/{file_key}"
            else:
                # 使用 COS 默认域名
                url = f"https://{credentials.bucket}.cos.{credentials.region}.myqcloud.com/{file_key}"

            logger.info(f"✅ 文件上传成功: {url} (耗时: {upload_time:.2f}s)")

            # 返回结果
            return UploadResult(
                filename=file_key,
                temp_visit=url,
                size=file_size,
                url=url,
                success=True
            )

        except Exception as e:
            logger.error(f"❌ 文件上传失败: {e}")
            return UploadResult(
                filename="",
                temp_visit="",
                size=0,
                url="",
                success=False,
                error=str(e)
            )

    def report_upload_result(self, result: UploadResult) -> Dict[str, Any]:
        """
        上报上传结果给后端

        Args:
            result: 上传结果

        Returns:
            上报结果
        """
        url = f"{self.api_base_url}/api/v1/upload-result"

        # 构建请求参数
        params = {
            "filename": result.filename,
            "tempVisit": result.temp_visit,
            "size": result.size,
            "success": result.success
        }

        # 构建 Headers
        headers = {
            "Content-Type": "application/json"
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        if self.secret_key:
            headers["X-Secret-Key"] = self.secret_key

        try:
            logger.info(f"正在上报上传结果: {result.filename}")
            response = requests.post(url, json=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get("code") != 0:
                logger.warning(f"上报上传结果失败: {data.get('msg', 'Unknown error')}")
            else:
                logger.info("✅ 上报上传结果成功")

            return data

        except Exception as e:
            logger.error(f"❌ 上报上传结果失败: {e}")
            # 上报失败不影响主流程
            return {"code": -1, "msg": str(e)}

    def upload_and_report(
        self,
        file_path: str,
        filename: Optional[str] = None,
        prefix: str = "assets/",
        on_progress: Optional[callable] = None
    ) -> UploadResult:
        """
        上传文件并上报结果

        Args:
            file_path: 本地文件路径
            filename: 文件名
            prefix: 上传前缀
            on_progress: 上传进度回调

        Returns:
            上传结果
        """
        # 上传文件
        result = self.upload_file(file_path, filename, prefix, on_progress)

        # 上报结果
        if result.success:
            self.report_upload_result(result)

        return result


# 测试代码
if __name__ == "__main__":
    print("测试腾讯云 COS 上传工具")
    print("=" * 80)

    # 创建上传器（需要配置真实的 API 地址和参数）
    try:
        uploader = TencentCOSUploader(
            api_base_url="https://api.example.com",
            scene_name="test",
            business_name="workflow",
            mode="dev"
        )

        # 测试上传
        test_file = "/tmp/test.png"
        if os.path.exists(test_file):
            result = uploader.upload_file(test_file, prefix="test/")
            print(f"上传结果: {result}")
        else:
            print(f"测试文件不存在: {test_file}")

    except Exception as e:
        print(f"测试失败: {e}")
