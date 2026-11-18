"""Recovers a node that stops making progress in the middle of a test case.

Every other safeguard in the node runs on the same thread as the test case, or
only after the test case returns. So when that thread itself blocks -- outside
an action, where `action_timeout` does not reach -- nothing notices: the
process stays alive, the server shows the node online, and the run stays
"In-Progress" until a person restarts the node by hand.

This module watches from its own thread. While a test case is running it
expects regular signs of progress (every log line is one). When none arrives
for too long it:

1. writes a dump of every thread's stack, so the cause can be found,
2. records why in the "interrupted test case" file,
3. calls the handler given to `start()`, which restarts the node.

After any restart -- by this watchdog, by `kill -9`, by a reboot -- the node
finds that file on startup and reports the test case to the server as Blocked
with the reason, so the run can finish instead of waiting for a result that
will never come.

Nothing here imports from Framework, so every module can call `progress()`.
"""

import faulthandler
import json
import os
import sys
import threading
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

# Seconds without progress before a test case is considered stuck. 0 turns the
# watchdog off.
QUIET_LIMIT_ENV = "ZEUZ_NODE_WATCHDOG_SECONDS"
DEFAULT_QUIET_LIMIT = 20 * 60

# An action is allowed its own action_timeout plus this much before the
# watchdog steps in, so the action timeout always gets to act first.
ACTION_MARGIN = 5 * 60

TICK_SECONDS = 5
# How often the progress of the running test case is saved to disk.
HEARTBEAT_SECONDS = 60
# A gap this long between two ticks means the whole process (or machine) was
# suspended. That is not the test case being stuck.
SUSPEND_GAP_SECONDS = 60
# If the interpreter itself is frozen (not even this thread gets to run) for
# this long, the process dumps its stacks and exits. Linux only.
INTERPRETER_FROZEN_SECONDS = 15 * 60

KEEP_DUMPS = 20
# An interrupted test case older than this is no longer reported: its run's
# queue has expired on the server.
MARKER_MAX_AGE_SECONDS = 3 * 24 * 3600

_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

_AUTOMATION_LOG = Path(__file__).resolve().parents[2] / "AutomationLog"
MARKER_FILE = _AUTOMATION_LOG / "interrupted_test_case.json"
DUMP_DIR = _AUTOMATION_LOG / "watchdog"

_lock = threading.RLock()
_current = None  # the test case being watched (dict), or None
_last_progress = 0.0  # time.monotonic() of the last sign of progress
_last_note = ""
_windows = []  # open allow_quiet() windows
_thread = None
_stop = threading.Event()
_on_stall = None
_backstop_file = None


def _now():
    return time.monotonic()


def _utc_text(timestamp=None):
    moment = (
        datetime.now(timezone.utc)
        if timestamp is None
        else datetime.fromtimestamp(timestamp, timezone.utc)
    )
    return moment.strftime(_TIME_FORMAT)


def quiet_limit():
    """Seconds without progress that mean "stuck", or None when the watchdog is off."""
    raw = os.environ.get(QUIET_LIMIT_ENV, "").strip()
    if not raw:
        return DEFAULT_QUIET_LIMIT
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_QUIET_LIMIT
    return value if value > 0 else None


def progress(note=None):
    """Record that the test case is still moving. Cheap; call it freely."""
    global _last_progress, _last_note
    _last_progress = _now()
    if note:
        _last_note = str(note)[:300]


class allow_quiet:
    """A stretch of work that is allowed to be silent for longer than usual.

    `seconds=None` means "as long as it takes" (for work that has no time limit
    of its own, such as an action with action_timeout turned off).
    """

    def __init__(self, name, seconds):
        self.name = name
        self.seconds = seconds

    def __enter__(self):
        progress()
        with _lock:
            _windows.append(self)
        return self

    def __exit__(self, *exc_info):
        with _lock:
            try:
                _windows.remove(self)
            except ValueError:
                pass
        progress()
        return False


def allow_quiet_for_action(action_timeout):
    """The window for one action: its own timeout plus a margin."""
    if action_timeout is None or action_timeout <= 0:
        return allow_quiet("action without a time limit", None)
    return allow_quiet("action", action_timeout + ACTION_MARGIN)


def _allowed_quiet():
    """How long the current work may be silent, or None for "no limit"."""
    base = quiet_limit()
    if base is None:
        return None
    with _lock:
        windows = list(_windows)
    allowed = base
    for window in windows:
        if window.seconds is None:
            return None
        allowed = max(allowed, window.seconds)
    return allowed


def _is_debug_run(run_id):
    return str(run_id).lower().startswith("debug")


# --- the "interrupted test case" file ------------------------------------------


def _write_marker(data):
    try:
        MARKER_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = MARKER_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(tmp, MARKER_FILE)
    except Exception:
        pass


def _marker_fields(current):
    return {
        "run_id": current["run_id"],
        "testcase_no": current["testcase_no"],
        "title": current["title"],
        "node_id": current["node_id"],
        "pid": os.getpid(),
        "started_at": current["started_at"],
        "last_progress_at": _utc_text(time.time() - max(0.0, _now() - _last_progress)),
        "last_activity": _last_note,
        "reason": current.get("reason", ""),
        "stack_dump": current.get("stack_dump", ""),
    }


def _on_record(current):
    """Whether the running test case is kept on disk, to be reported if the node stops now.

    Not for debug sessions (they have no result on the server), not once the
    result has been dealt with (reporting it again would overwrite the real
    one), and not when the delivery could not even be identified.
    """
    return bool(
        not current["debug"]
        and not current.get("result_handled")
        and current["run_id"]
        and current["testcase_no"]
    )


def begin_test_case(run_id, testcase_no, title="", node_id=""):
    """Start watching a test case."""
    global _current
    current = {
        "run_id": str(run_id),
        "testcase_no": str(testcase_no),
        "title": str(title or ""),
        "node_id": str(node_id or ""),
        "started_at": _utc_text(),
        "debug": _is_debug_run(run_id),
        "stalled": False,
        "heartbeat_at": _now(),
    }
    progress("test case received")
    with _lock:
        _current = current
        del _windows[:]
    if _on_record(current):
        _write_marker(_marker_fields(current))
    else:
        clear_interrupted()


def set_test_case(testcase_no, title=""):
    """Name the test case that is running now (a delivery can hold several)."""
    with _lock:
        current = _current
        if current is None:
            return
        current["testcase_no"] = str(testcase_no)
        current["title"] = str(title or "")
        current["started_at"] = _utc_text()
    progress("test case started")
    if _on_record(current):
        _write_marker(_marker_fields(current))


def result_handled():
    """The running test case's result reached the server, was saved for a later retry, or is not expected."""
    current = _current
    if current is not None:
        current["result_handled"] = True
        # From here on a restart must not report this test case as Blocked.
        clear_interrupted()


def end_test_case(error=None):
    """Stop watching the test case.

    Returns True when it ended without a result (something failed before the
    result could be produced). It is then left on record, exactly like a test
    case the node was stopped in, so the caller can report it and the server
    is not left waiting.
    """
    global _current
    with _lock:
        current, _current = _current, None
        del _windows[:]
    _cancel_backstop()
    if current is None or not _on_record(current):
        clear_interrupted()
        return False
    reason = "ZeuZ Node could not run this test case to the end, so there is no result for it."
    if error:
        reason += " Error: %s" % str(error)[:500]
    current["reason"] = reason
    _write_marker(_marker_fields(current))
    return True


def read_interrupted():
    """The test case that was running when the node last stopped, or None."""
    try:
        data = json.loads(MARKER_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None
    if (
        not isinstance(data, dict)
        or not data.get("run_id")
        or not data.get("testcase_no")
    ):
        return None
    return data


def clear_interrupted():
    try:
        MARKER_FILE.unlink()
    except FileNotFoundError:
        pass
    except Exception:
        pass


def _parse_utc(text):
    try:
        return datetime.strptime(text, _TIME_FORMAT).replace(tzinfo=timezone.utc)
    except Exception:
        return None


def interrupted_is_too_old(marker, now=None):
    """True when the run this test case belonged to can no longer be continued."""
    started = _parse_utc(marker.get("started_at", ""))
    if started is None:
        return True
    now = datetime.now(timezone.utc) if now is None else now
    return (now - started).total_seconds() > MARKER_MAX_AGE_SECONDS


def interrupted_report(marker, now=None):
    """The execution report that tells the server what happened to the test case.

    Same shape as the report a finished test case uploads, with the one test
    case marked Blocked and the reason in `failreason`.
    """
    now = datetime.now(timezone.utc) if now is None else now
    started = _parse_utc(marker.get("started_at", "")) or now
    ended = _parse_utc(marker.get("last_progress_at", "")) or now
    if ended < started:
        ended = started
    seconds = int((ended - started).total_seconds())
    duration = "%d:%02d:%02d" % (seconds // 3600, (seconds % 3600) // 60, seconds % 60)

    reason = marker.get("reason") or (
        "ZeuZ Node stopped while this test case was running (the node process was "
        "killed or crashed, or the machine restarted), so there is no result for it."
    )
    last_activity = marker.get("last_activity")
    if last_activity:
        reason += " Last activity: %s." % last_activity
    stack_dump = marker.get("stack_dump")
    if stack_dump:
        reason += " Thread dump saved on the node: %s" % stack_dump

    return [
        {
            "run_id": marker["run_id"],
            "machine_name": marker.get("node_id", ""),
            "test_cases": [
                {
                    "testcase_no": marker["testcase_no"],
                    "title": marker.get("title", ""),
                    "execution_detail": {
                        "teststarttime": started.strftime(_TIME_FORMAT),
                        "testendtime": ended.strftime(_TIME_FORMAT),
                        "duration": duration,
                        "status": "Blocked",
                        "failreason": reason,
                    },
                    "steps": [],
                }
            ],
        }
    ]


# --- stack dumps ------------------------------------------------------------------


def write_stack_dump(header):
    """Write every thread's stack to a new file and return its path (or "")."""
    try:
        DUMP_DIR.mkdir(parents=True, exist_ok=True)
        path = DUMP_DIR / (
            "stall_%s_pid%s.txt"
            % (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"), os.getpid())
        )
        names = {thread.ident: thread for thread in threading.enumerate()}
        with open(path, "w", encoding="utf-8") as f:
            f.write(header.rstrip() + "\n\n")
            for ident, frame in sys._current_frames().items():
                thread = names.get(ident)
                label = thread.name if thread is not None else "?"
                daemon = " daemon" if thread is not None and thread.daemon else ""
                f.write('Thread %s "%s"%s\n' % (ident, label, daemon))
                f.write("".join(traceback.format_stack(frame)))
                f.write("\n")
            f.write("--- faulthandler view (most recent call first) ---\n")
            f.flush()
            faulthandler.dump_traceback(file=f, all_threads=True)
        _prune_dumps()
        return str(path)
    except Exception:
        return ""


def _prune_dumps():
    try:
        dumps = sorted(
            DUMP_DIR.glob("stall_*.txt"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        for old in dumps[KEEP_DUMPS:]:
            old.unlink()
    except Exception:
        pass


# --- frozen interpreter -------------------------------------------------------------


def _arm_backstop():
    """If this thread stops running too, dump the stacks and exit the process.

    A thread can freeze the whole interpreter by blocking inside native code
    without releasing the GIL. Nothing written in Python can react to that, so
    faulthandler's own native timer is used. Each tick pushes it forward.
    """
    global _backstop_file
    if not sys.platform.startswith("linux"):
        return
    try:
        if _backstop_file is None:
            DUMP_DIR.mkdir(parents=True, exist_ok=True)
            _backstop_file = open(
                DUMP_DIR / "interpreter_frozen.txt", "a", encoding="utf-8"
            )
        faulthandler.dump_traceback_later(
            INTERPRETER_FROZEN_SECONDS, exit=True, file=_backstop_file
        )
    except Exception:
        pass


def _cancel_backstop():
    try:
        faulthandler.cancel_dump_traceback_later()
    except Exception:
        pass


# --- the watcher ---------------------------------------------------------------------


def _long_running_mode():
    """True during load/performance testing, which is silent for long stretches by design."""
    common_util = sys.modules.get("Framework.Utilities.CommonUtil")
    if common_util is None:
        return False
    return bool(
        getattr(common_util, "load_testing", False)
        or getattr(common_util, "performance_testing", False)
    )


def check(tick_gap=0.0):
    """One look at the running test case. Returns the stall details if it just got stuck."""
    current = _current
    if current is None:
        _cancel_backstop()
        return None

    if tick_gap > SUSPEND_GAP_SECONDS:
        progress("resumed after the node process was paused for %d seconds" % tick_gap)
    if _long_running_mode():
        progress()

    _arm_backstop()

    now = _now()
    if _on_record(current) and now - current["heartbeat_at"] >= HEARTBEAT_SECONDS:
        current["heartbeat_at"] = now
        _write_marker(_marker_fields(current))

    if current["stalled"]:
        return None
    allowed = _allowed_quiet()
    if allowed is None:
        return None
    quiet = now - _last_progress
    if quiet < allowed:
        return None

    current["stalled"] = True
    return _record_stall(current, quiet)


def _record_stall(current, quiet):
    minutes = max(1, int(round(quiet / 60.0)))
    reason = (
        "ZeuZ Node stopped this test case: it made no progress for %d minute(s), "
        "so the node restarted itself to recover." % minutes
    )
    header = (
        "ZeuZ Node watchdog\nrun_id: %s\ntest case: %s %s\nno progress for: %d seconds\nlast activity: %s\npid: %s\ntime (UTC): %s"
        % (
            current["run_id"],
            current["testcase_no"],
            current["title"],
            quiet,
            _last_note,
            os.getpid(),
            _utc_text(),
        )
    )
    dump_path = write_stack_dump(header)
    current["reason"] = reason
    current["stack_dump"] = dump_path
    if _on_record(current):
        _write_marker(_marker_fields(current))
    return {
        "run_id": current["run_id"],
        "testcase_no": current["testcase_no"],
        "title": current["title"],
        "debug": current["debug"],
        "quiet_seconds": quiet,
        "last_activity": _last_note,
        "stack_dump": dump_path,
        "reason": reason,
    }


def _loop():
    last_tick = _now()
    while not _stop.wait(TICK_SECONDS):
        now = _now()
        gap, last_tick = now - last_tick, now
        try:
            stall = check(gap - TICK_SECONDS)
            if stall is not None and _on_stall is not None:
                _on_stall(stall)
        except Exception:
            # The watchdog must outlive anything that goes wrong inside it.
            try:
                traceback.print_exc()
            except Exception:
                pass


def start(on_stall):
    """Start the watcher thread (once). `on_stall(details)` is called when a test case gets stuck."""
    global _thread, _on_stall
    _on_stall = on_stall
    with _lock:
        if _thread is not None and _thread.is_alive():
            return
        _stop.clear()
        _thread = threading.Thread(target=_loop, name="zeuz_node_watchdog", daemon=True)
        _thread.start()


def stop():
    """Stop the watcher thread and wait for it to end."""
    global _thread
    with _lock:
        thread, _thread = _thread, None
    _stop.set()
    if thread is not None and thread is not threading.current_thread():
        thread.join(TICK_SECONDS + 5)
    _cancel_backstop()
