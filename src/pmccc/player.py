"""
玩家相关
"""

__all__ = ["player_base", "player_offline", "player_online"]

import json
import typing
import hashlib
import urllib.parse
import urllib.request
import uuid as _uuid


class player_base:
    """
    玩家基类
    """

    def __init__(self) -> None:
        self.name = "Dev"
        self.uuid = "0123456789abcdef0123456789abcdef"
        self.type = "Legacy"
        self.access_token: typing.Optional[str] = None

    def __str__(self) -> str:
        return f"[{self.name}] <{self.uuid}> ({self.type})"


class player_offline(player_base):
    """
    离线模式
    """

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    @property
    def uuid(self) -> str:
        return str(_uuid.UUID(bytes=hashlib.md5(f"OfflinePlayer:{self.name}".encode("utf-8")).digest()))


class player_online(player_base):
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

    def __init__(self, microsoft_refresh_token: typing.Optional[str] = None):
        self.access_token: typing.Optional[str] = None
        self.microsoft_refresh_token = microsoft_refresh_token
        self.profile: dict[str, typing.Any] = {}
        self.type = "msa"

    @property
    def name(self) -> str:
        return self.profile.get("name", "")

    @property
    def uuid(self) -> str:
        return self.profile.get("id", "")

    @property
    def ready(self) -> bool:
        """
        是否可以启动
        """
        return bool(self.name and self.uuid)

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
        response = urllib.request.Request("https://login.live.com/oauth20_token.srf", bytes(urllib.parse.urlencode({
            "client_id": "00000000402B5328",
            "scope": "service::user.auth.xboxlive.com::MBI_SSL",
            "code": code,
            "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
            "grant_type": "authorization_code"
        }), encoding="utf-8"))
        response = urllib.request.urlopen(response)
        data = json.loads(response.read().decode("utf-8"))
        microsoft_token = data["access_token"]
        microsoft_refresh_token = data["refresh_token"]
        return microsoft_token, microsoft_refresh_token

    def login_token_xbox_live(self, microsoft_token: str) -> str:
        """
        登录第三步,获取Xbox Live令牌
        """
        response = urllib.request.Request("https://user.auth.xboxlive.com/user/authenticate", json.dumps({
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": microsoft_token
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT"
        },).encode("utf-8"), headers={"Content-Type": "application/json"})
        response = urllib.request.urlopen(response)
        data = json.loads(response.read().decode("utf-8"))
        return data["Token"]

    def login_token_xsts(self, xbox_live_token: str) -> tuple[str, str]:
        """
        登录第四步,获取XSTS令牌
        """
        response = urllib.request.Request("https://xsts.auth.xboxlive.com/xsts/authorize", json.dumps({
            "Properties": {
                "SandboxId": "RETAIL",
                "UserTokens": [xbox_live_token]
            },
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT"
        }).encode("utf-8"), headers={"Content-Type": "application/json"})
        response = urllib.request.urlopen(response)
        data = json.loads(response.read().decode("utf-8"))
        return data["DisplayClaims"]["xui"][0]["uhs"], data["Token"]

    def login_token_minecraft(self, xsts_userhash: str, xsts_token: str) -> str:
        """
        登录第五步,获取Minecraft令牌
        """
        response = urllib.request.Request("https://api.minecraftservices.com/authentication/login_with_xbox", json.dumps({
            "identityToken": f"XBL3.0 x={xsts_userhash};{xsts_token}"
        },).encode("utf-8"), headers={"Content-Type": "application/json"})
        response = urllib.request.urlopen(response)
        data = json.loads(response.read().decode("utf-8"))
        return data["access_token"]

    def login_auto_init(self, url: str) -> str:
        """
        初始化自动登陆,先访问login_url获取返回的url,返回refresh_token
        """
        microsoft_token, microsoft_refresh_token = self.login_token_microsoft(
            url)
        xbox_live_token = self.login_token_xbox_live(microsoft_token)
        xsts_userhash, xsts_token = self.login_token_xsts(xbox_live_token)
        minecraft_token = self.login_token_minecraft(xsts_userhash, xsts_token)
        self.get_profile(minecraft_token)
        self.access_token = minecraft_token
        self.microsoft_refresh_token = microsoft_refresh_token
        return microsoft_refresh_token

    def login_auto(self, microsoft_refresh_token: typing.Optional[str] = None) -> bool:
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
        self.get_profile(minecraft_token)
        self.access_token = minecraft_token
        self.microsoft_refresh_token = microsoft_refresh_token
        return True

    def refresh_token(self, microsoft_refresh_token: str) -> str:
        """
        刷新Microsoft令牌
        """
        response = urllib.request.Request("https://login.live.com/oauth20_token.srf", bytes(urllib.parse.urlencode({
            "scope": "service::user.auth.xboxlive.com::MBI_SSL",
            "client_id": "00000000402B5328",
            "grant_type": "refresh_token",
            "refresh_token": microsoft_refresh_token
        }), encoding="utf-8"))
        response = urllib.request.urlopen(response)
        data = json.loads(response.read().decode("utf-8"))
        return data["access_token"]

    def get_profile(self, minecraft_token: str) -> dict[str, typing.Any]:
        """
        获取档案
        """
        response = urllib.request.Request("https://api.minecraftservices.com/minecraft/profile", headers={
            "Authorization": f"Bearer {minecraft_token}"
        })
        response = urllib.request.urlopen(response)
        data = json.loads(response.read().decode("utf-8"))
        self.profile = data
        return data

    def refresh_profile(self) -> bool:
        """
        刷新档案
        """
        self.profile = {} if self.access_token is None else self.get_profile(
            self.access_token)
        return self.ready
