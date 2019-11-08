#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Test the editor GUI."""

import unittest
from PyQt5.Qt import QHBoxLayout, QTextCursor, Qt, QColor, QFont
from ligm.core.text.editor.syntax_sql import STYLES
from ligm.core.text import TextEditor
from ligm.core.qt import QTestHelper, TestableWidget
from ligm.core.common import SimpleConfig as Config


DEBUG = QTestHelper().start_tests()


# =============================================================================
class SQLHighlighterTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_highlightBlock")
    def test_highlightBlock(self):

        self.test = QTestHelper()

        # ---------------------------------------------------------------------
        # customize editor
        text = "select from 112\n/*\ncomment */"

        # noinspection PyUnusedLocal
        def save(txt):   # pragma: no cover
            return None

        def load():
            return text
        # ---------------------------------------------------------------------

        self.widget = TestableWidget(None)
        self.editor = TextEditor(self.widget, Config(), save=save, load=load,
                                 format="TEXT")
        self.editor.set_option(highlighter="SQL")
        self.editor.load()

        # ---------------------------------------------------------------------
        # customize the widget for placement
        layout = QHBoxLayout()
        layout.addWidget(self.editor, alignment=Qt.Alignment())
        self.widget.setLayout(layout)
        self.widget.resize(800, 450)
        self.widget.move(800, 150)

        self.test.show_and_wait_for_active(self.widget)

        idx = {
            text.index("select"): [None, STYLES["keyword"]],
            text.index("112"): [None, STYLES["numbers"]],
            text.index("comment"): [None, STYLES["comment"]],
        }

        cursor = self.editor._view.text.textCursor()
        cursor.movePosition(QTextCursor.Start)
        for i in range(len(text)):
            pos_in_block = cursor.positionInBlock()
            formats = cursor.block().layout().additionalFormats()

            for fmt in formats:
                if fmt.start <= pos_in_block < fmt.start + fmt.length:
                    if i in idx:
                        idx[i][0] = fmt

            cursor.movePosition(QTextCursor.NextCharacter)

        self.test.sleep()

        for i in idx:
            if idx[i][0] is None:   # pragma: no cover
                self.fail()
            self.assertEqual(
                idx[i][0].format.foreground().color().name(),
                idx[i][1].foreground().color().name())
            self.assertEqual(idx[i][0].format.fontWeight(),
                             idx[i][1].fontWeight())

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_format_style")
    def test_format_style(self):
        self.assertEqual(
            STYLES["operator"].foreground().color().name(),
            QColor("red").name())
        self.assertEqual(
            STYLES["string"].fontWeight(),
            QFont.Bold)
