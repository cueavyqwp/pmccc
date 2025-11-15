"""
处理版本文件相关
"""

from __future__ import annotations

__all__ = ["version_data", "version_manager"]

import typing
import shlex
import json
import os
import re

from ..lib import rules
from ..lib import sysinfo
from ..lib import java as _java
from ..lib import path as _path

from . import player as _player
from . import native as _native

from .library import library_data

if typing.TYPE_CHECKING:
    from .launcher import client_launcher_info


class version_data:
    """
    版本json文件
    """

    def __init__(
        self, data: dict[str, typing.Any], info: sysinfo | None = None
    ) -> None:
        """
        data: 版本json文件
        """
        self.data = data
        self.info = sysinfo() if info is None else info

    def rename(self, id: str) -> tuple[tuple[str, str], tuple[str, str]]:
        """
        重命名版本文件

        返回应更名的文件
        """
        old = self.data["id"]
        self.data["id"] = id
        return (f"{old}.json", f"{id}.json"), (f"{old}.jar", f"{id}.jar")

    def get_args(
        self, features: typing.Optional[dict[str, bool]] = None
    ) -> tuple[list[str], list[str]]:
        """
        返回jvm参数与游戏参数

        ---

        ## features
        `is_demo_user` demo版

        `has_custom_resolution` 自定义窗口大小
        """
        # 低版本不包含jvm参数
        if "minecraftArguments" in self.data:
            return [
                "-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump",
                "-Djava.library.path=${natives_directory}",
                "-Dminecraft.launcher.brand=${launcher_name}",
                "-Dminecraft.launcher.version=${launcher_version}",
                "-cp",
                "${classpath}",
            ][0 if self.info.os == "windows" else 1 :], shlex.split(
                self.data["minecraftArguments"]
            )
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

    def get_libraries(
        self, libraries: str | None = None
    ) -> tuple[list[str], list[str]]:
        """
        获取库与native列表

        libraries: libraries文件夹位置,为空返回相对路径
        """
        native: list[str] = []
        library: dict[str, library_data] = {}
        optifine: library_data | None = None
        ret: list[str] = []
        for item in self.data["libraries"]:
            if "rules" in item and not rules.check(item["rules"], info=self.info):
                continue
            data = library_data(item, self.info)
            if data.is_native():
                if self.info.os not in item["natives"]:
                    continue
                native.append(data.get_path(libraries))
            else:
                # optifine放最后
                if "optifine" in item["name"]:
                    optifine = data
                    continue
                key = data.name.get_key()
                if key in library:
                    library[key].name |= data.name
                else:
                    library[key] = data
        for value in library.values():
            ret.append(value.get_path(libraries))
        if optifine is not None:
            ret.append(optifine.get_path(libraries))
        return ret, native

    def get_jar(self) -> str:
        """
        获取版本文件所对应的jar文件名(不管是否真的存在)
        """
        return f"{self.data['id']}.jar"

    def merge_args(
        self, jvm: list[str], game: list[str], main_class: str | None = None
    ) -> list[str]:
        """
        合并jvm参数与游戏参数
        """
        ret: list[str] = []
        optifine = False
        if main_class is None:
            main_class = str(self.data["mainClass"])
        for item in [*jvm, main_class, *game]:
            # 对optifine做额外兼容
            if item == "optifine.OptiFineForgeTweaker":
                optifine = True
                ret.pop()
                continue
            ret.append(item)
        if optifine:
            ret += ["--tweakClass", "optifine.OptiFineForgeTweaker"]
        return ret

    def merge_cp(self, library: list[str], jar: str) -> str:
        """
        合并class path参数
        """
        return f"{self.info.split.join([*library, jar])}"

    def replace_args(
        self,
        launcher_info: client_launcher_info,
        java: str | _java.java_manager,
        args: list[str],
        class_path: str,
        player: _player.player_base,
        game_directory: str,
        assets_directory: str,
        natives_directory: str,
        replacement: typing.Optional[dict[str, typing.Any]] = None,
        force_utf8: bool = True,
    ) -> list[typing.Any]:
        """
        替换模板,获得完整的启动参数
        """
        if isinstance(java, _java.java_manager):
            java = java.select_java(
                self.data["javaVersion"]["majorVersion"]
                if "javaVersion" in self.data
                else 8
            )[0]
        ret: list[typing.Any] = [java]
        if force_utf8:
            ret.append("-Dfile.encoding=UTF-8")
        data: dict[str, typing.Any] = {
            "${auth_player_name}": player.name,
            "${version_name}": self.data["id"],
            "${game_directory}": game_directory,
            "${assets_root}": assets_directory,
            "${assets_index_name}": (
                self.data["assets"] if "assets" in self.data else "pre-1.6"
            ),
            "${game_assets}": os.path.join(assets_directory, "virtual", "legacy"),
            "${auth_uuid}": player.uuid,
            "${auth_access_token}": str(player.access_token),
            "${user_type}": player.type,
            "${version_type}": launcher_info.name,
            "${launcher_name}": launcher_info.name,
            "${launcher_version}": launcher_info.version,
            "${classpath}": class_path,
            "${natives_directory}": natives_directory,
            "${classpath_separator}": self.info.split,
        }
        if replacement is not None:
            data |= replacement
        for item in args:
            for key in re.findall("(\\$\\{\\w*\\})", item):
                if key in data:
                    item = item.replace(key, data[key])
            ret.append(item)
        return ret


class version_manager:
    """
    版本管理器
    """

    def __init__(self, file: str, info: sysinfo | None = None) -> None:
        self.info = sysinfo() if info is None else info
        self.version: version_data
        self.file = _path.format_abspath(file)
        self.reload()

    @property
    def filename(self) -> str:
        """
        版本json文件名称
        """
        return os.path.basename(self.file)

    @property
    def jarname(self) -> str:
        """
        版本jar名称
        """
        return os.path.splitext(self.filename)[0] + ".jar"

    @property
    def jarfile(self) -> str:
        """
        版本jar文件
        """
        return os.path.join(self.dirname, self.jarname)

    @property
    def nativename(self) -> str:
        """
        native文件夹名称
        """
        return os.path.splitext(self.filename)[0] + "-natives"

    @property
    def native(self) -> str:
        """
        native文件夹
        """
        return os.path.join(self.dirname, self.nativename)

    @property
    def dirname(self) -> str:
        """
        版本文件夹
        """
        return os.path.dirname(self.file)

    @property
    def name(self) -> str:
        """
        版本名称
        """
        return self.version.data["id"]

    def save(self) -> None:
        """
        保存版本json文件
        """
        with open(self.file, "w", encoding="utf-8") as fp:
            json.dump(self.version.data, fp, indent=4, ensure_ascii=False)

    def rename(self, name: str, check: bool = True) -> bool:
        """
        重命名版本文件夹,版本json与版本jar
        """
        if (
            check
            and not _path.valid_filename(name)
            or not _path.check_removeable(self.dirname)
        ):
            return False
        self.version.rename(name)
        self.save()
        oldir = self.dirname
        nativename = self.nativename
        os.rename(self.file, os.path.join(self.dirname, f"{name}.json"))
        os.rename(self.jarfile, os.path.join(self.dirname, f"{name}.jar"))
        self.file = os.path.join(os.path.dirname(self.dirname), name, f"{name}.json")
        os.rename(oldir, self.dirname)
        if os.path.isdir((native := os.path.join(self.dirname, nativename))):
            os.rename(native, self.native)
        return True

    def reload(self) -> None:
        """
        重新加载版本json文件
        """
        with open(self.file, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        self.version = version_data(data, self.info)

    def unzip_native(
        self, native: list[str] | None = None, cwd: str | None = None
    ) -> None:
        """
        解压native

        native: native文件列表

        cwd: 库文件夹
        """
        if native is None:
            native = self.version.get_libraries(cwd)[1]
        _native.unzip_all(native, self.native, self.info)

    def get_args(
        self,
        launcher_info: client_launcher_info,
        java: str | _java.java_manager,
        player: _player.player_base,
        assets_directory: str,
        libraries_directory: str,
        library: list[str] | None = None,
        custom_jvm: list[str] | None = None,
        custom_game: list[str] | None = None,
        main_class: str | None = None,
        replacement: typing.Optional[dict[str, typing.Any]] = None,
        features: typing.Optional[dict[str, bool]] = None,
        force_utf8: bool = True,
    ) -> list[typing.Any]:
        """
        获取启动参数
        """
        jvm, game = self.version.get_args(features)
        if library is None:
            library = self.version.get_libraries(libraries_directory)[0]
        if custom_jvm is not None:
            jvm = custom_jvm + jvm
        if custom_game is not None:
            game = custom_game + game
        return self.version.replace_args(
            launcher_info,
            java,
            self.version.merge_args(jvm, game, main_class),
            self.version.merge_cp(
                library,
                self.jarfile,
            ),
            player,
            self.dirname,
            assets_directory,
            self.native,
            replacement,
            force_utf8,
        )
