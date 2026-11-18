"""Tests for the watchdog that recovers a node stuck in the middle of a test case."""

import json
import threading
from datetime import datetime, timedelta, timezone

import pytest

from Framework.Utilities import node_watchdog

RUN_ID = "Tue-Nov-17-07:05:02-2026"
TC = "TEST-1730"


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock(monkeypatch, tmp_path):
    """A watchdog with a controllable clock, writing into a temp folder, with nothing left running."""
    clock = Clock()
    monkeypatch.setattr(node_watchdog, "_now", clock)
    monkeypatch.setattr(
        node_watchdog, "MARKER_FILE", tmp_path / "interrupted_test_case.json"
    )
    monkeypatch.setattr(node_watchdog, "DUMP_DIR", tmp_path / "watchdog")
    # The native "interpreter frozen" timer would outlive the test.
    monkeypatch.setattr(node_watchdog, "_arm_backstop", lambda: None)
    monkeypatch.setattr(node_watchdog, "_long_running_mode", lambda: False)
    monkeypatch.delenv(node_watchdog.QUIET_LIMIT_ENV, raising=False)
    yield clock
    node_watchdog.end_test_case()


def marker():
    return json.loads(node_watchdog.MARKER_FILE.read_text())


# --- when is a test case "stuck" ---------------------------------------------------


def test_nothing_is_watched_while_idle(clock):
    clock.advance(10 * node_watchdog.DEFAULT_QUIET_LIMIT)
    assert node_watchdog.check() is None
    assert not node_watchdog.MARKER_FILE.exists()


def test_progress_keeps_a_test_case_alive(clock):
    node_watchdog.begin_test_case(RUN_ID, TC, "Login", "node_2")
    for _ in range(20):
        clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT - 1)
        assert node_watchdog.check() is None
        node_watchdog.progress("still working")


def test_no_progress_for_the_limit_is_a_stall(clock):
    node_watchdog.begin_test_case(RUN_ID, TC, "Login", "node_2")
    node_watchdog.progress("Enter_Text_In_Text_Box : Selenium")

    clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT - 1)
    assert node_watchdog.check() is None

    clock.advance(1)
    stall = node_watchdog.check()

    assert stall["run_id"] == RUN_ID
    assert stall["testcase_no"] == TC
    assert stall["debug"] is False
    assert stall["quiet_seconds"] == node_watchdog.DEFAULT_QUIET_LIMIT
    assert stall["last_activity"] == "Enter_Text_In_Text_Box : Selenium"
    assert "no progress for 20 minute(s)" in stall["reason"]


def test_a_stall_is_reported_once(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT)
    assert node_watchdog.check() is not None
    clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT)
    assert node_watchdog.check() is None


def test_the_next_test_case_is_watched_again(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT)
    assert node_watchdog.check() is not None
    node_watchdog.end_test_case()

    node_watchdog.begin_test_case(RUN_ID, "TEST-1731")
    clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT)
    assert node_watchdog.check()["testcase_no"] == "TEST-1731"


def test_finishing_a_test_case_stops_the_watch(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    node_watchdog.end_test_case()
    clock.advance(10 * node_watchdog.DEFAULT_QUIET_LIMIT)
    assert node_watchdog.check() is None


@pytest.mark.parametrize(
    "value, expected",
    [
        ("", node_watchdog.DEFAULT_QUIET_LIMIT),
        ("90", 90.0),
        ("0", None),
        ("-5", None),
        ("soon", node_watchdog.DEFAULT_QUIET_LIMIT),
    ],
)
def test_quiet_limit_setting(clock, monkeypatch, value, expected):
    monkeypatch.setenv(node_watchdog.QUIET_LIMIT_ENV, value)
    assert node_watchdog.quiet_limit() == expected


def test_turned_off_never_reports_a_stall(clock, monkeypatch):
    monkeypatch.setenv(node_watchdog.QUIET_LIMIT_ENV, "0")
    node_watchdog.begin_test_case(RUN_ID, TC)
    clock.advance(100 * node_watchdog.DEFAULT_QUIET_LIMIT)
    assert node_watchdog.check() is None


# --- work that is allowed to be silent for longer -------------------------------


def test_an_action_gets_its_own_timeout_plus_a_margin(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    action_timeout = 1800  # the default, longer than the watchdog's own limit
    with node_watchdog.allow_quiet_for_action(action_timeout):
        clock.advance(action_timeout + node_watchdog.ACTION_MARGIN - 1)
        assert node_watchdog.check() is None  # the action timeout gets to act first
        clock.advance(1)
        assert node_watchdog.check() is not None  # the action never came back at all


def test_a_short_action_timeout_does_not_shorten_the_limit(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    with node_watchdog.allow_quiet_for_action(20):
        clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT - 1)
        assert node_watchdog.check() is None
        clock.advance(1)
        assert node_watchdog.check() is not None


@pytest.mark.parametrize("no_limit", [None, 0, -1])
def test_an_action_without_a_time_limit_is_never_a_stall(clock, no_limit):
    node_watchdog.begin_test_case(RUN_ID, TC)
    with node_watchdog.allow_quiet_for_action(no_limit):
        clock.advance(100 * node_watchdog.DEFAULT_QUIET_LIMIT)
        assert node_watchdog.check() is None


def test_leaving_a_quiet_window_counts_as_progress_and_restores_the_limit(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    with node_watchdog.allow_quiet("uploading", 7200):
        clock.advance(7000)
        assert node_watchdog.check() is None
    clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT - 1)
    assert node_watchdog.check() is None
    clock.advance(1)
    assert node_watchdog.check() is not None


def test_nested_windows_use_the_longest(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    with node_watchdog.allow_quiet("outer", 5000):
        with node_watchdog.allow_quiet("inner", 2000):
            clock.advance(4999)
            assert node_watchdog.check() is None
        clock.advance(4999)
        assert node_watchdog.check() is None
        clock.advance(1)
        assert node_watchdog.check() is not None


def test_a_window_left_open_by_an_abandoned_thread_ends_with_the_test_case(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    node_watchdog.allow_quiet("abandoned action", None).__enter__()
    node_watchdog.end_test_case()

    node_watchdog.begin_test_case(RUN_ID, "TEST-1731")
    clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT)
    assert node_watchdog.check() is not None


def test_windows_can_be_closed_from_another_thread(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    window = node_watchdog.allow_quiet("action", None)
    window.__enter__()
    closer = threading.Thread(target=window.__exit__, args=(None, None, None))
    closer.start()
    closer.join()
    clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT)
    assert node_watchdog.check() is not None


def test_load_and_performance_testing_is_never_a_stall(clock, monkeypatch):
    monkeypatch.setattr(node_watchdog, "_long_running_mode", lambda: True)
    node_watchdog.begin_test_case(RUN_ID, TC)
    for _ in range(5):
        clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT)
        assert node_watchdog.check() is None


def test_a_suspended_process_is_not_a_stall(clock):
    """The machine slept (or the process was paused) for an hour: give the test case a fresh window."""
    node_watchdog.begin_test_case(RUN_ID, TC)
    clock.advance(3600)
    assert node_watchdog.check(tick_gap=3600) is None
    clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT - 1)
    assert node_watchdog.check() is None
    clock.advance(1)
    assert node_watchdog.check() is not None


# --- the "interrupted test case" file -------------------------------------------


def test_a_running_test_case_is_recorded_on_disk(clock):
    node_watchdog.begin_test_case(RUN_ID, TC, "Login", "admin_node_2")
    data = marker()
    assert data["run_id"] == RUN_ID
    assert data["testcase_no"] == TC
    assert data["title"] == "Login"
    assert data["node_id"] == "admin_node_2"
    assert data["reason"] == ""


def test_the_record_is_removed_when_the_test_case_finishes(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    node_watchdog.result_handled()
    node_watchdog.end_test_case()
    assert node_watchdog.read_interrupted() is None


def test_the_record_follows_the_test_case_that_is_actually_running(clock):
    node_watchdog.begin_test_case(RUN_ID, TC, "first")
    node_watchdog.set_test_case("TEST-1731", "second")
    data = marker()
    assert (data["testcase_no"], data["title"]) == ("TEST-1731", "second")


def test_set_test_case_without_a_running_one_does_nothing(clock):
    node_watchdog.set_test_case(TC, "title")
    assert not node_watchdog.MARKER_FILE.exists()


def test_a_stall_adds_the_reason_and_the_dump_to_the_record(clock):
    node_watchdog.begin_test_case(RUN_ID, TC, "Login", "admin_node_2")
    node_watchdog.progress("upload_step_report : MainDriverApi")
    clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT)
    stall = node_watchdog.check()

    data = marker()
    assert "no progress for 20 minute(s)" in data["reason"]
    assert data["last_activity"] == "upload_step_report : MainDriverApi"
    assert data["stack_dump"] == stall["stack_dump"]


def test_the_record_is_refreshed_while_the_test_case_runs(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    first = marker()["last_activity"]
    node_watchdog.progress("step 2")
    clock.advance(node_watchdog.HEARTBEAT_SECONDS)
    node_watchdog.check()
    assert first != "step 2"
    assert marker()["last_activity"] == "step 2"


def test_a_test_case_that_ends_with_its_result_handled_leaves_no_record(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    node_watchdog.result_handled()
    assert node_watchdog.end_test_case() is False
    assert node_watchdog.read_interrupted() is None


def test_a_test_case_that_ends_without_a_result_stays_on_record(clock):
    node_watchdog.begin_test_case(RUN_ID, TC, "Login", "admin_node_2")

    assert node_watchdog.end_test_case() is True

    record = node_watchdog.read_interrupted()
    assert record["testcase_no"] == TC
    assert "could not run this test case to the end" in record["reason"]
    detail = node_watchdog.interrupted_report(record)[0]["test_cases"][0][
        "execution_detail"
    ]
    assert detail["status"] == "Blocked"


def test_the_error_that_stopped_a_test_case_is_part_of_the_reason(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)

    assert (
        node_watchdog.end_test_case("TypeError: 'NoneType' object is not subscriptable")
        is True
    )

    assert (
        "TypeError: 'NoneType' object is not subscriptable"
        in node_watchdog.read_interrupted()["reason"]
    )


def test_a_very_long_error_is_cut(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    node_watchdog.end_test_case("x" * 5000)
    assert len(node_watchdog.read_interrupted()["reason"]) < 700


def test_a_result_handled_before_the_error_wins(clock):
    """The result was uploaded and something failed afterwards: the real result stays."""
    node_watchdog.begin_test_case(RUN_ID, TC)
    node_watchdog.result_handled()
    assert node_watchdog.end_test_case("RuntimeError: cleanup failed") is False
    assert node_watchdog.read_interrupted() is None


def test_result_handled_without_a_running_test_case_does_nothing(clock):
    node_watchdog.result_handled()
    assert node_watchdog.end_test_case() is False


def test_ending_twice_reports_once(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    assert node_watchdog.end_test_case() is True
    node_watchdog.clear_interrupted()
    assert node_watchdog.end_test_case() is False


def test_once_the_result_is_handled_a_restart_reports_nothing(clock):
    """The result is on the server; a freeze during cleanup must not replace it with Blocked."""
    node_watchdog.begin_test_case(RUN_ID, TC)
    node_watchdog.result_handled()
    assert node_watchdog.read_interrupted() is None

    clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT)
    stall = node_watchdog.check()

    assert stall is not None  # the node is still recovered...
    assert stall["stack_dump"]
    assert (
        node_watchdog.read_interrupted() is None
    )  # ...but nothing is reported afterwards


def test_a_delivery_that_could_not_be_identified_leaves_no_record(clock):
    node_watchdog.begin_test_case("", "")
    assert not node_watchdog.MARKER_FILE.exists()
    assert node_watchdog.end_test_case("JSONDecodeError: bad delivery") is False
    assert not node_watchdog.MARKER_FILE.exists()


def test_a_new_test_case_replaces_an_old_record(clock):
    node_watchdog.begin_test_case(RUN_ID, TC)
    node_watchdog.begin_test_case("", "")
    assert node_watchdog.read_interrupted() is None


def test_debug_sessions_leave_no_record(clock):
    node_watchdog.begin_test_case("debug_admin_node_2_xyz", TC)
    assert not node_watchdog.MARKER_FILE.exists()
    clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT)
    stall = node_watchdog.check()
    assert stall["debug"] is True
    assert not node_watchdog.MARKER_FILE.exists()
    # ...and a debug session that ends without a result is not reported either.
    assert node_watchdog.end_test_case("RuntimeError: boom") is False
    assert not node_watchdog.MARKER_FILE.exists()


@pytest.mark.parametrize(
    "content",
    ["", "not json", "[]", "{}", '{"run_id": "x"}', '{"testcase_no": "TEST-1"}'],
)
def test_an_unreadable_record_is_ignored(clock, content):
    node_watchdog.MARKER_FILE.write_text(content)
    assert node_watchdog.read_interrupted() is None


def test_clearing_a_record_that_is_not_there_is_fine(clock):
    node_watchdog.clear_interrupted()
    node_watchdog.clear_interrupted()


# --- the stack dump -----------------------------------------------------------------


def test_the_dump_names_every_thread_and_where_it_is(clock):
    release = threading.Event()

    def stuck_in_here():
        release.wait(30)

    thread = threading.Thread(
        target=stuck_in_here, name="zeuz_stuck_example", daemon=True
    )
    thread.start()
    try:
        node_watchdog.begin_test_case(RUN_ID, TC, "Login")
        clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT)
        stall = node_watchdog.check()
    finally:
        release.set()
        thread.join()

    text = open(stall["stack_dump"]).read()
    assert RUN_ID in text and TC in text
    assert '"zeuz_stuck_example"' in text
    assert "stuck_in_here" in text
    assert "MainThread" in text


def test_old_dumps_are_removed(clock, monkeypatch):
    monkeypatch.setattr(node_watchdog, "KEEP_DUMPS", 3)
    node_watchdog.DUMP_DIR.mkdir(parents=True)
    for i in range(6):
        (node_watchdog.DUMP_DIR / f"stall_old_{i}.txt").write_text("x")
    node_watchdog.write_stack_dump("header")
    assert len(list(node_watchdog.DUMP_DIR.glob("stall_*.txt"))) == 3


def test_a_dump_that_cannot_be_written_does_not_stop_the_recovery(
    clock, monkeypatch, tmp_path
):
    blocker = tmp_path / "not_a_folder"
    blocker.write_text("x")
    monkeypatch.setattr(node_watchdog, "DUMP_DIR", blocker / "watchdog")
    node_watchdog.begin_test_case(RUN_ID, TC)
    clock.advance(node_watchdog.DEFAULT_QUIET_LIMIT)
    stall = node_watchdog.check()
    assert stall is not None
    assert stall["stack_dump"] == ""


# --- what the server is told -------------------------------------------------------


def test_report_for_a_test_case_the_watchdog_stopped():
    record = {
        "run_id": RUN_ID,
        "testcase_no": TC,
        "title": "Login",
        "node_id": "admin_node_2",
        "started_at": "2026-11-17 13:34:18",
        "last_progress_at": "2026-11-17 13:34:40",
        "last_activity": "Enter_Text_In_Text_Box : Selenium",
        "reason": "ZeuZ Node stopped this test case: it made no progress for 20 minute(s), so the node restarted itself to recover.",
        "stack_dump": "/node/AutomationLog/watchdog/stall_x.txt",
    }

    report = node_watchdog.interrupted_report(record)

    assert len(report) == 1
    assert report[0]["run_id"] == RUN_ID
    assert report[0]["machine_name"] == "admin_node_2"
    test_case = report[0]["test_cases"][0]
    assert test_case["testcase_no"] == TC
    assert test_case["steps"] == []
    detail = test_case["execution_detail"]
    assert detail["status"] == "Blocked"
    assert detail["teststarttime"] == "2026-11-17 13:34:18"
    assert detail["testendtime"] == "2026-11-17 13:34:40"
    assert detail["duration"] == "0:00:22"
    assert "no progress for 20 minute(s)" in detail["failreason"]
    assert "Enter_Text_In_Text_Box : Selenium" in detail["failreason"]
    assert "stall_x.txt" in detail["failreason"]
    json.dumps(report)  # must be serialisable as it is


def test_report_for_a_node_that_was_killed():
    record = {
        "run_id": RUN_ID,
        "testcase_no": TC,
        "started_at": "2026-11-17 13:34:18",
        "last_progress_at": "2026-11-17 15:40:00",
    }

    detail = node_watchdog.interrupted_report(record)[0]["test_cases"][0][
        "execution_detail"
    ]

    assert detail["status"] == "Blocked"
    assert detail["duration"] == "2:05:42"
    assert "killed or crashed, or the machine restarted" in detail["failreason"]


def test_report_survives_missing_or_broken_times():
    now = datetime(2026, 11, 18, 9, 0, 0, tzinfo=timezone.utc)
    record = {
        "run_id": RUN_ID,
        "testcase_no": TC,
        "started_at": "garbage",
        "last_progress_at": "",
    }

    detail = node_watchdog.interrupted_report(record, now=now)[0]["test_cases"][0][
        "execution_detail"
    ]

    assert detail["teststarttime"] == "2026-11-18 09:00:00"
    assert detail["testendtime"] == "2026-11-18 09:00:00"
    assert detail["duration"] == "0:00:00"


def test_report_never_ends_before_it_started():
    record = {
        "run_id": RUN_ID,
        "testcase_no": TC,
        "started_at": "2026-11-17 13:34:18",
        "last_progress_at": "2026-11-17 13:00:00",
    }

    detail = node_watchdog.interrupted_report(record)[0]["test_cases"][0][
        "execution_detail"
    ]

    assert detail["testendtime"] == detail["teststarttime"]
    assert detail["duration"] == "0:00:00"


def test_only_a_recent_interruption_is_reported():
    now = datetime(2026, 11, 18, 9, 0, 0, tzinfo=timezone.utc)
    fresh = {"started_at": (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")}
    stale = {"started_at": (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")}

    assert node_watchdog.interrupted_is_too_old(fresh, now) is False
    assert node_watchdog.interrupted_is_too_old(stale, now) is True
    assert node_watchdog.interrupted_is_too_old({"started_at": "garbage"}, now) is True
    assert node_watchdog.interrupted_is_too_old({}, now) is True


# --- the watcher thread --------------------------------------------------------------


def test_the_thread_calls_the_handler_when_a_test_case_gets_stuck(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        node_watchdog, "MARKER_FILE", tmp_path / "interrupted_test_case.json"
    )
    monkeypatch.setattr(node_watchdog, "DUMP_DIR", tmp_path / "watchdog")
    monkeypatch.setattr(node_watchdog, "_arm_backstop", lambda: None)
    monkeypatch.setattr(node_watchdog, "TICK_SECONDS", 0.05)
    monkeypatch.setenv(node_watchdog.QUIET_LIMIT_ENV, "0.2")
    stalls = []
    called = threading.Event()

    def handler(stall):
        stalls.append(stall)
        called.set()

    try:
        node_watchdog.start(handler)
        node_watchdog.begin_test_case(RUN_ID, TC, "Login", "admin_node_2")
        assert called.wait(10), "the watchdog never reported the stuck test case"
    finally:
        node_watchdog.stop()
        node_watchdog.end_test_case()

    assert stalls[0]["testcase_no"] == TC
    assert stalls[0]["stack_dump"]


def test_a_failing_handler_does_not_kill_the_thread(monkeypatch, tmp_path):
    monkeypatch.setattr(
        node_watchdog, "MARKER_FILE", tmp_path / "interrupted_test_case.json"
    )
    monkeypatch.setattr(node_watchdog, "DUMP_DIR", tmp_path / "watchdog")
    monkeypatch.setattr(node_watchdog, "_arm_backstop", lambda: None)
    monkeypatch.setattr(node_watchdog, "TICK_SECONDS", 0.05)
    monkeypatch.setenv(node_watchdog.QUIET_LIMIT_ENV, "0.2")
    calls = []
    second = threading.Event()

    def handler(stall):
        calls.append(stall["testcase_no"])
        if len(calls) == 1:
            raise RuntimeError("restart failed")
        second.set()

    try:
        node_watchdog.start(handler)
        node_watchdog.begin_test_case(RUN_ID, TC)
        deadline = threading.Event()
        while not calls and not deadline.wait(0.05):
            pass
        node_watchdog.end_test_case()
        node_watchdog.begin_test_case(RUN_ID, "TEST-1731")
        assert second.wait(10), "the watchdog stopped after its handler raised"
    finally:
        node_watchdog.stop()
        node_watchdog.end_test_case()

    assert calls == [TC, "TEST-1731"]
