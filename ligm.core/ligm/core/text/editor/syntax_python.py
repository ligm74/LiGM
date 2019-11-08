#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Syntax highlighter for the Python language."""

from PyQt5.QtCore import QRegExp
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
    'defclass': format_style('#000080', 'bold'),  # 'black'
    'string': format_style('#008080', 'bold'),
    'string2': format_style('#808080'),  # docstring
    'comment': format_style('#808080', 'italic'),
    'self': format_style('#94558D'),
    'numbers': format_style('#0000FF'),
    'prompt': format_style('darkBlue', 'bold'),
    'special': format_style('#B200B2'),
}


# =============================================================================
class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language."""
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False', 'self', 'with', 'as'
    ]
    special = ["__init__"]

    # -------------------------------------------------------------------------
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        #  syntax highlighting from this point onward (or like """'''''""")
        self.tri_quotes = ((QRegExp("'''"), 1, STYLES['string2']),
                           (QRegExp('"""'), 2, STYLES['string2']))
        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in PythonHighlighter.keywords]

        # All other rules
        rules += [
            (r'\bself\b', 0, STYLES['self']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0,
             STYLES['numbers']),

            # Match the prompt incase of a console
            (r'IN[^\:]*', 0, STYLES['prompt']),
            (r'OUT[^\:]*', 0, STYLES['prompt']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            # (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            (r'\bdef\b', 0, STYLES['defclass']),
            # 'class' followed by an identifier
            # (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),
            (r'\bclass\b', 0, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),
        ]

        rules += [(r'\b%s\b' % w, 0, STYLES['special'])
                  for w in PythonHighlighter.special]

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

        # Do multi-line strings
        for tri_quote in self.tri_quotes:
            if self.match_multiline(text, *tri_quote):
                break

    # -------------------------------------------------------------------------
    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
