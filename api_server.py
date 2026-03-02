"""
腾讯云 COS 上传后端 API 服务

提供获取 STS 临时凭证和上报上传结果的 API 接口
"""
import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)

# 配置
CONFIG = {
    "tencent": {
        "secret_id": os.getenv("TENCENT_SECRET_ID", ""),
        "secret_key": os.getenv("TENCENT_SECRET_KEY", ""),
        "region": os.getenv("TENCENT_REGION", "ap-shanghai"),
        "bucket": os.getenv("TENCENT_BUCKET", ""),
        "duration_seconds": int(os.getenv("TENCENT_DURATION_SECONDS", "900")),
        "allow_prefix": os.getenv("TENCENT_ALLOW_PREFIX", "frontend-automation/*")
    },
    "cusdomain": os.getenv("TENCENT_CUSDOMAIN", ""),  # 可选：自定义加速域名
    "secret_key": os.getenv("API_SECRET_KEY", ""),  # API 安全密钥
}


def verify_secret_key(headers):
    """验证 X-Secret-Key"""
    api_secret_key = CONFIG.get("secret_key", "")

    # 如果没有配置安全密钥，跳过验证
    if not api_secret_key:
        return True

    # 从 Headers 中获取 X-Secret-Key
    client_secret_key = headers.get("X-Secret-Key", "")

    # 如果客户端没有提供密钥，验证失败
    if not client_secret_key:
        return False

    # 验证密钥是否匹配
    return client_secret_key == api_secret_key


def generate_sts_policy(bucket, region, allow_prefix):
    """
    生成 STS 策略

    Args:
        bucket: 存储桶名称
        region: 区域
        allow_prefix: 允许的路径前缀

    Returns:
        STS 策略（JSON 字符串）
    """
    policy = {
        "version": "2.0",
        "statement": [
            {
                "action": [
                    "name/cos:PutObject",
                    "name/cos:PostObject",
                    "name/cos:HeadObject",
                    "name/cos:GetObject"
                ],
                "effect": "allow",
                "resource": [
                    f"qcs::cos:{region}:uid/*:{bucket}/{allow_prefix}"
                ]
            }
        ]
    }

    return json.dumps(policy)


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "ok",
        "service": "tencent-cos-upload-api",
        "version": "1.0.0"
    })


@app.route('/api/v1/upload-token', methods=['POST'])
def get_upload_token():
    """
    获取上传凭证（STS 临时凭证）

    请求参数：
    - mediaType: 媒体类型（image/video/file）
    - sceneName: 场景名称（如 imchat）
    - businessName: 业务名称（如 sale）
    - source: 来源（如 web、app）

    Headers：
    - X-Secret-Key: 安全密钥（可选，如果配置了的话）
    - Authorization: Bearer Token（可选）

    返回：
    - code: 状态码（0=成功）
    - data: 凭证数据
      - bucket: 存储桶名称
      - region: 区域
      - cusdomain: 自定义域名（可选）
      - tencent: 腾讯云临时凭证
        - tmpSecretId: 临时 SecretId
        - tmpSecretKey: 临时 SecretKey
        - sessionToken: 会话令牌
      - expiredTime: 过期时间（秒）
    """
    try:
        # 验证安全密钥
        if not verify_secret_key(request.headers):
            return jsonify({
                "code": -1,
                "msg": "Invalid secret key"
            }), 401

        # 获取请求参数
        data = request.get_json()
        media_type = data.get("mediaType", "image")
        scene_name = data.get("sceneName", "")
        business_name = data.get("businessName", "")
        source = data.get("source", "web")

        logger.info(f"收到上传凭证请求: mediaType={media_type}, sceneName={scene_name}, businessName={business_name}, source={source}")

        # 验证必需参数
        if not scene_name:
            return jsonify({
                "code": -1,
                "msg": "sceneName is required"
            }), 400

        if not business_name:
            return jsonify({
                "code": -1,
                "msg": "businessName is required"
            }), 400

        # 获取腾讯云配置
        config = CONFIG["tencent"]
        secret_id = config.get("secret_id")
        secret_key = config.get("secret_key")
        region = config.get("region")
        bucket = config.get("bucket")
        duration_seconds = config.get("duration_seconds")
        allow_prefix = f"{scene_name}/{business_name}/*"

        # 验证配置
        if not secret_id:
            return jsonify({
                "code": -1,
                "msg": "TENCENT_SECRET_ID is not configured"
            }), 500

        if not secret_key:
            return jsonify({
                "code": -1,
                "msg": "TENCENT_SECRET_KEY is not configured"
            }), 500

        if not bucket:
            return jsonify({
                "code": -1,
                "msg": "TENCENT_BUCKET is not configured"
            }), 500

        # 生成 STS 策略
        policy = generate_sts_policy(bucket, region, allow_prefix)

        # 调用腾讯云 STS 获取临时凭证
        logger.info("正在调用腾讯云 STS 获取临时凭证...")

        try:
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.sts.v20180813 import sts_client, models

            # 创建凭证
            cred = credential.Credential(secret_id, secret_key)

            # 创建 HTTP Profile
            httpProfile = HttpProfile()
            httpProfile.endpoint = "sts.tencentcloudapi.com"

            # 创建 Client Profile
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile

            # 创建 STS 客户端
            client = sts_client.StsClient(cred, region, clientProfile)

            # 创建请求
            req = models.GetFederationTokenRequest()
            req.Name = f"frontend-automation-{scene_name}-{business_name}"
            req.PolicyJson = policy
            req.DurationSeconds = duration_seconds

            # 调用 API
            resp = client.GetFederationToken(req)

            logger.info(f"✅ 获取临时凭证成功: Bucket={bucket}, Region={region}")

            # 返回结果
            result = {
                "code": 0,
                "data": {
                    "bucket": bucket,
                    "region": region,
                    "cusdomain": CONFIG.get("cusdomain", ""),
                    "tencent": {
                        "tmpSecretId": resp.Credentials.TmpSecretId,
                        "tmpSecretKey": resp.Credentials.TmpSecretKey,
                        "sessionToken": resp.Credentials.SessionToken
                    },
                    "expiredTime": duration_seconds
                }
            }

            return jsonify(result)

        except Exception as e:
            logger.error(f"调用腾讯云 STS 失败: {e}")
            return jsonify({
                "code": -1,
                "msg": f"Failed to get STS token: {str(e)}"
            }), 500

    except Exception as e:
        logger.error(f"获取上传凭证失败: {e}")
        return jsonify({
            "code": -1,
            "msg": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/v1/upload-result', methods=['POST'])
def report_upload_result():
    """
    上报上传结果

    请求参数：
    - filename: 文件名
    - tempVisit: 临时访问 URL
    - size: 文件大小
    - success: 是否成功

    Headers：
    - X-Secret-Key: 安全密钥（可选）
    - Authorization: Bearer Token（可选）

    返回：
    - code: 状态码（0=成功）
    - msg: 消息
    """
    try:
        # 验证安全密钥
        if not verify_secret_key(request.headers):
            return jsonify({
                "code": -1,
                "msg": "Invalid secret key"
            }), 401

        # 获取请求参数
        data = request.get_json()
        filename = data.get("filename", "")
        temp_visit = data.get("tempVisit", "")
        size = data.get("size", 0)
        success = data.get("success", False)

        logger.info(f"收到上传结果上报: filename={filename}, size={size}, success={success}")

        # 验证必需参数
        if not filename:
            return jsonify({
                "code": -1,
                "msg": "filename is required"
            }), 400

        # 这里可以将上传结果保存到数据库或进行其他处理
        # 目前仅记录日志

        if success:
            logger.info(f"✅ 文件上传成功: {filename} (URL: {temp_visit})")
        else:
            logger.warning(f"❌ 文件上传失败: {filename}")

        # 返回成功
        return jsonify({
            "code": 0,
            "msg": "Upload result reported successfully"
        })

    except Exception as e:
        logger.error(f"上报上传结果失败: {e}")
        return jsonify({
            "code": -1,
            "msg": f"Internal server error: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        "code": -1,
        "msg": "API endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    logger.error(f"Internal error: {error}")
    return jsonify({
        "code": -1,
        "msg": "Internal server error"
    }), 500


if __name__ == '__main__':
    # 检查配置
    logger.info("=" * 60)
    logger.info("腾讯云 COS 上传 API 服务启动")
    logger.info("=" * 60)

    # 打印配置信息（隐藏敏感信息）
    logger.info(f"Bucket: {CONFIG['tencent']['bucket']}")
    logger.info(f"Region: {CONFIG['tencent']['region']}")
    logger.info(f"Duration: {CONFIG['tencent']['duration_seconds']} 秒")
    logger.info(f"Allow Prefix: {CONFIG['tencent']['allow_prefix']}")
    logger.info(f"Cusdomain: {CONFIG.get('cusdomain', 'N/A')}")
    logger.info(f"Secret Key Configured: {'Yes' if CONFIG.get('secret_key') else 'No'}")

    # 检查必需的配置
    required_configs = [
        ("TENCENT_SECRET_ID", CONFIG["tencent"]["secret_id"]),
        ("TENCENT_SECRET_KEY", CONFIG["tencent"]["secret_key"]),
        ("TENCENT_BUCKET", CONFIG["tencent"]["bucket"]),
    ]

    missing_configs = [name for name, value in required_configs if not value]

    if missing_configs:
        logger.warning("=" * 60)
        logger.warning("⚠️  警告：缺少必需的配置！")
        for config_name in missing_configs:
            logger.warning(f"  - {config_name}")
        logger.warning("=" * 60)
        logger.warning("请检查 .env 文件并配置以上环境变量")
        logger.warning("当前服务将无法正常提供上传凭证服务")
        logger.warning("=" * 60)
    else:
        logger.info("✅ 所有必需的配置都已设置")

    logger.info("=" * 60)
    logger.info("API 端点:")
    logger.info("  - GET  /health - 健康检查")
    logger.info("  - POST /api/v1/upload-token - 获取上传凭证")
    logger.info("  - POST /api/v1/upload-result - 上报上传结果")
    logger.info("=" * 60)

    # 启动服务
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    app.run(host='0.0.0.0', port=port, debug=debug)
