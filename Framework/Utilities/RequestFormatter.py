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
    base_server_address = 'http://%s:%s/' % (str(web_server_address), str(web_server_port))
    return base_server_address+resource_path+'/'

def Post(resource_path,payload={}):
    try: return requests.post(form_uri(resource_path),data=json.dumps(payload), verify=False).json()
    except: return {}

def Get(resource_path,payload={}):
    try: return requests.get(form_uri(resource_path),params=json.dumps(payload), timeout=10).json()
    except: return {}

def Head(resource_path):
    try: return requests.head(form_uri(resource_path), timeout=10)
    except: return ''
