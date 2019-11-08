#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for the document class for the embeddable text editor."""

import unittest
import re
from PyQt5.Qt import (QFont, QTextCursor, QTextOption, Qt,
                      QColor, QTextCharFormat, QImage)
from ligm.core.text.editor.doc import Doc
from ligm.core.common import SimpleConfig as Config
from ligm.core.qt import QTestHelper


DEBUG = QTestHelper().start_tests()


# =============================================================================
class DocTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_text")
    def test_text(self):
        doc = Doc(Config())
        self.assertIn("QTextDocument", str(type(doc.text)))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_is_modified")
    def test_is_modified(self):
        doc = Doc(Config())
        self.assertEqual(doc.is_modified(), False)
        doc.text.setModified(True)
        self.assertEqual(doc.is_modified(), True)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_in_table")
    def test_in_table(self):
        doc = Doc(Config())

        def in_table():
            # is exists table in document ?
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            _in_table = False
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    _in_table = True
                    break
            return _in_table

        self.assertEqual(in_table(), False)
        doc.insert_table({"padding": 0, "space": 0, "rows": 1, "cols": 1})
        self.assertEqual(in_table(), True)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_default_font")
    def test_set_default_font(self):
        cfg = Config()
        doc = Doc(cfg)

        font_name = doc.text.defaultFont().family()
        font_size = doc.text.defaultFont().pointSize()

        font_name = "Arial" if font_name == "Mono" else "Mono"
        font_size = 12 if font_size == 10 else 10

        cfg["SYSTEM", "TextEditor/Font"] = font_name
        cfg["SYSTEM", "TextEditor/FontSize"] = font_size

        doc.set_default_font(True)

        self.assertEqual(font_name, doc.text.defaultFont().family())
        self.assertEqual(font_size, doc.text.defaultFont().pointSize())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_change")
    def test_change(self):
        cfg = Config()
        doc = Doc(cfg)
        txt = "1 row\n 2 row\n3 row"

        def chg(param):
            cnt_lines = len(txt.split("\n"))
            self.assertTrue(f"[{cnt_lines}]" in param["right"])

        def esave(param):
            self.assertEqual(param, True)

        doc.changed_status.connect(chg)
        doc.enabled_save.connect(esave)

        self.assertEqual(doc.is_modified(), False)
        doc.text.setPlainText(txt)
        doc.change()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_bold")
    def test_bold(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")

        result = []

        def chg(param):
            result.append(param)

        doc.changed_bold.connect(chg)

        doc.bold()  # add 'True'
        doc.bold()  # add 'False'

        self.assertEqual(result, [True, False])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_color")
    def test_color(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")

        # with patch.object(QColorDialog, 'getColor',
        #                  return_value=QColor("blue")):
        #    doc.color()
        doc.color("blue")

        color = doc._text_edit_cursor.charFormat().foreground().color().name()
        self.assertEqual(color, QColor("blue").name())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_background_color")
    def test_background_color(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")

        # with patch.object(QColorDialog, 'getColor',
        #                  return_value=QColor("blue")):
        #    doc.color()
        doc.background_color("blue")

        color = doc._text_edit_cursor.charFormat().background().color().name()
        self.assertEqual(color, QColor("blue").name())

        doc = Doc(Config())

        def in_table():
            # is exists table in document ?
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            _in_table = False
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    _in_table = True
                    doc.background_color("blue")
                    cc = doc._text_edit_cursor
                    cell = cc.currentTable().cellAt(cc).format()
                    clr = cell.background().color().name()
                    self.assertEqual(clr, QColor("blue").name())
                    break
            return _in_table

        doc.insert_table({"padding": 0, "space": 0, "rows": 1, "cols": 1})
        self.assertEqual(in_table(), True)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_font")
    def test_font(self):
        doc = Doc(Config())

        font_name = doc.text.defaultFont().family()
        font_size = doc.text.defaultFont().pointSize()

        font_name = "Arial" if font_name == "Mono" else "Mono"
        font_size = 12 if font_size == 10 else 10

        font = QFont(font_name, font_size)
        doc.font(font)
        fname = doc._text_edit_cursor.charFormat().font().family()
        self.assertEqual(font_name, fname)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_font_size")
    def test_font_size(self):
        doc = Doc(Config())
        font_size = doc.text.defaultFont().pointSize()
        font_size = 12 if font_size == 10 else 10
        doc.font_size(font_size)
        fsize = doc._text_edit_cursor.charFormat().font().pointSize()
        self.assertEqual(font_size, fsize)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_hline")
    def test_hline(self):
        doc = Doc(Config())

        result = []

        def chg(param):
            result.append(param["right"][-2:-1])

        doc.changed_status.connect(chg)
        doc.change()
        doc.hline()  # add line + new line (new block)

        self.assertEqual(result, ["1", "3"])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_hline_table")
    def test_hline_table(self):
        doc = Doc(Config())

        result = []

        def chg(param):
            result.append(int(param["right"].split("[")[-1].split("]")[0]))

        doc.changed_status.connect(chg)

        doc.insert_table({"padding": 0, "space": 0, "rows": 3, "cols": 2})

        def in_table():
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    break

        in_table()
        doc.change()
        doc.hline()  # add line + new line (new block)
        self.assertTrue(int(result[-2]) < int(result[-1]))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_show_hide_hidden_char")
    def test_show_hide_hidden_char(self):
        doc = Doc(Config())
        doc.show_hide_hidden_char(True)
        flags = doc.text.defaultTextOption().flags()
        self.assertEqual(int(flags & QTextOption.ShowTabsAndSpaces), 1)
        doc.show_hide_hidden_char(False)
        flags = doc.text.defaultTextOption().flags()
        self.assertEqual(int(flags & QTextOption.ShowTabsAndSpaces), 0)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_blist")
    def test_blist(self):
        doc = Doc(Config())
        self.assertFalse("</li></ul>" in doc.text.toHtml())
        doc.blist()
        self.assertTrue("</li></ul>" in doc.text.toHtml())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_nlist")
    def test_nlist(self):
        doc = Doc(Config())
        self.assertFalse("</li></ol>" in doc.text.toHtml())
        doc.nlist()
        self.assertTrue("</li></ol>" in doc.text.toHtml())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_copy_format")
    def test_copy_format(self):
        doc = Doc(Config())
        fmt = doc._text_edit_cursor.charFormat()
        fmt.font().setBold(True)

        fmt = doc._text_edit_cursor.charFormat()
        self.assertFalse(fmt.font().bold())

        font = fmt.font()
        font.setBold(True)
        fmt.setFont(font)

        doc.copy_format(fmt)
        fmt = doc._text_edit_cursor.charFormat()
        self.assertTrue(fmt.font().bold())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_clear_format")
    def test_clear_format(self):
        doc = Doc(Config())
        doc.nlist()
        self.assertTrue("</li></ol>" in doc.text.toHtml())
        doc.clear_format()
        self.assertFalse("</li></ol>" in doc.text.toHtml())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_text_align")
    def test_text_align(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")

        alignment = doc._text_edit_cursor.blockFormat().alignment()
        self.assertEqual(alignment, Qt.AlignLeft)

        doc.text_align(Qt.AlignRight, QTextCharFormat.AlignBottom)

        alignment = doc._text_edit_cursor.blockFormat().alignment()
        self.assertEqual(alignment, Qt.AlignRight)

        doc.insert_table({"padding": 0, "space": 0, "rows": 3, "cols": 2})

        def in_table():
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    doc.text_align(Qt.AlignRight, QTextCharFormat.AlignBottom)
                    a = doc._text_edit_cursor.charFormat().verticalAlignment()
                    self.assertEqual(a, QTextCharFormat.AlignBottom)
                    break

        in_table()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_insert_table")
    def test_insert_table(self):
        pass  # tested in other tests

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_table")
    def test_table(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")
        self.assertEqual(doc.table(), None)
        doc.insert_table({"padding": 0, "space": 0, "rows": 3, "cols": 2})

        def in_table():
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    break

        in_table()
        self.assertTrue("QTextTable" in str(type(doc.table())))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_cell")
    def test_cell(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")
        doc.insert_table({"padding": 0, "space": 0, "rows": 3, "cols": 2})

        def in_table():
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    cc = doc.table().cellAt(2, 1)
                    cc.firstCursorPosition().insertText("Hello")
                    doc.change(cc.firstCursorPosition())
                    break

        in_table()
        self.assertTrue("QTextTableCell" in str(type(doc.cell())))
        self.assertEqual(doc.cell().row(), 2)
        self.assertEqual(doc.cell().column(), 1)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_add_row")
    def test_add_row(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")
        doc.insert_table({"padding": 0, "space": 0, "rows": 3, "cols": 2})

        def in_table():
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    break

        in_table()

        self.assertEqual(doc.table().rows(), 3)
        self.assertEqual(doc.table().columns(), 2)
        doc.add_row()
        self.assertEqual(doc.table().rows(), 4)
        self.assertEqual(doc.table().columns(), 2)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_add_col")
    def test_add_col(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")
        doc.insert_table({"padding": 0, "space": 0, "rows": 3, "cols": 2})

        def in_table():
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    break

        in_table()

        self.assertEqual(doc.table().rows(), 3)
        self.assertEqual(doc.table().columns(), 2)
        doc.add_col()
        self.assertEqual(doc.table().rows(), 3)
        self.assertEqual(doc.table().columns(), 3)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_del_row")
    def test_del_row(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")
        doc.insert_table({"padding": 0, "space": 0, "rows": 3, "cols": 2})

        def in_table():
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    cc = doc.table().cellAt(2, 1)
                    cc.firstCursorPosition().insertText("Hello")
                    doc.change(cc.firstCursorPosition())

        in_table()

        self.assertEqual(doc.table().rows(), 3)
        self.assertEqual(doc.table().columns(), 2)
        doc.del_row()
        self.assertEqual(doc.table().rows(), 2)
        self.assertEqual(doc.table().columns(), 2)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_del_col")
    def test_del_col(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")
        doc.insert_table({"padding": 0, "space": 0, "rows": 3, "cols": 2})

        def in_table():
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    cc = doc.table().cellAt(2, 1)
                    cc.firstCursorPosition().insertText("Hello")
                    doc.change(cc.firstCursorPosition())

        in_table()

        self.assertEqual(doc.table().rows(), 3)
        self.assertEqual(doc.table().columns(), 2)
        doc.del_col()
        self.assertEqual(doc.table().rows(), 3)
        self.assertEqual(doc.table().columns(), 1)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_ins_row")
    def test_ins_row(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")
        doc.insert_table({"padding": 0, "space": 0, "rows": 3, "cols": 2})

        def in_table():
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    break

        in_table()

        self.assertEqual(doc.table().rows(), 3)
        self.assertEqual(doc.table().columns(), 2)
        doc.ins_row()
        self.assertEqual(doc.table().rows(), 4)
        self.assertEqual(doc.table().columns(), 2)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_ins_col")
    def test_ins_col(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")
        doc.insert_table({"padding": 0, "space": 0, "rows": 3, "cols": 2})

        def in_table():
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    break

        in_table()

        self.assertEqual(doc.table().rows(), 3)
        self.assertEqual(doc.table().columns(), 2)
        doc.ins_col()
        self.assertEqual(doc.table().rows(), 3)
        self.assertEqual(doc.table().columns(), 3)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_merge_cells")
    def test_merge_cells(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")
        doc.insert_table({"padding": 0, "space": 0, "rows": 4, "cols": 3})

        def in_table():
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    cc = doc.table().cellAt(2, 2)
                    cc.firstCursorPosition().insertText("Hello1")

                    cc = doc.table().cellAt(2, 1)
                    cc.firstCursorPosition().insertText("Hello")

                    c.movePosition(QTextCursor.EndOfBlock,
                                   QTextCursor.KeepAnchor)
                    break

        in_table()
        doc.merge_cells()  # ????? need merge cell in TextCursor
        doc.table().mergeCells(0, 0, 2, 2)
        self.assertTrue("colspan" in doc.text.toHtml())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_split_cells")
    def test_split_cells(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")
        doc.insert_table({"padding": 0, "space": 0, "rows": 4, "cols": 3})

        def in_table():
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_table():
                    cc = doc.table().cellAt(2, 2)
                    cc.firstCursorPosition().insertText("Hello1")

                    cc = doc.table().cellAt(2, 1)
                    cc.firstCursorPosition().insertText("Hello")

                    c.movePosition(QTextCursor.EndOfBlock,
                                   QTextCursor.KeepAnchor)
                    break

        in_table()
        doc.table().mergeCells(0, 0, 2, 2)
        doc.split_cells()
        self.assertFalse("colspan" in doc.text.toHtml())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_replace")
    def test_replace(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")
        self.assertFalse("HELLO" in doc.text.toHtml())
        doc.replace("HELLO")
        self.assertTrue("HELLO" in doc.text.toHtml())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_ins_date")
    def test_ins_date(self):
        doc = Doc(Config())
        len_txt = len(doc.text.toPlainText())
        doc.ins_date()
        self.assertEqual(len(doc.text.toPlainText()), len_txt + 11)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_ins_time")
    def test_ins_time(self):
        doc = Doc(Config())
        len_txt = len(doc.text.toPlainText())
        doc.ins_time()
        self.assertEqual(len(doc.text.toPlainText()), len_txt + 20)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_save")
    def test_save(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")
        doc.text.setModified(True)

        def save(txt):
            if txt:
                return None

        def save1(txt):
            if txt:
                return True

        self.assertTrue(doc.is_modified())
        doc.save(save)
        self.assertFalse(doc.is_modified())
        doc.text.setModified(True)
        doc.save(save1)
        self.assertTrue(doc.is_modified())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_load")
    def test_load(self):
        doc = Doc(Config())

        def load():
            return "HELLO"

        self.assertNotEqual(doc.text.toPlainText(), "HELLO")
        doc.load(load)
        self.assertEqual(doc.text.toPlainText(), "HELLO")

        cfg = Config()
        cfg["TextEditor/PlainText"] = True
        doc = Doc(cfg)

        self.assertNotEqual(doc.text.toPlainText(), "HELLO")
        doc.load(load)
        self.assertEqual(doc.text.toPlainText(), "HELLO")

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get_text")
    def test_get_text(self):
        doc = Doc(Config())
        doc.text.setPlainText("1 row\n 2 row\n3 row")

        cleantext = re.sub(re.compile('<.*?>'), '', doc.get_text())
        cleantext = cleantext.replace("p, li { white-space: pre-wrap; }", "")
        self.assertEqual("1 row\n 2 row\n3 row", cleantext.strip())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_is_empty")
    def test_is_empty(self):
        doc = Doc(Config())
        self.assertTrue(doc.is_empty())
        doc.text.setPlainText("1 row\n 2 row\n3 row")
        self.assertFalse(doc.is_empty())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_ins_image")
    def test_ins_image(self):

        doc = Doc(Config())
        img = QImage(10, 10, QImage.Format_ARGB32)

        self.assertFalse("data:image/png;base64" in doc.text.toHtml())
        self.assertFalse('width="10"' in doc.text.toHtml())

        doc.ins_image(img, "png", 10, 10)

        self.assertTrue("data:image/png;base64" in doc.text.toHtml())
        self.assertTrue('width="10"' in doc.text.toHtml())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_in_image")
    def test_in_image(self):

        doc = Doc(Config())
        img = QImage(10, 10, QImage.Format_ARGB32)
        doc._text_edit_cursor.insertImage(img)

        def in_image():
            c = QTextCursor(doc.text)
            c.movePosition(QTextCursor.Start)
            while c.movePosition(
                    QTextCursor.NextCharacter, QTextCursor.KeepAnchor):
                if doc.in_image():
                    break
        in_image()
        self.assertTrue(doc.in_image())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get_image")
    def test_get_image(self):

        doc = Doc(Config())
        img = QImage(10, 10, QImage.Format_ARGB32)
        doc.ins_image(img, "png", 10, 15)

        image, width, height, fmt = doc.get_image(doc.text.toHtml())

        self.assertEqual(fmt, "png")
        self.assertEqual(width, 10)
        self.assertEqual(height, 15)
        self.assertTrue("QPixmap" in str(type(image)))
