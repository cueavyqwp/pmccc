"""
网络相关
"""

__all__ = ["download_item", "download_task"]

import threading
import os

from . import path as _path
from . import verify

import requests


class download_item:
    """
    下载项
    """

    def __init__(
        self,
        url: str,
        to: str,
        size: int = -1,
        hasher: str | verify.verify_hash | None = None,
    ) -> None:
        _path.check_dir(to)
        self.to = _path.format_abspath(to)
        self.hasher = verify.verify_hash(hasher) if isinstance(hasher, str) else hasher
        self.size = size
        self.url = url

    def __hash__(self) -> int:
        return verify.to_hash(self.to)

    @property
    def dirname(self) -> str:
        return os.path.dirname(self.to)


class download_task:
    """
    下载任务
    """

    def __init__(self, *items: download_item) -> None:
        self.item: dict[int, download_item] = {hash(item): item for item in items}
