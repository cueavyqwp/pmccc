"""
玩家相关
"""

__all__ = [
    "player_base",
    "player_offline",
    "player_msa",
    "player_type",
    "player_manager",
]

import time
import typing
import hashlib
import urllib.parse
import uuid as _uuid

from ..lib import config
from ..lib.verify import to_hash

from ..types import SKIN_DEFAULT_TYPE, SKIN_ARM_TYPE, SKIN_DEFAULT, PmcccResponseError

import requests


class player_base(config.config_base):
    """
    玩家基类
    """

    def __init__(self) -> None:
        """
        注: 若需初始化,请覆写init而不是这里
        """
        self.name = "Dev"
        self.uuid = "0123456789abcdef0123456789abcdef"
        self.access_token = self.uuid
        self.manager_type = "custom"
        self.type = "Legacy"

    def init(self) -> None:
        """
        player_manager会调用此函数来进一步初始化
        """
        pass

    def __str__(self) -> str:
        return f"[{self.name}] <{self.uuid}> ({self.type})"

    def __hash__(self) -> int:
        return to_hash(str(self))

    def config_export(self) -> dict[str, typing.Any]:
        return {"type": self.manager_type, "name": self.name, "uuid": self.uuid}

    def config_loads(self, data: dict[str, typing.Any]) -> None:
        self.name = data["name"]
        self.access_token = self.uuid = data["uuid"]

    @property
    def ready(self) -> bool:
        """
        是否可以启动
        """
        return bool(self.name and self.uuid and self.access_token and self.type)

    def hashcode(self) -> int:
        """
        以Java中UUID.hashCode()的方式获取哈希值
        """
        bytes_data = _uuid.UUID(self.uuid).bytes
        # 提取mostSigBits和leastSigBits（Java是大端序）
        most_sig_bits = int.from_bytes(bytes_data[:8])
        least_sig_bits = int.from_bytes(bytes_data[8:])
        result = (
            (most_sig_bits >> 32)
            ^ most_sig_bits
            ^ (least_sig_bits >> 32)
            ^ least_sig_bits
        )
        # 转换为32位有符号整数
        result = result & 0xFFFFFFFF
        if result > 0x7FFFFFFF:
            result = result - 0x100000000
        return result

    def get_skin_default(self) -> tuple[SKIN_DEFAULT_TYPE, SKIN_ARM_TYPE]:
        """
        根据UUID获取默认皮肤以及手臂粗细
        """
        length = len(SKIN_DEFAULT)
        index = self.hashcode() % (length * 2)
        wide = False
        if index >= length:
            wide = True
        return SKIN_DEFAULT[index % 9], (
            SKIN_ARM_TYPE.WIDE if wide else SKIN_ARM_TYPE.SLIM
        )


class player_offline(player_base):
    """
    离线模式
    """

    def __init__(self, name: str = "Dev") -> None:
        """
        离线模式,uuid会自动计算

        name: 玩家名
        """
        self.name = name
        self.type = "Legacy"
        self.manager_type = "offline"
        self.uuid

    def config_export(self) -> dict[str, typing.Any]:
        return {"type": self.manager_type, "name": self.name}

    def config_loads(self, data: dict[str, typing.Any]) -> None:
        self.name = data["name"]

    @property
    def uuid(self) -> str:
        """
        将"OfflinePlayer:{玩家名}"的md5值转为uuid
        """
        md5_bytes = bytearray(
            hashlib.md5(f"OfflinePlayer:{self.name}".encode()).digest()
        )
        md5_bytes[6] = (md5_bytes[6] & 0x0F) | 0x30
        md5_bytes[8] = (md5_bytes[8] & 0x3F) | 0x80
        uuid_hex = md5_bytes.hex()
        self.access_token = f"{uuid_hex[:8]}-{uuid_hex[8:12]}-{uuid_hex[12:16]}-{uuid_hex[16:20]}-{uuid_hex[20:]}"
        return self.access_token


class player_msa(player_base):
    """
    微软登录

    ---

    使用`login_url`来获取登录链接

    除了刷新token,大部分token有效期只有一天

    刷新token若90天内没被使用就会失效

    ---

    参考

    [Mojang API之Microsoft身份认证](https://blog.goodboyboy.top/posts/2111486279.html)

    [dewycube/minecraft_token.py](https://gist.github.com/dewycube/223d4e9b3cddde932fbbb7cfcfb96759)

    """

    def __init__(self, microsoft_refresh_token: str | None = None, lastuse: int = -1):
        """
        微软登录

        microsoft_refresh_token: 微软账户刷新token

        lastuse: 上次刷新token使用时间
        """
        self.microsoft_refresh_token = microsoft_refresh_token
        self.access_token: str | None = None
        self.profile: dict[str, typing.Any] = {}
        self.lastuse = lastuse
        self.manager_type = "msa"
        self.type = "msa"

    def init(self) -> None:
        self.login_auto()

    def config_export(self) -> dict[str, typing.Any]:
        return {
            "type": self.manager_type,
            "refresh_token": self.microsoft_refresh_token,
            "lastuse": self.lastuse,
        }

    def config_loads(self, data: dict[str, typing.Any]) -> None:
        self.microsoft_refresh_token = str(data["refresh_token"])
        self.lastuse = int(data["lastuse"])

    @property
    def name(self) -> str:
        """
        玩家名
        """
        return self.profile.get("name", "")

    @property
    def uuid(self) -> str:
        """
        玩家uuid
        """
        return self.profile.get("id", "")

    def login_url(self) -> str:
        """
        登录第一步,获取Microsoft授权代码
        """
        return "https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&response_type=code&scope=service::user.auth.xboxlive.com::MBI_SSL"

    def login_token_microsoft(self, url: str) -> tuple[str, str]:
        """
        登录第二步,获取Microsoft令牌

        ---

        url: 第一步登录后跳转的地址
        """
        code = urllib.parse.urlparse(url).query.split("code=")[1].split("&")[0]
        response = requests.post(
            "https://login.live.com/oauth20_token.srf",
            data={
                "client_id": "00000000402B5328",
                "scope": "service::user.auth.xboxlive.com::MBI_SSL",
                "code": code,
                "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
                "grant_type": "authorization_code",
            },
        )
        if not response.ok:
            raise PmcccResponseError(response)
        data = response.json()
        microsoft_token = data["access_token"]
        microsoft_refresh_token = data["refresh_token"]
        return microsoft_token, microsoft_refresh_token

    def login_token_xbox_live(self, microsoft_token: str) -> str:
        """
        登录第三步,获取Xbox Live令牌
        """
        response = requests.post(
            "https://user.auth.xboxlive.com/user/authenticate",
            json={
                "Properties": {
                    "AuthMethod": "RPS",
                    "SiteName": "user.auth.xboxlive.com",
                    "RpsTicket": microsoft_token,
                },
                "RelyingParty": "http://auth.xboxlive.com",
                "TokenType": "JWT",
            },
        )
        if not response.ok:
            raise PmcccResponseError(response)
        data = response.json()
        return data["Token"]

    def login_token_xsts(self, xbox_live_token: str) -> tuple[str, str]:
        """
        登录第四步,获取XSTS令牌
        """
        response = requests.post(
            "https://xsts.auth.xboxlive.com/xsts/authorize",
            json={
                "Properties": {"SandboxId": "RETAIL", "UserTokens": [xbox_live_token]},
                "RelyingParty": "rp://api.minecraftservices.com/",
                "TokenType": "JWT",
            },
        )
        if not response.ok:
            raise PmcccResponseError(response)
        data = response.json()
        return data["DisplayClaims"]["xui"][0]["uhs"], data["Token"]

    def login_token_minecraft(self, xsts_userhash: str, xsts_token: str) -> str:
        """
        登录第五步,获取Minecraft令牌
        """
        response = requests.post(
            "https://api.minecraftservices.com/authentication/login_with_xbox",
            json={"identityToken": f"XBL3.0 x={xsts_userhash};{xsts_token}"},
        )
        if not response.ok:
            raise PmcccResponseError(response)
        data = response.json()
        return data["access_token"]

    def login_auto_init(self, url: str) -> str:
        """
        初始化自动登陆,先访问login_url获取返回的url,返回refresh_token
        """
        microsoft_token, microsoft_refresh_token = self.login_token_microsoft(url)
        self.lastuse = int(time.time())
        xbox_live_token = self.login_token_xbox_live(microsoft_token)
        xsts_userhash, xsts_token = self.login_token_xsts(xbox_live_token)
        minecraft_token = self.login_token_minecraft(xsts_userhash, xsts_token)
        self.access_token = minecraft_token
        self.microsoft_refresh_token = microsoft_refresh_token
        # 只要token能拿到就行,能不能更新档案不重要
        try:
            self.refresh_profile()
        except PmcccResponseError:
            pass
        return microsoft_refresh_token

    def login_auto(self, microsoft_refresh_token: str | None = None) -> bool:
        """
        自动登录
        """
        if microsoft_refresh_token is None:
            if self.microsoft_refresh_token is None:
                return False
            microsoft_refresh_token = self.microsoft_refresh_token
        microsoft_token = self.refresh_token(microsoft_refresh_token)
        xbox_live_token = self.login_token_xbox_live(microsoft_token)
        xsts_userhash, xsts_token = self.login_token_xsts(xbox_live_token)
        minecraft_token = self.login_token_minecraft(xsts_userhash, xsts_token)
        self.access_token = minecraft_token
        # 只要token能拿到就行,能不能更新档案不重要
        try:
            self.refresh_profile()
        except PmcccResponseError:
            pass
        return True

    def refresh_token(self, microsoft_refresh_token: str) -> str:
        """
        刷新Microsoft令牌
        """
        response = requests.post(
            "https://login.live.com/oauth20_token.srf",
            data={
                "scope": "service::user.auth.xboxlive.com::MBI_SSL",
                "client_id": "00000000402B5328",
                "grant_type": "refresh_token",
                "refresh_token": microsoft_refresh_token,
            },
        )
        if not response.ok:
            raise PmcccResponseError(response)
        self.lastuse = int(time.time())
        data = response.json()
        return data["access_token"]

    def get_profile(self, minecraft_token: str) -> dict[str, typing.Any]:
        """
        获取档案
        """
        response = requests.get(
            "https://api.minecraftservices.com/minecraft/profile",
            headers={"Authorization": f"Bearer {minecraft_token}"},
        )
        if not response.ok:
            raise PmcccResponseError(response)
        data = response.json()
        self.profile = data
        return data

    def refresh_profile(self) -> bool:
        """
        刷新档案
        """
        self.profile = (
            {} if self.access_token is None else self.get_profile(self.access_token)
        )
        return self.ready


class player_type:
    """
    玩家类型类
    """

    def __init__(self, **kwargs: type[player_base]) -> None:
        """
        玩家类型类

        键: 类型名

        值: player_base子类
        """
        self.types: dict[str, type[player_base]] = {
            "custom": player_base,
            "offline": player_offline,
            "msa": player_msa,
        }
        for key, types in kwargs.items():
            self.add_type(key, types)

    def add_type(self, type_name: str, types: type[player_base]) -> None:
        """
        添加玩家类型
        """
        self.types[type_name] = types

    def get_type(self, type_name: str) -> type[player_base]:
        """
        获取玩家类型
        """
        return self.types[type_name]


class player_manager(config.config_base):
    """
    玩家管理器
    """

    def __init__(
        self,
        types: player_type | None = None,
    ) -> None:
        """
        玩家管理器

        types: 玩家类型类
        """
        self.player: dict[int, player_base] = {}
        self.types = player_type() if types is None else types

    def __getitem__(self, index: int) -> player_base:
        return self.get_player(index)

    def __setitem__(
        self, types: str, args: tuple[typing.Any, ...] | list[typing.Any]
    ) -> None:
        self.add_player(types, *args)

    def __delitem__(self, index: int) -> None:
        self.remove_player(index)

    def config_export(self) -> dict[str, typing.Any]:
        return {str(key): value.config_export() for key, value in self.player.items()}

    def config_loads(self, data: dict[str, typing.Any]) -> None:
        for key, value in data.items():
            player = self.types.get_type(value["type"])()
            player.config_loads(value)
            player.init()
            self.player[int(key)] = player

    def add_player(self, types: str, *args: typing.Any, **kwargs: typing.Any) -> int:
        """
        添加玩家,返回其对应self.player的索引

        types: 玩家类型(manager_type)
        """
        player = self.types.get_type(types)(*args, **kwargs)
        player.init()
        index = hash(player)
        self.player[index] = player
        return index

    def get_player(self, index: int) -> player_base:
        """
        获取玩家
        """
        return self.player[index]

    def remove_player(self, index: int) -> None:
        """
        移除玩家
        """
        del self.player[index]

    def find_player_name(self, name: str, max_find: int = -1) -> list[player_base]:
        """
        通过玩家名寻找玩家
        """
        ret: list[player_base] = []
        for player in self.player.values():
            if max_find >= 0 and len(ret) >= max_find:
                break
            if player.name == name:
                ret.append(player)
        return ret

    def find_player_uuid(self, uuid: str, max_find: int = -1) -> list[player_base]:
        """
        通过uuid寻找玩家
        """
        ret: list[player_base] = []
        for player in self.player.values():
            if max_find >= 0 and len(ret) >= max_find:
                break
            if player.uuid == uuid:
                ret.append(player)
        return ret
