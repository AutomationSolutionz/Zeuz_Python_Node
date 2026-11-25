# -- coding: utf-8 --
# -- coding: cp1252 --
import asyncio
from . import ConfigModule
import os
import requests
import json
import pickle
import threading
import time
from urllib.parse import urlparse
from urllib3.exceptions import InsecureRequestWarning
from colorama import Fore
from datetime import datetime, timedelta, timezone

# Tags for reading data from settings.conf file.
AUTHENTICATION_CATEGORY = "Authentication"
SERVER_ADDRESS_TAG = "server_address"
SERVER_PORT_TAG = "server_port"
API_KEY_TAG = "api-key"

REQUEST_TIMEOUT = 2 * 60

API_KEY_HEADER_NAME = "X-API-KEY"

# Suppress the InsecureRequestWarning since we use verify=False parameter.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


session = requests.Session()
SESSION_FILE_NAME = "session.bin"
ACCESS_TOKEN_EXPIRES_AT = datetime.now()

def save_cookies(session: requests.Session, filename: str):
    try:
        with open(filename, 'wb') as f:
            pickle.dump(session.cookies, f)
    except Exception:
        print("[RequestFormatter] ERROR saving cookies to disk.")


def load_cookies(filename: os.PathLike):
    global session
    try:
        with open(filename, 'rb') as f:
            session.cookies.update(pickle.load(f))
    except FileNotFoundError:
        print("[RequestFormatter] No cookies found on disk.")
    except Exception:
        print("[RequestFormatter] ERROR loading cookies from disk.")


def set_access_token_expiration(date_string: str):
    global ACCESS_TOKEN_EXPIRES_AT

    ACCESS_TOKEN_EXPIRES_AT = datestring_to_obj(date_string)


def datestring_to_obj(date_string: str) -> datetime:
    try:
        date_obj = datetime.fromisoformat(date_string)
    except Exception:
        date_string = date_string[:date_string.index(".")]
        date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
        date_obj.replace(tzinfo=timezone.utc)

    return date_obj


def is_less_than_N_minutes_away(target_datetime, n):
    # Get the current time
    # Handle both timezone-aware and timezone-naive datetimes
    if target_datetime.tzinfo is None:
        # Target is naive, use naive current time
        current_time = datetime.now()
    else:
        # Target is aware, use aware current time in UTC
        current_time = datetime.now(timezone.utc)

    # Calculate the difference between the target datetime and the current time
    time_difference = target_datetime - current_time

    # Check if the difference is less than n minutes
    return time_difference < timedelta(minutes=n)


def renew_token_with_expiry_check():
    global _renewal_failed_at
    if not is_less_than_N_minutes_away(ACCESS_TOKEN_EXPIRES_AT, 10):
        return
    if (
        _renewal_failed_at is not None
        and time.monotonic() - _renewal_failed_at < RELOGIN_MIN_INTERVAL_SECONDS
    ):
        # Renewing and logging in both failed a moment ago. Trying again on
        # every request would only flood the server.
        return

    _, status_code = renew_token()
    if status_code == 200:
        _renewal_failed_at = None
        return

    if status_code in SESSION_REJECTED_STATUSES and relogin(
        f"renewing the session returned {status_code}"
    ):
        _renewal_failed_at = None
        return

    _renewal_failed_at = time.monotonic()


# Statuses with which the server says it no longer accepts this node's session
# (missing, expired, or unknown to it -- after a server upgrade or a Redis
# flush, for example). Logging in again with the API key fixes all of them.
SESSION_REJECTED_STATUSES = (400, 401, 403)

# Minimum seconds between two attempts to log in again. Stops a revoked API key
# from turning into a login request every few seconds.
RELOGIN_MIN_INTERVAL_SECONDS = 30

_relogin_lock = threading.Lock()
_last_relogin_attempt = None  # time.monotonic() of the last attempt
_last_relogin_success = None  # time.monotonic() of the last success
_renewal_failed_at = None  # time.monotonic() of the last failed renew + relogin


def relogin(reason: str) -> bool:
    """Gets a new session with the API key after the server stopped accepting
    the current one.

    Before this, a node whose session was lost (server upgrade, Redis flush)
    kept sending the dead session forever and the server answered 401 to every
    request until someone restarted the node by hand.

    Returns True when the node holds a working session afterwards. Safe to call
    from several threads at once: only one logs in, the others reuse its result.
    """
    global _last_relogin_attempt, _last_relogin_success

    called_at = time.monotonic()
    with _relogin_lock:
        if _last_relogin_success is not None and _last_relogin_success >= called_at:
            # Another thread logged in while this one waited for the lock.
            return True
        if (
            _last_relogin_attempt is not None
            and called_at - _last_relogin_attempt < RELOGIN_MIN_INTERVAL_SECONDS
        ):
            return False

        _last_relogin_attempt = time.monotonic()
        try:
            _, status_code = login()
        except Exception as e:
            print(Fore.RED + f"[RequestFormatter] Could not log in again ({reason}): {e}")
            return False

        if status_code != 200:
            print(
                Fore.RED
                + f"[RequestFormatter] The server no longer accepts this node's session ({reason}) "
                + f"and logging in again with the API key returned {status_code}. "
                + "Check the API key and the server address."
            )
            return False

        _last_relogin_success = time.monotonic()
        print(
            Fore.YELLOW
            + f"[RequestFormatter] The server no longer accepted this node's session ({reason}). "
            + "Logged in again with the API key."
        )
        return True


def _rewind_request_body(kwargs) -> bool:
    """Moves file objects in a request back to their start so the request can
    be sent again. Returns False when one of them cannot be rewound."""

    candidates = []
    files = kwargs.get("files")
    if isinstance(files, dict):
        candidates.extend(files.values())
    elif files:
        candidates.extend(
            item[1] if isinstance(item, (tuple, list)) and len(item) > 1 else item
            for item in files
        )
    candidates.append(kwargs.get("data"))

    for candidate in candidates:
        fileobj = (
            candidate[1]
            if isinstance(candidate, (tuple, list)) and len(candidate) > 1
            else candidate
        )
        if fileobj is None or isinstance(fileobj, (str, bytes, bytearray, dict, list, tuple)):
            continue
        if hasattr(fileobj, "seek"):
            try:
                fileobj.seek(0)
                continue
            except Exception:
                return False
        if hasattr(fileobj, "read") or hasattr(fileobj, "__next__"):
            # A stream or generator that was already consumed.
            return False
    return True


def _send(method: str, url: str, **kwargs) -> requests.Response:
    """Sends one request. If the server rejects the session (401), logs in
    again with the API key and sends the request once more."""

    response = session.request(method, url, **kwargs)
    if response.status_code != 401:
        return response

    if not relogin(f"{method.upper()} {_path_of(url)} returned 401"):
        return response
    if not _rewind_request_body(kwargs):
        return response
    return session.request(method, url, **kwargs)


def _path_of(url) -> str:
    try:
        return urlparse(str(url)).path or str(url)
    except Exception:
        return str(url)


def renew_token():
    global ACCESS_TOKEN_EXPIRES_AT

    r = session.post(
        url=form_uri("/zsvc/auth/v1/renew"),
        verify=False,
        timeout=70,
    )

    data = {}
    if r.status_code != 200:
        line_color = Fore.RED
        # print(line_color + "[RequestFormatter] token could not be renewed. Please login again.")
        return data, r.status_code

    data = r.json()
    set_access_token_expiration(data["access_token_expires_at"])

    # Save new tokens to disk
    save_cookies(session=session, filename=SESSION_FILE_NAME)

    return data, r.status_code


def login():
    global ACCESS_TOKEN_EXPIRES_AT

    api_key = ConfigModule.get_config_value(AUTHENTICATION_CATEGORY, API_KEY_TAG)
    payload = {
        "type": "api_key",
        "api_key": api_key,
    }
    r = session.post(
        url=form_uri("/zsvc/auth/v1/login"),
        json=payload,
        verify=False,
        timeout=70,
    )


    data = {}
    if r.status_code == 200:
        # Save new tokens to disk
        data = r.json()
        set_access_token_expiration(data["access_token_expires_at"])
        save_cookies(session=session, filename=SESSION_FILE_NAME)

    return data, r.status_code


def form_uri(resource_path: str | None = None) -> str:
    web_server_address = ConfigModule.get_config_value(AUTHENTICATION_CATEGORY, SERVER_ADDRESS_TAG)
    base_server_address = web_server_address
    if resource_path and len(resource_path) > 0:
        if resource_path[0] == "/":
            resource_path = resource_path[1:]
        base_server_address += "/" + resource_path

    return base_server_address


def add_api_key_to_headers(kwargs):
    """
    Adds the 'X-API-KEY' header to the passed dictionary's 'headers' key, which
    is used for every request. This makes it easy to authenticate all zeuz
    server requests without having to manually specifying the API key
    everywhere.
    """

    api_key = ConfigModule.get_config_value(AUTHENTICATION_CATEGORY, API_KEY_TAG)
    if api_key:
        if "headers" in kwargs:
            kwargs["headers"][API_KEY_HEADER_NAME] = api_key
        else:
            kwargs["headers"] = { API_KEY_HEADER_NAME: api_key }
    return kwargs


def request(*args, **kwargs):
    """
    request() is a wrapper for requests.request which handles automatic session
    management.
    Default values:
        verify = False
        timeout = 70 sec
    """
    renew_token_with_expiry_check()
    if "verify" not in kwargs:
        kwargs["verify"] = False
    if "timeout" not in kwargs:
        kwargs["timeout"] = 70

    args = list(args)
    method = args.pop(0) if args else kwargs.pop("method")
    url = args.pop(0) if args else kwargs.pop("url")
    if args:
        # Positional request options are passed through as they always were.
        return session.request(method, url, *args, **kwargs)
    return _send(method, url, **kwargs)

# async wrapper
async def async_request(*args, **kwargs):
    """
    Runs the blocking request() in a worker thread
    so the event loop is not blocked.
    """
    return await asyncio.to_thread(request, *args, **kwargs)


def Post(resource_path, payload=None, **kwargs):
    renew_token_with_expiry_check()
    if payload is None:  # Removing default mutable argument
        payload = {}
    try:
        kwargs = add_api_key_to_headers(kwargs)
        resp = _send(
            "post",
            form_uri(resource_path + "/"),
            data=json.dumps(payload),
            verify=False,
            timeout=REQUEST_TIMEOUT,
            **kwargs
        )
        return resp.json()
    except Exception as e:
        print("Post Exception: {}".format(e))
        return {}


def Get(resource_path, payload=None, **kwargs):
    renew_token_with_expiry_check()
    if payload is None:  # Removing default mutable argument
        payload = {}
    try:
        kwargs = add_api_key_to_headers(kwargs)
        return _send(
            "get",
            form_uri(resource_path),
            params=json.dumps(payload),
            timeout=REQUEST_TIMEOUT,
            verify=False,
            **kwargs
        ).json()

    except requests.exceptions.RequestException as e:
        print(e)
        return ""

    except Exception as e:
        print(e)
        return {}


# here params are passed as a plain dictionary for better catching get parameter values
def UpdatedGet(resource_path, payload=None, **kwargs):
    renew_token_with_expiry_check()
    if payload is None:  # Removing default mutable argument
        payload = {}
    try:
        kwargs = add_api_key_to_headers(kwargs)
        return _send(
            "get",
            form_uri(resource_path + "/"),
            params=payload,
            timeout=REQUEST_TIMEOUT,
            verify=False,
            **kwargs
        ).json()

    except requests.exceptions.RequestException as e:
        print(
            "Exception in UpdateGet: Authentication Failed. Please check your server, username and password. "
            "Please include full server name. Example: https://zeuz.zeuz.ai"
            "If you are using IP Address: Type in just the IP without http.  Example: 12.15.10.6"
        )
        return ""

    except Exception as e:
        print("Get Exception: {}".format(e))
        return {}
