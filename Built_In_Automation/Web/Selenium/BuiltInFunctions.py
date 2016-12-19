
# -*- coding: cp1252 -*-
'''
Created on May 15, 2016

@author: Built_In_Automation Solutionz Inc.
'''

import sys
import os
from operator import or_
from selenium.webdriver.support.expected_conditions import staleness_of
from Utilities.CompareModule import CompareModule
from json.decoder import errmsg
from docutils.nodes import status
from argparse import Action
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


sys.path.append("..")
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import inspect
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
#Ver1.0
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from Utilities import CommonUtil
#from Utilities import CompareModule
from selenium.webdriver.support import expected_conditions as EC
import types

global WebDriver_Wait 
WebDriver_Wait = 20
global WebDriver_Wait_Short
WebDriver_Wait_Short = 10

#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False

global sBrowser
sBrowser = None

def Open_Browser(browser):
    global sBrowser
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        sBrowser.close()
    except:
        True
    try:
        browser = browser.lower()
        if "chrome" in browser:
            sBrowser = webdriver.Chrome()
            sBrowser.implicitly_wait(WebDriver_Wait)
            sBrowser.maximize_window()
            CommonUtil.ExecLog(sModuleInfo, "Started Chrome Browser", 1, local_run)
            return "passed"
        elif browser == 'firefox':
            from sys import platform as _platform
            if _platform == "linux" or _platform == "linux2":
                # linux
                print "linux"
            elif _platform == "darwin":
                # MAC OS X
                print "mac"
            elif _platform == "win32":
                try:
                    import winreg
                except ImportError:
                    import _winreg as winreg
                handle = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe")
                num_values = winreg.QueryInfoKey(handle)[1]
                path = False
                for i in range(num_values):
                    path = (winreg.EnumValue(handle, i))
                    if path != False:
                        firefox_path =  path[1]
                        binary = FirefoxBinary(firefox_path)
                        break
            sBrowser = webdriver.Firefox(firefox_binary=binary)
            sBrowser.implicitly_wait(WebDriver_Wait)
            sBrowser.maximize_window()
            CommonUtil.ExecLog(sModuleInfo, "Started Firefox Browser", 1, local_run)
            return "passed"
        elif "ie" in browser:
            sBrowser = webdriver.Ie()
            sBrowser.implicitly_wait(WebDriver_Wait)
            sBrowser.maximize_window()
            CommonUtil.ExecLog(sModuleInfo, "Started Internet Explorer Browser", 1, local_run)
            return "passed"
        
        elif "safari" in browser:
            os.environ["SELENIUM_SERVER_JAR"] = os.sys.prefix + os.sep + "Scripts" + os.sep + "selenium-server-standalone-2.45.0.jar"
            sBrowser = webdriver.Safari()
            sBrowser.implicitly_wait(WebDriver_Wait)
            sBrowser.maximize_window()
            CommonUtil.ExecLog(sModuleInfo, "Started Safari Browser", 1, local_run)
            return "passed"
    
        else:
            CommonUtil.ExecLog(sModuleInfo, "You did not select a valid browser: %s" % browser, 3,local_run)
            return "failed"
        #time.sleep(3)
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start WebDriver. %s"%Error_Detail, 3,local_run)
        return "failed"

def Go_To_Link(link, page_title=False):
    #this function needs work with validating page title.  We need to check if user entered any title.
    #if not then we don't do the validation
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        sBrowser.get(link)
        sBrowser.implicitly_wait(WebDriver_Wait)
        CommonUtil.ExecLog(sModuleInfo, "Successfully opened your link: %s" % link, 1,local_run)
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
#         if page_title != False:
#             assert page_title in sBrowser.title
        #time.sleep(3)
        return "passed"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception :%s" % e, 3, local_run)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "failed to open your link: %s. Error:%s" %(link, Error_Detail), 3,local_run)
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        return "failed"


'============================= Sequential Action Section Begins=============================='

#Method to get the element step data from the original step_data
def Get_Element_Step_Data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get_Element_Step_Data", 1,local_run)
    try:
        element_step_data=[]
        for each in step_data[0]:
            #if each[1]=="":
#             if (each[1]!="action" or each[1]!="logic"):
#                 element_step_data.append(each)
#             else:
#                 CommonUtil.ExecLog(sModuleInfo, "End of element step data", 2,local_run)
#                 break
            if (each[1]=="action" or each[1]=="conditional action"):
                CommonUtil.ExecLog(sModuleInfo, "Not a part of element step data", 2,local_run)
                continue
            else:
                element_step_data.append(each)
                 
        return element_step_data
    
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not get element step data.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"


#Handles actions for the sequential logic, based on the input from the mentioned function
def Action_Handler(action_step_data, action_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Action_Handler", 1,local_run)
    try:
        if action_name =="click":
            result = Click_Element(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name == "hover":
            result = Hover_Over_Element(action_step_data)
            if result == "failed":
                return "failed"
        elif (action_name == "keystroke_keys" or action_name == "keystroke_chars"):
            result = Keystroke_For_Element(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name=="text":
            result = Enter_Text_In_Text_Box(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name =="wait":
            result = Wait_For_New_Element(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name == "sleep":
            result = Sleep(action_step_data)
            if result == "failed":
                return "failed"
        elif (action_name == "validate full text" or action_name == "validate partial text"):
            result = Validate_Text(action_step_data)
            if result == "failed":
                return "failed"
        elif (action_name == "scroll"):
            result = Scroll(action_step_data)
            if result == "failed":
                return "failed"
        elif (action_name == "step result"):
            result = Step_Result(action_step_data)
            if result == "failed":
                return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information on the data set(s).", 3,local_run)
            return "failed" 
        
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail
        return "failed"


#Method to enter texts in a text box; step data passed on by the user
def Enter_Text_In_Text_Box(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Enter_Text_In_Text_Box", 1,local_run)
    try:
        #If there are no two separate data-sets, or if the first data-set is not between 1 to 3 items, or if the second data-set doesn't have only 1 item                   
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):# or (len(step_data[1]) != 1)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3,local_run)
            return "failed"
        else:
            element_step_data=Get_Element_Step_Data(step_data)
            #element_step_data = step_data[0][0:len(step_data[0])-1:1]
            returned_step_data_list = Validate_Step_Data(element_step_data) 
            #returned_step_data_list = Validate_Step_Data(step_data[0])
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                    for each in step_data[0]:
                        if each[1]=="action":
                            text_value=each[2]
                        else:
                            continue
                    #text_value=step_data[0][len(step_data[0])-1][2]
                    Element.click()
                    Element.clear()
                    Element.send_keys(text_value)
                    Element.click()
                    CommonUtil.TakeScreenShot(sModuleInfo, local_run)
                    CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s"%text_value, 1,local_run)
                    return "passed"
                except Exception, e:
                    element_attributes = Element.get_attribute('outerHTML')
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3,local_run)
                    exc_type, exc_obj, exc_tb = sys.exc_info()        
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not select/click your element.  Error: %s"%(Error_Detail), 3,local_run)
                    return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find your element.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"


#Method to click on element; step data passed on by the user
def Keystroke_For_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Keystroke_For_Element", 1,local_run)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3,local_run)
            return "failed"
        else:
            #element_step_data = step_data[0][0:len(step_data[0])-1:1]
            element_step_data = Get_Element_Step_Data(step_data)
            returned_step_data_list = Validate_Step_Data(element_step_data) 
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                    for each in step_data[0]:
                        if each[1]=="action":
                            if each[0]=="keystroke_keys":
                                keystroke_value=(each[2]).upper()
                                get_keystroke_value = getattr(Keys, keystroke_value)
                                result = Element.send_keys(get_keystroke_value)
                            elif each[0] == "keystroke_chars":
                                keystroke_value=(each[2])
                                result = Element.send_keys(keystroke_value)
                            else:
                                CommonUtil.ExecLog(sModuleInfo, "The correct parameter for the action has not been entered. Please check for errors.", 2,local_run)
                                result = "failed"
                        else:
                            continue
#                     if step_data[0][len(step_data[0])-1][0] == "keystroke_keys":
#                         keystroke_value=(step_data[0][len(step_data[0])-1][2]).upper()
#                         get_keystroke_value = getattr(Keys, keystroke_value)
#                         result = Element.send_keys(get_keystroke_value)
# #                        Keystroke_Key_Mapping(Element, keystroke_value)
#                     elif step_data[0][len(step_data[0])-1][0] == "keystroke_chars":
#                         keystroke_value=(step_data[0][len(step_data[0])-1][2])
#                         result = Element.send_keys(keystroke_value)
#                     else:
#                         CommonUtil.ExecLog(sModuleInfo, "The correct parameter for the action has not been entered. Please check for errors.", 2,local_run)
#                         result = "failed"
                        
                    if (result != "failed"):
                        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
                        CommonUtil.ExecLog(sModuleInfo, "Successfully entered keystroke for the element with given parameters and values", 1,local_run)
                        return "passed"
                    else:
                        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
                        CommonUtil.ExecLog(sModuleInfo, "Could not enter keystroke for the element with given parameters and values", 3,local_run)
                        return "failed"
              
                except Exception, e:
                    element_attributes = Element.get_attribute('outerHTML')
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3,local_run)
                    exc_type, exc_obj, exc_tb = sys.exc_info()        
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not enter keystroke for your element.  Error: %s"%(Error_Detail), 3,local_run)
                    return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not enter keystroke for your element.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"


#Method to click on element; step data passed on by the user
def Click_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Click_Element", 1,local_run)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3,local_run)
            return "failed"
        else:
            #element_step_data = step_data[0][0:len(step_data[0])-1:1]
            element_step_data = Get_Element_Step_Data(step_data)            
            returned_step_data_list = Validate_Step_Data(element_step_data) 
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                    Element.click()
                    CommonUtil.TakeScreenShot(sModuleInfo, local_run)
                    CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element with given parameters and values", 1,local_run)
                    return "passed"
                except Exception, e:
                    element_attributes = Element.get_attribute('outerHTML')
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3,local_run)
                    exc_type, exc_obj, exc_tb = sys.exc_info()        
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not select/click your element.  Error: %s"%(Error_Detail), 3,local_run)
                    return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find/click your element.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"


#Method to hover over element; step data passed on by the user
def Hover_Over_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Hover_Over_Element", 1,local_run)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3,local_run)
            return "failed"
        else:
            #element_step_data = step_data[0][0:len(step_data[0])-1:1]
            element_step_data = Get_Element_Step_Data(step_data)
            returned_step_data_list = Validate_Step_Data(element_step_data) 
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                    hov = ActionChains(sBrowser).move_to_element(Element)
                    hov.perform()
                    CommonUtil.TakeScreenShot(sModuleInfo, local_run)
                    CommonUtil.ExecLog(sModuleInfo, "Successfully hovered over the element with given parameters and values", 1,local_run)
                    return "passed"
                except Exception, e:
                    element_attributes = Element.get_attribute('outerHTML')
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3,local_run)
                    exc_type, exc_obj, exc_tb = sys.exc_info()        
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not select/hover over your element.  Error: %s"%(Error_Detail), 3,local_run)
                    return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find/hover over your element.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"


#Search for element on new page after a particular time-out duration entered by the user through step-data
def Wait_For_New_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Wait_For_New_Page_Element", 1,local_run)
    try:                  
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):# or (len(step_data[1]) != 1)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3,local_run)
            return "failed"
        else:
            #element_step_data = step_data[0][0:len(step_data[0])-1:1]            
            element_step_data = Get_Element_Step_Data(step_data)
            returned_step_data_list = Validate_Step_Data(element_step_data)
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    for each in step_data[0]:
                        if each[1]=="action":
                            timeout_duration = int(each[2])                            
                    
                    start_time = time.time()
                    interval = 1
                    for i in range(timeout_duration):
                        time.sleep(start_time + i*interval - time.time())
                        Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                        if (Element == []):
                            continue
                        else:
                            break
                        
                    if ((Element == []) or (Element == "failed")):
                        return "failed"
                    else:
                        return Element
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()        
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not find the new page element requested.  Error: %s"%(Error_Detail), 3,local_run)
                    return "failed"   
        
    except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()        
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
            CommonUtil.ExecLog(sModuleInfo, "Could not find the new page element requested.  Error: %s"%(Error_Detail), 3,local_run)
            return "failed"


#Validating text from an element given information regarding the expected text
def Validate_Text(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Text", 1, local_run)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3, local_run)
            return "failed"
        else:
            for each in step_data[0]:
                if each[0] == "current_page":
                    try:
                        Element = Get_Element('tag', 'html')
                        break
                    except Exception, e:
                        errMsg = "Could not get element from the current page."
                        Exception_Info(sModuleInfo, errMsg)
                else:
                    element_step_data = Get_Element_Step_Data(step_data)
                    returned_step_data_list = Validate_Step_Data(element_step_data)
                    if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                        return "failed"
                    else:
                        try:
                            Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                            break
                        except Exception, e:
                            errMsg = "Could not get element based on the information provided."
                            Exception_Info(sModuleInfo, errMsg)            
            
#             if step_data[0][0][0] == "current_page":
#                 try:
#                     Element = Get_Element('tag', 'html')
#                 except Exception, e:
#                     errMsg = "Could not get element from the current page."
#                     Exception_Info(sModuleInfo, errMsg)
#             else:
#                 element_step_data = Get_Element_Step_Data(step_data)
#                 # element_step_data = step_data[0][0:len(step_data[0])-1:1]
#                 returned_step_data_list = Validate_Step_Data(element_step_data)
#                 if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
#                     return "failed"
#                 else:
#                     try:
#                         Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
#                     except Exception, e:
#                         errMsg = "Could not get element based on the information provided."
#                         Exception_Info(sModuleInfo, errMsg)
            for each_step_data_item in step_data[0]:
                if each_step_data_item[1]=="action":
                    expected_text_data = each_step_data_item[2]
                    validation_type = each_step_data_item[0]
            #expected_text_data = step_data[0][len(step_data[0]) - 1][2]
            list_of_element_text = Element.text.split('\n')
            visible_list_of_element_text = []
            for each_text_item in list_of_element_text:
                if each_text_item != "":
                    visible_list_of_element_text.append(each_text_item)
            
            #if step_data[0][len(step_data[0])-1][0] == "validate partial text":
            if validation_type == "validate partial text":
                actual_text_data = visible_list_of_element_text
                CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1, local_run)
                CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1, local_run)
                for each_actual_text_data_item in actual_text_data:
                    if expected_text_data in each_actual_text_data_item:
                        CommonUtil.ExecLog(sModuleInfo, "The text has been validated by a partial match.", 1, local_run)
                        return "passed"
                CommonUtil.ExecLog(sModuleInfo, "Unable to validate using partial match.", 3, local_run)
                return "failed"
            #if step_data[0][len(step_data[0])-1][0] == "validate full text":
            if validation_type == "validate full text":
                actual_text_data = visible_list_of_element_text
                CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1, local_run)
                CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1, local_run)
                if (expected_text_data in actual_text_data):
                    CommonUtil.ExecLog(sModuleInfo, "The text has been validated by using complete match.", 1, local_run)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to validate using complete match.", 3, local_run)
                    return "failed"
            
            else:
                CommonUtil.ExecLog(sModuleInfo, "Incorrect validation type. Please check step data", 3, local_run)
                return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not compare text as requested.  Error: %s" % (Error_Detail), 3,
                           local_run)
        return "failed"
    

#Method to sleep for a particular duration
def Sleep(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Sleep", 1, local_run)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3, local_run)
            return "failed"
        else:
            tuple = step_data[0][0]
            seconds = int(tuple[2])
            CommonUtil.ExecLog(sModuleInfo,"Sleeping for %s seconds"%seconds,1,local_run)
            result = time.sleep(seconds)

        return result
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print "%s" % Error_Detail
        return "failed"


#Method to scroll down a page
def Scroll(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Scroll", 1, local_run)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3, local_run)
            return "failed"
        else:
            tuple = step_data[0][0]
            scroll_direction = tuple[2]
            if scroll_direction == 'down':
                CommonUtil.ExecLog(sModuleInfo,"Scrolling down",1,local_run)
                result = sBrowser.execute_script("window.scrollBy(0,750)", "")
                time.sleep(5)
                return "passed"
            elif scroll_direction == 'up':
                CommonUtil.ExecLog(sModuleInfo, "Scrolling up", 1, local_run)
                result = sBrowser.execute_script("window.scrollBy(0,-750)", "")
                time.sleep(5)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Scrolling was not successful", 3, local_run)
                result = "failed"

        return result
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print "%s" % Error_Detail
        return "failed"
    

#Method to return pass or fail for the step outcome
def Step_Result(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Step_Result", 1, local_run)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3, local_run)
            return "failed"
        else:
            step_result = step_data[0][0][2]
            if step_result == 'pass':
                result = "passed"
            elif step_result == 'fail':
                result = "failed"

        return result
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print "%s" % Error_Detail
        return "failed"
    
    
#Performs a series of action or conditional logical action decisions based on user input
def Sequential_Actions(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Sequential_Actions", 1,local_run)
    try:            
        for each in step_data:
            logic_row=[]
            for row in each:
                #finding what to do for each dataset  
                #if len(row)==5 and row[1] != "":     ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement                
                if ((row[1] == "element parameter") or (row[1] == "reference parameter") or (row[1] == "relation type") or (row[1] == "element parameter 1 of 2") or (row[1] == "element parameter 2 of 2")):     ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement                
                    continue
                
                elif row[1]=="action":
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row", 1,local_run)
                    result = Action_Handler([each],row[0])
                    if result == [] or result == "failed":
                        return "failed"
                    
                elif row[1]=="conditional action":
                    CommonUtil.ExecLog(sModuleInfo, "Checking the logical conditional action to be performed in the conditional action row", 1,local_run)
                    logic_decision=""
                    logic_row.append(row)
                    if len(logic_row)==2:
                        #element_step_data = each[0:len(step_data[0])-2:1]
                        element_step_data = Get_Element_Step_Data([each])
                        returned_step_data_list = Validate_Step_Data(element_step_data) 
                        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                            return "failed"
                        else:
                            try:
                                Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                                if Element == 'failed':
                                    logic_decision = "false"
                                else:
                                    logic_decision = "true"                                        
                            except Exception, errMsg:
                                errMsg = "Could not find element in the by the criteria..."
                                Exception_Info(sModuleInfo, errMsg)            
                    else:
                        continue

                    for conditional_steps in logic_row:
                        if logic_decision in conditional_steps:
                            print conditional_steps[2]
                            list_of_steps = conditional_steps[2].split(",")
                            for each_item in list_of_steps:
                                data_set_index = int(each_item) - 1
                                cond_result = Sequential_Actions([step_data[data_set_index]])
                                if cond_result == "failed":
                                    return "failed"
                            return "passed"
                
                else:
                    CommonUtil.ExecLog(sModuleInfo, "The sub-field information is incorrect. Please provide accurate information on the data set(s).", 3,local_run)
                    return "failed"                 
        return "passed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3, local_run)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail
        CommonUtil.ExecLog(sModuleInfo, "Error: %s" % Error_Detail, 3, local_run)
        return "failed"

'===================== ===x=== Sequential Action Section Ends ===x=== ======================'
    

'============================= Validate Table Section Begins =============================='

def Model_Actual_Data(actual_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Model_Actual_Data", 1,local_run)
    try:
        Modeled_Data_Set = []
        row_count = 1
        for each_row in actual_data:
            column_count = 1
            for each_column in each_row:            
                temp_data_model = ["column "+ str(column_count), "row "+str(row_count)]
                temp_data_model.append(each_column.strip())
                #temp_data_model.append("False")
                #temp_data_model.append("False")
                Modeled_Data_Set.append(temp_data_model)
                column_count = column_count +1
            row_count = row_count+1
        return Modeled_Data_Set  
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not model actual data.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"


def Model_Actual_Data_Ignoring_Column(actual_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Model_Actual_Data_Ignoring_Column", 1,local_run)
    try:
        Modeled_Data_Set = []
        row_count = 1
        for each_row in actual_data:
            column_count = 1
            for each_column in each_row:            
                temp_data_model = ["row "+str(row_count)]
                temp_data_model.append(each_column.strip())
                #temp_data_model.append("False")
                #temp_data_model.append("False")
                Modeled_Data_Set.append(temp_data_model)
                column_count = column_count +1
            row_count = row_count+1
        return Modeled_Data_Set  
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not model actual data ignoring column.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"

    
def Model_Actual_Data_Ignoring_Row(actual_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Model_Actual_Data_Ignoring_Row", 1,local_run)
    try:
        Modeled_Data_Set = []
        row_count = 1
        for each_row in actual_data:
            column_count = 1
            for each_column in each_row:            
                temp_data_model = ["column "+str(column_count)]
                temp_data_model.append(each_column.strip())
                #temp_data_model.append("False")
                #temp_data_model.append("False")
                Modeled_Data_Set.append(temp_data_model)
                column_count = column_count +1
            row_count = row_count+1
        return Modeled_Data_Set  
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not model actual data ignoring row.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"


def Model_Expected_Data(expected_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Model_Expected_Data", 1,local_run)
    try:
        Modeled_Data_Set = []
        row_count = 1
        for each_row in expected_data:
            column_count = 1
            temp_data_model = []
            for each_column in each_row:
                if column_count <= 3:            
                    temp_data_model.append(each_column.strip())
                    column_count = column_count +1
                else:
                    break
            Modeled_Data_Set.append(temp_data_model)
            row_count = row_count+1
        return Modeled_Data_Set  
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not model expected data.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"


def Model_Expected_Data_Ignoring_Column(expected_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Model_Expected_Data_Ignoring_Column", 1,local_run)
    try:
        Modeled_Data_Set = []
        row_count = 1
        for each_row in expected_data:
            column_count = 1
            temp_data_model = []
            for each_column in each_row:
                if column_count <= 3:            
                    if column_count == 1:
                        column_count = column_count + 1
                    else:
                        temp_data_model.append(each_column.strip())
                        column_count = column_count +1
                else:
                    break
            Modeled_Data_Set.append(temp_data_model)
            row_count = row_count+1
        return Modeled_Data_Set  
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not model expected data ignoring column.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"


def Model_Expected_Data_Ignoring_Row(expected_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Model_Expected_Data_Ignoring_Row", 1,local_run)
    try:
        Modeled_Data_Set = []
        row_count = 1
        for each_row in expected_data:
            column_count = 1
            temp_data_model = []
            for each_column in each_row:
                if column_count <= 3:            
                    if column_count == 2:
                        column_count = column_count + 1
                    else:
                        temp_data_model.append(each_column.strip())
                        column_count = column_count +1
                else:
                    break
            Modeled_Data_Set.append(temp_data_model)
            row_count = row_count+1
        return Modeled_Data_Set  
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not model expected data ignoring row.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"
    
    
def Model_Expected_Column_Row(expect_data):
    #collect all column name
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Model_Expected_Column_Row", 1,local_run)
    try:
        column_names = []
        row_names = []
        for each in expect_data:
            if each[0] not in column_names:
                column_names.append(each[0])
            if each[1] not in row_names:
                row_names.append(each[1])
        return  column_names, row_names
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not model expected column row.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"
    

##Helper function for validate table - Exact Matching
def Validate_Table_Helper(expected_table_data, actual_table_data, validation_option):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        match_count = 0
        mismatch_count = 0
        matched_list = []
        mismatch_list = []
        
        actual_table_length = len(actual_table_data)
        expected_table_length = len(expected_table_data)
        if (actual_table_length != expected_table_length):
            CommonUtil.ExecLog(sModuleInfo, "Size of the tables do not match!", 2,local_run)  
            
        for each_item in expected_table_data:
            if validation_option == "default":
                ##Do default action
                if each_item in actual_table_data:
                    matched_list.append(each_item)
                    match_count = match_count + 1
                else:
                    mismatch_list.append(each_item)
                    mismatch_count = mismatch_count + 1
            
            ##Need to be implemented!        
            elif validation_option == "case_insensitive":
                CommonUtil.ExecLog(sModuleInfo, "Function yet to be provided. Please wait for the update.", 2,local_run)
            
        #sequential logical flow
        if mismatch_count == 0:
            CommonUtil.ExecLog(sModuleInfo, "There were 0 mismatches! Table has been validated.", 1,local_run)
            CommonUtil.ExecLog(sModuleInfo, "List of matched items: %s"%(matched_list), 1, local_run)
            CommonUtil.ExecLog(sModuleInfo, "List of mismatched items: %s"%(mismatch_list), 1, local_run)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "There were mismatches! Table has invalid data.", 3,local_run)
            CommonUtil.ExecLog(sModuleInfo, "List of matched items: %s"%(matched_list), 3, local_run)
            CommonUtil.ExecLog(sModuleInfo, "List of mismatched items: %s"%(mismatch_list), 3, local_run)
            return "failed"
            
        #print mismatch_count, match_count, mismatch_list, matched_list 
                       
    except Exception, e:
        errMsg = "Error when comparing the exact expected and actual data."
        Exception_Info(sModuleInfo, errMsg)  
                    
                      
#Validate table
def Validate_Table(step_data):    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        #element_step_data = Get_Element_Step_Data(step_data)
        table_validate_index = 0
        for each in step_data[0]:
            if each[1]=="":
                table_validate_index = table_validate_index + 1
            else:
                get_element_last_item = table_validate_index - 1
                print get_element_last_item
                break
          
        if get_element_last_item == 0:
            element_step_data = step_data[0][0]
        else:        
            element_step_data = step_data[0][0:get_element_last_item:1]
        ##print statement to be removed
        print element_step_data
        returned_step_data_list = Validate_Step_Data([element_step_data]) 
        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
            return "failed"
        else:
            try:
                #oCompare = CompareModule()
                expected_table_step_data = (step_data[0][table_validate_index+1:len(step_data[0])-1:1])
                actual_table_dataset = Get_Table_Elements(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                
                try:
                    validation_option=step_data[0][table_validate_index][2]
                    if (step_data[0][table_validate_index][0] == "exact"):
                        modelled_actual_table_step_data = Model_Actual_Data(actual_table_dataset)
                        modelled_expected_table_step_data = Model_Expected_Data(expected_table_step_data)
                        Validate_Table_Helper(modelled_expected_table_step_data, modelled_actual_table_step_data, validation_option)
                    
                    elif step_data[0][table_validate_index][0]== "ignore_row":
                        modelled_actual_table_step_data = Model_Actual_Data_Ignoring_Row(actual_table_dataset)
                        modelled_expected_table_step_data = Model_Expected_Data_Ignoring_Row(expected_table_step_data)
                        Validate_Table_Helper(modelled_expected_table_step_data, modelled_actual_table_step_data, validation_option)
                        
                    elif step_data[0][table_validate_index][0]== "ignore_column":
                        modelled_actual_table_step_data = Model_Actual_Data_Ignoring_Column(actual_table_dataset)
                        modelled_expected_table_step_data = Model_Expected_Data_Ignoring_Column(expected_table_step_data)
                        Validate_Table_Helper(modelled_expected_table_step_data, modelled_actual_table_step_data, validation_option)

                    else:
                        CommonUtil.ExecLog(sModuleInfo, "The information in the table validation index is incorrect. Please provide the appropriate information", 3,local_run)
                        return "failed"                        
                                                        
                    #status = oCompare.compare([expected_table_step_data], [modelled_actual_table_step_data])
                    #print status
                except Exception, e:
                    errMsg = "Error when comparing the expected and actual data."
                    Exception_Info(sModuleInfo, errMsg)
           
            except Exception, e:
                errMsg = "Unable to get table element. Please check if the correct information has been provided."
                Exception_Info(sModuleInfo, errMsg)
         
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find your element.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed" 
     

'===================== ===x=== Validate Table Section Ends ===x=== ======================'    



'============================= Get Elements Section Begins =============================='    

def Get_Element(element_parameter,element_value,reference_parameter=False,reference_value=False,reference_is_parent_or_child=False,get_all_unvalidated_elements=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        All_Elements_Found = []
        if reference_is_parent_or_child == False:
            if ((reference_parameter == False) and (reference_value == False)):
                All_Elements = Get_All_Elements(element_parameter,element_value)     
                if ((All_Elements == []) or (All_Elements == 'failed')):        
                    CommonUtil.ExecLog(sModuleInfo, "Could not find your element by parameter:%s and value:%s..."%(element_parameter,element_value), 3,local_run)
                    return "failed"
                else:
                    All_Elements_Found = All_Elements
            elif (reference_parameter != False and reference_value!= False):
                CommonUtil.ExecLog(sModuleInfo, "Locating element using double matching", 1,local_run)
                All_Elements = Get_Double_Matching_Elements(element_parameter, element_value, reference_parameter, reference_value)
                if ((All_Elements == []) or (All_Elements == "failed")):
                    CommonUtil.ExecLog(sModuleInfo, "Could not find your element by parameter1:%s , value1:%s and parameter2:%s , value2:%s..."%(element_parameter,element_value,reference_parameter,reference_value), 3,local_run)
                    return "failed"
                else:
                    All_Elements_Found = All_Elements
            else:
                CommonUtil.ExecLog(sModuleInfo, "Could not find your element because you are missing at least one parameter", 3,local_run)
                return "failed"
            
        elif reference_is_parent_or_child == "parent":     
            CommonUtil.ExecLog(sModuleInfo, "Locating all parents elements", 1,local_run)   
            all_parent_elements = Get_All_Elements(reference_parameter,reference_value)#,"parent")
            all_matching_elements = []
            for each_parent in all_parent_elements:
                interested_elem = Get_All_Elements(element_parameter,element_value,each_parent) #can there be a problem when we send in each parent, or does this contain both param and value?
                if interested_elem != "failed":
                    for each_matching in interested_elem:
                        all_matching_elements.append(each_matching)
            All_Elements_Found = all_matching_elements

        elif reference_is_parent_or_child == "child":        
            all_parent_elements = Get_All_Elements(element_parameter,element_value)
            all_matching_elements = []
            for each_parent in all_parent_elements:
                interested_elem = Get_All_Elements(reference_parameter,reference_value,each_parent)
                if interested_elem != "failed":
                    all_matching_elements.append(each_parent)
            All_Elements_Found=all_matching_elements
            
        elif reference_is_parent_or_child == "sibling":     
            CommonUtil.ExecLog(sModuleInfo, "Locating the sibling element", 1,local_run)   
            all_sibling_elements = Get_All_Elements(reference_parameter,reference_value)
            for each_sibling in all_sibling_elements:
                all_parent_elements = WebDriverWait(each_sibling, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "..")))
                all_matching_elements = []
                for each_parent in all_parent_elements:
                    interested_elem = Get_All_Elements(element_parameter,element_value,each_parent) #can there be a problem when we send in each parent, or does this contain both param and value?
                    if interested_elem != "failed":
                        for each_matching in interested_elem:
                            all_matching_elements.append(each_matching)
                All_Elements_Found = all_matching_elements
                        
        elif ((reference_is_parent_or_child!="parent") or (reference_is_parent_or_child!="child") or (reference_is_parent_or_child!=False)):
            CommonUtil.ExecLog(sModuleInfo, "Unspecified reference type; please indicate whether parent, child or leave blank", 3,local_run)
            return "failed"
        
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to run based on the current inputs, please check the inputs and re-enter values", 3,local_run)
            return "failed"
        
        #this method returns all the elements found without validation
        if(get_all_unvalidated_elements!=False):
            return All_Elements_Found
        else:
            #can later also pass on the index of the element we want
            result = Element_Validation(All_Elements_Found)#, index)
            return result
    
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find your element.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"       


#Method to get the elements based on type - more methods may be added in the future
#Called by: Get_Element
def Get_All_Elements(parameter,value,parent=False):
    #http://selenium-python.readthedocs.io/locating-elements.html
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if parent == False:
            if parameter == "text":
                All_Elements = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[text()='%s']"%value)))
            elif parameter == "tag":
                All_Elements = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.TAG_NAME, '%s'%(value))))
            elif ((parameter == "link_text") or (parameter == "href")):
                All_Elements = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.LINK_TEXT, '%s'%(value))))
            elif (parameter == "partial_link_text"):
                All_Elements = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, '%s'%(value))))
            elif parameter == "css":
                All_Elements = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '%s'%(value))))    
            else:
                All_Elements = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s']"%(parameter,value))))
        else:
            if parameter == "text":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[text()='%s']" %value)))
            elif parameter == "tag":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.TAG_NAME, '%s'%(value))))
            elif ((parameter == "link_text") or (parameter == "href")):
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.LINK_TEXT, '%s'%(value))))
            elif (parameter == "partial_link_text"):
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, '%s'%(value))))
            elif parameter == "css":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '%s'%(value))))
            else:
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s']"%(parameter,value))))
                
        return All_Elements
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to get the element.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"
 
    
#Use two parameters on the same level to get a specific element
#Called by: Get_Element
def Get_Double_Matching_Elements(param_1, value_1, param_2, value_2):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        #text, tagname,linktext/href,css,partiallinktext
        #All_Elements = []
        ##Text and Tag double matching
        if ((param_1 == "text" and param_2 == "tag") or (param_1 == "tag" and param_2 == "text")):
            CommonUtil.ExecLog(sModuleInfo, "Locating element using double matching, types: text and tag name", 1,local_run)
            try:
                if (param_1 == "text" and param_2 == "tag"):
                    text_value = value_1
                    tag_value = value_2
                elif(param_1 == "tag" and param_2 == "text"): 
                    text_value = value_2
                    tag_value = value_1  
                Text_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[text()='%s']"%text_value)))
                Tag_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.TAG_NAME, '%s'%(tag_value))))
                matched_element = []
                for item in Text_Element:
                    if item in Tag_Element:
                        matched_element.append(item)
                if matched_element != []:
                    return matched_element
                else:
                    return "failed"
            except Exception, e:
                errMsg = "Could not find elements by double matching with types text and tag name"
                Exception_Info(sModuleInfo, errMsg)
        
        ##Text and CSS double matching        
        elif ((param_1 == "text" and param_2 == "css") or (param_1 == "css" and param_2 == "text")):
            CommonUtil.ExecLog(sModuleInfo, "Locating element using double matching, types: text and css selector", 1,local_run)
            try:
                if (param_1 == "text" and param_2 == "css"):
                    text_value = value_1
                    css_value = value_2
                elif(param_1 == "css" and param_2 == "text"): 
                    text_value = value_2
                    css_value = value_1
                Text_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[text()='%s']"%text_value)))
                CSS_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '%s'%(css_value))))
                matched_element=[]
                for item in Text_Element:
                    if item in CSS_Element:
                        matched_element.append(item)
                if matched_element != []:
                    return matched_element
                else:
                    return "failed"
            except Exception, e:
                errMsg = "Could not find elements by double matching with types text and css selector"
                Exception_Info(sModuleInfo, errMsg)
        
        ##Link_Text and CSS double matching                
        elif (((param_1 == "link_text" or param_1 == "href") and param_2 == "css") or (param_1 == "css" and (param_2 == "link_text" or param_2 == "href"))):
            CommonUtil.ExecLog(sModuleInfo, "Locating element using double matching, types: link text and css selector", 1,local_run)
            try:
                if ((param_1 == "link_text" or param_1 == "href") and param_2 == "css"):
                    link_text_value = value_1
                    css_value = value_2
                elif(param_1 == "css" and (param_2 == "link_text" or param_2 == "href")): 
                    link_text_value = value_2
                    css_value = value_1
                Link_Text_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.LINK_TEXT, '%s'%link_text_value)))
                CSS_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '%s'%(css_value))))
                matched_element=[]
                for item in Link_Text_Element:
                    if item in CSS_Element:
                        matched_element.append(item)
                if matched_element != []:
                    return matched_element
                else:
                    return "failed"
            except Exception, e:
                errMsg = "Could not find elements by double matching with types link text and css selector"
                Exception_Info(sModuleInfo, errMsg)

        ##Tag and CSS double matching                
        elif ((param_1 == "tag" and param_2 == "css") or (param_1 == "css" and param_2 == "tag")):
            CommonUtil.ExecLog(sModuleInfo, "Locating element using double matching, types: tag and css selector", 1,local_run)
            try:
                if (param_1 == "tag" and param_2 == "css"):
                    tag_value = value_1
                    css_value = value_2
                elif(param_1 == "css" and param_2 == "tag"): 
                    tag_value = value_2
                    css_value = value_1
                Tag_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.TAG_NAME, '%s'%tag_value)))
                CSS_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '%s'%(css_value))))
                matched_element=[]
                for item in Tag_Element:
                    if item in CSS_Element:
                        matched_element.append(item)
                if matched_element != []:
                    return matched_element
                else:
                    return "failed"
            except Exception, e:
                errMsg = "Could not find elements by double matching with types tag and css selector"
                Exception_Info(sModuleInfo, errMsg)

        ##Link Text and Tag double matching               
        elif (((param_1 == "link_text" or param_1 == "href") and param_2 == "tag") or (param_1 == "tag" and (param_2 == "link_text" or param_2 == "href"))):
            CommonUtil.ExecLog(sModuleInfo, "Locating element using double matching, types: link text and tag", 1,local_run)
            try:
                if ((param_1 == "link_text" or param_1 == "href") and param_2 == "tag"):
                    link_text_value = value_1
                    tag_value = value_2
                elif(param_1 == "tag" and (param_2 == "link_text" or param_2 == "href")): 
                    link_text_value = value_2
                    tag_value = value_1
                Link_Text_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.LINK_TEXT, '%s'%link_text_value)))
                Tag_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.TAG_NAME, '%s'%(tag_value))))
                matched_element=[]
                for item in Link_Text_Element:
                    if item in Tag_Element:
                        matched_element.append(item)
                if matched_element != []:
                    return matched_element
                else:
                    return "failed"
            except Exception, e:
                errMsg = "Could not find elements by double matching with types link text and tag"
                Exception_Info(sModuleInfo, errMsg)

        ##Tag and Partial Link Text double matching                
        elif ((param_1 == "tag" and param_2 == "partial_link_text") or (param_1 == "partial_link_text" and param_2 == "tag")):
            CommonUtil.ExecLog(sModuleInfo, "Locating element using double matching, types: tag and partial link text", 1,local_run)
            try:
                if (param_1 == "tag" and param_2 == "partial_link_text"):
                    tag_value = value_1
                    partial_link_text_value = value_2
                elif(param_1 == "partial_link_text" and param_2 == "tag"): 
                    tag_value = value_2
                    partial_link_text_value = value_1
                Tag_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.TAG_NAME, '%s'%tag_value)))
                Partial_Link_Text_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, '%s'%(partial_link_text_value))))
                matched_element=[]
                for item in Tag_Element:
                    if item in Partial_Link_Text_Element:
                        matched_element.append(item)
                if matched_element != []:
                    return matched_element
                else:
                    return "failed"
            except Exception, e:
                errMsg = "Could not find elements by double matching with types tag and partial link text"
                Exception_Info(sModuleInfo, errMsg)
        
        ##CSS and Partial Link Text double matching                
        elif ((param_1 == "css" and param_2 == "partial_link_text") or (param_1 == "partial_link_text" and param_2 == "css")):
            CommonUtil.ExecLog(sModuleInfo, "Locating element using double matching, types: partial link text and css selector", 1,local_run)
            try:
                if (param_1 == "css" and param_2 == "partial_link_text"):
                    css_value = value_1
                    partial_link_text_value = value_2
                elif(param_1 == "partial_link_text" and param_2 == "css"): 
                    css_value = value_2
                    partial_link_text_value = value_1
                CSS_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '%s'%css_value)))
                Partial_Link_Text_Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, '%s'%(partial_link_text_value))))
                matched_element=[]
                for item in CSS_Element:
                    if item in Partial_Link_Text_Element:
                        matched_element.append(item)
                if matched_element != []:
                    return matched_element
                else:
                    return "failed"
            except Exception, e:
                errMsg = "Could not find elements by double matching with types partial link text and css selector"
                Exception_Info(sModuleInfo, errMsg)
                
        ##Other criteria double matching                        
        else:
            CommonUtil.ExecLog(sModuleInfo, "Locating element using double matching, type unspecific", 1,local_run)
            All_Elements=[]
            All_Elements = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s' and @%s='%s']"%(param_1,value_1,param_2,value_2))))
            if All_Elements != []:
                return All_Elements
            else:
                return "failed"
            
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to get the element.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"


def Get_Table_Elements(table_parameter,table_value, reference_parameter=False,reference_value=False,reference_is_parent_or_child=False,get_all_unvalidated_elements=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        table = Get_Element(table_parameter, table_value,reference_parameter,reference_value,reference_is_parent_or_child)
        all_rows = WebDriverWait(table, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "*")))
        master_text_table = []
        for each_row_obj in all_rows:
            if (each_row_obj.is_displayed()!=False):
                try:
                    row_element = WebDriverWait(each_row_obj, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "*")))
                    temp_row_holder = []
                    for each_column_obj in row_element:
                        temp_row_holder.append(each_column_obj.text)
                except Exception, e:
                    errMsg = "Could not find table row elements"
                    Exception_Info(sModuleInfo, errMsg)                
                master_text_table.append(temp_row_holder)
        print master_text_table
        return master_text_table    

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to get the element.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"


'===================== ===x=== Get Element Section Ends ===x=== ======================'


'============================= Validation Section Begins =============================='

def Element_Validation(All_Elements_Found):#, index):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        #index = int(index)
        return_element = []
        all_visible_elements = []
        all_invisible_elements = []
        if All_Elements_Found == []:        
            CommonUtil.ExecLog(sModuleInfo, "Could not find your element by given parameters and values", 3,local_run)
            return "failed"
        elif len(All_Elements_Found) == 1:
            for each_elem in All_Elements_Found:
                #Case 1: Found only one invisible element - pass with warning 
                if each_elem.is_displayed() == False:
                    return_element.append(each_elem)
                    CommonUtil.ExecLog(sModuleInfo, "Found one invisible element by given parameters and values", 2,local_run)
                #Case 2: Found only one visible element - pass
                elif each_elem.is_displayed() == True:
                    return_element.append(each_elem)
                    CommonUtil.ExecLog(sModuleInfo, "Found one visible element by given parameters and values", 1,local_run)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Could not find element by given parameters and values", 3,local_run)
                    return "failed"
            return return_element[0]

        elif len(All_Elements_Found) > 1:
            CommonUtil.ExecLog(sModuleInfo, "Found more than one element by given parameters and values, validating visible and invisible elements. Total number of elements found: %s"%(len(All_Elements_Found)), 2,local_run)
            for each_elem in All_Elements_Found:
                if each_elem.is_displayed() == True:
                    all_visible_elements.append(each_elem)
                else:
                    all_invisible_elements.append(each_elem)
            #sequential logic - if at least one is_displayed() elements, show that, else allow invisible elements
            if len(all_visible_elements) > 0:
                CommonUtil.ExecLog(sModuleInfo, "Found at least one visible element for given parameters and values, returning the first one or by the index specified", 2,local_run)
                return_element = all_visible_elements
            else:
                CommonUtil.ExecLog(sModuleInfo, "Did not find a visible element, however, invisible elements present", 2,local_run)    
                return_element = all_invisible_elements
            return return_element[0]#[index]

        else:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element by given parameters and values", 3,local_run)
            return "failed" 

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to get the element.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"


#Validation of step data passed on by the user
def Validate_Step_Data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Step_Data", 1,local_run)
    try:    
        if (len(step_data)==1):
            element_parameter = step_data[0][0]
            element_value = step_data[0][2]
            reference_parameter = False
            reference_value = False    
            reference_is_parent_or_child = False
        elif (len(step_data)==2):
            for each in step_data:
                if each[1]=="element parameter 1 of 2":
                    element_parameter = each[0]
                    element_value = each[2]
                elif each[1]=="element parameter 2 of 2":
                    reference_parameter = each[0]
                    reference_value = each[2]
            reference_is_parent_or_child = False
        elif (len(step_data)==3):
            for each in step_data:
                if each[1]=="element parameter":
                    element_parameter = each[0]
                    element_value = each[2]
                elif each[1]=="reference parameter":
                    reference_parameter = each[0]
                    reference_value = each[2]
                elif each[1]=="relation type":
                    reference_is_parent_or_child = each[2]
        else:
            CommonUtil.ExecLog(sModuleInfo, "Data set incorrect. Please provide accurate data set(s) information.", 3,local_run)
            return "failed"
        validated_data = (element_parameter, element_value, reference_parameter, reference_value, reference_is_parent_or_child)
        return validated_data
    except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()        
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
            CommonUtil.ExecLog(sModuleInfo, "Could not find the new page element requested.  Error: %s"%(Error_Detail), 3,local_run)
            return "failed"

'===================== ===x=== Validation Section Ends ===x=== ======================'
    
    
'''
    This section below contains methods similar to Sequential Actions, however
    different parameters are passed on as per user requests.
'''
'============================ Stand-alone Action Section Begins ============================='

def Click_Element_StandAlone(Element):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Click_Element_StandAlone", 1,local_run)
    try:
        if isinstance(Element, (WebElement)) == True:
            try:
                Element.click()
                CommonUtil.TakeScreenShot(sModuleInfo, local_run)
                CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1,local_run)
                return "passed"
            except Exception, e:
                element_attributes = Element.get_attribute('outerHTML')
                CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3,local_run)
                errMsg = "Could not find/click your element"
                Exception_Info(sModuleInfo, errMsg)
    except Exception, e:
        errMsg = "Could not find/click your element"
        Exception_Info(sModuleInfo, errMsg)


def Hover_Over_Element_StandAlone(Element):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Hover_Over_Element_StandAlone", 1,local_run)
    try:
        if isinstance(Element, (WebElement)) == True:
            try:
                hov = ActionChains(sBrowser).move_to_element(Element)
                hov.perform()
                CommonUtil.TakeScreenShot(sModuleInfo, local_run)
                CommonUtil.ExecLog(sModuleInfo, "Successfully hovered over the element", 1,local_run)
                return "passed"
            except Exception, e:
                element_attributes = Element.get_attribute('outerHTML')
                CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3,local_run)
                errMsg = "Could not find/hover over your element"
                Exception_Info(sModuleInfo, errMsg)
    except Exception, e:
        errMsg = "Could not find/hover over your element"
        Exception_Info(sModuleInfo, errMsg)


def Keystroke_Key_StandAlone(KeyToBePressed):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Keystroke_Key_StandAlone", 1,local_run)
    try:
        keystroke_value=KeyToBePressed.upper()
        get_keystroke_value = getattr(Keys, keystroke_value)
        result = ActionChains(sBrowser).send_keys(get_keystroke_value)
        #result.perform()
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Successfully pressed key", 1,local_run)
        return "passed"
    except Exception, e:
        errMsg = "Could not press the desired key"
        Exception_Info(sModuleInfo, errMsg)
        
        
def Keystroke_Characters_StandAlone(KeysToBePressed):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Keystroke_Characters_StandAlone", 1,local_run)
    try:
        result = ActionChains(sBrowser).send_keys(KeysToBePressed)
        #result.perform()
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Successfully pressed characters", 1,local_run)
        return "passed"
    except Exception, e:
        errMsg = "Could not press the desired characters"
        Exception_Info(sModuleInfo, errMsg)


def Scroll_StandAlone(scroll_direction):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Scroll_StandAlone", 1, local_run)
    try:
        if scroll_direction == 'down':
            CommonUtil.ExecLog(sModuleInfo,"Scrolling down",1,local_run)
            result = sBrowser.execute_script("window.scrollBy(0,750)", "")
            time.sleep(5)
        elif scroll_direction == 'up':
            CommonUtil.ExecLog(sModuleInfo, "Scrolling up", 1, local_run)
            result = sBrowser.execute_script("window.scrollBy(0,-750)", "")
            time.sleep(5)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Scrolling was not successful", 3, local_run)
            result = "failed"
        return result
    
    except Exception, e:
        errMsg = "Could not scroll in the desired direction"
        Exception_Info(sModuleInfo, errMsg)
    
'===================== ===x=== Stand-alone Action Section Ends ===x=== ======================'


def Tear_Down():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to tear down the page and close the browser...", 1,local_run)
        sBrowser.quit()
        CommonUtil.ExecLog(sModuleInfo, "Closed the browser successfully.", 1,local_run)
        return "passed"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3, local_run)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail
        CommonUtil.ExecLog(sModuleInfo, "Error: %s" % Error_Detail, 3, local_run)
        return "failed"


def get_driver():
    return sBrowser

def Exception_Info(sModuleInfo, errMsg):
    exc_type, exc_obj, exc_tb = sys.exc_info()        
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
    CommonUtil.ExecLog(sModuleInfo, errMsg + ".  Error: %s"%(Error_Detail), 3,local_run)
    return "failed"
