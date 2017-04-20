'''
Created on May 15, 2016

@author: RizDesktop
'''

import os, sys
import inspect
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions as bf


def launch_application(dependency, run_time_params, step_data, file_attachment, temp_q):
    try:
        app_name = step_data[0][0][2]
        package_name = step_data[0][1][2]
        activity_name = step_data[0][2][2]
        sTestStepReturnStatus = bf.launch_and_start_driver(package_name, activity_name)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus, temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)


def close_application(dependency, run_time_params, step_data, file_attachment, temp_q):
    try:
        sTestStepReturnStatus = bf.close()
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus, temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)


def install_application(dependency, run_time_params, step_data, file_attachment, temp_q):
    try:
        app_location = step_data[0][0][1]
        package_name = step_data[0][1][1]
        activity_name = step_data[0][2][1]
        sTestStepReturnStatus = bf.install(app_location, package_name, activity_name)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus, temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)


def remove_application(dependency, run_time_params, step_data, file_attachment, temp_q):
    try:
        app_package = step_data[0][0][1]
        sTestStepReturnStatus = bf.remove(app_package)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus, temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)


def click_element_appium(dependency, run_time_params, step_data, file_attachment, temp_q):
    try:
        element_parameter = step_data[0][0][0]
        element_value = step_data[0][0][2]
        sTestStepReturnStatus = bf.Click_Element(element_parameter, element_value)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus, temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)


def enter_text_appium(dependency, run_time_params, step_data, file_attachment, temp_q):
    try:
        element_parameter = step_data[0][0][0]
        element_value = step_data[0][0][2]
        text_value = step_data[0][1][2]
        sTestStepReturnStatus = bf.Set_Text(element_parameter, element_value, text_value)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus, temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)


def sequential_actions_appium(dependency, run_time_params, step_data, file_attachment, temp_q):
    try:
        sTestStepReturnStatus = bf.Sequential_Actions(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus, temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)
