import asyncio
import inspect
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from Framework.Utilities import decorators


def test_logger_awaits_async_function_before_exit_log(monkeypatch):
    logs = []

    def fake_exec_log(module_info, message, level):
        logs.append(message)

    monkeypatch.setattr(decorators.CommonUtil, "ExecLog", fake_exec_log)

    @decorators.logger
    async def async_action(data_set):
        decorators.CommonUtil.ExecLog(None, "Async action body log", 1)
        await asyncio.sleep(0)
        return "passed"

    assert inspect.iscoroutinefunction(async_action)

    result = asyncio.run(async_action([]))

    assert result == "passed"
    assert logs[0] == "Entering into function: 'async_action'."
    assert logs[1] == "Async action body log"
    assert logs[2].startswith("Exited from function: 'async_action'. Runtime:")


def test_logger_preserves_sync_function_behavior(monkeypatch):
    logs = []

    def fake_exec_log(module_info, message, level):
        logs.append(message)

    monkeypatch.setattr(decorators.CommonUtil, "ExecLog", fake_exec_log)

    @decorators.logger
    def sync_action(data_set):
        decorators.CommonUtil.ExecLog(None, "Sync action body log", 1)
        return "passed"

    assert not inspect.iscoroutinefunction(sync_action)

    result = sync_action([])

    assert result == "passed"
    assert logs[0] == "Entering into function: 'sync_action'."
    assert logs[1] == "Sync action body log"
    assert logs[2].startswith("Exited from function: 'sync_action'. Runtime:")


def test_logger_preserves_custom_fail_message_for_async_function(monkeypatch):
    logs = []

    def fake_exec_log(module_info, message, level):
        logs.append((message, level))

    monkeypatch.setattr(decorators.CommonUtil, "ExecLog", fake_exec_log)

    @decorators.logger
    async def async_action(data_set):
        return "zeuz_failed"

    result = asyncio.run(
        async_action(
            [
                ("click", "playwright action", "click"),
                ("fail message", "failmessage", "Custom failure"),
            ]
        )
    )

    assert result == "zeuz_failed"
    assert logs[0] == ("Entering into function: 'async_action'.", 5)
    assert logs[1] == ("Custom failure", 3)
    assert logs[2][0].startswith("Exited from function: 'async_action'. Runtime:")
    assert logs[2][1] == 5
