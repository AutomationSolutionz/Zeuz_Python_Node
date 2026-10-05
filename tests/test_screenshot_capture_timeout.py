"""Screen captures must be bounded.

Selenium/Appium screenshots are synchronous HTTP calls with no read timeout, and
TakeScreenShot runs outside _run_action_with_timeout, so a wedged browser used to
park the whole run on the "Capturing Screenshot" line indefinitely.
"""

import os
import sys
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from Framework.Utilities import CommonUtil


@pytest.fixture
def short_timeout(monkeypatch):
    monkeypatch.setattr(CommonUtil, "SCREENSHOT_CAPTURE_TIMEOUT_SECONDS", 1)


@pytest.fixture
def logs(monkeypatch):
    captured = []
    monkeypatch.setattr(
        CommonUtil,
        "ExecLog",
        lambda module, message, level=1, *a, **k: captured.append((level, str(message))),
    )
    return captured


def test_wedged_capture_times_out_instead_of_hanging(short_timeout, logs):
    release = threading.Event()

    def wedged_browser():
        release.wait()  # never released while we are timing

    start = time.perf_counter()
    try:
        ok = CommonUtil._capture_with_timeout(wedged_browser, "mod", "Sleep", "web")
        elapsed = time.perf_counter() - start
    finally:
        release.set()

    assert ok is False
    assert elapsed < 10, "capture was not bounded by the timeout"
    assert any(lvl == 2 and "did not finish" in msg for lvl, msg in logs)
    assert not any(lvl == 3 for lvl, _ in logs)


def test_abandoned_capture_cannot_hold_up_node_shutdown(short_timeout, logs):
    """The capture runs on a daemon thread, so an abandoned one never blocks exit."""
    release = threading.Event()
    try:
        assert CommonUtil._capture_with_timeout(release.wait, "mod", "Sleep", "web") is False
        stuck = [t for t in threading.enumerate() if t.name == "zeuz_screenshot_capture"]
        assert stuck and all(t.daemon for t in stuck)
    finally:
        release.set()


def test_successful_capture_returns_true(short_timeout, logs):
    calls = []

    ok = CommonUtil._capture_with_timeout(lambda: calls.append("captured"), "mod", "Go_To_Link", "web")

    assert ok is True
    assert calls == ["captured"]
    assert not any("did not finish" in msg for _, msg in logs)


def test_capture_errors_still_propagate(short_timeout, logs):
    """Thread_ScreenShot's WebDriverException/Exception handlers must still fire."""

    def broken_driver():
        raise RuntimeError("browser went away")

    with pytest.raises(RuntimeError, match="browser went away"):
        CommonUtil._capture_with_timeout(broken_driver, "mod", "Sleep", "web")


def test_thread_screenshot_does_not_hang_on_a_wedged_selenium_driver(short_timeout, logs, tmp_path):
    release = threading.Event()

    class WedgedSeleniumDriver:
        def get_screenshot_as_file(self, path):
            release.wait()

    start = time.perf_counter()
    try:
        CommonUtil.Thread_ScreenShot("Sleep", str(tmp_path), "web", WedgedSeleniumDriver(), "shot", skip_delay=True)
        elapsed = time.perf_counter() - start
    finally:
        release.set()

    assert elapsed < 10
    assert any(lvl == 2 and "did not finish" in msg for lvl, msg in logs)


def test_playwright_screenshot_uses_its_own_timeout_on_its_own_thread(short_timeout, logs, tmp_path):
    """Playwright pages must stay on their thread, so they get Playwright's timeout instead."""
    calls = []

    class FakePage:
        def screenshot(self, **kwargs):
            calls.append((threading.current_thread().name, kwargs))

    FakePage.__module__ = "playwright.sync_api._generated"

    CommonUtil.Thread_ScreenShot("Sleep", str(tmp_path), "web", FakePage(), "shot", skip_delay=True)

    assert len(calls) == 1
    thread_name, kwargs = calls[0]
    assert thread_name == threading.current_thread().name
    assert kwargs["timeout"] == 1 * 1000
    assert kwargs["path"].endswith("shot.png")
