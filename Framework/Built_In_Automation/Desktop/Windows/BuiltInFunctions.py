"""Windows automation file, element parameters can be found by running the inspectx64/x86.exe file"""
#########################
#                       #
#        Modules        #
#                       #
#########################

import sys, os

sys.path.append(os.path.dirname(__file__))
import pyautogui as gui  # https://pyautogui.readthedocs.io/en/latest/
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as Shared_Resources,
)
import inspect, time, datetime, os, sys
from Framework.Utilities import CommonUtil
from Framework.Utilities.decorators import logger

MODULE_NAME = inspect.getmodulename(__file__)


import clr, inspect
from _elementtree import Element

clr.AddReference("UIAutomationClient")
clr.AddReference("UIAutomationTypes")
clr.AddReference("UIAutomationProvider")
clr.AddReference("System.Windows.Forms")

import win32api
import win32con

from System.Windows.Automation import *


# this needs to be here on top, otherwise will return error
import clr, System

clr.AddReference("UIAutomationClient")
clr.AddReference("UIAutomationTypes")
clr.AddReference("UIAutomationProvider")
clr.AddReference("System.Windows.Forms")

import pyautogui  # Should be removed after we complete sequential actions
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

recur_count = 0  # To be deleted
common_sleep = 0


@logger
def go_to_desktop(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    Element = Element_only_search("", "Show desktop", "TrayShowDesktopButtonWClass")  # Todo: This line should generate bug so fix it.
    if Element == "zeuz_failed":
        CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
        return "zeuz_failed"
    try:
        result = Click_Element_None_Mouse(Element, None, True, None, None)
        if result == "zeuz_failed":
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
    expand = True

    # parse dataset and read data
    try:
        for left, mid, right in data_set:
            right = right.strip().lower()
            left = left.strip().lower()
            expand = not (left == "method" and right == "collapse")

    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "You have provided an invalid Click data.  Please refer to help", 3)
        CommonUtil.Exception_Handler(sys.exc_info(), None, "You have provided an invalid Click data.  Please refer to help")
        return "zeuz_failed"

    # Get element object
    # try for 10 seconds with 2 seconds delay
    max_try = 5
    sleep_in_sec = 2
    i = 0
    while i != max_try:
        Element = Get_Element(data_set)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
        else:
            break
        time.sleep(sleep_in_sec)
        i = i + 1
    if Element == "zeuz_failed":
        CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
        return "zeuz_failed"

    # If found Click element

    try:
        CommonUtil.ExecLog(sModuleInfo, "Element was located.  Performing action provided ", 1)
        result = Click_Element_None_Mouse(Element, expand)
        if result == "zeuz_failed":
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
            Element = Get_Element(data_set)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"

        x = int(
            Element.Current.BoundingRectangle.Right
            - Element.Current.BoundingRectangle.Width / 2
        )
        y = int(
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


"""
global recur_count
recur_count = 0
#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False
"""


def _found(dataset_val, object_val):
    try:
        if dataset_val[1] == "**":
            return dataset_val[0].lower() in object_val.lower()
        elif dataset_val[1] == "*":
            return dataset_val[0] in object_val
        else:
            return dataset_val[0] == object_val
    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        return False


@logger
def Element_only_search(
    window_name,
    element_name,
    element_class,
    element_automation,
    element_control,
    element_index
):
    # max_time is built in wait function.  It will try every seconds 15 times.
    try:
        ParentElement = _get_main_window(window_name)
        if ParentElement is None:
            return "zeuz_failed"

        all_elements = []
        all_elements += _child_search(
            ParentElement,
            element_name,
            element_class,
            element_automation,
            element_control,
            element_index
        )

        if all_elements:
            return all_elements
        else:
            return "zeuz_failed"

    except:
        return CommonUtil.Exception_Handler(sys.exc_info())



def _child_search(
    ParentElement,
    element_name,
    element_class,
    element_automation,
    element_control,
    element_index
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
        if (element_name, element_class, element_automation, element_control) == (None, None, None, None):
            return []
        NameE = ParentElement.Current.Name
        ClassE = ParentElement.Current.ClassName
        AutomationE = ParentElement.Current.AutomationId
        LocalizedControlTypeE = ParentElement.Current.LocalizedControlType

        all_elements = []
        found = True
        if found and element_name is not None and not _found(element_name, NameE): found = False
        if found and element_class is not None and not _found(element_class, ClassE): found = False
        if found and element_automation is not None and not _found(element_automation, AutomationE): found = False
        if found and element_control is not None and not _found(element_control, LocalizedControlTypeE): found = False
        """
        Below are 2 methods. 
        1st one is: if an element is found yet enter its descendants to find more (requires more time but safe)
        2nd one is: if an element is found dont need to go deeper anymore, search its siblings (requires less time)
        Assuming 1st method is better
        """
        if found:   # 1st method
            all_elements += [ParentElement]
            if len(all_elements) - 1 == element_index:
                return all_elements
        # if found: return [ParentElement]          # 2nd method

        child_elements = ParentElement.FindAll(TreeScope.Children, Condition.TrueCondition)

        if child_elements.Count == 0:
            return all_elements

        for each_child in child_elements:
            all_elements += _child_search(
                each_child,
                element_name,
                element_class,
                element_automation,
                element_control,
                element_index
            )
            if 0 <= element_index == len(all_elements) - 1:
                return all_elements

        return all_elements

    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        return []


@logger
def Parent_search(
    element_name, window_name, element_class, element_automation, element_control, element_index,
    parent_name, parent_class, parent_automation, parent_control,
):
    try:
        ParentElement = _get_main_window(window_name)
        if ParentElement is None:
            return "zeuz_failed"

        all_elements = []
        all_elements += _child_search_with_parent(
            ParentElement, element_name, element_class, element_automation, element_control, element_index,
            parent_name, parent_class, parent_automation, parent_control, False
        )

        if all_elements:
            return all_elements
        else:
            return "zeuz_failed"

    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _child_search_with_parent(
    ParentElement, element_name, element_class, element_automation, element_control, element_index,
    parent_name, parent_class, parent_automation, parent_control, parent_found
):
    try:
        NameE = ParentElement.Current.Name
        ClassE = ParentElement.Current.ClassName
        AutomationE = ParentElement.Current.AutomationId
        LocalizedControlTypeE = ParentElement.Current.LocalizedControlType

        all_elements = []
        if not parent_found:
            found = True
            if found and element_name is not None and not _found(parent_name, NameE): found = False
            if found and element_class is not None and not _found(parent_class, ClassE): found = False
            if found and element_automation is not None and not _found(parent_automation, AutomationE): found = False
            if found and element_control is not None and not _found(parent_control, LocalizedControlTypeE): found = False
            parent_found = found

        else:
            found = True
            if found and element_name is not None and not _found(element_name, NameE): found = False
            if found and element_class is not None and not _found(element_class, ClassE): found = False
            if found and element_automation is not None and not _found(element_automation, AutomationE): found = False
            if found and element_control is not None and not _found(element_control, LocalizedControlTypeE): found = False
            if found:
                all_elements += [ParentElement]
                if len(all_elements) - 1 == element_index:
                    return all_elements

        child_elements = ParentElement.FindAll(TreeScope.Children, Condition.TrueCondition)
        if child_elements.Count == 0:
            return all_elements

        for each_child in child_elements:
            all_elements += _child_search_with_parent(
                each_child, element_name, element_class, element_automation, element_control, element_index,
                parent_name, parent_class, parent_automation, parent_control, parent_found
            )
            if 0 <= element_index == len(all_elements) - 1:
                return all_elements

        return all_elements

    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        return []


@logger
def Sibling_search(
    element_name, window_name, element_class, element_automation, element_control, element_index,
    parent_name, parent_class, parent_automation, parent_control,
    sibling_name, sibling_class, sibling_automation, sibling_control,
):
    try:
        ParentElement = _get_main_window(window_name)
        if ParentElement is None:
            return "zeuz_failed"

        all_elements = []
        all_elements += _child_search_with_parent_sibling(
            ParentElement, element_name, element_class, element_automation, element_control, element_index,
            parent_name, parent_class, parent_automation, parent_control,
            sibling_name, sibling_class, sibling_automation, sibling_control, False
        )

        if all_elements:
            return all_elements
        else:
            return "zeuz_failed"

    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


sibling_found = False
@logger
def _child_search_with_parent_sibling(
    ParentElement, element_name, element_class, element_automation, element_control, element_index,
    parent_name, parent_class, parent_automation, parent_control,
    sibling_name, sibling_class, sibling_automation, sibling_control, parent_found
):
    try:
        NameE = ParentElement.Current.Name
        ClassE = ParentElement.Current.ClassName
        AutomationE = ParentElement.Current.AutomationId
        LocalizedControlTypeE = ParentElement.Current.LocalizedControlType

        all_elements = []
        parent_level = False
        global sibling_found
        if not parent_found:
            found = True
            if found and element_name is not None and not _found(parent_name, NameE): found = False
            if found and element_class is not None and not _found(parent_class, ClassE): found = False
            if found and element_automation is not None and not _found(parent_automation, AutomationE): found = False
            if found and element_control is not None and not _found(parent_control, LocalizedControlTypeE): found = False
            parent_found = found
            parent_level = found

        else:
            found = True
            if found and element_name is not None and not _found(sibling_name, NameE): found = False
            if found and element_class is not None and not _found(sibling_class, ClassE): found = False
            if found and element_automation is not None and not _found(sibling_automation, AutomationE): found = False
            if found and element_control is not None and not _found(sibling_control, LocalizedControlTypeE): found = False
            sibling_found = True if sibling_found else found

            found = True
            if found and element_name is not None and not _found(element_name, NameE): found = False
            if found and element_class is not None and not _found(element_class, ClassE): found = False
            if found and element_automation is not None and not _found(element_automation, AutomationE): found = False
            if found and element_control is not None and not _found(element_control, LocalizedControlTypeE): found = False
            if found:
                all_elements += [ParentElement]
                if len(all_elements) - 1 == element_index:
                    return all_elements

        child_elements = ParentElement.FindAll(TreeScope.Children, Condition.TrueCondition)
        if child_elements.Count == 0:
            return all_elements

        for each_child in child_elements:
            temp = _child_search_with_parent_sibling(
                each_child, element_name, element_class, element_automation, element_control, element_index,
                parent_name, parent_class, parent_automation, parent_control,
                sibling_name, sibling_class, sibling_automation, sibling_control, parent_found
            )
            if not parent_level:
                all_elements += temp
            elif parent_level and sibling_found:
                all_elements += temp
            if 0 <= element_index == len(all_elements) - 1:
                return all_elements
        if parent_level:
            sibling_found = False

        return all_elements

    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        return []


@logger
def Get_Element(data_set):
    """ Top function for searching an element """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    element_name, window_name, element_class, element_automation, element_control, elem = None, None, None, None, None, False
    parent_name, parent_class, parent_automation, parent_control, parent = None, None, None, None, False
    sibling_name, sibling_class, sibling_automation, sibling_control, sibling = None, None, None, None, False
    wait_time = 15
    element_index = 0
    # parse dataset and read data
    try:
        for left, mid, right in data_set:
            left = left.strip().lower()

            mid = mid.strip().lower()
            if left == "wait time": wait_time = int(right)  # Todo: this will be max retry
            elif left == "index": element_index = int(right.strip())
            elif "window" in left: window_name = [right, _count_star(left)]

            if mid == "element parameter":
                elem = True
                if "classname" in left: element_class = [right, _count_star(left)]
                elif "name" in left: element_name = [right, _count_star(left)]
                elif "automation" in left: element_automation = [right, _count_star(left)]  # automationid
                elif "control" in left: element_control = [right, _count_star(left)]    # localizedcontroltype

            elif mid == "parent parameter":
                parent = True
                if "classname" in left: parent_class = [right, _count_star(left)]
                elif "name" in left: parent_name = [right, _count_star(left)]
                elif "automation" in left: parent_automation = [right, _count_star(left)]  # automationid
                elif "control" in left: parent_control = [right, _count_star(left)]    # localizedcontroltype

            elif mid == "sibling parameter":
                sibling = True
                if "classname" in left: sibling_class = [right, _count_star(left)]
                elif "name" in left: sibling_name = [right, _count_star(left)]
                elif "automation" in left: sibling_automation = [right, _count_star(left)]  # automationid
                elif "control" in left: sibling_control = [right, _count_star(left)]    # localizedcontroltype

        if not elem:
            CommonUtil.ExecLog(sModuleInfo, "No element info is given", 3)
            return "zeuz_failed"
        if elem and (element_name, element_class, element_automation, element_control) == (None, None, None, None):
            CommonUtil.ExecLog(sModuleInfo, "We support only 'Window', 'Name', 'ClassName', 'LocalizedControlType', 'AutomationId'", 3)
            return "zeuz_failed"
        if sibling and not parent:
            CommonUtil.ExecLog(sModuleInfo, "A common PARENT of both ELEMENT and SIBLING should be provided", 3)
            return "zeuz_failed"
        if parent and (parent_name, parent_class, parent_automation, parent_control) == (None, None, None, None):
            CommonUtil.ExecLog(sModuleInfo, "We support only 'Window', 'Name', 'ClassName', 'LocalizedControlType', 'AutomationId'", 3)
            return "zeuz_failed"
        if sibling and (sibling_name, sibling_class, sibling_automation, sibling_control) == (None, None, None, None):
            CommonUtil.ExecLog(sModuleInfo, "We support only 'Window', 'Name', 'ClassName', 'LocalizedControlType', 'AutomationId'", 3)
            return "zeuz_failed"

        if parent and sibling:
            all_elements = Sibling_search(
                element_name, window_name, element_class, element_automation, element_control, element_index,
                parent_name, parent_class, parent_automation, parent_control,
                sibling_name, sibling_class, sibling_automation, sibling_control,
            )
        elif parent:
            all_elements = Parent_search(
                element_name, window_name, element_class, element_automation, element_control, element_index,
                parent_name, parent_class, parent_automation, parent_control,
            )
        else:
            all_elements = Element_only_search(
                window_name, element_name, element_class, element_automation, element_control, element_index
            )
        if all_elements == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "No element found", 3)
            return "zeuz_failed"
        if -len(all_elements) <= element_index < len(all_elements):
            CommonUtil.ExecLog(sModuleInfo, "Returning the element of index = %d" % element_index, 1)
        else:
            CommonUtil.ExecLog(sModuleInfo, "index out of range", 2)
            return "zeuz_failed"

        try:
            patter_list = Element.GetSupportedPatterns()
            if len(patter_list) == 0:
                CommonUtil.ExecLog(sModuleInfo, "No Pattern was detected for this element. However we did find the element", 2)

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

        return all_elements[element_index]
    except Exception:
        errMsg = "Could not get your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


def _get_main_window(WindowName):
    try:
        if WindowName is None:  # if window name is not specified in dataset
            return AutomationElement.RootElement

        MainWindowsList = AutomationElement.RootElement.FindAll(
            TreeScope.Children, Condition.TrueCondition
        )
        for MainWindowElement in MainWindowsList:
            try:
                NameS = MainWindowElement.Current.Name
                if _found(WindowName, NameS):
                    autoit.win_activate(NameS)
                    return MainWindowElement
            except:
                pass

        return None
    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        return None

@logger
def Click_Element_None_Mouse(Element, Expand=True):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        patter_list = Element.GetSupportedPatterns()
        if len(patter_list) == 0:
            # x = int (Element.Current.BoundingRectangle.X)
            # y = int (Element.Current.BoundingRectangle.Y)
            CommonUtil.ExecLog(sModuleInfo, "We did not find any pattern for this object, so we will click by mouse with location", 1)
            x = int(
                Element.Current.BoundingRectangle.Right
                - Element.Current.BoundingRectangle.Width / 2
            )
            y = int(
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
                CommonUtil.ExecLog(sModuleInfo, "Pattern name attached to the current element is: %s " % pattern_name, 1)

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
                    else:
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
                    x = int(
                        Element.Current.BoundingRectangle.Right
                        - Element.Current.BoundingRectangle.Width / 2
                    )
                    y = int(
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
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Drag_and_Drop_Element(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    element_name = []
    window_name = []

    try:
        for left, mid, right in data_set:
            if mid.strip().lower() == "element parameter":
                if left.strip().lower() == "name":
                    element_name.append(right)

                elif left.strip().lower() == "window":
                    window_name.append(right)

        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        while i != max_try:
            # Todo: there should be a bug here
            Element1 = Get_Element(data_set)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element1 == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"

        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        while i != max_try:
            # Todo: there should be a bug here
            Element2 = Get_Element(data_set)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element2 == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"

        result = Drag_Object(Element1, Element2)
        if result == "zeuz_failed":
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

        x_source = int(
            Element1_source.Current.BoundingRectangle.Right
            - Element1_source.Current.BoundingRectangle.Width / 2
        )
        y_source = int(
            Element1_source.Current.BoundingRectangle.Bottom
            - Element1_source.Current.BoundingRectangle.Height / 2
        )

        x_destination = int(
            Element2_destination.Current.BoundingRectangle.Right
            - Element2_destination.Current.BoundingRectangle.Width / 2
        )
        y_destination = int(
            Element2_destination.Current.BoundingRectangle.Bottom
            - Element2_destination.Current.BoundingRectangle.Height / 2
        )
        autoit.mouse_click_drag(
            x_source, y_source, x_destination, y_destination, button="left", speed=20
        )
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Double_Click_Element(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        while i != max_try:
            Element = Get_Element(data_set)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Could not find element.  Waiting and Trying again .... ",
                    2,
                )
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"
        x = int(
            Element.Current.BoundingRectangle.Right
            - Element.Current.BoundingRectangle.Width / 2
        )
        y = int(
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
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")


@logger
def Hover_Over_Element(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        while i != max_try:
            Element = Get_Element(data_set)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"
        x = int(
            Element.Current.BoundingRectangle.Right
            - Element.Current.BoundingRectangle.Width / 2
        )
        y = int(
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
        while i != max_try:
            Element = Get_Element(data_set)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element == "zeuz_failed":
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
def Save_Attribute(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        variable_name = ""
        field = "value"
        for left, mid, right in data_set:
            if mid.strip().lower() == "save parameter":
                field = left.lower().strip()
                variable_name = right.strip()

        # Get element object
        # try for 10 seconds with 2 seconds delay
        max_try = 5
        sleep_in_sec = 2
        i = 0
        while i != max_try:
            Element = Get_Element(data_set)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"

        actual_text = ""
        if "value" in field:
            actual_text = str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.Value).strip()
        elif "name" in field:
            actual_text = str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.Name).strip()
        elif "class" in field:
            actual_text = str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.ClassName).strip()
        elif "id" in field:
            actual_text = str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.AutomationId).strip()
        elif "type" in field or "control" in field:
            actual_text = str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.LocalizedControlType).strip()

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

        if result_x == "zeuz_failed" or result_x == "" or result_x is None:
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
        while i != max_try:
            Element = Get_Element(data_set)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1

        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find element to enter text", 3)
            return "zeuz_failed"

        if keystroke:
            x = int(
                Element.Current.BoundingRectangle.Right
                - Element.Current.BoundingRectangle.Width / 2
            )
            y = int(
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
        while i != max_try:
            Element = Get_Element(data_set)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find element.  Waiting and Trying again .... ", 2)
            else:
                break
            time.sleep(sleep_in_sec)
            i = i + 1
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"
        x = int(
            Element.Current.BoundingRectangle.Right
            - Element.Current.BoundingRectangle.Width / 2
        )
        y = int(
            Element.Current.BoundingRectangle.Bottom
            - Element.Current.BoundingRectangle.Height / 2
        )
        win32api.SetCursorPos((x, y))

        autoit.mouse_wheel("up", 10)
        time.sleep(1)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")


def _count_star(value):
    count = 0
    for i in value.replace(" ", ""):
        if i == "*":
            count += 1
        else:
            return "*"*count


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
        for left, mid, right in data_set:
            if mid.strip().lower() == "action":
                Desktop_app = right.strip()

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
            if "action" in mid.lower():
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
