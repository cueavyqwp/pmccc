"""
启动器相关内容
"""

__all__ = ["launcher_info"]

from .pmccc import __version__
from . import info

import typing


class launcher_info:

    def __init__(self, name: typing.Optional[str] = None, version: typing.Optional[str] = None) -> None:
        if name is None:
            name = "pmccc"
        if version is None:
            version = __version__
        self.name = name
        self.version = version


class launcher(launcher_info):

    def __init__(self, name: str | None = None, version: str | None = None) -> None:
        super().__init__(name, version)
        self.info = info()
        self.path_user_data = self.info.path_user_data("pmccc")
