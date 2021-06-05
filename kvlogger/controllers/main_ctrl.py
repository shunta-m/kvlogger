"""ソフトのメイン制御"""
from typing import List

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QApplication

from kvlogger.models import model
from kvlogger.views import (main_view, widget_items as wi)


class MainController:
    """メインコントローラ"""

    def __init__(self, app: QApplication) -> None:
        """初期化処理

        Parameters
        ----------
        app: QApplication
            イベント監視オブジェクト
        """

        self.app = app
        self.model = model.Model()
        self.view = main_view.MainWindow()
        # UIへアクセスする用のショートカット
        self.ui = self.view.ui

        # テーブルモデル作成
        table_model: wi.CurrentValueModel = wi.CurrentValueModel(self.model.config.all_items_name)
        self.ui.current_table.setModel(table_model)
        # tab
        for section in self.model.config.measure_sections:
            items: List[str] = self.model.config.get_section_items_name(section)
            unit: str = self.model.config.get_measure_section_unit(section)
            self.ui.add_tab(section, items, unit)

        self.connect_slot()

    def connect_slot(self) -> None:
        """uiイベントとスロット接続"""

    def start(self) -> None:
        """ソフト立上"""

        self.view.show()

