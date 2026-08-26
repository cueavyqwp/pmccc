"""
启动游戏Demo
"""

import argparse
import os

from .lib import java as _java
from .client import player as _player
from .client.launcher import client_launcher as _launcher
from .client.minecraft import minecraft_manager as _minecraft_manager

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A demo for launch minecraft.")
    parser.add_argument("-j", "--java", type=str, help="Java path", default=None)
    parser.add_argument(
        "-v", "--version", type=str, help="The version of the minecraft", default=None
    )
    parser.add_argument(
        "-n", "--name", type=str, help="Name of the player", default="Dev"
    )
    parser.add_argument(
        "-u", "--uuid", type=str, help="UUID of the player", default=None
    )
    parser.add_argument("minecraft", help="The path of .minecraft")
    args = parser.parse_args()
    # 验证文件夹是否存在
    minecraft = args.minecraft
    if not os.path.isdir(minecraft):
        raise NotADirectoryError(f"Path: {minecraft}")
    minecraft_manager = _minecraft_manager(minecraft)
    launcher = _launcher()
    # 玩家
    name = args.name
    uuid = args.uuid
    if uuid is None:
        player = _player.player_offline(name)
    else:
        player = _player.player_base()
        player.name = name
        player.uuid = uuid
    # 版本
    version = args.version
    if not isinstance(version, str):
        print("\n".join(minecraft_manager.version_list().keys()))
        version = input(">")
    # 获取Java
    java = args.java
    if isinstance(java, str):
        if not os.path.exists(java):
            raise FileNotFoundError(f"Path: {java}")
        java = _java.java_info(java).path
    else:
        java = _java.java_manager()
        java.search()
    launcher.launch(minecraft_manager, version, player, java).wait()
