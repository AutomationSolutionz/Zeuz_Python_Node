"""Screen captures must be bounded.

Selenium/Appium screenshots are synchronous HTTP calls with no read timeout, and
TakeScreenShot runs outside _run_action_with_timeout, so a wedged browser used to
park the whole run on the "Capturing Screenshot" line indefinitely.
"""

import asyncio
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

    async def scenario():
        start = time.perf_counter()
        ok = await CommonUtil._capture_with_timeout(
            wedged_browser, "mod", "Sleep", "web"
        )
        return ok, time.perf_counter() - start

    try:
        ok, elapsed = asyncio.run(scenario())
    finally:
        release.set()

    assert ok is False
    assert elapsed < 10, "capture was not bounded by the timeout"
    assert any(lvl == 2 and "did not finish" in msg for lvl, msg in logs)
    assert not any(lvl == 3 for lvl, _ in logs)


def test_event_loop_stays_responsive_while_a_capture_is_stuck(short_timeout, logs):
    """The capture must not run on the event loop -- other tasks keep working."""
    release = threading.Event()
    ticks = []

    async def scenario():
        async def heartbeat():
            while True:
                await asyncio.sleep(0.05)
                ticks.append(1)

        hb = asyncio.create_task(heartbeat())
        await CommonUtil._capture_with_timeout(release.wait, "mod", "Sleep", "web")
        hb.cancel()

    try:
        asyncio.run(scenario())
    finally:
        release.set()

    assert ticks, "event loop was blocked by the capture"


def test_successful_capture_returns_true(short_timeout, logs):
    calls = []

    async def scenario():
        return await CommonUtil._capture_with_timeout(
            lambda: calls.append("captured"), "mod", "Go_To_Link", "web"
        )

    assert asyncio.run(scenario()) is True
    assert calls == ["captured"]
    assert not any("did not finish" in msg for _, msg in logs)


def test_capture_errors_still_propagate(short_timeout, logs):
    """Thread_ScreenShot's WebDriverException/Exception handlers must still fire."""

    def broken_driver():
        raise RuntimeError("browser went away")

    async def scenario():
        return await CommonUtil._capture_with_timeout(
            broken_driver, "mod", "Sleep", "web"
        )

    with pytest.raises(RuntimeError, match="browser went away"):
        asyncio.run(scenario())


def test_awaitable_capture_is_bounded_too(short_timeout, logs):
    """Playwright captures are coroutines, not callables."""

    async def slow_playwright_screenshot():
        await asyncio.sleep(30)

    async def scenario():
        start = time.perf_counter()
        ok = await CommonUtil._capture_with_timeout(
            slow_playwright_screenshot(), "mod", "Sleep", "web"
        )
        return ok, time.perf_counter() - start

    ok, elapsed = asyncio.run(scenario())

    assert ok is False
    assert elapsed < 10
    assert any(lvl == 2 and "did not finish" in msg for lvl, msg in logs)
