# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

from . import ConfigModule
import requests
import json

SERVER_TAG = "Authentication"
SERVER_ADDRESS_TAG = "server_address"
SERVER_PORT = "server_port"
REQUEST_TIMEOUT = 2 * 60


def form_uri(resource_path):
    web_server_address = ConfigModule.get_config_value(SERVER_TAG, SERVER_ADDRESS_TAG)
    web_server_port = ""

    web_server_address = str(web_server_address).strip().strip("/")
    web_server_port = str(web_server_port).strip()
    if web_server_port == "":
        if web_server_address.startswith("https://"):
            web_server_port = "443"
        else:
            if web_server_address.startswith("http://"):
                web_server_domain = web_server_address.split("//")[1]
            else:
                web_server_domain = web_server_address.split("//")[0]
            if web_server_domain in ["localhost", "127.0.0.1"]:
                web_server_port = "8000"
            else:
                web_server_port = "80"
    ConfigModule.add_config_value("Authentication", "server_port", web_server_port)
    if web_server_address.startswith("http://") or web_server_address.startswith(
        "https://"
    ):
        base_server_address = "{}:{}/".format(web_server_address, web_server_port)
    else:
        base_server_address = "http://{}:{}/".format(
            web_server_address, web_server_port
        )
    return base_server_address + resource_path


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


def Get(resource_path, payload=None):
    if payload is None:  # Removing default mutable argument
        payload = {}
    try:
        return requests.get(
            form_uri(resource_path + "/"),
            params=json.dumps(payload),
            timeout=REQUEST_TIMEOUT,
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
            form_uri(resource_path + "/"), params=payload, timeout=REQUEST_TIMEOUT
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
        return requests.head(uri, timeout=REQUEST_TIMEOUT)

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
