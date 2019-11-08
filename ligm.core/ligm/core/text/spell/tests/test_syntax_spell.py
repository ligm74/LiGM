#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Test highlighter for spell checking."""

import unittest
from PyQt5.Qt import QHBoxLayout, QTextCursor, Qt, QTextCharFormat, QColor

from ligm.core.text import TextEditor
from ligm.core.qt import QTestHelper, TestableWidget
from ligm.core.common import SimpleConfig as Config
from ligm.core.text.spell import SpellChecker


DEBUG = QTestHelper().start_tests()


# =============================================================================
class SpellHighlighterTest(unittest.TestCase):

    # -------------------------------------------------------------------------
    @unittest.skipIf(DEBUG, "test_highlightBlock")
    def test_highlightBlock(self):

        self.test = QTestHelper()

        # ---------------------------------------------------------------------
        # customize editor
        text = " hello \n world1"

        # noinspection PyUnusedLocal
        def save(txt):   # pragma: no cover
            return None

        def load():
            return text
        # ---------------------------------------------------------------------

        self.widget = TestableWidget(None)
        self.editor = TextEditor(self.widget, Config(), save=save, load=load,
                                 format="HTML", spell=SpellChecker(True))
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
            text.index("hello"): [None, False],
            text.index("world1"): [None, True],
        }

        cursor = self.editor._view.text.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.test.sleep()
        for i in range(len(text)):
            pos_in_block = cursor.positionInBlock()
            formats = cursor.block().layout().additionalFormats()

            for fmt in formats:
                if fmt.start <= pos_in_block < fmt.start + fmt.length:
                    if i in idx:
                        idx[i][0] = fmt.format

            cursor.movePosition(QTextCursor.NextCharacter)

        self.test.sleep()

        for i in idx:
            if idx[i][1]:
                fmt = idx[i][0]
                self.assertEqual(QTextCharFormat.SpellCheckUnderline,
                                 fmt.underlineStyle())
                self.assertEqual(QColor("red").name(),
                                 fmt.underlineColor().name())
            else:
                self.assertIsNone(idx[i][0])
