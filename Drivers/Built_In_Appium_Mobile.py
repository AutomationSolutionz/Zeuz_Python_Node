'''
Created on May 15, 2016

@author: RizDesktop
'''


import os,sys
import inspect
from Utilities import CommonUtil
from Automation.Mobile.CrossPlatform.Appium import basicfunctions as bf

#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False


def open_app(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        package_name=step_data[0][0][1]
        activity_name=step_data[0][1][1]
        sTestStepReturnStatus = bf.launch(package_name,activity_name)
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to launch app: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"


def close_app(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        sTestStepReturnStatus = bf.close()
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close app: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    