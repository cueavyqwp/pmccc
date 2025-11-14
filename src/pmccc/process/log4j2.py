"""
log4j2相关
"""

from __future__ import annotations

__all__ = ["loginfo", "log4j2_base"]

import datetime
import typing
import abc
import os

from ..types import LOG_LEVEL_TYPE, LOG_LEVEL

if typing.TYPE_CHECKING:
    from .process import popen


class loginfo:
    """
    日志信息类
    """

    def __init__(self, text: str) -> None:
        """
        解析日志头
        """
        self.timestr, level, self.thread = text[1:-1].split("][")
        self.level = LOG_LEVEL.get(level.upper(), LOG_LEVEL_TYPE.INFO)
        self.time = datetime.datetime.strptime(self.timestr, "%Y/%m/%d %H:%M:%S")


class log4j2_base:
    """
    log4j2类

    你可以使用此类来解析log4j2日志
    """

    def __init__(
        self, config: str | None = None, info: type[loginfo] = loginfo
    ) -> None:
        self.config = (
            os.path.join(os.path.dirname(__file__), "log4j2.xml")
            if config is None or not os.path.isfile(config)
            else config
        )
        self.popen: popen | None = None
        self.info = info

    def is_output(self, text: str) -> bool:
        """
        是否是可输出的一行
        """
        return text != "\t\n"

    def split(self, line: str) -> tuple[loginfo, str]:
        """
        分割日志信息
        """
        head, text = line.split(": ", 1)
        return self.info(head), text

    def parse_call(self, text: str) -> None:
        """
        解析时调用
        """
        # 不让子类继承lines
        lines: list[str]
        if hasattr(self, "lines"):
            lines = getattr(self, "lines")
        else:
            lines = []
        if text == "\t\n":
            value = "".join(lines)
            self.parse(value)
            lines = []
        split = text.split(": ", 1)
        if len(split) >= 2 and split[0].startswith("[") and split[0].endswith("]"):
            lines = [text]
        elif lines:
            lines.append(text)
        setattr(self, "lines", lines)

    @abc.abstractmethod
    def parse(self, line: str) -> None:
        """
        可以通过覆写自定义解析
        """
        pass
