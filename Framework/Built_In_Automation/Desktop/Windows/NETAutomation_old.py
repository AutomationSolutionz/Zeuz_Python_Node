# coding=utf-8
#-*- coding: cp1252 -*-
'''
Created on Aug 15, 2016

@author: hossa
'''

import clr,System, inspect
import os, sys
from _elementtree import Element
clr.AddReference('UIAutomationClient')
clr.AddReference('UIAutomationTypes')
clr.AddReference('UIAutomationProvider')
clr.AddReference('System.Windows.Forms')
from System.Windows.Automation import *
from System.Threading import Thread
from System.Windows.Forms import SendKeys
import time,datetime
import win32api,win32con
import win32gui

import autoit

global recur_count
recur_count = 0 





def Get_Element(MainWindowName_OR_ParentElement, Element_Name, Element_Class,Element_AutomationID,Element_LocalizedControlType):
    try:
        if isinstance(MainWindowName_OR_ParentElement, basestring)  == True:
            ParentElement = _get_main_window (MainWindowName_OR_ParentElement)
            if ParentElement == None:
                print  "No windows found with the given name "
                return "failed"
            else:
                print "Calling the recur func"
                #ChildElement = _recursive_child_search(ParentElement, Element_Name, Element_Class,Element_AutomationID)
                ChildElement = _child_search(ParentElement, Element_Name,Element_Class,Element_AutomationID,Element_LocalizedControlType)
                print "recu count: %s" %recur_count
                return ChildElement
        else:
            ChildElement = _child_search(ParentElement, Element_Name,Element_Class,Element_AutomationID,Element_LocalizedControlType)
            #ChildElement = _recursive_child_search(MainWindowName_OR_ParentElement, Element_Name, Element_Class,Element_AutomationID)
            print "Found the element"
            print "recu count: %s" %recur_count
            return   ChildElement      
 
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))



def _child_search(ParentElement, Element_Name,Element_Class,Element_AutomationID,Element_LocalizedControlType):
    
    try:
        global recur_count
        recur_count = recur_count +1
         
        # Name, Class, AutomationID, LocalizedControlType
        try:
            if Element_Name!= None and Element_Class != None and Element_AutomationID != None and Element_LocalizedControlType!=None:
                NameE = ParentElement.Current.Name
                ClassE= ParentElement.Current.ClassName
                AutomationE = ParentElement.Current.AutomationId
                LocalizedControlTypeE=ParentElement.Current.LocalizedControlType
                if NameE == Element_Name and ClassE == Element_Class and AutomationE == Element_AutomationID and LocalizedControlTypeE == Element_LocalizedControlType:
                    print "Using Name, Class, AutomationID, LocalizedControlType"
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
                    print "Using Name and AutomationID"
                    return ParentElement
        except:
            None        
        
        
        # Name, LocalizedControlType

        try:
            if Element_Name!= None and Element_Class == None and Element_AutomationID == None and Element_LocalizedControlType!=None:
                
                NameE = ParentElement.Current.Name
                LocalizedControlTypeE=ParentElement.Current.LocalizedControlType
                if NameE == Element_Name and LocalizedControlTypeE == Element_LocalizedControlType:
                    print "Using Name and LocalizedControlType"
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
                    print "Using Class, AutomationID, LocalizedControlType"
                    return ParentElement
        except:
            None
        
        # Class, AutomationID
        
        try:
            if Element_Name== None and Element_Class != None and Element_AutomationID != None and Element_LocalizedControlType==None:
                ClassE= ParentElement.Current.ClassName
                AutomationE = ParentElement.Current.AutomationId
                if  ClassE == Element_Class and AutomationE == Element_AutomationID :
                    print "Using Class and AutomationID"
                    return ParentElement
        except:
            None        
        
        # Class, LocalizedControlType

        try:
            if Element_Name == None and Element_Class != None and Element_AutomationID == None and Element_LocalizedControlType!=None:
                ClassE= ParentElement.Current.ClassName
                LocalizedControlTypeE=ParentElement.Current.LocalizedControlType
                if ClassE == Element_Class and LocalizedControlTypeE == Element_LocalizedControlType:
                    print "Using Class, LocalizedControlType"
                    return ParentElement
        except:
            None
        
        # Class
        try:
            if Element_Name== None and Element_Class != None and Element_AutomationID == None and Element_LocalizedControlType==None:
                ClassE = ParentElement.Current.ClassName
                if ClassE == Element_Class:
                    print "Using Class only"
                    return ParentElement
        except:
            None
        
        # AutomationID, LocalizedControlType
        try:
            if Element_Name == None and Element_Class == None and Element_AutomationID != None and Element_LocalizedControlType!=None:
                AutomationE = ParentElement.Current.AutomationId
                LocalizedControlTypeE=ParentElement.Current.LocalizedControlType
                if  AutomationE == Element_AutomationID and LocalizedControlTypeE == Element_LocalizedControlType:
                    print "Using AutomationID, LocalizedControlType"
                    return ParentElement
        except:
            None        
        
        # AutomationID
        try:
            if Element_Name== None and Element_Class == None and Element_AutomationID != None and Element_LocalizedControlType==None:
                AutomationE = ParentElement.Current.AutomationId
                if AutomationE == Element_AutomationID:
                    print "Using AutomationID"
                    return ParentElement
        except:
            None
        
        # LocalizedControlType
        
        try:
            if Element_Name== None and Element_Class == None and Element_AutomationID == None and Element_LocalizedControlType!=None:
                LocalizedControlTypeE=ParentElement.Current.LocalizedControlType
                if LocalizedControlTypeE == Element_LocalizedControlType:
                    print "Using LocalizedControlType"
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
                    print "Using Name, Class, and AutomationID"
                    return ParentElement
        except:
            None
               
        # Name, Class
        try:
            if (Element_Name != None) and (Element_Class != None) and (Element_AutomationID == None) and (Element_LocalizedControlType==None):
                NameE = ParentElement.Current.Name
                ClassE= ParentElement.Current.ClassName
                if NameE == Element_Name and ClassE == Element_Class:
                    print "Using Name and Class"
                    return ParentElement
        except:
            None
        # Name
        try:
            if (Element_Name!= None) and (Element_Class == None) and (Element_AutomationID == None) and (Element_LocalizedControlType==None):
                

                NameE = ParentElement.Current.Name
                
                if NameE == Element_Name:
                    print "Using only Name"
                    return ParentElement
        except:
            None
    
       
        child_elements = ParentElement.FindAll(TreeScope.Children, Condition.TrueCondition)
        
        if child_elements.Count == 0:
            return None
        
        for each_child in child_elements:
            child = _child_search(each_child, Element_Name,Element_Class,Element_AutomationID,Element_LocalizedControlType)
            if child:
                return child
        
        return None

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        return "failed"
   

def Set_Text_Field(text, Element_Data):
    Text_Element = Get_Element(Element_Data[0], Element_Data[1], Element_Data[2],Element_Data[3],Element_Data[4])
    
    
    
    
def Drop_Down_Selection(Item_To_Select, DropDown_Element):
    
    DropDown = Get_Element(DropDown_Element[0], DropDown_Element[1], DropDown_Element[2],DropDown_Element[3],DropDown_Element[4])
    Item_To_Select = Get_Element(Item_To_Select[0], Item_To_Select[1], Item_To_Select[2],Item_To_Select[3],Item_To_Select[4])

def Check_Box(Checked_Unchecked, Check_Box_Element):
    DropDown = Get_Element(Check_Box_Element[0], Check_Box_Element[1], Check_Box_Element[2],Check_Box_Element[3],Check_Box_Element[4])

def Radio_Button(Radio_Button_Element):
    DropDown = Get_Element(Radio_Button_Element[0], Radio_Button_Element[1], Radio_Button_Element[2],Radio_Button_Element[3],Radio_Button_Element[4])
 
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


def Click_Element_None_Mouse(Element,Expand=None,Invoke=None,Select=None,Toggle=None):
    try:
        x = (int)(Element.Current.BoundingRectangle.Right - Element.Current.BoundingRectangle.Width / 2);
        y = (int)(Element.Current.BoundingRectangle.Bottom - Element.Current.BoundingRectangle.Height / 2);
        win32api.SetCursorPos((x,y))

        print "clicking your element"
        patter_list = Element.GetSupportedPatterns()
        for each in patter_list:
            pattern_name = Automation.PatternName(each)
            if pattern_name == "ExpandCollapse":
                if Expand==True:
                    #check to see if its expanded, if expanded, then do nothing... if not, expand it
                    status = Element.GetCurrentPattern(ExpandCollapsePattern.Pattern).Current.ExpandCollapseState
                    if status == 0:
                        Element.GetCurrentPattern(ExpandCollapsePattern.Pattern).Expand()
                    elif status == 1:
                        print "Already Expanded"
                elif Expand == False:
                    #check to see if its Collapsed, if Collapsed, then do nothing... if not, Collapse it
                    status = Element.GetCurrentPattern(ExpandCollapsePattern.Pattern).Current.ExpandCollapseState
                    if status == 1:
                        Element.GetCurrentPattern(ExpandCollapsePattern.Pattern).Collapse()  
                    elif status == 0:
                        print "Already Collapsed"                    
            
            
                      
            elif pattern_name == "Invoke":
                if Invoke==True:
                    print "invoking the button: %s" %Element.Current.Name
                    time.sleep(2)
                    Element.GetCurrentPattern(InvokePattern.Pattern).Invoke()

            
            
            elif pattern_name == "SelectionItem":
                Element.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
            elif pattern_name == "Toggle":
                Element.GetCurrentPattern(TogglePattern.Pattern).Toggle()
            else:
                #x = int (Element.Current.BoundingRectangle.X)
                #y = int (Element.Current.BoundingRectangle.Y)
        
                x = (int)(Element.Current.BoundingRectangle.Right - Element.Current.BoundingRectangle.Width / 2);
                y = (int)(Element.Current.BoundingRectangle.Bottom - Element.Current.BoundingRectangle.Height / 2);
                win32api.SetCursorPos((x,y))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
                time.sleep(0.1)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))


def Click_Element_Mouse(Element):
    try:
        Element = Get_Element(Element[0], Element[1], Element[2], Element[3], Element[4])
        

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))


def Drag_Object(Element1_source, Element2_destination):
    try:
        print "clicking your element"
        print Element1_source, Element2_destination
        
        x_source = (int)(Element1_source.Current.BoundingRectangle.Right - Element1_source.Current.BoundingRectangle.Width / 2);
        y_source = (int)(Element1_source.Current.BoundingRectangle.Bottom - Element1_source.Current.BoundingRectangle.Height / 2);
        
        x_destination = (int)(Element2_destination.Current.BoundingRectangle.Right - Element2_destination.Current.BoundingRectangle.Width / 2);
        y_destination = (int)(Element2_destination.Current.BoundingRectangle.Bottom - Element2_destination.Current.BoundingRectangle.Height / 2);
        


        autoit.mouse_click_drag(x_source, y_source, x_destination,y_destination, button="left", speed=20)
        


    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))

#Element_Class = None
#menu_bar = Get_Element("Skype", "Call mobiles and landlines from the dial pad.",None,None,None)
menu_bar = Get_Element("Skype", "Today", None, None, "button")
#menu_bar = Get_Element("Pictures", "UIRibbonDockTop", None)
#menu_bar1 = Get_Element(menu_bar, "Ribbon", None)
#menu_bar2 = Get_Element("Pictures", "Ribbon", None)

print menu_bar
Click_Element_None_Mouse(menu_bar,Expand=None,Invoke=True,Select=None,Toggle=None)
#Click_Element_By_Mouse(menu_bar)

#print menu_bar1 
#print menu_bar2
#menu_bar2 = Get_Element("Pictures", "Explorer Pane", None)
#print menu_bar2
# 
# 
# 
# 
# 
# time.sleep(3)
# 
# helpMenu = Get_Element(menu_bar, "Help", None)
# Click_Element_By_Mouse(helpMenu)
# time.sleep(3)

# Menu = Get_Element(menu_bar, "Tools", None)
# print Menu
#Click_Element_By_Mouse(Menu)
#time.sleep(3)


# MainWindowsList = AutomationElement.RootElement.FindAll(TreeScope.Children,Condition.TrueCondition)
# for each in MainWindowsList:
#     a=  each.Current.Name
#     print a
#     s3='Skype™ - Options'.decode('utf-8')
#     s3='Untitled - Notepad'.decode('utf-8')
#     if a == s3:
#         print "found your shit"

