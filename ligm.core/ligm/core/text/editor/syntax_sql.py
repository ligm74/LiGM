#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Syntax highlighter for the SQL."""

from PyQt5.QtCore import QRegExp, Qt
from PyQt5.Qt import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


# =============================================================================
def format_style(color, style=''):
    """Return a QTextCharFormat with the given attributes."""
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format_style('#000080', 'bold'),
    'operator': format_style('red'),
    'brace': format_style('darkGray'),
    'defclass': format_style('black', 'bold'),
    'string': format_style('#008080', 'bold'),
    'string2': format_style('#808080'),  # /* ... */
    'comment': format_style('#808080', 'italic'),
    'self': format_style('#94558D'),
    'numbers': format_style('#0000FF'),
    'types': format_style('#B200B2'),
}


# =============================================================================
class SQLHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language."""
    # Python keywords
    keywords = [
        'and', 'or', 'not', 'order', 'by', 'group', 'left', 'right', 'inner',
        'where', 'from', 'select', 'exists', 'having', 'join', 'in', 'as',
        'out', 'BEGIN', 'WITH', 'RECURSIVE', 'UNION', 'on', 'into',
        'LANGUAGE', 'end', 'DROP', 'FUNCTION', 'IF', 'EXISTS', 'CREATE',
        'REPLACE', 'reindex', 'count', 'sum', 'EXPLAIN', 'set', 'to', 'INDEX',
        'delete', 'insert', 'DATABASE', 'off', 'like', 'full', 'ANALYZE',
        'table', 'do', 'declare', 'for', 'loop', 'update', 'BETWEEN', 'RETURN',
        'WHEN', 'is', 'then', 'ELSE', 'ELSIF', 'COLLATE'
    ]
    types = ["varchar", "int", "Integer"]

    # -------------------------------------------------------------------------
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        self.rem_start = QRegExp("/\\*")
        self.rem_end = QRegExp("\\*/")

        rules = []

        # Keyword, operator, and brace rules
        rules += [(QRegExp(r'\b%s\b' % w, Qt.CaseInsensitive), 0,
                   STYLES['keyword']) for w in SQLHighlighter.keywords]

        rules += [(QRegExp(r'\b%s\b' % w, Qt.CaseInsensitive), 0,
                   STYLES['types']) for w in SQLHighlighter.types]

        # All other rules
        rules += [
            (r'\bself\b', 0, STYLES['self']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0,
             STYLES['numbers']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # From '#' until a newline
            (r'--[^\n]*', 0, STYLES['comment']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    # -------------------------------------------------------------------------
    def highlightBlock(self, text):

        """Apply syntax highlighting to the given block of text."""
        # Do other syntax formatting
        for expression, nth, fmt in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, fmt)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        start_idx = 0
        if self.previousBlockState() != 1:
            start_idx = self.rem_start.indexIn(text)

        while start_idx >= 0:
            end_idx = self.rem_end.indexIn(text, start_idx)

            if end_idx == -1:
                self.setCurrentBlockState(1)
                rem_len = len(text) - start_idx
            else:
                rem_len = end_idx - start_idx + self.rem_end.matchedLength()

            self.setFormat(start_idx, rem_len, STYLES['string2'])
            start_idx = self.rem_start.indexIn(text, start_idx + rem_len)
