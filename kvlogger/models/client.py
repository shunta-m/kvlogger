"""keyence機器と通信するクライアント"""
import enum
import socket
from struct import pack, unpack
from typing import Dict, List, Tuple, Union


class Status(enum.Flag):
    """機器接続状況"""

    NOT_CONNECTED = enum.auto()
    CONNECTED = enum.auto()
    ERROR = enum.auto()


class StrEnum(str, enum.Enum):
    """文字列と比較可能な列挙型"""


class StaticCommand(StrEnum):
    """KV7500使用可能な静的コマンド一蘭"""

    CLEAR_ERROR = 'ER\r'
    ERROR_NUM = '?E\r'
    DEVICE = '?K\r'


class DataFormat(StrEnum):
    """RD(読み出し), RDS(連続読み出し)に使用するデータ形式

    .U: 10進数16ビット符号なし
    .S: 10進数16ビット符号あり
    .D: 10進数32ビット符号なし
    .L: 10進数32ビット符号あり
    .H: 16進数16ビット
    """

    U = '.U'
    S = '.S'
    D = '.D'
    L = '.L'
    H = '.H'


def make_read_commands(address: List[str], fmts: List[str]) -> List[str]:
    """読み出しコマンド作成

    Parameters
    ----------
    address: List[str]
        アドレス項目. ex) ['DM1000', 'DM1010', ...]
    fmts: List[str]
        データ形式
        項目. ex) ['D', 'D', ...]
    """

    return [f"RD {address}.{fmt}\r" for address, fmt in zip(address, fmts)]


def convert_2word_to_double(value: int) -> float:
    """PLCから取得した数値を変換する
    32bit符号無し整数から符号あり浮動小数点数へ変更

    Parameters
    ----------
    value: int
        PLCから取得した値

    Returns
    -------
    result: float
        valueを変換した値

    """

    binary = pack('>L', value)
    return unpack('>f', binary)[0]


class KVClient:
    """keyence機器と通信するクラス

    Attributes
    -----
    client: socket.socket
        plcクライアント
    commands: List[str]
        plc読み出し時のコマンドのリスト. ex) ['RD DM1000.D\r', 'RD DM1010.D\r', ...]
    status: Status
        plc接続状況. 独自Enumクラス
    """

    def __init__(self, measure_name: List[str], address: List[str], fmts: List[str]) -> None:
        """初期化処理"""

        self.status: Status = Status.NOT_CONNECTED
        # ip4, TCP使用
        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.commands: Dict[str, str] = dict(zip(measure_name, make_read_commands(address, fmts)))

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
                self.client.connect(address)
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

        message: str = StaticCommand.DEVICE
        self.client.send(message.encode('ascii'))

        return self.client.recv(64).decode('utf-8')

    def get_plc_value(self) -> Dict[str, Union[int, float]]:
        """plcからデータを取得

        Returns
        -------
        result: Dict[str, Union[int, float]]
            全測定項目のデータを格納した辞書. キーは測項目名

        todo 接続が切れたときの処理がまだ
        """

        result: Dict[str, Union[int, float]] = {}
        for name, command in self.commands.items():
            self.client.send(command.encode('ascii'))
            response: Union[int, float] = int(self.client.recv(64).decode('utf-8'))
            if command[-3:] == '.D\r':
                response = convert_2word_to_double(response)
            result[name] = response

        return result


if __name__ == '__main__':
    test_name = [f"test{i}" for i in range(6)]
    test_address = [f"DM100{i}" for i in range(6)]
    test_fmts = ['D'] * 6
    c = KVClient(test_name, test_address, test_fmts)
    print(c.commands.items())
