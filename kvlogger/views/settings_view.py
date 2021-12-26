"""設定画面view"""
from typing import List, Optional, Tuple
from pathlib import Path

from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from kvlogger.views import settings_view_ui as svu


class SettingsDialog(QDialog):
    """設定ダイアログ"""

    def __init__(self, units: List[str], ini_unit: str, *args, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        units: List[str]
            コンボボックスの単位
        ini_unit: str
            初期表示のコンボボックスインデックス
        """

        super(SettingsDialog, self).__init__(*args, **kwargs)
        self.ui = svu.SettingsUI()
        self.ui.setup_ui(self)

        self.ui.interval_unit_combo.addItems(units)
        self.ui.interval_unit_combo.setCurrentText(ini_unit)

        self.ui.open_btn.clicked.connect(self.select_save_dir)

        self.ui.btns.accepted.disconnect()
        self.ui.btns.accepted.connect(self.accept_)

    def accept_(self) -> None:
        """okボタンが押されたときの動作"""

        if self.ui.file_name_edit.text() == '':
            QMessageBox.warning(self, 'Warning', 'ファイル名を入力してください')
            return
        self.accept()

    def exec_dialog(self, save_dir: Path, interval: float, unit: int, data_points: int) -> Optional[tuple]:
        """ダイアログモーダル表示

        Parameters
        ----------
        save_dir: str
            保存先ディレクトリパス
        interval: tuple
            測定間隔. (value, unit)
        unit: int
            測定間隔の単位
        data_points: int
            ファイル保存点数

        Returns
        ----------
        save_dir: str
            保存先ディレクトリパス
        filename: str
            保存ファイル名
        interval: float
            測定間隔.
        unit: str
            測定間隔の単位
        data_points: int
            ファイル保存点数
        """

        self.ui.save_dir_edit.setText(str(save_dir))
        self.ui.interval_spin.setValue(interval)
        self.ui.interval_unit_combo.setCurrentText(unit)
        self.ui.save_point_spin.setValue(data_points)

        result = self.exec()

        if result == self.Accepted:
            save_dir: str = self.ui.save_dir_edit.text()
            filename: str = self.ui.file_name_edit.text()
            interval: float = self.ui.interval_spin.trend_value()
            unit: str = self.ui.interval_unit_combo.currentText()
            data_points: int = self.ui.save_point_spin.trend_value()

            return save_dir, filename, interval, unit, data_points

    def get_interval(self) -> Tuple[float, int]:
        """測定間隔を取得する"""

        return self.ui.interval_spin.trend_value(), self.ui.interval_unit_combo.currentIndex()

    def select_save_dir(self) -> None:
        """保存先フォルダを選択する"""

        selected_dir: str = QFileDialog.getExistingDirectory(self,
                                                             '保存フォルダを選択',
                                                             str(Path.cwd().parent))
        if selected_dir == '':
            return

        self.ui.save_dir_edit.setText(selected_dir)


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dia = SettingsDialog(['a', 'b', 'c'], 'a')
    dia.exec_dialog(Path.cwd(), 5, 1, 1000)
    sys.exit(app.exec())
