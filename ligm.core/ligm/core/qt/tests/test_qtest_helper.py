#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for functions to work with Qt."""

import unittest
from ligm.core.qt import QTestHelper, diff


DEBUG = QTestHelper().start_tests()


# =============================================================================
class QTestHelperTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_is_interactive")
    def test_is_interactive(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_install_translators")
    def test_is_debug(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_start_tests")
    def test_start_tests(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_interactive")
    def test_set_interactive(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_debug")
    def test_set_debug(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_sleep")
    def test_sleep(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_key_click")
    def test_key_click(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_qtest_key_click")
    def test_qtest_key_click(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_key_clicks")
    def test_key_clicks(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_mouse_move")
    def test_mouse_move(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_mouse_click")
    def test_mouse_click(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_mouse_dbl_click")
    def test_mouse_dbl_click(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_install_translators")
    def test_show_and_wait_for_active(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get_xy_for_word")
    def test_get_xy_for_word(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_handle_modal_widget")
    def test_handle_modal_widget(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_handle_popup_widget")
    def test_handle_popup_widget(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_wrd_click")
    def test_wrd_click(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_wrd_d_click")
    def test_wrd_d_click(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_diff")
    def test_diff(self):
        diff("Hello")
        change = diff("HELLO")
        self.assertEqual(change["add"], "ELLO")
        self.assertEqual(change["del"], "ello")
