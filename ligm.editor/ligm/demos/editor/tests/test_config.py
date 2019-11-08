#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for configuration class for demos."""

import os
import unittest
from ligm.demos.editor import Config
from ligm.core.qt import QTestHelper


DEBUG = QTestHelper().start_tests()


# =============================================================================
class ConfigTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_load")
    def test_load(self):
        cfg = Config()
        cfg._filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "tst.json")

        t = cfg._settings.get("TextEditor/TimeoutBalloon", 0)
        cfg.save()
        cfg._settings["TextEditor/TimeoutBalloon"] = 15
        self.assertEqual(cfg._settings["TextEditor/TimeoutBalloon"], 15)
        cfg.load()
        self.assertEqual(cfg._settings.get("TextEditor/TimeoutBalloon", 0), t)
        if os.path.exists(cfg._filename):  # pragma: no cover
            os.remove(cfg._filename)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_save")
    def test_save(self):
        cfg = Config()
        cfg._filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "tst.json")
        if os.path.exists(cfg._filename):  # pragma: no cover
            os.remove(cfg._filename)
        cfg.save()
        self.assertEqual(os.path.exists(cfg._filename), True)
        if os.path.exists(cfg._filename):
            os.remove(cfg._filename)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get")
    def test_get(self):
        cfg = Config()
        self.assertEqual(cfg.get("TextEditor/TimeoutBalloon", 0),
                         cfg._settings["TextEditor/TimeoutBalloon"])
        self.assertEqual(cfg["TextEditor/TimeoutBalloon"],
                         cfg._settings["TextEditor/TimeoutBalloon"])
        self.assertEqual(cfg["ALL", "TextEditor/TimeoutBalloon"],
                         cfg._settings["TextEditor/TimeoutBalloon"])
        self.assertEqual(cfg.get("TextEditor/TimeoutBalloon----", 123), 123)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set")
    def test_set(self):
        cfg = Config()
        t = cfg.get("TextEditor/TimeoutBalloon", 0)
        cfg["TextEditor/TimeoutBalloon"] = 0
        self.assertEqual(cfg._settings["TextEditor/TimeoutBalloon"], 0)
        cfg.load()
        self.assertEqual(cfg._settings["TextEditor/TimeoutBalloon"], 0)
        cfg["TextEditor/TimeoutBalloon"] = t
        cfg.load()
        self.assertEqual(cfg._settings["TextEditor/TimeoutBalloon"], t)
