# LiGM

Ligm.Editor designed to demonstrate the integration of a simple editor into PyQt applications.

Built-in editor allows you to work:
* with text files with the ability to highlight the syntax of the code (currently implemented highlighting SQL and Python)
* with files containing formatted HTML text (in WYSIWYG mode). The editor has only the most basic elements of text formatting, such as font, size, color, etc. In addition to simple text formatting, work with HTML tables (insert tables, add/remove rows and columns) and images (insert, change the size) is implemented.

In both modes (text and HTML) there is a possibility of spell checking for English and Russian languages, preview and print the document, export to pdf. Ctrl-F, Ctrl-R, F3 (Shift-F3) are used to search and replace text. In addition to these combinations, there are combinations Ctrl-S and F 2 to save, Ctrl-D, Ctrl-T to insert the date and time, Ctrl-P-to print. 

If the system is set to Russian locale by default, it works automatically switching the input language (Ctrl-L-enable / disable automatic replacement) and replacing the text typed in the wrong encoding (F12).

## Editor appearance:

Fig. 1 - example of a document with a table and picture
Fig. 2 - example of correcting errors in the text
Fig. 3 - example source code (Python)
Fig. 4 - example source code (SQL)

## Dependencies.
It required Python 3.7+, PyQt5.

## Installation.

    pip install ligm.editor
    pip install ligm.spell (dictionaries for spell checking)

After install, run in the terminal `ligm.editor` to start the demo application.

To install only the embedded editor, without the demo application:
    `pip install ligm.core`


## Example of use.

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


 


### Class ligm.core.text.TextEditor:

Parameters of class constructor:
* `parent` - parent widget
* `config` - the configuration class
* `format` - the format of the text (default is HTML) 
* `save` - method to save the text
* `load` - method to load text
* `margins` - borders to display the widget in the parent widget
* `spell` - class spell checker (if not specified, a new class is created), to disable spell checking, you must explicitly specify `spell=False`
* `auto_key_switch` - enable automatic correction of the encoding of the typed text (if the locale in the system is English, this function will be disabled)
* `layout` - if this option is specified, the editor widget will be automatically added to the specified widget
* `auto_load` - automatic call to load text after creating the widget (otherwise you will need to call the method: `editor.load()`)


**save(txt)** - saving text (calls the method passed in the constructor, if the method return a value other than None, it is assumed that it was called unsuccessfully)

**load** - loading text into the editor (calls the method passed in the constructor)

**set_option**  - set the status of the editor

* `retranslate=""` - perform for all GUI elements the translation in the resp. with the current translator
* `format="HTML"` - set HTML/TEXT format
* `highlighter="..."` - activate specified syntax highlighting (--no--, Python, SQL)
* `invisible_symbol=""` - toggle the display of invisible characters
* `word_wrap=""` - switch the word wrap mode
* `btn_save_visible=True/False` - show/hide Save button
* `readonly=True/False` - enable / disable read-only mode
* `auto_save=True/False` - auto-save data after each change
* `margin_line=column` - position of drawing the right border in text mode
* `show_status_bar=True/False`  - show / hide status bar

**get_option(name)**  - return the state of the editor

* `name="word-wrap"` - status word wrap mode
* `name="readonly"` - read-only mode state

**search(text="", show_msg=True)** - starts searching for the text passed in the text parameter or (if text="") specified in the search string

**get_text()** - text in the editor (depends on the format).

**is_empty()** - checking document is empty or not.

