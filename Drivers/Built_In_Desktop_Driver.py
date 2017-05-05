'''
Created on December 14, 2016

@author: AutomationSolutionz Inc.
'''

import os,sys
import inspect
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Desktop.CrossPlatform import BuiltInFunctions as BuiltInFunctions
#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
local_run = False
#local_run = False



def sequential_actions_desktop(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Sequential Actions",1,local_run)
        sTestStepReturnStatus=BuiltInFunctions.Sequential_Actions(step_data,file_attachment)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Sequential Actions",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click element: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
