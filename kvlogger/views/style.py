"""UIのスタイルを記載"""
from colour import Color
import numpy as np
from PySide6.QtGui import QFont


def curve_colors(num: int, start: str = '#f00', end: str = '#00f') -> np.ndarray:
    """curveの色を作成

    Parameters
    ----------
    num: int
        色を作成する数
    start: str default='#f00'
        最初の色
    end: str default='#00f'
        最後の色

    Returns
    ----------
    colors: np.ndarray
        色. [(r, g, b), (r, g, b), ...]
    """

    start_c: Color = Color(start)
    end_c: Color = Color(end)
    return np.array([color.get_rgb() for color in start_c.range_to(end_c, num)]) * 255


def tag(name: str, fontsize: int):
    """タグ装飾用デコレータ

    Parameters
    ----------
    name: str
        タグの名前
    fontsize: int
        フォントサイズ
    """

    def _tag(f):
        def _wrapper(text: str):
            start_tag = f"<{name} style='font-size:{fontsize}px'>"
            body = f(text)
            end_tag = f"</{name}>"

            return start_tag + body + end_tag

        return _wrapper

    return _tag


@tag('div', 16)  # 第2引数(25の部分)を変更すると文字サイズが変わる
def curve_cursor(text) -> str:
    return text


def axis_label(color: str = '#969696', size: int = 12) -> dict:
    return {'color': color, 'font-size': f"{size}pt"}


def tick_font(size: int = 10) -> QFont:
    font = QFont()
    font.setPointSize(size)
    return font
