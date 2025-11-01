"""
log4j2相关
"""

__all__ = ["loginfo", "log4j2"]

import datetime
import typing
import os

from ..types import LOG_LEVEL_TYPE, LOG_LEVEL


class loginfo:

    def __init__(self, text: str) -> None:
        """
        解析日志信息
        """
        self.timestr, level, self.thread = text[1:-1].split("][")
        self.level = LOG_LEVEL.get(level, LOG_LEVEL_TYPE.INFO)
        self.time = datetime.datetime.strptime(
            self.timestr, "%Y/%m/%d %H:%M:%S")


class log4j2:

    def __init__(self, config: typing.Optional[str] = None, info: type[loginfo] = loginfo) -> None:
        self.config = os.path.join(os.path.dirname(
            __file__), "log4j2.xml") if config is None or not os.path.isfile(config) else config
        self.info = info

    def is_line(self, text: str) -> bool:
        """
        是否是新的一行
        """
        split = text.split(": ", 1)
        if len(split) < 2:
            return False
        return split[0].startswith("[") and split[0].endswith("]")

    def split(self, line: str) -> tuple[loginfo, str]:
        head, text = line.split(": ", 1)
        return self.info(head), text

    def parse(self, line: str) -> None:
        pass
