#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for SpellDict."""

import os
import unittest
from ligm.core.qt.qtest_helper import QTestHelper
from ligm.core.text.spell.spelldict import SpellDict
from ligm.core.common import get_res_dir


DEBUG = QTestHelper().start_tests()


# =============================================================================
class SpellDictTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.test = QTestHelper()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_enabled")
    def test_enabled(self):
        c = SpellDict("")
        self.assertFalse(c.enabled())

        # file man.dic must be exists
        # but after installation it is not
        # c = SpellDict(f"{get_res_dir()}/dict/man")
        # self.assertTrue(c.enabled())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_ecoding")
    def test_ecoding(self):
        c = SpellDict("")
        self.assertEqual(c._encoding, "UTF-8")

        c = SpellDict(f"{get_res_dir()}/dict/en_US")
        self.assertEqual(c._encoding, "UTF-8")
        c = SpellDict(f"{get_res_dir()}/dict/russian-aot")
        self.assertEqual(c._encoding, "KOI8-R")
        c = SpellDict(f"{get_res_dir()}/dict/man")
        self.assertEqual(c._encoding, "UTF-8")

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_check_word")
    def test_check_word(self):
        c = SpellDict(f"{get_res_dir()}/dict/en_US")

        self.assertTrue(c.check_word("hello"))
        self.assertFalse(c.check_word("hello_"))
        self.assertFalse(c.check_word("12"))
        self.assertTrue(c.check_word("HELLO"))
        self.assertFalse(c.check_word("ERR_ERR"))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_add_word")
    def test_add_word(self):
        c = SpellDict("/no/bo/dict")
        self.assertFalse(c.check_word("HELLO"))
        c.add_word("HELLO")
        self.assertFalse(c.check_word("HELLO"))

        c = SpellDict("/no/bo/dict", enable_add=True)
        self.assertFalse(c.check_word("HELLO"))
        c.add_word("HELLO", auto_save=True)
        self.assertTrue(c.check_word("HELLO"))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_save")
    def test_save(self):   # pragma: no cover
        path = f"{os.path.dirname(__file__)}/dd"

        def del_files():
            if os.path.exists(f"{path}.dic"):
                os.remove(f"{path}.dic")
            if os.path.exists(f"{path}.aff"):
                os.remove(f"{path}.aff")

        del_files()
        c = SpellDict(path)
        c.save()

        if os.path.exists(f"{path}.dic"):
            self.fail()

        c = SpellDict(path, enable_add=True)
        c.save()

        if not os.path.exists(f"{path}.dic"):
            self.fail()

        del_files()
