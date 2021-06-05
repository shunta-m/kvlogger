"""設定画面view"""
from typing import Optional, Tuple

from PySide6.QtWidgets import QDialog

from kvlogger.views import settings_view_ui as svu


class SettingsDialog(QDialog):
    """設定ダイアログ"""

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(SettingsDialog, self).__init__(*args, **kwargs)
        self.ui = svu.SettingsUI()
        self.ui.setup_ui(self)

    def exec_dialog(self) -> Optional[Tuple[str, str, float, int]]:
        """ダイアログモーダル表示

        Returns
        ----------
        save_dir: str
            保存先ディレクトリパス
        filename: str
            保存ファイル名
        interval: float
            測定間隔
        data_points: int
            ファイル保存点数
        """

        result = self.exec()

        if result == self.Accepted:
            save_dir: str = self.ui.save_dir_edit.text()
            filename: str = self.ui.file_name_edit.text()
            interval: float = self.calc_interval()
            data_points: int = self.ui.data_point_spin.value()

            return save_dir, filename, interval, data_points

    def calc_interval(self) -> float:
        """測定間隔を計算する"""

        value: int = self.ui.interval_spin.value()
        unit: str = self.ui.interval_unit_combo.currentText()

        if unit == svu.Unit.MILLISECONDS.value:
            return value / 1000
        elif unit == svu.Unit.SECONDS.value:
            return value
        elif unit == svu.Unit.MINUTES.value:
            return value * 60
        else:
            return value * 3600


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dia = SettingsDialog()
    dia.exec_dialog()
    sys.exit(app.exec())
