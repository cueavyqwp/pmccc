"""
启动器相关内容
"""

from __future__ import annotations

import collections.abc
import typing

__all__ = ["client_launcher_info", "client_lanucher_config", "client_launcher"]

from ..pmccc import __version__
from ..lib import sysinfo
from ..lib import config
from ..lib import java

from .. import process

from .player import player_base, player_manager


if typing.TYPE_CHECKING:
    from .minecraft import minecraft_manager
    from . import version as _version


class client_launcher_info:
    """
    启动器信息
    """

    def __init__(self, name: str | None = None, version: str | None = None) -> None:
        """
        启动器信息

        name: 启动器名称

        version: 启动器版本
        """
        if name is None:
            name = "pmccc"
        if version is None:
            version = __version__
        self.name = name
        self.version = version


class client_lanucher_config(config.config_base):
    """
    启动器配置
    """

    def config_export(self) -> dict[str, typing.Any]:
        return {}

    def config_loads(self, data: dict[str, typing.Any]) -> None:
        pass


class client_launcher:
    """
    启动器主类
    """

    def __init__(self, name: str | None = None, version: str | None = None) -> None:
        """
        启动器主类

        name: 启动器名称

        version: 启动器版本
        """
        self.info = client_launcher_info(name, version)
        self.player = player_manager()
        self.sysinfo = sysinfo()
        self.java = java.java_manager()

    def search_java(self, dirs: collections.abc.Iterable[str] | None = None) -> None:
        """
        寻找Java,默认从环境变量中找

        dirs: 文件夹列表
        """
        self.java.search(dirs)

    def get_args(
        self,
        minecraft: minecraft_manager,
        version: _version.version_manager,
        player: player_base,
        library: list[str] | None = None,
        custom_jvm: list[str] | None = None,
        custom_game: list[str] | None = None,
        main_class: str | None = None,
        replacement: dict[str, typing.Any] | None = None,
        features: typing.Optional[dict[str, bool]] = None,
        force_utf8: bool = True,
    ) -> list[typing.Any]:
        """
        获取启动参数

        minecraft: .minecraft文件夹管理器

        version: 版本管理器

        player: 玩家类型

        library: 库文件列表

        custom_jvm: 自定义jvm参数

        custom_game: 自定义游戏参数

        main_class: 主类

        replacement: 替换参数中"${键名}"

        features: 启用特性

        force_utf8: 强制使用utf-8编码
        """
        return version.get_args(
            self.info,
            self.java,
            player,
            minecraft.path_assets,
            minecraft.path_libraries,
            library,
            custom_jvm,
            custom_game,
            main_class,
            replacement,
            features,
            force_utf8,
        )

    def launch(
        self,
        minecraft: minecraft_manager,
        version: str | _version.version_manager,
        player: player_base | int,
        custom_jvm: list[str] | None = None,
        custom_game: list[str] | None = None,
        main_class: str | None = None,
        replacement: dict[str, typing.Any] | None = None,
        features: typing.Optional[dict[str, bool]] = None,
        force_utf8: bool = True,
        output: bool = True,
        log4j2: process.log4j2_base | None = None,
        daemon: bool = True,
    ) -> process.popen:
        """
        启动游戏,并返回popen

        minecraft: .minecraft文件夹管理器

        version: 版本名称或版本管理器

        player: 玩家或玩家索引

        custom_jvm: 自定义jvm参数

        custom_game: 自定义游戏参数

        main_class: 主类

        replacement: 替换参数中"${键名}"

        features: 启用特性

        output: 是否在命令行输出

        log4j2: log4j2类

        ignore_parse_error: 忽略日志解析错误

        daemon: 进程守护
        """
        if isinstance(version, str):
            version = minecraft.version_get(version)
        if isinstance(player, int):
            player = self.player.get_player(player)
        library, native = version.version.get_libraries(minecraft.path_libraries)
        version.unzip_native(native)
        return process.popen(
            self.get_args(
                minecraft,
                version,
                player,
                library,
                custom_jvm,
                custom_game,
                main_class,
                replacement,
                features,
                False,
            ),
            version.dirname,
            output,
            log4j2,
            force_utf8,
            daemon,
        )
