"""
安装器类
"""

from __future__ import annotations

from urllib import parse as _parse
import typing
import json
import os

from ..lib import rules
from ..lib.info import sysinfo
from ..lib import path as _path
from ..lib import mirror as _mirror
from ..client import namepath as _name
from ..lib.network import download_item
from ..types import HEADER, PmcccResponseError

import requests

if typing.TYPE_CHECKING:
    from ..client import version_data


class installer:
    """
    安装器
    """

    def __init__(
        self, mirror: _mirror.mirror_base | None = None, header: dict[str, str] = HEADER
    ) -> None:
        self.mirror = _mirror.mirror_base() if mirror is None else mirror
        self.header = header

    def get_version_list(self, unlisted: bool = False) -> dict[str, typing.Any]:
        response = requests.get(
            self.mirror.urls["version-unlisted" if unlisted else "version"],
            headers=self.header,
        )
        if not response.ok:
            raise PmcccResponseError(response)
        return response.json()

    def get_version_json(
        self,
        url: str,
        to: str | None = None,
    ) -> dict[str, typing.Any]:
        response = requests.get(self.mirror.parse(url), headers=self.header)
        if not response.ok:
            raise PmcccResponseError(response)
        data = response.json()
        if to is not None:
            _path.check_dir(to, parent=True)
            with open(to, "w", encoding="utf-8") as fp:
                json.dump(data, fp, indent=4, ensure_ascii=False)
        return data

    def get_client(self, version: version_data) -> download_item:
        data = version.data["downloads"]["client"]
        return download_item(self.mirror.parse(data["url"]), data["size"], data["sha1"])

    def get_server(self, version: version_data) -> download_item:
        data = version.data["downloads"]["server"]
        return download_item(self.mirror.parse(data["url"]), data["size"], data["sha1"])

    def get_log4j2(self, version: version_data) -> download_item:
        data = version.data["logging"]["client"]["file"]
        return download_item(self.mirror.parse(data["url"]), data["size"], data["sha1"])

    def get_libraries(
        self,
        version: version_data,
        library: str | None = None,
        info: sysinfo | None = None,
    ) -> dict[str, download_item]:
        if info is None:
            info = sysinfo()
        libraries: dict[str, download_item] = {}
        data: list[dict[str, typing.Any]] = version.data["libraries"]
        for item in data:
            if "rules" in item and not rules.check(item["rules"], info=info):
                continue
            if "natives" in item:
                if info.os not in item["natives"]:
                    continue
                if "downloads" in item:
                    value = item["downloads"]["classifiers"][item["natives"][info.os]]
                    libraries[_name.get_path(item["name"])] = download_item(
                        self.mirror.parse(value["url"]), value["size"], value["sha1"]
                    )
                else:
                    split = _name.split(item["name"])
                    split[3] = item["natives"][info.os]
                    path = _name.to_path(*split)
                    libraries[path] = download_item(
                        self.mirror.parse(
                            os.path.join(self.mirror.urls["libraries"], path)
                        )
                    )
            else:
                name = item["name"]
                path = _name.get_path(name)
                if "downloads" in item:
                    value = item["downloads"]["artifact"]
                    url = value["url"]
                    # forge,你是怎么做到有哈希值和文件大小,url却为空的
                    if not url:
                        if "minecraftforge" in name:
                            # forge的maven里找不到这个jar,但bmclapi却能找到
                            parse = _parse.urlparse(
                                "https://bmclapi2.bangbang93.com/maven"
                            )
                            url = self.mirror.parse(
                                _parse.urlunparse(
                                    parse._replace(path=parse.path + f"/{path}")
                                )
                            )
                        else:
                            # 其它特例遇见再说
                            raise NotImplementedError
                    libraries[path] = download_item(
                        self.mirror.parse(url),
                        value["size"] if "size" in value else -1,
                        value["sha1"] if "sha1" in value else None,
                    )
                elif "optifine" in name:
                    # optifine官网下载需要看广告,虽然应该可以通过写爬虫来绕过,但是还是直接用镜像吧
                    text = _name.split(name)[2]
                    mcversion, _, _, patch = text.split("_")
                    libraries[path] = download_item(
                        self.mirror.parse(
                            f"https://bmclapi2.bangbang93.com/optifine/{mcversion}/HD_U/{patch}"
                        )
                    )
                elif "net.minecraft" in name:
                    parse = _parse.urlparse(self.mirror.urls["libraries"])
                    url = self.mirror.parse(
                        _parse.urlunparse(parse._replace(path=parse.path + f"/{path}"))
                    )
                    libraries[path] = download_item(url)
                elif "net.fabricmc" in name:
                    # 给Fabric做兼容
                    path = _name.get_path(name)
                    parse = _parse.urlparse(self.mirror.urls["fabric"])
                    url = self.mirror.parse(
                        _parse.urlunparse(parse._replace(path=parse.path + f"/{path}"))
                    )
                    libraries[path] = download_item(url)
                else:
                    # 其余从其它maven仓库找
                    path = _name.get_path(name)
                    parse = _parse.urlparse(self.mirror.urls["maven"])
                    url = self.mirror.parse(
                        _parse.urlunparse(parse._replace(path=parse.path + f"/{path}"))
                    )
                    libraries[path] = download_item(url)
        if library is not None:
            return {
                os.path.join(library, path): item for path, item in libraries.items()
            }
        return libraries

    def get_assets_index(
        self, version: version_data, assets: str | None = None
    ) -> dict[str, typing.Any]:
        if assets:
            to = os.path.join(assets, "indexes", version.data["assets"] + ".json")
            _path.check_dir(to, parent=True)
        else:
            to = None
        response = requests.get(
            self.mirror.parse(version.data["assetIndex"]["url"]), headers=self.header
        )
        if not response.ok:
            raise PmcccResponseError(response)
        data = response.json()
        if to is not None:
            with open(to, "w", encoding="utf-8") as fp:
                json.dump(data, fp, indent=4, ensure_ascii=False)
        return data

    def get_assets_object(
        self, index: str | dict[str, typing.Any], assets: str | None = None
    ) -> dict[str, download_item]:
        ret: dict[str, download_item] = {}
        if isinstance(index, str):
            with open(index, "r", encoding="utf-8") as fp:
                data = json.load(fp)
        else:
            data = index
        for path, value in data["objects"].items():
            file_hash: str = value["hash"]
            uri = os.path.join(file_hash[:2], file_hash)
            if assets is not None:
                path = os.path.join(assets, "objects", uri)
            ret[path] = download_item(
                self.mirror.urls["assets"] + f"/{uri}",
                value["size"],
                file_hash,
            )
        return ret


class installer_manager:
    """
    安装管理器
    """

    def __init__(self) -> None:
        pass
