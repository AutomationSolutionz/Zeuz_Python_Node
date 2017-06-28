# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
# Android environment
from appium import webdriver
import os, sys, time, inspect
import subprocess,re
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Mobile.Android.adb_calls import adbOptions
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list, skipped_tag_list
from Framework.Built_In_Automation.Shared_Resources import LocateElement


PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

appium_binary = None
if os.name == 'posix':
    appium_binary = 'appium' # Appium directory/filename - May need to move to settings.conf
else:
    CommonUtil.ExecLog(__name__ + " : " + __file__, "Platform doesn't have an appium location defined: %s" % str(os.name), 3)
    
# Recall appium driver, if not already set - needed between calls in a Zeuz test case
global appium_driver
appium_driver = None
if Shared_Resources.Test_Shared_Variables('appium_driver'): # Check if driver is already set in shared variables
    appium_driver = Shared_Resources.Get_Shared_Variables('appium_driver') # Retreive appium driver

# Recall dependency, if not already set
dependency = None
if Shared_Resources.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables('dependency') # Retreive appium driver
else:
    CommonUtil.ExecLog(__name__ + " : " + __file__, "No dependency set - Cannot run", 3)

 
# Appium element wait time in seconds
global WebDriver_Wait 
WebDriver_Wait = 20

def get_driver():
    ''' For custom functions external to this script that need access to the driver '''
    # Caveat: create_appium_driver() must be executed before this variable is populated
    return appium_driver

def launch_application(data_set):
    ''' Launch the application the appium instance was created with, and create the instance if necessary '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
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
        
        if package_name == '' or package_name in failed_tag_list:
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
        if appium_driver == None: # Only create a new appium instance if we haven't already (may be done by install_and_start_driver())
            result = start_appium_driver(package_name, activity_name)
            if result == 'failed':
                return 'failed'
        
        CommonUtil.ExecLog(sModuleInfo,"Launching application",0)
        appium_driver.launch_app() # Launch program configured in the Appium capabilities
        CommonUtil.ExecLog(sModuleInfo,"Launched the application successfully.",1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def start_appium_server():
    ''' Starts the external Appium server '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
     
    if Shared_Resources.Test_Shared_Variables('appium_server'): # Check if the appium server was previously run (likely not)
        appium_server = Shared_Resources.Get_Shared_Variables('appium_server') # Get the subprocess object
        try:
            appium_server.kill() # Kill the server
        except:
            pass
    try:
        appium_server = subprocess.Popen([appium_binary], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) # Start the appium server
    except Exception, returncode: # Couldn't run server
        CommonUtil.ExecLog(sModuleInfo,"Couldn't start Appium server: %s" % returncode, 3)
        return 'failed'
    Shared_Resources.Set_Shared_Variables('appium_server', appium_server) # Save the server object, so we can retrieve it later
    CommonUtil.ExecLog(sModuleInfo,"Waiting 10 seconds for server to start", 0)
    time.sleep(10) # Wait for server to get to ready state
    if appium_server:
        CommonUtil.ExecLog(sModuleInfo,"Server started", 1)
        return 'passed'
    else:
        CommonUtil.ExecLog(sModuleInfo,"Server failed to start", 3)
        return 'failed'

def start_appium_driver(package_name = '', activity_name = '', filename = ''):
    ''' Creates appium instance using discovered and provided capabilities '''
    # Does not execute application
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        global appium_driver
        if appium_driver == None:
            # Start Appium server
            if start_appium_server() in failed_tag_list:
                return 'failed'
            
            # Create Appium driver
    
            # Setup capabilities
            desired_caps = {}
            desired_caps['platformName'] = dependency['Mobile'] # Set platform name
            desired_caps['autoLaunch'] = 'false' # Do not launch application
            desired_caps['fullReset'] = 'false' # Do not clear application cache when complete
            desired_caps['sendKeyStrategy'] = 'setValue' # Send text to element faster
            desired_caps['newCommandTimeout'] = 600 # Command timeout before appium destroys instance
            
            if dependency['Mobile'].lower() == 'android':
                adbOptions.wake_android() # Send wake up command to avoid issues with devices ignoring appium when they are in lower power mode (android 6.0+)
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
            CommonUtil.ExecLog(sModuleInfo,"Capabilities: %s" % str(desired_caps), 0)
            
            # Create Appium instance with capabilities
            appium_driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps) # Create instance
            if appium_driver: # Make sure we get the instance
                Shared_Resources.Set_Shared_Variables('appium_driver', appium_driver) # Save driver instance to make available to other modules
                CommonUtil.ExecLog(sModuleInfo,"Appium driver created successfully.",1)
                return "passed"
            else: # Error during setup, reset
                appium_driver = None
                CommonUtil.ExecLog(sModuleInfo,"Error during Appium setup", 3)
                return 'failed'
        else: # Driver is already setup, don't do anything
            CommonUtil.ExecLog(sModuleInfo,"Driver already configured, not re-doing", 0)
            return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
    
    
def teardown_appium(data_set):
    ''' Teardown of appium instance '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Appium instance
    try:
        global appium_driver
        appium_driver.quit() # Tell appium to shutdown instance
        CommonUtil.ExecLog(sModuleInfo,"Appium cleaned up successfully.",1)
    except:
        CommonUtil.ExecLog(sModuleInfo,"Error destroying Appium instance - appium may have already disconnected", 2)
    appium_driver = None # Clear driver variable, so next run will be fresh
    Shared_Resources.Set_Shared_Variables('appium_driver', '') # Clear the driver from shared variables

    # Appium server
    try:
        CommonUtil.ExecLog(sModuleInfo,"Destroying Appium server", 0)
        appium_server = Shared_Resources.Get_Shared_Variables('appium_server') # Get the subprocess object
        Shared_Resources.Set_Shared_Variables('appium_server', '') # Remove shared variable
        appium_server.kill() # Send kill appium process
    except:
        CommonUtil.ExecLog(sModuleInfo,"Error destroying Appium server - may already be down", 2)
        
    # Cleanup shared variables
    Shared_Resources.Clean_Up_Shared_Variables()
        
    return 'passed'

def close_application(data_set):
    ''' Exit the application '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to close the app", 0)
        appium_driver.close_app()
        CommonUtil.ExecLog(sModuleInfo,"Closed the app successfully",1)
        return "passed"
    except Exception:
        errMsg = "Unable to close the application."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    
def reset_application(data_set):
    ''' Resets / clears the application cache '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to reset the app", 0)
        appium_driver.reset() # Reset / clear application cache
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
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
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
        if appium_driver == None: # Only create a new appium instance if we haven't already (may be done by install_and_start_driver())
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
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
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
        CommonUtil.ExecLog(sModuleInfo,"Trying to remove app with package name %s"%app_package, 0)
        #if appium_driver.is_app_installed(app_package):
            #CommonUtil.ExecLog(sModuleInfo,"App is installed. Now removing...",1)
        if appium_driver == None:
            start_appium_driver(app_package,app_activity)
        appium_driver.remove_app(app_package)
        CommonUtil.ExecLog(sModuleInfo,"App is removed successfully.",1)
        return "passed"
    except Exception:
        errMsg = "Unable to uninstall"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)



def Sleep(data_set):
    ''' Sleep a specific number of seconds '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    try:
        seconds = int(data_set[0][2])
        CommonUtil.ExecLog(sModuleInfo, "Sleeping for %s seconds" % seconds, 1)
        time.sleep(seconds)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Swipe(x_start, y_start, x_end, y_end, duration = 1000):
    ''' Perform single swipe gesture with provided start and end positions '''
    # duration in mS - how long the gesture should take
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting to swipe the screen...", 0)
        appium_driver.swipe(x_start, y_start, x_end, y_end, duration)
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
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

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
        CommonUtil.ExecLog(sModuleInfo, "Swipe type: Single", 0)
        x1, y1, x2, y2 = action_value.split(',')
        Swipe(int(x1), int(y1), int(x2), int(y2))
    
    # Check for and handle simple gestures (swipe up/down/left/right), and may have a set number of swipes to execute
    elif action_value.count(',') == 0 or action_value.count(',') == 1:
        # Process number of swipes as well
        if action_value.count(',') == 1:
            action_value, count = action_value.split(',')
            count = int(count)
        else:
            count = 1
        CommonUtil.ExecLog(sModuleInfo, "Swipe type: Basic %s with a count of %d" % (action_value, count), 0)
            
        # Check for direction and calculate accordingly
        if action_value == 'up':
            x1 = 50 * w / 100 # Middle horizontal
            x2 = x1 # Middle horizontal
            y1 = 75 * h / 100 # 75% down 
            y2 = 1 # To top
        elif action_value == 'down':
            x1 = 50 * w / 100 # Middle horizontal
            x2 = x1 # Middle horizontal
            y1 = 25 * h / 100 # 25% down 
            y2 = h - 1 # To bottom
        elif action_value == 'left':
            x1 = 90 * w / 100 # Start 90% on right
            x2 = 10 * w / 100 # End 10% on left
            y1 = 50 * h / 100 # Middle vertical 
            y2 = y1 # Middle vertical
            if dependency['Mobile'].lower() == 'ios': y2 = 0 # In Appium v1.6.4, IOS doesn't swipe properly - always swipes at angles because y2 is added to y, which is different from Android. This gets around that issue
        elif action_value == 'right':
            x1 = 10 * w / 100 # Start 10% on left
            x2 = 90 * w / 100 # End 90% on right
            y1 = 50 * h / 100 # Middle vertical
            y2 = y1 # Middle vertical
            if dependency['Mobile'].lower() == 'ios': y2 = 0 # In Appium v1.6.4, IOS doesn't swipe properly - always swipes at angles because y2 is added to y, which is different from Android. This gets around that issue

        # Perform swipe as many times as specified, or once if not specified 
        for i in range(0, count):
            appium_driver.swipe(x1, y1, x2, y2)
            time.sleep(1) # Small sleep, so action animation (if any) can complete
        
    # Handle a series of almost identical gestures (swipe horizontally at different locations for example)
    elif action_value.count(',') == 2:
        # Split input into separate parameters
        horizontal, vertical, stepsize = action_value.split(',')
        CommonUtil.ExecLog(sModuleInfo, "Swipe type: Multiple", 0)
        
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
            if xstart <= 0: # appium_driver.swipe fails if we are outside the boundary, so correct any values necessary
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
            if ystart <= 0: # appium_driver.swipe fails if we are outside the boundary, so correct any values necessary
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
            y2 = y
            if dependency['Mobile'].lower() == 'ios': y2 = 0 # In Appium v1.6.4, IOS doesn't swipe properly - always swipes at angles because y2 is added to y, which is different from Android. This gets around that issue
            result = Swipe(xstart, y, xstop, y2) # Swipe screen - y must be the same for horizontal swipes
            if result == 'failed':
                return 'failed'


    # Invalid value
    else:
        CommonUtil.ExecLog(sModuleInfo, "The swipe data you entered is incorrect. Please provide accurate information on the data set(s).", 3) 
        return 'failed'

    # Swipe complete
    CommonUtil.ExecLog(sModuleInfo, "Swipe completed successfully", 1)    
    return 'passed'


#Validating text from an element given information regarding the expected text

def Save_Text(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
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
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    try:
        element_step_data = Get_Element_Step_Data_Appium([data_set])
        if ((element_step_data == []) or (element_step_data == "failed")):
            return "failed"
        else:
            return Shared_Resources.Compare_Variables([data_set])
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

  
def read_screen_heirarchy():
    ''' Read the XML string of the device's GUI and return it '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        data = appium_driver.page_source # Read screen and get xml formatted text
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
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    # Parse data set
    try:
        positions = []
        posX, posY = data_set[0][2].replace(' ','').split(',')
        positions.append((posX, posY)) # Put coordinates in a tuple inside of a list - must be this way for appium_driver.tap
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    try:
        appium_driver.tap(positions) # Tap the location (must be in list format)
        CommonUtil.ExecLog(sModuleInfo,"Tapped on location successfully", 0)
        return 'passed'
    except Exception:
        errMsg = "Tapped on location unsuccessfully"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_element_location_by_id(data_set):
    ''' Find and return an element's x,y coordinates '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
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
        elem = locate_element_by_id(appium_driver, _id) # Get element object for given id
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
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        return appium_driver.get_window_size() # Get window resolution in dictionary
        CommonUtil.ExecLog(sModuleInfo,"Read window size successfully", 0)
    except Exception:
        errMsg = "Read window size unsuccessfully"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    





def Initialize_List(data_set):
    ''' Temporary wrapper until we can convert everything to use just data_set and not need the extra [] '''
    return Shared_Resources.Initialize_List([data_set])

def Click_Element_Appium(data_set):
    ''' Click on an element '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    data_set = [data_set]

    try:
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
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    data_set = [data_set]
    
    try:
        element_step_data = Get_Element_Step_Data_Appium(data_set)            
        returned_step_data_list = Validate_Step_Data(element_step_data) 
        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
            return "failed"
        else:
            try:
                Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                if Element.is_enabled():
                    action = TouchAction(appium_driver)
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

def Double_Tap_Appium(data_set):
    #!!!not yet tested or used
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    try:
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
                    action = TouchAction(appium_driver)

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
    #!!!!Not yet tested or used
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
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
                    action = TouchAction(appium_driver)

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



def Enter_Text_Appium(data_set):
    ''' Write text to an element '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    # Find text from action line
    text_value = '' # Initialize as empty string in case user wants to pass an empty string
    try:
        for each in data_set:
            if each[1]=="action":
                text_value=each[2]
            else:
                continue
    except:
        errMsg = "Error while looking for action line"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
    # Enter text into element
    try:
        element_step_data=Get_Element_Step_Data_Appium([data_set])
        returned_step_data_list = Validate_Step_Data(element_step_data) 
        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
            return "failed"
        else:
            try:
                # Get element object
                Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                if Element in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Appium returned failed for element %s" % returned_step_data_list[1], 3)
                    return 'failed'
                
                # Enter text into element
                Element.click() # Set focus to textbox
                Element.clear() # Remove any text already existing
                if dependency['Mobile'].lower() == 'ios':
                    Element.set_value(text_value) # Work around for IOS issue in Appium v1.6.4 where send_keys() doesn't work
                else:
                    Element.send_keys(text_value) # Enter the user specified text
                appium_driver.hide_keyboard() # Remove keyboard
                CommonUtil.TakeScreenShot(sModuleInfo) # Capture screen
                CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s" % text_value, 1)
                return "passed"
            except Exception:
                errMsg = "Found element, but couldn't write text to it"
                return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    except Exception:
        errMsg = "Could not find element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Android_Keystroke_Key_Mapping(keystroke):
    ''' Provides a friendly interface to invoke key events '''
    # Keycodes: https://developer.android.com/reference/android/view/KeyEvent.html

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Sanitize input
    keystroke = keystroke.strip()
    keystroke = keystroke.lower()
    keystroke = keystroke.replace('_', ' ')
    
    try:
        if keystroke == "return" or keystroke == "enter":
            appium_driver.keyevent(66)
        elif keystroke == "go back" or keystroke == "back":
            appium_driver.back()
        elif keystroke == "spacebar":
            appium_driver.keyevent(62)
        elif keystroke == "backspace":
            appium_driver.keyevent(67)
        elif keystroke == "call": # Press call connect, or starts phone program if not already started
            appium_driver.keyevent(5)
        elif keystroke == "end call":
            appium_driver.keyevent(6)
        elif keystroke == "home":
            appium_driver.keyevent(3)
        elif keystroke == "mute":
            appium_driver.keyevent(164)
        elif keystroke == "volume down":
            appium_driver.keyevent(25)
        elif keystroke == "volume up":
            appium_driver.keyevent(24)
        elif keystroke == "wake":
            appium_driver.keyevent(224)
        elif keystroke == "power":
            appium_driver.keyevent(26)
        elif keystroke == "app switch": # Task switcher / overview screen
            appium_driver.keyevent(187)
        elif keystroke == "page down":
            appium_driver.keyevent(93)
        elif keystroke == "page up":
            appium_driver.keyevent(92)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unsupported key event: %s" % keystroke, 3)

        return 'passed'
    except Exception, e:
        return CommonUtil.Exception_Handler(sys.exc_info())

def iOS_Keystroke_Key_Mapping(keystroke):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    CommonUtil.ExecLog(sModuleInfo, "IOS key events not yet supported" % keystroke, 3)
    return 'failed'

    try:
        if keystroke == "return" or keystroke == 'enter':
            appium_driver.keyevent(13)
        elif keystroke == "go back" or keystroke == "back":
            appium_driver.back()
        elif keystroke == "space":
            appium_driver.keyevent(32)
        elif keystroke == "backspace":
            appium_driver.keyevent(8)
        elif keystroke == "call":
            appium_driver.keyevent(5)
        elif keystroke == "end call":
            appium_driver.keyevent(6)
                                     
    except Exception:
        errMsg = "Could not press enter for your element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


#Method to click on element; step data passed on by the user
def Keystroke_Appium(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
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


#Validating text from an element given information regarding the expected text
def Validate_Text_Appium(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    data_set = [data_set]
    try:
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
            CommonUtil.ExecLog(sModuleInfo, ">>>>>> Expected Text: %s" %expected_text_data, 0)
            CommonUtil.ExecLog(sModuleInfo, ">>>>>>>> Actual Text: %s" %actual_text_data, 0)
            for each_actual_text_data_item in actual_text_data:
                if expected_text_data[0] in each_actual_text_data_item: # index [0] used to remove the unicode 'u' from the text string
                    CommonUtil.ExecLog(sModuleInfo, "The text has been validated by a partial match.", 0)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to validate using partial match.", 3)
                    return "failed"
        
        # Validate the full text/string provided in the step data with the text obtained from the device
        if validation_type == "validate full text":
            actual_text_data = visible_list_of_element_text
            CommonUtil.ExecLog(sModuleInfo, ">>>>>> Expected Text: %s" %expected_text_data, 0)
            CommonUtil.ExecLog(sModuleInfo, ">>>>>>>> Actual Text: %s" %actual_text_data, 0)
            if (expected_text_data[0] == actual_text_data[0]): # index [0] used to remove the unicode 'u' from the text string
                CommonUtil.ExecLog(sModuleInfo, "The text has been validated by using complete match.", 0)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Unable to validate using complete match.", 3)
                return "failed"
        
        # Validate all the text/string provided in the step data with the text obtained from the device
        if validation_type == "validate screen text":
            CommonUtil.ExecLog(sModuleInfo, ">>>>>> Expected Text: %s" %expected_text_data, 0)
            CommonUtil.ExecLog(sModuleInfo, ">>>>>>>> Actual Text: %s" %visible_list_of_element_text, 0)
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
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
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
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
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
    ''' Find Package and Activity name based on wildcard match '''
    
    # Find package name for the program that's already installed
    try:
        cmd = 'adb shell pm list packages'
        res = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE).communicate(0)
        res = str(res).replace('\\r','')
        ary = res.split('\\n')
        p = re.compile('package(.*?' + search_name + '.*?)$')
        package_name = ''
        for line in ary:
            m = p.search(str(line))
            if m:
                package_name = m.group(1)[1:]
                break
    
        # Launch program using only package name
        cmd = 'adb shell monkey -p ' + m.group(1)[1:] + ' -c android.intent.category.LAUNCHER 1'
        res = subprocess.Popen(cmd.split(' '))
        time.sleep(3)
    
        # Get the activity name
        cmd = 'adb shell dumpsys window windows'
        res = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE).communicate(0)
        m = re.search('CurrentFocus=.*?FocusedApp.*?ActivityRecord{\w+\s+\w+\s+(.*?)/(.*?)\s+', str(res))
    
        # Return package and activity names
        if m.group(1) != '' and m.group(2) != '':
            return m.group(1), m.group(2)
        else:
            return '', ''
    except:
        result = CommonUtil.Exception_Handler(sys.exc_info())
        return result, ''
