# coding=utf-8
#-*- coding: cp1252 -*-
import clr, System, inspect
from Utilities import CommonUtil
clr.AddReference('UIAutomationClient')
clr.AddReference('UIAutomationTypes')
clr.AddReference('UIAutomationProvider')
from System.Windows.Automation import *
from System.Threading import Thread
from System.Windows.Forms import SendKeys
import time,datetime
import win32api,win32con
import sys
sys.path.append("..")


def FindElement_New(ItemNameID):
    try:
        MainWinElement = AutomationElement.RootElement.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.AutomationIdProperty, "MainView"))
        Element = MainWinElement.FindAll(TreeScope.Descendants,PropertyCondition(AutomationElement.AutomationIdProperty, ItemNameID ))
        if Element.Count == 0:
            Element = MainWinElement.FindAll(TreeScope.Descendants,PropertyCondition(AutomationElement.NameProperty, ItemNameID))
            if Element.Count == 0:
               Element = MainWinElement.FindAll(TreeScope.Descendants,PropertyCondition(AutomationElement.ClassNameProperty, ItemNameID))
               if Element.Count == 0:
                   return False
                       
                    
        return Element
        CommonUtil.ExecLog(sModuleName,"(%s) elements found using (%s) Name/Id" %(Element.Count,ItemNameID),1)
        
    except Exception, e:
            CommonUtil.ExecLog(sModuleName,"Unknown error happened. Returning False and exiting",1) 
            return False   
                   
                   
def FindTheMainWindow(WindowsNameID=None):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In FindTheMainWindow fn.","Info",1)
    winFound = False
    try:
        if WindowsNameID!= None:
            MainWindowsList = AutomationElement.RootElement.FindAll(TreeScope.Children,Condition.TrueCondition)
            for TheWindow in MainWindowsList:
                
                if TheWindow.Current.AutomationId==WindowsNameID:
                    CommonUtil.ExecutionLog(sModuleName,"Automation id matched. Returning True and exiting","Info",1)
                    winFound = True
                    return TheWindow
                elif TheWindow.Current.ClassName == WindowsNameID:
                    CommonUtil.ExecutionLog(sModuleName,"Classname id matched. Returning True and exiting","Info",1)
                    winFound = True
                    return TheWindow
                elif TheWindow.Current.Name == WindowsNameID:
                    CommonUtil.ExecutionLog(sModuleName,"Control Name id matched. Returning True and exiting","Info",1)
                    winFound = True
                    return TheWindow
        if winFound==False:
            CommonUtil.ExecutionLog(sModuleName,"Control not found. Returning False and exiting","Info",1)
            return False 
    except:
           CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
           return False
          
#def FindTheChildElementOfParentWindow(ParentWindowElement=None,ChildNameID=None):
#    sModuleName = inspect.stack()[0][3]+" : Program.py"
#    CommonUtil.ExecutionLog(sModuleName,"In FindTheMainWindow fn.","Info",1)
#    childElement = False
#    try:
#        if ParentWindowElement != None and ChildNameID != None :
#            TheChildElement = ParentWindowElement.FindFirst(TreeScope.Children,PropertyCondition(AutomationElement.ClassNameProperty,ChildNameID))
#            if TheChildElement != None:
#                CommonUtil.ExecutionLog(sModuleName,"Classname id matched. Returning True and exiting","Info",1)
#                childElement = True
#                return TheChildElement
#            TheChildElement = ParentWindowElement.FindFirst(TreeScope.Children,PropertyCondition(AutomationElement.AutomationIdProperty,ChildNameID))
#            if TheChildElement != None:
#                CommonUtil.ExecutionLog(sModuleName,"Automation id matched. Returning True and exiting","Info",1)
#                childElement = True
#                return TheChildElement
#            TheChildElement = ParentWindowElement.FindFirst(TreeScope.Children,PropertyCondition(AutomationElement.NameProperty,ChildNameID))
#            if TheChildElement != None:
#                childElement = True
#                CommonUtil.ExecutionLog(sModuleName,"Control Name id matched. Returning True and exiting","Info",1)
#                return TheChildElement
#        if childElement == False:
#            CommonUtil.ExecutionLog(sModuleName,"Control not found. Returning False and exiting","Info",1)
#            return False
#    except:
#        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
#        return False

def FindTheChildElementOfParentWindow(ParentWindowElement=None,ChildNameID=None):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In FindTheMainWindow fn.","Info",1)
    childElement = False
    try:
        if ParentWindowElement != None and ChildNameID != None :
            TheChildElement = ParentWindowElement.FindFirst(TreeScope.Children,PropertyCondition(AutomationElement.ClassNameProperty,ChildNameID))
            if TheChildElement != None:
                CommonUtil.ExecutionLog(sModuleName,"Classname id matched. Returning True and exiting","Info",1)
                childElement = True
                return TheChildElement
            TheChildElement = ParentWindowElement.FindFirst(TreeScope.Children,PropertyCondition(AutomationElement.AutomationIdProperty,ChildNameID))
            if TheChildElement != None:
                CommonUtil.ExecutionLog(sModuleName,"Automation id matched. Returning True and exiting","Info",1)
                childElement = True
                return TheChildElement
            TheChildElement = ParentWindowElement.FindFirst(TreeScope.Children,PropertyCondition(AutomationElement.NameProperty,ChildNameID))
            if TheChildElement != None:
                childElement = True
                CommonUtil.ExecutionLog(sModuleName,"Control Name id matched. Returning True and exiting","Info",1)
                return TheChildElement
            TheChildElement = ParentWindowElement.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.ClassNameProperty,ChildNameID))
            if TheChildElement != None:
                CommonUtil.ExecutionLog(sModuleName,"Classname id matched. Returning True and exiting","Info",1)
                childElement = True
                return TheChildElement
            TheChildElement = ParentWindowElement.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.AutomationIdProperty,ChildNameID))
            if TheChildElement != None:
                CommonUtil.ExecutionLog(sModuleName,"Automation id matched. Returning True and exiting","Info",1)
                childElement = True
                return TheChildElement
            TheChildElement = ParentWindowElement.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.NameProperty,ChildNameID))
            if TheChildElement != None:
                childElement = True
                CommonUtil.ExecutionLog(sModuleName,"Control Name id matched. Returning True and exiting","Info",1)
                return TheChildElement
        if childElement == False:
            CommonUtil.ExecutionLog(sModuleName,"Control not found. Returning False and exiting","Info",1)
            return False
    except:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return False
                     
def SelectTheItemFromList(AutoElement=None,ItemNameID=None):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In SelectTheItemFromList fn.","Info",1)
    itemFound = False
    try:
        if AutoElement != None and ItemNameID != None :
            SelectingItem = AutoElement.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.AutomationIdProperty,ItemNameID))
            if SelectingItem != None and (SelectingItem.Current.ClassName != "CheckBox"):
                SelectingItem.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
                itemFound = True
                Thread.Sleep(100)
                CommonUtil.ExecutionLog(sModuleName,"Automation id matched. Returning True and exiting","Info",1)
                return True
            SelectingItem = AutoElement.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.NameProperty,ItemNameID))
            if SelectingItem != None and (SelectingItem.Current.ClassName != "CheckBox"):
                SelectingItem.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
                itemFound = True        
                Thread.Sleep(100)
                CommonUtil.ExecutionLog(sModuleName,"Control Name id matched. Returning True and exiting","Info",1)
                return True
            SelectingItem = AutoElement.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.ClassNameProperty,ItemNameID))
            if SelectingItem != None:
                SelectingItem.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
                itemFound = True
                CommonUtil.ExecutionLog(sModuleName,"Classname id matched. Returning True and exiting","Info",1)
                Thread.Sleep(100)
                return True
        if itemFound == False:
            CommonUtil.ExecutionLog(sModuleName,"Control not found. Returning False and exiting","Info",1)
            return "No Property matched: " + ItemNameID + " not found"
    except Exception,e:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return e
        
def ClickTheButton(AutoElement,ButtonNameID):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In ClickTheButton fn.","Info",1)
    btnClick = False
    try:
        if AutoElement != None and ButtonNameID != None :
            ButtonElement = AutoElement.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.NameProperty,ButtonNameID))
            if ButtonElement != None:
                ButtonElement.GetCurrentPattern(InvokePattern.Pattern).Invoke()
                btnClick = True
                CommonUtil.ExecutionLog(sModuleName,"Control Name id matched. Returning True and exiting","Info",1)
                return True
            ButtonElement = AutoElement.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.AutomationIdProperty,ButtonNameID))
            if ButtonElement != None:
                ButtonElement.GetCurrentPattern(InvokePattern.Pattern).Invoke()
                btnClick = True
                CommonUtil.ExecutionLog(sModuleName,"Automation id matched. Returning True and exiting","Info",1)
                return True
            ButtonElement = AutoElement.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.ClassNameProperty,ButtonNameID))
            if ButtonElement != None:
                ButtonElement.GetCurrentPattern(InvokePattern.Pattern).Invoke()
                btnClick = True
                CommonUtil.ExecutionLog(sModuleName,"Classname id matched. Returning True and exiting","Info",1)
                return True
        if btnClick == False:
            CommonUtil.ExecutionLog(sModuleName,"Control not found. Returning False and exiting","Info",1)
            return "No property matched : " + ButtonNameID + " not found"
    except Exception,e:
        print "e: %s"%ButtonNameID,e
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return False
   
def ScrollUpAndDown(ListBoxElemet):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In ScrollUpAndDown fn.","Info",1)
    try:
        PlayList = ListBoxElemet.FindAll(TreeScope.Descendants,Condition.TrueCondition)
        IsScrollAble = ListBoxElemet.GetCurrentPattern(ScrollPattern.Pattern).Current.VerticallyScrollable
        if IsScrollAble:
            Counter = 0
            while Counter < PlayList.Count:
                ListBoxElemet.GetCurrentPattern(ScrollPattern.Pattern).ScrollVertical(ScrollAmount.SmallIncrement)
                Counter=Counter+1

            Counter = 0
            while Counter < PlayList.Count:
                ListBoxElemet.GetCurrentPattern(ScrollPattern.Pattern).ScrollVertical(ScrollAmount.SmallDecrement)
                Counter=Counter+1
            Thread.Sleep(500)
    except Exception, e:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return e

def ScrollDownToItem(ListBoxElemet,ItemName):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In ScrollUpAndDown fn.","Info",1)
    try:
        PlayList = ListBoxElemet.FindAll(TreeScope.Descendants,Condition.TrueCondition)
        IsScrollAble = ListBoxElemet.GetCurrentPattern(ScrollPattern.Pattern).Current.VerticallyScrollable
        if IsScrollAble:
            Counter = 0
            Item = FindTheChildElementOfParentWindow(ListBoxElemet,ItemName)
            if Item:
                if Item.Current.IsOffscreen == False:
                    return True            
            while Counter < PlayList.Count:
                try:
                    ListBoxElemet.GetCurrentPattern(ScrollPattern.Pattern).ScrollVertical(ScrollAmount.LargeIncrement)
                except ArgumentException:
                    ListBoxElemet.GetCurrentPattern(ScrollPattern.Pattern).ScrollVertical(ScrollAmount.SmallIncrement)
                Counter=Counter+1
                Item = FindTheChildElementOfParentWindow(ListBoxElemet,ItemName)
                if Item:
                    return True

            Counter = 0
            while Counter < PlayList.Count:
                try:
                    ListBoxElemet.GetCurrentPattern(ScrollPattern.Pattern).ScrollVertical(ScrollAmount.LargeDecrement)
                except ArgumentException:
                    ListBoxElemet.GetCurrentPattern(ScrollPattern.Pattern).ScrollVertical(ScrollAmount.SmallDecrement)
                Counter=Counter+1
                Item = FindTheChildElementOfParentWindow(ListBoxElemet,ItemName)
                if Item:
                    return True
                
            Thread.Sleep(500)
    except Exception, e:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return e
    
def ScrollLeftToRight(ListBoxElemet):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In ScrollLeftToRight fn.","Info",1)
    try:
        PlayList = ListBoxElemet.FindAll(TreeScope.Descendants,Condition.TrueCondition)
        IsScrollAble = ListBoxElemet.GetCurrentPattern(ScrollPattern.Pattern).Current.HorizontallyScrollable
        if IsScrollAble:
            Counter = 0
            while Counter < PlayList.Count:
                ListBoxElemet.GetCurrentPattern(ScrollPattern.Pattern).ScrollHorizontal(ScrollAmount.SmallIncrement)
                Counter=Counter+1

            Counter = 0
            while Counter < PlayList.Count:
                ListBoxElemet.GetCurrentPattern(ScrollPattern.Pattern).ScrollHorizontal(ScrollAmount.SmallDecrement)
                Counter=Counter+1
            Thread.Sleep(500)
    except Exception, e:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return e
                
def ToggleTheItem(ListBoxElement=None,ItemNameID=None):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In ToggleTheItem fn.","Info",1)
    def MarkUnMarkItem(ListBoxElement):
        sModuleName = inspect.stack()[0][3]+" : Program.py"
        CommonUtil.ExecutionLog(sModuleName,"In MarkUnMarkItem fn.","Info",1)
        try:
            #Checking if parent is checkbox item
            if ListBoxElement.Current.ClassName == "CheckBox":
                CheckItem = ListBoxElement
            elif ListBoxElement.Current.ClassName == "Button":
                CheckItem = ListBoxElement
            else:
                CheckItem = ListBoxElement.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.ClassNameProperty,"CheckBox"))
            
             #Checking if child of ListBoxItem is checkbox item    
            if  CheckItem.Current.ClassName == "CheckBox":
                CheckItem.GetCurrentPattern(TogglePattern.Pattern).Toggle()
                return True
                #Thread.Sleep(900)
            elif CheckItem.Current.ClassName == "Button":
                 CheckItem.GetCurrentPattern(TogglePattern.Pattern).Toggle()
                 return True
        except:
            CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
            return False
        
        
    if ListBoxElement != None or ItemNameID!= None:
        sModuleName = inspect.stack()[0][3]+" : Program.py"
        try:
            ListItem = FindTheChildElementOfParentWindow(ListBoxElement,ItemNameID + " Checked")
            if type(ListItem) == System.Windows.Automation.AutomationElement:
                if MarkUnMarkItem(ListItem) == True: 
                    return True 
            elif type(FindTheChildElementOfParentWindow(ListBoxElement,ItemNameID + " Unchecked")) == System.Windows.Automation.AutomationElement:
                ListItem = FindTheChildElementOfParentWindow(ListBoxElement,ItemNameID + " Unchecked")
                if MarkUnMarkItem(ListItem) == True:
                    return True
            elif type(FindTheChildElementOfParentWindow(ListBoxElement,ItemNameID)) == System.Windows.Automation.AutomationElement:
                ListItem = FindTheChildElementOfParentWindow(ListBoxElement,ItemNameID)
                if MarkUnMarkItem(ListItem) == True:
                    return True
        except:
            CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
            return False
            
def CheckBoxStatus(ListBoxElement=None,ItemNameID=None):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In CheckBoxStatus fn.","Info",1)
    try:   
        if ListBoxElement != None or ItemNameID!= None:
            ListItem = FindTheChildElementOfParentWindow(ListBoxElement,ItemNameID + " Checked")
            if ListItem.GetType() == System.Windows.Automation.AutomationElement:
                CommonUtil.ExecutionLog(sModuleName,"Checked returned and exiting","Info",1)
                return "Checked"
            elif FindTheChildElementOfParentWindow(ListBoxElement,ItemNameID + " Unchecked").GetType() == System.Windows.Automation.AutomationElement:
                CommonUtil.ExecutionLog(sModuleName,"Unchecked returned and exiting","Info",1)
                return "Unchecked"
            elif FindTheChildElementOfParentWindow(ListBoxElement,ItemNameID).GetType() == System.Windows.Automation.AutomationElement:
                ListItem = FindTheChildElementOfParentWindow(ListBoxElement,ItemNameID)
                return ListItem.Current.ToggleState
    except:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return False
                                  
def FindSupportedPatternNames(AutoElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In FindSupportedPatternNames fn.","Info",1)
    PatternList = AutoElement.GetSupportedPatterns()
    for i in PatternList:
        print Automation.PatternName(i)

def WaitTillMainWindowActive(WindowsElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In WaitTillMainWindowActive fn.","Info",1)
    try:
        WindowState = WindowsElement.GetCurrentPattern(WindowPattern.Pattern).Current.WindowInteractionState
        seconds = 1
        while WindowState != System.Windows.Automation.WindowInteractionState.ReadyForUserInteraction:
            if seconds == 40:
                CommonUtil.ExecutionLog(sModuleName,"WaitTillMainWindowActive timed out","Info",1)
                return "Time out"
            Thread.Sleep(100)
            WindowState = WindowsElement.GetCurrentPattern(WindowPattern.Pattern).Current.WindowInteractionState    
        return True
    except:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return False

def WaitTillChildWindowActive(WindowsElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In WaitTillChildWindowActive fn.","Info",1)
    try:
        WindowState = WindowsElement.GetCurrentPattern(WindowPattern.Pattern).Current.WindowInteractionState
        seconds = 1
        while WindowState != System.Windows.Automation.WindowInteractionState.Running:
            if seconds == 40:
                CommonUtil.ExecutionLog(sModuleName,"Time exceeded for child window active. Returning False and exiting","Info",1)
                return "Time out"
            Thread.Sleep(100)
            WindowState = WindowsElement.GetCurrentPattern(WindowPattern.Pattern).Current.WindowInteractionState
            seconds = seconds+1  
        CommonUtil.ExecutionLog(sModuleName,"Window active. Returning True and exiting","Info",1)  
        return True
    except:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return False

def CloseChildWindow(ParentWindowElement=None,ChildWindowNameID=None):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In CloseChildWindow fn.","Info",1)
    try:
        if ParentWindowElement != None and ChildWindowNameID != None :  
            Childelements = ParentWindowElement.FindAll(TreeScope.Children,Condition.TrueCondition)
            for eachElement in Childelements:
                if eachElement.Current.ClassName == "Window" and eachElement.Current.Name == ChildWindowNameID:
                    eachElement.GetCurrentPattern(WindowPattern.Pattern).Close()
                    return True
                elif eachElement.Current.ClassName == "Window" and eachElement.Current.ClassName == ChildWindowNameID:
                    eachElement.GetCurrentPattern(WindowPattern.Pattern).Close()
                    return True
                elif eachElement.Current.ClassName == "Window" and eachElement.Current.AutomationId == ChildWindowNameID:
                    eachElement.GetCurrentPattern(WindowPattern.Pattern).Close()
                    return True          
    except:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return False
                
def CloseChildWindowExceptThis(ParentWindowElement=None,ChildWindowNameID=None):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In CloseChildWindowExceptThis fn.","Info",1)
    try:
        if ParentWindowElement != None and ChildWindowNameID != None :
            AllChildElements = ParentWindowElement.FindAll(TreeScope.Children,Condition.TrueCondition)
            for eachElement in AllChildElements:
                if eachElement.Current.ClassName == "Window":
                    if eachElement.Current.Name != ChildWindowNameID and eachElement.Current.AutomationId != ChildWindowNameID:
                        #AutomationPropertyChangedEventArgs(eachElement.GetCurrentPattern(WindowPattern.Pattern).WindowInteractionStateProperty,WindowInteractionState.Running,WindowInteractionState.ReadyForUserInteraction)
                        eachElement.GetCurrentPattern(WindowPattern.Pattern).Close()
                        return True
    except:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return False
            
def WaitForChildWindow(ParentWindowNameID=None,ChildWindowNameID=None):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In WaitForChildWindow fn.","Info",1)
    CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
    if ParentWindowNameID != None and ChildWindowNameID != None :
        seconds = 1
        ParentWindow = FindTheMainWindow(ParentWindowNameID)
        ChildWindow = FindTheChildElementOfParentWindow(ParentWindow, ChildWindowNameID)
        while ChildWindow == False:
            if seconds == 40:
                CommonUtil.ExecutionLog(sModuleName,"Time exceeded for child window. Returning False and exiting","Info",1)
                return False
            Thread.Sleep(100)
            ChildWindow = FindTheChildElementOfParentWindow(ParentWindow, ChildWindowNameID)
            seconds = seconds + 1
        CommonUtil.ExecutionLog(sModuleName,"Child window found. Returning True and exiting","Info",1)  
        return True
                  
def WaitTillProgressComplete(WindowElement,ProgressBarID):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In WaitTillProgressComplete fn.","Info",1)
    try:
        ProgressBarElement = FindTheChildElementOfParentWindow(WindowElement,ProgressBarID)
        ProgressBarValue = 0
        Value = ProgressBarElement.GetCurrentPattern(RangeValuePattern.Pattern).Current.Value
        while Value != 100:
            Thread.Sleep(100)
            Value = ProgressBarElement.GetCurrentPattern(RangeValuePattern.Pattern).Current.Value
        CommonUtil.ExecutionLog(sModuleName,"Progress completed. Returning True and exiting","Info",1)  
        return True
    except:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return False     
    

"""
Following functions are made using above functions to make functionality more consised and easy to use.
""" 



def ElementExists(ItemNameID,*ParentWindowsElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In ToggleItem fn.","Info",1)
    """
        Parameters: ItemNameID is the name or automation id 
               ParentWindowsElement is list of the parent windows of the element you are looking for
        Example: You want to know if element (button, checkbox etc) exists on window D, where Window D is the child window of C and window C is child window of B and similarly
            B is child of window A. So you have following data,
            WindowA id is "NotePade"
            WindowB id is "Print"
            WindowC id is "Configure"
            WindowD id is "SetUp"
            CheckBoxElement id is "Yes"
            Let's call this function
            ElementExists("Yes","NotePade","Print", "Configure","SetUp")
        Rerurn: It will return True if "CheckBoxElement" exists on windows D otherwise False
   """
    if ParentWindowsElement != None and ItemNameID != None:
        try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1    
            if FindTheChildElementOfParentWindow(MainWin,ItemNameID) != False:
                return True
            else:
                 return False
        except:
            CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
            return False

def IsSelected(ItemNameID,*ParentWindowsElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In IsItemSelected fn.","info",1)
    try:
        if ParentWindowsElement != None:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            if ItemNameID != None:
                Item = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
                return Item.GetCurrentPattern(SelectionItemPattern.Pattern).Current.IsSelected
            
    except:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","info",3) 
        return False 
    
def IsOffscreen(ItemNameID,*ParentWindowsElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In ToggleItem fn.","Info",1)
    """
        Parameters: ItemNameID is the name or automation id 
               ParentWindowsElement is list of the parent windows of the element you are looking for
        Example: You want to know if image/element isoffscreen on window D, where Window D is the child window of C and window C is child window of B and similarly
            B is child of window A. So you have following data,
            WindowA id is "NotePade"
            WindowB id is "Print"
            WindowC id is "Configure"
            WindowD id is "SetUp"
            spinning image id is "spinning"
            Let's call this function
            IsOffscreen("spinning","NotePade","Print", "Configure","SetUp")
        Rerurn: It will return Yes if "spinning image" isoffscreen on windows D otherwise No, cos True/Flase is used by programm.py
   """
    if ParentWindowsElement != None and ItemNameID != None:
        try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1    
            if FindTheChildElementOfParentWindow(MainWin,ItemNameID).Current.IsOffscreen == False:
                return "No"
            else:
                 return "Yes"
        except:
            CommonUtil.ExecutionLog(sModuleName,"%s error happened","Info",1) 
            return False    

def ReturnChildElement(*ParentWindowsElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In ReturnChildElement fn.","Info",1)
    CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
    if ParentWindowsElement != None:
       try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            CommonUtil.ExecutionLog(sModuleName,"child element returned","Info",1) 
            return MainWin
       except:
           CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
           return False

def ReturnAllChildElements(*ParentWindowsElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In ReturnChildElement fn.","Info",1)
    CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
    if ParentWindowsElement != None:
       try:
            arglen = len(ParentWindowsElement)-1
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            CommonUtil.ExecutionLog(sModuleName,"child element returned","Info",1)
            ElementList = MainWin.FindAll(TreeScope.Children,PropertyCondition(AutomationElement.ClassNameProperty,ParentWindowsElement[-1]))
            return ElementList
       except:
           CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
           return False

def GetListViewItemNumber(*ParentWindowsElement):
    """
    Description: GetListViewItemNumber return the number of item in ListView element
    You can find how many radio buttons or check box are there in this listveiw element
    """
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In GetListViewItemsNumber fn.","Info",1)
    CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
    if ParentWindowsElement != None:
       try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            CommonUtil.ExecutionLog(sModuleName,"child element returned","Info",1) 
            return MainWin.GetCurrentPattern(GridPattern.Pattern).Current.RowCount
       except:
           CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
           return False
       

def WaitTillEnabled(ItemNameID = None,*ParentWindowsElement): 
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In WaitTillEnabled fn.","Info",1)
    if ParentWindowsElement != None:
        arglen = len(ParentWindowsElement)
        count = 1
        MainWin = FindTheMainWindow(ParentWindowsElement[0])
        while count < arglen:
            SubWin = ParentWindowsElement[count]
            MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
            count = count+1
        if ItemNameID != None:
            Item = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
            seconds = 0
            while Item == 0:
                if seconds == 5:
                    CommonUtil.ExecutionLog(sModuleName,"Time exceeded for child window. Returning False and exiting","Info",1)
                    return False
                Thread.Sleep(100)
                Item = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
                seconds = seconds+1
                
            return True
        else:
            MainWinStatus = MainWin.GetCurrentPattern(WindowPattern.Pattern).Current.WindowInteractionState
            seconds = 0
            while MainWinStatus == 0:
                if seconds == 15:
                    CommonUtil.ExecutionLog(sModuleName,"Time exceeded for child window. Returning False and exiting","Info",1)
                    return False
                Thread.Sleep(100)
                MainWinStatus = MainWin.GetCurrentPattern(WindowPattern.Pattern).Current.WindowInteractionState
                seconds = seconds+1
            CommonUtil.ExecutionLog(sModuleName,"control enabled. Returning True and exiting","Info",1)  
            return True
                   
def PressButton(ButtonNameID,*ParentWindowsElement):
    #Take screen capture before pressing button
    CommonUtil.TakeScreenShot("Before Clicking Button - "+ButtonNameID) 
    
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In PressButton fn.","Info",1)
    """
       Parameters: ButtonNameID is the name or automation id for the button you want to click
                   ParentWindowsElement is list of the parent windows of the button you want to click
       Example: You want to click on the OK button and Ok button placed on window D, where Window D is the child window of C and window C is child window of B and similarly
                B is child of window A. So you have following data,
                WindowA id is "NotePade"
                WindowB id is "Print"
                WindowC id is "Configure"
                WindowD id is "SetUp"
                Button id is "OKID"
                Let's call this function
                PressButton("OKID","NotePade","Print", "Configure","SetUp")
        Return: It will return "Button Click" string or "<Button name/id> not found" string if button was not found, otherwise it will return False if there is an error
    """
#   if WaitTillEnabled(ButtonNameID,ParentWindowsElement) == False:
#       return ButtonNameID + ": is not enabled"
    if ParentWindowsElement != None and ButtonNameID != None :
       try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            CommonUtil.ExecutionLog(sModuleName,"Calling click the button","Info",1)
            returnvalue = ClickTheButton(MainWin,ButtonNameID)  
            CommonUtil.TakeScreenShot("After Clicking Button - "+ButtonNameID)
            return returnvalue
       except Exception,e:
           print e
           CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
           CommonUtil.TakeScreenShot("Error Clicking Button - " + ButtonNameID) 
           return False
        
def ToggleItemStatus(ItemNameID,*ParentWindowsElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In ToggleItemStatus fn.","Info",1)
    """
        Parameters: ItemNameID is the name or automation id for the CheckBox you want to know the status(On/Off)
               ParentWindowsElement is list of the parent windows of the CheckBox you want to know the status(On/Off)
        Example: You want to know the status(On/Off) of the Checkbox and Checkbox is placed on window D, where Window D is the child window of C and window C is child window of B and similarly
            B is child of window A. So you have following data,
            WindowA id is "NotePade"
            WindowB id is "Print"
            WindowC id is "Configure"
            WindowD id is "SetUp"
            CheckBox id is "Yes"
            Let's call this function
            ToggleItemStatus("Yes","NotePade","Print", "Configure","SetUp")
        Return: It will return the status if checkbox in the forme of On/Off or Flase if there is an error
    """
    if ParentWindowsElement != None and ItemNameID != None :
        try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            ToggleItem = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
            sToggleItemStatus = GetItemStatus(ToggleItem)
            iSeconds = 0 
            while sToggleItemStatus == False:
               if iSeconds == 30:
                    print "Time out on getting Item Status of Item : ",ItemNameID
                    return False
               time.sleep(1)
               ToggleItem = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
               sToggleItemStatus = GetItemStatus(ToggleItem)
               iSeconds = iSeconds + 1
            if ToggleItem.Current.ClassName == "CheckBox":
                if ToggleItem.GetCurrentPattern(TogglePattern.Pattern).Current.ToggleState == 1:
                    CommonUtil.ExecutionLog(sModuleName,"Checkbox:  On","Info",1) 
                    return "On"
                else:
                    CommonUtil.ExecutionLog(sModuleName,"Checkbox: Off","Info",1) 
                    return "Off"
            if ToggleItem == False:
                 ToggleItem  = FindTheChildElementOfParentWindow(MainWin,ItemNameID + " Checked")
                 if ToggleItem == False:
                     ToggleItem = FindTheChildElementOfParentWindow(MainWin,ItemNameID + " Unchecked")
                     if ToggleItem == False:
                         CommonUtil.ExecutionLog(sModuleName,"Control not found. Returning False and exiting","Info",1)
                         return False
            CheckItem = ToggleItem.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.ClassNameProperty,"CheckBox"))
            
            if  CheckItem != None:   
                if CheckItem.GetCurrentPattern(TogglePattern.Pattern).Current.ToggleState == 1:
                    return "On"
                else:
                    return "Off"
            
            elif ToggleItem.Current.ClassName == "Button":
                 if ToggleItem.GetCurrentPattern(TogglePattern.Pattern).Current.ToggleState == 1:
                     return "On"
                 else:
                    return "Off"
            
        except Exception,e:
            CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1)
            time.sleep(5)
            print "Exception %s" %e 
            return False
                
def ToggleItem(ItemNameID,*ParentWindowsElement):
    CommonUtil.TakeScreenShot("Before Toggling Item - " + ItemNameID) 
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In ToggleItem fn.","Info",1)
    """
        Parameters: ItemNameID is the name or automation id for the CheckBox you want to click
               ParentWindowsElement is list of the parent windows of the button you want to Toggle
        Example: You want to Togggle on the Checkbox and Checkbox is placed on window D, where Window D is the child window of C and window C is child window of B and similarly
            B is child of window A. So you have following data,
            WindowA id is "NotePade"
            WindowB id is "Print"
            WindowC id is "Configure"
            WindowD id is "SetUp"
            CheckBox id is "Yes"
            Let's call this function
            ToggleItem("Yes","NotePade","Print", "Configure","SetUp")
        Rerurn: It will return "<item name/id> has been toggled" once it's done or False if there is an error
   """
    if ParentWindowsElement != None and ItemNameID != None:
        try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1    
            returnvalue = ToggleTheItem(MainWin,ItemNameID)
            CommonUtil.TakeScreenShot("After Toggling Item - " + ItemNameID)
            return returnvalue
        except:
            CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
            CommonUtil.TakeScreenShot("Error Toggling Item - " + ItemNameID) 
            return False
  
def ExpandListBox(ItemNameID,*ParentWindowsElement):
    CommonUtil.TakeScreenShot("Before Expanding List Box - " + ItemNameID) 
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    #CommonUtil.ExecutionLog(sModuleName,"In ExpandListBox fn.","Info",1)
    """
        Parameters: ItemNameID is the name or automation id for the ComboBoxItem you want to Expand
                    ParentWindowsElement is list of the parent windows of the ComboBoxItem you want to expand
        Example: You want to expand/drop down comboboxitem and comboboxitem is placed on window D, where Window D is the child window of C and window C is child window of B and similarly
            B is child of window A. So you have following data,
            WindowA id is "NotePade"
            WindowB id is "Print"
            WindowC id is "Configure"
            WindowD id is "SetUp"
            ComboBoxItem id is "File"
            Let's call this function
            ExpandListBox("File","NotePade","Print", "Configure","SetUp")
        Rerurn: It will return "Expended" string once it's done or it will return False if there is an error
   """
#    if ParentWindowsElement != None and ItemNameID != None:
#        try:
#            arglen = len(ParentWindowsElement)
#            count = 1
#            MainWin = FindTheMainWindow(ParentWindowsElement[0])
#            while count < arglen:
#                SubWin = ParentWindowsElement[count]
#                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
#                count = count+1
#            ComboBoxItem = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
#            ComboBoxItem.GetCurrentPattern(ExpandCollapsePattern.Pattern).Expand()
#            BoxState = ComboBoxItem.GetCurrentPattern(ExpandCollapsePattern.Pattern).Current.ExpandCollapseState
#            while BoxState == 0:
#                BoxState = ComboBoxItem.GetCurrentPattern(ExpandCollapsePattern.Pattern).Current.ExpandCollapseState
#            return True
#        except:
#            CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
#            return False 
    if ParentWindowsElement != None and ItemNameID != None:
        try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            Expanded = False
            NumTrys = 0
            while Expanded == False and NumTrys < 12:
                #print "Expanded: ",Expanded
                #print "NumTrys: ",NumTrys
                ComboBoxItem = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
                ComboBoxItem.GetCurrentPattern(ExpandCollapsePattern.Pattern).Expand()
                BoxState = ComboBoxItem.GetCurrentPattern(ExpandCollapsePattern.Pattern).Current.ExpandCollapseState
                ExpTimeOut = False
                seconds = 0
                if BoxState != 0:
                    Expanded = True
                while BoxState == 0 and ExpTimeOut == False:
                    time.sleep(.1)
                    #print "BoxState = ",BoxState
                    #print "ExpTimeOut = ",ExpTimeOut
                    #CommonUtil.ExecLog(sModuleInfo,"waiting for Boxstate : %s"%BoxState,1)
                    BoxState = ComboBoxItem.GetCurrentPattern(ExpandCollapsePattern.Pattern).Current.ExpandCollapseState
                    seconds = seconds + 1
                    if BoxState != 0:
                        Expanded = True
                    if seconds > 50:
                        ExpTimeOut = True
                #Try to expand again
                NumTrys = NumTrys + 1
            CommonUtil.TakeScreenShot("After Expanding List Box - " + ItemNameID) 
            return True
        except Exception,e:
            print "Exception: ",e
            CommonUtil.ExecLog(sModuleInfo,"Exception expanding menu : %s"%e,3)
            #CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
            CommonUtil.TakeScreenShot("Error Expanding List Box - " + ItemNameID) 
            return False 
            
def CollapseListBox(ItemNameID,*ParentWindowsElement):
    CommonUtil.TakeScreenShot("Before Collapsing List Box -  " + ItemNameID) 
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In CollapseListBox fn.","Info",1)
    """
        Parameters: ItemNameID is the name or automation id for the ComboBoxItem you want to Collapse
                    ParentWindowsElement is list of the parent windows of the ComboBoxItem you want to collapse
        Example: You want to collapse comboboxitem and comboboxitem is placed on window D, where Window D is the child window of C and window C is child window of B and similarly
            B is child of window A. So you have following data,
            WindowA id is "NotePade"
            WindowB id is "Print"
            WindowC id is "Configure"
            WindowD id is "SetUp"
            ComboBoxItem id is "File"
            Let's call this function
            CollapseListBox("File","NotePade","Print", "Configure","SetUp")
        Rerurn: It will return True string once it's done or it will return False if there is an error
   """
    if ParentWindowsElement != None and ItemNameID != None:
        try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            ComboBoxItem = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
            ComboBoxItem.GetCurrentPattern(ExpandCollapsePattern.Pattern).Collapse()
            BoxState = ComboBoxItem.GetCurrentPattern(ExpandCollapsePattern.Pattern).Current.ExpandCollapseState
            while BoxState == 1:
                BoxState = ComboBoxItem.GetCurrentPattern(ExpandCollapsePattern.Pattern).Current.ExpandCollapseState
            #Thread.Sleep(300)
            CommonUtil.TakeScreenShot("After Collapsing List Box - " + ItemNameID) 
            return True
        except:
            CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
            CommonUtil.TakeScreenShot("Error Collapsing List Box - " + ItemNameID) 
            return False 
          
def SelectItemFromList(ItemNameID,*ParentWindowsElement):
    CommonUtil.TakeScreenShot("Before Selecting Item From List - " + ItemNameID) 
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In SelectItemFromList fn.","Info",1)
    """
        Parameters: ItemNameID is the name or automation id for the List Item you want to select/click
                    ParentWindowsElement is list of the parent windows of the List item you want to select/click
        Example: You want to select/click item form the list and listbox is placed on window D, where Window D is the child window of C and window C is child window of B and similarly
            B is child of window A. So you have following data,
            WindowA id is "NotePade"
            WindowB id is "Print"
            WindowC id is "Configure"
            WindowD id is "SetUp"
            listitem id is "Exit"
            Let's call this function
            SelectItemFromList("Exit","NotePade","Print", "Configure","SetUp")
        Rerurn: It will return "Item Selected" string once it's done or "item not found" it does not find the item on the list, or it will return False if there is an error
   """
    if ParentWindowsElement != None and ItemNameID != None:
        try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1    
            returnvalue = SelectTheItemFromList(MainWin,ItemNameID)
            CommonUtil.TakeScreenShot("After Selecting Item From List - " + ItemNameID)
            return returnvalue        
        except Exception,e :
            CommonUtil.TakeScreenShot("Error Selecting Item From List - " + ItemNameID) 
            CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
            return e
   
def GetTheWindowOrItemState(ItemNameID = None,*ParentWindowsElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In GetTheWindowOrItemState fn.","Info",1)
    try:
        if ParentWindowsElement != None:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            if ItemNameID != None:
                Item = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
                return Item.Current.IsEnabled
            else:
                return MainWin.GetCurrentPattern(WindowPattern.Pattern).Current.WindowInteractionState
    except:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return False  

def GetWindowStatus(WindowElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In GetWindowStatus fn.","Info",1)
    try:
        if WindowElement != None:
            WindowState = WindowElement.GetCurrentPattern(WindowPattern.Pattern).Current.WindowInteractionState
        if WindowState == System.Windows.Automation.WindowInteractionState.ReadyForUserInteraction:
            return "Ready"
        if WindowState == System.Windows.Automation.WindowInteractionState.Running:
            return "Running"
    except:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return False

def GetItemStatus(WindowElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In GetItemStatus fn.","Info",1)
    try:
        if WindowElement != None:
            WindowState = WindowElement.Current.ClassName
        if WindowState:
            return "Ready"
        else:
            return "False"
    except:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return False

def IsKeyboardFocusable(ItemNameID = None,*ParentWindowsElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In IsKeyboardFocusable fn.","Info",1)
    try:
        if ParentWindowsElement != None:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            if ItemNameID != None:
                Item = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
                return Item.Current.IsKeyboardFocusable
            else:
                return MainWin.GetCurrentPattern(WindowPattern.Pattern).Current.WindowInteractionState
    except:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return False  

def IsItemEnable(ItemNameID = None,*ParentWindowsElement):
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In IsItemEnable fn.","Info",1)
    try:
        if ParentWindowsElement != None:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            if ItemNameID != None:
                Item = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
                return Item.Current.IsEnabled
            else:
                return MainWin.GetCurrentPattern(WindowPattern.Pattern).Current.WindowInteractionState
    except:
        CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
        return False 
          
def SetTextBoxValue(sStringValue,ItemNameID = None,*ParentWindowsElement):
    
    CommonUtil.TakeScreenShot("Before Setting Text Value in "+ ItemNameID) 
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In SetTextBoxValue fn.","Info",1)
    if ParentWindowsElement != None and ItemNameID != None and sStringValue != None:
       try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1

            TextBox = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
            TextBox.GetCurrentPattern(ValuePattern.Pattern).SetValue(sStringValue)
            CommonUtil.TakeScreenShot("After Setting Text Value in " + ItemNameID) 
            return True
       except:
           CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
           CommonUtil.TakeScreenShot("Error Setting Text Value in " + ItemNameID) 
           return False
                             
#def GetScreenShot(sTargetDirectoryPath):
#    sModuleName = inspect.stack()[0][3]+" : Program.py"
#    import ImageGrab # Please install Python Imaging Librar from http://www.pythonware.com/products/pil/ for this moduel
#    import os,time
#    #User Settings:
#    SaveDirectory=(sTargetDirectoryPath)
#    #ImageEditorPath=r'C:\WINDOWS\system32\mspaint.exe'
#    #Here is another example:
#    #ImageEditorPath=r'C:\Program Files\IrfanView\i_view32.exe'
#    #---------------------------------------------------------
#    
#    img=ImageGrab.grab()
#    saveas=os.path.join(SaveDirectory,'%s.png' %time.strftime("%m_%d_%Y  %I_%M_%S"))
#    img.save(saveas)
#    #editorstring='""%s" "%s"'% (ImageEditorPath,saveas) #Just for Windows right now?
#    #Notice the first leading " above? This is the bug in python that no one will admit...
#    #os.system(editorstring) 
#    return True         
    
def SelectTab(TabNameID,*ParentWindowsElement):
    CommonUtil.TakeScreenShot("Before Selecting Tab - "+ ItemNameID) 
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In SelectTab fn.","Info",1)
    """
   Parameters: TabNameID is the name or automation id for the Tab you want to Select
               ParentWindowsElement is list of the parent windows of the Tab you want to Select
   Example: You want to Select on the Media Tab and Media Tab placed on window D, where Window D is the child window of C and window C is child window of B and similarly
            B is child of window A. So you have following data,
            WindowA id is "NotePad"
            WindowB id is "Print"
            WindowC id is "Configure"
            WindowD id is "SetUp"
            Tab id is "TabID"
            Let's call this function
            SelectTab("TabID","NotePad","Print", "Configure","SetUp")
    Return: It will return "Tab Select" string or "<Tab name/id> not found" string if Tab was not found, otherwise it will return False if there is an error
    """

    if ParentWindowsElement != None and TabNameID != None :
       sModuleName = inspect.stack()[0][3]+" : Program.py"
       CommonUtil.ExecutionLog(sModuleName,"In SelectTheItemFromList fn.","Info",1)
       try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            tabSelect = False
            TabElement = MainWin.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.NameProperty,TabNameID))
            if TabElement != None:
                TabElement.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
                CommonUtil.ExecutionLog(sModuleName,"Control Name id matched. Returning True and exiting","Info",1)
                tabSelect = True
                CommonUtil.TakeScreenShot("After Selecting Tab - "+ ItemNameID) 
                return True
            TabElement = MainWin.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.AutomationIdProperty,ButtonNameID))
            if TabElement != None:
                TabElement.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
                CommonUtil.ExecutionLog(sModuleName,"Control Automation id matched. Returning True and exiting","Info",1)
                tabSelect = True
                CommonUtil.TakeScreenShot("After Selecting Tab - "+ ItemNameID)
                return True
            TabElement = MainWin.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.ClassNameProperty,ButtonNameID))
            if TabElement != None:
                TabElement.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
                CommonUtil.ExecutionLog(sModuleName,"ClassName id matched. Returning True and exiting","Info",1)
                tabSelect = True
                CommonUtil.TakeScreenShot("After Selecting Tab - "+ ItemNameID)
                return True
            if tabSelect == False:
                CommonUtil.TakeScreenShot("After Selecting Tab - "+ ItemNameID)
                return "No property matched : " + TabNameID + " not found"
 
       except:
           CommonUtil.ExecutionLog(sModuleName,"Unknown error happened. Returning False and exiting","Info",1) 
           CommonUtil.TakeScreenShot("Error Selecting Tab - "+ ItemNameID)
           return False

def ClickByKeyboard(ItemNameID,*ParentWindowsElement):
    CommonUtil.TakeScreenShot("Before Clicking By Keyboard - "+ ItemNameID)
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In SelectTab fn.","Info",1)
    """
   Parameters: ItemNameID is the name or automation id for the Focus you want
               ParentWindowsElement is list of the parent windows of the Tab you want to Select
   Example: You want to Select on the Media Tab and Media Tab placed on window D, where Window D is the child window of C and window C is child window of B and similarly
            B is child of window A. So you have following data,
            WindowA id is "NotePad"
            WindowB id is "Print"
            WindowC id is "Configure"
            WindowD id is "SetUp"
            Tab id is "TabID"
            Let's call this function
            SelectTab("TabID","NotePad","Print", "Configure","SetUp")
    Return: It will return "Tab Select" string or "<Tab name/id> not found" string if Tab was not found, otherwise it will return False if there is an error
    """

    if ParentWindowsElement != None and ItemNameID != None :
       sModuleName = inspect.stack()[0][3]+" : Program.py"
       CommonUtil.ExecutionLog(sModuleName,"In SelectTheItemFromList fn.","Info",1)
       try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            ItemFocus = False
            ItemElement = MainWin.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.NameProperty,ItemNameID))
            if ItemElement != None:
                ItemElement.SetFocus()
                print ItemElement.Current.HasKeyboardFocus
                #time.sleep(5)
                SendKeys.SendWait(" ")
                #ItemElement.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
                CommonUtil.ExecutionLog(sModuleName,"Control Name id matched. Returning True and exiting","Info",1)
                ItemFocus = True
                CommonUtil.TakeScreenShot("After Clicking By Keyboard - "+ ItemNameID)
                return True
            ItemElement = MainWin.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.AutomationIdProperty,ItemNameID))
            if ItemElement != None:
                ItemElement.SetFocus()
                SendKeys.SendWait(" ")
                CommonUtil.ExecutionLog(sModuleName,"Control Automation id matched. Returning True and exiting","Info",1)
                ItemFocus = True
                CommonUtil.TakeScreenShot("After Clicking By Keyboard - "+ ItemNameID)
                return True
            ItemElement = MainWin.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.ClassNameProperty,ItemNameID))
            if ItemElement != None:
                ItemElement.SetFocus()
                SendKeys.SendWait(" ")
#                ItemElement.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
                CommonUtil.ExecutionLog(sModuleName,"ClassName id matched. Returning True and exiting","Info",1)
                ItemFocus = True
                CommonUtil.TakeScreenShot("After Clicking By Keyboard - "+ ItemNameID)
                return True
            if ItemFocus == False:
                CommonUtil.TakeScreenShot("After Clicking By Keyboard - "+ ItemNameID)
                return "No property matched : " + ItemNameID + " not found"
 
       except Exception, e:
           CommonUtil.ExecutionLog(sModuleName,"Unknown error happened: %s" %e ,"Info",1) 
           CommonUtil.TakeScreenShot("Error Clicking By Keyboard - "+ ItemNameID)
           return False     

def ClickByMouse(ItemNameID,*ParentWindowsElement):
    CommonUtil.TakeScreenShot("Before Clicking By Mouse - "+ ItemNameID)
    sModuleName = inspect.stack()[0][3]+" : Program.py"
    CommonUtil.ExecutionLog(sModuleName,"In SelectTab fn.","Info",1)
    """
   Parameters: ItemNameID is the name or automation id for the Focus you want
               ParentWindowsElement is list of the parent windows of the Tab you want to Select
   Example: You want to Select on the Media Tab and Media Tab placed on window D, where Window D is the child window of C and window C is child window of B and similarly
            B is child of window A. So you have following data,
            WindowA id is "NotePad"
            WindowB id is "Print"
            WindowC id is "Configure"
            WindowD id is "SetUp"
            Tab id is "TabID"
            Let's call this function
            SelectTab("TabID","NotePad","Print", "Configure","SetUp")
    Return: It will return "Tab Select" string or "<Tab name/id> not found" string if Tab was not found, otherwise it will return False if there is an error
    """

    if ParentWindowsElement != None and ItemNameID != None :
       sModuleName = inspect.stack()[0][3]+" : Program.py"
       CommonUtil.ExecutionLog(sModuleName,"In SelectTheItemFromList fn.","Info",1)
       try:
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1
            ItemFocus = False
            ItemElement = MainWin.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.NameProperty,ItemNameID))
            if ItemElement != None:
                ItemElement.SetFocus()
                print ItemElement.Current.HasKeyboardFocus
                #time.sleep(5)
                SendKeys.SendWait(" ")
                #ItemElement.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
                CommonUtil.ExecutionLog(sModuleName,"Control Name id matched. Returning True and exiting","Info",1)
                ItemFocus = True
                CommonUtil.TakeScreenShot("After Clicking By Keyboard - "+ ItemNameID)
                return True
            ItemElement = MainWin.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.AutomationIdProperty,ItemNameID))
            if ItemElement != None:
                x = int(ItemElement.Current.BoundingRectangle.X) + 20
                y = int(ItemElement.Current.BoundingRectangle.Y) + 10
                print x,y
                win32api.SetCursorPos((x,y))
                time.sleep(1)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
                time.sleep(1)
                ItemFocus = True
                CommonUtil.TakeScreenShot("After Clicking By Keyboard - "+ ItemNameID)
                return True
            ItemElement = MainWin.FindFirst(TreeScope.Descendants,PropertyCondition(AutomationElement.ClassNameProperty,ItemNameID))
            if ItemElement != None:
                ItemElement.SetFocus()
                SendKeys.SendWait(" ")
#                ItemElement.GetCurrentPattern(SelectionItemPattern.Pattern).Select()
                CommonUtil.ExecutionLog(sModuleName,"ClassName id matched. Returning True and exiting","Info",1)
                ItemFocus = True
                CommonUtil.TakeScreenShot("After Clicking By Keyboard - "+ ItemNameID)
                return True
            if ItemFocus == False:
                CommonUtil.TakeScreenShot("After Clicking By Keyboard - "+ ItemNameID)
                return "No property matched : " + ItemNameID + " not found"
 
       except Exception, e:
           CommonUtil.ExecutionLog(sModuleName,"Unknown error happened: %s" %e ,"Info",1) 
           CommonUtil.TakeScreenShot("Error Clicking By Keyboard - "+ ItemNameID)
           return False     
            
def WaitTillItemAvailable(ItemNameID = None,*ParentWindowsElement):
    """
   Parameters: ItemNameID is the name or automation id 
               ParentWindowsElement is list of the parent windows of the Tab you want to Select
   Example: This function is to wait for an element to be available. It is not checking Enabled Property
            WindowA id is "NotePad"
            WindowB id is "Print"
            WindowC id is "Configure"
            WindowD id is "SetUp"
            Tab id is "TabID"
            Let's call this function
            WaitTillItemAvailable("TabPictures","MainView","PictureView")
    Return: It will return True once item is available. Or False on error or timeout
    """            
    try:
        if ParentWindowsElement != None and ItemNameID != None :
            arglen = len(ParentWindowsElement)
            count = 1
            ParentWindowList = []
            ParentWindowList.append(ParentWindowsElement[0])
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            starttime = datetime.datetime.now()
            duration = datetime.timedelta(0,0,0)
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                ParentWindowList.append(ParentWindowsElement[count])
                #Wait for the SubWin to be Ready
                MainWin = ReturnChildElement(*ParentWindowList)
                #MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                #iSeconds = 0
                while MainWin == False:
                    time.sleep(1)
                    endtime = datetime.datetime.now()
                    duration = endtime - starttime
                    if duration.seconds > 60:
                        print "Time out on getting Item Status of Item : ",SubWin
                        return False
                    MainWin = ReturnChildElement(*ParentWindowList)
                    #iSeconds = iSeconds + 1
                    print "waiting 1st loop"
                count = count+1            
            ParentWindowList.append(ItemNameID)
            #Item = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
            Item = ReturnChildElement(*ParentWindowList)
            sItemStatus = GetItemStatus(Item)
            #iSeconds = 0 
            starttime = datetime.datetime.now()
            duration = datetime.timedelta(0,0,0)
            while sItemStatus == False:
                endtime = datetime.datetime.now()
                duration = endtime - starttime
                if duration.seconds > 60:
                     print "Time out on getting Item Status of Item : ",ItemNameID
                     return False
                time.sleep(1)
                #Item = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
                Item = ReturnChildElement(*ParentWindowList)
                sItemStatus = GetItemStatus(Item)
                #iSeconds = iSeconds + 1
                print "waiting"
            return True
        else:
            return False
    except Exception,e:
        print "Exception ",e
        return False

def WaitTillItemEnabled(ItemNameID = None,*ParentWindowsElement):            
    """
   Parameters: ItemNameID is the name or automation id 
               ParentWindowsElement is list of the parent windows of the Tab you want to Select
   Example: This function is to wait for an element to be Enabled. 
            WindowA id is "NotePad"
            WindowB id is "Print"
            WindowC id is "Configure"
            WindowD id is "SetUp"
            Tab id is "TabID"
            Let's call this function
            WaitTillItemEnabled("TabPictures","MainView","PictureView")
    Return: It will return True once item is Enabled. Or False on error or timeout
    """            
    
    try:
        if ParentWindowsElement != None and ItemNameID != None :
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1            
            Item = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
            try:
                sItemStatus = Item.Current.IsEnabled
            except Exception,e:
                print "Exception: ",e
                sItemStatus = False
            iSeconds = 0 
            starttime = datetime.datetime.now()
            duration = datetime.timedelta(0,0,0)
            #print "waiting for %s to enable..." %ItemNameID
            while sItemStatus == False:
                endtime = datetime.datetime.now()
                duration = endtime - starttime

                if iSeconds == 60 or duration.seconds > 60:
                     print "Time out on getting Item Status of Item : ",ItemNameID
                     return False
                time.sleep(1)
                Item = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
                try:
                    sItemStatus = Item.Current.IsEnabled
                except Exception,e:
                    print "Exception: ",e
                    sItemStatus = False
                iSeconds = iSeconds + 1
               
            return True
        else:
            return False
    except Exception,e:
        print "Exception ",e
        return False

def WaitTillItemFocusable(ItemNameID = None,*ParentWindowsElement):            
    """
   Parameters: ItemNameID is the name or automation id 
               ParentWindowsElement is list of the parent windows of the Tab you want to Select
   Example: This function is to wait for an element to be Enabled. 
            WindowA id is "NotePad"
            WindowB id is "Print"
            WindowC id is "Configure"
            WindowD id is "SetUp"
            Tab id is "TabID"
            Let's call this function
            WaitTillItemFocusable("TabPictures","MainView","PictureView")
    Return: It will return True once item is Focusable. Or False on error or timeout
    """            
    
    try:
        if ParentWindowsElement != None and ItemNameID != None :
            arglen = len(ParentWindowsElement)
            count = 1
            MainWin = FindTheMainWindow(ParentWindowsElement[0])
            while count < arglen:
                SubWin = ParentWindowsElement[count]
                MainWin = FindTheChildElementOfParentWindow(MainWin,SubWin)
                count = count+1            
            Item = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
            sItemStatus = Item.Current.IsKeyboardFocusable
            iSeconds = 0 
            starttime = datetime.datetime.now()
            duration = datetime.timedelta(0,0,0)

            while sItemStatus == False:
                endtime = datetime.datetime.now()
                duration = endtime - starttime

                if iSeconds == 60 or duration.seconds > 60:
                     print "Time out on getting Item Status of Item : ",ItemNameID
                     return False
                time.sleep(1)
                Item = FindTheChildElementOfParentWindow(MainWin,ItemNameID)
                sItemStatus = Item.Current.IsKeyboardFocusable
                iSeconds = iSeconds + 1
                print "waiting"
            return True
        else:
            return False
    except Exception,e:
        print "Exception ",e
        return False

def main():
   
    pass

if __name__ == "__main__":
    #print ToggleItemStatus("Coffee (3)","MainView","MusicView","MusicCategoryView","Playlists")
    #print SelectItemFromList("Pictures","MainView","PictureView","TabPictures","PicturesOnComputer","UserControl","LibraryFoldersView","Folders")
    #print WaitTillItemEnabled("SplitButtonMain","MainView","SyncView","Sync")
    #print WaitTillItemAvailable("PicturesOnComputer","MainView","PictureView","TabPictures")
    main()
             


