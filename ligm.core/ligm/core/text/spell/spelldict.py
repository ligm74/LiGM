#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)
""" SpellDict class (dictionary for SpellChecker)."""

import os
import re


# =============================================================================
class SpellDict:
    """
    Dictionary class for SpellChecker
    !!!! Checked only SFX and PFX affixes
    """
    # -------------------------------------------------------------------------
    def __init__(self, path: str, enable_add: bool = False) -> None:
        """
        Loading dictionary
          path: path to dictionary files (*.aff, *.dic) without extensions
          enable_add: sign to enabled adding word
        """
        self._enable_add = enable_add
        self._filepath = path
        self._encoding = self._encoding()
        self._dic = {}  # words in keys and classes of word in values

        # values of next dict's is a list of [chars_to_del, class, condition]
        self._sfx = {}  # keys - suffix
        self._pfx = {}  # keys - prefix

        self._load_dic()
        self._load_aff()

    # -------------------------------------------------------------------------
    def enabled(self) -> bool:
        return bool(self._dic)

    # -------------------------------------------------------------------------
    def _encoding(self) -> str:
        """Detect encoding of dictionary"""
        encoding = "UTF-8"
        if not os.path.exists(self._filepath + ".aff"):
            return encoding

        with open(self._filepath + ".aff", "rb") as f:
            data = f.read()
            if b"SET" in data:
                idx_beg = data.index(b"SET")
                idx_end = data.index(b"\n", idx_beg + 1)
                encoding = data[idx_beg + 4:idx_end].decode()

        return encoding

    # -------------------------------------------------------------------------
    def _load_dic(self) -> None:
        """Load dictionary (list of words in *.dic file)"""
        if not os.path.exists(self._filepath + ".dic"):
            return

        with open(self._filepath + ".dic", encoding=self._encoding) as f:
            for line in f.read().split("\n")[1:]:
                word, affix = line.split("/") if "/" in line else (line, "")
                word = word.strip().lower()
                if not word:
                    continue
                if word in self._dic:
                    if affix in self._dic[word]:
                        continue
                    affix = self._dic[word] + affix.strip()
                self._dic[word] = affix.strip()

    # -------------------------------------------------------------------------
    def _load_aff(self) -> None:
        """Load file of affixes (in *.aff file)"""
        if not os.path.exists(self._filepath + ".aff"):
            return

        with open(self._filepath + ".aff", encoding=self._encoding) as f:
            data = f.read().split("\n")
            for line in data:
                afx = line.split()
                if len(afx) != 5:
                    continue
                if afx[0] not in ["SFX", "PFX"]:
                    continue
                to_del = afx[2] if afx[2] != "0" else ""
                affix = afx[3] if afx[3] != "0" else ""
                regexp = r".*" + afx[4] + "$"

                afx_dict = self._sfx if afx[0] == "SFX" else self._pfx
                if affix not in afx_dict:
                    afx_dict[affix] = []
                afx_dict[affix].append((to_del, afx[1], regexp))

    # -------------------------------------------------------------------------
    def _check_suffix(self, word) -> [bool, str]:
        """Checking exists word by replace suffixes in dictionary"""
        for i in range(len(word), 0, -1):

            if word[i:] not in self._sfx:
                continue

            for (to_del, class_, regexp) in self._sfx[word[i:]]:
                wrd = word[:i] + to_del
                # check word in dictionary and classes match
                if wrd not in self._dic or class_ not in self._dic[wrd]:
                    continue
                # check condition of affix
                if re.match(regexp, wrd) is not None:
                    return True, class_

        return False, ""

    # -------------------------------------------------------------------------
    def check_word(self, word) -> bool:
        """Checking exists word in dictionary"""
        word = word.lower()
        if word in self._dic:
            return True
        else:
            found, _ = self._check_suffix(word)
            if found:
                return True

            # check word with prefixes
            for i in range(1, len(word)):
                if word[:i] not in self._pfx:
                    continue

                for (to_del, class_aff, regexp) in self._pfx[word[:i]]:
                    wrd = to_del + word[i:]
                    if wrd in self._dic:
                        class_dic = self._dic[wrd]
                    else:
                        _, class_dic = self._check_suffix(wrd)

                    # check word in dictionary and classes match
                    if not class_dic or class_aff not in class_dic:
                        continue  # pragma: no cover

                    # check condition of affix
                    if re.match(regexp, wrd) is not None:
                        return True

        return False

    # -------------------------------------------------------------------------
    def add_word(self, word: str, auto_save: bool = True) -> None:
        """Add word in dictionary if enabled"""
        if not self._enable_add:
            return

        word = word.lower().strip()
        if word not in self._dic:
            self._dic[word] = ""

        if auto_save:
            self.save()

    # -------------------------------------------------------------------------
    def save(self) -> None:
        """Save dictionary"""
        if not self._enable_add:
            return
        if not os.path.exists(os.path.dirname(self._filepath)):
            return

        with open(self._filepath + ".dic", "w", encoding=self._encoding) as f:
            f.write(f"{len(self._dic)}\n")
            for word in sorted(self._dic.keys()):
                f.write(f"{word}\n")  # pragma: no cover
