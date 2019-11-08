#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Classes for working with settings."""

from functools import lru_cache


# =============================================================================
class ConfigHelper:
    # Helper class for passing parameter to methods and functions

    # -------------------------------------------------------------------------
    def __init__(self, cfg, **params):
        self._cfg = cfg
        self._params = params
        self.get.cache_clear()

    # -------------------------------------------------------------------------
    @lru_cache(maxsize=None)
    def get(self, name, default, system=False):
        if name in self._params:
            return self._params[name]
        return self._cfg.get(name, default, system)

    # -------------------------------------------------------------------------
    def __setitem__(self, key, value):
        name, system = key, False
        if type(key) == tuple:
            name, system = key[1], key[0].upper() == "SYSTEM"

        self.get.cache_clear()
        if name in self._params:
            self._params[name] = value
        elif system:
            self._cfg["SYSTEM", name] = value
        else:
            self._cfg[name] = value


# =============================================================================
class SimpleConfig:

    def __init__(self):
        self.values = {}
        self.values_sys = {}

    # -------------------------------------------------------------------------
    def get(self, name, default, system=False):
        if system:
            return self.values_sys.get(name, default)
        return self.values.get(name, default)

    # -------------------------------------------------------------------------
    def __setitem__(self, key, value):
        name, system = key, False
        if type(key) == tuple:
            name, system = key[1], key[0].upper() == "SYSTEM"

        if system:
            self.values_sys[name] = value
        else:
            self.values[name] = value

    # -------------------------------------------------------------------------
    def __getitem__(self, key):
        name, system = key, False
        if type(key) == tuple:
            name, system = key[1], key[0] == "SYSTEM"

        return self.get(name, None, system=system)
