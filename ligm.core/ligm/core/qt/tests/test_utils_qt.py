#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for functions to work with Qt."""

import unittest
from unittest.mock import patch
from PyQt5.Qt import QMessageBox, QCoreApplication, QLocale
from ligm.core.qt import (install_translators, yes_no, msg, QTestHelper,
                     get_current_language)


DEBUG = QTestHelper().start_tests()


# =============================================================================
class UtilsQtTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_install_translators")
    def test_install_translators(self):
        install_translators("ru_RU")
        txt = QCoreApplication.translate("@default", "Question")
        self.assertEqual(txt, "Вопрос")  # i18n
        install_translators("en_EN")
        txt = QCoreApplication.translate("@default", "Question")
        self.assertEqual(txt, "Question")
        install_translators()
        if QLocale.system().name() == "ru_RU":
            txt = QCoreApplication.translate("@default", "Question")
            self.assertEqual(txt, "Вопрос")  # i18n

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_yes_no")
    def test_yes_no(self):
        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.No):
            self.assertFalse(yes_no("ffff"))

        with patch.object(QMessageBox, 'question',
                          return_value=QMessageBox.Yes):
            self.assertTrue(yes_no("ffff"))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_msg")
    def test_msg(self):
        with patch.object(QMessageBox, 'show',
                          return_value=QMessageBox.No):
            self.assertEqual(msg("ffff"), None)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get_current_language")
    def test_get_current_language(self):
        install_translators("ru_RU")
        self.assertEqual(get_current_language(), "ru_RU")
        install_translators("en_EN")
        self.assertEqual(get_current_language(), "en_EN")
        install_translators()
        if QLocale.system().name() == "ru_RU":
            self.assertEqual(get_current_language(), "ru_RU")
