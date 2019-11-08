#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for demonstrate QTestHelper."""

import unittest
from PyQt5.Qt import (QPoint, QVBoxLayout, Qt, QLabel, QSpacerItem,
                      QSizePolicy, QTextCharFormat)
from ligm.core.text.editor.align import AlignText
from ligm.core.qt.qtest_helper import QTestHelper, TestableWidget


DEBUG = QTestHelper().start_tests()


# =============================================================================
class AlignTextTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.test = QTestHelper()
        cls.select_align = []

        cls.w = TestableWidget()
        cls.w.setWindowTitle("Test align text")
        cls.w.setGeometry(900, 300, 500, 320)
        cls.cp = AlignText()
        cls.cp.select_align.connect(
            lambda h, v: cls.select_align.append((h, v)))
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
        AlignTextTest.select_align = []
        self.lbl.setText("")

    # -------------------------------------------------------------------------
    def tearDown(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_all")
    def test_all(self):
        self.lbl.setText("CURRENT TEST: test_all")

        # no select align
        self.test.mouse_click(self.cp, QPoint(1, 1))
        self.test.sleep()
        self.test.mouse_click(self.cw, QPoint(-1, 1))
        self.test.sleep()
        self.assertEqual(self.select_align, [])

        # select first button in align grid
        self.test.mouse_click(self.cp, QPoint(1, 1))
        self.test.sleep()
        self.test.mouse_click(self.cw._clrbtn[0], QPoint(1, 1))
        self.test.sleep()
        self.assertEqual(self.select_align[-1][0], Qt.AlignLeft)
        self.assertEqual(self.select_align[-1][1], QTextCharFormat.AlignTop)

        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_AlignText.select_align_")
    def test_select_align_(self):

        self.cp.select_align_(2, 2)
        self.assertEqual(self.select_align[-1][0], Qt.AlignCenter)
        self.assertEqual(self.select_align[-1][1], QTextCharFormat.AlignMiddle)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_AlignTextWidget.select_align_")
    def test_align_text_widget_select_align_(self):

        self.cp.select_align_(3, 3)
        self.assertEqual(self.select_align[-1][0], Qt.AlignRight)
        self.assertEqual(self.select_align[-1][1], QTextCharFormat.AlignBottom)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_hide_form")
    def test_hide_form(self):
        self.lbl.setText("CURRENT TEST: test_hide_form")
        self.test.mouse_click(self.cp, QPoint(1, 1))
        self.assertTrue(self.cp.isChecked())
        self.test.sleep()
        self.cp.hide_form()
        self.assertFalse(self.cp.isChecked())
        self.test.sleep()

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_set_enable_vertical_align")
    def test_set_enable_vertical_align(self):

        self.cp.set_enable_vertical_align(True)
        self.assertTrue(self.cw._clrbtn[10].isVisible())
        self.cp.set_enable_vertical_align(False)
        self.assertFalse(self.cw._clrbtn[10].isVisible())

        self.cw.set_enable_vertical_align(True)
        self.assertTrue(self.cw._clrbtn[10].isVisible())
        self.cw.set_enable_vertical_align(False)
        self.assertFalse(self.cw._clrbtn[10].isVisible())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "show_form")
    def test_show_form(self):
        self.lbl.setText("CURRENT TEST: show_form")
        self.select_align.clear()
        self.cw.show_form(QPoint(100, 100))
        self.test.sleep()
        self.test.mouse_click(self.cw._clrbtn[2], QPoint(1, 1))
        self.test.sleep()
        self.assertEqual(self.select_align[-1][0], Qt.AlignRight)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_show_form_")
    def test_show_form_(self):
        self.lbl.setText("CURRENT TEST: test_show_form_")
        self.cp.show_form()
        self.test.sleep()
        self.test.mouse_click(self.cw._clrbtn[1], QPoint(1, 1))
        self.assertEqual(self.select_align[-1][0], Qt.AlignCenter)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_retranslate_ui")
    def test_retranslate_ui(self):
        pass

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
        pass  # tested in test_hide_form
