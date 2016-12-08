'''
Created on December 7, 2016

@author: AutomationSolutionz Inc.
'''

import os,sys
import inspect
from Utilities import CommonUtil
from Built_In_Automation.Web.SeleniumAutomation import BuiltInFunctions as Selenium_Built_In
#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
local_run = False
#local_run = False

import sys
import os
import requests
sys.path.append("..")

from Utilities import CommonUtil


#local_run = True
local_run = False

def Data_By_GET_Method(url):
    # this function needs work with validating page title.  We need to check if user entered any title.
    # if not then we don't do the validation
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:

        Data = requests.get(url)
        if(Data.status_code == 200):
            CommonUtil.ExecLog(sModuleInfo, "Received Proper Data your link: %s" % url, 1, local_run)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Received Wrong Data your link: %s" % url, 1, local_run)
            return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception :%s" % e, 3, local_run)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Received Wrong Data your link: %s. Error:%s" % (url, Error_Detail), 3, local_run)
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        return "failed"

def Data_By_POST_Method(url,payload):
    # this function needs work with validating page title.  We need to check if user entered any title.
    # if not then we don't do the validation
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:

        Data = requests.post(url, payload)
        if(Data.status_code == 200):
            CommonUtil.ExecLog(sModuleInfo, "Received Proper Data your link: %s" % url, 1, local_run)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Received Wrong Data your link: %s" % url, 1, local_run)
            return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception :%s" % e, 3, local_run)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Received Wrong Data your link: %s. Error:%s" % (url, Error_Detail), 3, local_run)
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        return "failed"

def Data_By_POST_Method_Multiple(url,payload,header):
    # this function needs work with validating page title.  We need to check if user entered any title.
    # if not then we don't do the validation
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:

        Data = requests.post(url, data=payload,headers=header)
        if(Data.status_code == 200):
            CommonUtil.ExecLog(sModuleInfo, "Received Proper Data your link: %s" % url, 1, local_run)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Received Wrong Data your link: %s" % url, 1, local_run)
            return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception :%s" % e, 3, local_run)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Received Wrong Data your link: %s. Error:%s" % (url, Error_Detail), 3, local_run)
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        return "failed"