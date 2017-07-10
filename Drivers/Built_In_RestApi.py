'''
Created on April 11, 2017

@author: AutomationSolutionz Inc.
'''

import os,sys
import inspect
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Web.REST import BuiltInFunctions


def sequential_actions_rest(dependency,run_time_params,step_data,file_attachment,temp_q,screen_capture):
    try:
        sTestStepReturnStatus=BuiltInFunctions.Sequential_Actions(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)