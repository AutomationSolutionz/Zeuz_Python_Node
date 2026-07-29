# -*- coding: utf-8 -*-
"""Playwright-managed browser installation helpers."""

import os
import subprocess
import sys
from pathlib import Path

from filelock import FileLock

from Framework.Utilities import CommonUtil
from settings import ZEUZ_NODE_DOWNLOADS_DIR


PLAYWRIGHT_BROWSERS_DIR = ZEUZ_NODE_DOWNLOADS_DIR / "playwright_browsers"
PLAYWRIGHT_INSTALLABLE_BROWSERS = {
    "firefox": "firefox",
    "webkit": "webkit",
    "safari": "webkit",
}
PLAYWRIGHT_SYSTEM_CHANNEL_BROWSERS = {
    "edge",
    "msedge",
    "microsoft edge",
}


def _set_playwright_browsers_path():
    PLAYWRIGHT_BROWSERS_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(PLAYWRIGHT_BROWSERS_DIR)
    return PLAYWRIGHT_BROWSERS_DIR


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
    output = result.stdout.strip()
    return Path(output.splitlines()[-1]) if output else None


def _is_playwright_browser_installed(browser_name):
    executable_path = _get_playwright_executable_path(browser_name)
    return bool(executable_path and executable_path.exists())


def ensure_playwright_browser_installed(sModuleInfo, browser_name):
    """Install Firefox/WebKit in Zeuz's persistent Playwright cache when needed."""
    try:
        browsers_dir = _set_playwright_browsers_path()
        requested_browser = (browser_name or "").strip().lower()
        install_browser = PLAYWRIGHT_INSTALLABLE_BROWSERS.get(requested_browser)

        if requested_browser in PLAYWRIGHT_SYSTEM_CHANNEL_BROWSERS:
            return True
        if not install_browser:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Playwright browser '{browser_name}' is not installable",
                3,
            )
            return False
        if _is_playwright_browser_installed(install_browser):
            return True

        with FileLock(str(browsers_dir / f"{install_browser}.install.lock")):
            if _is_playwright_browser_installed(install_browser):
                return True
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "playwright",
                    "install",
                    "--with-deps",
                    install_browser,
                ],
                env=os.environ.copy(),
            )

        if result.returncode == 0:
            return True
        CommonUtil.ExecLog(
            sModuleInfo,
            f"Failed to install Playwright {install_browser}. See terminal output for details.",
            3,
        )
        return False
    except Exception as exc:
        CommonUtil.ExecLog(
            sModuleInfo,
            f"Error setting up Playwright browser: {exc}",
            3,
        )
        return False
