"""
MasterGo API 工具
用于读取 MasterGo 设计稿、提取组件信息、布局结构和静态资源
"""
import os
import json
import requests
import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class MasterGoComponent(BaseModel):
    """MasterGo 组件数据模型"""
    id: str = Field(..., description="组件 ID")
    name: str = Field(..., description="组件名称")
    type: str = Field(..., description="组件类型 (button, input, text, image, container等)")
    variant: Optional[str] = Field(default="", description="组件变体")
    text: Optional[str] = Field(default="", description="文本内容")
    position: Dict[str, float] = Field(default={}, description="位置信息 (x, y, width, height)")
    style: Dict[str, Any] = Field(default={}, description="样式信息 (颜色、圆角、边框等)")
    assets: Dict[str, str] = Field(default={}, description="关联的静态资源")
    children: List['MasterGoComponent'] = Field(default=[], description="子组件")
    visible: bool = Field(default=True, description="是否可见")


class MasterGoLayout(BaseModel):
    """MasterGo 布局数据模型"""
    type: str = Field(..., description="布局类型 (vertical, horizontal, grid, absolute)")
    spacing: float = Field(default=0, description="间距")
    padding: Dict[str, float] = Field(default={}, description="内边距")
    alignment: str = Field(default="start", description="对齐方式")
    constraints: Dict[str, Any] = Field(default={}, description="约束")


class MasterGoAsset(BaseModel):
    """MasterGo 静态资源数据模型"""
    id: str = Field(..., description="资源 ID")
    type: str = Field(..., description="资源类型 (image, icon)")
    mastergo_node_id: str = Field(..., description="MasterGo 节点 ID")
    name: str = Field(..., description="资源名称")
    format: str = Field(default="png", description="导出格式")
    scales: List[int] = Field(default=[1, 2, 3], description="导出倍数")
    url: Optional[str] = Field(default="", description="永久访问 URL")


class MasterGoDesign(BaseModel):
    """MasterGo 设计稿数据模型"""
    page: str = Field(..., description="页面名称")
    mastergo_url: str = Field(..., description="MasterGo URL")
    file_id: str = Field(..., description="MasterGo 文件 ID")
    node_id: Optional[str] = Field(default=None, description="节点 ID")
    components: List[MasterGoComponent] = Field(default=[], description="组件列表")
    layout: Optional[MasterGoLayout] = Field(default=None, description="布局信息")
    static_assets: List[MasterGoAsset] = Field(default=[], description="静态资源列表")
    colors: Dict[str, str] = Field(default={}, description="颜色主题")
    fonts: List[str] = Field(default=[], description="字体列表")


class MasterGoAPI:
    """MasterGo API 客户端"""

    def __init__(self, token: Optional[str] = None, config_path: Optional[str] = None):
        """
        初始化 MasterGo API 客户端

        Args:
            token: MasterGo API Token
            config_path: 配置文件路径（可选）
        """
        # 加载配置
        self.config = self._load_config(config_path)

        # 获取 Token（优先级：参数 > 配置文件 > 环境变量）
        self.token = token or self.config.get("token", "") or os.getenv("MASTERGO_TOKEN")

        # 获取其他配置
        self.base_url = self.config.get("base_url", "https://api.mastergo.cn/openapi")
        timeout = self.config.get("timeout", 30)

        # 设置请求头
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        # 设置超时
        self.timeout = timeout

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            配置字典
        """
        # 默认配置文件路径
        if not config_path:
            # 尝试从项目根目录读取
            workspace_path = os.getenv("COZE_WORKSPACE_PATH", ".")
            config_path = os.path.join(workspace_path, "assets/config/mastergo_config.json")

        # 如果配置文件存在，加载配置
        config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"⚠️  加载 MasterGo 配置文件失败: {e}")
                print(f"   使用默认配置")

        return config

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键
            default: 默认值

        Returns:
            配置值
        """
        return self.config.get(key, default)

    def get_file(self, file_id: str, depth: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        获取 MasterGo 文件

        Args:
            file_id: MasterGo 文件 ID
            depth: 遍历深度（可选）

        Returns:
            文件数据字典，失败返回 None
        """
        url = f"{self.base_url}/files/{file_id}"
        params = {}
        if depth is not None:
            params["depth"] = depth

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取 MasterGo 文件失败: {e}")
            return None

    def get_file_nodes(self, file_id: str, node_ids: List[str]) -> Optional[Dict[str, Any]]:
        """
        获取特定节点

        Args:
            file_id: MasterGo 文件 ID
            node_ids: 节点 ID 列表

        Returns:
            节点数据字典，失败返回 None
        """
        url = f"{self.base_url}/files/{file_id}/nodes"
        params = {"ids": ",".join(node_ids)}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取 MasterGo 节点失败: {e}")
            return None

    def export_image(self, file_id: str, node_id: str,
                    format: str = "png", scale: int = 2) -> Optional[str]:
        """
        导出图片并获取永久 URL

        Args:
            file_id: MasterGo 文件 ID
            node_id: 节点 ID
            format: 导出格式 (png, svg, jpg)
            scale: 缩放比例 (1, 2, 3)

        Returns:
            图片永久 URL
        """
        url = f"{self.base_url}/files/{file_id}/nodes/{node_id}/export"

        params = {
            "format": format,
            "scale": scale
        }

        try:
            response = requests.post(url, headers=self.headers, json=params, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()

            # MasterGo 返回永久 URL
            return result.get("url")

        except requests.exceptions.RequestException as e:
            print(f"导出图片失败: {e}")
            return None

    def get_all_images(self, file_id: str) -> List[Dict[str, str]]:
        """
        获取文件中所有图片资源的永久 URL

        Args:
            file_id: MasterGo 文件 ID

        Returns:
            图片资源列表 [{id, name, url}, ...]
        """
        file_data = self.get_file(file_id)

        if not file_data:
            return []

        images = []

        # 递归查找所有 IMAGE 类型的节点
        def find_images(node: Dict[str, Any]):
            if node.get("type") == "IMAGE":
                node_id = node.get("id")
                node_name = node.get("name", "unnamed")

                # 导出图片
                url = self.export_image(file_id, node_id, format="png", scale=2)

                if url:
                    images.append({
                        "id": node_id,
                        "name": node_name,
                        "url": url
                    })

            # 递归处理子节点
            if "children" in node:
                for child in node["children"]:
                    find_images(child)

        find_images(file_data.get("document", {}))

        return images

    def parse_mastergo_url(self, mastergo_url: str) -> tuple:
        """
        解析 MasterGo URL，提取 file_id 和 node_id

        Args:
            mastergo_url: MasterGo 设计稿链接

        Returns:
            (file_id, node_id)
        """
        # 匹配 MasterGo URL 格式
        # 支持格式: https://mastergo.com/file/file_id/xxx?node_id=node_id
        # 或者: https://mastergo.com/design/file_id/xxx?node_id=node_id
        # 或者: https://mastergo.com/file/file_id?param=value

        patterns = [
            r'https://mastergo\.com/file/([a-zA-Z0-9]+)/.*?node_id=([a-zA-Z0-9:-]+)',
            r'https://mastergo\.com/design/([a-zA-Z0-9]+)/.*?node_id=([a-zA-Z0-9:-]+)',
            r'https://mastergo\.com/file/([a-zA-Z0-9]+)[/?]',
            r'https://mastergo\.com/design/([a-zA-Z0-9]+)[/?]',
            r'https://mastergo\.com/file/([a-zA-Z0-9]+)',
            r'https://mastergo\.com/design/([a-zA-Z0-9]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, mastergo_url)
            if match:
                file_id = match.group(1)
                node_id = match.group(2) if len(match.groups()) > 1 else None
                return file_id, node_id

        return None, None
