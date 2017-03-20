'''
Created on December 7, 2016

@author: AutomationSolutionz Inc.

@asifurrouf
'''

import inspect


import sys
import os
import requests
sys.path.append("..")

from Utilities import CommonUtil




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

def Data_By_GET_Method_Multiple(url,payload,header):
    # this function needs work with validating page title.  We need to check if user entered any title.
    # if not then we don't do the validation
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:

        Data = requests.get(url,params=payload,headers=header)
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


def Data_By_POST_Method(url,payload):
    # this function needs work with validating page title.  We need to check if user entered any title.
    # if not then we don't do the validation
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:

        Data = requests.post(url, payload)
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

def Data_By_POST_Method_Multiple(url,payload,header):
    # this function needs work with validating page title.  We need to check if user entered any title.
    # if not then we don't do the validation
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:

        Data = requests.post(url, data=payload,headers=header)
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