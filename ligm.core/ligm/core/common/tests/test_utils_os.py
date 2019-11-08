#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for various functions to work with folders, files, etc."""

import os
import sys
from shutil import rmtree
import unittest

from ligm.core.common import get_app_dir, img, run_cmd, realpath, get_res_dir
from ligm.core.qt import QTestHelper


DEBUG = QTestHelper().start_tests()


# =============================================================================
class UtilsOSTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get_res_dir")
    def test_get_res_dir(self):
        path = os.sep.join(os.path.dirname(__file__).split(os.sep)[:-1])
        path = path.replace('\\', '/')
        resource_dir = os.path.join(path, "resources").replace('\\', '/')
        if not os.path.exists(resource_dir):
            os.mkdir(resource_dir)

        get_app_dir.cache_clear()
        get_res_dir.cache_clear()
        self.assertEqual(resource_dir, get_res_dir())

        with self.assertRaises(Exception) as err:
            get_res_dir("NOT_FOUND_RESOURCES_DIR")

        self.assertEqual(err.exception.args[0],
                         "Application directory not found.")

        get_res_dir.cache_clear()
        get_app_dir.cache_clear()
        rmtree(resource_dir)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_get_app_dir")
    def test_get_app_dir(self):
        path = os.sep.join(os.path.dirname(__file__).split(os.sep)[:-1])
        path = path.replace('\\', '/')
        resource_dir = os.path.join(path, "resources")
        if not os.path.exists(resource_dir):
            os.mkdir(resource_dir)

        get_app_dir.cache_clear()
        self.assertEqual(path, get_app_dir())

        with self.assertRaises(Exception) as err:
            get_app_dir("NOT_FOUND_RESOURCES_DIR")

        self.assertEqual(err.exception.args[0],
                         "Application directory not found.")

        get_app_dir.cache_clear()
        rmtree(resource_dir)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_img")
    def test_img(self):
        path = os.sep.join(os.path.dirname(__file__).split(os.sep)[:-1])
        resource_dir = os.path.join(path, "resources")
        image_dir = os.path.join(resource_dir, "images")
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        img_path = os.path.join(image_dir, "tmp.png")
        img_path = img_path.replace('\\', '/')
        if not os.path.exists(img_path):
            with open(img_path, "w") as f:
                f.write(" ")

        self.assertEqual(img_path, img("tmp"))
        self.assertEqual("", img(""))

        self.assertEqual("", img("tmp11.png"))
        self.assertEqual("", img("tmp11.png"))

        get_app_dir.cache_clear()
        img.cache_clear()
        rmtree(resource_dir)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_run_cmd")
    def test_run_cmd(self):
        nul = "/dev/null" if sys.platform == "linux" else "nul"
        self.assertEqual(run_cmd(f"dir > {nul}", test=True), (True, 'OK'))
        self.assertEqual(run_cmd(f"dir > {nul}", ".", test=True), (True, 'OK'))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_realpath")
    def test_realpath(self):
        self.assertEqual("HH", realpath("HH"))
        self.assertEqual("", realpath("////"))
