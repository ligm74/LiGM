#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for GUI interface of embeddable text editor."""

import unittest
from unittest.mock import patch
from PyQt5.Qt import Qt, QTextEdit, QPainter
from ligm.core.text.editor.view import View, StatusBar, LineNumberArea, ImageSize
from ligm.core.text.editor.instable import TableParamsDlg
from ligm.core.common import SimpleConfig as Config
from ligm.core.qt import QTestHelper, TestableWidget


DEBUG = QTestHelper().start_tests()


# =============================================================================
class ViewTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_init_ui")
    def test_init_ui(self):
        v = View(TestableWidget(None), Config())
        # init_ui() called in constructor of class View
        self.assertEqual(len(v.cursors), 2)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_update_ui")
    def test_update_ui(self):
        cfg = Config()
        w = TestableWidget(None)
        v = View(w, cfg, margins=(0, 0, 0, 0))

        QTestHelper().show_and_wait_for_active(w)

        cfg["TextEditor/WordWrap"] = 0
        v.update_ui()
        self.assertEqual(v.text.lineWrapMode(), QTextEdit.NoWrap)

        cfg["TextEditor/WordWrap"] = 1
        v.update_ui()
        self.assertEqual(v.text.lineWrapMode(), QTextEdit.WidgetWidth)

        cfg["TextEditor/PlainText"] = 1
        v.update_ui()
        self.assertEqual(v.text.acceptRichText(), False)

        cfg["TextEditor/PlainText"] = 0
        v.update_ui()
        self.assertEqual(v.text.acceptRichText(), True)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_scroll_contents_by")
    def test_scroll_contents_by(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_contents_change")
    def test_contents_change(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_resize_event")
    def test_resize_event(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_highlight_cur_line")
    def test_highlight_cur_line(self):
        cfg = Config()
        v = View(TestableWidget(None), cfg)

        cfg["TextEditor/HighlightCurrentLine"] = 0
        v.contents_change()
        self.assertEqual(len(v.text.extraSelections()), 0)

        cfg["TextEditor/HighlightCurrentLine"] = 1
        v.highlight_cur_line()
        self.assertEqual(len(v.text.extraSelections()), 1)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_show_hide_search_panel")
    def test_show_hide_search_panel(self):
        cfg = Config()
        w = TestableWidget(None)
        v = View(w, cfg)

        QTestHelper().show_and_wait_for_active(w)
        w.resize(100, 100)
        w.move(100, 500)

        self.assertFalse(v.search_replace.isVisible())
        v.show_hide_search_panel(Qt.Key_F)
        self.assertTrue(v.search_replace.only_search)
        v.show_hide_search_panel(Qt.Key_R)
        self.assertFalse(v.search_replace.only_search)
        self.assertTrue(v.search_replace.isVisible())
        v.show_hide_search_panel(Qt.Key_Escape)
        self.assertFalse(v.search_replace.isVisible())

        v.show_hide_search_panel(Qt.Key_R)
        self.assertFalse(v.search_replace.only_search)
        v.show_hide_search_panel(Qt.Key_R)
        self.assertFalse(v.search_replace.isVisible())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_retranslate_ui")
    def test_retranslate_ui(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_show_info")
    def test_show_info(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_paint")
    def test_paint(self):
        ok = []

        # noinspection PyUnusedLocal
        def effect(*args, **kwargs):
            ok.append("OK")

        cfg = Config()
        cfg["TextEditor/PlainText"] = 1
        cfg["TextEditor/MarginLine"] = 1
        w = TestableWidget(None)
        View(w, cfg)
        QTestHelper().show_and_wait_for_active(w)

        with patch.object(QPainter, 'drawLine',
                          side_effect=effect):
            w.repaint()

        self.assertTrue(ok)
        self.assertEqual(ok[-1], "OK")


# =============================================================================
class StatusBarTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set")
    def test_set(self):
        sb = StatusBar()
        sb.set({"left": "kk"})
        self.assertEqual(sb.controls["left"].text(), "kk")


# =============================================================================
class LineNumberAreaTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_paintEvent")
    def test_paintEvent(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_width")
    def test_width(self):
        cfg = Config()
        e = QTextEdit()
        ln = LineNumberArea(e, cfg)

        cfg["TextEditor/ShowLineNumbers"] = 1
        self.assertTrue(ln.width() > 0)
        cfg["TextEditor/ShowLineNumbers"] = 0
        self.assertTrue(ln.width() == 0)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_resize")
    def test_resize(self):
        pass


# =============================================================================
class SearchAndReplaceBarTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_visible")
    def test_set_visible(self):
        cfg = Config()
        w = TestableWidget(None)
        v = View(w, cfg)

        QTestHelper().show_and_wait_for_active(w)
        w.resize(100, 100)
        w.move(100, 500)

        self.assertFalse(v.search_replace.isVisible())
        v.search_replace.set_visible(True)
        self.assertTrue(v.search_replace.isVisible())


# =============================================================================
class TableTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_insert")
    def test_insert(self):
        t = TableParamsDlg(config=Config())
        self.assertFalse(len(t.table_params))

        t.insert()

        t.controls[0].setValue(1)
        t.controls[1].setValue(1)
        t.insert()
        self.assertEqual(len(t.table_params), 4)


# =============================================================================
class BalloonWidgetTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_show_msg")
    def test_show_msg(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_mousePressEvent")
    def test_mousePressEvent(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_keyPressEvent")
    def test_keyPressEvent(self):
        pass


# =============================================================================
class ImageSizeTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_change")
    def test_change(self):
        w, h = 800, 600
        t = ImageSize(None, 400, 300, w, h)

        QTestHelper().show_and_wait_for_active(t)
        QTestHelper().sleep()

        nw = 8
        t.controls[0].setValue(nw)
        QTestHelper().sleep()
        self.assertEqual(t.controls[1].value(), h * nw // w)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_change_image")
    def test_change_image(self):
        w, h = 800, 600
        t = ImageSize(None, 400, 300, w, h)

        QTestHelper().show_and_wait_for_active(t)
        QTestHelper().sleep()

        nw = 8
        t.controls[0].setValue(nw)
        QTestHelper().sleep()

        t.change_button.click()

        self.assertEqual(t.params["width"], nw)
        self.assertEqual(t.params["height"], h * nw // w)

        # --------------------
        t = ImageSize(None, 400, 300, w, h)

        QTestHelper().show_and_wait_for_active(t)
        QTestHelper().sleep()

        nw = 8
        t.controls[1].setValue(nw)
        QTestHelper().sleep()

        t.change_button.click()

        QTestHelper().sleep()
        self.assertEqual(t.params["width"], nw * w // h)
        self.assertEqual(t.params["height"], nw)

        # --------------------
        t = ImageSize(None, 400, 300, w, h)

        QTestHelper().show_and_wait_for_active(t)
        QTestHelper().sleep()

        t.controls[2].setChecked(False)
        t.controls[0].setValue(20)
        t.controls[1].setValue(10)
        QTestHelper().sleep()

        t.change_button.click()

        QTestHelper().sleep()
        self.assertEqual(t.params["width"], 20)
        self.assertEqual(t.params["height"], 10)
