"""
启动器相关内容
"""

from __future__ import annotations

__all__ = ["launcher_info"]

from .player import player_base, player_manager

from ..pmccc import __version__
from ..lib import system
from ..lib import config
from ..lib import java
from .. import process

import typing

if typing.TYPE_CHECKING:
    from .minecraft import minecraft_manager
    from .version import version_manager


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

    def config_export(self) -> dict[str, typing.Any]:
        return {}

    def config_loads(self, data: dict[str, typing.Any]) -> None:
        pass


class launcher:
    """
    启动器主类
    """

    def __init__(self, name: str | None = None, version: str | None = None) -> None:
        self.info = launcher_info(name, version)
        self.player = player_manager()
        self.sysinfo = system.sysinfo()
        self.java = java.java_manager()

    def search_java(self, dirs: list[str] | None = None) -> None:
        """
        寻找Java,默认从环境变量中找
        """
        self.java.search(dirs)

    def get_args(self, minecraft: minecraft_manager, version: version_manager, player: player_base, custom_jvm: list[str] | None = None, custom_game: list[str] | None = None, main_class: str | None = None, replacement: dict[str, typing.Any] | None = None, force_utf8: bool = True) -> list[typing.Any]:
        return version.get_args(
            self.info,
            self.java,
            player,
            minecraft.path_assets,
            minecraft.path_libraries,
            custom_jvm,
            custom_game,
            main_class,
            replacement,
            force_utf8
        )

    def launch(self, minecraft: minecraft_manager, version_name: str, player: int, custom_jvm: list[str] | None = None, custom_game: list[str] | None = None, main_class: str | None = None, replacement: dict[str, typing.Any] | None = None, force_utf8: bool = True, log4j2: process.log4j2 | None = None, ignore_parse_error: bool = True) -> process.popen:
        version = minecraft.version_get(version_name)
        return process.popen(
            self.get_args(
                minecraft,
                version,
                self.player.get_player(player),
                custom_jvm,
                custom_game,
                main_class,
                replacement,
                force_utf8
            ),
            version.dirname,
            log4j2,
            ignore_parse_error
        )
