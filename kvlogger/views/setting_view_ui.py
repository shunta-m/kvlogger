"""設定画面UI"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox,
                               QGridLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QSpinBox, QVBoxLayout)

from kvlogger.views import widget_items as wi


class SettingsUI:
    """設定画面UI"""

    def setup_ui(self, dialog: QDialog) -> None:
        """UIを設定する

        Parameters
        ----------
        dialog: QtWidgets.QDialog
            ウィジットを設置するダイアログ
        """

        dialog.setWindowTitle('設定')
        font = QFont()
        font.setPointSize(10)
        dialog.setFont(font)

        dialog.setModal(True)

        self.make_widgets(dialog)
        self.make_layouts()
        self.set_layout(dialog)

    def make_widgets(self, dialog: QDialog) -> None:
        """UI作成"""

        self.save_dir_edit = QLineEdit()
        self.file_name_edit = QLineEdit()

        self.open_btn = QPushButton('開く')

        self.interval_spin = QSpinBox()
        self.interval_spin.setMaximum(1000)
        self.interval_spin.setValue(1)

        self.interval_unit_combo = QComboBox()
        self.interval_unit_combo.addItems(['ms', 's', 'min', 'h'])
        self.interval_unit_combo.setCurrentIndex(1)

        self.data_point_spin = QSpinBox()
        self.data_point_spin.setMaximum(100000)
        self.data_point_spin.setValue(10000)

        self.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, dialog)
        self.btns.accepted.connect(dialog.accept)
        self.btns.rejected.connect(dialog.reject)

    def make_layouts(self) -> None:
        """レイアウト作成"""

        self.main_lay = QVBoxLayout()

        self.grid_lay = QGridLayout()
        self.interval_lay = QHBoxLayout()

    def set_layout(self, dialog: QDialog) -> None:
        """レイアウト設定"""

        dialog.setLayout(self.main_lay)

        self.main_lay.addLayout(self.grid_lay)
        self.main_lay.addSpacing(10)
        self.main_lay.addWidget(wi.StaticHLine())
        self.main_lay.addWidget(self.btns)
        self.main_lay.addStretch()

        self.grid_lay.addWidget(QLabel('保存フォルダ'), 0, 0)
        self.grid_lay.addWidget(self.save_dir_edit, 0, 1)
        self.grid_lay.addWidget(self.open_btn, 0, 2)
        self.grid_lay.addWidget(QLabel('保存ファイル名'), 1, 0)
        self.grid_lay.addWidget(self.file_name_edit, 1, 1)
        self.grid_lay.addWidget(QLabel('測定間隔'), 2, 0)
        self.grid_lay.addLayout(self.interval_lay, 2, 1, alignment=Qt.AlignLeft)
        self.grid_lay.addWidget(QLabel('ファイル保存点数'), 3, 0)
        self.grid_lay.addWidget(self.data_point_spin, 3, 1, alignment=Qt.AlignLeft)

        self.interval_lay.addWidget(self.interval_spin)
        self.interval_lay.addWidget(self.interval_unit_combo)


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    dia = QDialog()
    ui = SettingsUI()
    ui.setup_ui(dia)
    dia.show()

    sys.exit(app.exec())
