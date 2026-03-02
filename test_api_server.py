"""
测试脚本：验证腾讯云 COS 上传 API 服务

测试以下功能：
1. 健康检查接口
2. 获取上传凭证接口
3. 上报上传结果接口
"""
import os
import sys
import json
import time
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API 配置
API_BASE_URL = os.getenv("TENCENT_API_BASE_URL", "http://localhost:5000")
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "")

# 测试配置
TEST_CONFIG = {
    "scene_name": os.getenv("TENCENT_SCENE_NAME", "frontend-automation"),
    "business_name": os.getenv("TENCENT_BUSINESS_NAME", "workflow"),
    "source": "test-script"
}


def print_test_header(test_name):
    """打印测试标题"""
    print("\n" + "=" * 60)
    print(f"测试: {test_name}")
    print("=" * 60)


def print_result(success, message):
    """打印测试结果"""
    status = "✅ 通过" if success else "❌ 失败"
    print(f"{status}: {message}")
    return success


def test_health_check():
    """测试健康检查接口"""
    print_test_header("健康检查接口")

    try:
        url = f"{API_BASE_URL}/health"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return print_result(True, f"服务状态: {data.get('status', 'unknown')}")
        else:
            return print_result(False, f"HTTP 状态码: {response.status_code}")

    except Exception as e:
        return print_result(False, f"请求失败: {e}")


def test_get_upload_token():
    """测试获取上传凭证接口"""
    print_test_header("获取上传凭证接口")

    url = f"{API_BASE_URL}/api/v1/upload-token"

    # 构建请求参数
    payload = {
        "mediaType": "image",
        "sceneName": TEST_CONFIG["scene_name"],
        "businessName": TEST_CONFIG["business_name"],
        "source": TEST_CONFIG["source"]
    }

    # 构建 Headers
    headers = {
        "Content-Type": "application/json"
    }

    # 添加 X-Secret-Key（如果配置了）
    if API_SECRET_KEY:
        headers["X-Secret-Key"] = API_SECRET_KEY

    print(f"请求参数:")
    print(f"  URL: {url}")
    print(f"  Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200:
            data = response.json()

            if data.get("code") == 0:
                result_data = data.get("data", {})

                # 验证返回的字段
                required_fields = [
                    "bucket",
                    "region",
                    "tencent.tmpSecretId",
                    "tencent.tmpSecretKey",
                    "tencent.sessionToken",
                    "expiredTime"
                ]

                missing_fields = []
                for field in required_fields:
                    if "." in field:
                        parent, child = field.split(".")
                        if parent not in result_data or child not in result_data[parent]:
                            missing_fields.append(field)
                    else:
                        if field not in result_data:
                            missing_fields.append(field)

                if missing_fields:
                    return print_result(False, f"缺少必需字段: {', '.join(missing_fields)}")

                # 打印凭证信息（隐藏敏感信息）
                print(f"\n凭证信息:")
                print(f"  Bucket: {result_data.get('bucket')}")
                print(f"  Region: {result_data.get('region')}")
                print(f"  Cusdomain: {result_data.get('cusdomain', 'N/A')}")
                print(f"  临时 SecretId: {result_data['tencent']['tmpSecretId'][:8]}...")
                print(f"  临时 SecretKey: {result_data['tencent']['tmpSecretKey'][:8]}...")
                print(f"  SessionToken: {result_data['tencent']['sessionToken'][:8]}...")
                print(f"  过期时间: {result_data['expiredTime']} 秒")

                return print_result(True, "获取上传凭证成功")
            else:
                return print_result(False, f"API 返回错误: {data.get('msg', 'Unknown error')}")
        else:
            return print_result(False, f"HTTP 状态码: {response.status_code}")

    except Exception as e:
        return print_result(False, f"请求失败: {e}")


def test_report_upload_result():
    """测试上报上传结果接口"""
    print_test_header("上报上传结果接口")

    url = f"{API_BASE_URL}/api/v1/upload-result"

    # 构建请求参数
    payload = {
        "filename": "test-image.png",
        "tempVisit": "https://example.com/test-image.png",
        "size": 1024,
        "success": True
    }

    # 构建 Headers
    headers = {
        "Content-Type": "application/json"
    }

    # 添加 X-Secret-Key（如果配置了）
    if API_SECRET_KEY:
        headers["X-Secret-Key"] = API_SECRET_KEY

    print(f"请求参数:")
    print(f"  URL: {url}")
    print(f"  Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200:
            data = response.json()

            if data.get("code") == 0:
                return print_result(True, "上报上传结果成功")
            else:
                return print_result(False, f"API 返回错误: {data.get('msg', 'Unknown error')}")
        else:
            return print_result(False, f"HTTP 状态码: {response.status_code}")

    except Exception as e:
        return print_result(False, f"请求失败: {e}")


def test_invalid_secret_key():
    """测试无效的安全密钥"""
    print_test_header("无效安全密钥测试")

    url = f"{API_BASE_URL}/api/v1/upload-token"

    # 构建请求参数
    payload = {
        "mediaType": "image",
        "sceneName": TEST_CONFIG["scene_name"],
        "businessName": TEST_CONFIG["business_name"],
        "source": TEST_CONFIG["source"]
    }

    # 构建 Headers（使用错误的密钥）
    headers = {
        "Content-Type": "application/json",
        "X-Secret-Key": "invalid-secret-key"
    }

    print(f"请求参数:")
    print(f"  URL: {url}")
    print(f"  Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    print(f"  X-Secret-Key: invalid-secret-key")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 401:
            return print_result(True, "正确拒绝无效密钥")
        elif response.status_code == 200:
            return print_result(False, "接受了无效密钥（安全风险！）")
        else:
            return print_result(False, f"意外的响应: HTTP {response.status_code}")

    except Exception as e:
        return print_result(False, f"请求失败: {e}")


def test_missing_parameters():
    """测试缺少必需参数"""
    print_test_header("缺少必需参数测试")

    url = f"{API_BASE_URL}/api/v1/upload-token"

    # 构建请求参数（缺少 sceneName 和 businessName）
    payload = {
        "mediaType": "image",
        "source": TEST_CONFIG["source"]
    }

    # 构建 Headers
    headers = {
        "Content-Type": "application/json"
    }

    if API_SECRET_KEY:
        headers["X-Secret-Key"] = API_SECRET_KEY

    print(f"请求参数:")
    print(f"  URL: {url}")
    print(f"  Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 400:
            return print_result(True, "正确拒绝缺少参数的请求")
        else:
            return print_result(False, f"意外的响应: HTTP {response.status_code}")

    except Exception as e:
        return print_result(False, f"请求失败: {e}")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始测试腾讯云 COS 上传 API 服务")
    print("=" * 60)
    print(f"\n配置:")
    print(f"  API Base URL: {API_BASE_URL}")
    print(f"  API Secret Key: {'已配置' if API_SECRET_KEY else '未配置'}")
    print(f"  Scene Name: {TEST_CONFIG['scene_name']}")
    print(f"  Business Name: {TEST_CONFIG['business_name']}")
    print(f"  Source: {TEST_CONFIG['source']}")

    # 等待服务启动
    print(f"\n等待服务启动...")
    time.sleep(2)

    # 运行测试
    test_results = []

    test_results.append(("健康检查", test_health_check()))
    test_results.append(("获取上传凭证", test_get_upload_token()))
    test_results.append(("上报上传结果", test_report_upload_result()))

    # 仅在配置了安全密钥时测试无效密钥
    if API_SECRET_KEY:
        test_results.append(("无效安全密钥", test_invalid_secret_key()))

    test_results.append(("缺少必需参数", test_missing_parameters()))

    # 打印测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed_count = 0
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed_count += 1

    print(f"\n总计: {passed_count}/{len(test_results)} 测试通过")

    if passed_count == len(test_results):
        print("\n🎉 所有测试通过！API 服务运行正常")
        return True
    else:
        print(f"\n⚠️  {len(test_results) - passed_count} 个测试失败")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
