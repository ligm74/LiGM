#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Example class for demonstrate QTestHelper."""


import sys
from PyQt5.Qt import (QApplication, QMessageBox, QTextEdit,
                      QPushButton, QVBoxLayout, Qt)
from ligm.core.qt import TestableDialog, TestableWidget, TestableMessageBox


# =============================================================================
class ExampleDlg(TestableDialog):

    # -------------------------------------------------------------------------
    def __init__(self, parent):
        TestableDialog.__init__(self, parent)
        self.text = QTextEdit()
        self.result = True
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Cancel")
        self.init_ui()

    # -------------------------------------------------------------------------
    def init_ui(self):
        self.setWindowTitle('Example Dialog')
        v = QVBoxLayout()
        self.text.setText("HELLO")
        v.addWidget(self.text, alignment=Qt.Alignment())
        v.addWidget(self.btn_ok, alignment=Qt.Alignment())
        v.addWidget(self.btn_cancel, alignment=Qt.Alignment())
        self.setLayout(v)
        self.btn_ok.clicked.connect(self.ok)
        self.btn_cancel.clicked.connect(self.cancel)

    # -------------------------------------------------------------------------
    def ok(self):
        self.result = True
        self.accept()

    # -------------------------------------------------------------------------
    def cancel(self):
        self.result = False
        self.reject()


# =============================================================================
class Example(TestableWidget):

    # -------------------------------------------------------------------------
    def __init__(self):
        TestableWidget.__init__(self, None)
        self.text = QTextEdit()
        self.btn_msgbox = QPushButton("QMessageBox")
        self.btn_mydlg = QPushButton("My Dlg")
        self.init_ui()

    # -------------------------------------------------------------------------
    def init_ui(self):
        self.setGeometry(900, 300, 500, 320)
        self.setWindowTitle('Simple APP')
        v = QVBoxLayout()
        self.text.setText(
            "In ten hours a day you have time to fall twice as far " +
            "behind your commitments as in five hours a day.\n" +
            "CORRECT:\n" +
            "Data expands to fill the space available for storage."
        )
        self.btn_msgbox.clicked.connect(self.msgbox)
        self.btn_mydlg.clicked.connect(self.mydlg)
        v.addWidget(self.text, alignment=Qt.Alignment())
        v.addWidget(self.btn_msgbox, alignment=Qt.Alignment())
        v.addWidget(self.btn_mydlg, alignment=Qt.Alignment())
        self.setLayout(v)

    # -------------------------------------------------------------------------
    def msgbox(self):
        msg = TestableMessageBox()
        msg.setIcon(QMessageBox.Information)

        text = self.text.textCursor().selection().toPlainText()
        msg.setText(text)
        msg.setWindowTitle("MessageBox")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()
        if retval == QMessageBox.Ok:
            self.text.textCursor().insertText("ERROR for computers")

    # -------------------------------------------------------------------------
    def mydlg(self):
        dlg = ExampleDlg(self)
        dlg.exec_()
        if dlg.result:
            self.text.textCursor().insertText(dlg.text.toPlainText())


# =============================================================================
if __name__ == "__main__":  # pragma: no cover
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())
