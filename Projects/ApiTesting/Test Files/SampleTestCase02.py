# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import requests

url = "https://httpbin.org/post"

querystring = {"foo":["bar","baz"]}

payload = "foo=bar&bar=bazfoo=bar&bar=bazfoo=bar&bar=bazfoo=bar&bar=bazfoo=bar&bar=bazfoo=bar&bar=bazfoo=bar&bar=bazfoo=bar&bar=baz"


response = requests.request("POST", url, data=payload, params=querystring)

print(response.text)