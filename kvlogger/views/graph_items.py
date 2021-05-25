"""UIで使用するグラフアイテム"""
import datetime as dt
from typing import Callable, Dict, List, Tuple

import numpy as np
from PySide6.QtGui import QColor
from PySide6.QtCore import Slot, Signal, QPointF
from PySide6.QtWidgets import QGraphicsWidget, QGraphicsGridLayout
import pyqtgraph as pg

from kvlogger.views import CurveStatus
from kvlogger.views import style


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
    idx: int
        整列番号
    color: Tuple[int, int, int, int]
        自身の色.
    """

    sigSentInfo: Signal = Signal(tuple)
    emit_num: int = 0
    nearest: List[float] = [1.0, 1.0]

    def __init__(self, idx: int, *args, **kwargs) -> None:
        """初期化処理


        Parameters
        ----------
        idx: int
            整列番号
        """

        self.idx: int = idx
        super(SortableCurve, self).__init__(*args, **kwargs)

        self.color: Tuple[int, int, int, int] = self.opts['pen'].color().getRgb()

    @Slot(int, QPointF)
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
            info: Tuple[str, tuple] = self.opts['name'], self.color

            idx_y: int = np.argmin(np.abs(coord.y() - self.yData))
            x_diff: float = np.min(np.abs(coord.x() - self.xData[idx_y]))

            idx_x: int = np.argmin(np.abs(coord.x() - self.xData))
            y_diff: float = np.min(np.abs(coord.y() - self.yData[idx_x]))

            if self.select_emitter(emit_num, x_diff, y_diff):
                self.sigSentInfo.emit(info)

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

    def set_data(self, values: np.ndarray) -> None:
        """測定値をグラフ表示する.

        Parameters
        ----------
        values: np.ndarray
            測定値
        """

        self.setData(values)


class RegionCurve(SortableCurve):
    """Region付curve"""

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        self.min_: float = 0
        self.max_: float = 0
        super(RegionCurve, self).__init__(*args, **kwargs)
        color: QColor = QColor(*self.color[:-1], a=32)
        self.region = pg.LinearRegionItem(orientation='horizontal',
                                          brush=pg.mkBrush(color),
                                          pen=pg.mkPen(color),
                                          movable=False)
        self.region.setRegion((0, 0))
        self.region.setZValue(10)

    def added(self, widget: pg.PlotItem) -> None:
        """自身とregionをwidgetに追加する

        Parameters
        ----------
        widget: pg.PlotItem
            追加するプロットアイテム
        """

        if self not in widget.items:
            widget.addItem(self, ignoreBounds=False)
        if self.region not in widget.items:
            widget.addItem(self.region, ignoreBounds=True)

    def reset_region(self) -> None:
        """regionをリセットする"""

        self.min_, self.max_ = min(self.yData), max(self.yData)
        self.region.setRegion((self.min_, self.max_))

    def removed(self, widget: pg.PlotItem) -> None:
        """自身とregionをwidgetから削除する

        Parameters
        ----------
        widget: pg.PlotItem
            curveとregionを削除するプロットアイテム
        """

        if self in widget.items:
            widget.removeItem(self)
            widget.removeItem(self.region)

    def set_data(self, values: np.ndarray) -> None:
        """測定値をグラフ表示する. regionの範囲を最大、最小値に合わせる

        Parameters
        ----------
        values: np.ndarray
            測定値
        """

        self.min_, self.max_ = np.min(values), np.max(values)

        self.setData(values)
        self.region.setRegion((self.min_, self.max_))

    def removed_region(self, widget: pg.PlotItem) -> None:
        """regionの表示 / 非表示切り替え

        Parameters
        ----------
        widget: pg.PlotItem
            regionを削除するプロットアイテム
        """

        if self.region in widget.items:
            widget.removeItem(self.region)
        if self not in widget.items:
            widget.addItem(self)

    def update_data(self, values: np.ndarray) -> None:
        """測定値を更新する

        Parameters
        ----------
        values: np.ndarray
            測定値
        """

        min_, max_ = min(values), max(values)
        self.min_ = min(self.min_, min_)
        self.max_ = max(self.max_, max_)

        self.setData(values)
        self.region.setRegion((self.min_, self.max_))


class CursorLabel(QGraphicsWidget):
    """マウスカーソル位置表示用ラベル

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

        super(CursorLabel, self).__init__(*args, **kwargs)
        self.curve_label = pg.LabelItem(justify='left')
        self.x_label = pg.LabelItem(justify='left')
        self.y_label = pg.LabelItem(justify='left')

        prefix_curve = pg.LabelItem(style.curve_cursor('Curve: '), justify='left')
        prefix_x = pg.LabelItem(style.curve_cursor('Time: '), justify='left')
        prefix_y = pg.LabelItem(style.curve_cursor(f"{y_label}:"), justify='left')

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

    @Slot(int, QPointF)
    def set_coord_text(self, _: int, coord: QPointF) -> None:
        """座標ラベル表示

        Parameters
        ----------
        _: int
            使わない
        coord: QtCore.QPointF
            マウス座標
        """

        self.x_label.setText(style.curve_cursor(TimeAxisItem.calc_time(coord.x())))
        self.y_label.setText(style.curve_cursor(f"{coord.y():.3e}"))

    @Slot(tuple)
    def set_curve_label(self, info: Tuple[str, tuple]) -> None:
        """curveラベル表示

        Parameters
        ----------
        info: Tuple[str, tuple]
            curve名と色
        """

        self.curve_label.setText(style.curve_cursor(info[0]), color=info[1])


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
    start_time: dt.datetime = dt.datetime.now()

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

        super().__init__(**kwargs)
        if self.format_ == 'date':
            self.setLabel(text='Time', units=None, **style.axis_label())
        elif self.format_ == 'elapsed':
            self.setLabel(text='Elapsed time', units='s', **style.axis_label())
        else:
            raise ValueError('format_は"date"か"elapsed"です')

        self.setTickFont(style.tick_font())

        self.enableAutoSIPrefix(False)
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

        def convert_elapsed(values: list) -> list:
            """経過時間列変換関数
            表示中の0点から最大値までの経過時間を作成する
            """

            array: np.ndarray = np.array(values) * self.interval
            return np.round(array, decimals=3).tolist()

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

    @classmethod
    def calc_time(cls, value: float) -> str:
        """その時点での時刻を計算する

        Parameters
        ----------
        value: float
            時刻を知りたいポイント

        Returns
        -------
        time: str
            時刻
        """

        elapsed: float = value * cls.interval
        time_point = cls.start_time + dt.timedelta(seconds=elapsed)
        return time_point.strftime('%y/%m/%d %H:%M:%S')

    @classmethod
    def update_start_time(cls) -> None:
        """測定開始時間を更新する"""

        cls.start_time = dt.datetime.now()


class MainPlot(pg.GraphicsLayoutWidget):
    """x軸が複数あるプロット

    Attributes
    ----------
    emit_no: int
        sigMouseMoved(pg.PlotItemのシグナル)を受け取ったタイミングを判別する変数.
    curves: Dict[int, RegionCurve]

    labels: CursorLabel
        マウスカーソル位置表示用ラベル
    plot: pg.PlotItem
        プロット
    """

    mouseMoved = Signal(int, QPointF)

    def __init__(self, ylabel: str, *args, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        ylabel: str
            y軸ラベル
        """

        self.emit_no = 0
        self.curves: Dict[int, RegionCurve] = {}
        super(MainPlot, self).__init__(*args, **kwargs)

        self.labels: CursorLabel = CursorLabel(ylabel)
        self.plot: pg.PlotItem = pg.PlotItem()
        yaxis: pg.AxisItem = self.plot.getAxis('left')
        yaxis.setTickFont(style.tick_font())
        yaxis.setLabel(text=ylabel, **style.axis_label())

        self.plot.showGrid(y=True, alpha=0.8)

        self.addItem(self.labels, 0, 0)
        self.addItem(self.plot, 1, 0)

        self.plot.setAxisItems({'bottom': TimeAxisItem('date', orientation='bottom')})
        sub_xaxis: TimeAxisItem = TimeAxisItem('elapsed', alpha=0,
                                               orientation='bottom', linkView=self.plot.vb)
        sub_xaxis.setZValue(-1000)
        self.plot.layout.addItem(sub_xaxis, 4, 1)
        self.plot.layout.setVerticalSpacing(10)

        self.mouseMoved.connect(self.labels.set_coord_text)
        self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved,
                                    rateLimit=60,
                                    slot=self.get_mouse_position)

    def add_curve(self, idx: int, color: tuple, name: str) -> None:
        """プロットするcurveを追加する

        Parameters
        ----------
        idx: int
            カーブ番号
        color: tuple
            (r, g, b)
        name: str
            curveの名前
        """

        curve: RegionCurve = RegionCurve(idx, name=name, pen=color)
        curve.sigSentInfo.connect(self.labels.set_curve_label)
        self.mouseMoved.connect(curve.send_info)
        curve.added(self.plot)
        self.curves[idx] = curve

    def get_mouse_position(self, event: Tuple[QPointF]) -> None:
        """

        Parameters
        ----------
        event: Tuple[QtCore.QPointF]
            画面のピクセル座標
        """

        self.emit_no += 1
        if self.emit_no == 128:
            self.emit_no = 0

        pos = event[0]
        if not self.plot.sceneBoundingRect().contains(pos):
            # posがplot内の座標ではなかったら終了
            return

        # グラフの座標取得
        # ex) coord=PyQt5.QtCore.QPointF(141.6549821809388, 4.725564511858496)
        coord = self.plot.vb.mapSceneToView(pos)
        self.mouseMoved.emit(self.emit_no, coord)

    @Slot(int, CurveStatus)
    def switch_curve_visible(self, idx: int, status: CurveStatus) -> None:
        """curveとregionの表示を切り替える

        Parameters
        ----------
        idx: int
            curve番号
        status: CurveStatus
            表示 / 非表示判定
        """

        if idx not in self.curves:
            raise ValueError('番号が存在していません')

        if status == CurveStatus.VISIBLE:
            self.curves[idx].added(self.plot)
        elif status == CurveStatus.CURVE_ONLY:
            self.curves[idx].removed_region(self.plot)
        elif status == CurveStatus.INVISIBLE:
            self.curves[idx].removed(self.plot)


if __name__ == '__main__':
    import sys

    from PySide6.QtWidgets import QApplication

    data = np.linspace(0, 100, 1001)

    app = QApplication(sys.argv)

    plot = MainPlot('test', ['test1', 'test2'])

    plot.curves[0].set_data(data)

    # plot.switch_curve_visible(0, False)
    # plot.curves[0].switch_region_visible(plot.plot, True)
    plot.curves[1].set_data(-1 * data)

    TimeAxisItem.calc_interval(1, 's')

    plot.show()
    sys.exit(app.exec())
