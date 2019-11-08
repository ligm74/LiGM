#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Widget for insert a table."""

from PyQt5.Qt import (Qt, QPoint, QToolButton, QAction, QGridLayout, QSpinBox,
                      QVBoxLayout, QPen, QColor, QIcon, QPainter, QLabel,
                      QFrame, QHBoxLayout, pyqtSignal, QApplication,
                      QPushButton)
from ligm.core.common import img
from ligm.core.qt import TestableDialog, TestableWidget, msg


# =============================================================================
class InsertTable(QToolButton):
    """Widget for select a size of table."""

    insert_table = pyqtSignal(dict)

    def __init__(self, text=None, color_caption="#F0F0FF", icon="",
                 config=None):
        """
        text - text in caption and tooltip
        icon - filename for icon of button
        """
        QToolButton.__init__(self, None)
        self.setAutoRaise(True)

        self._cfg = config
        self._text = self.tr("Table") if text is None else text
        self._color_caption = color_caption

        # ------------------------------------------------------

        self._colors_widget = InsertTableWidget(color_caption=color_caption)
        self._colors_widget.select_size.connect(self.select_size_)
        self._colors_widget.hide_form.connect(self.hide_form)
        self._colors_widget.other_size.connect(self.other_size)

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
    def select_size_(self, width, height):
        table_params = {
            "rows": height,
            "cols": width,
            "padding": self._cfg.get('TextEditor/PaddingInTable', 3),
            "space": self._cfg.get('TextEditor/SpaceInTable', 0),
        }
        self.insert_table.emit(table_params)

    # -------------------------------------------------------------------------
    def other_size(self):
        t = TableParamsDlg(self.parent(), self._cfg)
        if t.exec_():
            self.insert_table.emit(t.table_params)

    # -------------------------------------------------------------------------
    def hide_form(self):
        self.setCheckable(False)

    # -------------------------------------------------------------------------
    def retranslate_ui(self, text):
        self._text = self.tr("Table") if text is None else text
        self._colors_widget.retranslate_ui(self._text)
        self.setToolTip(self._text)


# =============================================================================
class InsertTableWidget(TestableWidget):

    select_size = pyqtSignal(int, int)
    hide_form = pyqtSignal()
    other_size = pyqtSignal()

    # -------------------------------------------------------------------------
    def __init__(self, color_caption):
        TestableWidget.__init__(self)
        self.setWindowFlags(Qt.Popup)
        self._text = self.tr("Table")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        b = "border: 1px solid #9b9b9b;"
        self._styles = {
            "border": b,
            "border_blue": "border: 0px solid blue;",
            "selection": f"QToolButton {{{b}background-color:#fee5e2;}}",
            "white": f"QToolButton {{{b}background-color:white;}}",
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
        cells.setSpacing(1)
        cellsbox.setLayout(cells)
        cells.setContentsMargins(9, 0, 9, 0)
        self._nn = 10
        self._clrbtn = []
        colors = ["white" for _ in range(self._nn ** 2)]
        cellsbox.leaveEvent = lambda x: self._leave_cell()
        for i, color in enumerate(colors):
            self._clrbtn.append(QToolButton())
            # noinspection PyPep8Naming
            self._clrbtn[-1].enterEvent = lambda x, n=i: self._enter_cell(n)
            self._clrbtn[-1].setStyleSheet(self._styles["white"])
            self._clrbtn[-1].clicked.connect(
                lambda x, n=i: self.select_size_(n))
            # noinspection PyArgumentList
            cells.addWidget(self._clrbtn[-1], i // self._nn, i % self._nn)

        # -- SPLITTER ---------------------------------
        h_frame = QFrame(None, flags=Qt.WindowFlags())
        h_frame.setFrameShape(QFrame.HLine)
        h_frame.setContentsMargins(0, 0, 0, 0)

        # -- BOTTOM (other color) ---------------------
        btns = QFrame(self, flags=Qt.WindowFlags())
        btn_layout = QHBoxLayout()
        other = QToolButton()
        other.clicked.connect(self.other_size_)
        other.setAutoRaise(True)
        other.setIcon(QIcon(img("editor/table_gray")))
        btn_layout.addWidget(other, alignment=Qt.Alignment())
        self._lbl_other = QLabel(self.tr("insert table"))
        btn_layout.addWidget(self._lbl_other, alignment=Qt.Alignment())
        btns.setLayout(btn_layout)
        btn_layout.setContentsMargins(9, 0, 9, 9)
        self._clrbtn.append(other)

        # ---------------------------------------------
        main_layout.addWidget(caption, alignment=Qt.Alignment())
        main_layout.addWidget(cellsbox, alignment=Qt.Alignment())
        main_layout.addWidget(h_frame, alignment=Qt.Alignment())
        main_layout.addWidget(btns, alignment=Qt.Alignment())

        self.setLayout(main_layout)

    # -------------------------------------------------------------------------
    def _enter_cell(self, n):  # pragma: no cover
        h, w = 1 + n // self._nn, 1 + n % self._nn
        self._lbl_caption.setText(f"{self._text} - {w} x {h}")

        for i in range(self._nn ** 2):
            x, y = i // self._nn, i % self._nn
            if x < h and y < w:
                self._clrbtn[i].setStyleSheet(self._styles["selection"])
            else:
                self._clrbtn[i].setStyleSheet(self._styles["white"])

    # -------------------------------------------------------------------------
    def _leave_cell(self):  # pragma: no cover
        self._lbl_caption.setText(self._text)
        for clrbtn in self._clrbtn:
            clrbtn.setStyleSheet(self._styles["white"])

    # -------------------------------------------------------------------------
    def other_size_(self):
        self.hide()
        self.other_size.emit()

    # -------------------------------------------------------------------------
    def select_size_(self, n):
        self.hide()
        self.select_size.emit(1 + n % self._nn, 1 + n // self._nn)

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
        self._text = self.tr("Table")
        self._lbl_other.setText(self.tr("insert table"))
        self._lbl_caption.setText(text)


# =============================================================================
class TableParamsDlg(TestableDialog):

    # -------------------------------------------------------------------------
    def __init__(self, parent=None, config=None):
        super(TableParamsDlg, self).__init__(parent)
        self.parent = parent
        self._cfg = config
        self.table_params = {}
        self.controls = []
        self.init_ui()

    # -------------------------------------------------------------------------
    def init_ui(self):

        layout = QGridLayout()
        for i, lbl in enumerate((
                self.tr("Rows"), self.tr("Columns"),
                self.tr("The distance between the outer borders"),
                self.tr("Distance between border and content"))):
            # noinspection PyArgumentList
            layout.addWidget(QLabel(lbl, self), i, 0)
            self.controls.append(QSpinBox(self))
            # noinspection PyArgumentList
            layout.addWidget(self.controls[-1], i, 1)
        self.controls[2].setValue(
            self._cfg.get('TextEditor/PaddingInTable', 3))
        self.controls[3].setValue(self._cfg.get('TextEditor/SpaceInTable', 0))

        insert_button = QPushButton(self.tr("Insert"), self)
        insert_button.clicked.connect(self.insert)
        # noinspection PyArgumentList
        layout.addWidget(insert_button, 4, 0, 1, 2)
        self.controls.append(insert_button)

        self.setWindowTitle(self.tr("Insert table"))
        # self.setGeometry(300, 300, 200, 100)
        self.setLayout(layout)

    # -------------------------------------------------------------------------
    def insert(self):

        if not self.controls[0].value() or not self.controls[1].value():
            msg(self.tr(
                "Number of rows and columns should not be zero!"), self)
            return

        self.table_params = {
            "rows": self.controls[0].value(),
            "cols": self.controls[1].value(),
            "padding": self.controls[2].value(),
            "space": self.controls[3].value(),
        }

        self._cfg['TextEditor/PaddingInTable'] = self.controls[2].value()
        self._cfg['TextEditor/SpaceInTable'] = self.controls[3].value()

        super(TableParamsDlg, self).accept()
