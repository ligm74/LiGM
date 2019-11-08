#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Demo for embedded text editor."""

import sys
import os
import json
from typing import Dict
from PyQt5.Qt import (QIcon, Qt, QMenu, QApplication, QAction, QMessageBox,
                      QPoint, QSize)
from PyQt5.QtWidgets import (QComboBox, QLabel, QCheckBox, QFileDialog,
                             QTabWidget)

from ligm.core.text import SpellChecker
from ligm.core.common import img
from ligm.core.qt import (yes_no, install_translators, TestableMainWindow,
                     get_current_language)
from .config import Config
from .tabedit import TabEdit


# =============================================================================
class MainWindow(TestableMainWindow):

    # -------------------------------------------------------------------------
    def __init__(self, test_mode=False):
        super(MainWindow, self).__init__(None)

        self.setWindowIcon(QIcon(img('editor/editor.png')))

        self.cfg = Config()
        self._tabs = QTabWidget()
        self._actions: Dict[str, QAction] = {}
        self._menus: Dict[str, QMenu] = {}
        self._make_actions()
        self._spell = SpellChecker(enabled=not test_mode)
        self._init_ui()

    # -------------------------------------------------------------------------
    def _actions_data(self):
        about_qt = QApplication.instance().aboutQt
        for name, title, triggered in (
                ("new", self.tr("New"), lambda: self.open_file()),
                ("open", self.tr("Open"), self.open),
                ("save", self.tr("Save"), self.save),
                ("save_as", self.tr("Save as ..."), self.saveas),
                ("exit", self.tr("Exit"), self.close),
                ("about", self.tr("About"), self.about),
                ("about_qt", self.tr("About Qt"), about_qt),
                ("help", self.tr("User manual"), lambda: self.help()),
                ("eng", self.tr("English"), lambda: self.set_lang("en_EN")),
                ("rus", self.tr("Russian"), lambda: self.set_lang("ru_RU")),

                ("text", self.tr("Only text"), lambda: self.set_format("txt")),
                ("html", self.tr("HTML"), lambda: self.set_format("html")),
                ("no-syntax", self.tr("--no--"),
                 lambda: self.set_syntax("--no--")),
                ("python", self.tr("Python"),
                 lambda: self.set_syntax("Python")),
                ("sql", self.tr("SQL"), lambda: self.set_syntax("SQL")),
                ("invisible-symbol", self.tr("Show/hide invisible symbol"),
                 self.set_invisible_symbol),
                ("read-only", self.tr("Read only"), self._read_only),
                ("word-wrap", self.tr("Word wrap"), self.word_wrap),

                ("rus-spell", self.tr("russian language"),
                 lambda x: self._spell.set_enabled("rus", x)),
                ("eng-spell", self.tr("english language"),
                 lambda x: self._spell.set_enabled("eng", x)),
        ):
            yield name, title, triggered

    # -------------------------------------------------------------------------
    def _read_only(self):
        if not self._tabs.count():  # pragma: no cover
            return
        w = self._tabs.widget(self._tabs.currentIndex())
        w.set_read_only(not w.is_read_only())
        self.change_tab(self._tabs.currentIndex())

    # -------------------------------------------------------------------------
    def _make_actions(self):
        for name, title, triggered in self._actions_data():
            self._actions[name] = QAction(title, None)
            self._actions[name].setIcon(QIcon(img("editor/" + name)))
            if triggered:
                self._actions[name].triggered.connect(triggered)

    # -------------------------------------------------------------------------
    def retranslate_ui(self):
        for name, title, _ in self._actions_data():
            self._actions[name].setText(title)
            self._actions[name].setStatusTip(title)
            self._actions[name].setToolTip(title)

        self._menus["file"].setTitle(self.tr("&File"))
        self._menus["lang"].setTitle(self.tr("&Language"))
        self._menus["help"].setTitle(self.tr("&Help"))
        self._menus["view"].setTitle(self.tr("&View"))
        self._menus["format"].setTitle(self.tr("&Format"))
        self._menus["syntax"].setTitle(self.tr("&Syntax"))
        self._menus["spell"].setTitle(self.tr("&Check spelling"))

        idx_current = self._tabs.currentIndex()
        idx_help = -1
        for i in range(self._tabs.count()):
            w = self._tabs.widget(i)
            w.retranslate_ui()
            self._tabs.setTabText(i, w.get_name())
            path = (w.get_path() + "/") if not w.is_help_text() else ""
            self._tabs.setTabToolTip(i, f"{path}{w.get_name()}")
            if w.is_help_text():
                idx_help = i

        # if need, reopen user manual with current language
        if idx_help != -1:
            self.close_tab(idx_help)
            self.help(position=idx_help)

        self._tabs.setCurrentIndex(idx_current)
        self.setWindowTitle(self.tr("[Demo] Embedded text editor"))

    # -------------------------------------------------------------------------
    def _init_ui(self):
        self.setWindowTitle(self.tr("[Demo] Embedded text editor"))
        self.setGeometry(800, 150, 1000, 500)

        self._tabs.setTabsClosable(True)
        self._tabs.setMovable(True)
        self._tabs.tabCloseRequested.connect(self.close_tab)
        self._tabs.currentChanged.connect(self.change_tab)
        self.setCentralWidget(self._tabs)

        # Setup the menu
        self._menus["file"] = self.menuBar().addMenu(self.tr("&File"))
        self._menus["view"] = self.menuBar().addMenu(self.tr("&View"))
        self._menus["help"] = self.menuBar().addMenu(self.tr("&Help"))

        # Populate the Menu with Actions
        self._menus["help"].addAction(self._actions["help"])
        self._menus["help"].addSeparator()
        self._menus["help"].addAction(self._actions["about"])
        # self._menus["help"].addAction(self._actions["about_qt"])

        self._menus["file"].addAction(self._actions["new"])
        self._menus["file"].addAction(self._actions["open"])
        self._menus["file"].addAction(self._actions["save"])
        self._menus["file"].addAction(self._actions["save_as"])
        self._menus["file"].addSeparator()

        self._menus["lang"] = self._menus["file"].addMenu(self.tr("&Language"))
        self._menus["lang"].addAction(self._actions["eng"])
        self._menus["lang"].addAction(self._actions["rus"])

        self._menus["file"].addSeparator()
        self._menus["file"].addAction(self._actions["exit"])

        self._menus["format"] = self._menus["view"].addMenu(self.tr("&Format"))
        self._menus["format"].addAction(self._actions["text"])
        self._menus["format"].addAction(self._actions["html"])
        self._menus["syntax"] = self._menus["view"].addMenu(self.tr("&Syntax"))
        self._menus["syntax"].addAction(self._actions["no-syntax"])
        self._menus["syntax"].addAction(self._actions["python"])
        self._menus["syntax"].addAction(self._actions["sql"])
        self._menus["spell"] = self._menus["view"].addMenu(
            self.tr("&Check spelling"))
        self._menus["spell"].addAction(self._actions["eng-spell"])
        self._menus["spell"].addAction(self._actions["rus-spell"])
        self._menus["view"].addSeparator()
        self._menus["view"].addAction(self._actions["word-wrap"])
        self._menus["view"].addAction(self._actions["invisible-symbol"])
        self._menus["view"].addSeparator()
        self._menus["view"].addAction(self._actions["read-only"])

        open_files = json.loads(self.cfg.get("open_files", "{}", system=True))
        for key, (fmt, highlighter) in open_files.items():
            self.open_file(key, fmt=fmt, hl=highlighter)
        if not self._tabs.count():  # pragma: no cover
            self._actions["save"].setEnabled(False)
            self._actions["save_as"].setEnabled(False)

        self._actions["word-wrap"].setCheckable(True)
        self._actions["read-only"].setCheckable(True)

        self._actions["eng-spell"].setCheckable(True)
        self._actions["rus-spell"].setCheckable(True)
        self._actions["eng-spell"].setChecked(True)
        self._actions["rus-spell"].setChecked(True)
        self._actions["eng-spell"].setEnabled(self._spell.enabled("eng"))
        self._actions["rus-spell"].setEnabled(self._spell.enabled("rus"))
        self._menus["spell"].setEnabled(self._spell.enabled("all"))

        self.retranslate_ui()
        self.read_settings()
        self.show()

        if self._tabs.count() > 0:  # pragma: no cover
            self._tabs.widget(self._tabs.currentIndex()).set_focus()
        else:  # pragma: no cover
            self._menus["view"].setEnabled(False)

        if not self._spell.enabled():
            self._menus["spell"].menuAction().setVisible(False)

    # -------------------------------------------------------------------------
    def set_lang(self, locale):
        install_translators(locale)
        self.retranslate_ui()

    # -------------------------------------------------------------------------
    def word_wrap(self):
        if self._tabs.count() > 0:
            self._tabs.widget(self._tabs.currentIndex()).set_word_wrap()

    # -------------------------------------------------------------------------
    def closeEvent(self, event):
        self.write_settings()
        """
        s = (self.tr("This will exit the editor.") + "\n" +
             self.tr("Do you want to continue ?"))
        if yes_no(s, self):
            event.accept()
        else:
            event.ignore()
        """
        open_files = {}
        for i in range(self._tabs.count()):
            w = self._tabs.widget(i)
            if w.is_modified():  # pragma: no cover
                self.save_text_tab(i)
            open_files[w.file_path()] = (w.text_format(False), w.highlighter())
        self.cfg["SYSTEM", "open_files"] = json.dumps(open_files)
        event.accept()

    # -------------------------------------------------------------------------
    def save_text_tab(self, idx_tab):
        w = self._tabs.widget(idx_tab)
        name = w.file_path() if w.file_path() else w.get_name()
        t1 = self.tr("The file")
        t2 = self.tr("is changed")
        t3 = self.tr("Save it ?")
        if w.is_modified():
            if yes_no(f"{t1} <b>{name}</b> {t2}.<br><br>{t3}", self):
                w.save()

    # -------------------------------------------------------------------------
    def close_tab(self, idx_tab):
        self.save_text_tab(idx_tab)
        self._tabs.removeTab(idx_tab)
        if not self._tabs.count():  # pragma: no cover
            self._actions["save"].setEnabled(False)
            self._actions["save_as"].setEnabled(False)
            self._menus["view"].setEnabled(False)

    # -------------------------------------------------------------------------
    def change_tab(self, idx_tab):
        if not self._tabs.count():  # pragma: no cover
            return
        self._menus["view"].setEnabled(True)
        w = self._tabs.widget(idx_tab)
        self._actions["save"].setEnabled(w.is_modified())
        self._tabs.setTabText(idx_tab, w.get_name())
        textmode = w.text_format().upper() != "HTML"
        self._actions["text"].setEnabled(not textmode)
        self._actions["html"].setEnabled(textmode)
        self._actions["word-wrap"].setChecked(w.get_word_wrap())
        self._actions["read-only"].setChecked(
            w.is_read_only() or w.is_help_text())
        self._actions["read-only"].setEnabled(not w.is_help_text())
        self._menus["format"].setEnabled(not w.is_read_only())
        self._menus["syntax"].setEnabled(textmode)
        self._menus["spell"].setEnabled(
            not textmode and self._spell.enabled("all"))

    # -------------------------------------------------------------------------
    def change_enabled_save(self):
        self.change_tab(self._tabs.currentIndex())

    # -------------------------------------------------------------------------
    def about(self):
        text = self.tr("Demo for 'Embedded text editor'")
        author = self.tr("(C) 2019, Vladimir Rukavishnikov")
        QMessageBox().about(self,
                            self.tr("Information"), f"{text}\n\n{author}")

    # -------------------------------------------------------------------------
    def set_format(self, name_format):
        if self._tabs.count() > 0:
            idx = self._tabs.currentIndex()
            self._tabs.widget(idx).set_text_format(name_format)
            self.change_tab(idx)

    # -------------------------------------------------------------------------
    def set_syntax(self, name_syntax):
        if self._tabs.count() > 0:
            self._tabs.widget(
                self._tabs.currentIndex()).set_highlighter(name_syntax)

    # -------------------------------------------------------------------------
    def set_invisible_symbol(self):
        if self._tabs.count() > 0:
            self._tabs.widget(self._tabs.currentIndex()).set_invisible_symbol()

    # -------------------------------------------------------------------------
    def read_settings(self):
        pos = QPoint(self.cfg.get("MainWindow.X", 800, True),
                     self.cfg.get("MainWindow.Y", 150, True))
        sz = QSize(self.cfg.get("MainWindow.width", 1000, True),
                   self.cfg.get("MainWindow.height", 500, True))
        self.move(pos)
        self.resize(sz)

    # -------------------------------------------------------------------------
    def write_settings(self):
        self.cfg["SYSTEM", "MainWindow.X"] = self.pos().x()
        self.cfg["SYSTEM", "MainWindow.Y"] = self.pos().y()
        self.cfg["SYSTEM", "MainWindow.width"] = self.size().width()
        self.cfg["SYSTEM", "MainWindow.height"] = self.size().height()

    # -------------------------------------------------------------------------
    def open_file(self, path=None, fmt="html", hl=""):
        if path is not None and not os.path.exists(path):
            return

        # after saving config file, need to reload the configuration
        is_config_file = path == self.cfg.get("Config/FilePath", "")
        func_after_save = self.cfg.load if is_config_file else None

        te = TabEdit(self, file_path=path, text_format=fmt, highlighter=hl,
                     func_after_save=func_after_save, spell=self._spell)
        idx = self._tabs.addTab(te, te.get_name())
        self._tabs.setCurrentIndex(idx)
        path = (te.get_path() + "/") if not te.is_help_text() else ""
        self._tabs.setTabToolTip(idx, f"{path}{te.get_name()}")
        te.enabled_save_signal.connect(self.change_enabled_save)
        self._actions["save_as"].setEnabled(bool(self._tabs.count()))

        if te.is_help_text():
            self._read_only()

    # -------------------------------------------------------------------------
    def save(self):
        if self._tabs.currentIndex() >= 0:
            self._tabs.widget(self._tabs.currentIndex()).save()
            self.change_tab(self._tabs.currentIndex())

    # -------------------------------------------------------------------------
    def saveas(self):
        self._tabs.widget(self._tabs.currentIndex()).save_as()
        self.change_tab(self._tabs.currentIndex())

    # -------------------------------------------------------------------------
    def open(self):
        """
        File dialog with selections syntax and file type.
        """
        filedialog = QFileDialog(self)
        filedialog.setOption(QFileDialog.DontUseNativeDialog)
        filedialog.setDefaultSuffix("*.*")
        filedialog.setDirectory(self.cfg.get(
            "TextEditor/LastPath", ".", system=True))
        layout = filedialog.layout()

        type_files = [  # type, syntax, is HTML, list of exts
            (self.tr("All files (*)"), self.tr("-- no --"), True, []),
            (self.tr("Python files (*.py *.pyw)"),
             "Python", False, ["py", "pyw"]),
            (self.tr("SQL scripts (*.sql)"), "SQL", False, ["sql"]),
            (self.tr("Text files (*.txt)"),
             self.tr("-- no --"), False, ["txt"]),
        ]
        filedialog.setNameFilters([t[0] for t in type_files])

        syntax = QComboBox()
        __in_cmb = []
        for t in type_files:
            if t[1] not in __in_cmb:
                __in_cmb.append(t[1])
                syntax.addItem(t[1])

        lbl_syntax = QLabel(self.tr("Syntax"))
        format_text = QCheckBox("HTML")
        format_text.setChecked(True)

        col, row = layout.columnCount(), layout.rowCount()
        layout.addWidget(syntax, row, col - 1)
        layout.addWidget(format_text, row, col - 1)
        layout.addWidget(lbl_syntax, row, 0)
        layout.addWidget(syntax, row, col - 2)
        layout.itemAtPosition(row, col - 1).setAlignment(Qt.AlignCenter)

        layout.update()
        layout.activate()

        def _change_syntax_and_type(idx):  # pragma: no cover
            syntax.setCurrentText(type_files[idx][1])
            format_text.setChecked(type_files[idx][2])

        def _filter_selected(name):  # pragma: no cover
            for i, (nm, _, _, _) in enumerate(type_files):
                if name == nm:
                    _change_syntax_and_type(i)

        def _current_changed(name):  # pragma: no cover
            if "." in name:
                ext = name.split(".")[-1].lower()
                for i, (_, _, _, exts) in enumerate(type_files):
                    if ext in exts:
                        _change_syntax_and_type(i)
                        return
            _change_syntax_and_type(0)

        filedialog.currentChanged.connect(_current_changed)
        filedialog.filterSelected.connect(_filter_selected)

        if filedialog.exec_():
            text_format = "html" if format_text.isChecked() else "text"
            path = filedialog.selectedFiles()[0]
            self.open_file(path=path, fmt=text_format, hl=syntax.currentText())
            self.cfg["SYSTEM", "TextEditor/LastPath"] = os.path.dirname(path)

    # -------------------------------------------------------------------------
    def help(self, position=-1):
        """
        Show text description of editor
        """
        # check if already open
        for i in range(self._tabs.count()):
            if self._tabs.widget(i).is_help_text():
                self._tabs.setCurrentIndex(i)
                return

        # open file
        path = os.path.join(os.path.dirname(__file__), "doc")
        lang = "." + get_current_language()
        filepath = f"{path}{os.sep}demoedit{lang}.html"
        if not os.path.exists(filepath):
            filepath = f"{path}{os.sep}demoedit.html"
        if not os.path.exists(filepath):  # pragma: no cover
            return
        self.open_file(filepath, hl="Python")

        if position != -1:
            self._tabs.tabBar().moveTab(self._tabs.count() - 1, position)


# =============================================================================
class Main:  # pragma: no cover

    @staticmethod
    def start():
        os.environ['XDG_SESSION_TYPE'] = ""
        app = QApplication(sys.argv)

        f = app.font()
        f.setPointSize(8 if sys.platform[:3] == 'win' else 10)
        app.setFont(f)

        install_translators()
        MainWindow()
        app.exec_()
