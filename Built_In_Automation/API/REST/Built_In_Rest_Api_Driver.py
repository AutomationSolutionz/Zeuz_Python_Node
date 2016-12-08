'''
Created on May 15, 2016

@author: AutomationSolutionz Inc.
'''

import os,sys
import inspect
from Utilities import CommonUtil
from Built_In_Automation.API.REST import BuiltInFunctions as REST_Api_Built_In


#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
local_run = False
#local_run = False

def get_method(dependency, run_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Now We are going to use GET Method", 1, local_run)


        url=step_data[0][0][2]

        #sTestStepReturnStatus = Selenium_Built_In.Go_To_Link(web_link)

        sTestStepReturnStatus = REST_Api_Built_In.Data_By_GET_Method(url)
        temp_q.put(sTestStepReturnStatus)

        CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Data have been Received POST Method", 1, local_run)
        return sTestStepReturnStatus

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go to webpage Selenium:%s" % (Error_Detail), 3, local_run)
        temp_q.put("Failed")
        return "failed"


def post_method(dependency, run_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Now We are going to use POST Method", 1, local_run)


        url=step_data[0][0][2]
        param=step_data[1][0][2]
        statuscode=step_data[2][0][2]

        #sTestStepReturnStatus = Selenium_Built_In.Go_To_Link(web_link)

        sTestStepReturnStatus = REST_Api_Built_In.Data_By_POST_Method(url,param,statuscode)
        temp_q.put(sTestStepReturnStatus)

        CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Data have been Received POST Method", 1, local_run)
        return sTestStepReturnStatus

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception :%s" % e, 3, local_run)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Received Wrong Data your link: %s. Error:%s" % (url, Error_Detail), 3,
                           local_run)
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        return "failed"