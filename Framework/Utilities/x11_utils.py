"""X11 helpers that keep a broken X connection from hanging or starving the node.

pyautogui (built on python3-xlib) keeps one X connection per process, to the
display that was current when it was first imported. Two problems made that
connection able to hang a node for days:

1. python3-xlib uses no-op locks unless ``Xlib.threaded`` is imported, so a
   thread waiting for another thread's X reply busy-spins instead of waiting.
   ``enable_xlib_threading()`` switches it to real locks.

2. When the X server behind the connection goes away (for example the node's
   own Xvfb is stopped at teardown), python3-xlib 0.15 hits a bug on the next
   request (``'BrokenPipeError' object is not subscriptable``) that leaves the
   connection marked busy, and every later request waits forever.
   ``ensure_pyautogui_display()`` runs before each action and keeps pyautogui
   on the node's current DISPLAY, or makes its calls fail fast when there is
   no working display.
   ``recover_x11_for_hung_thread()`` does the same for an action that timed
   out inside an X call.

This module also records the Xvfb processes the node starts, so ones left
behind by a crashed or killed node process can be cleaned up on the next start.
"""

import importlib
import json
import os
import socket
import sys
import threading
from pathlib import Path

_IS_LINUX = sys.platform.startswith("linux")

_CONNECT_TIMEOUT = 5  # seconds to wait for a new X connection

_rebind_lock = threading.Lock()
_connect_helper = None  # the last connection attempt, which may still be waiting
_failed_rebind = None  # (dead connection, DISPLAY, timed out) of the last failed attempt

_XVFB_REGISTRY = Path(__file__).resolve().parents[2] / "AutomationLog" / "xvfb_processes.json"
_xvfb_registry_lock = threading.Lock()


def enable_xlib_threading():
    """Make python3-xlib thread-safe. Returns True if enabled.

    Must run before any Xlib Display is created (i.e. before pyautogui is
    imported); displays created earlier keep their no-op locks.
    """
    if not _IS_LINUX:
        return False
    try:
        import Xlib.threaded  # noqa: F401  (swaps in real locks on import)
        return True
    except Exception:
        return False


def _pyautogui_x11():
    return sys.modules.get("pyautogui._pyautogui_x11")


def _pyautogui_connection():
    """The protocol-level Xlib display pyautogui is using, or None."""
    return getattr(getattr(_pyautogui_x11(), "_display", None), "display", None)


def _connection_alive(conn):
    """True unless the connection is closed or its X server has gone away.

    Peeks at the socket without blocking and without consuming anything.
    """
    if getattr(conn, "socket_error", None) is not None:
        return False
    try:
        data = conn.socket.recv(1, socket.MSG_PEEK | socket.MSG_DONTWAIT)
    except (BlockingIOError, InterruptedError):
        return True  # open, nothing to read
    except Exception:
        return False
    return data != b""  # b"" means the server closed the connection


def _abandon_connection(conn):
    """Make calls on `conn` fail instead of waiting on it forever.

    Shutting the socket down wakes a thread blocked reading it; the socket is
    not closed, because closing a descriptor another thread is using is unsafe.
    New requests on it raise ConnectionClosedError right away.
    """
    try:
        conn.socket.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass
    if getattr(conn, "socket_error", None) is None:
        try:
            from Xlib import error as xlib_error
            conn.socket_error = xlib_error.ConnectionClosedError("X server connection was abandoned")
        except Exception:
            pass


def _run_with_timeout(fn):
    """Run fn() on a helper thread; returns (finished, result or exception).

    Connecting to a frozen X server blocks forever, and the caller must not
    block with it, so the caller stops waiting after _CONNECT_TIMEOUT. fn
    itself decides what happens if it finishes later. Only one attempt runs at
    a time, so a frozen server cannot pile up waiting threads.
    """
    global _connect_helper
    if _connect_helper is not None and _connect_helper.is_alive():
        return False, TimeoutError("an earlier connection attempt is still waiting for the X server")
    outcome = {}

    def target():
        try:
            outcome["result"] = fn()
        except Exception as e:
            outcome["error"] = e

    helper = threading.Thread(target=target, name="zeuz_x11_connect", daemon=True)
    _connect_helper = helper
    helper.start()
    helper.join(_CONNECT_TIMEOUT)
    if helper.is_alive():
        return False, TimeoutError("no answer within %s seconds" % _CONNECT_TIMEOUT)
    if "error" in outcome:
        return False, outcome["error"]
    return True, outcome.get("result")


def _reconnect_pyautogui_to(display_name):
    """Give pyautogui a new connection to the same display (same key mapping)."""
    x11 = _pyautogui_x11()
    commit = threading.Lock()
    state = {"gave_up": False}

    def connect():
        from Xlib.display import Display
        new_display = Display(display_name)
        with commit:
            if state["gave_up"]:
                new_display.close()
            else:
                x11._display = new_display

    finished, error = _run_with_timeout(connect)
    with commit:
        state["gave_up"] = not finished
    return finished, error


def _rebind_pyautogui_to_current_display():
    """Reload pyautogui's X11 backend so it connects to the current DISPLAY.

    Reloading (rather than swapping the connection) also rebuilds pyautogui's
    key mapping for that display. If DISPLAY is unset or unreachable, the
    backend keeps its old, abandoned connection, so its calls fail fast. A
    reload still connecting after the timeout completes on its own later.
    """
    finished, error = _run_with_timeout(lambda: importlib.reload(_pyautogui_x11()))
    return finished, error


def _display_name(conn):
    return getattr(conn, "display_name", "?")


def _same_display(name_a, name_b):
    """True if two DISPLAY names refer to the same X server (":1" == ":1.0")."""
    try:
        from Xlib.support import connect
        _, host_a, number_a, _ = connect.get_display(name_a)
        _, host_b, number_b, _ = connect.get_display(name_b)
        return (host_a, number_a) == (host_b, number_b)
    except Exception:
        return name_a == name_b


def ensure_pyautogui_display():
    """Before an action: keep pyautogui on the node's current X display.

    pyautogui connects once, to the DISPLAY current when it was imported. The
    node changes DISPLAY when it starts and stops Xvfb for headless browsers,
    so without this pyautogui would keep using an old display, and once that
    Xvfb is stopped every desktop action would hang. So when DISPLAY points to
    a different display, or pyautogui's X server is gone, pyautogui is
    reconnected to the current DISPLAY. If it cannot be (DISPLAY unset or not
    answering), a dead connection is closed so desktop actions fail fast.

    Cheap when there is nothing to do (a dict lookup when pyautogui is not
    loaded, one non-blocking socket peek and a name comparison when it is). A
    failure is reported once, and retried only when DISPLAY changes or, if the
    X server did not answer, once that earlier attempt has ended. Returns log
    messages as (text, log level) pairs.
    """
    global _failed_rebind
    if not _IS_LINUX:
        return []
    conn = _pyautogui_connection()
    if conn is None:
        return []
    target = os.environ.get("DISPLAY")
    alive = _connection_alive(conn)
    if alive and (not target or _same_display(_display_name(conn), target)):
        return []
    if _failed_rebind is not None and _failed_rebind[:2] == (conn, target):
        still_waiting = _connect_helper is not None and _connect_helper.is_alive()
        if not _failed_rebind[2] or still_waiting:
            return []  # already reported; nothing new to try yet
    if not _rebind_lock.acquire(blocking=False):
        return []  # another thread is already rebinding
    try:
        if _pyautogui_connection() is not conn:
            return []
        old_name = _display_name(conn)
        if not alive:
            _abandon_connection(conn)
        finished, error = _rebind_pyautogui_to_current_display()
        new_conn = _pyautogui_connection()
        if finished and new_conn is not conn and new_conn is not None:
            _failed_rebind = None
            why = "switched to" if alive else "is no longer available; reconnected to"
            return [(
                "Desktop automation display '%s' %s the current display '%s'."
                % (old_name, why, _display_name(new_conn)),
                1,
            )]
        _failed_rebind = (conn, target, isinstance(error, TimeoutError))
        if alive:
            return [(
                "Could not switch desktop automation from display '%s' to '%s': %s. "
                "Desktop actions still use '%s'." % (old_name, target, error, old_name),
                2,
            )]
        reason = (
            "DISPLAY is not set" if not target
            else "could not connect to '%s': %s" % (target, error)
        )
        return [(
            "Desktop automation's X display '%s' is no longer available, and %s. "
            "Desktop actions will fail until an X display is available." % (old_name, reason),
            2,
        )]
    except Exception as e:
        return [("Could not check the desktop automation X display: %s" % e, 2)]
    finally:
        _rebind_lock.release()


def _connections_used_by_thread(thread):
    """Return the protocol-level Xlib displays `thread` is currently inside."""
    try:
        from Xlib import display as xlib_display
        from Xlib.protocol import display as protocol_display
    except Exception:
        return []

    frame = sys._current_frames().get(thread.ident)
    found = []
    while frame is not None:
        obj = frame.f_locals.get("self")
        if isinstance(obj, xlib_display.Display):
            obj = obj.display
        elif obj is not None and type(obj).__module__.startswith("Xlib."):
            # Reply objects (Xlib.protocol.rq) keep their display in `_display`
            obj = getattr(obj, "_display", None)
        if isinstance(obj, protocol_display.Display) and all(obj is not d for d in found):
            found.append(obj)
        frame = frame.f_back
    return found


def recover_x11_for_hung_thread(thread):
    """After an action timed out: free it if it is stuck in an X11 call.

    Abandons every X connection the thread is inside, so its pending call can
    end and new calls on it fail fast. If pyautogui was using that connection,
    pyautogui gets a new one: to the same display if that X server still
    answers, otherwise to the current DISPLAY. Returns log messages as
    (text, log level) pairs.
    """
    messages = []
    if not _IS_LINUX or thread is None or not thread.is_alive():
        return messages
    try:
        for conn in _connections_used_by_thread(thread):
            name = _display_name(conn)
            _abandon_connection(conn)
            messages.append((
                "The timed-out action was stuck in an X11 call on display '%s'. "
                "Closed that connection so the call can end." % name,
                2,
            ))
            if _pyautogui_connection() is not conn:
                continue
            with _rebind_lock:
                finished, error = _reconnect_pyautogui_to(name)
                if not finished:
                    finished, error = _rebind_pyautogui_to_current_display()
            new_conn = _pyautogui_connection()
            if finished and new_conn is not conn and new_conn is not None:
                messages.append(("Reconnected desktop automation to display '%s'." % _display_name(new_conn), 2))
            else:
                messages.append((
                    "Could not reconnect desktop automation to an X display: %s. "
                    "Desktop actions will fail until an X display is available." % error,
                    2,
                ))
    except Exception as e:
        messages.append(("Could not inspect the timed-out action for a stuck X11 call: %s" % e, 2))
    return messages


# --- Xvfb process tracking -----------------------------------------------------

def _read_xvfb_registry():
    try:
        entries = json.loads(_XVFB_REGISTRY.read_text(encoding="utf-8"))
        return entries if isinstance(entries, list) else []
    except Exception:
        return []


def _write_xvfb_registry(entries):
    try:
        _XVFB_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        _XVFB_REGISTRY.write_text(json.dumps(entries), encoding="utf-8")
    except Exception:
        pass


def remember_xvfb(pid, display):
    """Record an Xvfb process started by this node process."""
    try:
        import psutil
        created = psutil.Process(pid).create_time()
        owner = psutil.Process(os.getpid()).create_time()
    except Exception:
        return
    with _xvfb_registry_lock:
        entries = [e for e in _read_xvfb_registry() if e.get("pid") != pid]
        entries.append({
            "pid": pid,
            "display": ":%s" % display,
            "create_time": created,
            "owner_pid": os.getpid(),
            "owner_create_time": owner,
        })
        _write_xvfb_registry(entries)


def forget_xvfb(pid):
    """Remove an Xvfb process from the registry once it has been stopped."""
    with _xvfb_registry_lock:
        entries = _read_xvfb_registry()
        remaining = [e for e in entries if e.get("pid") != pid]
        if len(remaining) != len(entries):
            _write_xvfb_registry(remaining)


def _same_process(proc, create_time):
    try:
        return abs(proc.create_time() - float(create_time)) < 1
    except Exception:
        return False


def cleanup_orphaned_xvfb():
    """Stop Xvfb processes left behind by an earlier run of this node folder.

    Call once at node startup. An Xvfb is only stopped if it is the exact
    process that was recorded (same pid, start time and display) and the node
    process that started it is gone, or is this process before a restart.
    Returns the pids that were stopped.
    """
    if not _IS_LINUX:
        return []
    try:
        import psutil
    except Exception:
        return []

    stopped = []
    kept = []
    with _xvfb_registry_lock:
        entries = _read_xvfb_registry()
        if not entries:
            return []
        for entry in entries:
            try:
                owner_pid = entry.get("owner_pid")
                owner_alive = False
                if owner_pid and owner_pid != os.getpid():
                    try:
                        owner = psutil.Process(owner_pid)
                        # A killed node can briefly remain as a zombie; that is not alive.
                        owner_alive = (_same_process(owner, entry.get("owner_create_time"))
                                       and owner.status() != psutil.STATUS_ZOMBIE)
                    except psutil.NoSuchProcess:
                        owner_alive = False
                if owner_alive:
                    kept.append(entry)  # still owned by a live node process; leave it alone
                    continue

                proc = psutil.Process(entry["pid"])
                if not _same_process(proc, entry.get("create_time")):
                    continue  # pid was reused by an unrelated process
                cmdline = proc.cmdline()
                if not cmdline or os.path.basename(cmdline[0]) != "Xvfb" or entry.get("display") not in cmdline:
                    continue
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    proc.kill()
                stopped.append(entry["pid"])
            except Exception:
                continue
        _write_xvfb_registry(kept)
    return stopped
