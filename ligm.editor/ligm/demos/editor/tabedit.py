#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Tab for editable file."""

import os
import shutil
from typing import Union
from PyQt5.Qt import QWidget, Qt, QVBoxLayout, pyqtSignal, QFileDialog
from ligm.core.text import TextEditor
from ligm.core.common import realpath
from ligm.core.qt import TestableWidget


TWidget = Union[QWidget, TestableWidget]


# =============================================================================
class TabEdit(TestableWidget):

    enabled_save_signal = pyqtSignal(bool)     # for update status "Save"

    # -------------------------------------------------------------------------
    def __init__(self, parent: TWidget, file_path=None,
                 text_format="HTML", highlighter="", func_after_save=None,
                 spell=None):
        super(TabEdit, self).__init__()

        self._editor = TextEditor(parent, parent.cfg,
                                  show_status_bar=True,
                                  show_tool_bar=True,
                                  format=text_format,
                                  load=self._load,
                                  save=self._save,
                                  spell=spell)
        self._editor.enabled_save_signal.connect(self.set_enabled_save)
        self._func_after_save = func_after_save
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        layout.addWidget(self._editor, alignment=Qt.Alignment())

        self._parent = parent
        self._file_path = file_path
        self._text_format = text_format.upper()
        name = "HTML" if text_format.upper() == "HTML" else "TEXT"
        self._prev_text_format = name
        self._highlighter = highlighter
        self._is_modified = False
        self._editor.set_option(highlighter=highlighter)
        self._editor.load()

    # -------------------------------------------------------------------------
    def set_read_only(self, value):
        self._editor.set_option(readonly=value)

    # -------------------------------------------------------------------------
    def is_read_only(self):
        return self._editor.get_option("readonly")

    # -------------------------------------------------------------------------
    def set_focus(self):
        self._editor.setFocus()

    # -------------------------------------------------------------------------
    def set_invisible_symbol(self):
        self._editor.set_option(invisible_symbol="")

    # -------------------------------------------------------------------------
    def set_text_format(self, format_name):
        if self._editor.set_option(format=format_name):
            name = "HTML" if format_name.upper() == "HTML" else "TEXT"
            self._text_format = name

    # -------------------------------------------------------------------------
    def set_highlighter(self, highlighter):
        self._highlighter = highlighter
        self._editor.set_option(highlighter=highlighter)

    # -------------------------------------------------------------------------
    def get_word_wrap(self):
        return self._editor.get_option("word-wrap")

    # -------------------------------------------------------------------------
    def set_word_wrap(self):
        self._editor.set_option(word_wrap="")

    # -------------------------------------------------------------------------
    def file_path(self):
        return (realpath(self._file_path) if self._file_path else
                self._file_path)

    # -------------------------------------------------------------------------
    def is_modified(self):
        return self._is_modified

    # -------------------------------------------------------------------------
    def text_format(self, current=True):
        return self._text_format if current else self._prev_text_format

    # -------------------------------------------------------------------------
    def highlighter(self):
        return self._highlighter

    # -------------------------------------------------------------------------
    def set_enabled_save(self, is_enabled):
        self._is_modified = is_enabled
        self.enabled_save_signal.emit(is_enabled)

    # -------------------------------------------------------------------------
    def get_path(self):
        return os.path.dirname(self._file_path) if self._file_path else ""

    # -------------------------------------------------------------------------
    def get_name(self):
        if self.is_help_text():
            return self.tr("User manual")
        name = "* " if self._is_modified else ""
        if self._file_path:
            name += self._file_path.replace("\\", "/").split("/")[-1]
        else:
            name += self.tr("Untitled")
        return name

    # -------------------------------------------------------------------------
    def retranslate_ui(self):
        self._editor.set_option(retranslate=True)

    # -------------------------------------------------------------------------
    def _load(self):  # pragma: no cover
        if not self._file_path:
            return ""
        if not os.path.exists(self._file_path):
            return ""
        with open(self._file_path, encoding="utf-8") as file:
            return file.read()

    # -------------------------------------------------------------------------
    def save(self):  # pragma: no cover
        self._editor.save()

    # -------------------------------------------------------------------------
    def get_filename_for_save(self):  # pragma: no cover
        filedialog = QFileDialog(self)
        filedialog.setOption(QFileDialog.DontUseNativeDialog)
        filedialog.setAcceptMode(QFileDialog.AcceptSave)

        filedialog.setDirectory(self._parent.cfg.get(
            "TextEditor/LastPath", ".", system=True))

        if filedialog.exec_():
            self._file_path = filedialog.selectedFiles()[0]
            self._parent.cfg["SYSTEM", "TextEditor/LastPath"] = (
                os.path.dirname(self._file_path))
            return True

        return False

    # -------------------------------------------------------------------------
    def save_as(self):  # pragma: no cover
        old_file_path = self._file_path
        if not os.path.exists(old_file_path):
            return
        if self.get_filename_for_save():
            self._prev_text_format = self._text_format
            if self.is_modified():
                self.save()
            else:
                shutil.copy(old_file_path, self._file_path)

    # -------------------------------------------------------------------------
    def _save(self, txt):  # pragma: no cover
        if not self._file_path:
            if not self.get_filename_for_save():
                return False
        self._prev_text_format = self._text_format
        with open(self._file_path, "w", encoding="utf-8") as file:
            file.write(txt)

        if self._func_after_save is not None:
            self._func_after_save()

    # -------------------------------------------------------------------------
    def is_help_text(self):
        """
        Is the text a user guide ?
        """
        if not self.file_path():
            return False
        path_doc = os.path.join(realpath(os.path.dirname(__file__)), "doc")
        path_doc = path_doc.replace("\\", "/")
        path = self.file_path().replace(path_doc, "")
        name = path.split(".")[0][1:]
        return path.endswith(".html") and name == "demoedit"
