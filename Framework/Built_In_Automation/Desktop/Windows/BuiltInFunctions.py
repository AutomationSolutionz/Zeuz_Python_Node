"""Windows automation file, element parameters can be found by running the inspectx64/x86.exe file"""
#########################
#                       #
#        Modules        #
#                       #
#########################
code_debug = False
tabs = 0
import sys, os
import re
from collections import deque

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

import win32api
import win32con



# this needs to be here on top, otherwise will return error
import clr, System
dll_path = os.getcwd().split("Framework")[0] + "Framework" + os.sep + "windows_dll_files" + os.sep
clr.AddReference(dll_path+"UIAutomationClient")
clr.AddReference(dll_path+"UIAutomationTypes")
clr.AddReference(dll_path+"UIAutomationProvider")
clr.AddReference("System.Windows.Forms")

from System.Windows.Automation import *
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
unnecessary_sleep = 0
gui_action_sleep = 2


@logger
def go_to_desktop(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    Element = Element_only_search(None, None, ["Show desktop", ""], ["TrayShowDesktopButtonWClass", ""], None, None, 0)[0]
    if Element == "zeuz_failed":
        CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
        return "zeuz_failed"
    try:
        result = Click_Element_None_Mouse(Element)
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
    Gui = False

    # parse dataset and read data
    try:
        for left, mid, right in data_set:
            right = right.strip().lower()
            left = left.strip().lower()
            if left == "method":
                if right == "collapse":
                    expand = False
                elif right == "gui":
                    Gui = True
    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "You have provided an invalid Click data.  Please refer to help", 3)
        CommonUtil.Exception_Handler(sys.exc_info(), None, "You have provided an invalid Click data.  Please refer to help")
        return "zeuz_failed"

    Element = Get_Element(data_set)
    if Element == "zeuz_failed":
        return "zeuz_failed"

    # If found Click element

    try:
        CommonUtil.ExecLog(sModuleInfo, "Element was located.  Performing action provided ", 1)
        result = Click_Element_None_Mouse(Element, expand, Gui)
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
        Element = Get_Element(data_set)
        if Element == "zeuz_failed":
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


def _count_star(value):
    count = 0
    for i in value.replace(" ", ""):
        if i == "*":
            count += 1
        else:
            return "*"*count


def _not_found_log(element_name, element_class, element_automation, element_control):
    msg = "The following element is not found\n"
    if element_name is not None:
        msg += '%sName="%s"' % (element_name[1], element_name[0])
    if element_control is not None:
        msg += ', %sControlType="%s"' % (element_control[1], element_control[0])
    if element_class is not None:
        msg += ', %sClass="%s"' % (element_class[1], element_class[0])
    if element_automation is not None:
        msg += ', %sAutomationId="%s"' % (element_automation[1], element_automation[0])
    return msg


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
    Parent_Element,
    window_name,
    element_name,
    element_class,
    element_automation,
    element_control,
    element_index
):
    # max_time is built in wait function.  It will try every seconds 15 times.
    try:
        if Parent_Element is not None:
            ParentElement = Parent_Element
            element_index = -1
        else:
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


def _child_bfs_search(
    ParentElement,
    element_name,
    element_class,
    element_automation,
    element_control,
    element_index
):
    try:
        q = deque()
        child_elements = ParentElement.FindAll(TreeScope.Children, Condition.TrueCondition)
        if child_elements.Count == 0:
            return []
        for each_child in child_elements:
            q.append(each_child)
        all_elements = []
        while q:
            child = q.popleft()
            NameE = child.Current.Name
            ClassE = child.Current.ClassName
            AutomationE = child.Current.AutomationId
            LocalizedControlTypeE = child.Current.LocalizedControlType
            found = True
            if found and element_name is not None and not _found(element_name, NameE): found = False
            if found and element_class is not None and not _found(element_class, ClassE): found = False
            if found and element_automation is not None and not _found(element_automation, AutomationE): found = False
            if found and element_control is not None and not _found(element_control, LocalizedControlTypeE): found = False
            if found:
                all_elements.append(child)
            if element_index == len(all_elements) - 1:
                return all_elements[element_index]
            child_elements = child.FindAll(TreeScope.Children, Condition.TrueCondition)
            if child_elements.Count != 0:
                for each in child_elements:
                    q.append(each)

        if -len(all_elements) <= element_index < len(all_elements):
            return all_elements[element_index]  # in case of, negative index
        else:
            return []
    except:
        CommonUtil.Exception_Handler(sys.exc_info())
        return []

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
                if code_debug: print('name="%s", controlType="%s", automationId="%s", class="%s"' % (NameE, LocalizedControlTypeE, AutomationE, ClassE))
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
                if code_debug: print('name="%s", controlType="%s", automationId="%s", class="%s"' % (NameE, LocalizedControlTypeE, AutomationE, ClassE))
                return all_elements
        if all_elements:
            if code_debug: print('name="%s", controlType="%s", automationId="%s", class="%s"' % (NameE, LocalizedControlTypeE, AutomationE, ClassE))

        return all_elements

    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        return []


@logger
def Parent_search(
    Parent_Element, element_name, window_name, element_class, element_automation, element_control, element_index,
    parent_name, parent_class, parent_automation, parent_control,
):
    try:
        if Parent_Element is not None:
            ParentElement = Parent_Element
            element_index = -1
        else:
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
            if found and parent_name is not None and not _found(parent_name, NameE): found = False
            if found and parent_class is not None and not _found(parent_class, ClassE): found = False
            if found and parent_automation is not None and not _found(parent_automation, AutomationE): found = False
            if found and parent_control is not None and not _found(parent_control, LocalizedControlTypeE): found = False
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
    Parent_Element, element_name, window_name, element_class, element_automation, element_control, element_index,
    parent_name, parent_class, parent_automation, parent_control,
    sibling_name, sibling_class, sibling_automation, sibling_control,
):
    try:
        if Parent_Element is not None:
            ParentElement = Parent_Element
            element_index = -1
        else:
            ParentElement = _get_main_window(window_name)
        if ParentElement is None:
            return "zeuz_failed"
        global sibling_found
        sibling_found = False
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
            if found and parent_name is not None and not _found(parent_name, NameE): found = False
            if found and parent_class is not None and not _found(parent_class, ClassE): found = False
            if found and parent_automation is not None and not _found(parent_automation, AutomationE): found = False
            if found and parent_control is not None and not _found(parent_control, LocalizedControlTypeE): found = False
            parent_found = found
            parent_level = found

        else:
            found = True
            if found and sibling_name is not None and not _found(sibling_name, NameE): found = False
            if found and sibling_class is not None and not _found(sibling_class, ClassE): found = False
            if found and sibling_automation is not None and not _found(sibling_automation, AutomationE): found = False
            if found and sibling_control is not None and not _found(sibling_control, LocalizedControlTypeE): found = False
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
            all_elements += temp
        if parent_level:
            if sibling_found and 0 <= element_index == len(all_elements) - 1:
                sibling_found = False
                return all_elements
            else:
                sibling_found = False
                return []

        return all_elements

    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        return []


def _element_path_parser(element_path: str):
    try:
        element_name, element_control, element_automation, element_class, element_index = None, None, None, None, 0
        element_path = element_path.strip()
        if element_path.startswith(".."):
            exact = False
            element_path = element_path[element_path.find(">") + 1:].strip()
        else:
            exact = True

        while True:
            attribute = element_path[:element_path.find("=")].strip().lower()
            element_path = element_path[element_path.find("=") + 1:].strip()
            att_value = re.findall('\d+', element_path)[0].strip() if "index" in attribute else re.findall('(\'[^\']*\'|"[^"]*")', element_path)[0].strip()
            # regex meaning = inside single quotation zero or more not(single_quote) OR inside double quotation zero or more not(double_quote)

            if "index" in attribute and element_path[element_path.find(att_value) - 1] in ("'", '"'):
                element_path = element_path[len(att_value) + 2:].strip()
            else:
                element_path = element_path[len(att_value):].strip()
            if "index" not in attribute: att_value = att_value[1:-1]

            if "class" in attribute: element_class = [att_value, _count_star(attribute)]
            elif "name" in attribute: element_name = [att_value, _count_star(attribute)]
            elif "automation" in attribute: element_automation = [att_value, _count_star(attribute)]  # automationid
            elif "control" in attribute: element_control = [att_value, _count_star(attribute)]  # localizedcontroltype
            elif "index" in attribute: element_index = int(att_value)

            if element_path[0] == ",": element_path = element_path[1:]
            elif element_path[0] == ">": element_path = element_path[1:]; break

        return element_path, exact, element_name, element_control, element_automation, element_class, element_index
    except:
        CommonUtil.Exception_Handler(sys.exc_info())
        return "", "error", None, None, None, None, 0


@logger
def Element_path_search(window_name, element_path):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        ParentElement = _get_main_window(window_name)
        if ParentElement is None:
            return "zeuz_failed"
        """
        ...>*Name='panel',**control="screen">**name='message',index=5>...> *Name='submit',**control='button'>
        """
        if window_name is None:
            CommonUtil.ExecLog(sModuleInfo, 'Searching for:\n%s' % element_path[:-1], 1)
        else:
            CommonUtil.ExecLog(sModuleInfo, 'Window="%s" is selected. We are stepping inside the Window and will search for:\n%s'
                % (ParentElement.Current.Name, element_path[:-1]), 1)
        global tabs
        tabs = 0
        temp = _child_search_by_path(
            ParentElement,
            element_path,
            sModuleInfo
        )
        if temp == []: temp = "zeuz_failed"
        return temp

    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _child_search_by_path(
    ParentElement,
    element_path,
    sModuleInfo
):
    element_name, element_class, element_automation, element_control = None, None, None, None
    global tabs
    try:
        element_path, exact, element_name, element_control, element_automation, element_class, element_index = _element_path_parser(element_path)
        if exact == "error":
            return []
        if (element_name, element_class, element_automation, element_control) == (None, None, None, None):
            CommonUtil.ExecLog(sModuleInfo, "Element information is missing in a potion of Element Path", 3)
            return []
        if element_index < 0:
            CommonUtil.ExecLog(sModuleInfo, "Please provide positive index in case of Element Path search", 2)
        if exact:
            child_elements = ParentElement.FindAll(TreeScope.Children, Condition.TrueCondition)
            if child_elements.Count == 0:
                CommonUtil.ExecLog(sModuleInfo, "The following element has no child:\n" + 'Name="%s", ControlType="%s", Class="%s", AutomationId="%s"' %
                (ParentElement.Current.Name, ParentElement.Current.LocalizedControlType, ParentElement.Current.ClassName, ParentElement.Current.AutomationId), 3)
                return []
            all_elements = []
            for each_child in child_elements:
                NameE = each_child.Current.Name
                ClassE = each_child.Current.ClassName
                AutomationE = each_child.Current.AutomationId
                LocalizedControlTypeE = each_child.Current.LocalizedControlType
                if code_debug: print("  " * tabs + 'name="%s", controlType="%s", automationId="%s", class="%s"' % (NameE, LocalizedControlTypeE, AutomationE, ClassE))

                found = True
                if found and element_name is not None and not _found(element_name, NameE): found = False
                if found and element_class is not None and not _found(element_class, ClassE): found = False
                if found and element_automation is not None and not _found(element_automation, AutomationE): found = False
                if found and element_control is not None and not _found(element_control, LocalizedControlTypeE): found = False

                if found: all_elements.append(each_child)
                if 0 <= element_index == len(all_elements) - 1: break

            if code_debug: tabs += 1
            if not (-len(all_elements) <= element_index < len(all_elements)):
                CommonUtil.ExecLog(sModuleInfo, _not_found_log(element_name, element_class, element_automation, element_control), 3)
                return []
            if element_path:
                return _child_search_by_path(
                    all_elements[element_index],
                    element_path,
                    sModuleInfo
                )
            else:
                return [all_elements[element_index]]

        else:
            temp = _child_search(
                ParentElement,
                element_name,
                element_class,
                element_automation,
                element_control,
                element_index
            )
            if temp == []:
                CommonUtil.ExecLog(sModuleInfo, _not_found_log(element_name, element_class, element_automation, element_control), 3)
                return []
            if element_path:
                return _child_search_by_path(
                    temp[element_index],
                    element_path,
                    sModuleInfo
                )
            else:
                return [temp]

    except:
        CommonUtil.Exception_Handler(sys.exc_info(), None, _not_found_log(element_name, element_class, element_automation, element_control))
        return []

@logger
def Get_Element(data_set, wait_time=10, Parent_Element=None):
    """ Top function for searching an element """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    element_name, window_name, element_class, element_automation, element_control, element_path, elem = None, None, None, None, None, "", False
    parent_name, parent_class, parent_automation, parent_control, parent = None, None, None, None, False
    sibling_name, sibling_class, sibling_automation, sibling_control, sibling = None, None, None, None, False
    element_index = 0
    try:
        for left, mid, right in data_set:
            left = left.strip().lower()
            mid = mid.strip().lower()

            if left == "wait time": wait_time = int(right)
            elif left == "index": element_index = int(right.strip())
            elif "window" in left: window_name = [right, _count_star(left)]

            if mid == "element parameter":
                elem = True
                if "class" in left: element_class = [right, _count_star(left)]
                elif "name" in left: element_name = [right, _count_star(left)]
                elif "automation" in left: element_automation = [right, _count_star(left)]  # automationid
                elif "control" in left: element_control = [right, _count_star(left)]    # localizedcontroltype
                elif "path" in left: element_path = right.strip()

            elif mid == "parent parameter":
                parent = True
                if "class" in left: parent_class = [right, _count_star(left)]
                elif "name" in left: parent_name = [right, _count_star(left)]
                elif "automation" in left: parent_automation = [right, _count_star(left)]  # automationid
                elif "control" in left: parent_control = [right, _count_star(left)]    # localizedcontroltype

            elif mid == "sibling parameter":
                sibling = True
                if "class" in left: sibling_class = [right, _count_star(left)]
                elif "name" in left: sibling_name = [right, _count_star(left)]
                elif "automation" in left: sibling_automation = [right, _count_star(left)]  # automationid
                elif "control" in left: sibling_control = [right, _count_star(left)]    # localizedcontroltype

        if not elem:
            CommonUtil.ExecLog(sModuleInfo, "No element info is given", 3)
            return "zeuz_failed"
        if elem and (element_name, element_class, element_automation, element_control, element_path) == (None, None, None, None, ""):
            CommonUtil.ExecLog(sModuleInfo, "We support only 'Window', 'Name', 'ClassName', 'LocalizedControlType', 'AutomationId', 'element path'", 3)
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
        if window_name is None and Parent_Element is None and not element_path:
            CommonUtil.ExecLog(sModuleInfo, "You should provide 'Window' otherwise the search won't be efficient", 2)

        s = time.time()
        while True:
            if element_path:
                if element_path[-1] != ">": element_path = element_path.strip() + ">"
                if element_path[0] == ">": element_path = element_path[1:]
                if element_index != 0:
                    CommonUtil.ExecLog(sModuleInfo, "Index is not allowed other than 0 for 'element path' search. Setting index = 0", 2)
                all_elements = Element_path_search(window_name, element_path)

            elif parent and sibling:
                all_elements = Sibling_search(
                    Parent_Element, element_name, window_name, element_class, element_automation, element_control, element_index,
                    parent_name, parent_class, parent_automation, parent_control,
                    sibling_name, sibling_class, sibling_automation, sibling_control,
                )
            elif parent:
                all_elements = Parent_search(
                    Parent_Element, element_name, window_name, element_class, element_automation, element_control, element_index,
                    parent_name, parent_class, parent_automation, parent_control,
                )
            else:
                all_elements = Element_only_search(
                    Parent_Element, window_name, element_name, element_class, element_automation, element_control, element_index
                )

            if all_elements != "zeuz_failed" and -len(all_elements) <= element_index < len(all_elements) or time.time() > s + wait_time:
                break
            time.sleep(0.5)   # Sleep is needed. dont need unlimited searching

        if all_elements == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find the element", 3)
            return "zeuz_failed"
        if Parent_Element is not None:
            return all_elements
        if -len(all_elements) <= element_index < len(all_elements):
            if element_index == 0:
                CommonUtil.ExecLog(sModuleInfo, "Returning the 1st element that is found", 1)
            else:
                CommonUtil.ExecLog(sModuleInfo, "Returning the element of index = %d" % element_index, 1)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Index out of range", 3)
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
def Click_Element_None_Mouse(Element, Expand=True, Gui=False):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        patter_list = Element.GetSupportedPatterns()
        if len(patter_list) == 0 or Gui:
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
                    time.sleep(unnecessary_sleep)
                    Element.GetCurrentPattern(InvokePattern.Pattern).Invoke()
                    return "passed"
                # Selection of an item
                elif pattern_name == "SelectionItem":
                    CommonUtil.ExecLog(sModuleInfo, "Selecting an item", 1)
                    Element.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
                    time.sleep(unnecessary_sleep)
                    return "passed"
                # Toggling action

                elif pattern_name == "Toggle":
                    CommonUtil.ExecLog(sModuleInfo, "Toggling an item", 1)
                    Element.GetCurrentPattern(TogglePattern.Pattern).Toggle()
                    time.sleep(unnecessary_sleep)
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
                    time.sleep(unnecessary_sleep)
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

    source = []
    destination = []
    try:
        for left, mid, right in data_set:
            if "src" in left or "source" in left:
                source.append((left.replace("src", "").replace("source", ""), mid, right))
            elif "dst" in left or "destination" in left:
                destination.append((left.replace("dst", "").replace("destination", ""), mid, right))

        Element1 = Get_Element(source)
        if Element1 == "zeuz_failed":
            return "zeuz_failed"

        Element2 = Get_Element(destination)
        if Element2 == "zeuz_failed":
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
        Gui = False
        for left, mid, right in data_set:
            right = right.strip().lower()
            left = left.strip().lower()
            if left == "method" and right == "gui":
                    Gui = True

        Element = Get_Element(data_set)
        if Element == "zeuz_failed":
            return "zeuz_failed"

        patter_list = Element.GetSupportedPatterns()
        if len(patter_list) > 0 and not Gui:
            for each in patter_list:
                pattern_name = Automation.PatternName(each)
                CommonUtil.ExecLog(sModuleInfo, "Pattern name attached to the current element is: %s " % pattern_name, 1)
                if pattern_name == "Invoke":
                    CommonUtil.ExecLog(sModuleInfo, "Double Invoking the object", 1)
                    Element.GetCurrentPattern(InvokePattern.Pattern).Invoke()
                    time.sleep(0.1)
                    Element.GetCurrentPattern(InvokePattern.Pattern).Invoke()
                    return "passed"

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
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")


@logger
def Hover_Over_Element(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        Element = Get_Element(data_set)
        if Element == "zeuz_failed":
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
        time.sleep(unnecessary_sleep)
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

        Element = Get_Element(data_set)
        if Element == "zeuz_failed":
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

        Element = Get_Element(data_set)
        if Element == "zeuz_failed":
            return "zeuz_failed"

        actual_text = ""
        if "value" in field:
            actual_text = str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.Value).strip()
        elif "name" in field:
            actual_text = str(Element.Current.Name).strip()
        elif "class" in field:
            actual_text = str(Element.Current.ClassName).strip()
        elif "id" in field or "automation" in field:
            actual_text = str(Element.Current.AutomationId).strip()
        elif "type" in field or "control" in field:
            actual_text = str(Element.Current.LocalizedControlType).strip()

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
        keystroke = False

        for left, mid, right in data_set:
            if mid.lower().strip() == "action":
                text = right
            elif left.lower().strip() == "method" and right.lower().strip() == "keystroke":
                keystroke = True

        Element = Get_Element(data_set)
        if Element == "zeuz_failed":
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
                time.sleep(unnecessary_sleep)
                Element.GetCurrentPattern(ValuePattern.Pattern).SetValue(text)
            except:
                time.sleep(0.5)
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
def Swipe(data_set):
    try:
        direction = "down"
        max_scroll = 1
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        Element = Get_Element(data_set)
        if Element == "zeuz_failed":
            return "zeuz_failed"
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                mid = mid.strip().lower()
                right = right.replace("%", "").replace(" ", "").lower()
                if "scroll parameter" in mid:
                    if left == "direction":
                        if right in ("up", "down"):
                            direction = right
                    elif left == "scroll count":
                        max_scroll = int(right)
        except:
            CommonUtil.Exception_Handler(sys.exc_info(), None, "Unable to parse data. Please write data in correct format")
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

        autoit.mouse_wheel(direction, max_scroll)
        time.sleep(unnecessary_sleep)
        CommonUtil.ExecLog(sModuleInfo, "Scrolled %s the window element %s times" % (direction, max_scroll), 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Can't scroll the given window element.")


@logger
def Scroll_to_element(dataset):
    pass


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

    try:
        keystroke_value = ""
        keystroke_char = ""
        method_name = "pyautogui"
        for left, mid, right in data_set:
            left = left.strip().lower()
            if "action" in mid.lower():
                if left == "keystroke keys":
                    keystroke_value = right.lower()  # Store keystroke
                elif left == "keystroke chars":
                    keystroke_char = right
            if "parameter"in mid.lower():
                if left == "method":
                    method_name= right.lower()

        if keystroke_value == "" and keystroke_char == "":
            CommonUtil.ExecLog(sModuleInfo, "Invalid action found", 3)
            return "zeuz_failed"

    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    try:
        time.sleep(gui_action_sleep)
        if method_name == 'pyautogui':
            try:
                if keystroke_char != "":
                    pyautogui.write(keystroke_char)
                    CommonUtil.ExecLog(sModuleInfo, "Successfully entered characters with pyautogui:\n%s" % keystroke_char, 1)
                    return "passed"

            except:
                errMsg = "Could not enter characters with pyautogui"
                return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

            count = 1
            if "," in keystroke_value:
                keystroke_value, count = keystroke_value.split(",")
                count = int(count.strip())
            keys = keystroke_value.split("+")
            keys = [x.strip() for x in keys]

            for i in range(count):
                gui.hotkey(*keys)  # Send keypress (as individual values using the asterisk)
            CommonUtil.ExecLog(sModuleInfo, "Successfully entered keystroke", 1)
            return "passed"

        elif method_name=='autoit':
            try:
                if keystroke_char != "":
                    autoit.send(keystroke_char)
                    CommonUtil.ExecLog(sModuleInfo, "Successfully entered character with autoit:\n%s" % keystroke_char, 1)
                    return "passed"
            except:
                errMsg = "Could not enter characters with autoit"
                return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

            count = 1
            keystroke_value = keystroke_value
            if "," in keystroke_value:
                keystroke_value, count = keystroke_value.split(",")
                count = int(count.strip())
            keys = keystroke_value.split("+")
            keys = [x.strip() for x in keys]

            send_key = ""
            for i in range(len(keys)):
                if i == len(keys)-1:
                    send_key += '{' + keys[i] + ' ' + str(count) + '}'
                else:
                    upper = keys[i].upper()
                    if upper == 'SHIFT':
                        send_key += '+'
                    elif upper == 'CTRL':
                        send_key += '^'
                    elif upper == 'ALT':
                        send_key += '!'
                    elif upper == 'WIN':
                        send_key += '#'
            # print(send_key)
            autoit.send(send_key)
            CommonUtil.ExecLog(sModuleInfo, "Successfully entered the keystroke", 1)
            return "passed"

    except Exception:
        errMsg = "Could not enter keystroke for your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def wait_for_element(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        timeout_duration = 10
        appear_condition = True
        for left, mid, right in data_set:
            if mid.strip().lower() == "action":
                if left.strip().lower() == "wait to disappear":
                    appear_condition = False
                timeout_duration = int(right.strip())

        end_time = time.time() + timeout_duration
        while time.time() <= end_time:
            Element = Get_Element(data_set, 0)
            if appear_condition and Element != "zeuz_failed":  # Element found
                CommonUtil.ExecLog(sModuleInfo, "Found element", 1)
                return "passed"
            elif not appear_condition and Element == "zeuz_failed":  # Element removed
                CommonUtil.ExecLog(sModuleInfo, "Element disappeared", 1)
                return "passed"
            time.sleep(1)

        CommonUtil.ExecLog(sModuleInfo, "Wait for element failed", 3)
        return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def save_attribute_values_in_list(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        Element = Get_Element(data_set)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find the main Element. We are searching for targets through out the whole desktop", 2)
            Element = AutomationElement.RootElement

        all_elements = []
        target_index = 0
        target = []
        paired = True
        p = False
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                mid = mid.strip().lower()
                right = right.strip()
                if "target parameter" in mid:
                    target.append([[], "", [], []])
                    temp = right.strip(",").split(",")
                    data = []
                    for each in temp:
                        data.append(each.strip().split("="))
                    for i in range(len(data)):
                        for j in range(len(data[i])):
                            data[i][j] = data[i][j].strip()
                            if j == 1:
                                data[i][j] = data[i][j].strip('"')  # dont add another strip here. dont need to strip inside quotation mark

                    for Left, Right in data:
                        if Left == "return":
                            target[target_index][1] = Right
                        elif Left == "return_contains":
                            target[target_index][2].append(Right)
                        elif Left == "return_does_not_contain":
                            target[target_index][3].append(Right)
                        else:
                            target[target_index][0].append((Left, 'element parameter', Right))

                    target_index = target_index + 1
                elif left == "save attribute values in list":
                    variable_name = right
                elif left == "paired":
                    paired = False if right.lower() == "no" else True
                    p = True

        except:
            CommonUtil.Exception_Handler(sys.exc_info())
            CommonUtil.ExecLog(sModuleInfo, "Unable to parse data. Please write data in correct format", 3)
            return "zeuz_failed"

        if not p and len(target) == 1:
            paired = False

        for each in target:
            all_elements.append(Get_Element(each[0], Parent_Element=Element))

        if paired:
            variable_value_size = 0
            variable_value = []
            for each in all_elements:
                variable_value_size = max(variable_value_size, len(each))
            for i in range(variable_value_size):
                variable_value.append([])
            i = 0
            for each in all_elements:
                search_by_attribute = target[i][1] if target[i][1] else "Value"
                j = 0
                for elem in each:
                    if search_by_attribute.strip().lower() == "value":
                        Attribute_value = eval("elem.GetCurrentPattern(ValuePattern.Pattern).Current.Value" + search_by_attribute)
                    else:
                        Attribute_value = eval("elem.Current." + search_by_attribute)
                    try:
                        for search_contain in target[i][2]:
                            if not isinstance(search_contain, type(Attribute_value)) or search_contain in Attribute_value or len(search_contain) == 0:
                                break
                        else:
                            if target[i][2]:
                                Attribute_value = None

                        for search_doesnt_contain in target[i][3]:
                            if isinstance(search_doesnt_contain, type(Attribute_value)) and search_doesnt_contain in Attribute_value and len(search_doesnt_contain) != 0:
                                Attribute_value = None
                    except:
                        CommonUtil.ExecLog(sModuleInfo, "Couldn't search by return_contains and return_does_not_contain", 2)
                    variable_value[j].append(Attribute_value)
                    j = j + 1
                i = i + 1
        elif not paired or len(target) == 1:
            variable_value = []
            for i in range(len(all_elements)):
                variable_value.append([])
            i = 0
            for each in all_elements:
                search_by_attribute = target[i][1] if target[i][1] else "Value"
                j = 0
                for elem in each:
                    if search_by_attribute.strip().lower() == "value":
                        Attribute_value = eval("elem.GetCurrentPattern(ValuePattern.Pattern).Current.Value" + search_by_attribute)
                    else:
                        Attribute_value = eval("elem.Current." + search_by_attribute)
                    try:
                        for search_contain in target[i][2]:
                            if not isinstance(search_contain, type(Attribute_value)) or search_contain in Attribute_value or len(search_contain) == 0:
                                break
                        else:
                            if target[i][2]:
                                Attribute_value = None

                        for search_doesnt_contain in target[i][3]:
                            if isinstance(search_doesnt_contain, type(Attribute_value)) and search_doesnt_contain in Attribute_value and len(search_doesnt_contain) != 0:
                                Attribute_value = None
                    except:
                        CommonUtil.ExecLog(sModuleInfo, "Couldn't search by return_contains and return_does_not_contain", 2)
                    variable_value[i].append(Attribute_value)
                    j = j + 1
                i = i + 1
            if len(target) == 1:
                variable_value = variable_value[0]

        return Shared_Resources.Set_Shared_Variables(variable_name, variable_value)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

