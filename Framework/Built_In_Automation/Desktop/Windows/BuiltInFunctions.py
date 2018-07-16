'''Windows automation file, element parameters can be found by running the inspectx64/x86.exe file'''
#########################
#                       #
#        Modules        #
#                       #
#########################

import sys, os, time, inspect
import glob
sys.path.append(os.path.dirname(__file__))
from Framework.Utilities import CommonUtil
import pyautogui as gui # https://pyautogui.readthedocs.io/en/latest/
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources
from Framework.Built_In_Automation.Shared_Resources import LocateElement
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list, skipped_tag_list

import clr,System, inspect, time,datetime, os, sys
from _elementtree import Element # What is this for?
from Framework.Utilities import CommonUtil

#this needs to be here on top, otherwise will return error
clr.AddReference('UIAutomationClient')
clr.AddReference('UIAutomationTypes')
clr.AddReference('UIAutomationProvider')
clr.AddReference('System.Windows.Forms')

# Do these need to be here?
from System.Windows.Automation import *
from System.Threading import Thread
from System.Windows.Forms import SendKeys

import win32api,win32con # What is this for?
import pyautogui # Should be removed after we complete sequential actions
import win32gui # Needed?
import autoit # The likely method we'll use



#########################
#                       #
#    Global Variables   #
#                       #
#########################
# Recall dependency, if not already set
dependency = None
if Shared_Resources.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables('dependency') # Retreive appium driver



global recur_count
recur_count = 0 # To be deleted

def go_to_desktop(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    invoke='true'
    Element = get_element('', 'Show desktop', 'TrayShowDesktopButtonWClass')
    if Element in failed_tag_list:
        CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
        return 'failed'
    try:
        result = Click_Element_None_Mouse(Element,None,True,None,None)
        CommonUtil.TakeScreenShot(sModuleInfo)
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not click element", 3)
            return 'failed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1)
            return "passed"
    except Exception:
        errMsg = "Could not select/click your element."
        CommonUtil.ExecLog(sModuleInfo,errMsg, 3)
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

# Method to click on element; step data passed on by the user
def Click_Element(data_set):
    ''' Click using element, first get the elemnent then click'''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    element_name = ''
    window_name = ''
    pane_name=''
    expand = None
    invoke = None
    select = None
    toggle = None

    #parse dataset and read data
    try:
        for row in data_set:
            if row[1] == 'element parameter':
                if row[0] == 'element name':
                    element_name=row[2]
                elif row[0] == 'window name':
                    window_name=row[2]
                elif row[0] == 'pane name':
                    pane_name = row[2]
                elif str(row[0]).strip().lower() == 'expand' or str(row[0]).strip().lower() == 'invoke' or str(row[0]).strip().lower() == 'select' or str(row[0]).strip().lower() == 'toggle':
                    value = None
                    if str(row[2]).strip().lower() == "yes" or str(row[2]).strip().lower() == "true":
                        value=True
                    elif str(row[2]).strip().lower() == "no" or str(row[2]).strip().lower() == "false":
                        value = False
                    else:
                        CommonUtil.ExecLog(sModuleInfo,"Element Paramter expand/invoke/select/toggle takes 'true'/'false'/'yes'/'no' as input",3)
                        return "failed"
                    if row[0]=="expand": expand=value
                    if row[0] == "invoke": invoke = value
                    if row[0] == "select": select = value
                    if row[0] == "toggle": toggle = value

                else:
                    CommonUtil.ExecLog(sModuleInfo, "Error in data set, please use 'element name' or 'window name' as element parameter", 3)
                    return "failed"

        if element_name == '':
            element_name = None #element name can be empty if user want the full window as an element

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Click using element
    CommonUtil.ExecLog(sModuleInfo, "Looking for element", 0)

    # Get element object
    Element = get_element(window_name,element_name)
    if Element in failed_tag_list:
        CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
        return 'failed'

    #If found Click element
    try:
        result = Click_Element_None_Mouse(Element,expand,invoke,select,toggle)
        CommonUtil.TakeScreenShot(sModuleInfo)
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not click element", 3)
            return 'failed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1)
            return "passed"
    except Exception:
        errMsg = "Could not select/click your element."
        CommonUtil.ExecLog(sModuleInfo,errMsg, 3)
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

def Right_Click_Element(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    element_name = ''
    window_name = ''
    try:
        for row in data_set:
            if row[1] == 'element parameter':
                if row[0] == 'element name':
                    element_name=row[2]
                elif row[0] == 'window name':
                    window_name=row[2]
        Element = get_element(window_name, element_name)
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return 'failed'
        x = (int)(Element.Current.BoundingRectangle.Right - Element.Current.BoundingRectangle.Width / 2);
        y = (int)(Element.Current.BoundingRectangle.Bottom - Element.Current.BoundingRectangle.Height / 2);
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

def get_element(window_name, element_name=None, element_class=None, automation_id=None, control_type=None):
    root = _get_main_window(window_name)
    if root is None:
        print "No window found with the name: " + window_name
        return None

    return find_element(root, element_name, element_class, automation_id, control_type)

def _get_main_window (WindowName):
    try:
        MainWindowsList = AutomationElement.RootElement.FindAll(TreeScope.Children,Condition.TrueCondition)
        UnicodeWinName=WindowName.decode('utf-8')
        for MainWindowElement in MainWindowsList:
            try:
                NameS =  MainWindowElement.Current.Name
                if UnicodeWinName in NameS:
                    autoit.win_activate(NameS)
                    return MainWindowElement
            except:
                NameS = None


        return None
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))


def Click_Element_None_Mouse(Element, Expand=None, Invoke=None, Select=None, Toggle=None):
    try:
        x = (int)(Element.Current.BoundingRectangle.Right - Element.Current.BoundingRectangle.Width / 2);
        y = (int)(Element.Current.BoundingRectangle.Bottom - Element.Current.BoundingRectangle.Height / 2);
        win32api.SetCursorPos((x, y))

        print "clicking your element"
        patter_list = Element.GetSupportedPatterns()
        for each in patter_list:
            pattern_name = Automation.PatternName(each)
            if pattern_name == "ExpandCollapse":
                if Expand == True:
                    # check to see if its expanded, if expanded, then do nothing... if not, expand it
                    status = Element.GetCurrentPattern(ExpandCollapsePattern.Pattern).Current.ExpandCollapseState
                    if status == 0:
                        Element.GetCurrentPattern(ExpandCollapsePattern.Pattern).Expand()
                    elif status == 1:
                        print "Already Expanded"
                elif Expand == False:
                    # check to see if its Collapsed, if Collapsed, then do nothing... if not, Collapse it
                    status = Element.GetCurrentPattern(ExpandCollapsePattern.Pattern).Current.ExpandCollapseState
                    if status == 1:
                        Element.GetCurrentPattern(ExpandCollapsePattern.Pattern).Collapse()
                    elif status == 0:
                        print "Already Collapsed"



            elif pattern_name == "Invoke":
                if Invoke == True:
                    print "invoking the button: %s" % Element.Current.Name
                    time.sleep(2)
                    Element.GetCurrentPattern(InvokePattern.Pattern).Invoke()



            elif pattern_name == "SelectionItem":
                Element.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
            elif pattern_name == "Toggle":
                Element.GetCurrentPattern(TogglePattern.Pattern).Toggle()

            else:
                # x = int (Element.Current.BoundingRectangle.X)
                # y = int (Element.Current.BoundingRectangle.Y)

                x = (int)(Element.Current.BoundingRectangle.Right - Element.Current.BoundingRectangle.Width / 2);
                y = (int)(Element.Current.BoundingRectangle.Bottom - Element.Current.BoundingRectangle.Height / 2);
                win32api.SetCursorPos((x, y))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                time.sleep(0.1)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

        return "passed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))

        return "failed"


def Drag_and_Drop_Element(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)


    element_name=[]
    window_name= []

    try:
        for row in data_set:
            if row[1] == 'element parameter':
                if row[0] == 'element name':
                    element_name.append(row[2])

                elif row[0] == 'window name':
                    window_name.append(row[2])

        Element1 = get_element(window_name[0], element_name[0])
        if Element1 in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return 'failed'
        Element2 = get_element(window_name[1], element_name[1])
        if Element2 in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return 'failed'

        result=Drag_Object(Element1, Element2)
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not Drag element", 3)
            return 'failed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Successfully dragged and dropped the element", 1)
            return "passed"


    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

def Drag_Object(Element1_source, Element2_destination):
    try:
        print "clicking your element"
        print Element1_source, Element2_destination

        x_source = (int)(
            Element1_source.Current.BoundingRectangle.Right - Element1_source.Current.BoundingRectangle.Width / 2);
        y_source = (int)(
            Element1_source.Current.BoundingRectangle.Bottom - Element1_source.Current.BoundingRectangle.Height / 2);

        x_destination = (int)(
            Element2_destination.Current.BoundingRectangle.Right - Element2_destination.Current.BoundingRectangle.Width / 2);
        y_destination = (int)(
            Element2_destination.Current.BoundingRectangle.Bottom - Element2_destination.Current.BoundingRectangle.Height / 2);
        autoit.mouse_click_drag(x_source, y_source, x_destination, y_destination, button="left", speed=20)
        return 'passed'




    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        return 'failed'

def Double_Click_Element(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    element_name = ''
    window_name = ''
    try:
        for row in data_set:
            if row[1] == 'element parameter':
                if row[0] == 'element name':
                    element_name = row[2]
                elif row[0] == 'window name':
                    window_name = row[2]
        Element = get_element(window_name, element_name)
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return 'failed'
        x = (int)(Element.Current.BoundingRectangle.Right - Element.Current.BoundingRectangle.Width / 2);
        y = (int)(Element.Current.BoundingRectangle.Bottom - Element.Current.BoundingRectangle.Height / 2);
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

def Hover_Over_Element (data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    element_name = ''
    window_name = ''
    try:
        for row in data_set:
            if row[1] == 'element parameter':
                if row[0] == 'element name':
                    element_name = row[2]
                elif row[0] == 'window name':
                    window_name = row[2]
        Element = get_element(window_name, element_name)
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return 'failed'
        x = (int)(Element.Current.BoundingRectangle.Right - Element.Current.BoundingRectangle.Width / 2);
        y = (int)(Element.Current.BoundingRectangle.Bottom - Element.Current.BoundingRectangle.Height / 2);
        win32api.SetCursorPos((x, y))

        autoit.mouse_move(x,y,speed=20)
        time.sleep(1)
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")


def getCoordinates(element, position):
    ''' Return coordinates of attachment's centre '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    # Parse input
    try:
        x = element[0]
        y = element[1]
        w = element[2]
        h = element[3]
        position = position.lower().strip()

        if position not in positions:
            CommonUtil.ExecLog(sModuleInfo, "Position must be one of: %s" % positions, 3)
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

def Enter_Text_In_Text_Box(data_set):
    ''' Insert text '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    # Parse data set
    try:
        element_parameter = False
        text_value = ''
        for row in data_set:
            if "action" in row[1]:
                text_value = row[2]
            if row[1] == 'element parameter':  # Indicates we should find the element instead of assuming we have keyboard focus
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
            element = LocateElement.Get_Element(data_set, gui)  # (x, y, w, h)
            if element in failed_tag_list:  # Error reason logged by Get_Element
                CommonUtil.ExecLog(sModuleInfo, "Could not locate element", 3)
                return 'failed'

            # Get coordinates for position user specified
            x, y = getCoordinates(element, 'centre')  # Find coordinates (x,y)
            if x in failed_tag_list:  # Error reason logged by Get_Element
                CommonUtil.ExecLog(sModuleInfo, "Error calculating coordinates", 3)
                return 'failed'
            CommonUtil.ExecLog(sModuleInfo, "Image coordinates on screen %d x %d" % (x, y), 0)
            gui.click(x, y)  # Single click
        else:
            CommonUtil.ExecLog(sModuleInfo, "No element provided. Assuming textbox has keyboard focus", 0)

        CommonUtil.TakeScreenShot(sModuleInfo)  # Capture screenshot, if settings allow for it

        # Enter text
        gui.typewrite(text_value)
        CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s" % text_value, 1)
        return "passed"

    except Exception:
        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

def Validate_Text(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)
    file_list=[]
    file_list=(glob.glob("C:/Users/zeuzi/Downloads/*"))
    for row in data_set:
        if "action" in row[1]:
            text_value = row[2]
    if (text_value in file_list):
        return "passed"
    else:
        errMsg = "Could not find the folder"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

def Keystroke_For_Element(data_set):
    ''' Insert characters - mainly key combonations'''
    # Example: Ctrl+c
    # Repeats keypress if a number follows, example: tab,3

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    # Parse dataset
    try:
        time.sleep(2)
        keystroke_value = ''
        for row in data_set:
            if "action" in row[1]:
                if row[0] == "keystroke keys":
                    keystroke_value = str(row[2]).lower()  # Store keystrok

        if keystroke_value == '':
            CommonUtil.ExecLog(sModuleInfo, "Invalid action found", 3)
            return 'failed'

    except Exception:
        errMsg = "Error parsing data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Perform action
    try:
        count = 1
        if ',' in keystroke_value:  # Check for delimiter indicating multiple keystrokes
            keystroke_value, count = keystroke_value.split(',')  # Separate keystroke and count
            count = int(count.strip())
        keys = keystroke_value.split('+')  # Split string into array
        keys = [x.strip() for x in keys]  # Clean it up

        for i in range(count): gui.hotkey(*keys)  # Send keypress (as individual values using the asterisk)

        CommonUtil.TakeScreenShot(sModuleInfo)  # Capture screenshot, if settings allow for it

        CommonUtil.ExecLog(sModuleInfo, "Successfully entered keystroke", 1)
        return 'passed'

    except Exception:
        errMsg = "Could not enter keystroke for your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

def Scroll (data_set):
    element_name = ''
    window_name = ''
    try:
        for row in data_set:
            if row[1] == 'element parameter':

                if row[0] == 'window name':
                    window_name = row[2]
        Element = get_element(window_name)
        x = (int)(Element.Current.BoundingRectangle.Right - Element.Current.BoundingRectangle.Width / 2);
        y = (int)(Element.Current.BoundingRectangle.Bottom - Element.Current.BoundingRectangle.Height / 2);
        win32api.SetCursorPos((x, y))

        autoit.mouse_wheel("up",10)
        time.sleep(1)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

def find_element(root, element_name, element_class, automation_id, control_type):
    found = element_name is None or element_name == root.Current.Name
    found &= element_class is None or element_class == root.Current.ClassName
    found &= automation_id is None or automation_id == root.Current.AutomationId
    found &= control_type is None or control_type == root.Current.LocalizedControlType

    if found:
        print "Element found: '%s' (%s)" % (root.Current.Name, root.Current.LocalizedControlType)
        return root

    children = root.FindAll(TreeScope.Children, Condition.TrueCondition)

    for child in children:
        element = find_element(child, element_name, element_class, automation_id, control_type)
        if element:
            return element

    return None




