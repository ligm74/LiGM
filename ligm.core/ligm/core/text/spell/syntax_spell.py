#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)
"""Highlighter for spell checking."""

import re
from PyQt5.QtCore import Qt
from PyQt5.Qt import QTextCharFormat, QSyntaxHighlighter


# =============================================================================
class SpellHighlighter(QSyntaxHighlighter):

    # -------------------------------------------------------------------------
    def __init__(self, document, dictionary):
        QSyntaxHighlighter.__init__(self, document)
        self._dictionary = dictionary

    # -------------------------------------------------------------------------
    def highlightBlock(self, text):
        words = re.compile('[^_\\W]+', flags=re.UNICODE)

        char_format = QTextCharFormat()
        char_format.setUnderlineColor(Qt.red)
        char_format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)

        # collect data for checking
        mark = []
        for match in words.finditer(text):
            final_format = QTextCharFormat()
            final_format.merge(char_format)
            final_format.merge(self.format(match.start()))

            if self._dictionary.word_needs_no_verification(match.group(0)):
                continue

            mark.append((match.group(0).lower(), match.start(),
                         match.end() - match.start(), final_format))

        # word check
        for word, start, length, fmt in mark:
            if not self._dictionary.check_word(word):
                self.setFormat(start, length, fmt)
