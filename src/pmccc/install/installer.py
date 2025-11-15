"""
安装器类
"""

from __future__ import annotations

import typing
import json
import os

from ..lib import rules
from ..lib.info import sysinfo
from ..lib import path as _path
from ..lib import mirror as _mirror
from ..lib.network import download_item

from ..client.library import library_data

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
        libraries: str | None = None,
        info: sysinfo | None = None,
    ) -> list[download_item]:
        if info is None:
            info = sysinfo()
        ret: list[download_item] = []
        for item in version.data["libraries"]:
            if "rules" in item and not rules.check(item["rules"], info=info):
                continue
            lib = library_data(item, info)
            ret.append(lib.get_download(libraries, self.mirror))
        return ret

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
