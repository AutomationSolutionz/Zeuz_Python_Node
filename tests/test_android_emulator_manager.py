from types import SimpleNamespace

import pytest

from Framework.deploy_handler.adapter import normalize_mobile_execution
from Framework.install_handler.android import emulator_manager


def test_parse_adb_devices_returns_only_online_devices():
    output = """List of devices attached
emulator-5554\tdevice product:sdk_gphone model:sdk_gphone
R58M123\toffline
R58M456\tunauthorized

"""

    assert emulator_manager._parse_adb_devices(output) == ["emulator-5554"]


def test_headless_command_preserves_data_and_can_skip_snapshot_load(monkeypatch):
    monkeypatch.setattr(
        emulator_manager,
        "get_emulator_path",
        lambda: emulator_manager.Path("/android/emulator"),
    )

    command = emulator_manager._build_emulator_command(
        "Pixel_7",
        headless=True,
        cold_boot=True,
    )

    assert command == [
        "/android/emulator",
        "-avd",
        "Pixel_7",
        "-no-audio",
        "-no-boot-anim",
        "-no-window",
        "-no-snapshot-load",
    ]
    assert "-wipe-data" not in command


def test_resolve_avd_uses_first_installed_avd_when_multiple_exist(monkeypatch):
    monkeypatch.delenv("ZEUZ_ANDROID_DEFAULT_AVD", raising=False)
    monkeypatch.setattr(
        emulator_manager,
        "list_avd_names",
        lambda: ["Pixel_7", "Tablet_API_36"],
    )

    assert emulator_manager.resolve_avd_name("auto") == "Pixel_7"


def test_resolve_avd_uses_configured_default(monkeypatch):
    monkeypatch.setenv("ZEUZ_ANDROID_DEFAULT_AVD", "Pixel_7")
    monkeypatch.setattr(
        emulator_manager,
        "list_avd_names",
        lambda: ["Pixel_7", "Tablet_API_36"],
    )

    assert emulator_manager.resolve_avd_name("auto") == "Pixel_7"


def test_system_ui_anr_dismissal_clicks_only_wait(monkeypatch):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<hierarchy>
  <node text="System UI isn't responding" resource-id="android:id/alertTitle" bounds="[0,0][100,100]" />
  <node text="Close app" resource-id="android:id/aerr_close" bounds="[0,100][100,200]" />
  <node text="Wait" resource-id="android:id/aerr_wait" bounds="[100,100][300,200]" />
</hierarchy>
"""
    commands = []
    monkeypatch.setattr(emulator_manager, "_dump_ui", lambda serial: xml)
    monkeypatch.setattr(emulator_manager.time, "sleep", lambda seconds: None)

    def fake_run(command, **kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(emulator_manager, "_run", fake_run)

    assert emulator_manager._dismiss_system_ui_anr("emulator-5554") is True
    assert commands
    assert commands[0][-5:] == ["input", "touchscreen", "tap", "200", "150"]


def test_stability_wait_captures_anr_and_uses_supplied_wait_action(monkeypatch):
    clock = [0.0]
    focus_values = iter(
        [
            "mCurrentFocus=Window{ Application Error: com.android.systemui }",
            "mCurrentFocus=Window{ com.example/.MainActivity }",
            "mCurrentFocus=Window{ com.example/.MainActivity }",
        ]
    )
    screenshots = []
    wait_actions = []

    monkeypatch.setattr(
        emulator_manager,
        "_run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout="1234",
            stderr="",
        ),
    )
    monkeypatch.setattr(
        emulator_manager,
        "_focused_window",
        lambda serial: next(focus_values),
    )
    monkeypatch.setattr(
        emulator_manager,
        "_capture_failure_screenshot",
        lambda serial, name: screenshots.append((serial, name)),
    )
    monkeypatch.setattr(emulator_manager.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        emulator_manager.time,
        "sleep",
        lambda seconds: clock.__setitem__(0, clock[0] + seconds),
    )

    emulator_manager._wait_for_stable_system_ui(
        "emulator-5554",
        deadline=20,
        stability_seconds=2,
        anr_wait_action=lambda: wait_actions.append("wait") or True,
    )

    assert wait_actions == ["wait"]
    assert screenshots == [
        ("emulator-5554", "system-ui-anr-emulator-5554"),
    ]


def test_unhealthy_quick_boot_retries_with_snapshot_loading_disabled(monkeypatch):
    spawned_modes = []
    stopped = []
    stability_attempts = 0
    process = SimpleNamespace(poll=lambda: None, pid=1234)

    monkeypatch.setattr(emulator_manager, "list_running_emulators", lambda: [])
    monkeypatch.setattr(
        emulator_manager, "resolve_avd_name", lambda requested: "Pixel_7"
    )
    monkeypatch.setattr(emulator_manager, "list_online_android_serials", lambda: [])
    monkeypatch.setattr(
        emulator_manager,
        "_spawn_emulator",
        lambda avd_name, headless, cold_boot: (
            spawned_modes.append((headless, cold_boot)) or process
        ),
    )
    monkeypatch.setattr(
        emulator_manager,
        "_wait_for_serial",
        lambda avd_name, process, baseline_serials, deadline: "emulator-5554",
    )
    monkeypatch.setattr(emulator_manager, "_wait_for_android_boot", lambda *args: None)

    def wait_for_stability(*args, **kwargs):
        nonlocal stability_attempts
        stability_attempts += 1
        if stability_attempts == 1:
            raise emulator_manager.SystemUiAnrError("System UI is not responding")

    monkeypatch.setattr(
        emulator_manager,
        "_wait_for_stable_system_ui",
        wait_for_stability,
    )
    monkeypatch.setattr(
        emulator_manager, "_capture_failure_screenshot", lambda *args: None
    )
    monkeypatch.setattr(
        emulator_manager,
        "_stop_owned_emulator",
        lambda avd_name, serial="": stopped.append((avd_name, serial)),
    )
    monkeypatch.setattr(emulator_manager.time, "sleep", lambda seconds: None)

    target = emulator_manager.ensure_android_emulator(
        requested_avd="auto",
        headless=True,
    )

    assert target.serial == "emulator-5554"
    assert spawned_modes == [(True, False), (True, True)]
    assert stopped == [("Pixel_7", "emulator-5554")]


def test_requested_serial_selects_one_running_emulator(monkeypatch):
    running = [
        emulator_manager.RunningEmulator("emulator-5554", "Pixel_7"),
        emulator_manager.RunningEmulator("emulator-5556", "Tablet_API_36"),
    ]
    prepared = []
    monkeypatch.setattr(emulator_manager, "list_running_emulators", lambda: running)

    def prepare(target, **kwargs):
        prepared.append(target.serial)
        return emulator_manager.EmulatorTarget(
            serial=target.serial,
            avd_name=target.avd_name,
            launched_by_zeuz=False,
            headless=kwargs["headless"],
        )

    monkeypatch.setattr(emulator_manager, "_prepare_running_target", prepare)

    target = emulator_manager.ensure_android_emulator(
        requested_serial="emulator-5556",
        headless=True,
    )

    assert target.serial == "emulator-5556"
    assert prepared == ["emulator-5556"]


@pytest.mark.parametrize(
    ("selection", "platform", "target", "headless"),
    [
        ("Android", "Android", "auto", False),
        ("Android Headless", "Android", "emulator", True),
        ("Android-Headless", "Android", "emulator", True),
        ("iOS Simulator", "iOS", "simulator", False),
    ],
)
def test_mobile_selection_is_normalized_for_action_filtering(
    selection,
    platform,
    target,
    headless,
):
    normalized_platform, execution = normalize_mobile_execution(selection)

    assert normalized_platform == platform
    assert execution["target"] == target
    assert execution["headless"] is headless
