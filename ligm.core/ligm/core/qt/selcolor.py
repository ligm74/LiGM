#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Widget for select a color."""

from PyQt5.Qt import (Qt, QPoint, QToolButton, QAction, QGridLayout,
                      QVBoxLayout, QPen, QColor, QIcon, QPainter, QLabel,
                      QFrame, QHBoxLayout, pyqtSignal, QColorDialog,
                      QApplication)
from ligm.core.common import img
from ligm.core.qt import TestableWidget


# =============================================================================
class ColorPicker(QToolButton):
    """Widget for select a color."""

    select_color = pyqtSignal(str)

    def __init__(self, text=None, color_caption="#F0F0FF",
                 icon="", config=None):
        """
        text - text in caption and tooltip
        icon - filename for icon of button
        list_colors - list colors for select
        """
        QToolButton.__init__(self, None)
        self.setAutoRaise(True)

        self._text = self.tr("Color") if text is None else text
        self._color_caption = color_caption

        # --- list of colors -----------------------------------
        lst = []
        if config:
            lst = [
                c for c in config.get("TextEditor/Colors", "").split(";") if c]

        if not lst:
            lst = [
                "#99cc00", "#e2fbfe", "#fee5e2", "#fa8072", "#f5f7a8",
                "#fef65b", "#ff9a00", "#ff00f4", "#f6f900", "#914285",
                "#c0d6e4", "#f5f5dc", "#3d40a2", "#acd2cd", "#ff9966",
                "#a4c73c", "#ff7373", "#50d4ee", "#8d5959", "#104022",
                "#000000", "#160042", "#6e57d2", "#4c9828", "#444193",
                "#0000ff", "#ff0000", "white", "#AA0000", "#00AA00",
                "#0040C2", "#550000", "#004100", "#BF4040"]
        if config:
            config["TextEditor/Colors"] = ";".join(lst)

        lst.append(color_caption)  # the list must contain a background color
        self._colors = lst
        # ------------------------------------------------------

        self._colors_widget = ColorsWidget(text=self._text,
                                           colors=self._colors,
                                           color_caption=color_caption)
        self._colors_widget.select_color.connect(self.select_color_)
        self._colors_widget.hide_form.connect(self.hide_color_form)
        self._colors_widget.other_color.connect(self.other_color)

        self._action = QAction(self._text, None)
        self._action.setIcon(QIcon(img(icon)))
        self._action.triggered.connect(self.show_form_colors)

        self.setDefaultAction(self._action)

    # -------------------------------------------------------------------------
    def show_form_colors(self):
        self.setCheckable(True)
        self.setChecked(True)
        QApplication.processEvents()
        pos = QPoint(self.rect().left(), self.rect().bottom())
        self._colors_widget.show_form(self.mapToGlobal(pos))

    # -------------------------------------------------------------------------
    def select_color_(self, color):
        self.select_color.emit(color)

    # -------------------------------------------------------------------------
    def _get_color(self):  # pragma: no cover
        """
        The method is made to bypass the program crashes during testing
        in Ubuntu. Tests terminated if QColorDialog used in other_color.

        For use in tests (obj is object of ColorPicker):
          with patch.object(obj, '_get_color', return_value=QColor("blue")):
        """
        return QColorDialog(self).getColor(initial=QColor("black"))

    # -------------------------------------------------------------------------
    def other_color(self):
        color = self._get_color()
        QApplication.processEvents()
        if color.isValid():
            self.select_color.emit(color.name())

    # -------------------------------------------------------------------------
    def hide_color_form(self):
        self.setCheckable(False)

    # -------------------------------------------------------------------------
    def retranslate_ui(self, text):
        self._text = self.tr("Color") if text is None else text
        self._colors_widget.retranslate_ui(self._text)
        self.setToolTip(self._text)


# =============================================================================
class ColorsWidget(TestableWidget):

    select_color = pyqtSignal(str)
    hide_form = pyqtSignal()
    other_color = pyqtSignal()

    # -------------------------------------------------------------------------
    def __init__(self, text, colors, color_caption):
        TestableWidget.__init__(self)
        self.setWindowFlags(Qt.Popup)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        border = "border: 1px solid #9b9b9b;"
        self.setStyleSheet('QFrame[frameShape="4"]{  color: #9b9b9b;}')

        # -- CAPTION ----------------------------------
        caption = QFrame(self, flags=Qt.WindowFlags())
        caption_layout = QHBoxLayout()
        self._lbl_caption = QLabel(text)
        self._lbl_caption.setStyleSheet("border: 0px solid blue;")
        caption_layout.addWidget(self._lbl_caption, alignment=Qt.Alignment())
        caption.setLayout(caption_layout)
        caption_layout.setContentsMargins(9, 5, 9, 5)
        caption.setStyleSheet(f"background-color: {color_caption}; {border}")

        # -- COLORS GRID ------------------------------
        colorbox = QFrame(self, flags=Qt.WindowFlags())
        color_layout = QGridLayout()
        colorbox.setLayout(color_layout)
        color_layout.setContentsMargins(9, 0, 9, 0)
        nn = 7
        self.clrbtn = []
        for i, color in enumerate(colors):
            self.clrbtn.append(QToolButton())
            css = (f"QToolButton {{{border}background-color:{color};}}"
                   f"QToolButton:hover {{border: 1px solid red; }}")
            self.clrbtn[-1].setStyleSheet(css)
            self.clrbtn[-1].clicked.connect(
                lambda x, c=color: self.select_color_(c))
            # noinspection PyArgumentList
            color_layout.addWidget(self.clrbtn[-1], i // nn, i % nn)

        # -- SPLITTER ---------------------------------
        h_frame = QFrame(None, flags=Qt.WindowFlags())
        h_frame.setFrameShape(QFrame.HLine)
        h_frame.setContentsMargins(0, 0, 0, 0)

        # -- BOTTOM (other color) ---------------------
        btns = QFrame(self, flags=Qt.WindowFlags())
        btn_layout = QHBoxLayout()
        other = QToolButton()
        other.clicked.connect(self.other_color_)
        other.setAutoRaise(True)
        other.setIcon(QIcon(img("editor/colorwheel")))
        btn_layout.addWidget(other, alignment=Qt.Alignment())
        self._lbl_other = QLabel(self.tr("other colors"))
        btn_layout.addWidget(self._lbl_other, alignment=Qt.Alignment())
        btns.setLayout(btn_layout)
        btn_layout.setContentsMargins(9, 0, 9, 9)
        self.clrbtn.append(other)

        # ---------------------------------------------
        main_layout.addWidget(caption, alignment=Qt.Alignment())
        main_layout.addWidget(colorbox, alignment=Qt.Alignment())
        main_layout.addWidget(h_frame, alignment=Qt.Alignment())
        main_layout.addWidget(btns, alignment=Qt.Alignment())

        self.setLayout(main_layout)

    # -------------------------------------------------------------------------
    def other_color_(self):
        self.hide()
        self.other_color.emit()

    # -------------------------------------------------------------------------
    def select_color_(self, color):
        self.hide()
        self.select_color.emit(color)

    # -------------------------------------------------------------------------
    def show_form(self, top):
        self.move(top.x(), top.y() + 1)
        self.setVisible(True)

    # -------------------------------------------------------------------------
    def paintEvent(self, event):
        # draw border
        painter = QPainter(self)
        painter.setPen(QPen(QColor("#9b9b9b"), 2, Qt.SolidLine, Qt.RoundCap))
        painter.drawRect(0, 0, self.width(), self.height())

    # -------------------------------------------------------------------------
    def mouseReleaseEvent(self, event):  # pragma: no cover
        self.hide()  # self.close()

    # -------------------------------------------------------------------------
    def hideEvent(self, event):
        self.hide_form.emit()

    # -------------------------------------------------------------------------
    def retranslate_ui(self, text):
        self._lbl_other.setText(self.tr("other colors"))
        self._lbl_caption.setText(text)
