"""
对RCON协议的支持
"""

__all__ = [
    "SERVERDATA_AUTH",
    "SERVERDATA_EXECCOMMAND",
    "SERVERDATA_AUTH_RESPONSE",
    "SERVERDATA_RESPONSE_VALUE",
    "read",
    "send_packet",
    "recv_packet",
    "rcon_client",
    "rcon_server",
]

import socket as _socket
import threading
import typing
import struct
import queue
import abc

SERVERDATA_AUTH = 3
SERVERDATA_EXECCOMMAND = 2
SERVERDATA_AUTH_RESPONSE = 2
SERVERDATA_RESPONSE_VALUE = 0


def read(socket: _socket.socket, length: int) -> bytes:
    data = b""
    while len(data) < length:
        chunk = socket.recv(length - len(data))
        if chunk == b"":
            raise ConnectionError
        data += chunk
    return data


def send_packet(socket: _socket.socket, req_id: int, p_type: int, body: str):
    data = body.encode("utf8") + b"\x00\x00"
    length = len(data) + 8
    packet = struct.pack("<iii", length, req_id, p_type) + data
    socket.sendall(packet)


def recv_packet(socket: _socket.socket) -> tuple[int, int, str]:
    length = struct.unpack("<i", read(socket, 4))[0]
    data = read(socket, length)
    req_id, p_type = struct.unpack("<ii", data[:8])
    body = data[8:-2].decode("utf-8")
    return req_id, p_type, body


class rcon_client:
    """
    RCON客户端
    """

    def __init__(
        self,
        server: str = "localhost",
        port: int = 25575,
        password: str = "",
        reconnect: int = 3,
    ) -> None:
        self.reconnect = reconnect
        self.password = password
        self.connecting = False
        self.server = server
        self.port = port
        self.lock = threading.Lock()
        self.socket = _socket.socket()
        self.event = threading.Event()
        self.thread = threading.Thread(target=self.recv_func, daemon=True)
        self.queue: queue.Queue[
            tuple[str, typing.Callable[[str], typing.Any] | None]
        ] = queue.Queue()
        self.socket.settimeout(5)
        self.thread.start()

    @property
    def ok(self) -> bool:
        """
        是否处于连接状态
        """
        try:
            timeout = self.socket.gettimeout()
            self.socket.settimeout(0)
            try:
                data = self.socket.recv(1, _socket.MSG_PEEK)
                return data != b""
            except BlockingIOError:
                return True
            finally:
                self.socket.settimeout(timeout)
        except:
            return False

    def __enter__(self) -> "rcon_client":
        self.ensure_connect()
        return self

    def __exit__(self, *_) -> None:
        try:
            self.disconnect()
        except:
            pass

    def connect(self) -> int | bool:
        """
        建立socket连接,成功时返回True
        """
        try:
            self.socket.connect((self.server, self.port))
        except OSError as e:
            ret = e.errno
            return -1 if ret is None else ret
        send_packet(self.socket, 0, SERVERDATA_AUTH, self.password)
        req_id, p_type, _ = recv_packet(self.socket)
        if p_type != SERVERDATA_AUTH_RESPONSE or req_id != 0:
            return -2
        return True

    def disconnect(self) -> None:
        """
        关闭socket连接
        """
        self.event.set()
        while not self.queue.empty():
            self.queue.get(False)
        self.socket.close()

    def ensure_connect(self) -> None:
        """
        确保处于连接状态
        """
        if self.ok or self.connecting:
            return
        self.connecting = True
        self.socket = _socket.socket()
        reconnect = self.reconnect
        ret = self.connect()
        while (not self.ok) and (reconnect != 0):
            if (ret := self.connect()) is True:
                break
            if reconnect > 0:
                reconnect -= 1
        if ret is not True:
            raise ConnectionError(ret)
        self.connecting = False

    def command(self, command: str) -> str:
        """
        发送命令
        """
        with self.lock:
            send_packet(self.socket, 0, SERVERDATA_EXECCOMMAND, command)
            return recv_packet(self.socket)[2]

    def command_call(
        self, command: str, func: typing.Callable[[str], typing.Any] | None = None
    ) -> None:
        """
        将函数添加进等待列表中,得到回复时调用函数
        """
        self.queue.put((command, func))

    def say(self, msg: str) -> None:
        """
        执行/say,并且能够处理换行
        """
        for line in msg.splitlines():
            # 处理单\n的行
            if line == "":
                line = " "
            self.command(f"say {line}")

    def recv_func(self) -> None:
        while not self.event.is_set():
            try:
                command, func = self.queue.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                ret = self.command(command)
            except Exception as error:
                ret = f"Python Error: {repr(error)}"
            if func:
                func(ret)


class rcon_server:
    """
    RCON服务端
    """

    def __init__(
        self,
        ip: str = "localhost",
        port: int = 25575,
        password: str = "",
    ) -> None:
        self.password = password
        self.address = (ip, port)
        self.socket = _socket.socket()
        self.event = threading.Event()
        self.thread = threading.Thread(target=self.main, daemon=True)

    def start(self) -> None:
        self.socket.bind(self.address)
        self.socket.listen(0)
        self.thread.start()

    def main(self) -> None:
        """
        服务端主逻辑
        """
        while True:
            threading.Thread(
                target=self.user, args=(self.socket.accept()[0],), daemon=True
            ).start()

    def user(self, user: _socket.socket) -> None:
        """
        与客户端通信
        """
        try:
            req_id, p_type, body = recv_packet(user)
            # 客户端首次必须登录
            assert p_type == SERVERDATA_AUTH
            ok = body == self.password
            # 密码匹配req_id原样返回,否则返回-1
            send_packet(user, req_id if ok else -1, SERVERDATA_AUTH_RESPONSE, "")
            assert ok
            while True:
                req_id, p_type, body = recv_packet(user)
                # 此时按理类型都为SERVERDATA_EXECCOMMAND
                if p_type != SERVERDATA_EXECCOMMAND:
                    continue
                try:
                    ret = self.command(body)
                except Exception as error:
                    ret = f"Python Error: {repr(error)}"
                send_packet(user, req_id, SERVERDATA_RESPONSE_VALUE, ret)
        except AssertionError:
            pass
        except (OSError, ConnectionError):
            # 捕捉连接类错误,跟着正常逻辑一块关闭socket
            pass
        user.close()

    @abc.abstractmethod
    def command(self, command: str) -> str:
        """
        执行命令
        """
        pass
