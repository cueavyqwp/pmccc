"""
用于获取系统信息
"""

__all__ = ["sysinfo"]

import platform
import typing

import psutil


class sysinfo:
    """
    系统信息类
    """

    def __init__(self) -> None:
        self.os: typing.Literal["windows", "linux", "osx"]
        self.os_version: str
        self.arch: typing.Literal["x64", "x86"]
        self.update()

    def update(self) -> None:
        """
        更新系统信息
        """
        self.os = {"Windows": "windows", "Linux": "linux", "Darwin": "osx"}.get(
            platform.system(),
            "windows",
        )  # pyright: ignore[reportAttributeAccessIssue]
        self.os_version = platform.version()
        self.arch = "x64" if "64" in platform.machine() else "x86"

    def __str__(self) -> str:
        return f"{self.os}({self.os_version}) {self.arch}"

    @property
    def split(self) -> str:
        """
        系统文件分隔符
        """
        return ";" if self.os == "windows" else ":"

    @property
    def native(self) -> str:
        """
        native库后缀
        """
        return {"windows": "dll", "linux": "so", "osx": "jnilib"}.get(self.os, "dll")

    @property
    def memory_total(self) -> int:
        """
        内存总量 (单位:字节)
        """
        return psutil.virtual_memory().total

    @property
    def memory_available(self) -> int:
        """
        内存可用 (单位:字节)
        """
        return psutil.virtual_memory().available

    @property
    def memory_used(self) -> int:
        """
        内存已用 (单位:字节)
        """
        return psutil.virtual_memory().used

    @property
    def memory_percent(self) -> float:
        """
        内存使用率
        """
        return psutil.virtual_memory().percent
