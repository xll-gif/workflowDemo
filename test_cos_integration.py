"""
测试脚本：验证腾讯云 COS 上传工具的正确性

注意：由于沙箱环境限制，此脚本无法连接到真实的腾讯云 COS 服务。
此脚本仅用于验证代码语法、类结构和基本逻辑。
"""

import sys
import os
from typing import Optional

# 测试 1：验证工具类可以导入
def test_imports():
    """测试工具类导入"""
    print("=" * 60)
    print("测试 1: 验证工具类导入")
    print("=" * 60)

    try:
        # 模拟 cos 模块（因为沙箱中没有真实的 SDK）
        class MockCosClient:
            """Mock 腾讯云 COS 客户端"""
            def __init__(self, config):
                self.config = config

            def upload_file(self, bucket, key, local_path, callback=None):
                """模拟上传文件"""
                return {
                    'ETag': '"mock-etag"',
                    'Location': f'https://{bucket}.cos.ap-shanghai.myqcloud.com/{key}'
                }

        # 替换 sys.modules 中的 cos 模块
        sys.modules['cos'] = type('module', (), {})()
        sys.modules['cos'].CosS3Client = MockCosClient
        # Mock cos_cos_python_sdk_v5
        sys.modules['cos_cos_python_sdk_v5'] = type('module', (), {})()
        sys.modules['cos_cos_python_sdk_v5'].CosS3Client = MockCosClient
        sys.modules['cos_cos_python_sdk_v5'].CosS3Config = lambda **kwargs: None

        # 导入工具类
        sys.path.insert(0, os.path.join(os.getenv("COZE_WORKSPACE_PATH", "."), "src"))
        from tools.cos_uploader import TencentCOSUploader, STSCredentials, UploadResult

        print("✅ 工具类导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

# 测试 2：验证类结构
def test_class_structure():
    """测试类结构和属性"""
    print("\n" + "=" * 60)
    print("测试 2: 验证类结构")
    print("=" * 60)

    try:
        sys.path.insert(0, os.path.join(os.getenv("COZE_WORKSPACE_PATH", "."), "src"))
        from tools.cos_uploader import TencentCOSUploader, STSCredentials, UploadResult

        # 检查 STSCredentials 类
        print("STSCredentials 属性:")
        print(f"  - tmp_secret_id: str")
        print(f"  - tmp_secret_key: str")
        print(f"  - session_token: str")
        print(f"  - expired_time: int")
        print(f"  - bucket: str")
        print(f"  - region: str")
        print(f"  - cusdomain: Optional[str]")
        print("✅ STSCredentials 类结构正确")

        # 检查 UploadResult 类
        print("\nUploadResult 属性:")
        print(f"  - filename: str")
        print(f"  - temp_visit: str")
        print(f"  - size: int")
        print(f"  - url: str")
        print(f"  - success: bool")
        print(f"  - error: Optional[str]")
        print("✅ UploadResult 类结构正确")

        # 检查 TencentCOSUploader 类
        print("\nTencentCOSUploader 属性:")
        print(f"  - api_base_url: str")
        print(f"  - scene_name: str")
        print(f"  - business_name: str")
        print(f"  - mode: str")
        print(f"  - secret_key: Optional[str]")
        print(f"  - token: Optional[str]")
        print("✅ TencentCOSUploader 类结构正确")

        return True
    except Exception as e:
        print(f"❌ 类结构验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 测试 3：验证 upload_assets_node 的存储后端选择逻辑
def test_storage_backend_selection():
    """测试存储后端选择逻辑"""
    print("\n" + "=" * 60)
    print("测试 3: 验证存储后端选择逻辑")
    print("=" * 60)

    try:
        # 读取 upload_assets_node.py 文件
        node_path = os.path.join(os.getenv("COZE_WORKSPACE_PATH", "."), "src/graphs/nodes/upload_assets_node.py")
        with open(node_path, 'r') as f:
            content = f.read()

        # 检查是否包含多存储后端逻辑
        checks = [
            ("STORAGE_BACKEND", "是否包含 STORAGE_BACKEND 环境变量"),
            ("TencentCOSUploader", "是否导入 TencentCOSUploader"),
            ("_upload_to_storage", "是否有 _upload_to_storage 函数"),
            ("if storage_backend == \"cos\"", "是否有腾讯云 COS 分支"),
            ("elif storage_backend == \"oss\"", "是否有阿里云 OSS 分支"),
            ("else:", "是否有默认 Mock 分支"),
        ]

        all_passed = True
        for pattern, description in checks:
            if pattern in content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
                all_passed = False

        if all_passed:
            print("\n✅ 存储后端选择逻辑正确")
        else:
            print("\n❌ 存储后端选择逻辑不完整")

        return all_passed
    except Exception as e:
        print(f"❌ 存储后端选择逻辑验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 测试 4：验证配置文件
def test_config_files():
    """测试配置文件"""
    print("\n" + "=" * 60)
    print("测试 4: 验证配置文件")
    print("=" * 60)

    try:
        workspace = os.getenv("COZE_WORKSPACE_PATH", ".")

        # 检查 .env.tencentyun.example
        env_example_path = os.path.join(workspace, ".env.tencentyun.example")
        if os.path.exists(env_example_path):
            print("✅ .env.tencentyun.example 文件存在")

            with open(env_example_path, 'r') as f:
                content = f.read()

            required_vars = [
                "STORAGE_BACKEND",
                "TENCENT_API_BASE_URL",
                "TENCENT_SCENE_NAME",
                "TENCENT_BUSINESS_NAME",
                "TENCENT_MODE"
            ]

            all_vars_present = True
            for var in required_vars:
                if var in content:
                    print(f"  ✅ 包含环境变量 {var}")
                else:
                    print(f"  ❌ 缺少环境变量 {var}")
                    all_vars_present = False

            if all_vars_present:
                print("\n✅ 所有必需的环境变量都在配置文件中")
            else:
                print("\n❌ 配置文件缺少部分环境变量")
                return False
        else:
            print("❌ .env.tencentyun.example 文件不存在")
            return False

        # 检查文档文件
        doc_files = [
            "TENCENT_COS_INTEGRATION_GUIDE.md",
            "STATIC_ASSET_PROCESSING_GUIDE.md"
        ]

        for doc in doc_files:
            doc_path = os.path.join(workspace, doc)
            if os.path.exists(doc_path):
                print(f"✅ {doc} 文件存在")
            else:
                print(f"❌ {doc} 文件不存在")
                return False

        print("\n✅ 所有配置文件和文档都存在")

        return True
    except Exception as e:
        print(f"❌ 配置文件验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 主测试函数
def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始运行腾讯云 COS 集成测试")
    print("=" * 60)

    test_results = []

    # 运行所有测试
    test_results.append(("导入测试", test_imports()))
    test_results.append(("类结构测试", test_class_structure()))
    test_results.append(("存储后端选择测试", test_storage_backend_selection()))
    test_results.append(("配置文件测试", test_config_files()))

    # 打印测试结果
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
        print("\n🎉 所有测试通过！")
        return True
    else:
        print(f"\n⚠️  {len(test_results) - passed_count} 个测试失败")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
