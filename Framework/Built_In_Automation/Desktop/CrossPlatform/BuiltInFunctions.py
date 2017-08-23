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
local_run = False

Passed = "Passed"
Failed = "Failed"
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr

# Recall dependency, if not already set
dependency = None
if Shared_Resources.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables('dependency') # Retreive appium driver
else:
    CommonUtil.ExecLog(__name__ + " : " + __file__, "No dependency set - Cannot run", 3)
'============================================'

'============================= Sequential Action Section Begins=============================='

file_attachment = []
if sr.Test_Shared_Variables('file_attachment'):
        file_attachment = sr.Get_Shared_Variables('file_attachment')





# Method to enter texts in a text box; step data passed on by the user
def Enter_Text_In_Text_Box(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Enter_Text_In_Text_Box", 1, local_run)
    try:
        for each in step_data:
            if "action" in each[1]:
                text_value = each[2]
            else:
                continue
                # text_value=step_data[0][len(step_data[0])-1][2]
        da.type_text(text_value)
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s" % text_value, 1,
                                       local_run)
        return "passed"

    except Exception:
        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)



# Method to click on element; step data passed on by the user
def Keystroke_For_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Keystroke_For_Element", 1, local_run)
    try:
        result = ""
        for each in step_data:
            if "action" in each[1]:
                if each[0] == "keystroke keys":
                    keystroke_value = str(each[2]).lower()

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
                    CommonUtil.ExecLog(sModuleInfo,
                                        "The correct parameter for the action has not been entered. Please check for errors.",
                                        2, local_run)
                    result = "failed"
            else:
                continue


        if (result != "failed"):
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            CommonUtil.ExecLog(sModuleInfo,
                                       "Successfully entered keystroke for the element with given parameters and values",
                                       1, local_run)
            return "passed"
        else:
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            CommonUtil.ExecLog(sModuleInfo,
                                "Could not enter keystroke for the element with given parameters and values",
                                    3, local_run)
            return "failed"

    except Exception:
        errMsg = "Could not enter keystroke for your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)



# Method to click on element; step data passed on by the user

def click_on_image(file_name, _file_attachment=[],no_of_clicks=1):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
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
        if click_status == "Failed":
            CommonUtil.ExecLog(sModuleInfo, "Could Not click on Button %s" % file_name, 3)
            return Failed
        else:
            CommonUtil.ExecLog(sModuleInfo, "Successfully Clicked on Button %s" % file_name, 1)
            return Passed

    except Exception:
        errMsg = "Unable to click using image"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)






def get_center_using_image(file_name, file_attachment):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
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


def run_cmd(command, return_status=False, is_shell=True, stdout_val=subprocess.PIPE, local_run=False):

    '''Begin Constants'''
    Passed = "Passed"
    Failed = "Failed"
    Running = 'running'
    '''End Constants'''

    # Run 'command' via command line in a bash shell, and store outputs to stdout_val
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    subprocess_dict = {}
    try:
        #global subprocess_dict
        CommonUtil.ExecLog(sModuleInfo, "Trying to run command: %s" % command, 1, local_run)

        # open a subprocess with command, and assign a session id to the shell process
        # this is will make the shell process the group leader for all the child processes spawning from it
        status = subprocess.Popen(command, shell=is_shell, stdout=stdout_val, preexec_fn=os.setsid)
        subprocess_dict[status] = Running

        if return_status:
            return status
        else:
            return Passed

    except Exception, e:
        return CommonUtil.Exception_Handler(sys.exc_info())

def close_program(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Closing program.", 1, local_run)
        if dependency['PC'].lower() == 'linux' or dependency['PC'].lower() == 'mac':
            command = 'pkill '+ step_data[0][2]
            close_status = run_cmd(command)

            if close_status == Passed:
                CommonUtil.ExecLog(sModuleInfo, "Sent signal to close program.", 0, local_run)
                return Passed
            elif close_status == Failed:
                CommonUtil.ExecLog(sModuleInfo, "Could send signal to close program.", 3, local_run)
                return Failed
        elif dependency['PC'].lower() == 'windows':
            command = "taskkill /F /IM "+step_data[0][2]+".exe"
            close_status = FU.run_win_cmd(command)

            if close_status == Passed:
                CommonUtil.ExecLog(sModuleInfo, "Sent signal to close program.", 0, local_run)
                return Passed
            elif close_status == Failed:
                CommonUtil.ExecLog(sModuleInfo, "Could send signal to close program.", 3, local_run)
                return Failed
    except Exception:
        errMsg = "Could not close the program"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Double_Click_Element(step_data, _file_attachment=[]):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if _file_attachment == []:
            global file_attachment
            _file_attachment = file_attachment
        # element_step_data = step_data[0][0:len(step_data[0])-1:1]
        returned_step_data_list = Validate_Step_Data(step_data)
        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
            return "failed"
        else:
            if returned_step_data_list[0] == 'image':
                result = click_on_image(returned_step_data_list[1],_file_attachment,2)
            else:
                CommonUtil.ExecLog(sModuleInfo,
                                       "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                                       3, local_run)

        if result!=Failed:
            CommonUtil.ExecLog(sModuleInfo,
                               "Successfully clicked on element with given images/text", 1,
                               local_run)
            return Passed
        else:
            CommonUtil.ExecLog(sModuleInfo,
                               "Couldn't click on element with given images/text", 3,
                               local_run)
            return Failed


    except Exception:
        errMsg = "Unable to click using image/text"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Click_Element(step_data, _file_attachment=[]):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
            # element_step_data = step_data[0][0:len(step_data[0])-1:1]
        if _file_attachment == []:
            global file_attachment
            _file_attachment = file_attachment

        returned_step_data_list = Validate_Step_Data(step_data)
        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
            return "failed"
        else:
            if returned_step_data_list[0] == 'image':
                result = click_on_image(returned_step_data_list[1],_file_attachment,1)
            else:
                CommonUtil.ExecLog(sModuleInfo,
                                   "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                                   3, local_run)

        if result!=Failed:
            CommonUtil.ExecLog(sModuleInfo,
                               "Successfully clicked on element with given images/text", 1,
                               local_run)
            return Passed
        else:
            CommonUtil.ExecLog(sModuleInfo,
                               "Couldn't click on element with given images/text", 3,
                               local_run)
            return Failed


    except Exception:
        errMsg = "Unable to click using image/text"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Hover_Over_Element(step_data, _file_attachment=[]):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if _file_attachment == []:
            global file_attachment
            _file_attachment = file_attachment

            # element_step_data = step_data[0][0:len(step_data[0])-1:1]
        returned_step_data_list = Validate_Step_Data(step_data)
        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
            return "failed"
        else:
            if returned_step_data_list[0] == 'image':
                center = get_center_using_image(returned_step_data_list[1],_file_attachment)
            else:
                CommonUtil.ExecLog(sModuleInfo,
                                       "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                                       3, local_run)

        gui.FAILSAFE = False
        result = gui.moveTo(center[0],center[1])


        if result!=Failed:
            CommonUtil.ExecLog(sModuleInfo,
                               "Successfully hover oover element with given images/text", 1,
                               local_run)
            return Passed
        else:
            CommonUtil.ExecLog(sModuleInfo,
                               "Couldn't hover over element with given images/text", 3,
                               local_run)
            return Failed


    except Exception:
        errMsg = "Unable to hover using image/text"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)




# Method to return pass or fail for the step outcome
def Step_Result(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Step_Result", 1, local_run)
    try:
        step_result = step_data[0][0][2]
        if step_result == 'pass':
            result = "passed"
        elif step_result == 'fail':
            result = "failed"

        return result

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())



# Validation of step data passed on by the user
def Validate_Step_Data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Step_Data", 1, local_run)
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
        CommonUtil.ExecLog(sModuleInfo, "Data set incorrect. Please provide accurate data set(s) information.", 3,
                               local_run)
        return "failed"




'===================== ===x=== Validation Section Ends ===x=== ======================'