# -- coding: utf-8 --
# -- coding: cp1252 --

from . import ConfigModule
import requests
import json
from urllib3.exceptions import InsecureRequestWarning

SERVER_TAG = "Authentication"
SERVER_ADDRESS_TAG = "server_address"
SERVER_PORT = "server_port"
REQUEST_TIMEOUT = 2 * 60

# Suppress the InsecureRequestWarning since we use verify=False parameter.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def form_uri(resource_path):
    web_server_address = ConfigModule.get_config_value(SERVER_TAG, SERVER_ADDRESS_TAG)
    base_server_address = web_server_address
    if len(resource_path) > 0:
        if resource_path[0] == "/":
            resource_path = resource_path[1:]
        base_server_address += "/" + resource_path 

    return base_server_address


def Post(resource_path, payload=None):
    if payload is None:  # Removing default mutable argument
        payload = {}
    try:
        return requests.post(
            form_uri(resource_path + "/"),
            data=json.dumps(payload),
            verify=False,
            timeout=REQUEST_TIMEOUT,
        ).json()
    except Exception as e:
        print("Post Exception: {}".format(e))
        return {}


def Get(resource_path, payload=None,**kwargs):
    if payload is None:  # Removing default mutable argument
        payload = {}
    try:
        return requests.get(
            form_uri(resource_path ),
            params=json.dumps(payload),
            timeout=REQUEST_TIMEOUT,
            verify=False,
            **kwargs
        ).json()

    except requests.exceptions.RequestException:
        print(
            "Exception in UpdateGet: Authentication Failed. Please check your server, username and password. "
            "Please include full server name. Example: https://zeuz.zeuz.ai. "
            "If you are using IP Address: Type in just the IP without http.  Example: 12.15.10.6"
        )
        return ""

    except Exception as e:
        print("Get Exception: {}".format(e))
        return {}


# here params are passed as a plain dictionary for better catching get parameter values
def UpdatedGet(resource_path, payload=None):
    if payload is None:  # Removing default mutable argument
        payload = {}
    try:
        return requests.get(
            form_uri(resource_path + "/"),
            params=payload,
            timeout=REQUEST_TIMEOUT,
            verify=False,
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


def Head(resource_path):
    try:
        uri = form_uri(resource_path)
        return requests.head(uri, timeout=REQUEST_TIMEOUT, verify=False)

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
