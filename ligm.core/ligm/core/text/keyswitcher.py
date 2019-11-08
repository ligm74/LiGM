#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Automatic switch the keyboard layout."""

from PyQt5.Qt import (QObject, QKeyEvent, Qt, QEvent, QTextCursor, QCheckBox,
                      QGridLayout, QRadioButton, QPushButton)
from ligm.core.qt.qtest_helper import TestableDialog


FREQ = {
    # ENGLISH
    # Quadgram Frequencies
    "TION": 0.31, "OTHE": 0.16, "THEM": 0.12, "NTHE": 0.27, "TTHE": 0.16,
    "RTHE": 0.12, "THER": 0.24, "DTHE": 0.15, "THEP": 0.11, "THAT": 0.21,
    "INGT": 0.15, "FROM": 0.10, "OFTH": 0.19, "ETHE": 0.15, "THIS": 0.10,
    "FTHE": 0.19, "SAND": 0.14, "TING": 0.10, "THES": 0.18, "STHE": 0.14,
    "THEI": 0.10, "WITH": 0.18, "HERE": 0.13, "NGTH": 0.10, "INTH": 0.17,
    "THEC": 0.13, "IONS": 0.10, "ATIO": 0.17, "MENT": 0.12, "ANDT": 0.10,
    # Trigram Frequencies
    "THE": 1.81, "ERE": 0.31, "HES": 0.24, "AND": 0.73, "TIO": 0.31,
    "VER": 0.24, "ING": 0.72, "TER": 0.30, "HIS": 0.24, "ENT": 0.42,
    "EST": 0.28, "OFT": 0.22, "ION": 0.42, "ERS": 0.28, "ITH": 0.21,
    "HER": 0.36, "ATI": 0.26, "FTH": 0.21, "FOR": 0.34, "HAT": 0.26,
    "STH": 0.21, "THA": 0.33, "ATE": 0.25, "OTH": 0.21, "NTH": 0.33,
    "ALL": 0.25, "RES": 0.21, "INT": 0.32, "ETH": 0.24, "ONT": 0.20,
    # Bigram Frequencies
    "TH": 2.71, "EN": 1.13, "NG": 0.89, "HE": 2.33, "AT": 1.12, "AL": 0.88,
    "IN": 2.03, "ED": 1.08, "IT": 0.88, "ER": 1.78, "ND": 1.07, "AS": 0.87,
    "AN": 1.61, "TO": 1.07, "IS": 0.86, "RE": 1.41, "OR": 1.06, "HA": 0.83,
    "ES": 1.32, "EA": 1.00, "ET": 0.76, "ON": 1.32, "TI": 0.99, "SE": 0.73,
    "ST": 1.25, "AR": 0.98, "OU": 0.72, "NT": 1.17, "TE": 0.98, "OF": 0.71,

    # RUSSIAN
    # Quadgram Frequencies
    "ЕНИЯ": 0.16, "ЕННО": 0.12, "ГОДА": 0.10, "ЕНИЕ": 0.16,         # i18n
    "ЕТСЯ": 0.11, "ВАНИ": 0.10, "НОГО": 0.14, "ИТЕЛ": 0.11,         # i18n
    "КОГО": 0.10, "ЛЬНО": 0.13, "ОВАН": 0.11, "СТВО": 0.09,         # i18n
    "ИЧЕС": 0.13, "ОТОР": 0.11, "СКОЙ": 0.09, "НОСТ": 0.13,         # i18n
    "ОСТА": 0.11, "ПРЕД": 0.09, "ЧЕСК": 0.13, "КОТО": 0.11,         # i18n
    "ЛЬНЫ": 0.09, "ТЕЛЬ": 0.13, "СТАВ": 0.10, "СТВЕ": 0.09,         # i18n
    "АЛЬН": 0.13, "ЕЛЬН": 0.10, "ОСТИ": 0.09, "ЛЕНИ": 0.12,         # i18n
    "ЕСТВ": 0.10, "ПЕРЕ": 0.08,                                     # i18n
    # Trigram Frequencies
    "ЕНИ": 0.46, "ЛЬН": 0.27, "СТО": 0.22, "ОСТ": 0.42, "ОВА": 0.26,    # i18n
    "ПОЛ": 0.21, "ОГО": 0.36, "НИЯ": 0.25, "НОВ": 0.21, "СТВ": 0.32,    # i18n
    "НИЕ": 0.25, "ЛЕН": 0.21, "СКО": 0.31, "ПРИ": 0.24, "СТИ": 0.21,    # i18n
    "СТА": 0.30, "ЕНН": 0.24, "ПЕР": 0.21, "АНИ": 0.29, "ГОД": 0.23,    # i18n
    "ЕГО": 0.20, "ПРО": 0.29, "ОРО": 0.22, "ТСЯ": 0.20, "ЕСТ": 0.28,    # i18n
    "ТЕЛ": 0.22, "АСТ": 0.20, "ТОР": 0.27, "СКИ": 0.22, "РОВ": 0.20,    # i18n
    # Bigram Frequencies
    "СТ": 1.62, "АН": 1.03, "ВО": 0.78, "ЕН": 1.28, "ОС": 1.00,     # i18n
    "ЕС": 0.76, "ОВ": 1.23, "ПО": 0.96, "АЛ": 0.75, "НО": 1.23,     # i18n
    "ГО": 0.92, "ЛИ": 0.74, "НИ": 1.22, "ЕР": 0.92, "ОЛ": 0.73,     # i18n
    "НА": 1.21, "ОД": 0.88, "ОМ": 0.71, "РА": 1.15, "РЕ": 0.87,     # i18n
    "ЛЕ": 0.70, "КО": 1.12, "ОР": 0.85, "СК": 0.70, "ТО": 1.04,     # i18n
    "ПР": 0.80, "ВА": 0.70, "РО": 1.04, "ТА": 0.79, "ЕТ": 0.69,     # i18n
}


# =============================================================================
class KeySwitcher(QObject):

    RUSSIAN = "йцукенгшщзхъфывапролджэячсмитьбюё"                    # i18n
    ENGLISH = "abcdefghijklmnopqrstuvwxyz"
    ENGLISH_TABLE = ("qwertyuiop[]asdfghjkl;'zxcvbnm,.`/"
                     'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~@#$^&|')
    RUSSIAN_TABLE = ('йцукенгшщзхъфывапролджэячсмитьбюё.'            # i18n
                     'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё"№;:?/')     # i18n
    EN_RU = str.maketrans(ENGLISH_TABLE, RUSSIAN_TABLE)
    RU_EN = str.maketrans(RUSSIAN_TABLE, ENGLISH_TABLE)

    # -------------------------------------------------------------------------
    def __init__(self, textedit, spell):
        QObject.__init__(self)
        self._current_word = ""
        self._textedit = textedit
        self._spell = spell
        self._enabled = self._spell.enabled()
        self._current_lang = "ENG"

    # -------------------------------------------------------------------------
    def key_press(self, event: QKeyEvent):

        if event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
            if not self._spell.enabled():
                return []
            f_param = KeySwitcherParams(self._textedit,
                                        self._current_lang, self._enabled)
            if f_param.exec_():
                self._enabled = f_param.params["enabled"]
                self._current_lang = "ENG" if f_param.params["eng"] else "RUS"
            return []

        if event.key() == Qt.Key_F12:
            self._replace_selection()
            return []

        if not self._enabled:
            return [event]

        if event.key() == Qt.Key_Backspace:
            if self._current_word.strip():
                self._current_word = self._current_word.strip()[:-1]
            return [event]

        char = event.text().strip()

        if not char:
            shift = event.modifiers() & Qt.ShiftModifier
            ctrl = event.modifiers() & Qt.ControlModifier
            if not (shift or ctrl):
                self._current_word = ""
            return [event]

        # ---------------------------------------------------------------------
        # check the current word, if there was any movement, e.g. mouse
        old_cur = self._textedit.textCursor()
        cursor = self._textedit.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        word = cursor.selectedText()
        self._textedit.setTextCursor(old_cur)
        if self._current_word.strip() != word.strip():
            self._current_word = ""
            return [event]
        # ---------------------------------------------------------------------

        # detect char language
        char_lang = "UNKNOWN"
        if char.lower() in KeySwitcher.RUSSIAN:
            char_lang = "RUS"
        if char.lower() in KeySwitcher.ENGLISH:
            char_lang = "ENG"

        # add char to current word
        if self._current_lang != char_lang:  # and char_lang != "UNKNOWN":
            char = KeySwitcher.switch_charset(char, self._current_lang)
            event = QKeyEvent(
                QEvent.KeyPress, event.key(), event.modifiers(), char)
        self._current_word += char

        # early to check language
        if len(self._current_word) < 2:
            return [event]

        # detect language
        rus_chars = 0
        eng_chars = 0
        for char in set(self._current_word.lower()):
            if char in KeySwitcher.RUSSIAN:
                rus_chars += 1
            if char in KeySwitcher.ENGLISH:
                eng_chars += 1
        if rus_chars and eng_chars:
            return [event]

        if not self._ok_locale(
                self._current_word,
                KeySwitcher.switch_charset(
                    self._current_word, "ENG" if rus_chars else "RUS")):
            return [event] + self._replace_current_word()

        return [event]

    # -------------------------------------------------------------------------
    @staticmethod
    def switch_charset(string, new_lang="RUS"):
        trans = KeySwitcher.EN_RU if new_lang == "RUS" else KeySwitcher.RU_EN
        return string.translate(trans)

    # -------------------------------------------------------------------------
    def _replace_current_word(self):
        self._current_lang = "ENG" if self._current_lang == "RUS" else "RUS"
        self._current_word = self.switch_charset(self._current_word,
                                                 self._current_lang)

        backspace = QKeyEvent(QEvent.KeyPress, Qt.Key_Backspace, Qt.NoModifier)
        events = [backspace for _ in range(len(self._current_word))]

        for c in self._current_word:
            key_event = QKeyEvent(QEvent.KeyPress, 0, Qt.NoModifier, c)
            events.append(key_event)

        return events

    # -------------------------------------------------------------------------
    def _replace_selection(self):
        text = self._textedit.textCursor().selection().toPlainText()
        if not text.strip():
            return
        eng = sum(1 for c in text if c in KeySwitcher.ENGLISH_TABLE)
        rus = sum(1 for c in text if c in KeySwitcher.RUSSIAN_TABLE)
        lang = "RUS" if eng > rus else "ENG"
        text = KeySwitcher.switch_charset(text, lang)

        self._textedit.textCursor().insertText(text)

    # -------------------------------------------------------------------------
    def current_lang(self):
        return self._current_lang

    # -------------------------------------------------------------------------
    def set_current_lang(self, lang="ENG"):
        self._current_lang = lang

    # -------------------------------------------------------------------------
    def enabled(self):
        return self._enabled

    # -------------------------------------------------------------------------
    def set_enabled(self, enabled=True):
        self._enabled = enabled

    # -------------------------------------------------------------------------
    def _ok_locale(self, word_orig, word_change):
        if self._spell.check_word_without_verification(word_orig):
            return True
        if self._spell.check_word_without_verification(word_change):
            return False

        ngrams_o, ngrams_c = set(), set()
        for i in range(len(word_orig) - 1):
            for l in range(3):
                ngrams_o.add(word_orig[i: i + 2 + l].upper())
                ngrams_c.add(word_change[i: i + 2 + l].upper())

        freq_o = 0
        for ngram in ngrams_o:
            if ngram in FREQ:
                freq_o += FREQ[ngram] * (100 ** (len(ngram) - 2))

        freq_c = 0
        for ngram in ngrams_c:
            if ngram in FREQ:
                freq_c += FREQ[ngram] * (100 ** (len(ngram) - 2))

        return bool(freq_o >= freq_c)


# =============================================================================
class KeySwitcherParams(TestableDialog):

    # -------------------------------------------------------------------------
    def __init__(self, parent=None, lang="ENG", enabled=True):
        super(KeySwitcherParams, self).__init__(parent)

        self.parent = parent
        self.params = {}
        self.controls = []
        self.init_ui()

        self.controls[0].setChecked(lang == "ENG")
        self.controls[1].setChecked(lang != "ENG")
        self.controls[2].setChecked(enabled)

    # -------------------------------------------------------------------------
    def init_ui(self):

        layout = QGridLayout()
        self.controls.append(QRadioButton(self.tr("english")))
        # noinspection PyArgumentList
        layout.addWidget(self.controls[-1], 0, 0)
        self.controls.append(QRadioButton(self.tr("russian")))
        # noinspection PyArgumentList
        layout.addWidget(self.controls[-1], 1, 0)
        self.controls.append(QCheckBox(self.tr("auto switch language")))
        # noinspection PyArgumentList
        layout.addWidget(self.controls[-1], 2, 0)
        self.controls.append(QPushButton(self.tr("Apply")))
        # noinspection PyArgumentList
        layout.addWidget(self.controls[-1], 4, 0)

        self.controls[-1].clicked.connect(self.apply)

        self.setWindowTitle(self.tr("Auto switch params"))
        # self.setGeometry(300, 300, 200, 100)
        self.setLayout(layout)

    # -------------------------------------------------------------------------
    def apply(self):

        self.params = {
            "eng": self.controls[0].isChecked(),
            "rus": self.controls[1].isChecked(),
            "enabled": self.controls[2].isChecked(),
        }

        super(KeySwitcherParams, self).accept()
