# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
"""
    Automation Solutionz Inc.
    Name: Built In Functions - Desktop (using PyAutoGui)
    Description: Sequential Actions for controlling the desktop on Linux/Windows/Mac
"""

#########################
#                       #
#        Modules        #
#                       #
#########################
try:
    import pyautogui as gui
except:
    True  # https://pyautogui.readthedocs.io/en/latest/
from fileinput import filename
import os, os.path, sys, time, inspect, subprocess
from turtle import right

from Framework.Utilities import CommonUtil, FileUtilities as FL
from Framework.Utilities.decorators import logger
from Framework.Built_In_Automation.Built_In_Utility.CrossPlatform import BuiltInUtilityFunction as FU
# from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as Shared_Resources,
)
from Framework.Utilities.CommonUtil import (
    passed_tag_list,
    failed_tag_list,
    skipped_tag_list,
)  # Allowed return strings, used to normalize pass/fail
from Framework.Built_In_Automation.Shared_Resources import LocateElement
from Framework.Built_In_Automation.Desktop.RecordPlayback.ChoosePlaybackModule import ChoosePlaybackModule
from Framework.Utilities import ConfigModule
import traceback
import platform
import easyocr
from thefuzz import fuzz
import threading
from pathlib import Path
from itertools import repeat


# Disable pyautogui failsafe when moving to top left corner
gui.FAILSAFE = False

#########################
#                       #
#    Global Variables   #
#                       #
#########################

temp_config = os.path.join(
    os.path.join(
        os.path.abspath(__file__).split("Framework")[0],
        os.path.join(
            "AutomationLog", ConfigModule.get_config_value("Advanced Options", "_file")
        ),
    )
)

MODULE_NAME = inspect.getmodulename(__file__)

# Valid image positions
positions = ("left", "right", "centre", "center")

# Recall dependency, if not already set
dependency = None
if Shared_Resources.Test_Shared_Variables("dependency"):  # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables("dependency")  # Retreive appium driver
else:
    raise ValueError("No dependency set - Cannot run")

# Recall file attachment, if not already set
file_attachment = []
if Shared_Resources.Test_Shared_Variables("file_attachment"):
    file_attachment = Shared_Resources.Get_Shared_Variables("file_attachment")

#########################
#                       #
#   Helper Functions    #
#                       #
#########################


@logger
def get_driver():
    """ Returns pyautogui as the driver for compatibility with other modules """
    return gui


@logger
def getCoordinates(element, position):
    """ Return coordinates of attachment's centre """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Parse input
    try:
        x = element[0]
        y = element[1]
        w = element[2]
        h = element[3]
        position = position.lower().strip()

        if position not in positions:
            CommonUtil.ExecLog(sModuleInfo, "Position must be one of: %s" % positions, 3)
            return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing coordinates")

    # Perform calculations
    try:
        if position in ("center", "centre"):
            result_x, result_y = gui.center(element)
        elif position == "left":
            result_x = x + (w * 0.01)
            result_y = y + (h / 2)
        elif position == "right":
            result_x = x + (w * 0.99)
            result_y = y + (h / 2)

        if result_x in failed_tag_list or result_x == "" or result_x == None:
            return "zeuz_failed", ""
        return int(result_x), int(result_y)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error calculating coordinates")


@logger
def get_exec_from_icon(file_name):
    """ Read the Exec line from a Linux icon file """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        # Open file and read into memory
        with open(file_name, "r") as myfile:
            data = myfile.readlines()

        # Examine each line, looking for the Exec line
        for element in data:
            if element[:5] == "Exec=":
                result = element[
                    5:
                ].strip()  # Save execution line without the Exec= part

        if result == "":
            return "zeuz_failed"
        return result

    except Exception:
        errMsg = "Can't get the exec of the file"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


#########################
#                       #
#  Sequential Actions   #
#                       #
#########################


@logger
def Enter_Text(data_set):
    """ Insert text """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Parse data set
    try:
        element_parameter = False
        text_value = ""
        for row in data_set:
            if "action" in row[1]:
                text_value = row[2]
            if row[1] == "element parameter":  # Indicates we should find the element instead of assuming we have keyboard focus
                element_parameter = True

        if text_value == "":
            CommonUtil.ExecLog(sModuleInfo, "Could not find value for this action", 3)
            return "zeuz_failed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Perform action
    try:
        # Find image coordinates
        if element_parameter:
            CommonUtil.ExecLog(sModuleInfo, "Trying to locate element", 0)

            # (x, y, w, h)

            # Get element object
            # try for 10 seconds with 2 seconds delay
            max_try = 5
            sleep_in_sec = 2
            i = 0
            while i != max_try:
                try:
                    Element = LocateElement.Get_Element(data_set, gui)
                except:
                    True
                if Element is None:
                    CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
                else:
                    break
                time.sleep(sleep_in_sec)
                i = i + 1
            if Element in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
                return "zeuz_failed"

            # Get coordinates for position user specified
            x, y = getCoordinates(Element, "centre")  # Find coordinates (x,y)
            if x in failed_tag_list:  # Error reason logged by Get_Element
                CommonUtil.ExecLog(sModuleInfo, "Error calculating coordinates", 3)
                return "zeuz_failed"
            CommonUtil.ExecLog(sModuleInfo, "Image coordinates on screen %d x %d" % (x, y), 0)
            gui.click(x, y)  # Single click
        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "No element provided. Assuming textbox has keyboard focus",
                0,
            )

        # Enter text
        gui.typewrite(text_value)
        CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s" % text_value, 1)
        return "passed"

    except Exception:
        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def execute_hotkey(data_set) -> str:
    """Executes the provided hotkey.
    The hotkey sequence should be a plus (+) separated string:

      Alt + Tab,
      Ctrl + F,
      Ctrl + Shift + S,

    Args:
        data_set: The data set is only one row,

        Example 1:
        Field       Sub field           Value
        hotkey      desktop action      Ctrl + Shift + S

        Example 2:
        Field       Sub field           Value
        hotkey      desktop action      tab
        count       optional parameter  3

        Find all valid string to pass into hotkey() from link below:
        https://pyautogui.readthedocs.io/en/latest/keyboard.html#the-hotkey-function
    
    Returns:
        "passed" if successful.
        "zeuz_failed" otherwise.
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        count = 1
        for left, mid, right in data_set:
            left = left.strip()
            if "hotkey" in left:
                hotkey_combination = [i.strip().replace("plus", "+") for i in right.split("+")]
            elif "count" in left:
                try:
                    count = int(right)
                except:
                    count = 1
                    CommonUtil.ExecLog(sModuleInfo, "Count is set to 1", 2,)
    except:
        CommonUtil.ExecLog(sModuleInfo, "Couldn't  parse data_set", 3,)
        return "zeuz_failed"

    try:
        for i in range(count):
            gui.hotkey(*hotkey_combination)

        CommonUtil.ExecLog(
            sModuleInfo,
            "Successfully executed hotkey "
            + str(hotkey_combination)
            + " "
            + str(count)
            + " times",
            1,
        )
        return "passed"
    except:
        errMsg = "Failed to execute hotkey"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def move_mouse_cursor(data_set) -> str:
    """Moves the mouse cursor to the given coordinate from the current position.

    The movement can be either absolute or relative from current mouse position,
    as specified by the "relative" optional parameter. An optional "duration" can
    also be set which will simulate mouse movement from one place to another as if
    someone was using it.

    Args:
        data_set:
          
          move mouse cursor     desktop action          100, 100 (x, y - int, int)
          relative              optional parameter      true (bool)
          duration              optional parameter      2.5 (float)
    
    Returns:
        "passed" if successful.
        "zeuz_failed" otherwise.
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        relative = False
        duration = 0.0
        x = 0
        y = 0

        for left, _, right in data_set:
            left = left.lower()
            right = right.lower()

            if "move mouse cursor" in left:
                x, y = right.split(",")
                x = int(x.strip())
                y = int(y.strip())
            if "relative" in left:
                relative = right in ["true", "1"]
            if "duration" in left:
                duration = float(right)

        if relative:
            gui.moveRel(x, y, duration)
        else:
            gui.moveTo(x, y, duration)
        return "passed"
    except:
        errMsg = "Failed to move cursor to given position"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def click_on_coordinates(data_set):
    """
    This action executes a Left Click on the location of a given X,Y coordinates. Example:

    Field	                Sub Field	     Value
    click on coordinates	desktop action	 271,1051

    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        data = ""
        for left, _, right in data_set:
            if "click on coordinates" in left.lower():
                data = right

        try:
            x, y = data.replace(" ", "").split(",")
            x = int(x)
            y = int(y)

        except:
            errMsg = "Coordinate values were not set according to the correct format"
            return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

        gui.click(x, y)

        max_x, max_y = gui.size()
        x = max_x if x > max_x else x
        x = 0 if x < 0 else x
        y = max_y if y > max_y else y
        y = 0 if y < 0 else y
        Msg = "Clicked on " + str(x) + ", " + str(y) + " successfully"
        CommonUtil.ExecLog(sModuleInfo, Msg, 1)
        return "passed"

    except:
        errMsg = "Failed to click on coordinates"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Wait_For_Element_Pyautogui(data_set):
    """
    You need to add an image in the attachment section and mention the filename as below. This action will then search
    for the image attached in the test session and wait for the image to appear or disappear. You can set the time to
    wait in second. By default it is 10 seconds.
    Example:

    Action: Wait for an item to appear
    Field	    Sub Field	        Value
    image       element parameter	attachment.png
    wait gui    desktop action      10

    Action: Wait for an item to disappear
    Field	            Sub Field	        Value
    image               element parameter	attachment.png
    wait disable gui    desktop action      10

    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        wait_for_element_to_disappear = False

        # Find the wait time from the data set
        for left, _, right in data_set:
            if "wait disable gui" in left.lower():
                wait_for_element_to_disappear = True
                timeout_duration = int(right.strip())
            elif "wait gui" in left.lower():
                wait_for_element_to_disappear = False
                timeout_duration = int(right.strip())

        # Check for element every second
        end_time = (
            time.time() + timeout_duration
        )  # Time at which we should stop looking
        for i in range(
            timeout_duration
        ):  # Keep testing element until this is reached (likely never hit due to timeout below)
            # Wait and then test if we are over our alloted time limit
            if (
                time.time() >= end_time
            ):  # Keep testing element until this is reached (ensures we wait exactly the specified amount of time)
                break
            time.sleep(1)

            # Test if element exists or not
            Element = LocateElement.Get_Element(data_set, gui)

            # Check if element exists or not, depending on the type of wait the user wanted
            if wait_for_element_to_disappear == False:  # Wait for it to appear
                if Element not in failed_tag_list:  # Element has appeared !
                    CommonUtil.ExecLog(sModuleInfo, "Found element", 1)
                    return "passed"
                else:  # Element not found, keep waiting
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Element does not exist. Sleep and try again - %d" % i,
                        0,
                    )
            else:  # Wait for it to be removed/hidden/disabled
                if Element in failed_tag_list:  # Element has disappeared !
                    CommonUtil.ExecLog(sModuleInfo, "Element disappeared", 1)
                    return "passed"
                else:  # Element found, keep waiting
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Element still exists. Sleep and try again - %d" % i,
                        0,
                    )

        # Element status not changed after time elapsed, to exit with failure
        CommonUtil.ExecLog(sModuleInfo, "Wait for element failed", 3)
        return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def close_program(data_set):
    """ Exit a running program via process kill """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Parse data set
    try:
        program_name = ""
        for row in data_set:
            if row[1] == "action":
                program_name = row[2]  # Program name passed by user

        if program_name == "":
            CommonUtil.ExecLog(sModuleInfo, "Expected a program name in Value", 3)
            return "zeuz_failed"
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Perform action
    try:
        if dependency["OS"].lower() == "linux" or dependency["OS"].lower() == "mac":
            command = (
                "pkill -f " + program_name
            )  # Try Process Kill with full command checking set, which finds most programs automatically
            try:
                subprocess.Popen(
                    command.split(" ")
                )  # FU.run_cmd() blocks further execution, so we'll just use subprocess here
                # Check result
                close_status = "passed"

            # pkill failed, try another method
            except Exception:
                CommonUtil.ExecLog(
                    sModuleInfo, "pKill command failed, trying another method", 0
                )
                command = (
                    "ps aux | grep -i '%s' | grep -v grep | awk '{print $2}'"
                    % program_name
                )  # Try to find the PID
                close_status, output = FU.run_cmd(
                    command, return_status=True
                )  # Run the command above and return the output which should contain a list of PIDs found
                if output != []:
                    output = output[0].strip()  # First PID found
                    close_status = FU.run_cmd(
                        "kill -9 %s" % output
                    )  # Send the terminate signal to this PID
                else:
                    close_status = "zeuz_failed"  # No PID received - error occurred or program doesn't exist

        elif dependency["PC"].lower() == "windows":
            command = "taskkill /F /IM " + program_name + ".exe"
            close_status = FU.run_win_cmd(command)

        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Uknown dependency %s" % dependency["PC"], 3
            )
            return "zeuz_failed"

        # CommonUtil.TakeScreenShot(
        #     sModuleInfo
        # )  # Capture screenshot, if settings allow for it

        # Check result
        if close_status in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo, "Could not send signal to close program.", 3
            )
            return "zeuz_failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Sent signal to close program.", 1)
            return "passed"

    except Exception:
        errMsg = "Could not close the program"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Click_Element(data_set):
    """ Single or double mouse click on element """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Parse data set
    try:
        cmd = ""
        file_name = ""
        position = "centre"
        for row in data_set:
            if row[1] == "action":
                if row[0] == "click":
                    cmd = "click"
                    position = row[2]
                elif row[0] in ("doubleclick", "double click"):
                    cmd = "doubleclick"
                    position = row[2]
                elif row[0] in ("rightclick", "right click"):
                    cmd = "rightclick"
                    position = row[2]
            elif row[1] == "element parameter":
                file_name = row[2]

        if cmd == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Valid action not found. Expected Field set to 'click' or 'doubleclick', and the Value one of: %s"
                % str(positions),
                3,
            )
            return "zeuz_failed"
        if position not in positions:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Will click on centre of element. Expected Value to be one of: %s"
                % str(positions),
                2,
            )
            position = "centre"

        if file_name == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Valid element not found. Expected Sub-Field to be 'element parameter', and Value to be a filename",
                3,
            )
            return "zeuz_failed"

    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Perform action
    try:
        # Find image coordinates
        CommonUtil.ExecLog(
            sModuleInfo, "Performing %s action on file %s" % (cmd, file_name), 0
        )
        element = LocateElement.Get_Element(data_set, gui)  # (x, y, w, h)
        if element in failed_tag_list:  # Error reason logged by Get_Element
            CommonUtil.ExecLog(sModuleInfo, "Could not locate element", 3)
            return "zeuz_failed"

        # Get coordinates for position user specified
        x, y = getCoordinates(element, position)  # Find coordinates (x,y)
        if x in failed_tag_list:  # Error reason logged by Get_Element
            CommonUtil.ExecLog(sModuleInfo, "Error calculating coordinates", 3)
            return "zeuz_failed"
        CommonUtil.ExecLog(
            sModuleInfo, "Image coordinates on screen %d x %d" % (x, y), 0
        )

        # Click on image
        if cmd == "click":
            result = gui.click(x, y)  # Single click
        elif cmd == "doubleclick":
            result = gui.doubleClick(x, y)  # Double click
        elif cmd == "rightclick":
            result = gui.click(x, y, button="right") # Right click

        # CommonUtil.TakeScreenShot(
        #     sModuleInfo
        # )  # Capture screenshot, if settings allow for it

        # Check result and return
        if result in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo, "Couldn't click on element with given images", 3
            )
            return "zeuz_failed"
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Successfully clicked on element with given images", 1
            )
            return "passed"

    except Exception:
        errMsg = "Error while trying to perform click action"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def check_for_element(data_set):
    """ Tests whether or not an element is visible on screen """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    result = False
    var_name = 'check'
    # Parse data set
    try:
        file_name = ""
        for row in data_set:
            if row[1] == "element parameter":
                file_name = row[2]
            elif "action" in row[1].strip().lower():
                var_name = row[2].strip()

        if file_name == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Valid element not found. Expected Sub-Field to be 'element parameter', and Value to be a filename",
                3,
            )
            return "zeuz_failed"

    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Perform action
    try:
        CommonUtil.ExecLog(
            sModuleInfo, "Performing check action on file %s" % (file_name), 0
        )
        element = LocateElement.Get_Element(data_set, gui)  # (x, y, w, h)

        # CommonUtil.TakeScreenShot(
        #     sModuleInfo
        # )  # Capture screenshot, if settings allow for it

        if element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Found element", 1)
            result = True

        Shared_Resources.Set_Shared_Variables(var_name, result)
        return "passed"
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_bbox(data_set):
    """
    This action provides the (x, y, width, height) parameters of a bbox of an image as a list. 

    Field	                Sub Field	            Value
    image	                element parameter	    filename.png  
    get bounding box        desktop action          **variable name that will store the parameters 
                                                    of the bounding box e.g. cords**
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    filename = ''
    var_name = 'cords'

    try:
        for row in data_set:
            if row[1] == "element parameter":
                filename = row[2].strip()
            elif "action" in row[1].strip().lower():
                var_name = row[2].strip()

        if filename == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Valid element not found. Expected Sub-Field to be 'element parameter', and Value to be a filename",
                3,
            )
            return "zeuz_failed"

    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
    
    try:
        element = LocateElement.Get_Element(data_set, gui)  # (x, y, w, h)
        if element in failed_tag_list:  # Error reason logged by Get_Element
            CommonUtil.ExecLog(sModuleInfo, "Could not locate element", 3)
            return "zeuz_failed"

        # Get parameters of the bbox
        CommonUtil.ExecLog(
            sModuleInfo, "Bbox paramaters on screen X:%d, Y:%d, Width:%d, Height:%d" %(element[0], element[1], element[2], element[3]), 0
        )
        Shared_Resources.Set_Shared_Variables(var_name, element)
        return element
    except Exception:
        errMsg = "Error locating the element"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def launch_program(data_set):
    """ Execute a program or desktop icon """
    # If a linux desktop icon filename is specified, then it will read the file, and extract the Exec line to execute it directly
    # Anything else is executed, including if it's an attachment

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Parse data set
    try:
        file_name = data_set[0][2]  # Get filename from data set
        Command = ""
        if file_name == "":
            CommonUtil.ExecLog(sModuleInfo, "Value field empty. Expected filename or full file path", 3)
            return "zeuz_failed"
    except:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Execute program
    try:
        # Check if filename from data set is an icon file on the desktop by using full or partial match
        path = os.path.join(
            FU.get_home_folder(), "Desktop"
        )  # Prepare path for desktop if needed
        files = [
            f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
        ]  # Get list of files in specified directory
        for f in files:  # For each file found
            if file_name in f:  # If filename from data set matches fully or partially
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
            CommonUtil.ExecLog(
                sModuleInfo,
                "Could not find file attachment called %s, and could not find it locally"
                % file_name,
                3,
            )
            return "zeuz_failed"
        if file_name in file_attachment:
            Command = file_attachment[
                file_name
            ]  # In file is an attachment, get the full path
        elif os.path.exists(file_name) and Command == "":  # User provided correct path
            Command = file_name

        # Now file_name should have a directory/file pointing to the correct image

        launch_status = "success"

        # Execute program
        if platform.system().lower() == "linux" or platform.system().lower() == "mac":
            launch_status = subprocess.Popen(
                Command.split(" ")
            )  # FU.run_cmd() blocks further execution, so we'll just use subprocess here

        elif platform.system().lower() == "windows":
            # launch_status = subprocess.Popen('%s' % Command) # FU.run_cmd() blocks further execution, so we'll just use subprocess here
            # launch_status = FU.run_win_cmd(Command)
            # This is the same as double clicking on Windows
            # https://stackoverflow.com/a/34738279
            os.startfile(Command)

        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Unknown dependency %s" % dependency["PC"], 3
            )
            return "zeuz_failed"

        # CommonUtil.TakeScreenShot(
        #     sModuleInfo
        # )  # Capture screenshot, if settings allow for it

        # Check result and return
        if launch_status in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not launch the program", 3)
            return "zeuz_failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Program launched successfully.", 1)
            return "passed"

    except Exception:
        errMsg = "Can't execute the program"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def teardown(data_set):
    """ Cleanup automation """

    # Cleanup shared variables
    Shared_Resources.Clean_Up_Shared_Variables()
    return "passed"


@logger
def Drag_Element(data_set):
    """ Drag element from source to destination

    Action: Drag an element to a specific coordinates
    Field	        Sub Field	        Value
    coordinates     element parameter	100,250
    image           source parameter    source_image.png
    drag            desktop action      left

    Action: Drag element by images
    Field	        Sub Field	        Value
    image           element parameter	destination_image.png
    image           source parameter    source_image.png
    drag            desktop action      left
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Parse data set
    try:
        cmd = ""
        file_name = ""
        src_file_name = ""
        position = "centre"
        Drag_Element_to_a_coordinate = False

        for row in data_set:
            if row[1] == "action":
                if row[0] == "drag":
                    cmd = "drag"
                    position = row[2]
            elif row[1] == "element parameter":
                if "coordinates" in row[0].lower():
                    dst_x, dst_y = row[2].replace(" ", "").split(",")
                    dst_x, dst_y = int(dst_x), int(dst_y)
                    Drag_Element_to_a_coordinate = True
                else:
                    file_name = row[2]
            elif row[1] == "source parameter":
                src_file_name = row[2]

        if cmd == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Valid action not found. Expected Field set to 'drag' and the Value one of: %s"
                % str(positions),
                3,
            )
            return "zeuz_failed"
        if position not in positions:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Will click on centre of element. Expected Value to be one of: %s"
                % str(positions),
                2,
            )
            position = "centre"

        if src_file_name == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Valid element not found. Expected Sub-Field to be 'source parameter', and Value to be a filename",
                3,
            )
            return "zeuz_failed"

    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Perform action
    try:
        # Get coordinates for source and destiniation
        for filename in (file_name, src_file_name):
            if Drag_Element_to_a_coordinate and filename == file_name:
                continue
            tmp_data_set = [("image", "element parameter", filename)]
            # Find image coordinates for destination element
            CommonUtil.ExecLog(
                sModuleInfo, "Performing %s action on file %s" % (cmd, filename), 0
            )
            element = LocateElement.Get_Element(tmp_data_set, gui)  # (x, y, w, h)
            if element in failed_tag_list:  # Error reason logged by Get_Element
                CommonUtil.ExecLog(
                    sModuleInfo, "Could not locate element: %s" % filename, 3
                )
                return "zeuz_failed"

            # DESTINATION  Get coordinates for position user specified
            x, y = getCoordinates(element, position)  # Find coordinates (x,y)
            if x in failed_tag_list:  # Error reason logged by Get_Element
                CommonUtil.ExecLog(sModuleInfo, "Error calculating coordinates", 3)
                return "zeuz_failed"
            CommonUtil.ExecLog(
                sModuleInfo, "Image coordinates on screen %d x %d" % (x, y), 0
            )

            # Put the x,y in usable variables
            if filename == file_name:
                dst_x, dst_y = x, y
            else:
                src_x, src_y = x, y

        # Drag source to destination
        gui.moveTo(src_x, src_y)  # Move to source
        result = gui.dragTo(
            dst_x, dst_y, 2, button="left"
        )  # Click and drag to destination, taking two seconds, then release - the 2 seconds is important for some drags because without the time, it happens too fast and the drag command is missed by the window manager

        # CommonUtil.TakeScreenShot(
        #     sModuleInfo
        # )  # Capture screenshot, if settings allow for it

        # Check result and return
        if result in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo, "Couldn't dragged element with given images", 3
            )
            return "zeuz_failed"
        elif Drag_Element_to_a_coordinate:

            max_x, max_y = gui.size()
            dst_x = max_x if dst_x > max_x else dst_x
            dst_x = 0 if dst_x < 0 else dst_x
            dst_y = max_y if dst_y > max_y else dst_y
            dst_y = 0 if dst_y < 0 else dst_y

            CommonUtil.ExecLog(
                sModuleInfo,
                "Successfully dragged element to the %d, %d coordinates"
                % (dst_x, dst_y),
                1,
            )
            return "passed"
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Successfully dragged element with given images", 1
            )
            return "passed"

    except Exception:
        errMsg = "Error while trying to perform drag action"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def navigate_listbox(data_set):
    """ Scroll listbox until image element is found or timeout is hit

    Action: Finding element from dropdown list
    Field	        Sub Field	        Value
    image           element parameter	file_name.png
    listbox         desktop action      5
    """
    # Continually presses page down and checks for the image
    # Assumptions: Listbox already has focus - user ought to use click action to click on the listbox, or the drop down menu's arrow
    # Assumptions: User has image of the list item they want to find
    # Produces: Pass/Fail - User is responsible for performing the action they desire now that the listbox is where their element is visible

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Maximum number of tries to find the element. Have no way of knowing when we hit the last list item, so we have to hard code a value
    max_tries = 10

    # Delay before checking for image element
    delay = 1

    # Parse data set
    try:
        file_name = ""
        for row in data_set:
            if row[1] == "element parameter":
                file_name = row[2]
            elif row[1] == "action":
                try:
                    max_tries = int(
                        row[2].strip()
                    )  # Test if user specified a max_tries on the action line
                except:
                    max_tries = 10  # Default max_tries - user did not specify

        if file_name == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Valid element not found. Expected Sub-Field to be 'element parameter', and Value to be a filename",
                3,
            )
            return "zeuz_failed"
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Perform action
    try:
        # Get coordinates for source and destiniation
        for i in range(max_tries):
            CommonUtil.ExecLog(sModuleInfo, "Checking listbox for element", 0)
            element = LocateElement.Get_Element(data_set, gui)  # (x, y, w, h)
            if element in failed_tag_list:  # Error reason logged by Get_Element
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Could not locate element - trying a new position. Attempt #%d" % i,
                    0,
                )
                gui.hotkey("pgdn")
                time.sleep(delay)  # Wait for listbox to update
            else:
                CommonUtil.ExecLog(
                    sModuleInfo, "Found element after %d tries" % (i + 1), 1
                )
                return "passed"

        # CommonUtil.TakeScreenShot(
        #     sModuleInfo
        # )  # Capture screenshot, if settings allow for it

        CommonUtil.ExecLog(
            sModuleInfo, "Could not locate element after %d attempts" % max_tries, 3
        )
        return "zeuz_failed"

    except Exception:
        errMsg = "Error while trying to perform drag action"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def playback_recorded_events(data_set):
    """Plays back the recorded events from a given file."""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Parse data set
    try:
        filepath = ""
        speed_factor = 1.0

        for left, _, right in data_set:
            left = left.lower().strip()
            if "file path" in left:
                filepath = right.strip()
                filepath = CommonUtil.path_parser(filepath)
            elif "speed factor" in left:
                speed_factor = float(right.strip())

        if filepath == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "A valid path to the recorded event file must be provided. If you've uploaded it into attachments with name `recording_1.zvt`,"
                " you can use it by providing the path as `%|recording_1.zvt|%`",
                3,
            )
            return "zeuz_failed"

    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Perform action
    try:
        CommonUtil.ExecLog(
            sModuleInfo, "Playing the events recorded in - %s" % filepath, 1
        )

        playback_chooser = ChoosePlaybackModule(filepath)
        playback_chooser.play(speed_factor=speed_factor)

        CommonUtil.ExecLog(
            sModuleInfo, "DONE playing back events.", 1
        )
        return "passed"

    except Exception:
        errMsg = "Failed to playback recorded events from file: %s" % filepath
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

partial_ss_path = None
@logger
def take_partial_screenshot(data_set):
    """
    This action takes a partial screenshot of the active window.
    One has to provide the path where the screenshot will be saved. 
    One can provide x,y coordinates, width and height to take screenshot 
    of a specific region by using the bbox optional parameter. 

    Field	                Sub Field	            Value
    screenshot save path	element parameter	    C:\\User\\path\\image.png
    bbox                    optional parameter      (x, y, width, height)
    take screenshot         desktop action          
    """
    import time
    from PIL import Image

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    path = None
    x_cord = None
    y_cord = None
    width = None
    height = None
    global partial_ss_path

    try:
        for left, _, right in data_set:
            if "path" in left.lower().strip():
                path = right.strip()
            elif left.lower().strip() == "bbox":
                x_cord, y_cord, width, height = right.replace('(','').replace(')','').split(',')
                x_cord = int(x_cord.strip())
                y_cord = int(y_cord.strip())
                width = int(width.strip())
                height = int(height.strip())
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    try:
        if path is None:
            filename_format = "%Y_%m_%d_%H-%M-%S"
            filename = time.strftime(filename_format) + ".png"
            screenshot_folder = ConfigModule.get_config_value(
                "sectionOne", "screen_capture_folder", temp_config
            )
            path = str(Path(screenshot_folder) / Path(filename))
        
        partial_ss_path = path
        gui.screenshot(path)
    
        if x_cord is not None and y_cord is not None and width is not None and height is not None:
            im = Image.open(path)
            im1 = im.crop((x_cord, y_cord, (x_cord+width), (y_cord+height)))
            im1.save(path)
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Proper bounding box parameters are not provided", 3
            )
            return "zeuz_failed"
            
        return "passed"
    except:
        errMsg = "Could not take the screenshot"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
    

@logger
def keystroke_for_element(data_set):
    """
    Enter sequential characters or strings, for example, Hello World 
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        chars = ""
        delay = 0.0
        for left, mid, right in data_set:
            if "delay" in left.lower().strip():
                delay = float(right.strip())
            elif "action" in mid.lower().strip():
                chars = right.strip()
        if chars == "":
            CommonUtil.ExecLog(sModuleInfo, "Invalid action found", 3)
            return "zeuz_failed"
    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
    
    try:
        gui.write(chars, interval=delay)
        CommonUtil.ExecLog(sModuleInfo, "Successfully entered characters with pyautogui:\n%s" % chars, 1)
        return "passed"

    except:
        errMsg = "Could not enter characters with pyautogui"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
    

#########################
#                       #
#   OCR Functions       #
#                       #
#########################

reader = None

# initialize the OCR
def get_easyocr_reader():
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global reader
    if not reader:
        CommonUtil.ExecLog(sModuleInfo, "Initializing EasyOCR reader...", 1)
        reader = easyocr.Reader(['en'])
    else:
        CommonUtil.ExecLog(sModuleInfo, "EasyOCR reader already initialized.", 1)
        return reader
    
# create a list of texts
def get_only_text(data:tuple):
    return data[1]

# get the index of the matching text
def get_fuzzy_score(text1, text2, method):
    if "partial" in method:
        score = fuzz.partial_ratio(text1, text2)
    elif "loose" in method:
        score = fuzz.partial_token_sort_ratio(text1,text2)
    else:
        score = fuzz.ratio(text1,text2)
    return score

# take a screenshot of the screen
def ocr_screenshot():
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    
    # take screenshot of the current screen
    CommonUtil.ExecLog(sModuleInfo, "Taking full screenshot\n", 1)
    local_time = time.localtime()
    local_time_str = time.strftime("%H%M%S_%d%m%Y", local_time)
    filename = f"{local_time_str}.png"
    screenshot_folder = ConfigModule.get_config_value(
        "sectionOne", "screen_capture_folder", temp_config
    )
    path = str(Path(screenshot_folder) / Path(filename))
    gui.screenshot(path)

    return path


@logger
def ocr_click(data_set):
    """
    This action lets you find a text through OCR and click on it. It also lets you do right click and double click.

    Field	                    Sub Field	                Value
    text	                    element parameter	        String you want to click on. ex: 'Advanced Settings'
    method                      optional parameter          “match”/ “partial match”/ “loose match”
    threshold                   optional parameter          Threshold of the match. ex: 90
    ocr click                   desktop action              click/double click/right click
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    text = None
    method = "match"
    threshold = 70
    did_fuzzy = False
    click_type = 'click'
    global reader

    # parse the data
    try:
        for left, mid, right in data_set:
            if left.strip().lower() == "text":
                text = right.strip()
            elif left.strip().lower() == "method":
                method = right.strip().lower()
            elif left.strip().lower() == "threshold":
                threshold = int(right.strip())
            elif "action" in mid.strip().lower():
                click_type = right.strip().lower()
    except:
        CommonUtil.ExecLog(
                sModuleInfo, "Could not parse the data", 3
            )
        return "zeuz_failed"

    if text == None:
        CommonUtil.ExecLog(
                sModuleInfo, "Text field cannot be empty", 3
            )
        return "zeuz_failed"
    
    if reader is None:
        ocr_thread = threading.Thread(target=get_easyocr_reader)
        ocr_thread.start()
        path = ocr_screenshot()
        # wait for the OCR thread to finish
        ocr_thread.join()
    else:
        path = ocr_screenshot()
    result = reader.readtext(path) 

    texts = list(map(get_only_text, result))

    if text in texts:
        idx = texts.index(text)
    else:
        # text_list = [text for _ in range(len(texts))]
        fuzzy_text_scores = list(map(get_fuzzy_score, texts, repeat(text), repeat(method)))
        idx = fuzzy_text_scores.index(max(fuzzy_text_scores))
        did_fuzzy = True

    # get the scores
    if did_fuzzy:
        text_score = fuzzy_text_scores[idx]
        if text_score < threshold:
            CommonUtil.ExecLog(sModuleInfo, f"After fuzzy match, score {text_score} falls below the threshold {threshold}", 3)
            CommonUtil.ExecLog(sModuleInfo, f"The closest  match is '{texts[idx]}'", 3)
            CommonUtil.ExecLog(
                sModuleInfo, f"If you want to interact with this word then either use differenet method or lower the threshold", 3
            )
            return "zeuz_failed"
        CommonUtil.ExecLog(
            sModuleInfo, f"Similar text after fuzzy {method} is '{texts[idx]}' with a score of {fuzzy_text_scores[idx]}", 1
        )
    else:
        text_score = int(result[idx][2]*100)
        if text_score < threshold: 
            CommonUtil.ExecLog(sModuleInfo, f"Score {text_score} below the threshodl {threshold}", 3)
            return "zeuz_failed"
        
    coordinates = result[idx][0]
    coord_x = (coordinates[1][0] + coordinates[0][0])//2
    coord_y = (coordinates[2][1] + coordinates[1][1])//2
    if click_type == "click":
        gui.click(x=coord_x, y=coord_y)
    elif click_type == "right click":
        gui.click(x=coord_x, y=coord_y, button="right")
    elif click_type == "double click":
        gui.doubleClick(x=coord_x, y=coord_y)
    return "passed"


@logger
def ocr_get_value_with_coordinates(data_set):
    """
    This action lets you crop a portion of the image of the screen and extract the text shown in that 
    particular portion of the image
    Field	                        Sub Field	                    Value
    coordinates	                    element parameter	            top, left, bottom, right coordinates. ex: 50, 120, 90, 320
    ocr get value with coordinate   desktop action                  variable name that will hold the value
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    topcord = None
    leftcord = None
    bottomcord = None
    rightcord = None
    var_name = None
    global partial_ss_path

    # parse the data
    try:
        for left, mid, right in data_set:
            if left.strip().lower() == "coordinates":
                coords = right.strip().split(",")
                topcord = int(coords[0])
                leftcord = int(coords[1])
                bottomcord = int(coords[2])
                rightcord = int(coords[3])
            elif "action" in mid.strip().lower():
                var_name = right.strip()
    except:
        CommonUtil.ExecLog(
                sModuleInfo, "Could not parse the data", 3
            )
        return "zeuz_failed"
    
    if (topcord >  bottomcord or leftcord > rightcord):
        CommonUtil.ExecLog(
                sModuleInfo, "Please insert correct coordinates", 3
            )
        return "zeuz_failed"
    
    if var_name is None:
        CommonUtil.ExecLog(
                sModuleInfo, "Please provide a variable name to store the extracted value", 3
            )
        return "zeuz_failed"

    data = (
        ("bbox", "optional parameter", f"({leftcord}, {topcord}, {rightcord-leftcord}, {bottomcord-topcord})"),
        ("take screenshot ", "desktop action", None)
    )
    
    take_partial_screenshot(data)
    get_easyocr_reader()
    result = reader.readtext(partial_ss_path)

    if not result:
        CommonUtil.ExecLog(
                sModuleInfo, "Could not read any text", 3
            )
        return "zeuz_failed"
    
    text = result[0][1]
    
    CommonUtil.ExecLog(sModuleInfo, f"The extracted text is {text}", 1)
    Shared_Resources.Set_Shared_Variables(var_name, text)
    return "passed"


def compare_ocr_coordinates(results, image_coords_updated,  direction, gap):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    res_coords = [0, 0, 0, 0]
    diff = 9999
    if gap != 0:
        tslr = gap
        tstb = gap
    else:
        tslr = 25
        tstb = 100
    
    # extract top, left, bottom, right from the results and assign them to res_cords
    res_coords[0] = results[0][0][1]
    res_coords[1] = results[0][0][0]
    res_coords[2] = results[0][2][1]
    res_coords[3] = results[0][1][0]

    if direction == "left" or direction == "right":
        # check the difference between the top and bottom value of the image and OCR extracted text
        if abs(res_coords[0]-image_coords_updated[0]) <= tslr and abs(res_coords[2]-image_coords_updated[2]) <= tslr:
            if direction == "right":
                diff = res_coords[1]-image_coords_updated[3] if res_coords[1]-image_coords_updated[3] > 0 else 9999
            elif direction == "left":
                diff = image_coords_updated[1]-res_coords[3] if image_coords_updated[1]-res_coords[3] > 0 else 9999
    elif direction == "top" or direction == "bottom":
        # check the difference between the left and right value of the image and OCR extracted text
        if abs(res_coords[1]-image_coords_updated[1]) <= tstb and abs(res_coords[3]-image_coords_updated[3]) <= tstb:
            if direction == "bottom":
                diff = res_coords[0]-image_coords_updated[2] if res_coords[0]-image_coords_updated[2] > 0 else 9999
            elif direction == "top":
                diff = image_coords_updated[0]-res_coords[2] if image_coords_updated[0]-res_coords[2] > 0 else 9999
    return diff


@logger
def ocr_get_value_with_image(data_set):
    """
    This action lets you extract a text based on the position of the text with respect to the image you provide. The image has to be attached
    in the attachment section.
    Field	                    Sub Field	                Value
    image	                    element parameter	        enter the image that is closer to the text you want to extract
    direction                   element parameter           direction of the text to be extracted regarding the given image
    ocr get value with image    desktop action              variable name that will hold the value
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    image_name = None
    image_direction = None
    var_name = None
    image_coords_updated = [0, 0, 0, 0]
    text_gap = 0
    global reader

    # parse the data
    try:
        for left, mid, right in data_set:
            if left.strip().lower() == "image":
                image_name = right.strip()
            elif left.strip().lower() == "direction":
                image_direction = right.strip()
            elif "gap" in left.strip().lower():
                text_gap = int(right.strip())
            elif "action" in mid.strip().lower():
                var_name = right.strip()
    except:
        CommonUtil.ExecLog(
                sModuleInfo, "Could not parse the data", 3
            )
        return "zeuz_failed"
    
    get_bbox_dataset = (
        ("image", "element parameter", f"{image_name}"),
        ("get bounding box", "desktop action", "coords")
    )

    # update the image_coords_updated to hold the coordinates like top, left, bottom, right
    image_coords = get_bbox(get_bbox_dataset)
    image_coords_updated[0] = image_coords[1]
    image_coords_updated[1] = image_coords[0]
    image_coords_updated[2] = image_coords[1]+image_coords[3]
    image_coords_updated[3] = image_coords[0]+image_coords[2]

    if reader is None:
        ocr_thread = threading.Thread(target=get_easyocr_reader)
        ocr_thread.start()
        path = ocr_screenshot()
        # wait for the OCR thread to finish
        ocr_thread.join()
    else:
        path = ocr_screenshot()
    
    results = reader.readtext(path)

    text_diff = list(map(compare_ocr_coordinates, results, repeat(image_coords_updated), repeat(image_direction), repeat(text_gap)))
    min_diff = min(text_diff)
    if min_diff == 9999:
        CommonUtil.ExecLog(sModuleInfo, f"Could not find any element {image_direction} to the image", 3)
        return "zeuz_failed"

    idx = text_diff.index(min_diff)
    text = results[idx][1]

    Shared_Resources.Set_Shared_Variables(var_name, text)
    return "passed"


@logger
def ocr_get_value_with_text(data_set):
    """
    This action lets you extract a text based on the position of the text you provide.
    Field	                    Sub Field	                Value
    text	                    element parameter	        enter the text that is closer to the text you want to extract
    direction                   element parameter           direction of the text to be extracted regarding the given tex
    ocr get value with text     desktop action              variable name that will hold the value
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    given_text = None
    text_direction = None
    var_name = None
    given_text_coordinates = [0, 0, 0, 0]
    threshold = 70
    method = "match"
    did_fuzzy = False
    text_gap = 0
    global reader

    # parse the data
    try:
        for left, mid, right in data_set:
            if left.strip().lower() == "text":
                given_text = right.strip()
            elif left.strip().lower() == "direction":
                text_direction = right.strip()
            elif left.strip().lower() == "threshold":
                threshold = int(right.strip())
            elif "gap" in left.strip().lower():
                text_gap = int(right.strip())
            elif "action" in mid.strip().lower():
                var_name = right.strip()
    except:
        CommonUtil.ExecLog(
                sModuleInfo, "Could not parse the data", 3
            )
        return "zeuz_failed"
    
    if reader is None:
        ocr_thread = threading.Thread(target=get_easyocr_reader)
        ocr_thread.start()
        path = ocr_screenshot()
        # wait for the OCR thread to finish
        ocr_thread.join()
    else:
        path = ocr_screenshot()
    
    results = reader.readtext(path)

    text_list = list(map(get_only_text, results))

    if given_text in text_list:
        idx = text_list.index(given_text)
    else:
        fuzzy_text_scores = list(map(get_fuzzy_score, text_list, repeat(given_text), repeat(method)))
        idx = fuzzy_text_scores.index(max(fuzzy_text_scores))
        did_fuzzy = True

    # get the scores
    if did_fuzzy:
        text_score = fuzzy_text_scores[idx]
        if text_score < threshold:
            CommonUtil.ExecLog(sModuleInfo, f"After fuzzy match, score {text_score} falls below the threshold {threshold}", 3)
            CommonUtil.ExecLog(sModuleInfo, f"The closest  match is '{text_list[idx]}'", 3)
            CommonUtil.ExecLog(
                sModuleInfo, f"If you want to use this word as reference then either use differenet method or lower the threshold", 3
            )
            return "zeuz_failed"
        CommonUtil.ExecLog(
            sModuleInfo, f"Similar text after fuzzy {method} is '{text_list[idx]}' with a score of {fuzzy_text_scores[idx]}", 1
        )
    else:
        text_score = int(results[idx][2]*100)
        if text_score < threshold: 
            CommonUtil.ExecLog(sModuleInfo, f"Score {text_score} below the threshodl {threshold}", 3)
            return "zeuz_failed"

    
    result = results[idx][0]
    given_text_coordinates[0] = result[0][1]
    given_text_coordinates[1] = result[0][0]
    given_text_coordinates[2] = result[2][1]
    given_text_coordinates[3] = result[1][0]

    text_diff = list(map(compare_ocr_coordinates, results, repeat(given_text_coordinates), repeat(text_direction), repeat(text_gap)))
    min_diff = min(text_diff)
    if min_diff == 9999:
        CommonUtil.ExecLog(sModuleInfo, f"Could not find any element {text_direction} to the text", 3)
        return "zeuz_failed"

    idx = text_diff.index(min_diff)
    text = results[idx][1]

    Shared_Resources.Set_Shared_Variables(var_name, text)
    return "passed"