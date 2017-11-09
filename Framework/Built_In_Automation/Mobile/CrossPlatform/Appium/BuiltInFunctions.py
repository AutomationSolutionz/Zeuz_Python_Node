# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

from appium import webdriver
import os, sys, time, inspect, subprocess, re, signal
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Mobile.Android.adb_calls import adbOptions
from Framework.Built_In_Automation.Mobile.iOS import iosOptions
from appium.webdriver.common.touch_action import TouchAction
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list, skipped_tag_list
from Framework.Built_In_Automation.Shared_Resources import LocateElement


PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)
   
# Recall appium driver, if not already set - needed between calls in a Zeuz test case
appium_port = 4721 # Default appium port - changes if we have multiple devices
appium_details = {} # Used to store device serial number, appium driver, if multiple devices are used
appium_driver = None # Holds the currently used appium instance
device_serial = '' # Holds the identifier for the currently used device (if any are specified)
device_id = '' # Holds the name of the device the user has specified, if any. Relationship is set elsewhere
if Shared_Resources.Test_Shared_Variables('appium_details'): # Check if driver is already set in shared variables
    appium_details = Shared_Resources.Get_Shared_Variables('appium_driver') # Retreive appium driver
    # Populate the global variables with one of the device information. If more than one device is used, then it'll be the last. The user is responsible for calling either launch_application() or switch_device() to focus on the one they want
    for name in appium_details:
        appium_driver = appium_details[name]['driver']
        appium_server = appium_details[name]['server']
        device_serial = appium_details[name]['serial']
        device_id = name
    

# Recall device_info, if not already set
device_info = {}
if Shared_Resources.Test_Shared_Variables('device_info'): # Check if device_info is already set in shared variables
    device_info = Shared_Resources.Get_Shared_Variables('device_info') # Retreive device_info
    
def find_appium():
    ''' Do our very best to find the appium executable '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    # Expected locations
    appium_list = [
        '/usr/bin/appium',
        os.path.join(str(os.getenv('HOME')), '.linuxbrew/bin/appium'),
        os.path.join(str(os.getenv('ProgramFiles')), 'APPIUM','Appium.exe'),
        os.path.join(str(os.getenv('USERPROFILE')), 'AppData', 'Roaming', 'npm','appium.cmd')
        ] # getenv() must be wrapped in str(), so it doesn't fail on other platforms
    
    # Try to find the appium executable
    global appium_binary
    appium_binary = ''
    for binary in appium_list:
        if os.path.exists(binary):
            appium_binary = binary
            break
    
    # Try to find the appium executable in the PATH variable
    if appium_binary == '': # Didn't find where appium was installed
        CommonUtil.ExecLog(sModuleInfo, "Searching PATH for appium", 0)
        for exe in ('appium', 'appium.exe', 'appium.bat', 'appium.cmd'):
            result = find_exe_in_path(exe) # Get path and search for executable with in
            if result != 'failed':
                appium_binary = result
                break

    # Verify if we have the binary location    
    if appium_binary == '': # Didn't find where appium was installed
        CommonUtil.ExecLog(sModuleInfo, "Appium not found. Trying to locate via which", 0)
        try: appium_binary = subprocess.check_output('which appium', shell = True).strip()
        except: pass
        
        if appium_binary == '': # Didn't find where appium was installed
            appium_binary = 'appium' # Default filename of appium, assume in the PATH
            CommonUtil.ExecLog(sModuleInfo,"Appium still not found. Assuming it's in the PATH.", 2)
        else:
            CommonUtil.ExecLog(sModuleInfo,"Found appium: %s" % appium_binary, 1)
    else: # Found appium's path
        CommonUtil.ExecLog(sModuleInfo,"Found appium: %s" % appium_binary, 1)

def find_exe_in_path(exe):
    ''' Search the path for an executable '''
    
    try:
        path = os.getenv('PATH') # Linux/Windows path
        
        if ';' in path: # Windows delimiter
            dirs = path.split(';')
        elif ':' in path: # Linux delimiter
            dirs = path.split(':')
        else:
            return 'failed'
        
        for directory in dirs: # Try each directory
            filename = os.path.join(directory, exe) # Create full path
            if os.path.isfile(filename): # If it exists, return it and stop
                return filename
        
        # No matches
        return 'failed'

    except Exception:
        errMsg = "Error searching PATH"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

# Try to find appium
appium_binary = ''
find_appium()

def get_driver():
    ''' For custom functions external to this script that need access to the driver '''
    # Caveat: create_appium_driver() must be executed before this variable is populated
    return appium_driver

def find_correct_device_on_first_run(serial_or_name, device_info):
    ''' Considers information from the data set, deployed devices, and connected devices to determine which device to use '''
    # Only used when launching an application, which creates the appium instance. 
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    global device_id, device_serial, appium_details
    CommonUtil.ExecLog(sModuleInfo, "List of devices provided by server: %s" % str(device_info), 1)
    
    try:
        # Get list of connected devices
        devices = {} # Temporarily store connected device serial numbers
        for device in adbOptions.get_devices(): # Get connected Android devices (Format: SERIAL_NO word)
            if device != '': devices[device.split(' ')[0].strip()] = 'android' # Save type
        if sys.platform == 'darwin': # Only check for IOS if on Mac
            for device in iosOptions.get_list_udid(): # Get connected IOS devices
                if device != '': devices[device] = 'ios' # Save type
        CommonUtil.ExecLog(sModuleInfo,"Connected devices: %s" % str(devices), 0)
        
        # Ensure we have at least one device connected
        if len(devices) == 0:
            CommonUtil.ExecLog(sModuleInfo,"Could not detect any connected devices. Ensure at least one is attached via USB, and that it is authorized - Trusted / USB Debugging enabled", 3)
            return 'failed'
        
        # Check if serial provided is a real serial number, name or rubish that should be ignored
        serial_check = False
        for device in devices: # For each device serial number
            if serial_or_name.lower() == device.lower():
                serial = device
                device_type = devices[device]
                did = 'default'
                serial_check = True # Flag as found
                CommonUtil.ExecLog(sModuleInfo,"Found serial number in data set: %s" % serial, 0)
                break
            
        # Check if user provided name - must be accompanied by device_info, sent by server
        if serial_check == False:
            for dname in device_info:
                if serial_or_name.lower() == dname.lower():
                    did = dname # Save device name
                    serial = device_info[did]['id'] # Save serial number
                    device_type = device_info[did]['type'].lower() # Save device type android/ios
                    serial_check = True
                    CommonUtil.ExecLog(sModuleInfo,"Found device name in data set: %s" % did, 0)
                    break
                    
        ### If we were given either a serial/uuid or name in the data set, we should now have what we need to run ###

        # Not found, so now we have to look at the device_info dictionary from the server to determine the device to use
        if serial_check == False:
            # At least one device sent by server
            if len(device_info) > 0:
                for dname in device_info:
                    did = dname
                    serial = device_info[did]['id']
                    device_type = device_info[did]['type'].lower()
                    CommonUtil.ExecLog(sModuleInfo,"Found a device selected at Deploy: %s" % did, 0)
                    break
                
            # Lastly, if nothing above is set, the user did not specify anything, and we have no information from the server. Pick a connected device, and fail if there are none
            else: # No devices sent, none specified
                for device in devices:
                    did = 'default'
                    serial = device # Get Serial
                    device_type = devices[device] # Get type
                    CommonUtil.ExecLog(sModuleInfo,"No device information found. Picked one that is connected: %s" % serial, 0)
                    break # Only take the first device

        # At the end, we should have at least one device
        if serial != '' and device_type != '' and did != '':
            # Verify this device was not already selected and run previously
            if did in appium_details:
                CommonUtil.ExecLog(sModuleInfo,"The selected device was previously run. You cannot run it more than once in a session. Either your step data is calling the 'launch' action multiple times without specifying specific devices, or you did not call the 'teardown' action in a previous run.", 3)
                return 'failed'
             
            # Verify this device is actually connected
            if serial not in devices:
                CommonUtil.ExecLog(sModuleInfo,"Although we have a selected device, it did not appear in the list of connected devices. Please ensure the device information aligns with what is connected: %s (%s)" % (did, serial), 3)
                return 'failed'
            
            # Global variables for quick access to currently selected device
            device_serial = serial
            device_id = did
            
            # Global variable that holds data required by appium
            appium_details[device_id] = {}
            if 'driver' not in appium_details[device_id]: appium_details[device_id]['driver'] = None # Initialize appium driver object
            appium_details[device_id]['serial'] = serial
            appium_details[device_id]['type'] = device_type
            
            # Store in shared variable, so it doens't get forgotten
            Shared_Resources.Set_Shared_Variables('device_serial', device_serial, protected = True)

            CommonUtil.ExecLog(sModuleInfo,"Matched provided device identifier as %s (%s)" % (device_id, serial), 1)
            return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo,"Although we found connected devices, provided information could not get all required information. Found devices: %s | Deployed device list: %s" % (str(devices), str(device_info)), 3)
            return 'failed'
        
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error trying to read device information")
     
def launch_application(data_set):
    ''' Launch the application the appium instance was created with, and create the instance if necessary '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    global device_serial, appium_details, appium_driver, device_id, device_info
    
    # Parse data set
    try:
        package_name = '' # Name of application package
        activity_name = '' # Name of application activity
        serial = '' # Serial number (may also be random string like "launch", "na", etc)

        for row in data_set: # Find required data
            if row[0] == 'package' and row[1] == 'element parameter':
                package_name = row[2]
            elif row[0] in ('app activity', 'activity') and row[1] == 'element parameter':
                activity_name = row[2]
            elif row[1] == 'action':
                serial = row[2].lower().strip()


        # Set the global variable for the preferred connected device
        if find_correct_device_on_first_run(serial, device_info) in failed_tag_list: return 'failed'
            
        # Send wake up command to avoid issues with devices ignoring appium when they are in lower power mode (android 6.0+), and unlock if passworded
        if appium_details[device_id]['type'] == 'android':
            result = adbOptions.wake_android(device_serial)
            if result in failed_tag_list: return 'failed'

        # If android, then we will try to find the activity name, IOS doesn't need this
        if activity_name == '':
            if appium_details[device_id]['type'] == 'android':
                package_name, activity_name = get_program_names(package_name) # Android only to match a partial package name if provided by the user
            
        # Verify data
        if package_name == '' or package_name in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Could not find package name", 3)
            return 'failed'
        elif appium_details[device_id]['type'] == 'android' and activity_name == '':
            CommonUtil.ExecLog(sModuleInfo,"Could not find activity name", 3)
            return 'failed'
        
        
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    # Launch application
    try:
        if appium_details[device_id]['driver'] == None: # Only create a new appium instance if we haven't already (may be done by install_and_start_driver())
            result = start_appium_driver(package_name, activity_name)
            if result == 'failed':
                return 'failed'
        
        CommonUtil.ExecLog(sModuleInfo,"Launching %s" % package_name,0)
        appium_driver.launch_app() # Launch program configured in the Appium capabilities
        CommonUtil.ExecLog(sModuleInfo,"Launched the application successfully.",1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Could not create Appium Driver, Either device is not connected, or authorized, or a capability is incorrect.")

def set_pdeathsig(sig = signal.SIGTERM):
    ''' Linux only - Capture any children that are spawned by programs executed by Popen() '''
    
    import ctypes

    libc = ctypes.CDLL("libc.so.6")
    def callable():
        return libc.prctl(1, sig)
    return callable

def start_appium_server():
    ''' Starts the external Appium server '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    global appium_port, appium_details, device_serial, appium_binary, device_id

    try:
        # Shutdown appium server if it's already running
        if appium_details[device_id]['driver']: # Check if the appium server was previously run (likely not)
            appium_server = appium_details[device_id]['driver'] # Get the subprocess object
            try:
                appium_server.kill() # Kill the server
            except:
                pass
            
        # Execute appium server
        appium_port += 2 # Increment the port number (by 2 because adb seems to grab the next port), for the next time we run, so we can have multiple instances
        
        try:
            if sys.platform  == 'win32': # We need to open appium in it's own command dos box on Windows
                cmd = 'start "Appium Server" /wait /min cmd /c %s -p %d' % (appium_binary, appium_port) # Use start to execute and minimize, then cmd /c will remove the dos box when appium is killed
                appium_server = subprocess.Popen(cmd, shell=True) # Needs to run in a shell due to the execution command
            elif sys.platform == 'linux2':
                appium_server = subprocess.Popen("%s -p %d" % (appium_binary, appium_port), shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn = set_pdeathsig(signal.SIGTERM)) # Start the appium server
            else:
                appium_server = subprocess.Popen("%s -p %d" % (appium_binary, appium_port), shell = True, stdout=subprocess.PIPE) # Start the appium server

            appium_details[device_id]['server'] = appium_server # Save the server object for teardown
        except Exception, returncode: # Couldn't run server
            return CommonUtil.Exception_Handler(sys.exc_info(), None, "Couldn't start Appium server. May not be installed, or not in your PATH: %s" % returncode)
        
        # Wait for server to startup and return
        CommonUtil.ExecLog(sModuleInfo,"Waiting 10 seconds for server to start on port %d: %s" % (appium_port, appium_binary), 0)
        time.sleep(10) # Wait for server to get to ready state
        if appium_server:
            CommonUtil.ExecLog(sModuleInfo,"Server started", 1)
            return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo,"Server failed to start", 3)
            return 'failed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error starting Appium server")

def start_appium_driver(package_name = '', activity_name = '', filename = ''):
    ''' Creates appium instance using discovered and provided capabilities '''
    # Does not execute application
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        global appium_driver, appium_details, device_id
        if appium_details[device_id]['driver'] == None:
            # Start Appium server
            if start_appium_server() in failed_tag_list:
                return 'failed'

            # Create Appium driver
    
            # Setup capabilities
            desired_caps = {}
            desired_caps['platformName'] = appium_details[device_id]['type'] # Set platform name
            desired_caps['autoLaunch'] = 'false' # Do not launch application
            desired_caps['fullReset'] = 'false' # Do not clear application cache when complete
            desired_caps['newCommandTimeout'] = 600 # Command timeout before appium destroys instance
            
            if appium_details[device_id]['type'] == 'android':
                if adbOptions.is_android_connected(device_serial) == False:
                    CommonUtil.ExecLog(sModuleInfo, "Could not detect any connected Android devices", 3)
                    return 'failed'

                CommonUtil.ExecLog(sModuleInfo,"Setting up with Android",1)
                desired_caps['platformVersion'] = adbOptions.get_android_version(appium_details[device_id]['serial']).strip()
                desired_caps['deviceName'] = adbOptions.get_device_model(appium_details[device_id]['serial']).strip()
                if package_name:
                    desired_caps['appPackage'] = package_name.strip()
                if activity_name:
                    desired_caps['appActivity'] = activity_name.strip()
                if filename and package_name == '': # User must specify package or file, not both. Specifying filename instructs Appium to install
                    desired_caps['app'] = PATH(filename).strip()
                    
            elif appium_details[device_id]['type'] == 'ios':
                CommonUtil.ExecLog(sModuleInfo,"Setting up with IOS",1)
                desired_caps['sendKeyStrategy'] = 'setValue' # Use set_value() for writing to element
                desired_caps['platformVersion'] = '10.3' # Read version #!!! Temporarily hard coded
                desired_caps['deviceName'] = 'iPhone' # Read model (only needs to be unique if using more than one)
                desired_caps['bundleId'] = package_name
                desired_caps['udid'] = appium_details[device_id]['serial'] # Device unique identifier - use auto if using only one phone
            else:
                CommonUtil.ExecLog(sModuleInfo, "Invalid device type: %s" % str(appium_details[device_id]['type']), 3)
                return 'failed'
            CommonUtil.ExecLog(sModuleInfo,"Capabilities: %s" % str(desired_caps), 0)
            
            # Create Appium instance with capabilities
            try:
                appium_driver = webdriver.Remote('http://localhost:%d/wd/hub' % appium_port, desired_caps) # Create instance
                if appium_driver: # Make sure we get the instance
                    appium_details[device_id]['driver'] = appium_driver
                    CommonUtil.ExecLog(sModuleInfo,"Appium driver created successfully.",1)
                    return "passed"
                else: # Error during setup, reset
                    appium_driver = None
                    CommonUtil.ExecLog(sModuleInfo,"Error during Appium setup", 3)
                    return 'failed'
            except:
                return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error connecting to Appium server to create driver instance")

        else: # Driver is already setup, don't do anything
            CommonUtil.ExecLog(sModuleInfo,"Driver already configured, not re-doing", 0)
            return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def kill_appium_on_windows(appium_server):
    ''' Killing Appium server on windows involves killing off it's children '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    try:
        import psutil, signal
            
        for child in psutil.Process(appium_server.pid).children(recursive=True): # For eah child in process
            try:
                cpid = int(str(child.as_dict(attrs=['pid'])['pid']).replace("'", "")) # Get child PID
                CommonUtil.ExecLog(sModuleInfo,"Killing Appium child: %d" % cpid, 0)
                psutil.Process(cpid).send_signal(signal.SIGTERM) # Send kill to it
                #print h.terminate()
            except: pass
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error killing Appium and it's children")

def teardown_appium(data_set):
    ''' Teardown of appium instance '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    global appium_details, appium_server, device_id, device_serial, device_info
    
    try:
        for name in appium_details: # For each connected device
            try:
                CommonUtil.ExecLog(sModuleInfo,"Teardown for: %s" % name, 0)
                try: appium_details[name]['driver'].quit() # Destroy driver
                except: pass
                if sys.platform  == 'win32': # Special kill for appium children on Windows
                    kill_appium_on_windows(appium_details[name]['server'])
                appium_details[name]['server'].kill() # Terminate server
            except:
                CommonUtil.ExecLog(sModuleInfo,"Error destroying Appium instance/server for %s - may already be killed" % name, 2)
        
        # Kill adb server to ensure it doesn't hang
        adbOptions.kill_adb_server()
        
        # Delete variables
        appium_details = {}
        device_info = {}
        appium_server, device_id, device_serial = '', '', ''
        Shared_Resources.Set_Shared_Variables('appium_details', '')
        Shared_Resources.Set_Shared_Variables('device_info', '')
    except:
        CommonUtil.ExecLog(sModuleInfo,"Error destroying Appium instance/server - may already be killed", 2)
    
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

def Swipe(x_start, y_start, x_end, y_end, duration = 1000, adb = False):
    ''' Perform single swipe gesture with provided start and end positions '''
    # duration in mS - how long the gesture should take
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting to swipe the screen...", 0)
        if adb:
            CommonUtil.ExecLog(sModuleInfo, "Using ADB swipe method", 0)
            adbOptions.swipe_android(x_start, y_start, x_end, y_end, device_serial) # Use adb if specifically asked for it
        else:
            appium_driver.swipe(x_start, y_start, x_end, y_end, duration) # Use Appium to swipe by default
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
    adb_swipe_method = False
    window_size1 = get_window_size() # get_size method (standard)
    window_size2 = get_window_size(True) # xpath() method
    if window_size1 == 'failed':
        return 'failed'
    height_with_navbar = int(window_size1['height']) # Read standard height (on devices with a nav bar, this is not the actual height of the screen)
    height_without_navbar = int(window_size2['height']) # Read full screen height (not at all accurate on devices without a navbar
    if height_with_navbar < height_without_navbar: # Detected full screen mode and the height readings were different, indicating a navigation bar needs to be compensated for
        w = int(window_size2['width'])
        h = int(window_size2['height'])
        CommonUtil.ExecLog(sModuleInfo, "Detected navigation bar. Enabling ADB swipe for that area", 0)
        adb_swipe_method = True # Flag to use adb to swipe later on
    else:
        w = int(window_size1['width'])
        h = int(window_size1['height'])


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
            if appium_details[device_id]['type'] == 'ios': y2 = 0 # In Appium v1.6.4, IOS doesn't swipe properly - always swipes at angles because y2 is added to y, which is different from Android. This gets around that issue
        elif action_value == 'right':
            x1 = 10 * w / 100 # Start 10% on left
            x2 = 90 * w / 100 # End 90% on right
            y1 = 50 * h / 100 # Middle vertical
            y2 = y1 # Middle vertical
            if appium_details[device_id]['type'] == 'ios': y2 = 0 # In Appium v1.6.4, IOS doesn't swipe properly - always swipes at angles because y2 is added to y, which is different from Android. This gets around that issue

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
    
        #Everything will be calculated off the larger height value
        for y in range(ystart, ystop, stepsize): # For each row, assuming stepsize, swipe and move to next row
            y2 = y
            if appium_details[device_id]['type'] == 'ios': y2 = 0 # In Appium v1.6.4, IOS doesn't swipe properly - always swipes at angles because y2 is added to y, which is different from Android. This gets around that issue

            if adb_swipe_method == True and y >= height_with_navbar: # Swipe in the navigation bar area if the device has one
                result = Swipe(xstart, y, xstop, y2, adb = True) # Using adb to perform gesture, because Appium errors when we try to acces it
            else: # Swipe via appium by default
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
        Element = LocateElement.Get_Element(data_set,appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed" 
        location = Element.location # Get element x,y coordinates
        positions = "%s,%s" % (location['x'], location['y']) # Save as a string - The function that uses this will need to put it in the format it needs
        CommonUtil.ExecLog(sModuleInfo,"Retreived location successfully",1)
        
        result = Shared_Resources.Set_Shared_Variables(action_value, positions) # Save position in shared variables
        return result
    except Exception:
        errMsg = "Retreived location unsuccessfully"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
        

def get_window_size(read_type = False):
    ''' Read the device's LCD resolution / screen size '''
    # Returns a dictionary of width and height
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        if read_type:
            return appium_driver.find_element_by_xpath("//*[not(*)]").size # Works well at reading height in full screen mode, but Appium may complain if you work outside the boundaries it has set
        else:
            return appium_driver.get_window_size() # Read the screen size as reported by the device - this is always the safe value to work within
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

    try:
        Element = LocateElement.Get_Element(data_set,appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed" 
        else:
            try:
               
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

    try:
        Element = LocateElement.Get_Element(data_set,appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed" 
        else:
            try:
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
        Element = LocateElement.Get_Element(data_set,appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed" 
        else:
            try:
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
        Element = LocateElement.Get_Element(data_set,appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed" 
        else:
            try:
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
        Element = LocateElement.Get_Element(data_set,appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed" 
        else:
            try:
                # Enter text into element
                Element.click() # Set focus to textbox
                Element.clear() # Remove any text already existing

                if appium_details[device_id]['type'] == 'ios':
                    Element.set_value(text_value) # Work around for IOS issue in Appium v1.6.4 where send_keys() doesn't work
            except Exception:
                errMsg = "Found element, but couldn't write text to it"
                return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

            # This is wrapped in it's own try block because we sometimes get an error from send_keys stating "Parameters were incorrect". However, most devices work only with send_keys
            try:
                if appium_details[device_id]['type'] != 'ios':
                    Element.send_keys(text_value) # Enter the user specified text
            except Exception:
                CommonUtil.ExecLog(sModuleInfo, "Found element, but couldn't write text to it. Trying another method", 2)
                try:
                    Element.set_value(text_value) # Enter the user specified text
                except Exception:
                    errMsg = "Found element, but couldn't write text to it. Giving up"
                    return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

            # Complete the action
            try:
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
        elif keystroke in ("app switch", "task switch", "overview", "recents"): # Task switcher / overview screen
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
        if appium_details[device_id]['type'] == 'android':
            result = Android_Keystroke_Key_Mapping(keystroke_value)
        elif appium_details[device_id]['type'] == 'ios':
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
    '''

    @sreejoy, this will need your review 

    This needs more time to fix.
    Should be a lot more simple design
    '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    data_set = [data_set]
    try:
        for each_step_data_item in data_set[0]:
            if each_step_data_item[1]=="element parameter" and each_step_data_item[2] == '':
                Element = appium_driver.find_elements_by_xpath("//*[@%s]" %each_step_data_item[0])
            if each_step_data_item[1]=="element parameter" and each_step_data_item[2] != '':
                Element = LocateElement.Get_Element(data_set[0],appium_driver)
                Element = [Element]
                
        if Element == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed" 
        
        # Get the 'action' parameter and 'value' from step data
        for each_step_data_item in data_set[0]:
            if each_step_data_item[1]=="action":
                expected_text_data = each_step_data_item[2].split('||') # Split the separator in case multiple string provided in the same data_set
                validation_type = each_step_data_item[0]
        
        #Get the string for a single and multiple element(s)
        list_of_element_text = []
        list_of_element = []
        if len(Element)== 0:
            return False
        elif len(Element) == 1:           
            for each_text in Element:
                list_of_element = each_text.text # Extract the text element
                list_of_element_text.append(list_of_element)
        elif len(Element) > 1:           
            for each_text in Element:
                list_of_element = each_text.text.split('\n') # Extract the text elements
                list_of_element_text.append(list_of_element[0])
        else:
            return "failed"
            
        #Extract only the visible element(s)
        visible_list_of_element_text = []
        for each_text_item in list_of_element_text:
            if each_text_item != "":
                visible_list_of_element_text.append(each_text_item)
        
        # Validate the partial text/string provided in the step data with the text obtained from the device
        if validation_type == "validate partial text":
            actual_text_data = visible_list_of_element_text
            CommonUtil.ExecLog(sModuleInfo, ">>>>>> Expected Text: %s" %expected_text_data, 0)
#             print (">>>>>> Expected Text: %s" %expected_text_data)
            CommonUtil.ExecLog(sModuleInfo, ">>>>>>>> Actual Text: %s" %actual_text_data, 0)
#             print (">>>>>>>> Actual Text: %s" %actual_text_data)
            for each_actual_text_data_item in actual_text_data:
                if expected_text_data[0] in each_actual_text_data_item: # index [0] used to remove the unicode 'u' from the text string
                    CommonUtil.ExecLog(sModuleInfo, "Validate the text element %s using partial match." %visible_list_of_element_text, 0)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to validate the text element %s. Check the text element(s) in step_data(s) and/or in screen text." %visible_list_of_element_text, 3)
                    return "failed"
        
        # Validate the full text/string provided in the step data with the text obtained from the device
        if validation_type == "validate full text":
            actual_text_data = visible_list_of_element_text
            CommonUtil.ExecLog(sModuleInfo, ">>>>>> Expected Text: %s" %expected_text_data, 0)
#             print (">>>>>> Expected Text: %s" %expected_text_data)
            CommonUtil.ExecLog(sModuleInfo, ">>>>>>>> Actual Text: %s" %actual_text_data, 0)
#             print (">>>>>>>> Actual Text: %s" %actual_text_data)
            if (expected_text_data[0] == actual_text_data[0]): # index [0] used to remove the unicode 'u' from the text string
                CommonUtil.ExecLog(sModuleInfo, "Validate the text element %s using complete match." %visible_list_of_element_text, 0)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Unable to validate the text element %s. Check the text element(s) in step_data(s) and/or in screen text." %visible_list_of_element_text, 3)
                return "failed"
        
        # Validate all the text/string provided in the step data with the text obtained from the device
        if validation_type == "validate screen text":
            CommonUtil.ExecLog(sModuleInfo, ">>>>>> Expected Text: %s" %expected_text_data, 0)
#             print (">>>>>> Expected Text: %s" %expected_text_data)
            CommonUtil.ExecLog(sModuleInfo, ">>>>>>>> Actual Text: %s" %visible_list_of_element_text, 0)
#             print (">>>>>>>> Actual Text: %s" %visible_list_of_element_text)
            i = 0
            for x in xrange(0, len(visible_list_of_element_text)): 
                if (visible_list_of_element_text[x] == expected_text_data[i]): # Validate the matching string
                    CommonUtil.ExecLog(sModuleInfo, "The text element '%s' has been validated by using complete match." %visible_list_of_element_text[x], 1)
                    i += 1
                    return "passed"
                else:
                    visible_elem = [ve for ve in visible_list_of_element_text[x].split()]
                    expected_elem = [ee for ee in expected_text_data[i].split()]
                    for elem in visible_elem: # Validate the matching word
                        if elem in expected_elem:
                            CommonUtil.ExecLog(sModuleInfo, "Validate the text element '%s' using element match." %elem, 1)
                            return "passed"
                        else:
                            CommonUtil.ExecLog(sModuleInfo, "Unable to validate the text element '%s'. Check the text element(s) in step_data(s) and/or in screen text." %elem, 1)
                            return "failed"
                    if (visible_elem[0] in expected_elem):
                        i += 1
                        
        else:
            CommonUtil.ExecLog(sModuleInfo, "Incorrect validation type. Please check step data", 3)
            return "failed"
        
    except Exception:
        errMsg = "Could not compare text as requested."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_program_names(search_name):
    ''' Find Package and Activity name based on wildcard match '''
    # Android only
    # Tested as working on v4.4.4, v5.1, v6.0.1
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    global device_serial
    serial = ''
    if device_serial != '': serial = "-s %s" % device_serial
    
    # Find package name for the program that's already installed
    try:
        if adbOptions.is_android_connected(device_serial) == False:
            CommonUtil.ExecLog(sModuleInfo, "Could not detect any connected Android devices", 3)
            return '', '' # Failure handling in calling function

        cmd = 'adb %s shell pm list packages' % serial
        res = subprocess.check_output(cmd, shell = True) # Get list of installed packages on device
        res = str(res).replace('\\r','') # Remove \r text if any
        res = str(res).replace('\\n','\n') # replace \n text with line feed
        res = str(res).replace('\r','') # Remove \r carriage return if any
        ary = res.split('\n') # Split into list
        
        package_name = ''
        package_list = []
        for line in ary: # For each package
            if search_name.lower() in line:
                package_list.append(line.replace('package', '').replace(':', ''))
                
        if len(package_list) == 0:
            CommonUtil.ExecLog(sModuleInfo, "Did not find installed package: %s" % search_name, 3)
            return '', ''
        elif len(package_list) > 1: CommonUtil.ExecLog(sModuleInfo, "Found more than one packages. Will use the first found. Please specify a more accurate package name. Found packages: %s" % package_list, 2)
        package_name = package_list[0] # Save first package found
            
        # Launch program using only package name
        cmd = 'adb %s shell monkey -p %s -c android.intent.category.LAUNCHER 1' % (serial, package_name)
        res = subprocess.check_output(cmd, shell = True)
        time.sleep(3)
    
        # Get the activity name
        cmd = 'adb %s shell dumpsys window windows' % serial
        res = subprocess.check_output(cmd, shell = True)
        m = re.search('CurrentFocus=.*?\s+([\w\.]+)/([\w\.]+)', str(res))
    
        # Return package and activity names
        if m.group(1) != '' and m.group(2) != '':
            return m.group(1), m.group(2)
        else:
            return '', ''
    except:
        result = CommonUtil.Exception_Handler(sys.exc_info())
        return result, ''

def device_information(data_set):
    ''' Returns the requested device information '''
    # This is the sequential action interface for much of the adbOptions.py and iosOptions.py, which provides direct device access via their standard comman line tools
    # Note: This function does not require an Appium instance, so it can be called without calling launch_application() first
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    # Parse data set
    try:
        
        if device_id:
            dep = appium_details[device_id]['type']
        else: # In case this was invoked without setting up appium, try to figure out connected device type. This could be useful if user just wants to reboot the phone
            if adbOptions.is_android_connected(device_serial):
                dep = 'android'
            else:
                dep = 'ios'
        cmd = ''
        shared_var = ''
        
        for row in data_set: # Check each row
            if row[1] == 'action': # If this is the action row
                cmd = row[0].lower().strip() # Save the command type
                shared_var = row[2] # Save the name of the shared variable
                break

        if cmd == '':
            CommonUtil.ExecLog(sModuleInfo,"Action's Field contains incorrect information", 3)
            return 'failed'
        if shared_var == '':
            CommonUtil.ExecLog(sModuleInfo,"Action's Value contains incorrect information. Expected Shared Variable, or string", 3)
            return 'failed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error when trying to read Field and Value for action on device '%s' with appium details: %s" % (device_id, str(appium_details)))

    # Ensure device is connected
    if dep == 'android':
        if adbOptions.is_android_connected(device_serial) == False:
            CommonUtil.ExecLog(sModuleInfo, "Could not detect any connected Android devices", 3)
            return 'failed'

    # Get device information
    try:
        if cmd == 'imei':
            if dep == 'android': output = adbOptions.get_device_imei_info(device_serial)
            elif dep == 'ios': output = iosOptions.get_ios_imei(device_serial)
        elif cmd == 'version':
            if dep == 'android':output = adbOptions.get_android_version(device_serial)
            elif dep == 'ios': output = iosOptions.get_ios_version(device_serial)
        elif cmd == 'model name':
            if dep == 'android': output = adbOptions.get_device_model(device_serial)
            elif dep == 'ios': output = iosOptions.get_product_name(device_serial)
        elif cmd == 'phone name':
            if dep == 'ios': output = iosOptions.get_phone_name(device_serial)
        elif cmd == 'serial no':
            if dep == 'android': output = adbOptions.get_device_serial_no(device_serial)
        elif cmd == 'storage':
            if dep == 'android': output = adbOptions.get_device_storage(device_serial)
        elif cmd == 'reboot':
            if shared_var == '*': # If asterisk, then assume one or more attached and reset them all
                shared_var = '' # Unset this, so we don't create a shared variable with it 
                if dep == 'android': adbOptions.reset_all_android()
            else: # Reset device. If shared_var is a serial number (shared variable or string), it will reset that one specifically
                if dep == 'android': adbOptions.reset_android(shared_var) # Reset this one device
            output = 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo,"Action's Field contains incorrect information", 3)
            return 'failed'

        if output in failed_tag_list or output=='':
            CommonUtil.ExecLog(sModuleInfo, "Could not find the device info about '%s'" % (cmd), 3)
            return "failed"
            
        # Save the output to the user specified shared variable
        if shared_var != '':
            Shared_Resources.Set_Shared_Variables(shared_var, output)
            CommonUtil.ExecLog(sModuleInfo,"Saved %s [%s] as %s" % (cmd, str(output), shared_var), 1)
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def set_device_password(data_set):
    ''' Saves the device password to shared variables for use in unlocking the phone '''
    # Caveat: Only allows one password stored at a time
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    # Parse data set
    try:
        password = data_set[0][2].strip() # Read password from Value field
        if password != '':
            Shared_Resources.Set_Shared_Variables('device_password', password)
            CommonUtil.ExecLog(sModuleInfo, "Device password saved as: %s" % password, 1)
            return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Password cannot be blank. Expected Value field of action row to be a PIN or PASSWORD", 3)
            return 'failed'
        
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error when trying to read Field and Value for action")

def switch_device(data_set):
    ''' When multiple devices are connected, switches focus to one in particular given the serial number '''
    # Device will be set as default until this function is called again
    # Not needed when only one device is connected
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    # Parse data set
    try:
        ID = data_set[0][2].lower().strip() # Read password from Value field
        if ID != '':
            global device_serial, appium_details, appium_driver, device_id
            
            # Get information from dictionary, and update global variables
            device_serial = appium_details[ID]['serial']
            appium_driver = appium_details[ID]['driver']
            device_id = ID

            CommonUtil.ExecLog(sModuleInfo, "Switched focus to: %s" % ID, 1)
            return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Serial number cannot be blank. Expected Value field of action row to be a serial number or UUID of the device connected via USB", 3)
            return 'failed'
        
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error when trying to read Field and Value for action")

