#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for demonstrate QTestHelper."""

import unittest
from PyQt5.Qt import QPoint
from ligm.core.qt.simple import Example
from ligm.core.qt.qtest_helper import QTestHelper


DEBUG = QTestHelper().start_tests()


# =============================================================================
class ExampleTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        pass

    # -------------------------------------------------------------------------
    def setUp(self):
        self.test = QTestHelper()

        self.w = Example()
        self.test.show_and_wait_for_active(self.w)

    # -------------------------------------------------------------------------
    def tearDown(self):
        self.w.close()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_example")
    def test_example(self):

        # ---------------------------------------------------------------------
        def check(txt):
            return txt == self.w.text.toPlainText().split("\n")[1]

        # ---------------------------------------------------------------------
        # select word "CORRECT"
        pos = self.test.get_xy_for_word(self.w.text, "CORRECT")
        self.test.mouse_dbl_click(self.w.text.viewport(), pos, delay=1)

        # ---------------------------------------------------------------------
        # click Message Box and select Cancel button
        def click_cancel(widget):
            test = QTestHelper()
            test.sleep()
            btn = [b for b in widget.buttons()
                   if "Cancel" in b.text() or "Отмена" in        # i18n
                   b.text().replace("&", "")][0]
            test.mouse_click(btn, QPoint(1, 1))
            self.assertEqual(widget.text(), "CORRECT")

        self.test.handle_modal_widget(click_cancel)
        self.test.mouse_click(self.w.btn_msgbox, QPoint(1, 1))
        self.assertTrue(check("CORRECT:"))
        self.test.sleep()

        # ---------------------------------------------------------------------
        # click Message Box and select OK button
        def click_ok(widget):
            test = QTestHelper()
            test.sleep()
            btn = [b for b in widget.buttons() if "OK" in b.text()][0]
            test.mouse_click(btn, QPoint(1, 1))

        self.test.handle_modal_widget(click_ok)
        self.test.mouse_click(self.w.btn_msgbox, QPoint(1, 1))
        self.assertTrue(check("ERROR for computers:"))
        self.test.sleep()

        # ---------------------------------------------------------------------
        # select word "ERROR"
        self.test.mouse_dbl_click(self.w.text.viewport(), pos, delay=1)

        # ---------------------------------------------------------------------
        def click_hello(widget):
            test = QTestHelper()
            test.sleep()
            test.mouse_click(widget.btn_cancel, QPoint(1, 1))

        self.test.handle_modal_widget(click_hello)
        self.test.mouse_click(self.w.btn_mydlg, QPoint(1, 1))

        # ---------------------------------------------------------------------
        # click MyDialog, press "Paraphrasing" and select OK button
        def click_hello(widget):
            test = QTestHelper()
            test.sleep()
            test.mouse_dbl_click(widget.text.viewport(), QPoint(1, 1), delay=1)
            test.key_clicks(widget.text, "Paraphrasing", delay=1)
            test.mouse_click(widget.btn_ok, QPoint(1, 1))

        self.test.handle_modal_widget(click_hello)
        self.test.mouse_click(self.w.btn_mydlg, QPoint(1, 1))
        self.assertTrue(check("Paraphrasing for computers:"))
        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_init_ui")
    def test_init_ui(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_msgbox")
    def test_msgbox(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_mydlg")
    def test_mydlg(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_ok")
    def test_ok(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_cancel")
    def test_cancel(self):
        pass
