#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Abstract superclass for embeddable text editor."""

from abc import ABCMeta, abstractmethod


# =============================================================================
class IEditor(metaclass=ABCMeta):

    # -------------------------------------------------------------------------
    @abstractmethod
    def save(self):
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def load(self):
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def set_option(self, **options):
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def get_option(self, name):
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def search(self, text="", show_msg=True):
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def get_text(self):
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def is_empty(self):
        pass
