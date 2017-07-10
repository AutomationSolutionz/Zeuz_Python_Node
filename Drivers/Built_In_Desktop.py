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



def sequential_actions_desktop(dependency,run_time_params,step_data,file_attachment,temp_q,screen_capture):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Sequential Actions",1,local_run)
        sTestStepReturnStatus=BuiltInFunctions.Sequential_Actions(step_data,file_attachment)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Sequential Actions",1,local_run)
        return sTestStepReturnStatus


    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)
