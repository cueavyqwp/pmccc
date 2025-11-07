"""
导出为批处理
"""

__all__ = ["export_bat", "export_shell"]

import subprocess
import typing
import shlex

from ..lib import path


def export_bat(args: list[typing.Any], file: str | None = None) -> str:
    """
    导出为bat

    **注意accessToken也会出现到导出的脚本中**
    """
    cwd = ""
    for index in range(len(args)):
        if args[index] == "--gameDir":
            cwd = str(args[index + 1])
            break
    ret = [
        "@echo off",
        "chcp 65001 > nul",
        f'cd /D "{cwd}"',
        subprocess.list2cmdline(args),
    ]
    if file:
        path.check_dir(file)
        with open(file, "w", encoding="utf-8") as fp:
            for line in ret:
                fp.write(f"{line}\n")
    return "\n".join(ret)


def export_shell(args: list[typing.Any], file: str | None = None) -> str:
    """
    导出为shell

    **注意accessToken也会出现到导出的脚本中**
    """
    cwd = ""
    for index in range(len(args)):
        if args[index] == "--gameDir":
            cwd = str(args[index + 1])
            break
    ret = ["#!/bin/bash", f'cd "{cwd}"', shlex.join(args)]
    if file:
        path.check_dir(file)
        with open(file, "w", encoding="utf-8") as fp:
            for line in ret:
                fp.write(f"{line}\n")
    return "\n".join(ret)
