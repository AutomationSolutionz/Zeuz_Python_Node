'''
Created on May 15, 2016

@author: RizDesktop
'''

import sys
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions as bf

def sequential_actions_appium(dependency, run_time_params, step_data, file_attachment, temp_q):
    try:
        sTestStepReturnStatus = bf.Sequential_Actions_Appium(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus, temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)
