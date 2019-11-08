#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Widget for align text."""

from PyQt5.Qt import (Qt, QPoint, QToolButton, QAction, QGridLayout, QLabel,
                      QVBoxLayout, QPen, QColor, QIcon, QPainter, QApplication,
                      QFrame, QHBoxLayout, pyqtSignal, QSize, QTextCharFormat)
from ligm.core.common import img
from ligm.core.qt import TestableWidget


# =============================================================================
class AlignText(QToolButton):
    """Widget for select a align of text."""

    # noinspection PyUnresolvedReferences
    select_align = pyqtSignal(Qt.Alignment, QTextCharFormat.VerticalAlignment)

    def __init__(self, text=None, color_caption="#F0F0FF", icon=""):
        """
        text - text in caption and tooltip
        icon - filename for icon of button
        """
        QToolButton.__init__(self, None)
        self.setAutoRaise(True)

        self._text = self.tr("Alignment") if text is None else text
        self._color_caption = color_caption

        # ------------------------------------------------------
        self._colors_widget = AlignTextWidget(color_caption=color_caption)
        self._colors_widget.select_align.connect(self.select_align_)
        self._colors_widget.hide_form.connect(self.hide_form)

        self._action = QAction(self._text, None)
        self._action.setIcon(QIcon(img(icon)))
        self._action.triggered.connect(self.show_form)
        self.setDefaultAction(self._action)

    # -------------------------------------------------------------------------
    def show_form(self):
        self.setCheckable(True)
        self.setChecked(True)
        QApplication.processEvents()
        pos = QPoint(self.rect().left(), self.rect().bottom())
        self._colors_widget.show_form(self.mapToGlobal(pos))

    # -------------------------------------------------------------------------
    def select_align_(self, r, c):
        horiz = {
            1: Qt.AlignLeft,
            2: Qt.AlignCenter,
            3: Qt.AlignRight,
            4: Qt.AlignJustify,
        }
        vert = {
            1: QTextCharFormat.AlignTop,
            2: QTextCharFormat.AlignMiddle,
            3: QTextCharFormat.AlignBottom,
        }
        self.select_align.emit(horiz[c], vert[r])

    # -------------------------------------------------------------------------
    def hide_form(self):
        self.setCheckable(False)

    # -------------------------------------------------------------------------
    def retranslate_ui(self, text):
        self._text = self.tr("Alignment") if text is None else text
        self._colors_widget.retranslate_ui()
        self.setToolTip(self._text)

    # -------------------------------------------------------------------------
    def set_enable_vertical_align(self, value):
        self._colors_widget.set_enable_vertical_align(value)


# =============================================================================
class AlignTextWidget(TestableWidget):

    select_align = pyqtSignal(int, int)
    hide_form = pyqtSignal()

    # -------------------------------------------------------------------------
    def __init__(self, color_caption):
        TestableWidget.__init__(self)
        self.setWindowFlags(Qt.Popup)
        self._text = self.tr("Alignment text")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        b = "border: 1px solid #9b9b9b;"
        self._styles = {"border": b,
                        "border_blue": "border: 0px solid blue;",
                        "frame": 'QFrame[frameShape="4"]{color: #9b9b9b;}'}

        self.setStyleSheet(self._styles["frame"])

        # -- CAPTION ----------------------------------
        caption = QFrame(self, flags=Qt.WindowFlags())
        caption_layout = QHBoxLayout()
        self._lbl_caption = QLabel(self._text)
        self._lbl_caption.setStyleSheet(self._styles["border_blue"])
        caption_layout.addWidget(self._lbl_caption, alignment=Qt.Alignment())
        caption.setLayout(caption_layout)
        caption_layout.setContentsMargins(9, 5, 9, 5)
        caption.setStyleSheet(
            f"background-color: {color_caption}; {self._styles['border']}")

        # -- CELLS GRID -------------------------------
        cellsbox = QFrame(self, flags=Qt.WindowFlags())
        cells = QGridLayout()
        cellsbox.setLayout(cells)
        cells.setContentsMargins(9, 0, 9, 9)
        self._clrbtn = []
        for i in range(1, 4):
            for j in range(1, 5):
                self._clrbtn.append(QToolButton())
                self._clrbtn[-1].clicked.connect(
                    lambda z, y=i, x=j: self.select_align_(x, y))
                self._clrbtn[-1].setAutoRaise(True)

                sz = 48
                self._clrbtn[-1].setFixedSize(sz, sz)
                self._clrbtn[-1].setIconSize(QSize(sz, sz))

                self._clrbtn[-1].setIcon(QIcon(img(f"editor/a{i}{j}.png")))
                # noinspection PyArgumentList
                cells.addWidget(self._clrbtn[-1], i - 1, j - 1)

        # ---------------------------------------------
        main_layout.addWidget(caption, alignment=Qt.Alignment())
        main_layout.addWidget(cellsbox, alignment=Qt.Alignment())

        self.setLayout(main_layout)

    # -------------------------------------------------------------------------
    def select_align_(self, n, m):
        self.hide()
        self.select_align.emit(m, n)

    # -------------------------------------------------------------------------
    def show_form(self, top):
        self.move(top.x(), top.y() + 1)
        self.setVisible(True)
        self.adjustSize()

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
    def retranslate_ui(self):
        self._text = self.tr("Alignment text")
        self._lbl_caption.setText(self._text)

    # -------------------------------------------------------------------------
    def set_enable_vertical_align(self, value):
        if value:
            for i in range(1, 4):
                for j in range(1, 5):
                    k = (i - 1) * 4 + j - 1
                    self._clrbtn[k].setIcon(QIcon(img(f"editor/a{i}{j}.png")))
                    self._clrbtn[k].setVisible(True)
        else:
            for i in range(4):
                self._clrbtn[i].setIcon(QIcon(img(f"editor/a0{i + 1}.png")))
            for i in range(4, 12):
                self._clrbtn[i].setVisible(False)
