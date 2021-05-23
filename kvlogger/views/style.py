"""UIのスタイルを記載"""
from PySide6.QtGui import QFont


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
