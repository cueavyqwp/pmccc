"""
native相关处理
"""

__all__ = ["unzip", "unzip_all"]

import os
import typing
import shutil
import zipfile

from ..lib import system
from ..lib import path as _path


def unzip(src: str, to: str, info: typing.Optional[system.sysinfo_base] = None) -> None:
    """
    解压到指定文件夹下
    """
    if info is None:
        info = system.sysinfo_base()
    _path.check_dir(to)
    with zipfile.ZipFile(src) as zp:
        for zipinfo in zp.filelist:
            name = os.path.basename(zipinfo.filename)
            if name.endswith(info.native) and ("64" in name or "86" not in name or ("86" in name and "64" in name), "32" in name or ("86" in name and "64" not in name))[info.arch == "x86"]:
                with zp.open(zipinfo) as fps:
                    with open(os.path.join(to, name), "wb") as fpt:
                        shutil.copyfileobj(fps, fpt)


def unzip_all(src: list[str], to: str, info: typing.Optional[system.sysinfo_base] = None) -> None:
    """
    解压全部native
    """
    for file in src:
        unzip(file, to, info)
