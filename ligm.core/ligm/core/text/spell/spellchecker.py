#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)
""" SpellChecker class."""

import re
from PyQt5.Qt import pyqtSignal, QObject
from ligm.core.common import get_res_dir
from .spelldict import SpellDict


# =============================================================================
class SpellChecker(QObject):

    change_enabled = pyqtSignal()

    # -------------------------------------------------------------------------
    def __init__(self, enabled=False):

        super(SpellChecker, self).__init__()

        self._enabled_all = enabled
        self._enabled_en, self._enabled_ru = False, False

        if not enabled:
            return

        self._en = SpellDict(f"{get_res_dir()}/dict/en_US")
        self._ru = SpellDict(f"{get_res_dir()}/dict/russian-aot")
        self._man = SpellDict(f"{get_res_dir()}/dict/man", enable_add=True)

        self._enabled_en = self._en.enabled()
        self._enabled_ru = self._ru.enabled()

    # -------------------------------------------------------------------------
    def enabled(self, name_dict="all"):
        if name_dict.lower() == "eng":
            return self._enabled_en
        if name_dict.lower() == "rus":
            return self._enabled_ru
        if name_dict.lower() == "all":
            return self._enabled_all
        return False

    # -------------------------------------------------------------------------
    def set_enabled(self, name_dict="all", value=True):
        if not self._enabled_all:
            return
        if name_dict.lower() == "eng":
            self._enabled_en = value
        if name_dict.lower() == "rus":
            self._enabled_ru = value
        if name_dict.lower() == "all":
            self._enabled_en = value
            self._enabled_ru = value
        self.change_enabled.emit()

    # -------------------------------------------------------------------------
    @staticmethod
    def _is_english(word):
        return not bool(re.search(r"[^a-zA-Z0-9]", word))

    # -------------------------------------------------------------------------
    @staticmethod
    def _is_number(word):
        num = r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$"
        # + "1" for correctly parse numbers such as 12e-123
        # word "12e-123" is split to two: 12e and 123
        return bool(re.match(num, word + "1"))

    # -------------------------------------------------------------------------
    def word_needs_no_verification(self, word):
        if len(word.strip()) == 1:
            return True
        if SpellChecker._is_number(word):
            return True

        is_eng = SpellChecker._is_english(word)

        if not self._enabled_all:
            return True

        if is_eng and not self._enabled_en:
            return True

        if not is_eng and not self._enabled_ru:
            return True

        return False

    # -------------------------------------------------------------------------
    def check_word(self, word):
        if self.word_needs_no_verification(word):
            return True
        return self.check_word_without_verification(word)

    # -------------------------------------------------------------------------
    def check_word_without_verification(self, word):
        if not self._enabled_all:
            return False

        if self._man.check_word(word):
            return True  # pragma: no cover

        if self._enabled_en and self._en.check_word(word):
            return True

        if self._enabled_ru:
            if self._ru.check_word(word):
                return True
            if "ё" in word.lower():                                      # i18n
                if self._ru.check_word(word.replace("ё", "е")):          # i18n
                    return True

        return False

    # -------------------------------------------------------------------------
    def candidates(self, word):
        if not self._enabled_all:
            return []  # pragma: no cover

        result = []
        for wrd in self._edit_distance_1(word):
            if self.check_word_without_verification(wrd):
                result.append(wrd)

        return sorted(result)[:15]

    # -------------------------------------------------------------------------
    @staticmethod
    def _edit_distance_1(word):
        """ Compute all strings that are one edit away from `word` """
        word = word.lower()
        if SpellChecker._is_english(word):
            sym = [chr(ch) for ch in list(range(ord('a'), ord('z')+1))]
        else:
            sym = [chr(ch) for ch in list(range(ord('а'), ord('я')+1))]  # i18n
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in sym]
        inserts = [L + c + R for L, R in splits for c in sym]
        return set(deletes + transposes + replaces + inserts)

    # -------------------------------------------------------------------------
    def add_word(self, word, auto_save=True):
        if not self.check_word(word):
            self._man.add_word(word, auto_save)  # pragma: no cover
