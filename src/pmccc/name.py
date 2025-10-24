"""
name转路径
"""

import typing
import os

__all__ = ["split", "to_path", "get_path", "compare"]


def split(text: str) -> list[str]:
    """
    分割name
    """
    split = text.split(":")
    return [*split[:3], split[3] if len(split) > 3 else ""]


def to_path(package: str, name: str, version: str, platform: typing.Optional[str] = None) -> str:
    """
    把split转为相对路径
    """
    return os.path.join(*package.split("."), name, version, f"{name}-{version}{f'-{platform}' if platform else ''}.jar")


def get_path(text: str) -> str:
    """
    把name转为相对路径
    """
    return to_path(*split(text))


def compare(first: str, second: str) -> bool:
    """
    比较版本号a >= b
    """
    split_first = [int(num) for num in first.split(".") if num.isdigit()]
    split_second = [int(num) for num in second.split(".") if num.isdigit()]
    len_first = len(split_first)
    len_second = len(split_second)
    if len_first > len_second:
        split_second += [0]*(len_first-len_second)
    else:
        split_first += [0]*(len_second-len_first)
    for numf, nums in zip(split_first, split_second):
        if numf >= nums:
            return True
    return False
