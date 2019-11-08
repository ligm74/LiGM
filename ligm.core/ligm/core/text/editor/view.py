#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""GUI interface of embeddable text editor."""

from typing import Union
from PyQt5.Qt import (Qt, QObject, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                      QToolButton, QTextEdit, QSpacerItem, QSizePolicy, QFrame,
                      QFontComboBox, QSpinBox, QPalette, QColor, QCursor,
                      QPixmap, QPainter, QPoint, QTextCursor, QFont, QCheckBox,
                      QFontMetrics, QTextFormat, QLineEdit, QPushButton,
                      QGridLayout, QTimer)
from ligm.core.common import img
from ligm.core.qt import ColorPicker, BlockSignals, TestableWidget, TestableDialog
from .instable import InsertTable
from .align import AlignText


TWidget = Union[QWidget, TestableWidget]


# =============================================================================
class View(QObject):

    # -------------------------------------------------------------------------
    def __init__(self, parent: TWidget, config, margins=None):
        super(View, self).__init__()
        self._parent = parent
        self._cfg = config

        self.toolbar = ToolBar(self._cfg)
        self.text = QTextEdit()
        self.status = StatusBar()
        self.search_replace = SearchAndReplaceBar()
        self.line_numbers = LineNumberArea(self.text, self._cfg)

        self.cursors = {}
        self.init_ui(margins)
        self.update_ui()

        self._balloon = None

    # -------------------------------------------------------------------------
    def init_ui(self, margins=None):
        layout = QVBoxLayout()
        if margins:
            layout.setContentsMargins(*margins)
        layout.addWidget(self.toolbar, alignment=Qt.Alignment())
        layout.addWidget(self.search_replace, alignment=Qt.Alignment())
        layout.addWidget(self.text, alignment=Qt.Alignment())
        layout.addWidget(self.status, alignment=Qt.Alignment())
        self._parent.setLayout(layout)

        p = self.text.palette()
        p.setColor(QPalette.Base, QColor(
            self._cfg.get("TextEditor/Background", "#F0F0FF", system=True)))
        self.text.setPalette(p)

        self.cursors["normal"] = self.text.viewport().cursor()
        self.cursors["copyfmt"] = QCursor(
            QPixmap(img('editor/copy_format')), 0, 0)

        # for refresh self.line_numbers (LineNumberArea)
        if self.line_numbers:
            self.text.resizeEvent = self.resize_event
            self.text.scrollContentsBy = self.scroll_contents_by
            self.contents_change()

        self._parent.setFocusPolicy(Qt.StrongFocus)

    # -------------------------------------------------------------------------
    def update_ui(self):
        self.toolbar.setVisible(self._cfg.get("TextEditor/ShowToolBar", 1))
        self.status.setVisible(self._cfg.get("TextEditor/ShowStatusBar", 1))

        if not self._cfg.get("TextEditor/WordWrap", 0):
            self.text.setLineWrapMode(QTextEdit.NoWrap)
        else:
            self.text.setLineWrapMode(QTextEdit.WidgetWidth)

        if self._cfg.get("TextEditor/PlainText", 0):
            self.text.setAcceptRichText(False)
        else:
            self.text.setAcceptRichText(True)

        self.text.paintEvent = self.paint

        self.contents_change()

    # -------------------------------------------------------------------------
    def scroll_contents_by(self, dx, dy):  # pragma: no cover
        QTextEdit.scrollContentsBy(self.text, dx, dy)
        self.line_numbers.update()
        self.text.viewport().repaint()

    # -------------------------------------------------------------------------
    def contents_change(self):
        if self.line_numbers:
            self.text.setViewportMargins(self.line_numbers.width(), 0, 0, 0)
            self.line_numbers.update()
        self.text.setExtraSelections([])
        self.highlight_cur_line()

    # -------------------------------------------------------------------------
    def resize_event(self, event):
        self.line_numbers.resize(self.text.contentsRect())
        QTextEdit.resizeEvent(self.text, event)

    # -------------------------------------------------------------------------
    def highlight_cur_line(self):
        if not self._cfg.get("TextEditor/HighlightCurrentLine", 1):
            return
        selection = QTextEdit.ExtraSelection()
        color = self._cfg.get(
            "TextEditor/HighlightCurrentLineColor", "yellow", system=True)
        selection.format.setBackground(QColor(color))
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.text.textCursor()
        selection.cursor.clearSelection()
        self.text.setExtraSelections([selection])

    # -------------------------------------------------------------------------
    def show_hide_search_panel(self, key):

        if key == Qt.Key_F:
            # show or hide search panel
            visible = self.search_replace.isVisible()
            self.search_replace.only_search = True
            self.search_replace.set_visible(not visible)

        if key == Qt.Key_R:
            # show or hide replace panel
            visible = self.search_replace.isVisible()
            only_search = self.search_replace.only_search
            if visible:
                if only_search:
                    self.search_replace.only_search = False
                else:
                    visible = False
            else:
                self.search_replace.only_search = False
                visible = True
            self.search_replace.set_visible(visible)

        if key == Qt.Key_Escape:
            self.search_replace.set_visible(False)

    # -------------------------------------------------------------------------
    def retranslate_ui(self):
        self.search_replace.retranslate_ui()
        self.toolbar.retranslate_ui()

    # -------------------------------------------------------------------------
    def show_info(self, text):
        self._balloon = BalloonWidget(self._cfg, text)
        top = self._parent.mapToGlobal(self.text.geometry().topLeft())
        width = self.text.geometry().width()
        if self.text.verticalScrollBar().isVisible():  # pragma: no cover
            width -= self.text.verticalScrollBar().width()
        self._balloon.show_msg(top, width)

    # -------------------------------------------------------------------------
    def paint(self, event):
        # draw right border (if need)
        QTextEdit.paintEvent(self.text, event)

        if not self._cfg.get("TextEditor/PlainText", 0):
            return

        numline = self._cfg.get("TextEditor/MarginLine", 0)
        if not numline:  # pragma: no cover
            return

        painter = QPainter(self.text.viewport())
        painter.setPen(QColor("lightgray"))

        fm = QFontMetrics(QFont(
            self._cfg.get("TextEditor/MonospaceFont", "Mono", system=True),
            self._cfg.get("TextEditor/MonospaceFontSize", 11, system=True)))

        x = self.text.document().documentMargin() + fm.width("A") * numline - 1
        painter.drawLine(x, 0, x, self.text.viewport().height())


# =============================================================================
class ToolBar(TestableWidget):

    # -------------------------------------------------------------------------
    def __init__(self, config):
        TestableWidget.__init__(self, None)
        self._cfg = config
        self.controls = {}
        self.init_ui()

    # -------------------------------------------------------------------------
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.controls["save"] = QToolButton(self)
        self.controls["save"].setAutoRaise(True)
        layout.addWidget(self.controls["save"], alignment=Qt.Alignment())

        spacer = QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addItem(spacer)

        self.controls["auto-lang"] = QLabel("")
        layout.addWidget(self.controls["auto-lang"], alignment=Qt.Alignment())
        font = self.controls["auto-lang"].font()
        font.setPointSize(8)
        self.controls["auto-lang"].setFont(font)

        self.controls["font-name"] = QFontComboBox(self)
        layout.addWidget(self.controls["font-name"], alignment=Qt.Alignment())
        self.controls["font-size"] = QSpinBox(self)
        layout.addWidget(self.controls["font-size"], alignment=Qt.Alignment())

        self.controls["font-name"].setEditText(
            self._cfg.get("TextEditor/Font", "Mono", system=True))
        self.controls["font-size"].setValue(
            self._cfg.get("TextEditor/FontSize", 10, system=True))

        color = self._cfg.get("TextEditor/Background", "white", system=True)
        for name in ("align", "font-color", "background-color", "bold",
                     "hline", "table", "list", "number", "image", "format",
                     "eraser", "invisible-symbol"):
            if name == "font-color":
                self.controls[name] = ColorPicker(
                    text=self.tr("Text color"),
                    icon="editor/font-color",
                    color_caption=color,
                    config=self._cfg)
            elif name == "background-color":
                self.controls[name] = ColorPicker(
                    text=self.tr("Background color"),
                    icon="editor/backgroundcolor",
                    color_caption=color,
                    config=self._cfg)
            elif name == "align":
                self.controls[name] = AlignText(
                    text=self.tr("Alignment"),
                    icon="editor/align",
                    color_caption=color)
            elif name == "table":
                self.controls[name] = InsertTable(
                    text=self.tr("Insert table"),
                    icon="editor/table",
                    color_caption=color,
                    config=self._cfg)
            else:
                self.controls[name] = QToolButton(self)
            self.controls[name].setAutoRaise(True)
            layout.addWidget(self.controls[name], alignment=Qt.Alignment())
            if name == "image":
                line = QFrame(None, Qt.WindowFlags())
                line.setFrameShape(QFrame.VLine)
                line.setFrameShadow(QFrame.Sunken)
                layout.addWidget(line, alignment=Qt.Alignment())

        self.setLayout(layout)

    # -------------------------------------------------------------------------
    def retranslate_ui(self):
        for key, text in (("font-color", self.tr("Text color")),
                          ("background-color", self.tr("Background color")),
                          ("table", self.tr("Insert table")),
                          ("align", self.tr("Alignment")),
                          ):
            self.controls[key].retranslate_ui(text)


# =============================================================================
class StatusBar(TestableWidget):

    # -------------------------------------------------------------------------
    def __init__(self):
        TestableWidget.__init__(self, None)
        self.controls = {}
        self.init_ui()

    # -------------------------------------------------------------------------
    def init_ui(self):
        self.controls["left"] = QLabel("OK")
        self.controls["right"] = QLabel("")
        self.controls["center"] = QLabel("")

        self.controls["right"].setAlignment(Qt.AlignRight)
        self.controls["center"].setAlignment(Qt.AlignRight)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        # noinspection PyArgumentList
        layout.addWidget(self.controls["left"], 0, 0)
        # noinspection PyArgumentList
        layout.addWidget(self.controls["center"], 0, 1)
        # noinspection PyArgumentList
        layout.addWidget(self.controls["right"], 0, 2)
        self.setLayout(layout)

    # -------------------------------------------------------------------------
    def set(self, data: dict):
        for key, val in data.items():
            self.controls[key].setText(val)


# =============================================================================
class LineNumberArea(TestableWidget):

    # -------------------------------------------------------------------------
    def __init__(self, textedit, cfg):
        TestableWidget.__init__(self, textedit)
        self._textedit = textedit
        self._cfg = cfg

        self._font = QFont(
            self._cfg.get("TextEditor/MonospaceFont", "Mono", system=True),
            self._cfg.get("TextEditor/MonospaceFontSize", 10, system=True))
        self._fm = QFontMetrics(self._font)

        self._background = QColor(self._cfg.get(
            "TextEditor/BackgroundLineNumberArea", "#E8E8E8", system=True))
        self._fontcolor = QColor(self._cfg.get(
            "TextEditor/NumberColorLineNumberArea", "gray", system=True))

    # -------------------------------------------------------------------------
    def paintEvent(self, event):  # pragma: no cover
        painter = QPainter(self)
        painter.setFont(self._font)
        painter.fillRect(event.rect(), self._background)
        painter.setPen(self._fontcolor)
        cursor = self._textedit.cursorForPosition(QPoint(0, 0))
        at_end = False

        font_height = self._fm.height()
        height = self._textedit.height()
        while not at_end:
            rect = self._textedit.cursorRect(cursor)
            if rect.top() >= height:
                break
            number = str(cursor.blockNumber() + 1)
            painter.drawText(0, rect.top(), self.width() - 2 - 3,
                             font_height, Qt.AlignRight, number)
            cursor.movePosition(QTextCursor.EndOfBlock)
            at_end = cursor.atEnd()
            if not at_end:
                cursor.movePosition(QTextCursor.NextBlock)
        painter.drawLine(self.width() - 1, 0, self.width() - 1, height)

    # -------------------------------------------------------------------------
    def width(self):
        if self._cfg.get("TextEditor/ShowLineNumbers", 1):
            cursor = QTextCursor(self._textedit.document())
            cursor.movePosition(QTextCursor.End)
            digits = len(str(cursor.blockNumber() + 1))
            return 5 + self._fm.width('9') * digits + 3
        return 0

    # -------------------------------------------------------------------------
    def resize(self, rect):
        self.setGeometry(rect.left(), rect.top(), self.width(), rect.height())


# =============================================================================
class SearchAndReplaceBar(TestableWidget):

    # -------------------------------------------------------------------------
    def __init__(self, only_search=True):
        TestableWidget.__init__(self, None)
        self.only_search = only_search

        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vlayout)

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_widget = QWidget(self, Qt.WindowFlags())
        search_widget.setLayout(search_layout)
        vlayout.addWidget(search_widget, alignment=Qt.Alignment())

        repl_layout = QHBoxLayout()
        repl_layout.setContentsMargins(0, 0, 0, 0)
        self.replace_widget = QWidget(self, Qt.WindowFlags())
        self.replace_widget.setLayout(repl_layout)
        vlayout.addWidget(self.replace_widget, alignment=Qt.Alignment())

        self.controls = {
            "find-all": QToolButton(self),
            "find-prev": QToolButton(self),
            "find-next": QToolButton(self),
            "replace": QToolButton(self),
            "replace-all": QToolButton(self),
            "search-edit": QLineEdit(self),
            "replace-edit": QLineEdit(self),
            "cs-box": QCheckBox(self.tr("case-sensitive"), self),
        }

        self.controls["find-all"].setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon)

        for c in ("search-edit", "find-prev", "find-next", "find-all",
                  "cs-box", "replace-edit", "replace", "replace-all"):
            layout = repl_layout if c.startswith("replace") else search_layout
            layout.addWidget(self.controls[c], alignment=Qt.Alignment())

        for c in ("find-prev", "find-next", "find-all",
                  "replace", "replace-all"):
            self.controls[c].setAutoRaise(True)

        self.controls["search-edit"].returnPressed.connect(
            self.controls["find-all"].click)

        self.set_visible(False)

    # -------------------------------------------------------------------------
    def set_visible(self, visible):
        if not self.isVisible():
            self.controls["search-edit"].setFocus()
        self.setVisible(visible)
        self.replace_widget.setVisible(not self.only_search)

    # -------------------------------------------------------------------------
    def retranslate_ui(self):
        self.controls["cs-box"].setText(self.tr("case-sensitive"))
        self.controls["search-edit"].setPlaceholderText(self.tr("Search"))
        self.controls["replace-edit"].setPlaceholderText(
            self.tr("Replace with"))


# =============================================================================
class BalloonWidget(TestableWidget):

    # -------------------------------------------------------------------------
    def __init__(self, config, text):
        TestableWidget.__init__(self)
        self.setWindowFlags(Qt.Popup)

        self.text = text
        self._cfg = config
        self.offset_x, self.offset_y = 10, 10
        self.out_info = QLabel(self)
        self.setStyleSheet("QWidget {border:15px solid yellow;"
                           "background: yellow; color: blue}")
        self.timer = QTimer()
        self.timer.timeout.connect(self.close)

    # -------------------------------------------------------------------------
    def show_msg(self, top, width):
        self.out_info.setText(self.text)
        self.out_info.show()
        self.adjustSize()

        move_x = top.x() + width - self.offset_x - self.width()
        move_y = top.y() + self.offset_y

        self.move(move_x, move_y)
        self.setVisible(True)

        self.timer.start(self._cfg.get("TextEditor/TimeoutBalloon", 3000))

    # -------------------------------------------------------------------------
    def mousePressEvent(self, event):  # pragma: no cover
        self.close()

    # -------------------------------------------------------------------------
    def keyPressEvent(self, event):  # pragma: no cover
        self.close()


# =============================================================================
class ImageSize(TestableDialog):

    # -------------------------------------------------------------------------
    def __init__(self, parent, width, height, orig_width, orig_height):
        super(ImageSize, self).__init__(parent)
        self.parent = parent
        self.params = {
            "width": width,
            "height": height,
            "orig_width": orig_width,
            "orig_height": orig_height,
        }
        self.controls = []
        self.init_ui()

    # -------------------------------------------------------------------------
    def init_ui(self):
        self.setWindowTitle(self.tr("Image of size"))
        layout = QGridLayout()

        txt = self.tr("Original size: ")
        txt += f"{self.params['orig_width']}x{self.params['orig_height']}"
        # noinspection PyArgumentList
        layout.addWidget(QLabel(txt), 0, 0, 1, 2)

        # noinspection PyArgumentList
        layout.addWidget(QLabel(self.tr("Width"), self), 1, 0)
        # noinspection PyArgumentList
        layout.addWidget(QLabel(self.tr("Height"), self), 2, 0)

        self.controls.append(QSpinBox(self))
        self.controls.append(QSpinBox(self))
        self.controls[0].setMinimum(1)
        self.controls[1].setMinimum(1)
        self.controls[0].setMaximum(10000)
        self.controls[1].setMaximum(10000)
        self.controls[0].setValue(self.params['width'])
        self.controls[1].setValue(self.params['height'])
        # noinspection PyArgumentList
        layout.addWidget(self.controls[0], 1, 1)
        # noinspection PyArgumentList
        layout.addWidget(self.controls[1], 2, 1)
        self.controls[0].valueChanged.connect(lambda x: self.change(0))
        self.controls[1].valueChanged.connect(lambda x: self.change(1))

        self.controls.append(QCheckBox(self.tr("proportional size"), self))
        # noinspection PyArgumentList
        layout.addWidget(self.controls[2], 3, 0, 1, 2)
        self.controls[2].setChecked(True)

        line = QFrame(None, Qt.WindowFlags())
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        # noinspection PyArgumentList
        layout.addWidget(line, 4, 0, 1, 2)

        self.change_button = QPushButton(self.tr("Change size"), self)
        self.change_button.clicked.connect(self.change_image)
        # noinspection PyArgumentList
        layout.addWidget(self.change_button, 5, 0, 1, 2)

        self.setLayout(layout)

    # -------------------------------------------------------------------------
    def change(self, n):
        if not self.controls[2].isChecked():
            return
        k = self.params['orig_height'] / self.params['orig_width']
        if n == 0:  # width
            with BlockSignals(self.controls[1]):
                self.controls[1].setValue(int(self.controls[0].value() * k))
        if n == 1:  # height
            with BlockSignals(self.controls[0]):
                self.controls[0].setValue(int(self.controls[1].value() / k))

    # -------------------------------------------------------------------------
    def change_image(self):
        self.params = {
            "width": self.controls[0].value(),
            "height": self.controls[1].value(),
        }
        super(ImageSize, self).accept()
