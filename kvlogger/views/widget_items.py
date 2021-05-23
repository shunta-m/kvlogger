"""UIで使用するウィジットアイテム"""
import enum
from typing import List, Optional

import pandas as pd
from PySide6.QtCore import (QAbstractTableModel, QModelIndex, Qt,
                            Signal, Slot)
from PySide6.QtWidgets import (QAbstractScrollArea, QCheckBox, QFrame,
                               QListWidget, QListWidgetItem, QTableView,
                               QWidget)

from kvlogger.views import style


class CurveStatus(enum.Flag):
    """curve表示状態の列挙型

    VISIBLE: curve, region共に表示
    CURVE_ONLY: curveのみ表示
    INVISIBLE: curve, region共に非表示
    """

    VISIBLE = enum.auto()
    CURVE_ONLY = enum.auto()
    INVISIBLE = enum.auto()


class DataFrameModel(QAbstractTableModel):
    """pd.DataFrameをモデルにするTableModel

    Attributes
    ----------
    data_frame: pd.DataFrame
        モデルにするデータフレーム
    """

    def __init__(self, data_frame: pd.DataFrame, parent=None) -> None:
        """初期化処理

        Parameters
        ----------
        data_frame: pd.DataFrame
            モデルにするデータフレーム
        """

        self.data_frame: pd.DataFrame = data_frame
        super(DataFrameModel, self).__init__(parent)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        """列数を返す

        Returns
        ----------
        columnCount: int
            列数
        """

        return self.data_frame.shape[1]

    def data(self, index: QModelIndex, role: int = 0) -> Optional[str]:
        """ビューが指定している座標のデータを返す

        Parameters
        ----------
        index: QtCore.QModelIndex
            ビューが要求しているデータの座標
        role: int default=0
            要求しているデータ形式. 0でDisplayRole(文字列).
            表示中のデータを文字列で要求している.

        Returns
        ----------
        data: str
            ビューに要求されたデータ
        """

        if not index.isValid():
            return

        if role == 0:
            return str(self.data_frame.iloc[index.row(), index.column()])

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = 0) -> str:
        """sectionで指定したカラムインデックスの値を返す

        Parameters
        ----------
        section: int
            カラムインデックス
        orientation: QtCore.Qt.Orientation
            ヘッダーの向き
        role: int default=0
            要求しているデータ形式. 0でDisplayRole(文字列).
            表示中のデータを文字列で要求している.

        Returns
        -------
        headerData: str
            ヘッダー
        """

        if orientation == Qt.Orientation.Horizontal and role == 0:
            return str(self.data_frame.columns[section])

        if orientation == Qt.Orientation.Vertical and role == 0:
            return str(self.data_frame.index[section])

    def rowCount(self, parent: QModelIndex = ...) -> int:
        """行数を返す

        Returns
        ----------
        rowCount: int
            行数
        """

        return self.data_frame.shape[0]

    def reset_data(self, data: pd.DataFrame) -> None:
        """モデルを再定義する

        Parameters
        ----------
        data: pd.DataFrame
            新しくモデルにするデータフレーム
        """

        self.beginResetModel()
        self.data_frame = data.copy()
        self.endResetModel()


class DataFrameView(QTableView):
    """pd.DataFrameを見るTableView"""

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(DataFrameView, self).__init__(*args, **kwargs)
        self.setAlternatingRowColors(True)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def set_row_height(self, height: int = 70) -> None:
        """行の高さを変更する

        Parameters
        ----------
        height: int default=50
            高さ
        """

        v_header = self.verticalHeader()
        for v in range(v_header.count()):
            v_header.setDefaultSectionSize(height)


class LegendCheckBox(QCheckBox):
    """グラフ曲線のshow/hideを変更する為の凡例チェックボックス
    QtWidgets.QListWidgetに追加して使う

    Attributes
    ----------
    idx: int
        QListWidgetの何行目に追加したかを記憶
    """

    statusChanged = Signal(int, CurveStatus)

    def __init__(self, idx: int, color: str, *args, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        idx: int
            QListWidgetの何行目に追加したか
        color: str
            インジケーターの色表示
        """

        self.idx: int = idx
        self.color: str = color
        self.status: CurveStatus = CurveStatus.VISIBLE

        super(LegendCheckBox, self).__init__(*args, **kwargs)
        self.setStyleSheet(style.curve_check(color, self.status.value))
        self.stateChanged.connect(self.changed_check_color)

    @Slot()
    def changed_check_color(self) -> None:
        """チェックボックスの状態を判断して色を変える"""

        if self.status == CurveStatus.VISIBLE:
            self.status = CurveStatus.CURVE_ONLY
        elif self.status == CurveStatus.CURVE_ONLY:
            self.status = CurveStatus.INVISIBLE
        else:
            self.status = CurveStatus.VISIBLE

        self.emit_status_changed()

    def emit_status_changed(self) -> None:
        """statusChanged送信用"""

        self.setStyleSheet(style.curve_check(self.color, self.status.value))
        self.statusChanged.emit(self.idx, self.status)


class LegendListWidget(QListWidget):
    """グラフ曲線のshow/hideを変更するチェックボックスを格納するリストウィジット

    Attributes
    ----------
    check_list: List[LegendCheckBox]
        チェックボックス格納
    """

    checkStatusChanged = Signal(int, CurveStatus)

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        self.check_list: List[LegendCheckBox] = []

        super(LegendListWidget, self).__init__(*args, **kwargs)
        self.add_all_checkbox()

    def add_all_checkbox(self) -> None:
        """リスト内の全てのチェックボックスを操作するチェックボックスを追加"""

        self.add_checkbox(-1, '#000', 'all')

    def add_checkbox(self, idx: int, color: str, label: str) -> None:
        """LegendCheckBoxを追加する

        Parameters
        ----------
        idx: int
            チェックボックス番号
        color: str
            チェックボックスインジケーターの色
        label: str
            チェックボックスラベル
        """

        check: LegendCheckBox = LegendCheckBox(idx, color, label)
        item = QListWidgetItem()

        self.addItem(item)
        self.setItemWidget(item, check)

        self.check_list.append(check)
        check.statusChanged.connect(self.changed_status)

    def clear_checkbox(self) -> None:
        """リスト内のチェックボックスを消去する"""

        for check in self.check_list:
            check.statusChanged.disconnect(self.changed_status)

        self.clear()
        self.check_list.clear()

    @Slot(int, CurveStatus)
    def changed_status(self, idx: int, status: CurveStatus) -> None:
        """チェックボックスの状態が変わったとき、チャンネル番号を追加してcheckStateChangedを発火

        Parameters
        ----------
        idx: int
            チェックボックスの行番号
        status: CurveStatus
            curveの状態
        """

        if idx == -1:
            for check in self.check_list[1:]:
                check.status = status
                check.emit_status_changed()
        else:
            self.checkStatusChanged.emit(idx, status)


class SectionMeasureWidget(QWidget):
    """セクションごとの測定画面"""

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(SectionMeasureWidget, self).__init__(*args, **kwargs)
        

class StaticHLine(QFrame):
    """横線"""

    def __init__(self) -> None:
        super(StaticHLine, self).__init__()
        self.setFrameStyle(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

        self.setLineWidth(0)
        self.setMidLineWidth(1)


if __name__ == '__main__':
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = LegendListWidget()

    length = 5
    colors = style.curve_colors(length)
    colors_hex = list(map(style.rgb_to_hex, colors))

    for i in range(length):
        win.add_checkbox(i, colors_hex[i], f"test{i}")
    win.show()

    sys.exit(app.exec())
