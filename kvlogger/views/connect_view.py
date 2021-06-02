"""接続ボタン押下時に表示する画面"""
from PySide6.QtGui import QFont, QIntValidator, QValidator
from PySide6.QtWidgets import (QDialog, QFormLayout, QHBoxLayout,
                               QLabel, QLineEdit, QPushButton, QVBoxLayout)


class IP4Validator(QValidator):
    """IPアドレス用Validator
    https://stackoverflow.com/questions/53873737/pyqt5-qline-setinputmask-setvalidator-ip-address
    """

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(IP4Validator, self).__init__(*args, **kwargs)

    def validate(self, address, pos):
        if not address:
            return QValidator.Acceptable, pos
        octets = address.split(".")
        size = len(octets)
        if size > 4:
            return QValidator.Invalid, pos
        empty_octet = False
        for octet in octets:
            if not octet or octet == "___" or octet == "   ":  # check for mask symbols
                empty_octet = True
                continue
            try:
                value = int(str(octet).strip(' _'))  # strip mask symbols
            except:
                return QValidator.Intermediate, pos
            if value < 0 or value > 255:
                return QValidator.Invalid, pos
        if size < 4 or empty_octet:
            return QValidator.Intermediate, pos
        return QValidator.Acceptable, pos


class ConnectDialogUI:
    """接続画面UI"""

    def set_up(self, dialog: QDialog) -> None:
        """UIを設定する

        Parameters
        ----------
        dialog: QtWidgets.QDialog
            ウィジットを設置するダイアログ
        """

        font = QFont()
        font.setPointSize(10)
        dialog.setFont(font)

        dialog.setModal(True)

        self.make_widgets()
        self.make_layouts()
        self.set_layout(dialog)

    def make_widgets(self) -> None:
        """UI作成"""

        self.ip_edit = QLineEdit()
        self.ip_edit.setInputMask('000.000.000.000;_')
        self.ip_edit.setValidator(IP4Validator())

        self.port_edit = QLineEdit()
        self.port_edit.setValidator(QIntValidator())

        self.ok_btn = QPushButton('ok')
        self.cancel_btn = QPushButton('cancel')

    def make_layouts(self) -> None:
        """レイアウト作成"""

        self.main_lay = QVBoxLayout()
        self.form_lay = QFormLayout()
        self.btn_lay = QHBoxLayout()

    def set_layout(self, dialog: QDialog) -> None:
        """レイアウト設定"""

        dialog.setLayout(self.main_lay)
        self.main_lay.addWidget(QLabel('接続先'))
        self.main_lay.addLayout(self.form_lay)
        self.main_lay.addSpacing(10)
        self.main_lay.addLayout(self.btn_lay)

        self.form_lay.addRow('IP Address', self.ip_edit)
        self.form_lay.addRow('Port', self.port_edit)

        self.btn_lay.addWidget(self.ok_btn)
        self.btn_lay.addWidget(self.cancel_btn)


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    dia = QDialog()
    ui = ConnectDialogUI()
    ui.set_up(dia)
    dia.show()

    sys.exit(app.exec())
