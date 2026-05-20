# -*- coding: utf-8 -*-
"""
Playwright Utility Functions for Zeuz Node

This module provides utility functions for Playwright automation,
including browser download and setup functionality.

Author: Zeuz/AutomationSolutionz
"""

import os
import subprocess
import sys
from pathlib import Path

from filelock import FileLock

from Framework.Utilities import CommonUtil
from settings import ZEUZ_NODE_DOWNLOADS_DIR

PLAYWRIGHT_BROWSERS_DIR = ZEUZ_NODE_DOWNLOADS_DIR / "playwright_browsers"
PLAYWRIGHT_INSTALLABLE_BROWSERS = {
    "chromium": "chromium",
    "chrome": "chromium",
    "firefox": "firefox",
    "webkit": "webkit",
    "safari": "webkit",
}
PLAYWRIGHT_SYSTEM_CHANNEL_BROWSERS = {
    "edge",
    "msedge",
    "microsoft edge",
    "chrome-beta",
}


def _set_playwright_browsers_path():
    """Use Zeuz's persistent downloads directory for Playwright browser binaries."""

    PLAYWRIGHT_BROWSERS_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(PLAYWRIGHT_BROWSERS_DIR)
    return PLAYWRIGHT_BROWSERS_DIR


def _get_playwright_browser_name(browser_name):
    browser_name = (browser_name or "chromium").strip().lower()
    return PLAYWRIGHT_INSTALLABLE_BROWSERS.get(browser_name)


def _get_playwright_executable_path(browser_name):
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from playwright.sync_api import sync_playwright\n"
                "with sync_playwright() as p:\n"
                f"    print(p.{browser_name}.executable_path)\n"
            ),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=os.environ.copy(),
    )

    if result.returncode != 0:
        return None

    executable_path = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    return Path(executable_path) if executable_path else None


def _is_playwright_browser_installed(browser_name):
    executable_path = _get_playwright_executable_path(browser_name)
    return bool(executable_path and executable_path.exists())


def ensure_playwright_browser_installed(sModuleInfo, browser_name="chromium"):
    """
    Ensure Playwright's managed browser is installed in Zeuz's persistent cache.
     
    Args:
        sModuleInfo: Module information for logging
        browser_name: Requested Playwright browser/channel name
         
    Returns:
        bool: True if the browser is ready or no managed download is required
    """
    try:
        browsers_dir = _set_playwright_browsers_path()
        requested_browser = (browser_name or "chromium").strip().lower()
        install_browser = _get_playwright_browser_name(requested_browser)

        if requested_browser in PLAYWRIGHT_SYSTEM_CHANNEL_BROWSERS:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Using Playwright browser cache: {browsers_dir}. Browser '{browser_name}' uses a system channel.",
                1,
            )
            return True

        if not install_browser:
            install_browser = "chromium"
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Unknown browser '{browser_name}', preparing Playwright chromium",
                2,
            )

        CommonUtil.ExecLog(
            sModuleInfo,
            f"Ensuring Playwright {install_browser} browser is installed in {browsers_dir}",
            1,
        )

        if _is_playwright_browser_installed(install_browser):
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Playwright {install_browser} browser already exists in {browsers_dir}",
                1,
            )
            return True

        lock_path = browsers_dir / f"{install_browser}.install.lock"
        with FileLock(str(lock_path)):
            if _is_playwright_browser_installed(install_browser):
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Playwright {install_browser} browser already exists in {browsers_dir}",
                    1,
                )
                return True

            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "--with-deps", install_browser],
                env=os.environ.copy(),
            )

        if result.returncode == 0:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Playwright {install_browser} browser is ready",
                1,
            )
            return True

        CommonUtil.ExecLog(
            sModuleInfo,
            f"Failed to install Playwright {install_browser} browser. See terminal output for details.",
            3,
        )
        return False

    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, f"Error setting up Playwright browser: {str(e)}", 3)
        return False
