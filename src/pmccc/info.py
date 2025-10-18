"""
用于获取系统信息
"""

__all__ = ["info"]

import platform
import typing


class info:

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
