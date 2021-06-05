"""keyence機器と通信するクライアント"""
import enum
import socket
from typing import Tuple

from kvlogger.models import command


class Status(enum.Flag):
    """機器接続状況"""

    NOT_CONNECTED = enum.auto()
    CONNECTED = enum.auto()
    ERROR = enum.auto()


class KVClient:
    """keyence機器と通信するクラス"""

    def __init__(self) -> None:
        """初期化処理"""

        self.status: Status = Status.NOT_CONNECTED
        # ip4, TCP使用
        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, address: Tuple[str, int], timeout: float = 2.0) -> None:
        """keyence機器と接続する

        Parameters
        ----------
        address: Tuple[str, int]
            IPアドレスとポート番号
        timeout: float default=10.0
            接続タイムアウト時間
        """

        self.client.settimeout(timeout)
        if self.status in Status.NOT_CONNECTED | Status.ERROR:
            try:
                self.client.connect_ex(address)
                self.status = Status.CONNECTED
            except socket.timeout as s_timeout:
                self.status = Status.NOT_CONNECTED
                self.disconnect()

                raise OSError('タイムアウトしました') from s_timeout

    def disconnect(self) -> None:
        """切断する"""

        self.client.close()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.status = Status.NOT_CONNECTED

    def get_device_name(self) -> str:
        """接続中のデバイス名取得"""

        message: str = command.StaticCommand.DEVICE
        self.client.send(message.encode('ascii'))

        return self.client.recv(64).decode('utf-8')

    def get_value(self, d_type_no: str, *args) -> float:
        """デバイス値取得

        Parameters
        ----------
        d_type_no: str
            デバイス種別と番号. ex) DM1000

        Returns
        -------
        response: float
            keyenceから取得した値
        """

        message: str = command.make_read_command(d_type_no, *args)
        self.client.send(message.encode('ascii'))

        response: str = self.client.recv(64).decode('utf-8')
        return float(response)
