"""Linux-only tests against a real Xvfb, pyautogui and python3-xlib.

They reproduce how desktop actions used to hang a node (and starve it of CPU)
once pyautogui's X server was gone, and check that the node recovers instead.
Each scenario runs in its own process, because pyautogui binds to an X display
when it is imported.
"""

import json
import os
import shutil
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    not sys.platform.startswith("linux") or shutil.which("Xvfb") is None,
    reason="needs Linux with Xvfb",
)

PRELUDE = textwrap.dedent(f"""
    import json, os, subprocess, sys, threading, time
    sys.path.insert(0, {str(REPO)!r})
    from Framework.Utilities import x11_utils
    x11_utils.enable_xlib_threading()  # what the node does at startup
    from xvfbwrapper import Xvfb

    def timed(fn):
        start = time.monotonic()
        try:
            fn()
            outcome = "ok"
        except BaseException as e:
            outcome = type(e).__name__
        return outcome, round(time.monotonic() - start, 2)

    def report(data):
        print(json.dumps(data), flush=True)  # flush: the scenario ends with os._exit

    def cpu_seconds_over(seconds):
        start = time.process_time()
        time.sleep(seconds)
        return round(time.process_time() - start, 2)
""")


def run_scenario(body, tmp_path, timeout=120):
    xauthority = tmp_path / "Xauthority"
    xauthority.touch()
    env = dict(os.environ, XAUTHORITY=str(xauthority))
    env.pop("DISPLAY", None)
    script = PRELUDE + textwrap.dedent(body)
    result = subprocess.run(
        [sys.executable, "-c", script], cwd=REPO, env=env,
        capture_output=True, text=True, timeout=timeout,
    )
    lines = [line for line in result.stdout.splitlines() if line.startswith("{")]
    assert lines, result.stdout + result.stderr
    return json.loads(lines[-1])


def test_pyautogui_follows_the_display_after_its_xvfb_is_stopped(tmp_path):
    report = run_scenario("""
        first = Xvfb(width=800, height=600); first.start()
        import pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.hotkey("ctrl", "a")

        first.stop()                                            # teardown stops the display
        second = Xvfb(width=800, height=600); second.start()  # the next test case's browser

        messages = x11_utils.ensure_pyautogui_display()
        outcome = timed(lambda: pyautogui.hotkey("ctrl", "a"))
        report({
            "messages": messages,
            "bound_to": pyautogui._pyautogui_x11._display.get_display_name(),
            "second": ":%s" % second.new_display,
            "hotkey": outcome,
            "check_again": x11_utils.ensure_pyautogui_display(),
        })
        second.stop()
        os._exit(0)
    """, tmp_path)
    assert report["bound_to"] == report["second"]
    assert report["hotkey"][0] == "ok"
    assert len(report["messages"]) == 1 and "reconnected to" in report["messages"][0][0]
    assert report["check_again"] == []  # nothing to do once healthy


def test_pyautogui_follows_display_changes_while_the_old_display_is_alive(tmp_path):
    report = run_scenario("""
        desktop = Xvfb(width=800, height=600); desktop.start()   # like the VM's VNC desktop
        import pyautogui
        pyautogui.FAILSAFE = False
        browser_display = Xvfb(width=800, height=600); browser_display.start()  # headless browser

        to_browser = x11_utils.ensure_pyautogui_display()
        on_browser = pyautogui._pyautogui_x11._display.get_display_name()
        hotkey_browser = timed(lambda: pyautogui.hotkey("ctrl", "a"))

        browser_display.stop()  # teardown: DISPLAY goes back to the desktop
        back = x11_utils.ensure_pyautogui_display()
        on_desktop = pyautogui._pyautogui_x11._display.get_display_name()
        hotkey_desktop = timed(lambda: pyautogui.hotkey("ctrl", "a"))
        report({"to_browser": to_browser, "on_browser": on_browser, "browser": ":%s" % browser_display.new_display,
                "hotkey_browser": hotkey_browser, "back": back, "on_desktop": on_desktop,
                "desktop": ":%s" % desktop.new_display, "hotkey_desktop": hotkey_desktop,
                "quiet": x11_utils.ensure_pyautogui_display()})
        desktop.stop()
        os._exit(0)
    """, tmp_path)
    assert report["on_browser"] == report["browser"] and report["hotkey_browser"][0] == "ok"
    assert "switched to" in report["to_browser"][0][0]
    assert report["on_desktop"] == report["desktop"] and report["hotkey_desktop"][0] == "ok"
    assert report["quiet"] == []


def test_desktop_actions_fail_fast_without_any_display_and_recover_later(tmp_path):
    report = run_scenario("""
        first = Xvfb(width=800, height=600); first.start()
        import pyautogui
        pyautogui.FAILSAFE = False
        first.stop()  # DISPLAY is unset again now

        messages = x11_utils.ensure_pyautogui_display()
        repeated = [x11_utils.ensure_pyautogui_display() for _ in range(3)]
        calls = [timed(lambda: pyautogui.hotkey("ctrl", "a")) for _ in range(3)]
        cpu = cpu_seconds_over(2)

        later = Xvfb(width=800, height=600); later.start()
        messages_later = x11_utils.ensure_pyautogui_display()
        after = timed(lambda: pyautogui.hotkey("ctrl", "a"))
        report({"messages": messages, "repeated": repeated, "calls": calls, "cpu": cpu,
                          "messages_later": messages_later, "after": after})
        later.stop()
        os._exit(0)
    """, tmp_path)
    assert "DISPLAY is not set" in report["messages"][0][0]
    assert report["repeated"] == [[], [], []]  # reported once, not before every action
    for outcome, seconds in report["calls"]:
        assert outcome != "ok" and seconds < 1  # fails right away instead of hanging
    assert report["cpu"] < 0.5
    assert "reconnected to" in report["messages_later"][0][0]
    assert report["after"][0] == "ok"


def test_action_stuck_in_an_x_call_is_freed_and_desktop_actions_keep_working(tmp_path):
    report = run_scenario("""
        from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr
        sr.Set_Shared_Variables("dependency", {"Browser": "Chrome"}, print_variable=False)
        from Framework.Built_In_Automation.Sequential_Actions import sequential_actions
        from Framework.Utilities import node_health
        sequential_actions._get_action_timeout = lambda: 2
        sequential_actions._force_kill_hung_browser_sessions = lambda: None

        display = Xvfb(width=800, height=600); display.start()
        import pyautogui
        pyautogui.FAILSAFE = False

        # Another client grabs the X server, so pyautogui's request gets no reply.
        grabber = subprocess.Popen([sys.executable, "-c", (
            "import sys\\n"
            "from Xlib.display import Display\\n"
            "d = Display(); d.grab_server(); d.sync()\\n"
            "print('grabbed', flush=True)\\n"
            "sys.stdin.readline()\\n"
            "d.ungrab_server(); d.sync()\\n"
        )], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        while grabber.stdout.readline().strip() != "grabbed":  # Xlib may print warnings first
            pass
        # Release the grab shortly after the action times out, like a server that recovers.
        threading.Timer(2.5, lambda: (grabber.stdin.write("\\n"), grabber.stdin.flush())).start()

        cpu = {}
        def sample_cpu():
            time.sleep(0.5); cpu["during_hang"] = cpu_seconds_over(1)
        threading.Thread(target=sample_cpu, daemon=True).start()

        def hotkey_action(_):
            pyautogui.hotkey("ctrl", "a")
            return "passed"

        logged = []
        sequential_actions.CommonUtil.ExecLog = lambda module, msg, level=1, *a, **k: logged.append((msg, level))
        first = sequential_actions._run_action_with_timeout(hotkey_action, [])
        stuck_right_after = len(node_health.stuck_threads())
        freed = False
        for _ in range(50):
            if not node_health.stuck_threads():
                freed = True
                break
            time.sleep(0.1)
        second = sequential_actions._run_action_with_timeout(hotkey_action, [])
        report({"first": first, "second": second, "cpu": cpu, "logged": logged,
                          "stuck_right_after": stuck_right_after, "freed": freed})
        grabber.wait(5)
        display.stop()
        os._exit(0)
    """, tmp_path)
    assert report["first"] == "zeuz_failed"
    assert report["cpu"]["during_hang"] < 0.3  # waiting, not spinning
    assert report["freed"] is True  # the stuck thread ended, so no restart is needed
    assert report["second"] == "passed"
    messages = " ".join(m for m, _ in report["logged"])
    assert "stuck in an X11 call" in messages and "Reconnected desktop automation" in messages


def test_selenium_headless_browsers_share_one_xvfb_and_stop_it(tmp_path, monkeypatch):
    import psutil

    from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr
    from Framework.Utilities import x11_utils

    had_dependency = sr.Test_Shared_Variables("dependency")
    if not had_dependency:
        sr.Set_Shared_Variables("dependency", {"Browser": "Chrome"}, print_variable=False)
    from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as selenium_actions

    monkeypatch.setattr(x11_utils, "_XVFB_REGISTRY", tmp_path / "xvfb_processes.json")
    monkeypatch.setattr(selenium_actions, "vdisplay", None)
    monkeypatch.setattr(selenium_actions, "selenium_details", {})

    def xvfb_children():
        return [p for p in psutil.Process().children() if p.name() == "Xvfb"]

    try:
        selenium_actions.use_xvfb_or_headless(lambda: pytest.fail("fell back to headless"))
        selenium_actions.use_xvfb_or_headless(lambda: pytest.fail("fell back to headless"))
        assert len(xvfb_children()) == 1
        assert len(x11_utils._read_xvfb_registry()) == 1

        assert selenium_actions.Tear_Down_Selenium([]) == "passed"
        assert xvfb_children() == []
        assert x11_utils._read_xvfb_registry() == []
    finally:
        selenium_actions._stop_vdisplay()
        if not had_dependency:
            sr.Remove_From_Shared_Variables("dependency")


def test_xvfb_left_by_a_killed_node_is_cleaned_up_on_next_start(tmp_path, monkeypatch):
    import psutil

    from Framework.Utilities import x11_utils

    registry = tmp_path / "xvfb_processes.json"
    xauthority = tmp_path / "Xauthority"
    xauthority.touch()
    crashed_node = subprocess.Popen([sys.executable, "-c", textwrap.dedent(f"""
        import os, signal, sys
        sys.path.insert(0, {str(REPO)!r})
        from pathlib import Path
        from Framework.Utilities import x11_utils
        x11_utils._XVFB_REGISTRY = Path({str(registry)!r})
        from xvfbwrapper import Xvfb
        display = Xvfb(width=800, height=600); display.start()
        x11_utils.remember_xvfb(display.proc.pid, display.new_display)
        print(display.proc.pid, flush=True)
        os.kill(os.getpid(), signal.SIGKILL)  # node killed (OOM, kill -9, ...)
    """)], stdout=subprocess.PIPE, text=True, env=dict(os.environ, XAUTHORITY=str(xauthority)))
    xvfb_pid = int(crashed_node.stdout.readline())
    crashed_node.wait(30)
    try:
        assert psutil.Process(xvfb_pid).is_running()  # orphaned

        monkeypatch.setattr(x11_utils, "_XVFB_REGISTRY", registry)
        assert x11_utils.cleanup_orphaned_xvfb() == [xvfb_pid]
        deadline = time.monotonic() + 5
        while psutil.pid_exists(xvfb_pid) and time.monotonic() < deadline:
            time.sleep(0.05)
        assert not psutil.pid_exists(xvfb_pid) or psutil.Process(xvfb_pid).status() == psutil.STATUS_ZOMBIE
        assert x11_utils._read_xvfb_registry() == []
    finally:
        try:
            os.kill(xvfb_pid, signal.SIGKILL)
        except OSError:
            pass
