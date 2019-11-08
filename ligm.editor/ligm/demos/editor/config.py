#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Configuration class for demos."""

import json
import os
import socket


# =============================================================================
class Config:

    # -------------------------------------------------------------------------
    def __init__(self):
        self._settings = {}
        self._filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "config.json")
        self.load()

    # -------------------------------------------------------------------------
    def load(self):
        if os.path.exists(self._filename):
            with open(self._filename, "r", encoding="utf-8") as f:
                self._settings = json.load(f)

    # -------------------------------------------------------------------------
    def save(self):
        with open(self._filename, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, indent=4, sort_keys=True)

    # -------------------------------------------------------------------------
    def get(self, name, default, system=False):
        if name == "Config/FilePath":
            return self._filename

        path_with_system = f"{socket.gethostname()}/{name}"

        if system and path_with_system in self._settings:
            result = self._settings[path_with_system]

        elif name in self._settings:
            result = self._settings[name]

        else:
            result = default

        self._settings[path_with_system if system else name] = result
        return result

    # -------------------------------------------------------------------------
    def __setitem__(self, key, value):
        name = key
        if type(key) == tuple:
            name = key[1]
            if key[0].upper() == "SYSTEM":
                name = f"{socket.gethostname()}/{key[1]}"

        self._settings[name] = value
        self.save()

    # -------------------------------------------------------------------------
    def __getitem__(self, key):
        name, system = key, False
        if type(key) == tuple:
            name, system = key[1], key[0] == "SYSTEM"

        return self.get(name, None, system=system)
