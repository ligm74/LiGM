#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Test the editor GUI."""

import sys
import re
import unittest
import time
from unittest.mock import patch
from PyQt5.Qt import (
    QColor, QMouseEvent, QEvent, QMessageBox, Qt, QPoint, QImage, QHBoxLayout,
    QApplication, QCoreApplication, QFileDialog)
from ligm.core.text import TextEditor
from ligm.core.qt import QTestHelper, TestableWidget, diff
from ligm.core.common import SimpleConfig as Config
from ligm.core.text.editor.view import ImageSize
from ligm.core.text.spell import SpellChecker


DEBUG = QTestHelper().start_tests()


# =============================================================================
class EditorTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.test = QTestHelper()

        # ---------------------------------------------------------------------
        # customize editor
        # noinspection PyUnusedLocal
        def save(txt):
            return None

        def load():
            return "HELLO"

        cls.widget = TestableWidget(None)
        cls.spell = SpellChecker(enabled=True)
        cls.editor = TextEditor(cls.widget, Config(), save=save, load=load,
                                spell=cls.spell)

        # ---------------------------------------------------------------------
        # customize the widget for placement
        layout = QHBoxLayout()
        layout.addWidget(cls.editor, alignment=Qt.Alignment())
        cls.widget.setLayout(layout)
        cls.widget.resize(800, 450)
        cls.widget.move(800, 150)

        cls.test.show_and_wait_for_active(cls.widget)

    # -------------------------------------------------------------------------
    def setUp(self):
        self.editor.doc.clear_format()
        self.text = self.editor._view.text
        test_str = "Hello\n  WdItOr !!! \n World. test 1234\n How do YOU DO ?"
        self.text.setText(test_str)
        self.test.sleep(1)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_bold")
    def test_set_bold(self):
        self.test.wrd_d_click(self.text, "rld")
        self.test.key_clicks(self.text, "World.upper()=WORLD", delay=1)

        bold = self.editor.view.toolbar.controls["bold"]

        self.test.wrd_d_click(self.text, "WdItOr")
        diff(self.text.toHtml())
        self.test.mouse_click(bold, QPoint(1, 1), delay=1)
        changed = diff(self.text.toHtml())
        self.assertTrue("font-weight:600" in changed["add"])
        self.assertTrue(bold.isChecked())

        self.test.wrd_click(self.text, "llo")
        self.assertFalse(bold.isChecked())

        self.test.wrd_click(self.text, "dItOr")
        self.assertTrue(bold.isChecked())

        diff(self.text.toHtml())
        self.test.wrd_d_click(self.text, "WdItOr")
        self.test.mouse_click(bold, QPoint(1, 1), delay=1)
        changed = diff(self.text.toHtml())
        self.assertFalse(bold.isChecked())
        self.assertTrue("font-weight:600" in changed["del"])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_change_font")
    def test_change_font(self):
        fn = self.editor.view.toolbar.controls["font-name"]

        diff(self.text.toHtml())
        self.test.wrd_d_click(self.text, "WdItOr")
        # select all text
        self.test.key_click(fn, Qt.Key_A, "", Qt.ControlModifier, delay=1)
        self.test.key_clicks(fn, "Arial Black")
        changed = diff(self.text.toHtml())
        self.assertTrue("font-family:'Arial Black'" in changed["add"])

        diff(self.text.toHtml())
        self.test.wrd_d_click(self.text, "Hello")
        self.test.key_click(fn, Qt.Key_A, "", Qt.ControlModifier, delay=1)
        self.test.key_clicks(fn, "Courier New")
        changed = diff(self.text.toHtml())
        self.assertTrue("font-family:'Courier New'" in changed["add"])

        self.test.wrd_click(self.text, "dItOr")
        self.assertEqual(fn.currentText(), "Arial Black")
        self.test.sleep()
        self.test.wrd_click(self.text, "llo")
        self.assertEqual(fn.currentText(), "Courier New")
        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_change_size")
    def test_change_size(self):
        fn = self.editor.view.toolbar.controls["font-size"]

        self.test.wrd_d_click(self.text, "WdItOr")
        diff(self.text.toHtml())
        # select all text
        self.test.key_click(fn, Qt.Key_A, "", Qt.ControlModifier)
        self.test.key_clicks(fn, "50", delay=1)
        changed = diff(self.text.toHtml())
        self.assertTrue("font-size:50pt" in changed["add"])

        self.test.wrd_d_click(self.text, "Hello")
        diff(self.text.toHtml())
        # select all text
        self.test.key_click(fn, Qt.Key_A, "", Qt.ControlModifier)
        self.test.key_clicks(fn, "5", delay=1)
        changed = diff(self.text.toHtml())
        self.assertTrue("font-size:5pt" in changed["add"])

        self.test.wrd_click(self.text, "", delay=1)

        self.test.wrd_click(self.text, "dItOr", delay=1)
        self.assertEqual(fn.value(), 50)
        self.test.wrd_click(self.text, "llo", delay=1)
        self.assertEqual(fn.value(), 5)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_change_color")
    def test_change_color(self):
        self.test.wrd_d_click(self.text, "WdItOr")
        diff(self.text.toHtml())

        color = self.editor.view.toolbar.controls["font-color"]

        with patch.object(color, '_get_color', return_value=QColor("blue")):
            self.test.mouse_click(color, QPoint(1, 1))
            self.test.sleep()
            self.test.mouse_click(
                color._colors_widget.clrbtn[-1], QPoint(3, 3))
            self.test.sleep()

        changed = diff(self.text.toHtml())
        self.assertTrue("color:" + QColor("blue").name() in changed["add"])

        diff(self.text.toHtml())
        self.test.wrd_d_click(self.text, "YOU")
        with patch.object(color, '_get_color', return_value=QColor("red")):
            self.test.mouse_click(color, QPoint(1, 1))
            self.test.sleep()
            color._colors_widget.other_color_()
        changed = diff(self.text.toHtml())
        self.assertTrue("color:" + QColor("red").name() in changed["add"])

        self.test.wrd_click(self.text, "rld", delay=1)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_background_color")
    def test_background_color(self):
        self.test.wrd_d_click(self.text, "WdItOr")
        diff(self.text.toHtml())

        color = self.editor.view.toolbar.controls["background-color"]

        with patch.object(color, '_get_color', return_value=QColor("blue")):
            self.test.mouse_click(color, QPoint(1, 1))
            self.test.sleep()
            self.test.mouse_click(
                color._colors_widget.clrbtn[-1], QPoint(3, 3))
            self.test.sleep()

        changed = diff(self.text.toHtml())
        self.assertTrue("color:" + QColor("blue").name() in changed["add"])

        diff(self.text.toHtml())
        self.test.wrd_d_click(self.text, "YOU")
        with patch.object(color, '_get_color', return_value=QColor("yellow")):
            self.test.mouse_click(color, QPoint(1, 1))
            self.test.sleep()
            color._colors_widget.other_color_()
        changed = diff(self.text.toHtml())
        self.assertTrue("background-color:" + QColor("yellow").name()
                        in changed["add"])

        self.test.wrd_click(self.text, "rld", delay=1)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_horizontal_line")
    def test_horizontal_line(self):
        diff(self.text.toHtml())
        self.test.mouse_click(self.text.viewport(), QPoint(200, 51))

        hline = self.editor.view.toolbar.controls["hline"]
        self.test.mouse_click(hline, QPoint(1, 1))
        changed = diff(self.text.toHtml())
        self.assertTrue('background-color:#c1c1c1' in changed["add"])
        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_list")
    def test_list(self):
        diff(self.text.toHtml())
        self.test.wrd_click(self.text, "!!!")

        list_ = self.editor.view.toolbar.controls["list"]
        self.test.mouse_click(list_, QPoint(1, 1))
        changed = diff(self.text.toHtml())
        self.assertTrue('<ul' in changed["add"])
        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_number_list")
    def test_number_list(self):
        diff(self.text.toHtml())
        self.test.wrd_click(self.text, "!!!")

        number = self.editor.view.toolbar.controls["number"]
        self.test.mouse_click(number, QPoint(1, 1))
        changed = diff(self.text.toHtml())
        self.assertTrue('<ol' in changed["add"])
        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_copy_format")
    def test_copy_format(self):
        self.test.wrd_d_click(self.text, "WdItOr")
        bold = self.editor.view.toolbar.controls["bold"]
        self.test.mouse_click(bold, QPoint(1, 1))

        self.test.wrd_click(self.text, "ItOr")
        fmt = self.editor.view.toolbar.controls["format"]
        self.test.mouse_click(fmt, QPoint(1, 1))

        pos_beg = self.test.get_xy_for_word(self.text, "Hello")
        pos_end = self.test.get_xy_for_word(self.text, "l")

        w = self.text.viewport()

        def m_event(_event, _pos):
            e = QMouseEvent(_event, QPoint(_pos), w.mapToGlobal(_pos),
                            Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
            QApplication.postEvent(w, e)

        m_event(QEvent.MouseButtonPress, pos_beg)
        m_event(QEvent.MouseMove, pos_beg)
        m_event(QEvent.MouseButtonPress, pos_beg)

        for x in range(pos_beg.x(), pos_end.x()):
            m_event(QEvent.MouseMove, QPoint(x, pos_beg.y()))

        self.test.sleep()
        m_event(QEvent.MouseButtonRelease, pos_end)

        self.test.wrd_click(self.text, "o")
        self.assertFalse(bold.isChecked())
        self.test.wrd_click(self.text, "e")
        self.assertTrue(bold.isChecked())

        self.test.wrd_click(self.text, "ItOr")
        self.test.mouse_click(fmt, QPoint(1, 1))
        self.test.mouse_click(bold, QPoint(1, 1))  # to check reset cursor
        self.test.sleep()

        self.test.wrd_click(self.text, "ItOr")
        self.test.mouse_click(fmt, QPoint(1, 1))
        self.test.mouse_click(fmt, QPoint(1, 1))
        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_clear_format")
    def test_clear_format(self):
        clear = self.text.toHtml()
        self.test.wrd_d_click(self.text, "WdItOr")
        bold = self.editor.view.toolbar.controls["bold"]
        self.test.mouse_click(bold, QPoint(1, 1))
        self.test.wrd_d_click(self.text, "")
        self.assertNotEqual(clear, self.text.toHtml())

        eraser = self.editor.view.toolbar.controls["eraser"]
        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.No):
            self.test.mouse_click(eraser, QPoint(1, 1))
        self.assertNotEqual(clear, self.text.toHtml())

        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.Yes):
            self.test.mouse_click(eraser, QPoint(1, 1))
        self.assertEqual(clear, self.text.toHtml())
        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_hidden_char")
    def test_hidden_char(self):
        self.test.wrd_d_click(self.text, "Hello")

        fn = self.editor.view.toolbar.controls["font-size"]
        self.test.key_click(fn, Qt.Key_A, "", Qt.ControlModifier)
        self.test.key_clicks(fn, "5", delay=1)

        y = self.test.get_xy_for_word(self.text, "YOU").y()
        self.test.wrd_d_click(self.text, "WdItOr")

        invis_sym = self.editor.view.toolbar.controls["invisible-symbol"]
        self.test.mouse_click(invis_sym, QPoint(1, 1))

        # reduced the size of the 1st line (with word "Hello")
        y1 = self.test.get_xy_for_word(self.text, "YOU").y()
        self.test.wrd_d_click(self.text, "")

        self.assertNotEqual(y, y1)
        self.test.sleep()
        # switch off (for next tests)
        self.test.mouse_click(invis_sym, QPoint(1, 1))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_view")
    def test_view(self):
        self.assertIn("View", str(type(self.editor.view)))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_doc")
    def test_doc(self):
        self.assertIn("Doc", str(type(self.editor.doc)))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "set_option")
    def test_set_option(self):
        self.assertFalse(self.editor.view.text.isReadOnly())
        self.editor.set_option(readonly=True)
        self.assertTrue(self.editor.view.text.isReadOnly())
        self.editor.set_option(readonly=False)
        self.assertFalse(self.editor.view.text.isReadOnly())

        self.assertFalse(self.editor._cfg.get("TextEditor/PlainText", 0))
        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.No):
            self.editor.set_option(format="text")
        self.assertFalse(self.editor._cfg.get("TextEditor/PlainText", 0))

        self.editor.set_option(format="html")
        self.assertFalse(self.editor._cfg.get("TextEditor/PlainText", 0))

        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.Yes):
            self.editor.set_option(format="text")
        self.assertTrue(self.editor._cfg.get("TextEditor/PlainText", 0))
        self.assertTrue(self.editor.doc.get_text())

        self.editor.set_option(format="html")
        self.assertFalse(self.editor._cfg.get("TextEditor/PlainText", 0))

        self.editor.set_option(retranslate="")
        self.editor.set_option(invisible_symbol="")

        self.editor.set_option(auto_save=1)
        self.assertTrue(self.editor._cfg.get("TextEditor/AutoSave", 1))

        self.editor.set_option(margin_line=1)
        self.assertTrue(self.editor._cfg.get("TextEditor/MarginLine", 1))

        self.editor.set_option(show_status_bar=0)
        self.assertFalse(self.editor._cfg.get("TextEditor/ShowStatusBar", 1))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "get_option")
    def test_get_option(self):
        self.assertTrue(self.editor.get_option("word-wrap"))
        self.editor.set_option(word_wrap=False)
        self.assertFalse(self.editor.get_option("word-wrap"))
        self.assertFalse(self.editor.get_option("readonly"))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "save")
    def test_save(self):
        self.assertFalse(self.editor.doc.is_modified())
        self.editor.doc.text.setModified(True)
        self.assertTrue(self.editor.doc.is_modified())

        self.editor.save()
        self.assertFalse(self.editor.doc.is_modified())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "load")
    def test_load(self):
        txt = "Hello\n  WdItOr !!! \n World. test 1234\n How do YOU DO ?"
        self.assertEqual(self.editor.doc.text.toPlainText(), txt)
        self.editor.load()
        self.assertEqual(self.editor.doc.text.toPlainText(), "HELLO")

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "search")
    def test_search(self):
        self.test.key_click(self.text.viewport(), Qt.Key_F, "",
                            Qt.ControlModifier, delay=1)
        fn = self.editor.view.search_replace.controls["search-edit"]
        self.test.key_clicks(fn, "How", Qt.NoModifier, delay=1)
        self.assertEqual(len(self.editor.view.text.extraSelections()), 0)

        find = self.editor.view.search_replace.controls["find-all"]
        self.test.mouse_click(find, QPoint(1, 1))

        # one result found
        self.assertEqual(len(self.editor.view.text.extraSelections()), 1)
        self.test.sleep()

        txt = "Hello\n  WdItOr !!! \n World. test 1234\n How do YOU DO ?"
        self.text.setText(txt * 5)
        self.test.sleep()
        self.test.mouse_click(find, QPoint(1, 1))
        self.assertEqual(len(self.editor.view.text.extraSelections()), 5)
        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_btn_save_visible")
    def test_set_btn_save_visible(self):
        save = self.editor.view.toolbar.controls["save"]

        self.assertTrue(save.isVisible())
        self.test.sleep()
        self.editor._set_btn_save_visible(False)
        self.test.sleep()
        self.assertFalse(save.isVisible())

        self.editor.set_option(btn_save_visible=True)
        self.assertTrue(save.isVisible())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_align_menu")
    def test_align_menu(self):
        diff(self.text.toHtml())
        align = self.editor.view.toolbar.controls["align"]
        self.test.mouse_click(align, QPoint(1, 1))  # align.click() trigger()
        self.test.sleep()
        self.test.mouse_click(align._colors_widget._clrbtn[2], QPoint(3, 3))
        # TODO: .
        #  !!!! -------------------------------------------------------!!!!
        #  !!!! I do not know how to select an item and close the menu !!!!
        #  !!!! -------------------------------------------------------!!!!
        #  QTest.mouseClick(self.interactive.controls["ALIGN"],
        #                  Qt.LeftButton, Qt.NoModifier, QPoint(30, 10))
        self.test.sleep()
        changed = diff(self.text.toHtml())
        self.assertTrue("right" in changed["add"])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_key_press")
    def test_key_press(self):
        self.test.wrd_click(self.text, "rld")

        def pkey(text, key):
            self.test.key_click(
                text, key, "", Qt.ControlModifier, delay=1)

        # for invisible object (self.test.is_interactive() == False)
        with patch.object(self.text, 'hasFocus',
                          return_value=True):
            ll = len(self.text.toHtml())
            pkey(self.text, Qt.Key_D)
            self.assertEqual(len(self.text.toHtml()) - ll, 11)

            ll = len(self.text.toHtml())
            pkey(self.text, Qt.Key_T)
            self.assertEqual(len(self.text.toHtml()) - ll, 20)

            v = self.editor._view
            self.assertFalse(v.search_replace.isVisible())
            pkey(self.text, Qt.Key_F)
            self.assertTrue(v.search_replace.only_search)
            pkey(self.text, Qt.Key_R)
            self.assertFalse(v.search_replace.only_search)
            self.assertTrue(v.search_replace.isVisible())
            v.show_hide_search_panel(Qt.Key_Escape)
            self.assertFalse(v.search_replace.isVisible())
            pkey(self.text, Qt.Key_R)
            self.assertFalse(v.search_replace.only_search)
            pkey(self.text, Qt.Key_R)
            self.assertFalse(v.search_replace.isVisible())

            pkey(self.text, Qt.Key_S)

        # patch due to LONG runtime  (~ 0.3 sec.)
        with patch.object(self.editor, '_print_text', return_value=None):
            pkey(self.text, Qt.Key_P)

        # ------
        ok = []

        # noinspection PyUnusedLocal
        def effect(**kw):
            ok.append("OK")

        self.assertEqual(len(ok), 0)
        with patch.object(self.editor, '_search',
                          side_effect=effect):
            self.test.key_click(self.text, Qt.Key_F3, "", Qt.ShiftModifier)
            self.test.key_click(self.text, Qt.Key_F3, "", Qt.NoModifier)
        self.test.sleep()

        keyswitcher = self.editor._keyswitcher
        self.editor._keyswitcher = False
        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_clicks(self.text, "helll")
        self.editor._keyswitcher = keyswitcher

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_context_menu")
    def test_context_menu(self):
        self.test.wrd_click(self.text, "rld")

        doc = self.editor.doc
        table = doc.insert_table(
            {"padding": 0, "space": 0, "rows": 3, "cols": 2})
        cc = table.cellAt(2, 1)
        cc.firstCursorPosition().insertText("TABLE")
        doc.change(cc.firstCursorPosition())

        # copy text in clipboard
        self.test.wrd_d_click(self.text, "TABLE", delay=1)

        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_click(
                self.text, Qt.Key_C, "", Qt.ControlModifier, delay=1)

        time.sleep(0.51)
        QApplication.processEvents()

        pos = self.test.get_xy_for_word(self.text, "TABLE")
        self.test.wrd_click(self.text, "TABLE", delay=1)

        def key_switcher_params(widget):
            paste_txt = QCoreApplication.translate("@default", "Paste")
            paste_act = (
                [a for a in widget.actions()
                 if a.text().split("\t")[0].replace("&", "") == paste_txt])[0]
            test = QTestHelper()
            test.sleep()
            widget.setActiveAction(paste_act)
            test.sleep()
            test.key_click(widget, Qt.Key_Enter)

        diff(self.text.toHtml())
        self.test.handle_popup_widget(key_switcher_params)
        self.editor.view.text.customContextMenuRequested.emit(pos)

        self.test.sleep(1)
        changed = diff(self.text.toHtml())
        self.assertTrue("TABLE" in changed["add"])

        # - test image -
        self.editor._doc.ins_image(QImage(), "png", 1, 1)

        def image_param(widget):
            image_txt = QCoreApplication.translate("@default",
                                                   "Change size of image")
            image_act = (
                [a for a in widget.actions()
                 if a.text().split("\t")[0].replace("&", "") == image_txt])
            test = QTestHelper()
            test.sleep()
            # check item in menu
            self.assertEqual(len(image_act), 1)
            widget.hide()

        self.test.handle_popup_widget(image_param)
        with patch.object(self.editor._doc, "in_image", returning_value=True):
            self.editor.view.text.selectAll()
            self.editor.view.text.customContextMenuRequested.emit(pos)
        self.test.sleep()

        # - test spellchecker -
        def spell_no(widget):
            image_txt = QCoreApplication.translate("@default",
                                                   "Add to the dictionary")
            image_act = (
                [a for a in widget.actions()
                 if a.text().split("\t")[0].replace("&", "") == image_txt])
            test = QTestHelper()
            test.sleep()
            # check item in menu
            self.assertEqual(len(image_act), 1)
            widget.hide()

        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_clicks(self.text, " hello_hello")
        self.test.wrd_click(self.text, "hello_hello")

        self.test.handle_popup_widget(spell_no)
        self.editor.view.text.customContextMenuRequested.emit(pos)

        self.test.wrd_click(self.text, "")
        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_clicks(self.text, " hell2 ")
        self.test.wrd_click(self.text, "hell2")

        self.test.handle_popup_widget(spell_no)
        self.editor.view.text.customContextMenuRequested.emit(pos)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_search_replace")
    def test_search_replace(self):
        txt = self.editor._view.text
        search = self.editor._view.search_replace.controls["search-edit"]
        replace = self.editor._view.search_replace.controls["replace-edit"]
        cs_box = self.editor._view.search_replace.controls["cs-box"]

        search.setText("HELLO")
        self.assertTrue(self.editor._search())
        self.test.wrd_click(self.text, "WdItOr", delay=1)

        self.assertTrue(self.editor._search(True))
        self.test.wrd_click(self.text, "WdItOr", delay=1)

        cs_box.setChecked(True)
        self.editor._search()
        self.assertFalse(self.editor._search(False))

        self.test.wrd_click(self.text, "WdItOr", delay=1)
        self.assertFalse(self.editor._search(True))

        self.editor.search(show_msg=False)

        search.setText("Hello")
        replace.setText("REPLACE")
        diff(txt.toHtml())
        self.assertTrue(self.editor._search(True))
        self.editor._replace()
        changed = diff(txt.toHtml())
        self.assertTrue("REPLACE" in changed["add"])

        search.setText("REPLACE")
        replace.setText("XXX")
        diff(txt.toHtml())
        self.assertTrue(self.editor._search(True))
        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.No):
            self.editor._replace_all()
        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.Yes):
            self.editor._replace_all()
        changed = diff(txt.toHtml())
        self.assertTrue("XXX" in changed["add"])

        search.setText("!-!-!-!")
        self.editor._replace_all()
        self.editor._view.show_hide_search_panel(Qt.Key_Escape)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_undo")
    def test_undo(self):
        self.editor.set_option(auto_save=0)
        self.test.wrd_click(self.text, "WdItOr", delay=1)
        self.assertFalse(self.editor.doc.is_modified())

        # for invisible object (self.test.is_interactive() == False)
        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_clicks(self.text, "** == **", delay=1)
            self.assertTrue(self.editor.doc.is_modified())

            self.test.key_click(
                self.text, Qt.Key_Z, "", Qt.ControlModifier, delay=1)
        self.assertFalse(self.editor.doc.is_modified())
        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get_text")
    def test_get_text(self):
        test_str = "Hello\n  WdItOr !!! \n World. test 1234\n How do YOU DO ?"
        cleantext = re.sub(re.compile('<.*?>'), '', self.editor.get_text())
        cleantext = cleantext.replace("p, li { white-space: pre-wrap; }", "")
        self.assertEqual(test_str.strip(), cleantext.strip())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_is_empty")
    def test_is_empty(self):
        self.assertFalse(self.editor.is_empty())
        self.text.setText("")
        self.assertTrue(self.editor.is_empty())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_insert_table")
    def test_insert_table(self):
        diff(self.text.toHtml())
        table = self.editor.view.toolbar.controls["table"]
        self.test.mouse_click(table, QPoint(1, 1))
        self.test.mouse_click(table._colors_widget._clrbtn[35], QPoint(1, 1))
        changed = diff(self.text.toHtml())
        self.test.sleep()
        self.assertTrue('table' in changed["add"])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_insert_image")
    def test_insert_image(self):
        diff(self.text.toHtml())
        self.test.wrd_click(self.text, "!!!")

        image = self.editor.view.toolbar.controls["image"]
        with patch.object(QFileDialog, "exec_", returning_value=True):
            self.test.mouse_click(image, QPoint(1, 1))
        changed = diff(self.text.toHtml())
        self.assertTrue('image' in changed["add"])
        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_insert_from_mime_data")
    def test_insert_from_mime_data(self):

        # ------------------------------------------
        class TstSource:

            # noinspection PyPep8Naming
            @staticmethod
            def hasImage():
                return True

            @staticmethod
            def formats():
                return ["image/png"]

            # noinspection PyPep8Naming
            @staticmethod
            def imageData():
                return QImage()
        # ------------------------------------------

        diff(self.text.toHtml())
        with patch.object(sys, 'platform', "windows"):
            self.editor._insert_from_mime_data(TstSource())
        changed = diff(self.text.toHtml())
        self.assertTrue('image' in changed["add"])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_change_image_size")
    def test_change_image_size(self):
        diff(self.text.toHtml())
        param = (QImage(), 123, 1, "png",)
        with patch.object(ImageSize, "exec_", returning_value=True):
            self.editor._change_image_size(param)
        changed = diff(self.text.toHtml())
        self.assertTrue('width="123"' in changed["add"])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_fix_word")
    def test_fix_word(self):
        self.editor._cursor_fix_word = True
        self._cursor_to_change_word = self.text.textCursor()
        word = "FIX-WORD"
        diff(self.text.toHtml())
        self.editor._fix_word(word)
        changed = diff(self.text.toHtml())
        self.assertTrue(word in changed["add"])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_add_word_to_spell")
    def test_add_word_to_spell(self):
        ok = []

        def effect(res):
            res.append("OK")

        self.assertEqual(len(ok), 0)
        with patch.object(self.editor, '_rehighlight',
                          side_effect=lambda: effect(ok)):
            self.editor._add_word_to_spell("hello")

        self.assertEqual(len(ok), 1)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_rehighlight")
    def test_rehighlight(self):
        ok = []

        def effect(res):
            res.append("OK")

        self.assertEqual(len(ok), 0)
        with patch.object(self.editor._highlighter_cls, 'rehighlight',
                          side_effect=lambda: effect(ok)):
            self.editor._rehighlight()

        self.assertEqual(len(ok), 1)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_clear_highlighter")
    def test_clear_highlighter(self):
        ok = []

        def effect(res):
            res.append("OK")

        self.assertEqual(len(ok), 0)
        with patch.object(self.editor._highlighter_cls, 'setDocument',
                          side_effect=lambda x: effect(ok)):
            self.editor._clear_highlighter()

        self.assertEqual(len(ok), 1)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_format_text")
    def test_set_format_text(self):
        diff(self.text.toHtml())
        self.editor.doc.insert_table(
            {"padding": 0, "space": 0, "rows": 3, "cols": 2})
        changed = diff(self.text.toHtml())
        self.assertTrue('table' in changed["add"])

        self.test.sleep()
        diff(self.text.toHtml())
        self.editor._set_format_text()
        changed = diff(self.text.toHtml())
        self.assertTrue('table' in changed["del"])
        self.test.sleep()

        self.editor._set_format_html()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_enabled_save")
    def test_enabled_save(self):
        old = self.editor.view.toolbar.controls["save"].isVisible()
        self.editor.set_option(auto_save=0)
        self.editor._enabled_save(False)

        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_clicks(self.text, "asdasdasd")

        self.assertTrue(self.editor._doc.is_modified())
        self.editor.set_option(auto_save=1)
        self.editor._enabled_save(True)
        self.assertFalse(self.editor._doc.is_modified())

        self.editor._enabled_save(old)
        self.editor.set_option(btn_save_visible=True)
