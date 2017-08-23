# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
'''
Created on May 15, 2016

@author: Built_In_Automation Solutionz Inc.
'''


import pyautogui as gui
import os,sys,time
import inspect
import subprocess
from Framework.Utilities import CommonUtil, FileUtilities  as FL
from Framework.Built_In_Automation.Desktop.CrossPlatform import DesktopAutomation as da
from Framework.Built_In_Automation.Built_In_Utility.CrossPlatform import BuiltInUtilityFunction as FU
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list, skipped_tag_list # Allowed return strings, used to normalize pass/fail
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr

# Recall dependency, if not already set
dependency = None
if Shared_Resources.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables('dependency') # Retreive appium driver
else:
    CommonUtil.ExecLog(__name__ + " : " + __file__, "No dependency set - Cannot run", 3)

# Recall file attachment, if not already set
file_attachment = []
if sr.Test_Shared_Variables('file_attachment'):
    file_attachment = sr.Get_Shared_Variables('file_attachment')

''' **************************** Helper functions **************************** '''



# Validation of step data passed on by the user
def Validate_Step_Data(step_data): 
    ''' !!! This needs to be deleted ??? '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        element_parameter = step_data[0][0]
        element_value = step_data[0][2]
        reference_parameter = False
        reference_value = False
        reference_is_parent_or_child = False
        validated_data = (
                element_parameter, element_value, reference_parameter, reference_value, reference_is_parent_or_child)
        return validated_data
    except:
        CommonUtil.ExecLog(sModuleInfo, "Data set incorrect. Please provide accurate data set(s) information.", 3)
        return "failed"

def get_center_using_image(file_name, file_attachment):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        logo = None
        # Loop through data sets to see if ok_logo/program_logo/config_logo text is present in any data field
        logo = file_attachment[file_name]
        CommonUtil.ExecLog(sModuleInfo, "Trying to Click Button Logo: %s" % file_name)
        result = da.getCenter(logo)
        return result


    except Exception:
        errMsg = "Unable to get center using image"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


# Method to click on element; step data passed on by the user
def click_on_image(file_name, _file_attachment=[],no_of_clicks=1):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        if _file_attachment == []:
            global file_attachment
            _file_attachment = file_attachment

        logo = None
        # Loop through data sets to see if ok_logo/program_logo/config_logo text is present in any data field
        logo = _file_attachment[file_name]


        CommonUtil.ExecLog(sModuleInfo, "Trying to Click Button Logo: %s" % file_name)

        click_status = da.click(logo, no_of_clicks)
        time.sleep(5)
        if click_status in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could Not click on Button %s" % file_name, 3)
            return 'failed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Successfully Clicked on Button %s" % file_name, 1)
            return 'passed'

    except Exception:
        errMsg = "Unable to click using image"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

''' *********************************** Sequential Actions ************************************************ '''

# Method to enter texts in a text box; step data passed on by the user
def Enter_Text_In_Text_Box(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        for row in data_set:
            if "action" in row[1]:
                text_value = row[2]
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())
    
    try:
        da.type_text(text_value)
        CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s" % text_value, 1)
        return "passed"

    except Exception:
        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)



# Method to click on element; step data passed on by the user
def Keystroke_For_Element(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        result = ""
        for row in data_set:
            if "action" in row[1]:
                if row[0] == "keystroke keys":
                    keystroke_value = str(row[2]).lower()

                    keys = keystroke_value.split('+')

                    keys_list = []
                    for each in keys:
                        keys_list.append(each.strip())

                    print keys_list

                    i = 1
                    for each in keys_list:
                        if i == len(keys_list):
                            gui.press(each)
                        else:
                            gui.keyDown(each)
                        i += 1

                    time.sleep(5)

                    for each in keys_list:
                        gui.keyUp(each)


                else:
                    CommonUtil.ExecLog(sModuleInfo, "Invalid action found", 3)
                    return 'failed'


        CommonUtil.ExecLog(sModuleInfo,"Successfully entered keystroke", 1)
        return 'passed'

    except Exception:
        errMsg = "Could not enter keystroke for your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)




def close_program(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        if dependency['PC'].lower() == 'linux' or dependency['PC'].lower() == 'mac':
            command = 'pkill '+ data_set[2]
            close_status = FU.run_cmd(command)

            if close_status in passed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Sent signal to close program.", 1)
                return 'passed'
            elif close_status in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could send signal to close program.", 3)
                return 'failed'
            
        elif dependency['PC'].lower() == 'windows':
            command = "taskkill /F /IM " + data_set[2] + ".exe"
            close_status = FU.run_win_cmd(command)

            if close_status in passed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Sent signal to close program.", 1)
                return 'passed'
            elif close_status in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could send signal to close program.", 3)
                return 'failed'
            
    except Exception:
        errMsg = "Could not close the program"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Double_Click_Element(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    _file_attachment = '' #!!!! Not sure what this is,but it needs to be handled
    
    try:
        returned_step_data_list = Validate_Step_Data([data_set])

        if ((returned_step_data_list == []) or (returned_step_data_list in failed_tag_list)):
            return "failed"
        else:
            if returned_step_data_list[0] == 'image':
                result = click_on_image(returned_step_data_list[1],_file_attachment,2)
            else:
                CommonUtil.ExecLog(sModuleInfo,"", 3)

        if result in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,
                               "Successfully clicked on element with given images/text", 1)
            return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Couldn't click on element with given images/text", 3)
            return 'failed'


    except Exception:
        errMsg = "Unable to click using image/text"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Click_Element(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    _file_attachment = '' #!!!! Not sure what this is,but it needs to be handled
    
    try:
        returned_step_data_list = Validate_Step_Data([data_set])
        
        if ((returned_step_data_list == []) or (returned_step_data_list in failed_tag_list)):
            return "failed"
        
        else:
            if returned_step_data_list[0] == 'image':
                result = click_on_image(returned_step_data_list[1],_file_attachment,1)
            else:
                CommonUtil.ExecLog(sModuleInfo,"This error needs more definition !!!", 3) #!!!

        if result in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Successfully clicked on element with given images/text", 1)
            return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Couldn't click on element with given images/text", 3)
            return 'failed'


    except Exception:
        errMsg = "Unable to click using image/text"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Hover_Over_Element(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    _file_attachment = '' #!!!! Not sure what this is,but it needs to be handled
    
    try:
        returned_step_data_list = Validate_Step_Data([data_set])

        if ((returned_step_data_list == []) or (returned_step_data_list in failed_tag_list)):
            return "failed"
        
        else:
            if returned_step_data_list[0] == 'image':
                center = get_center_using_image(returned_step_data_list[1],_file_attachment)
            else:
                CommonUtil.ExecLog(sModuleInfo,"This error needs to be defined !!!", 3) #!!!

        gui.FAILSAFE = False
        result = gui.moveTo(center[0],center[1])


        if result in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Successfully hover oover element with given images/text", 1)
            return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Couldn't hover over element with given images/text", 3)
            return 'failed'

    except Exception:
        errMsg = "Unable to hover using image/text"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


