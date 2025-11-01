"""
处理.minecraft文件夹
"""

__all__ = ["minecraft_manager"]

import os

from ..lib import path as _path
from .version import version_manager


class minecraft_manager:

    def __init__(self, home: str) -> None:
        self.versions: dict[str, str] = {}
        self.home = _path.format_abspath(home)
        for path in (self.path_versions, self.path_assets, self.path_libraries):
            _path.check_dir(path)

    @property
    def path_assets(self) -> str:
        return os.path.join(self.home, "assets")

    @property
    def path_libraries(self) -> str:
        return os.path.join(self.home, "libraries")

    @property
    def path_versions(self) -> str:
        return os.path.join(self.home, "versions")

    def version_list(self) -> dict[str, str]:
        return {name: path for name in os.listdir(self.path_versions) if os.path.isdir(path := os.path.join(self.path_versions, name))}

    def version_get(self, name: str) -> version_manager:
        return version_manager(os.path.join(self.path_versions, name, f"{name}.json"))

    def update(self) -> None:
        """
        更新版本列表
        """
        self.versions = self.version_list()
