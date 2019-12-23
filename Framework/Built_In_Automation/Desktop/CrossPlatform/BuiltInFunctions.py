# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
'''
    Created on May 15, 2016

    @author: Built_In_Automation Solutionz Inc.
    Name: Built In Functions - Desktop (using PyAutoGui)
    Description: Sequential Actions for controlling the desktop on Linux/Windows/Mac
'''

#########################
#                       #
#        Modules        #
#                       #
#########################

import pyautogui as gui # https://pyautogui.readthedocs.io/en/latest/
import os, os.path, sys, time, inspect, subprocess
from Framework.Utilities import CommonUtil, FileUtilities  as FL
from Framework.Built_In_Automation.Built_In_Utility.CrossPlatform import BuiltInUtilityFunction as FU
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list, skipped_tag_list # Allowed return strings, used to normalize pass/fail
from Framework.Built_In_Automation.Shared_Resources import LocateElement

# Disable pyautogui failsafe when moving to top left corner
gui.FAILSAFE = False

#########################
#                       #
#    Global Variables   #
#                       #
#########################

MODULE_NAME = inspect.getmodulename(__file__)

# Valid image positions
positions = ('left', 'right', 'centre', 'center')

# Recall dependency, if not already set
dependency = None
if Shared_Resources.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables('dependency') # Retreive appium driver
else:
    raise ValueError("No dependency set - Cannot run")

# Recall file attachment, if not already set
file_attachment = []
if Shared_Resources.Test_Shared_Variables('file_attachment'):
    file_attachment = Shared_Resources.Get_Shared_Variables('file_attachment')

#########################
#                       #
#   Helper Functions    #
#                       #
#########################

def get_driver():
    ''' Returns pyautogui as the driver for compatibility with other modules '''
    return gui

def getCoordinates(element, position):
    ''' Return coordinates of attachment's centre '''
    
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    # Parse input
    try:
        x = element[0]
        y = element[1]
        w = element[2]
        h = element[3]
        position = position.lower().strip()
        
        if position not in positions:
            CommonUtil.ExecLog(sModuleInfo,"Position must be one of: %s" % positions, 3)
            return 'failed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing coordinates")
    
    # Perform calculations
    try:
        if position in ('center', 'centre'):
            result_x, result_y = gui.center(element)
        elif position == 'left':
            result_x = x + (w * 0.01)
            result_y = y + (h / 2)
        elif position == 'right':
            result_x = x + (w * 0.99)
            result_y = y + (h / 2)

        if result_x in failed_tag_list or result_x == '' or result_x == None:
            return 'failed', ''
        return int(result_x), int(result_y)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error calculating coordinates")

def get_exec_from_icon(file_name):
    ''' Read the Exec line from a Linux icon file '''
    
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
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


#########################
#                       #
#  Sequential Actions   #
#                       #
#########################

def Enter_Text(data_set):
    ''' Insert text '''
    
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Parse data set
    try:
        element_parameter = False
        text_value = ''
        for row in data_set:
            if "action" in row[1]:
                text_value = row[2]
            if row[1] == 'element parameter': # Indicates we should find the element instead of assuming we have keyboard focus
                element_parameter = True
                
        if text_value == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find value for this action", 3)
            return 'failed'
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")
    
    # Perform action
    try:
        # Find image coordinates
        if element_parameter:
            CommonUtil.ExecLog(sModuleInfo, "Trying to locate element", 0)
            element = LocateElement.Get_Element(data_set, gui) # (x, y, w, h)
            if element in failed_tag_list: # Error reason logged by Get_Element
                CommonUtil.ExecLog(sModuleInfo, "Could not locate element", 3)
                return 'failed'
            
            # Get coordinates for position user specified
            x, y = getCoordinates(element, 'centre') # Find coordinates (x,y)
            if x in failed_tag_list: # Error reason logged by Get_Element
                CommonUtil.ExecLog(sModuleInfo, "Error calculating coordinates", 3)
                return 'failed'
            CommonUtil.ExecLog(sModuleInfo, "Image coordinates on screen %d x %d" % (x, y), 0)
            gui.click(x, y) # Single click
        else:
            CommonUtil.ExecLog(sModuleInfo, "No element provided. Assuming textbox has keyboard focus", 0)

        CommonUtil.TakeScreenShot(sModuleInfo) # Capture screenshot, if settings allow for it
                
        # Enter text
        gui.typewrite(text_value)
        CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s" % text_value, 1)
        return "passed"

    except Exception:
        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)



def Keystroke_For_Element(data_set):
    ''' Insert characters - mainly key combonations'''
    # Example: Ctrl+c
    # Repeats keypress if a number follows, example: tab,3 
    
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
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

        CommonUtil.TakeScreenShot(sModuleInfo) # Capture screenshot, if settings allow for it
        
        CommonUtil.ExecLog(sModuleInfo,"Successfully entered keystroke", 1)
        return 'passed'

    except Exception:
        errMsg = "Could not enter keystroke for your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def close_program(data_set):
    ''' Exit a running program via process kill '''
    
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Parse data set
    try:
        program_name = ''
        for row in data_set:
            if row[1] == 'action':
                program_name = row[2] # Program name passed by user
                
        if program_name == '':
            CommonUtil.ExecLog(sModuleInfo,"Expected a program name in Value", 3)
            return 'failed'
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    # Perform action    
    try:
        if dependency['PC'].lower() == 'linux' or dependency['PC'].lower() == 'mac':
            command = 'pkill -f '+ program_name # Try Process Kill with full command checking set, which finds most programs automatically
            close_status, output = FU.run_cmd(command, return_status=True) # Execute command and return the return code

            # Check result
            if close_status == None or close_status < 1:
                close_status = 'passed'

            # pkill failed, try another method
            else:
                CommonUtil.ExecLog(sModuleInfo,"pKill command failed, trying another method", 0)
                command = "ps aux | grep -i '%s' | grep -v grep | awk '{print $2}'" % program_name # Try to find the PID
                close_status, output = FU.run_cmd(command, return_status=True) # Run the command above and return the output which should contain a list of PIDs found
                if output != []:
                    output = output[0].strip() # First PID found
                    close_status = FU.run_cmd("kill -9 %s" % output) # Send the terminate signal to this PID
                else: close_status = 'failed' # No PID received - error occurred or program doesn't exist

        elif dependency['PC'].lower() == 'windows':
            command = "taskkill /F /IM " + program_name + ".exe"
            close_status = FU.run_win_cmd(command)

        else:
            CommonUtil.ExecLog(sModuleInfo, "Uknown dependency %s" % dependency['PC'], 3)
            return 'failed'

        CommonUtil.TakeScreenShot(sModuleInfo) # Capture screenshot, if settings allow for it
        
        # Check result
        if close_status in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not send signal to close program.", 3)
            return 'failed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Sent signal to close program.", 1)
            return 'passed'
        
            
    except Exception:
        errMsg = "Could not close the program"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def move_mouse(data_set):
    ''' Hover over element or move to specified x,y coordinates '''

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Parse data set
    try:
        cmd = ''
        file_name = ''
        position = 'centre'
        for row in data_set:
            if row[1] == 'action':
                if row[0] == 'hover':
                    cmd = 'hover'
                    position = row[2] # Store coordinates
                elif row[0] == 'move':
                    cmd = 'move'
                    file_name = row[2] # Store position (see positions at top)
            elif row[1] == 'element parameter':
                file_name = row[2] # Store filename for hover
        
        if cmd == '':
            CommonUtil.ExecLog(sModuleInfo, "Valid action not found. Expected Field set to 'move' or 'hover'", 3)
            return 'failed'
        
        if cmd == 'hover':
            if file_name == '':
                CommonUtil.ExecLog(sModuleInfo, "Valid element not found. Expected Sub-Field to be 'element parameter', and Value to be a filename", 3)
                return 'failed'
            if position not in positions:
                CommonUtil.ExecLog(sModuleInfo, "Will click on centre of element. Expected Value to be one of: %s" % str(positions), 2)
                position = 'centre'
        elif cmd == 'move':
            if file_name == '':
                CommonUtil.ExecLog(sModuleInfo, "Valid action not found. Expected Value to be coordinates in format of 'x,y'", 3)
                return 'failed'
        
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)    

    # Perform action
    try:
        if cmd == 'hover':
            # Find image coordinates
            CommonUtil.ExecLog(sModuleInfo, "Performing %s action on file %s" % (cmd, file_name), 0)
            element = LocateElement.Get_Element(data_set, gui) # (x, y, w, h)
            if element in failed_tag_list: # Error reason logged by Get_Element
                CommonUtil.ExecLog(sModuleInfo, "Could not locate element", 3)
                return 'failed'
            
            # Get coordinates for position user specified
            x, y = getCoordinates(element, position) # Find coordinates (x,y)
            if x in failed_tag_list: # Error reason logged by Get_Element
                CommonUtil.ExecLog(sModuleInfo, "Error calculating coordinates", 3)
                return 'failed'
            CommonUtil.ExecLog(sModuleInfo, "Image coordinates on screen %d x %d" % (x, y), 0)
        
        elif cmd == 'move':
            try:
                if ',' not in file_name:
                    CommonUtil.ExecLog(sModuleInfo, "Expected Value to be 'X,Y' format for coordinates. If you want to use an image, try using the 'hover' action", 3)
                    return 'failed'
                
                x, y = file_name.replace(' ', '').split(',') # Get the coordinates
                x = int(x)
                y = int(y)
            except:
                return CommonUtil.Exception_Handler(sys.exc_info(), None, "Expected Value to be 'X,Y' format for coordinates. If you want to use an image, try using the 'hover' action")

        # Move mouse pointer
        CommonUtil.ExecLog(sModuleInfo, "Image coordinates on screen %d x %d" % (x, y), 0)
        result = gui.moveTo(x, y) # Move to element / Hover over element

        CommonUtil.TakeScreenShot(sModuleInfo) # Capture screenshot, if settings allow for it

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
    
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Parse data set
    try:
        cmd = ''
        file_name = ''
        position = 'centre'
        for row in data_set:
            if row[1] == 'action':
                if row[0] == 'click':
                    cmd = 'click'
                    position = row[2]
                elif row[0] in ('doubleclick', 'double click'):
                    cmd = 'doubleclick'
                    position = row[2]
            elif row[1] == 'element parameter':
                file_name = row[2]
        
        if cmd == '':
            CommonUtil.ExecLog(sModuleInfo, "Valid action not found. Expected Field set to 'click' or 'doubleclick', and the Value one of: %s" % str(positions), 3)
            return 'failed'
        if position not in positions:
            CommonUtil.ExecLog(sModuleInfo, "Will click on centre of element. Expected Value to be one of: %s" % str(positions), 2)
            position = 'centre'
        
        if file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Valid element not found. Expected Sub-Field to be 'element parameter', and Value to be a filename", 3)
            return 'failed'
        
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    # Perform action
    try:
        # Find image coordinates
        CommonUtil.ExecLog(sModuleInfo, "Performing %s action on file %s" % (cmd, file_name), 0)
        element = LocateElement.Get_Element(data_set, gui) # (x, y, w, h)
        if element in failed_tag_list: # Error reason logged by Get_Element
            CommonUtil.ExecLog(sModuleInfo, "Could not locate element", 3)
            return 'failed'
        
        # Get coordinates for position user specified
        x, y = getCoordinates(element, position) # Find coordinates (x,y)
        if x in failed_tag_list: # Error reason logged by Get_Element
            CommonUtil.ExecLog(sModuleInfo, "Error calculating coordinates", 3)
            return 'failed'
        CommonUtil.ExecLog(sModuleInfo, "Image coordinates on screen %d x %d" % (x, y), 0)
        
        # Click on image
        if cmd == 'click':
            result = gui.click(x, y) # Single click
        elif cmd == 'doubleclick':
            result = gui.doubleClick(x, y) # Double click

        CommonUtil.TakeScreenShot(sModuleInfo) # Capture screenshot, if settings allow for it
        
        # Check result and return
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

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    # Parse data set
    try:
        file_name = ''
        for row in data_set:
            if row[1] == 'element parameter':
                file_name = row[2]
        
        if file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Valid element not found. Expected Sub-Field to be 'element parameter', and Value to be a filename", 3)
            return 'failed'
        
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    # Perform action
    try:
        CommonUtil.ExecLog(sModuleInfo, "Performing check action on file %s" % (file_name), 0)
        element = LocateElement.Get_Element(data_set, gui) # (x, y, w, h)
        
        CommonUtil.TakeScreenShot(sModuleInfo) # Capture screenshot, if settings allow for it
        
        if element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return 'failed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Found element", 1)
            return 'passed'
        
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def launch_program(data_set):
    ''' Execute a program or desktop icon '''
    # If a linux desktop icon filename is specified, then it will read the file, and extract the Exec line to execute it directly
    # Anything else is executed, including if it's an attachment

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    # Parse data set
    try:
        file_name = data_set[0][2] # Get filename from data set
        Command = ''
        if file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Value field empty. Expected filename or full file path", 3)
            return 'failed'
    except:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Execute program    
    try:
        # Check if filename from data set is an icon file on the desktop by using full or partial match
        path = os.path.join(FU.get_home_folder(), 'Desktop') # Prepare path for desktop if needed
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))] # Get list of files in specified directory
        for f in files: # For each file found
            if file_name in f: # If filename from data set matches fully or partially
                # Save full path/file
                file_name = os.path.join(path, f)

                # Read first line to check if it's an icon file
                with open(file_name, "rb") as myfile:
                    data = myfile.read()[:16]
                    if data.strip() == "[Desktop Entry]":
                        Command = get_exec_from_icon(file_name)
                
                break

        # Try to find the image file
        if file_name not in file_attachment and os.path.exists(file_name) == False:
            CommonUtil.ExecLog(sModuleInfo, "Could not find file attachment called %s, and could not find it locally" % file_name, 3)
            return 'failed'
        if file_name in file_attachment:
            Command = file_attachment[file_name] # In file is an attachment, get the full path
        elif os.path.exists(file_name) and Command == '': # User provided correct path
            Command = file_name

        # Now file_name should have a directory/file pointing to the correct image

        # Execute program
        if dependency['PC'].lower() == 'linux' or dependency['PC'].lower() == 'mac':
            launch_status = subprocess.Popen(Command.split(' ')) # FU.run_cmd() blocks further execution, so we'll just use subprocess here

        elif dependency['PC'].lower() == 'windows':
            launch_status = FU.run_win_cmd(Command)

        else:
            CommonUtil.ExecLog(sModuleInfo, "Unknown dependency %s" % dependency['PC'], 3)
            return 'failed'

        CommonUtil.TakeScreenShot(sModuleInfo) # Capture screenshot, if settings allow for it
        
        # Check result and return
        if launch_status in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not launch the program", 3)
            return 'failed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Program launched successfully.", 1)
            return 'passed'


    except Exception:
        errMsg = "Can't execute the program"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
    
def teardown(data_set):
    ''' Cleanup automation '''
    
    # Cleanup shared variables
    Shared_Resources.Clean_Up_Shared_Variables()
    return 'passed'

def Drag_Element(data_set):
    ''' Drag element from source to destination '''
    
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Parse data set
    try:
        cmd = ''
        file_name = ''
        src_file_name = ''
        position = 'centre'
        for row in data_set:
            if row[1] == 'action':
                if row[0] == 'drag':
                    cmd = 'drag'
                    position = row[2]
            elif row[1] == 'element parameter':
                file_name = row[2]
            elif row[1] == 'source parameter':
                src_file_name = row[2]
        
        if cmd == '':
            CommonUtil.ExecLog(sModuleInfo, "Valid action not found. Expected Field set to 'click' or 'doubleclick', and the Value one of: %s" % str(positions), 3)
            return 'failed'
        if position not in positions:
            CommonUtil.ExecLog(sModuleInfo, "Will click on centre of element. Expected Value to be one of: %s" % str(positions), 2)
            position = 'centre'
        
        if file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Valid element not found. Expected Sub-Field to be 'element parameter', and Value to be a filename", 3)
            return 'failed'
        
        if src_file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Valid element not found. Expected Sub-Field to be 'source parameter', and Value to be a filename", 3)
            return 'failed'
        
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    # Perform action
    try:
        # Get coordinates for source and destiniation
        for filename in (file_name, src_file_name):
            tmp_data_set = [('image', 'element parameter', filename)]
            # Find image coordinates for destination element
            CommonUtil.ExecLog(sModuleInfo, "Performing %s action on file %s" % (cmd, filename), 0)
            element = LocateElement.Get_Element(tmp_data_set, gui) # (x, y, w, h)
            if element in failed_tag_list: # Error reason logged by Get_Element
                CommonUtil.ExecLog(sModuleInfo, "Could not locate element: %s" % filename, 3)
                return 'failed'
    
            # DESTINATION  Get coordinates for position user specified
            x, y = getCoordinates(element, position) # Find coordinates (x,y)
            if x in failed_tag_list: # Error reason logged by Get_Element
                CommonUtil.ExecLog(sModuleInfo, "Error calculating coordinates", 3)
                return 'failed'
            CommonUtil.ExecLog(sModuleInfo, "Image coordinates on screen %d x %d" % (x, y), 0)
            
            # Put the x,y in usable variables
            if filename == file_name:
                dst_x, dst_y = x, y
            else:
                src_x, src_y = x, y

        # Drag source to destination
        gui.moveTo(src_x, src_y) # Move to source
        result = gui.dragTo(dst_x, dst_y, 2, button = 'left') # Click and drag to destination, taking two seconds, then release - the 2 seconds is important for some drags because without the time, it happens too fast and the drag command is missed by the window manager

        CommonUtil.TakeScreenShot(sModuleInfo) # Capture screenshot, if settings allow for it
        
        # Check result and return
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Couldn't dragged element with given images", 3)
            return 'failed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Successfully dragged element with given images", 1)
            return 'passed'

    except Exception:
        errMsg = "Error while trying to perform drag action"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def navigate_listbox(data_set):
    ''' Scroll listbox until image element is found or timeout is hit '''
    # Continually presses page down and checks for the image
    # Assumptions: Listbox already has focus - user ought to use click action to click on the listbox, or the drop down menu's arrow
    # Assumptions: User has image of the list item they want to find
    # Produces: Pass/Fail - User is responsible for performing the action they desire now that the listbox is where their element is visible
    
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Maximum number of tries to find the element. Have no way of knowing when we hit the last list item, so we have to hard code a value
    max_tries = 10
    
    # Delay before checking for image element
    delay = 1
    
    # Parse data set
    try:
        file_name = ''
        for row in data_set:
            if row[1] == 'element parameter':
                file_name = row[2]
            elif row[1] == 'action':
                try:
                    delay = int(row[2]) # Test if user specified a delay on the action line
                    CommonUtil.ExecLog(sModuleInfo, "Using customer specified delay of %d" % delay, 1)
                except: delay = 1 # Default delay - user did not specify
        
        if file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Valid element not found. Expected Sub-Field to be 'element parameter', and Value to be a filename", 3)
            return 'failed'
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    # Perform action
    try:
        # Get coordinates for source and destiniation
        for i in range(max_tries):
            CommonUtil.ExecLog(sModuleInfo, "Checking listbox for element", 0)
            element = LocateElement.Get_Element(data_set, gui) # (x, y, w, h)
            if element in failed_tag_list: # Error reason logged by Get_Element
                CommonUtil.ExecLog(sModuleInfo, "Could not locate element - trying a new position. Attempt #%d" % i, 0)
                gui.hotkey('pgdn')
                time.sleep(delay) # Wait for listbox to update
            else:
                CommonUtil.ExecLog(sModuleInfo, "Found element", 1)
                return 'passed'
        
        CommonUtil.TakeScreenShot(sModuleInfo) # Capture screenshot, if settings allow for it
        
        CommonUtil.ExecLog(sModuleInfo, "Could not locate element after %d attempts" % max_tries, 3)
        return 'failed'
    
    except Exception:
        errMsg = "Error while trying to perform drag action"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    