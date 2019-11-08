#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Helper classes for testing GUI."""

import sys
import time
import os
import threading
import difflib
import json
from typing import Callable, Union
from PyQt5.Qt import (QDialog, Qt, QApplication, QWidget, QKeyEvent, QEvent,
                      QMouseEvent, QObject, QCoreApplication, QPoint, QTest,
                      QTextCursor, QTextEdit, QMessageBox, QMainWindow)
from ligm.core.common import get_res_dir
from ligm.core.qt import install_translators


TypeWidget = Union[QWidget, QDialog, None]
# function to run after modal widget is found
TypeFuncAfter = Callable[[TypeWidget, ], None]


# =============================================================================
def diff(s):
    """
    Compare two strings. In the first call transfered the first string.
    In the second call transfered second string and the result of the
    comparison is returned
    """
    add_str, del_str = "", ""
    if not hasattr(diff, 'mem'):
        diff.mem = s
    else:
        gen_diff = list(difflib.ndiff(diff.mem, s))
        del_str = "".join([c[-1] for c in gen_diff if c[0] == "-"])
        add_str = "".join([c[-1] for c in gen_diff if c[0] == "+"])
        del diff.mem
    return {"add": add_str, "del": del_str}


# =============================================================================
class QTestHelper(QObject):  # pragma: no cover
    """Helper class for testing GUI"""
    _interactive: bool = True
    _debug: bool = False
    _in_test: bool = False
    _tests_delay: float = 1.0         # delay in seconds
    _tests_min_delay: float = 0.0001  # min delay in seconds
    _tests_delay_key: float = 0.05    # delay between key clicks (in seconds)

    # -------------------------------------------------------------------------
    def __new__(cls):
        """Singleton class"""
        if not hasattr(cls, '_instance'):
            cls._instance = super(QTestHelper, cls).__new__(cls)

            # read settings: DEBUG and INTERACTIVE
            test_ini_file = f"{get_res_dir()}/test.ini"
            with open(test_ini_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            cls._interactive = data["INTERACTIVE"]
            cls._debug = data["DEBUG"]

        return cls._instance

    # -------------------------------------------------------------------------
    def __init__(self):
        QObject.__init__(self)

        if not QApplication.instance():  # pragma: no cover
            os.environ['XDG_SESSION_TYPE'] = ""
            self._app = QApplication(sys.argv)
            install_translators()
        else:
            self._app = QApplication.instance()

    # -------------------------------------------------------------------------
    @staticmethod
    def is_interactive() -> bool:
        """Return mode: if False, the forms are not shown"""
        if not QTestHelper._in_test:
            return True
        return QTestHelper._interactive

    # -------------------------------------------------------------------------
    @staticmethod
    def is_debug() -> bool:
        """Return mode: if True, some tests are skipped"""
        return QTestHelper._debug

    # -------------------------------------------------------------------------
    @staticmethod
    def start_tests() -> bool:
        """Return mode: if True, some tests are skipped"""
        QTestHelper._in_test = True
        return QTestHelper._debug

    # -------------------------------------------------------------------------
    @staticmethod
    def set_interactive(mode: bool) -> None:
        """Set mode: if False, the forms are not shown"""
        QTestHelper._interactive = mode
        QTestHelper._save_settings()

    # -------------------------------------------------------------------------
    @staticmethod
    def set_debug(mode: bool) -> None:
        """Set mode: if True, some tests are skipped"""
        QTestHelper._debug = mode
        QTestHelper._save_settings()

    # -------------------------------------------------------------------------
    @staticmethod
    def _save_settings() -> None:
        """Save settings: DEBUG and INTERACTIVE"""
        test_ini_file = f"{get_res_dir()}/test.ini"
        with open(test_ini_file, "w", encoding="utf-8") as f:
            json.dump({
                "DEBUG": QTestHelper._debug,
                "INTERACTIVE": QTestHelper._interactive
            }, f, indent=4, sort_keys=True)

    # -------------------------------------------------------------------------
    def sleep(self, delay: float = 1) -> None:
        """The delay between the actions in an interactive mode"""
        self._app.processEvents()
        time.sleep(delay * self._tests_delay if self.is_interactive() else
                   self._tests_min_delay)

    # -------------------------------------------------------------------------
    def key_click(self, widget: QWidget, key: int = 0, txt: str = "",
                  modifier: int = Qt.NoModifier, delay: float = 0) -> None:
        """Send press key event to widget"""
        widget.setFocus()

        key_press = QKeyEvent(QEvent.KeyPress, key, modifier, txt, False)
        key_release = QKeyEvent(QEvent.KeyRelease, key, modifier, txt, False)

        QCoreApplication.postEvent(widget, key_press)
        QCoreApplication.postEvent(widget, key_release)

        self.sleep(delay)

    # -------------------------------------------------------------------------
    def qtest_key_click(self, key: int = 0, modifier: int = Qt.NoModifier,
                        delay: float = 0) -> None:
        # noinspection PyTypeChecker,PyCallByClass
        QTest.keyClick(None, key, modifier)
        self.sleep(delay)

    # -------------------------------------------------------------------------
    def key_clicks(self, widget: QWidget, txt: str = "",
                   modifier: int = Qt.NoModifier, delay: float = 0) -> None:
        """Send string to widget"""
        timeout: float = self._tests_delay_key if delay else 0
        if not self.is_interactive():
            timeout = 0

        for char in txt:
            key = QKeyEvent(QEvent.KeyPress, 0, modifier, char, False)
            QCoreApplication.postEvent(widget, key)
            if timeout:
                self.sleep(timeout)

        self.sleep(delay)

    # -------------------------------------------------------------------------
    @staticmethod
    def mouse_move(widget: QWidget, pos: QPoint) -> None:
        """Move mouse ono widget"""
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseMove(widget, pos)

    # -------------------------------------------------------------------------
    def _mouse_event(self, mtype: int, pos: QPoint, btn: int) -> QMouseEvent:
        """Create mouse event"""
        return QMouseEvent(
            mtype, pos, btn,
            self._app.mouseButtons(), self._app.keyboardModifiers())

    # -------------------------------------------------------------------------
    def mouse_click(self, widget: QWidget, pos: QPoint = QPoint(0, 0),
                    btn: int = Qt.LeftButton, delay: float = 0) -> None:
        """Send mouse click to widget"""
        # TODO: if delete a comment from the next line, the program crashes
        #  Process finished with exit code 139 (interrupted signal 11: SIGSEGV)
        # widget.setFocus()  # !!! find the cause of the error !!!
        mouse_press = self._mouse_event(QEvent.MouseButtonPress, pos, btn)
        mouse_release = self._mouse_event(QEvent.MouseButtonRelease, pos, btn)
        QCoreApplication.postEvent(widget, mouse_press)
        QCoreApplication.postEvent(widget, mouse_release)
        self.sleep(delay)

    # -------------------------------------------------------------------------
    def mouse_dbl_click(self, widget: QWidget, pos: QPoint = QPoint(0, 0),
                        btn: int = Qt.LeftButton, delay: float = 0) -> None:
        """Send mouse double click to widget"""
        widget.setFocus()
        mouse_dbl = self._mouse_event(QEvent.MouseButtonDblClick, pos, btn)
        QCoreApplication.postEvent(widget, mouse_dbl)
        self.sleep(delay)

    # -------------------------------------------------------------------------
    def show_and_wait_for_active(self, widget: QWidget,
                                 timeout: int = 5000) -> None:
        """Wait for active widget"""
        widget.show()
        if self.is_interactive():
            # noinspection PyTypeChecker,PyCallByClass
            QTest.qWaitForWindowActive(widget, timeout)

    # -------------------------------------------------------------------------
    @staticmethod
    def get_xy_for_word(text: QTextEdit, word: str) -> QPoint:
        """
        Returns the pixel coordinates of the word on the QTextEdit canvas.
        If QTextEdit does not contain the specified word or it is invisible,
        returns 0, 0.
        """
        _text = text.toPlainText()
        x, y = 0, 0
        if word and word in _text:
            idx = _text.index(word)
            cursor = text.textCursor()
            cursor.movePosition(QTextCursor.Start)
            for _ in range(idx):
                cursor.movePosition(QTextCursor.NextCharacter)
            rect = text.cursorRect(cursor)
            x = rect.x() + rect.width()
            y = rect.y() + rect.height() // 2
            if x < 0 or y < 0:  # pragma: no cover
                x, y = 0, 0
        return QPoint(x, y)

    # -------------------------------------------------------------------------
    def handle_modal_widget(self, func: TypeFuncAfter) -> None:
        """Listens for a modal widget"""
        thread = threading.Thread(target=self._close_modal, args=(func,))
        thread.start()

    # -------------------------------------------------------------------------
    def _close_modal(self, func: TypeFuncAfter, timeout: float = 10) -> None:
        """Endlessly waits for a modal widget"""
        modal_widget: TypeWidget = None
        start: float = time.time()
        while modal_widget is None and time.time() - start < timeout:
            modal_widget = self._app.activeModalWidget()
            time.sleep(0.01)

        func(modal_widget)

    # -------------------------------------------------------------------------
    def handle_popup_widget(self, func: TypeFuncAfter) -> None:
        """Listens for a popup widget"""
        thread = threading.Thread(target=self._close_popup, args=(func,))
        thread.start()

    # -------------------------------------------------------------------------
    def _close_popup(self, func: TypeFuncAfter, timeout: float = 10) -> None:
        """Endlessly waits for a popup widget"""
        modal_widget: TypeWidget = None
        start: float = time.time()
        while modal_widget is None and time.time() - start < timeout:
            modal_widget = self._app.activePopupWidget()
            time.sleep(0.01)

        func(modal_widget)

    # -------------------------------------------------------------------------
    def _mouse_click(self, te: QTextEdit, word: str, delay: float,
                     dbl: bool) -> None:
        pos = self.get_xy_for_word(te, word)
        func = self.mouse_dbl_click if dbl else self.mouse_click
        func(te.viewport(), pos, delay=delay)

    # -------------------------------------------------------------------------
    def wrd_click(self, te: QTextEdit, word: str, delay: float = 1) -> None:
        """Mouse click on word in QTextEdit"""
        self._mouse_click(te, word, delay, False)

    # -------------------------------------------------------------------------
    def wrd_d_click(self, te: QTextEdit, word: str, delay: float = 1) -> None:
        """Mouse double click on word in QTextEdit"""
        self._mouse_click(te, word, delay, True)


# =============================================================================
class TestableDialog(QDialog):
    """Class for dont show dialog in test"""

    def __init__(self, parent=None):
        QDialog.__init__(self, parent, Qt.WindowFlags())

        if not QTestHelper().is_interactive():
            self.setAttribute(Qt.WA_DontShowOnScreen)


# =============================================================================
class TestableWidget(QWidget):
    """Class for dont show widget in test"""

    def __init__(self, parent=None):
        QWidget.__init__(self, parent, Qt.WindowFlags())

        if not QTestHelper().is_interactive():
            self.setAttribute(Qt.WA_DontShowOnScreen)


# =============================================================================
class TestableMessageBox(QMessageBox):
    """Class for dont show QMessageBox in test"""

    def __init__(self, parent=None):
        QMessageBox.__init__(self, parent)

        if not QTestHelper().is_interactive():
            self.setAttribute(Qt.WA_DontShowOnScreen)


# =============================================================================
class TestableMainWindow(QMainWindow):  # pragma: no cover
    """Class for dont show QMessageBox in test"""

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent, Qt.WindowFlags())

        if not QTestHelper().is_interactive():
            self.setAttribute(Qt.WA_DontShowOnScreen)
