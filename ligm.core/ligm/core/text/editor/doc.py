#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""The document class for the embeddable text editor."""

import datetime
from PyQt5.Qt import (pyqtSignal, QTextDocument, QFont, QTextCursor, QObject,
                      QTextOption, QTextListFormat, Qt, QBrush, QPixmap,
                      QTextBlockFormat, QTextTableFormat, QByteArray, QColor,
                      QTextCharFormat, QBuffer, QIODevice)


# =============================================================================
class Doc(QObject):

    changed_status = pyqtSignal(dict)   # for update the status bar
    changed_bold = pyqtSignal(bool)     # for update button "Bold"
    enabled_save = pyqtSignal(bool)     # for update button "Save"

    # -------------------------------------------------------------------------
    def __init__(self, config):
        super(Doc, self).__init__()
        self._text = QTextDocument()
        self._cfg = config
        self._text_edit_cursor = QTextCursor(self._text)
        self._text.setIndentWidth(self._cfg.get("TextEditor/IndentWidth", 24))

        self.set_default_font()

    # -------------------------------------------------------------------------
    @property
    def text(self):
        return self._text

    # -------------------------------------------------------------------------
    def is_modified(self):
        return self._text.isModified()

    # -------------------------------------------------------------------------
    def in_table(self):
        return bool(self._text_edit_cursor.currentTable())

    # -------------------------------------------------------------------------
    def set_default_font(self, set_modified=False):
        font_name = self._cfg.get("TextEditor/Font", "Mono", system=True)
        sz = self._cfg.get("TextEditor/FontSize", 10, system=True)
        font = QFont(font_name, sz)
        self._text.setDefaultFont(font)
        if set_modified:
            self._text.setModified(True)
            self.change(self._text_edit_cursor)

    # -------------------------------------------------------------------------
    def change(self, text_cursor: QTextCursor = None):
        """
        Called (from QTextEdit event) with changed text or position of cursor
        """
        if text_cursor:
            self._text_edit_cursor = text_cursor

        # refresh data on statusbar
        y = self._text_edit_cursor.blockNumber() + 1
        cnt = self._text.lineCount()
        x = self._text_edit_cursor.columnNumber() + 1
        chg = (self.tr("The document is not saved")
               if self._text.isModified() else "")
        xy = f"{y} : {x} [{cnt}]"
        self.changed_status.emit({"left": chg, "right": xy})
        self.enabled_save.emit(self.is_modified())

    # -------------------------------------------------------------------------
    def bold(self):
        """
        Set/unset bold font
        """
        fmt = self._text_edit_cursor.charFormat()
        typ = QFont.Normal if fmt.fontWeight() == QFont.Bold else QFont.Bold
        fmt.setFontWeight(typ)
        self._text_edit_cursor.setCharFormat(fmt)
        self.change(self._text_edit_cursor)
        self.changed_bold.emit(typ == QFont.Bold)

    # -------------------------------------------------------------------------
    def color(self, color):
        fmt = self._text_edit_cursor.charFormat()
        fmt.setForeground(QColor(color))
        self._text_edit_cursor.setCharFormat(fmt)

    # -------------------------------------------------------------------------
    def background_color(self, color):
        fmt = self._text_edit_cursor.charFormat()
        if self.in_table():
            table = self._text_edit_cursor.currentTable()
            cell = table.cellAt(self._text_edit_cursor)
            cell_format = cell.format()
            cell_format.setBackground(QColor(color))
            cell.setFormat(cell_format)
        else:
            fmt.setBackground(QColor(color))
        self._text_edit_cursor.setCharFormat(fmt)

    # -------------------------------------------------------------------------
    def font(self, font):
        fmt = self._text_edit_cursor.charFormat()
        fmt.setFont(font)
        self._text_edit_cursor.setCharFormat(fmt)

    # -------------------------------------------------------------------------
    def font_size(self, font_size):
        fmt = self._text_edit_cursor.charFormat()
        fmt.setFontPointSize(font_size)
        self._text_edit_cursor.setCharFormat(fmt)

    # -------------------------------------------------------------------------
    def hline(self):
        """
        Insert horizontal line
        """
        # Tag HR is not correctly displayed  in QTextview
        cur_char_fmt = self._text_edit_cursor.charFormat()
        cur_block_fmt = self._text_edit_cursor.blockFormat()
        if bool(self._text_edit_cursor.currentTable()):
            self._text_edit_cursor.insertBlock(cur_block_fmt, cur_char_fmt)

        block_fmt = QTextBlockFormat()
        block_fmt.setTopMargin(5)
        block_fmt.setBottomMargin(5)
        block_fmt.setAlignment(Qt.AlignLeft)
        block_fmt.setBackground(QBrush(QColor("#C1C1C1")))

        char_format = QTextCharFormat()
        char_format.setFont(QFont("Arial", 1))

        self._text_edit_cursor.insertBlock(block_fmt, char_format)
        self._text_edit_cursor.insertText(" ")

        self._text_edit_cursor.insertBlock(cur_block_fmt, cur_char_fmt)

        self.change(self._text_edit_cursor)

    # -------------------------------------------------------------------------
    def show_hide_hidden_char(self, show: bool):
        if show:
            # show hidden char
            option = self._text.defaultTextOption()
            option.setFlags(
                option.flags() |
                QTextOption.ShowTabsAndSpaces |
                QTextOption.ShowLineAndParagraphSeparators |
                QTextOption.AddSpaceForLineAndParagraphSeparators
            )
            self._text.setDefaultTextOption(option)
        else:
            # remove hidden char
            option = self._text.defaultTextOption()
            stas = ~QTextOption.ShowTabsAndSpaces
            slaps = ~QTextOption.ShowLineAndParagraphSeparators
            asflaps = ~QTextOption.AddSpaceForLineAndParagraphSeparators
            option.setFlags(option.flags() & stas & slaps & asflaps)
            self._text.setDefaultTextOption(option)

    # -------------------------------------------------------------------------
    def blist(self):
        self._text_edit_cursor.insertList(QTextListFormat.ListDisc)

    # -------------------------------------------------------------------------
    def nlist(self):
        self._text_edit_cursor.insertList(QTextListFormat.ListDecimal)

    # -------------------------------------------------------------------------
    def copy_format(self, fmt):
        self._text_edit_cursor.setCharFormat(fmt)

    # -------------------------------------------------------------------------
    def clear_format(self):
        txt = self._text.toPlainText()
        self._text_edit_cursor.beginEditBlock()  # ----  begin -------
        self._text_edit_cursor.select(QTextCursor.Document)
        self._text_edit_cursor.removeSelectedText()
        fmt = QTextBlockFormat()
        self._text_edit_cursor.setBlockFormat(fmt)
        self._text_edit_cursor.insertText(txt)
        self._text_edit_cursor.endEditBlock()    # ----  end ---------

    # -------------------------------------------------------------------------
    def text_align(self, horiz, vert):

        fmt = QTextBlockFormat()
        fmt.setAlignment(horiz)
        self._text_edit_cursor.mergeBlockFormat(fmt)

        if self.in_table():
            table = self._text_edit_cursor.currentTable()
            cell = table.cellAt(self._text_edit_cursor)
            cell_format = cell.format()
            cell_format.setVerticalAlignment(vert)
            cell.setFormat(cell_format)

    # -------------------------------------------------------------------------
    def insert_table(self, table_params):
        fmt = QTextTableFormat()
        fmt.setCellPadding(table_params["padding"])
        fmt.setCellSpacing(table_params["space"])
        return self._text_edit_cursor.insertTable(
            table_params["rows"], table_params["cols"], fmt)

    # -------------------------------------------------------------------------
    def table(self):
        """
        Current table if cursor in table
        """
        return self._text_edit_cursor.currentTable()

    # -------------------------------------------------------------------------
    def cell(self):
        """
        Cell in current table
        """
        return self.table().cellAt(self._text_edit_cursor)

    # -------------------------------------------------------------------------
    def add_row(self):
        self.table().appendRows(1)

    # -------------------------------------------------------------------------
    def add_col(self):
        self.table().appendColumns(1)

    # -------------------------------------------------------------------------
    def del_row(self):
        self.table().removeRows(self.cell().row(), 1)

    # -------------------------------------------------------------------------
    def del_col(self):
        self.table().removeColumns(self.cell().column(), 1)

    # -------------------------------------------------------------------------
    def ins_row(self):
        self.table().insertRows(self.cell().row(), 1)

    # -------------------------------------------------------------------------
    def ins_col(self):
        self.table().insertColumns(self.cell().column(), 1)

    # -------------------------------------------------------------------------
    def merge_cells(self):
        self.table().mergeCells(self._text_edit_cursor)

    # -------------------------------------------------------------------------
    def split_cells(self):
        self.table().splitCell(self.cell().row(), self.cell().column(), 1, 1)

    # -------------------------------------------------------------------------
    def replace(self, replace_text):
        self._text_edit_cursor.insertText(replace_text)

    # -------------------------------------------------------------------------
    def ins_date(self):
        self._text_edit_cursor.insertText(
            datetime.datetime.now().strftime("%d.%m.%Y "))

    # -------------------------------------------------------------------------
    def ins_time(self):
        self._text_edit_cursor.insertText(
            datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S "))

    # -------------------------------------------------------------------------
    def in_image(self):
        return self._text_edit_cursor.charFormat().isImageFormat()

    # -------------------------------------------------------------------------
    def ins_image(self, image, fmt, width, height, insert_space=True):
        bytes_ = QByteArray()
        buffer = QBuffer(bytes_)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, fmt)
        buffer.close()

        base64 = bytes_.toBase64().data().decode(encoding="utf-8")

        s = (f'<img width="{width}" height="{height}" '
             f'src="data:image/{fmt};base64,{base64}"')

        self._text_edit_cursor.insertHtml(s)

        if insert_space:
            self._text_edit_cursor.insertText(" ")

    # -------------------------------------------------------------------------
    @staticmethod
    def get_image(html):
        image, width, height, fmt = None, -1, -1, "png"
        if "<img" in html:
            raw = html[html.index("<img"):].split(">")[0].split('"')
            for i, r in enumerate(raw):
                if "base64" in r:
                    img_txt = r.split(",")[-1].encode(encoding="utf-8")
                    image = QPixmap()
                    image.width()
                    image.height()
                    image.loadFromData(QByteArray.fromBase64(img_txt))
                    fmt = r.split("image/")[1].split(";")[0]
                if "width" in r and i + 1 < len(raw):
                    width = int(raw[i + 1])
                if "height" in r and i + 1 < len(raw):
                    height = int(raw[i + 1])
        return image, width, height, fmt

    # -------------------------------------------------------------------------
    def save(self, save_proc):
        if self._text.isModified():
            self._text.setModified(False)
            if self._cfg.get("TextEditor/PlainText", 0):
                txt = str(self._text.toPlainText())
                if self._cfg.get("TextEditor/ReplaceTabWithSpace", 0):
                    cnt = self._cfg.get("TextEditor/CountSpaceInTab", 1)
                    txt = txt.replace("\t", " " * cnt)
                res = save_proc(txt)
            else:
                res = save_proc(str(self._text.toHtml(encoding=QByteArray())))
            if res is not None:
                self._text.setModified(True)

        self.change(self._text_edit_cursor)

    # -------------------------------------------------------------------------
    def load(self, load_proc):
        self._text.clear()
        if self._cfg.get("TextEditor/PlainText", 0):
            self._text.setPlainText(load_proc())
        else:
            self._text.setHtml(load_proc())
        self._text.setModified(False)

    # -------------------------------------------------------------------------
    def get_text(self):
        if self._cfg.get("TextEditor/PlainText", 0):
            return str(self._text.toPlainText())
        else:
            return str(self._text.toHtml(encoding=QByteArray()))

    # -------------------------------------------------------------------------
    def is_empty(self):
        return not bool(len(self._text.toPlainText().strip()))
