#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Fake tests (made for report of coverage)."""

import unittest
from ligm.core.text import IEditor
from ligm.core.qt import QTestHelper


DEBUG = QTestHelper().start_tests()


# =============================================================================
class TestEditor(IEditor):

    # -------------------------------------------------------------------------
    def save(self):
        super().save()

    # -------------------------------------------------------------------------
    def load(self):
        super().load()

    # -------------------------------------------------------------------------
    def set_option(self, **options):
        super().set_option(**options)

    # -------------------------------------------------------------------------
    def get_option(self, name):
        super().get_option(name)

    # -------------------------------------------------------------------------
    def search(self, text="", show_msg=True):
        super().search(show_msg)

    # -------------------------------------------------------------------------
    def get_text(self):
        super().get_text()

    # -------------------------------------------------------------------------
    def is_empty(self):
        super().is_empty()


# =============================================================================
class IEditorTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_init")
    def test_init(self):
        self.assertIsNotNone(TestEditor())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_save")
    def test_save(self):
        self.assertIsNone(TestEditor().save())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_load")
    def test_load(self):
        self.assertIsNone(TestEditor().load())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_option")
    def test_set_option(self):
        self.assertIsNone(TestEditor().set_option())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get_option")
    def test_get_option(self):
        self.assertIsNone(TestEditor().get_option("name"))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_search")
    def test_search(self):
        self.assertIsNone(TestEditor().search())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get_text")
    def test_get_text(self):
        self.assertIsNone(TestEditor().get_text())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_is_empty")
    def test_is_empty(self):
        self.assertIsNone(TestEditor().is_empty())
