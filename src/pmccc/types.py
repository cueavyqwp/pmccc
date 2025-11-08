"""
pmccc自定义的类型
"""

__all__ = [
    "HASH_TYPE",
    "HASHER",
    "SKIN_DEFAULT_TYPE",
    "SKIN_ARM_TYPE",
    "SKIN_DEFAULT",
    "LOG_LEVEL_TYPE",
    "LOG_LEVEL",
    "PmcccException",
    "PmcccResponseError",
    "PmcccJavaNotFoundError",
]

import hashlib
import typing
import enum

import requests

# 校验相关


class HASH_TYPE(enum.Enum):
    SHA1 = 0
    SHA256 = 1
    SHA512 = 2
    MD5 = 3


HASHER = {
    HASH_TYPE.SHA1: hashlib.sha1,
    HASH_TYPE.SHA256: hashlib.sha256,
    HASH_TYPE.SHA512: hashlib.sha512,
    HASH_TYPE.MD5: hashlib.md5,
}

# 默认皮肤


class SKIN_DEFAULT_TYPE(enum.Enum):
    ALEX = 0
    ARI = 1
    EFE = 2
    KAI = 3
    MAKENA = 4
    NOOR = 5
    STEVE = 6
    SUNNY = 7
    ZURI = 8


class SKIN_ARM_TYPE(enum.Enum):
    WIDE = 0
    SLIM = 1


SKIN_DEFAULT = [
    SKIN_DEFAULT_TYPE.ALEX,
    SKIN_DEFAULT_TYPE.ARI,
    SKIN_DEFAULT_TYPE.EFE,
    SKIN_DEFAULT_TYPE.KAI,
    SKIN_DEFAULT_TYPE.MAKENA,
    SKIN_DEFAULT_TYPE.NOOR,
    SKIN_DEFAULT_TYPE.STEVE,
    SKIN_DEFAULT_TYPE.SUNNY,
    SKIN_DEFAULT_TYPE.ZURI,
]

# 日志等级


class LOG_LEVEL_TYPE(enum.Enum):
    OFF = 0
    FATAL = 1
    ERROR = 2
    WARN = 3
    INFO = 4
    DEBUG = 5
    TRACE = 6
    ALL = 7


LOG_LEVEL = {
    "OFF": LOG_LEVEL_TYPE.OFF,
    "FATAL": LOG_LEVEL_TYPE.FATAL,
    "ERROR": LOG_LEVEL_TYPE.ERROR,
    "WARN": LOG_LEVEL_TYPE.WARN,
    "INFO": LOG_LEVEL_TYPE.INFO,
    "DEBUG": LOG_LEVEL_TYPE.DEBUG,
    "TRACE": LOG_LEVEL_TYPE.TRACE,
    "ALL": LOG_LEVEL_TYPE.ALL,
}

# 网络请求Header
HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# 自定义异常


class PmcccException(Exception):
    """
    pmccc异常基类
    """

    def __init__(
        self, *args: tuple[typing.Any, ...], **kwargs: dict[str, typing.Any]
    ) -> None:
        """
        pmccc异常
        """
        super().__init__(*args, **kwargs)


class PmcccResponseError(PmcccException):
    """
    pmccc回应异常
    """

    def __init__(
        self,
        response: requests.Response,
        *args: tuple[typing.Any, ...],
        **kwargs: dict[str, typing.Any],
    ) -> None:
        self.response = response
        super().__init__(*args, **kwargs)


class PmcccJavaNotFoundError(PmcccException):
    """
    Java未找到异常
    """

    pass
