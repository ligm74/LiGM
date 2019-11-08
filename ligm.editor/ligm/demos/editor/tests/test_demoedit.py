#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for demo for embedded text editor."""

import unittest
from unittest.mock import patch
from PyQt5.Qt import QMessageBox, QFileDialog, QTextOption, QPoint, Qt
from ligm.demos.editor.tabedit import TabEdit
from ligm.demos.editor.demoedit import MainWindow
from ligm.core.qt import install_translators, QTestHelper


DEBUG = QTestHelper().start_tests()


# =============================================================================
class DemoEditTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """
        Create the GUI
        """
        cls.m = MainWindow(test_mode=True)
        cls.m.setAttribute(Qt.WA_DontShowOnScreen)

    # -------------------------------------------------------------------------
    def tearDown(self):
        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.No):
            for i in range(self.m._tabs.count() - 1):
                self.m.close_tab(i)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_retranslate_ui")
    def test_retranslate_ui(self):

        self.m.help()
        for i in range(self.m._tabs.count()):
            if self.m._tabs.widget(i).is_help_text():
                self.m.close_tab(i)
                break

        install_translators("en_EN")
        self.m.retranslate_ui()
        self.assertEqual(self.m._menus["file"].title(), "&File")
        install_translators("ru_RU")
        self.m.retranslate_ui()
        self.assertEqual(self.m._menus["file"].title(), "&Файл")  # i18n

        self.m.help()

        install_translators("en_EN")
        self.m.retranslate_ui()
        self.assertEqual(self.m._menus["file"].title(), "&File")
        install_translators("ru_RU")
        self.m.retranslate_ui()
        self.assertEqual(self.m._menus["file"].title(), "&Файл")  # i18n

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_lang")
    def test_set_lang(self):
        self.m.set_lang("en_EN")
        self.assertEqual(self.m._menus["file"].title(), "&File")
        self.m.set_lang("ru_RU")
        self.assertEqual(self.m._menus["file"].title(), "&Файл")  # i18n

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_read_only")
    def test_read_only(self):
        cnt = self.m._tabs.count()
        self.m.open_file()
        self.assertEqual(self.m._tabs.widget(cnt).is_read_only(), False)
        self.m._read_only()
        self.assertEqual(self.m._tabs.widget(cnt).is_read_only(), True)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_word_wrap")
    def test_word_wrap(self):
        cnt = self.m._tabs.count()
        self.m.open_file()
        self.assertEqual(self.m._tabs.widget(cnt).get_word_wrap(), True)
        self.m.word_wrap()
        self.assertEqual(self.m._tabs.widget(cnt).get_word_wrap(), False)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_closeEvent")
    def test_closeEvent(self):
        cnt = self.m._tabs.count()
        self.m.open_file()
        self.assertEqual(self.m._tabs.count(), cnt + 1)

        self.m.close()
        # self.m._tabs.count()  # why no exceptions ????

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_save_text_tab")
    def test_save_text_tab(self):
        cnt = self.m._tabs.count()
        self.m.open_file()
        self.m._tabs.widget(cnt)._editor._actions["hline"].trigger()

        ok = []

        def effect(res):
            res.append("OK")

        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.Yes):
            with patch.object(TabEdit, 'save', side_effect=lambda: effect(ok)):
                self.m.save_text_tab(cnt)

        self.assertEqual(ok, ["OK"])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_close_tab")
    def test_close_tab(self):
        cnt = self.m._tabs.count()
        self.m.open_file()
        self.assertEqual(self.m._tabs.count(), cnt + 1)
        self.m.close_tab(cnt)
        self.assertEqual(self.m._tabs.count(), cnt)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_change_tab")
    def test_change_tab(self):
        cnt = self.m._tabs.count()
        self.m.open_file()
        self.m.open_file()

        w = self.m._tabs.widget(cnt + 1)
        self.assertEqual(self.m._actions["save"].isEnabled(), False)
        w._editor._actions["hline"].trigger()
        self.assertEqual(self.m._actions["save"].isEnabled(), True)

        self.m.change_tab(cnt)
        self.assertEqual(self.m._actions["save"].isEnabled(), False)
        self.m.change_tab(cnt + 1)
        self.assertEqual(self.m._actions["save"].isEnabled(), True)

        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.No):
            self.m.save_text_tab(cnt + 1)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_change_enabled_save")
    def test_change_enabled_save(self):
        pass  # checked previous test (test_change_tab)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_about")
    def test_about(self):
        cnt = self.m._tabs.count()
        self.m.open_file()
        self.m._tabs.widget(cnt)._editor._actions["hline"].trigger()

        ok = []

        def effect(res):
            res.append("OK")

        with patch.object(QMessageBox, 'about',
                          return_value=QMessageBox.Ok,
                          side_effect=lambda x, y, z: effect(ok)):
            self.m.about()

        self.assertEqual(ok, ["OK"])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_format")
    def test_set_format(self):
        cnt = self.m._tabs.count()
        self.m.open_file()
        w = self.m._tabs.widget(cnt)
        self.m.change_tab(cnt)

        self.assertEqual(w.text_format(), "HTML")

        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.Yes):
            self.m.set_format("text")

        self.assertEqual(w.text_format(), "TEXT")

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_syntax")
    def test_set_syntax(self):
        cnt = self.m._tabs.count()
        self.m.open_file()
        w = self.m._tabs.widget(cnt)
        self.m.change_tab(cnt)

        self.assertEqual(w.highlighter(), "")
        self.m.set_syntax("Python")
        self.assertEqual(w.highlighter(), "Python")

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_invisible_symbol")
    def test_set_invisible_symbol(self):
        cnt = self.m._tabs.count()
        self.m.open_file()
        w = self.m._tabs.widget(cnt)
        self.m.change_tab(cnt)

        def status():
            f = w._editor.doc._text.defaultTextOption().flags()
            return bool(f & QTextOption.ShowTabsAndSpaces)

        self.assertEqual(status(), False)
        self.m.set_invisible_symbol()
        self.assertEqual(status(), True)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_read_settings")
    def test_read_settings(self):
        x, y = self.m.pos().x(), self.m.pos().y()
        self.m.move(QPoint(0, 0))
        self.assertEqual(self.m.pos().x(), 0)
        self.m.read_settings()
        self.assertEqual(self.m.pos().x(), x)
        self.assertEqual(self.m.pos().y(), y)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_write_settings")
    def test_write_settings(self):
        x, y = self.m.pos().x(), self.m.pos().y()
        self.m.move(QPoint(0, 0))
        self.m.write_settings()
        self.assertEqual(self.m.pos().x(), 0)
        self.m.read_settings()
        self.assertEqual(self.m.pos().x(), 0)
        self.m.move(QPoint(x, y))
        self.m.write_settings()
        self.assertEqual(self.m.pos().x(), x)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_open_file")
    def test_open_file(self):
        pass  # checked earlier

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_save")
    def test_save(self):
        cnt = self.m._tabs.count()
        self.m.open_file()
        self.m.change_tab(cnt)

        ok = []

        def effect(res):
            res.append("OK")

        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.Yes):
            with patch.object(TabEdit, 'save', side_effect=lambda: effect(ok)):
                self.m.save()

        self.assertEqual(ok, ["OK"])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_start")
    def test_start(self):
        pass  # no need test for Main.start

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_saveas")
    def test_saveas(self):
        cnt = self.m._tabs.count()
        self.m.open_file()
        self.m.change_tab(cnt)

        ok = []

        def effect(res):
            res.append("OK")

        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.Yes):
            with patch.object(TabEdit, 'save_as',
                              side_effect=lambda: effect(ok)):
                self.m.saveas()

        self.assertEqual(ok, ["OK"])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_open")
    def test_open(self):
        ok = []

        def effect(res):
            res.append("OK")

        with patch.object(QFileDialog, 'exec_',
                          return_value=True):
            with patch.object(MainWindow, 'open_file',
                              side_effect=lambda path, fmt, hl: effect(ok)):
                self.m.open()

        self.assertEqual(ok, ["OK"])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_help")
    def test_help(self):

        def check_is_help():
            ok = False
            for ii in range(self.m._tabs.count()):
                ok |= self.m._tabs.widget(ii).is_help_text()
            return ok

        self.m.help()
        self.m.help()
        self.assertEqual(check_is_help(), True)

        for i in range(self.m._tabs.count()):
            if self.m._tabs.widget(i).is_help_text():
                self.m.close_tab(i)
                break
        self.assertEqual(check_is_help(), False)

        self.m.help()
        self.assertEqual(check_is_help(), True)
