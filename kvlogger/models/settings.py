"""測定設定保持"""
import dataclasses
import enum
from pathlib import Path
import re
from typing import Optional


class DirectoryExistsError(Exception):
    """ディレクトリが存在しなかったときの例外"""


class Unit(enum.Enum):
    """測定間隔単位"""
    MILLISECONDS = 'ms'
    SECONDS = 's'
    MINUTES = 'min'
    HOURS = 'h'


class Status(enum.Flag):
    """設定状態"""
    NOT_SET = 0
    SET = 0


@dataclasses.dataclass
class Settings:
    """測定設定保持クラス

    Attributes
    ----------
    _save_dir: Path default=Path().cwd().parent
        保存先フォルダ
    _filename: Optional[str] default=None
        保存ファイル名
    interval_value: float default=1.0
        測定間隔
    interval_unit: str default=Unit.SECONDS.value
        測定間隔の単位
    data_point: int default=10000
        ファイルに保存するデータ数
    status: Status default=Status.NOT_SET
        設定が完了したかのフラグ
    """

    _save_dir: Path = Path().cwd().parent
    _filename: Optional[str] = None
    interval_value: float = 1.0
    interval_unit: str = Unit.SECONDS.value
    data_point: int = 10000
    status: Status = dataclasses.field(default=Status.NOT_SET, init=False)

    @property
    def save_dir(self) -> Optional[Path]:
        """_save_dirゲッター"""

        return self._save_dir

    @save_dir.setter
    def save_dir(self, path: str) -> None:
        """self._save_dirセッター

        Parameters
        ----------
        path: str
            新保存先パス
        """

        save_dir = Path(path)
        if save_dir.exists():
            self._save_dir = save_dir
        else:
            raise DirectoryExistsError('ディレクトリが存在しません。\n(ディレクトリの最後にスペースがある場合、このエラーが発生します。)')

    @property
    def filename(self) -> Optional[str]:
        """_filenameゲッター"""

        return self._filename

    @filename.setter
    def filename(self, name: str) -> None:
        """self._filenameセッター

        Parameters
        ----------
        name: str
            新ファイル名
        """

        self._filename = regular_expression(name)

    def calc_interval(self) -> float:
        """測定間隔秒換算"""

        value: float = self.interval_value
        unit: str = self.interval_unit

        if Unit(unit) == Unit.MILLISECONDS:
            return value / 1000
        if Unit(unit) == Unit.SECONDS:
            return value
        if Unit(unit) == Unit.MINUTES:
            return value * 60
        else:
            return value * 3600

    def update(self, new_settings: tuple) -> None:
        """設定更新

        Parameters
        ----------
        new_settings: tuple
            新しい設定
        """

        self.filename = new_settings[1]
        self.interval_value = new_settings[2]
        self.interval_unit = new_settings[3]
        self.data_point = new_settings[4]

        # エラー発生の可能性がある為最後に入力
        self.save_dir = new_settings[0]


def regular_expression(text: str) -> str:
    """パス禁止文字を'-'に変える

    Parameters
    ----------
    text: str
        正規表現前の文字列

    Returns
    ----------
    regular_expression: str
        正規表現後の文字列
    """

    path_ng_pattern = re.compile(r'[\\|/|:|?|.|"|<|>|\|]')
    return path_ng_pattern.sub('-', text)
