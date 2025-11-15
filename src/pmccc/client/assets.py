"""
assets类
"""

__all__ = ["assets_data"]

import concurrent.futures
import typing
import shutil
import json
import os

from ..lib import path as _path


def copy(src: str, dst: str) -> None:
    _path.check_dir(dst, parent=True)
    shutil.copyfile(src, dst)


class assets_data:
    """
    assets信息
    """

    def __init__(self, index: str | dict[str, typing.Any], assets: str) -> None:
        if isinstance(index, str):
            if os.path.splitext(index)[1] != ".json":
                index = os.path.join(assets, "indexes", f"{index}.json")
            with open(index, "r", encoding="utf-8") as fp:
                self.index = json.load(fp)
        else:
            self.index = index
        self.assets = assets

    def copy_object(self, to: str) -> None:
        """
        复制object到目标文件夹
        """
        args: list[tuple[str, str]] = []
        for item in self.index["objects"].values():
            value: str = item["hash"]
            base = os.path.join(value[:2], value)
            args.append(
                (
                    os.path.join(self.assets, "objects", base),
                    os.path.join(to, base),
                )
            )
        with concurrent.futures.ThreadPoolExecutor(128) as thread:
            for value in args:  # pyright: ignore[reportAssignmentType]
                thread.submit(copy, *value)
