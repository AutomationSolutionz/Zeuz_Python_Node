'''
Created on April 11, 2017

@author: AutomationSolutionz Inc.
'''

import os,sys
import inspect
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Desktop.Windows import NETAutomation


def copy_attachments_to_sharepoint(dependency,run_time_params,step_data,file_attachment,temp_q,screen_capture,device_info):
    try:
        sTestStepReturnStatus=NETAutomation.save_email_attachment_to_sharepoint(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)

def view_info_about_colligo(dependency,run_time_params,step_data,file_attachment,temp_q,screen_capture):
    try:
        sTestStepReturnStatus=NETAutomation.view_info_about_colligo(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)

def synchronize_all_emails_using_colligo(dependency,run_time_params,step_data,file_attachment,temp_q,screen_capture,device_info):
    try:
        sTestStepReturnStatus=NETAutomation.synchronize_all_emails_using_colligo(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)