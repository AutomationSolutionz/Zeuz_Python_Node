
# Android environment
from appium import webdriver
import os, sys, time, inspect, json
from Framework.Utilities import CommonUtil, FileUtilities
from Framework.Built_In_Automation.Mobile.Android.adb_calls import adbOptions
from appium.webdriver.common.touch_action import TouchAction
#from Built_In_Automation.Mobile.CrossPlatform.Appium import clickinteraction as ci
#from Built_In_Automation.Mobile.CrossPlatform.Appium import textinteraction as ti

#from selenium import webdriver as webdriverSelenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dropbox.files import Dimensions
from common_functions import *

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

# Recall appium driver, if not already set - needed between calls in a Zeuz test case
global driver
driver = None
if CommonUtil.Test_Shared_Variables('appium_driver'): # Check if driver is already set in shared variables
    driver = CommonUtil.Get_Shared_Variables('appium_driver') # Retreive appium driver

# Recall dependency, if not already set
dependency = 'Android' #{'Mobile OS':'Android'} #!!! Will be updated by sequential_actions_appium() in the future
if CommonUtil.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
    dependency = CommonUtil.Get_Shared_Variables('dependency') # Retreive appium driver
 

global WebDriver_Wait 
WebDriver_Wait = 20




################################### APPIUM COMMANDS ###################################
################################### APPIUM COMMANDS ###################################
################################### APPIUM COMMANDS ###################################
def launch_application(package_name, activity_name):
    ''' Launch the application the appium instance was created with, and create the instance if necessary '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if driver == None: # Only create a new appium instance if we haven't already (may be done by install_and_start_driver())
            result = start_appium_driver(package_name, activity_name)
            if result == 'failed':
                return 'failed'
        
        driver.launch_app() # Launch program configured in the Appium capabilities
        CommonUtil.ExecLog(sModuleInfo,"Launched the app successfully.",1)
        return "passed"
    except Exception, e:
        return CommonUtil.Exception_Handler(sys.exc_info())

def start_appium_driver(package_name = '', activity_name = '', filename = ''):
    ''' Creates appium instance using discovered and provided capabilities '''
    # Does not execute application
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Trying to create Appium instance...",1)
    
    try:
        if driver == None:
            # Setup capabilities
            desired_caps = {}
            desired_caps['platformName'] = dependency # Set platform name
            desired_caps['autoLaunch'] = 'false' # Do not launch application
            
            if dependency == 'Android':
                CommonUtil.ExecLog(sModuleInfo,"Setting up with Android",1)
                desired_caps['platformVersion'] = adbOptions.get_android_version().strip()
                desired_caps['deviceName'] = adbOptions.get_device_model().strip()
                if package_name:
                    desired_caps['appPackage'] = package_name.strip()
                if activity_name:
                    desired_caps['appActivity'] = activity_name.strip()
                if filename and package_name == '': # User must specify package or file, not both. Specifying filename instructs Appium to install
                    desired_caps['app'] = PATH(filename).strip()
            elif dependency == 'IOS':
                CommonUtil.ExecLog(sModuleInfo,"Setting up with IOS",1)
                desired_caps['platformVersion'] = '' # Read version
                desired_caps['deviceName'] = '' # Read model
                desired_caps['bundleId'] = package_name
                desired_caps['udid'] = '' # Read UDID
                CommonUtil.ExecLog(sModuleInfo, "IOS not yet supported", 3)
                return 'failed'
            else:
                CommonUtil.ExecLog(sModuleInfo, "Invalid dependency: " + dependency, 3)
                return 'failed'
            CommonUtil.ExecLog(sModuleInfo,"Capabilities: %s" % str(desired_caps),1)
            
            # Create Appium instance with capabilities
            global driver
            driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps) # Create instance
            if driver: # Make sure we get the instance
                CommonUtil.Set_Shared_Variables('appium_driver', driver) # Save driver instance to make available to other modules
                CommonUtil.ExecLog(sModuleInfo,"Launched the app successfully.",1)
                return "passed"
            else: # Error during setup, reset
                driver = None
                CommonUtil.ExecLog(sModuleInfo,"Error during Appium setup", 3)
                return 'failed'
        else: # Driver is already setup, don't do anything
            CommonUtil.ExecLog(sModuleInfo,"Driver already configured, not re-doing",1)
            return 'passed'
    except Exception, e:
        return CommonUtil.Exception_Handler(sys.exc_info())
    
    
def teardown_appium():
    ''' Teardown of appium instance '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Starting Appium cleanup.",1)
    try:
        global driver
        driver.quit() # Tell appium to shutdown instance
        driver = None # Clear driver variable, so next run will be fresh
        CommonUtil.Set_Shared_Variables('appium_driver', '') # Clear the driver from shared variables
        CommonUtil.ExecLog(sModuleInfo,"Appium cleaned up successfully.",1)
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def close_application():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to close the app",1)
        driver.close_app()
        CommonUtil.ExecLog(sModuleInfo,"Closed the app successfully",1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close the driver. %s"%Error_Detail, 3)
        return "failed"
    
    
def install_application(app_location, activity_name=''):
    ''' Install application to device '''
    # Webdriver does the installation and verification
    # If the user tries to call install again, nothing will happen because we don't want to create another instance. User should teardown(), then install
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Trying to install and then launch the app...",1)
    
    try:
        if driver == None: # Only create a new appium instance if we haven't already (may be done by install_and_start_driver())
            result = start_appium_driver('', activity_name, app_location) # Install application and create driver instance. First parameter is always empty. We specify the third parameter with the file, and optionally the second parameter with the activity name if it's needed
            if result == 'failed':
                return 'failed'

        CommonUtil.ExecLog(sModuleInfo,"Installed and launched the app successfully.",1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start WebDriver. %s"%Error_Detail, 3)
        return "failed"


def wait(_time): # To be replaced with sleep()
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Starting waiting for %s seconds.."%_time,1)
        driver.implicitly_wait(float(_time)) # Instructs appium not to timeout while we wait (it has a 60 second timeout by default)
        time.sleep(_time) # Stop here the specified amount of time
        CommonUtil.ExecLog(sModuleInfo,"Waited successfully",1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to wait. %s"%Error_Detail, 3)
        return "failed"

    
def uninstall_application(app_package):
    ''' Uninstalls/removes application from device '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to remove app with package name %s..."%app_package,1)
        #if driver.is_app_installed(app_package):
            #CommonUtil.ExecLog(sModuleInfo,"App is installed. Now removing...",1)
        try:
            driver.remove_app(app_package)
            CommonUtil.ExecLog(sModuleInfo,"App is removed successfully.",1)
            return "passed"
        except:
            CommonUtil.ExecLog(sModuleInfo, "Unable to remove the app", 3)
            return "failed"
        """else:   
            CommonUtil.ExecLog(sModuleInfo,"App is not found.",3)
            return "failed" """
        
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to wait. %s"%Error_Detail, 3)
        return "failed"

def Android_Keystroke_Key_Mapping(keystroke):
    ''' Provides a friendly interface to invoke key events '''
    # Keycodes: https://developer.android.com/reference/android/view/KeyEvent.html

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Starting Android key event handling for %s" % keystroke, 1)
    
    # Sanitize input
    keystroke = keystroke.strip()
    keystroke = keystroke.lower()
    keystroke = keystroke.replace('_', ' ')
    
    try:
        if keystroke == "return" or keystroke == "enter":
            driver.keyevent(66)
        elif keystroke == "go back":
            driver.back()
        elif keystroke == "spacebar":
            driver.keyevent(62)
        elif keystroke == "backspace":
            driver.keyevent(67)
        elif keystroke == "call": # Press call connect, or starts phone program if not already started
            driver.keyevent(5)
        elif keystroke == "end call":
            driver.keyevent(6)
        elif keystroke == "home":
            driver.keyevent(3)
        elif keystroke == "mute":
            driver.keyevent(164)
        elif keystroke == "volume down":
            driver.keyevent(25)
        elif keystroke == "volume up":
            driver.keyevent(24)
        elif keystroke == "wake":
            driver.keyevent(224)
        elif keystroke == "power":
            driver.keyevent(26)
        elif keystroke == "app switch": # Task switcher / overview screen
            driver.keyevent(187)
        elif keystroke == "page down":
            driver.keyevent(93)
        elif keystroke == "page up":
            driver.keyevent(92)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unsupported key event: %s" % keystroke, 3)

        return 'passed'
    except Exception, e:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Click_Element(element_parameter, element_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to click on element...", 1)
        if element_parameter == "name":
            result = click_element_by_name(driver, element_value)
        elif element_parameter == "id":
            result = click_element_by_id(driver, element_value)
        elif element_parameter == "accessibility_id":
            result = click_element_by_accessibility_id(driver, element_value)
        elif element_parameter == "class_name":
            result = click_element_by_class_name(driver, element_value)
        elif element_parameter == "xpath":
            result = click_element_by_xpath(driver, element_value)
        elif element_parameter == "android_uiautomator_text":
            result = click_element_by_android_uiautomator_text(driver, element_value)
        elif element_parameter == "android_uiautomator_description":
            result = click_element_by_android_uiautomator_description(driver, element_value)
        elif element_parameter == "ios_uiautomation":
            result = click_element_by_ios_uiautomation(driver, element_value)
        else:
            try:
                CommonUtil.ExecLog(sModuleInfo,
                                   "Trying to click on element with parameter - %s and value - %s ..." % (element_parameter, element_value),
                                   1)
                elem = driver.find_element_by_xpath("//*[@%s='%s']" % (element_parameter, element_value))
                if elem.is_enabled():
                    elem.click()
                    CommonUtil.ExecLog(sModuleInfo, "Clicked on element successfully", 1)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to click. The element is disabled.", 3)
                    return "failed"
            except Exception, e:
                CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
                    exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
                CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s" % Error_Detail, 3)
                return "failed"

        if result == "passed":
            CommonUtil.ExecLog(sModuleInfo, "Clicked on element successfully", 1)
            return "passed"
        elif result == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to click. The element is disabled.", 3)
            return "failed"

        """element_data = Validate_Step_Data(step_data)
        elem = Get_Element(element_data[0], element_data[1])
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo, "Clicked on element successfully", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to click. The element is disabled.", 3)
            return "failed" """
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s" % Error_Detail, 3)
        return "failed"


# Method to enter texts in a text box; step data passed on by the user
def Set_Text(element_parameter, element_value, text_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Inside Enter Text In Text Box function", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to set text in the textbox...", 1)
        if element_parameter == "name":
            result = set_text_by_name(driver, element_value, text_value)
        elif element_parameter == "id":
            result = set_text_by_id(driver, element_value, text_value)
        elif element_parameter == "accessibility_id":
            result = set_text_by_accessibility_id(driver, element_value, text_value)
        elif element_parameter == "class_name":
            result = set_text_by_class_name(driver, element_value, text_value)
        elif element_parameter == "xpath":
            result = set_text_by_xpath(driver, element_value, text_value)
        elif element_parameter == "android_uiautomator_text":
            result = set_text_by_android_uiautomator_text(driver, element_value, text_value)
        elif element_parameter == "android_uiautomator_description":
            result = set_text_by_android_uiautomator_description(driver, element_value, text_value)
        elif element_parameter == "ios_uiautomation":
            result = set_text_by_ios_uiautomation(driver, element_value, text_value)
        else:
            elem = driver.find_element_by_xpath("//*[@%s='%s']" % (element_parameter, element_value))
            elem.click()
            elem.send_keys(text_value)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Entered text on element successfully", 1)
            return "passed"

        if result == "passed":
            CommonUtil.ExecLog(sModuleInfo, "Entered text successfully", 1)
            return "passed"
        elif result == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to enter text.", 3)
            return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not set text.  Error: %s" % (Error_Detail), 3)
        return "failed"


# Method to enter text in a text box and press enter to search of something
def Set_Text_Enter(element_parameter, element_value, text_value):
    # !!! Should be removed - can be performed with two sequential actions (text & click, element & ENTER key)
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Inside Enter Text In Text Box function", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to set text in the textbox...", 1)

        #elem = driver.find_element_by_xpath("//*[@%s='%s']" % (element_parameter, element_value))
        elem = Get_Single_Element(element_parameter, element_value)
        elem.click()
        elem.send_keys(text_value + "\n")
        CommonUtil.ExecLog(sModuleInfo, "Entered text on element successfully", 1)
        return "passed"
        CommonUtil.ExecLog(sModuleInfo, "Entered and searched text successfully", 1)

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not set text and search.  Error: %s" % (Error_Detail), 3)
        return "failed"

# Method to enter texts in a text box; step data passed on by the user
def Enter_Text_In_Text_Box(step_data):
    # !!! Should be removed - can be performed with two sequential actions (text & click, element & ENTER key)
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Inside Enter Text In Text Box function", 1)
    try:
        # If there are no two separate data-sets, or if the first data-set is not between 1 to 3 items, or if the second data-set doesn't have only 1 item
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):  # or (len(step_data[1]) != 1)):
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
            return "failed"
        else:
            element_step_data = step_data[0][0:len(step_data[0]) - 1:1]
            returned_step_data_list = Validate_Step_Data(element_step_data)
            # returned_step_data_list = Validate_Step_Data(step_data[0])
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1],
                                          returned_step_data_list[2], returned_step_data_list[3],
                                          returned_step_data_list[4])
                    text_value = step_data[0][len(step_data[0]) - 1][2]
                    # text_value = step[1][0][2]
                    # text_value=step_data[1][0][1]
                    Element.click()
                    Element.clear()
                    Element.set_value(text_value)
                    Element.click()
                    CommonUtil.TakeScreenShot(sModuleInfo)
                    CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s" % text_value,
                                       1)
                    return "passed"
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = (
                    (str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
                        exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo,
                                       "Could not select/click your element.  Error: %s" % (Error_Detail), 3)
                    return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find your element.  Error: %s" % (Error_Detail), 3)
        return "failed"

def Swipe(x_start, y_start, x_end, y_end, duration = 1000):
    ''' Perform single swipe gesture with provided start and end positions '''
    # duration in mS - how long the gesture should take
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting to swipe the screen...", 1)
        driver.swipe(x_start, y_start, x_end, y_end, duration)
        CommonUtil.ExecLog(sModuleInfo, "Swiped the screen successfully", 1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to swipe. %s" % Error_Detail, 3)
        return "failed"

def swipe_handler(action_value):
    ''' Swipe screen based on user input '''
    # Functions: General swipe (up/down/left/right), multiple swipes (X coordinate (from-to), Y coordinate (from-to), stepsize)
    # action_value: comma delimited string containing swipe details
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Starting swipe handler", 1)

    # Get screen size for calculations
    window_size = get_window_size()
    if window_size == 'failed':
        return 'failed'
    w = int(window_size['width'])
    h = int(window_size['height'])

    # Sanitize input
    action_value = str(action_value) # Convert to string
    action_value = action_value.replace(' ','') # Remove spaces
    action_value = action_value.lower() # Convert to lowercase
    
    # Specific swipe dimensions given - just pass to swipe()
    if action_value.count(',') == 3:
        CommonUtil.ExecLog(sModuleInfo, "Swipe type: Single", 1)
        x1, y1, x2, y2 = action_value.split(',')
        Swipe(int(x1), int(y1), int(x2), int(y2))
    
    # Check for and handle simple gestures (swipe up/down/left/right), and may have a set number of swipes to exceute
    elif action_value.count(',') == 0 or action_value.count(',') == 1:
        # Process number of swipes as well
        if action_value.count(',') == 1:
            action_value, count = action_value.split(',')
            count = int(count)
        else:
            count = 1
        CommonUtil.ExecLog(sModuleInfo, "Swipe type: Basic %s with a count of %d" % (action_value, count), 1)
            
        # Check for direction and calculate accordingly
        if action_value == 'up':
            x1 = 50 * w / 100 # Middle horizontal
            x2 = x1 # Midle horizontal
            y1 = 75 * h / 100 # 75% down 
            y2 = 1 # To top
        elif action_value == 'down':
            x1 = 50 * w / 100 # Middle horizontal
            x2 = x1 # Midle horizontal
            y1 = 25 * h / 100 # 25% down 
            y2 = h - 1 # To bottom
        elif action_value == 'left':
            x1 = 90 * w / 100 # Start 90% on right
            x2 = 10 * w / 100 # End 10% on left
            y1 = 50 * h / 100 # Middle vertical 
            y2 = y1 # Middle vertical
        elif action_value == 'right':
            x1 = 10 * w / 100 # Start 10% on left
            x2 = 90 * w / 100 # End 90% on right
            y1 = 50 * h / 100 # Middle vertical
            y2 = y1 # Middle vertical

        # Perform swipe as many times as specified, or once if not specified 
        for i in range(0, count):
            driver.swipe(x1, y1, x2, y2)
            wait(1) # Small sleep, so action animation (if any) can complete
        
    # Handle a series of almost identical gestures (swipe horizontally at different locations for example)
    elif action_value.count(',') == 2:
        # Split input into separate parameters
        horizontal, vertical, stepsize = action_value.split(',')
        CommonUtil.ExecLog(sModuleInfo, "Swipe type: Multiple", 1)
        
        # Stepsize - How far to skip
        if stepsize.isdigit(): # Stepsize given in pixels
            stepsize = int(stepsize)
        elif '%' in stepsize: # Stepsize given as a percentage
            stepsize = int(stepsize.replace('%', '')) # Convert to integer
            stepsize = stepsize * h / 100 # Convert from percentage to pixels
        elif stepsize == 'none':
            stepsize = 1
        elif stepsize == 'small':
            stepsize = 50
        elif stepsize == 'medium':
            stepsize = 100
        elif stepsize == 'large' or stepsize == 'big':
            stepsize = 250
        
        # Horizontal - Start and end
        xstart, xstop = horizontal.split('-')
        if xstart.isdigit(): # X given in pixels
            xstart = int(xstart)
            xstop = int(xstop)
        elif '%' in horizontal: # X given in percentage
            xstart = int(xstart.replace('%', '')) # Convert to integer
            xstart = xstart * w / 100 # Convert from percentage to pixels
            xstop = int(xstop.replace('%', '')) # Convert to integer
            xstop = xstop * w / 100 # Convert from percentage to pixels
            if xstart <= 0: # driver.swipe fails if we are outside the boundary, so correct any values necessary
                xstart = 1
            if xstop >= w:
                xstop = w - 1
        elif horizontal == 'left-right': # Replace descriptive words with default values for them (FROM-TO)
            xstart = 1
            xstop = w - 1
        elif horizontal == 'right-left': # Replace descriptive words with default values for them (FROM-TO)
            xstart = w - 1
            xstop = 1
        
        # Vertical - Start and end
        ystart, ystop = vertical.split('-')
        if ystart.isdigit(): # X given in pixels
            ystart = int(ystart)
            ystop = int(ystop)
        elif '%' in vertical: # X given in percentage
            ystart = int(ystart.replace('%', '')) # Convert to integer
            ystart = ystart * h / 100 # Convert from percentage to pixels
            ystop = int(ystop.replace('%', '')) # Convert to integer
            ystop = ystop * h / 100 # Convert from percentage to pixels
            if ystart <= 0: # driver.swipe fails if we are outside the boundary, so correct any values necessary
                ystart = 1
            if ystop >= h:
                ystop = h - 1
        elif vertical == 'top-bottom': # Replace descriptive words with default values for them (FROM-TO)
            ystart = 1
            ystop = h - 1
        elif vertical == 'bottom-top': # Replace descriptive words with default values for them (FROM-TO)
            ystart = h - 1
            ystop = 1
            stepsize *= -1 # Convert stepsize to negative, so range() works as expected
    
        # Perform swipe given computed dimensions above
        for y in range(ystart, ystop, stepsize): # For each row, assuming stepsize, swipe and move to next row
            result = Swipe(xstart, y, xstop, y) # Swipe screen - y must be the same for horizontal swipes
            if result == 'failed':
                return 'failed'

    # Invalid value
    else:
        CommonUtil.ExecLog(sModuleInfo, "The swipe data you entered is incorrect. Please provide accurate information on the data set(s).", 3) 
        return 'failed'

    # Swipe complete
    CommonUtil.ExecLog(sModuleInfo, "Swipe completed successfully", 1)    
    return 'passed'

def Tap(element_parameter, element_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting to tap the element...", 1)
        #element_data = Validate_Step_Data(step_data)
        elem = Get_Element(element_parameter, element_value)
        if elem.is_enabled():
            action = TouchAction(driver)
            action.tap(elem).perform()
            CommonUtil.ExecLog(sModuleInfo, "Tapped on element successfully", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to tap. The element is disabled.", 3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to tap. %s" % Error_Detail, 3)
        return "failed"

def read_screen_heirarchy():
    ''' Read the XML string of the device's GUI and return it '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    
    try:
        data = driver.page_source # Read screen and get xml formatted text
        CommonUtil.ExecLog(sModuleInfo,"Read screen heirarchy successfully",1)
        if data:
            return data
        else:
            return False
    except:
        CommonUtil.ExecLog(sModuleInfo,"Read screen heirarchy unsuccessfully",3)
        return False

def tap_location(positions):
    ''' Tap the provided position using x,y cooridnates '''
    # positions: list containing x,y coordinates
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        driver.tap(positions) # Tap the location (must be in list format)
        CommonUtil.ExecLog(sModuleInfo,"Tapped on location successfully",1)
        return 'passed'
    except:
        CommonUtil.ExecLog(sModuleInfo,"Tapped on location unsuccessfully",3)
        return 'failed'
    
def get_element_location_by_id(_id):
    ''' Find and return an element's x,y coordinates '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    
    try:
        positions = []
        elem = locate_element_by_id(driver, _id) # Get element object for given id
        location = elem.location # Get element x,y coordinates
        positions.append((location['x'], location['y'])) # Put them on an array - Needs to be in this format for dirver.tap()
        CommonUtil.ExecLog(sModuleInfo,"Retreived location successfully",1)
        return positions # Return array
    except:
        CommonUtil.ExecLog(sModuleInfo,"Retreived location unsuccessfully",3)
        return 'failed'
        

def get_window_size():
    ''' Read the device's LCD resolution / screen size '''
    # Returns a dictionary of width and height
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    
    try:
        return driver.get_window_size() # Get window resolution in dictionary
        CommonUtil.ExecLog(sModuleInfo,"Read window size successfully",1)
    except:
        CommonUtil.ExecLog(sModuleInfo,"Read window size unsuccessfully",1)
        return 'failed'
    
    

################################### APPIUM COMMANDS ###################################
################################### APPIUM COMMANDS ###################################
################################### APPIUM COMMANDS ###################################




################################# SEQUENTIAL ACTIONS HELPER FUNCTIONS ###################################
################################# SEQUENTIAL ACTIONS HELPER FUNCTIONS ###################################
################################# SEQUENTIAL ACTIONS HELPER FUNCTIONS ###################################





    # Method to get the elements based on type - more methods may be added in the future
    # Called by: Get_Elements
def Get_Single_Element(parameter, value, parent=False):
    # http://selenium-python.readthedocs.io/locating-elements.html
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        All_Elements = []
        if parent == False:
            if parameter == "name":
                All_Elements = driver.find_element_by_name(value)
            elif parameter == "id":
                All_Elements = driver.find_element_by_id(value)
            elif parameter == "accessibility_id":
                All_Elements = driver.find_element_by_accessibility_id(value)
            elif parameter == "class_name":
                All_Elements = driver.find_element_by_class_name(value)
            elif parameter == "xpath":
                #All_Elements = driver.find_element_by_xpath(value)
                All_Elements == driver.find_element_by_xpath("//*[@%s='%s']" % (parameter, value))
            elif parameter == "android_uiautomator_text":
                All_Elements == driver.find_element_by_android_uiautomator('new UiSelector().text(' + value + ')')
            elif parameter == "android_uiautomator_description":
                All_Elements == driver.find_element_by_android_uiautomator(
                    'new UiSelector().description(' + value + ')')
            elif parameter == "ios_uiautomation":
                All_Elements == driver.find_element_by_ios_uiautomation('.elements()[0]')
            else:
                All_Elements == driver.find_element_by_xpath("//*[@%s='%s']"%(parameter, value))

        elif parent == True:
            if parameter == "name":
                All_Elements = driver.find_element_by_xpath("//*[@text='%s']" % value)
            elif parameter == "id":
                All_Elements = driver.find_element_by_id(value)
            elif parameter == "accessibility_id":
                All_Elements = driver.find_element_by_accessibility_id(value)
            elif parameter == "class_name":
                All_Elements = driver.find_element_by_class_name(value)
            elif parameter == "xpath":
                #All_Elements = driver.find_element_by_xpath(value)
                All_Elements == driver.find_element_by_xpath("//*[@%s='%s']" % (parameter, value))
            elif parameter == "android_uiautomator_text":
                All_Elements == driver.find_element_by_android_uiautomator('new UiSelector().text(' + value + ')')
            elif parameter == "android_uiautomator_description":
                All_Elements == driver.find_element_by_android_uiautomator(
                    'new UiSelector().description(' + value + ')')
            elif parameter == "ios_uiautomation":
                All_Elements == driver.find_element_by_ios_uiautomation('.elements()[0]')
            else:
                All_Elements == driver.find_element_by_xpath("//*[@%s='%s']"%(parameter,value))

        return All_Elements
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to get the element.  Error: %s" % (Error_Detail), 3)
        return "failed"


# Method to get the elements based on type - more methods may be added in the future
# Called by: Get_Elements
def Get_All_Elements(parameter, value, parent=False):
    # http://selenium-python.readthedocs.io/locating-elements.html
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        All_Elements = []
        if parent == False:
            if parameter == "name":
                All_Elements = driver.find_elements_by_name(value)
            elif parameter == "id":
                All_Elements = driver.find_elements_by_id(value)
            elif parameter == "accessibility_id":
                All_Elements = driver.find_elements_by_accessibility_id(value)
            elif parameter == "class_name":
                All_Elements = driver.find_elements_by_class_name(value)
            elif parameter == "xpath":
                All_Elements = driver.find_elements_by_xpath(value)
            elif parameter == "android_uiautomator_text":
                All_Elements == driver.find_elements_by_android_uiautomator('new UiSelector().text('+value+')')
            elif parameter == "android_uiautomator_description":
                All_Elements == driver.find_elements_by_android_uiautomator('new UiSelector().description('+value+')')
        elif parent == True:
            if parameter == "name":
                All_Elements = driver.find_elements_by_name(value)
            elif parameter == "id":
                All_Elements = driver.find_elements_by_id(value)
            elif parameter == "accessibility_id":
                All_Elements = driver.find_elements_by_accessibility_id(value)
            elif parameter == "class_name":
                All_Elements = driver.find_elements_by_class_name(value)
            elif parameter == "xpath":
                All_Elements = driver.find_elements_by_xpath(value)
            elif parameter == "android_uiautomator_text":
                All_Elements == driver.find_elements_by_android_uiautomator('new UiSelector().text('+value+')')
            elif parameter == "android_uiautomator_description":
                All_Elements == driver.find_elements_by_android_uiautomator('new UiSelector().description('+value+')')

        return All_Elements
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to get the element.  Error: %s" % (Error_Detail), 3)
        return "failed"




def Element_Validation(All_Elements_Found):#, index):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        #index = int(index)
        return_element = []
        all_visible_elements = []
        all_invisible_elements = []
        if All_Elements_Found == []:
            CommonUtil.ExecLog(sModuleInfo, "Could not find your element by given parameters and values", 3)
            return "failed"
        elif len(All_Elements_Found) == 1:
            for each_elem in All_Elements_Found:
                #Case 1: Found only one invisible element - pass with warning
                if each_elem.is_displayed() == False:
                    return_element.append(each_elem)
                    CommonUtil.ExecLog(sModuleInfo, "Found one invisible element by given parameters and values", 2)
                #Case 2: Found only one visible element - pass
                elif each_elem.is_displayed() == True:
                    return_element.append(each_elem)
                    CommonUtil.ExecLog(sModuleInfo, "Found one visible element by given parameters and values", 1)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Could not find element by given parameters and values", 3)
                    return "failed"
            return return_element[0]

        elif len(All_Elements_Found) > 1:
            CommonUtil.ExecLog(sModuleInfo, "Found more than one element by given parameters and values, validating visible and invisible elements. Total number of elements found: %s"%(len(All_Elements_Found)), 2)
            for each_elem in All_Elements_Found:
                if each_elem.is_displayed() == True:
                    all_visible_elements.append(each_elem)
                else:
                    all_invisible_elements.append(each_elem)
            #sequential logic - if at least one is_displayed() elements, show that, else allow invisible elements
            if len(all_visible_elements) > 0:
                CommonUtil.ExecLog(sModuleInfo, "Found at least one visible element for given parameters and values, returning the first one or by the index specified", 2)
                return_element = all_visible_elements
            else:
                CommonUtil.ExecLog(sModuleInfo, "Did not find a visible element, however, invisible elements present", 2)
                return_element = all_invisible_elements
            return return_element[0]#[index]

        else:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element by given parameters and values", 3)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to get the element.  Error: %s"%(Error_Detail), 3)
        return "failed"


def Wait(time_to_wait): #!!! To be replaced with Wait_For_New_Element()
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting waiting for %s seconds.." % time_to_wait, 1)
        #function_data = Validate_Step_Data(step_data)
        driver.implicitly_wait(float(time_to_wait))
        #time.sleep(float(time_to_wait))
        CommonUtil.ExecLog(sModuleInfo, "Waited successfully", 1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to wait. %s" % Error_Detail, 3)
        return "failed"



# Validating text from an element given information regarding the expected text
def Validate_Text(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Text_Data", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            dimension = driver.get_window_size('current')
            print dimension
            
            for each in step_data[0]:
                if each[0] == "current_page":
                    try:
                        Element = Get_Element_Appium('tag', 'html')
                        break
                    except Exception, e:
                        CommonUtil.ExecLog(sModuleInfo, "Could not get element from the current page.", 3)
                        CommonUtil.Exception_Handler(sys.exc_info())
                else:
                    element_step_data = Get_Element_Step_Data_Appium(step_data)
                    returned_step_data_list = Validate_Step_Data(element_step_data)
                    if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                        return "failed"
                    else:
                        try:
                            Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                            break
                        except Exception, e:
                            CommonUtil.ExecLog(sModuleInfo, "Could not get element based on the information provided.", 3)
                            CommonUtil.Exception_Handler(sys.exc_info())            
 
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

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not compare text as requested.  Error: %s" % (Error_Detail), 3)
        return "failed"


#Validating text from an element given information regarding the expected text
def Save_Text(step_data, variable_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Save Text", 1)
    try:
        if ((1 < len(step_data[0][0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return "failed"
        else:
            for each in step_data:
                element_step_data = Get_Element_Step_Data_Appium([step_data])
                returned_step_data_list = Validate_Step_Data(element_step_data)
                if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                    return "failed"
                else:
                    try:
                        Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                        break

                    except Exception:
                        errMsg = "Could not get element based on the information provided."
                        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

            list_of_element_text = Element.text.split('\n')
            visible_list_of_element_text = ""
            for each_text_item in list_of_element_text:
                if each_text_item != "":
                    visible_list_of_element_text+=each_text_item

            result = CommonUtil.Set_Shared_Variables(variable_name, visible_list_of_element_text)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Value of Variable '%s' could not be saved!!!", 3)
                return "failed"
            else:
                CommonUtil.Show_All_Shared_Variables()
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Validating text from an element given information regarding the expected text
def Compare_Variables(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare Variables", 1)
    try:
        element_step_data = Get_Element_Step_Data_Appium([step_data])
        if ((element_step_data == []) or (element_step_data == "failed")):
            return "failed"
        else:
            pass_count = 0
            fail_count = 0
            variable_list1 = []
            variable_list2 = []
            result = []
            for each_step_data_item in step_data:
                if each_step_data_item[1]!="action":
                    if '%|' in each_step_data_item[0].strip():
                        previous_name = each_step_data_item[0].strip()
                        new_name = CommonUtil.get_previous_response_variables_in_strings(each_step_data_item[0].strip())
                        tuple1 = ('Variable',"'%s'"%previous_name,new_name)
                    else:
                        tuple1 = ('Text','',each_step_data_item[0].strip())
                    variable_list1.append(tuple1)

                    if '%|' in each_step_data_item[2].strip():
                        previous_name = each_step_data_item[2].strip()
                        new_name = CommonUtil.get_previous_response_variables_in_strings(each_step_data_item[2].strip())
                        tuple2 = ('Variable',"'%s'"%previous_name,new_name)
                    else:
                        tuple2 = ('Text','',each_step_data_item[2].strip())
                    variable_list2.append(tuple2)


            for i in range(0,len(variable_list1)):
                if variable_list1[i][2] == variable_list2[i][2]:
                    result.append(True)
                    pass_count+=1
                else:
                    result.append(False)
                    fail_count+=1

            CommonUtil.ExecLog(sModuleInfo,"###Variable Comaparison Results###",1)
            CommonUtil.ExecLog(sModuleInfo,"Matched Variables: %d"%pass_count,1)
            CommonUtil.ExecLog(sModuleInfo, "Not Matched Variables: %d" % fail_count, 1)

            for i in range(0, len(variable_list1)):
                if result[i] == True:
                    CommonUtil.ExecLog(sModuleInfo,"Item %d. %s %s - %s :: %s %s - %s : Matched"%(i+1,variable_list1[i][0],variable_list1[i][1],variable_list1[i][2],variable_list2[i][0],variable_list2[i][1],variable_list2[i][2]),1)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Item %d. %s %s - %s :: %s %s - %s : Not Matched" % (i + 1, variable_list1[i][0], variable_list1[i][1], variable_list1[i][2], variable_list2[i][0],variable_list2[i][1], variable_list2[i][2]),3)

            if fail_count > 0:
                CommonUtil.ExecLog(sModuleInfo,"Error: %d item(s) did not match"%fail_count,3)
                return "failed"
            else:
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())




################################# SEQUENTIAL ACTIONS HELPER FUNCTIONS ###################################
################################# SEQUENTIAL ACTIONS HELPER FUNCTIONS ###################################
################################# SEQUENTIAL ACTIONS HELPER FUNCTIONS ###################################





################################# TO BE MERGED WITH EXISTING FUNCTIONS ###################################
################################# TO BE MERGED WITH EXISTING FUNCTIONS ###################################
################################# TO BE MERGED WITH EXISTING FUNCTIONS ###################################

def locate_element_by_id(driver, _id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by id: %s"%_id,1)
        elem = driver.find_element_by_id(_id)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)

def locate_elements_by_id(driver, _id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate elements by id: %s"%_id,1)
        elems = driver.find_elements_by_id(_id)
        return elems
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate elements. %s"%Error_Detail, 3)

    
def locate_element_by_name(driver, _name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by name: %s"%_name,1)
        elem = driver.find_element_by_name(_name)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)
    
    
def locate_element_by_class_name(driver, _class):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by class: %s"%_class,1)
        elem = driver.find_element_by_class_name(_class)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)
    
    
def locate_element_by_xpath(driver, _classpath):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by xpath: %s"%_classpath,1)
        elem = driver.find_element_by_xpath(_classpath)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)
    
def locate_element_by_accessibility_id(driver, _id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by accessibility id: %s"%_id,1)
        elem = driver.find_element_by_accessibility_id(_id)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)


def locate_element_by_android_uiautomator_text(driver, _text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by android uiautomator text: %s"%_text,1)
        elem = driver.find_element_by_android_uiautomator('new UiSelector().text('+_text+')')
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)


def locate_element_by_android_uiautomator_description(driver, _description):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by android uiautomator description: %s"%_description,1)
        elem = driver.find_element_by_android_uiautomator('new UiSelector().description('+_description+')')
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)


def locate_element_by_ios_uiautomation(driver, _description):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by ios uiautomatoion: %s"%_description,1)
        elem = driver.find_element_by_ios_uiautomation('.elements()[0]')
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)


    
def click_element_by_id(driver, _id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by id: %s"%_id,1)
        elem = locate_element_by_id(driver, _id)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"
    
def click_element_by_name(driver, _name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by name: %s"%_name,1)
        elem = locate_element_by_name(driver, _name)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"
    
def click_element_by_class_name(driver, _class):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by class: %s"%_class,1)
        elem = locate_element_by_class_name(driver, _class)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"
    
def click_element_by_xpath(driver, _classpath):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by xpath: %s"%_classpath,1)
        elem = locate_element_by_xpath(driver, _classpath)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"
    
def click_element_by_accessibility_id(driver, _id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by accessibility id: %s"%_id,1)
        elem = locate_element_by_accessibility_id(driver, _id)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"
    
def click_element_by_android_uiautomator_text(driver, _text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by android uiautomator text: %s"%_text,1)
        elem = locate_element_by_android_uiautomator_text(driver, _text)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"
    
def click_element_by_android_uiautomator_description(driver, _description):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by android uiautomator description: %s"%_description,1)
        elem = locate_element_by_android_uiautomator_description(driver, _description)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"


def click_element_by_ios_uiautomation(driver, _description):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by android uiautomator description: %s"%_description,1)
        elem = locate_element_by_ios_uiautomation(driver, _description)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"

#text



def set_text_by_id(driver, _id, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by id: %s"%_id,1)
        elem = locate_element_by_id(driver, _id)
        if elem.is_displayed():
            elem.click()
            #driver.hide_keyboard()
            #elem.set_value(text)
            #driver.set_value(elem, text)
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"
        #driver.set_value(elem, text)

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s"%Error_Detail, 3)
        return "failed"


def set_text_by_name(driver, _name, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by name: %s"%_name,1)
        elem = locate_element_by_name(driver, _name)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s"%Error_Detail, 3)
        return "failed"


def set_text_by_class_name(driver, _class, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by class: %s"%_class,1)
        elem = locate_element_by_class_name(driver, _class)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s"%Error_Detail, 3)
        return "failed"


def set_text_by_xpath(driver, _classpath, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by xpath: %s"%_classpath,1)
        elem = locate_element_by_xpath(driver, _classpath)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s"%Error_Detail, 3)
        return "failed"


def set_text_by_accessibility_id(driver, _id, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by accessibility id: %s"%_id,1)
        elem = locate_element_by_accessibility_id(driver, _id)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s" % Error_Detail, 3)
        return "failed"


def set_text_by_android_uiautomator_text(driver, _text, text_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to click on element by android uiautomator text: %s" % _text, 1)
        elem = locate_element_by_android_uiautomator_text(driver, _text)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text_value)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s" % Error_Detail, 3)
        return "failed"


def set_text_by_android_uiautomator_description(driver, _description, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,
                           "Trying to click on element by android uiautomator description: %s" % _description, 1)
        elem = locate_element_by_android_uiautomator_description(driver, _description)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s" % Error_Detail, 3)
        return "failed"


def set_text_by_ios_uiautomation(driver, _description, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,
                           "Trying to click on element by android uiautomator description: %s" % _description, 1)
        elem = locate_element_by_ios_uiautomation(driver, _description)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s" % Error_Detail, 3)
        return "failed"

################################# TO BE MERGED WITH EXISTING FUNCTIONS ###################################
################################# TO BE MERGED WITH EXISTING FUNCTIONS ###################################
################################# TO BE MERGED WITH EXISTING FUNCTIONS ###################################







################################# NEW AND UNUSED FUNCTIONS ###################################
################################# NEW AND UNUSED FUNCTIONS ###################################
################################# NEW AND UNUSED FUNCTIONS ###################################

#Method to get the elements based on type - more methods may be added in the future
#Called by: Get_Element
def Get_All_Elements_Appium(parameter,value,parent=False):
    #http://selenium-python.readthedocs.io/locating-elements.html
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if parent == False:
            if parameter == "id":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_id(value))
            elif parameter == "name":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_name(value))
            elif parameter == "class_name":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_class_name(value))
            elif parameter == "xpath":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_xpath(value))
            elif parameter == "accessibility_id":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_accessibility_id(value))    
            elif parameter == "android_uiautomator":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_android_uiautomator(value))    
            elif parameter == "ios_uiautomation":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_ios_uiautomation(value))    
            else:
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_xpath("//*[@%s='%s']" %(parameter,value)))
        else:
            if parameter == "id":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_id(value))
            elif parameter == "name":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_name(value))
            elif parameter == "class_name":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_class_name(value))
            elif parameter == "xpath":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_xpath(value))
            elif parameter == "accessibility_id":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_accessibility_id(value))    
            elif parameter == "android_uiautomator":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_android_uiautomator(value))    
            elif parameter == "ios_uiautomation":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_ios_uiautomation(value))    
            else:
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_xpath("//*[@%s='%s']" %(parameter,value)))    
        
        return All_Elements
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())




#Method to click on element; step data passed on by the user
def Click_Element_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Click_Element_Appium", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            #element_step_data = step_data[0][0:len(step_data[0])-1:1]
            element_step_data = Get_Element_Step_Data_Appium(step_data)            
            returned_step_data_list = Validate_Step_Data(element_step_data) 
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                    if Element.is_enabled():
                        Element.click()
                        CommonUtil.TakeScreenShot(sModuleInfo)
                        CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element with given parameters and values", 1)
                        return "passed"
                    else:
                        CommonUtil.TakeScreenShot(sModuleInfo)
                        CommonUtil.ExecLog(sModuleInfo, "Element not enabled. Unable to click.", 3)
                        return "failed"
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()        
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not select/click your element.  Error: %s"%(Error_Detail), 3)
                    return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find/click your element.  Error: %s"%(Error_Detail), 3)
        return "failed"
    
    
def Tap_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Tap_Appium", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:    
            element_step_data = Get_Element_Step_Data_Appium(step_data)            
            returned_step_data_list = Validate_Step_Data(element_step_data) 
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                    if Element.is_enabled():
                        action = TouchAction(driver)
                        action.tap(Element).perform()
                        CommonUtil.ExecLog(sModuleInfo, "Tapped on element successfully", 1)
                        return "passed"
                    else:
                        CommonUtil.TakeScreenShot(sModuleInfo)
                        CommonUtil.ExecLog(sModuleInfo, "Element not enabled. Unable to click.", 3)
                        return "failed"
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()        
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not select/click your element.  Error: %s"%(Error_Detail), 3)
                    return "failed"
                
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to tap. %s" % Error_Detail, 3)
        return "failed"

# def Double_Tap_Appium_asifurrouf

def Double_Tap_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function:Double_Tap_Appium", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
            return "failed"
        else:
            element_step_data = Get_Element_Step_Data_Appium(step_data)
            returned_step_data_list = Validate_Step_Data(element_step_data)
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1],
                                                 returned_step_data_list[2], returned_step_data_list[3],
                                                 returned_step_data_list[4])
                    if Element.is_enabled():
                        action = TouchAction(driver)

                        action.press(Element).wait(100).release().press(Element).wait(100).release().perform()

                        CommonUtil.ExecLog(sModuleInfo, "Double Tapped on element successfully", 1)
                        return "passed"
                    else:
                        CommonUtil.TakeScreenShot(sModuleInfo)
                        CommonUtil.ExecLog(sModuleInfo, "Element not enabled. Unable to click.", 3)
                        return "failed"
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
                        exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not select/click your element.  Error: %s" % (Error_Detail),
                                       3)
                    return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to tap. %s" % Error_Detail, 3)
        return "failed"

# Long_Press_Appium_asifurrouf_fixed Long Press time

def Long_Press_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Long_Press_Appium", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
            return "failed"
        else:
            element_step_data = Get_Element_Step_Data_Appium(step_data)
            returned_step_data_list = Validate_Step_Data(element_step_data)
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1],
                                                 returned_step_data_list[2], returned_step_data_list[3],
                                                 returned_step_data_list[4])
                    if Element.is_enabled():
                        action = TouchAction(driver)

                        action.long_press(Element, 150, 10).release().perform()

                        CommonUtil.ExecLog(sModuleInfo, "Long Pressed on element successfully", 1)
                        return "passed"
                    else:
                        CommonUtil.TakeScreenShot(sModuleInfo)
                        CommonUtil.ExecLog(sModuleInfo, "Element not enabled. Unable to click.", 3)
                        return "failed"
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
                        exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not select/click your element.  Error: %s" % (Error_Detail),
                                       3)
                    return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to tap. %s" % Error_Detail, 3)
        return "failed"

#asifurrouf_long_press_double_tap

#Method to enter texts in a text box; step data passed on by the user
def Enter_Text_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Enter_Text_Appium", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            element_step_data=Get_Element_Step_Data_Appium(step_data)
            returned_step_data_list = Validate_Step_Data(element_step_data) 
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
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
                    CommonUtil.TakeScreenShot(sModuleInfo)
                    CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s"%text_value, 1)
                    return "passed"
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()        
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not enter text in the desired element.  Error: %s"%(Error_Detail), 3)
                    return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find your element.  Error: %s"%(Error_Detail), 3)
        return "failed"



def iOS_Keystroke_Key_Mapping(keystroke):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: iOS_Keystroke_Key_Mapping", 1)
    try:
        if keystroke == "RETURN":
            driver.keyevent(13)
        #elif keystroke == "GO BACK":
        #    driver.back()
        elif keystroke == "SPACE":
            driver.keyevent(32)
        elif keystroke == "BACKSPACE":
            driver.keyevent(8)
        elif keystroke == "CALL":
            driver.keyevent(5)            
        elif keystroke == "END CALL":
            driver.keyevent(6)
                                     
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not press enter for your element.  Error: %s"%(Error_Detail), 3)
        return "failed"   


#Method to click on element; step data passed on by the user
def Keystroke_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Keystroke_Appium", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            for each in step_data[0]:
                if each[1]=="action":
                    if each[0]=="iOS keystroke":
                        keystroke_value=(each[2]).upper()
                        result = iOS_Keystroke_Key_Mapping(keystroke_value)
                    elif each[0] == "Android keystroke":
                        keystroke_value=(each[2]).upper()
                        result = Android_Keystroke_Key_Mapping(keystroke_value)
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
              
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not enter keystroke.  Error: %s"%(Error_Detail), 3)
        return "failed"


"""NEED TO BE CHANGED QUITE A BIT. CURRENT_PAGE WILL BE MODIFIED TO HAVE SOMETHING ELSE"""
#Validating text from an element given information regarding the expected text
def Validate_Text_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Text", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return "failed"
        else:
            for each in step_data[0]:
                if each[0] == "current_page":
                    try:
                        Element = Get_Element_Appium('tag', 'html')
                        break
                    except Exception, e:
                        CommonUtil.ExecLog(sModuleInfo, "Could not get element from the current page.", 3)
                        CommonUtil.Exception_Handler(sys.exc_info())
                else:
                    element_step_data = Get_Element_Step_Data_Appium(step_data)
                    returned_step_data_list = Validate_Step_Data(element_step_data)
                    if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                        return "failed"
                    else:
                        try:
                            Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                            break
                        except Exception, e:
                            CommonUtil.ExecLog(sModuleInfo, "Could not get element based on the information provided.", 3)
                            CommonUtil.Exception_Handler(sys.exc_info())
 
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
 
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not compare text as requested.  Error: %s" % (Error_Detail), 3)
        return "failed"

################################# NEW AND UNUSED FUNCTIONS ###################################
################################# NEW AND UNUSED FUNCTIONS ###################################
################################# NEW AND UNUSED FUNCTIONS ###################################



