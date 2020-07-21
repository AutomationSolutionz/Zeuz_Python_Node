# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-


url_ip = "https://httpbin.org/ip"
Status_OK = 200
url_GET = "https://httpbin.org/get"
url_GET_status = 200

url_GET_2 = "https://httpbin.org/post"
url_GET_2_status = 405

url_Post = "https://httpbin.org/post"
url_Post_status = 200

url_Patch = "https://httpbin.org/patch"

url_Put = "https://httpbin.org/put"
url_Delete = "https://httpbin.org/delete"

data = {
    "eventType": "AAS_PORTAL_START",
    "data": {"uid": "hfe3hf45huf33545", "aid": "1", "vid": "1"},
}
params = {
    "sessionKey": "9ebbd0b25760557393a43064a92bae539d962103",
    "format": "xml",
    "platformId": 1,
}

headers = {
    "status": "200 OK",
    "content-encoding": "gzip",
    "transfer-encoding": "chunked",
    "connection": "close",
    "server": "nginx/1.0.4",
    "x-runtime": "148ms",
    "etag": '"e1ca502697e5c9317743dc078f67693f"',
    "content-type": "application/json; charset=utf-8",
}


""" import json
row = [1L,[0.1,0.2],[[1234L,1],[134L,2]]]
json.dumps(row)
'[1, [0.1, 0.2], [[1234, 1], [134, 2]]]'

 """

import json

value = []
element = []
data = []

for i in range(1, 100, 1):
    element.append("Element_" + str(i))
    value.append("Value_" + str(i))
    data[i] = str(element[i]) + str(value[i])


print data

Element = json.dumps(element)
Value = json.dumps(value)

Data = Element + Value

print Data

"""for m in range(1,100,1):
  data[m] = str(json.dumps(Element[m]))+":"+str(json.dumps(value[m]))
  print data[m]

print json.dumps(data) """
