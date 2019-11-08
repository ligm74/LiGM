#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""The main class for the embeddable text editor."""

import os
import sys
from abc import ABCMeta
from typing import Dict
from PyQt5.Qt import (QAction, QIcon, QWidget, Qt, QObject, QTextCursor,
                      QTextEdit, QCursor, QFileDialog, QFileInfo, QColor,
                      QTextDocument, pyqtSignal, QWidgetAction, QLabel,
                      QImageReader, QLocale)
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter
from ligm.core.common import img, ConfigHelper
from ligm.core.qt import BlockSignals, yes_no
from .abstract import IEditor
from .doc import Doc
from .view import View, ImageSize
from .syntax_python import PythonHighlighter
from .syntax_sql import SQLHighlighter
from ..spell import SpellChecker, SpellHighlighter
from ..keyswitcher import KeySwitcher
from ligm.core.qt import TestableWidget


# =============================================================================
class IQWidgetEditor(ABCMeta, type(QObject)):
    def __init__(cls, name, bases, attrs):
        super(IQWidgetEditor, cls).__init__(name, bases, attrs)


# =============================================================================
class TextEditor(TestableWidget, IEditor, metaclass=IQWidgetEditor):

    enabled_save_signal = pyqtSignal(bool)     # for update status "Save"

    # constans for copying text format
    NORMAL_MODE = 1
    READY_TO_FORMAT_COPY = 2
    COPY_FORMAT = 3

    # -------------------------------------------------------------------------
    def __init__(self, parent: QWidget, config, **params):
        super(TextEditor, self).__init__(None)

        self._parent = parent

        # add keys for local vars
        for p in ["PlainText", "Font", "FontSize", "ShowLineNumbers",
                  "WordWrap", "HighlightCurrentLine", "ShowToolBar",
                  "ShowStatusBar", "AutoSave"]:
            params["TextEditor/" + p] = ""
        textmode = "format" in params and params["format"].upper() != "HTML"

        self._load = params["load"] if "load" in params else lambda:  ""
        self._save = params["save"] if "save" in params else lambda x: True
        self._cfg = ConfigHelper(config, **params)
        self._init_params_in_cfg()
        self._set_vars(textmode)
        self._doc = Doc(self._cfg)
        margins = params["margins"] if "margins" in params else None
        self._view = View(self, self._cfg, margins)

        self._spell = params["spell"] if "spell" in params else None
        if not self._spell:
            self._spell = SpellChecker()
        self._spell.change_enabled.connect(self._rehighlight)

        auto_key_switch = "auto_key_switch" in params
        cond1 = auto_key_switch and not params["auto_key_switch"]
        cond2 = not auto_key_switch and QLocale.system().name() == "en_EN"
        if cond1 or cond2:
            self._keyswitcher = None  # pragma: no cover
        else:
            self._keyswitcher = KeySwitcher(self._view.text, self._spell)

        self._highlighter = ""
        self._highlighter_cls = None
        self._set_highlighter(self._highlighter)

        self._view.text.setAcceptRichText(
            not self._cfg.get("TextEditor/PlainText", 0))

        self._actions: Dict[str, QAction] = {}
        self._make_actions()
        self._bind_controls()

        # code for copying text format
        self._current_format = self._view.text.currentCharFormat()
        self._copy_format_mode = TextEditor.NORMAL_MODE

        self._cursor_to_change_word = None

        if "layout" in params:
            params["layout"].addWidget(self)  # pragma: no cover
        if "auto_load" in params and params["auto_load"]:
            self.load()

    # -------------------------------------------------------------------------
    @property
    def view(self):
        return self._view

    # -------------------------------------------------------------------------
    @property
    def doc(self):
        return self._doc

    # -------------------------------------------------------------------------
    def _set_vars(self, textmode):
        branch = "TextEditor/"
        if textmode:
            self._cfg[f"{branch}PlainText"] = 1
            self._cfg[f"{branch}WordWrap"] = 0
            fname, fsize, line_num, highlight_cur_line = (
                self._cfg.get(f"{branch}MonospaceFont", "", system=True),
                self._cfg.get(f"{branch}MonospaceFontSize", 10, system=True),
                self._cfg.get(f"{branch}ShowLineNumbersInTextMode", 1),
                self._cfg.get(f"{branch}HighlightCurrentLineInTextMode", 1))
            self._cfg[f"{branch}ShowToolBar"] = 0
            self._cfg[f"{branch}ShowStatusBar"] = 1
        else:
            self._cfg[f"{branch}PlainText"] = 0
            self._cfg[f"{branch}WordWrap"] = 1
            fname, fsize, line_num, highlight_cur_line = (
                self._cfg.get(f"{branch}HtmlFont", "", system=True),
                self._cfg.get(f"{branch}HtmlFontSize", 10, system=True),
                False, False)
            self._cfg[f"{branch}ShowToolBar"] = 1
            self._cfg[f"{branch}ShowStatusBar"] = 0

        self._cfg[f"{branch}Font"] = fname
        self._cfg[f"{branch}FontSize"] = fsize
        self._cfg[f"{branch}ShowLineNumbers"] = line_num
        self._cfg[f"{branch}HighlightCurrentLine"] = highlight_cur_line

    # -------------------------------------------------------------------------
    def _actions_data(self):
        for name, title, triggered in (
                # toolbar actions
                ("save", self.tr("Save document"), self.save),
                ("bold", self.tr("Bold font"), self._doc.bold),
                ("hline", self.tr("Insert line"), self._doc.hline),
                ("list", self.tr("Insert list"), self._doc.blist),
                ("number", self.tr("Insert numbered list"), self._doc.nlist),
                ("image", self.tr("Insert image"), self._insert_image),
                ("format", self.tr("Copy format"), self._prepare_copy_format),
                ("eraser", self.tr("Clear format"), self._clear_format),
                ("invisible-symbol", self.tr("Show hidden char"), None),

                # popup menu actions
                ("toPDF", self.tr("Save to PDF"), self._save_pdf),
                ("print", self.tr("Print"), self._print_text),

                # table actions
                ("add-row", self.tr("Add row"), self._doc.add_row),
                ("add-col", self.tr("Add column"), self._doc.add_col),
                ("del-row", self.tr("Delete row"), self._doc.del_row),
                ("del-col", self.tr("Delete column"), self._doc.del_col),
                ("ins-row", self.tr("Insert row"), self._doc.ins_row),
                ("ins-col", self.tr("Insert column"), self._doc.ins_col),
                ("merge-cells", self.tr("Merge cells"), self._doc.merge_cells),
                ("split-cells", self.tr("Split cells"), self._doc.split_cells),

                # search/replace actions
                ("find-all", self.tr("Find all"),
                 lambda: self.search(show_msg=True)),
                ("find-prev", self.tr("go to previous"),
                 lambda: self._search(forward=True)),
                ("find-next", self.tr("go to next"),
                 lambda: self._search(forward=False)),
                ("replace", self.tr("Replace"), self._replace),
                ("replace-all", self.tr("Replace all"), self._replace_all),
        ):
            yield name, title, triggered

    # -------------------------------------------------------------------------
    def _make_actions(self):
        self._actions: Dict[str, QAction] = {}
        for name, title, triggered in self._actions_data():
            self._actions[name] = QAction(title, None)
            self._actions[name].setIcon(QIcon(img("editor/" + name)))
            if triggered:
                self._actions[name].triggered.connect(triggered)

        self._actions["bold"].setCheckable(True)
        self._actions["invisible-symbol"].setCheckable(True)
        self._actions["save"].setEnabled(False)

        self._retranslate_ui()

    # -------------------------------------------------------------------------
    def _set_readonly(self, value=True):
        self._set_toolbar_enabled(not value)
        self._view.text.setReadOnly(value)

    # -------------------------------------------------------------------------
    def _set_toolbar_enabled(self, value=True):
        for name in ["save", "bold", "hline", "image", "list", "number",
                     "format", "eraser", "invisible-symbol"]:
            self._actions[name].setEnabled(value)
        if value:
            self._actions["save"].setEnabled(self._doc.is_modified())
        self._view.toolbar.controls["font-name"].setEnabled(value)
        self._view.toolbar.controls["font-size"].setEnabled(value)
        self._view.toolbar.controls["font-color"].setEnabled(value)
        self._view.toolbar.controls["align"].setEnabled(value)
        self._view.toolbar.controls["table"].setEnabled(value)
        self._view.toolbar.controls["background-color"].setEnabled(value)

    # -------------------------------------------------------------------------
    def _set_btn_save_visible(self, value=True):
        self._view.toolbar.controls["save"].setVisible(value)

    # -------------------------------------------------------------------------
    def _set_align_menu(self):
        self._view.toolbar.controls["align"].set_enable_vertical_align(
            self._doc.in_table())

    # -------------------------------------------------------------------------
    def _bind_controls(self):
        self._view.text.setDocument(self._doc.text)

        # for update the status bar
        self._doc.changed_status.connect(self._view.status.set)

        # for update buttons
        self._doc.changed_bold.connect(self._actions["bold"].setChecked)
        self._doc.enabled_save.connect(self._enabled_save)

        self._actions["invisible-symbol"].triggered.connect(
            lambda: self._doc.show_hide_hidden_char(
                self._actions["invisible-symbol"].isChecked()))

        # for font name and size
        self._view.toolbar.controls["font-name"].currentTextChanged.connect(
            self._change_font_name)
        self._view.toolbar.controls["font-size"].valueChanged.connect(
            self._change_font_size)

        # for colors
        self._view.toolbar.controls["font-color"].select_color.connect(
            self._color)
        self._view.toolbar.controls["background-color"].select_color.connect(
            self._background_color)

        # for table
        self._view.toolbar.controls["table"].insert_table.connect(
            self._ins_table)

        # for aligment text
        self._view.toolbar.controls["align"].select_align.connect(
            self._doc.text_align)

        # to track ALL text changes
        self._view.text.cursorPositionChanged.connect(self._position_changed)
        self._view.text.textChanged.connect(
            lambda: self._doc.change(self._view.text.textCursor()))

        # binding ToolButtons to Actions
        for name, btn in self._view.toolbar.controls.items():
            if name in self._actions:
                btn.setDefaultAction(self._actions[name])

        # code for copying text format
        self._view.text.mousePressEvent = self._mouse_press_on_text
        self._view.text.mouseReleaseEvent = self._mouse_release_on_text

        # context menu for QTextEdit
        self._view.text.setContextMenuPolicy(Qt.CustomContextMenu)
        self._view.text.customContextMenuRequested.connect(self._context_menu)

        # for enable drop image to QTextEdit
        self._view.text.insertFromMimeData = self._insert_from_mime_data
        self._view.text.canInsertFromMimeData = self._can_insert_from_mime_data
        self._view.text.createMimeDataFromSelection = self._create_mime_data

        # search panel
        for name, btn in self._view.search_replace.controls.items():
            if name in self._actions:
                btn.setDefaultAction(self._actions[name])

        self.keyPressEvent = self._key_press_event
        self._old_text_key_press = self._view.text.keyPressEvent
        self._view.text.keyPressEvent = self._key_press_event

    # -------------------------------------------------------------------------
    def _clear_selection(self):
        cursor = self._view.text.textCursor()
        cursor.clearSelection()
        self._view.text.setTextCursor(cursor)

    # -------------------------------------------------------------------------
    def _color(self, color):
        self._doc.color(color)
        self._clear_selection()

    # -------------------------------------------------------------------------
    def _background_color(self, color):
        self._doc.background_color(color)
        self._clear_selection()

    # -------------------------------------------------------------------------
    def _restore_cursor(self):
        # clear copy format mode (if need)
        if self._copy_format_mode == TextEditor.READY_TO_FORMAT_COPY:
            self._view.text.viewport().setCursor(self._view.cursors["normal"])
            self._copy_format_mode = TextEditor.NORMAL_MODE

    # -------------------------------------------------------------------------
    def _enabled_save(self, is_enabled):
        self._restore_cursor()
        self._actions["save"].setEnabled(is_enabled)
        self.enabled_save_signal.emit(is_enabled)

        if self._doc.is_modified():
            if self._cfg.get("TextEditor/AutoSave", 0):
                self.save()

    # -------------------------------------------------------------------------
    def _key_press_event(self, event):
        if self._keyswitcher:
            for key_event in self._keyswitcher.key_press(event):
                self._key_press_events_(key_event)

            self._view.toolbar.controls["auto-lang"].setText(
                self._keyswitcher.current_lang() + "   ")
            self._view.toolbar.controls["auto-lang"].setEnabled(
                self._keyswitcher.enabled())
        else:
            self._key_press_events_(event)
            self._view.toolbar.controls["auto-lang"].setText("")

    # -------------------------------------------------------------------------
    def _key_press_events_(self, event):

        key = event.key()
        ctrl = event.modifiers() & Qt.ControlModifier
        shift = event.modifiers() & Qt.ShiftModifier
        text_focus = self._view.text.hasFocus()

        if key == Qt.Key_D and ctrl and text_focus:
            self._doc.ins_date()

        elif key == Qt.Key_T and ctrl and text_focus:
            self._doc.ins_time()

        elif key == Qt.Key_P and ctrl:
            self._print_text()

        elif (key == Qt.Key_S and ctrl) or key == Qt.Key_F2:
            self.save()

        elif (key in (Qt.Key_R, Qt.Key_F) and ctrl) or key == Qt.Key_Escape:
            # disable replace text in read only mode
            if not(self._view.text.isReadOnly() and key == Qt.Key_R):
                self._view.show_hide_search_panel(key)

        elif not shift and key == Qt.Key_F3:
            self._search()

        elif shift and key == Qt.Key_F3:
            self._search(forward=True)

        elif text_focus:
            self._old_text_key_press(event)

    # -------------------------------------------------------------------------
    def _prepare_copy_format(self):
        self._current_format = self._view.text.currentCharFormat()

        if self._copy_format_mode == TextEditor.NORMAL_MODE:
            self._view.text.viewport().setCursor(self._view.cursors["copyfmt"])
            self._copy_format_mode = TextEditor.READY_TO_FORMAT_COPY
        else:
            self._view.text.viewport().setCursor(self._view.cursors["normal"])
            self._copy_format_mode = TextEditor.NORMAL_MODE

    # -------------------------------------------------------------------------
    def _mouse_press_on_text(self, event):

        if event.button() == Qt.LeftButton:
            if self._copy_format_mode == TextEditor.READY_TO_FORMAT_COPY:
                self._copy_format_mode = TextEditor.COPY_FORMAT

        QTextEdit.mousePressEvent(self._view.text, event)

    # -------------------------------------------------------------------------
    def _mouse_release_on_text(self, event):

        if self._copy_format_mode == TextEditor.COPY_FORMAT:
            self._doc.copy_format(self._current_format)
            self._doc.change(self._view.text.textCursor())

        self._view.text.viewport().setCursor(self._view.cursors["normal"])
        self._copy_format_mode = TextEditor.NORMAL_MODE

        QTextEdit.mouseReleaseEvent(self._view.text, event)

    # -------------------------------------------------------------------------
    def _clear_format(self):
        """
        Clearing format ALL text
        """
        msg = self.tr("Are you sure want for clear text formatting ?")
        if yes_no(msg, self):
            self._doc.clear_format()

    # -------------------------------------------------------------------------
    def _font_name_color(self, color: str):
        """
        Set color for edit line in QFontComboBox
        """
        self._view.toolbar.controls["font-name"].setStyleSheet(
            "QComboBox:editable {color: " + color + ";}")

    # -------------------------------------------------------------------------
    def _change_font_size(self, size):
        self._doc.font_size(size)
        self._view.text.setFontPointSize(size)
        self._doc.change(self._view.text.textCursor())

    # -------------------------------------------------------------------------
    def _change_font_name(self, font_name):
        font = self._view.text.textCursor().charFormat().font()
        font.setFamily(font_name)
        self._font_name_color("black")
        self._doc.font(font)
        self._view.text.setCurrentFont(font)
        self._doc.change(self._view.text.textCursor())

    # -------------------------------------------------------------------------
    def _position_changed(self):
        self._doc.change(self._view.text.textCursor())
        self._view.contents_change()

        self._set_align_menu()  # update align menu (need if cursor in table)

        # update font controls (bold)
        fmt = self._view.text.textCursor().charFormat()
        self._actions["bold"].setChecked(fmt.font().bold())

        size = max(fmt.font().pointSize(), fmt.font().pixelSize())
        self._update_font_controls(size, fmt.font().family())

    # -------------------------------------------------------------------------
    def _update_font_controls(self, size, name):
        # update font controls (size)
        font_size_control = self._view.toolbar.controls["font-size"]
        with BlockSignals(font_size_control):
            font_size_control.setValue(size)

        # update font controls (name)
        font_name_control = self._view.toolbar.controls["font-name"]
        index = font_name_control.findText(name)
        with BlockSignals(font_name_control):
            font_name_control.setEditText(name)
            self._font_name_color("black" if index >= 0 else "red")

    # -------------------------------------------------------------------------
    def _ins_table(self, table_params):
        self._doc.insert_table(table_params)

    # -------------------------------------------------------------------------
    def _insert_image(self):
        filedialog = QFileDialog(self)
        filedialog.setOption(QFileDialog.DontUseNativeDialog)
        filedialog.setDefaultSuffix("*.jpg")
        filedialog.setDirectory(self._cfg.get(
            "TextEditor/LastPath", ".", system=True))

        type_files = (
            self.tr("JPEG (*.jpg)"),
            self.tr("GIF (*.gif)"),
            self.tr("PNG (*.png)"),
            self.tr("BMP (*.bmp)"),
            self.tr("All files (*)"),
        )
        filedialog.setNameFilters(type_files)

        if filedialog.exec_():
            path = filedialog.selectedFiles()[0]
            fmt = path.split(".")[-1]
            image = QImageReader(path).read()
            self._doc.ins_image(image, fmt, image.width(), image.height())
            self._cfg["SYSTEM", "TextEditor/LastPath"] = (
                os.path.dirname(path))

    # -------------------------------------------------------------------------
    def _insert_from_mime_data(self, source):
        if source.hasImage():
            formats = [f for f in source.formats() if f.startswith("image")]

            if sys.platform[:3] == 'win':
                formats = [f for f in source.formats() if "image" in f]
                if formats:
                    formats = ["/png"]
            if formats:
                fmt = formats[0].split("/")[-1]
                image = source.imageData()
                self._doc.ins_image(image, fmt, image.width(), image.height())
                return
        QTextEdit.insertFromMimeData(self._view.text, source)

    # -------------------------------------------------------------------------
    def _create_mime_data(self):
        """Creates a mime data object from selection"""
        mime_data = QTextEdit.createMimeDataFromSelection(self._view.text)

        if mime_data.hasHtml():
            image, _, _, _ = self._doc.get_image(mime_data.html())
            if image:
                mime_data.setImageData(image)  # pragma: no cover
        return mime_data

    # -------------------------------------------------------------------------
    def _can_insert_from_mime_data(self, source):
        return (source.hasImage() or
                QTextEdit.canInsertFromMimeData(self._view.text, source))

    # -------------------------------------------------------------------------
    def _change_image_size(self, param_):
        (image, width, height, fmt) = param_
        t = ImageSize(self, width, height, image.width(), image.height())
        if t.exec_():
            width, height = t.params["width"], t.params["height"]
            self._doc.ins_image(image, fmt, width, height, insert_space=False)

    # -------------------------------------------------------------------------
    def _context_menu(self, pos):
        text = self._view.text

        if not text.textCursor().hasSelection():
            # move to mouse position
            text.setTextCursor(text.cursorForPosition(pos))

        image, width, height, fmt = None, -1, -1, ""
        if self._doc.in_image():
            # select image
            text.setTextCursor(text.cursorForPosition(pos))
            cursor = text.textCursor()
            p = cursor.position()
            cursor.setPosition(p)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            text.setTextCursor(cursor)
            if "<img" not in cursor.selection().toHtml():
                cursor.setPosition(p)
                cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
                text.setTextCursor(cursor)

            image, width, height, fmt = (
                self._doc.get_image(cursor.selection().toHtml()))

        menu = text.createStandardContextMenu()

        # ---------------------------------------------------------------------
        # menu for change size of image
        if image:
            menu.insertSeparator(menu.actions()[0])
            param = (image, width, height, fmt)
            change_size = QAction(self.tr("Change size of image"), None)
            change_size.triggered.connect(
                lambda y, x=param: self._change_image_size(x))
            menu.insertAction(menu.actions()[0], change_size)

        # ---------------------------------------------------------------------
        # menu for spell checker
        if self._spell.enabled() and text.toPlainText():

            old_cur = text.textCursor()
            cursor = text.cursorForPosition(pos)
            curchar = text.document().characterAt(cursor.position())
            isalpha = curchar.isalpha()
            cursor.select(QTextCursor.WordUnderCursor)

            word = ""
            if isalpha:
                text.setTextCursor(cursor)
                word = cursor.selectedText()

            text.setTextCursor(old_cur)

            if word and not self._spell.check_word(word):

                to_dict_action = QAction(
                    self.tr("Add to the dictionary"), None)
                to_dict_action.triggered.connect(
                    lambda y, x=word: self._add_word_to_spell(x))
                font = to_dict_action.font()

                repl_actions = []
                to_repl = self._spell.candidates(word)
                if to_repl:
                    self._cursor_to_change_word = cursor
                    font.setBold(True)
                    enabled = not self._view.text.isReadOnly()
                    for wrd in to_repl:
                        repl_actions.append(QAction(wrd, None))
                        repl_actions[-1].setFont(font)
                        repl_actions[-1].setEnabled(enabled)
                        repl_actions[-1].triggered.connect(
                            lambda y, x=wrd: self._fix_word(x))
                else:
                    repl_actions.append(QWidgetAction(self))
                    label = QLabel(self.tr("There are no words to replace"))
                    label.setContentsMargins(28, 6, 6, 6)
                    label.setStyleSheet("color: red")
                    repl_actions[0].setDefaultWidget(label)
                    repl_actions[0].setEnabled(False)

                menu.insertSeparator(menu.actions()[0])
                menu.insertAction(menu.actions()[0], to_dict_action)
                menu.insertSeparator(menu.actions()[0])

                for a in reversed(repl_actions):
                    menu.insertAction(menu.actions()[0], a)

        # ---------------------------------------------------------------------
        # solving the problem of missing icons in Windows
        name_actions = {
            self.tr("Undo"): "Undo",
            self.tr("Redo"): "Redo",
            self.tr("Cut"): "Cut",
            self.tr("Copy"): "Copy",
            self.tr("Paste"): "Paste",
            self.tr("Delete"): "Delete",
        }
        for a in menu.actions():
            txt = a.text().replace("&", "")
            if txt in name_actions:
                a.setIcon(QIcon(img(f"edit-{name_actions[txt].lower()}")))

        # ---------------------------------------------------------------------
        # menu for table
        if self._doc.in_table() and not self._view.text.isReadOnly():
            menu.addSeparator()
            t_menu = menu.addMenu(self.tr("Table"))
            t_menu.addAction(self._actions["add-row"])
            t_menu.addAction(self._actions["add-col"])
            t_menu.addSeparator()
            t_menu.addAction(self._actions["del-row"])
            t_menu.addAction(self._actions["del-col"])
            t_menu.addSeparator()
            t_menu.addAction(self._actions["ins-row"])
            t_menu.addAction(self._actions["ins-col"])
            t_menu.addSeparator()
            t_menu.addAction(self._actions["merge-cells"])
            t_menu.addAction(self._actions["split-cells"])

            cursor = text.textCursor()
            self._actions["merge-cells"].setEnabled(cursor.hasSelection())
            cell = cursor.currentTable().cellAt(cursor)
            self._actions["split-cells"].setEnabled(
                cell.rowSpan() > 1 or cell.columnSpan() > 1)

        menu.addSeparator()
        menu.addAction(self._actions["toPDF"])
        menu.addAction(self._actions["print"])

        menu.exec_(QCursor().pos())
        self._restore_cursor()

    # -------------------------------------------------------------------------
    def _fix_word(self, word):
        if self._cursor_to_change_word:
            self._view.text.setTextCursor(self._cursor_to_change_word)
            self._view.text.insertPlainText(word)
            self._cursor_to_change_word = None

    # -------------------------------------------------------------------------
    def _add_word_to_spell(self, word):
        self._spell.add_word(word)
        self._rehighlight()

    # -------------------------------------------------------------------------
    def _rehighlight(self):
        if self._highlighter_cls:
            self._highlighter_cls.rehighlight()

    # -------------------------------------------------------------------------
    def _print_text(self):  # pragma: no cover
        dialog = QPrintPreviewDialog()
        dialog.paintRequested.connect(self._view.text.print_)
        dialog.exec_()

    # -------------------------------------------------------------------------
    def _save_pdf(self):  # pragma: no cover
        filename = QFileDialog().getSaveFileName(
            self, self.tr("Export document to PDF"), "",
            self.tr("PDF files (*.pdf)"), options=QFileDialog.ShowDirsOnly)[0]
        if filename:
            if not QFileInfo(filename).suffix():
                filename += ".pdf"

            printer = QPrinter()
            printer.setPageSize(QPrinter.A4)
            printer.setColorMode(QPrinter.Color)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename)
            self._doc.text.print_(printer)

    # -------------------------------------------------------------------------
    def _retranslate_ui(self):
        for name, title, _ in self._actions_data():
            self._actions[name].setText(title)
            self._actions[name].setStatusTip(title)
            self._actions[name].setToolTip(title)

        self._view.retranslate_ui()
        self._doc.change()  # for update status bar

    # -------------------------------------------------------------------------
    def _search(self, forward=False):
        find_text = self._view.search_replace.controls["search-edit"].text()
        txt = self.tr("End of document.")
        flags = QTextDocument.FindFlags()
        if self._view.search_replace.controls["cs-box"].isChecked():
            flags |= QTextDocument.FindCaseSensitively
        if forward:
            flags |= QTextDocument.FindBackward
            txt = self.tr("Begin of document.")
        if not self._view.text.find(find_text, options=flags):
            self._view.show_info(txt)
            return False
        return True

    # -------------------------------------------------------------------------
    def search(self, text="", show_msg=True):  # impl. of interface IEditor
        find_text = self._view.search_replace.controls["search-edit"].text()
        if not show_msg and text.strip():
            find_text = text  # pragma: no cover

        flags = QTextDocument.FindFlags()
        if self._view.search_replace.controls["cs-box"].isChecked():
            flags |= QTextDocument.FindCaseSensitively

        old_cursor = self._view.text.textCursor()
        self._view.text.moveCursor(QTextCursor.Start)
        color = QColor(Qt.yellow).lighter(130)

        extra_sels = []
        while self._view.text.find(find_text, options=flags):
            extra = QTextEdit.ExtraSelection()
            extra.format.setBackground(color)
            extra.cursor = self._view.text.textCursor()
            extra_sels.append(extra)

        self._view.text.setExtraSelections(extra_sels)

        if len(extra_sels) != 0:
            txt = self.tr("Results found")
            txt = f'{txt}: {len(extra_sels)}'
            cursor = self._view.text.textCursor()
            cursor.clearSelection()
            self._view.text.setTextCursor(cursor)
        else:
            txt = self.tr("Nothing found :(")
            self._view.text.setTextCursor(old_cursor)

        if show_msg:
            self._view.show_info(txt)

    # -------------------------------------------------------------------------
    def _replace(self):
        find_text = self._view.search_replace.controls["search-edit"].text()
        repl_text = self._view.search_replace.controls["replace-edit"].text()
        cs_box = self._view.search_replace.controls["cs-box"].isChecked()

        if self._view.text.textCursor().hasSelection():
            txt = self._view.text.textCursor().selection().toPlainText()
            to_repl = find_text.upper() == txt.upper()
            if cs_box:
                to_repl = find_text == txt

            if to_repl:
                self._doc.replace(repl_text)
                self._search()

    # -------------------------------------------------------------------------
    def _replace_all(self):
        find_text = self._view.search_replace.controls["search-edit"].text()
        repl_text = self._view.search_replace.controls["replace-edit"].text()

        flags = QTextDocument.FindFlags()
        if self._view.search_replace.controls["cs-box"].isChecked():
            flags |= QTextDocument.FindCaseSensitively

        old_cursor = self._view.text.textCursor()
        self._view.text.moveCursor(QTextCursor.Start)

        cnt = 0
        while self._view.text.find(find_text, options=flags):
            cnt += 1

        self._view.text.setTextCursor(old_cursor)
        if not cnt:
            return

        txt = (self.tr("Results found: ") + str(cnt) +
               self.tr(". Replace everything ?"))
        if not yes_no(txt, self):
            return

        cnt = 0
        self._view.text.moveCursor(QTextCursor.Start)
        while self._view.text.find(find_text, options=flags):
            self._doc.replace(repl_text)
            cnt += 1

        if cnt:
            txt = self.tr("Replacements done")
            self._view.show_info(f'{txt}: {cnt}')

    # -------------------------------------------------------------------------
    def _clear_highlighter(self):
        if self._highlighter_cls:
            self._highlighter_cls.setDocument(None)

    # -------------------------------------------------------------------------
    def _set_highlighter_cls(self, highlighter_cls):
        self._clear_highlighter()
        if self._cfg.get("TextEditor/PlainText", 1):
            if highlighter_cls:
                self._highlighter_cls = highlighter_cls(self._doc.text)
        else:
            if self._spell.enabled():
                self._highlighter_cls = SpellHighlighter(
                    self._doc.text, self._spell)

    # -------------------------------------------------------------------------
    def _set_highlighter(self, highlighter):

        if highlighter.upper() in ["PYTHON", "SQL"]:
            self._highlighter = highlighter
            if highlighter.upper() == "PYTHON":
                self._set_highlighter_cls(PythonHighlighter)
            if highlighter.upper() == "SQL":
                self._set_highlighter_cls(SQLHighlighter)
        else:
            self._highlighter = ""
            self._set_highlighter_cls(None)
        self._view.status.set({"center": self._highlighter})

    # -------------------------------------------------------------------------
    def _set_format_text(self):
        self._doc.set_default_font()
        self._doc.clear_format()
        self._set_highlighter(self._highlighter)

    # -------------------------------------------------------------------------
    def _set_format_html(self):
        self._doc.set_default_font(True)
        self._update_font_controls(
            self._cfg.get("TextEditor/FontSize", 1),
            self._cfg.get("TextEditor/Font", ""))
        self._set_highlighter(self._highlighter)

    # -------------------------------------------------------------------------
    def set_option(self, **options):  # implementation of interface IEditor

        # ---------------------------------------------------------------------
        if "retranslate" in options:
            self._retranslate_ui()

        # ---------------------------------------------------------------------
        if "format" in options:
            old_txt_mode = self._cfg.get("TextEditor/PlainText", 0)
            new_txt_mode = options["format"].upper() != "HTML"
            if old_txt_mode == new_txt_mode:
                return False

            if new_txt_mode:
                msg1 = self.tr("Text formatting will be lost")
                msg2 = self.tr("do you want to continue ?")
                if not yes_no(f"{msg1},\n{msg2}", self):
                    return False

            self._set_vars(new_txt_mode)
            self._view.update_ui()
            if new_txt_mode:
                self._set_format_text()
            else:
                self._set_format_html()

            return True

        # ---------------------------------------------------------------------
        if "highlighter" in options:
            self._set_highlighter(options["highlighter"])

        # ---------------------------------------------------------------------
        if "invisible_symbol" in options:
            self._actions["invisible-symbol"].trigger()

        # ---------------------------------------------------------------------
        if "word_wrap" in options:
            self._cfg["TextEditor/WordWrap"] = (
                not self._cfg.get("TextEditor/WordWrap", 0))
            self._view.update_ui()

        # ---------------------------------------------------------------------
        if "btn_save_visible" in options:
            self._set_btn_save_visible(options["btn_save_visible"])

        # ---------------------------------------------------------------------
        if "readonly" in options:
            self._set_readonly(options["readonly"])

        # ---------------------------------------------------------------------
        if "auto_save" in options:
            self._cfg["TextEditor/AutoSave"] = options["auto_save"]
            self._set_btn_save_visible(not bool(options["auto_save"]))

        # ---------------------------------------------------------------------
        if "margin_line" in options:
            self._cfg["TextEditor/MarginLine"] = options["margin_line"]
            self._view.update_ui()

        # ---------------------------------------------------------------------
        if "show_status_bar" in options:
            self._cfg["TextEditor/ShowStatusBar"] = options["show_status_bar"]
            self._view.update_ui()

    # -------------------------------------------------------------------------
    def get_option(self, name):  # implementation of interface IEditor
        if name == "word-wrap":
            return self._cfg.get("TextEditor/WordWrap", 0)
        if name == "readonly":
            return self._view.text.isReadOnly()

    # -------------------------------------------------------------------------
    def save(self):  # implementation of interface IEditor
        self._doc.save(self._save)

    # -------------------------------------------------------------------------
    def load(self):  # implementation of interface IEditor
        with BlockSignals(self._view.text):
            self._doc.load(self._load)
        self._view.text.moveCursor(QTextCursor.Start)

    # -------------------------------------------------------------------------
    def get_text(self):  # implementation of interface IEditor
        return self._doc.get_text()

    # -------------------------------------------------------------------------
    def is_empty(self):  # implementation of interface IEditor
        return self._doc.is_empty()

    # -------------------------------------------------------------------------
    def _init_params_in_cfg(self):
        """Save initial setting values"""
        sz = 10 if sys.platform == "linux" else 11
        nm = "DejaVu Sans Mono" if sys.platform == "linux" else "Courier New"

        # default values
        for key, value in {
            "TextEditor/ShowLineNumbersInTextMode": 1,
            "TextEditor/HighlightCurrentLineInTextMode": 1,
            "-TextEditor/HighlightCurrentLineColor": "#FFFFC8",
            "-TextEditor/Background": "#F0F0FF",
            "-TextEditor/MonospaceFont": nm,
            "-TextEditor/MonospaceFontSize": sz,
            "-TextEditor/HtmlFont": "Arial",
            "-TextEditor/HtmlFontSize": 11,
            "TextEditor/IndentWidth": 30,
            "-TextEditor/BackgroundLineNumberArea": "#E8E8E8",
            "-TextEditor/NumberColorLineNumberArea": "gray",
            "TextEditor/MarginLine": 79,
            "TextEditor/PaddingInTable": 3,
            "TextEditor/SpaceInTable": 0,
            "TextEditor/TimeoutBalloon": 3000,
            "TextEditor/ReplaceTabWithSpace": 1,
            "TextEditor/CountSpaceInTab": 4,
        }.items():
            key_name = key if key[0] != "-" else key[1:]
            system = key[0] == "-"
            # check for existence
            if self._cfg.get(key_name, -1, system=system) == -1:
                if system:
                    self._cfg["SYSTEM", key_name] = value
                else:
                    self._cfg[key_name] = value
