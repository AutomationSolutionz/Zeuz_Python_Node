"""Tests for the fixes that stop a hung action from degrading a node over time."""

import argparse
import ast
import json
import os
import subprocess
import sys
import textwrap
import threading
import time
from pathlib import Path

import psutil
import pytest

from Framework.Built_In_Automation.Sequential_Actions import sequential_actions
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr
from Framework.Utilities import ConfigModule, node_health, x11_utils

NODE_CLI = Path(__file__).resolve().parents[1] / "node_cli.py"


@pytest.fixture
def selenium_actions():
    """The Selenium actions module (it needs a dependency set before import)."""
    had_dependency = sr.Test_Shared_Variables("dependency")
    if not had_dependency:
        sr.Set_Shared_Variables("dependency", {"Browser": "Chrome"}, print_variable=False)
    from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions

    yield BuiltInFunctions
    if not had_dependency:
        sr.Remove_From_Shared_Variables("dependency")


def _node_cli_function(name, namespace):
    """Load one top-level function from node_cli.py (importing it starts the node)."""
    tree = ast.parse(NODE_CLI.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module([fn], []), str(NODE_CLI), "exec"), namespace)
    return namespace[name]


# --- Config cache --------------------------------------------------------------

def test_config_cache_sees_writes_from_this_process(tmp_path):
    ini = tmp_path / "temp_config.ini"
    ini.write_text("[sectionOne]\nsTestStepExecLogId = run|tc|1|1\n")
    assert ConfigModule.get_config_value("sectionOne", "sTestStepExecLogId", ini) == "run|tc|1|1"

    # Same size, written right away: must not be served from the cache.
    ConfigModule.add_config_value("sectionOne", "sTestStepExecLogId", "run|tc|1|2", ini)
    assert ConfigModule.get_config_value("sectionOne", "sTestStepExecLogId", ini) == "run|tc|1|2"

    ConfigModule.remove_config_value("sectionOne", "sTestStepExecLogId", ini)
    assert ConfigModule.get_config_value("sectionOne", "sTestStepExecLogId", ini) == ""


def test_config_cache_sees_changes_from_other_processes(tmp_path):
    ini = tmp_path / "settings.conf"
    ini.write_text("[Advanced Options]\nstop_live_log = False\n")
    assert ConfigModule.get_config_value("Advanced Options", "stop_live_log", ini) == "False"

    ini.write_text("[Advanced Options]\nstop_live_log = True\n")
    st = ini.stat()
    os.utime(ini, ns=(st.st_atime_ns, st.st_mtime_ns + 10**9))  # same size, newer mtime
    assert ConfigModule.get_config_value("Advanced Options", "stop_live_log", ini) == "True"

    ini.write_text("[Advanced Options]\nstop_live_log = disable\n")  # different size
    assert ConfigModule.get_config_value("Advanced Options", "stop_live_log", ini) == "disable"


def test_config_cache_does_not_reread_an_unchanged_file(tmp_path, monkeypatch):
    ini = tmp_path / "settings.conf"
    ini.write_text("[Advanced Options]\n_file = temp_config.ini\n")
    reads = []
    original_read = ConfigModule.configparser.ConfigParser.read
    monkeypatch.setattr(
        ConfigModule.configparser.ConfigParser, "read",
        lambda self, *a, **k: reads.append(1) or original_read(self, *a, **k),
    )
    for _ in range(5):
        assert ConfigModule.get_config_value("Advanced Options", "_file", ini) == "temp_config.ini"
    assert len(reads) == 1


def test_config_missing_file_and_missing_keys(tmp_path):
    ini = tmp_path / "later.ini"
    assert ConfigModule.get_config_value("s", "k", ini) == ""
    ini.write_text("[s]\nk = v\n")
    assert ConfigModule.get_config_value("s", "k", ini) == "v"
    assert ConfigModule.get_config_value("s", "missing", ini) == ""
    assert ConfigModule.get_config_value("missing", "k", ini) == ""


def test_config_remote_values_still_take_priority(tmp_path):
    ini = tmp_path / "settings.conf"
    ini.write_text("[RunDefinition]\nthreading = True\n")
    assert ConfigModule.get_config_value("RunDefinition", "threading", ini) == str(ConfigModule.remote_config["threading"])


# --- Stuck action workers ----------------------------------------------------------

@pytest.fixture
def fast_action_timeout(monkeypatch):
    monkeypatch.setattr(sequential_actions, "_action_worker", None)
    monkeypatch.setattr(sequential_actions, "_get_action_timeout", lambda: 0.3)
    monkeypatch.setattr(sequential_actions, "_force_kill_hung_browser_sessions", lambda: None)
    monkeypatch.setattr(node_health, "_workers", [])


def _wait_until(condition, timeout=5):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.02)
    return condition()


def test_timed_out_action_is_tracked_and_its_worker_exits_once_it_returns(fast_action_timeout):
    release = threading.Event()

    def hung_action(_):
        release.wait(10)
        return "passed"

    assert sequential_actions._run_action_with_timeout(hung_action, []) == "zeuz_failed"
    stuck = node_health.stuck_threads()
    assert len(stuck) == 1 and stuck[0].name == "zeuz_action_worker"

    # The next action runs on a fresh worker and is not affected.
    assert sequential_actions._run_action_with_timeout(lambda _: "passed", []) == "passed"
    assert sequential_actions._action_worker.thread is not stuck[0]

    release.set()
    stuck[0].join(5)
    assert not stuck[0].is_alive()  # the abandoned worker was retired
    assert node_health.stuck_threads() == []


def test_thread_affine_timeout_keeps_its_worker_and_recovers(fast_action_timeout):
    release = threading.Event()

    def hung_affine_action(_):
        release.wait(10)
        return "passed"

    hung_affine_action._zeuz_thread_affine = True
    assert sequential_actions._run_action_with_timeout(hung_affine_action, []) == "zeuz_failed"
    worker = sequential_actions._action_worker
    assert worker is not None  # kept for thread affinity
    assert node_health.stuck_threads() == [worker.thread]

    release.set()
    assert _wait_until(lambda: node_health.stuck_threads() == [])
    assert worker.thread.is_alive()
    assert sequential_actions._run_action_with_timeout(lambda _: "passed", []) == "passed"


def test_actions_that_finish_in_time_are_never_tracked(fast_action_timeout):
    for _ in range(3):
        assert sequential_actions._run_action_with_timeout(lambda _: "passed", []) == "passed"
    with pytest.raises(ValueError):
        sequential_actions._run_action_with_timeout(lambda _: (_ for _ in ()).throw(ValueError("boom")), [])
    assert node_health.stuck_threads() == []
    assert node_health._workers == []


def test_x11_recovery_ignores_threads_not_in_x11():
    release = threading.Event()
    thread = threading.Thread(target=release.wait, daemon=True)
    thread.start()
    try:
        assert x11_utils.recover_x11_for_hung_thread(thread) == []
    finally:
        release.set()


# --- Restart -------------------------------------------------------------------------

def test_restart_args_keep_run_options_and_drop_credentials_and_logout():
    parser = _node_cli_function("_build_arg_parser", {"argparse": argparse})()
    parsed = parser.parse_args([
        "-s", "https://server", "-k", "SECRET-KEY", "-n", "node_1", "-d", "/tmp/logs",
        "-spu", "-slg", "-cf", "3", "--disable-mobile-install",
    ])
    args = node_health.restart_cli_args(parsed)
    assert args == ["-n", "node_1", "-d", "/tmp/logs", "-spu", "-slg", "-cf", "3", "--disable-mobile-install"]
    assert "SECRET-KEY" not in args and "https://server" not in args

    assert node_health.restart_cli_args(parser.parse_args(["-l"])) == []
    assert node_health.restart_cli_args(parser.parse_args([])) == []


def test_restart_command_keeps_interpreter_and_its_options():
    cmd = node_health.restart_command(
        "/venv/bin/python3",
        ["/venv/bin/python3", "-u", "-X", "dev", "node_cli.py", "-s", "x"],
        ["node_cli.py", "-s", "x"],
        "/nodes/node1/node_cli.py",
        ["-n", "node_1"],
    )
    assert cmd == ["/venv/bin/python3", "-u", "-X", "dev", "/nodes/node1/node_cli.py", "-n", "node_1"]
    assert node_health.restart_command("/py", ["/py", "node_cli.py"], ["node_cli.py"], "/a/node_cli.py", []) == [
        "/py", "/a/node_cli.py"
    ]


def test_kill_old_process_does_not_kill_itself_after_an_in_place_restart(tmp_path):
    pid_file = tmp_path / "pid.txt"
    script = textwrap.dedent(f"""
        import ast, os, psutil
        tree = ast.parse(open({str(NODE_CLI)!r}).read())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "kill_old_process")
        ns = {{"os": os, "psutil": psutil}}
        exec(compile(ast.Module([fn], []), "node_cli.py", "exec"), ns)
        open({str(pid_file)!r}, "w").write(str(os.getpid()))
        ns["kill_old_process"]({str(pid_file)!r})
        print("still running", open({str(pid_file)!r}).read() == str(os.getpid()))
    """)
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=60)
    assert result.stdout.strip() == "still running True", result.stderr


# --- Masking credentials -----------------------------------------------------------

def test_mask_sensitive_values_masks_credentials_without_changing_the_value():
    value = {
        "url": "https://app.example.com",
        "email": "qa@example.com",
        "password": "Teamqa@987",
        "nested": {"API_KEY": "abc", "clientSecret": "def", "items": [{"auth-token": "t"}, "plain"]},
    }
    masked = sr.mask_sensitive_values(value)
    assert masked == {
        "url": "https://app.example.com",
        "email": "qa@example.com",
        "password": "*****",
        "nested": {"API_KEY": "*****", "clientSecret": "*****", "items": [{"auth-token": "*****"}, "plain"]},
    }
    assert value["password"] == "Teamqa@987"
    assert sr.mask_sensitive_values("hunter2", "DB_PASSWORD") == "*****"
    assert sr.mask_sensitive_values("https://x", "HUBSPOT_URL") == "https://x"


def test_run_time_params_are_masked_when_printed_but_stored_intact(monkeypatch):
    logged, printed = [], []
    monkeypatch.setattr(sr.CommonUtil, "ExecLog", lambda *a, **k: logged.append((a, k)))
    monkeypatch.setattr(sr.CommonUtil, "prettify", lambda key, val: printed.append(val))
    value = {"url": "https://login", "email": "qa@example.com", "password": "Teamqa@987"}
    try:
        assert sr.Set_Shared_Variables("zz_test_hubspot", value, mask_sensitive=True) == "passed"
        assert sr.Set_Shared_Variables("zz_test_db_password", "hunter2", mask_sensitive=True) == "passed"
        assert sr.Get_Shared_Variables("zz_test_hubspot", log=False)["password"] == "Teamqa@987"
        assert sr.Get_Shared_Variables("zz_test_db_password", log=False) == "hunter2"
        output = str(logged) + str(printed)
        assert "Teamqa@987" not in output and "hunter2" not in output
        assert "qa@example.com" in output and "*****" in output

        # Without the flag, printing is unchanged.
        printed.clear()
        sr.Set_Shared_Variables("zz_test_plain", {"password": "visible"})
        assert "visible" in printed[0]
    finally:
        for key in ("zz_test_hubspot", "zz_test_db_password", "zz_test_plain"):
            sr.Remove_From_Shared_Variables(key)


# --- save attribute values in list ---------------------------------------------------

class _FakeElement:
    def __init__(self, text):
        self.text = text


def _save_attribute_step_data():
    return [
        ("tag", "element parameter", "app-company-list"),
        ("attributes", "target parameter", 'xpath="//div[@class=\'company-overflow\']",\nreturn="text"'),
        ("save attribute values in list", "selenium action", "zz_test_keywords"),
    ]


def test_save_attribute_values_in_list_fails_clearly_when_nothing_matches(selenium_actions, monkeypatch):
    logged = []
    monkeypatch.setattr(selenium_actions.CommonUtil, "ExecLog", lambda *a, **k: logged.append(a))
    monkeypatch.setattr(
        selenium_actions.LocateElement, "Get_Element",
        lambda *a, **k: [] if k.get("return_all_elements") else object(),
    )
    assert selenium_actions.save_attribute_values_in_list(_save_attribute_step_data()) == "zeuz_failed"
    assert any("No element matched the target parameter" in str(a) for a in logged)
    assert not any("Traceback" in str(a) or "IndexError" in str(a) for a in logged)


def test_save_attribute_values_in_list_still_saves_matches(selenium_actions, monkeypatch):
    monkeypatch.setattr(selenium_actions.CommonUtil, "ExecLog", lambda *a, **k: None)
    monkeypatch.setattr(
        selenium_actions.LocateElement, "Get_Element",
        lambda *a, **k: [_FakeElement("AI"), _FakeElement("SaaS")] if k.get("return_all_elements") else object(),
    )
    try:
        assert selenium_actions.save_attribute_values_in_list(_save_attribute_step_data()) == "passed"
        assert sr.Get_Shared_Variables("zz_test_keywords", log=False) == ["AI", "SaaS"]
    finally:
        sr.Remove_From_Shared_Variables("zz_test_keywords")


# --- Xvfb reuse and cleanup ------------------------------------------------------------

class _FakeXvfbProcess:
    _next_pid = 50000

    def __init__(self):
        _FakeXvfbProcess._next_pid += 1
        self.pid = _FakeXvfbProcess._next_pid
        self.returncode = None

    def poll(self):
        return self.returncode


class _FakeXvfb:
    instances = []

    def __init__(self, **kwargs):
        self.proc = None
        self.new_display = None
        self.stopped = False
        _FakeXvfb.instances.append(self)

    def start(self):
        self.proc = _FakeXvfbProcess()
        self.new_display = 100 + len(_FakeXvfb.instances)
        os.environ["DISPLAY"] = ":%s" % self.new_display

    def stop(self):
        self.stopped = True
        self.proc = None


@pytest.fixture
def fake_xvfb(selenium_actions, monkeypatch):
    _FakeXvfb.instances = []
    remembered, forgotten = [], []
    monkeypatch.setattr(selenium_actions.platform, "system", lambda: "Linux")
    monkeypatch.setattr(selenium_actions, "Xvfb", _FakeXvfb, raising=False)
    monkeypatch.setattr(selenium_actions, "vdisplay", None)
    monkeypatch.setattr(selenium_actions.x11_utils, "remember_xvfb", lambda pid, display: remembered.append(pid))
    monkeypatch.setattr(selenium_actions.x11_utils, "forget_xvfb", lambda pid: forgotten.append(pid))
    monkeypatch.setattr(selenium_actions.CommonUtil, "ExecLog", lambda *a, **k: None)
    monkeypatch.setenv("DISPLAY", ":0")
    return remembered, forgotten


def test_headless_browsers_share_one_xvfb(selenium_actions, fake_xvfb):
    remembered, _ = fake_xvfb
    selenium_actions.use_xvfb_or_headless(lambda: pytest.fail("should not fall back to headless"))
    os.environ["DISPLAY"] = ":0"  # something else changed it in between
    selenium_actions.use_xvfb_or_headless(lambda: pytest.fail("should not fall back to headless"))
    assert len(_FakeXvfb.instances) == 1
    assert os.environ["DISPLAY"] == ":101"
    assert remembered == [_FakeXvfb.instances[0].proc.pid]


def test_exited_xvfb_is_replaced(selenium_actions, fake_xvfb):
    remembered, forgotten = fake_xvfb
    selenium_actions.use_xvfb_or_headless(lambda: None)
    first = _FakeXvfb.instances[0]
    first_pid = first.proc.pid
    first.proc.returncode = 1  # Xvfb crashed
    selenium_actions.use_xvfb_or_headless(lambda: None)
    assert len(_FakeXvfb.instances) == 2
    assert first.stopped and forgotten == [first_pid]
    assert selenium_actions.vdisplay is _FakeXvfb.instances[1]


def test_xvfb_failure_still_falls_back_to_headless(selenium_actions, fake_xvfb, monkeypatch):
    class BrokenXvfb(_FakeXvfb):
        def start(self):
            raise RuntimeError("Xvfb did not start")

    monkeypatch.setattr(selenium_actions, "Xvfb", BrokenXvfb)
    fell_back = []
    selenium_actions.use_xvfb_or_headless(lambda: fell_back.append(True))
    assert fell_back == [True]


class _FakeDriver:
    def __init__(self):
        self.quit_called = False

    def quit(self):
        self.quit_called = True


def test_xvfb_is_stopped_only_when_the_last_selenium_browser_is_torn_down(selenium_actions, fake_xvfb, monkeypatch):
    selenium_actions.use_xvfb_or_headless(lambda: None)
    display = selenium_actions.vdisplay
    a, b = _FakeDriver(), _FakeDriver()
    monkeypatch.setattr(selenium_actions, "selenium_details", {"a": {"driver": a}, "b": {"driver": b}})
    monkeypatch.setattr(selenium_actions, "selenium_driver", b)
    monkeypatch.setattr(selenium_actions.Shared_Resources, "Set_Shared_Variables", lambda *a, **k: "passed")
    monkeypatch.setattr(selenium_actions.Shared_Resources, "Remove_From_Shared_Variables", lambda *a, **k: "passed")

    assert selenium_actions.Tear_Down_Selenium([("driver id", "optional parameter", "a")]) == "passed"
    assert a.quit_called and not display.stopped
    assert selenium_actions.vdisplay is display

    assert selenium_actions.Tear_Down_Selenium([]) == "passed"
    assert b.quit_called and display.stopped
    assert selenium_actions.vdisplay is None


def _spawn_fake_xvfb(display):
    # A process whose command line looks like "Xvfb :<display> ...". PYTHONHOME is
    # needed because some Python builds locate their stdlib from argv[0].
    return subprocess.Popen(
        ["Xvfb", "-c", "import time; time.sleep(60)", display],
        executable=sys.executable,
        env=dict(os.environ, PYTHONHOME=sys.base_prefix),
    )


def _process_create_time(pid):
    return psutil.Process(pid).create_time()


def test_cleanup_orphaned_xvfb_only_stops_recorded_orphans(tmp_path, monkeypatch):
    monkeypatch.setattr(x11_utils, "_IS_LINUX", True)
    monkeypatch.setattr(x11_utils, "_XVFB_REGISTRY", tmp_path / "xvfb_processes.json")

    orphan = _spawn_fake_xvfb(":4242")
    owned = _spawn_fake_xvfb(":4243")
    unrelated = _spawn_fake_xvfb(":4244")
    live_owner = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    dead_owner = subprocess.Popen([sys.executable, "-c", "pass"])
    dead_owner.wait()
    try:
        assert _wait_until(lambda: "Xvfb" in " ".join(psutil.Process(orphan.pid).cmdline()))
        x11_utils._write_xvfb_registry([
            {"pid": orphan.pid, "display": ":4242", "create_time": _process_create_time(orphan.pid),
             "owner_pid": dead_owner.pid, "owner_create_time": 0},
            {"pid": owned.pid, "display": ":4243", "create_time": _process_create_time(owned.pid),
             "owner_pid": live_owner.pid, "owner_create_time": _process_create_time(live_owner.pid)},
            # Recorded pid now belongs to a different process (start time differs): leave it alone.
            {"pid": unrelated.pid, "display": ":4244", "create_time": 1.0,
             "owner_pid": dead_owner.pid, "owner_create_time": 0},
        ])

        assert x11_utils.cleanup_orphaned_xvfb() == [orphan.pid]
        assert orphan.wait(5) is not None
        assert owned.poll() is None and unrelated.poll() is None
        remaining = x11_utils._read_xvfb_registry()
        assert [e["pid"] for e in remaining] == [owned.pid]
    finally:
        for proc in (orphan, owned, unrelated, live_owner):
            proc.kill()
            proc.wait()


def test_cleanup_treats_a_zombie_owner_as_dead(tmp_path, monkeypatch):
    """Right after kill -9 the old node can linger as a zombie; its Xvfb must still be cleaned up."""
    monkeypatch.setattr(x11_utils, "_IS_LINUX", True)
    monkeypatch.setattr(x11_utils, "_XVFB_REGISTRY", tmp_path / "xvfb_processes.json")
    orphan = _spawn_fake_xvfb(":4250")
    zombie_owner = subprocess.Popen([sys.executable, "-c", "pass"])  # exits; not reaped yet
    try:
        assert _wait_until(lambda: psutil.Process(zombie_owner.pid).status() == psutil.STATUS_ZOMBIE)
        assert _wait_until(lambda: "Xvfb" in " ".join(psutil.Process(orphan.pid).cmdline()))
        x11_utils._write_xvfb_registry([
            {"pid": orphan.pid, "display": ":4250", "create_time": _process_create_time(orphan.pid),
             "owner_pid": zombie_owner.pid, "owner_create_time": _process_create_time(zombie_owner.pid)},
        ])
        assert x11_utils.cleanup_orphaned_xvfb() == [orphan.pid]
    finally:
        orphan.kill()
        orphan.wait()
        zombie_owner.wait()


def test_remember_and_forget_xvfb(tmp_path, monkeypatch):
    monkeypatch.setattr(x11_utils, "_XVFB_REGISTRY", tmp_path / "nested" / "xvfb_processes.json")
    proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    try:
        x11_utils.remember_xvfb(proc.pid, 77)
        entries = x11_utils._read_xvfb_registry()
        assert len(entries) == 1
        assert entries[0]["display"] == ":77" and entries[0]["owner_pid"] == os.getpid()
        x11_utils.forget_xvfb(proc.pid)
        assert x11_utils._read_xvfb_registry() == []
    finally:
        proc.kill()
        proc.wait()


@pytest.mark.skipif(os.name != "posix", reason="the node restarts itself in place only on POSIX")
def test_restart_node_process_replaces_itself_in_place(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    state_file = tmp_path / "state.json"
    fake_node = tmp_path / "fake_node.py"
    fake_node.write_text(textwrap.dedent(f"""
        import argparse, ast, json, os, subprocess, sys
        sys.path.insert(0, {str(repo)!r})
        from Framework.Utilities import node_bootstrap, node_health
        import psutil
        from colorama import Fore

        ns = dict(argparse=argparse, os=os, sys=sys, psutil=psutil, Fore=Fore,
                  node_health=node_health, node_bootstrap=node_bootstrap)
        tree = ast.parse(open({str(NODE_CLI)!r}).read())
        for fn in tree.body:
            if isinstance(fn, ast.FunctionDef) and fn.name in (
                "kill_child_processes", "_build_arg_parser", "restart_node_process"
            ):
                exec(compile(ast.Module([fn], []), "node_cli.py", "exec"), ns)

        state_file = {str(state_file)!r}
        if not os.path.exists(state_file):
            child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
            json.dump({{"pid": os.getpid(), "child": child.pid}}, open(state_file, "w"))
            os.environ["DISPLAY"] = ":999"  # changed during the run (e.g. by Xvfb)
            os.chdir("/")
            ns["restart_node_process"]()
            print("restart did not happen")
            sys.exit(1)

        state = json.load(open(state_file))
        try:
            child_alive = psutil.Process(state["child"]).status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            child_alive = False
        print(json.dumps({{
            "same_pid": state["pid"] == os.getpid(),
            "child_alive": child_alive,
            "display": os.environ.get("DISPLAY"),
            "cwd": os.getcwd(),
            "orig_argv": sys.orig_argv[1:],
        }}))
    """))
    env = dict(os.environ, DISPLAY=":1")
    result = subprocess.run(
        [sys.executable, "-u", str(fake_node), "-s", "https://server", "-k", "KEY", "-n", "node_7", "-spu"],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout.strip().splitlines()[-1])
    assert os.path.realpath(report.pop("cwd")) == os.path.realpath(tmp_path)
    assert report == {
        "same_pid": True,
        "child_alive": False,
        "display": ":1",
        "orig_argv": ["-u", str(fake_node), "-n", "node_7", "-spu"],
    }
