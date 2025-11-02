"""
服务端启动类
"""

import typing
import os

from ..lib import java as _java
from ..lib import system
from .. import process


class launcher:

    def __init__(self, cwd: str, args: typing.Optional[list[typing.Any]] = None, log4j2: typing.Optional[process.log4j2] = None, ignore_parse_error: bool = False) -> None:
        self.ignore_parse_error = ignore_parse_error
        self.args = [] if args is None else args
        self.java = _java.java_manager()
        self.info = system.sysinfo()
        self.log4j2 = log4j2
        self.cwd = cwd

    def search_java(self, dirs: list[str] | None = None) -> None:
        """
        寻找Java,默认从环境变量中找
        """
        self.java.search(dirs)

    def launch(self, java: str | int | _java.java_info, eula: bool = False) -> process.popen:
        if isinstance(java, int):
            java = self.java.java[java][0]
        if isinstance(java, _java.java_info):
            java = java.path
        if eula:
            file = os.path.join(self.cwd, "eula.txt")
            with open(file, "w", encoding="utf-8") as fp:
                fp.write("eula=true")
        return process.popen(
            [java, *self.args],
            self.cwd,
            self.log4j2,
            self.ignore_parse_error
        )
