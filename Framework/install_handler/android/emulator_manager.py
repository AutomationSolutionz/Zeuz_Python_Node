"""Runtime lifecycle helpers for Android Virtual Devices.

The installer UI and Appium actions both use this module so an emulator is not
considered usable merely because its host process was spawned.  A target is
returned only after Android, Package Manager, and System UI have been stable
for a short period.
"""

from __future__ import annotations

import atexit
import os
import platform
import re
import subprocess
import tempfile
import threading
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from Framework.install_handler.android.android_sdk import _get_sdk_root, get_adb_path
from Framework.install_handler.install_log_config import get_logger


logger = get_logger()

DEFAULT_BOOT_TIMEOUT = 180
DEFAULT_STABILITY_SECONDS = 12
_POLL_INTERVAL_SECONDS = 2
_AUTO_AVD_VALUES = {"", "auto", "default", "none"}
_OWNED_PROCESSES: dict[str, subprocess.Popen] = {}
_REGISTRY_LOCK = threading.RLock()
_LIFECYCLE_LOCK = threading.RLock()


class EmulatorRuntimeError(RuntimeError):
    """Raised when an AVD cannot be prepared for automation."""


class SystemUiAnrError(EmulatorRuntimeError):
    """Raised when the emulator remains blocked by a System UI ANR."""


@dataclass(frozen=True)
class RunningEmulator:
    serial: str
    avd_name: str


@dataclass(frozen=True)
class EmulatorTarget:
    serial: str
    avd_name: str
    launched_by_zeuz: bool
    headless: bool


def _android_process_env() -> dict[str, str]:
    sdk_root = _get_sdk_root()
    env = os.environ.copy()
    env["ANDROID_HOME"] = str(sdk_root)
    env["ANDROID_SDK_ROOT"] = str(sdk_root)
    sdk_paths = [
        str(sdk_root / "platform-tools"),
        str(sdk_root / "emulator"),
        str(sdk_root / "cmdline-tools" / "latest" / "bin"),
    ]
    current_path = env.get("PATH", "")
    env["PATH"] = os.pathsep.join([*sdk_paths, current_path])
    return env


def _candidate_sdk_roots() -> list[Path]:
    """SDK roots to search for an AVD's system image, most-preferred first.

    ZeuZ's managed SDK is always tried first so that setups where the image lives
    inside the managed SDK (the normal Windows/Linux case) keep their current
    behaviour unchanged. Only when the image is missing there do we fall back to
    an SDK provided by the user's environment (e.g. an Android Studio install).
    """
    roots: list[Path] = [_get_sdk_root()]
    for var in ("ANDROID_SDK_ROOT", "ANDROID_HOME"):
        value = os.environ.get(var, "").strip()
        if value:
            roots.append(Path(value))
    system = platform.system()
    if system == "Darwin":
        roots.append(Path.home() / "Library" / "Android" / "sdk")
    elif system == "Linux":
        roots.append(Path.home() / "Android" / "Sdk")
    elif system == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
        if local_app_data:
            roots.append(Path(local_app_data) / "Android" / "Sdk")

    unique: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root)
        if key not in seen:
            seen.add(key)
            unique.append(root)
    return unique


def _find_avd_config_dir(avd_name: str) -> Path | None:
    """Locate an AVD's ``.avd`` directory (which holds ``config.ini``).

    AVDs live under an AVD home that is independent of the SDK root. We honour the
    standard override variables and fall back to ``~/.android/avd``. The
    authoritative pointer is ``<name>.ini`` (it stores the real ``path=``), with a
    direct ``<name>.avd`` lookup as a fallback.
    """
    avd_homes: list[Path] = []
    for var in ("ANDROID_AVD_HOME", "ANDROID_EMULATOR_HOME"):
        value = os.environ.get(var, "").strip()
        if value:
            avd_homes.append(Path(value))
    for var in ("ANDROID_SDK_HOME", "ANDROID_PREFS_ROOT"):
        value = os.environ.get(var, "").strip()
        if value:
            avd_homes.append(Path(value) / ".android" / "avd")
    avd_homes.append(Path.home() / ".android" / "avd")

    for avd_home in avd_homes:
        pointer = avd_home / f"{avd_name}.ini"
        if pointer.is_file():
            try:
                for line in pointer.read_text(
                    encoding="utf-8", errors="ignore"
                ).splitlines():
                    if line.strip().startswith("path="):
                        avd_dir = Path(line.split("=", 1)[1].strip())
                        if avd_dir.is_dir():
                            return avd_dir
            except Exception:
                pass  # Fall through to the direct-directory fallback
        direct = avd_home / f"{avd_name}.avd"
        if direct.is_dir():
            return direct
    return None


def _resolve_emulator_sdk_root(avd_name: str) -> Path:
    """Return the SDK root whose ``system-images`` tree holds the AVD's image.

    The emulator resolves the relative ``image.sysdir.1`` from ``config.ini``
    against ANDROID_SDK_ROOT, so pointing it at an SDK that lacks the image makes
    it fail with "Broken AVD system path". We pick the first candidate SDK root
    that actually contains the image; ZeuZ's managed SDK is checked first, so
    setups that already work are left untouched. Falls back to the managed SDK
    when nothing matches (e.g. absolute image paths, or config we can't read).
    """
    default_root = _get_sdk_root()
    avd_dir = _find_avd_config_dir(avd_name)
    if avd_dir is None:
        return default_root

    system_image_subdir = ""
    try:
        for line in (avd_dir / "config.ini").read_text(
            encoding="utf-8", errors="ignore"
        ).splitlines():
            if line.strip().startswith("image.sysdir.1="):
                system_image_subdir = line.split("=", 1)[1].strip()
                break
    except Exception:
        return default_root

    if not system_image_subdir:
        return default_root

    for root in _candidate_sdk_roots():
        if (root / system_image_subdir).is_dir():
            return root
    return default_root


def _emulator_process_env(avd_name: str) -> dict[str, str]:
    """Process env for launching ``avd_name``, pointed at an SDK that has its image."""
    env = _android_process_env()
    sdk_root = _resolve_emulator_sdk_root(avd_name)
    if str(sdk_root) != env.get("ANDROID_SDK_ROOT"):
        logger.info(
            "[emulator-runtime] AVD %s system image not found under the managed "
            "SDK; using SDK root %s instead.",
            avd_name,
            sdk_root,
        )
    env["ANDROID_HOME"] = str(sdk_root)
    env["ANDROID_SDK_ROOT"] = str(sdk_root)
    return env


def get_emulator_path() -> Path:
    executable = "emulator.exe" if platform.system() == "Windows" else "emulator"
    return _get_sdk_root() / "emulator" / executable


def _run(
    command: list[str],
    *,
    timeout: int = 20,
    text: bool = True,
) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=text,
            timeout=timeout,
            env=_android_process_env(),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        empty_output = "" if text else b""
        return subprocess.CompletedProcess(
            command,
            124,
            stdout=exc.stdout or empty_output,
            stderr=exc.stderr or empty_output,
        )


def _adb_command(*args: str) -> list[str]:
    return [str(get_adb_path()), *args]


def _parse_adb_devices(output: str) -> list[str]:
    serials = []
    for line in output.replace("\r", "").splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[1] == "device":
            serials.append(fields[0])
    return serials


def list_online_android_serials() -> list[str]:
    try:
        result = _run(_adb_command("devices"), timeout=20)
    except (FileNotFoundError, subprocess.SubprocessError):
        return []
    if result.returncode != 0:
        return []
    return _parse_adb_devices(result.stdout)


def _is_emulator(serial: str) -> bool:
    if serial.startswith("emulator-"):
        return True
    result = _run(
        _adb_command("-s", serial, "shell", "getprop", "ro.kernel.qemu"),
        timeout=10,
    )
    return result.returncode == 0 and result.stdout.strip() == "1"


def _get_running_avd_name(serial: str) -> str:
    result = _run(_adb_command("-s", serial, "emu", "avd", "name"), timeout=10)
    if result.returncode != 0:
        return ""
    for line in result.stdout.replace("\r", "").splitlines():
        value = line.strip()
        if value and value.upper() != "OK":
            return value
    return ""


def list_running_emulators() -> list[RunningEmulator]:
    emulators = []
    for serial in list_online_android_serials():
        if not _is_emulator(serial):
            continue
        emulators.append(
            RunningEmulator(serial=serial, avd_name=_get_running_avd_name(serial))
        )
    return emulators


def list_avd_names() -> list[str]:
    emulator_path = get_emulator_path()
    if not emulator_path.is_file():
        managed_adb = get_adb_path()
        missing = ["Android Emulator"]
        if not managed_adb.is_file():
            missing.insert(0, "ADB")
        raise EmulatorRuntimeError(
            f"Android tooling is not installed for this {platform.system()} ZeuZ Node. "
            f"Missing: {', '.join(missing)}. Expected SDK location: "
            f"{_get_sdk_root()}. Install Android SDK and an AVD from Connected "
            "ZeuZ Nodes, then run the test again."
        )
    result = _run([str(emulator_path), "-list-avds"], timeout=30)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise EmulatorRuntimeError(f"Unable to list Android AVDs: {detail}")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def resolve_avd_name(requested_avd: str | None = None) -> str:
    requested = (requested_avd or "").strip()
    available = list_avd_names()
    if requested.lower() not in _AUTO_AVD_VALUES:
        if requested not in available:
            raise EmulatorRuntimeError(
                f"Requested AVD '{requested}' is not installed. Available AVDs: "
                f"{', '.join(available) or 'none'}"
            )
        return requested

    configured_default = os.environ.get("ZEUZ_ANDROID_DEFAULT_AVD", "").strip()
    if configured_default:
        if configured_default not in available:
            raise EmulatorRuntimeError(
                "ZEUZ_ANDROID_DEFAULT_AVD points to an AVD that is not installed: "
                f"{configured_default}"
            )
        return configured_default

    if not available:
        raise EmulatorRuntimeError(
            "No Android AVD is installed. Install one from Connected ZeuZ Nodes first."
        )
    if len(available) > 1:
        logger.warning(
            "[emulator-runtime] Multiple AVDs are installed; using %s. "
            "Set ZEUZ_ANDROID_DEFAULT_AVD or provide avd=<name> to choose another.",
            available[0],
        )
    return available[0]


def _build_emulator_command(
    avd_name: str,
    *,
    headless: bool,
    cold_boot: bool,
) -> list[str]:
    command = [
        str(get_emulator_path()),
        "-avd",
        avd_name,
        "-no-audio",
        "-no-boot-anim",
    ]
    if headless:
        command.append("-no-window")
    if cold_boot:
        # Skip loading a potentially unhealthy Quick Boot snapshot without
        # wiping the AVD's user data.
        command.append("-no-snapshot-load")
    return command


def _log_directory() -> Path:
    path = Path(tempfile.gettempdir()) / "zeuz" / "android_emulator_logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _safe_avd_filename(avd_name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]", "_", avd_name) or "avd"


def _spawn_emulator(
    avd_name: str,
    *,
    headless: bool,
    cold_boot: bool,
) -> subprocess.Popen:
    log_path = _log_directory() / f"{_safe_avd_filename(avd_name)}.log"
    command = _build_emulator_command(
        avd_name,
        headless=headless,
        cold_boot=cold_boot,
    )
    popen_options = {
        "stdout": None,
        "stderr": subprocess.STDOUT,
        "env": _emulator_process_env(avd_name),
    }
    if os.name == "nt":
        popen_options["creationflags"] = getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0
        ) | getattr(subprocess, "DETACHED_PROCESS", 0)
    else:
        popen_options["start_new_session"] = True

    with open(log_path, "w", encoding="utf-8") as log_file:
        popen_options["stdout"] = log_file
        process = subprocess.Popen(command, **popen_options)

    with _REGISTRY_LOCK:
        _OWNED_PROCESSES[avd_name] = process
    logger.info(
        "[emulator-runtime] Started AVD %s (PID %s, headless=%s, cold_boot=%s)",
        avd_name,
        process.pid,
        headless,
        cold_boot,
    )
    return process


def _read_log_tail(avd_name: str, max_lines: int = 25) -> str:
    log_path = _log_directory() / f"{_safe_avd_filename(avd_name)}.log"
    try:
        lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        return " | ".join(line.strip() for line in lines[-max_lines:] if line.strip())
    except Exception:
        return ""


def _wait_for_serial(
    avd_name: str,
    process: subprocess.Popen,
    baseline_serials: set[str],
    deadline: float,
) -> str:
    fallback_serial = ""
    while time.monotonic() < deadline:
        if process.poll() is not None:
            hint = _read_log_tail(avd_name)
            raise EmulatorRuntimeError(
                f"AVD '{avd_name}' exited during startup with code {process.returncode}. "
                f"{hint}"
            )
        for emulator in list_running_emulators():
            if emulator.avd_name == avd_name:
                return emulator.serial
            if emulator.serial not in baseline_serials:
                fallback_serial = emulator.serial
        if fallback_serial:
            return fallback_serial
        time.sleep(_POLL_INTERVAL_SECONDS)
    raise EmulatorRuntimeError(
        f"AVD '{avd_name}' did not connect to ADB before the startup timeout."
    )


def _getprop(serial: str, prop: str) -> str:
    result = _run(
        _adb_command("-s", serial, "shell", "getprop", prop),
        timeout=10,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _package_manager_is_ready(serial: str) -> bool:
    result = _run(
        _adb_command(
            "-s", serial, "shell", "cmd", "package", "list", "packages", "android"
        ),
        timeout=20,
    )
    return result.returncode == 0 and "package:android" in result.stdout


def _wait_for_android_boot(serial: str, deadline: float) -> None:
    while time.monotonic() < deadline:
        if serial not in list_online_android_serials():
            time.sleep(_POLL_INTERVAL_SECONDS)
            continue
        boot_completed = _getprop(serial, "sys.boot_completed") == "1"
        boot_animation = _getprop(serial, "init.svc.bootanim")
        if (
            boot_completed
            and boot_animation in {"", "stopped"}
            and _package_manager_is_ready(serial)
        ):
            return
        time.sleep(_POLL_INTERVAL_SECONDS)
    raise EmulatorRuntimeError(
        f"Android on {serial} did not finish booting before the startup timeout."
    )


def _focused_window(serial: str) -> str:
    result = _run(
        _adb_command("-s", serial, "shell", "dumpsys", "window", "windows"),
        timeout=20,
    )
    if result.returncode != 0:
        return ""
    focus_lines = [
        line
        for line in result.stdout.splitlines()
        if "mCurrentFocus" in line or "mFocusedApp" in line
    ]
    return "\n".join(focus_lines)


def _is_system_ui_anr_text(value: str) -> bool:
    lowered = value.lower().replace("’", "'")
    mentions_system_ui = "com.android.systemui" in lowered or "system ui" in lowered
    mentions_anr = (
        "isn't responding" in lowered
        or "is not responding" in lowered
        or "application error" in lowered
        or "application not responding" in lowered
    )
    return mentions_system_ui and mentions_anr


def _parse_bounds(value: str) -> tuple[int, int] | None:
    match = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", value or "")
    if not match:
        return None
    left, top, right, bottom = map(int, match.groups())
    return ((left + right) // 2, (top + bottom) // 2)


def _dump_ui(serial: str) -> str:
    remote_path = "/data/local/tmp/zeuz-window.xml"
    dump = _run(
        _adb_command(
            "-s", serial, "shell", "uiautomator", "dump", "--compressed", remote_path
        ),
        timeout=25,
    )
    if dump.returncode != 0:
        return ""
    result = _run(
        _adb_command("-s", serial, "exec-out", "cat", remote_path),
        timeout=15,
    )
    return result.stdout if result.returncode == 0 else ""


def _dismiss_system_ui_anr(serial: str) -> bool:
    """Click only Android's ANR "Wait" button; never close the System UI app."""
    for _ in range(3):
        xml = _dump_ui(serial)
        if not xml:
            time.sleep(_POLL_INTERVAL_SECONDS)
            continue
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            time.sleep(_POLL_INTERVAL_SECONDS)
            continue

        all_text = " ".join(
            " ".join(
                filter(
                    None,
                    (node.attrib.get("text", ""), node.attrib.get("content-desc", "")),
                )
            )
            for node in root.iter()
        )
        if not _is_system_ui_anr_text(all_text):
            return True

        for node in root.iter():
            resource_id = node.attrib.get("resource-id", "").lower()
            text = node.attrib.get("text", "").strip().lower()
            if resource_id.endswith("aerr_wait") or text == "wait":
                center = _parse_bounds(node.attrib.get("bounds", ""))
                if not center:
                    continue
                result = _run(
                    _adb_command(
                        "-s",
                        serial,
                        "shell",
                        "input",
                        "touchscreen",
                        "tap",
                        str(center[0]),
                        str(center[1]),
                    ),
                    timeout=10,
                )
                if result.returncode == 0:
                    logger.warning(
                        "[emulator-runtime] Dismissed System UI ANR with the safe Wait action on %s",
                        serial,
                    )
                    time.sleep(4)
                    return True
        time.sleep(_POLL_INTERVAL_SECONDS)
    return False


def _wait_for_stable_system_ui(
    serial: str,
    *,
    deadline: float,
    stability_seconds: int,
    anr_wait_action: Callable[[], bool] | None = None,
) -> None:
    stable_since: float | None = None
    saw_system_ui_anr = False

    while time.monotonic() < deadline:
        pid = _run(
            _adb_command("-s", serial, "shell", "pidof", "com.android.systemui"),
            timeout=10,
        )
        focus = _focused_window(serial)
        if _is_system_ui_anr_text(focus):
            if not saw_system_ui_anr:
                _capture_failure_screenshot(serial, f"system-ui-anr-{serial}")
            saw_system_ui_anr = True
            stable_since = None
            try:
                if anr_wait_action is not None:
                    anr_wait_action()
                else:
                    _dismiss_system_ui_anr(serial)
            except Exception:
                logger.warning(
                    "[emulator-runtime] Could not select the System UI ANR Wait action on %s",
                    serial,
                )
            time.sleep(_POLL_INTERVAL_SECONDS)
            continue

        if pid.returncode == 0 and pid.stdout.strip():
            if stable_since is None:
                stable_since = time.monotonic()
            if time.monotonic() - stable_since >= stability_seconds:
                return
        else:
            stable_since = None
        time.sleep(_POLL_INTERVAL_SECONDS)

    if saw_system_ui_anr:
        raise SystemUiAnrError(
            f"System UI on {serial} remained unresponsive after Android booted."
        )
    raise EmulatorRuntimeError(
        f"System UI on {serial} did not remain stable for {stability_seconds} seconds."
    )


def _capture_failure_screenshot(serial: str, avd_name: str) -> Path | None:
    try:
        result = _run(
            _adb_command("-s", serial, "exec-out", "screencap", "-p"),
            timeout=20,
            text=False,
        )
        if result.returncode != 0 or not result.stdout:
            return None
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        path = _log_directory() / f"{_safe_avd_filename(avd_name)}-{timestamp}.png"
        path.write_bytes(result.stdout)
        logger.warning("[emulator-runtime] Saved readiness screenshot to %s", path)
        return path
    except Exception:
        return None


def _prepare_running_target(
    emulator: RunningEmulator,
    *,
    headless: bool,
    boot_timeout: int,
    stability_seconds: int,
) -> EmulatorTarget:
    boot_deadline = time.monotonic() + boot_timeout
    try:
        _wait_for_android_boot(emulator.serial, boot_deadline)
        _wait_for_stable_system_ui(
            emulator.serial,
            deadline=time.monotonic() + max(60, stability_seconds * 3),
            stability_seconds=stability_seconds,
        )
    except EmulatorRuntimeError:
        _capture_failure_screenshot(emulator.serial, emulator.avd_name or "emulator")
        raise
    with _REGISTRY_LOCK:
        process = _OWNED_PROCESSES.get(emulator.avd_name)
        owned = process is not None and process.poll() is None
    return EmulatorTarget(
        serial=emulator.serial,
        avd_name=emulator.avd_name,
        launched_by_zeuz=owned,
        headless=headless,
    )


def _stop_owned_emulator(avd_name: str, serial: str = "") -> None:
    if serial:
        try:
            _run(_adb_command("-s", serial, "emu", "kill"), timeout=15)
        except Exception:
            pass
    with _REGISTRY_LOCK:
        process = _OWNED_PROCESSES.pop(avd_name, None)
    if process is not None and process.poll() is None:
        try:
            process.terminate()
            process.wait(timeout=15)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass


def wait_for_android_runtime_stability(
    serial: str,
    *,
    stability_seconds: int = DEFAULT_STABILITY_SECONDS,
    timeout: int = 60,
    anr_wait_action: Callable[[], bool] | None = None,
) -> None:
    """Wait until System UI is healthy after Appium activates an application."""
    try:
        _wait_for_stable_system_ui(
            serial,
            deadline=time.monotonic() + max(timeout, stability_seconds * 3),
            stability_seconds=stability_seconds,
            anr_wait_action=anr_wait_action,
        )
    except EmulatorRuntimeError:
        running = next(
            (item for item in list_running_emulators() if item.serial == serial),
            None,
        )
        _capture_failure_screenshot(
            serial,
            running.avd_name if running else "emulator",
        )
        raise


def _ensure_android_emulator(
    *,
    requested_avd: str | None = None,
    requested_serial: str | None = None,
    headless: bool = False,
    boot_timeout: int = DEFAULT_BOOT_TIMEOUT,
    stability_seconds: int = DEFAULT_STABILITY_SECONDS,
) -> EmulatorTarget:
    """Reuse a running AVD or launch and fully prepare one for Appium."""
    requested = (requested_avd or "").strip()
    running = list_running_emulators()
    if requested.lower() not in _AUTO_AVD_VALUES:
        running = [item for item in running if item.avd_name == requested]

    serial_request = (requested_serial or "").strip()
    ignored_serials = {*_AUTO_AVD_VALUES, "launch", "na", "n/a"}
    if serial_request.lower() not in ignored_serials:
        serial_matches = [item for item in running if item.serial == serial_request]
        if serial_matches:
            running = serial_matches
        elif serial_request.startswith("emulator-"):
            raise EmulatorRuntimeError(
                f"Requested Android emulator '{serial_request}' is not connected."
            )

    if len(running) == 1:
        logger.info(
            "[emulator-runtime] Reusing running AVD %s (%s)",
            running[0].avd_name or "unknown",
            running[0].serial,
        )
        return _prepare_running_target(
            running[0],
            headless=headless,
            boot_timeout=boot_timeout,
            stability_seconds=stability_seconds,
        )
    if len(running) > 1:
        choices = ", ".join(
            f"{item.avd_name or 'unknown'} ({item.serial})" for item in running
        )
        raise EmulatorRuntimeError(
            f"Multiple Android emulators are running. Provide avd=<name>. Found: {choices}"
        )

    avd_name = resolve_avd_name(requested)
    baseline_serials = set(list_online_android_serials())
    last_error: Exception | None = None

    # Quick Boot first. If a restored snapshot leaves System UI unhealthy,
    # retry once with a cold boot while preserving the AVD's user data.
    for cold_boot in (False, True):
        process = _spawn_emulator(
            avd_name,
            headless=headless,
            cold_boot=cold_boot,
        )
        boot_deadline = time.monotonic() + boot_timeout
        serial = ""
        try:
            serial = _wait_for_serial(
                avd_name,
                process,
                baseline_serials,
                boot_deadline,
            )
            _wait_for_android_boot(serial, boot_deadline)
            _wait_for_stable_system_ui(
                serial,
                deadline=time.monotonic() + max(60, stability_seconds * 3),
                stability_seconds=stability_seconds,
            )
            logger.info(
                "[emulator-runtime] AVD %s is ready for automation on %s",
                avd_name,
                serial,
            )
            return EmulatorTarget(
                serial=serial,
                avd_name=avd_name,
                launched_by_zeuz=True,
                headless=headless,
            )
        except EmulatorRuntimeError as exc:
            last_error = exc
            if serial:
                _capture_failure_screenshot(serial, avd_name)
            _stop_owned_emulator(avd_name, serial)
            if not cold_boot:
                logger.warning(
                    "[emulator-runtime] Quick Boot for %s was not healthy (%s). Retrying with snapshot loading disabled.",
                    avd_name,
                    exc,
                )
                time.sleep(3)
                continue
            break

    detail = _read_log_tail(avd_name)
    raise EmulatorRuntimeError(
        f"Unable to prepare AVD '{avd_name}' for automation: {last_error}. {detail}"
    )


def ensure_android_emulator(
    *,
    requested_avd: str | None = None,
    requested_serial: str | None = None,
    headless: bool = False,
    boot_timeout: int = DEFAULT_BOOT_TIMEOUT,
    stability_seconds: int = DEFAULT_STABILITY_SECONDS,
) -> EmulatorTarget:
    """Serialize AVD preparation so parallel runs cannot launch the same AVD twice."""
    with _LIFECYCLE_LOCK:
        return _ensure_android_emulator(
            requested_avd=requested_avd,
            requested_serial=requested_serial,
            headless=headless,
            boot_timeout=boot_timeout,
            stability_seconds=stability_seconds,
        )


def stop_all_owned_emulators() -> None:
    with _REGISTRY_LOCK:
        owned_names = list(_OWNED_PROCESSES)
    if not owned_names:
        return
    try:
        running_by_name = {
            emulator.avd_name: emulator.serial for emulator in list_running_emulators()
        }
    except Exception:
        running_by_name = {}
    for avd_name in owned_names:
        _stop_owned_emulator(avd_name, running_by_name.get(avd_name, ""))


atexit.register(stop_all_owned_emulators)
