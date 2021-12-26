"""modelクラス"""
from kvlogger.models import (configs, client, settings)


class Model:
    """ソフトの内部処理まとめ"""

    def __init__(self) -> None:
        """初期化処理"""

        self.configs = configs.Configs()
        self.client = client.KVClient(self.configs.measure_name_items,
                                      self.configs.address_items,
                                      self.configs.format_items)
        self.settings = settings.Settings()
