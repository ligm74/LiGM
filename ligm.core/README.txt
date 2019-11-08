Description
===========

LiGM-core: general classes, methods, etc.

Example usage
===========

from PyQt5.Qt import QApplication

from ligm.core.text import TextEditor
from ligm.core.qt import install_translators
from ligm.core.common import SimpleConfig

filename= "example.html"

def load():
    with open(filename, encoding="utf-8") as f:
        return f.read()

def save(txt):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(txt)
    
app = QApplication([])
install_translators()
cfg = SimpleConfig()
editor = TextEditor(None, cfg, save=save, load=load, auto_load=True)
editor.setGeometry(100, 100, 600, 500)
editor.show()
app.exec()

