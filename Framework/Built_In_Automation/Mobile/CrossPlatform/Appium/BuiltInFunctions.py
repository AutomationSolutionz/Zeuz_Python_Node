# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

''' Name: Built In Functions - Appium
    Description: Contains all Sequential Actions related to automating Android and IOS using Appium
'''

#########################
#                       #
#        Modules        #
#                       #
#########################

from appium import webdriver
import os, sys, time, inspect, subprocess, re, signal, thread, requests
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

#########################
#                       #
#   Global Variables    #
#                       #
#########################
# Recall appium driver, if not already set - needed between calls in a Zeuz test case
appium_port = 4721 # Default appium port - changes if we have multiple devices
wdaLocalPort = 8100
appium_details = {} # Used to store device serial number, appium driver, if multiple devices are used
appium_driver = None # Holds the currently used appium instance
device_serial = '' # Holds the identifier for the currently used device (if any are specified)
device_id = '' # Holds the name of the device the user has specified, if any. Relationship is set elsewhere

from Framework.Utilities import All_Device_Info

# Recall dependency, if not already set
dependency = None
if Shared_Resources.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables('dependency') # Retreive appium driver
else:
    pass # May be phasing out dependency for mobile 
    #raise ValueError("No dependency set - Cannot run")

# Recall file attachments
file_attachment = {}
if Shared_Resources.Test_Shared_Variables('file_attachment'): # Check if file_attachement is set
    file_attachment = Shared_Resources.Get_Shared_Variables('file_attachment') # Retreive file attachments

# Recall appium details
if Shared_Resources.Test_Shared_Variables('appium_details'): # Check if driver is already set in shared variables
    appium_details = Shared_Resources.Get_Shared_Variables('appium_details') # Retreive appium driver
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
        all_device_info = All_Device_Info.get_all_connected_device_info()
        
        # Ensure we have at least one device connected
        if len(all_device_info) == 0:
            CommonUtil.ExecLog(sModuleInfo,"Could not detect any connected devices. Ensure at least one is attached via USB, and that it is authorized - Trusted / USB Debugging enabled", 3)
            return 'failed'

        imei=''
        device_name = ''
        product_version = ''
        serial = ''
        did = ''
        device_type = ''

        # Check if serial provided is a real serial number, name or rubish that should be ignored
        serial_check = False
        for device in all_device_info: # For each device serial number
            if serial_or_name.lower() == device.lower():
                serial = all_device_info[device]['id']  # Save serial number
                device_type = all_device_info[device]['type'].lower()  # Save device type android/ios
                imei = all_device_info[device]['imei']
                device_name = all_device_info[device]['model']
                product_version = all_device_info[device]['osver']
                did = device
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
                    imei = device_info[did]['imei']
                    device_name = all_device_info[device]['model']
                    product_version = all_device_info[device]['osver']
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
                    imei = device_info[did]['imei']
                    device_type = device_info[did]['type'].lower()
                    device_name = all_device_info[device]['model']
                    product_version = all_device_info[device]['osver']
                    CommonUtil.ExecLog(sModuleInfo,"Found a device selected at Deploy: %s" % did, 0)
                    break

            # Lastly, if nothing above is set, the user did not specify anything, and we have no information from the server. Pick a connected device, and fail if there are none
            else: # No devices sent, none specified
                for device in devices:
                    did = 'default'
                    serial = device # Get Serial
                    device_type = devices[device] # Get type
                    CommonUtil.ExecLog(sModuleInfo,"No device information found. Picked one that is connected: %s" % serial, 0)
                    break # Only take the first device'''

        # At the end, we should have at least one device
        if serial != '' and device_type != '' and did != '':
            # Verify this device was not already selected and run previously
            if did in appium_details:
                CommonUtil.ExecLog(sModuleInfo,"The selected device was previously run. You cannot run it more than once in a session. Either your step data is calling the 'launch' action multiple times without specifying specific devices, or you did not call the 'teardown' action in a previous run.", 3)
                return 'failed'

            # Verify this device is actually connected
            if not serial_in_devices(serial,all_device_info):
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
            appium_details[device_id]['imei'] = imei
            appium_details[device_id]['platform_version'] = product_version
            appium_details[device_id]['device_name'] = device_name
            
            # Store in shared variable, so it doens't get forgotten
            Shared_Resources.Set_Shared_Variables('device_serial', device_serial, protected = True)
            Shared_Resources.Set_Shared_Variables('device_id', device_id, protected = True) # Save device id, because functions outside this file may require it

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
    # Recall appium details
    if Shared_Resources.Test_Shared_Variables('device_info'):  # Check if device_info is already set in shared variables
        device_info = Shared_Resources.Get_Shared_Variables('device_info')  # Retreive device_info
    
    # Parse data set
    try:
        package_name = '' # Name of application package
        activity_name = '' # Name of application activity
        serial = '' # Serial number (may also be random string like "launch", "na", etc)
        platform_version = ''
        device_name = ''
        ios = ''

        for row in data_set: # Find required data
            if str(row[0]).strip().lower() in ('android package','package') and row[1] == 'element parameter':
                package_name = row[2]
            elif str(row[0]).strip().lower() in ('app activity', 'activity','android activity') and row[1] == 'element parameter':
                activity_name = row[2]
            elif str(row[0]).strip().lower() in ('ios','ios simulator') and row[1] == 'element parameter':
                ios = row[2]
            elif str(row[1]).strip().lower() == 'action':
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
        if appium_details[device_id]['type'] == 'android' and package_name == '' or package_name in failed_tag_list:
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
        if 'platform_version' in appium_details[device_id]:
            platform_version = appium_details[device_id]['platform_version']
        if 'device_name' in appium_details[device_id]:
            device_name = appium_details[device_id]['device_name']
        launch_app = True
        if appium_details[device_id]['driver'] == None: # Only create a new appium instance if we haven't already (may be done by install_and_start_driver())
            result,launch_app = start_appium_driver(package_name, activity_name,platform_version=platform_version,device_name=device_name,ios=ios)
            if result == 'failed':
                return 'failed'
        
        CommonUtil.ExecLog(sModuleInfo,"Launching %s" % package_name,0)
        if launch_app: #if ios simulator then no need to launch app again
            appium_driver.launch_app() # Launch program configured in the Appium capabilities
        CommonUtil.TakeScreenShot(sModuleInfo) # Capture screenshot, if settings allow for it
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
    
    global appium_port, appium_details, device_serial, appium_binary, device_id, wdaLocalPort

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
        wdaLocalPort += 2
        try:
            appium_server = None
            if sys.platform  == 'win32': # We need to open appium in it's own command dos box on Windows
                cmd = 'start "Appium Server" /wait /min cmd /c %s -p %d' % (appium_binary, appium_port) # Use start to execute and minimize, then cmd /c will remove the dos box when appium is killed
                appium_server = subprocess.Popen(cmd, shell = True) # Needs to run in a shell due to the execution command
            elif sys.platform == 'darwin':
                appium_server = subprocess.Popen([appium_binary, '-p', str(appium_port)])
            else:
                try:
                    appium_binary_path = os.path.normpath(appium_binary)
                    appium_binary_path = os.path.abspath(os.path.join(appium_binary_path, os.pardir))
                    env = {"PATH": str(appium_binary_path)}
                    appium_server = subprocess.Popen(['appium', '-p', str(appium_port)], env=env)
                except:
                    CommonUtil.ExecLog(sModuleInfo,"Couldn't launch appium server, please do it manually ny typing 'appium &' in the terminal",2)
                    pass
            appium_details[device_id]['server'] = appium_server # Save the server object for teardown
        except Exception, returncode: # Couldn't run server
            return CommonUtil.Exception_Handler(sys.exc_info(), None, "Couldn't start Appium server. May not be installed, or not in your PATH: %s" % returncode)
        
        # Wait for server to startup and return
        CommonUtil.ExecLog(sModuleInfo,"Waiting for server to start on port %d: %s" % (appium_port, appium_binary), 0)
        maxtime = time.time() + 10 # Maximum time to wait for appium server
        while True: # Dynamically wait for appium to start by polling it
            if time.time() > maxtime: break # Give up if max time was hit
            try: # If this works, then stop waiting for appium
                r = requests.get('http://localhost:%d/wd/hub/sessions' % appium_port) # Poll appium server
                if r.status_code: break
            except: pass # Keep waiting for appium to start

        if appium_server:
            CommonUtil.ExecLog(sModuleInfo,"Server started", 1)
            return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo,"Server failed to start", 3)
            return 'failed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error starting Appium server")

def start_appium_driver(package_name = '', activity_name = '', filename = '', platform_version='', device_name='',ios=''):
    ''' Creates appium instance using discovered and provided capabilities '''
    # Does not execute application
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        global appium_driver, appium_details, device_id, wdaLocalPort
        launch_app = True
        if appium_details[device_id]['driver'] == None:
            # Start Appium server
            if start_appium_server() in failed_tag_list:
                return 'failed',launch_app

            # Create Appium driver
    
            # Setup capabilities
            desired_caps = {}
            desired_caps['platformName'] = appium_details[device_id]['type'] # Set platform name
            desired_caps['autoLaunch'] = 'false' # Do not launch application
            desired_caps['fullReset'] = 'false' # Do not clear application cache when complete
            desired_caps['noReset'] = 'true' # Do not clear application cache when complete
            desired_caps['newCommandTimeout'] = 600 # Command timeout before appium destroys instance
            
            if str(appium_details[device_id]['type']).lower() == 'android':
                if adbOptions.is_android_connected(device_serial) == False:
                    CommonUtil.ExecLog(sModuleInfo, "Could not detect any connected Android devices", 3)
                    return 'failed',launch_app

                CommonUtil.ExecLog(sModuleInfo,"Setting up with Android",1)
                desired_caps['platformVersion'] = adbOptions.get_android_version(appium_details[device_id]['serial']).strip()
                desired_caps['deviceName'] = adbOptions.get_device_model(appium_details[device_id]['serial']).strip()
                if package_name:
                    desired_caps['appPackage'] = package_name.strip()
                if activity_name:
                    desired_caps['appActivity'] = activity_name.strip()
                if filename and package_name == '': # User must specify package or file, not both. Specifying filename instructs Appium to install
                    desired_caps['app'] = PATH(filename).strip()
                    
            elif str(appium_details[device_id]['type']).lower() == 'ios':
                CommonUtil.ExecLog(sModuleInfo,"Setting up with IOS",1)
                if appium_details[device_id]['imei'] == 'Simulated': #ios simulator
                    launch_app = False #ios simulator so need to launch app again
                    if Shared_Resources.Test_Shared_Variables('ios_simulator_folder_path'): #if simulator path already exists
                        app = Shared_Resources.Get_Shared_Variables('ios_simulator_folder_path')
                        app = os.path.normpath(app)
                    else:
                        app = os.path.normpath(os.getcwd()+os.sep + os.pardir)
                        app = os.path.join(app,"iosSimulator")
                        #saving simulator path for future use
                        Shared_Resources.Set_Shared_Variables('ios_simulator_folder_path',str(app))
                    app = os.path.join(app, ios)
                    bundle_id = str(subprocess.check_output(['osascript', '-e', 'id of app "%s"'%str(app)])).strip()
                    desired_caps = {}
                    desired_caps['app'] = app  # Use set_value() for writing to element
                    desired_caps['platformName'] = 'iOS'  # Read version #!!! Temporarily hard coded
                    desired_caps['platformVersion'] = platform_version
                    desired_caps['deviceName'] = device_name
                    desired_caps['bundleId'] = bundle_id
                    desired_caps['wdaLocalPort'] = wdaLocalPort
                    desired_caps['udid'] = appium_details[device_id]['serial']
                    desired_caps['newCommandTimeout'] = 6000
                else: #for real ios device, not developed yet
                    desired_caps['sendKeyStrategy'] = 'setValue' # Use set_value() for writing to element
                    desired_caps['platformVersion'] = '10.3' # Read version #!!! Temporarily hard coded
                    desired_caps['deviceName'] = 'iPhone' # Read model (only needs to be unique if using more than one)
                    desired_caps['bundleId'] = ios
                    desired_caps['udid'] = appium_details[device_id]['serial'] # Device unique identifier - use auto if using only one phone
            else:
                CommonUtil.ExecLog(sModuleInfo, "Invalid device type: %s" % str(appium_details[device_id]['type']), 3)
                return 'failed',launch_app
            CommonUtil.ExecLog(sModuleInfo,"Capabilities: %s" % str(desired_caps), 0)
            
            # Create Appium instance with capabilities
            try:
                appium_driver = webdriver.Remote('http://localhost:%d/wd/hub' % appium_port, desired_caps) # Create instance

                if appium_driver: # Make sure we get the instance
                    appium_details[device_id]['driver'] = appium_driver
                    Shared_Resources.Set_Shared_Variables('appium_details', appium_details)
                    CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export()) # Get all the shared variables, and pass them to CommonUtil
                    CommonUtil.ExecLog(sModuleInfo,"Appium driver created successfully.",1)
                    return "passed",launch_app
                else: # Error during setup, reset
                    appium_driver = None
                    CommonUtil.ExecLog(sModuleInfo,"Error during Appium setup", 3)
                    return 'failed',launch_app
            except Exception,e:
                print e
                return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error connecting to Appium server to create driver instance"),launch_app

        else: # Driver is already setup, don't do anything
            CommonUtil.ExecLog(sModuleInfo,"Driver already configured, not re-doing", 0)
            return 'passed',launch_app
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info()),launch_app

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
    
    global appium_details, appium_server, device_id, device_serial, device_info, appium_port, wdaLocalPort
    
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
        appium_port = 4721
        wdaLocalPort = 8100
        appium_server, device_id, device_serial = '', '', ''
        Shared_Resources.Set_Shared_Variables('appium_details', '')
        Shared_Resources.Set_Shared_Variables('device_info', '')
        Shared_Resources.Set_Shared_Variables('device_id', '')
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
    
    
def install_application(data_set):
    ''' Install application to device '''
    # adb does the work. Does not require appium instance. User needs to call launch action to create instance
    # Two formats allowed: Filename on action row, or filename on element parameter row, and optional serial number on action row
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Parse data set
    try:
        file_name = ''
        serial = ''
        for row in data_set: # Find required data
            if row[1] == 'action': # If using format of package on action line, and no serial number
                serial = row[2].strip() # May be serial or filename, we'll figure out later
            elif row[1] == 'element parameter': # If using the format of filename on it's own row, and possibly a serial number on the action line
                file_name = row[2].strip() # Save filename
        if file_name == '': # Fix previous filename from action row if no element parameter specified
            file_name = serial # There was no element parameter row, so take the action row value for the filename
            serial = ''

        # Try to find the image file
        if file_name not in file_attachment and os.path.exists(file_name) == False:
            CommonUtil.ExecLog(sModuleInfo, "Could not find file attachment called %s, and could not find it locally" % file_name, 3)
            return 'failed'
        if file_name in file_attachment: file_name = file_attachment[file_name] # In file is an attachment, get the full path
        if file_name == '':
            CommonUtil.ExecLog(sModuleInfo,"File not specified or there was a problem reading the file attachments", 3)
            return 'failed'

        # Try to determine device serial
        if serial != '':
            find_correct_device_on_first_run(serial, device_info)
            serial = device_serial # Should be populated with an available device serial or nothing
            
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    try:
        result = adbOptions.install_app(file_name, serial)
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Could not install application (%s)" % file_name, 3)
            return 'failed'
        CommonUtil.ExecLog(sModuleInfo, "Installed %s to device %s" % (file_name, serial), 1)
        return 'passed'

    except Exception:
        errMsg = "Error installing application"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def uninstall_application(data_set):
    ''' Uninstalls/removes application from device '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Parse data set
    try:
        package = ''
        serial = ''
        for row in data_set: # Find required data
            if row[1] == 'action': # If using format of package on action line, and no serial number
                serial = row[2].strip() # May be serial or filename, we'll figure out later
            elif row[1] == 'element parameter': # If using the format of filename on it's own row, and possibly a serial number on the action line
                package = row[2].strip() # Save filename
        if package == '': # Fix previous filename from action row if no element parameter specified
            package = serial # There was no element parameter row, so take the action row value for the filename
            serial = ''

        # Try to find package name
        package, activity_name = get_program_names(package) # Get package name

        # Try to determine device serial
        if serial != '':
            find_correct_device_on_first_run(serial, device_info)
            serial = device_serial # Should be populated with an available device serial or nothing
            
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    try:
        result = adbOptions.uninstall_app(package, serial)
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Could not uninstall application (%s)" % package, 3)
            return 'failed'
        CommonUtil.ExecLog(sModuleInfo, "Uninstalled %s from device %s" % (package, serial), 1)
        return 'passed'

    except Exception:
        errMsg = "Error uninstalling application"
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
            adbOptions.swipe_android(x_start, y_start, x_end, y_end, duration, device_serial) # Use adb if specifically asked for it
        else:
            appium_driver.swipe(x_start, y_start, x_end, y_end, duration) # Use Appium to swipe by default

        CommonUtil.TakeScreenShot(sModuleInfo) # Capture screenshot, if settings allow for it
        return "passed"
    except Exception:
        errMsg = "Unable to swipe."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def swipe_handler(data_set):
    ''' Swipe screen based on user input '''
    '''
        Function: Performs a single swipe gesture in a vertical or horizonal direction
        Inputs:
            direction (mandatory except when using exact): left/right/up/down (eg: 'left' = from right to left)
            exact: Ignores all other settings, user needs to specify exact coordinates in the format of x1, y1, x2, y2
            inset (optional): Defaults to 10%. Swipe starts at inset
            position (optional): Defaults to 50%. Swipe this far from the top or left. So if I swipe left to right, Y will be 50%, so the middle of the screen with a horizontal swipe
            duration (optional): Defaults to 100ms. Complete the swipe gesture over this time period
            element parameter: Ignores  "exact". Direction is required. Use an element as the starting point (top left corner of the element). Calculations are based off that
    '''
     
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
 
    def Calc_Swipe(w, h, inset, direction, position, exact):
        ''' Calculate swipe based on area of interest (screen or element) '''
        try:
            # Adjust numbers depending on type provided by user - float or integer expected here - convert into pixels
            if exact != '': # User specified exact coordinates, so use those and nothing else
                x1, y1, x2, y2 = map(int, exact.split(','))
            else:
                inset = int(str(inset).replace('%', '')) / 100.0 # Convert % to float
                position = int(str(position).replace('%', '')) / 100.0 # Convert % to float
                
                if direction == 'left':
                    tmp = 1.0 - inset # Calculate from other end (X% from max width)
                    inset = int(tmp * w)
                    position = int(position * h)
                elif direction == 'down':
                    inset = int(inset * h) # Convert into pixels for that direction
                    position = int(position * w)
                elif direction == 'right':
                    inset = int(inset * w) # Convert into pixels for that direction
                    position = int(position * h)
                elif direction == 'up':
                    tmp = 1.0 - inset # Calculate from other end (X% from max height)
                    inset = int(tmp * h)
                    position = int(position * w)
                
                # Calculate exact pixel for the swipe
                if direction == 'left':
                    x1 = inset
                    x2 = 1
                    y1 = position
                    y2 = position
                elif direction == 'down':
                    x1 = position
                    x2 = position
                    y1 = inset
                    y2 = h
                elif direction == 'right':
                    x1 = inset
                    x2 = w
                    y1 = position
                    y2 = position
                elif direction == 'up':
                    x1 = position
                    x2 = position
                    y1 = inset
                    y2 = 1
                    
            return x1, x2, y1, y2, inset, position # Return inset and position just for logging purposes)
        except Exception:
            errMsg = "Error calculating swipe gesture"
            result = CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
            return result, '', '', ''

    # Get screen size for calculations
    try:
        full_screen_mode = False # Use appium swipe instead of adb swipe (which is used when there's a vitual navigation bar that we need to swipe under)
        window_size1 = get_window_size() # get_size method (standard)
        window_size2 = get_window_size(True) # xpath() method
        if window_size1 == 'failed':
            CommonUtil.ExecLog(sModuleInfo, "Couldn't read screen size", 3)
            return 'failed'
        height_with_navbar = int(window_size1['height']) # Read standard height (on devices with a nav bar, this is not the actual height of the screen)
        height_without_navbar = int(window_size2['height']) # Read full screen height (not at all accurate on devices without a navbar
        if height_with_navbar < height_without_navbar: # Detected full screen mode and the height readings were different, indicating a navigation bar needs to be compensated for
            w = int(window_size2['width'])
            h = int(window_size2['height'])
            CommonUtil.ExecLog(sModuleInfo, "Detected navigation bar. Enabling ADB swipe for that area", 0)
            full_screen_mode = True # Flag to use adb to swipe later on
        else:
            w = int(window_size1['width'])
            h = int(window_size1['height'])

        CommonUtil.ExecLog(sModuleInfo, "Screen size (WxH): %d x %d" % (w, h), 0)
    except Exception:
        errMsg = "Unable to read screen size"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)     

    # Parse data set
    try:
        inset = 10 # Default 10% of screen from edge as start of swipe
        direction = '' # Left/right/up/down
        exact = '' # Coordinates of exact swipe gesture in x1, y1, x2, y2
        position =  50 # Default 50% of screen from edge for general swipes
        Element = '' # Optional element object
        duration = 100 # Duration of the swipe in ms
        for row in data_set:
            if row[1] == 'input parameter':
                op = row[0].strip().lower()
                if op == 'inset':
                    inset = row[2].strip()
                elif op == 'direction':
                    direction = row[2].lower().strip()
                elif op == 'exact':
                    exact = row[2].lower().strip().replace(' ','')
                elif op == 'position':
                    position = row[2].lower().strip()
                elif op == 'duration':
                    duration = int(row[2].lower().strip())
            elif row[1] == 'element parameter':
                Element = LocateElement.Get_Element(data_set,appium_driver)
                if Element == "failed":
                    CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                    return "failed" 

        # Verify we have what we need
        if inset == '' or direction not in ('left', 'right', 'up', 'down') or position == '':
            if exact == '': # If this is set, then the others don't matter, so continue with the gesture
                CommonUtil.ExecLog(sModuleInfo, "Missing critical swipe values. Either 'inset' (optional), 'direction' (required), or 'position' (optional) are missing, wrong or blank", 3)
                return 'failed'
        
        # If an element parameter was provided, get it's x, y, w, h
        if Element:
            location = Element.location # Get element x,y coordinates
            size = Element.size
            elementX, elementY = int(location['x']), int(location['y'])
            elementW, elementH = int(size['width']), int(size['height'])
            CommonUtil.ExecLog(sModuleInfo,"Element X, Y, W, H: %d, %d, %d, %d" % (elementX, elementY, elementW, elementH), 0)
            
            # Calculate coordinates, based on element position and size
            x1, x2, y1, y2, inset, position = Calc_Swipe(elementW, elementH, inset, direction, position, '')
            if x1 in failed_tag_list: return "failed"
            # Using element calculations, now calculate to make relative to entire screen size
            if direction == 'left':
                x1 += elementX
                y1 += elementY
                y2 += elementY
            elif direction == 'down':
                y1 += elementY
                y2 = h
                x1 += elementX
                x2 += elementX
            elif direction == 'right':
                x1 += elementX
                x2 = w
                y1 += elementY
                y2 += elementY
            elif direction == 'up':
                y1 += elementY
                x1 += elementX
                x2 += elementX
        else:
            # No element, calculate swipe coordinates based on screen size
            x1, x2, y1, y2, inset, position = Calc_Swipe(w, h, inset, direction, position, exact)
            if x1 in failed_tag_list: return "failed" 
            
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    # Perform swipe gesture 
    try:
        if exact != '': CommonUtil.ExecLog(sModuleInfo, "Performing an exact swipe using coordinates: %d, %d to %d, %d %d ms" % (x1, y1, x2, y2, duration), 1)
        else: CommonUtil.ExecLog(sModuleInfo, "Performing calculated swipe gesture based on inset: %d, position: %d, direction: %s, calculated as %d, %d to %d, %d %d ms" % (inset, position, direction, x1, y1, x2, y2, duration), 1) 
        
        if full_screen_mode == True and (y1 >= height_with_navbar or y2 >= height_with_navbar): # Swipe in the navigation bar area if the device has one, when in full screen mode
            result = Swipe(x1, y1, x2, y2, duration, adb = True) # Perform swipe using adb
        else: # Swipe via appium by default
            result = Swipe(x1, y1, x2, y2, duration, adb = True) # Perform swipe !!!adb set True for testing

        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not swipe the screen", 1)
            return 'failed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Swiped the screen successfully", 1)
            return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(),None, "Error performing swipe gesture")     

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

def Long_Press_Appium(data_set):
    ''' Press and hold an element '''
    
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

                if str(appium_details[device_id]['type']).lower() == 'ios':
                    Element.set_value(text_value) # Work around for IOS issue in Appium v1.6.4 where send_keys() doesn't work
            except Exception:
                errMsg = "Found element, but couldn't write text to it"
                return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

            # This is wrapped in it's own try block because we sometimes get an error from send_keys stating "Parameters were incorrect". However, most devices work only with send_keys
            try:
                if str(appium_details[device_id]['type']).lower() != 'ios':
                    Element.send_keys(text_value) # Enter the user specified text
            except Exception:
                CommonUtil.ExecLog(sModuleInfo, "Found element, but couldn't write text to it. Trying another method", 2)
                '''try:
                    Element.set_value(text_value) # Enter the user specified text
                except Exception:
                    errMsg = "Found element, but couldn't write text to it. Giving up"
                    return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)'''

            # Complete the action
            try:
                #appium_driver.hide_keyboard() # Remove keyboard
                CommonUtil.TakeScreenShot(sModuleInfo) # Capture screen
                CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s" % text_value, 1)
                return "passed"
            except Exception:
                errMsg = "Found element, but couldn't write text to it"
                return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    except Exception:
        errMsg = "Could not find element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def Android_Keystroke_Key_Mapping(keystroke, hold_key = False):
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
            key = 66
        elif keystroke == "go back" or keystroke == "back":
            key = 4
        elif keystroke == "spacebar":
            key = 62
        elif keystroke == "backspace":
            key = 67
        elif keystroke == "call": # Press call connect, or starts phone program if not already started
            key = 5
        elif keystroke == "end call":
            key = 6
        elif keystroke == "home":
            key = 3
        elif keystroke == "mute":
            key = 164
        elif keystroke == "volume down":
            key = 25
        elif keystroke == "volume up":
            key = 24
        elif keystroke == "wake":
            key = 224
        elif keystroke == "power":
            key = 26
        elif keystroke in ("app switch", "task switch", "overview", "recents"): # Task switcher / overview screen
            key = 187
        elif keystroke == "page down":
            key = 93
        elif keystroke == "page up":
            key = 92
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unsupported key event: %s" % keystroke, 3)
            return 'failed'
        
        if hold_key:
            appium_driver.long_press_keycode(key) # About 0.5s hold, not configurable
        else:
            appium_driver.press_keycode(key) # driver.keyevent() is depreciated

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


def Keystroke_Appium(data_set):
    ''' Send physical or virtual key press or long key press event '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Parse data set
    try:
        keystroke_type = data_set[0][0].replace(' ', '').lower() # "keypress" or "long press"
        keystroke_value = data_set[0][2]
        
        if keystroke_value == '':
            CommonUtil.ExecLog(sModuleInfo,"Could not find keystroke value", 3)
            return 'failed'
        
        if keystroke_type == 'keypress': hold_key = False
        else: hold_key = True
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    try:
        # Execute the correct key stroke handler for the dependency
        if appium_details[device_id]['type'] == 'android':
            result = Android_Keystroke_Key_Mapping(keystroke_value, hold_key)
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
    # Note: Some programs require the very first activity name in order to launch the program. This may be a splash screen.
    # Alternative method to obtain activity name: Android-sdk/build-tools/aapt dumb badging program.apk| grep -i activity. This extracts it from the apk directly
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
#     def find_activity(secs):
#         global activity_list
#         activity_list = []
#         etime = time.time() + secs # End time
#         
#         cmd = 'adb %s shell dumpsys window windows' % serial # Command
#         while True:
#             try:
#                 # Get the activity name
#                 res = subprocess.check_output(cmd, shell = True) # Execute
#                 activity_list.append(res)
#             except: # If we dont' get a regex match, we may get here, not a problem
#                 pass
#             if time.time() > etime: # Exit loop if time expires
#                 break
#             
#         for i in range(len(activity_list)):
#             try:
#                 res = activity_list[i]
#                 m = re.search('CurrentFocus=.*?\s+([\w\.]+/[\w\.]+)', str(res)) # Find program which has the foreground focus
#                 if m.group(1) != '':
#                     activity_list[i] = m.group(1)
#                 else:
#                     activity_list[i] = ''
#             except:
#                 activity_list[i] = ''
    
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
            if search_name.lower() in line.lower():
                package_list.append(line.replace('package', '').replace(':', ''))
                
        if len(package_list) == 0:
            CommonUtil.ExecLog(sModuleInfo, "Did not find installed package: %s" % search_name, 3)
            return '', ''
        elif len(package_list) > 1: CommonUtil.ExecLog(sModuleInfo, "Found more than one packages. Will use the first found. Please specify a more accurate package name. Found packages: %s" % package_list, 2)
        package_name = package_list[0] # Save first package found

        # Get activity name
        cmd='adb %s shell pm dump %s' % (serial,package_name)
        res = subprocess.check_output(cmd, shell = True)
        res = str(res).replace('\\r','') # Remove \r text if any
        res = str(res).replace('\\n','\n') # replace \n text with line feed
        res = str(res).replace('\r','') # Remove \r carriage return if any
        p = re.compile('MAIN:.*?\s+([\w\.]+)/([\w\.]+)', re.S)
        m = p.search(str(res))
        try:
            if m.group(1) != '' and m.group(2) != '':
                return m.group(1), m.group(2)
        except:
            pass # Error handling by calling function
        
        # !!! This does work, but if the above works for everything, then we can delete this, and the find_activity() function above
#         # Close program if running, so we get the first activity name
#         cmd = 'adb %s shell am force-stop %s' % (serial, package_name)
#         res = subprocess.check_output(cmd, shell = True)
#         time.sleep(1) # Wait for program to close
#         
#         # Start reading activity names
#         secs = 2 # Seconds to monitor foreground activity
#         thread.start_new_thread(find_activity, (secs,))
#                     
#         # Launch program using only package name
#         cmd = 'adb %s shell monkey -p %s -c android.intent.category.LAUNCHER 1' % (serial, package_name)
#         res = subprocess.check_output(cmd, shell = True)
#         
#         # Wait for program to launch
#         time.sleep(secs + 1) # Must be enough for the thread above to complete
# 
#         # Close program if running, so customer doesn't see it all the time
#         cmd = 'adb %s shell am force-stop %s' % (serial, package_name)
#         res = subprocess.check_output(cmd, shell = True)
#         
#         # Find activity name in the list
#         global activity_list
#         for package_activity in activity_list: # Test each package_activity read, in order
#             if package_name in package_activity: # If package name is in the string, this is the first instance of the program, and thus should contain the very first activity name
#                 return package_activity.split('/') # Split package and activity name and return
        
        return '', '' # Nothing found if we get here. Error handling handled by calling function

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
            # If asterisk, then assume one or more attached and reset them all
            if shared_var == '*':
                if dep == 'android': output = adbOptions.reset_all_android()
            
            # Anything else, try to figure out what it is
            else:
                if shared_var in appium_details: # If user provided device name, get the associated serial number
                    shared_var = appium_details[shared_var]['serial']
                elif adbOptions.is_android_connected(shared_var): # Check if the specified device is connected via serial
                    pass
                else: # No serial or name provided, and the string provided is not a connected device, just try to connect to the first device and reset it
                    shared_var = ''
    
                # Reset this one device
                if dep == 'android': output = adbOptions.reset_android(shared_var)

            shared_var = '' # Unset this, so we don't create a shared variable with it
            if output in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Failed to reboot device", 3)
                return 'failed'

        elif cmd == 'wake':
            if dep == 'android':
                if shared_var in appium_details: # If user provided device name, get the associated serial number
                    shared_var = appium_details[shared_var]['serial']
                elif adbOptions.is_android_connected(shared_var): # Check if the specified device is connected via serial
                    pass
                else: # No serial or name provided, and the string provided is not a connected device, just try to connect to the first device and reset it
                    shared_var = ''
                
                output = adbOptions.wake_android(shared_var)
                shared_var = ''
            
            if output in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Failed to wake device", 3)
                return 'failed'
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
            
            # Update shared variables, for anything that requires accessing that information
            Shared_Resources.Set_Shared_Variables('device_id', device_id, protected = True) # Save device id, because functions outside this file may require it
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export()) # Get all the shared variables, and pass them to CommonUtil

            CommonUtil.ExecLog(sModuleInfo, "Switched focus to: %s" % ID, 1)
            return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Serial number cannot be blank. Expected Value field of action row to be a serial number or UUID of the device connected via USB", 3)
            return 'failed'
        
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error when trying to read Field and Value for action")

def package_information(data_set):
    ''' Performs serveral actions on a package '''
    # Note: Appium doens't have an API that allows us to execute anything we want, so this is the solution
    # Format is package, element parameter, PACKAGE_NAME | COMMAND, action, SHARED_VAR_NAME
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    # Parse data set
    try:
        package_name = ''
        shared_var = ''
        cmd = ''
        value = ''
        for row in data_set:
            if row[1] == 'element parameter': 
                package_name = row[2].strip()
            elif row[1] == 'action':
                cmd = row[0].strip().lower().replace('  ', '')
                shared_var = row[2].strip() # Not used for all commands
        
        if package_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Full or partial package name missing. Expected Value field to contain it", 3)
            return 'failed'
        
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error when trying to read Value for action")
    
    # Get package name (if given partially)
    try:
        package_name, activity_name = get_program_names(package_name) # Get package name
        if package_name in ('', 'failed'):
            return 'failed' # get_program_names() logs the error
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error trying to get package name")
    
    # Perform action
    try:
        if cmd == 'package version':
            if shared_var == '': 
                CommonUtil.ExecLog(sModuleInfo, "Shared Variable name expected in Value field on action row", 3)
                return 'failed'
            value = adbOptions.get_package_version(package_name, device_serial)
            result = Shared_Resources.Set_Shared_Variables(shared_var, value)
        elif cmd == 'package installed':
            value = package_name # Store package name in shared variables, if user wants it
            if shared_var != '': result = Shared_Resources.Set_Shared_Variables(shared_var, value) # Optional
            result = 'passed' # Do nothing. If the package is not installed, get_program_names() above will fail and return
            
        # Check result
        if result in failed_tag_list or result == '':
            CommonUtil.ExecLog(sModuleInfo, "Error trying to execute mobile program", 3)
            return 'failed'
        
        CommonUtil.ExecLog(sModuleInfo, "%s was successful" % cmd, 1)
        if shared_var != '': CommonUtil.ExecLog(sModuleInfo, "Value '%s' saved to Shared Variable '%s'" % (value, shared_var), 1)
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error trying to execute mobile program")

def minimize_appilcation(data_set):
    ''' Hides the foreground application by pressing the home key '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    try:
        appium_driver.press_keycode(3)
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error trying to minimize application by sending home key press")

def maximize_appilcation(data_set):
    ''' Displays the original program that was launched by appium '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    try:
        appium_driver.launch_app()
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error trying to maximize application")


def serial_in_devices(serial,devices):
    ''' Displays the original program that was launched by appium '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    try:
        for device in devices:
            if devices[device]['id'] == serial or str(device).lower() == serial.lower():
                return True
        return False
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error trying to maximize application")
