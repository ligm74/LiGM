#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Various functions to work with Qt."""


import os

from PyQt5.QtCore import QTranslator, QLocale, QCoreApplication
from PyQt5.Qt import QMessageBox, QApplication

from ligm.core.common import get_app_dir


__translators = []
__locale = "en_EN"


# =============================================================================
def install_translators(locale=None):
    """
    Install all translation files in the application
    """
    if not locale:
        locale = QLocale.system().name()

    global __translators, __locale
    _remove_translators()

    __locale = locale

    if locale == "en_EN":
        return

    __translators = []

    for root, dirs, _ in os.walk(get_app_dir()):
        if root.endswith("locale"):
            if locale in dirs:
                for file in os.listdir(root + os.sep + locale):
                    if file.endswith(".qm"):
                        path = root + os.sep + locale + os.sep + file
                        __translators.append(QTranslator())
                        __translators[-1].load(path)
                        QApplication.instance().installTranslator(
                            __translators[-1])


# -----------------------------------------------------------------------------
def _remove_translators():
    """
    Remove installed translation files
    """
    global __translators
    for translator in __translators:
        QApplication.instance().removeTranslator(translator)


# -----------------------------------------------------------------------------
def get_current_language():
    global __locale
    return __locale


# =============================================================================
def yes_no(message, parent=None):
    result = QMessageBox.question(
        parent, QCoreApplication.translate("@default", "Question"),
        message, QMessageBox.Yes, QMessageBox.No)
    return result == QMessageBox.Yes


# =============================================================================
def msg(message, parent=None):
    popup = QMessageBox(
        QMessageBox.Warning,
        QCoreApplication.translate("@default", "Error in parameters"),
        message, QMessageBox.Ok, parent)
    popup.show()


# =============================================================================
class BlockSignals:
    """
    Context manager for disable signals of widget
    """
    def __init__(self, widget):
        self.widget = widget

    def __enter__(self):
        self.widget.blockSignals(True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.widget.blockSignals(False)
