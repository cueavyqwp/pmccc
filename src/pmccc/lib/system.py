"""
用于获取系统信息
"""

__all__ = ["sysinfo_base"]

import platform
import typing

import psutil


class sysinfo_base:

    def __init__(self) -> None:
        self.os: typing.Literal["windows", "linux", "osx"]
        self.os_version: str
        self.arch: typing.Literal["x64", "x86"]
        self.update()

    def update(self) -> None:
        self.os = {"Windows": "windows", "Linux": "linux", "Darwin": "osx"}.get(
            platform.system(), "windows")  # type: ignore
        self.os_version = platform.version()
        self.arch = "x64" if "64" in platform.machine() else "x86"

    def __str__(self) -> str:
        return f"{self.os}({self.os_version}) {self.arch}"

    @property
    def split(self) -> str:
        return ";" if self.os == "windows" else ":"

    @property
    def native(self) -> str:
        return {"windows": "dll", "linux": "so", "osx": "jnilib"}.get(self.os, "dll")


class sysinfo(sysinfo_base):

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
