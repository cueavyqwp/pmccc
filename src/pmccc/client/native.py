"""
native相关处理
"""

__all__ = ["unzip", "unzip_all"]

import threading
import zipfile
import shutil
import os

from ..lib import verify
from ..lib import sysinfo
from ..lib import path as _path


def copy(zp: zipfile.ZipFile, zipinfo: zipfile.ZipInfo, to: str) -> None:
    """
    解压压缩包内文件
    """
    with zp.open(zipinfo) as fps:
        with open(to, "wb") as fpt:
            shutil.copyfileobj(fps, fpt)


def unzip(src: str, to: str, info: sysinfo | None = None) -> None:
    """
    解压到指定文件夹下
    """
    if info is None:
        info = sysinfo()
    _path.check_dir(to)
    sha1: dict[str, str] = {}
    native: dict[str, zipfile.ZipInfo] = {}
    with zipfile.ZipFile(src) as zp:
        for zipinfo in zp.filelist:
            name = os.path.basename(zipinfo.filename)
            if (
                ("32" in name or "86" in name) and "64" not in name
                if info.arch == "x86"
                else "32" not in name and ("86" not in name or "64" in name)
            ):
                suffix = os.path.splitext(name)[1]
                if not suffix:
                    continue
                suffix = suffix[1:]
                if suffix == "sha1":
                    with zp.open(zipinfo) as fp:
                        sha1[name[:-5]] = fp.readline().splitlines()[0].decode("utf-8")
                elif suffix == info.native:
                    native[name] = zipinfo
        threads: list[threading.Thread] = []
        for name, zipinfo in native.items():
            target = os.path.join(to, name)
            if (
                name in sha1
                and os.path.isfile(target)
                and verify.verify_file(target).check(sha1[name])
            ):
                continue
            threads.append(
                threading.Thread(target=copy, args=(zp, zipinfo, target), daemon=True)
            )
            threads[-1].start()
        for thread in threads:
            thread.join()


def unzip_all(src: list[str], to: str, info: sysinfo | None = None) -> None:
    """
    解压全部native
    """
    threads: list[threading.Thread] = []
    for file in src:
        threads.append(
            threading.Thread(target=unzip, args=(file, to, info), daemon=True)
        )
        threads[-1].start()
    for thread in threads:
        thread.join()
