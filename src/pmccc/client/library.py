"""
库文件数据
"""

__all__ = ["library_data"]

from urllib import parse as _parse
import typing
import os

from ..lib import mirror as _mirror
from ..lib import info as _info
from ..lib import download_item


from .namepath import name as _namepath


class library_data:

    def __init__(
        self, data: dict[str, typing.Any], info: _info.sysinfo | None = None
    ) -> None:
        self.info = _info.sysinfo() if info is None else info
        self.data = data
        self.name = _namepath(data["name"])
        if self.is_native():
            self.name.platform = data["natives"][self.info.os]

    def is_native(self) -> bool:
        """
        是否是native库
        """
        return "natives" in self.data

    def get_path(self, libraries: str | None = None) -> str:
        """
        获取jar路径

        libraries: libraries文件夹
        """
        if libraries is None:
            return self.name.get_path()
        return os.path.join(libraries, self.name.get_path())

    def get_download(
        self, libraries: str | None = None, mirror: _mirror.mirror_base | None = None
    ) -> download_item:
        if mirror is None:
            mirror = _mirror.mirror_base()
        data = self.data
        path = self.get_path()
        to = path if libraries is None else os.path.join(libraries, path)
        if self.is_native():
            if "downloads" in data:
                value = data["downloads"]["classifiers"][data["natives"][self.info.os]]
                return download_item(
                    mirror.parse(value["url"]),
                    value["size"],
                    value["sha1"],
                    to,
                )
            else:
                return download_item(
                    mirror.parse(
                        os.path.join(mirror.urls["libraries"], self.get_path())
                    ),
                    to=to,
                )
        else:
            name = data["name"]
            if "downloads" in data:
                value = data["downloads"]["artifact"]
                url = value["url"]
                # forge,你是怎么做到有哈希值和文件大小,url却为空的
                if not url:
                    if "minecraftforge" in name:
                        # forge的maven里找不到这个jar,但bmclapi却能找到
                        parse = _parse.urlparse("https://bmclapi2.bangbang93.com/maven")
                        url = mirror.parse(
                            _parse.urlunparse(
                                parse._replace(path=parse.path + f"/{path}")
                            )
                        )
                    else:
                        # 其它特例遇见再说
                        raise NotImplementedError
                return download_item(
                    mirror.parse(url),
                    value["size"] if "size" in value else -1,
                    value["sha1"] if "sha1" in value else None,
                    to,
                )
            elif "optifine" in name:
                # optifine官网下载链接无法直接拼接路径得到,写爬虫能实现,但是还是直接用镜像吧
                text = _namepath(name).version
                mcversion, _, _, patch = text.split("_")
                return download_item(
                    mirror.parse(
                        f"https://bmclapi2.bangbang93.com/optifine/{mcversion}/HD_U/{patch}"
                    ),
                    to=to,
                )
            elif "net.minecraft" in name:
                parse = _parse.urlparse(mirror.urls["libraries"])
                url = mirror.parse(
                    _parse.urlunparse(parse._replace(path=parse.path + f"/{path}"))
                )
                return download_item(url, to=to)
            elif "net.fabricmc" in name:
                # 给Fabric做兼容
                path = _namepath(name).get_path()
                parse = _parse.urlparse(mirror.urls["fabric"])
                url = mirror.parse(
                    _parse.urlunparse(parse._replace(path=parse.path + f"/{path}"))
                )
                return download_item(url, to=to)
            else:
                # 其余从其它maven仓库找
                path = _namepath(name).get_path()
                parse = _parse.urlparse(mirror.urls["maven"])
                url = mirror.parse(
                    _parse.urlunparse(parse._replace(path=parse.path + f"/{path}"))
                )
                return download_item(url, to=to)
