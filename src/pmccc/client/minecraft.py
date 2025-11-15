"""
处理.minecraft文件夹
"""

__all__ = ["minecraft_manager"]

import os

from ..lib import path as _path

from .version import version_manager


class minecraft_manager:
    """
    .minecraft文件夹管理器
    """

    def __init__(self, home: str) -> None:
        """
        .minecraft文件夹管理器

        home: .minecraft文件夹路径
        """
        self.versions: dict[str, str] = {}
        self.home = _path.format_abspath(home)
        for path in (self.path_versions, self.path_assets, self.path_libraries):
            _path.check_dir(path)

    @property
    def path_assets(self) -> str:
        """
        资源文件路径
        """
        return os.path.join(self.home, "assets")

    @property
    def path_libraries(self) -> str:
        """
        库文件夹
        """
        return os.path.join(self.home, "libraries")

    @property
    def path_versions(self) -> str:
        """
        版本文件夹
        """
        return os.path.join(self.home, "versions")

    def version_list(self) -> dict[str, str]:
        """
        获取版本列表,返回版本名及其对应路径
        """
        return {
            name: path
            for name in os.listdir(self.path_versions)
            if os.path.isdir(path := os.path.join(self.path_versions, name))
        }

    def version_get(self, name: str) -> version_manager:
        """
        获取版本,返回对应版本管理器

        name: 版本名称
        """
        return version_manager(os.path.join(self.path_versions, name, f"{name}.json"))

    def update(self) -> None:
        """
        更新版本列表
        """
        self.versions = self.version_list()
