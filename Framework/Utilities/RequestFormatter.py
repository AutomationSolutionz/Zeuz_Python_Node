# -- coding: utf-8 --
# -- coding: cp1252 --

from . import ConfigModule
import requests
import json
import pickle
from datetime import datetime, timezone, timedelta
from urllib3.exceptions import InsecureRequestWarning
from colorama import Fore

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
# TODO: session neeeds to be renewed every 10 mins, keep a global variable in
# this module and track if a new token is necessary, if necessary, perform a
# renewal.

def save_cookies(session: requests.Session, filename: str):
    try:
        with open(filename, 'wb') as f:
            pickle.dump(session.cookies, f)
    except:
        print("[RequestFormatter] ERROR saving cookies to disk.")


def load_cookies(session: requests.Session, filename: str):
    try:
        with open(filename, 'rb') as f:
            session.cookies.update(pickle.load(f))
    except:
        print("[RequestFormatter] ERROR loading cookies from disk.")


def datestring_to_obj(date_string: str) -> datetime:
    date_string = date_string[:date_string.index(".")]
    date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
    date_obj.replace(tzinfo=timezone.utc)
    return date_obj


def is_less_than_N_minutes_away(target_datetime, n):
    # Get the current time
    current_time = datetime.utcnow()

    # Calculate the difference between the target datetime and the current time
    time_difference = target_datetime - current_time

    # Check if the difference is less than 2 minutes
    return time_difference < timedelta(minutes=n)


def renew_token():
    global ACCESS_TOKEN_EXPIRES_AT
    if not is_less_than_N_minutes_away(ACCESS_TOKEN_EXPIRES_AT, 1):
        return

    r = session.post(
        url=form_uri("/zsvc/auth/v1/renew"),
    )

    if r.status_code != 200:
        line_color = Fore.RED
        print(line_color + "[RequestFormatter] token could not be renewed. Please login again.")
        return

    data = r.json()
    ACCESS_TOKEN_EXPIRES_AT = datestring_to_obj(data["access_token_expires_at"])

    # Save new tokens to disk
    save_cookies(session=session, filename=SESSION_FILE_NAME)


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
    )


    data = {}
    if r.status_code == 200:
        # Save new tokens to disk
        data = r.json()
        ACCESS_TOKEN_EXPIRES_AT = datestring_to_obj(data["access_token_expires_at"])
        save_cookies(session=session, filename=SESSION_FILE_NAME)

    return data, r.status_code


def form_uri(resource_path):
    web_server_address = ConfigModule.get_config_value(AUTHENTICATION_CATEGORY, SERVER_ADDRESS_TAG)
    base_server_address = web_server_address
    if len(resource_path) > 0:
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
    """
    renew_token()
    return session.request(*args, **kwargs)


def Post(resource_path, payload=None, **kwargs):
    renew_token()
    if payload is None:  # Removing default mutable argument
        payload = {}
    try:
        kwargs = add_api_key_to_headers(kwargs)
        resp = session.post(
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
    renew_token()
    if payload is None:  # Removing default mutable argument
        payload = {}
    try:
        kwargs = add_api_key_to_headers(kwargs)
        return session.get(
            form_uri(resource_path),
            params=json.dumps(payload),
            timeout=REQUEST_TIMEOUT,
            verify=False,
            **kwargs
        ).json()

    except requests.exceptions.RequestException:
        print(
            "Exception in UpdateGet: Authentication Failed. Please check your server, username and password. "
            "Please include full server name. Example: https://zeuz.zeuz.ai.\n"
            "If you are using IP Address: Type in just the IP without http.  Example: 12.15.10.6"
        )
        return ""

    except Exception as e:
        print("Get Exception: {}".format(e))
        return {}


# here params are passed as a plain dictionary for better catching get parameter values
def UpdatedGet(resource_path, payload=None, **kwargs):
    renew_token()
    if payload is None:  # Removing default mutable argument
        payload = {}
    try:
        kwargs = add_api_key_to_headers(kwargs)
        return session.get(
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
