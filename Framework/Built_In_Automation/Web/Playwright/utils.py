# -*- coding: utf-8 -*-
"""
Playwright Utility Functions for Zeuz Node

This module provides utility functions for Playwright automation,
including browser download and setup functionality.

Author: Zeuz/AutomationSolutionz
"""

import subprocess
import os
import sys
from pathlib import Path
from Framework.Utilities import CommonUtil
from settings import ZEUZ_NODE_DOWNLOADS_DIR

PW_BROWSERS_DIR = ZEUZ_NODE_DOWNLOADS_DIR / "pw-browsers"

def check_playwright_browser_exists():
    if not PW_BROWSERS_DIR.exists():
        return False

    # Check if a folder name exists that starts with "chromium-"
    for folder in PW_BROWSERS_DIR.iterdir():
        if folder.name.startswith("chromium-"):
            # Check if a file named "INSTALLATION_COMPLETE" exist
            if (folder / "INSTALLATION_COMPLETE").exists():
                return True
    return False


def download_playwright_browser(brand="chromium", download_path=PW_BROWSERS_DIR):
    """
    Download Playwright browser for the specified brand.
    
    Args:
        brand (str): Browser brand to download (default: "chromium")
        download_path (Path): Path to download the browser to (default: PW_BROWSERS_DIR)
    """
    
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(download_path)

    CommonUtil.ExecLog("", f"Downloading Playwright browser: {brand} to {os.environ['PLAYWRIGHT_BROWSERS_PATH']}", 2)
    # Execute the command with the current Python instance (venv)
    python_path = sys.executable
    install = subprocess.run([python_path, "-m", "playwright", "install", "--no-shell", brand])

    if install.returncode == 0:
        CommonUtil.ExecLog("", f"Playwright browser downloaded successfully: {brand}", 2)
        return True
    else:
        CommonUtil.ExecLog("", f"Failed to download Playwright browser: {brand}", 2)
        return False
