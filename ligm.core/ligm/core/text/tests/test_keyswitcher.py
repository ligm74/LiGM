#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for  KeySwitcher."""

import unittest
from unittest.mock import patch
from PyQt5.Qt import QHBoxLayout, Qt, QKeyEvent, QEvent, QPoint
from ligm.core.qt import QTestHelper, TestableWidget
from ligm.core.text.editor import TextEditor
from ligm.core.text.spell import SpellChecker
from ligm.core.text.keyswitcher import KeySwitcherParams
from ligm.core.common import SimpleConfig as Config


DEBUG = QTestHelper().start_tests()


# =============================================================================
class KeySwitcherTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.test = QTestHelper()

        # ---------------------------------------------------------------------
        # customize editor
        # noinspection PyUnusedLocal
        def save(txt):   # pragma: no cover
            return None

        def load():
            return "HELLO hello1 hell привет приве 2"      # i18n

        cls.widget = TestableWidget(None)
        cls.editor = TextEditor(cls.widget, Config(), save=save, load=load,
                                spell=SpellChecker(enabled=True),
                                auto_load=True, auto_key_switch=True)
        cls.keyswitcher = cls.editor._keyswitcher
        cls.spell = cls.editor._spell

        # ---------------------------------------------------------------------
        # customize the widget for placement
        layout = QHBoxLayout()
        layout.addWidget(cls.editor, alignment=Qt.Alignment())
        cls.widget.setLayout(layout)
        cls.widget.resize(800, 450)
        cls.widget.move(800, 150)

        cls.test.show_and_wait_for_active(cls.widget)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_key_press")
    def test_key_press(self):
        self.text = self.editor._view.text
        self.test.sleep()

        # ---------------------------------------------------------------------
        # Qt.Key_L
        key_event = QKeyEvent(QEvent.KeyPress, Qt.Key_L, Qt.ControlModifier,
                              "", False)
        self.spell._enabled_all = False
        result = self.keyswitcher.key_press(key_event)
        self.assertEqual(result, [])
        self.spell._enabled_all = True

        # ---------------------------------------------------------------------
        def key_switcher_params(widget):
            test = QTestHelper()
            test.sleep()
            test.mouse_click(widget.controls[-1], QPoint(1, 1))

        self.test.handle_modal_widget(key_switcher_params)
        result = self.keyswitcher.key_press(key_event)
        self.assertEqual(result, [])
        self.test.sleep(1)

        # ---------------------------------------------------------------------
        # Qt.Key_F12
        self.test.wrd_d_click(self.editor._view.text, "hello1")
        self.test.sleep(1)
        key_event = QKeyEvent(QEvent.KeyPress, Qt.Key_F12, Qt.NoModifier,
                              "", False)
        point = self.test.get_xy_for_word(self.editor._view.text, "hello1")
        x = point.x()
        self.assertTrue(x)
        result = self.keyswitcher.key_press(key_event)
        self.assertEqual(result, [])

        point = self.test.get_xy_for_word(self.editor._view.text, "hello1")
        self.assertFalse(point.x())
        point = self.test.get_xy_for_word(
            self.editor._view.text, "руддщ1")     # i18n
        self.assertEqual(point.x(), x)

        # no selection -> no change
        cursor = self.text.textCursor()
        cursor.clearSelection()
        self.text.setTextCursor(cursor)
        self.keyswitcher._replace_selection()
        self.assertEqual(point.x(), x)
        self.test.sleep(1)

        # ---------------------------------------------------------------------
        # not enabled keyswitcher
        key_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Backspace, Qt.NoModifier,
                              "", False)
        self.keyswitcher._enabled = False
        result = self.keyswitcher.key_press(key_event)
        self.assertEqual(result[0], key_event)

        # ---------------------------------------------------------------------
        # Qt.Key_Backspace
        self.keyswitcher._enabled = True
        self.test.wrd_d_click(self.editor._view.text, "2")
        self.test.sleep()
        self.editor._view.text.setFocus()
        self.editor._view.text.setFocus()
        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_clicks(self.text, " wo")
        self.test.sleep()
        self.assertEqual(self.keyswitcher._current_word, "wo")
        self.test.sleep()
        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_click(self.text, Qt.Key_Backspace)
        self.assertEqual(result[0], key_event)
        self.assertEqual(self.keyswitcher._current_word, "w")
        self.test.sleep()

        # ---------------------------------------------------------------------
        # not char
        key_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Up, Qt.NoModifier,
                              "", False)
        result = self.keyswitcher.key_press(key_event)
        self.assertEqual(result[0], key_event)
        self.assertEqual(self.keyswitcher._current_word, "")
        self.test.sleep()

        # ---------------------------------------------------------------------
        # char and there was mouse movement
        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_clicks(self.text, " wo")
        self.assertEqual(self.keyswitcher._current_word, "wo")
        self.test.wrd_click(self.editor._view.text, "")
        self.test.key_click(self.editor._view.text, Qt.Key_A, "A")
        self.assertEqual(self.keyswitcher._current_word, "")
        self.test.sleep()

        # ---------------------------------------------------------------------
        # add char to current word
        self.assertEqual(self.keyswitcher._current_lang, "ENG")
        self.test.wrd_d_click(self.editor._view.text, "wo")
        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_clicks(self.text, " a")
            self.test.key_clicks(self.text, "ф")      # i18n
        self.assertEqual(self.keyswitcher._current_word, "aa")
        self.test.sleep()

        # ---------------------------------------------------------------------
        # check switch lang
        self.test.wrd_d_click(self.editor._view.text, "aa")
        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_clicks(self.text, " 123")  # no switch
        self.test.sleep()

        self.test.wrd_d_click(self.editor._view.text, "123")
        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_clicks(self.text, " rybu")
        self.test.sleep()
        self.assertEqual(self.keyswitcher._current_word, "книг")  # i18n

        self.test.wrd_d_click(self.editor._view.text, "книг")  # i18n
        self.test.sleep()
        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_clicks(self.text, " рудд")  # i18n
        self.test.sleep()
        self.assertEqual(self.keyswitcher._current_word, "hell")

        # ---------------------------------------------------------------------
        self.keyswitcher.set_enabled(False)
        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_clicks(self.text, " фFфF")                 # i18n
        self.keyswitcher.set_enabled(True)
        self.keyswitcher._current_word = "фFфF"                      # i18n
        with patch.object(self.text, 'hasFocus', return_value=True):
            self.test.key_clicks(self.text, "1")
        self.assertEqual(self.keyswitcher._current_word, "фFфF1")    # i18n
        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_switch_charset")
    def test_switch_charset(self):
        self.assertEqual(self.keyswitcher.switch_charset("ghbdtn"),
                         "привет")  # i18n

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_current_lang")
    def test_current_lang(self):
        self.assertEqual(self.keyswitcher.current_lang(), "ENG")

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_current_lang")
    def test_set_current_lang(self):
        self.keyswitcher.set_current_lang("RUS")
        self.assertEqual(self.keyswitcher.current_lang(), "RUS")

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_enabled")
    def test_enabled(self):
        self.assertTrue(self.keyswitcher.enabled())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_enabled")
    def test_set_enabled(self):
        self.keyswitcher.set_enabled(False)
        self.assertFalse(self.keyswitcher.enabled())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_init_ui")
    def test_init_ui(self):
        tt = KeySwitcherParams()

        # ---------------------------------------------------------------------
        def key_switcher_params(widget):
            test = QTestHelper()
            test.sleep()
            test.mouse_click(widget.controls[-1], QPoint(1, 1))

        self.test.handle_modal_widget(key_switcher_params)
        tt.exec_()

        self.assertEqual(len(tt.controls), 4)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_apply")
    def test_apply(self):
        tt = KeySwitcherParams()

        # ---------------------------------------------------------------------
        def key_switcher_params(widget):
            test = QTestHelper()
            test.sleep()
            widget.apply()

        self.test.handle_modal_widget(key_switcher_params)
        tt.exec_()

        self.assertEqual(len(tt.controls), 4)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_ok_locale")
    def test_ok_locale(self):
        self.assertTrue(self.keyswitcher._ok_locale("HELL", "РУДД"))     # i18n
        self.assertTrue(self.keyswitcher._ok_locale("hello", "руддщ"))   # i18n
        self.assertTrue(self.keyswitcher._ok_locale("HELL1", "РУДД1"))   # i18n

        self.assertFalse(self.keyswitcher._ok_locale("РУДД", "HELL"))    # i18n
        self.assertFalse(self.keyswitcher._ok_locale("руддщ", "hello"))  # i18n
        self.assertFalse(self.keyswitcher._ok_locale("РУДД1", "HELL1"))  # i18n
