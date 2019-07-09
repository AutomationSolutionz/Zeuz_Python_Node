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

    expand = None
    invoke = None
    select = None
    toggle = None

    #parse dataset and read data
    try:
        for row in data_set:
            if row[1] == 'element parameter':
                if str(row[2]).strip().lower() == 'expand' or str(row[2]).strip().lower() == 'invoke' or str(row[2]).strip().lower() == 'select' or str(row[2]).strip().lower() == 'toggle':
                    if str(row[0]).strip().lower() == 'method':
                        if str(row[2]).strip().lower()=="expand": expand=True
                        elif str(row[2]).strip().lower() == "invoke": invoke = True
                        elif str(row[2]).strip().lower() == "select": select = True
                        elif str(row[2]).strip().lower() == "toggle": toggle = True

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Click using element
    CommonUtil.ExecLog(sModuleInfo, "Looking for element", 0)

    # Get element object
    Element = Get_Element(data_set)
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
    try:
        Element = Get_Element(window_name, element_name)
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


import clr, inspect, System
import os, sys
from _elementtree import Element
clr.AddReference('UIAutomationClient')
clr.AddReference('UIAutomationTypes')
clr.AddReference('UIAutomationProvider')
clr.AddReference('System.Windows.Forms')

import time,datetime
import win32api,win32con
import win32gui
import random
import string
import autoit

from System.Windows.Automation import *

'''
global recur_count
recur_count = 0 
#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False
'''



def get_element(MainWindowName_OR_ParentElement, Element_Name, Element_Class,Element_AutomationID,Element_LocalizedControlType,max_try = 1):
    #max_time is built in wait function.  It will try every seconds 15 times.  

    recur_count = 0 
    try:
        

        try:
            if isinstance(MainWindowName_OR_ParentElement, basestring)  == True:
                ParentElement = _get_main_window (MainWindowName_OR_ParentElement)
                if ParentElement == None:
                    return "failed"
                else:


                    ChildElement = _child_search(ParentElement, Element_Name,Element_Class,Element_AutomationID,Element_LocalizedControlType)

                    if ChildElement != None:
                        return ChildElement
                    else:
                        return "failed"
            else:
                ChildElement = _child_search(ParentElement, Element_Name,Element_Class,Element_AutomationID,Element_LocalizedControlType)
                

                if ChildElement != None:
                    return ChildElement
                else:
                    return "failed"

        except:
            return "failed"

            
     
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))



def _child_search(ParentElement, Element_Name,Element_Class,Element_AutomationID,Element_LocalizedControlType):
    
    try:
        '''
        global recur_count
        recur_count = recur_count +1
        print recur_count
        
        if recur_count == 100:
            time.sleep(5)
            '''
        # Name, Class, AutomationID, LocalizedControlType
        try:
            if Element_Name!= None and Element_Class != None and Element_AutomationID != None and Element_LocalizedControlType!=None:
                NameE = ParentElement.Current.Name
                ClassE= ParentElement.Current.ClassName
                AutomationE = ParentElement.Current.AutomationId
                LocalizedControlTypeE=ParentElement.Current.LocalizedControlType
                if NameE == Element_Name and ClassE == Element_Class and AutomationE == Element_AutomationID and LocalizedControlTypeE == Element_LocalizedControlType:

                    return ParentElement
        except:
            None
        
        # Name, Class
        try:
            if Element_Name!= None and Element_Class != None and Element_AutomationID == None and Element_LocalizedControlType==None:
                NameE = ParentElement.Current.Name
                ClassE= ParentElement.Current.ClassName

                if NameE == Element_Name and ClassE == Element_Class :
                    return ParentElement
        except:
            None


        # Name, AutomationID
        try:
            if Element_Name!= None and Element_Class == None and Element_AutomationID != None and Element_LocalizedControlType==None:
                NameE = ParentElement.Current.Name
                AutomationE = ParentElement.Current.AutomationId
                if NameE == Element_Name and AutomationE == Element_AutomationID:
                    return ParentElement
        except:
            None        
        
        
        # Name, LocalizedControlType

        try:
            if Element_Name!= None and Element_Class == None and Element_AutomationID == None and Element_LocalizedControlType!=None:
                
                NameE = ParentElement.Current.Name
                LocalizedControlTypeE=ParentElement.Current.LocalizedControlType
                if NameE == Element_Name and LocalizedControlTypeE == Element_LocalizedControlType:
                    return ParentElement
        except:
            None

        # Class, AutomationID, LocalizedControlType
        try:
            if Element_Name== None and Element_Class != None and Element_AutomationID != None and Element_LocalizedControlType!=None:
                ClassE= ParentElement.Current.ClassName
                AutomationE = ParentElement.Current.AutomationId
                LocalizedControlTypeE=ParentElement.Current.LocalizedControlType
                if ClassE == Element_Class and AutomationE == Element_AutomationID and LocalizedControlTypeE == Element_LocalizedControlType:
                    return ParentElement
        except:
            None
        
        # Class, AutomationID
        
        try:
            if Element_Name== None and Element_Class != None and Element_AutomationID != None and Element_LocalizedControlType==None:
                ClassE= ParentElement.Current.ClassName
                AutomationE = ParentElement.Current.AutomationId
                if  ClassE == Element_Class and AutomationE == Element_AutomationID :

                    return ParentElement
        except:
            None        
        
        # Class, LocalizedControlType

        try:
            if Element_Name == None and Element_Class != None and Element_AutomationID == None and Element_LocalizedControlType!=None:
                ClassE= ParentElement.Current.ClassName
                LocalizedControlTypeE=ParentElement.Current.LocalizedControlType
                if ClassE == Element_Class and LocalizedControlTypeE == Element_LocalizedControlType:
                    return ParentElement
        except:
            None
        
        # Class
        try:
            if Element_Name== None and Element_Class != None and Element_AutomationID == None and Element_LocalizedControlType==None:
                ClassE = ParentElement.Current.ClassName
                if ClassE == Element_Class:

                    return ParentElement
        except:
            None
        
        # AutomationID, LocalizedControlType
        try:
            if Element_Name == None and Element_Class == None and Element_AutomationID != None and Element_LocalizedControlType!=None:
                AutomationE = ParentElement.Current.AutomationId
                LocalizedControlTypeE=ParentElement.Current.LocalizedControlType
                if  AutomationE == Element_AutomationID and LocalizedControlTypeE == Element_LocalizedControlType:

                    return ParentElement
        except:
            None        
        
        # AutomationID
        try:
            if Element_Name== None and Element_Class == None and Element_AutomationID != None and Element_LocalizedControlType==None:
                AutomationE = ParentElement.Current.AutomationId
                if AutomationE == Element_AutomationID:

                    return ParentElement
        except:
            None
        
        # LocalizedControlType
        
        try:
            if Element_Name== None and Element_Class == None and Element_AutomationID == None and Element_LocalizedControlType!=None:
                LocalizedControlTypeE=ParentElement.Current.LocalizedControlType
                if LocalizedControlTypeE == Element_LocalizedControlType:

                    return ParentElement
        except:
            None        
        # Name, Class, AutomationID
        try:
            if Element_Name!= None and Element_Class != None and Element_AutomationID != None and Element_LocalizedControlType==None:
                NameE = ParentElement.Current.Name
                ClassE= ParentElement.Current.ClassName
                AutomationE = ParentElement.Current.AutomationId
                if NameE == Element_Name and ClassE == Element_Class and AutomationE == Element_AutomationID :
                    return ParentElement
        except:
            None
               
        # Name, Class
        try:
            if (Element_Name != None) and (Element_Class != None) and (Element_AutomationID == None) and (Element_LocalizedControlType==None):
                NameE = ParentElement.Current.Name
                ClassE= ParentElement.Current.ClassName
                if NameE == Element_Name and ClassE == Element_Class:

                    return ParentElement
        except:
            None
        # Name
        try:
            if (Element_Name!= None) and (Element_Class == None) and (Element_AutomationID == None) and (Element_LocalizedControlType==None):
                

                NameE = ParentElement.Current.Name
                
                if NameE == Element_Name:

                    return ParentElement
        except:
            None
    
        try:
            child_elements = ParentElement.FindAll(TreeScope.Children, Condition.TrueCondition)
            
            if child_elements.Count == 0:
                return None
            
            for each_child in child_elements:

                child = _child_search(each_child, Element_Name,Element_Class,Element_AutomationID,Element_LocalizedControlType)
                if child:
                    return child
            
            return None
        except:
            return None

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        return "failed"

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
        patter_list = Element.GetSupportedPatterns()
        if len(patter_list) == 0:
            # x = int (Element.Current.BoundingRectangle.X)
            # y = int (Element.Current.BoundingRectangle.Y)
            print "no pattern found going with mouse click"
            x = (int)(Element.Current.BoundingRectangle.Right - Element.Current.BoundingRectangle.Width / 2);
            y = (int)(Element.Current.BoundingRectangle.Bottom - Element.Current.BoundingRectangle.Height / 2);
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            return "passed"
        else:
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
                    print "no pattern found going with mouse click"
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
    try:
        Element = Get_Element(data_set)
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
    try:
        Element = Get_Element(data_set)
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


def Validate_Text (data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        expected_text=''
        for row in data_set:
            if str(row[1]).strip().lower() == 'action':
                expected_text = str(row[2])

        Element = Get_Element(data_set)
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return 'failed'

        actual_text=str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.Value).strip().lower()

        if expected_text == actual_text:
            CommonUtil.ExecLog(sModuleInfo,"Text '%s' is found in the element"%expected_text,1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Couldn't find text '%s' in any element"%expected_text,3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")


def Save_Text(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        variable_name=''
        field = 'value'
        for row in data_set:
            if str(row[1]).strip().lower() == 'action':
                variable_name = str(row[2])
            elif str(row[1]).strip().lower() == 'element parameter' and str(row[0]).strip().lower() == 'field':
                field = str(row[2]).lower().strip()

        Element = Get_Element(data_set)
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return 'failed'

        actual_text = ''
        if field == 'value':
            actual_text=str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.Value).strip()
        elif field == 'name':
            actual_text=str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.Name).strip()
        elif field == 'class':
            actual_text = str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.ClassName).strip()
        elif 'id' in field:
            actual_text = str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.AutomationId).strip()
        elif 'type' in field or 'control' in field:
            actual_text = str(Element.GetCurrentPattern(ValuePattern.Pattern).Current.LocalizedControlType).strip()

        Shared_Resources.Set_Shared_Variables(variable_name, actual_text)

        CommonUtil.ExecLog(sModuleInfo,"Text '%s' is saved in the variable '%s'"%(actual_text, variable_name),1)
        return "passed"
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
    try:
        text=''
        keystroke = True

        for row in data_set:
            if str(row[1]).lower().strip() == 'action':
                text = str(row[2])
            elif str(row[0]).lower().strip() == 'method' and str(row[0]).lower().strip() == 'set value':
                keystroke=False


        Element = Get_Element(data_set)

        if keystroke:
            if Element in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Couldn't find element",3)
                return "failed"

            x = (int)(Element.Current.BoundingRectangle.Right - Element.Current.BoundingRectangle.Width / 2);
            y = (int)(Element.Current.BoundingRectangle.Bottom - Element.Current.BoundingRectangle.Height / 2);
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            time.sleep(0.5)
            autoit.send("^a")  # select all
            autoit.send(text)
        else:
            Element.GetCurrentPattern(ValuePattern.Pattern).SetValue(text)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Couln't enter text")


def Scroll (data_set):
    try:
        Element = Get_Element(data_set)
        x = (int)(Element.Current.BoundingRectangle.Right - Element.Current.BoundingRectangle.Width / 2);
        y = (int)(Element.Current.BoundingRectangle.Bottom - Element.Current.BoundingRectangle.Height / 2);
        win32api.SetCursorPos((x, y))

        autoit.mouse_wheel("up",10)
        time.sleep(1)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")


def Get_Element(data_set):
    ''' Insert text '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    element_name = ''
    window_name = ''
    element_class = None
    automationid = None
    control_type = None
    wait_time = 15

    # parse dataset and read data
    try:
        for row in data_set:
            if row[1] == 'element parameter':
                if str(row[0]).strip().lower() == 'element name':
                    element_name = row[2]
                elif str(row[0]).strip().lower() == 'window name':
                    window_name = row[2]
                elif str(row[0]).strip().lower() == 'element class':
                    element_class = row[2]
                elif str(row[0]).strip().lower() == 'automation id':
                    automationid = row[2]
                elif str(row[0]).strip().lower() == 'control type':
                    control_type = row[2]
                elif str(row[0]).strip().lower() == 'wait time':
                    wait_time = int(str(row[2]))

        if element_name == '':
            element_name = None  # element name can be empty if user want the full window as an element

        # Click using element
        CommonUtil.ExecLog(sModuleInfo, "Looking for element", 0)

            # Get element object
        Element = get_element(window_name, element_name, element_class, automationid, control_type, wait_time)
        if Element == None:
            return "failed"

        return Element
    except Exception:
        errMsg = "Could not get your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


def Run_Application(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)
    try:
        Desktop_app = ''
        for row in data_set:
            if str(row[1]).strip().lower() == 'action':
                Desktop_app = str(row[2]).strip()

        autoit.send("^{ESC}")
        time.sleep(0.1)
        autoit.send(Desktop_app)
        time.sleep(0.1)
        autoit.send("{ENTER}")
        CommonUtil.ExecLog(sModuleInfo, "Succesfully launched your app", 1)

        return "passed"
    except:
        CommonUtil.ExecLog(sModuleInfo, "Unable to start your app %s" % Desktop_app,3)
        return "failed"


def Close_Application(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)
    try:
        Desktop_app = ''
        for row in data_set:
            if str(row[1]).strip().lower() == 'action':
                Desktop_app = str(row[2]).strip()

        if ".exe" not in Desktop_app:
            Desktop_app = Desktop_app + ".exe"
            os.system("TASKKILL /F /IM %s" % Desktop_app)
        else:
            os.system("TASKKILL /F /IM %s" % Desktop_app)
        CommonUtil.ExecLog(sModuleInfo, "Succesfully closed your app",1)

        return "passed"
    except:
        CommonUtil.ExecLog(sModuleInfo, "Unable to start your app %s" % Desktop_app,3)
        return "failed"


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