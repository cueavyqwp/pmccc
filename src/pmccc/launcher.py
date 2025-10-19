"""
启动器相关内容
"""

__all__ = ["launcher_info"]

from .pmccc_version import __version__

import typing


class launcher_info:

    def __init__(self, name: typing.Optional[str] = None, version: typing.Optional[str] = None) -> None:
        if name is None:
            name = "pmccc"
        if version is None:
            version = __version__
        self.name = name
        self.version = version
