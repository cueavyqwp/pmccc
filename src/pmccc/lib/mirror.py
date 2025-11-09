"""
链接与镜像
"""

import urllib.parse

__all__ = ["mirror_base", "mirror_bmclapi"]


class mirror_base:
    """
    镜像基类
    """

    urls = {
        "version": "http://launchermeta.mojang.com/mc/game/version_manifest_v2.json",
        "version-unlisted": "https://zkitefly.github.io/unlisted-versions-of-minecraft/version_manifest.json",
        "assets": "https://resources.download.minecraft.net",
        "libraries": "https://libraries.minecraft.net",
        "maven": "https://maven.aliyun.com/repository/public",
        "forge": "https://files.minecraftforge.net/maven",
        "fabric": "https://maven.fabricmc.net",
        "fabric-meta": "https://meta.fabricmc.net",
        "neoforge-forge": "https://maven.neoforged.net/releases/net/neoforged/forge",
        "neoforge": "https://maven.neoforged.net/releases/net/neoforged/neoforge",
    }

    def parse(self, url: str) -> str:
        """
        解析url
        """
        return url


class mirror_bmclapi(mirror_base):
    """
    bmclapi镜像

    https://bmclapidoc.bangbang93.com
    """

    urls = {
        "version": "https://bmclapi2.bangbang93.com/mc/game/version_manifest_v2.json",
        "version-unlisted": "https://alist.8mi.tech/d/mirror/unlisted-versions-of-minecraft/Auto/version_manifest.json",
        "assets": "https://bmclapi2.bangbang93.com/assets",
        "libraries": "https://bmclapi2.bangbang93.com/maven",
        "maven": "https://bmclapi2.bangbang93.com/maven",
        "forge": "https://bmclapi2.bangbang93.com/maven",
        "fabric": "https://bmclapi2.bangbang93.com/maven",
        "fabric-meta": "https://bmclapi2.bangbang93.com/fabric-meta",
        "neoforge-forge": "https://bmclapi2.bangbang93.com/maven/net/neoforged/forge",
        "neoforge": "https://bmclapi2.bangbang93.com/maven/net/neoforged/neoforge",
    }

    def parse(self, url: str) -> str:
        ret = None
        parse = urllib.parse.urlparse(url)
        if parse.netloc in (
            "launchermeta.mojang.com",
            "launcher.mojang.com",
            "files.minecraftforge.net",
            "piston-data.mojang.com",
        ):
            ret = urllib.parse.urlunparse(
                parse._replace(netloc="bmclapi2.bangbang93.com")
            )
        elif parse.netloc == "resources.download.minecraft.net":
            ret = urllib.parse.urlunparse(
                parse._replace(
                    netloc="bmclapi2.bangbang93.com",
                    path="/assets" + parse.path,
                )
            )
        elif parse.netloc in (
            "libraries.minecraft.net",
            "maven.minecraftforge.net",
            "maven.fabricmc.net",
        ):
            ret = urllib.parse.urlunparse(
                parse._replace(
                    netloc="bmclapi2.bangbang93.com",
                    path="/maven" + parse.path,
                )
            )
        elif parse.netloc == "meta.fabricmc.net":
            ret = urllib.parse.urlunparse(
                parse._replace(
                    netloc="bmclapi2.bangbang93.com",
                    path="/fabric-meta" + parse.path,
                )
            )
        elif parse.netloc == "maven.neoforged.net":
            ret = urllib.parse.urlunparse(
                parse._replace(
                    netloc="bmclapi2.bangbang93.com",
                    path=parse.path.replace("/releases", "/maven"),
                )
            )
        elif parse.netloc == "zkitefly.github.io":
            ret = urllib.parse.urlunparse(
                parse._replace(
                    netloc="alist.8mi.tech",
                    path=f"/d/mirror/unlisted-versions-of-minecraft/Auto/{parse.path[32:]}",
                )
            )
        return url if ret is None else ret
