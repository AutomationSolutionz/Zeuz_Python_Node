"""Startup state for node_cli.py. Import this before any other Framework module.

Captures how the node was launched, before anything changes it, so the node
can restart itself with exactly that environment. Also makes python3-xlib
thread-safe before anything imports pyautogui (see x11_utils).
"""

import os
import sys

from Framework.Utilities.x11_utils import enable_xlib_threading

STARTUP_ENV = dict(os.environ)
STARTUP_CWD = os.getcwd()
STARTUP_SCRIPT = os.path.abspath(sys.argv[0]) if sys.argv and sys.argv[0] else ""

enable_xlib_threading()
