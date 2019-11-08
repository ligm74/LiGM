#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for SpellChecker."""

import unittest
from ligm.core.qt.qtest_helper import QTestHelper
from ligm.core.text.spell import SpellChecker
from ligm.core.text.spell.spelldict import SpellDict


DEBUG = QTestHelper().start_tests()


# =============================================================================
class SpellCheckerTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.test = QTestHelper()

    # -------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        pass

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def tearDown(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_enabled")
    def test_enabled(self):
        c = SpellChecker()
        self.assertFalse(c.enabled("rus"))
        self.assertFalse(c.enabled("eng"))
        self.assertFalse(c.enabled("all"))

        c = SpellChecker(enabled=True)
        self.assertTrue(c.enabled("rus"))
        self.assertTrue(c.enabled("eng"))
        self.assertTrue(c.enabled("all"))
        self.assertFalse(c.enabled("---"))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_enabled")
    def test_set_enabled(self):
        c = SpellChecker()

        c.set_enabled("rus", True)
        self.assertFalse(c.enabled("rus"))
        c.set_enabled("eng", True)
        self.assertFalse(c.enabled("eng"))
        c.set_enabled("all", True)
        self.assertFalse(c.enabled("all"))

        c = SpellChecker(enabled=True)
        self.assertTrue(c.enabled("rus"))
        self.assertTrue(c.enabled("eng"))
        self.assertTrue(c.enabled("all"))
        self.assertFalse(c.enabled("---"))

        c.set_enabled("rus", False)
        self.assertFalse(c.enabled("rus"))
        c.set_enabled("eng", False)
        self.assertFalse(c.enabled("eng"))

        c.set_enabled("all", True)
        self.assertTrue(c.enabled("rus"))
        self.assertTrue(c.enabled("eng"))

        c.set_enabled("all", False)
        self.assertFalse(c.enabled("rus"))
        self.assertFalse(c.enabled("eng"))

        c = SpellChecker(enabled=True)
        change_enabled = []
        c.change_enabled.connect(lambda: change_enabled.append(1))
        c.set_enabled("rus", True)
        c.set_enabled("rus", True)
        self.assertEqual(len(change_enabled), 2)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_word_needs_no_verification")
    def test_word_needs_no_verification(self):
        c = SpellChecker()

        self.assertTrue(c.word_needs_no_verification(""))
        self.assertTrue(c.word_needs_no_verification("a"))

        c._enabled_all = False
        self.assertTrue(c.word_needs_no_verification("hello"))
        c._enabled_all = True

        c.set_enabled("eng", False)
        self.assertTrue(c.word_needs_no_verification("hello"))

        c.set_enabled("rus", False)
        self.assertTrue(c.word_needs_no_verification("hello_"))

        c.set_enabled("eng", True)
        self.assertFalse(c.word_needs_no_verification("hello"))

        self.assertTrue(c.word_needs_no_verification("1"))
        self.assertTrue(c.word_needs_no_verification("1.0"))
        self.assertTrue(c.word_needs_no_verification("1e-5"))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_check_word")
    def test_check_word(self):
        c = SpellChecker(enabled=True)

        self.assertTrue(c.check_word("HELLO"))
        self.assertFalse(c.check_word("ERR_ERR"))
        self.assertTrue(c.check_word("2.045E-25"))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_check_word_without_verification")
    def test_check_word_without_verification(self):
        c = SpellChecker(enabled=True)

        self.assertTrue(c.check_word_without_verification("HELLO"))
        c._enabled_all = False
        self.assertFalse(c.check_word_without_verification("HELLO"))

        c._man = SpellDict("man", enable_add=True)
        c.add_word("TTT")
        self.assertTrue(c.check_word("TTT"))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_candidates")
    def test_candidates(self):
        c = SpellChecker(enabled=True)
        candidates = list(c.candidates("hell1"))
        self.assertTrue("hell" in candidates)
        self.assertTrue("hello" in candidates)

        candidates = list(c.candidates("hel"))
        self.assertEqual(len(candidates), 15)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_add_word")
    def test_add_word(self):
        pass
