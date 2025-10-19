"""
处理版本文件相关
"""

__all__ = ["version"]

import typing

from . import name
from . import rules
from . import verify
from . import launcher
from . import info as _info
from . import player as _player


class version:

    def __init__(self, data: dict[str, typing.Any], info: typing.Optional[_info] = None) -> None:
        """
        data: 版本json文件
        """
        self.data = data
        self.info = _info() if info is None else info

    def rename(self, id: str) -> tuple[tuple[str, str], tuple[str, str]]:
        """
        重命名版本文件

        返回应更名的文件
        """
        old = self.data["id"]
        self.data["id"] = id
        return (f"{old}.json", f"{id}.json"), (f"{old}.jar", f"{id}.jar")

    def get_args(self, features: typing.Optional[dict[str, bool]] = None) -> tuple[list[str], list[str]]:
        """
        返回jvm参数与游戏参数

        ---

        ## features
        `is_demo_user` demo版

        `has_custom_resolution` 自定义窗口大小
        """
        # 低版本不包含jvm参数
        if "minecraftArguments" in self.data:
            return ["-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump",
                    "-Djava.library.path=${natives_directory}",
                    "-Dminecraft.launcher.brand=${launcher_name}",
                    "-Dminecraft.launcher.version=${launcher_version}",
                    "-cp",
                    "${classpath}",], self.data["minecraftArguments"].split(" ")
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
        """
        获取库文件列表
        """
        library: list[str] = []
        for item in self.data["libraries"]:
            if "rules" in item and not rules.check(item["rules"], info=self.info):
                continue
            library.append(name.to_path(item["name"]))
        return library

    def get_native(self) -> list[str]:
        """
        获取native列表
        """
        native: list[str] = []
        for item in self.data["libraries"]:
            if "natives" not in item or self.info.os not in item["natives"] or "rules" in item and not rules.check(item["rules"], info=self.info):
                continue
            native.append(item["downloads"]["classifiers"]
                          [item["natives"][self.info.os]]["path"])
        return native

    def get_jar(self) -> str:
        """
        获取版本文件所对应的jar文件名(不管是否真的存在)
        """
        return f"{self.data['id']}.jar"

    def merge_args(self, jvm: list[str], game: list[str], main_class: typing.Optional[str] = None) -> list[str]:
        """
        合并jvm参数与游戏参数
        """
        if main_class is None:
            main_class = self.data["mainClass"]
        return [*jvm, main_class, *game]  # type: ignore

    def merge_cp(self, library: list[str], jar: str) -> str:
        """
        合并class path参数
        """
        return f"{self.info.split.join([*library, jar])}"

    def replace_args(self,  launcher_info: launcher.launcher_info, java: str, args: list[str], class_path: str, player: _player.player_base, game_directory: str, assets_directory: str, natives_directory: str, replacement: typing.Optional[dict[str, typing.Any]] = None) -> list[typing.Any]:
        """
        替换模板,获得完整的启动参数
        """
        ret: list[typing.Any] = [java]
        data: dict[str, typing.Any] = {
            "${auth_player_name}": player.name,
            "${version_name}": self.data["id"],
            "${game_directory}": game_directory,
            "${assets_root}": assets_directory,
            "${assets_index_name}": self.data["assets"],
            "${auth_uuid}": player.uuid,
            "${auth_access_token}": str(player.access_token),
            "${user_type}": player.type,
            "${version_type}": launcher_info.name,
            "${launcher_name}": launcher_info.name,
            "${launcher_version}": launcher_info.version,
            "${classpath}": class_path,
            "${natives_directory}": natives_directory,
            "${classpath_separator}": self.info.split
        }
        if replacement is not None:
            data.update(replacement)
        for item in args:
            for key in data.keys():
                if key in item:
                    item = item.replace(key, data[key])
            ret.append(item)
        return ret
