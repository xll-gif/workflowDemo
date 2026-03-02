#!/usr/bin/env python3
"""
Mock 服务生成工具

支持：
1. MSW (Mock Service Worker) - 推荐，现代且功能强大
2. Mock.js - 简单易用

功能：
- 从 API 定义生成 Mock 服务代码
- 支持真实的模拟数据
- 支持自定义响应模板
"""

import json
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class MockType(Enum):
    """Mock 类型"""
    MSW = "msw"
    MOCKJS = "mockjs"


@dataclass
class MockGeneratorConfig:
    """Mock 生成器配置"""
    use_realistic_data: bool = True
    use_delay: bool = True
    delay_time: int = 500  # 毫秒


class MockServiceGenerator:
    """Mock 服务生成器"""
    
    def __init__(self, config: MockGeneratorConfig = None):
        """
        初始化生成器
        
        Args:
            config: 生成器配置
        """
        self.config = config or MockGeneratorConfig()
    
    def generate_msw_mock(self, api_definitions: List[Dict[str, Any]]) -> str:
        """
        生成 MSW Mock 服务代码
        
        Args:
            api_definitions: API 定义列表
        
        Returns:
            MSW Mock 代码
        """
        # 生成导入语句
        imports = self._generate_msw_imports()
        
        # 生成 handlers
        handlers = []
        for api in api_definitions:
            handler = self._generate_msw_handler(api)
            handlers.append(handler)
        
        # 生成导出语句
        exports = "\n".join([
            "",
            "// 导出 handlers",
            "export const handlers = [",
            "  " + ",\n  ".join(handlers) + ",",
            "]"
        ])
        
        # 组装完整代码
        full_code = imports + "\n" + exports
        
        return full_code
    
    def generate_mockjs_mock(self, api_definitions: List[Dict[str, Any]]) -> str:
        """
        生成 Mock.js Mock 服务代码
        
        Args:
            api_definitions: API 定义列表
        
        Returns:
            Mock.js Mock 代码
        """
        # 生成导入语句
        imports = self._generate_mockjs_imports()
        
        # 生成 mocks
        mocks = []
        for api in api_definitions:
            mock = self._generate_mockjs_mock(api)
            mocks.append(mock)
        
        # 生成导出语句
        exports = "\n".join([
            "",
            "// 导出 mocks",
            "export default {",
            "  " + ",\n  ".join(mocks),
            "}"
        ])
        
        # 组装完整代码
        full_code = imports + "\n" + exports
        
        return full_code
    
    def generate(self, api_definitions: List[Dict[str, Any]], mock_type: str = "msw") -> str:
        """
        生成 Mock 服务代码
        
        Args:
            api_definitions: API 定义列表
            mock_type: Mock 类型（msw/mockjs）
        
        Returns:
            Mock 代码
        """
        if mock_type == "msw":
            return self.generate_msw_mock(api_definitions)
        elif mock_type == "mockjs":
            return self.generate_mockjs_mock(api_definitions)
        else:
            raise ValueError(f"不支持的 Mock 类型: {mock_type}")
    
    def _generate_msw_imports(self) -> str:
        """生成 MSW 导入语句"""
        return """// Mock Service Worker - 生成于: 自动化工作流
import { rest } from 'msw'

// Mock 数据生成工具
const generateId = () => Math.random().toString(36).substr(2, 9)
const generateToken = () => 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.' + Math.random().toString(36).substr(2)
"""
    
    def _generate_msw_handler(self, api: Dict[str, Any]) -> str:
        """
        生成单个 MSW handler
        
        Args:
            api: API 定义
        
        Returns:
            MSW handler 代码
        """
        method = api.get("method", "GET").lower()
        path = api.get("path", "/")
        name = api.get("name", "API")
        response_example = api.get("response_example", {})
        
        # 生成响应体
        response_body = json.dumps(response_example, indent=12, ensure_ascii=False)
        
        # 生成延迟
        delay = f"delay({self.config.delay_time})" if self.config.use_delay else ""
        
        # 生成 handler
        handler = f"""// {name}
rest.{method}('{path}', ({delay}, req, res, ctx) => {{
  return res(
    ctx.status({api.get('status_code', 200)}),
    ctx.json({response_body})
  )
}})"""
        
        return handler
    
    def _generate_mockjs_imports(self) -> str:
        """生成 Mock.js 导入语句"""
        return """// Mock.js - 生成于: 自动化工作流
import Mock from 'mockjs'

// Mock 数据生成工具
const Random = Mock.Random
"""
    
    def _generate_mockjs_mock(self, api: Dict[str, Any]) -> str:
        """
        生成单个 Mock.js mock
        
        Args:
            api: API 定义
        
        Returns:
            Mock.js mock 代码
        """
        method = api.get("method", "GET").lower()
        path = api.get("path", "/")
        name = api.get("name", "API")
        response_example = api.get("response_example", {})
        
        # 转换响应体为 Mock.js 模板
        response_template = self._convert_to_mockjs_template(response_example)
        
        # 生成 mock
        mock = f"""// {name}
'{path} {method}': {{
  'method': '{method}',
  'url': '{path}',
  'response': {response_template}
}}"""
        
        return mock
    
    def _convert_to_mockjs_template(self, data: Any) -> str:
        """
        将数据转换为 Mock.js 模板
        
        Args:
            data: 原始数据
        
        Returns:
            Mock.js 模板字符串
        """
        if isinstance(data, dict):
            items = []
            for key, value in data.items():
                mock_value = self._convert_value_to_mockjs(value, key)
                items.append(f'  "{key}": {mock_value}')
            return "{\n" + ",\n".join(items) + "\n  }"
        elif isinstance(data, list):
            if len(data) > 0:
                return f"[{self._convert_value_to_mockjs(data[0], 'item')}]"
            return "[]"
        else:
            return self._convert_value_to_mockjs(data, "")
    
    def _convert_value_to_mockjs(self, value: Any, field_name: str) -> str:
        """
        将值转换为 Mock.js 表达式
        
        Args:
            value: 原始值
            field_name: 字段名
        
        Returns:
            Mock.js 表达式字符串
        """
        if isinstance(value, dict):
            return self._convert_to_mockjs_template(value)
        elif isinstance(value, list):
            if len(value) > 0:
                return f"[{self._convert_value_to_mockjs(value[0], field_name)}]"
            return "[]"
        elif isinstance(value, str):
            # 根据字段名生成适当的 Mock.js 表达式
            if "token" in field_name.lower():
                return "@string('lower', 32)"
            elif "email" in field_name.lower():
                return "@email()"
            elif "name" in field_name.lower():
                return "@cname()"
            elif "phone" in field_name.lower():
                return "'1' + @pick('3','5','7','8','9') + @string('number', 9)"
            elif "avatar" in field_name.lower() or "image" in field_name.lower():
                return "@image('100x100')"
            elif "url" in field_name.lower():
                return "@url()"
            elif "id" in field_name.lower():
                return "@id()"
            elif "date" in field_name.lower() or "time" in field_name.lower():
                return "@datetime()"
            elif "price" in field_name.lower() or "money" in field_name.lower():
                return "@float(0, 1000, 2, 2)"
            else:
                # 检查是否是固定的 token 或特殊字符串
                if value.startswith("eyJ") or len(value) > 30:
                    return f"'{value}'"  # 保持原样
                return f"'{value}'"
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, float):
            return str(value)
        elif isinstance(value, bool):
            return "true" if value else "false"
        else:
            return "null"


# 便捷函数
def generate_mock_service(
    api_definitions: List[Dict[str, Any]],
    mock_type: str = "msw",
    config: MockGeneratorConfig = None
) -> str:
    """
    生成 Mock 服务代码（便捷函数）
    
    Args:
        api_definitions: API 定义列表
        mock_type: Mock 类型（msw/mockjs）
        config: 生成器配置
    
    Returns:
        Mock 代码
    """
    generator = MockServiceGenerator(config)
    return generator.generate(api_definitions, mock_type)


# 示例 API 定义
EXAMPLE_API_DEFINITIONS = [
    {
        "name": "登录",
        "method": "POST",
        "path": "/api/v1/login",
        "description": "用户登录",
        "request_body": {
            "email": "user@example.com",
            "password": "123456"
        },
        "response_example": {
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
        "status_code": 200
    },
    {
        "name": "获取用户信息",
        "method": "GET",
        "path": "/api/v1/user/info",
        "description": "获取当前用户信息",
        "response_example": {
            "code": 0,
            "message": "获取成功",
            "data": {
                "id": "123",
                "name": "张三",
                "email": "user@example.com",
                "phone": "13800138000",
                "avatar": "https://example.com/avatar.png",
                "created_at": "2024-01-01 00:00:00"
            }
        },
        "status_code": 200
    }
]


if __name__ == "__main__":
    """主函数：示例用法"""
    import sys
    import os
    
    # 添加 src 到路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
    
    print("=" * 80)
    print("🧪 Mock 服务生成器测试")
    print("=" * 80)
    
    # 生成 MSW Mock
    print("\n📋 生成 MSW Mock 服务:\n")
    msw_mock = generate_mock_service(EXAMPLE_API_DEFINITIONS, "msw")
    print(msw_mock)
    
    print("\n" + "=" * 80)
    print("\n📋 生成 Mock.js Mock 服务:\n")
    mockjs_mock = generate_mock_service(EXAMPLE_API_DEFINITIONS, "mockjs")
    print(mockjs_mock)
    
    print("\n" + "=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)
