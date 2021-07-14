"""Windows automation file, element parameters can be found by running the inspectx64/x86.exe file"""
#########################
#                       #
#        Modules        #
#                       #
#########################

import sys, os, time, inspect
import glob

sys.path.append(os.path.dirname(__file__))
from Framework.Utilities import CommonUtil
import pyautogui as gui  # https://pyautogui.readthedocs.io/en/latest/
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as Shared_Resources,
)
from Framework.Built_In_Automation.Shared_Resources import LocateElement
from Framework.Utilities.CommonUtil import (
    passed_tag_list,
    failed_tag_list,
    skipped_tag_list,
)

import inspect, time, datetime, os, sys
from os import system
from _elementtree import Element  # What is this for?
from Framework.Utilities import CommonUtil
from Framework.Utilities.decorators import logger

MODULE_NAME = inspect.getmodulename(__file__)

# this needs to be here on top, otherwise will return error
import clr, System

clr.AddReference("UIAutomationClient")
clr.AddReference("UIAutomationTypes")
clr.AddReference("UIAutomationProvider")
clr.AddReference("System.Windows.Forms")

# Do these need to be here?
from System.Windows.Automation import *
from System.Threading import Thread
from System.Windows.Forms import SendKeys

import win32api, win32con  # What is this for?
import pyautogui  # Should be removed after we complete sequential actions
import win32gui  # Needed?
import autoit  # The likely method we'll use

#########################
#                       #
#    Global Variables   #
#                       #
#########################
# Recall dependency, if not already set
dependency = None
if Shared_Resources.Test_Shared_Variables("dependency"):  # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables("dependency")  # Retreive appium driver

global recur_count
recur_count = 0  # To be deleted
common_sleep = 0


@logger
def go_to_desktop(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    Element = get_element("", "Show desktop",
                          "TrayShowDesktopButtonWClass")  # Todo: This line should generate bug so fix it.
    if Element in failed_tag_list:
        CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
        return "zeuz_failed"
    try:
        result = Click_Element_None_Mouse(Element, None, True, None, None)
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not click element", 3)
            return "zeuz_failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1)
            return "passed"
    except Exception:
        errMsg = "Could not select/click your element."
        CommonUtil.ExecLog(sModuleInfo, errMsg, 3)
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


# Method to click on element; step data passed on by the user
@logger
def Click_Element(data_set):
    """ Click using element, first get the element then click"""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    expand = None
    invoke = None
    select = None
    toggle = None

    # parse dataset and read data
    try:
        for left, mid, right in data_set:
            right = right.strip().lower()
            if left.strip().lower() == "method" and mid == "element parameter" and right in (
                    "expand", "invoke", "select", "toggle"):
                exec(right + "=True")
                break

    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "You have provided an invalid Click data.  Please refer to help", 3)
        CommonUtil.Exception_Handler(sys.exc_info(), None,
                                     "You have provided an invalid Click data.  Please refer to help")
        return "zeuz_failed"

    # Get element object
    # try for 10 seconds with 2 seconds delay
    max_try = 5
    sleep_in_sec = 2
    i = 0
    while i != max_try:
        try:
            Element = Get_Element(data_set)
        except:
            True
        if Element is None or Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
        else:
            break
        time.sleep(sleep_in_sec)
        i = i + 1
    if Element in failed_tag_list:
        CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
        return "zeuz_failed"

    # If found Click element

    try:
        CommonUtil.ExecLog(sModuleInfo, "Element was located.  Performing action provided ", 1)
        result = Click_Element_None_Mouse(Element, expand, invoke, select, toggle)
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not click element", 3)
            return "zeuz_failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1)
            return "passed"
    except Exception:
        errMsg = "Could not select/click your element."
        CommonUtil.ExecLog(sModuleInfo, errMsg, 3)
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Right_Click_Element(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        while i != max_try:
            try:
                Element = Get_Element(data_set)
            except:
                True
            if Element is None or Element in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"

        x = (int)(
            Element.Current.BoundingRectangle.Right
            - Element.Current.BoundingRectangle.Width / 2
        )
        y = (int)(
            Element.Current.BoundingRectangle.Bottom
            - Element.Current.BoundingRectangle.Height / 2
        )
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")


import clr, inspect, System
import os, sys
from _elementtree import Element

clr.AddReference("UIAutomationClient")
clr.AddReference("UIAutomationTypes")
clr.AddReference("UIAutomationProvider")
clr.AddReference("System.Windows.Forms")

import time, datetime
import win32api, win32con
import win32gui
import random
import string
import autoit

from System.Windows.Automation import *

"""
global recur_count
recur_count = 0
#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False
"""


def get_element(
        MainWindowName_OR_ParentElement,
        Element_Name,
        Element_Class,
        Element_AutomationID,
        Element_LocalizedControlType,
        max_try=1,
):
    # max_time is built in wait function.  It will try every seconds 15 times.

    recur_count = 0
    try:

        try:
            if isinstance(MainWindowName_OR_ParentElement, str):
                ParentElement = _get_main_window(MainWindowName_OR_ParentElement)
                if ParentElement is None:
                    return "zeuz_failed"
                else:
                    all_elements = []
                    all_elements += _child_search(
                        ParentElement,
                        Element_Name,
                        Element_Class,
                        Element_AutomationID,
                        Element_LocalizedControlType
                    )

                    if all_elements:
                        return all_elements
                    else:
                        return "zeuz_failed"
            else:
                # Todo: dont know what to do here and what code is written below. Where is the ParentElement ??
                ChildElement = _child_search(
                    ParentElement,
                    Element_Name,
                    Element_Class,
                    Element_AutomationID,
                    Element_LocalizedControlType,
                )

                if ChildElement is not None:
                    return ChildElement
                else:
                    return "zeuz_failed"

        except:
            return "zeuz_failed"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            (
                    (str(exc_type).replace("type ", "Error Type: "))
                    + ";"
                    + "Error Message: "
                    + str(exc_obj)
                    + ";"
                    + "File Name: "
                    + fname
                    + ";"
                    + "Line: "
                    + str(exc_tb.tb_lineno)
            )
        )


def _child_search(
        ParentElement,
        Element_Name,
        Element_Class,
        Element_AutomationID,
        Element_LocalizedControlType,
):
    try:
        """
        global recur_count
        recur_count = recur_count +1
        print recur_count
        
        if recur_count is 100:
            time.sleep(5)
            """
        # Name, Class, AutomationID, LocalizedControlType
        try:
            NameE = ParentElement.Current.Name
            ClassE = ParentElement.Current.ClassName
            AutomationE = ParentElement.Current.AutomationId
            LocalizedControlTypeE = ParentElement.Current.LocalizedControlType
            if (
                    Element_Name is not None
                    and Element_Class is not None
                    and Element_AutomationID is not None
                    and Element_LocalizedControlType is not None

                    and NameE == Element_Name
                    and ClassE == Element_Class
                    and AutomationE == Element_AutomationID
                    and LocalizedControlTypeE == Element_LocalizedControlType
            ):
                return [ParentElement]

            # Name, Class
            if (
                    Element_Name is not None
                    and Element_Class is not None
                    and Element_AutomationID is None
                    and Element_LocalizedControlType is None

                    and NameE == Element_Name
                    and ClassE == Element_Class
            ):
                return [ParentElement]

            # Name, AutomationID
            if (
                    Element_Name is not None
                    and Element_Class is None
                    and Element_AutomationID is not None
                    and Element_LocalizedControlType is None

                    and NameE == Element_Name
                    and AutomationE == Element_AutomationID
            ):
                return [ParentElement]

            # Name, LocalizedControlType
            if (
                    Element_Name is not None
                    and Element_Class is None
                    and Element_AutomationID is None
                    and Element_LocalizedControlType is not None

                    and NameE == Element_Name
                    and LocalizedControlTypeE == Element_LocalizedControlType
            ):
                return [ParentElement]

            # Class, AutomationID, LocalizedControlType
            if (
                    Element_Name is None
                    and Element_Class is not None
                    and Element_AutomationID is not None
                    and Element_LocalizedControlType is not None

                    and ClassE == Element_Class
                    and AutomationE == Element_AutomationID
                    and LocalizedControlTypeE == Element_LocalizedControlType
            ):
                return [ParentElement]

            # Class, AutomationID
            if (
                    Element_Name is None
                    and Element_Class is not None
                    and Element_AutomationID is not None
                    and Element_LocalizedControlType is None

                    and ClassE == Element_Class
                    and AutomationE == Element_AutomationID
            ):
                return [ParentElement]

            # Class, LocalizedControlType

            if (
                    Element_Name is None
                    and Element_Class is not None
                    and Element_AutomationID is None
                    and Element_LocalizedControlType is not None

                    and ClassE == Element_Class
                    and LocalizedControlTypeE == Element_LocalizedControlType
            ):
                return [ParentElement]

            # Class
            if (
                    Element_Name is None
                    and Element_Class is not None
                    and Element_AutomationID is None
                    and Element_LocalizedControlType is None

                    and ClassE == Element_Class
            ):
                return [ParentElement]

            # AutomationID, LocalizedControlType
            if (
                    Element_Name is None
                    and Element_Class is None
                    and Element_AutomationID is not None
                    and Element_LocalizedControlType is not None

                    and AutomationE == Element_AutomationID
                    and LocalizedControlTypeE == Element_LocalizedControlType
            ):
                return [ParentElement]

            # AutomationID
            if (
                    Element_Name is None
                    and Element_Class is None
                    and Element_AutomationID is not None
                    and Element_LocalizedControlType is None
                    and AutomationE == Element_AutomationID
            ):
                return [ParentElement]

            # LocalizedControlType
            if (
                    Element_Name is None
                    and Element_Class is None
                    and Element_AutomationID is None
                    and Element_LocalizedControlType is not None

                    and LocalizedControlTypeE == Element_LocalizedControlType
            ):
                return [ParentElement]
            # Name, Class, AutomationID
            if (
                    Element_Name is not None
                    and Element_Class is not None
                    and Element_AutomationID is not None
                    and Element_LocalizedControlType is None

                    and NameE == Element_Name
                    and ClassE == Element_Class
                    and AutomationE == Element_AutomationID
            ):
                return [ParentElement]

            # Name, Class
            if (
                    Element_Name is not None
                    and Element_Class is not None
                    and Element_AutomationID is None
                    and Element_LocalizedControlType is None

                    and NameE == Element_Name
                    and ClassE == Element_Class
            ):
                return [ParentElement]

            # Name
            if (
                    (Element_Name is not None)
                    and (Element_Class is None)
                    and (Element_AutomationID is None)
                    and (Element_LocalizedControlType is None)

                    and NameE == Element_Name
            ):
                return [ParentElement]

            child_elements = ParentElement.FindAll(
                TreeScope.Children, Condition.TrueCondition
            )

            if child_elements.Count == 0:
                return []

            all_elements = []
            for each_child in child_elements:
                all_elements += _child_search(
                    each_child,
                    Element_Name,
                    Element_Class,
                    Element_AutomationID,
                    Element_LocalizedControlType,
                )

            return all_elements
        except:
            return []

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            (
                    (str(exc_type).replace("type ", "Error Type: "))
                    + ";"
                    + "Error Message: "
                    + str(exc_obj)
                    + ";"
                    + "File Name: "
                    + fname
                    + ";"
                    + "Line: "
                    + str(exc_tb.tb_lineno)
            )
        )
        return "zeuz_failed"


def _get_main_window(WindowName):
    try:
        MainWindowsList = AutomationElement.RootElement.FindAll(
            TreeScope.Children, Condition.TrueCondition
        )
        UnicodeWinName = WindowName
        for MainWindowElement in MainWindowsList:
            try:
                NameS = MainWindowElement.Current.Name
                if UnicodeWinName in NameS:
                    autoit.win_activate(NameS)
                    return MainWindowElement
            except:
                NameS = None

        return None
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            (
                    (str(exc_type).replace("type ", "Error Type: "))
                    + ";"
                    + "Error Message: "
                    + str(exc_obj)
                    + ";"
                    + "File Name: "
                    + fname
                    + ";"
                    + "Line: "
                    + str(exc_tb.tb_lineno)
            )
        )


@logger
def Click_Element_None_Mouse(
        Element, Expand=None, Invoke=None, Select=None, Toggle=None
):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        patter_list = Element.GetSupportedPatterns()
        if len(patter_list) == 0:
            # x = int (Element.Current.BoundingRectangle.X)
            # y = int (Element.Current.BoundingRectangle.Y)
            CommonUtil.ExecLog(sModuleInfo,
                               "We did not find any pattern for this object, so we will click by mouse with location",
                               1)
            x = (int)(
                Element.Current.BoundingRectangle.Right
                - Element.Current.BoundingRectangle.Width / 2
            )
            y = (int)(
                Element.Current.BoundingRectangle.Bottom
                - Element.Current.BoundingRectangle.Height / 2
            )
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            return "passed"
        else:
            for each in patter_list:
                pattern_name = Automation.PatternName(each)
                CommonUtil.ExecLog(sModuleInfo, "Pattern name attached to the current element is: %s " % pattern_name,
                                   1)

                # Expand and collapse actions
                if pattern_name == "ExpandCollapse":
                    if Expand:
                        # check to see if its expanded, if expanded, then do nothing... if not, expand it
                        status = Element.GetCurrentPattern(
                            ExpandCollapsePattern.Pattern
                        ).Current.ExpandCollapseState
                        if status == 0:
                            CommonUtil.ExecLog(sModuleInfo, "Expanding the item", 1)
                            Element.GetCurrentPattern(
                                ExpandCollapsePattern.Pattern
                            ).Expand()
                            return "passed"
                        elif status == 1:
                            CommonUtil.ExecLog(sModuleInfo, "Already expanded", 1)
                            return "passed"
                    elif Expand == False:
                        # check to see if its Collapsed, if Collapsed, then do nothing... if not, Collapse it
                        status = Element.GetCurrentPattern(
                            ExpandCollapsePattern.Pattern
                        ).Current.ExpandCollapseState
                        if status == 1:
                            CommonUtil.ExecLog(sModuleInfo, "Collapsing the item", 1)
                            Element.GetCurrentPattern(
                                ExpandCollapsePattern.Pattern
                            ).Collapse()
                            return "passed"
                        elif status == 0:
                            CommonUtil.ExecLog(sModuleInfo, "Already collapsed", 1)
                            return "passed"
                # Invoking actions
                elif pattern_name == "Invoke":
                    if Invoke:
                        CommonUtil.ExecLog(sModuleInfo, "Invoking the object", 1)
                        time.sleep(1)
                        Element.GetCurrentPattern(InvokePattern.Pattern).Invoke()
                        return "passed"
                # Selection of an item
                elif pattern_name == "SelectionItem":
                    CommonUtil.ExecLog(sModuleInfo, "Selecting an item", 1)
                    Element.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
                    time.sleep(1)
                    return "passed"
                # Toggling action

                elif pattern_name == "Toggle":
                    CommonUtil.ExecLog(sModuleInfo, "Toggling an item", 1)
                    Element.GetCurrentPattern(TogglePattern.Pattern).Toggle()
                    time.sleep(1)
                    return "passed"
                # if no patterns are found, then we do an actual mouse click
                else:
                    # x = int (Element.Current.BoundingRectangle.X)
                    # y = int (Element.Current.BoundingRectangle.Y)
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "We did not find any pattern for this object, so we will click by mouse with location",
                        1,
                    )
                    x = (int)(
                        Element.Current.BoundingRectangle.Right
                        - Element.Current.BoundingRectangle.Width / 2
                    )
                    y = (int)(
                        Element.Current.BoundingRectangle.Bottom
                        - Element.Current.BoundingRectangle.Height / 2
                    )
                    win32api.SetCursorPos((x, y))
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                    time.sleep(0.1)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
                    time.sleep(1)
                    return "passed"

        CommonUtil.ExecLog(sModuleInfo, "Unable to perform the action on the object", 3)
        return "zeuz_failed"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            (
                    (str(exc_type).replace("type ", "Error Type: "))
                    + ";"
                    + "Error Message: "
                    + str(exc_obj)
                    + ";"
                    + "File Name: "
                    + fname
                    + ";"
                    + "Line: "
                    + str(exc_tb.tb_lineno)
            )
        )

        return "zeuz_failed"


@logger
def Drag_and_Drop_Element(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    element_name = []
    window_name = []

    try:
        for left, mid, right in data_set:
            if mid == "element parameter":
                if left.strip().lower() == "element name":
                    element_name.append(right)

                elif left.strip().lower() == "window name":
                    window_name.append(right)

        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        while i != max_try:
            try:
                Element1 = Get_Element(data_set)
            except:
                pass
            if Element1 is None or Element in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element1 in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"

        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        while i != max_try:
            try:
                Element2 = Get_Element(data_set)
            except:
                True
            if Element2 is None or Element in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element2 in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"

        result = Drag_Object(Element1, Element2)
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not Drag element", 3)
            return "zeuz_failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Successfully dragged and dropped the element", 1)
            return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")


@logger
def Drag_Object(Element1_source, Element2_destination):
    try:
        print("clicking your element")
        print(Element1_source, Element2_destination)

        x_source = (int)(
            Element1_source.Current.BoundingRectangle.Right
            - Element1_source.Current.BoundingRectangle.Width / 2
        )
        y_source = (int)(
            Element1_source.Current.BoundingRectangle.Bottom
            - Element1_source.Current.BoundingRectangle.Height / 2
        )

        x_destination = (int)(
            Element2_destination.Current.BoundingRectangle.Right
            - Element2_destination.Current.BoundingRectangle.Width / 2
        )
        y_destination = (int)(
            Element2_destination.Current.BoundingRectangle.Bottom
            - Element2_destination.Current.BoundingRectangle.Height / 2
        )
        autoit.mouse_click_drag(
            x_source, y_source, x_destination, y_destination, button="left", speed=20
        )
        return "passed"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(
            (str(exc_type).replace("type ", "Error Type: "))
            + ";"
            + "Error Message: "
            + str(exc_obj)
            + ";"
            + "File Name: "
            + fname
            + ";"
            + "Line: "
            + str(exc_tb.tb_lineno)
        )
        return "zeuz_failed"


@logger
def Double_Click_Element(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        Element = None
        while i != max_try:
            try:
                Element = Get_Element(data_set)
            except:
                pass
            if Element is None or Element in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Could not find element.  Waiting and Trying again .... ",
                    2,
                )
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"
        x = (int)(
            Element.Current.BoundingRectangle.Right
            - Element.Current.BoundingRectangle.Width / 2
        )
        y = (int)(
            Element.Current.BoundingRectangle.Bottom
            - Element.Current.BoundingRectangle.Height / 2
        )
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error parsing data set"
        )


@logger
def Hover_Over_Element(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        Element = None
        while i != max_try:
            try:
                Element = Get_Element(data_set)
            except:
                True
            if Element is None or Element in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"
        x = (int)(
            Element.Current.BoundingRectangle.Right
            - Element.Current.BoundingRectangle.Width / 2
        )
        y = (int)(
            Element.Current.BoundingRectangle.Bottom
            - Element.Current.BoundingRectangle.Height / 2
        )
        win32api.SetCursorPos((x, y))

        autoit.mouse_move(x, y, speed=20)
        time.sleep(1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")


@logger
def Validate_Text(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        expected_text = ""
        for left, mid, right in data_set:
            if mid.strip().lower() == "action":
                expected_text = right

        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        Element = None
        while i != max_try:
            try:
                Element = Get_Element(data_set)
            except:
                pass
            if Element is None or Element in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"

        actual_text = str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.Value).strip().lower()

        if expected_text == actual_text:
            CommonUtil.ExecLog(sModuleInfo, "Text '%s' is found in the element" % expected_text, 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Couldn't find text '%s' in any element" % expected_text, 3)
            return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")


@logger
def Save_Text(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        variable_name = ""
        field = "value"
        for left, mid, right in data_set:
            if mid.strip().lower() == "action":
                variable_name = right
            elif mid.strip().lower() == "element parameter" and left.strip().lower() == "field":
                field = right.lower().strip()

        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        Element = None
        while i != max_try:
            try:
                Element = Get_Element(data_set)
            except:
                pass
            if Element is None or Element in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"

        actual_text = ""
        if field == "value":
            actual_text = str(
                Element.GetCurrentPattern(ValuePattern.Pattern).Current.Value
            ).strip()
        elif field == "name":
            actual_text = str(
                Element.GetCurrentPattern(ValuePattern.Pattern).Current.Name
            ).strip()
        elif field == "class":
            actual_text = str(
                Element.GetCurrentPattern(ValuePattern.Pattern).Current.ClassName
            ).strip()
        elif "id" in field:
            actual_text = str(
                Element.GetCurrentPattern(ValuePattern.Pattern).Current.AutomationId
            ).strip()
        elif "type" in field or "control" in field:
            actual_text = str(
                Element.GetCurrentPattern(
                    ValuePattern.Pattern
                ).Current.LocalizedControlType
            ).strip()

        Shared_Resources.Set_Shared_Variables(variable_name, actual_text)

        CommonUtil.ExecLog(sModuleInfo, "Text '%s' is saved in the variable '%s'" % (actual_text, variable_name), 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")


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

        if result_x in failed_tag_list or result_x == "" or result_x is None:
            return "zeuz_failed", ""
        return int(result_x), int(result_y)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error calculating coordinates")


@logger
def Enter_Text_In_Text_Box(data_set):
    """ Insert text """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        text = ""
        keystroke = True

        for left, mid, right in data_set:
            if mid.lower().strip() == "action":
                text = right
            elif left.lower().strip() == "method" and right.lower().strip() == "set value":
                keystroke = False

        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        Element = None
        while i != max_try:
            try:
                Element = Get_Element(data_set)
            except:
                pass
            if Element is None or Element in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1

        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element to enter text", 3)
            return "zeuz_failed"

        if keystroke:
            x = (int)(
                Element.Current.BoundingRectangle.Right
                - Element.Current.BoundingRectangle.Width / 2
            )
            y = (int)(
                Element.Current.BoundingRectangle.Bottom
                - Element.Current.BoundingRectangle.Height / 2
            )
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            time.sleep(0.5)
            autoit.send("^a")  # select all
            autoit.send(text)
        else:
            try:
                CommonUtil.ExecLog(sModuleInfo, "Trying to set the value by ValuePattern", 1)
                time.sleep(common_sleep)
                Element.GetCurrentPattern(ValuePattern.Pattern).SetValue(text)
            except:
                time.sleep(common_sleep)
                autoit.send("^a")
                autoit.send(text)
                CommonUtil.ExecLog(
                    sModuleInfo, "Retrying with autoit. Yet if it does not work please try 'keystroke' as method instead", 2
                )
                # return "zeuz_failed"

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Couln't enter text")


@logger
def Scroll(data_set):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        Element = None
        while i != max_try:
            try:
                Element = Get_Element(data_set)
            except:
                pass
            if Element is None or Element in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"
        x = (int)(
            Element.Current.BoundingRectangle.Right
            - Element.Current.BoundingRectangle.Width / 2
        )
        y = (int)(
            Element.Current.BoundingRectangle.Bottom
            - Element.Current.BoundingRectangle.Height / 2
        )
        win32api.SetCursorPos((x, y))

        autoit.mouse_wheel("up", 10)
        time.sleep(1)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")


@logger
def Get_Element(data_set):
    """ Insert text """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    element_name = ""
    window_name = ""
    element_class = None
    automationid = None
    control_type = None
    wait_time = 15
    index = 0
    # parse dataset and read data
    try:
        for left, mid, right in data_set:
            if mid == "element parameter":
                if left.strip().lower() == "element name":
                    element_name = right
                elif left.strip().lower() == "window name":
                    window_name = right
                elif left.strip().lower() == "element class":
                    element_class = right
                elif left.strip().lower() == "automation id":
                    automationid = right
                elif left.strip().lower() == "control type":
                    control_type = right
                elif left.strip().lower() == "wait time":
                    wait_time = int(right)
                elif left.strip().lower() == "index":
                    index = int(right.strip())

        if element_name == "":
            element_name = None  # element name can be empty if user want the full window as an element

        # Get element object
        all_elements = get_element(
            window_name,
            element_name,
            element_class,
            automationid,
            control_type,
            wait_time,
        )
        if all_elements == []:
            CommonUtil.ExecLog(sModuleInfo, "No element found", 2)
            return "zeuz_failed"
        if -len(all_elements) <= index < len(all_elements):
            # Todo: we need more logs here. check Locate Element
            pass
        else:
            CommonUtil.ExecLog(sModuleInfo, "index out of range", 2)
            return "zeuz_failed"
        patter_list = 0
        try:
            patter_list = Element.GetSupportedPatterns()
            if len(patter_list) == 0:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "No Pattern was detected for this element.  However we did find the element",
                    2,
                )

            else:
                pattern_found = []
                for each in patter_list:
                    try:
                        pattern_name = Automation.PatternName(each)
                        pattern_found.append(pattern_name)
                    except:
                        pass

                CommonUtil.ExecLog(sModuleInfo, "Following patterns were found: %s" % pattern_found, 1)
        except:
            pass

        return all_elements[index]
    except Exception:
        errMsg = "Could not get your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Run_Application(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        Desktop_app = ""
        for left, mid, right in data_set:
            if mid.strip().lower() == "action":
                Desktop_app = right.strip()

        autoit.send("^{ESC}")
        time.sleep(0.5)
        autoit.send(Desktop_app)
        time.sleep(0.5)
        autoit.send("{ENTER}")
        CommonUtil.ExecLog(sModuleInfo, "Successfully launched your app", 1)
        time.sleep(2)
        return "passed"
    except:
        CommonUtil.ExecLog(sModuleInfo, "Unable to start your app %s" % Desktop_app, 3)
        return "zeuz_failed"


@logger
def Close_Application(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        Desktop_app = ""
        for row in data_set:
            if str(row[1]).strip().lower() == "action":
                Desktop_app = str(row[2]).strip()

        if ".exe" not in Desktop_app:
            Desktop_app = Desktop_app + ".exe"
            os.system("TASKKILL /F /IM %s" % Desktop_app)
        else:
            os.system("TASKKILL /F /IM %s" % Desktop_app)
        CommonUtil.ExecLog(sModuleInfo, "Succesfully closed your app", 1)

        return "passed"
    except:
        CommonUtil.ExecLog(sModuleInfo, "Unable to start your app %s" % Desktop_app, 3)
        return "zeuz_failed"


@logger
def Keystroke_For_Element(data_set):
    """ Insert characters - mainly key combonations"""
    # Example: Ctrl+c
    # Repeats keypress if a number follows, example: tab,3

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Parse dataset
    try:
        time.sleep(2)
        keystroke_value = ""
        keystroke_char = ""
        for left, mid, right in data_set:
            left = left.strip().lower()
            if left == "autoit":  # Todo: organize this one
                autoit.send(right)
                return "passed"
            if "action" in mid:
                if left == "keystroke keys":
                    keystroke_value = right.lower()  # Store keystroke
                elif left == "keystroke chars":
                    keystroke_char = right

        if keystroke_value == "" and keystroke_char == "":
            CommonUtil.ExecLog(sModuleInfo, "Invalid action found", 3)
            return "zeuz_failed"

    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Perform action
    try:
        try:
            if keystroke_char != "":
                pyautogui.write(keystroke_char)
                CommonUtil.ExecLog(sModuleInfo, "Successfully entered characters %s" % keystroke_char, 1)
                return "passed"
        except:
            errMsg = "Could not enter characters for your element."
            return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

        count = 1
        if "," in keystroke_value:  # Check for delimiter indicating multiple keystrokes
            keystroke_value, count = keystroke_value.split(",")  # Separate keystroke and count
            count = int(count.strip())
        keys = keystroke_value.split("+")  # Split string into array
        keys = [x.strip() for x in keys]  # Clean it up

        for i in range(count):
            gui.hotkey(*keys)  # Send keypress (as individual values using the asterisk)

        CommonUtil.ExecLog(sModuleInfo, "Successfully entered keystroke", 1)
        return "passed"

    except Exception:
        errMsg = "Could not enter keystroke for your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
