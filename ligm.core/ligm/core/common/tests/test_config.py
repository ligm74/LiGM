#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for class ConfigHelper."""

import unittest
from ligm.core.common import ConfigHelper, SimpleConfig
from ligm.core.qt import QTestHelper


DEBUG = QTestHelper().start_tests()


# =============================================================================
class ConfigHelperTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set")
    def test_set(self):
        _cfg = SimpleConfig()
        cfg = ConfigHelper(_cfg, kk="hello", mm=321)

        self.assertNotIn("nn", _cfg.values)
        self.assertNotIn("nn", _cfg.values_sys)
        cfg["SYSTEM", "nn"] = 1
        self.assertNotIn("nn", _cfg.values)
        self.assertEqual(_cfg.values_sys["nn"], 1)

        cfg["nn"] = 2
        self.assertEqual(_cfg.values_sys["nn"], 1)
        self.assertEqual(_cfg.values["nn"], 2)

        cfg["nn"] = 3
        self.assertEqual(_cfg.values_sys["nn"], 1)
        self.assertEqual(_cfg.values["nn"], 3)

        self.assertNotIn("kk", _cfg.values)
        self.assertNotIn("kk", _cfg.values_sys)
        self.assertNotIn("mm", _cfg.values)
        self.assertNotIn("mm", _cfg.values_sys)

        cfg["kk"] = "world"
        cfg["mm"] = -1

        self.assertNotIn("kk", _cfg.values)
        self.assertNotIn("kk", _cfg.values_sys)
        self.assertNotIn("mm", _cfg.values)
        self.assertNotIn("mm", _cfg.values_sys)

        self.assertFalse(cfg.get.cache_info().currsize > 0)
        cfg.get.cache_clear()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get")
    def test_get(self):
        _cfg = SimpleConfig()
        cfg = ConfigHelper(_cfg, kk="hello", mm=321)

        self.assertEqual(cfg.get("nn", 11, True), 11)
        self.assertEqual(cfg.get("nn", 12, False), 12)
        cfg["SYSTEM", "nn"] = 1
        self.assertEqual(cfg.get("nn", 11, True), 1)
        self.assertEqual(cfg.get("nn", 12, False), 12)

        cfg["nn"] = 2
        self.assertEqual(cfg.get("nn", 11, True), 1)
        self.assertEqual(cfg.get("nn", 12, False), 2)

        cfg["nn"] = 3
        self.assertEqual(cfg.get("nn", 11, True), 1)
        self.assertEqual(cfg.get("nn", 12, False), 3)

        self.assertNotIn("kk", _cfg.values)
        self.assertNotIn("kk", _cfg.values_sys)
        self.assertNotIn("mm", _cfg.values)
        self.assertNotIn("mm", _cfg.values_sys)

        self.assertEqual(cfg.get("kk", 11), "hello")
        self.assertEqual(cfg.get("mm", 11), 321)
        self.assertTrue(cfg.get.cache_info().currsize > 0)
        cfg["kk"] = "world"
        self.assertFalse(cfg.get.cache_info().currsize > 0)
        cfg["mm"] = -1
        self.assertEqual(cfg.get("kk", 11), "world")
        self.assertEqual(cfg.get("mm", 11), -1)
        self.assertEqual(cfg.get("kk", 11, True), "world")
        self.assertEqual(cfg.get("mm", 11, system=True), -1)

        self.assertTrue(cfg.get.cache_info().currsize > 0)
        cfg.get.cache_clear()

        cfg["SYSTEM", "nn"] = 1
        cfg["nn"] = 3
        self.assertEqual(_cfg["SYSTEM", "nn"], 1)
        self.assertEqual(_cfg["nn"], 3)
