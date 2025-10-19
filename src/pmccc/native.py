"""
native相关处理
"""

__all__ = ["unzip", "clear", "unzip_all"]

import os
import typing
import shutil
import zipfile

from . import info as _info


def unzip(src: str, to: str, info: typing.Optional[_info] = None) -> None:
    """
    解压到指定文件夹下
    """
    if info is None:
        info = _info()
    if not os.path.isdir(to):
        os.makedirs(to)
    with zipfile.ZipFile(src) as zp:
        for zipinfo in zp.filelist:
            name = os.path.basename(zipinfo.filename)
            print(name)
            if name.endswith(info.native) and ((info.arch == "x64" and not ("32" in name or "86" in name)) or (info.arch == "x86" and "64" not in name and ("32" in name or "86" in name))):
                with zp.open(zipinfo) as fps:
                    with open(os.path.join(to, name), "wb") as fpt:
                        shutil.copyfileobj(fps, fpt)


def clear(src: str) -> None:
    """
    清理文件夹下所有文件
    """
    if os.path.isfile(src):
        return
    for name in os.listdir(src):
        path = os.path.join(src, name)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def unzip_all(src: list[str], to: str, info: typing.Optional[_info] = None) -> None:
    """
    解压全部native
    """
    for file in src:
        unzip(file, to, info)
