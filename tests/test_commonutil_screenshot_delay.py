import os
import sys
from unittest.mock import MagicMock

import pytest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Framework.Utilities import CommonUtil


@pytest.fixture(autouse=True)
def reset_commonutil_state(monkeypatch):
    monkeypatch.setattr(CommonUtil, "debug_status", False)
    monkeypatch.setattr(CommonUtil, "run_cancel", "")
    monkeypatch.setattr(CommonUtil, "run_cancelled", False)
    monkeypatch.setattr(CommonUtil, "performance_testing", False)
    monkeypatch.setattr(CommonUtil, "AUTO_SCREENSHOT_DEBUG_DELAY_SECONDS", 5)
    monkeypatch.setattr(CommonUtil, "AUTO_SCREENSHOT_DEBUG_DELAY_POLL_SECONDS", 0.25)
    monkeypatch.setattr(CommonUtil, "ExecLog", MagicMock())
    monkeypatch.setattr(CommonUtil.live_log_service, "binary", MagicMock())


def test_thread_screenshot_waits_in_debug_before_web_capture(monkeypatch, tmp_path):
    driver = MagicMock()
    sleep = MagicMock()
    image = MagicMock()

    monkeypatch.setattr(CommonUtil, "debug_status", True)
    monkeypatch.setattr(CommonUtil.time, "sleep", sleep)
    monkeypatch.setattr(CommonUtil.os.path, "exists", lambda _: True)
    monkeypatch.setattr(CommonUtil.Image, "open", MagicMock(return_value=image))
    monkeypatch.setattr(CommonUtil, "pil_image_to_bytearray", MagicMock(return_value=b"image-bytes"))
    monkeypatch.setattr(CommonUtil, "AUTO_SCREENSHOT_DEBUG_DELAY_POLL_SECONDS", 5)

    CommonUtil.Thread_ScreenShot("click", str(tmp_path), "web", driver, "debug_image")

    sleep.assert_called_once_with(5)
    driver.get_screenshot_as_file.assert_called_once()
    CommonUtil.live_log_service.binary.assert_called_once_with(b"image-bytes")


def test_thread_screenshot_waits_in_debug_before_desktop_capture(monkeypatch, tmp_path):
    sleep = MagicMock()
    capture_image = MagicMock()
    reduced_image = MagicMock()

    monkeypatch.setattr(CommonUtil, "debug_status", True)
    monkeypatch.setattr(CommonUtil.time, "sleep", sleep)
    monkeypatch.setattr(CommonUtil.sys, "platform", "win32")
    monkeypatch.setattr(CommonUtil, "ImageGrab_Mac_Win", MagicMock(grab=MagicMock(return_value=capture_image)), raising=False)
    monkeypatch.setattr(CommonUtil.os.path, "exists", lambda _: True)
    monkeypatch.setattr(CommonUtil.Image, "open", MagicMock(return_value=reduced_image))
    monkeypatch.setattr(CommonUtil, "pil_image_to_bytearray", MagicMock(return_value=b"desktop-bytes"))
    monkeypatch.setattr(CommonUtil, "AUTO_SCREENSHOT_DEBUG_DELAY_POLL_SECONDS", 5)

    CommonUtil.Thread_ScreenShot("click", str(tmp_path), "desktop", None, "desktop_image")

    sleep.assert_called_once_with(5)
    CommonUtil.ImageGrab_Mac_Win.grab.assert_called_once()
    CommonUtil.live_log_service.binary.assert_called_once_with(b"desktop-bytes")


def test_thread_screenshot_skips_delay_in_non_debug_run(monkeypatch, tmp_path):
    driver = MagicMock()
    sleep = MagicMock()
    image = MagicMock()

    monkeypatch.setattr(CommonUtil.time, "sleep", sleep)
    monkeypatch.setattr(CommonUtil.os.path, "exists", lambda _: True)
    monkeypatch.setattr(CommonUtil.Image, "open", MagicMock(return_value=image))

    CommonUtil.Thread_ScreenShot("click", str(tmp_path), "web", driver, "deploy_image")

    sleep.assert_not_called()
    driver.get_screenshot_as_file.assert_called_once()


def test_thread_screenshot_skips_delay_when_driver_missing(monkeypatch, tmp_path):
    sleep = MagicMock()

    monkeypatch.setattr(CommonUtil, "debug_status", True)
    monkeypatch.setattr(CommonUtil.time, "sleep", sleep)

    CommonUtil.Thread_ScreenShot("click", str(tmp_path), "web", None, "missing_driver")

    sleep.assert_not_called()
    CommonUtil.ExecLog.assert_any_call(
        "Thread_ScreenShot : CommonUtil",
        "Can't capture screen, driver not available for type: web, or invalid driver: None",
        3,
    )


def test_thread_screenshot_aborts_when_cancelled_during_delay(monkeypatch, tmp_path):
    driver = MagicMock()
    image = MagicMock()

    monkeypatch.setattr(CommonUtil, "debug_status", True)
    monkeypatch.setattr(CommonUtil.os.path, "exists", lambda _: True)
    monkeypatch.setattr(CommonUtil.Image, "open", MagicMock(return_value=image))
    monkeypatch.setattr(CommonUtil, "AUTO_SCREENSHOT_DEBUG_DELAY_SECONDS", 1)
    monkeypatch.setattr(CommonUtil, "AUTO_SCREENSHOT_DEBUG_DELAY_POLL_SECONDS", 0.5)

    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)
        CommonUtil.run_cancelled = True

    monkeypatch.setattr(CommonUtil.time, "sleep", fake_sleep)

    CommonUtil.Thread_ScreenShot("click", str(tmp_path), "web", driver, "cancelled_image")

    assert sleep_calls == [0.5]
    driver.get_screenshot_as_file.assert_not_called()
    CommonUtil.live_log_service.binary.assert_not_called()


def test_take_screenshot_skips_queue_when_capture_disabled(monkeypatch):
    submit = MagicMock()

    monkeypatch.setattr(CommonUtil, "ws_ss_log", True)
    monkeypatch.setattr(CommonUtil, "screen_capture_type", "web")
    monkeypatch.setattr(CommonUtil, "screen_capture_driver", MagicMock())
    monkeypatch.setattr(CommonUtil, "current_action_name", "Click")
    monkeypatch.setattr(CommonUtil, "current_step_no", "1")
    monkeypatch.setattr(CommonUtil, "current_action_no", "1")
    monkeypatch.setattr(CommonUtil.ConfigModule, "get_config_value", MagicMock(side_effect=["false", "/tmp"]))
    monkeypatch.setattr(CommonUtil.os.path, "exists", lambda _: True)
    monkeypatch.setattr(CommonUtil.executor, "submit", submit)

    CommonUtil.TakeScreenShot("click")

    submit.assert_not_called()
