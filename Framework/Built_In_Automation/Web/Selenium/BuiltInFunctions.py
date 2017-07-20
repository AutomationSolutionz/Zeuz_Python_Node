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
from Framework.Built_In_Automation.Shared_Resources import LocateElement
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
dependency = None
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
    ''' Temporary wrapper for open_browser() until that function can be updated to use only data_set '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        global dependency
        # Get the dependency again in case it was missed
        if Shared_Resources.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
            dependency = Shared_Resources.Get_Shared_Variables('dependency') # Retreive selenium driver
    

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



def Initialize_List(data_set):
    ''' Temporary wrapper until we can convert everything to use just data_set and not need the extra [] '''
    return Shared_Resources.Initialize_List([data_set])

#Method to enter texts in a text box; step data passed on by the user
def Enter_Text_In_Text_Box(step_data):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        Element = LocateElement.Get_Element(step_data,selenium_driver)
        if Element != "failed":
            for each in step_data:
                if each[1]=="action":
                    text_value=each[2]
                    break
                else:
                    continue
            Element.click()
            Element.clear()
            Element.send_keys(text_value)
            Element.click()
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s"%text_value, 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed"
    except Exception:
        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def Keystroke_For_Element(data_set):
    ''' Send a key stroke or string to an element or wherever the cursor is located '''
    # Keystroke Keys: Any key. Eg: Tab, Escape, etc
    # Keystroke Chars: Any string. Eg: The quick brown...
    # If no element parameter is provided, it will enter the keystroke wherever the cursor is located
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    # Parse the data set
    try:
        stype = '' # keys/chars
        get_element = False # Use element
        key_count = 1 # Default number of button presses
        for row in data_set:
            if row[1] == "action":
                if row[0] == "keystroke keys": # Keypress
                    stype = 'keys'
                    keystroke_value = row[2]
                    if ',' in keystroke_value: # If user supplied a number of presses
                        keystroke_value.replace(' ', '')
                        keystroke_value, key_count = keystroke_value.split(',') # Save keypress and count
                        key_count = int(key_count)
                elif row[0] == "keystroke chars": # String
                    stype = 'chars'
                    keystroke_value = row[2]
            elif row[1] == 'element parameter':
                get_element = True

        if stype == '':
            CommonUtil.ExecLog(sModuleInfo, "Field contains incorrect data", 3)
            return 'failed'
        
        
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(),None, "Error parsing data set")
        

    # Get the element, or if none provided, create action chains for keystroke insertion without an element
    if get_element == True:
        Element = LocateElement.Get_Element(data_set, selenium_driver)
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Failed to locate element", 3)
            return 'failed'
    else:
        Element = ActionChains(selenium_driver)

            
    # Insert keystroke
    try:
        if stype == 'keys':
            # Requires: python-selenium v3.1+, geckodriver v0.15.0+
            get_keystroke_value = getattr(Keys, keystroke_value.upper()) # Create an object for the keystroke
            result = Element.send_keys(get_keystroke_value * key_count) # Prepare keystroke for sending if Actions, or send if Element
            if get_element == False: Element.perform() # Send keystroke
        else:
            result = Element.send_keys(keystroke_value)
            if get_element == False: Element.perform()
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(),None, "Error sending keystroke %s: %s" % (stype, keystroke_value))


    # Test result
    if result not in failed_tag_list:
        CommonUtil.ExecLog(sModuleInfo, "Successfully sent %s: %s %d times" % (stype, keystroke_value, key_count), 1)
        return 'passed'
    else:
        CommonUtil.ExecLog(sModuleInfo, "Error sending keystroke %s: %s %d times" % (stype, keystroke_value, key_count), 3)
        return 'failed'


#Method to click on element; step data passed on by the user
def Click_Element(data_set):
    ''' Click using element or location '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
        
    try:
        bodyElement = ''
        for row in data_set:
            if row[0] == 'location' and row[1] == 'element parameter':
                bodyElement = LocateElement.Get_Element([('tag', 'element parameter', 'body')], selenium_driver) # Get element object of webpage body, so we can have a reference to the 0,0 coordinates
                shared_var = row[2] # Save shared variable name, or coordinates if entered directory in step data
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")
        
    # Click using element
    if bodyElement == '':
        CommonUtil.ExecLog(sModuleInfo, "Looking for element", 0)
        
        # Get element object
        Element = LocateElement.Get_Element(data_set,selenium_driver)
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return 'failed'
        
        # Click element
        try:
            Element.click()
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1)
            return "passed"
        except Exception:
            element_attributes = Element.get_attribute('outerHTML')
            CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
            errMsg = "Could not select/click your element."
            return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    # Click using location    
    else:
        CommonUtil.ExecLog(sModuleInfo, "Using provided location", 0)
        try:
            # Get coordinates
            if ',' in shared_var: # These are coordinates, use directly
                location = shared_var
            else: # Shared variable name was provided
                location = Shared_Resources.Get_List_from_Shared_Variables(shared_var)
            location = location.replace(' ', '')
            location = location.split(',')
            x = float(location[0])
            y = float(location[1])
            
            # Click coordinates
            actions = ActionChains(selenium_driver) # Create actions object
            actions.move_to_element_with_offset(bodyElement, x, y) # Move to coordinates (referrenced by body at 0,0)
            actions.click() # Click action
            actions.perform() # Perform all actions
        
            CommonUtil.ExecLog(sModuleInfo, "Click on location successful", 1)
            return 'passed'
        except Exception:
            return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error clicking location")
        


#Method to click and hold on element; step data passed on by the user
def Click_and_Hold_Element(step_data):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        Element = LocateElement.Get_Element(step_data,selenium_driver)
        if Element != "failed":
                try:
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
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed"    
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Method to right click on element; step data passed on by the user
def Context_Click_Element(step_data):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        Element = LocateElement.Get_Element(step_data,selenium_driver)
        if Element != "failed":
                try:
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
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed"  
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to double click on element; step data passed on by the user
def Double_Click_Element(step_data):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        Element = LocateElement.Get_Element(step_data,selenium_driver)
        if Element != "failed":
            try:
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
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed"      
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Method to move to middle of the element; step data passed on by the user
def Move_To_Element(step_data):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        Element = LocateElement.Get_Element(step_data,selenium_driver)
        if Element != "failed":
            try:
                move = ActionChains(selenium_driver).move_to_element(Element).perform()
                CommonUtil.TakeScreenShot(sModuleInfo)
                CommonUtil.ExecLog(sModuleInfo, "Successfully moved to the middle of the element with given parameters and values", 1)
                return "passed"
            except Exception:
                element_attributes = Element.get_attribute('outerHTML')
                CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
                errMsg = "Could not move to your element your element."
                return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed"   
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Method to hover over element; step data passed on by the user
def Hover_Over_Element(step_data):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        Element = LocateElement.Get_Element(step_data,selenium_driver)
        if Element != "failed":
            try:
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
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed"   
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def get_location_of_element(data_set):
    ''' Returns the x,y location of an element '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    # Parse data set
    try:
        shared_var = ''
        for row in data_set:
            if row[1] == 'action':
                shared_var = row[2] # Save the shared variable name
        
        if shared_var == '':
            CommonUtil.ExecLog(sModuleInfo, "Shared variable name missing from Value on action row", 3)
            return 'failed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Get element object
    Element = LocateElement.Get_Element(data_set, selenium_driver)
    if Element in failed_tag_list:
        CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
        return 'failed'
    
    # Get element location
    try:
        location = Element.location # Retreive the dictionary containing the x,y location coordinates
        if location in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not get element location", 3)
            return 'failed'
    
        # Save location as string, in preparation for the shared variable
        x = str(location['x'])
        y = str(location['y'])
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error retrieving element location")
    
    # Save location in shared variable
    Shared_Resources.Set_Shared_Variables(shared_var, "%s,%s" % (x, y))
    return 'passed'

    
#Search for element on new page after a particular time-out duration entered by the user through step-data
def Wait_For_New_Element(step_data):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        Element = LocateElement.Get_Element(step_data,selenium_driver)
        wait_for_element_to_disappear = False
        for each in step_data:
            if each[1]=="action":
                timeout_duration = int(each[2])
                if(each[0] == 'wait disable'):
                    wait_for_element_to_disappear = True
        start_time = time.time()
        interval = 1
        for i in range(timeout_duration):
            time.sleep(time.time() + i*interval - start_time)
            Element = LocateElement.Get_Element(step_data,selenium_driver)
            if wait_for_element_to_disappear == False:
                if (Element == 'failed'):
                    continue
                else:
                    return 'passed'
            else:
                if (Element == 'failed'):
                    return 'passed'
                else:
                    continue
        if wait_for_element_to_disappear == False:
            CommonUtil.ExecLog(sModuleInfo, "Waited for %s seconds but couldnt locate your element", 3)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Waited for %s seconds but your element still exists", 3)
        return 'failed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Validating text from an element given information regarding the expected text
def Compare_Lists(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        return Shared_Resources.Compare_Lists([step_data])
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Validating text from an element given information regarding the expected text
def Compare_Variables(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        return Shared_Resources.Compare_Variables([step_data])
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Inserting a field into a list of shared variables
def Insert_Into_List(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
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
                CommonUtil.ExecLog(sModuleInfo, "Value must contain more than one item, and must be comma separated", 3)
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

        else:
            Element = LocateElement.Get_Element(step_data,selenium_driver)
            if Element == "failed":
                CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                return "failed"  
            list_name = ''
            key = ''
            for each_step_data_item in step_data:
                if each_step_data_item[1] == "action":
                    key = each_step_data_item[2]
            # get list name from full input_string
            temp_list = key.split(',')
            if len(temp_list) == 1:
                CommonUtil.ExecLog(sModuleInfo, "Value must contain more than one item, and must be comma separated", 3)
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

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Validating text from an element given information regarding the expected text
def Save_Text(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        Element = LocateElement.Get_Element(step_data,selenium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed" 
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
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        Element = LocateElement.Get_Element(step_data,selenium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed" 
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
            CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, )
            CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 0)
            for each_actual_text_data_item in actual_text_data:
                if expected_text_data in each_actual_text_data_item:
                    CommonUtil.ExecLog(sModuleInfo, "The text has been validated by a partial match.", 1)
                    return "passed"
            CommonUtil.ExecLog(sModuleInfo, "Unable to validate using partial match.", 3)
            return "failed"
        #if step_data[0][len(step_data[0])-1][0] == "validate full text":
        if validation_type == "validate full text":
            actual_text_data = visible_list_of_element_text
            CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 0)
            CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 0)
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
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if ((1 < len(step_data) >= 2)):
            CommonUtil.ExecLog(sModuleInfo,"Please provide single row of data for only sleep. Consider using wait instead",3)
            return "failed"
        else:
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
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if ((1 < len(step_data) >= 2)):
            CommonUtil.ExecLog(sModuleInfo,"Please provide only single row of data",3)
            return "failed"
        else:
            tuple = step_data[0]
            scroll_direction = tuple[2]
            if scroll_direction == 'down':
                CommonUtil.ExecLog(sModuleInfo,"Scrolling down", 1)
                result = selenium_driver.execute_script("window.scrollBy(0,750)", "")
                time.sleep(2)
                return "passed"
            elif scroll_direction == 'up':
                CommonUtil.ExecLog(sModuleInfo, "Scrolling up", 1)
                result = selenium_driver.execute_script("window.scrollBy(0,-750)", "")
                time.sleep(2)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Value invalid. Only 'up', and 'down' allowed", 3)
                result = "failed"
                return result

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())



#Method to return pass or fail for the step outcome
def Navigate(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if ((1 < len(step_data) >= 2)):
            CommonUtil.ExecLog(sModuleInfo,"Please provide only single row of data",3)
            return "failed"
        else:
            navigate = step_data[0][2]
            if navigate == 'back':
                selenium_driver.back()
                CommonUtil.ExecLog(sModuleInfo, "Performing browser back", 1)
            elif navigate == 'forward':
                selenium_driver.forward()
                CommonUtil.ExecLog(sModuleInfo, "Performing browser forward", 1)
            elif navigate == 'refresh':
                selenium_driver.refresh()
                CommonUtil.ExecLog(sModuleInfo, "Performing browser refresh", 1)
            else:
                CommonUtil.ExecLog(sModuleInfo, "Value invalid. Only 'back', 'forward', 'refresh' allowed", 3)
                return "failed"
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def Select_Deselect(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        Element = LocateElement.Get_Element(step_data,selenium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed" 

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
                    CommonUtil.ExecLog(sModuleInfo, "Value invalid. Only 'deselect all', 'deselect by visible text', etc allowed", 3)
                    result = "failed"

            else:
                continue

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


'===================== ===x=== Sequential Action Section Ends ===x=== ======================'


'============================= Validate Table Section Begins =============================='

def Model_Actual_Data(actual_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
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

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(),None,"Could not model actual data")



def Model_Actual_Data_Ignoring_Column(actual_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        Modeled_Data_Set = []
        row_count = 1
        for each_row in actual_data:
            column_count = 1
            for each_column in each_row:
                temp_data_model = ["row "+str(row_count)]
                temp_data_model.append(each_column.strip())
                Modeled_Data_Set.append(temp_data_model)
                column_count = column_count +1
            row_count = row_count+1
        return Modeled_Data_Set
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(),None,"Could not model actual data ignoring column")



def Model_Actual_Data_Ignoring_Row(actual_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        Modeled_Data_Set = []
        row_count = 1
        for each_row in actual_data: # For each row in the table data
            column_count = 1
            for each_column in each_row: # For each column of this row
                temp_data_model = ["column "+str(column_count)] # ??
                temp_data_model.append(each_column.strip()) # Save the column
                Modeled_Data_Set.append(temp_data_model) # Add row to result array
                column_count = column_count +1
            row_count = row_count+1
        return Modeled_Data_Set
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(),None,"Could not model actual data ignoring column")



def Model_Expected_Data(expected_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
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
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(),None,"Could not model expected data")



def Model_Expected_Data_Ignoring_Column(expected_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
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
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(),None,"Could not model expected data ignoring column.")



def Model_Expected_Data_Ignoring_Row(expected_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        Modeled_Data_Set = []
        row_count = 1
        for each_row in expected_data: # For each row in step data (just the table data)
            column_count = 1
            temp_data_model = []
            for each_column in each_row: # For each column on this row
                if column_count <= 3:
                    if column_count == 2:
                        column_count = column_count + 1
                    else:
                        temp_data_model.append(each_column.strip()) # Save column
                        column_count = column_count +1
                else:
                    break
            Modeled_Data_Set.append(temp_data_model)
            row_count = row_count+1
        return Modeled_Data_Set
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(),None,"Could not model expected data ignoring row.")



def Model_Expected_Column_Row(expect_data):
    #collect all column name
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        column_names = []
        row_names = []
        for each in expect_data:
            if each[0] not in column_names:
                column_names.append(each[0])
            if each[1] not in row_names:
                row_names.append(each[1])
        return  column_names, row_names
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(),None,"Could not model expected column row. ")



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
            CommonUtil.ExecLog(sModuleInfo, "Size of the tables do not match!", 2)

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
                CommonUtil.ExecLog(sModuleInfo, "Function yet to be provided. Please wait for the update.", 2)

        #sequential logical flow
        if mismatch_count == 0:
            CommonUtil.ExecLog(sModuleInfo, "There were 0 mismatches! Table has been validated.", 1)
            CommonUtil.ExecLog(sModuleInfo, "List of matched items: %s"%(matched_list), 1)
            CommonUtil.ExecLog(sModuleInfo, "List of mismatched items: %s"%(mismatch_list), 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "There were mismatches! Table has invalid data.", 3)
            CommonUtil.ExecLog(sModuleInfo, "List of matched items: %s"%(matched_list), 3)
            CommonUtil.ExecLog(sModuleInfo, "List of mismatched items: %s"%(mismatch_list), 3)
            return "failed"

        #print mismatch_count, match_count, mismatch_list, matched_list

    except Exception:


        errMsg = "Error when comparing the exact expected and actual data."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


#Validate table
def Validate_Table(step_data):
    '''
    Text to read must come after validate table, and not be the last row
    
    '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
            
        ''' *** TEMPORARY WORKAROUND TO MAKE TRY BLOCK WORK AS DESIGNED ***
            REQUIRED FORMAT:
                ...Element parameters...
                Validate Table
                ...Table data...
                * relation type, can use a number in the "Field" field to represent the nTH element if more than one is matched
                
        '''
        
        # Convert tuples in step data to lists, to work with current implementation
        new_step_data = []
        for data_set in step_data:
            new_data_set = []
            for row in data_set:
                new_data_set.append(list(row))
            new_step_data.append(new_data_set)
        step_data = new_step_data

        # Find relation type, and get the table number, if specified
        preferred_match = 1
        for row in range(len(step_data[0])):
            if step_data[0][row][1] == 'relation type':
                try:
                    preferred_match = int(step_data[0][row][0]) # User specified a specific match - because there was more than one
                    CommonUtil.ExecLog(sModuleInfo, 'Will use matching table number %d' % preferred_match, 1)
                except:
                    pass
            
        # Find validate table, which is the divider between element data and table data we want to verify
        table_validate_index = ''
        for row in range(len(step_data[0])):
            if step_data[0][row][1] == 'validate table':
                table_validate_index = row
        if table_validate_index == '':
            CommonUtil.ExecLog(sModuleInfo, 'Step data missing "validate table" action', 3)
            return 'failed'

        # Using location of validate table, everything above it is element data        
        get_element_last_item = table_validate_index
        element_step_data = step_data[0][0:get_element_last_item:1]
        #element_step_data = Get_Element_Step_Data([step_data]) # Adds extra brackets around step data that creat an issue with validate 
        
        # Using location of validate table, everything below it is table data we want to verify
        expected_table_step_data = step_data[0][table_validate_index + 1:len(step_data[0]):1]


        try:
            #oCompare = CompareModule()
            #expected_table_step_data = (step_data[0][table_validate_index+1:len(step_data[0])-1:1])
            actual_table_dataset = Get_Table_Elements(step_data[0], preferred_match = preferred_match)
            if actual_table_dataset in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not get table elements", 3)
                return 'failed'

            try:
                validation_option=step_data[0][table_validate_index][2] # The "default" (case sensitive). Other type is not implemented

                # Process slightly differently depending on if the user wants to ignore a row or column, or match exactly                    
                if (step_data[0][table_validate_index][0] == "exact"):
                    modelled_actual_table_step_data = Model_Actual_Data(actual_table_dataset)
                    modelled_expected_table_step_data = Model_Expected_Data(expected_table_step_data)
                    result = Validate_Table_Helper(modelled_expected_table_step_data, modelled_actual_table_step_data, validation_option)

                elif step_data[0][table_validate_index][0]== "ignore row":
                    modelled_actual_table_step_data = Model_Actual_Data_Ignoring_Row(actual_table_dataset)
                    modelled_expected_table_step_data = Model_Expected_Data_Ignoring_Row(expected_table_step_data)
                    result = Validate_Table_Helper(modelled_expected_table_step_data, modelled_actual_table_step_data, validation_option)

                elif step_data[0][table_validate_index][0]== "ignore column":
                    modelled_actual_table_step_data = Model_Actual_Data_Ignoring_Column(actual_table_dataset)
                    modelled_expected_table_step_data = Model_Expected_Data_Ignoring_Column(expected_table_step_data)
                    result = Validate_Table_Helper(modelled_expected_table_step_data, modelled_actual_table_step_data, validation_option)

                else:
                    CommonUtil.ExecLog(sModuleInfo, "The information in the table validation index is incorrect. Please provide the appropriate information", 3)
                    return "failed"

                if result in failed_tag_list:
                    return 'failed'
                #status = oCompare.compare([expected_table_step_data], [modelled_actual_table_step_data])
                #print status
            except Exception:
                errMsg = "Error when comparing the expected and actual data."
                return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

        except Exception:
            errMsg = "Unable to get table element. Please check if the correct information has been provided."
            return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(),None,"Could not find your element.")



'===================== ===x=== Validate Table Section Ends ===x=== ======================'




def Get_Table_Elements(step_data,get_all_unvalidated_elements=False, preferred_match = 1):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        
        table = LocateElement.Get_Element(step_data,selenium_driver)
        if table == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed"  
           
        
        all_rows = WebDriverWait(table, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "*")))
        master_text_table = []
        for each_row_obj in all_rows:
            if (each_row_obj.is_displayed()!=False):
                try:
                    row_element = WebDriverWait(each_row_obj, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "*")))
                    temp_row_holder = []
                    for each_column_obj in row_element:
                        temp_row_holder.append(each_column_obj.text)
                except Exception:
                    errMsg = "Could not find table row elements"
                    return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
                master_text_table.append(temp_row_holder)
#         print master_text_table
        return master_text_table


    except Exception:
        errMsg = "Unable to get the element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)



'===================== ===x=== Get Element Section Ends ===x=== ======================'

def Tear_Down_Selenium(step_data = [[[]]]):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to tear down the page and close the browser...", 0)
        selenium_driver.quit()
        CommonUtil.ExecLog(sModuleInfo, "Closed the browser successfully.", 1)
        return "passed"
    except Exception:
        errMsg = "Unable to tear down selenium browsers"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


##@Riz and @Sreejoy: More work is needed here. Please investigate further.
def Get_Plain_Text_Element(element_parameter, element_value, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
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
            CommonUtil.ExecLog(sModuleInfo, "Value invalid. Only 'plain_text', 'partial_plain_text' allowed", 3)
            return "failed"

        return return_element

    except Exception:
        errMsg = "Could not get the element by plain text search"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_driver():
    return selenium_driver
