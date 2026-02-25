import json
import ssl
import time
from threading import Lock, Thread, Timer
from urllib.parse import urlparse

import websocket


# Websocket connection object that runs on a different thread.
ws = None
connected = False
ws_url = None
ws_thread = None
should_run = False
connection_lock = Lock()
MIN_RECONNECT_DELAY_SECONDS = 3
MAX_RECONNECT_DELAY_SECONDS = 300
BACKOFF_MULTIPLIER = 2
BUFFER_FLUSH_INTERVAL = 0.5  # seconds
MAX_BUFFER_SIZE = 500
BATCH_MIN_VERSION = (2, 0, 0)
WARN_COLOR = "\033[33m"
RESET_COLOR = "\033[0m"
attempt_opened = False
reconnect_delay_seconds = MIN_RECONNECT_DELAY_SECONDS
server_version = None  # version tuple, e.g. (2, 0, 0), set on connect
_log_buffer = []  # buffered log dicts awaiting flush
_buffer_lock = Lock()
_flush_timer = None  # type: Timer | None


def _parse_version(version_str):
    """Parse a semver-like string into a tuple of ints, e.g. '2.0.0' -> (2, 0, 0).

    Pre-release suffixes (e.g. '2.0.0-beta.1') are stripped before parsing.
    """
    try:
        core = version_str.strip().split("-")[0]  # strip pre-release suffix
        return tuple(int(p) for p in core.split("."))
    except (ValueError, AttributeError):
        return None


def _log(message):
    print(f"[live-log] {message}")


def _warn(message):
    print(f"{WARN_COLOR}[live-log][warn] {message}{RESET_COLOR}")


def _is_localhost_url(url):
    try:
        parsed = urlparse(url or "")
        return parsed.hostname == "localhost"
    except Exception:
        return False


def _build_websocket(url):
    app = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    app.on_open = on_open
    return app


def send_file(data, ws):
    """Send binary data through websocket."""

    try:
        if ws is None:
            return
        ws.send(data, websocket.ABNF.OPCODE_BINARY)
    except Exception:
        return


def send(msg, ws):
    """Send plain text through websocket."""

    try:
        if ws is None:
            return
        if not isinstance(msg, str):
            msg = json.dumps(msg)
        ws.send(msg)
    except Exception:
        return


def _schedule_flush():
    """Schedule a buffer flush after BUFFER_FLUSH_INTERVAL if not already scheduled."""
    global _flush_timer
    if _flush_timer is not None:
        return  # already scheduled
    _flush_timer = Timer(BUFFER_FLUSH_INTERVAL, _flush_buffer)
    _flush_timer.daemon = True
    _flush_timer.start()


def _flush_buffer():
    """Send all buffered log entries as a single batch message."""
    global _flush_timer
    with _buffer_lock:
        _flush_timer = None
        if not _log_buffer:
            return
        batch = list(_log_buffer)
        _log_buffer.clear()
    msg = {"type": "log", "msg": batch}
    global ws
    send(msg, ws)


def log(module_info, log_level, description):
    entry = {
        "module_info": module_info,
        "log_level": log_level,
        "msg": description,
    }

    if server_version is not None and server_version >= BATCH_MIN_VERSION:
        with _buffer_lock:
            if len(_log_buffer) < MAX_BUFFER_SIZE:
                _log_buffer.append(entry)
            _schedule_flush()
    else:
        msg = {"type": "log", "msg": entry}
        global ws
        send(msg, ws)


def binary(data):
    global ws
    send_file(data, ws)


def close():
    global ws
    global connected
    global should_run
    global _flush_timer
    global server_version

    # Prevent new logs from being buffered while we drain.
    server_version = None

    # Flush any remaining buffered logs before closing.
    with _buffer_lock:
        if _flush_timer is not None:
            _flush_timer.cancel()
            _flush_timer = None
    _flush_buffer()

    connected = False
    should_run = False
    if ws is not None:
        try:
            ws.close(status=1000, reason="Test Set run complete")
        except Exception:
            return


def on_message(ws, message):
    global server_version
    try:
        data = json.loads(message)
        if isinstance(data, dict) and data.get("type") == "version":
            server_version = _parse_version(data["msg"])
            _log(f"Server version: {server_version}")
            if server_version is not None and server_version >= BATCH_MIN_VERSION:
                _log("Batch log buffering enabled.")
            return
    except Exception:
        pass
    print("[ws] Message:\n", message)


def on_error(ws, error):
    if isinstance(error, AttributeError):
        return
    elif isinstance(error, OSError):
        # Prevent bad file descriptor error from showing
        return
    _log(f"Connection failed: {error}")


def on_close(ws=None, a=None, b=None):
    global connected
    global should_run
    global reconnect_delay_seconds
    global server_version
    global _flush_timer
    connected = False
    server_version = None
    # Cancel any pending flush timer on disconnect.
    with _buffer_lock:
        if _flush_timer is not None:
            _flush_timer.cancel()
            _flush_timer = None
        _log_buffer.clear()
    if should_run:
        _log(
            f"Disconnected. Reconnecting in {reconnect_delay_seconds}s..."
        )


def on_open(ws):
    global connected
    global attempt_opened
    connected = True
    attempt_opened = True
    _log("Live log connection established.")


def run_ws_thread():
    global ws
    global connected
    global should_run
    global ws_url
    global attempt_opened
    global reconnect_delay_seconds

    while should_run:
        next_ws = None
        attempt_opened = False
        try:
            next_ws = _build_websocket(ws_url)
            with connection_lock:
                ws = next_ws
            next_ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            _log(f"Connection attempt failed: {e}")
        finally:
            connected = False
            with connection_lock:
                if ws is not None and next_ws is not None and ws is next_ws:
                    ws = None

            if (
                should_run
                and (not attempt_opened)
                and _is_localhost_url(ws_url)
            ):
                _warn(
                    "Detected 'localhost' and failed to establish live-log connection. "
                    "If your server is in WSL, use '127.0.0.1' instead."
                )

        if should_run:
            time.sleep(reconnect_delay_seconds)
            if attempt_opened:
                reconnect_delay_seconds = MIN_RECONNECT_DELAY_SECONDS
            else:
                reconnect_delay_seconds = min(
                    MAX_RECONNECT_DELAY_SECONDS,
                    reconnect_delay_seconds * BACKOFF_MULTIPLIER,
                )


def connect(url):
    global ws
    global connected
    global ws_url
    global ws_thread
    global should_run
    global reconnect_delay_seconds

    # Uncomment next line for debugging.
    # websocket.enableTrace(True)
    previous_url = ws_url
    ws_url = url
    should_run = True
    reconnect_delay_seconds = MIN_RECONNECT_DELAY_SECONDS

    if ws_thread is not None and ws_thread.is_alive():
        if previous_url != url:
            _log(f"Live log server changed. Switching immediately to: {url}")
            with connection_lock:
                current_ws = ws
            if current_ws is not None:
                try:
                    current_ws.close(status=1000, reason="Switching live log server")
                except Exception:
                    pass
        return

    ws_thread = Thread(target=run_ws_thread, daemon=True)
    ws_thread.start()

