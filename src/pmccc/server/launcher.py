"""
服务端启动类
"""

__all__ = ["server_launcher"]

import collections.abc
import typing
import os

from ..lib import java as _java
from ..lib import sysinfo

from .. import process


class server_launcher:

    def __init__(
        self,
        cwd: str,
        args: list[typing.Any] | None = None,
        log4j2: process.log4j2_base | None = None,
    ) -> None:
        self.args = [] if args is None else args
        self.java = _java.java_manager()
        self.info = sysinfo()
        self.log4j2 = log4j2
        self.cwd = cwd

    def search_java(self, dirs: collections.abc.Iterable[str] | None = None) -> None:
        """
        寻找Java,默认从环境变量中找
        """
        self.java.search(dirs)

    def launch(
        self, java: str | int | _java.java_info, eula: bool = False, output: bool = True
    ) -> process.popen:
        if isinstance(java, int):
            java = self.java.java[java][0]
        if isinstance(java, _java.java_info):
            java = java.path
        if eula:
            file = os.path.join(self.cwd, "eula.txt")
            with open(file, "w", encoding="utf-8") as fp:
                fp.write("eula=true")
        """
        启动服务端
        """
        return process.popen(
            [java, *self.args], self.cwd, output=output, log4j2=self.log4j2
        )
