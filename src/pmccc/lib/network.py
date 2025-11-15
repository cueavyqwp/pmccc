"""
网络相关
"""

__all__ = ["download_item", "download_task"]

import threading
import typing
import os

from . import path as _path
from . import verify

from .config import config_base

from ..types import HEADER, PmcccResponseError

import requests


class download_item:
    """
    下载项
    """

    def __init__(
        self,
        url: str,
        size: int = -1,
        hasher: str | verify.verify_hash | None = None,
        to: str | None = None,
    ) -> None:
        """
        下载项

        url: 链接

        name: 文件名

        size: 文件大小(Bytes),-1为未知大小

        hasher: verify_hash或哈希值字符串,为None不校验

        to: 目标地址,默认为空
        """
        self.hasher = verify.verify_hash(hasher) if isinstance(hasher, str) else hasher
        self.size = size
        self.url = url
        self.to = to


class download_task(config_base):
    """
    下载任务
    """

    def __init__(
        self,
        item: download_item,
        name: str = "",
        to: str | None = None,
        header: dict[str, str] = HEADER,
    ) -> None:
        if to is None:
            if item.to is None:
                raise ValueError
            else:
                to = item.to
        if name:
            to = os.path.join(to, name)
        self.to = _path.format_abspath(to)
        self.header = header
        self.item = item

    def __hash__(self) -> int:
        """
        这里哈希值用于索引,文件哈希在hasher那里
        """
        return verify.to_hash(self.to)

    def config_export(self) -> dict[str, typing.Any]:
        return {
            "hash": "" if self.item.hasher is None else self.item.hasher.value,
            "size": self.item.size,
            "url": self.item.url,
        }

    def config_save(self, path: str = "") -> None:
        super().config_save(path if path else self.infoname)

    def config_loads(self, data: dict[str, typing.Any]) -> None:
        hasher = data["hash"]
        if hasher:
            self.item.hasher = verify.verify_hash(hasher)
        else:
            self.item.hasher = None
        self.item.size = data["size"]
        self.item.url = data["url"]

    def config_load(self, path: str = "") -> None:
        super().config_load(path if path else self.infoname)

    @property
    def dirname(self) -> str:
        return os.path.dirname(self.to)

    @property
    def filename(self) -> str:
        return os.path.basename(self.to)

    @property
    def infoname(self) -> str:
        return self.to + ".download"

    def remove_split(self) -> None:
        os.remove(self.infoname)

    def download_thread(
        self, block_size: int = 4096, rewrite: bool = False
    ) -> threading.Thread:
        if not os.path.isdir(self.dirname):
            os.makedirs(self.dirname)
        if not rewrite and os.path.isfile(self.infoname):
            self.config_load()
        else:
            # 初次链接看能拿到啥文件信息
            response = requests.head(
                self.item.url, headers=self.header, allow_redirects=True
            )
            if not response.ok:
                raise PmcccResponseError(response)
            headers = response.headers
            self.split = (
                "Accept-Ranges" in headers and headers["Accept-Ranges"] == "bytes"
            )
            size = headers.get("Content-Length")
            if self.item.size <= 0 and size is not None:
                self.item.size = int(size)
            self.config_save()
        return threading.Thread(
            target=self.download_func, args=(block_size,), daemon=True
        )

    def download_func(self, block_size: int = 4096):
        block_size *= 1024
        response = requests.get(self.item.url, stream=True, headers=self.header)
        if not response.ok:
            raise PmcccResponseError(response)
        with open(self.to, "wb") as fp:
            for chunk in response.iter_content(block_size):
                fp.write(chunk)
                if self.item.hasher:
                    self.item.hasher.update(chunk)
        self.remove_split()

    def download(self, block_size: int = 4096, rewrite: bool = False) -> bool:
        thread = self.download_thread(block_size, rewrite)
        thread.start()
        thread.join()
        return self.check()

    def check(self) -> bool:
        if self.item.hasher is None:
            return True
        else:
            return self.item.hasher.check()
