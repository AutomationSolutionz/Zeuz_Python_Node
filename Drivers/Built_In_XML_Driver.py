'''
Created on Apr 20, 2017

@author: mchowdhury
Comment: Not published yet
'''

import sys
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.XML import BuiltInFunctions_XML


def sequential_actions_xml(dependency,run_time_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus = BuiltInFunctions_XML.xml_sequential_actions(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)    
    except Exception:
        errMsg = "Unable to perform action on target element."
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q, errMsg)