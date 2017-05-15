# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

from Built_In_Automation.API.REST.BuiltInFunctions import HttpMethods
from Built_In_Automation.API.REST.Files.DataFromUI import *

Method=HttpMethods

Method.GET(url_GET,url_GET_status)
Method.GET(url_GET_2,url_GET_2_status)

Method.POST(url_Post,data,url_Post_status)
Method.POST(url_Post,data,url_GET_2_status)

Method.PATCH(url_Patch,data,Status_OK)
Method.PUT(url_Put,data,Status_OK)