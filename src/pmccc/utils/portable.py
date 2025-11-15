"""
导出为便携版(不包含java)
"""

__all__ = ["export"]

import subprocess
import shutil
import shlex
import os

from ..lib.info import sysinfo
from ..lib import path as _path

from ..client.native import unzip_all
from ..client.assets import assets_data
from ..client.player import player_base
from ..client.version import version_manager
from ..client.launcher import client_launcher_info


def export(
    version: version_manager,
    assets: str,
    libraries: str,
    to: str,
    player: player_base | None = None,
    launcher_info: client_launcher_info | None = None,
    info: sysinfo | None = None,
) -> None:
    if info is None:
        info = sysinfo()
    else:
        version.info = info
    if player is None:
        player = player_base()
    if launcher_info is None:
        launcher_info = client_launcher_info()
    _path.check_dir(to)
    # 解压native库,然后就不需要导出native库了
    lib, native = version.version.get_libraries()
    unzip_all(
        [os.path.join(libraries, value) for value in native],
        os.path.join(to, "natives"),
    )
    # 获取args
    _path.check_dir(os.path.join(to, "data"))
    args = version.version.replace_args(
        launcher_info=launcher_info,
        java="java",
        args=version.version.merge_args(*version.version.get_args()),
        class_path=version.version.merge_cp(
            [os.path.join("{path}", "libraries", value) for value in lib],
            os.path.join("{path}", "client.jar"),
        ),
        player=player,
        game_directory=os.path.join("{path}", "data"),
        assets_directory=os.path.join("{path}", "assets"),
        natives_directory=os.path.join("{path}", "natives"),
    )
    # 复制库
    for src in lib:
        file = os.path.join(libraries, src)
        dst = os.path.join(to, "libraries", src)
        _path.check_dir(dst, parent=True)
        shutil.copyfile(file, dst)
    # 复制assets
    base = os.path.join("indexes", version.version.data["assets"] + ".json")
    src = os.path.join(assets, base)
    dst = os.path.join(to, "assets", base)
    _path.check_dir(dst, parent=True)
    shutil.copyfile(src, dst)
    assets_data(src, assets).copy_object(os.path.join(to, "assets", "objects"))
    # 复制jar
    shutil.copyfile(version.jarfile, os.path.join(to, "client.jar"))
    # 生成脚本
    if info.os == "windows":
        lines = [
            "@echo off",
            "chcp 65001 > nul",
            f'cd /D "%~dp0"',
            subprocess.list2cmdline(args).replace("{path}", "%~dp0"),
        ]
        with open(os.path.join(to, "run.bat"), "w", encoding="utf-8") as fp:
            for line in lines:
                fp.write(f"{line}\n")

    else:
        lines = [
            "#!/bin/bash",
            "CWD=$(dirname $0)",
            f'cd "$CWD"',
            " ".join(
                (
                    '"' + value.replace('"', '\\"') + '"'
                    if "{path}" in value
                    else shlex.quote(value)
                )
                for value in args
            ).replace("{path}", "${CWD}"),
        ]
        with open(os.path.join(to, "run.sh"), "w", encoding="utf-8") as fp:
            for line in lines:
                fp.write(f"{line}\n")
