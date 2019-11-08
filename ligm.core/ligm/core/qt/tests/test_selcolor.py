#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for ColorPicker widget."""

import unittest
from PyQt5.Qt import (QPoint, QVBoxLayout, Qt, QLabel, QSpacerItem, QColor,
                      QSizePolicy)
from ligm.core.common import SimpleConfig as Config
from ligm.core.qt import ColorPicker
from unittest.mock import patch
from ligm.core.qt.qtest_helper import QTestHelper, TestableWidget


DEBUG = QTestHelper().start_tests()


# =============================================================================
class ColorPickerTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.test = QTestHelper()
        cls.selected_colors = []

        cls.w = TestableWidget()
        cls.w.setWindowTitle("Test select color")
        cls.w.setGeometry(900, 300, 500, 320)
        cls.cp = ColorPicker(config=Config())
        cls.cp.select_color.connect(
            lambda color: cls.selected_colors.append(color))
        cls.cw = cls.cp._colors_widget

        cls.v = QVBoxLayout()
        cls.v.addWidget(cls.cp, alignment=Qt.Alignment())
        cls.v.addWidget(QLabel(""), alignment=Qt.Alignment())
        cls.v.addItem(QSpacerItem(0, 0,
                                  QSizePolicy.Fixed, QSizePolicy.Expanding))

        cls.lbl = QLabel("")
        cls.v.addWidget(cls.lbl, alignment=Qt.Alignment())
        cls.w.setLayout(cls.v)

        cls.test.show_and_wait_for_active(cls.w)

    # -------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        pass

    # -------------------------------------------------------------------------
    def setUp(self):
        self.lbl.setText("")

    # -------------------------------------------------------------------------
    def tearDown(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_all")
    def test_all(self):
        self.lbl.setText("CURRENT TEST: test_all")

        # no select color
        self.test.mouse_click(self.cp, QPoint(1, 1))
        self.test.sleep()
        self.test.mouse_click(self.cw, QPoint(-1, 1))
        self.test.sleep()
        self.assertEqual(self.selected_colors, [])

        # select first button in colors grid
        self.test.mouse_click(self.cp, QPoint(1, 1))
        self.test.sleep()
        self.test.mouse_click(self.cw.clrbtn[0], QPoint(1, 1))
        self.test.sleep()
        self.assertEqual(self.selected_colors[-1], self.cp._colors[0])

        # select other color
        with patch.object(self.cp, '_get_color', return_value=QColor("blue")):
            self.test.mouse_click(self.cp, QPoint(1, 1))
            self.test.sleep()
            self.test.mouse_click(self.cw.clrbtn[-1], QPoint(3, 3))
            self.test.sleep()
        self.assertEqual(self.selected_colors[-1], QColor("blue").name())

        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_show_form_colors")
    def test_show_form_colors(self):
        self.lbl.setText("CURRENT TEST: test_show_form_colors")
        self.cp.show_form_colors()
        self.test.sleep()
        self.test.mouse_click(self.cw.clrbtn[1], QPoint(1, 1))
        self.assertEqual(self.selected_colors[-1], self.cp._colors[1])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_select_color_")
    def test_select_color_(self):
        self.lbl.setText("CURRENT TEST: test_select_color_")
        self.cp.select_color_("TEST")
        self.assertEqual(self.selected_colors[-1], "TEST")

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_other_color")
    def test_other_color(self):
        self.lbl.setText("CURRENT TEST: test_other_color")
        with patch.object(self.cp, '_get_color', return_value=QColor("green")):
            self.cp.other_color()
        self.assertEqual(self.selected_colors[-1], QColor("green").name())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_hide_color_form")
    def test_hide_color_form(self):
        self.lbl.setText("CURRENT TEST: test_hide_color_form")
        self.test.mouse_click(self.cp, QPoint(1, 1))
        self.assertTrue(self.cp.isChecked())
        self.test.sleep()
        self.cp.hide_color_form()
        self.assertFalse(self.cp.isChecked())
        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_retranslate_ui")
    def test_retranslate_ui(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_other_color_")
    def test_other_color_(self):
        self.lbl.setText("CURRENT TEST: test_other_color_")
        with patch.object(self.cp, '_get_color', return_value=QColor("red")):
            self.cw.other_color_()
        self.assertEqual(self.selected_colors[-1], QColor("red").name())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "show_form")
    def test_show_form(self):
        self.lbl.setText("CURRENT TEST: show_form")
        self.cw.show_form(QPoint(100, 100))
        self.test.sleep()
        self.test.mouse_click(self.cw.clrbtn[2], QPoint(1, 1))
        self.assertEqual(self.selected_colors[-1], self.cp._colors[2])

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_paintEvent")
    def test_paintEvent(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_mouseReleaseEvent")
    def test_mouseReleaseEvent(self):
        pass  # tested in test_all (mouse_click(self.cw, QPoint(-1, 1))

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_hideEvent")
    def test_hideEvent(self):
        pass  # tested in test_hide_color_form
