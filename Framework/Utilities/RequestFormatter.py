# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

from . import ConfigModule
import requests,json
SERVER_TAG='Server'
SERVER_ADDRESS_TAG='server_address'
SERVER_PORT='server_port'

def form_uri(resource_path):
    web_server_address = ConfigModule.get_config_value(SERVER_TAG, SERVER_ADDRESS_TAG)
    web_server_port = ConfigModule.get_config_value(SERVER_TAG, SERVER_PORT)

    web_server_address = str(web_server_address).strip().strip("/")
    web_server_port = str(web_server_port).strip()
    if web_server_port == "":
        web_server_port = "80"

    if web_server_address.startswith("http://") or web_server_address.startswith("https://"):
        base_server_address = "{}:{}/".format(web_server_address,web_server_port)
    else:
        base_server_address = 'http://{}:{}/'.format(web_server_address, web_server_port)
    return base_server_address+resource_path+'/'


def Post(resource_path,payload=None):
    if payload is None: # Removing default mutable argument
        payload = {}
    try:
        return requests.post(form_uri(resource_path),data=json.dumps(payload), verify=False).json()
    except Exception as e:
        print("Post Exception: {}".format(e))
        return {}


def Get(resource_path,payload=None):
    if payload is None: # Removing default mutable argument
        payload = {}
    try:
        return requests.get(form_uri(resource_path),params=json.dumps(payload), timeout=10).json()
    except Exception as e:
        print("Get Exception: {}".format(e))
        return {}

def Head(resource_path):
    try:
        return requests.head(form_uri(resource_path), timeout=10)
    except Exception as e:
        print("Exception in Head {}".format(e))
        return ''
