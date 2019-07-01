# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
'''
    Created on May 15, 2016

    @author: Built_In_Automation Solutionz Inc.
    Name: Built In Functions - Selenium
    Description: Sequential Actions for controlling Web Browsers - All main Web Browsers supported on Linux/Windows/Mac
'''

#########################
#                       #
#        Modules        #
#                       #
#########################
import sys, os, time, inspect
sys.path.append("..")
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
from pyautogui import press, typewrite

from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources
from Framework.Built_In_Automation.Shared_Resources import LocateElement
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list, skipped_tag_list

#########################
#                       #
#    Global Variables   #
#                       #
#########################

global WebDriver_Wait
WebDriver_Wait = 20
global WebDriver_Wait_Short
WebDriver_Wait_Short = 10

global selenium_driver
selenium_driver = None

#if Shared_Resources.Test_Shared_Variables('selenium_driver'): # Check if driver is already set in shared variables
#    selenium_driver = Shared_Resources.Get_Shared_Variables('selenium_driver') # Retreive appium driver

# Recall dependency, if not already set
dependency = None
if Shared_Resources.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables('dependency') # Retreive appium driver
else:
    raise ValueError("No dependency set - Cannot run")



def Open_Browser(dependency):
    ''' Launch browser and create instance '''
    
    global selenium_driver
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

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
        if "chrome" in browser or "chromeheadless" in browser:

            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-extensions")
            options.add_experimental_option("useAutomationExtension",False)
            d = DesiredCapabilities.CHROME
            d['loggingPrefs'] = {'browser': 'ALL'}
            if "chromeheadless" in browser: options.add_argument("--headless") # Enable headless operation if dependency set
            selenium_driver = webdriver.Chrome(chrome_options = options,desired_capabilities=d)
            selenium_driver.implicitly_wait(WebDriver_Wait)
            selenium_driver.maximize_window()
            CommonUtil.ExecLog(sModuleInfo, "Started Chrome Browser", 1)
            Shared_Resources.Set_Shared_Variables('selenium_driver',selenium_driver)
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
            return "passed"


        elif browser == 'firefox':
            from sys import platform as _platform
            if _platform == "win32":
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
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
            return "passed"
        elif "ie" in browser:
            selenium_driver = webdriver.Ie()
            selenium_driver.implicitly_wait(WebDriver_Wait)
            selenium_driver.maximize_window()
            CommonUtil.ExecLog(sModuleInfo, "Started Internet Explorer Browser", 1)
            Shared_Resources.Set_Shared_Variables('selenium_driver', selenium_driver)
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
            return "passed"

        elif "safari" in browser:
            os.environ["SELENIUM_SERVER_JAR"] = os.sys.prefix + os.sep + "Scripts" + os.sep + "selenium-server-standalone-2.45.0.jar"
            selenium_driver = webdriver.Safari()
            selenium_driver.implicitly_wait(WebDriver_Wait)
            selenium_driver.maximize_window()
            CommonUtil.ExecLog(sModuleInfo, "Started Safari Browser", 1)
            Shared_Resources.Set_Shared_Variables('selenium_driver', selenium_driver)
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
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
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        global dependency
        # Get the dependency again in case it was missed
        if Shared_Resources.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
            dependency = Shared_Resources.Get_Shared_Variables('dependency') # Retreive selenium driver
    
        cmd = step_data[0][2] # Expected "open" or "close" for current method. May contain other strings for old method of Field="open browser"
        if cmd.lower().strip() == 'close': # User issued close command
            try: selenium_driver.close()
            except: pass
            return 'passed'
        else: # User issued "open" command or used old method of "open browser"
            return Open_Browser(dependency)
    except Exception:
        ErrorMessage =  "failed to open browser"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)


def Go_To_Link(step_data, page_title=False):
    #this function needs work with validating page title.  We need to check if user entered any title.
    #if not then we don't do the validation
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Open browser and create driver if user has not already done so
    try:
        global selenium_driver
        if Shared_Resources.Test_Shared_Variables('selenium_driver') == False:
            CommonUtil.ExecLog(sModuleInfo, "Browser not previously opened, doing so now", 1)
            global dependency
            # Get the dependency again in case it was missed
            if Shared_Resources.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
                dependency = Shared_Resources.Get_Shared_Variables('dependency') # Retreive selenium driver
        
    
            result = Open_Browser(dependency)
            if result in failed_tag_list:
                return 'failed'
        else:
            selenium_driver = Shared_Resources.Get_Shared_Variables("selenium_driver")
    except Exception:
        ErrorMessage =  "failed to open browser"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)

    # Open URL in browser
    try:
        web_link=step_data[0][2] # Save Value field (URL)
        selenium_driver.get(web_link) # Open in browser
        selenium_driver.implicitly_wait(WebDriver_Wait) # Wait for page to load
        CommonUtil.ExecLog(sModuleInfo, "Successfully opened your link: %s" % web_link, 1)
        CommonUtil.TakeScreenShot(sModuleInfo)
        return "passed"
    except Exception:
        ErrorMessage =  "failed to open your link: %s" %(web_link)
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)


def Handle_Browser_Alert(step_data):
    #accepts browser alert
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        choice = str(step_data[0][2]).lower()
        if choice == 'accept' or choice == 'pass' or choice == 'yes' or choice == 'ok':
            try:
                selenium_driver.switch_to_alert().accept()
                CommonUtil.ExecLog(sModuleInfo, "Browser alert accepted", 1)
                return "passed"
            except NoAlertPresentException as e:
                CommonUtil.ExecLog(sModuleInfo, "Browser alert not found", 2)
                return "passed"
        elif choice == 'reject' or choice == 'fail' or choice == 'no' or choice == 'cancel':
            try:
                selenium_driver.switch_to_alert().dismiss()
                CommonUtil.ExecLog(sModuleInfo, "Browser alert rejected", 1)
                return "passed"
            except NoAlertPresentException as e:
                CommonUtil.ExecLog(sModuleInfo, "Browser alert not found", 2)
                return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Wrong Step Data", 3)
            return "failed"

    except Exception:
        ErrorMessage =  "Failed to accept browser alert"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)



def Initialize_List(data_set):
    ''' Temporary wrapper until we can convert everything to use just data_set and not need the extra [] '''
    return Shared_Resources.Initialize_List([data_set])

#Method to enter texts in a text box; step data passed on by the user
def Enter_Text_In_Text_Box(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    try:
        delay=0
        text_value=""
        global selenium_driver
        Element = LocateElement.Get_Element(step_data,selenium_driver)
        if Element != "failed":
            for each in step_data:
                if each[1]=="action":
                    text_value=each[2]
                    break
                elif each[0]=="delay":
                    delay=float(each[2])
                else:
                    continue
            Element.click()
            #Element.clear()
            Element.send_keys(Keys.CONTROL, 'a')
            if delay == 0:
                Element.send_keys(text_value)
            else:
                for c in text_value:
                    Element.send_keys(c)
                    time.sleep(delay)
            try:
                Element.click()
            except: #sometimes text field can be unclickable after entering text
                pass
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
    global selenium_driver
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
    global selenium_driver
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
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    global selenium_driver
    try:
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
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    global selenium_driver
    try:
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
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    global selenium_driver
    try:
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
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    global selenium_driver
    try:
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
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    global selenium_driver
    try:
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
    global selenium_driver
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
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    global selenium_driver
    try:
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
    global selenium_driver
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
    global selenium_driver
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
    global selenium_driver
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
    global selenium_driver
    try:
        scroll_inside_element = False
        scroll_window_name = 'window'
        scroll_window = ""
        action_row = None

        for row in step_data:
            if str(row[1]) == 'action':
                action_row = row
                break

        if not action_row:
            CommonUtil.ExecLog(sModuleInfo,"No action row defined",3)
            return "failed"

        if len(step_data)>1: #element given scroll inside element, not on full window
            scroll_inside_element=True
            scroll_window_name='arguments[0]'

        if scroll_inside_element:
            scroll_window = LocateElement.Get_Element(step_data, selenium_driver)
            if scroll_window in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Element through which instructed to scroll not found",3)
                return "failed"

            CommonUtil.ExecLog(sModuleInfo,"Element inside which instructed to scroll has been found. Scrolling thorugh it",1)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Scrolling through main window",1)

        scroll_direction = str(action_row[2]).strip().lower()
        if scroll_direction == 'down':
            CommonUtil.ExecLog(sModuleInfo,"Scrolling down", 1)
            result = selenium_driver.execute_script("%s.scrollBy(0,750)"%scroll_window_name, scroll_window)
            time.sleep(2)
            return "passed"
        elif scroll_direction == 'up':
            CommonUtil.ExecLog(sModuleInfo, "Scrolling up", 1)
            result = selenium_driver.execute_script("%s.scrollBy(0,-750)"%scroll_window_name, scroll_window)
            time.sleep(2)
            return "passed"
        elif scroll_direction == 'left':
            CommonUtil.ExecLog(sModuleInfo, "Scrolling left", 1)
            result = selenium_driver.execute_script("%s.scrollBy(-750,0)"%scroll_window_name, scroll_window)
            time.sleep(2)
            return "passed"
        elif scroll_direction == 'right':
            CommonUtil.ExecLog(sModuleInfo, "Scrolling right", 1)
            result = selenium_driver.execute_script("%s.scrollBy(750,0)"%scroll_window_name, scroll_window)
            time.sleep(2)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Value invalid. Only 'up', 'down', 'right' and 'left' allowed", 3)
            result = "failed"
            return result

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to scroll to view an element
def scroll_to_element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    global selenium_driver
    try:
        scroll_element = LocateElement.Get_Element(step_data, selenium_driver)
        if scroll_element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Element to which instructed to scroll not found",3)
            return "failed"

        CommonUtil.ExecLog(sModuleInfo,"Element to which instructed to scroll has been found. Scrolling to view it",1)
        actions = ActionChains(selenium_driver)
        actions.move_to_element(scroll_element)
        actions.perform()
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to return pass or fail for the step outcome
def Navigate(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    global selenium_driver
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
    global selenium_driver
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

def validate_table(data_set):
    ''' Compare the table provided in step data with the one found on the web page '''
    # Compare a webpage table with one specified in the step data
    # All inputs have the sub-field set as "table parameter"
    # Valid table parameters:
    # > ignore rows: Ignores the comma delimited rows specified in the Value field
    # > ignore columns: Ignores the comma delimited columns specified in the Value field
    # > case: Value=Sensitive: This is the default, and values must match exactly. Value=insensitive: Perform case insensitive matching
    # > exact: True (default) do nothing. False= Infer which cells to ignore. This is similar to ignore rows/cols, but can ignore specific cells if the user does not specify them. Mutually exclusive of ignore rows/cols
    global selenium_driver
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    # Initialize variables
    have_table = False # Tells us if we read a table from the step data
    case_sensitive = True # Case sensitive search
    ignore_rows = [] # List of rows to ignore/skip
    ignore_cols = [] # List of columns to ignore/skip
    user_table = {} # Constructed user-defined table
    webpage_table = {} # Constructed webpage table
    exact_table = True # Require exact table match
    table_type = '' # Type of table (css/html)
    
    # Parse data set
    try:
        for row in data_set:
            field, subfield, value = row[0], row[1], row[2] # Put data row in understandable variables
            
            if subfield == 'action':
                if value.strip().lower() in ('css', 'html'):
                    table_type = value
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Invalid table type in Value on Action line. Should be 'html' or 'css'", 3)
                    return 'failed'
            elif subfield == 'table parameter': # Inspect the table parameters (element parameters go to a different section)
                
                # Parse table instructions
                if field == 'ignore row' or field == 'ignore rows': # User specified list of rows to ignore
                    ignore_rows = value.split(',') # Get rows as comma delimited string and store in list
                    ignore_rows = map(int, ignore_rows) # Convert to integers
                elif field == 'ignore column' or field == 'ignore columns': # User specified list of columns to ignore
                    ignore_cols = value.split(',') # Get columns as comma delimited string and store in list
                    ignore_cols = map(int, ignore_cols) # Convert to integers
                elif field == 'case': # User specified case sensitivity
                    if value.lower().strip() == 'exact' or value.lower().strip() == 'sensitive': # Sensitive match (default)
                        case_sensitive = True
                    elif value.lower().strip() == 'insensitive': # Insensitive match - we'll convert everything to lower case
                        case_sensitive = False
                elif field == 'exact': # User specified type of table matching
                    if value.lower().strip() == 'true' or value.lower().strip() == 'yes': # Exact table match, but user can specify rows/columns to ignore
                        exact_table = True
                    elif value.lower().strip() == 'false' or value.lower().strip() == 'no': # Not an exact match for all cells, only match the ones the user specified
                        exact_table = False
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Unknown Value for table parameter 'exact'. Should be true or false.", 3)
                        return 'failed'
                
                # Create user-defined table 
                else:
                    try:
                        table_row, table_col = ('', '')
                        table_row, table_col = field.split(',') # Field should be in the format of ROW,COL
                        if table_row != '' and table_col != '': # Check to ensure this was a table cell identifier - may not be
                            if case_sensitive == False: # User specified case insensitive serach
                                value = value.lower() # Prepare this table by setting all cell values to lowercase
                            user_table["%s,%s" % (table_row, table_col)] = value # Save value using the row,col as an identifier
                            have_table = True # Indicate we have at least one cell of a table specified
                        else:
                            CommonUtil.ExecLog(sModuleInfo, "Unknown Field for table parameter", 3)
                            return 'failed'
                    except: # Row may have been blank, or some other issue
                        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Unknown Field for table parameter")

        # Ensure we have a table from the user
        if have_table == False:
            CommonUtil.ExecLog(sModuleInfo, "No table values found, or they were not entered in the format of row,column (Eg: 1,2). Please create a table as defined in the documentation", 3)
            return 'failed'
        CommonUtil.ExecLog(sModuleInfo, "Table parameters - Case Sensitive: %s - ignore_rows: %s - ignore_cols: %s - exact: %s" % (str(case_sensitive), str(ignore_rows), str(ignore_cols), str(exact_table)), 0)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error while parsing the data set")
   
    # Get table from web page
    if table_type == 'html': # HTML type table
        webpage_table = get_webpage_table_html(data_set, ignore_rows, ignore_cols, case_sensitive) # Produces an array that should match the user array
    elif table_type == 'css': # CSS type table
        webpage_table = get_webpage_table_css(data_set, ignore_rows, ignore_cols, case_sensitive) # Produces an array that should match the user array
    CommonUtil.ExecLog(sModuleInfo, "Webpage table  : %s" % webpage_table, 0)
    CommonUtil.ExecLog(sModuleInfo, "Step data table: %s" % user_table, 0)
    if webpage_table in failed_tag_list:
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
        return "failed"
    
    # If user did not specify any rows or columns to ignore, we will infer that rows and columns NOT defined are meant to be ignored
    # We do this by modifying the webpage table to remove rows and columns that don't match
    if exact_table == False and ignore_rows == [] and ignore_cols == []: # If user did not specify anything to ignore
        CommonUtil.ExecLog(sModuleInfo, "Inferring which cells from the webpage table to ignore", 0)
        unmatched_cells = []
        for ids in webpage_table: # For each table cell on the user table - basically looking for items that are specified, but not found
            if ids not in user_table: # if cell from user table not found in webpage table
                unmatched_cells.append(ids) # Keep list of cell IDs we want to trim from the webpage table
        CommonUtil.ExecLog(sModuleInfo, "Removing inferred cells: %s" % str(unmatched_cells), 0)
        for ids in unmatched_cells: # Remove these cells from the webpage table
            if ids in webpage_table: # Check if the ID exists in case the user specified something that's not actually in the webpage table
                del(webpage_table[ids])

    
    # Check if arrays match
    failed_matches = []
    for ids in webpage_table: # For each table cell on the webpage table
        if ids in user_table: # If that table cell is also in the user defined table
            if webpage_table[ids] != user_table[ids]: # Check if the values of these two cells match
                failed_matches.append('%s:"%s" != %s:"%s"' % (ids, user_table[ids], ids, webpage_table[ids])) # Record the unmatched cells
        else: # Not in user table
            failed_matches.append("Cell %s is not defined in the step data" % ids)
    
    for ids in user_table: # For each table cell on the user table - basically looking for items that are specified, but not found
        if ids not in webpage_table: # if cell from user table not found in webpage table
            failed_matches.append("Cell %s is not found in the webpage table" % ids)
            
    # If any failed matches, list them in the log, so the user can see and exit
    if len(failed_matches) > 0:
        CommonUtil.ExecLog(sModuleInfo, "Tables do not match - %s" % str(failed_matches), 3)
        return 'failed'
    
    CommonUtil.ExecLog(sModuleInfo, "Tables match", 1)
    return 'passed'


def validate_table_row_size(data_set):
    ''' Save row size in a share variable of the table provided in step data'''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    global selenium_driver
    try:
        # Initialize variables
        expected_row = '' #variable where the row size will be saved
        table_type = ''  # Type of table (css/html)

        # Parse data set

        for row in data_set:
            field, subfield, value = row[0], row[1], row[2]  # Put data row in understandable variables

            if subfield == 'action':
                table_type,expected_row = str(value).split(',')




        if table_type == '' or expected_row == '':
            CommonUtil.ExecLog(sModuleInfo, "No table type or expected row is given.. table type should be html or css, expected row is a number which is the expected row size", 3)
            return "failed"

        # Get table from web page
        table = LocateElement.Get_Element(data_set, selenium_driver)

        if table in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your table with given data.", 3)
            return "failed"

        all_rows = []
        if table_type == 'html':  # HTML type table
            all_rows = table.find_elements_by_tag_name('tr')  # Get element list for all rows
        elif table_type == 'css':  # CSS type table
            all_rows = WebDriverWait(table, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "*")))

        row_size = len(all_rows)

        CommonUtil.ExecLog(sModuleInfo, "Webpage table row size: %s" %row_size, 1)
        CommonUtil.ExecLog(sModuleInfo, "Expected table row size: %s" % expected_row, 1)

        if int(row_size) != int(expected_row):
            CommonUtil.ExecLog(sModuleInfo, "Row sizes don't match", 3)
            return "failed"

        CommonUtil.ExecLog(sModuleInfo, "Row sizes match", 1)
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None)

def validate_table_column_size(data_set):
    ''' Save row size in a share variable of the table provided in step data'''
    global selenium_driver
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        # Initialize variables
        expected_col = ''  # variable where the row size will be saved
        table_type = ''  # Type of table (css/html)

        # Parse data set

        for row in data_set:
            field, subfield, value = row[0], row[1], row[2]  # Put data row in understandable variables

            if subfield == 'action':
                table_type, expected_col = str(value).split(',')




        if table_type == '' or expected_col == '':
            CommonUtil.ExecLog(sModuleInfo, "No table type or expected column is given.. table type should be html or css, expected column is a number which is the expected row size", 3)
            return "failed"

        # Get table from web page
        table = LocateElement.Get_Element(data_set, selenium_driver)

        if table in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your table with given data.", 3)
            return "failed"

        all_rows = []
        all_cols = []
        if table_type == 'html':  # HTML type table
            all_rows = table.find_elements_by_tag_name('tr')  # Get element list for all rows
            if len(all_rows)>0:
                all_cols = all_rows[0].find_elements_by_tag_name('td')  # Get element list for all columns in this row
                if len(all_cols) == 0:  # No <TD> type columns, so check if there were header type columns, and use those instead
                    all_cols = all_rows[0].find_elements_by_tag_name('th')  # Get element list for all header columns in this row
        elif table_type == 'css':  # CSS type table
            all_rows = WebDriverWait(table, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "*")))
            for row_obj in all_rows:  # For each row
                if row_obj.is_displayed() != False:
                            # Get elements for each column
                    all_cols = WebDriverWait(row_obj, WebDriver_Wait).until(
                                EC.presence_of_all_elements_located((By.XPATH, "*")))
                    break

        col_size = len(all_cols)

        CommonUtil.ExecLog(sModuleInfo, "Webpage table column size: %s" % col_size, 1)
        CommonUtil.ExecLog(sModuleInfo, "Expected table column size: %s" % expected_col, 1)

        if int(col_size) != int(expected_col):
            CommonUtil.ExecLog(sModuleInfo, "Column sizes don't match", 3)
            return "failed"

        CommonUtil.ExecLog(sModuleInfo, "Column sizes match", 1)
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None)

def get_webpage_table_html(data_set, ignore_rows = [], ignore_cols = [], retain_case = True):
    ''' Find an HTML table given the elements, extract the text and return as a dictionary containing lists holding the data '''
    # data_set: Contains user defined identifiers used to get the element of table
    # ignore_rows: List containing rows to ignore
    # ignore_cols: List containing columns to ignore
    # retain_case: Set to true to keep data exactly as is. Set to false to set it to lower case which is useful for case insensitive matching
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    global selenium_driver
    try:
        # Get element representing entire table
        table = LocateElement.Get_Element(data_set, selenium_driver)
        if table in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed"  
       
        master_text_table = {}
        table_row = 0
        tr_list = table.find_elements_by_tag_name('tr') # Get element list for all rows
        for tr in tr_list: # For each row element
            table_row += 1
            table_col = 0
            td_list = tr.find_elements_by_tag_name('td') # Get element list for all columns in this row
            if len(td_list) == 0: # No <TD> type columns, so check if there were header type columns, and use those instead
                td_list = tr.find_elements_by_tag_name('th') # Get element list for all header columns in this row
            for td in td_list: # For each column element
                table_col += 1
                value = str(td.text).strip() # Save the text from this cell (also removing any HTML tags that may be in it)
                if retain_case == False: value = value.lower() # change cell text to lower case
                master_text_table["%s,%s" % (table_row, table_col)] = value # Put value from cell in dictionary

        return master_text_table # Return table text as dictionary
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error while parsing the table")

def get_webpage_table_css(data_set, ignore_rows = [], ignore_cols = [], retain_case = True):
    ''' Find a CSS table given the elements, extract the text and return as a dictionary containing lists holding the data '''
    # data_set: Contains user defined identifiers used to get the element of table
    # ignore_rows: List containing rows to ignore
    # ignore_cols: List containing columns to ignore
    # retain_case: Set to true to keep data exactly as is. Set to false to set it to lower case which is useful for case insensitive matching
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    global selenium_driver
    try:
        # Get element representing entire table
        table = LocateElement.Get_Element(data_set, selenium_driver)
        if table in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed"  
           
        # Get element for all rows
        all_rows = WebDriverWait(table, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "*")))
        
        master_text_table = {}
        table_row = 0
        for row_obj in all_rows: # For each row
            table_row += 1
            if row_obj.is_displayed() != False:
                if table_row not in ignore_rows: # Skip rows the user wants to ignore
                    try:
                        # Get elements for each column 
                        col_element = WebDriverWait(row_obj, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "*")))
                        
                        table_col = 0
                        for column_obj in col_element: # For each column on the row
                            table_col += 1
                            if table_col not in ignore_cols: # Skip columns the user wants to ignore
                                value = str(column_obj.text).strip() # Save the text from this cell (also removing any HTML tags that may be in it)
                                if retain_case == False: value = value.lower() # change cell text to lower case
                                master_text_table["%s,%s" % (table_row, table_col)] = value # Put value from cell in dictionary
                            
                    except: # This will crash for single column tables or lists
                        table_col = 1 # Likely only one column
                        value = str(row_obj.text).strip() # Save the text from this cell (also removing any HTML tags that may be in it)
                        if retain_case == False: value = value.lower() # change cell text to lower case
                        master_text_table["%s,%s" % (table_row, table_col)] = value # Put value from cell in dictionary

        return master_text_table # Return table text as dictionary
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error while parsing the table")


def Tear_Down_Selenium(step_data = [[[]]]):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    global selenium_driver
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
    global selenium_driver
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
    global selenium_driver
    return selenium_driver


#Method to open a new tab
def open_new_tab(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    global selenium_driver
    try:
        time.sleep(2)
        CommonUtil.ExecLog(sModuleInfo, "Opening New Tab in Browser", 1)
        selenium_driver.execute_script('''window.open(" ","_blank");''')

        CommonUtil.ExecLog(sModuleInfo, "New Tab Opened Successfully in Browser", 1)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to switch to a new tab
def switch_tab(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    global selenium_driver
    try:
        tab = 1
        for each in step_data:
            if each[1] == "action":
                tab = int(str(each[2]))

        CommonUtil.ExecLog(sModuleInfo, "Switching to Tab %d in Browser"%tab, 1)
        windows = selenium_driver.window_handles
        selenium_driver.switch_to.window(windows[tab-1])
        CommonUtil.ExecLog(sModuleInfo, "Switched to Tab %s Successfully in Browser"%tab, 1)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to upload file
def upload_file(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    global selenium_driver
    try:
        file_name = ''
        for each in step_data:
            if each[1] == "action":
                file_name = str(each[2]).strip()

        if file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "File name can't be empty!",3)
            return "failed"
        elif not os.path.exists(file_name):
            CommonUtil.ExecLog(sModuleInfo, "File '%s' can't be found.. please give a valid file path"%file_name,3)
            return "failed"

        if sys.platform != 'darwin':
            file_window=LocateElement.Get_Element(step_data, selenium_driver)
            file_window.click()
            time.sleep(5) #wait for the window to appear

            pyautogui.typewrite(file_name) #type file name
            pyautogui.hotkey('ENTER')
            CommonUtil.ExecLog(sModuleInfo, "File '%s' uploaded successfully" % file_name,1)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Uploading file not supported in Mac Platform right now!",2)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to upload file
def drag_and_drop(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    global selenium_driver
    try:
        source = ''
        destination = ''
        for each in step_data:
            if each[0] == "source":
                source = str(each[2]).strip()
            elif each[0] == "destination":
                destination = str(each[2]).strip()

        if source == '':
            CommonUtil.ExecLog(sModuleInfo, "No source element specified for drag and drop",3)
            return "failed"
        elif destination == '':
            CommonUtil.ExecLog(sModuleInfo, "No destination element specified for drag and drop",3)
            return "failed"


        source_element = Shared_Resources.Get_Shared_Variables(source)
        if source_element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "No element found in shared variables named '%s' which is defined as source for drag and drop",source,3)


        destination_element = Shared_Resources.Get_Shared_Variables(destination)
        if destination_element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"No element found in shared variables named '%s' which is defined as source for drag and drop",source,3)

        ActionChains(selenium_driver).drag_and_drop(source_element, destination_element).perform()
        CommonUtil.ExecLog(sModuleInfo,"Drag and drop completed from source '%s' to destination '%s'"%(source, destination))

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def if_element_exists(data_set):
    ''' Click on an element '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)
    global selenium_driver
    try:
        variable_name = ''
        boolean = 'true'
        for row in data_set:
            if str(row[1]) == 'action':
                splitted = str(row[2]).split("=")
                if len(splitted) < 2:
                    CommonUtil.ExecLog(sModuleInfo,
                                       "Data should be like variable_name=boolean (for example: abc=True, Here abc is the variable name and True is the boolean value)",
                                       3)
                    return "failed"
                variable_name = str(splitted[0]).strip()
                variable_name = variable_name.split('%|')[1].split('|%')[0]
                boolean = str(splitted[1]).strip().lower()

        if variable_name == '':
            CommonUtil.ExecLog(sModuleInfo,
                               "Data should be like variable_name=boolean (for example: abc=True, Here abc is the variable name and True is the boolean value)",
                               3)
            return "failed"

        Element = LocateElement.Get_Element(data_set, selenium_driver)
        if Element in failed_tag_list:
            Shared_Resources.Set_Shared_Variables(variable_name, str(not boolean))
        else:
            Shared_Resources.Set_Shared_Variables(variable_name, str(boolean))
        return "passed"
    except Exception:
        errMsg = "Could not find your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)