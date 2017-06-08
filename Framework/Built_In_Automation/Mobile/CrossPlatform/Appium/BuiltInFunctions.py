# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
# Android environment
from appium import webdriver
import os, sys, time, inspect, json
import subprocess,re
from Framework.Utilities import CommonUtil, FileUtilities
from Framework.Built_In_Automation.Mobile.Android.adb_calls import adbOptions
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources


passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True','1','Success','success','SUCCESS',True]
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE','0',False]
skipped_tag_list=['skip','SKIP','Skip','skipped','SKIPPED','Skipped']

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

# Recall appium driver, if not already set - needed between calls in a Zeuz test case
global driver
driver = None
if Shared_Resources.Test_Shared_Variables('appium_driver'): # Check if driver is already set in shared variables
    driver = Shared_Resources.Get_Shared_Variables('appium_driver') # Retreive appium driver

# Recall dependency, if not already set
dependency = {'Mobile':'Android'} #!!! TEMP - Replace with None for production
if Shared_Resources.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables('dependency') # Retreive appium driver
 

global WebDriver_Wait 
WebDriver_Wait = 20

################################### UNUSED - SEEMS TO INVOLVE SETTING UP APPIUM #########################################
global APPIUM_DRIVER_LIST
APPIUM_DRIVER_LIST = {}


def getDriversList():
    return APPIUM_DRIVER_LIST


def getDriver(index):
    try:
        return APPIUM_DRIVER_LIST[index]
    except Exception, e:
        return False


def addDriver(position, driver, port):
    try:
        APPIUM_DRIVER_LIST.update({position: {'driver':driver, 'port': port}})
        return True
    except Exception, e:
        return False


def start_selenium_hub(file_location = os.path.join(FileUtilities.get_home_folder(), os.path.join('Desktop', 'selenium-server-standalone-2.43.1.jar'))):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting Selenium Hub", 1)
        console_run("java -jar %s -role hub" % file_location)
        CommonUtil.ExecLog(sModuleInfo, "Selenium Hub Command given", 1)
        return True
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to Start Selenium Hub: Error:%s" % (Error_Detail), 3)
        return False

def console_run(run_command):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        os.system("gnome-terminal --working-directory %s -e 'bash -c \"%s ;exec bash\"'" % (FileUtilities.get_home_folder(),run_command))
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to run command", 3)
        return False


def init_config_for_device(port_to_connect, device_index, hub_address='127.0.0.1', hub_port=4444, base_location = os.path.join(FileUtilities.get_home_folder(), os.path.join('Desktop', 'appiumConfig')), **kwargs):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        dictJson={
            "configuration":
                {
                    "nodeTimeout": 120,
                    "port": port_to_connect,
                    "hubPort": hub_port,
                    "proxy": "org.openqa.grid.selenium.proxy.DefaultRemoteProxy",
                    "url": "http://%s:%d/wd/hub"%(hub_address,port_to_connect),
                    "hub": "%s:%d/grid/register"%(hub_address, hub_port),
                    "hubHost": "%s"%(hub_address),
                    "nodePolling": 2000,
                    "registerCycle": 10000,
                    "register": True,
                    "cleanUpCycle": 2000,
                    "timeout": 30000,
                    "maxSession": 1
                }
        }
        dictJson.update({'capabilities':[kwargs]})
        if not os.path.exists(base_location):
            FileUtilities.CreateFolder(base_location)
        file_location = os.path.join(base_location, 'nodeConfig%d.json'%device_index)
        with open(file_location, 'w') as txtfile:
            json.dump(dictJson, txtfile)
        #start appium instance
        set_appium_specific_variable()
        start_appium_instances(port_to_connect, file_location)
        return True
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to initiate appium instance for device:%d"%device_index, 3)
        return False


def set_appium_specific_variable():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        env_vars = {'PATH': '', 'LD_LIBRARY_PATH': '', 'ANDROID_HOME': '', 'HOME': ''}
        not_set = False

        for var in env_vars.keys():
            env_value = os.getenv(var)

            if env_value:
                env_vars[var] = env_value

            elif not env_value:
                not_set = True

        if not_set:
            os.environ['PATH'] = env_vars['HOME'] + "/.linuxbrew/bin:" + env_vars['PATH']
            env_vars['PATH'] = env_vars['HOME'] + "/.linuxbrew/bin:" + env_vars['PATH']

            os.environ['LD_LIBRARY_PATH'] = env_vars['HOME'] + "/.linuxbrew/lib:" + env_vars['LD_LIBRARY_PATH']
            env_vars['LD_LIBRARY_PATH'] = env_vars['HOME'] + "/.linuxbrew/lib:" + env_vars['LD_LIBRARY_PATH']

            os.environ['ANDROID_HOME'] = os.path.join(FileUtilities.get_home_folder(), "android-sdk-linux")
            env_vars['ANDROID_HOME'] = os.path.join(FileUtilities.get_home_folder(), "android-sdk-linux")

            os.environ['PATH'] = env_vars['PATH'] + ":" + env_vars['ANDROID_HOME'] + "/tools:" + \
                                 env_vars['ANDROID_HOME'] + "/platform-tools"
            env_vars['PATH'] = env_vars['PATH'] + ":" + env_vars['ANDROID_HOME'] + "/tools:" + \
                               env_vars['ANDROID_HOME'] + "/platform-tools"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set appium variable", 3)
        return False

def start_appium_instances(port_to_connect, file_location, hub_address = '127.0.0.1' ):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        run_command = "appium -a %s -p %d --nodeconfig %s" % (hub_address, port_to_connect, file_location)
        console_run(run_command)
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start appium instance at port :%d"%port_to_connect, 3)
        return False
################################### UNUSED - SEEMS TO INVOLVE SETTING UP APPIUM #########################################

def launch_application(data_set):
    ''' Launch the application the appium instance was created with, and create the instance if necessary '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Launching application", 1)
    
    # Parse data set
    try:
        package_name = '' # Name of application package
        activity_name = '' # Name of application activity
        package_only = False
        for row in data_set: # Find required data
            if row[0] == 'package' and row[1] == 'element parameter':
                if dependency['Mobile'].lower() == 'android':
                    package_name, activity_name = get_program_names(row[2]) # Android only to match a partial package name if provided by the user
                else:
                    package_name = row[2] # IOS package name
                package_only = True
                    
            if not package_only:
                if row[0] == 'launch' and row[1] == 'action':
                    package_name = row[2]
                elif row[0] == 'app activity' and row[1] == 'element parameter':
                    activity_name = row[2]
        
        if package_name == '':
            CommonUtil.ExecLog(sModuleInfo,"Could not find package name", 3)
            return 'failed'
        elif dependency['Mobile'].lower() == 'android' and activity_name == '':
            CommonUtil.ExecLog(sModuleInfo,"Could not find activity name", 3)
            return 'failed'
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    # Launch application
    try:
        if driver == None: # Only create a new appium instance if we haven't already (may be done by install_and_start_driver())
            result = start_appium_driver(package_name, activity_name)
            if result == 'failed':
                return 'failed'
        
        CommonUtil.ExecLog(sModuleInfo,"Sending driver call.",1)
        driver.launch_app() # Launch program configured in the Appium capabilities
        CommonUtil.ExecLog(sModuleInfo,"Launched the application successfully.",1)
        return "passed"
    except Exception:
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
            desired_caps['platformName'] = dependency['Mobile'] # Set platform name
            desired_caps['autoLaunch'] = 'false' # Do not launch application
            desired_caps['fullReset'] = 'false' # Do not clear application cache when complete
            desired_caps['sendKeyStrategy'] = 'setValue' #!!! Needed for send_keys?
            
            if dependency['Mobile'].lower() == 'android':
                CommonUtil.ExecLog(sModuleInfo,"Setting up with Android",1)
                desired_caps['platformVersion'] = adbOptions.get_android_version().strip()
                desired_caps['deviceName'] = adbOptions.get_device_model().strip()
                if package_name:
                    desired_caps['appPackage'] = package_name.strip()
                if activity_name:
                    desired_caps['appActivity'] = activity_name.strip()
                if filename and package_name == '': # User must specify package or file, not both. Specifying filename instructs Appium to install
                    desired_caps['app'] = PATH(filename).strip()
            elif dependency['Mobile'].lower() == 'ios':
                CommonUtil.ExecLog(sModuleInfo,"Setting up with IOS",1)
                desired_caps['platformVersion'] = '10.3' # Read version #!!! Temporarily hard coded
                desired_caps['deviceName'] = 'iPhone' # Read model (only needs to be unique if using more than one)
                desired_caps['bundleId'] = package_name
                desired_caps['udid'] = 'auto' # Device unique identifier - use auto if using only one phone
            else:
                CommonUtil.ExecLog(sModuleInfo, "Invalid dependency: %s" % str(dependency), 3)
                return 'failed'
            CommonUtil.ExecLog(sModuleInfo,"Capabilities: %s" % str(desired_caps),1)
            
            # Create Appium instance with capabilities
            global driver
            driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps) # Create instance
            if driver: # Make sure we get the instance
                Shared_Resources.Set_Shared_Variables('appium_driver', driver) # Save driver instance to make available to other modules
                CommonUtil.ExecLog(sModuleInfo,"Appium driver created successfully.",1)
                return "passed"
            else: # Error during setup, reset
                driver = None
                CommonUtil.ExecLog(sModuleInfo,"Error during Appium setup", 3)
                return 'failed'
        else: # Driver is already setup, don't do anything
            CommonUtil.ExecLog(sModuleInfo,"Driver already configured, not re-doing",1)
            return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
    
    
def teardown_appium(data_set):
    ''' Teardown of appium instance '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Starting Appium cleanup.",1)
    try:
        global driver
        driver.quit() # Tell appium to shutdown instance
        driver = None # Clear driver variable, so next run will be fresh
        Shared_Resources.Set_Shared_Variables('appium_driver', '') # Clear the driver from shared variables
        CommonUtil.ExecLog(sModuleInfo,"Appium cleaned up successfully.",1)
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def close_application(data_set):
    ''' Exit the application '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to close the app",1)
        driver.close_app()
        CommonUtil.ExecLog(sModuleInfo,"Closed the app successfully",1)
        return "passed"
    except Exception:
        errMsg = "Unable to close the application."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    
def reset_application(data_set):
    ''' Resets / clears the application cache '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to reset the app",1)
        driver.reset() # Reset / clear application cache
        CommonUtil.ExecLog(sModuleInfo,"Reset the app successfully",1)
        return "passed"
    except Exception:
        errMsg = "Unable to Reset the application."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    
def install_application(data_set): #app_location, activity_name=''
    ''' Install application to device '''
    # Webdriver does the installation and verification
    # If the user tries to call install again, nothing will happen because we don't want to create another instance. User should teardown(), then install
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Trying to install and then launch the app...", 1)
    
    # Parse data set
    try:
        app_location = '' # File location on disk
        activity_name = '' # Optional value needed for some programs
        for row in data_set: # Find required data
            if row[0] == 'install' and row[1] == 'action':
                app_location = row[2]
            elif row[0] == 'app activity' and row[1] == 'element parameter': # Optional parameter
                activity_name = row[2]
        if app_location == '':
            CommonUtil.ExecLog(sModuleInfo,"Could not find file location", 3)
            return 'failed'
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    try:
        if driver == None: # Only create a new appium instance if we haven't already (may be done by install_and_start_driver())
            result = start_appium_driver('', activity_name, app_location) # Install application and create driver instance. First parameter is always empty. We specify the third parameter with the file, and optionally the second parameter with the activity name if it's needed
            if result == 'failed':
                return 'failed'

        CommonUtil.ExecLog(sModuleInfo,"Installed and launched the app successfully.",1)
        return "passed"
    except Exception:
        errMsg = "Unable to start WebDriver."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def uninstall_application(data_set):
    ''' Uninstalls/removes application from device '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Uninstalling application", 1)
    
    # Parse data set
    try:
        sample_package = False
        app_package = ''
        for row in data_set:
            if row[0].strip() == 'package':
                app_package,app_activity = get_program_names(row[2].strip())
                app_activity=app_package+app_activity
                sample_package = True
        if not sample_package:
            app_package = data_set[0][2]
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to remove app with package name %s"%app_package,1)
        #if driver.is_app_installed(app_package):
            #CommonUtil.ExecLog(sModuleInfo,"App is installed. Now removing...",1)
        if driver == None:
            start_appium_driver(app_package,app_activity)
        driver.remove_app(app_package)
        CommonUtil.ExecLog(sModuleInfo,"App is removed successfully.",1)
        return "passed"
    except Exception:
        errMsg = "Unable to uninstall"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


#################################Generic functions###################################

def Get_Element(element_parameter, element_value, reference_parameter=False, reference_value=False,
                reference_is_parent_or_child=False, get_all_unvalidated_elements=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting locating element...", 1)
        #all_elements = Get_All_Elements(element_parameter,element_value)
        element = Get_Single_Element(element_parameter, element_value)
        if ((element == []) or (element == "failed")):
            CommonUtil.ExecLog(sModuleInfo, "Could not get the element with the given parameters and values. Please provide accurate data set(s) information.", 3)
            return "failed"
        #element = Element_Validation(element)
        return element
    except Exception:
        errMsg = "Could not find your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)




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
            elif parameter == "accessibility id":
                All_Elements = driver.find_element_by_accessibility_id(value)
            elif parameter == "class name":
                All_Elements = driver.find_element_by_class_name(value)
            elif parameter == "xpath":
                #All_Elements = driver.find_element_by_xpath(value)
                All_Elements == driver.find_element_by_xpath("//*[@%s='%s']" % (parameter, value))
            elif parameter == "android uiautomator text":
                All_Elements == driver.find_element_by_android_uiautomator('new UiSelector().text(' + value + ')')
            elif parameter == "android uiautomator description":
                All_Elements == driver.find_element_by_android_uiautomator(
                    'new UiSelector().description(' + value + ')')
            elif parameter == "ios uiautomation":
                All_Elements == driver.find_element_by_ios_uiautomation('.elements()[0]')
            else:
                All_Elements == driver.find_element_by_xpath("//*[@%s='%s']"%(parameter, value))

        elif parent == True:
            if parameter == "name":
                All_Elements = driver.find_element_by_xpath("//*[@text='%s']" % value)
            elif parameter == "id":
                All_Elements = driver.find_element_by_id(value)
            elif parameter == "accessibility id":
                All_Elements = driver.find_element_by_accessibility_id(value)
            elif parameter == "class name":
                All_Elements = driver.find_element_by_class_name(value)
            elif parameter == "xpath":
                #All_Elements = driver.find_element_by_xpath(value)
                All_Elements == driver.find_element_by_xpath("//*[@%s='%s']" % (parameter, value))
            elif parameter == "android uiautomator text":
                All_Elements == driver.find_element_by_android_uiautomator('new UiSelector().text(' + value + ')')
            elif parameter == "android uiautomator description":
                All_Elements == driver.find_element_by_android_uiautomator(
                    'new UiSelector().description(' + value + ')')
            elif parameter == "ios uiautomation":
                All_Elements == driver.find_element_by_ios_uiautomation('.elements()[0]')
            else:
                All_Elements == driver.find_element_by_xpath("//*[@%s='%s']"%(parameter,value))

        return All_Elements
    except Exception:
        errMsg = "Unable to get the element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


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
            elif parameter == "accessibility id":
                All_Elements = driver.find_elements_by_accessibility_id(value)
            elif parameter == "class name":
                All_Elements = driver.find_elements_by_class_name(value)
            elif parameter == "xpath":
                All_Elements = driver.find_elements_by_xpath(value)
            elif parameter == "android uiautomator text":
                All_Elements == driver.find_elements_by_android_uiautomator('new UiSelector().text('+value+')')
            elif parameter == "android uiautomator description":
                All_Elements == driver.find_elements_by_android_uiautomator('new UiSelector().description('+value+')')
        elif parent == True:
            if parameter == "name":
                All_Elements = driver.find_elements_by_name(value)
            elif parameter == "id":
                All_Elements = driver.find_elements_by_id(value)
            elif parameter == "accessibility id":
                All_Elements = driver.find_elements_by_accessibility_id(value)
            elif parameter == "class name":
                All_Elements = driver.find_elements_by_class_name(value)
            elif parameter == "xpath":
                All_Elements = driver.find_elements_by_xpath(value)
            elif parameter == "android uiautomator text":
                All_Elements == driver.find_elements_by_android_uiautomator('new UiSelector().text('+value+')')
            elif parameter == "android uiautomator description":
                All_Elements == driver.find_elements_by_android_uiautomator('new UiSelector().description('+value+')')

        return All_Elements
    except Exception:
        errMsg = "Unable to get the element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Validate_Step_Data(data_set):
    ''' Ensures step data is accurate, and returns only the pertinent values '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Step_Data", 1)

    # Initialize variables
    element_parameter = False
    element_value = False
    reference_parameter = False
    reference_value = False    
    reference_is_parent_or_child = False

    try:    
        if (len(data_set)==1): # One row in the data set
            element_parameter = data_set[0][0] # Get Field (element object)
            element_value = data_set[0][2] # Get element value
            reference_parameter = False
            reference_value = False    
            reference_is_parent_or_child = False
#         elif (len(data_set)==2): #??? Whys is this commented out ???
#             for each in data_set:
#                 if each[1]=="element parameter 1 of 2":
#                     element_parameter = each[0]
#                     element_value = each[2]
#                 elif each[1]=="element parameter 2 of 2":
#                     reference_parameter = each[0]
#                     reference_value = each[2]
#             reference_is_parent_or_child = False
        elif (len(data_set)==3): # Three rows in the data set
            for each in data_set: # For each row
                if each[1]=="element parameter": # If Sub-Field is element parameter
                    element_parameter = each[0] # Get Field (element object)
                    element_value = each[2] # Get element value
                elif each[1]=="reference parameter": # If Sub-FIeld is reference parameter
                    reference_parameter = each[0] # Get Field (element object)
                    reference_value = each[2] # Get element value
                elif each[1]=="relation type": # If Sub-Field is relation type
                    reference_is_parent_or_child = each[2] # Get reference value
        else: # Invalid step data
            CommonUtil.ExecLog(sModuleInfo, "Data set incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"

        validated_data = (element_parameter, element_value, reference_parameter, reference_value, reference_is_parent_or_child)
        return validated_data # Return data as tuple
    except Exception:
        errMsg = "Could not find the new page element requested."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


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
        # If only one element found
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

        # If max 5 elements found
        elif len(All_Elements_Found) > 1 and len(All_Elements_Found) <= 5:
            CommonUtil.ExecLog(sModuleInfo, "Found more than one element by given parameters and values, validating visible and invisible elements. Total number of elements found: %s"%(len(All_Elements_Found)), 2)
            # If at least one is_displayed() elements, add that in visible elements list, else add that in invisible elements list
            for each_elem in All_Elements_Found:
                if each_elem.is_displayed() == True:
                    all_visible_elements.append(each_elem)
                else:
                    all_invisible_elements.append(each_elem)
            # If at least one is_displayed() elements, show that, else allow invisible elements
            if len(all_visible_elements) > 0:
                CommonUtil.ExecLog(sModuleInfo, "Found at least one visible element for given parameters and values, returning the first one or by the index specified", 2)
                return_element = all_visible_elements
            else:
                CommonUtil.ExecLog(sModuleInfo, "Did not find a visible element, however, invisible elements present", 2)
                return_element = all_invisible_elements
            return return_element[0]#[index]

        # If more that 5 elements found
        elif len(All_Elements_Found) > 5:
            CommonUtil.ExecLog(sModuleInfo, "Found more than ten element by given parameters and values, validating visible and invisible elements. Total number of elements found: %s"%(len(All_Elements_Found)), 2)
            # If at least one is_displayed() elements, add that in visible elements list, else add that in invisible elements list
            for each_elem in All_Elements_Found:
                if each_elem.is_displayed() == True:
                    all_visible_elements.append(each_elem)
                else:
                    all_invisible_elements.append(each_elem)
            # If at least one is_displayed() elements, show that, else allow invisible elements
            if len(all_visible_elements) > 0:
                CommonUtil.ExecLog(sModuleInfo, "Found at least one visible element for given parameters and values, returning the first one or by the index specified", 2)
                return_element = all_visible_elements
            else:
                CommonUtil.ExecLog(sModuleInfo, "Did not find a visible element, however, invisible elements present", 2)
                return_element = all_invisible_elements
            return return_element
        
        else:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element by given parameters and values", 3)
            return "failed"

    except Exception:
        errMsg = "Unable to get the element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def Sleep(data_set):
    ''' Sleep a specific number of seconds '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Sleep", 1)

    try:
        seconds = int(data_set[0][2])
        CommonUtil.ExecLog(sModuleInfo, "Sleeping for %s seconds" % seconds, 1)
        time.sleep(seconds)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def Wait_For_New_Element(data_set):
    ''' Continuously monitors an element for a specified amount of time and returns whether or not it is available '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Wait_For_New_Page_Element", 1)
    
    try:
        data_set = [data_set]
        element_step_data = Get_Element_Step_Data_Appium(data_set)
        returned_step_data_list = Validate_Step_Data(element_step_data)
        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
            return "failed"
        else:
            try:
                # Find the wait time from the data set
                for each in data_set[0]:
                    if each[1]=="action":
                        timeout_duration = int(each[2])

                # Check for element every second 
                end_time = time.time() + timeout_duration # Time at which we should stop looking
                for i in range(timeout_duration): # Keep testing element until this is reached
                    # Wait and then test if we are over our alloted time limit
                    time.sleep(1)
                    if time.time() >= end_time: # Keep testing element until this is reached (ensures we wait exactly the specified amount of time)
                        break
                    
                    # Test if element exists and exit loop if it does
                    Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                    if Element != [] and Element not in failed_tag_list: # Expect Element == failed when it doesn't exist
                        break
                
                # Test whether or not timeout was reached
                if ((Element == []) or (Element == "failed")):
                    return "failed"
                else:
                    return "passed" # Didn't timeout, so element must exist
            except Exception:
                element_attributes = Element.get_attribute('outerHTML')
                CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
                errMsg = "Could not find the new page element requested."
                return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def Swipe(x_start, y_start, x_end, y_end, duration = 1000):
    ''' Perform single swipe gesture with provided start and end positions '''
    # duration in mS - how long the gesture should take
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting to swipe the screen...", 1)
        driver.swipe(x_start, y_start, x_end, y_end, duration)
        CommonUtil.ExecLog(sModuleInfo, "Swiped the screen successfully", 1)
        return "passed"
    except Exception:
        errMsg = "Unable to swipe."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def swipe_handler(data_set):
    ''' Swipe screen based on user input '''
    # Functions: General swipe (up/down/left/right), multiple swipes (X coordinate (from-to), Y coordinate (from-to), stepsize)
    # action_value: comma delimited string containing swipe details
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Starting swipe handler", 1)

    # Parse data set
    try:
        action_value = data_set[0][2]
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

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
            time.sleep(1) # Small sleep, so action animation (if any) can complete
        
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

# Validating text from an element given information regarding the expected text
def Validate_Text(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Text_Data", 1)
    try:
        if ((len(data_set) != 1) or (1 < len(data_set[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            dimension = driver.get_window_size('current')
            
            for each in data_set[0]:
                if each[0] == "current page":
                    try:
                        Element = Get_Element_Appium('tag', 'html')
                        break
                    except Exception:
                        errMsg = "Could not get element from the current page."
                        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
                else:
                    element_step_data = Get_Element_Step_Data_Appium(data_set)
                    returned_step_data_list = Validate_Step_Data(element_step_data)
                    if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                        return "failed"
                    else:
                        try:
                            Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                            break
                        except Exception:
                            errMsg = "Could not get element based on the information provided.",
                            return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
 
            for each_step_data_item in data_set[0]:
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
        errMsg = "Could not compare text as requested."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


#Validating text from an element given information regarding the expected text
def Save_Text(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Save Text", 1)
    
    data_set = [data_set]
    
    # Parse data set
    try:
        variable_name = ''
        for each in data_set:
            for row in each:
                if row[1] == 'action':
                    variable_name = row[2]
        if variable_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Unable to parse data set", 3)
            return 'failed'
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    try:
        if (len(data_set[0]) < 1):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return "failed"
        else:
            for each in data_set:
                element_step_data = Get_Element_Step_Data_Appium(data_set)
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

            result = Shared_Resources.Set_Shared_Variables(variable_name, visible_list_of_element_text)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Value of Variable '%s' could not be saved!!!", 3)
                return "failed"
            else:
                Shared_Resources.Show_All_Shared_Variables()
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Validating text from an element given information regarding the expected text
def Compare_Variables(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare Variables", 1)
    try:
        element_step_data = Get_Element_Step_Data_Appium([data_set])
        if ((element_step_data == []) or (element_step_data == "failed")):
            return "failed"
        else:
            return Shared_Resources.Compare_Variables([data_set])
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

'''
   Moving all locate, Click and text interaction function under one 
'''
    
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
    except Exception:
        CommonUtil.ExecLog(sModuleInfo,"Read screen heirarchy unsuccessfully",3)
        return False

def tap_location(data_set):
    ''' Tap the provided position using x,y cooridnates '''
    # positions: list containing x,y coordinates
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    # Parse data set
    try:
        positions = []
        posX, posY = data_set[0][2].replace(' ','').split(',')
        positions.append((posX, posY)) # Put coordinates in a tuple inside of a list - must be this way for driver.tap
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    try:
        driver.tap(positions) # Tap the location (must be in list format)
        CommonUtil.ExecLog(sModuleInfo,"Tapped on location successfully",1)
        return 'passed'
    except Exception:
        errMsg = "Tapped on location unsuccessfully"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_element_location_by_id(data_set):
    ''' Find and return an element's x,y coordinates '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Searching for coordinates", 1)
    
    # Parse data set
    try:
        _id = ''
        action_value = ''
        for row in data_set: # Find element name from element parameter
            if row[1] == 'element parameter':
                _id = (row[2])
            elif row[1] == 'action':
                action_value = row[2]
        if _id == '' or action_value == '':
            CommonUtil.ExecLog(sModuleInfo,"Could not find element parameter", 3)
            return 'failed'
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    try:
        elem = locate_element_by_id(driver, _id) # Get element object for given id
        location = elem.location # Get element x,y coordinates
        positions = "%s,%s" % (location['x'], location['y']) # Save as a string - The function that uses this will need to put it in the format it needs
        CommonUtil.ExecLog(sModuleInfo,"Retreived location successfully",1)
        
        result = Shared_Resources.Set_Shared_Variables(action_value, positions) # Save position in shared variables
        return result
    except Exception:
        errMsg = "Retreived location unsuccessfully"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
        

def get_window_size():
    ''' Read the device's LCD resolution / screen size '''
    # Returns a dictionary of width and height
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    
    try:
        return driver.get_window_size() # Get window resolution in dictionary
        CommonUtil.ExecLog(sModuleInfo,"Read window size successfully",1)
    except Exception:
        errMsg = "Read window size unsuccessfully"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    
def locate_element_by_id(driver, _id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by id: %s"%_id,1)
        elem = driver.find_element_by_id(_id)
        return elem
    except Exception:
        errMsg = "Unable to locate the element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def locate_elements_by_id(driver, _id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate elements by id: %s"%_id,1)
        elems = driver.find_elements_by_id(_id)
        return elems
    except Exception:
        errMsg = "Unable to locate elements."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    
def locate_element_by_name(driver, _name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by name: %s"%_name,1)
        elem = driver.find_element_by_name(_name)
        return elem
    except Exception:
        errMsg = "Unable to locate the element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    
def locate_element_by_class_name(driver, _class):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by class: %s"%_class,1)
        elem = driver.find_element_by_class_name(_class)
        return elem
    except Exception:
        errMsg = "Unable to locate the element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    
def locate_element_by_xpath(driver, _classpath):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by xpath: %s"%_classpath,1)
        elem = driver.find_element_by_xpath(_classpath)
        return elem
    except Exception:
        errMsg = "Unable to locate the element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def locate_element_by_accessibility_id(driver, _id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by accessibility id: %s"%_id,1)
        elem = driver.find_element_by_accessibility_id(_id)
        return elem
    except Exception:
        errMsg = "Unable to locate the element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def locate_element_by_android_uiautomator_text(driver, _text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by android uiautomator text: %s"%_text,1)
        elem = driver.find_element_by_android_uiautomator('new UiSelector().text('+_text+')')
        return elem
    except Exception:
        errMsg = "Unable to locate the element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def locate_element_by_android_uiautomator_description(driver, _description):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by android uiautomator description: %s"%_description,1)
        elem = driver.find_element_by_android_uiautomator('new UiSelector().description('+_description+')')
        return elem
    except Exception:
        errMsg = "Unable to locate the element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def locate_element_by_ios_uiautomation(driver, _description):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by ios uiautomatoion: %s"%_description,1)
        elem = driver.find_element_by_ios_uiautomation('.elements()[0]')
        return elem
    except Exception:
        errMsg = "Unable to locate the element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'============================= Get Elements Section Begins =============================='    

def Get_Element_Appium(element_parameter,element_value,reference_parameter=False,reference_value=False,reference_is_parent_or_child=False,get_all_unvalidated_elements=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        All_Elements_Found = []
        # Get the element(s) if parent and/or child value not provided in the step data
        if reference_is_parent_or_child == False:
            # Get the element(s) if parent value not provided in the step data
            if ((reference_parameter == False) and (reference_value == False)):
                All_Elements = Get_All_Elements_Appium(element_parameter,element_value)     
                if ((All_Elements == []) or (All_Elements == 'failed')):        
                    CommonUtil.ExecLog(sModuleInfo, "Could not find your element by parameter:%s and value:%s..."%(element_parameter,element_value), 3)
                    return "failed"
                else:
                    All_Elements_Found = All_Elements
            #elif (reference_parameter != False and reference_value!= False):
            #    CommonUtil.ExecLog(sModuleInfo, "Locating element using double matching", 1)
            #    All_Elements = Get_Double_Matching_Elements(element_parameter, element_value, reference_parameter, reference_value)
            #    if ((All_Elements == []) or (All_Elements == "failed")):
            #        CommonUtil.ExecLog(sModuleInfo, "Could not find your element by parameter1:%s , value1:%s and parameter2:%s , value2:%s..."%(element_parameter,element_value,reference_parameter,reference_value), 3)
            #        return "failed"
            #    else:
            #        All_Elements_Found = All_Elements
            else:
                CommonUtil.ExecLog(sModuleInfo, "Could not find your element because you are missing at least one parameter", 3)
                return "failed"
            
        # Get the element(s) if child value not provided in the step data
        elif reference_is_parent_or_child == "parent":     
            CommonUtil.ExecLog(sModuleInfo, "Locating all parents elements", 1)   
            all_parent_elements = Get_All_Elements_Appium(reference_parameter,reference_value)#,"parent")
            all_matching_elements = []
            for each_parent in all_parent_elements:
                interested_elem = Get_All_Elements_Appium(element_parameter,element_value,each_parent) #can there be a problem when we send in each parent, or does this contain both param and value?
                if interested_elem != "failed":
                    for each_matching in interested_elem:
                        all_matching_elements.append(each_matching)
            All_Elements_Found = all_matching_elements

        # Get the element(s) if parent value not provided in the step data
        elif reference_is_parent_or_child == "child":        
            all_parent_elements = Get_All_Elements_Appium(element_parameter,element_value)
            all_matching_elements = []
            for each_parent in all_parent_elements:
                interested_elem = Get_All_Elements_Appium(reference_parameter,reference_value,each_parent)
                if interested_elem != "failed":
                    all_matching_elements.append(each_parent)
            All_Elements_Found=all_matching_elements
            
        elif ((reference_is_parent_or_child!="parent") or (reference_is_parent_or_child!="child") or (reference_is_parent_or_child!=False)):
            CommonUtil.ExecLog(sModuleInfo, "Unspecified reference type; please indicate whether parent, child or leave blank", 3)
            return "failed"
        
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to run based on the current inputs, please check the inputs and re-enter values", 3)
            return "failed"
        
        # This method returns all the elements found without validation
        if(get_all_unvalidated_elements!=False):
            return All_Elements_Found
        else:
            #can later also pass on the index of the element we want
            result = Element_Validation(All_Elements_Found)#, index)
            return result
    
    except Exception:
        errMsg = "Could not find your element"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


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
            elif parameter == "class name":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_class_name(value))
            elif parameter == "xpath":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_xpath(value))
            elif parameter == "current screen": # Read full screen text
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_xpath("//*"))
            elif parameter == "accessibility id":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_accessibility_id(value))    
            elif parameter == "android uiautomator":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_android_uiautomator(value))    
            elif parameter == "ios uiautomation":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_ios_uiautomation(value))    
            else:
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_xpath("//*[@%s='%s']" %(parameter,value)))
        else:
            if parameter == "id":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_id(value))
            elif parameter == "name":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_name(value))
            elif parameter == "class name":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_class_name(value))
            elif parameter == "xpath":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_xpath(value))
            elif parameter == "accessibility id":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_accessibility_id(value))    
            elif parameter == "android uiautomator":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_android_uiautomator(value))    
            elif parameter == "ios uiautomation":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_ios_uiautomation(value))    
            else:
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_xpath("//*[@%s='%s']" %(parameter,value)))    
        
        return All_Elements
    except Exception:
        errMsg = "Unable to get the element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


'===================== ===x=== Get Element Section Ends ===x=== ======================'    
    
'============================= NEW Sequential Actions Section Begins =============================='

#Method to get the element step data from the original step_data
def Get_Element_Step_Data_Appium(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function - Get Element Step Data", 1)
    try:
        element_step_data=[]
        for each in data_set[0]:
            if (each[1]=="action" or each[1]=="conditional action"):
                CommonUtil.ExecLog(sModuleInfo, "Not a part of element step data", 2)
                continue
            else:
                element_step_data.append(each)
                 
        return element_step_data
    
    except Exception:
        errMsg = "Could not get element step data."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Sequential_Actions_Appium(step_data):
    ''' Main Sequential Actions function - Performs logical decisions based on user input '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    
    if verify_step_data(step_data) in failed_tag_list:
        CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
        return "failed"
    
    try:            
        for data_set in step_data: # For each data set within step data
            logic_row=[] # Initialize conditional action list
            for row in data_set: # For each row of the data set
                # Don't process these items right now, but also dont' fail
                if ((row[1] == "element parameter") or (row[1] == "reference parameter") or (row[1] == "relation type") or (row[1] == "element parameter 1 of 2") or (row[1] == "element parameter 2 of 2") or (row[1] == "compare")):
                    continue

                # If middle column = action, call action handler
                elif row[1]=="action":
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row: %s" % str(row), 1)
                    result = Action_Handler_Appium(data_set,row[0]) # Pass data set, and action_name to action handler
                    if result == [] or result == "failed": # Check result of action handler
                        return "failed"
                    elif result in skipped_tag_list:
                        return "skipped"
                
                # If middle column = action, call action handler, but always return a pass
                elif row[1]=="optional action":
                    CommonUtil.ExecLog(sModuleInfo, "Checking the optional action to be performed in the action row: %s" % str(row), 1)
                    result = Action_Handler_Appium(data_set,row[0]) # Pass data set, and action_name to action handler
                    if result == 'failed':
                        CommonUtil.ExecLog(sModuleInfo, "Optional action failed. Returning pass anyway", 2)
                    result = 'passed'
                    
                # If middle column = conditional action, evaluate data set
                elif row[1]=="conditional action":
                    CommonUtil.ExecLog(sModuleInfo, "Checking the logical conditional action to be performed in the conditional action row: %s" % str(row), 1)
                    logic_row.append(row)
                    
                    # Only run this when we have two conditional actions for this data set (a true and a false preferably)
                    if len(logic_row) == 2:
                        CommonUtil.ExecLog(sModuleInfo, "Found 2 conditional actions - moving ahead with them", 1)
                        return Conditional_Action_Handler(step_data, data_set, row, logic_row) # Pass step_data, and current iteration of data set to decide which data sets will be processed next
                
                # Middle column not listed above, so data set is wrong
                else:
                    CommonUtil.ExecLog(sModuleInfo, "The sub-field information is incorrect. Please provide accurate information on the data set(s).", 3)
                    return "failed"                 
        
        # No failures, return pass
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
    
def Conditional_Action_Handler(step_data, data_set, row, logic_row):
    ''' Process conditional actions, called only by Sequential_Actions() '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    
    element_step_data = Get_Element_Step_Data_Appium([data_set]) # Pass data set as a list, and get back anything that's not an "action" or "conditional action"
    returned_step_data_list = Validate_Step_Data(element_step_data) # Make sure the element step data we got back from above is good
    if ((returned_step_data_list == []) or (returned_step_data_list == "failed")): # Element step data is bad, so fail
        CommonUtil.ExecLog(sModuleInfo, "Element data is bad: %s" % str(element_step_data), 3)
        return "failed"
    else: # Element step data is good, so continue
        # Check if element from data set exists on device
        try:
            Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
            if Element == 'failed': # Element doesn't exist, proceed with the step data following the fail/false path
                logic_decision = "false"
            else: # Any other return means we found the element, proceed with the step data following the pass/true pass
                logic_decision = "true"
        except Exception: # Element doesn't exist, proceed with the step data following the fail/false path
            errMsg = "Could not find element in the by the criteria..."
            return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
                    
        # Process the path as defined above (pass/fail)
        for conditional_steps in logic_row: # For each conditional action from the data set
            CommonUtil.ExecLog(sModuleInfo, "Processing conditional action: %s" % str(conditional_steps), 1)
            if logic_decision in conditional_steps: # If we have a result from the element check above (true/false)
                list_of_steps = conditional_steps[2].split(",") # Get the data set numbers for this conditional action and put them in a list
                for each_item in list_of_steps: # For each data set number we need to process before finishing
                    CommonUtil.ExecLog(sModuleInfo, "Processing conditional step %s" % str(each_item), 1)
                    data_set_index = int(each_item) - 1 # data set number, -1 to offset for data set numbering system

                    if step_data[data_set_index] == data_set: # If the data set we are GOING to pass back to sequential_actions() is the same one that called THIS function in the first place, then the step data is calling itself again, and we must pass all of the step data instead, so it doesn't crash later when it tries to refer to data sets that don't exist
                        result = Sequential_Actions_Appium(step_data) # Pass the step data to sequential_actions() - Mainly used when the step data is in a deliberate recursive loop of conditional actions
                    else: # Normal process - most conditional actions will come here
                            result = Sequential_Actions_Appium([step_data[data_set_index]]) # Recursively call this function until all called data sets are complete

                return result # Return only the last result of the last row of the last data set processed - This should generally be a "step result action" command

    # Shouldn't get here, but just in case
    return 'passed'

#Handles actions for the sequential logic, based on the input from the mentioned function
def Action_Handler_Appium(_data_set, action_name):
    ''' Handle Sub-Field=Action from step data, called only by Sequential_Actions() '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    # Strip the "optional" keyword, so functions work properly
    data_set = []
    for row in _data_set:
        new_row = list(row)
        if 'optional' in row[1]:
            new_row[1] = row[1].replace('optional', '').strip()
        data_set.append(tuple(new_row))
    
    # Convert shared variables to their string equivelent !!! Needs to be moved within try block after below for row in data_set is removed
    data_set = shared_variable_to_value(data_set)
    if data_set in failed_tag_list:
        return 'failed'
    
    # Perform an action based on Field from step data
    try:
        # Multiple row actions
        if action_name == "click": # Click an element
            result = Click_Element_Appium(data_set)
        elif action_name == "text": # Enter text string into element
            result = Enter_Text_Appium(data_set)
        elif action_name == "wait": # Wait until element is available/enabled
            result = Wait_For_New_Element(data_set)
        elif action_name == "tap": # Tap an element
            result = Tap_Appium(data_set)
        elif action_name == "validate screen text" or action_name == "validate full text" or action_name == "validate partial text": # Test if text string exists
            result = Validate_Text_Appium([data_set])
        elif action_name == "save text": # Save text string
            result = Save_Text(data_set)
        elif action_name == "compare variable": # Compare two "shared" variables
            result = Compare_Variables(data_set)
        elif action_name == "insert into list":
            result = Insert_Into_List(data_set)
        elif action_name == "initialize list":
            result = Initialize_List(data_set)
        elif (action_name == "compare list"):
            result = Compare_Lists(data_set)
        elif action_name == "step result": # Result from step data the user wants to specify (passed/failed)
            result = step_result(data_set)
        elif action_name == "install": # Install and execute application
            result = install_application(data_set) # file location, activity_name(optional)
        elif action_name == "launch": # Launch program and get appium driver instance
            result = launch_application(data_set) # Package name, Activity name
        elif action_name == "get location":
            result = get_element_location_by_id(data_set) # Get x,y coordinates of the pass button

        # Single row actions
        elif action_name == "sleep": # Sleep a specific amount of time
            result = Sleep(data_set)
        elif action_name == "swipe": # Swipe screen
            result = swipe_handler(data_set)
        elif action_name == "close": # Close foreground application
            result = close_application(data_set)
        elif action_name == "uninstall": # Uninstall application
            result = uninstall_application(data_set)
        elif action_name == 'teardown': # Cleanup Appium instance
            result = teardown_appium(data_set)
        elif action_name == 'keypress': # Press hardware, software or virtual key
            result = Keystroke_Appium(data_set) # To be replaced with handler dependent on android/ios
        elif action_name == "tap location":
            result = tap_location(data_set)

        # Anything else is an invalid action
        else:
            CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information on the data set(s).", 3)
            return "failed" 
        
        # Check result of the above if() statement
        if result == "failed":
            return "failed"
        elif result == 'skipped':
            return "skipped"

        
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def shared_variable_to_value(data_set): #!!! Should be moved to Shared_Variable.py
    ''' Look for any Shared Variable strings in step data, convert them into their values, and return '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    new_data = [] # Rebuild the data_set with the new variable (because it's a list of tuples which we can't update)

    try:
        for row in data_set: # For each row of the data set
            data_row = list(row) # Convert row which is a tuple to a list, so we can update it if we need to
            for i in range(0, 3): # For each field (Field, Sub-Field, Value)
                if row[i] != False:
                    if "%|" in row[i] and "|%" in row[i]: # If string contains these characters, it's a shared variable
                        CommonUtil.ExecLog(sModuleInfo, "Shared Variable: %s" % row[i], 1)
                        left_index = row[i].index('%|') # Get index of left marker
                        right_index = row[i].index('|%') # Get index of right marker
                        var = row[i][left_index:right_index + 2] # Copy entire shared variable
                        var_clean = var[2:len(var)-2] # Remove markers
                        data_row[i] = Shared_Resources.Get_Shared_Variables(var_clean) # Get the string for this shared variable 
                        if row[i] == 'failed':
                            CommonUtil.ExecLog(sModuleInfo, "Invalid shared variable", 3)
                            return "failed"
            new_data.append(tuple(data_row)) # Convert row from list to tuple, and append to new data_set
        return new_data
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def verify_step_data(step_data):
    ''' Verify step data is valid '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Verifying Step Data", 1)
    
    try:
        for data_set in step_data:
            for row in data_set:
                if len(row[0]) == 0:
                    CommonUtil.ExecLog(sModuleInfo, "Data Set Field is empty", 3)
                    return 'failed'
                elif len(row[1]) == 0:
                    CommonUtil.ExecLog(sModuleInfo, "Data Set Sub-Field is empty", 3)
                    return 'failed'
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
    

def step_result(data_set):
    ''' Process what the user specified as the outcome with step result '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Verifying step data", 1)
    
    # Parse data set
    try:
        action_value = ''
        for row in data_set: # Find required data
            if row[0] == 'step result':
                action_value = row[2]
        if action_value == '':
            CommonUtil.ExecLog(sModuleInfo,"Could not find step result", 3)
            return 'failed'
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    if action_value in failed_tag_list: # Convert user specified pass/fail into standard result
        result = 'failed'
    elif action_value in passed_tag_list:
        result = 'passed'
    elif action_value in skipped_tag_list:
        result = 'skipped'
    return result

def Initialize_List(data_set):
    ''' Temporary wrapper until we can convert everything to use just data_set and not need the extra [] '''
    return Shared_Resources.Initialize_List([data_set])

#Method to click on element; step data passed on by the user
def Click_Element_Appium(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Click_Element_Appium", 1)
    
    data_set = [data_set]

    try:
        if len(data_set[0]) < 1:
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            #element_step_data = step_data[0][0:len(step_data[0])-1:1]
            element_step_data = Get_Element_Step_Data_Appium(data_set)            
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
                except Exception:
                    errMsg = "Could not select/click your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    except Exception:
        errMsg = "Could not find/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    
def Tap_Appium(data_set):
    ''' Execute "Tap" for an element '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Tap_Appium", 1)
    
    data_set = [data_set]
    
    try:
        if (len(data_set) != 1):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:    
            element_step_data = Get_Element_Step_Data_Appium(data_set)            
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
                except Exception:
                    errMsg = "Could not select/click your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
                
    except Exception:
        errMsg = "Unable to tap."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

# def Double_Tap_Appium_asifurrouf

def Double_Tap_Appium(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function:Double_Tap_Appium", 1)
    try:
        if ((len(data_set) != 1) or (1 < len(data_set[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
            return "failed"
        else:
            element_step_data = Get_Element_Step_Data_Appium(data_set)
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
                except Exception:
                    errMsg = "Could not select/click your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    except Exception:
        errMsg = "Unable to tap."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

# Long_Press_Appium_asifurrouf_fixed Long Press time

def Long_Press_Appium(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Long_Press_Appium", 1)
    try:
        if ((len(data_set) != 1) or (1 < len(data_set[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
            return "failed"
        else:
            element_step_data = Get_Element_Step_Data_Appium(data_set)
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
                except Exception:
                    errMsg = "Could not select/click your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    except Exception:
        errMsg = "Unable to tap."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

#asifurrouf_long_press_double_tap

#Method to enter texts in a text box; step data passed on by the user
def Enter_Text_Appium(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Enter_Text_Appium", 1)
    
    data_set = [data_set]
    
    try:
        if ((len(data_set) != 1) or (1 < len(data_set[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            element_step_data=Get_Element_Step_Data_Appium(data_set)
            returned_step_data_list = Validate_Step_Data(element_step_data) 
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                    for each in data_set[0]:
                        if each[1]=="action":
                            text_value=each[2]
                        else:
                            continue
                    #text_value=step_data[0][len(step_data[0])-1][2]
                    Element.click() # Set focus to textbox
                    Element.clear() # Remove any text already existing
                    if dependency['Mobile'].lower() == 'ios':
                        Element.set_value(text_value) # Work around for IOS issue in Appium v1.6.4 where send_keys() doesn't work
                    else:
                        Element.send_keys(text_value) # Enter the user specified text
                    driver.hide_keyboard() # Remove keyboard
                    CommonUtil.TakeScreenShot(sModuleInfo) # Capture screen
                    CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s"%text_value, 1)
                    return "passed"
                except Exception:
                    errMsg = "Could not enter text in the desired element."
                    return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    except Exception:
        errMsg = "Could not find your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


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
        elif keystroke == "go back" or keystroke == "back":
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

def iOS_Keystroke_Key_Mapping(keystroke):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: iOS_Keystroke_Key_Mapping", 1)
    
    CommonUtil.ExecLog(sModuleInfo, "IOS key events not yet supported" % keystroke, 3)
    return 'failed'

    try:
        if keystroke == "return" or keystroke == 'enter':
            driver.keyevent(13)
        elif keystroke == "go back" or keystroke == "back":
            driver.back()
        elif keystroke == "space":
            driver.keyevent(32)
        elif keystroke == "backspace":
            driver.keyevent(8)
        elif keystroke == "call":
            driver.keyevent(5)            
        elif keystroke == "end call":
            driver.keyevent(6)
                                     
    except Exception:
        errMsg = "Could not press enter for your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


#Method to click on element; step data passed on by the user
def Keystroke_Appium(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Keystroke_Appium", 1)
    
    # Parse data set
    try:
        keystroke_value = data_set[0][2]
        if keystroke_value == '':
            CommonUtil.ExecLog(sModuleInfo,"Could not find keystroke value", 3)
            return 'failed'
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    try:
        # Execute the correct key stroke handler for the dependency
        if dependency['Mobile'].lower() == 'android':
            result = Android_Keystroke_Key_Mapping(keystroke_value)
        elif dependency['Mobile'].lower() == 'ios':
            result = iOS_Keystroke_Key_Mapping(keystroke_value)
        else:
            result = 'failed'
                
        if result in passed_tag_list:
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Successfully entered keystroke for the element with given parameters and values", 1)
            return "passed"
        else:
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Could not enter keystroke for the element with given parameters and values", 3)
            return "failed"
              
    except Exception:
        errMsg = "Could not enter keystroke."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


"""NEED TO BE CHANGED QUITE A BIT. CURRENT_PAGE WILL BE MODIFIED TO HAVE SOMETHING ELSE"""
#Validating text from an element given information regarding the expected text
def Validate_Text_Appium(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Text", 1)
    try:
        if ((len(data_set) != 1) or (1 < len(data_set[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return "failed"
        else:
            Element = []
            Elements = []
            for each in data_set[0]:
                # Get all elements from current screen based on step_data
                if each[0] == "current page":
                    try:
                        Element = Get_Element_Appium('tag', 'html')
                        break
                    except Exception:
                        errMsg = "Could not get element from the current page."
                        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
                    
                # Get all elements from current screen based on step_data
                elif each[0] == "current screen":
                    try:
                        Elements = Get_Element_Appium(each[0], '')
                        break
                    except Exception, e:
                        errMsg = "Could not get element from the current screen."
                        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg) 
                    
                else:
                    # Get all the element step data(s) other than 'action' and 'conditional action'
                    element_step_data = Get_Element_Step_Data_Appium(data_set)
                    # Get all the element step data's parameter and value
                    returned_step_data_list = Validate_Step_Data(element_step_data)
                    if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                        return "failed"
                    else:
                        try:
                            # Get single element from the device based on step_data
                            Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                            break
                        except Exception:
                            errMsg = "Could not get element based on the information provided."
                            return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)           
 
            # Get the 'action' parameter and 'value' from step data
            for each_step_data_item in data_set[0]:
                if each_step_data_item[1]=="action":
                    expected_text_data = each_step_data_item[2].split('||') # Split the separator in case multiple string provided in the same data_set
                    validation_type = each_step_data_item[0]
            
            visible_list_of_element_text = []
            # Get the string for a single element
            if Element != []:
                list_of_element_text = Element.text.split('\n') # Extract the text element
                visible_list_of_element_text = []
                for each_text_item in list_of_element_text:
                    if each_text_item != "":
                        visible_list_of_element_text.append(each_text_item)

            # Get all the strings for multiple elements
            elif Elements != []:
                for each_item in Elements:
                    each_text_item = each_item.text # Extract the text element
                    if each_text_item != '':
                        visible_list_of_element_text.append(each_text_item)
             
            # Validate the partial text/string provided in the step data with the text obtained from the device
            if validation_type == "validate partial text":
                actual_text_data = visible_list_of_element_text
                CommonUtil.ExecLog(sModuleInfo, ">>>>>> Expected Text: %s" %expected_text_data, 1)
                CommonUtil.ExecLog(sModuleInfo, ">>>>>>>> Actual Text: %s" %actual_text_data, 1)
                for each_actual_text_data_item in actual_text_data:
                    if expected_text_data[0] in each_actual_text_data_item: # index [0] used to remove the unicode 'u' from the text string
                        CommonUtil.ExecLog(sModuleInfo, "The text has been validated by a partial match.", 1)
                        return "passed"
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Unable to validate using partial match.", 3)
                        return "failed"
            
            # Validate the full text/string provided in the step data with the text obtained from the device
            if validation_type == "validate full text":
                actual_text_data = visible_list_of_element_text
                CommonUtil.ExecLog(sModuleInfo, ">>>>>> Expected Text: %s" %expected_text_data, 1)
                CommonUtil.ExecLog(sModuleInfo, ">>>>>>>> Actual Text: %s" %actual_text_data, 1)
                if (expected_text_data[0] == actual_text_data[0]): # index [0] used to remove the unicode 'u' from the text string
                    CommonUtil.ExecLog(sModuleInfo, "The text has been validated by using complete match.", 1)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to validate using complete match.", 3)
                    return "failed"

            # Validate all the text/string provided in the step data with the text obtained from the device
            if validation_type == "validate screen text":
                CommonUtil.ExecLog(sModuleInfo, ">>>>>> Expected Text: %s" %expected_text_data, 1)
                CommonUtil.ExecLog(sModuleInfo, ">>>>>>>> Actual Text: %s" %visible_list_of_element_text, 1)
                i = 0
                for x in xrange(0, len(visible_list_of_element_text)): 
                    if (visible_list_of_element_text[x] == expected_text_data[i]): # Validate the matching string
                        CommonUtil.ExecLog(sModuleInfo, "The text element '%s' has been validated by using complete match." %visible_list_of_element_text[x], 1)
                        i += 1
                    else:
                        visible_elem = [ve for ve in visible_list_of_element_text[x].split()]
                        expected_elem = [ee for ee in expected_text_data[i].split()]
                        for elem in visible_elem: # Validate the matching word
                            if elem in expected_elem:
                                CommonUtil.ExecLog(sModuleInfo, "Validate the element '%s' using element match." %elem, 1)
                            else:
                                CommonUtil.ExecLog(sModuleInfo, "Unable to validate the element '%s'. Check the element(s) in step_data(s) and/or in screen text." %elem, 1)
                        if (visible_elem[0] in expected_elem):
                            i += 1
                            
            else:
                CommonUtil.ExecLog(sModuleInfo, "Incorrect validation type. Please check step data", 3)
                return "failed"
 
    except Exception:
        errMsg = "Could not compare text as requested."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


#Inserting a field into a list of shared variables
def Insert_Into_List(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Insert_Into_List", 1)
    data_set = [data_set]
    
    try:
        if len(data_set[0]) == 1: #will have to test #saving direct input string data
            list_name = ''
            key = ''
            value = ''
            full_input_key_value_name = ''

            for each_step_data_item in data_set[0]:
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

        elif len(data_set[0]) > 1 and len(data_set[0]) <=5:
            for each in data_set[0]:
                element_step_data = Get_Element_Step_Data_Appium(data_set)
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

            list_name = ''
            key = ''
            for each_step_data_item in data_set[0]:
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
def Compare_Lists(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Lists", 1)
    try:
        element_step_data = Get_Element_Step_Data_Appium([data_set])
        if ((element_step_data == []) or (element_step_data == "failed")):
            return "failed"
        else:
            return Shared_Resources.Compare_Lists([data_set])
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

'===================== ===x=== Sequential Actions Section Ends ===x=== ======================'


def get_program_names(search_name):
    print "Trying to find package and activity names"
    # Find package name for the program that's already installed
    cmd = 'adb shell pm list packages'
    res = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE).communicate(0)
    ary = str(res).split('\\r\\n')
    p = re.compile('package(.*?' + search_name + '.*?)$')
    package_name = ''
    for line in ary:
        m = p.search(str(line))
        if m:
            package_name = m.group(1)[1:]
            break

    # Launch program using only package name
    print "Trying to launch", package_name
    cmd = 'adb shell monkey -p ' + m.group(1)[1:] + ' -c android.intent.category.LAUNCHER 1'
    res = subprocess.Popen(cmd.split(' '))
    time.sleep(3)

    # Get the activity name
    cmd = 'adb shell dumpsys window windows'
    res = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE).communicate(0)
    m = re.search('CurrentFocus=.*?FocusedApp.*?ActivityRecord{\w+\s+\w+\s+(.*?)/(.*?)\s+', str(res))

    # Return package and activity names
    if m.group(1) != '' and m.group(2) != '':
        print "Package name:", m.group(1)
        print "Activity name:", m.group(2)
        return m.group(1), m.group(2)
    else:
        return '', ''