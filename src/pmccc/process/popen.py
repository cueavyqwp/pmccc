"""
自定义Popen类
"""

__all__ = ["popen"]

import subprocess
import threading
import typing

from .log4j2 import log4j2 as _log4j2


class popen(subprocess.Popen[str]):
    """
    自定义Popen类
    """

    def __init__(self, args: list[typing.Any], cwd: typing.Optional[str] = None, log4j2: typing.Optional[_log4j2] = None, ignore_parse_error: bool = True) -> None:
        self.ignore_parse_error = ignore_parse_error
        self.log4j2 = log4j2
        if log4j2 is not None:
            args.insert(1, f"-Dlog4j.configurationFile={log4j2.config}")
        # 获取游戏所在目录
        if cwd is None:
            for index in range(len(args)):
                if args[index] == "--gameDir":
                    cwd = str(args[index+1])
                    break
        super().__init__(args, stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
                         stdout=subprocess.PIPE,  encoding="utf-8", text=True, cwd=cwd)
        self.parse_thread = threading.Thread(
            target=self.parse, daemon=True)
        self.parse_thread.start()

    def parse(self):
        """
        分出每行并调用log4j2类中的parse
        """
        if self.log4j2 is None:
            return
        line: list[str] = []
        for text in iter(self.stdout.readline, ""):  # type: ignore
            if self.log4j2.is_line(text):
                if line:
                    self.parse_call("".join(line))
                line = [text]
            elif line:
                line.append(text)
        if line:
            self.parse_call("".join(line))

    def parse_call(self, line: str) -> None:
        """
        调用log4j2类中的parse
        """
        if self.log4j2 is None:
            return
        try:
            self.log4j2.parse(line)
        except Exception as error:
            if not self.ignore_parse_error:
                raise error
