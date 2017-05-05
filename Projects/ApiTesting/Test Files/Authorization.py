'''
Created on December 7, 2016

@author: AutomationSolutionz Inc.
'''

import os,sys
import inspect
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as Selenium_Built_In

import sys
import os
import requests
sys.path.append("..")

from Framework.Utilities import CommonUtil

class AuthorizationData:

    def __init__(self,
                 account_id=None,
                 customer_id=None,
                 developer_token=None,
                 authentication=None):

        self._account_id = account_id
        self._customer_id = customer_id
        self._developer_token = developer_token
        self._authentication = authentication

    @property
    def account_id(self):
        return self._account_id

    @property
    def customer_id(self):
        return self._customer_id

    @property
    def developer_token(self):
        return self._developer_token

    @property
    def authentication(self):
        return self._authentication

    @account_id.setter
    def account_id(self, account_id):
        self._account_id = account_id

    @customer_id.setter
    def customer_id(self, customer_id):
        self._customer_id = customer_id

    @developer_token.setter
    def developer_token(self, developer_token):
        self._developer_token = developer_token

    @authentication.setter
    def authentication(self, authentication):
        self._authentication = authentication


class HttpMethods():

    @staticmethod
    def GET(url,statuscode):
        if(url==" "):
         print "Empty String"
        else:
           Data=requests.get(url)
           print "Status Code:", statuscode

           if(statuscode==Data.status_code):
               print "Status Code Matched",Data.status_code
           else:
               print "Status Code Not Matched"



    @staticmethod
    def POST(url,data,statuscode):
        if (url == " "):
            print "Empty String"
        else:
            Data=requests.post(url,data)
            print "Status Code:",statuscode

            if (statuscode == Data.status_code):
                print "Status Code Matched", Data.status_code
            else:
                print "Status Code Not Matched"

    @staticmethod
    def PATCH(url, data, statuscode):
        if (url == " "):
            print "Empty String"
        else:
            Data = requests.post(url, data)
            print "Status Code:", statuscode

            if (statuscode == Data.status_code):
                print "Status Code Matched", Data.status_code
            else:
                print "Status Code Not Matched"

    @staticmethod
    def PUT(url, data, statuscode):
        if (url == " "):
            print "Empty String"
        else:
            Data = requests.post(url, data)
            print "Status Code:", statuscode

            if (statuscode == Data.status_code):
                print "Status Code Matched", Data.status_code
            else:
                print "Status Code Not Matched"

def Data_By_GET_Method(url):
    # this function needs work with validating page title.  We need to check if user entered any title.
    # if not then we don't do the validation
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:

        Data = requests.get(url)
        if(Data.status_code == 200):
            CommonUtil.ExecLog(sModuleInfo, "Received Proper Data your link: %s" % url, 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Received Wrong Data your link: %s" % url, 1)
            return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception :%s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Received Wrong Data your link: %s. Error:%s" % (url, Error_Detail), 3)
        CommonUtil.TakeScreenShot(sModuleInfo)
        return "failed"

def Data_By_POST_Method(url,param,statuscode):
    # this function needs work with validating page title.  We need to check if user entered any title.
    # if not then we don't do the validation
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:

        Data = requests.post(url, param)
        if(statuscode == Data.status_code):
            CommonUtil.ExecLog(sModuleInfo, "Received Proper Data your link: %s" % url, 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Received Wrong Data your link: %s" % url, 1)
            return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception :%s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Received Wrong Data your link: %s. Error:%s" % (url, Error_Detail), 3)
        CommonUtil.TakeScreenShot(sModuleInfo)
        return "failed"
