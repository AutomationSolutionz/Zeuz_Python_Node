#Sample Test Case

from DataFromUI import *
from BuiltInFunctions import HttpMethods

Method=HttpMethods

Method.GET(url_GET,url_GET_status)
Method.GET(url_GET_2,url_GET_2_status)

Method.POST(url_Post,data,url_Post_status)
Method.POST(url_Post,data,url_GET_2_status)

Method.PATCH(url_Patch,data,Status_OK)
Method.PUT(url_Put,data,Status_OK)