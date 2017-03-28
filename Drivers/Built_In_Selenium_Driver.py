'''
Created on May 15, 2016

@author: AutomationSolutionz Inc.
'''

import sys
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as Selenium_Built_In

def open_browser(dependency,run_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus = Selenium_Built_In.Open_Browser(dependency)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)

def go_to_webpage(dependency,run_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus=Selenium_Built_In.Go_To_Link(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)

def enter_text_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus=Selenium_Built_In.Enter_Text_In_Text_Box(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)

def keystroke_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus=Selenium_Built_In.Keystroke_For_Element(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)

def click_element_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus=Selenium_Built_In.Click_Element(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)

def hover_over_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus=Selenium_Built_In.Hover_Over_Element(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)
   
def wait_for_element_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus=Selenium_Built_In.Wait_For_New_Element(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)

def validate_text_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus=Selenium_Built_In.Validate_Text(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)


def sleep_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus=Selenium_Built_In.Sleep(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)

def scroll_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus=Selenium_Built_In.Scroll(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)

def step_result_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus=Selenium_Built_In.Step_Result(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)

def sequential_actions_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus=Selenium_Built_In.Sequential_Actions(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)

def validate_table_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus=Selenium_Built_In.Validate_Table(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)

def tear_down_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    try:
        sTestStepReturnStatus=Selenium_Built_In.Tear_Down_Selenium()
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)


