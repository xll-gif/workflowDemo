#!/usr/bin/env python3
"""
Mock 服务生成节点

根据 API 定义生成 Mock 服务代码（MSW / Mock.js）
"""

import json
import os
import sys

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import (
    MockServiceGeneratorInput,
    MockServiceGeneratorOutput,
    ApiDefinition
)
from tools.mock_service_generator import MockServiceGenerator, MockGeneratorConfig


def mock_service_generator_node(
    state: MockServiceGeneratorInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> MockServiceGeneratorOutput:
    """
    Mock 服务生成节点
    
    功能：
    1. 接收 API 定义列表
    2. 生成 Mock 服务代码（MSW / Mock.js）
    3. 返回生成的代码
    
    Args:
        state: 节点输入，包含：
            - api_definitions: API 定义列表
            - mock_type: Mock 类型（msw/mockjs）
            - use_realistic_data: 是否使用真实模拟数据
        
        config: 运行配置
        
        runtime: 运行时上下文
    
    Returns:
        节点输出，包含：
            - success: 是否成功
            - mock_code: 生成的 Mock 代码
            - mock_file_name: Mock 文件名
            - message: 处理消息
            - api_count: 生成的 API 数量
    """
    """
    title: Mock 服务生成
    desc: 根据 API 定义生成 Mock 服务代码，支持 MSW 和 Mock.js 两种格式
    integrations: 无
    """
    ctx = runtime.context
    
    try:
        print("=" * 80)
        print("🚀 Mock 服务生成节点")
        print("=" * 80)
        
        # 1. 验证输入
        print("\n📋 步骤 1: 验证输入")
        print("-" * 80)
        
        if not state.api_definitions:
            print("❌ API 定义列表为空")
            return MockServiceGeneratorOutput(
                success=False,
                mock_code="",
                mock_file_name="",
                message="API 定义列表为空",
                api_count=0
            )
        
        print(f"✅ API 定义数量: {len(state.api_definitions)}")
        print(f"✅ Mock 类型: {state.mock_type}")
        print(f"✅ 使用真实数据: {state.use_realistic_data}")
        
        # 2. 转换 API 定义为字典格式
        print("\n📋 步骤 2: 转换 API 定义")
        print("-" * 80)
        
        api_dicts = []
        for i, api_def in enumerate(state.api_definitions, 1):
            # 处理 ApiDefinition 对象或字典
            if isinstance(api_def, ApiDefinition):
                api_dict = {
                    "name": api_def.name,
                    "method": api_def.method,
                    "path": api_def.path,
                    "description": api_def.description or "",
                    "request_params": api_def.request_params or {},
                    "request_body": api_def.request_body or {},
                    "response_example": api_def.response_example or {},
                    "status_code": api_def.status_code or 200
                }
            else:
                api_dict = api_def
            
            api_dicts.append(api_dict)
            print(f"   {i}. {api_dict['name']} - {api_dict['method']} {api_dict['path']}")
        
        # 3. 生成 Mock 代码
        print("\n📋 步骤 3: 生成 Mock 代码")
        print("-" * 80)
        
        # 配置生成器
        generator_config = MockGeneratorConfig(
            use_realistic_data=state.use_realistic_data,
            use_delay=True,
            delay_time=500
        )
        
        # 创建生成器
        generator = MockServiceGenerator(generator_config)
        
        # 生成代码
        mock_code = generator.generate(api_dicts, state.mock_type)
        
        print(f"✅ 代码生成成功")
        print(f"   Mock 类型: {state.mock_type}")
        print(f"   代码行数: {len(mock_code.splitlines())}")
        
        # 4. 确定文件名
        if state.mock_type == "msw":
            mock_file_name = "mockHandlers.js"
        elif state.mock_type == "mockjs":
            mock_file_name = "mockConfig.js"
        else:
            mock_file_name = "mock.js"
        
        print(f"✅ 文件名: {mock_file_name}")
        
        # 5. 生成代码预览
        print("\n📋 步骤 4: 代码预览（前 20 行）")
        print("-" * 80)
        preview_lines = mock_code.splitlines()[:20]
        for line in preview_lines:
            print(line)
        
        if len(mock_code.splitlines()) > 20:
            print(f"... (省略 {len(mock_code.splitlines()) - 20} 行)")
        
        # 6. 返回结果
        print("\n" + "=" * 80)
        print("✅ Mock 服务生成完成！")
        print("=" * 80)
        
        return MockServiceGeneratorOutput(
            success=True,
            mock_code=mock_code,
            mock_file_name=mock_file_name,
            message=f"成功生成 {len(api_dicts)} 个 API 的 Mock 服务代码",
            api_count=len(api_dicts)
        )
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ Mock 服务生成失败")
        print("=" * 80)
        print(f"错误信息: {e}")
        
        import traceback
        traceback.print_exc()
        
        return MockServiceGeneratorOutput(
            success=False,
            mock_code="",
            mock_file_name="",
            message=f"生成失败: {str(e)}",
            api_count=0
        )


if __name__ == "__main__":
    """主函数：节点测试"""
    print("\n" + "=" * 80)
    print("🧪 Mock 服务生成节点测试")
    print("=" * 80 + "\n")
    
    # 准备测试输入
    test_input = MockServiceGeneratorInput(
        api_definitions=[
            ApiDefinition(
                name="登录",
                method="POST",
                path="/api/v1/login",
                description="用户登录",
                request_body={
                    "email": "user@example.com",
                    "password": "123456"
                },
                response_example={
                    "code": 0,
                    "message": "登录成功",
                    "data": {
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example",
                        "user": {
                            "id": "123",
                            "name": "张三",
                            "email": "user@example.com",
                            "avatar": "https://example.com/avatar.png"
                        }
                    }
                },
                status_code=200
            ),
            ApiDefinition(
                name="获取用户信息",
                method="GET",
                path="/api/v1/user/info",
                description="获取当前用户信息",
                response_example={
                    "code": 0,
                    "message": "获取成功",
                    "data": {
                        "id": "123",
                        "name": "张三",
                        "email": "user@example.com",
                        "phone": "13800138000",
                        "avatar": "https://example.com/avatar.png"
                    }
                },
                status_code=200
            )
        ],
        mock_type="msw",
        use_realistic_data=True
    )
    
    # 创建模拟配置和 runtime
    config = RunnableConfig(
        configurable={
            "metadata": {
                "type": "task",
                "description": "生成 Mock 服务代码"
            }
        }
    )
    
    try:
        # 调用节点函数
        result = mock_service_generator_node(
            state=test_input,
            config=config,
            runtime=Runtime[Context]()
        )
        
        # 显示结果
        print("\n📊 执行结果:")
        print("-" * 80)
        print(f"   成功: {result.success}")
        print(f"   消息: {result.message}")
        print(f"   API 数量: {result.api_count}")
        print(f"   文件名: {result.mock_file_name}")
        print(f"   代码长度: {len(result.mock_code)} 字符")
        print()
        
        if result.success:
            print("📦 生成的 Mock 代码:")
            print("-" * 80)
            print(result.mock_code[:500])
            if len(result.mock_code) > 500:
                print("... (省略剩余代码)")
            print()
        
    except Exception as e:
        print(f"\n❌ 节点测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 80 + "\n")
