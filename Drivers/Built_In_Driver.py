'''
Created on May 15, 2016

@author: RizDesktop
'''

import sys
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Sequential_Actions import sequential_actions as sa

def sequential_actions(dependency, run_time_params, step_data, file_attachment, temp_q,screen_capture,device_info, debug_actions=None):
    try:
        sTestStepReturnStatus = sa.Sequential_Actions(step_data,dependency,run_time_params,file_attachment,temp_q,screen_capture,device_info, debug_actions)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus, temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)
