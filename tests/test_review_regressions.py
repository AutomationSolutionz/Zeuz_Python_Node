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
