"""modelクラス"""
from kvlogger.models import configs, client


class Model:
    """ソフトの内部処理まとめ"""

    def __init__(self) -> None:
        """初期化処理"""

        self.config = configs.InitConfig()
        self.client = client.KVClient()
