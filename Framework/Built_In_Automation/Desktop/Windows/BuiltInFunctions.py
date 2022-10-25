"""Windows automation file, element parameters can be found by running the inspectx64/x86.exe file"""
#########################
#                       #
#        Modules        #
#                       #
#########################
import pdb

code_debug = False
tabs = 0
import sys, os, subprocess
import re
from collections import deque
from pathlib import Path
import pygetwindow

sys.path.append(os.path.dirname(__file__))
import pyautogui as gui  # https://pyautogui.readthedocs.io/en/latest/
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources, LocateElement

import inspect, time
from Framework.Utilities import CommonUtil
from Framework.Utilities.decorators import logger

MODULE_NAME = inspect.getmodulename(__file__)

import inspect
from _elementtree import Element

import win32api
import win32con

import PIL
from PIL import Image, ImageGrab


python_folder = []
for location in subprocess.getoutput("where python").split("\n"):
    if "Microsoft" not in location:
        python_folder.append(location)
try:
    python_location = "" if len(python_folder) == 0 else "by going to {}".format(python_folder[0].split("Python")[0] + "Python")
except:
    python_location = ""
if not 3.5 <= float(sys.version.split(" ")[0][0:3]) <= 3.8:
    error_msg = "You have the wrong Python version or bit" \
                + "\nFollow this procedure" \
                + "\n1.Go to settings, then go to Apps and in search box type python and uninstall all python related things" \
                + "\n2.Delete your Python folder" \
                + python_location \
                + "\n3.Go to this link and download python https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe" \
                + "\n4.During installation, give uncheck 'for all user' and check 'Add Python to Path'. This is very important." \
                + "\n5.Relaunch zeuz node_cli.py"
    CommonUtil.ExecLog("", error_msg, 3)

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
def go_to_desktop(data_set=[]):
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


def get_coords(Element):
    x = int(
        Element.Current.BoundingRectangle.Left
        + Element.Current.BoundingRectangle.Width / 2
    )
    y = int(
        Element.Current.BoundingRectangle.Top
        + Element.Current.BoundingRectangle.Height / 2
    )
    return x, y


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
    # if Element == "zeuz_failed":
    if type(Element) == str and Element == "zeuz_failed":
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
def Click_Element_None_Mouse(Element, Expand=True, Gui=False):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        patter_list = Element.GetSupportedPatterns()
        if len(patter_list) == 0 or Gui:
            # x = int (Element.Current.BoundingRectangle.X)
            # y = int (Element.Current.BoundingRectangle.Y)
            CommonUtil.ExecLog(sModuleInfo, "We did not find any pattern for this object, so we will click by mouse with location", 1)
            x, y = get_coords(Element)
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
                    x, y = get_coords(Element)
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
def Check_uncheck(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    command = "check"
    try:
        for left, mid, right in data_set:
            left = left.lower().strip()
            if "check uncheck" == left:
                command = "uncheck" if "uncheck" in right.lower() else "check"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    Element = Get_Element(data_set)
    # if Element == "zeuz_failed":
    if type(Element) == str and Element == "zeuz_failed":
        CommonUtil.ExecLog(sModuleInfo, "Could not find the element", 3)
        return "zeuz_failed"

    pattern_list = [Automation.PatternName(i) for i in Element.GetSupportedPatterns()]
    if "Toggle" in pattern_list:
        is_selected = str(Element.GetCurrentPattern(TogglePattern.Pattern).Current.ToggleState)
    else:
        CommonUtil.ExecLog(sModuleInfo, "No Toggle pattern found for the Element", 3)
        return "zeuz_failed"

    if command == "check" and is_selected == "On":
        CommonUtil.ExecLog(sModuleInfo, "The element is already checked so skipped it", 1)
        return "passed"
    elif command == "uncheck" and not is_selected:
        CommonUtil.ExecLog(sModuleInfo, "The element is already unchecked so skipped it", 1)
        return "passed"
    try:
        if "Toggle" in pattern_list:
            Element.GetCurrentPattern(TogglePattern.Pattern).Toggle()
        if command == "check":
            CommonUtil.ExecLog(sModuleInfo, "The element is checked successfully", 1)
        else:
            CommonUtil.ExecLog(sModuleInfo, "The element is unchecked successfully", 1)
        return "passed"
    except:
        if command == "check":
            CommonUtil.ExecLog(sModuleInfo, "The element couldn't be checked", 3)
        else:
            CommonUtil.ExecLog(sModuleInfo, "The element couldn't be unchecked", 3)
        return "zeuz_failed"


@logger
def Right_Click_Element(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        Element = Get_Element(data_set)
        # if Element == "zeuz_failed":
        if type(Element) == str and Element == "zeuz_failed":
            return "zeuz_failed"

        x, y = get_coords(Element)
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


def _get_attribute(value):
    val = value.strip().lower()
    d = {"class": "ClassName", "name": "Name", "automation": "AutomationId", "control": "LocalizedControlType"}
    if val in d:
        return d[val]
    return value


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
            sModuleInfo,
            True if window_name is None else False
        )
        if temp == []: temp = "zeuz_failed"
        return temp

    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _child_search_by_path(
    ParentElement,
    element_path,
    sModuleInfo,
    switch_window=False
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

                if found:
                    if switch_window:
                        CommonUtil.ExecLog(sModuleInfo, "Switching to window: %s" % NameE, 1)
                        autoit.win_activate(NameE)
                    all_elements.append(each_child)
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
                return [temp[element_index]]

    except:
        CommonUtil.Exception_Handler(sys.exc_info(), None, _not_found_log(element_name, element_class, element_automation, element_control))
        return []


class _Element:
    def __init__(self, element):
        self.Current = self.Current(element)

    class Current:
        def __init__(self, element):
            self.BoundingRectangle = self.BoundingRectangle(element)

        class BoundingRectangle:
            def __init__(self, image):
                self.Left = image[0]
                self.Top = image[1]
                self.Width = image[2]
                self.Height = image[3]

    def GetSupportedPatterns(self, *args, **kwargs):
        return []


@logger
def image_search(step_data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        file_name = ""
        resolution = ""
        idx = 0
        confidence = 0.85
        parent_dataset = []
        image_text = ""
        for left, mid, right in step_data_set:
            left = left.strip().lower()
            mid = mid.strip().lower()
            if mid == "element parameter":
                if "resolution" in left:
                    resolution = right.strip().lower()
                elif "index" in left:
                    idx = int(right.strip())
                elif "confidence" in left:
                    confidence = float(right.replace("%", "").replace(" ", "").lower()) / 100
                elif "text" in left:
                    image_text = right
                else:
                    file_name = right.strip()
                    if "~" in file_name:
                        file_name = str(Path(os.path.expanduser(file_name)))
            if mid == "parent parameter":
                parent_dataset.append((left, "element parameter", right))

        if parent_dataset:
            parent = Get_Element(parent_dataset)
            if type(parent) == str and parent == "zeuz_failed":
                return parent
            left = parent.Current.BoundingRectangle.Left
            top = parent.Current.BoundingRectangle.Top
            width = parent.Current.BoundingRectangle.Width
            height = parent.Current.BoundingRectangle.Height
        else:
            left, top = 0, 0
            width, height = pyautogui.size()
        print("left,top,width,height=", (left, top, width, height))

        if file_name == "" and image_text == "":
            return "zeuz_failed"

        if file_name and not os.path.exists(file_name):
            CommonUtil.ExecLog(
                sModuleInfo,
                "Could not find file attachment called %s" % file_name,
                3,
            )
            return "zeuz_failed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Find element information
    try:
        if image_text:
            import cv2
            from pytesseract import pytesseract
            pytesseract.tesseract_cmd = os.environ["PROGRAMFILES"] + r"\Tesseract-OCR\tesseract.exe"

            image_text = image_text.replace(" ", "").lower()
            PIL.ImageGrab.grab().crop((left, top, left + width, top + height)).save("sample.jpg")
            imge = cv2.imread("sample.jpg")
            gray = cv2.cvtColor(imge, cv2.COLOR_BGR2GRAY)

            data = pytesseract.image_to_boxes(gray)
            all_letters = data.split("\n")
            print(all_letters)
            full_string = ""
            for i in all_letters:
                full_string += i[0] if len(i) > 0 else "~"
            full_string = full_string.lower()

            all_pos = [m.start() for m in re.finditer(image_text, full_string)]

            if -len(all_pos) <= idx < len(all_pos):
                CommonUtil.ExecLog(sModuleInfo, "Found %s text elements. Returning element of index %s" % (len(all_pos), idx), 1)
                i = all_pos[idx]
            elif len(all_pos) != 0:
                CommonUtil.ExecLog(sModuleInfo, "Found %s text elements. Index out of range" % len(all_pos), 3)
                return "zeuz_failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, 'Could not find text "%s"' % image_text, 3)
                return "zeuz_failed"

            msg = ""
            a = all_letters[i:i + len(image_text)]
            for i in a:
                msg += i + "\n"
            left_top = list(map(int, a[0].split(" ")[1:3]))
            right_bottom = list(map(int, a[-1].split(" ")[3:5]))
            center = left + (right_bottom[0] + left_top[0]) // 2, top + height - (right_bottom[1] + left_top[1]) // 2
            msg += "Center = " + str(center) + "\n"
            # pyautogui.moveTo(center)

            element = left_top[0] + left, height - right_bottom[1] + top, right_bottom[0] - left_top[0], right_bottom[1] - left_top[1]
            msg += "Coordinates = " + str(element) + "\n"
            CommonUtil.ExecLog(sModuleInfo, msg, 5)

            return _Element(element)
        else:
            # Scale image if required
            regex = re.compile(r"(\d+)\s*x\s*(\d+)", re.IGNORECASE)  # Create regex object with expression
            match = regex.search(file_name)  # Search for resolution within filename (this is the resolution of the screen the image was captured on)
            if match is None and resolution != "":  # If resolution not in filename, try to find it in the step data
                match = regex.search(resolution)  # Search for resolution within the Field of the element paramter row (this is the resolution of the screen the image was captured on)

            if match is not None:  # Match found, so scale
                CommonUtil.ExecLog(sModuleInfo, "Scaling image (%s)" % match.group(0), 5)
                size_w, size_h = (
                    int(match.group(1)),
                    int(match.group(2)),
                )  # Extract width, height from match (is screen resolution of desktop image was taken on)
                file_name = _scale_image(file_name, size_w, size_h)  # Scale image element

            element = pyautogui.locateAllOnScreen(
                file_name, grayscale=True, confidence=confidence, region=(left, top, width, height)
            )  # Get coordinates of element. Use greyscale for increased speed and better matching across machines. May cause higher number of false-positives
            element_list = tuple(element)

            element = None
            if -len(element_list) <= idx < len(element_list):
                CommonUtil.ExecLog(sModuleInfo, "Found %s elements. Returning element of index %s" % (len(element_list), idx), 1)
                element = element_list[idx]
            elif len(element_list) != 0:
                CommonUtil.ExecLog(sModuleInfo, "Found %s elements. Index out of range" % len(element_list), 3)
            else:
                CommonUtil.ExecLog(sModuleInfo, "Element was not found", 3)

            if element is None:
                return "zeuz_failed"
            return _Element(element)
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _scale_image(file_name, size_w, size_h):
    """ This function calculates ratio and scales an image for comparison by _pyautogui() """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Only used by desktop, so only import here
    import pyautogui
    from PIL import Image
    from decimal import Decimal

    try:
        # Open image file
        file_name = open(file_name, "rb")  # Read file into memory
        file_name = Image.open(file_name)  # Convert to PIL format

        # Read sizes
        screen_w, screen_h = pyautogui.size()  # Read screen resolution
        image_w, image_h = file_name.size  # Read the image element's actual size

        # Calculate new image size
        if size_w > screen_w:  # Make sure we create the scaling ratio in the proper direction
            ratio = Decimal(size_w) / Decimal(screen_w)  # Get ratio (assume same for height)
        else:
            ratio = Decimal(screen_w) / Decimal(size_w)  # Get ratio (assume same for height)
        size = (int(image_w * ratio), int(image_h * ratio))  # Calculate new resolution of image element

        # Scale image
        # file_name.thumbnail(size, Image.ANTIALIAS)  # Resize image per calculation above

        return file_name.resize(size)  # Return the scaled image object
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error scaling image")


@logger
def Get_Element(data_set, wait_time=Shared_Resources.Get_Shared_Variables("element_wait"), Parent_Element=None):
    """ Top function for searching an element """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    element_name, window_name, element_class, element_automation, element_control, element_path, elem, element_image = None, None, None, None, None, "", False, []
    parent_name, parent_class, parent_automation, parent_control, parent = None, None, None, None, False
    parent_path = ""
    sibling_name, sibling_class, sibling_automation, sibling_control, sibling = None, None, None, None, False
    element_index = 0
    parent_index = 0
    try:
        for left, mid, right in data_set:
            left = left.replace(" ", "").replace("_", "").lower()
            mid = mid.strip().lower()

            if left == "wait": wait_time = float(right.strip())
            # elif left == "index": element_index = int(right.strip())
            elif "windowpid" in left: window_name = [right, _count_star(left), "pid"]
            elif "window" in left: window_name = [right, _count_star(left), "name"]

            if mid == "element parameter":
                elem = True
                if "class" in left: element_class = [right, _count_star(left)]
                elif left == "index": element_index = int(right.strip())
                elif "name" in left: element_name = [right, _count_star(left)]
                elif "automation" in left: element_automation = [right, _count_star(left)]  # automationid
                elif "control" in left: element_control = [right, _count_star(left)]    # localizedcontroltype
                elif "path" in left: element_path = right.strip()
                elif "image" in left:
                    element_image.append((left, mid, right))

            elif mid == "parent parameter":
                parent = True
                if "class" in left: parent_class = [right, _count_star(left)]
                elif "name" in left: parent_name = [right, _count_star(left)]
                elif "automation" in left: parent_automation = [right, _count_star(left)]  # automationid
                elif "control" in left: parent_control = [right, _count_star(left)]    # localizedcontroltype
                elif "path" in left: parent_path = right.strip()
                elif "index" in left: parent_index = right.strip()

            elif mid == "sibling parameter":
                sibling = True
                if "class" in left: sibling_class = [right, _count_star(left)]
                elif "name" in left: sibling_name = [right, _count_star(left)]
                elif "automation" in left: sibling_automation = [right, _count_star(left)]  # automationid
                elif "control" in left: sibling_control = [right, _count_star(left)]    # localizedcontroltype

        if not elem:
            CommonUtil.ExecLog(sModuleInfo, "No element info is given", 3)
            return "zeuz_failed"
        if elem and (element_name, element_class, element_automation, element_control, element_path, element_image) == (None, None, None, None, "", []):
            CommonUtil.ExecLog(sModuleInfo, "We support only 'Window', 'Name', 'ClassName', 'LocalizedControlType', 'AutomationId', 'element path', 'image'", 3)
            return "zeuz_failed"
        if sibling and not parent:
            CommonUtil.ExecLog(sModuleInfo, "A common PARENT of both ELEMENT and SIBLING should be provided", 3)
            return "zeuz_failed"
        if parent and element_image and (parent_name, parent_class, parent_automation, parent_control, parent_path) == (None, None, None, None, ""):
            CommonUtil.ExecLog(sModuleInfo, "For image parent, We support only 'Window', 'Name', 'ClassName', 'LocalizedControlType', 'AutomationId', 'path'", 3)
            return "zeuz_failed"
        elif parent and not element_image and (parent_name, parent_class, parent_automation, parent_control) == (None, None, None, None):
            CommonUtil.ExecLog(sModuleInfo, "We support only 'Window', 'Name', 'ClassName', 'LocalizedControlType', 'AutomationId'", 3)
            return "zeuz_failed"
        if sibling and (sibling_name, sibling_class, sibling_automation, sibling_control) == (None, None, None, None):
            CommonUtil.ExecLog(sModuleInfo, "We support only 'Window', 'Name', 'ClassName', 'LocalizedControlType', 'AutomationId'", 3)
            return "zeuz_failed"
        if window_name is None and Parent_Element is None and not element_path:
            CommonUtil.ExecLog(sModuleInfo, "You should provide 'Window' otherwise the search won't be efficient", 2)
        if element_path:
            if element_path[-1] != ">": element_path = element_path.strip() + ">"
            if element_path[0] == ">": element_path = element_path[1:]
            if element_index != 0:
                CommonUtil.ExecLog(sModuleInfo, "Index is not allowed other than 0 for 'element path' search. Setting index = 0", 2)

        s = time.time()
        while True:
            if element_image:
                _get_main_window(window_name)
                for i in (("name", parent_name), ("class", parent_class), ("automationid", parent_automation), ("control", parent_control), ("path", parent_path), ("window", window_name), ("index", parent_index)):
                    if i[1]:
                        if type(i[1]) == list and len(i[1]) >= 2:
                            data = (i[1][1] + i[0], "parent parameter", i[1][0])
                        else:
                            data = (i[0], "parent parameter", i[1])
                        element_image.append(data)
                element_image.append(("index", "element parameter", str(element_index)))
                result = image_search(element_image)
                return result
            if element_path:
                all_elements = Element_path_search(window_name, element_path)
                if all_elements == "zeuz_failed" and time.time() < s + wait_time:
                    time.sleep(0.5)  # Sleep is needed to avoid unlimited logging

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
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        if WindowName is None:  # if window name is not specified in dataset
            return AutomationElement.RootElement

        MainWindowsList = AutomationElement.RootElement.FindAll(
            TreeScope.Children, Condition.TrueCondition
        )
        for MainWindowElement in MainWindowsList:
            try:
                if WindowName[2] == "pid":
                    try:
                        if MainWindowElement.Current.ProcessId == int(WindowName[0]):
                            return MainWindowElement
                    except:
                        pass
                else:
                    NameS = MainWindowElement.Current.Name
                    if _found(WindowName, NameS):
                        CommonUtil.ExecLog(sModuleInfo, "Switching to window: %s" % NameS, 1)
                        autoit.win_activate(NameS)
                        return MainWindowElement
            except:
                pass

        return None
    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        return None


@logger
def Drag_and_Drop_Element(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    source = []
    destination = []
    try:
        for left, mid, right in data_set:
            left = left.strip().lower()
            if "src" in left or "source" in left:
                source.append((left.replace("src", "").replace("source", ""), mid, right))
            elif "dst" in left or "destination" in left:
                destination.append((left.replace("dst", "").replace("destination", ""), mid, right))

        Element1 = Get_Element(source)
        if type(Element1) == str and Element1 == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find source element", 3)
            return "zeuz_failed"

        Element2 = Get_Element(destination)
        if type(Element2) == str and Element2 == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not destination element", 3)
            return "zeuz_failed"

        x_source, y_source = get_coords(Element1)
        x_destination, y_destination = get_coords(Element2)
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
        # if Element == "zeuz_failed":
        if type(Element) == str and Element == "zeuz_failed":
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

        x, y = get_coords(Element)
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
        # if Element == "zeuz_failed":
        if type(Element) == str and Element == "zeuz_failed":
            return "zeuz_failed"
        x, y = get_coords(Element)
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
        # if Element == "zeuz_failed":
        if type(Element) == str and Element == "zeuz_failed":
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
                field = left.replace(" ", "").lower()
                field2 = left.strip()
                variable_name = right.strip()

        Element = Get_Element(data_set)
        # if Element == "zeuz_failed":
        if type(Element) == str and Element == "zeuz_failed":
            return "zeuz_failed"

        pattern_list = [Automation.PatternName(i) for i in Element.GetSupportedPatterns()]
        print(pattern_list)

        actual_text = ""
        if "value" in field:
            if "Value" not in pattern_list:
                CommonUtil.ExecLog(sModuleInfo, "Value pattern is not found for this Element", 3)
                return "zeuz_failed"
            actual_text = str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.Value)
        elif "togglepattern" in field:
            if "Toggle" not in pattern_list:
                CommonUtil.ExecLog(sModuleInfo, "Toggle pattern is not found for this Element", 3)
                return "zeuz_failed"

            actual_text = True if str(Element.GetCurrentPattern(TogglePattern.Pattern).Current.ToggleState) == "On"  else False
        elif "select" in field and "pattern" in field:
            if not "SelectionItem" in pattern_list:
                CommonUtil.ExecLog(sModuleInfo, "SelectionItemPattern is not found for this Element", 3)
                return "zeuz_failed"
            actual_text = True if str(Element.GetCurrentPattern(SelectionItemPattern.Pattern).Current.IsSelected) == "True" else False
        elif "name" in field:
            actual_text = str(Element.Current.Name).strip()
        elif "class" in field:
            actual_text = str(Element.Current.ClassName).strip()
        elif "id" in field or "automation" in field:
            actual_text = str(Element.Current.AutomationId).strip()
        elif "type" in field or "control" in field:
            actual_text = str(Element.Current.LocalizedControlType).strip()
        else:
            actual_text = eval("Element.Current." + field2)

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
            if left.lower().strip() == "text":
                text = right
            elif left.lower().strip() == "method" and right.lower().strip() in ("gui", "keystroke"):
                keystroke = True

        Element = Get_Element(data_set)
        # if Element == "zeuz_failed":
        if type(Element) == str and Element == "zeuz_failed":
            return "zeuz_failed"

        if keystroke:
            x, y = get_coords(Element)
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
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Couldn't enter text")


@logger
def Swipe(data_set):
    try:
        direction = "down"
        scroll_count = 1
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        Element = Get_Element(data_set)
        # if Element == "zeuz_failed":
        if type(Element) == str and Element == "zeuz_failed":
            return "zeuz_failed"
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                mid = mid.strip().lower()
                right = right.replace("%", "").replace(" ", "").lower()
                if "scroll parameter" in mid:
                    if left == "direction":
                        if right in ("up", "down","right","left"):
                            direction = right
                    elif left == "scroll count":
                        scroll_count = int(right)
        except:
            CommonUtil.Exception_Handler(sys.exc_info(), None, "Unable to parse data. Please write data in correct format")
            return "zeuz_failed"
        x, y = get_coords(Element)
        win32api.SetCursorPos((x, y))
        if direction == "right":
            pyautogui.keyDown('shift')
            autoit.mouse_wheel("down", scroll_count)
            pyautogui.keyUp('shift')
        elif direction == "left":
            pyautogui.keyDown('shift')
            autoit.mouse_wheel("up", scroll_count)
            pyautogui.keyUp('shift')
        else:
            autoit.mouse_wheel(direction, scroll_count)

        time.sleep(unnecessary_sleep)
        CommonUtil.ExecLog(sModuleInfo, "Scrolled %s the window element %s times" % (direction, scroll_count), 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Can't scroll the given window element.")


@logger
def Scroll_to_element(dataset):
    try:
        direction = "down"
        scroll_count = 1
        max_try = 50
        desired_dataset = []
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        Element = Get_Element(dataset)
        # if Element == "zeuz_failed":
        if type(Element) == str and Element == "zeuz_failed":
            return "zeuz_failed"
        try:
            for left, mid, right in dataset:
                left = left.strip().lower()
                mid = mid.strip().lower()
                right = right.strip()
                if mid.startswith("desired"):
                    desired_dataset.append((left, 'element parameter', right))
                if "scroll parameter" in mid:
                    if left == "direction":
                        if right in ("up", "down", "right", "left"):
                            direction = right
                        else:
                            CommonUtil.ExecLog(sModuleInfo, "direction should be one of up/down/left/right", 3)
                            return "zeuz_failed"
                    elif left == "scroll count":
                        scroll_count = int(right)
                    elif left == "max try":
                        max_try = int(right)

        except:
            return CommonUtil.Exception_Handler(sys.exc_info(), None, "Unable to parse data. Please write data in correct format")

        x, y = get_coords(Element)
        win32api.SetCursorPos((x, y))

        desired_Element = Get_Element(desired_dataset, 0)
        if not(type(desired_Element) == str and desired_Element == "zeuz_failed"):
            CommonUtil.ExecLog(sModuleInfo, "Desired element is found.No need to scroll.", 1)
            return "passed"
        else:
            count = 0
            while True:
                if direction == "right":
                    pyautogui.keyDown('shift')
                    autoit.mouse_wheel("down", scroll_count)
                    pyautogui.keyUp('shift')
                elif direction == "left":
                    pyautogui.keyDown('shift')
                    autoit.mouse_wheel("up", scroll_count)
                    pyautogui.keyUp('shift')
                else:
                    autoit.mouse_wheel(direction, scroll_count)
                desired_Element = Get_Element(desired_dataset, 0)
                count += 1
                if count > max_try or not(type(desired_Element) == str and desired_Element == "zeuz_failed"):
                    break

            if count < max_try:
                CommonUtil.ExecLog(sModuleInfo, "Scrolled %s the window element %s times" % (direction, scroll_count * count), 1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Scrolled %s the window element %s times" % (direction, scroll_count * count), 1)
                return "zeuz_failed"
        time.sleep(unnecessary_sleep)




    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Can't scroll the given window element.")


def _open_inspector(inspector, args):
    d = {"uispy": ["UI Spy", "UISpy"], "inspectx64": ["Inspect  (HWND", "InspectX64"], "inspectx86": ["Inspect  (HWND", "InspectX86"]}
    if len(pygetwindow.getWindowsWithTitle(d[inspector][0])) > 0:
        for i in pygetwindow.getWindowsWithTitle(d[inspector][0]):
            i.minimize()
    else:
        subprocess.Popen(r"..\Apps\Windows\%s.exe" % d[inspector][1], **args)
        for i in range(30):
            if len(pygetwindow.getWindowsWithTitle(d[inspector][0])) > 0:
                break
            time.sleep(0.5)
        time.sleep(1)
        pygetwindow.getWindowsWithTitle(d[inspector][0])[0].minimize()


@logger
def Run_Application(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        args = {"shell": True, "stdin": None, "stdout": None, "stderr": None}
        launch_cond = ""
        Desktop_app = ""
        size, top_left, maximize = None, None, False
        wait = Shared_Resources.Get_Shared_Variables("element_wait")
        for left, mid, right in data_set:
            left = left.replace(" ", "").replace("_", "").replace("-", "").lower()
            r = right.strip().lower()
            yes_cond = r in ("yes", "ok", "true", "enable")
            if mid.strip().lower() == "action":
                Desktop_app = CommonUtil.path_parser(right.strip())
            elif "uispy" in left and yes_cond:
                _open_inspector("uispy", args)
            elif "inspectx64" in left and yes_cond:
                _open_inspector("inspectx64", args)
            elif "inspectx86" in left and yes_cond:
                _open_inspector("inspectx86", args)
            elif "size" == left:
                size = r
            elif "topleft" in left or "location" in left:
                top_left = r
            elif "maximize" in left and yes_cond:
                maximize = True
            elif "relaunch" in left and yes_cond:
                launch_cond = "relaunch"
            elif "launchagain" in left and yes_cond:
                launch_cond = "launchagain"
            elif "wait" == left:
                wait = float(r)

        if not launch_cond and len(pygetwindow.getWindowsWithTitle(Desktop_app)) > 0:
            CommonUtil.ExecLog(
                sModuleInfo,
                "The App has already been launched earlier. So not launching again.\n" +
                'If you want to quit the existing app and relaunch it then add a row ("relaunch", "optional parameter", "yes")\n' +
                'If you want to keep the existing app and launch another instance of it then add a row ("launch again", "optional parameter", "yes")', 2)
        else:
            if launch_cond == "relaunch":
                Close_Application([("close app", "action", Desktop_app)])
            if os.path.isfile(Desktop_app):
                cmd = f'''{Desktop_app[:2]} && cd "{os.path.dirname(Desktop_app)}" && start cmd.exe /K "{Desktop_app}\"'''
                CommonUtil.ExecLog(sModuleInfo, "Running following cmd:\n" + cmd, 1)
                subprocess.Popen(cmd, **args)
                # Desktop_app = os.path.basename(Desktop_app)
            else:
                autoit.send("^{ESC}")
                time.sleep(0.5)
                autoit.send(Desktop_app)
                time.sleep(0.5)
                autoit.send("{ENTER}")
                CommonUtil.ExecLog(sModuleInfo, "Successfully launched your app", 1)
                time.sleep(2)

            # if not Desktop_app.endswith(".exe"):
            #     Desktop_app += ".exe"
            CommonUtil.ExecLog(sModuleInfo, "Waiting for the app to launch for maximum %s seconds" % wait, 1)
            s = time.time()
            while time.time() - s < wait:
                # if len(pygetwindow.getWindowsWithTitle(Desktop_app)) > 0:     # This is case in-sensitive
                if Desktop_app in pygetwindow.getActiveWindow().title:          # This is case sensitive
                    break
                time.sleep(0.5)
            else:
                if maximize or size is not None:
                    CommonUtil.ExecLog(sModuleInfo, "Could not find any launched app with title: %s however continuing. Maximize or custom app size wont work" % Desktop_app, 2)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Could not find any launched app with title: %s however continuing" % Desktop_app, 2)
                return "passed"

        if maximize:
            win = pygetwindow.getWindowsWithTitle(Desktop_app)[0]
            win.maximize()
            CommonUtil.ExecLog(sModuleInfo, "Maximizing your app. Your Desktop Resolution = %s" % str((gui.size()[0], gui.size()[1])), 1)
        elif size is not None:
            size = tuple([int(i) for i in size.split(",")])
            if top_left is None:
                top_left = (0, 0)
            else:
                top_left = tuple([int(i) for i in top_left.split(",")])
            CommonUtil.ExecLog(sModuleInfo, "Restoring and Resizing the app with Size = %s and Top_Left = %s" % (size, top_left), 1)
            win = pygetwindow.getWindowsWithTitle(Desktop_app)[0]
            win.restore()
            win.size = size
            win.topleft = top_left

        return "passed"
    except:
        CommonUtil.Exception_Handler(sys.exc_info())
        return "zeuz_failed"


def get_pids_from_title(title):
    MainWindowsList = AutomationElement.RootElement.FindAll(
        TreeScope.Children, Condition.TrueCondition
    )
    pids = []
    for window in MainWindowsList:
        try:
            NameS = window.Current.Name
            if title in NameS:
                pids.append(window.Current.ProcessId)
        except:
            pass
    return pids


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
        CommonUtil.Exception_Handler(sys.exc_info())
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
                    keystroke_value = right.strip().lower()  # Store keystroke
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
            for i in range(len(keys)):
                keys[i] = keys[i].strip()
                if keys[i] == "plus":
                    keys[i] = "+"
                elif keys[i] == "minus":
                    keys[i] = "-"
                elif keys[i] == "comma":
                    keys[i] = ","

            for i in range(count):
                gui.hotkey(*keys)  # Send keypress (as individual values using the asterisk)
            CommonUtil.ExecLog(sModuleInfo, "Successfully entered keystroke", 1)
            return "passed"

        elif method_name == 'autoit':
            try:
                if keystroke_char != "":
                    autoit.send(keystroke_char)
                    CommonUtil.ExecLog(sModuleInfo, "Successfully entered character with autoit:\n%s" % keystroke_char, 1)
                    return "passed"
            except:
                errMsg = "Could not enter characters with autoit"
                return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

            count = 1
            if "," in keystroke_value:
                keystroke_value, count = keystroke_value.split(",")
                count = int(count.strip())
            keys = keystroke_value.split("+")
            for i in range(len(keys)):
                keys[i] = keys[i].strip()
                if keys[i] == "plus":
                    keys[i] = "+"
                elif keys[i] == "minus":
                    keys[i] = "-"
                elif keys[i] == "comma":
                    keys[i] = ","

            send_key = ""
            for i in range(len(keys)):
                if i == len(keys)-1:
                    send_key += '{' + keys[i] + ' ' + str(count) + '}'
                else:
                    if keys[i] == 'shift':
                        send_key += '+'
                    elif keys[i] == 'ctrl':
                        send_key += '^'
                    elif keys[i] == 'alt':
                        send_key += '!'
                    elif keys[i] == 'win':
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
            if appear_condition and not (type(Element) == str and Element == "zeuz_failed") :  # Element found
                CommonUtil.ExecLog(sModuleInfo, "Found element", 1)
                return "passed"
            elif not appear_condition and type(Element) == str and Element == "zeuz_failed":  # Element removed
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
        # if Element == "zeuz_failed":
        if type(Element) == str and Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find the main Element. We are searching for targets through out the whole desktop", 2)
            Element = AutomationElement.RootElement

        all_elements = []
        target_index = 0
        target = []
        paired = True
        p = False
        scroll_count = 3
        scroll_value = None

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
                    paired = False if right.lower() in ("no", "false") or "colum" in right.lower() else True
                    p = True
                elif left == "scroll count":
                    scroll_count = int(right)

        except:
            CommonUtil.Exception_Handler(sys.exc_info())
            CommonUtil.ExecLog(sModuleInfo, "Unable to parse data. Please write data in correct format", 3)
            return "zeuz_failed"

        # if not p and len(target) == 1:
        #     paired = False
        try:
            while True:
                all_elements = []
                for each in target:
                    all_elements.append(Get_Element(each[0], Parent_Element=Element))

                if paired and not len(target) == 1:
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
                                Attribute_value = eval("elem.GetCurrentPattern(ValuePattern.Pattern).Current.Value")
                            else:
                                Attribute_value = eval("elem.Current." + _get_attribute(search_by_attribute))
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
                                Attribute_value = eval("elem.GetCurrentPattern(ValuePattern.Pattern).Current.Value")
                            else:
                                Attribute_value = eval("elem.Current." + _get_attribute(search_by_attribute))
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
                            if len(target) == 1:
                                variable_value[i].append([Attribute_value, elem])
                            else:
                                variable_value[i].append(Attribute_value)
                            j = j + 1
                        i = i + 1
                    if len(target) == 1:
                        variable_value = variable_value[0]
                        new_values = {}
                        for i in variable_value:
                            top = str(i[1].Current.BoundingRectangle.Top)
                            if top in new_values:
                                new_values[top] += [i[0]]
                            else:
                                new_values[top] = [i[0]]
                        variable_value = []
                        for i in new_values:
                            variable_value.append(new_values[i])

                if scroll_value is None:
                    scroll_value = variable_value
                else:
                    i = len(variable_value)
                    while i > 0:
                        if scroll_value[len(scroll_value)-i:] == variable_value[:i]:
                            temp = variable_value[i:]
                            break
                        i -= 1
                    else:
                        temp = variable_value
                    if i == len(variable_value):
                        break
                    scroll_value += temp
                win32api.SetCursorPos(get_coords(Element))
                autoit.mouse_wheel("down", scroll_count)

            if not paired:
                scroll_value = list(map(list, zip(*scroll_value)))
            return Shared_Resources.Set_Shared_Variables(variable_name, scroll_value)
        except:
            CommonUtil.Exception_Handler(sys.exc_info())
            return Shared_Resources.Set_Shared_Variables(variable_name, [])
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
