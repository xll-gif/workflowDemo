"""
MasterGo Magic MCP 客户端工具

使用 MCP (Model Context Protocol) 与 MasterGo Magic MCP 服务器通信
"""
import os
import json
import subprocess
import time
import uuid
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class MCPMessage(BaseModel):
    """MCP 消息基类"""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC 版本")
    id: Optional[str] = Field(default=None, description="请求 ID")


class MCPRequest(MCPMessage):
    """MCP 请求"""
    method: str = Field(..., description="方法名")
    params: Optional[Dict[str, Any]] = Field(default=None, description="参数")

    def __init__(self, method: str, params: Optional[Dict[str, Any]] = None):
        super().__init__(id=str(uuid.uuid4()), method=method, params=params)


class MCPResponse(MCPMessage):
    """MCP 响应"""
    result: Optional[Any] = Field(default=None, description="结果")
    error: Optional[Dict[str, Any]] = Field(default=None, description="错误")


class MasterGoMCPClient:
    """MasterGo Magic MCP 客户端"""

    def __init__(self, token: str, api_url: str = "https://mastergo.com"):
        """
        初始化 MCP 客户端

        Args:
            token: MasterGo MCP Token
            api_url: MasterGo API URL
        """
        self.token = token
        self.api_url = api_url
        self.mcp_process = None
        self.stdin = None
        self.stdout = None
        self.stderr = None

    def start(self) -> bool:
        """
        启动 MCP 服务器

        Returns:
            是否启动成功
        """
        # 启动 MCP 服务器
        cmd = [
            "npx",
            "-y",  # 自动安装
            "@mastergo/magic-mcp",
            "--token", self.token,
            "--url", self.api_url
        ]

        try:
            self.mcp_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # 等待服务器启动
            time.sleep(2)

            # 检查进程状态
            if self.mcp_process.poll() is None:
                return True
            else:
                return False

        except Exception as e:
            print(f"启动 MCP 服务器失败: {e}")
            return False

    def stop(self):
        """停止 MCP 服务器"""
        if self.mcp_process:
            self.mcp_process.terminate()
            try:
                self.mcp_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.mcp_process.kill()

    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        发送 MCP 请求

        Args:
            method: 方法名
            params: 参数

        Returns:
            响应结果
        """
        # 创建请求
        request = MCPRequest(method=method, params=params)

        # 发送请求
        request_json = json.dumps(request.model_dump(), ensure_ascii=False) + "\n"

        if not self.mcp_process or self.mcp_process.poll() is not None:
            raise RuntimeError("MCP 服务器未运行")

        try:
            # 写入请求
            self.mcp_process.stdin.write(request_json)
            self.mcp_process.stdin.flush()

            # 读取响应
            response_line = self.mcp_process.stdout.readline()
            if not response_line:
                raise RuntimeError("未收到响应")

            # 解析响应
            response_data = json.loads(response_line.strip())
            response = MCPResponse(**response_data)

            if response.error:
                raise RuntimeError(f"MCP 错误: {response.error}")

            return response.result

        except Exception as e:
            raise RuntimeError(f"MCP 通信失败: {e}")

    def get_design(self, design_url: str) -> Dict[str, Any]:
        """
        获取设计文件 DSL 数据

        Args:
            design_url: 设计文件 URL

        Returns:
            设计数据
        """
        return self.send_request(
            method="get_design",
            params={"url": design_url}
        )

    def list_components(self, design_url: str) -> List[Dict[str, Any]]:
        """
        列出设计中的所有组件

        Args:
            design_url: 设计文件 URL

        Returns:
            组件列表
        """
        return self.send_request(
            method="list_components",
            params={"url": design_url}
        )

    def export_assets(self, design_url: str, asset_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        导出设计中的资源

        Args:
            design_url: 设计文件 URL
            asset_types: 资源类型列表

        Returns:
            资源列表
        """
        if asset_types is None:
            asset_types = ["IMAGE", "ICON"]

        return self.send_request(
            method="export_assets",
            params={
                "url": design_url,
                "asset_types": asset_types
            }
        )


class MockMasterGoMCPClient:
    """
    Mock MasterGo MCP 客户端

    用于开发阶段，当真实 MCP 不可用时使用
    """

    def __init__(self, token: str, api_url: str = "https://mastergo.com"):
        self.token = token
        self.api_url = api_url

    def start(self) -> bool:
        """启动（Mock）"""
        return True

    def stop(self):
        """停止（Mock）"""
        pass

    def get_design(self, design_url: str) -> Dict[str, Any]:
        """获取设计（Mock）"""
        return {
            "success": True,
            "design_url": design_url,
            "components": [
                {
                    "id": "btn_login",
                    "name": "LoginButton",
                    "type": "BUTTON",
                    "props": {
                        "text": "登录",
                        "backgroundColor": "#1890ff",
                        "borderRadius": 4,
                        "width": 200,
                        "height": 40
                    }
                },
                {
                    "id": "input_username",
                    "name": "UsernameInput",
                    "type": "INPUT",
                    "props": {
                        "placeholder": "请输入用户名",
                        "borderRadius": 4,
                        "borderWidth": 1,
                        "width": 300,
                        "height": 40
                    }
                },
                {
                    "id": "input_password",
                    "name": "PasswordInput",
                    "type": "INPUT",
                    "props": {
                        "placeholder": "请输入密码",
                        "borderRadius": 4,
                        "borderWidth": 1,
                        "width": 300,
                        "height": 40,
                        "secure": True
                    }
                }
            ],
            "assets": [
                {
                    "id": "img_logo",
                    "name": "logo.png",
                    "type": "IMAGE",
                    "url": f"{self.api_url}/assets/logo.png",
                    "width": 100,
                    "height": 100
                }
            ],
            "styles": {
                "colors": {
                    "primary": "#1890ff",
                    "background": "#ffffff",
                    "text": "#000000",
                    "border": "#d9d9d9"
                },
                "fonts": {
                    "primary": "PingFang SC",
                    "code": "Monaco"
                },
                "spacing": {
                    "xs": 4,
                    "sm": 8,
                    "md": 16,
                    "lg": 24,
                    "xl": 32
                }
            }
        }

    def list_components(self, design_url: str) -> List[Dict[str, Any]]:
        """列出组件（Mock）"""
        design = self.get_design(design_url)
        return design.get("components", [])

    def export_assets(self, design_url: str, asset_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """导出资源（Mock）"""
        design = self.get_design(design_url)
        return design.get("assets", [])


def create_mastergo_client(use_mock: bool = False) -> Any:
    """
    创建 MasterGo MCP 客户端

    Args:
        use_mock: 是否使用 Mock 客户端

    Returns:
        MCP 客户端实例
    """
    token = os.getenv("MASTERGO_MCP_TOKEN", "mock_token")  # Mock 模式下使用默认 Token
    api_url = os.getenv("MASTERGO_API_URL", "https://mastergo.com")

    if use_mock:
        return MockMasterGoMCPClient(token, api_url)
    else:
        if not token or token == "mock_token":
            raise ValueError("真实模式需要设置 MASTERGO_MCP_TOKEN 环境变量")
        return MasterGoMCPClient(token, api_url)


# 测试代码
if __name__ == "__main__":
    # 测试 Mock 客户端
    print("测试 Mock 客户端")
    print("=" * 80)

    client = create_mastergo_client(use_mock=True)

    # 获取设计
    design = client.get_design("https://mastergo.com/design/login")
    print(f"设计数据: {json.dumps(design, ensure_ascii=False, indent=2)}")

    # 列出组件
    components = client.list_components("https://mastergo.com/design/login")
    print(f"\n组件列表: {json.dumps(components, ensure_ascii=False, indent=2)}")

    # 导出资源
    assets = client.export_assets("https://mastergo.com/design/login")
    print(f"\n资源列表: {json.dumps(assets, ensure_ascii=False, indent=2)}")

    print("\n✅ Mock 客户端测试通过！")
