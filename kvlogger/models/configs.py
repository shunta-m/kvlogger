"""inifile読込"""
import configparser
from pathlib import Path
from typing import List, Tuple

CURRENT_DIR = Path(__file__).parent
CONFIG_FILE_PATH = str(CURRENT_DIR / r'config.ini')


class InitConfig:
    """コンフィグファイル情報保持"""

    def __init__(self, configfile: str = CONFIG_FILE_PATH) -> None:
        """初期化処理

        Parameters
        ----------
        configfile: str default=CONFIG_FILE_PATH
            コンフィグファイルパス
        """

        self.config = configparser.ConfigParser()
        self.config.read(configfile, encoding='utf-8')

    @property
    def all_items_name(self) -> List[str]:
        """測定パラメタの名前を返す"""

        items = [self.config.items(section) for section in self.measure_sections]
        return [col[0] for col in sum(items, []) if col[0] != 'unit']

    @property
    def demo(self) -> bool:
        """demoモード判別"""

        section: List[Tuple[str, str]] = self.config.items(self.sections[0])
        if section[0][1].upper() == 'TRUE':
            return True
        return False

    @property
    def measure_sections(self) -> List[str]:
        """測定に使用するセクションを返す"""

        return self.sections[2:]

    @property
    def sections(self) -> List[str]:
        """全てのセクションを返す"""

        return self.config.sections()

    @property
    def server(self) -> Tuple[str, int]:
        """IPアドレスとポート番号を返す"""

        section: List[Tuple[str, str]] = self.config.items(self.sections[1])
        return section[0][1], int(section[1][1])

    @property
    def unit(self) -> List[str]:
        """測定パラメタのユニットを返す"""

        items = [self.config.items(section) for section in self.measure_sections]
        return [col[1] for col in sum(items, []) if col[0] == 'unit']

    def get_section_items_name(self, section: str) -> List[str]:
        """指定したセクション内のアイテム名を返す

        Parameters
        ----------
        section: str
            セクション

        Returns
        ----------
        names: List[str]
            名前
        """

        items: List[Tuple[str, str]] = self.config.items(section)
        return [col[0] for col in items if col[0] != 'unit']

    def get_section_items_tn(self, section: str) -> List[str]:
        """指定したセクション内のtype noを返す

        Parameters
        ----------
        section: str
            セクション

        Returns
        ----------
        tn: Tuple[str]
            タイプと番号. ex) DM****
        """

        items: List[Tuple[str, str]] = self.config.items(section)
        return [col[1] for col in items if col[0] != 'unit']

    def get_measure_section_unit(self, section: str) -> str:
        """指定したセクション内のunitを返す

        Parameters
        ----------
        section: str
            セクション

        Returns
        ----------
        unit: str
            単位
        """

        return self.config[section]['unit']

# config = InitConfig()
# sections = config.measure_sections
# print(config.get_section_items_tn(sections[0]))
# print(config.get_section_items_name(sections[0]))
# print(config.get_measure_section_unit(sections[0]))
