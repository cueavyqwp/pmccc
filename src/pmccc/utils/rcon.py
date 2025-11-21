"""
对MC服务端RCON协议的支持
"""

__all__ = [
    "SERVERDATA_AUTH",
    "SERVERDATA_EXECCOMMAND",
    "SERVERDATA_AUTH_RESPONSE",
    "SERVERDATA_RESPONSE_VALUE",
    "rcon_client",
]

import threading
import random
import typing
import socket
import struct
import time

SERVERDATA_AUTH = 3
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_AUTH_RESPONSE = 2
SERVERDATA_RESPONSE_VALUE = 0


class rcon_client:
    """
    RCON客户端
    """

    def __init__(
        self, server: str = "127.0.0.1", port: int = 25575, password: str = ""
    ) -> None:
        self.password = password
        self.server = server
        self.port = port
        self.lastsend = 0.0
        self.socket = socket.socket()
        self.thread = threading.Thread(target=self.recv_func, daemon=True)
        self.id: dict[int, typing.Callable[[str], typing.Any] | None] = {}

    def __enter__(self) -> "rcon_client":
        self.connect()
        if not self.login():
            raise ConnectionError
        return self

    def __exit__(self, *_) -> None:
        try:
            self.disconnect()
        except:
            pass

    def connect(
        self,
    ) -> None:
        """
        建立socket连接,执行后还需要login
        """
        self.socket.connect((self.server, self.port))

    def disconnect(self) -> None:
        """
        关闭socket连接
        """
        self.socket.close()

    def login(self) -> bool:
        """
        发送登录请求,返回登录是否成功
        """
        self.send_packet(0, SERVERDATA_AUTH, self.password)
        return self.recv_packet()[0] == 0

    def command(self, command: str, req_id: int = 0) -> str:
        """
        发送命令,无需指定请求ID,因此仅推荐在单线程时使用
        """
        self.send_packet(req_id, SERVERDATA_EXECCOMMAND, command)
        return self.recv_packet()[2]

    def command_call(
        self, command: str, func: typing.Callable[[str], typing.Any] | None = None
    ) -> int:
        """
        将函数添加进等待列表中,得到回复时调用函数
        """
        req_id: int | None = None
        while req_id is None or req_id in self.id:
            req_id = random.randint(0, 2147483647)
        wait = 0.001 - time.time() + self.lastsend
        if wait > 0:
            time.sleep(wait)
        self.send_packet(req_id, SERVERDATA_EXECCOMMAND, command)
        self.lastsend = time.time()
        self.id[req_id] = func
        return req_id

    def recv_thred(self) -> None:
        """
        启动接收线程
        """
        self.thread.start()

    def recv_func(self) -> None:
        while True:
            try:
                req_id, p_type, body = self.recv_packet()
            except socket.error:
                break
            if req_id not in self.id or p_type != SERVERDATA_RESPONSE_VALUE:
                continue
            func = self.id.pop(req_id)
            if func:
                func(body)

    def read(self, length: int) -> bytes:
        data = b""
        while len(data) < length:
            data += self.socket.recv(length - len(data))
        return data

    def send_packet(self, req_id: int, p_type: int, body: str):
        data = body.encode("utf8") + b"\x00\x00"
        length = len(data) + 8
        packet = struct.pack("<iii", length, req_id, p_type) + data
        self.socket.sendall(packet)

    def recv_packet(self) -> tuple[int, int, str]:
        length = struct.unpack("<i", self.read(4))[0]
        data = self.read(length)
        req_id, p_type = struct.unpack("<ii", data[:8])
        body = data[8:-2].decode()
        return req_id, p_type, body
