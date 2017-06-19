# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
'''
Created on May 15, 2016

@author: Built_In_Automation Solutionz Inc.
'''

import sys
import os

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

from Framework.Utilities import CommonUtil

from selenium.webdriver.support import expected_conditions as EC
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list, skipped_tag_list

global WebDriver_Wait
WebDriver_Wait = 20
global WebDriver_Wait_Short
WebDriver_Wait_Short = 10

global selenium_driver
selenium_driver = None

if Shared_Resources.Test_Shared_Variables('selenium_driver'): # Check if driver is already set in shared variables
    selenium_driver = Shared_Resources.Get_Shared_Variables('selenium_driver') # Retreive appium driver

global dependency
dependency = {'Browser':'chrome'}
if Shared_Resources.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables('dependency') # Retreive selenium driver



def Open_Browser(dependency):
    global selenium_driver
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    try:
        browser=dependency['Browser']
    except Exception:
        ErrorMessage =  "Dependency not set for browser. Please set the Apply Filter value to YES."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)
    try:
        selenium_driver.close()
    except:
        True
    try:
        browser = browser.lower()
        if "chrome" in browser:

            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-extensions")
            selenium_driver = webdriver.Chrome(chrome_options = options)
            selenium_driver.implicitly_wait(WebDriver_Wait)
            selenium_driver.maximize_window()
            CommonUtil.ExecLog(sModuleInfo, "Started Chrome Browser", 1)
            Shared_Resources.Set_Shared_Variables('selenium_driver',selenium_driver)
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
            selenium_driver = webdriver.Firefox()
            selenium_driver.implicitly_wait(WebDriver_Wait)
            selenium_driver.maximize_window()
            CommonUtil.ExecLog(sModuleInfo, "Started Firefox Browser", 1)
            Shared_Resources.Set_Shared_Variables('selenium_driver', selenium_driver)
            return "passed"
        elif "ie" in browser:
            selenium_driver = webdriver.Ie()
            selenium_driver.implicitly_wait(WebDriver_Wait)
            selenium_driver.maximize_window()
            CommonUtil.ExecLog(sModuleInfo, "Started Internet Explorer Browser", 1)
            Shared_Resources.Set_Shared_Variables('selenium_driver', selenium_driver)
            return "passed"

        elif "safari" in browser:
            os.environ["SELENIUM_SERVER_JAR"] = os.sys.prefix + os.sep + "Scripts" + os.sep + "selenium-server-standalone-2.45.0.jar"
            selenium_driver = webdriver.Safari()
            selenium_driver.implicitly_wait(WebDriver_Wait)
            selenium_driver.maximize_window()
            CommonUtil.ExecLog(sModuleInfo, "Started Safari Browser", 1)
            Shared_Resources.Set_Shared_Variables('selenium_driver', selenium_driver)
            return "passed"

        else:
            CommonUtil.ExecLog(sModuleInfo, "You did not select a valid browser: %s" % browser, 3)
            return "failed"
        #time.sleep(3)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Open_Browser_Wrapper(step_data):
    #this function needs work with validating page title.  We need to check if user entered any title.
    #if not then we don't do the validation
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        global dependency
        #browser = dependency['Browser']
        #dict = {'Browser':browser}
        return Open_Browser(dependency)
    except Exception:
        ErrorMessage =  "failed to open browser"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)


def Go_To_Link(step_data, page_title=False):
    #this function needs work with validating page title.  We need to check if user entered any title.
    #if not then we don't do the validation
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:

        web_link=step_data[0][2]
        selenium_driver.get(web_link)
        selenium_driver.implicitly_wait(WebDriver_Wait)
        CommonUtil.ExecLog(sModuleInfo, "Successfully opened your link: %s" % web_link, 1)
        CommonUtil.TakeScreenShot(sModuleInfo)
#         if page_title != False:
#             assert page_title in selenium_driver.title
        #time.sleep(3)
        return "passed"
    except Exception:
        ErrorMessage =  "failed to open your link: %s" %(web_link)
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)



'============================= Sequential Action Section Begins=============================='

#Method to get the element step data from the original step_data
def Get_Element_Step_Data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get_Element_Step_Data", 1)
    try:
        element_step_data=[]
        for each in step_data:
            #if each[1]=="":
#             if (each[1]!="action" or each[1]!="logic"):
#                 element_step_data.append(each)
#             else:
#                 CommonUtil.ExecLog(sModuleInfo, "End of element step data", 2)
#                 break
            if (each[1]=="action" or each[1]=="conditional action"):
                CommonUtil.ExecLog(sModuleInfo, "Not a part of element step data", 2)
                continue
            else:
                element_step_data.append(each)

        return element_step_data

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def Initialize_List(data_set):
    ''' Temporary wrapper until we can convert everything to use just data_set and not need the extra [] '''
    return Shared_Resources.Initialize_List([data_set])

#Method to enter texts in a text box; step data passed on by the user
def Enter_Text_In_Text_Box(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Enter_Text_In_Text_Box", 1)
    
    try:
        Element = Get_Element(step_data)
        for each in step_data:
            if each[1]=="action":
                text_value=each[2]
            else:
                continue
        #text_value=step_data[0][len(step_data[0])-1][2]
        Element.click()
        Element.clear()
        Element.send_keys(text_value)
        Element.click()
        CommonUtil.TakeScreenShot(sModuleInfo)
        CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s"%text_value, 1)
        return "passed"
    except Exception:
        element_attributes = Element.get_attribute('outerHTML')
        CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


#Method to click on element; step data passed on by the user
def Keystroke_For_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Keystroke_For_Element", 1)

    try:
        Element = Get_Element(step_data)
        for each in step_data:
            if each[1]=="action":
                if each[0]=="keystroke keys":
                    keystroke_value=(each[2]).upper()
                    get_keystroke_value = getattr(Keys, keystroke_value)
                    result = Element.send_keys(get_keystroke_value)
                elif each[0] == "keystroke chars":
                    keystroke_value=(each[2])
                    result = Element.send_keys(keystroke_value)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "The correct parameter for the action has not been entered. Please check for errors.", 2)
                    result = "failed"
            else:
                continue
        if (result != "failed"):
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Successfully entered keystroke for the element with given parameters and values", 1)
            return "passed"
        else:
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Could not enter keystroke for the element with given parameters and values", 3)
            return "failed"
    except Exception:
        element_attributes = Element.get_attribute('outerHTML')
        CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
        errMsg = "Could not enter keystroke for your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)




#Method to click on element; step data passed on by the user
def Click_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Click_Element", 1)

    try:
        Element = Get_Element(step_data)
        Element.click()
        CommonUtil.TakeScreenShot(sModuleInfo)
        CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element with given parameters and values", 1)
        return "passed"
    except Exception:
        element_attributes = Element.get_attribute('outerHTML')
        CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)



#Method to click and hold on element; step data passed on by the user
def Click_and_Hold_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Click_and_Hold_Element", 1)
    try:
        Element = Get_Element(step_data)
        click_and_hold = ActionChains(selenium_driver).click_and_hold(Element)
        click_and_hold.perform()
        CommonUtil.TakeScreenShot(sModuleInfo)
        CommonUtil.ExecLog(sModuleInfo, "Successfully clicked and held the element with given parameters and values", 1)
        return "passed"
    except Exception:
        element_attributes = Element.get_attribute('outerHTML')
        CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
        errMsg = "Could not click and hold your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)



#Method to right click on element; step data passed on by the user
def Context_Click_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Context_Click_Element", 1)

    try:
        Element = Get_Element(step_data)
        context_click = ActionChains(selenium_driver).context_click(Element)
        context_click.perform()
        CommonUtil.TakeScreenShot(sModuleInfo)
        CommonUtil.ExecLog(sModuleInfo, "Successfully right clicked the element with given parameters and values", 1)
        return "passed"
    except Exception:
        element_attributes = Element.get_attribute('outerHTML')
        CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
        errMsg = "Could not right click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


#Method to double click on element; step data passed on by the user
def Double_Click_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Double_Click_Element", 1)

    try:
        Element = Get_Element(step_data)
        double_click = ActionChains(selenium_driver).double_click(Element)
        double_click.perform()
        CommonUtil.TakeScreenShot(sModuleInfo)
        CommonUtil.ExecLog(sModuleInfo, "Successfully double clicked the element with given parameters and values", 1)
        return "passed"
    except Exception:
        element_attributes = Element.get_attribute('outerHTML')
        CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
        errMsg = "Could not double click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


#Method to move to middle of the element; step data passed on by the user
def Move_To_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Move_To_Element", 1)
    try:
        Element = Get_Element(step_data)
        move = ActionChains(selenium_driver).move_to_element(Element).perform()
        CommonUtil.TakeScreenShot(sModuleInfo)
        CommonUtil.ExecLog(sModuleInfo, "Successfully moved to the middle of the element with given parameters and values", 1)
        return "passed"
    except Exception:
        element_attributes = Element.get_attribute('outerHTML')
        CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
        errMsg = "Could not move to your element your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


#Method to hover over element; step data passed on by the user
def Hover_Over_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Hover_Over_Element", 1)

    try:
        Element = Get_Element(step_data)
        hov = ActionChains(selenium_driver).move_to_element(Element)
        hov.perform()
        CommonUtil.TakeScreenShot(sModuleInfo)
        CommonUtil.ExecLog(sModuleInfo, "Successfully hovered over the element with given parameters and values", 1)
        return "passed"
    except Exception:
        element_attributes = Element.get_attribute('outerHTML')
        CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
        errMsg = "Could not select/hover over your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


#Search for element on new page after a particular time-out duration entered by the user through step-data
def Wait_For_New_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Wait_For_New_Page_Element", 1)

    try:
        for each in step_data:
            if each[1]=="action":
                timeout_duration = int(each[2])

        start_time = time.time()
        interval = 1
        for i in range(timeout_duration):
            time.sleep(time.time() + i*interval - start_time)
            Element = Get_Element(step_data)
            if (Element == []):
                continue
            else:
                break

        if ((Element == []) or (Element == "failed")):
            return "failed"
        else:
            #return Element
            return "passed"
    except Exception:
        element_attributes = Element.get_attribute('outerHTML')
        CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
        errMsg = "Could not find the new page element requested."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


#Validating text from an element given information regarding the expected text
def Compare_Lists(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Lists", 1)
    try:
        element_step_data = Get_Element_Step_Data(step_data)
        if ((element_step_data == []) or (element_step_data == "failed")):
            return "failed"
        else:
            return Shared_Resources.Compare_Lists([step_data])
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Validating text from an element given information regarding the expected text
def Compare_Variables(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Variables", 1)
    try:
        element_step_data = Get_Element_Step_Data(step_data)
        if ((element_step_data == []) or (element_step_data == "failed")):
            return "failed"
        else:
            return Shared_Resources.Compare_Variables([step_data])
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Inserting a field into a list of shared variables
def Insert_Into_List(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Insert_Into_List", 1)
    try:
        if len(step_data) == 1: #will have to test #saving direct input string data
            list_name = ''
            key = ''
            value = ''
            full_input_key_value_name = ''

            for each_step_data_item in step_data:
                if each_step_data_item[1]=="action":
                    full_input_key_value_name = each_step_data_item[2]

            temp_list = full_input_key_value_name.split(',')
            if len(temp_list) == 1:
                CommonUtil.ExecLog(sModuleInfo,
                                   "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                                   3)
                return "failed"
            else:
                list_name = temp_list[0].split(':')[1].strip()
                key = temp_list[1].split(':')[1].strip()
                value = temp_list[2].split(':')[1].strip()

            result = Shared_Resources.Set_List_Shared_Variables(list_name,key, value)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "In list '%s' Value of Variable '%s' could not be saved!!!"%(list_name, key), 3)
                return "failed"
            else:
                Shared_Resources.Show_All_Shared_Variables()
                return "passed"

        elif 1 < len(step_data) <= 5:
            for each in step_data:
                element_step_data = Get_Element_Step_Data(step_data)
                returned_step_data_list = Validate_Step_Data(element_step_data)
                if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                    return "failed"
                else:
                    try:
                        Element = Get_Element(step_data)
                        break

                    except Exception:
                        errMsg = "Could not get element based on the information provided."
                        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

            list_name = ''
            key = ''
            for each_step_data_item in step_data:
                if each_step_data_item[1] == "action":
                    key = each_step_data_item[2]

            # get list name from full input_string

            temp_list = key.split(',')
            if len(temp_list) == 1:
                CommonUtil.ExecLog(sModuleInfo,
                    "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                        3)
                return "failed"
            else:
                list_name = str(temp_list[0]).split(':')[1].strip()
                key = str(temp_list[1]).strip()

            #get text from selenium element
            list_of_element_text = Element.text.split('\n')
            visible_list_of_element_text = ""
            for each_text_item in list_of_element_text:
                if each_text_item != "":
                    visible_list_of_element_text+=each_text_item


            #save text in the list of shared variables in CommonUtil
            result = Shared_Resources.Set_List_Shared_Variables(list_name,key, visible_list_of_element_text)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "In list '%s' Value of Variable '%s' could not be saved!!!"%(list_name, key), 3)
                return "failed"
            else:
                Shared_Resources.Show_All_Shared_Variables()
                return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Validating text from an element given information regarding the expected text
def Save_Text(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Save_Text", 1)
    try:
        if ((1 < len(step_data) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return "failed"
        else:
            for each in step_data:
                element_step_data = Get_Element_Step_Data(step_data)
                returned_step_data_list = Validate_Step_Data(element_step_data)
                if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                    return "failed"
                else:
                    try:
                        Element = Get_Element(step_data)
                        break

                    except Exception:
                        errMsg = "Could not get element based on the information provided."
                        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

            for each_step_data_item in step_data:
                if each_step_data_item[1]=="action":
                    variable_name = each_step_data_item[2]

            list_of_element_text = Element.text.split('\n')
            visible_list_of_element_text = ""
            for each_text_item in list_of_element_text:
                if each_text_item != "":
                    visible_list_of_element_text+=each_text_item

            result = Shared_Resources.Set_Shared_Variables(variable_name, visible_list_of_element_text)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Value of Variable '%s' could not be saved!!!"%variable_name, 3)
                return "failed"
            else:
                Shared_Resources.Show_All_Shared_Variables()
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Validating text from an element given information regarding the expected text
def Validate_Text(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Text", 1)
    try:
        if ((1 < len(step_data) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return "failed"
        else:
            for each in step_data:
                if each[0] == "current_page":
                    try:
                        Element = Get_Element('tag', 'html')
                        break
                    except Exception:
                        return CommonUtil.Exception_Handler(sys.exc_info(),None,"Could not get element from the current page.")
                else:
                    element_step_data = Get_Element_Step_Data(step_data)
                    returned_step_data_list = Validate_Step_Data(element_step_data)
                    if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                        return "failed"
                    else:
                        try:
                            Element = Get_Element(step_data)
                            break

                        except Exception:
                            errMsg = "Could not get element based on the information provided."
                            return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

#             if step_data[0][0][0] == "current_page":
#                 try:
#                     Element = Get_Element('tag', 'html')
#                 except Exception:
#                     errMsg = "Could not get element from the current page."
#                     return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
#             else:
#                 element_step_data = Get_Element_Step_Data(step_data)
#                 # element_step_data = step_data[0][0:len(step_data[0])-1:1]
#                 returned_step_data_list = Validate_Step_Data(element_step_data)
#                 if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
#                     return "failed"
#                 else:
#                     try:
#                         Element = Get_Element(step_data)
#                     except Exception:
#                         errMsg = "Could not get element based on the information provided."
#                         return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
            for each_step_data_item in step_data:
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
                CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1)
                CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1)
                for each_actual_text_data_item in actual_text_data:
                    if expected_text_data in each_actual_text_data_item:
                        CommonUtil.ExecLog(sModuleInfo, "The text has been validated by a partial match.", 1)
                        return "passed"
                CommonUtil.ExecLog(sModuleInfo, "Unable to validate using partial match.", 3)
                return "failed"
            #if step_data[0][len(step_data[0])-1][0] == "validate full text":
            if validation_type == "validate full text":
                actual_text_data = visible_list_of_element_text
                CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1)
                CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1)
                if (expected_text_data in actual_text_data):
                    CommonUtil.ExecLog(sModuleInfo, "The text has been validated by using complete match.", 1)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to validate using complete match.", 3)
                    return "failed"

            else:
                CommonUtil.ExecLog(sModuleInfo, "Incorrect validation type. Please check step data", 3)
                return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Method to sleep for a particular duration
def Sleep(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Sleep", 1)
    try:
        #update this function with filter
        tuple = step_data[0]
        seconds = int(tuple[2])
        CommonUtil.ExecLog(sModuleInfo,"Sleeping for %s seconds"%seconds,1)
        time.sleep(seconds)
        return "passed"
        #return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Method to scroll down a page
def Scroll(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Scroll", 1)
    try:
        if ((1 < len(step_data) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
            return "failed"
        else:
            tuple = step_data[0]
            scroll_direction = tuple[2]
            if scroll_direction == 'down':
                CommonUtil.ExecLog(sModuleInfo,"Scrolling down",1)
                result = selenium_driver.execute_script("window.scrollBy(0,750)", "")
                time.sleep(5)
                return "passed"
            elif scroll_direction == 'up':
                CommonUtil.ExecLog(sModuleInfo, "Scrolling up", 1)
                result = selenium_driver.execute_script("window.scrollBy(0,-750)", "")
                time.sleep(5)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Scrolling was not successful", 3)
                result = "failed"
                return result

        #return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Method to return pass or fail for the step outcome
def Step_Result(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Step_Result", 1)
    try:
        if ((1 < len(step_data) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            result = "failed"
        else:
            step_result = step_data[0][2]
            if step_result == 'pass':
                result = "passed"
            elif step_result == 'skip':
                result = 'skipped'
            elif step_result == 'fail':
                result = "failed"

        return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def Select_Deselect(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Step_Result", 1)
 
    try:
        Element = Get_Element(step_data)
        for each in step_data:
            if each[1]=="action":
                if each[0]=="deselect all":
                    CommonUtil.ExecLog(sModuleInfo, "Deselect all elements", 1)
                    result = Select(Element).deselect_all()
                    #result = selected_Element.deselect_all()
                    return "passed"
                elif each[0] == "deselect by visible text":
                    CommonUtil.ExecLog(sModuleInfo, "Deselect by visible text", 1)
                    visible_text=each[2]
                    selected_Element = Select(Element)
                    result = selected_Element.deselect_by_visible_text(visible_text)
                    return "passed"
                elif each[0] == "deselect by value":
                    CommonUtil.ExecLog(sModuleInfo, "Deselect by value", 1)
                    value=each[2]
                    selected_Element = Select(Element)
                    result = selected_Element.deselect_by_value(value)
                    return "passed"
                elif each[0] == "deselect by index":
                    CommonUtil.ExecLog(sModuleInfo, "Deselect by index", 1)
                    index=int(each[2])
                    selected_Element = Select(Element)
                    result = selected_Element.deselect_by_index(index)
                    return "passed"
                elif each[0] == "select by index":
                    CommonUtil.ExecLog(sModuleInfo, "Select by index", 1)
                    index=each[2]
                    selected_Element = Select(Element)
                    result = selected_Element.select_by_index(index)
                    return "passed"
                elif each[0] == "select by value":
                    CommonUtil.ExecLog(sModuleInfo, "Select by value", 1)
                    value=each[2]
                    selected_Element = Select(Element)
                    result = selected_Element.select_by_value(value)
                    return "passed"
                elif each[0] == "select by visible text":
                    CommonUtil.ExecLog(sModuleInfo, "Select by visible text", 1)
                    visible_text=each[2]
                    selected_Element = Select(Element)
                    result = selected_Element.select_by_visible_text(visible_text)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "The correct parameter for the action has not been entered. Please check for errors.", 2)
                    result = "failed"

            else:
                continue

    except Exception:
        element_attributes = Element.get_attribute('outerHTML')
        CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
        errMsg = "Could not select/hover over your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)




'===================== ===x=== Sequential Action Section Ends ===x=== ======================'


'============================= Validate Table Section Begins =============================='

'===================== ===x=== Validate Table Section Ends ===x=== ======================'



'============================= Get Elements Section Begins =============================='

def _construct_query (step_data_set): 
    '''
    first find out if in our dataset user is using css or xpath.  If they are using css or xpath, they cannot use any 
    other feature such as child parameter or multiple element parameter to locate the element
    '''
    collect_all_attribute = [x[0] for x in step_data_set]
    # find out if ref exists.  If it exists, it will set the value to True else False
    child_ref_exits = any("child parameter" in s for s in step_data_set)
    parent_ref_exits = any("parent parameter" in s for s in step_data_set)
    #remove index.  We need to remove index, because they dont get used to construct the xpath pat
    remove_index_child = filter(lambda x: 'index' not in x[0], step_data_set)  
    remove_index_element = filter(lambda x: 'index' not in x[0], step_data_set) 
    remove_index_parent = filter(lambda x: 'index' not in x[0], step_data_set) 
    #get all child, element, and parent only
    child_parameter_list = filter(lambda x: 'child parameter' in x[1], remove_index_child) 
    element_parameter_list = filter(lambda x: 'element parameter' in x[1], remove_index_element) 
    parent_parameter_list = filter(lambda x: 'parent parameter' in x[1], remove_index_parent) 
    
    if "css" in collect_all_attribute and "xpath" not in collect_all_attribute:
        # return the raw css command with css as type
        return ((filter(lambda x: 'css' in x[0], step_data_set) [0][2]), "css")
    elif "xpath" in collect_all_attribute and "css" not in collect_all_attribute:
        # return the raw xpath command with xpath as type
        return ((filter(lambda x: 'xpath' in x[0], step_data_set) [0][2]), "xpath" )       
    elif child_ref_exits == False and parent_ref_exits == False :
        '''  If  there are no child or parent as reference, then we construct the xpath differently'''
        #first we collect all rows with element parameter only 
        xpath_element_list = (_construct_xpath_list(element_parameter_list))
        return (_construct_xpath_string_from_list(xpath_element_list), "xpath")
    elif child_ref_exits == True and parent_ref_exits == False:
        '''  If  There is child but making sure no parent'''
        xpath_child_list =  _construct_xpath_list(child_parameter_list,True)
        child_xpath_string = _construct_xpath_string_from_list(xpath_child_list) 
        xpath_element_list = _construct_xpath_list(element_parameter_list)
        #Take the first element, remove ]; add the 'and'; add back the ]; put the modified back into list. 
        xpath_element_list[1] = (xpath_element_list[1]).replace("]","") + ' and ' + child_xpath_string + "]"
        return (_construct_xpath_string_from_list(xpath_element_list), "xpath")
    elif child_ref_exits == False and parent_ref_exits == True:
        '''  If  There is parent but making sure no child'''
        xpath_parent_list =  _construct_xpath_list(parent_parameter_list)
        parent_xpath_string = _construct_xpath_string_from_list(xpath_parent_list) 
        xpath_element_list = _construct_xpath_list(element_parameter_list,True)
        #Take the first element, remove ]; add the 'and'; add back the ]; put the modified back into list. 
        xpath_element_list[1] = (xpath_element_list[1]).replace("]","") + ' and ' + parent_xpath_string + "]"
        return (_construct_xpath_string_from_list(xpath_element_list), "xpath")
    else:
        return False, False

def _construct_xpath_list(parameter_list,add_dot=False):
    '''
    This function constructs the raw data from step data into a xpath friendly format but in a list
    '''
    element_main_body_list = []
    #these are special cases where we cannot treat their attribute as any other attribute such as id, class and so on...  
    excluded_attribute = ["*text", "text", "tag", "css", "index","xpath"]
    for each_data_row in parameter_list:
        attribute = (each_data_row[0].strip()).lower()
        attribute_value = each_data_row[2]
        if attribute == "text":
            text_value = '[text()="%s"]'%attribute_value
            element_main_body_list.append(text_value)
        elif attribute == "*text":
            text_value = '[contains(text(),"%s")]'%attribute_value    
            element_main_body_list.append(text_value)
        elif attribute not in excluded_attribute and '*' not in attribute:
            other_value = '[@%s="%s"]'%(attribute,attribute_value)
            element_main_body_list.append(other_value)
        elif attribute not in excluded_attribute and '*' in attribute:
            other_value = '[contains(@%s,"%s")]'%(attribute.split('*')[1],attribute_value)
            element_main_body_list.append(other_value)
    #we do the tag on its own  
    #tag_was_given = any("tag" in s for s in parameter_list)
    if "tag" in [x[0] for x in parameter_list]:
        tag_item = "//"+ filter(lambda x: 'tag' in x, parameter_list)[0][2]
    else:
        tag_item = "//*"
    if add_dot != False:
        tag_item = '.'+tag_item
    element_main_body_list.append(tag_item)
    #We need to reverse the list so that tag comes at the begining 
    return list(reversed(element_main_body_list))

def _construct_xpath_string_from_list(xpath_list): 
    '''
    in this function, we simply take the list and construct the actual query in string
    '''
    xpath_string_format = ""
    for each in xpath_list:
        xpath_string_format = xpath_string_format+each   
    return  xpath_string_format
    
def _get_xpath_or_css_element(element_query,css_xpath, index_number=False):  
    '''
    Here, we actually execute the query based on css/xpath and then analyze if there are multiple.
    If we find multiple we give warning and send the first one we found.
    We also consider if user sent index.  If they did, we send them the index they provided
    '''
    all_matching_elements = []
    if css_xpath == "xpath":
        all_matching_elements = selenium_driver.find_elements_by_xpath(element_query)
    elif css_xpath == "css":
        all_matching_elements = selenium_driver.find_elements_by_css_selector(element_query)
    
    if len(all_matching_elements)== 0:
        return False
    elif len(all_matching_elements)==1 and index_number == False:
        return all_matching_elements[0]
    elif len(all_matching_elements)>1 and index_number == False:
        print "Warning: found more than one element with given condition.  Returning first item.  Consider providing index"
        return all_matching_elements[0]  
    elif len(all_matching_elements)==1 and abs(index_number) >0:
        print "Warning: we only found single element but you provided an index number greater than 0.  Returning the only element"  
        return all_matching_elements[0]
    elif len(all_matching_elements) >1 and index_number != False:
        if (len(all_matching_elements)-1) < abs(index_number):
            print "Warning: your index exceed the the number of elements found. Returning the last element instead"
            return all_matching_elements[(len(all_matching_elements)-1)]
        else:
            return all_matching_elements[index_number]    
    else:
        return "Failed"   
     
def _locate_index_number(step_data_set):
    '''
    Check if index exists, if it does, get the index value.
    if we cannot convert index to integer, set it to False
    '''
    if "index" in [x[0] for x in step_data_set]:
        index_number = filter(lambda x: 'index' in x[0], step_data_set) [0][2] 
        try:
            index_number = int (index_number)
        except:
            index_number =False
    else:
        index_number =False
    return index_number

def Get_Element(step_data_set):
    '''
    This funciton will return "Failed" if something went wrong, else it will always return a single element
    '''
    index_number = _locate_index_number(step_data_set)
    element_query, query_type = _construct_query (step_data_set)
    if element_query == False:
        return "Failed"
    elif query_type == "xpath" and element_query != False:
        return _get_xpath_or_css_element(element_query,"xpath",index_number)
    elif query_type == "css" and element_query != False:
        return _get_xpath_or_css_element(element_query,"css",index_number)
        
   





'===================== ===x=== Get Element Section Ends ===x=== ======================'


'============================= Validation Section Begins =============================='


'===================== ===x=== Validation Section Ends ===x=== ======================'


'''
    This section below contains methods similar to Sequential Actions, however
    different parameters are passed on as per user requests.
'''
'============================ Stand-alone Action Section Begins ============================='

def Click_Element_StandAlone(Element):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Click_Element_StandAlone", 1)
    try:
        if isinstance(Element, (WebElement)) == True:
            try:
                Element.click()
                CommonUtil.TakeScreenShot(sModuleInfo)
                CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1)
                return "passed"
            except Exception:
                element_attributes = Element.get_attribute('outerHTML')
                CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
                errMsg = "Could not find/click your element"
                return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    except Exception:
        errMsg = "Could not find/click your element"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Hover_Over_Element_StandAlone(Element):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Hover_Over_Element_StandAlone", 1)
    try:
        if isinstance(Element, (WebElement)) == True:
            try:
                hov = ActionChains(selenium_driver).move_to_element(Element)
                hov.perform()
                CommonUtil.TakeScreenShot(sModuleInfo)
                CommonUtil.ExecLog(sModuleInfo, "Successfully hovered over the element", 1)
                return "passed"
            except Exception:
                element_attributes = Element.get_attribute('outerHTML')
                CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
                errMsg = "Could not find/hover over your element"
                return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    except Exception:
        errMsg = "Could not find/hover over your element"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Keystroke_Key_StandAlone(KeyToBePressed):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Keystroke_Key_StandAlone", 1)
    try:
        keystroke_value=KeyToBePressed.upper()
        get_keystroke_value = getattr(Keys, keystroke_value)
        result = ActionChains(selenium_driver).send_keys(get_keystroke_value)
        #result.perform()
        CommonUtil.TakeScreenShot(sModuleInfo)
        CommonUtil.ExecLog(sModuleInfo, "Successfully pressed key", 1)
        return "passed"
    except Exception:
        errMsg = "Could not press the desired key"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Keystroke_Characters_StandAlone(KeysToBePressed):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Keystroke_Characters_StandAlone", 1)
    try:
        result = ActionChains(selenium_driver).send_keys(KeysToBePressed)
        #result.perform()
        CommonUtil.TakeScreenShot(sModuleInfo)
        CommonUtil.ExecLog(sModuleInfo, "Successfully pressed characters", 1)
        return "passed"
    except Exception:
        errMsg = "Could not press the desired characters"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Scroll_StandAlone(scroll_direction):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Scroll_StandAlone", 1)
    try:
        if scroll_direction == 'down':
            CommonUtil.ExecLog(sModuleInfo,"Scrolling down",1)
            result = selenium_driver.execute_script("window.scrollBy(0,750)", "")
            time.sleep(5)
        elif scroll_direction == 'up':
            CommonUtil.ExecLog(sModuleInfo, "Scrolling up", 1)
            result = selenium_driver.execute_script("window.scrollBy(0,-750)", "")
            time.sleep(5)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Scrolling was not successful", 3)
            result = "failed"
        return result

    except Exception:
        errMsg = "Could not scroll in the desired direction"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'===================== ===x=== Stand-alone Action Section Ends ===x=== ======================'


def Tear_Down_Selenium(step_data = [[[]]]):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to tear down the page and close the browser...", 1)
        selenium_driver.quit()
        CommonUtil.ExecLog(sModuleInfo, "Closed the browser successfully.", 1)
        return "passed"
    except Exception:
        errMsg = "Unable to tear down selenium browsers"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


##@Riz and @Sreejoy: More work is needed here. Please investigate further.
def Get_Plain_Text_Element(element_parameter, element_value, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get_Plain_Text_Element", 1)
    try:
        if parent==False:
            all_elements_with_text = selenium_driver.find_elements_by_xpath(".//*")
        else:
            all_elements_with_text = parent.find_elements_by_xpath(".//*")

        #Sequential logical flow
        if element_parameter == "plain_text":
            index = 0
            full_list = []
            for each in all_elements_with_text:
                text_to_print = None
                try:
                    text_to_print = each.text
                except:
                    False
                if text_to_print == element_value:
                    full_list.append(each)
                    break
                index = index +1
            return_element = full_list[len(full_list) - 1]

        elif element_parameter == "partial_plain_text":
            index = 0
            full_list = []
            for each in all_elements_with_text:
                text_to_print = None
                try:
                    text_to_print = each.text
                except:
                    False
                if element_value in text_to_print:
                    full_list.append(each)
                    break
                index = index +1
            return_element = full_list[len(full_list) - 1]

        else:
            CommonUtil.ExecLog(sModuleInfo, "Incorrect element parameter entered, please check the value.", 3)
            return "failed"

        return return_element

    except Exception:
        errMsg = "Could not get the element by plain text search"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_driver():
    return selenium_driver
