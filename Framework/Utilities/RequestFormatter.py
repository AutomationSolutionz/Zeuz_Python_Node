# -- coding: utf-8 --
# -- coding: cp1252 --
import asyncio
import time
from . import ConfigModule
import os
import requests
import json
import pickle
from urllib3.exceptions import InsecureRequestWarning
from colorama import Fore
from datetime import datetime, timedelta, timezone
from .verbose_log import vlog, VERBOSE as _VERBOSE
import Framework.Utilities.verbose_log as _vmod

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
    global ACCESS_TOKEN_EXPIRES_AT
    if not is_less_than_N_minutes_away(ACCESS_TOKEN_EXPIRES_AT, 10):
        return

    renew_token()


def renew_token():
    global ACCESS_TOKEN_EXPIRES_AT

    url = form_uri("/zsvc/auth/v1/renew")
    vlog(f"POST {url}")
    t0 = time.perf_counter()
    r = session.post(
        url=url,
        verify=False,
    )
    elapsed = time.perf_counter() - t0
    vlog(f"POST {url} -> {r.status_code} ({elapsed:.3f}s)")

    data = {}
    if r.status_code != 200:
        return data, r.status_code

    data = r.json()
    set_access_token_expiration(data["access_token_expires_at"])

    save_cookies(session=session, filename=SESSION_FILE_NAME)

    return data, r.status_code


def login():
    global ACCESS_TOKEN_EXPIRES_AT

    api_key = ConfigModule.get_config_value(AUTHENTICATION_CATEGORY, API_KEY_TAG)
    payload = {
        "type": "api_key",
        "api_key": api_key,
    }
    url = form_uri("/zsvc/auth/v1/login")
    vlog(f"POST {url}")
    t0 = time.perf_counter()
    r = session.post(
        url=url,
        json=payload,
        verify=False,
    )
    elapsed = time.perf_counter() - t0
    vlog(f"POST {url} -> {r.status_code} ({elapsed:.3f}s)")

    data = {}
    if r.status_code == 200:
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

    method = args[0] if args else kwargs.get("method", "?")
    url = args[1] if len(args) > 1 else kwargs.get("url", "?")
    if _vmod.VERBOSE:
        vlog(f"request {method.upper()} {url}")
    t0 = time.perf_counter()
    resp = session.request(*args, **kwargs)
    elapsed = time.perf_counter() - t0
    if _vmod.VERBOSE:
        vlog(f"request {method.upper()} {url} -> {resp.status_code} ({elapsed:.3f}s)")
    return resp

async def async_request(*args, **kwargs):
    """
    Runs the blocking request() in a worker thread
    so the event loop is not blocked.
    """
    method = args[0] if args else kwargs.get("method", "?")
    url = args[1] if len(args) > 1 else kwargs.get("url", "?")
    if _vmod.VERBOSE:
        vlog(f"async_request {method.upper()} {url}")
    t0 = time.perf_counter()
    resp = await asyncio.to_thread(request, *args, **kwargs)
    elapsed = time.perf_counter() - t0
    if _vmod.VERBOSE:
        vlog(f"async_request {method.upper()} {url} -> {resp.status_code} ({elapsed:.3f}s)")
    return resp


def Post(resource_path, payload=None, **kwargs):
    renew_token_with_expiry_check()
    if payload is None:
        payload = {}
    try:
        kwargs = add_api_key_to_headers(kwargs)
        url = form_uri(resource_path + "/")
        if _vmod.VERBOSE:
            vlog(f"Post {url}")
        t0 = time.perf_counter()
        resp = session.post(
            url,
            data=json.dumps(payload),
            verify=False,
            timeout=REQUEST_TIMEOUT,
            **kwargs
        )
        elapsed = time.perf_counter() - t0
        if _vmod.VERBOSE:
            vlog(f"Post {url} -> {resp.status_code} ({elapsed:.3f}s)")
        return resp.json()
    except Exception as e:
        print("Post Exception: {}".format(e))
        return {}


def Get(resource_path, payload=None, **kwargs):
    renew_token_with_expiry_check()
    if payload is None:
        payload = {}
    try:
        kwargs = add_api_key_to_headers(kwargs)
        url = form_uri(resource_path)
        if _vmod.VERBOSE:
            vlog(f"Get {url}")
        t0 = time.perf_counter()
        resp = session.get(
            url,
            params=json.dumps(payload),
            timeout=REQUEST_TIMEOUT,
            verify=False,
            **kwargs
        )
        elapsed = time.perf_counter() - t0
        if _vmod.VERBOSE:
            vlog(f"Get {url} -> {resp.status_code} ({elapsed:.3f}s)")
        return resp.json()

    except requests.exceptions.RequestException as e:
        print(e)
        return ""

    except Exception as e:
        print(e)
        return {}


def UpdatedGet(resource_path, payload=None, **kwargs):
    renew_token_with_expiry_check()
    if payload is None:
        payload = {}
    try:
        kwargs = add_api_key_to_headers(kwargs)
        url = form_uri(resource_path + "/")
        if _vmod.VERBOSE:
            vlog(f"UpdatedGet {url}")
        t0 = time.perf_counter()
        resp = session.get(
            url,
            params=payload,
            timeout=REQUEST_TIMEOUT,
            verify=False,
            **kwargs
        )
        elapsed = time.perf_counter() - t0
        if _vmod.VERBOSE:
            vlog(f"UpdatedGet {url} -> {resp.status_code} ({elapsed:.3f}s)")
        return resp.json()

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
