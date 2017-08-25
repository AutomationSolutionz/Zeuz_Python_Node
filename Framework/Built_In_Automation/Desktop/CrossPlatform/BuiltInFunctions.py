# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
'''
Created on May 15, 2016

@author: Built_In_Automation Solutionz Inc.
'''


import pyautogui as gui # https://pyautogui.readthedocs.io/en/latest/
import os, os.path, sys, time, inspect
from Framework.Utilities import CommonUtil, FileUtilities  as FL
#from Framework.Built_In_Automation.Desktop.CrossPlatform import DesktopAutomation as da
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


def get_center_using_image(file_name):
    ''' Return coordinates of attachment's centre '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        result = gui.center(file_attachment[file_name]) # Get coordinates of centre of image
        
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Looking for centre of image %s" % file_name, 0)
            return 'failed'
        CommonUtil.ExecLog(sModuleInfo, "Successfully found centre of image", 0)
        return result


    except Exception:
        errMsg = "Unable to get center using image"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_exec_from_icon(file_name):
    ''' Read the Exec line from a Linux icon file '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    try:
        # Open file and read into memory
        with open(file_name, "r") as myfile:
            data = myfile.readlines()
            
        # Examine each line, looking for the Exec line
        for element in data:
            if element[:5] == "Exec=":
                result = element[5:].strip() # Save execution line without the Exec= part
        
        if result == '':
            return 'failed'
        return result

    except Exception:
        errMsg = "Can't get the exec of the file"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


''' *********************************** Sequential Actions ************************************************ '''

def Enter_Text(data_set):
    ''' Insert text '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Parse data set
    try:
        text_value = ''
        for row in data_set:
            if "action" in row[1]:
                text_value = row[2]
                
        if text_value == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find value for this action", 3)
            return 'failed'
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")
    
    # Perform action
    try:
        gui.typewrite(text_value)
        CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s" % text_value, 1)
        return "passed"

    except Exception:
        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)



def Keystroke_For_Element(data_set):
    ''' Insert characters - mainly key combonations'''
    # Example: Ctrl+c
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Parse dataset
    try:
        keystroke_value = ''
        for row in data_set:
            if "action" in row[1]:
                if row[0] == "keystroke keys":
                    keystroke_value = str(row[2]).lower() # Store keystrok

        if keystroke_value == '':
            CommonUtil.ExecLog(sModuleInfo, "Invalid action found", 3)
            return 'failed'

    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    # Perform action
    try:
        count = 1
        if ',' in keystroke_value: # Check for delimiter indicating multiple keystrokes
            keystroke_value, count = keystroke_value.split(',') # Separate keystroke and count
            count = int(count.strip())
        keys = keystroke_value.split('+') # Split string into array
        keys = [x.strip() for x in keys] # Clean it up
        
        for i in range(count): gui.hotkey(*keys) # Send keypress (as individual values using the asterisk)

        CommonUtil.ExecLog(sModuleInfo,"Successfully entered keystroke", 1)
        return 'passed'

    except Exception:
        errMsg = "Could not enter keystroke for your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def close_program(data_set):
    ''' Exit a running program via process kill '''
    
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
        else:
            CommonUtil.ExecLog(sModuleInfo, "Uknown dependency %s" % dependency['PC'], 3)
            return 'failed'
            
    except Exception:
        errMsg = "Could not close the program"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def move_mouse(data_set):
    ''' Hover over element or move to coordinates '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Parse data set
    try:
        cmd = ''
        file_name = ''
        for row in data_set:
            if row[1] == 'action':
                if row[0] == 'move':
                    cmd = 'move'
                    file_name = row[2] # Just re-using the same filename, even though this is not a file. Should be "x,y"
                if row[0] == 'hover':
                    cmd = 'hover'
                    file_name = row[2]
        
        if cmd == '' or file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Valid action not found. Exected Field set to 'click' or 'doubleclick', and the Value set to a filename representing an attachment", 3)
            return 'failed'
        
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    # Perform action
    try:
        if cmd == 'hover':
            if file_name not in file_attachment and os.path.exists(file_name) == False:
                CommonUtil.ExecLog(sModuleInfo, "Could not find file attachment called %s, and could not find it locally" % file_name, 3)
                return 'failed'
            if file_name in file_attachment: file_name = file_attachment[file_name] # In file is an attachment, get the full path

            # Find image, and get coordinates of centre
            CommonUtil.ExecLog(sModuleInfo, "Performing %s action on file %s" % (cmd, file_name), 0)
            element = gui.locateOnScreen(file_name) # Get coordinates of element
            x, y = gui.center(element) # Find centre
        
        elif cmd == 'move':
            x, y = file_name.replace(' ', '').split(',') # Get the coordinates
            x = int(x)
            y = int(y)

        CommonUtil.ExecLog(sModuleInfo, "Image coordinates on screen %d x %d" % (x, y), 0)
        result = gui.moveTo(x, y) # Move to element / Hover over element


        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Couldn't move mouse pointer", 3)
            return 'failed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Successfully mouse pointer", 1)
            return 'passed'

    except Exception:
        errMsg = "Error while trying to move mouse pointer"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Click_Element(data_set):
    ''' Single or double mouse click on element '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Parse data set
    try:
        cmd = ''
        file_name = ''
        for row in data_set:
            if row[1] == 'action':
                if row[0] == 'click':
                    cmd = 'click'
                    file_name = row[2]
                elif row[0] in ('doubleclick', 'double click'):
                    cmd = 'doubleclick'
                    file_name = row[2]
        
        if cmd == '' or file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Valid action not found. Exected Field set to 'click' or 'doubleclick', and the Value set to a filename representing an attachment", 3)
            return 'failed'
        
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    # Perform action
    try:
        if file_name not in file_attachment and os.path.exists(file_name) == False:
            CommonUtil.ExecLog(sModuleInfo, "Could not find file attachment called %s, and could not find it locally" % file_name, 3)
            return 'failed'
        if file_name in file_attachment: file_name = file_attachment[file_name] # In file is an attachment, get the full path

        # Find image, and get coordinates of centre
        CommonUtil.ExecLog(sModuleInfo, "Performing %s action on file %s" % (cmd, file_name), 0)
        element = gui.locateOnScreen(file_name) # Get coordinates of element
        x, y = gui.center(element) # Find centre
        CommonUtil.ExecLog(sModuleInfo, "Image coordinates on screen %d x %d" % (x, y), 0)
        
        # Click on image
        if cmd == 'click':
            result = gui.click(x, y) # Single click
        elif cmd == 'doubleclick':
            result = gui.doubleClick(x, y) # Double click

        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Couldn't click on element with given images", 3)
            return 'failed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Successfully clicked on element with given images", 1)
            return 'passed'

    except Exception:
        errMsg = "Error while trying to perform click action"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def check_for_element(data_set):
    ''' Tests whether or not an element is visible on screen '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    try:
        file_name = ''
        for row in data_set:
            if row[1] == 'action' and row[0] == 'check':
                file_name = row[2]
                
        if file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find action. Expected 'check' in Field and filename in Value", 3)
            return 'failed'
        
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    try:
        CommonUtil.ExecLog(sModuleInfo, "Performing check action on file %s" % (file_name), 0)
        element = gui.locateOnScreen(file_name) # Get coordinates of element
        if element:
            CommonUtil.ExecLog(sModuleInfo, "Found element", 1)
            return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return 'failed'
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

