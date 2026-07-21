import asyncio

from Framework.Utilities import CommonUtil


def test_post_action_screenshot_is_skipped_when_mobile_driver_was_not_created(
    monkeypatch,
    tmp_path,
):
    logs = []
    thread_calls = []
    monkeypatch.setattr(CommonUtil, "ws_ss_log", True)
    monkeypatch.setattr(CommonUtil, "performance_testing", False)
    monkeypatch.setattr(CommonUtil, "upload_on_fail", False)
    monkeypatch.setattr(CommonUtil, "screen_capture_type", "mobile")
    monkeypatch.setattr(CommonUtil, "screen_capture_driver", None)
    monkeypatch.setattr(
        CommonUtil.ConfigModule,
        "get_config_value",
        lambda section, key, *args: (
            "true" if key == "take_screenshot" else str(tmp_path)
        ),
    )
    monkeypatch.setattr(
        CommonUtil,
        "ExecLog",
        lambda module, message, level, *args, **kwargs: logs.append((message, level)),
    )

    async def thread_screenshot(*args, **kwargs):
        thread_calls.append((args, kwargs))

    monkeypatch.setattr(CommonUtil, "Thread_ScreenShot", thread_screenshot)

    asyncio.run(CommonUtil.TakeScreenShot("launch_application"))

    assert thread_calls == []
    assert any("driver is not available" in message for message, _ in logs)
    assert not any(level == 3 for _, level in logs)
