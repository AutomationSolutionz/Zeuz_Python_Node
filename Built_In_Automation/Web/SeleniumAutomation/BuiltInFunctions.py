
# -*- coding: cp1252 -*-
'''
Created on May 15, 2016

@author: Built_In_Automation Solutionz Inc.
'''

import sys
import os


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
from selenium.webdriver.support import expected_conditions as EC

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
            sBrowser = webdriver.Firefox()
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
    #if not then we dont do the validation
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
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "failed to open your link: %s. Error:%s" %(link, Error_Detail), 3,local_run)
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        return "failed"

def Login_To_Application(user_name,password,user_element,password_element,button_to_click,logged_name=False):
    #logged name needs update
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        #If you are not sure what the ID are for the field... then you need to customize this a little...
        CommonUtil.ExecLog(sModuleInfo, "Entering logging credential by ID...", 1, local_run)
        Set_Text_Field_Value_By_ID(user_element,user_name)
        Set_Text_Field_Value_By_ID(password_element,password)
        Click_Element_By_ID(button_to_click)
        time.sleep(2)
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        #if user selected to validate login name then we shall do that...  
        if logged_name == True:
            element_login = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_element_located((By.XPATH, "//*[@title='View profile']")))
            if (WebDriverWait(element_login, WebDriver_Wait).until(lambda driver : element_login.text)) == logged_name:
                CommonUtil.ExecLog(sModuleInfo, "Verified that logged in as: %s"%logged_name, 1,local_run)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Log in failed for user: %s"%logged_name, 3,local_run)
                return "failed"
        #if user didn't want to validate login name, and we didn't run into any exception, then we return pass
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to login.  %s"%Error_Detail, 3,local_run)
        return "failed"
    
def Click_By_Parameter_And_Value(parameter,value, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Locating your element...", 1, local_run)
        if isinstance(parent, (bool)) == True:
            Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_element_located((By.XPATH, "//*[@%s='%s']"%(parameter,value))))
        else:
            Element = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_element_located((By.XPATH, "//*[@%s='%s']"%(parameter,value))))
        CommonUtil.ExecLog(sModuleInfo, "Found element and clicking..", 1, local_run)
        Element.click()
        CommonUtil.ExecLog(sModuleInfo, "Successfully clicked by %s and %s"%(parameter,value), 1,local_run)
        return "passed" 
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate element to click.  Parameter: %s & Value: %s  Error: %s"%(parameter,value,Error_Detail), 3,local_run)
        return "failed"
    
def Click_Element_By_Name(_name,parent=False):
    '''
    Use this function only if you are sure that there wont be any conflicting Name.
    If possible use Click_Element_By_ID
    
    '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        #Find all elements containing the name
        CommonUtil.ExecLog(sModuleInfo, "Trying to find element by name: %s"%_name, 1,local_run)
        if isinstance(parent, (bool)) == True:
            allElements = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[text()='%s']"%_name)))        
        else:
            allElements = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[text()='%s']"%_name)))
        if allElements == []:        
            CommonUtil.ExecLog(sModuleInfo, "Could not find your element by name: %s"%_name, 3,local_run)
            return "failed"
        else:
            if len(allElements) > 1:
                CommonUtil.ExecLog(sModuleInfo, "Found more than one element and will use the first one.  ** if fails, try providing parent element or try by ID** ", 2, local_run)
            for each in allElements:
                if (WebDriverWait(each, WebDriver_Wait).until(lambda driver : each.is_displayed())) == True:
                    Element = each
                    CommonUtil.ExecLog(sModuleInfo, "Found your element by name: %s.  Using the first element found to click"%_name, 1,local_run)
                    break   
        #Now we simply click it
        Element.click()
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Successfully clicked your element: %s"%_name, 1,local_run)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to expand menu: %s.   Error: %s"%(_name,Error_Detail), 3,local_run)
        return "failed"    
 
def Click_Element_By_ID(_id,parent=False):    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Trying to find element by ID: %s"%_id, 1,local_run)
        try:
            Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_element_located((By.ID, _id)))
        except:
            CommonUtil.ExecLog(sModuleInfo, "Could not find your element by name or ID: %s"%_id, 3,local_run)
            return "failed"
        #Now we simply click it
        Element.click()
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Successfully clicked your element: %s"%_id, 1,local_run)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click element by ID: %s.  Error: %s"%(_id,Error_Detail), 3,local_run)
        return "failed"    

def Set_Text_Field_Value_By_ID(_id,value):
    
    '''
    
    should be deleted
    '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Trying to find element by id: %s"%_id, 1,local_run)
        try:
            Element = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_element_located((By.ID, _id)))
        except:
            CommonUtil.ExecLog(sModuleInfo, "Could not find your element by ID: %s"%_id, 3,local_run)
            return "failed"  
        #Now we simply click it
        Element.click()
        Element.clear()
        Element.send_keys(value)
        Element.click()
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text with ID: %s"%_id, 1,local_run)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set value for your ID: %s.  Error: %s"%(_id, Error_Detail), 3,local_run)
        return "failed"    

def Set_Text_Field_By_Parameter_And_Value(parameter,value,text,parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Locating your element by parameter:%s and value:%s..."%(parameter,value), 1, local_run)
        if isinstance(parent, (bool)) == True:
            All_Elements = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s']"%(parameter,value))))
        else:
            All_Elements = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s']"%(parameter,value))))
        if All_Elements == []:        
            CommonUtil.ExecLog(sModuleInfo, "Could not find your element by parameter:%s and value:%s..."%(parameter,value), 3,local_run)
            return "failed"
        else:
            if len(All_Elements) > 1:
                CommonUtil.ExecLog(sModuleInfo, "Found more than one element and will use the first one.  ** if fails, try providing parent element** ", 2, local_run)
                CommonUtil.TakeScreenShot(sModuleInfo, local_run)
                if (WebDriverWait(All_Elements[0], WebDriver_Wait).until(lambda driver : All_Elements[0].is_displayed())) == True:
                    Element = All_Elements[0]
                    CommonUtil.ExecLog(sModuleInfo, "Using the *first* element to set the text", 2,local_run)
            else:
                CommonUtil.ExecLog(sModuleInfo, "Found one element and will set the text on that", 1, local_run)
                if (WebDriverWait(All_Elements[0], WebDriver_Wait).until(lambda driver : All_Elements[0].is_displayed())) == True:
                    Element = All_Elements[0]
        Element.click()
        Element.clear()
        Element.send_keys(text)
        Element.click()
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)

        CommonUtil.ExecLog(sModuleInfo, "Successfully clicked by %s and %s"%(parameter,value), 1,local_run)
        return "passed" 
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate element to click.  Parameter: %s & Value: %s  Error: %s"%(parameter,value,Error_Detail), 3,local_run)
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        return "failed"


'''
need improvmenets.. we need to do this by using all elements concept

'''


def Get_Parent_Element(parameter,value,parent = False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Locating your element by parameter:%s and value:%s..." % (parameter, value), 1,
                           local_run)
        if isinstance(parent, (bool)) == True:
            All_Elements = WebDriverWait(sBrowser, WebDriver_Wait).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s']" % (parameter, value))))
        else:
            All_Elements = WebDriverWait(parent, WebDriver_Wait).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s']" % (parameter, value))))
        if All_Elements == []:
            CommonUtil.ExecLog(sModuleInfo,
                               "Could not find your element by parameter:%s and value:%s..." % (parameter, value), 3,
                               local_run)
            return "failed"
        else:
            if len(All_Elements) > 1:
                CommonUtil.ExecLog(sModuleInfo,
                                   "Found more than one element and will use the first one.  ** if fails, try providing parent element** ",
                                   2, local_run)
                CommonUtil.TakeScreenShot(sModuleInfo, local_run)
                if (WebDriverWait(All_Elements[0], WebDriver_Wait).until(
                        lambda driver: All_Elements[0].is_displayed())) == True:
                    Element = All_Elements[0]
                    CommonUtil.ExecLog(sModuleInfo, "Using the *first* element to find its parent", 2, local_run)
            else:
                CommonUtil.ExecLog(sModuleInfo, "Found one element and will find parent of that", 1, local_run)
                if (WebDriverWait(All_Elements[0], WebDriver_Wait).until(
                        lambda driver: All_Elements[0].is_displayed())) == True:
                    Element = All_Elements[0]
        Parent_Element=Element.find_element_by_xpath('..')
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)

        CommonUtil.ExecLog(sModuleInfo, "Successfully found the parent element by %s and %s" % (parameter, value), 1, local_run)
        return Parent_Element
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to find parent element.  Parameter: %s & Value: %s  Error: %s" % (
        parameter, value, Error_Detail), 3, local_run)
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        return "failed"


'''
    Need to write code.  Should return a list of child elements.
'''


def Get_Child_Elements(parameter,value,parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Locating your element by parameter:%s and value:%s..." % (parameter, value), 1,
                           local_run)
        if isinstance(parent, (bool)) == True:
            All_Elements = WebDriverWait(sBrowser, WebDriver_Wait).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s']" % (parameter, value))))
        else:
            All_Elements = WebDriverWait(parent, WebDriver_Wait).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s']" % (parameter, value))))
        if All_Elements == []:
            CommonUtil.ExecLog(sModuleInfo,
                               "Could not find your element by parameter:%s and value:%s..." % (parameter, value), 3,
                               local_run)
            return "failed"
        else:
            if len(All_Elements) > 1:
                CommonUtil.ExecLog(sModuleInfo,
                                   "Found more than one element and will use the first one.  ** if fails, try providing parent element** ",
                                   2, local_run)
                CommonUtil.TakeScreenShot(sModuleInfo, local_run)
                if (WebDriverWait(All_Elements[0], WebDriver_Wait).until(
                        lambda driver: All_Elements[0].is_displayed())) == True:
                    Element = All_Elements[0]
                    CommonUtil.ExecLog(sModuleInfo, "Using the *first* element to find its all childs", 2, local_run)
            else:
                CommonUtil.ExecLog(sModuleInfo, "Found one element and will find all childs of that", 1, local_run)
                if (WebDriverWait(All_Elements[0], WebDriver_Wait).until(
                        lambda driver: All_Elements[0].is_displayed())) == True:
                    Element = All_Elements[0]
        Child_Elements = Element.find_elements_by_xpath(".//*")
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)

        CommonUtil.ExecLog(sModuleInfo, "Successfully found all the child elements by %s and %s" % (parameter, value), 1,
                           local_run)
        return Child_Elements
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to find parent element.  Parameter: %s & Value: %s  Error: %s" % (
            parameter, value, Error_Detail), 3, local_run)
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        return "failed"

  

def Get_Element(parameter,value,parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if isinstance(parent, (bool)) == True:
            All_Elements = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s']"%(parameter,value))))
        else:
            All_Elements = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s']"%(parameter,value))))
        if All_Elements == []:        
            CommonUtil.ExecLog(sModuleInfo, "Could not find your element by parameter:%s and value:%s..."%(parameter,value), 3,local_run)
            return "failed"
        else:
            if len(All_Elements) > 1:
                CommonUtil.ExecLog(sModuleInfo, "Found more than one element and will use the first one.  ** if fails, try providing parent element** ", 2, local_run)
                CommonUtil.TakeScreenShot(sModuleInfo, local_run)
                if (WebDriverWait(All_Elements[0], WebDriver_Wait).until(lambda driver : All_Elements[0].is_displayed())) == True:
                    Element = All_Elements[0]
                    CommonUtil.ExecLog(sModuleInfo, "Using the *first* element to set the text", 2,local_run)
            else:
                CommonUtil.ExecLog(sModuleInfo, "Found one element and will set the text on that", 1, local_run)
                if (WebDriverWait(All_Elements[0], WebDriver_Wait).until(lambda driver : All_Elements[0].is_displayed())) == True:
                    Element = All_Elements[0]
        CommonUtil.ExecLog(sModuleInfo, "We found the element of your given parameter and value", 1,local_run)
        return Element
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to get the parent element.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"


'''
need coding...

The purpose of this function is to minimize finding duplicate element in the easiest way..
a lot of time we get duplicate elements with matching condition.
If we can actually provide some child/parent information, then the permutation becomes a
lot more harder to duplicate.

user will provide the element's parameter and value and then provide either the child or parent
and then function will return an element.

make sure you use Get_Element(parameter,value,parent=False) as reference ..
we always want to make sure that we are looking for all elements.....

if a user gives a child as reference .. then you need to find all the children of the given parent
and look for the interested item...


'''


def Get_Element_With_Reference(element_parameter,element_value,reference_parameter,reference_value,child_parent):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Locating your element by parameter:%s and value:%s..." % (element_parameter, element_value), 1,
                           local_run)

        All_Elements = WebDriverWait(sBrowser, WebDriver_Wait).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s']" % (element_parameter, element_value))))

        if All_Elements == []:
            CommonUtil.ExecLog(sModuleInfo,
                               "Could not find your element by parameter:%s and value:%s..." % (element_parameter, element_value), 3,
                               local_run)
            return "failed"
        else:
            if len(All_Elements) > 1:
                CommonUtil.ExecLog(sModuleInfo,
                                   "Found more than one element and will use the first one.  ** if fails, try providing parent element** ",
                                   2, local_run)
                CommonUtil.TakeScreenShot(sModuleInfo, local_run)

                child_parent=child_parent.lower()

                if child_parent == 'child':
                    valid_parent_element = []
                    child_element = Get_Element(reference_parameter, reference_value)
                    for possible_parent_element in All_Elements:
                        parent = Get_Parent_Element(reference_parameter,reference_value)
                        if possible_parent_element == parent:
                            valid_parent_element.append(possible_parent_element)

                    if valid_parent_element == []:
                        CommonUtil.ExecLog(sModuleInfo,
                                   "Could not find your element by parameter:%s and value:%s with referenece child parameter:%s and reference child value:%s..." % (
                                   element_parameter, element_value,reference_parameter,reference_value), 3,
                                   local_run)
                    else:
                        if len(valid_parent_element) > 1:
                            CommonUtil.ExecLog(sModuleInfo,
                                   "Found more than one element and return the first one.  ** if fails, try providing parent element** ",
                                   2, local_run)
                            if (WebDriverWait(valid_parent_element[0], WebDriver_Wait).until(
                                    lambda driver: valid_parent_element[0].is_displayed())) == True:
                                Element = valid_parent_element[0]
                                return Element
                        else:
                            CommonUtil.ExecLog(sModuleInfo, "Found one element and will return that", 1, local_run)
                            if (WebDriverWait(valid_parent_element[0], WebDriver_Wait).until(
                                lambda driver: valid_parent_element[0].is_displayed())) == True:
                                Element = valid_parent_element[0]
                                return Element


                elif child_parent == 'parent':
                    valid_child_element = []
                    parent_element = Get_Element(reference_parameter, reference_value)
                    for possible_child_element in All_Elements:
                        all_child = Get_Child_Elements(reference_parameter, reference_value)
                        if possible_child_element in all_child:
                            valid_child_element.append(possible_child_element)

                    if valid_child_element == []:
                        CommonUtil.ExecLog(sModuleInfo,
                                           "Could not find your element by parameter:%s and value:%s with referenece parent parameter:%s and reference parent value:%s..." % (
                                               element_parameter, element_value, reference_parameter, reference_value), 3,
                                           local_run)
                    else:
                        if len(valid_child_element) > 1:
                            CommonUtil.ExecLog(sModuleInfo,
                                               "Found more than one element and return the first one.  ** if fails, try providing parent element** ",
                                               2, local_run)
                            if (WebDriverWait(valid_child_element[0], WebDriver_Wait).until(
                                    lambda driver: valid_child_element[0].is_displayed())) == True:
                                Element = valid_child_element[0]
                                return Element
                        else:
                            CommonUtil.ExecLog(sModuleInfo, "Found one element and will return that", 1, local_run)
                            if (WebDriverWait(valid_child_element[0], WebDriver_Wait).until(
                                    lambda driver: valid_child_element[0].is_displayed())) == True:
                                Element = valid_child_element[0]
                                return Element

            else:
                CommonUtil.ExecLog(sModuleInfo, "Found one element and will return that", 1, local_run)
                if (WebDriverWait(All_Elements[0], WebDriver_Wait).until(
                        lambda driver: All_Elements[0].is_displayed())) == True:
                    Element = All_Elements[0]
                    return Element

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find your element by parameter:%s and value:%s with referenece parent parameter:%s and reference parent value:%s... Error: %s" % (
                                               element_parameter, element_value, reference_parameter, reference_value,Error_Detail), 3, local_run)
        CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        return "failed"
    
 
    
def Tear_Down():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to tear down the page and close the browser...", 1,local_run)
        sBrowser.quit()
        CommonUtil.ExecLog(sModuleInfo, "Closed the browser successfully.", 1,local_run)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail
        return "failed"


def get_driver():
    return sBrowser

