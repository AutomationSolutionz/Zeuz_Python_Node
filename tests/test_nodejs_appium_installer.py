import asyncio
import json
import subprocess

from Framework import nodejs_appium_installer as installer
from Framework.install_handler.android import appium as appium_service


def completed(command, returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(
        command,
        returncode,
        stdout=stdout,
        stderr=stderr,
    )


def test_check_installations_verifies_managed_binaries_and_drivers(
    monkeypatch,
    tmp_path,
):
    node_path = tmp_path / "node"
    appium_path = tmp_path / "appium"
    node_path.touch()
    appium_path.touch()

    monkeypatch.setattr(installer, "get_node_path", lambda: node_path)
    monkeypatch.setattr(installer, "get_appium_path", lambda: appium_path)

    def run_local(command, **kwargs):
        if command == [str(node_path), "--version"]:
            return completed(command, stdout="v22.20.0\n")
        if command == [str(appium_path), "--version"]:
            return completed(command, stdout="3.5.2\n")
        if command == [
            str(appium_path),
            "driver",
            "list",
            "--installed",
            "--json",
        ]:
            return completed(
                command,
                stdout=json.dumps({"uiautomator2": {"installed": True}}),
            )
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(installer, "_run_local", run_local)

    assert installer.check_installations() == (True, True, [])


def test_install_drivers_skips_an_existing_driver(monkeypatch):
    checks = []
    monkeypatch.setattr(
        installer,
        "check_appium_drivers",
        lambda: checks.append(True) or ["uiautomator2"],
    )
    monkeypatch.setattr(
        installer,
        "_run_local",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("driver install must not run")
        ),
    )

    assert installer.install_drivers(["uiautomator2"]) is True
    assert len(checks) == 2


def test_install_appium_rechecks_drivers_instead_of_blindly_installing(
    monkeypatch,
    tmp_path,
):
    node_dir = tmp_path / "nodejs"
    npm_path = node_dir / "bin" / "npm"
    appium_path = node_dir / "bin" / "appium"
    npm_path.parent.mkdir(parents=True)
    npm_path.touch()
    appium_path.touch()
    commands = []

    monkeypatch.setattr(installer, "get_node_dir", lambda: node_dir)
    monkeypatch.setattr(installer, "get_npm_path", lambda: npm_path)
    monkeypatch.setattr(installer, "get_appium_path", lambda: appium_path)

    def run_local(command, **kwargs):
        commands.append(command)
        if command[:3] == [str(npm_path), "install", "-g"]:
            return completed(command, stdout="installed")
        if command == [str(appium_path), "--version"]:
            return completed(command, stdout="3.5.2\n")
        if command == [
            str(appium_path),
            "driver",
            "list",
            "--installed",
            "--json",
        ]:
            return completed(
                command,
                stdout=json.dumps({"uiautomator2": {"installed": True}}),
            )
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(installer, "_run_local", run_local)
    monkeypatch.setattr(installer, "get_required_drivers", lambda: ["uiautomator2"])

    assert installer.install_appium() is True
    assert not any(command[1:3] == ["driver", "install"] for command in commands)
    assert "--prefix" in commands[0]
    assert str(node_dir) in commands[0]


def test_install_drivers_reports_a_real_install_failure(monkeypatch):
    checks = iter([[], []])
    monkeypatch.setattr(installer, "check_appium_drivers", lambda: next(checks))
    monkeypatch.setattr(
        installer,
        "_run_local",
        lambda command, **kwargs: completed(
            command,
            returncode=1,
            stderr="network unavailable",
        ),
    )

    assert installer.install_drivers(["uiautomator2"]) is False


def test_setup_does_not_claim_success_when_a_required_driver_fails(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(installer, "check_and_remove_global_appium", lambda: None)
    monkeypatch.setattr(installer, "update_path", lambda: None)
    monkeypatch.setattr(
        installer,
        "check_installations",
        lambda: (True, True, ["uiautomator2"]),
    )
    monkeypatch.setattr(installer, "install_missing_drivers", lambda drivers: False)

    assert installer.setup_nodejs_appium() is False
    output = capsys.readouterr().out
    assert "setup was not completed" in output
    assert "setup verified successfully" not in output


def test_local_node_environment_takes_precedence(monkeypatch, tmp_path):
    node_dir = tmp_path / "nodejs"
    monkeypatch.setattr(installer, "get_node_dir", lambda: node_dir)
    monkeypatch.setenv("PATH", f"/system/bin:{node_dir / 'bin'}:/other/bin")
    monkeypatch.setattr(installer.platform, "system", lambda: "Linux")

    path_parts = installer.get_local_node_env()["PATH"].split(installer.os.pathsep)

    assert path_parts[0] == str(node_dir / "bin")
    assert path_parts.count(str(node_dir / "bin")) == 1


def test_appium_ui_status_reports_missing_driver(monkeypatch):
    responses = []
    monkeypatch.setattr(
        appium_service,
        "check_installations",
        lambda: (True, True, ["uiautomator2"]),
    )

    async def send_response(payload):
        responses.append(payload)

    monkeypatch.setattr(appium_service, "send_response", send_response)

    assert asyncio.run(appium_service.check_status()) is False
    assert responses[-1]["data"]["status"] == "not installed"
    assert "uiautomator2" in responses[-1]["data"]["comment"]
