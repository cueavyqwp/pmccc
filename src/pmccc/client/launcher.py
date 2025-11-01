"""
启动器相关内容
"""

__all__ = ["launcher_info"]

from ..pmccc import __version__
from ..lib import system
from ..lib import config

import typing


class launcher_info:
    """
    启动器信息
    """

    def __init__(self, name: typing.Optional[str] = None, version: typing.Optional[str] = None) -> None:
        if name is None:
            name = "pmccc"
        if version is None:
            version = __version__
        self.name = name
        self.version = version


class lanucher_config(config.config_base):
    """
    启动器配置
    """

    def __init__(self) -> None:
        pass


class launcher(launcher_info):
    """
    启动器主类
    """

    def __init__(self, name: str | None = None, version: str | None = None) -> None:
        super().__init__(name, version)
        self.info = system.sysinfo()
