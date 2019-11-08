#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (2.6.0)

"""Various functions to work with folders, files, etc."""

import os
import sys
import subprocess
from functools import lru_cache


# =============================================================================
# in WINDOWS __file__ returns the path in lower case (not always)
def _case(folder, findme):
    items = os.listdir(folder)
    output = ""
    for item in items:
        if item.lower() == findme.lower():
            output = os.path.join(folder, item)
            break
    return output


def realpath(file_path):
    # in linux file_path.split(os.sep)[0] empty, in windows c: (or other disk)
    file_path = file_path.replace("\\", "/")
    output = file_path.split("/")[0].upper() + os.sep

    for part in file_path.split("/")[1:]:
        if not part:
            continue  # skip blanks
        output = os.path.join(output, _case(output, part))

    output = output.replace("\\", "/")

    if output and output[-1] == "/":
        output = output[:-1]

    return output


# =============================================================================
@lru_cache(maxsize=None)
def get_res_dir(dir_name="resources"):
    """
    Path to the resources directory
    """
    return f"{get_app_dir(dir_name)}/{dir_name}"


# =============================================================================
@lru_cache(maxsize=None)
def get_app_dir(dir_name="resources"):
    """
    Path to the application directory
    """
    # -------------------------------------------------------------------------
    # expression "arr_path = os.path.realpath(__file__).split(os.sep)[:-1]"
    # does not work correctly in WINDOWS (returns the path in lower case)
    arr_path = realpath(__file__).split("/")[:-1]
    # -------------------------------------------------------------------------

    while arr_path:
        for root, dirs, _ in os.walk(os.sep.join(arr_path)):
            if dir_name in dirs:
                return root.replace('\\', '/')

        arr_path.pop()
        # if the root of the disk, do not search files on the entire disk
        if len(arr_path) == 2:
            break
    raise Exception("Application directory not found.")


# =============================================================================
@lru_cache(maxsize=None)
def img(img_name, app_path=None):
    """
    Path of image (or empty string).

    The image is searched in the following ways:
    1. %APP_DIR%/resources/images + "img_name"
    2. %APP_DIR%/resources/images/common + "img_name" without first dir
    3. %APP_DIR%/resources/images + only name of file in "img_name"
    """
    if not app_path:
        app_path = get_app_dir()
    img_path = app_path + "/resources/images/"

    path_arr = img_name.replace('\\', '/').split('/')
    file_name = path_arr[-1]
    dir_without_first = "/".join(path_arr[1:-1] if len(path_arr) > 2 else [])

    path1 = img_path + img_name
    path2 = img_path + 'common/' + dir_without_first + "/" + file_name
    path3 = img_path + file_name

    for path in [path1, path2, path3]:
        for ext in [".png", ".jpg", ".gif", ".jpeg", ".cur"]:
            if path.lower().endswith(ext):
                if os.path.exists(path):
                    return path
            if os.path.exists(path + ext):
                return path + ext

    return ""


# =============================================================================
def run_cmd(cmd, cmd_cur_dir=None, wait=False, test=False):
    """
    Run shell command.
    """
    cur_dir = os.getcwd()
    if cmd_cur_dir is not None:
        os.chdir(cmd_cur_dir)

    if sys.platform == "linux":  # pragma: no cover
        process = subprocess.Popen(['/bin/sh', '-c', cmd])
    else:  # pragma: no cover
        # hide console window in Windows
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        try:
            process = subprocess.Popen(
                cmd, startupinfo=startupinfo, shell=True)
        except Exception as err:
            return False, "ERROR: run_cmd: {} ({})".format(err, cmd)

    if wait or test:
        try:
            process.wait()
        except Exception as err:  # pragma: no cover
            return False, "ERROR: run_cmd: {} ({})".format(err, cmd)

    os.chdir(cur_dir)

    return True, "OK"
