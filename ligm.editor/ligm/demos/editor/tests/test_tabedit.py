#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for tab of editable file."""

import os
import unittest
from unittest.mock import patch
from PyQt5.Qt import QMessageBox, QTextEdit, Qt
from ligm.demos.editor.tabedit import TabEdit
from ligm.demos.editor import Config
from ligm.core.qt import (install_translators, get_current_language, QTestHelper,
                     TestableWidget)


DEBUG = QTestHelper().start_tests()


# =============================================================================
class TabEditTest(unittest.TestCase):

    _INTERACTIVE = False

    # -------------------------------------------------------------------------
    def setUp(self):
        """
        Create the GUI
        """
        self.w = TestableWidget(None)
        self.w.cfg = Config()
        self.te = TabEdit(self.w)
        self.te.setAttribute(Qt.WA_DontShowOnScreen)

    # -------------------------------------------------------------------------
    def tearDown(self):
        self.w.close()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_read_only")
    def test_set_read_only(self):
        self.assertFalse(self.te._editor.view.text.isReadOnly())
        self.te.set_read_only(True)
        self.assertTrue(self.te._editor.view.text.isReadOnly())
        self.te.set_read_only(False)
        self.assertFalse(self.te._editor.view.text.isReadOnly())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_is_read_only")
    def test_is_read_only(self):
        self.assertFalse(self.te.is_read_only())
        self.te.set_read_only(True)
        self.assertTrue(self.te.is_read_only())
        self.te.set_read_only(False)
        self.assertFalse(self.te.is_read_only())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_focus")
    def test_set_focus(self):
        self.te.set_focus()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_invisible_symbol")
    def test_set_invisible_symbol(self):
        is_checked = self.te._editor._actions["invisible-symbol"].isChecked
        self.assertFalse(is_checked())
        self.te.set_invisible_symbol()
        self.assertTrue(is_checked())
        self.te.set_invisible_symbol()
        self.assertFalse(is_checked())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_text_format")
    def test_set_text_format(self):
        branch = "TextEditor/"
        self.assertFalse(self.te._editor._cfg.get(f"{branch}PlainText", 1))
        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.Yes):
            self.te.set_text_format("text")
        self.assertTrue(self.te._editor._cfg.get(f"{branch}PlainText", 1))
        self.te.set_text_format("hTmL")
        self.assertFalse(self.te._editor._cfg.get(f"{branch}PlainText", 1))
        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.Yes):
            self.te.set_text_format("")  # text
        self.assertTrue(self.te._editor._cfg.get(f"{branch}PlainText", 1))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_highlighter")
    def test_set_highlighter(self):
        self.assertEqual(self.te._editor._highlighter, "")
        self.te.set_highlighter("XXX")
        self.assertEqual(self.te._editor._highlighter, "")
        self.te.set_highlighter("Python")
        self.assertEqual(self.te._editor._highlighter, "Python")
        self.te.set_highlighter("SQL")
        self.assertEqual(self.te._editor._highlighter, "SQL")

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get_word_wrap")
    def test_get_word_wrap(self):
        c = self.te._editor._view.text.lineWrapMode() == QTextEdit.WidgetWidth
        self.assertEqual(c, self.te.get_word_wrap())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_word_wrap")
    def test_set_word_wrap(self):
        c = self.te._editor._view.text.lineWrapMode() == QTextEdit.WidgetWidth
        c_no = self.te._editor._view.text.lineWrapMode() == QTextEdit.NoWrap
        self.assertEqual(c, self.te.get_word_wrap())
        self.te.set_word_wrap()
        self.assertEqual(c_no, self.te.get_word_wrap())
        self.te.set_word_wrap()
        self.assertEqual(c, self.te.get_word_wrap())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_file_path")
    def test_file_path(self):
        self.assertIsNone(self.te.file_path())
        te = TabEdit(self.w, "PATH")
        self.assertEqual(te.file_path(), "PATH")

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_is_modified")
    def test_is_modified(self):
        self.assertFalse(self.te.is_modified())
        self.te._editor.doc.text.setModified(True)
        self.te._editor.enabled_save_signal.emit(True)
        self.assertTrue(self.te.is_modified())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_text_format")
    def test_text_format(self):
        self.assertEqual(self.te.text_format(), "HTML")
        self.assertEqual(self.te.text_format(False), "HTML")

        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.Yes):
            self.te.set_text_format("text")

        self.assertEqual(self.te.text_format(), "TEXT")
        self.assertEqual(self.te.text_format(False), "HTML")

        self.te.set_text_format("hTmL")

        self.assertEqual(self.te.text_format(), "HTML")
        self.assertEqual(self.te.text_format(False), "HTML")

        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.Yes):
            self.te.set_text_format("")  # text

        self.assertEqual(self.te.text_format(), "TEXT")
        self.assertEqual(self.te.text_format(False), "HTML")

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_highlighter")
    def test_highlighter(self):
        self.assertEqual(self.te._editor._highlighter, "")
        self.assertEqual(self.te.highlighter(), "")
        self.te.set_highlighter("XXX")
        self.assertEqual(self.te._editor._highlighter, "")
        self.assertEqual(self.te.highlighter(), "XXX")
        self.te.set_highlighter("Python")
        self.assertEqual(self.te._editor._highlighter, "Python")
        self.assertEqual(self.te.highlighter(), "Python")
        self.te.set_highlighter("SQL")
        self.assertEqual(self.te._editor._highlighter, "SQL")
        self.assertEqual(self.te.highlighter(), "SQL")

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_enabled_save")
    def test_set_enabled_save(self):
        self.assertFalse(self.te.is_modified())
        self.te.set_enabled_save(True)
        self.assertTrue(self.te.is_modified())
        self.te.set_enabled_save(False)
        self.assertFalse(self.te.is_modified())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get_path")
    def test_get_path(self):
        self.assertIsNone(self.te.file_path())
        self.assertEqual(self.te.get_path(), "")
        te = TabEdit(self.w, __file__)
        self.assertEqual(te.get_path(), os.path.dirname(__file__))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get_name")
    def test_get_name(self):
        install_translators("en_EN")
        self.assertEqual(self.te.get_name(), "Untitled")
        self.te.set_enabled_save(True)
        self.assertEqual(self.te.get_name(), "* Untitled")

        te = TabEdit(self.w, __file__)
        self.assertEqual(te.get_name(), os.path.basename(__file__))
        te.set_enabled_save(True)
        self.assertEqual(te.get_name(), "* " + os.path.basename(__file__))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_retranslate_ui")
    def test_retranslate_ui(self):
        # noinspection PyBroadException
        try:
            self.te.retranslate_ui()
        except Exception:  # pragma: no cover
            self.fail('unexpected exception raised')

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_save")
    def test_save(self):  # pragma: no cover
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get_filename_for_save")
    def test_get_filename_for_save(self):  # pragma: no cover
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_save_as")
    def test_save_as(self):  # pragma: no cover
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_is_help_text")
    def test_is_help_text(self):  # pragma: no cover
        path = os.path.join(os.path.dirname(__file__), "../doc")
        path = os.path.realpath(path)
        lang = "." + get_current_language()
        filepath = f"{path}{os.sep}demoedit{lang}.html"
        if not os.path.exists(filepath):
            filepath = f"{path}{os.sep}demoedit.html"
        if not os.path.exists(filepath):
            self.fail()
        te = TabEdit(self.w, filepath)
        self.assertEqual(te.is_help_text(), True)
