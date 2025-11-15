"""
路径相关
"""

import shutil
import os

__all__ = [
    "format_abspath",
    "format_relpath",
    "check_dir",
    "check_removeable",
    "remove",
    "valid_filename",
]


def format_abspath(path: str) -> str:
    """
    格式化为绝对路径
    """
    return os.path.normpath(os.path.abspath(path))


def format_relpath(path: str, start: str | None = None) -> str:
    """
    格式化为相对路径
    """
    return os.path.normpath(os.path.relpath(path, start))


def check_dir(path: str, mkdir: bool = True, parent: bool = False) -> bool:
    """
    检查路径所在文件夹是否存在并创建文件夹
    """
    path = format_abspath(path)
    if parent:
        path = os.path.dirname(path)
    if os.path.exists(path):
        return True
    if mkdir and not os.path.exists(path):
        os.makedirs(path)
    return False


def check_removeable(path: str) -> bool:
    """
    检查目录/文件是否能被删除
    """
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            if not any(
                os.access(value, os.W_OK)
                for value in [root, *(os.path.join(root, item) for item in files)]
            ):
                return False
        return True
    else:
        return os.access(path, os.W_OK)


def remove(path: str, keepdir: bool = False) -> None:
    """
    清除文件/清理文件夹
    """
    if os.path.isfile(path):
        os.remove(path)
        return
    for name in os.listdir(path):
        path = os.path.join(path, name)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    if not keepdir:
        os.rmdir(path)


def valid_filename(name: str) -> bool:
    """
    检查文件名是否合法
    """
    if not name or "\0" in name or "/" in name:
        return False
    bad = set('<>:"\\|?*')
    if set(name) & bad:
        return False
    if os.path.splitext(name)[0].upper() in (
        "AUX",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "CON",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
        "NUL",
        "PRN",
    ):
        return False
    return True
