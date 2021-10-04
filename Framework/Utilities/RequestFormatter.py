# -- coding: utf-8 --
# -- coding: cp1252 --

from . import ConfigModule
import requests
import json
from urllib3.exceptions import InsecureRequestWarning

# Tags for reading data from settings.conf file.
AUTHENTICATION_CATEGORY = "Authentication"
SERVER_ADDRESS_TAG = "server_address"
SERVER_PORT_TAG = "server_port"
API_KEY_TAG = "api-key"

REQUEST_TIMEOUT = 2 * 60

API_KEY_HEADER_NAME = "X-API-KEY"

# Suppress the InsecureRequestWarning since we use verify=False parameter.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


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


def Post(resource_path, payload=None, **kwargs):
    if payload is None:  # Removing default mutable argument
        payload = {}
    try:
        kwargs = add_api_key_to_headers(kwargs)
        return requests.post(
            form_uri(resource_path + "/"),
            data=json.dumps(payload),
            verify=False,
            timeout=REQUEST_TIMEOUT,
            **kwargs
        ).json()
    except Exception as e:
        print("Post Exception: {}".format(e))
        return {}


def Get(resource_path, payload=None, **kwargs):
    if payload is None:  # Removing default mutable argument
        payload = {}
    try:
        kwargs = add_api_key_to_headers(kwargs)
        return requests.get(
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
    if payload is None:  # Removing default mutable argument
        payload = {}
    try:
        kwargs = add_api_key_to_headers(kwargs)
        return requests.get(
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


def Head(resource_path, **kwargs):
    try:
        kwargs = add_api_key_to_headers(kwargs)
        uri = form_uri(resource_path)
        return requests.head(
            uri,
            timeout=REQUEST_TIMEOUT,
            verify=False,
            **kwargs
        )

    except requests.exceptions.RequestException:
        print(
            "Exception in Head: Please check your server address "
            "Please include full server name. Example: https://zeuz.zeuz.ai"
            "If you are using IP Address: Type in just the IP without http.  Example: 12.15.10.6"
        )
        return False
    except Exception as e:
        print("Exception in Head {}".format(e))
        return False
