#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tests for demonstrate InsertTable."""

import unittest
from PyQt5.Qt import (QPoint, QVBoxLayout, Qt, QLabel, QSpacerItem,
                      QSizePolicy)
from ligm.core.common import SimpleConfig as Config
from ligm.core.text.editor.instable import InsertTable, TableParamsDlg
from ligm.core.qt.qtest_helper import QTestHelper, TestableWidget


DEBUG = QTestHelper().start_tests()


# =============================================================================
class InsertTableTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.test = QTestHelper()
        cls.insert_table = []

        cls.w = TestableWidget()
        cls.w.setWindowTitle("Test insert table")
        cls.w.setGeometry(900, 300, 500, 500)
        cls.cp = InsertTable(config=Config())
        cls.cp.insert_table.connect(
            lambda data: cls.insert_table.append(data))
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
    @staticmethod
    def _click_insert(widget, r, c):
        test = QTestHelper()
        test.key_click(widget.controls[0], Qt.Key_A,
                       modifier=Qt.ControlModifier)
        test.sleep(0.5)
        test.key_clicks(widget.controls[0], str(r))
        test.sleep(0.5)
        test.key_click(widget.controls[1], Qt.Key_A,
                       modifier=Qt.ControlModifier)
        test.sleep(0.5)
        test.key_clicks(widget.controls[1], str(c))
        test.sleep(0.5)
        test.mouse_click(widget.controls[-1], QPoint(1, 1))
        test.sleep(0.5)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_all")
    def test_all(self):
        self.lbl.setText("CURRENT TEST: test_all")

        # no select
        self.test.mouse_click(self.cp, QPoint(1, 1))
        self.test.sleep()
        self.test.mouse_click(self.cw, QPoint(-1, 1))
        self.test.sleep()
        self.assertEqual(self.insert_table, [])

        # select first button in grid
        self.test.mouse_click(self.cp, QPoint(1, 1))
        self.test.mouse_move(self.cw, QPoint(100, 100))
        self.test.sleep()
        self.test.mouse_move(self.cw._clrbtn[35], QPoint(1, 1))
        self.test.sleep()
        self.test.mouse_click(self.cw._clrbtn[35], QPoint(1, 1))
        self.test.sleep()
        self.assertEqual(self.insert_table[-1]["rows"], 4)
        self.assertEqual(self.insert_table[-1]["cols"], 6)

        # select insert table
        self.test.mouse_click(self.cp, QPoint(1, 1))
        self.test.sleep()
        self.test.handle_modal_widget(
            lambda w, r=2, c=5: self._click_insert(w, r, c))
        self.test.mouse_click(self.cw._clrbtn[-1], QPoint(3, 3))
        self.assertEqual(self.insert_table[-1]["rows"], 2)
        self.assertEqual(self.insert_table[-1]["cols"], 5)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_InsertTable.show_form")
    def test_show_form(self):
        self.lbl.setText("CURRENT TEST: InsertTable.show_form")
        self.cp.show_form()
        self.test.sleep()
        self.test.mouse_click(self.cw._clrbtn[1], QPoint(1, 1))
        self.assertEqual(self.insert_table[-1]["rows"], 1)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_InsertTableWidget.show_form")
    def test_show_form_(self):
        self.lbl.setText("CURRENT TEST: InsertTableWidget.show_form")
        self.cw.show_form(QPoint(100, 100))
        self.test.sleep()
        self.test.mouse_click(self.cw._clrbtn[2], QPoint(1, 1))
        self.assertEqual(self.insert_table[-1]["rows"], 1)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_select_size_")
    def test_select_size_(self):
        self.lbl.setText("CURRENT TEST: test_select_size_")
        self.cp.select_size_(100, 100)
        self.assertEqual(self.insert_table[-1]["rows"], 100)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_InsertTableWidget.select_size_")
    def test_select_size__(self):
        self.lbl.setText("CURRENT TEST: test_InsertTableWidget.select_size_")
        self.cw.select_size_(12)
        self.assertEqual(self.insert_table[-1]["rows"], 2)
        self.assertEqual(self.insert_table[-1]["cols"], 3)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_other_size")
    def test_other_size(self):
        self.lbl.setText("CURRENT TEST: test_other_size")
        self.test.handle_modal_widget(
            lambda w, r=21, c=51: self._click_insert(w, r, c))
        self.cp.other_size()
        self.assertEqual(self.insert_table[-1]["rows"], 21)
        self.assertEqual(self.insert_table[-1]["cols"], 51)

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_other_size_")
    def test_other_size_(self):
        self.lbl.setText("CURRENT TEST: test_other_size_")
        self.test.handle_modal_widget(
            lambda w, r=15, c=20: self._click_insert(w, r, c))
        self.cw.other_size_()
        self.assertEqual(self.insert_table[-1]["rows"], 15)
        self.assertEqual(self.insert_table[-1]["cols"], 20)

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
    @unittest.skipIf(DEBUG, "test_hideEvent")
    def test_hideEvent(self):
        self.lbl.setText("CURRENT TEST: test_hideEvent")
        self.test.mouse_click(self.cp, QPoint(1, 1))
        self.assertTrue(self.cp.isChecked())
        self.test.sleep()
        self.cw.hide()
        self.assertFalse(self.cp.isChecked())
        self.test.sleep()

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
    @unittest.skipIf(DEBUG, "test_init_ui")
    def test_init_ui(self):
        pass

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_insert")
    def test_insert(self):

        def click_insert(widget):
            test = QTestHelper()
            test.mouse_click(widget.controls[-1], QPoint(1, 1))
            test.sleep(0.5)
            widget.close()

        self.test.handle_modal_widget(click_insert)
        tt = TableParamsDlg(self.w, config=Config())
        tt.exec_()
        self.test.sleep()
        self.assertEqual(tt.table_params, {})
