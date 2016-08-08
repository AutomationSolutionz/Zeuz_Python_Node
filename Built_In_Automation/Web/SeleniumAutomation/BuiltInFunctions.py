
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


global WebDriver_Wait 
WebDriver_Wait = 20
global WebDriver_Wait_Short
WebDriver_Wait_Short = 10

#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
local_run = True
#local_run = False

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
        time.sleep(5)
        Click_Element_By_ID(button_to_click)
        #time.sleep(2)
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


def Get_Element_OLD(parameter,value,index_number=0,parent=False):
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
                if (WebDriverWait(All_Elements[index_number], WebDriver_Wait).until(lambda driver : All_Elements[index_number].is_displayed())) == True:
                    Element = All_Elements[index_number]
                    CommonUtil.ExecLog(sModuleInfo, "Using the *first* element to set the text", 2,local_run)
            else:
                CommonUtil.ExecLog(sModuleInfo, "Found one element and will set the text on that", 1, local_run)
                if (WebDriverWait(All_Elements[index_number], WebDriver_Wait).until(lambda driver : All_Elements[index_number].is_displayed())) == True:
                    Element = All_Elements[index_number]
        CommonUtil.ExecLog(sModuleInfo, "We found the element of your given parameter and value", 1,local_run)
        return Element
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to get the element.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"



def Locate_Element_By_Tag(tag_text,parent=False,multiple=False):

    try:
        if isinstance(parent,bool) == True:
            if not multiple:
                e=sBrowser.find_element_by_tag_name(tag_text)
            else:
                e=sBrowser.find_elements_by_tag_name(tag_text)
        else:
            if not multiple:
                e=parent.find_element_by_tag_name(tag_text)
            else:
                e=parent.find_elements_by_tag_name(tag_text)
        return e
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))


'============================================'

#Method to enter texts in a text box; step data passed on by the user
def Enter_Text_In_Text_Box(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Inside Enter Text In Text Box function", 1,local_run)
    try:
        #If there are no two separate data-sets, or if the first data-set is not between 1 to 3 items, or if the second data-set doesn't have only 1 item                   
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):# or (len(step_data[1]) != 1)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3,local_run)
            return "failed"
        else:
            element_step_data = step_data[0][0:len(step_data[0])-1:1]
            returned_step_data_list = Validate_Step_Data(element_step_data) 
            #returned_step_data_list = Validate_Step_Data(step_data[0])
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                    text_value=step_data[0][len(step_data[0])-1][2]
                    #text_value = step[1][0][2]
                    #text_value=step_data[1][0][1]
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
def Click_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Inside Click Element function", 1,local_run)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3,local_run)
            return "failed"
        else:
            element_step_data = step_data[0][0:len(step_data[0])-1:1]
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
    CommonUtil.ExecLog(sModuleInfo, "Inside Hover Over Element function", 1,local_run)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3,local_run)
            return "failed"
        else:
            element_step_data = step_data[0][0:len(step_data[0])-1:1]
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
            element_step_data = step_data[0][0:len(step_data[0])-1:1]            
            returned_step_data_list = Validate_Step_Data(element_step_data)
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    timeout_duration = int(step_data[0][len(step_data[0])-1][2])
                    start_time = time.time()
                    interval = 1
                    for i in range(timeout_duration):
                        time.sleep(start_time + i*interval - time.time())
                        Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                 
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


#Handles actions for the sequential logic, based on the input from the mentioned function
def Action_Handler(action_step_data, action_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if action_name =="click":
            result = Click_Element(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name == "hover":
            result = Hover_Over_Element(action_step_data)
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
        else:
            CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information on the data set(s).", 3,local_run)
            return "failed" 
        
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail
        return "failed"  
    

#Performs a series of action or logical decisions based on user input
def Sequential_Actions(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:            
        for each in step_data:
            logic_row=[]
            for row in each:
                #finding what to do for each dataset  
                if len(row)==5:                    
                    if row[1]=="action":
                        result = Action_Handler([each],row[0])
                        if result == [] or result == "failed":
                            return "failed"
                        
                    elif row[1]=="logic":
                        logic_decision=""
                        logic_row.append(row)
                        if len(logic_row)==2:
                            element_step_data = each[0:len(step_data[0])-2:1]
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
                                    Sequential_Actions([step_data[data_set_index]])
                                return "passed"
                    
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "The sub-field information is incorrect. Please provide accurate information on the data set(s).", 3,local_run)
                        return "failed"                 
        return "passed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail
        return "failed"

#Validation of step data passed on by the user
def Validate_Step_Data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Step_Data", 1,local_run)
    try:    
        if (len(step_data)==1):
            element_parameter = step_data[0][0]
            element_value = step_data[0][1]
            reference_parameter = False
            reference_value = False    
            reference_is_parent_or_child = False
        elif (len(step_data)==2):
            element_parameter = step_data[0][0]
            element_value = step_data[0][1]
            reference_parameter = step_data[1][0]
            reference_value = step_data[1][1]
            reference_is_parent_or_child = False
        elif (len(step_data)==3):
            element_parameter = step_data[0][0]
            element_value = step_data[0][1]
            reference_parameter = step_data[1][0]
            reference_value = step_data[1][1]    
            reference_is_parent_or_child = step_data[2][1]
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


#Validating text from an element given information regarding the expected text
def Validate_Text(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Text_Data", 1,local_run)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3,local_run)
            return "failed"
        else:
#             oCompare = CompareModule()
            expected_text_data = step_data[0][1][2]
            if step_data[0][0][0] == "current_page":
                try:
                    Element = Get_Element('tag', 'html')
                except Exception, e:
                    errMsg = "Could not get element from the current page."
                    Exception_Info(sModuleInfo, errMsg)
            else:
                element_step_data = step_data[0][0:len(step_data[0])-1:1]
                returned_step_data_list = Validate_Step_Data(element_step_data) 
                if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                    return "failed"
                else:
                    try:
                        Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])    
                    except Exception, e:
                        errMsg = "Could not get element based on the information provided."
                        Exception_Info(sModuleInfo, errMsg)
                
            list_of_element_text = Element.text.split('\n')
            visible_list_of_element_text = []
            for each_text_item in list_of_element_text:
                if each_text_item != "":
                    visible_list_of_element_text.append(each_text_item)                
            if step_data[0][1][1] == "partial match":
                actual_text_data = visible_list_of_element_text
                CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1,local_run)
                CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1,local_run)
                if (expected_text_data in each_item for each_item in actual_text_data):
                    CommonUtil.ExecLog(sModuleInfo, "The text has been validated by a partial match.", 1,local_run)
                    return "passed"
                else: 
                    CommonUtil.ExecLog(sModuleInfo, "Unable to validate using partial match.", 3,local_run)
                    return "failed"
            if step_data[0][1][1] == "full match":
                actual_text_data = visible_list_of_element_text
                CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1,local_run)
                CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1,local_run)
                if (expected_text_data in actual_text_data):
                    CommonUtil.ExecLog(sModuleInfo, "The text has been validated by using complete match.", 1,local_run)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to validate using complete match.", 3,local_run) 
                    return "failed" 
                                        
#             expected_text_dataset = [step_data[0]]#[0][1]##[[('Starting from*', 'car1', '$101,770', False, False)]]#[step_data[0]]#[0][1]
#             returned_expected_step_data = Validate_Step_Data(step_data[1])
#             if ((returned_expected_step_data == []) or (returned_expected_step_data == "failed")):
#                 return "failed"
#             else:
#                 try:
#                     Element = Get_Element(returned_expected_step_data[0], returned_expected_step_data[1], returned_expected_step_data[2], returned_expected_step_data[3], returned_expected_step_data[4])
#                     #need to verify
#                     actual_text_dataset = [[('text', Element.text, False, False)]]#[[(u'Starting from*', 'car1', u'$101,770', False, False)]]
#                     
#                 except Exception, e:
#                     exc_type, exc_obj, exc_tb = sys.exc_info()        
#                     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#                     Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
#                     CommonUtil.ExecLog(sModuleInfo, "Could not compare text as requested.  Error: %s"%(Error_Detail), 3,local_run)
#                     return "failed"    
#             status=oCompare.compare(expected_text_dataset,actual_text_dataset)
#             print status
            
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not compare text as requested.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"
    

##Things to do:
#1) get the table data from the element step data
#2) for expected data, for each row in the step_data: 
#   if subfield row is not empty and length of step-data = 5:
#   for each_row in the step_data, append item in a list for a particular row 
#[[u'1486543', u'353513070625277', u'N/A', u'SAMSUNG-SM-G928A', u'MCHOWDHURY', u'2016-08-04 08:55:56 EDT', u'2016-08-04 09:09:18 EDT', u'Diagnostics - Quick', u'FAIL', u'DEFAULT', u'N/A'], [u'1486542', u'353513070625277', u'N/A', u'SAMSUNG-SM-G928A', u'MCHOWDHURY', u'2016-08-04 08:44:02 EDT', u'2016-08-04 08:55:47 EDT', u'Diagnostics - Quick', u'FAIL', u'DEFAULT', u'N/A'], [u'1486538', u'353926064400988', u'N/A', u'PRIMO_RX2', u'FD363A605A2B11E', u'2016-08-04 06:14:36 EDT', u'2016-08-04 06:16:48 EDT', u'Diagnostics - Appium', u'INCOMPLETE', u'N/A', u'N/A'], [u'1486533', u'353926064400988', u'N/A', u'PRIMO_RX2', u'E2B1EC4E5A2A11E', u'2016-08-04 06:06:31 EDT', u'2016-08-04 06:09:29 EDT', u'Diagnostics - Appium', u'INCOMPLETE', u'N/A', u'N/A'], [u'1486528', u'353926064400988', u'N/A', u'PRIMO_RX2', u'46EB791E5A2611E', u'2016-08-04 05:33:29 EDT', u'2016-08-04 05:52:23 EDT', u'Diagnostics - Appium', u'INCOMPLETE', u'N/A', u'N/A'], [u'1486518', u'353926064400988', u'N/A', u'PRIMO_RX2', u'SREEJOY', u'2016-08-04 02:20:49 EDT', u'2016-08-04 02:22:05 EDT', u'Diagnostics - Appium', u'PASS', u'PASS', u'N/A'], [u'1486517', u'353926064400988', u'N/A', u'PRIMO_RX2', u'SREEJOY', u'2016-08-04 02:19:08 EDT', u'2016-08-04 02:20:38 EDT', u'Diagnostics - Appium', u'FAIL', u'GENERAL TEST FAILURE', u'N/A'], [u'1486510', u'911338900054604', u'N/A', u'GENERIC', u'TEST', u'2016-08-04 02:11:25 EDT', u'2016-08-04 02:12:08 EDT', u'Diagnostics - Unsupported Device', u'CRASH', u'N/A', u'N/A'], [u'1486509', u'911338900054604', u'N/A', u'GENERIC', u'TEST', u'2016-08-04 02:10:25 EDT', u'2016-08-04 02:11:00 EDT', u'Diagnostics - Appium', u'CRASH', u'N/A', u'N/A'], [u'1486505', u'911338900054604', u'N/A', u'GENERIC', u'TEST', u'2016-08-04 02:04:14 EDT', u'2016-08-04 02:04:53 EDT', u'Diagnostics - Appium', u'CRASH', u'N/A', u'N/A'], [u'1486496', u'911338900054604', u'N/A', u'GENERIC', u'SREEJOY', u'2016-08-04 01:58:20 EDT', u'2016-08-04 01:58:26 EDT', u'Diagnostics - Appium', u'INCOMPLETE', u'N/A', u'N/A'], [u'1486492', u'911338900054604', u'N/A', u'GENERIC', u'SREEJOY', u'2016-08-04 01:55:53 EDT', u'2016-08-04 01:56:24 EDT', u'Diagnostics - Appium', u'CRASH', u'N/A', u'N/A'], [u'1486488', u'911338900054604', u'N/A', u'GENERIC', u'SREEJOY', u'2016-08-04 01:45:27 EDT', u'2016-08-04 01:46:14 EDT', u'Diagnostics - Appium', u'CRASH', u'N/A', u'N/A'], [u'1486486', u'357185067524411', u'N/A', u'XPLORER ZV', u'SREEJOY', u'2016-08-04 01:44:31 EDT', u'2016-08-04 01:45:16 EDT', u'Diagnostics - Appium', u'CRASH', u'N/A', u'N/A'], [u'1486477', u'N/A', u'N/A', u'UNDEFINED', u'NIKOLAS', u'2016-08-03 18:44:41 EDT', u'2016-08-03 18:44:41 EDT', u'N/A', u'CRASH', u'N/A', u'N/A'], [u'1486474', u'N/A', u'N/A', u'UNDEFINED', u'ASCI', u'2014-06-19 15:29:57 EDT', u'2014-06-19 15:29:57 EDT', u'Quick Suite - Android 1.20.1 - iOS 1.10.7', u'FAIL', u'FAIL', u'N/A'], [u'1486472', u'355451060315922', u'N/A', u'GENERIC', u'JAVIER', u'2016-08-03 18:17:10 EDT', u'2016-08-03 18:18:07 EDT', u'Diagnostics - Generic Device', u'CRASH', u'N/A', u'N/A'], [u'1486470', u'355451060315922', u'N/A', u'GENERIC', u'JAVIER', u'2016-08-03 18:12:18 EDT', u'2016-08-03 18:12:59 EDT', u'Diagnostics - Generic Device', u'CRASH', u'N/A', u'N/A'], [u'1486468', u'N/A', u'N/A', u'UNDEFINED', u'SANDEEP', u'2014-08-08 06:13:38 EDT', u'2014-08-08 06:13:38 EDT', u'All Tests - Android 1.21.4 + iOS 1.11.2', u'FAIL', u'FAIL', u'N/A'], [u'1486466', u'N/A', u'N/A', u'UNDEFINED', u'DSE22', u'2016-08-03 17:59:13 EDT', u'2016-08-03 18:05:37 EDT', u'Software Flash', u'RETRY', u'N/A', u'N/A']]        row_number = 1
def Validate_Table(step_data):    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        new_data_group_index = 0
        for each in step_data[0]:
            if len(each) != 5:
                new_data_group_index = new_data_group_index + 1
            else:
                get_element_last_item = new_data_group_index - 1
                print get_element_last_item
                break
                
        element_step_data = step_data[0][0:get_element_last_item:1]
        ##print statement to be removed
        print element_step_data
        returned_step_data_list = Validate_Step_Data(element_step_data) 
        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
            return "failed"
        else:
            try:
                actual_table_data = Get_Table_Elements('tag', 'tbody')
                #actual_table_dataset = Get_Table_Elements(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
            except Exception, e:
                errMsg = "Unable to get table element. Please check if the correct information has been provided."
                Exception_Info(sModuleInfo, errMsg)
        
#         all_rows = WebDriverWait(table, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "*")))
#         master_text_table = []
#         for each_row_obj in all_rows:
#             if (each_row_obj.is_displayed()!=False):
#                 try:
#                     row_element = WebDriverWait(each_row_obj, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "*")))
#                     temp_row_holder = []
#                     for each_column_obj in row_element:
#                         temp_row_holder.append(each_column_obj.text)
#                 except Exception, e:
#                     errMsg = "Could not find table row elements"
#                     Exception_Info(sModuleInfo, errMsg)                
#                 master_text_table.append(temp_row_holder)
        expected_table_step_data = step_data[0][new_data_group_index:len(step_data[0])-1:1]
        print expected_table_step_data
        
        expected_table_data_set = []
        row_index = 1
        for each_row in expected_table_step_data:
            if each[1] == row_index:
                temp_row_holder = []
                for each_item_in_row in each_row:
                    temp_row_holder.append(step_data[0][row_index][2])
            row_index= row_index + 1  
        
        print "a"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find your element.  Error: %s"%(Error_Detail), 3,local_run)
        return "failed" 
    
    
    
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

def Exception_Info(sModuleInfo, errMsg):
    exc_type, exc_obj, exc_tb = sys.exc_info()        
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
    CommonUtil.ExecLog(sModuleInfo, errMsg + ".  Error: %s"%(Error_Detail), 3,local_run)
    return "failed"

# b = Get_Element(element_parameter, element_value, reference_parameter, reference_value, reference_is_parent_or_child, get_all_unvalidated_elements)
# if b == "failed":
#     b = 'false'
# else:
#     b = 'true'
#     
#     
# a = [('true','logic',"34,3,3"),('false','logic',"5,2,5")]
# b = 'true'
# #b = 'false'
# for each_row in a:
#     if b in each_row:
#         print each_row[2]