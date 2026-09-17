"""Checks for authentication cleanup, installer callbacks, and channel caching."""
import ast
import asyncio
import datetime
import threading
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from Framework.Built_In_Automation.Web.Selenium import utils
from server.installers import _maybe_await


def test_authentication_session_cleanup(tmp_path):
    # Load only the helper: importing node_cli initializes the entire node.
    source = Path(__file__).resolve().parents[1] / "node_cli.py"
    tree = ast.parse(source.read_text())
    helper = next(node for node in tree.body if getattr(node, "name", None) == "destroy_session")
    session = tmp_path / "session.bin"
    namespace = {"Path": Path, "RequestFormatter": SimpleNamespace(SESSION_FILE_NAME=session)}
    exec(compile(ast.Module(body=[helper], type_ignores=[]), str(source), "exec"), namespace)
    session.write_bytes(b"old credentials")
    assert namespace["destroy_session"]() is None
    assert not session.exists()
    assert namespace["destroy_session"]() is None


def test_installer_callbacks_execute_and_return_results():
    async def check():
        loop_thread = threading.get_ident()

        async def status(value):
            assert threading.get_ident() == loop_thread
            return value

        def synchronous(value):
            assert threading.get_ident() != loop_thread
            return value

        assert await _maybe_await(status, "async") == "async"
        assert await _maybe_await(synchronous, "sync") == "sync"
        assert await _maybe_await(lambda: status("wrapped")) == "wrapped"

    asyncio.run(check())


def test_chrome_cache_keeps_channels_separate(monkeypatch, tmp_path):
    monkeypatch.delenv("CHROME_DAYS_BEFORE_FETCH", raising=False)
    chrome = utils.ChromeForTesting.__new__(utils.ChromeForTesting)
    chrome.CHROME_BASE_DIR = tmp_path
    chrome.CHROME_INFO_FILE = tmp_path / "info.json"
    # An old cache does not identify its channel; never trust it as Stable.
    chrome._save_info({"latest": {"version": "old-beta", "last_check": datetime.date.today().isoformat()}})
    versions = {"Stable": {"version": "100"}, "Beta": {"version": "101"}}
    response = Mock()
    response.json.return_value = {"channels": versions}
    get = Mock(return_value=response)
    monkeypatch.setattr(utils.requests, "get", get)

    assert chrome.get_latest_version("Beta") == "101"
    assert chrome.get_latest_version("Stable") == "100"
    assert chrome.get_latest_version("Beta") == "101"
    assert chrome.get_latest_version("Stable") == "100"
    assert get.call_count == 2
    versions["Stable"]["version"] = "102"
    assert chrome.get_latest_version("Stable", force_check=True) == "102"
    assert chrome.get_latest_version("Beta") == "101"
    assert get.call_count == 3


def test_chrome_version_validation_and_channel_resolution(tmp_path):
    chrome = utils.ChromeForTesting.__new__(utils.ChromeForTesting)
    chrome.CHROME_VERSIONS_DIR = tmp_path
    chrome.cleanup_old_versions = Mock()
    chrome.get_latest_version = Mock(return_value="130.0.6723.1")
    chrome.is_version_installed = Mock(return_value=True)
    chrome._update_installed_version_date = Mock()
    chrome.get_chrome_binary_path = chrome.get_driver_binary_path = lambda _: tmp_path
    for version in ("99.0.0.0", "114.0.9999.0", "115.0.5762.9", "system"):
        assert chrome.setup_chrome_for_testing(version) == (None, None)
    for version in ("115.0.5763.0", "130.0.1.0"):
        assert chrome.setup_chrome_for_testing(version) == (tmp_path, tmp_path)
    assert chrome.setup_chrome_for_testing(" Beta ") == (tmp_path, tmp_path)
    chrome.get_latest_version.assert_called_once_with(channel="Beta", force_check=False)
    for version in ("bad", "130", "../../tmp", "130.0.x.0"):
        try:
            chrome.setup_chrome_for_testing(version)
        except ValueError:
            pass
        else:
            raise AssertionError(version)


def test_affine_timeout_preserves_worker_and_performance_concurrency(monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from Framework.Built_In_Automation.Sequential_Actions import sequential_actions as sa
    from Framework.Built_In_Automation.Web.Playwright import BuiltInFunctions as pw

    monkeypatch.setattr(sa, "_action_worker", None)
    monkeypatch.setattr(sa, "_get_action_timeout", lambda: 0.05)
    monkeypatch.setattr(sa, "load_testing", False)
    monkeypatch.setattr(sa.CommonUtil, "load_testing", False)
    monkeypatch.setattr(sa, "_force_kill_hung_browser_sessions", lambda: None)
    monkeypatch.setattr(sa.CommonUtil, "ExecLog", lambda *_: None)
    release = threading.Event()

    def blocked(_):
        pw._browser_state.current_driver_id = "retained"
        release.wait(5)
    blocked._zeuz_thread_affine = True
    try:
        assert sa._run_action_with_timeout(blocked, []) == "zeuz_failed"
        worker = sa._action_worker
        assert worker is not None
        release.set()
        monkeypatch.setattr(sa, "_get_action_timeout", lambda: 2)
        def resume(_):
            return pw._browser_state.current_driver_id
        resume._zeuz_thread_affine = True
        assert sa._run_action_with_timeout(resume, []) == "retained"
        assert sa._action_worker is worker
    finally:
        release.set()

    monkeypatch.setattr(sa.CommonUtil, "load_testing", True)
    barrier = threading.Barrier(2)

    def journey(value):
        caller = threading.get_ident()
        def action(_):
            pw._browser_state.current_driver_id = value
            barrier.wait(timeout=2)
            assert pw._browser_state.current_driver_id == value
            assert threading.get_ident() == caller
            return "passed"
        action._zeuz_thread_affine = True
        return sa._run_action_with_timeout(action, [])
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(journey, ("one", "two"))) == ["passed", "passed"]


def test_custom_driver_sync_and_async_steps(monkeypatch):
    from Framework import MainDriverApi as main

    monkeypatch.setattr(main.CommonUtil, "ExecLog", lambda *_: None)
    async def async_step(data, info, result_queue, debug):
        await asyncio.sleep(0)
        result_queue.put("passed")
        return "passed"
    def sync_step(data, info, result_queue, debug):
        result_queue.put("passed")
        return "passed"
    for step in (async_step, sync_step):
        monkeypatch.setattr(main.importlib, "import_module", lambda _: SimpleNamespace(step=step))
        for threaded in ("true", "false"):
            monkeypatch.setattr(main.ConfigModule, "get_config_value", lambda *_: threaded)
            assert main.call_driver_function_of_test_step(
                "test", [{"step_driver_type": "custom", "step_function": "step"}],
                1, 1, "step", [], [],
            ) == "PASSED"


def test_playwright_installer_includes_dependencies(monkeypatch):
    from Framework.install_handler.web import playwright_browsers as installer
    from unittest.mock import AsyncMock
    run = AsyncMock(return_value=(0, ""))
    monkeypatch.setattr(installer, "_run", run)
    monkeypatch.setattr(installer, "_status", AsyncMock())
    assert asyncio.run(installer.install()) is True
    run.assert_awaited_once_with("install", "--with-deps", "firefox", "webkit")


def test_existing_channel_cache_works_offline(monkeypatch):
    chrome = utils.ChromeForTesting.__new__(utils.ChromeForTesting)
    monkeypatch.delenv("CHROME_DAYS_BEFORE_FETCH", raising=False)
    monkeypatch.setattr(chrome, "_load_info", lambda: {"channels": {
        channel: {"version": version, "last_check": datetime.date.today().isoformat()}
        for channel, version in (("Stable", "100"), ("Beta", "101"))
    }})
    monkeypatch.setattr(utils.requests, "get", Mock(side_effect=AssertionError("Network used")))
    assert chrome.get_latest_version("Stable") == "100"
    assert chrome.get_latest_version("Beta") == "101"


def test_execute_python_sync_and_top_level_await(monkeypatch):
    from Framework.Built_In_Automation.Sequential_Actions import common_functions as common

    namespace = {}
    monkeypatch.setattr(common.sr, "shared_variables", namespace)
    monkeypatch.setattr(common.CommonUtil, "ExecLog", lambda *_args, **_kwargs: None)
    for code in ("answer = 41", "import asyncio\nawait asyncio.sleep(0)\nanswer += 1"):
        assert common.execute_python_code([("execute python code", "action", code)]) == "passed"
    assert namespace["answer"] == 42
    assert common.execute_python_code([("execute python code", "action", "await missing()")]) == "zeuz_failed"


def test_debug_extensions_and_active_cdp_port(monkeypatch):
    from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr
    monkeypatch.setitem(sr.shared_variables, "dependency", {"Browser": "Chrome"})
    from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as selenium
    from playwright import sync_api

    monkeypatch.setattr(selenium.CommonUtil, "debug_status", True)
    monkeypatch.setattr(selenium.ConfigModule, "get_config_value", lambda *_: "true")
    monkeypatch.setattr(selenium, "set_extension_variables", lambda: None)
    for browser, engine in (("chrome", "chrome"), ("microsoft edge chromium", "edge")):
        options = selenium.generate_options(browser, {"capabilities": {}, engine: {
            "add_argument": [], "add_experimental_option": {},
            "add_extension": [], "add_encoded_extension": [],
        }})
        assert f"--load-extension={selenium.aiplugin_path},{selenium.ai_recorder_path}" in options.arguments

    driver = SimpleNamespace(capabilities={"goog:chromeOptions": {"debuggerAddress": "localhost:32123"}})
    monkeypatch.setattr(selenium, "selenium_driver", driver)
    monkeypatch.setattr(selenium, "current_driver_id", "active")
    monkeypatch.setattr(selenium, "selenium_details", {"active": {"driver": driver}})
    page = SimpleNamespace(wait_for_event=Mock())
    connect = Mock(return_value=SimpleNamespace(contexts=[SimpleNamespace(pages=[page])]))
    manager = Mock()
    manager.__enter__ = Mock(return_value=SimpleNamespace(chromium=SimpleNamespace(connect_over_cdp=connect)))
    manager.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(sync_api, "sync_playwright", lambda: manager)
    assert selenium.playwright([]) == "passed"
    connect.assert_called_once_with("http://localhost:32123")


def test_delayed_and_cached_alert_rows(monkeypatch):
    from Framework.Built_In_Automation.Web.Playwright import BuiltInFunctions as pw
    from playwright.sync_api import TimeoutError

    state, saved = {}, {}
    rows = [("handle alert", "action", "accept"),
            ("prompt text", "input parameter", "answer"),
            ("message", "save parameter", ""), ("wait", "optional parameter", "0.25")]
    dialog = SimpleNamespace(message="question", type="prompt", accept=Mock(), dismiss=Mock())
    def wait(event, timeout):
        assert (event, timeout) == ("dialog", 250)
        pw._on_dialog(state, dialog)
    monkeypatch.setattr(pw, "_state", lambda: state)
    monkeypatch.setattr(pw, "get_page", lambda: SimpleNamespace(wait_for_event=wait))
    monkeypatch.setattr(pw.sr, "Set_Shared_Variables", lambda name, value: saved.update({name: value}))
    assert pw.Handle_Browser_Alert(rows) == "passed"
    dialog.accept.assert_called_once_with("answer")
    assert saved == {"message": "question"}
    assert state == {}
    monkeypatch.setattr(pw.CommonUtil, "current_action_no", "1")
    monkeypatch.setattr(pw.sr, "Get_Shared_Variables", lambda *_args, **_kwargs: [[], rows])
    pw._on_dialog(state, dialog)
    assert pw.Handle_Browser_Alert(rows) == "passed"
    assert dialog.accept.call_count == 2
    monkeypatch.setattr(pw, "get_page", lambda: SimpleNamespace(wait_for_event=Mock(side_effect=TimeoutError("timeout"))))
    assert pw.Handle_Browser_Alert(rows) == "zeuz_failed"
    assert state == {}
