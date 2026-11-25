"""A node must get back in by itself when the server drops its session.

On 2026-11-23 a server upgrade lost every node session kept in Redis. Nodes kept
sending the dead session, the server answered 401 to each long-poll, and no
node ran anything until it was restarted by hand -- two days later. These tests
run the real RequestFormatter against a small local server that behaves like
zsvc: cookie sessions, login with an API key, renew, and a "flush" that forgets
every session.
"""

import ast
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from Framework.Utilities import RequestFormatter

GOOD_API_KEY = "good-key"


class FakeZsvc:
    def __init__(self):
        self.lock = threading.Lock()
        self.sessions = set()
        self.counter = 0
        self.logins = 0
        self.renews = 0
        self.uploads = []
        self.login_status = None  # force a status for login, e.g. 502

    def flush(self):
        with self.lock:
            self.sessions.clear()

    def new_session(self):
        with self.lock:
            self.counter += 1
            token = f"t{self.counter}"
            self.sessions.add(token)
            return token

    def valid(self, token):
        with self.lock:
            return token in self.sessions

    def rotate(self, token):
        """Like zsvc's renew: the old session ends and a new one is issued.
        Returns None when the old session is unknown."""
        with self.lock:
            if token not in self.sessions:
                return None
            self.sessions.discard(token)
        return self.new_session()


def make_handler(server_state: FakeZsvc):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _token(self):
            for part in (self.headers.get("Cookie") or "").split(";"):
                name, _, value = part.strip().partition("=")
                if name == "zeuz_access_token":
                    return value
            return None

        def _reply(self, status, body=None, cookie=None):
            payload = json.dumps(body or {}).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            if cookie:
                self.send_header("Set-Cookie", f"zeuz_access_token={cookie}; Path=/")
            self.end_headers()
            self.wfile.write(payload)

        def _body(self):
            length = int(self.headers.get("Content-Length") or 0)
            return self.rfile.read(length)

        def _expires(self):
            return (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

        def do_POST(self):
            body = self._body()
            if self.path == "/zsvc/auth/v1/login":
                with server_state.lock:
                    server_state.logins += 1
                if server_state.login_status is not None:
                    return self._reply(server_state.login_status)
                if json.loads(body).get("api_key") != GOOD_API_KEY:
                    return self._reply(401)
                token = server_state.new_session()
                return self._reply(
                    200,
                    {"access_token_expires_at": self._expires(), "user": {"username": "n"}},
                    cookie=token,
                )
            if self.path == "/zsvc/auth/v1/renew":
                with server_state.lock:
                    server_state.renews += 1
                new_token = server_state.rotate(self._token())
                if new_token is None:
                    return self._reply(403, {"error": "session does not exist"})
                return self._reply(
                    200, {"access_token_expires_at": self._expires()}, cookie=new_token
                )
            if not server_state.valid(self._token()):
                return self._reply(401)
            if self.path == "/upload/":
                server_state.uploads.append(body)
            return self._reply(200, {"ok": True})

        def do_GET(self):
            if not server_state.valid(self._token()):
                return self._reply(401)
            return self._reply(200, {"ok": True})

    return Handler


@pytest.fixture
def zsvc(monkeypatch, tmp_path):
    state = FakeZsvc()

    class Server(ThreadingHTTPServer):
        request_queue_size = 64  # the default of 5 resets a burst of connections

    httpd = Server(("127.0.0.1", 0), make_handler(state))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    address = f"http://127.0.0.1:{httpd.server_address[1]}"
    config = {"server_address": address, "api-key": GOOD_API_KEY}

    monkeypatch.setattr(
        RequestFormatter.ConfigModule,
        "get_config_value",
        lambda section, key, *a, **k: config.get(key, ""),
    )
    monkeypatch.setattr(RequestFormatter, "SESSION_FILE_NAME", str(tmp_path / "session.bin"))
    RequestFormatter.session.cookies.clear()
    monkeypatch.setattr(RequestFormatter, "_last_relogin_attempt", None, raising=False)
    monkeypatch.setattr(RequestFormatter, "_last_relogin_success", None, raising=False)
    monkeypatch.setattr(RequestFormatter, "_renewal_failed_at", None, raising=False)

    state.config = config
    state.address = address
    yield state
    httpd.shutdown()
    RequestFormatter.session.cookies.clear()


def _logged_in(zsvc):
    data, status = RequestFormatter.login()
    assert status == 200
    zsvc.logins = 0


def test_request_logs_in_again_after_the_server_lost_the_session(zsvc):
    _logged_in(zsvc)
    zsvc.flush()  # server upgrade / Redis FLUSHALL

    resp = RequestFormatter.request("get", zsvc.address + "/zsvc/deploy/v1/next/node")

    assert resp.status_code == 200
    assert zsvc.logins == 1
    # And it stays fixed: no further logins for the next requests.
    for _ in range(3):
        assert RequestFormatter.request("get", zsvc.address + "/x").status_code == 200
    assert zsvc.logins == 1


def test_request_accepts_method_and_url_as_keywords(zsvc):
    _logged_in(zsvc)
    zsvc.flush()

    resp = RequestFormatter.request(method="GET", url=zsvc.address + "/secrets")

    assert resp.status_code == 200


def test_many_threads_hitting_401_together_log_in_once(zsvc):
    _logged_in(zsvc)
    zsvc.flush()
    results = []
    barrier = threading.Barrier(10)

    def call():
        barrier.wait()
        results.append(RequestFormatter.request("get", zsvc.address + "/x").status_code)

    threads = [threading.Thread(target=call) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results == [200] * 10
    assert zsvc.logins == 1


def test_a_rejected_api_key_is_not_retried_on_every_request(zsvc, capsys):
    _logged_in(zsvc)
    zsvc.flush()
    zsvc.config["api-key"] = "revoked-key"

    first = RequestFormatter.request("get", zsvc.address + "/x")
    second = RequestFormatter.request("get", zsvc.address + "/x")

    assert first.status_code == 401
    assert second.status_code == 401
    assert zsvc.logins == 1  # the second request did not try again within the interval
    assert "Check the API key" in capsys.readouterr().out


def test_login_is_tried_again_after_the_interval(zsvc, monkeypatch):
    _logged_in(zsvc)
    zsvc.flush()
    zsvc.login_status = 502  # server briefly down while logging in

    assert RequestFormatter.request("get", zsvc.address + "/x").status_code == 401
    zsvc.login_status = None
    monkeypatch.setattr(RequestFormatter, "RELOGIN_MIN_INTERVAL_SECONDS", 0, raising=False)

    assert RequestFormatter.request("get", zsvc.address + "/x").status_code == 200
    assert zsvc.logins == 2


def test_upload_is_sent_again_with_its_whole_content(zsvc, tmp_path):
    _logged_in(zsvc)
    zsvc.flush()
    report = tmp_path / "report.zip"
    report.write_bytes(b"ZIPDATA" * 1000)

    with open(report, "rb") as f:
        resp = RequestFormatter.request(
            "post", zsvc.address + "/upload/", files=[("file", f)], data={"machine_name": "n"}
        )

    assert resp.status_code == 200
    assert len(zsvc.uploads) == 1
    assert b"ZIPDATA" * 1000 in zsvc.uploads[0]


def test_post_and_get_helpers_recover_too(zsvc, monkeypatch):
    _logged_in(zsvc)
    zsvc.flush()

    assert RequestFormatter.Post("thing", {"a": 1}) == {"ok": True}
    # A second loss right after the first is only retried once the interval
    # has passed; skip the wait here.
    monkeypatch.setattr(RequestFormatter, "RELOGIN_MIN_INTERVAL_SECONDS", 0, raising=False)
    zsvc.flush()
    assert RequestFormatter.UpdatedGet("thing", {"a": 1}) == {"ok": True}
    assert zsvc.logins == 2


def test_failed_renewal_falls_back_to_login(zsvc, monkeypatch):
    _logged_in(zsvc)
    zsvc.flush()
    # The access token is about to expire, so the next request renews first.
    monkeypatch.setattr(
        RequestFormatter, "ACCESS_TOKEN_EXPIRES_AT", datetime.now(timezone.utc)
    )

    resp = RequestFormatter.request("get", zsvc.address + "/x")

    assert resp.status_code == 200
    assert zsvc.renews == 1
    assert zsvc.logins == 1
    # The new session carries a fresh expiry, so no renew storm follows.
    for _ in range(5):
        RequestFormatter.request("get", zsvc.address + "/x")
    assert zsvc.renews == 1


def test_failed_renewal_is_not_retried_on_every_request(zsvc, monkeypatch):
    _logged_in(zsvc)
    zsvc.flush()
    zsvc.config["api-key"] = "revoked-key"
    monkeypatch.setattr(
        RequestFormatter, "ACCESS_TOKEN_EXPIRES_AT", datetime.now(timezone.utc)
    )

    for _ in range(5):
        RequestFormatter.request("get", zsvc.address + "/x")

    # Before: one renew per request, 327,156 of them in two days on one server.
    assert zsvc.renews == 1
    assert zsvc.logins == 1


def test_startup_with_a_stale_session_file_continues_to_connect():
    """node_cli.Login must not return after logging in again: it used to, so a
    node restarted with an old session.bin never started polling for work."""
    source = Path(__file__).resolve().parents[1] / "node_cli.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    login = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "Login"
    )
    stale_session_branches = [
        node
        for node in ast.walk(login)
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == "load_from_session"
    ]
    assert stale_session_branches, "Login no longer checks load_from_session"
    for branch in stale_session_branches:
        for node in ast.walk(branch):
            assert not isinstance(node, ast.Return), (
                f"node_cli.py:{node.lineno} returns while handling a stale session"
            )
