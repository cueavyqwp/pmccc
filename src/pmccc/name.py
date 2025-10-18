"""
name转路径
"""

import os

__all__ = ["to_path"]


def to_path(text: str) -> str:
    """
    把name转为相对路径
    """
    split = text.split(":")
    package = split[0]
    name = split[1]
    version = split[2]
    platform = split[3] if len(split) > 3 else ""
    return os.path.join(*package.split("."), name, version, f"{name}-{version}{f'-{platform}' if platform else ''}.jar")
