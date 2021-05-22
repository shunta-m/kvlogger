"""UIで使用するグラフアイテム"""
from typing import List, Tuple

import numpy as np
from PySide6 import QtGui
from PySide6.QtCore import Slot, Signal, QPointF

import pyqtgraph as pg


class SortableCurve(pg.PlotCurveItem):
    """並べ替え可能なpg.PlotCurveItem

    sigSentInfo: Signal
        自身の情報(名前, 色)を送信するシグナル
    emit_num: int
        sigMouseMoved(pg.PlotItemのシグナル)を受け取ったタイミングを判別する変数.
    nearest: List[float] = [1.0, 1.0]
        sigMouseMovedを受け取ったとき、どのcurveが一番近いか判別するリスト

    Attributes
    ----------
    num: int
        整列番号
    """

    sigSentInfo: Signal = Signal(tuple)
    emit_num: int = 0
    nearest: List[float] = [1.0, 1.0]

    def __init__(self, number: int, *args, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        number: int
            整列番号
        """

        self.number: int = number
        super(SortableCurve, self).__init__(*args, **kwargs)

    @Slot(int, QPointF, result=None)
    def send_info(self, emit_num: int, coord: QPointF) -> None:
        """

        Parameters
        ----------
        emit_num: int
            同じタイミングのsigMouseMovedシグナルかどうかを調べる数字
        coord: QPointF
            マウスカーソルがあるグラフ座標
        """

        if self.mouseShape().contains(coord):
            info: Tuple[str, QtGui.QColor] = self.opts['name'], self.opts['pen'].color()

            idx_y: int = np.argmin(np.abs(coord.y() - self.yData))
            x_diff: float = np.min(np.abs(coord.x() - self.xData[idx_y]))

            idx_x: int = np.argmin(np.abs(coord.x() - self.xData))
            y_diff: float = np.min(np.abs(coord.y() - self.yData[idx_x]))

            if self.select_emitter(emit_num, x_diff, y_diff):
                self.sigSendInfo.emit(info)

    @classmethod
    def select_emitter(cls, emit_num: int, x_diff: float, y_diff: float) -> bool:
        """どのcurveのsigSentInfoシグナルを発火するかを決める.
        マウスカーソルが一番近いcurveを調べてsigSendInfoを発火する.

        Parameters
        ----------
        emit_num: int
            同じタイミングのsigMouseMovedシグナルかどうかを調べる数字
        x_diff: float
            マウスカーソルの座標とその座標のcurveのx値の差分
        y_diff: float
            マウスカーソルの座標とその座標のcurveのy値の差分

        Returns
        -------
        result: bool
            sigSentInfoを送信するかの結果
        """

        if cls.emit_num != emit_num:
            cls.emit_num = emit_num
            cls.nearest = [1.0, 1.0]

        result: bool = False

        if cls.nearest[0] > x_diff:
            cls.nearest[0] = x_diff
            result = True

        if cls.nearest[1] > y_diff:
            cls.nearest[1] = y_diff
            result = True
        return result