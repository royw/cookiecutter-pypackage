#!/usr/bin/env python
"""Function to get the terminal size.

Used in application_settings adjust the argparse display width to fill the width of the console.

From:  https://gist.github.com/jtriley/1108174
"""

import os
import platform
import shlex
import struct
import subprocess
import sys
from typing import Tuple, Optional


# noinspection HttpUrlsUsage
def get_terminal_size() -> Tuple[int, int]:
    """Get the terminal size.  Supports multiple platforms.

    - get width and height of console
    - works on linux,os x,windows,cygwin(windows)

    originally retrieved from:

    http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    tuple_xy = None
    if sys.platform == "win32":
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if sys.platform.startswith("linux") or sys.platform == "darwin" or platform.system().startswith("CYGWIN"):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        tuple_xy = (80, 25)  # default value
    return tuple_xy


def _get_terminal_size_windows() -> Optional[Tuple[int, int]]:
    if sys.platform == "win32":
        # noinspection PyBroadException
        try:
            from ctypes import create_string_buffer, windll

            # stdin handle is -10
            # stdout handle is -11
            # stderr handle is -12
            h = windll.kernel32.GetStdHandle(-12)
            csbi = create_string_buffer(22)
            res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
            if res:
                # noinspection SpellCheckingInspection
                (
                    bufx,
                    bufy,
                    curx,
                    cury,
                    wattr,
                    left,
                    top,
                    right,
                    bottom,
                    maxx,
                    maxy,
                ) = struct.unpack("hhhhHhhhhhh", csbi.raw)
                size_x_ = right - left + 1
                size_y_ = bottom - top + 1
                return size_x_, size_y_
        except Exception:
            pass
    return None


def _get_terminal_size_tput() -> Optional[Tuple[int, int]]:
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    if sys.platform == "win32":
        # noinspection PyBroadException
        try:
            cols = int(subprocess.check_call(shlex.split("tput cols")))
            rows = int(subprocess.check_call(shlex.split("tput lines")))
            return cols, rows
        except Exception:
            pass
    return None


# noinspection PyTypeChecker
def _get_terminal_size_linux() -> Optional[Tuple[int, int]]:
    if sys.platform.startswith("linux") or sys.platform == "darwin" or platform.system().startswith("CYGWIN"):
        # noinspection PyPep8Naming,PyDocstring,PyShadowingNames
        def ioctl_GWINSZ(fd):
            # noinspection PyBroadException
            try:
                # noinspection PyCompatibility
                import fcntl

                # noinspection PyCompatibility
                import termios

                cr = struct.unpack("hh", fcntl.ioctl(fd, termios.TIOCGWINSZ, "1234"))
                return cr
            except Exception:
                pass

        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
        if not cr:
            # noinspection PyBroadException
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except Exception:
                pass
        if not cr:
            # noinspection PyBroadException
            try:
                cr = (os.environ["LINES"], os.environ["COLUMNS"])
            except Exception:
                return None
        return int(cr[1]), int(cr[0])
    return None


if __name__ == "__main__":
    size_x, size_y = get_terminal_size()
    print("width =", size_x, "height =", size_y)
