"""The common "sleep" action declares screenshot "auto", so the capture type is
chosen from whichever driver the test currently has open."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Framework.Built_In_Automation.Sequential_Actions.action_declarations import common
from Framework.Utilities import CommonUtil


def _reset(monkeypatch):
    monkeypatch.setattr(CommonUtil, "screen_capture_type", "none")
    monkeypatch.setattr(CommonUtil, "screen_capture_driver", None)


def test_sleep_action_is_declared_auto():
    sleep_action = next(d for d in common.declarations if d["name"] == "sleep")
    assert sleep_action["screenshot"] == "auto"


def test_auto_resolves_to_web_for_selenium(monkeypatch):
    _reset(monkeypatch)
    driver = object()

    CommonUtil.set_screenshot_vars({"screen_capture": "auto", "selenium_driver": driver})

    assert CommonUtil.screen_capture_type == "web"
    assert CommonUtil.screen_capture_driver is driver


def test_auto_resolves_to_web_for_playwright(monkeypatch):
    _reset(monkeypatch)
    page = object()

    CommonUtil.set_screenshot_vars({
        "screen_capture": "auto",
        "active_web_driver_type": "playwright",
        "playwright_page": page,
    })

    assert CommonUtil.screen_capture_type == "web"
    assert CommonUtil.screen_capture_driver is page


def test_auto_resolves_to_none_without_a_web_driver(monkeypatch):
    _reset(monkeypatch)

    CommonUtil.set_screenshot_vars({"screen_capture": "auto"})

    assert CommonUtil.screen_capture_type == "none"


def test_auto_resolves_to_none_when_browser_was_torn_down(monkeypatch):
    """A stale key left behind as None must not be mistaken for a live driver."""
    _reset(monkeypatch)

    CommonUtil.set_screenshot_vars({
        "screen_capture": "auto",
        "selenium_driver": None,
        "playwright_page": None,
    })

    assert CommonUtil.screen_capture_type == "none"


def test_explicit_types_are_untouched(monkeypatch):
    for declared in ("none", "web", "mobile", "desktop"):
        _reset(monkeypatch)
        CommonUtil.set_screenshot_vars({"screen_capture": declared})
        assert CommonUtil.screen_capture_type == declared
