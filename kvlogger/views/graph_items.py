"""UIで使用するグラフアイテム"""
import datetime as dt
from typing import Callable, List, Tuple

import numpy as np
from PySide6.QtGui import QColor
from PySide6.QtCore import Slot, Signal, QPointF
from PySide6.QtWidgets import QApplication, QGraphicsWidget, QGraphicsGridLayout
import pyqtgraph as pg


class SortableCurve(pg.PlotDataItem):
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
            info: Tuple[str, QColor] = self.opts['name'], self.opts['pen'].color()

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


class PlotLabel(QGraphicsWidget):
    """プロットタイトル

    Attributes
    ----------
    curve_label: pg.LabelItem
        curve名表示ラベル
    x_label: pg.LabelItem
        x座標表示ラベル
    y_label: pg.LabelItem
        y座標表示ラベル
    """

    def __init__(self, y_label: str, *args, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        y_label: str
            y座標ラベル
        """

        super(PlotLabel, self).__init__(*args, **kwargs)
        self.curve_label = pg.LabelItem()
        self.x_label = pg.LabelItem()
        self.y_label = pg.LabelItem()

        prefix_curve = pg.LabelItem('Curve: ', justify='left')
        prefix_x = pg.LabelItem('Time: ', justify='left')
        prefix_y = pg.LabelItem(f"{y_label}", justify='left')

        layout = QGraphicsGridLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        layout.addItem(prefix_curve, 0, 0)
        layout.addItem(self.curve_label, 0, 1)
        layout.addItem(prefix_x, 0, 2)
        layout.addItem(self.x_label, 0, 3)
        layout.addItem(prefix_y, 0, 4)
        layout.addItem(self.y_label, 0, 5)

        self.setLayout(layout)

        layout.setColumnStretchFactor(1, 2)
        layout.setColumnStretchFactor(3, 1)
        layout.setColumnStretchFactor(5, 1)


class TimeAxisItem(pg.AxisItem):
    """時間軸

    Attributes
    ----------
    format_: str
        日付表示 or 経過時間表示
    start_time: dt.datetime
        初期時刻
    """

    interval: float = 1.0

    def __init__(self, format_: str, alpha: float = 0.8, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        format_: str
            表示する時刻形式. 'date' or 'elapsed'
        alpha: float default=0.8
            x軸のグリッド線の透明度. 0.0 - 1.0の間.
        """

        self.format_: str = format_
        self.start_time = dt.datetime.now()

        super().__init__(orientation='bottom', **kwargs)
        if self.format_ == 'date':
            self.setLabel(text='Time', units=None)
        elif self.format_ == 'elapsed':
            self.setLabel(text='Elapsed time', units='s')
        else:
            raise ValueError('format_は"date"か"elapsed"です')

        self.converter: Callable = self.select_converter()
        self.setGrid(alpha * 255)

    def select_converter(self) -> Callable:
        """x軸表示を時刻か経過時間か選択する

        Returns
        ----------
        converter: Callable
            x軸表示を変換する関数
        """

        def convert_date(values: list) -> List[str]:
            """時刻列変換関数"""

            def convert(value: float) -> str:
                date: dt.datetime = self.start_time + dt.timedelta(seconds=value * self.interval)
                return date.strftime('%y/%m/%d %H:%M:%S')

            return list(map(convert, values))

        def convert_elapsed(values: list) -> np.ndarray:
            """経過時間列変換関数
            表示中の0点から最大値までの経過時間を作成する
            """
            return np.array(values) * self.interval

        if self.format_ == 'date':
            return convert_date
        return convert_elapsed

    def tickStrings(self, values, scale, spacing):
        """override. x tick表示"""

        return self.converter(values)

    @classmethod
    def calc_interval(cls, value: float, unit: str) -> None:
        """x軸表示を時刻か経過時間か選択する

        Parameters
        ----------
        value: float
            測定間隔
        unit: str
            時間単位
        """

        if unit == 's':
            cls.interval = value
        elif unit == 'min':
            cls.interval = value * 60
        elif unit == 'h':
            cls.interval = value * 3600
        else:
            raise ValueError('intervalは"s", "min", "h"のどれかです')


class SamplePlot(pg.PlotItem):
    def __init__(self, *args, **kwargs) -> None:
        super(SamplePlot, self).__init__(*args, **kwargs)


if __name__ == '__main__':
    import sys

    data = np.linspace(0, 100, 30)

    app = QApplication(sys.argv)

    plot = SamplePlot(title='test')
    MainPlot = pg.PlotWidget(plotItem=plot)
    # win.addItem(plot)

    TimeAxisItem.calc_interval(60, 's')
    plot.setAxisItems({'bottom': TimeAxisItem('date')})
    AuxPlot = TimeAxisItem('elapsed', alpha=0, linkView=plot.vb)
    # MainPlot.showAxis('top')
    # MainPlot.scene().addItem(AuxPlot)
    # AuxPlot.setGeometry(MainPlot.getPlotItem().vb.sceneBoundingRect())
    # MainPlot.getAxis('top').linkToView(AuxPlot)
    # plot.scene().addItem(AuxPlot)
    # plot.showAxis('bottom')
    # AuxPlot.setGeometry(plot.vb.sceneBoundingRect())
    # AuxPlot.linkToView(plot.vb)
    # plot.axes['bottom'] = {"item": AuxPlot, "pos": [3, 1]}
    print(plot.layout)
    plot.layout.addItem(AuxPlot, 4, 1)
    plot.layout.setContentsMargins(1, 1, 1, 1)
    plot.layout.setVerticalSpacing(10)

    # plot.layout.setRowStretchFactor(1, 3)
    # plot.layout.setRowStretchFactor(2, 10)
    # plot.layout.setRowStretchFactor(3, 3)
    # plot.layout.setRowStretchFactor(4, 4)

    plot.plot(data)
    MainPlot.show()
    sys.exit(app.exec())
