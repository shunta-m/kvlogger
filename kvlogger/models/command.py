"""keyenceに使用できるコマンド一蘭"""
import enum


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

    KV7500でDMを読む時, デフォルトは.U
    """

    U = '.U'
    S = '.S'
    D = '.D'
    L = '.L'
    H = '.H'


def make_read_command(d_type_no: str, d_format: DataFormat = DataFormat.U,
                      times: int = 1) -> str:
    """読み出しコマンド作成

    Parameters
    ----------
    d_type_no: str
        デバイス種別と番号. ex) DM1000
    d_format: DataFormat default=DataFormat.U
        データ形式
    times: int default=1
        読み出し回数

    Examples
    ----------
    DM1000からDM10004を読み出す
    >>> make_read_command('DM1000', times=5)
    'RDS DM1000.U 5\r'
    """

    if times == 1:
        return f"RD {d_type_no}{d_format}\r"
    return f"RDS {d_type_no}{d_format} {times}\r"


def make_timeset_command(yy: int, mm: int, dd: int,
                         HH: int, MM: int, SS: int,
                         week: int) -> str:
    """時間設定コマンド作成

    Parameters
    ----------
    yy: int
        西暦. 範囲は0~99. ex) 2021 = 21
    mm: int
        月. 範囲は1 ~ 12
    dd: int
        日付. 範囲は1 ~ 31
    HH: int
        時間. 範囲は0 ~ 23
    MM: int
        分. 範囲は0 ~ 60
    SS: int
        秒. 範囲は0 ~ 60
    week: int
        週. 範囲は0 ~ 6. 0が日曜で6が土曜

    Returns
    -------
    command: str
        日付設定コマンド
    """
    return f"WRT {yy:02} {mm:02} {dd:02} {HH:02} {MM:02} {SS:02} {week:01}\r"


if __name__ == '__main__':
    import doctest

    doctest.testmod()
