from Framework.Utilities import All_Device_Info


def test_missing_adb_returns_no_devices_without_invoking_a_shell(monkeypatch):
    monkeypatch.setattr(All_Device_Info, "_get_adb_executable", lambda: None)
    monkeypatch.setattr(
        All_Device_Info.subprocess,
        "check_output",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("adb must not be invoked when it is unavailable")
        ),
    )

    assert All_Device_Info.get_all_connected_android_info() == {}


def test_adb_helper_uses_an_argument_list_without_shell(monkeypatch):
    calls = []

    def check_output(command, **kwargs):
        calls.append((command, kwargs))
        return "List of devices attached\n"

    monkeypatch.setattr(All_Device_Info.subprocess, "check_output", check_output)

    All_Device_Info._adb_output("/android/platform-tools/adb", "devices")

    assert calls[0][0] == ["/android/platform-tools/adb", "devices"]
    assert "shell" not in calls[0][1]
