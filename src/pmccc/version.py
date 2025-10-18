"""
处理版本文件相关
"""

__all__ = ["version"]

import typing

from . import name
from . import rules
from . import verify
from . import info as _info


class version:

    def __init__(self, data: dict[str, typing.Any], info: typing.Optional[_info] = None) -> None:
        """
        data: 版本json文件
        """
        self.data = data
        self.info = _info() if info is None else info

    def get_args(self, features: typing.Optional[dict[str, bool]] = None) -> tuple[list[str], list[str]]:
        """
        返回jvm参数与游戏参数

        ---

        ## features
        `is_demo_user` demo版

        `has_custom_resolution` 自定义窗口大小
        """
        data = self.data["arguments"]
        arg_game: list[str] = []
        arg_jvm: list[str] = []
        for item in data["game"]:
            if isinstance(item, str):
                arg_game.append(item)
                continue
            if not rules.check(item["rules"], features, self.info):
                continue
            if isinstance(item["value"], str):
                arg_game.append(item["value"])
            else:
                arg_game += item["value"]
        for item in data["jvm"]:
            if isinstance(item, str):
                arg_jvm.append(item)
                continue
            if not rules.check(item["rules"], info=self.info):
                continue
            if isinstance(item["value"], str):
                arg_jvm.append(item["value"])
            else:
                arg_jvm += item["value"]
        return arg_jvm, arg_game

    def get_library(self) -> list[str]:
        library: list[str] = []
        for item in self.data["libraries"]:
            if "rules" in item and not rules.check(item["rules"], info=self.info):
                continue
            library.append(name.to_path(item["name"]))
        return library
