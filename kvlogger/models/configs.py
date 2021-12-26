"""inifile読込"""
import configparser
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

CURRENT_DIR = Path(__file__).parent
CONNECT_CONFIG_FILE_PATH = str(CURRENT_DIR / r'config.ini')
DATA_CONFIG_FILE_PATH = str(CURRENT_DIR / r'config.csv')


class ConnectConfig:
    """コンフィグファイル情報保持
       demoモード, IPアドレス, ポート番号情報
    """

    def __init__(self, configfile: str = CONNECT_CONFIG_FILE_PATH) -> None:
        """初期化処理

        Parameters
        ----------
        configfile: str default=CONFIG_FILE_PATH
            コンフィグファイルパス
        """

        self.config = configparser.ConfigParser()
        self.config.read(configfile, encoding='utf-8')

    @property
    def demo(self) -> bool:
        """demoモード判別"""

        section: List[Tuple[str, str]] = self.config.items(self.sections[0])
        if section[0][1].upper() == 'TRUE':
            return True
        return False

    @property
    def sections(self) -> List[str]:
        """全てのセクションを返す"""

        return self.config.sections()

    @property
    def server(self) -> Tuple[str, int]:
        """IPアドレスとポート番号を返す"""

        section: List[Tuple[str, str]] = self.config.items(self.sections[1])
        return section[0][1], int(section[1][1])


class MeasureConfig:
    """測定データ設定値保持"""

    def __init__(self, config_csv: str = DATA_CONFIG_FILE_PATH) -> None:
        """初期化処理

        Parameters
        ----------
        config_csv: str default=DATA_CONFIG_FILE_PATH
            設定値保存ファイルのパス
        """

        self.measure_config: pd.DataFrame = pd.read_csv(config_csv, encoding='shift_jis', index_col=[0])

    @property
    def address_items(self) -> List[str]:
        """アドレス項目"""
        return self.measure_config.loc['address'].tolist()

    @property
    def format_items(self) -> List[str]:
        """データ形式項目"""
        return self.measure_config.loc['format'].tolist()

    @property
    def label_items(self) -> List[str]:
        """ラベル項目"""
        labels = self.measure_config.loc['label'].tolist()
        return sorted(set(labels), key=labels.index)

    @property
    def measure_name_items(self) -> List[str]:
        """測定項目"""
        return self.measure_config.columns.tolist()

    @property
    def label_measurement_items(self) -> Dict[str, List[str]]:
        """ラベルと測定項目の辞書
        {ラベル:[測定項目]}"""

        result = {}
        for label in self.label_items:
            bool_l: List[bool] = self.measure_config.loc['label'] == label
            result[label] = self.measure_config.columns[bool_l].tolist()
        return result


class Configs(ConnectConfig, MeasureConfig):
    def __init__(self) -> None:
        ConnectConfig.__init__(self)
        MeasureConfig.__init__(self)


if __name__ == '__main__':
    # connect_config = ConnectConfig()
    # measure_config = MeasureConfig()
    configs = Configs()
    print(configs.server)
    print(configs.format_items)
