# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

""" Name: Built In Functions - Appium
    Description: Contains all Sequential Actions related to automating Android and IOS using Appium
"""

#########################
#                       #
#        Modules        #
#                       #
#########################

from appium import webdriver
import traceback
import socket
import os, sys, datetime, time, inspect, subprocess, re, signal, _thread, requests, copy
from Framework.Utilities import CommonUtil
from Framework.Utilities.decorators import logger
from Framework.Built_In_Automation.Built_In_Utility.CrossPlatform import (
    BuiltInUtilityFunction as Utility_Functions,
)
from Framework.Built_In_Automation.Mobile.Android.adb_calls import adbOptions
from Framework.Built_In_Automation.Mobile.iOS import iosOptions
from appium.webdriver.common.touch_action import TouchAction
from Framework.Utilities import ConfigModule
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as Shared_Resources,
)
from Framework.Utilities.CommonUtil import (
    passed_tag_list,
    failed_tag_list,
    skipped_tag_list,
)
from Framework.Built_In_Automation.Shared_Resources import LocateElement
import psutil

temp_config = os.path.join(
    os.path.join(
        os.path.abspath(__file__).split("Framework")[0],
        os.path.join(
            "AutomationLog", ConfigModule.get_config_value("Advanced Options", "_file")
        ),
    )
)

MODULE_NAME = inspect.getmodulename(__file__)

PATH_ = lambda p: os.path.abspath(os.path.join(os.path.dirname(__file__), p))
PATH = "%s" % PATH_
#########################
#                       #
#   Global Variables    #
#                       #
#########################
# Recall appium driver, if not already set - needed between calls in a Zeuz test case
appium_port = 4721  # Default appium port - changes if we have multiple devices
wdaLocalPort = 8100
appium_details = (
    {}
)  # Used to store device serial number, appium driver, if multiple devices are used
appium_driver = None  # Holds the currently used appium instance
device_serial = (
    ""  # Holds the identifier for the currently used device (if any are specified)
)
device_id = ""  # Holds the name of the device the user has specified, if any. Relationship is set elsewhere

from Framework.Utilities import All_Device_Info


# Recall dependency, if not already set
dependency = None
if Shared_Resources.Test_Shared_Variables(
    "dependency"
):  # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables(
        "dependency"
    )  # Retreive appium driver
else:
    pass  # May be phasing out dependency for mobile
    # raise ValueError("No dependency set - Cannot run")

# Recall file attachments
file_attachment = {}
if Shared_Resources.Test_Shared_Variables(
    "file_attachment"
):  # Check if file_attachement is set
    file_attachment = Shared_Resources.Get_Shared_Variables(
        "file_attachment"
    )  # Retreive file attachments

# Recall appium details
if Shared_Resources.Test_Shared_Variables(
    "appium_details"
):  # Check if driver is already set in shared variables
    appium_details = Shared_Resources.Get_Shared_Variables(
        "appium_details"
    )  # Retreive appium driver
    # Populate the global variables with one of the device information. If more than one device is used, then it'll be the last. The user is responsible for calling either launch_application() or switch_device() to focus on the one they want
    for name in appium_details:
        appium_driver = appium_details[name]["driver"]
        appium_server = appium_details[name]["server"]
        device_serial = appium_details[name]["serial"]
        device_id = name


# Recall device_info, if not already set
device_info = {}
if Shared_Resources.Test_Shared_Variables(
    "device_info"
):  # Check if device_info is already set in shared variables
    device_info = Shared_Resources.Get_Shared_Variables(
        "device_info"
    )  # Retreive device_info


@logger
def find_appium():
    """ Do our very best to find the appium executable """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Expected locations
    appium_list = [
        "/usr/bin/appium",
        os.path.join(str(os.getenv("HOME")), ".linuxbrew/bin/appium"),
        os.path.join(str(os.getenv("ProgramFiles")), "APPIUM", "Appium.exe"),
        os.path.join(
            str(os.getenv("USERPROFILE")), "AppData", "Roaming", "npm", "appium.cmd"
        ),
    ]  # getenv() must be wrapped in str(), so it doesn't fail on other platforms

    # Try to find the appium executable
    global appium_binary
    appium_binary = ""
    for binary in appium_list:
        if os.path.exists(binary):
            appium_binary = binary
            break

    # Try to find the appium executable in the PATH variable
    if appium_binary == "":  # Didn't find where appium was installed
        CommonUtil.ExecLog(sModuleInfo, "Searching PATH for appium", 0)
        for exe in ("appium", "appium.exe", "appium.bat", "appium.cmd"):
            result = find_exe_in_path(exe)  # Get path and search for executable with in
            if result != "failed":
                appium_binary = result
                break

    # Verify if we have the binary location
    if appium_binary == "":  # Didn't find where appium was installed
        CommonUtil.ExecLog(
            sModuleInfo, "Appium not found. Trying to locate via which", 0
        )
        try:
            appium_binary = subprocess.check_output(
                "which appium", encoding="utf-8", shell=True
            ).strip()
        except:
            pass

        if appium_binary == "":  # Didn't find where appium was installed
            appium_binary = "appium"  # Default filename of appium, assume in the PATH
            CommonUtil.ExecLog(
                sModuleInfo, "Appium still not found. Assuming it's in the PATH.", 2
            )
        else:
            CommonUtil.ExecLog(sModuleInfo, "Found appium: %s" % appium_binary, 1)
    else:  # Found appium's path
        CommonUtil.ExecLog(sModuleInfo, "Found appium: %s" % appium_binary, 1)


@logger
def find_exe_in_path(exe):
    """ Search the path for an executable """

    try:
        path = os.getenv("PATH")  # Linux/Windows path

        if ";" in path:  # Windows delimiter
            dirs = path.split(";")
        elif ":" in path:  # Linux delimiter
            dirs = path.split(":")
        else:
            return "failed"

        for directory in dirs:  # Try each directory
            filename = os.path.join(directory, exe)  # Create full path
            if os.path.isfile(filename):  # If it exists, return it and stop
                return filename

        # No matches
        return "failed"

    except Exception:
        errMsg = "Error searching PATH"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


# Try to find appium
appium_binary = ""
find_appium()


@logger
def get_driver():
    """ For custom functions external to this script that need access to the driver """
    # Caveat: create_appium_driver() must be executed before this variable is populated
    return appium_driver


@logger
def find_correct_device_on_first_run(serial_or_name, device_info):
    """ Considers information from the data set, deployed devices, and connected devices to determine which device to use """
    # Only used when launching an application, which creates the appium instance.

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global device_id, device_serial, appium_details
    CommonUtil.ExecLog(
        sModuleInfo, "List of devices provided by server: %s" % str(device_info), 1
    )

    try:
        # Get list of connected devices
        devices = {}  # Temporarily store connected device serial numberspick
        all_device_info = All_Device_Info.get_all_connected_device_info()

        # Ensure we have at least one device connected
        if len(all_device_info) == 0:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Could not detect any connected devices. Ensure at least one is attached via USB, and that it is authorized - Trusted / USB Debugging enabled",
                3,
            )
            return "failed"

        imei = ""
        device_name = ""
        product_version = ""
        serial = ""
        did = ""
        device_type = ""

        # Check if serial provided is a real serial number, name or rubish that should be ignored
        serial_check = False
        for device in all_device_info:  # For each device serial number
            if serial_or_name.lower() == device.lower():
                serial = all_device_info[device]["id"]  # Save serial number
                device_type = all_device_info[device][
                    "type"
                ].lower()  # Save device type android/ios
                imei = all_device_info[device]["imei"]
                device_name = all_device_info[device]["model"]
                product_version = all_device_info[device]["osver"]
                did = device
                serial_check = True  # Flag as found
                CommonUtil.ExecLog(
                    sModuleInfo, "Found serial number in data set: %s" % serial, 0
                )
                break

        # Check if user provided name - must be accompanied by device_info, sent by server
        if serial_check == False:
            for dname in device_info:
                if serial_or_name.lower() == dname.lower():
                    did = dname  # Save device name
                    serial = device_info[did]["id"]  # Save serial number
                    device_type = device_info[did][
                        "type"
                    ].lower()  # Save device type android/ios
                    imei = device_info[did]["imei"]
                    device_name = all_device_info[device]["model"]
                    product_version = all_device_info[device]["osver"]
                    serial_check = True
                    CommonUtil.ExecLog(
                        sModuleInfo, "Found device name in data set: %s" % did, 0
                    )
                    break

        ### If we were given either a serial/uuid or name in the data set, we should now have what we need to run ###

        # Not found, so now we have to look at the device_info dictionary from the server to determine the device to use
        if serial_check == False:
            # At least one device sent by server
            if len(device_info) > 0:
                for dname in device_info:
                    did = dname
                    serial = device_info[did]["id"]
                    imei = device_info[did]["imei"]
                    device_type = device_info[did]["type"].lower()
                    device_name = all_device_info[device]["model"]
                    product_version = all_device_info[device]["osver"]
                    CommonUtil.ExecLog(
                        sModuleInfo, "Found a device selected at Deploy: %s" % did, 0
                    )
                    break

            # Lastly, if nothing above is set, the user did not specify anything, and we have no information from the server. Pick a connected device, and fail if there are none
            else:  # No devices sent, none specified
                for device in devices:
                    did = "default"
                    serial = device  # Get Serial
                    device_type = devices[device]  # Get type
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "No device information found. Picked one that is connected: %s"
                        % serial,
                        0,
                    )
                    break  # Only take the first device'''

        # At the end, we should have at least one device
        if serial != "" and device_type != "" and did != "":
            # Verify this device was not already selected and run previously
            if did in appium_details:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "The selected device was previously run. You cannot run it more than once in a session. Either your step data is calling the 'launch' action multiple times without specifying specific devices, or you did not call the 'teardown' action in a previous run.",
                    2,
                )
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "If test case fails, please quit node, and make sure you have added tear down in your test.",
                    2,
                )
                return "passed"

            # Verify this device is actually connected
            if not serial_in_devices(serial, all_device_info):
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Although we have a selected device, it did not appear in the list of connected devices. Please ensure the device information aligns with what is connected: %s (%s)"
                    % (did, serial),
                    3,
                )
                return "failed"

            # Global variables for quick access to currently selected device
            device_serial = serial
            device_id = did

            # Global variable that holds data required by appium
            appium_details[device_id] = {}
            if "driver" not in appium_details[device_id]:
                appium_details[device_id][
                    "driver"
                ] = None  # Initialize appium driver object
            appium_details[device_id]["serial"] = serial
            appium_details[device_id]["type"] = device_type
            appium_details[device_id]["imei"] = imei
            appium_details[device_id]["platform_version"] = product_version
            appium_details[device_id]["device_name"] = device_name

            # Store in shared variable, so it doens't get forgotten
            Shared_Resources.Set_Shared_Variables(
                "device_serial", device_serial, protected=True
            )
            Shared_Resources.Set_Shared_Variables(
                "device_id", device_id, protected=True
            )  # Save device id, because functions outside this file may require it

            CommonUtil.ExecLog(
                sModuleInfo,
                "Matched provided device identifier as %s (%s)" % (device_id, serial),
                1,
            )
            return "passed"
        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Although we found connected devices, provided information could not get all required information. Found devices: %s | Deployed device list: %s"
                % (str(devices), str(device_info)),
                3,
            )
            return "failed"

    except:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error trying to read device information"
        )


@logger
def unlock_android_device(data_set):
    """ Unlocks an androi device with adb commands"""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    global device_serial, appium_details, appium_driver, device_id, device_info
    # Recall appium details
    if Shared_Resources.Test_Shared_Variables(
        "device_info"
    ):  # Check if device_info is already set in shared variables
        device_info = Shared_Resources.Get_Shared_Variables(
            "device_info"
        )  # Retreive device_info

    # Parse data set
    try:
        serial = (
            ""  # Serial number (may also be random string like "launch", "na", etc)
        )
        password = ""

        for row in data_set:  # Find required data
            if str(row[1]).strip().lower() == "action":
                password = str(row[2]).lower().strip()

        # Set the global variable for the preferred connected device
        if find_correct_device_on_first_run(serial, device_info) in failed_tag_list:
            return "failed"

        if appium_details[device_id]["type"] == "android":
            Shared_Resources.Set_Shared_Variables("device_password", password)
            result = adbOptions.unlock_android(device_serial)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Couldn't unlock the android device", 3)
                return "failed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo, "Unlocked android device successfully", 1
                )
                return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "The device type is not android", 3)
            return "failed"

        CommonUtil.ExecLog(sModuleInfo, "Unlocked android device successfully", 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(),
            None,
            " Either device is not connected, or authorized, or a capability is incorrect.",
        )


@logger
def unlock_android_app(data_set):
    """ Unlocks an androi device with adb commands"""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    global device_serial, appium_details, appium_driver, device_id, device_info
    # Recall appium details
    if Shared_Resources.Test_Shared_Variables(
        "device_info"
    ):  # Check if device_info is already set in shared variables
        device_info = Shared_Resources.Get_Shared_Variables(
            "device_info"
        )  # Retreive device_info

    # Parse data set
    try:
        serial = (
            ""  # Serial number (may also be random string like "launch", "na", etc)
        )
        password = ""

        for row in data_set:  # Find required data
            if str(row[1]).strip().lower() == "action":
                password = str(row[2]).lower().strip()

        # Set the global variable for the preferred connected device
        if find_correct_device_on_first_run(serial, device_info) in failed_tag_list:
            return "failed"

        if appium_details[device_id]["type"] == "android":
            Shared_Resources.Set_Shared_Variables("device_password", password)
            result = adbOptions.unlock_android_app(device_serial)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Couldn't unlock your app", 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Unlocked your app successfully", 1)
                return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "The device type is not android", 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(),
            None,
            " Either device is not connected, or authorized, or a capability is incorrect.",
        )


@logger
def launch_application(data_set):
    """ Launch the application the appium instance was created with, and create the instance if necessary """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    global device_serial, appium_details, appium_driver, device_id, device_info
    # Recall appium details
    if Shared_Resources.Test_Shared_Variables(
        "device_info"
    ):  # Check if device_info is already set in shared variables
        device_info = Shared_Resources.Get_Shared_Variables(
            "device_info"
        )  # Retreive device_info

    # Parse data set
    try:
        browserstack_run = False
        for did in device_info:
            if "browserstack" in did:
                browserstack_run = True
                break
        if browserstack_run:
            desiredcaps = device_info["browserstack device 1"]

        else:
            package_name = ""  # Name of application package
            activity_name = ""  # Name of application activity
            serial = (
                ""  # Serial number (may also be random string like "launch", "na", etc)
            )
            platform_version = ""
            device_name = ""
            ios = ""
            no_reset = False
            work_profile = False

            for row in data_set:  # Find required data
                if (
                    str(row[0]).strip().lower() in ("android package", "package")
                    and row[1] == "element parameter"
                ):
                    package_name = row[2]
                elif (
                    str(row[0]).strip().lower()
                    in ("app activity", "activity", "android activity")
                    and row[1] == "element parameter"
                ):
                    activity_name = row[2]
                elif (
                    str(row[0]).strip().lower() in ("ios", "ios simulator")
                    and row[1] == "element parameter"
                ):
                    ios = row[2]
                elif str(row[0]).strip().lower() == "work profile" and str(
                    row[2]
                ).strip().lower() in ("yes", "true"):
                    work_profile = True
                elif (
                    str(row[0]).strip().lower() in ("no reset", "no_reset", "noreset")
                    and row[1] == "element parameter"
                ):
                    if str(row[2]).strip().lower() in ("yes", "true"):
                        no_reset = True
                    else:
                        no_reset = False
                elif str(row[1]).strip().lower() == "action":
                    serial = row[2].lower().strip()

            # desired capabilities for specific platforms
            desiredcaps = dict()
            # Set the global variable for the preferred connected device
            if find_correct_device_on_first_run(serial, device_info) in failed_tag_list:
                return "failed"

            device_type = appium_details[device_id]["type"].lower().strip()

            for left, mid, right in data_set:
                left, mid = left.strip().lower(), mid.strip().lower()

                if "parameter" in mid and "=" in right:
                    # key, value
                    k, v = map(lambda x: x.strip(), right.split("="))

                    if left in (device_type, "multi"):
                        desiredcaps[k] = v

            # Send wake up command to avoid issues with devices ignoring appium when they are in lower power mode (android 6.0+), and unlock if passworded
            if appium_details[device_id]["type"] == "android":
                result = adbOptions.wake_android(device_serial)
                if result in failed_tag_list:
                    return "failed"

            # If android, then we will try to find the activity name, IOS doesn't need this
            if activity_name == "":
                if appium_details[device_id]["type"] == "android":
                    package_name, activity_name = get_program_names(
                        package_name
                    )  # Android only to match a partial package name if provided by the user
                    Shared_Resources.Set_Shared_Variables("package_name", str(package_name))

            # Verify data
            if (
                appium_details[device_id]["type"] == "android"
                and package_name == ""
                or package_name in failed_tag_list
            ):
                CommonUtil.ExecLog(sModuleInfo, "Could not find package name", 3)
                return "failed"
            elif appium_details[device_id]["type"] == "android" and activity_name == "":
                CommonUtil.ExecLog(sModuleInfo, "Could not find activity name", 3)
                return "failed"

    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Launch application
    try:
        launch_app = True
        if browserstack_run:
            result, launch_app = start_appium_driver(
                desiredcaps=desiredcaps,
                browserstack_run=browserstack_run,
            )
        else:
            if "platform_version" in appium_details[device_id]:
                platform_version = appium_details[device_id]["platform_version"]
            if "device_name" in appium_details[device_id]:
                device_name = appium_details[device_id]["device_name"]
            if (
                appium_details[device_id]["driver"] == None
            ):  # Only create a new appium instance if we haven't already (may be done by install_and_start_driver())
                result, launch_app = start_appium_driver(
                    package_name,
                    activity_name,
                    platform_version=platform_version,
                    device_name=device_name,
                    ios=ios,
                    no_reset=no_reset,
                    work_profile=work_profile,
                    desiredcaps=desiredcaps,
                )
                if result == "failed":
                    return "failed"

        if launch_app:  # if ios simulator then no need to launch app again
            appium_driver.launch_app()  # Launch program configured in the Appium capabilities
        # CommonUtil.TakeScreenShot(
        #     sModuleInfo
        # )  # Capture screenshot, if settings allow for it
        CommonUtil.ExecLog(sModuleInfo, "Launched the application successfully.", 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(),
            None,
            "Could not create Appium Driver, Either device is not connected, or authorized, or a capability is incorrect.",
        )


@logger
def set_pdeathsig(sig=signal.SIGTERM):
    """ Linux only - Capture any children that are spawned by programs executed by Popen() """

    import ctypes

    libc = ctypes.CDLL("libc.so.6")

    @logger
    def callable():
        return libc.prctl(1, sig)

    return callable


@logger
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


@logger
def start_appium_server():
    """ Starts the external Appium server """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    global appium_port, appium_details, device_serial, appium_binary, device_id, wdaLocalPort

    try:
        # Shutdown appium server if it's already running
        # if appium_details[device_id][
        #     "driver"
        # ]:  # Check if the appium server was previously run (likely not)
        #     appium_server = appium_details[device_id][
        #         "driver"
        #     ]  # Get the subprocess object
        #     try:
        #         appium_server.kill()  # Kill the server
        #     except:
        #         pass

        # Execute appium server
        # appium_port += 2  # Increment the port number (by 2 because adb seems to grab the next port), for the next time we run, so we can have multiple instances
        # wdaLocalPort += 2

        appium_port = 4723
        wdaLocalPort = 8100
        tries = 0
        while is_port_in_use(appium_port) and tries < 20:
            appium_port += 2
            wdaLocalPort += 2

        if tries >= 20:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Failed to find a free port for running appium after 20 tries.",
                1,
            )
            return "failed"

        try:
            appium_server = None
            if (
                sys.platform == "win32"
            ):  # We need to open appium in it's own command dos box on Windows
                cmd = (
                    'start "Appium Server" /wait /min cmd /c %s --allow-insecure chromedriver_autodownload -p %d'
                    % (appium_binary, appium_port)
                )  # Use start to execute and minimize, then cmd /c will remove the dos box when appium is killed
                appium_server = subprocess.Popen(
                    cmd, shell=True
                )  # Needs to run in a shell due to the execution command
            elif sys.platform == "darwin":
                appium_server = subprocess.Popen(
                    "%s --allow-insecure chromedriver_autodownload -p %s"
                    % (appium_binary, str(appium_port)),
                    shell=True,
                )
            elif sys.platform == "linux" or sys.platform == "linux2":
                appium_server = subprocess.Popen(
                    "%s --allow-insecure chromedriver_autodownload -p %s"
                    % (appium_binary, str(appium_port)),
                    shell=True,
                )
            else:
                try:

                    appium_binary_path = os.path.normpath(appium_binary)
                    appium_binary_path = os.path.abspath(
                        os.path.join(appium_binary_path, os.pardir)
                    )
                    env = {"PATH": str(appium_binary_path)}
                    appium_server = subprocess.Popen(
                        subprocess.Popen(
                            "%s --allow-insecure chromedriver_autodownload -p %s"
                            % (appium_binary, str(appium_port)),
                            shell=True,
                        ),
                        env=env,
                    )
                except:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Couldn't launch appium server, please do it manually by typing 'appium &' in the terminal",
                        2,
                    )
            appium_details[device_id][
                "server"
            ] = appium_server  # Save the server object for teardown
        except Exception as returncode:  # Couldn't run server
            return CommonUtil.Exception_Handler(
                sys.exc_info(),
                None,
                "Couldn't start Appium server. May not be installed, or not in your PATH: %s"
                % returncode,
            )

        # Wait for server to startup and return
        CommonUtil.ExecLog(
            sModuleInfo,
            "Waiting for server to start on port %d: %s" % (appium_port, appium_binary),
            0,
        )
        maxtime = time.time() + 10  # Maximum time to wait for appium server
        while True:  # Dynamically wait for appium to start by polling it
            if time.time() > maxtime:
                break  # Give up if max time was hit
            try:  # If this works, then stop waiting for appium
                r = requests.get(
                    "http://localhost:%d/wd/hub/sessions" % appium_port
                )  # Poll appium server
                if r.status_code:
                    break
            except:
                pass  # Keep waiting for appium to start

        if appium_server:
            CommonUtil.ExecLog(sModuleInfo, "Server started", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Server failed to start", 3)
            return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error starting Appium server"
        )


@logger
def start_appium_driver(
    package_name="",
    activity_name="",
    filename="",
    platform_version="",
    device_name="",
    ios="",
    no_reset=False,
    work_profile=False,
    desiredcaps=None,
    browserstack_run=False,
):
    """ Creates appium instance using discovered and provided capabilities """
    # Does not execute application

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        global appium_driver, appium_details, device_id, wdaLocalPort
        launch_app = True
        if browserstack_run:
            appium_driver = webdriver.Remote(
                command_executor="http://hub-cloud.browserstack.com/wd/hub",
                desired_capabilities=desiredcaps
            )
            appium_details["browserstack device 1"] = {"driver": appium_driver}
            Shared_Resources.Set_Shared_Variables("appium_details", appium_details)
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())  # Get all the shared variables, and pass them to CommonUtil
            CommonUtil.ExecLog(sModuleInfo, "Appium driver created successfully.", 1)
            return "passed", launch_app

        if appium_details[device_id]["driver"] == None:
            # Start Appium server
            if start_appium_server() in failed_tag_list:
                return "failed", launch_app

            # Create Appium driver
            # Setup capabilities
            desired_caps = {}

            # Include the user provided desired capabilities
            desired_caps.update(desiredcaps)

            if str(appium_details[device_id]["type"]).lower() == "android":

                desired_caps["platformName"] = appium_details[device_id][
                    "type"
                ]  # Set platform name
                desired_caps["autoLaunch"] = "false"  # Do not launch application
                desired_caps[
                    "fullReset"
                ] = "false"  # Do not clear application cache when complete
                desired_caps[
                    "noReset"
                ] = "true"  # Do not clear application cache when complete
                desired_caps[
                    "newCommandTimeout"
                ] = 6000  # Command timeout before appium destroys instance
                desired_caps["automationName"] = "UiAutomator2"
                if adbOptions.is_android_connected(device_serial) == False:
                    CommonUtil.ExecLog(
                        sModuleInfo, "Could not detect any connected Android devices", 3
                    )
                    return "failed", launch_app

                if work_profile:
                    work_profile_from_adb = adbOptions.get_work_profile()
                    if work_profile_from_adb in failed_tag_list:
                        CommonUtil.ExecLog(
                            sModuleInfo, "Couldn't get the work profile", 3
                        )
                        return "failed"
                    desired_caps[
                        "userProfile"
                    ] = work_profile_from_adb  # Command timeout before appium destroys instance

                CommonUtil.ExecLog(sModuleInfo, "Setting up with Android", 1)
                desired_caps["platformVersion"] = adbOptions.get_android_version(
                    appium_details[device_id]["serial"]
                ).strip()
                desired_caps["deviceName"] = adbOptions.get_device_model(
                    appium_details[device_id]["serial"]
                ).strip()
                if package_name:
                    desired_caps["appPackage"] = package_name.strip()
                if activity_name:
                    desired_caps["appActivity"] = activity_name.strip()
                if (
                    filename and package_name == ""
                ):  # User must specify package or file, not both. Specifying filename instructs Appium to install
                    desired_caps["app"] = PATH(filename).strip()

            elif str(appium_details[device_id]["type"]).lower() == "ios":
                CommonUtil.ExecLog(sModuleInfo, "Setting up with IOS", 1)
                if appium_details[device_id]["imei"] == "Simulated":  # ios simulator
                    launch_app = False  # ios simulator so need to launch app again

                    if "browserName" in desired_caps:
                        # We're trying to launch the Safari browser
                        # NOTE: Other browsers are not supported by appium on iOS
                        if "safariAllowPopups" not in desired_caps:
                            # Allow popups by default, unless specified by the user
                            desired_caps["safariAllowPopups"] = True
                    else:
                        # We're trying to launch an application using .app file
                        if Shared_Resources.Test_Shared_Variables(
                            "ios_simulator_folder_path"
                        ):  # if simulator path already exists
                            app = Shared_Resources.Get_Shared_Variables(
                                "ios_simulator_folder_path"
                            )
                            app = os.path.normpath(app)
                        else:
                            app = os.path.normpath(os.getcwd() + os.sep + os.pardir)
                            app = os.path.join(app, "iosSimulator")
                            # saving simulator path for future use
                            Shared_Resources.Set_Shared_Variables(
                                "ios_simulator_folder_path", str(app)
                            )

                        app = os.path.join(app, ios)
                        encoding = "utf-8"
                        bundle_id = str(
                            subprocess.check_output(
                                ["osascript", "-e", 'id of app "%s"' % str(app)]
                            ),
                            encoding=encoding,
                        ).strip()

                        desired_caps[
                            "app"
                        ] = app  # Use set_value() for writing to element
                        desired_caps["bundleId"] = bundle_id.replace("\\n", "")

                    desired_caps[
                        "platformName"
                    ] = "iOS"  # Read version #!!! Temporarily hard coded
                    desired_caps["platformVersion"] = platform_version
                    desired_caps["deviceName"] = device_name
                    desired_caps["automationName"] = "XCUITest"
                    desired_caps["wdaLocalPort"] = wdaLocalPort
                    desired_caps["udid"] = appium_details[device_id]["serial"]
                    desired_caps["newCommandTimeout"] = 6000
                    if no_reset:
                        desired_caps[
                            "noReset"
                        ] = "true"  # Do not clear application cache when complete
                else:  # for real ios device, not developed yet
                    desired_caps[
                        "sendKeyStrategy"
                    ] = "setValue"  # Use set_value() for writing to element
                    desired_caps[
                        "platformVersion"
                    ] = "13.5"  # Read version #!!! Temporarily hard coded
                    desired_caps[
                        "deviceName"
                    ] = "iPhone"  # Read model (only needs to be unique if using more than one)
                    desired_caps["bundleId"] = ios
                    desired_caps["udid"] = appium_details[device_id][
                        "serial"
                    ]  # Device unique identifier - use auto if using only one phone
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Invalid device type: %s" % str(appium_details[device_id]["type"]),
                    3,
                )
                return "failed", launch_app
            CommonUtil.ExecLog(sModuleInfo, "Capabilities: %s" % str(desired_caps), 1)

            # Create Appium instance with capabilities
            try:
                count = 1
                while count <= 5:
                    try:
                        appium_driver = webdriver.Remote(
                            "http://localhost:%d/wd/hub" % appium_port, desired_caps
                        )  # Create instance
                        if appium_driver:
                            break
                        count += 1
                        time.sleep(10)
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Failed to create appium driver, trying again",
                            2,
                        )
                    except:
                        count += 1
                        time.sleep(10)
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Failed to create appium driver, trying again",
                            2,
                        )

                if appium_driver:  # Make sure we get the instance
                    appium_details[device_id]["driver"] = appium_driver
                    Shared_Resources.Set_Shared_Variables(
                        "appium_details", appium_details
                    )
                    CommonUtil.set_screenshot_vars(
                        Shared_Resources.Shared_Variable_Export()
                    )  # Get all the shared variables, and pass them to CommonUtil
                    CommonUtil.ExecLog(
                        sModuleInfo, "Appium driver created successfully.", 1
                    )
                    return "passed", launch_app
                else:  # Error during setup, reset
                    appium_driver = None
                    CommonUtil.ExecLog(sModuleInfo, "Error during Appium setup", 3)
                    return "failed", launch_app
            except Exception as e:
                print(e)
                return (
                    CommonUtil.Exception_Handler(
                        sys.exc_info(),
                        None,
                        "Error connecting to Appium server to create driver instance",
                    ),
                    launch_app,
                )

        else:  # Driver is already setup, don't do anything
            CommonUtil.ExecLog(
                sModuleInfo, "Driver already configured, not re-doing", 0
            )
            return "passed", launch_app
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info()), launch_app


@logger
def kill_appium_on_windows(appium_server):
    """ Killing Appium server on windows involves killing off it's children """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        import psutil, signal

        for child in psutil.Process(appium_server.pid).children(
            recursive=True
        ):  # For eah child in process
            try:
                cpid = int(
                    str(child.as_dict(attrs=["pid"])["pid"]).replace("'", "")
                )  # Get child PID
                CommonUtil.ExecLog(sModuleInfo, "Killing Appium child: %d" % cpid, 0)
                psutil.Process(cpid).send_signal(signal.SIGTERM)  # Send kill to it
                # print h.terminate()
            except:
                pass
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error killing Appium and it's children"
        )


@logger
def kill_node():
    """ Kill appium node"""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    CommonUtil.ExecLog(sModuleInfo, "Killing Node Forcefully", 0)
    try:

        for proc in psutil.process_iter():
            # check whether the process name matches
            try:
                if "name='node.exe'" in str(proc.name) or "name='node'" in str(
                    proc.name
                ):
                    proc.kill()
            except:
                pass
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Unable to kill Node.js"
        )


@logger
def teardown_appium(data_set):
    """ Teardown of appium instance """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    global appium_details, appium_server, device_id, device_serial, device_info, appium_port, wdaLocalPort

    try:
        for name in appium_details:  # For each connected device
            try:
                CommonUtil.ExecLog(sModuleInfo, "Teardown for: %s" % name, 0)
                try:
                    appium_details[name]["driver"].quit()  # Destroy driver
                except:
                    pass
                # if (
                #     sys.platform == "win32"
                # ):  # Special kill for appium children on Windows
                #     kill_appium_on_windows(appium_details[name]["server"])
                try:
                    appium_details[name]["server"].kill()  # Terminate server
                except:
                    pass

                # kill_node()
            except:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Error destroying Appium instance/server for %s - may already be killed"
                    % name,
                    2,
                )

        # Kill adb server to ensure it doesn't hang
        try:

            for proc in psutil.process_iter():
                # check whether the process name matches
                try:
                    if "name='adb" in str(proc.name):
                        adbOptions.kill_adb_server()
                except:
                    pass
        except:
            pass
        # Delete variables
        appium_details = {}
        device_info = {}
        # appium_port = 4721
        # wdaLocalPort = 8100
        appium_server, device_id, device_serial = "", "", ""
        Shared_Resources.Set_Shared_Variables("appium_details", "")
        Shared_Resources.Set_Shared_Variables("device_info", "")
        Shared_Resources.Set_Shared_Variables("device_id", "")
    except:
        CommonUtil.ExecLog(
            sModuleInfo,
            "Error destroying Appium instance/server - may already be killed",
            2,
        )

    return "passed"


@logger
def close_application(data_set):
    """ Exit the application """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to close the app", 0)
        appium_driver.close_app()
        CommonUtil.ExecLog(sModuleInfo, "Closed the app successfully", 1)
        return "passed"
    except Exception:
        errMsg = "Unable to close the application."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def reset_application(data_set):
    """ Resets / clears the application cache """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to reset the app", 0)
        appium_driver.reset()  # Reset / clear application cache
        CommonUtil.ExecLog(sModuleInfo, "Reset the app successfully", 1)
        return "passed"
    except Exception:
        errMsg = "Unable to Reset the application."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def install_application(data_set):
    """ Install application to device """
    # adb does the work. Does not require appium instance. User needs to call launch action to create instance
    # Two formats allowed: Filename on action row, or filename on element parameter row, and optional serial number on action row

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return

    # Parse data set
    try:
        file_name = ""
        serial = ""
        for row in data_set:  # Find required data
            if (
                row[1] == "action"
            ):  # If using format of package on action line, and no serial number
                serial = row[
                    2
                ].strip()  # May be serial or filename, we'll figure out later
            elif (
                row[1] == "element parameter"
            ):  # If using the format of filename on it's own row, and possibly a serial number on the action line
                file_name = row[2].strip()  # Save filename
        if (
            file_name == ""
        ):  # Fix previous filename from action row if no element parameter specified
            file_name = serial  # There was no element parameter row, so take the action row value for the filename
            serial = ""

        # Try to find the image file
        if file_name not in file_attachment and os.path.exists(file_name) == False:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Could not find file attachment called %s, and could not find it locally"
                % file_name,
                3,
            )
            return "failed"
        if file_name in file_attachment:
            file_name = file_attachment[
                file_name
            ]  # In file is an attachment, get the full path
        if file_name == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "File not specified or there was a problem reading the file attachments",
                3,
            )
            return "failed"

        # Try to determine device serial
        if serial != "":
            find_correct_device_on_first_run(serial, device_info)
            serial = device_serial  # Should be populated with an available device serial or nothing

    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    try:
        result = adbOptions.install_app(file_name, serial)
        if result in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo, "Could not install application (%s)" % file_name, 3
            )
            return "failed"
        CommonUtil.ExecLog(
            sModuleInfo, "Installed %s to device %s" % (file_name, serial), 1
        )
        return "passed"

    except Exception:
        errMsg = "Error installing application"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def uninstall_application(data_set):
    """ Uninstalls/removes application from device """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    # Parse data set
    try:
        package = ""
        serial = ""
        for row in data_set:  # Find required data
            if (
                row[1] == "action"
            ):  # If using format of package on action line, and no serial number
                serial = row[
                    2
                ].strip()  # May be serial or filename, we'll figure out later
            elif (
                row[1] == "element parameter"
            ):  # If using the format of filename on it's own row, and possibly a serial number on the action line
                package = row[2].strip()  # Save filename
        if (
            package == ""
        ):  # Fix previous filename from action row if no element parameter specified
            package = serial  # There was no element parameter row, so take the action row value for the filename
            serial = ""

        # Try to find package name
        package, activity_name = get_program_names(package)  # Get package name

        # Try to determine device serial
        if serial != "":
            find_correct_device_on_first_run(serial, device_info)
            serial = device_serial  # Should be populated with an available device serial or nothing

    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    try:
        result = adbOptions.uninstall_app(package, serial)
        if result in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo, "Could not uninstall application (%s)" % package, 3
            )
            return "failed"
        CommonUtil.ExecLog(
            sModuleInfo, "Uninstalled %s from device %s" % (package, serial), 1
        )
        return "passed"

    except Exception:
        errMsg = "Error uninstalling application"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Swipe(x_start, y_start, x_end, y_end, duration=1000, adb=False):
    """ Perform single swipe gesture with provided start and end positions """
    # duration in mS - how long the gesture should take

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting to swipe the screen...", 0)
        if adb:
            CommonUtil.ExecLog(sModuleInfo, "Using ADB swipe method", 0)
            adbOptions.swipe_android(
                x_start, y_start, x_end, y_end, duration, device_serial
            )  # Use adb if specifically asked for it
        else:
            appium_driver.swipe(
                x_start, y_start, x_end, y_end, duration
            )  # Use Appium to swipe by default

        # CommonUtil.TakeScreenShot(
        #     sModuleInfo
        # )  # Capture screenshot, if settings allow for it
        return "passed"
    except Exception:
        errMsg = "Unable to swipe."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def swipe_in_direction(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    try:
        id = ""
        class_name = ""
        index = ""
        horizontal_scrolling = False
        direction = "scrollForward()"
        try:
            for each in data_set:
                if str(each[0]).strip().lower() == "resource-id":
                    id = str(each[2]).strip()
                elif str(each[0]).strip().lower() == "class":
                    class_name = str(each[2]).strip()
                elif str(each[0]).strip().lower() == "index":
                    index = str(each[2]).strip()
                elif str(each[0]).strip().lower() == "direction":
                    if str(each[0]).strip().lower() in ("down", "right"):
                        direction = "scrollForward()"
                    else:
                        direction = "scrollBackward()"
                elif str(each[0]).strip().lower() == "horizontal scrolling" and str(
                    each[2]
                ).strip().lower() in ("yes", "true"):
                    horizontal_scrolling = True
        except:
            errMsg = "Error while looking for action line"
            return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

        parent_string = "new UiScrollable(new UiSelector()"
        horizontal_string = ""
        child_string = ""
        index_string = ")"

        if id != "":
            child_string = 'resourceId("%s")' % id
        elif class_name != "":
            child_string = 'className("%s")' % class_name

        if horizontal_scrolling:
            horizontal_string = "setAsHorizontalList()."

        if index != "":
            index_string = ".instance(%s))" % index

        final_search_string = "%s.%s%s.%s%s" % (
            parent_string,
            child_string,
            index_string,
            horizontal_string,
            direction,
        )
        try:
            appium_driver.find_element_by_android_uiautomator(final_search_string)
        except:
            pass
        CommonUtil.ExecLog(sModuleInfo, "Swiped to the element successfully", 1)

        return "passed"
    except:
        errMsg = "Unable to swipe."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def swipe_handler_wrapper(data_set):
    try:
        if appium_details[device_id]["type"] == "ios":  # for ios
            return swipe_handler_ios(data_set)
        else:  # for android
            return swipe_handler_android(data_set)
    except:
        errMsg = "Unable to swipe."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def swipe_handler_ios(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    try:
        direction = ""
        predicateString = ""
        swipe_direction_and_predicate = ""
        element_given = False
        try:
            for each in data_set:
                if "element parameter" in each[1]:
                    element_given = True
                elif "direction" in each[0]:
                    swipe_direction_and_predicate = str(each[2]).strip()

        except:
            errMsg = "Invalid action data. Please try with a valid action data by adding a new action."
            return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

        if swipe_direction_and_predicate in ("up", "down", "left", "right"):
            direction = swipe_direction_and_predicate
        else:
            predicateString = swipe_direction_and_predicate

        try:
            swipe_dict = {}

            if element_given:
                Element = LocateElement.Get_Element(data_set, appium_driver)
                if Element == "failed":
                    CommonUtil.ExecLog(
                        sModuleInfo, "Unable to locate the element, performing swipe without element.", 2
                    )
                else:
                    swipe_dict["element"] = Element

            if direction != "":
                swipe_dict["direction"] = direction
            else:
                swipe_dict["predicateString"] = predicateString
            appium_driver.execute_script("mobile: scroll", swipe_dict)
        except:
            errMsg = "Failed to perform swipe."
            return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

        return "passed"
    except:
        errMsg = "Unable to swipe."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def swipe_handler_android(data_set=[], save_att_data_set={}):
    """ Swipe screen based on user input """
    """
        Function: Performs a single swipe gesture in a vertical or horizonal direction
        Inputs:
            direction (mandatory except when using exact): left/right/up/down (eg: 'left' = from right to left)
            exact: Ignores all other settings, user needs to specify exact coordinates in the format of x1, y1, x2, y2
            inset (optional): Defaults to 10%. Swipe starts at inset
            position (optional): Defaults to 50%. Swipe this far from the top or left. So if I swipe left to right, Y will be 50%, so the middle of the screen with a horizontal swipe
            duration (optional): Defaults to 100ms. Complete the swipe gesture over this time period
            element parameter: Ignores  "exact". Direction is required. Use an element as the starting point (top left corner of the element). Calculations are based off that
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    @logger
    def Calc_Swipe(w, h, inset, direction, position, exact, adjust):
        """ Calculate swipe based on area of interest (screen or element) """
        try:
            # Adjust numbers depending on type provided by user - float or integer expected here - convert into pixels
            if (
                exact != ""
            ):  # User specified exact coordinates, so use those and nothing else
                x1, y1, x2, y2 = list(map(int, exact.split(",")))
            else:
                inset = float(str(inset).replace("%", "")) / 100.0  # Convert % to float
                position = float(str(position).replace("%", "")) / 100.0  # Convert % to float
                adjust = int(adjust) if adjust else 0

                if direction == "left":
                    tmp = 1.0 - inset  # Calculate from other end (X% from max width)
                    inset = round(tmp * w)
                    position = round(position * h)
                elif direction == "down":
                    inset = round(inset * h)  # Convert into pixels for that direction
                    position = round(position * w)
                elif direction == "right":
                    inset = round(inset * w)  # Convert into pixels for that direction
                    position = round(position * h)
                elif direction == "up":
                    tmp = 1.0 - inset  # Calculate from other end (X% from max height)
                    inset = round(tmp * h)
                    position = round(position * w)

                # Calculate exact pixel for the swipe
                if direction == "left":
                    x1 = inset - 1
                    x2 = adjust       # don't need +1 here
                    y1 = position
                    y2 = position
                elif direction == "down":
                    x1 = position
                    x2 = position
                    y1 = inset     # don't need +1 here
                    y2 = h - 1 + adjust
                elif direction == "right":
                    x1 = inset      # don't need +1 here
                    x2 = w - 1 - adjust
                    y1 = position
                    y2 = position
                elif direction == "up":
                    x1 = position
                    x2 = position
                    y1 = inset - 1
                    y2 = - adjust       # don't need +1 here

            return (
                x1,
                x2,
                y1,
                y2,
                inset,
                position,
            )  # Return inset and position just for logging purposes)
        except Exception:
            errMsg = "Error calculating swipe gesture"
            result = CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
            return result, "", "", ""

    # Get screen size for calculations
    try:
        full_screen_mode = False  # Use appium swipe instead of adb swipe (which is used when there's a vitual navigation bar that we need to swipe under)
        window_size1 = get_window_size()  # get_size method (standard)
        window_size2 = get_window_size(True)  # xpath() method
        if window_size1 == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Couldn't read screen size", 3)
            return "failed"
        height_with_navbar = int(
            window_size1["height"]
        )  # Read standard height (on devices with a nav bar, this is not the actual height of the screen)
        height_without_navbar = int(
            window_size2["height"]
        )  # Read full screen height (not at all accurate on devices without a navbar
        if (
            height_with_navbar < height_without_navbar
        ):  # Detected full screen mode and the height readings were different, indicating a navigation bar needs to be compensated for
            w = int(window_size2["width"])
            h = int(window_size2["height"])
            CommonUtil.ExecLog(
                sModuleInfo,
                "Detected navigation bar. Enabling ADB swipe for that area",
                0,
            )
            full_screen_mode = True  # Flag to use adb to swipe later on
        else:
            w = int(window_size1["width"])
            h = int(window_size1["height"])

        CommonUtil.ExecLog(sModuleInfo, "Screen size (WxH): %d x %d" % (w, h), 0)
    except Exception:
        errMsg = "Unable to read screen size"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Parse data set
    try:
        if save_att_data_set:
            inset = save_att_data_set["inset"]  # Default 0% of screen from edge as start of swipe
            direction = save_att_data_set["direction"]  # Left/right/up/down
            exact = save_att_data_set["exact"]  # Coordinates of exact swipe gesture in x1, y1, x2, y2
            position = save_att_data_set["position"]  # Default 50% of screen from edge for general swipes
            Element = save_att_data_set["Element"]  # Optional element object
            duration = save_att_data_set["duration"]  # Duration of the swipe in ms. default 5000 ms for 1550 pixel
            ADB = save_att_data_set["adb"]  # Check which method to be used for swipe
            adjust = save_att_data_set["adjust"]    # Adjust the scrolling amount
        else:
            adjust = ""
            inset = 10  # Default 10% of screen from edge as start of swipe
            direction = ""  # Left/right/up/down
            exact = ""  # Coordinates of exact swipe gesture in x1, y1, x2, y2
            position = 50  # Default 50% of screen from edge for general swipes
            Element = ""  # Optional element object
            duration = 100  # Duration of the swipe in ms
            for row in data_set:
                if row[1] == "input parameter":
                    op = row[0].strip().lower()
                    if op == "inset":
                        inset = row[2].strip()
                    elif op == "direction":
                        direction = row[2].lower().strip()
                    elif op == "exact":
                        exact = row[2].lower().strip().replace(" ", "")
                    elif op == "position":
                        position = row[2].lower().strip()
                    elif op == "duration":
                        duration = int(row[2].lower().strip())
                    elif op == "adjust pixel":
                        adjust = row[2].strip()
                elif row[1] == "element parameter" or row[1] == "unique parameter":
                    Element = LocateElement.Get_Element(data_set, appium_driver)
                    if Element == "failed":
                        CommonUtil.ExecLog(
                            sModuleInfo, "Unable to locate your element with given data.", 3
                        )
                        return "failed"

        # Verify we have what we need
        if (
            inset == ""
            or direction not in ("left", "right", "up", "down")
            or position == ""
        ):
            if (
                exact == ""
            ):  # If this is set, then the others don't matter, so continue with the gesture
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Missing critical swipe values. Either 'inset' (optional), 'direction' (required), or 'position' (optional) are missing, wrong or blank",
                    3,
                )
                return "failed"

        # If an element parameter was provided, get it's x, y, w, h
        if Element:
            location = Element.location  # Get element x,y coordinates
            size = Element.size
            elementX, elementY = int(location["x"]), int(location["y"])
            elementW, elementH = int(size["width"]), int(size["height"])
            CommonUtil.ExecLog(
                sModuleInfo,
                "Element X, Y, W, H: %d, %d, %d, %d"
                % (elementX, elementY, elementW, elementH),
                0,
            )

            # Calculate coordinates, based on element position and size
            x1, x2, y1, y2, inset, position = Calc_Swipe(
                elementW, elementH, inset, direction, position, "", adjust
            )
            # Using element calculations, now calculate to make relative to entire screen size
            if direction == "left":
                x1 += elementX
                x2 += elementX
                y1 += elementY
                y2 += elementY
            elif direction == "down":
                y1 += elementY
                y2 += elementY
                x1 += elementX
                x2 += elementX
            elif direction == "right":
                x1 += elementX
                x2 += elementX
                y1 += elementY
                y2 += elementY
            elif direction == "up":
                y2 += elementY
                y1 += elementY
                x1 += elementX
                x2 += elementX
        else:
            # No element, calculate swipe coordinates based on screen size
            x1, x2, y1, y2, inset, position = Calc_Swipe(
                w, h, inset, direction, position, exact, adjust
            )
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Perform swipe gesture
    try:
        if exact != "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Performing an exact swipe using coordinates: %d, %d to %d, %d %d ms"
                % (x1, y1, x2, y2, duration),
                1,
            )
        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Performing calculated swipe gesture based on inset: %d, position: %d, direction: %s, calculated as %d, %d to %d, %d %d ms"
                % (inset, position, direction, x1, y1, x2, y2, duration),
                1,
            )

        if save_att_data_set and ADB:
            # Use ADB forcely if ADB is set to True otherwise check y1,height_with_navbar as usual
            result = Swipe(
                x1, y1, x2, y2, duration, adb=True
            )
        elif full_screen_mode and (y1 >= height_with_navbar or y2 >= height_with_navbar):
            # Swipe in the navigation bar area if the device has one, when in full screen mode
            result = Swipe(
                x1, y1, x2, y2, duration, adb=True
            )  # Perform swipe using adb
        else:  # Swipe via appium by default
            result = Swipe(
                x1, y1, x2, y2, duration, adb=False
            )  # Perform swipe !!!adb set True for testing

        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not swipe the screen", 1)
            return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Swiped the screen successfully", 1)
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error performing swipe gesture"
        )


@logger
def read_screen_heirarchy():
    """ Read the XML string of the device's GUI and return it """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        data = appium_driver.page_source  # Read screen and get xml formatted text
        CommonUtil.ExecLog(sModuleInfo, "Read screen heirarchy successfully", 1)
        if data:
            return data
        else:
            return False
    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Read screen heirarchy unsuccessfully", 3)
        return False


@logger
def clear_existing_media_ios(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Clears all media (photos and videos) from a booted device

    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to clear media.", 0)

        # get booted device id if not already available
        deviceid = subprocess.getoutput(
            "xcrun simctl list | grep 'Booted' | awk 'match($0, /\(([-0-9A-F]+)\)/) { print substr( $0, RSTART + 1, RLENGTH - 2 )}'"
        )

        # clear all media from the selected simulator
        os.system(
            "rm -rf ~/Library/Developer/CoreSimulator/Devices/%s/data/Media/DCIM/"
            % deviceid
        )
        os.system(
            "rm -rf ~/Library/Developer/CoreSimulator/Devices/%s/data/Media/PhotoData/"
            % deviceid
        )

        # Reboot simulator - Required if any new media is to be added afterwards
        os.system("xcrun simctl shutdown %s" % deviceid)
        os.system("xcrun simctl boot %s" % deviceid)

        CommonUtil.ExecLog(
            sModuleInfo, "Closed the media successfully from simulator.", 1
        )
        return "passed"

    except:
        errMsg = "No device, please ensure a device is booted to clear its media."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def add_media_ios(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        media_name = str(data_set[0][2]).strip()
        # Add image or video to a booted ios simulator
        os.system("xcrun simctl addmedia booted %s" % media_name)
        CommonUtil.ExecLog(sModuleInfo, "Successfully added media to device.", 0)
        return "passed"
    except:
        errMsg = "Unable to add media to device. Either no device is booted or media name is wrong."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def take_screenshot_appium(data_set):
    """
    Data set:
    take screenshot     appium action           filename_format

    The filename of the saved screenshot will be stored in the "zeuz_screenshot"
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    from pathlib import Path
    import time

    # Parse data set
    try:
        # There's only one row
        left, mid, right = data_set[0]

        filename_format = right
        if "default" in filename_format:
            filename_format = "%Y_%m_%d_%H-%M-%S"

        screenshot_folder = ConfigModule.get_config_value(
            "sectionOne", "screen_capture_folder", temp_config
        )
        filename = time.strftime(filename_format) + ".png"
        screenshot_path = str(Path(screenshot_folder) / Path(filename))
        appium_driver.save_screenshot(screenshot_path)

        # Save the screenshot's name into a variable
        Shared_Resources.Set_Shared_Variables("zeuz_screenshot", filename)
        Shared_Resources.Set_Shared_Variables("zeuz_screenshot_path", screenshot_path)

        return "passed"
    except:
        traceback.print_exc()
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def go_to_webpage(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    # Parse data set
    try:
        url = data_set[0][2]

        for _ in range(3):
            try:
                appium_driver.get(url)
                return "passed"
            except:
                CommonUtil.ExecLog(
                    sModuleInfo, "Failed executing go_to_webpage. Retrying...", 2
                )
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def tap_location(data_set):
    """ Tap the provided position using x,y cooridnates """
    # positions: list containing x,y coordinates

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    # Parse data set
    try:
        positions = []
        posX, posY = data_set[0][2].replace(" ", "").split(",")
        positions.append(
            (posX, posY)
        )  # Put coordinates in a tuple inside of a list - must be this way for appium_driver.tap
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    try:
        appium_driver.tap(positions)  # Tap the location (must be in list format)
        CommonUtil.ExecLog(sModuleInfo, "Tapped on location successfully", 0)
        return "passed"
    except Exception:
        errMsg = "Tapped on location unsuccessfully"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_element_location_by_id(data_set):
    """ Find and return an element's x,y coordinates """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    # Parse data set
    try:
        _id = ""
        action_value = ""
        for row in data_set:  # Find element name from element parameter
            if row[1] == "element parameter":
                _id = row[2]
            elif row[1] == "action":
                action_value = row[2]
        if _id == "" or action_value == "":
            CommonUtil.ExecLog(sModuleInfo, "Could not find element parameter", 3)
            return "failed"
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    try:
        Element = LocateElement.Get_Element(data_set, appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "failed"
        location = Element.location  # Get element x,y coordinates
        positions = "%s,%s" % (
            location["x"],
            location["y"],
        )  # Save as a string - The function that uses this will need to put it in the format it needs
        CommonUtil.ExecLog(sModuleInfo, "Retreived location successfully", 1)

        result = Shared_Resources.Set_Shared_Variables(
            action_value, positions
        )  # Save position in shared variables
        return result
    except Exception:
        errMsg = "Retreived location unsuccessfully"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_window_size(read_type=False):
    """ Read the device's LCD resolution / screen size """
    # Returns a dictionary of width and height

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        if read_type:
            return appium_driver.find_element_by_xpath(
                "//*[not(*)]"
            ).size  # Works well at reading height in full screen mode, but Appium may complain if you work outside the boundaries it has set
        else:
            return (
                appium_driver.get_window_size()
            )  # Read the screen size as reported by the device - this is always the safe value to work within
        CommonUtil.ExecLog(sModuleInfo, "Read window size successfully", 0)
    except Exception:
        errMsg = "Read window size unsuccessfully"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Click_Element_Appium(data_set):
    """ Execute "click" for an element 
    
      if optional parameter is provided for offset, we will take it from the center of the object and % center of the bound
      
      Example:
      below example will offset by 25% to the right off the center of the element.  If we select 100% it will go to the right edge of the bound.  If you want to go left prove -25.
            
      x_offset:y_offset             optional option           25:0
    
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    context_switched = False
    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    try:

        x_offset = False
        y_offset = False
        offset = False

        for row in data_set:
            if (
                "option" in str(row[1]).lower().strip()
                and "x_offset:y_offset" in str(row[0]).lower().strip()
            ):
                offset = True
                x_offset = ((str(row[2]).lower().strip()).split(":")[0]).strip()
                y_offset = ((str(row[2]).lower().strip()).split(":")[1]).strip()

        Element = LocateElement.Get_Element(data_set, appium_driver)

        if Element == "failed":

            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            CommonUtil.ExecLog(sModuleInfo, "Trying to see if there are contexts", 1)

            context_result = auto_switch_context_and_try("webview")
            if context_result == "failed":
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Unable to locate your element with different contexts.",
                    3,
                )
                return "failed"
            else:
                context_switched = True
            Element = LocateElement.Get_Element(data_set, appium_driver)
            if Element == "failed":
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Unable to locate your element with different contexts.",
                    3,
                )
                if context_switched == True:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Context was switched during this action.  Switching back to default Native Context",
                        1,
                    )
                    context_result = auto_switch_context_and_try("native")
                return "failed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo, "Found your element with different context", 1
                )

        if Element.is_enabled():
            if offset == True:
                try:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Clicking the element based on offset with appium TouchAction.",
                        1,
                    )
                    start_loc = Element.location
                    height_width = Element.size
                    start_x = int((start_loc)["x"])
                    start_y = int((start_loc)["y"])
                    ele_width = int((height_width)["width"])
                    ele_height = int((height_width)["height"])

                    # calculate center of the elem
                    center_x = start_x + (ele_width / 2)
                    center_y = start_y + (ele_height / 2)
                    # we need to divide the width and height by 2 as we are offseting from the center not the full
                    total_x_offset = (int(x_offset) / 100) * (ele_width / 2)
                    total_y_offset = (int(y_offset) / 100) * (ele_height / 2)

                    x_cord_to_tap = center_x + total_x_offset
                    y_cord_to_tap = center_y + total_y_offset
                    TouchAction(appium_driver).tap(
                        None, x_cord_to_tap, y_cord_to_tap, 1
                    ).perform()
                    CommonUtil.ExecLog(
                        sModuleInfo, "Tapped on element by offset successfully", 1
                    )
                    if context_switched == True:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Context was switched during this action.  Switching back to default Native Context",
                            1,
                        )
                        context_result = auto_switch_context_and_try("native")

                    return "passed"

                except:
                    # CommonUtil.TakeScreenShot(sModuleInfo)
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Element is enabled. Unable to tap based on offset.",
                        3,
                    )
                    if context_switched == True:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Context was switched during this action.  Switching back to default Native Context",
                            1,
                        )
                        context_result = auto_switch_context_and_try("native")

                    return "failed"

            else:
                try:
                    Element.click()
                    # CommonUtil.TakeScreenShot(sModuleInfo)
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Successfully clicked the element with given parameters and values",
                        1,
                    )
                    if context_switched == True:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Context was switched during this action.  Switching back to default Native Context",
                            1,
                        )
                        context_result = auto_switch_context_and_try("native")
                    return "passed"

                except Exception:
                    errMsg = "Could not select/click your element."

                    if context_switched == True:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Context was switched during this action.  Switching back to default Native Context",
                            1,
                        )
                        context_result = auto_switch_context_and_try("native")
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

        else:
            # CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Element not enabled. Unable to click.", 3)
            if context_switched == True:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Context was switched during this action.  Switching back to default Native Context",
                    1,
                )
                context_result = auto_switch_context_and_try("native")
            return "failed"

    except Exception:
        if context_switched == True:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Context was switched during this action.  Switching back to default Native Context",
                1,
            )
            context_result = auto_switch_context_and_try("native")
        errMsg = "Could not find/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Tap_Appium(data_set):
    """ Execute "Tap" for an element 
      if optional parameter is provided for offset, we will take it from the center of the object and % center of the bound
      
      Example:
      below example will offset by 25% to the right off the center of the element.  If we select 100% it will go to the right edge of the bound.  If you want to go left prove -25.
            
      x_offset:y_offset             optional parameter           25:0
    
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    try:

        x_offset = False
        y_offset = False
        offset = False

        for row in data_set:
            if (
                "option" in str(row[1]).lower().strip()
                and "x_offset:y_offset" in str(row[0]).lower().strip()
            ):
                offset = True
                x_offset = ((str(row[2]).lower().strip()).split(":")[0]).strip()
                y_offset = ((str(row[2]).lower().strip()).split(":")[1]).strip()

        Element = LocateElement.Get_Element(data_set, appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "failed"
        else:
            try:
                if Element.is_enabled():

                    if offset == True:
                        try:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Tapping the element based on offset using TouchAction",
                                1,
                            )
                            start_loc = Element.location
                            height_width = Element.size

                            start_x = int((start_loc)["x"])
                            start_y = int((start_loc)["y"])

                            ele_width = int((height_width)["width"])
                            ele_height = int((height_width)["height"])

                            # calculate center of the elem
                            center_x = start_x + (ele_width / 2)
                            center_y = start_y + (ele_height / 2)
                            # we need to divide the width and height by 2 as we are offseting from the center not the full
                            total_x_offset = (int(x_offset) / 100) * (ele_width / 2)
                            total_y_offset = (int(y_offset) / 100) * (ele_height / 2)

                            x_cord_to_tap = center_x + total_x_offset
                            y_cord_to_tap = center_y + total_y_offset
                            TouchAction(appium_driver).tap(
                                None, x_cord_to_tap, y_cord_to_tap, 1
                            ).perform()
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Tapped on element by offset successfully",
                                1,
                            )
                            return "passed"

                        except:
                            # CommonUtil.TakeScreenShot(sModuleInfo)
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Element is enabled. Unable to tap based on offset.",
                                3,
                            )
                            return "failed"
                    else:

                        action = TouchAction(appium_driver)
                        action.tap(Element).perform()
                        CommonUtil.ExecLog(
                            sModuleInfo, "Tapped on element successfully", 1
                        )
                        return "passed"
                else:
                    # CommonUtil.TakeScreenShot(sModuleInfo)
                    CommonUtil.ExecLog(
                        sModuleInfo, "Element not enabled. Unable to click.", 3
                    )
                    return "failed"
            except Exception:
                errMsg = "Could not select/click your element."
                return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    except Exception:
        errMsg = "Unable to tap."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Double_Tap_Appium(data_set):
    #!!!not yet tested or used
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    try:
        Element = LocateElement.Get_Element(data_set, appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "failed"
        else:
            try:
                if Element.is_enabled():
                    action = TouchAction(appium_driver)

                    action.press(Element).wait(100).release().press(Element).wait(
                        100
                    ).release().perform()

                    CommonUtil.ExecLog(
                        sModuleInfo, "Double Tapped on element successfully", 1
                    )
                    return "passed"
                else:
                    # CommonUtil.TakeScreenShot(sModuleInfo)
                    CommonUtil.ExecLog(
                        sModuleInfo, "Element not enabled. Unable to click.", 3
                    )
                    return "failed"
            except Exception:
                errMsg = "Could not select/click your element."
                return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    except Exception:
        errMsg = "Unable to tap."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Long_Press_Appium(data_set):
    """ Press and hold an element """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    try:
        Element = LocateElement.Get_Element(data_set, appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "failed"
        else:
            try:
                if Element.is_enabled():
                    action = TouchAction(appium_driver)

                    action.long_press(Element, 150, 10).release().perform()

                    CommonUtil.ExecLog(
                        sModuleInfo, "Long Pressed on element successfully", 1
                    )
                    return "passed"
                else:
                    # CommonUtil.TakeScreenShot(sModuleInfo)
                    CommonUtil.ExecLog(
                        sModuleInfo, "Element not enabled. Unable to click.", 3
                    )
                    return "failed"
            except Exception:
                errMsg = "Could not select/click your element."
                return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    except Exception:
        errMsg = "Unable to tap."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Enter_Text_Appium(data_set):
    """ Write text to an element """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    context_switched = False

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    # Find text from action line
    text_value = (
        ""  # Initialize as empty string in case user wants to pass an empty string
    )
    try:
        for each in data_set:
            if each[1] == "action":
                text_value = each[2]
            else:
                continue
    except:
        errMsg = "Error while looking for action line"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Enter text into element
    try:
        Element = LocateElement.Get_Element(data_set, appium_driver)
        if Element == "failed":

            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            CommonUtil.ExecLog(sModuleInfo, "Trying to see if there are contexts", 1)

            context_result = auto_switch_context_and_try("webview")
            if context_result == "failed":
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Unable to locate your element with different contexts.",
                    3,
                )
                return "failed"
            else:
                context_switched = True
            Element = LocateElement.Get_Element(data_set, appium_driver)
            if Element == "failed":
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Unable to locate your element with different contexts.",
                    3,
                )
                if context_switched == True:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Context was switched during this action.  Switching back to default Native Context",
                        1,
                    )
                    context_result = auto_switch_context_and_try("native")
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Unable to locate your element with different contexts.",
                    3,
                )
                return "failed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo, "Found your element with different context", 1
                )

        # Click and clear the text box for both iOS and Android
        # We found found the element
        # sometimes when we click on the element, the element properties may stay same but the
        # actual reference may change. So in this case, we will need to search for element again once w
        # click on the element.
        try:
            CommonUtil.ExecLog(sModuleInfo, "Clicking and clearing the text field", 1)
            Element.click()  # Set focus to textbox
            Element = LocateElement.Get_Element(data_set, appium_driver)
            if Element == "failed":
                CommonUtil.ExecLog(
                    sModuleInfo, "Unable to locate your element with given data.", 3
                )
                CommonUtil.ExecLog(
                    sModuleInfo, "Trying to see if there are contexts", 1
                )
                context_result = auto_switch_context_and_try("webview")
                if context_result == "failed":
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Unable to locate your element with different contexts.",
                        3,
                    )
                    return "failed"
                else:
                    context_switched = True
                Element = LocateElement.Get_Element(data_set, appium_driver)
                if Element == "failed":
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Unable to locate your element with different contexts.",
                        3,
                    )
                    if context_switched == True:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Context was switched during this action.  Switching back to default Native Context",
                            1,
                        )
                        context_result = auto_switch_context_and_try("native")
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Unable to locate your element with different contexts.",
                        3,
                    )
                    return "failed"
                else:
                    CommonUtil.ExecLog(
                        sModuleInfo, "Found your element with different context", 1
                    )
            Element.clear()  # Remove any text already existing
        except:
            # just in case we run into any error, we will still try to proceed
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to click and clear the text field", 2
            )
            True

        try:
            # Trying to send text using send keys method
            Element.send_keys(
                text_value
            )  # Work around for IOS issue in Appium v1.6.4 where send_keys() doesn't work
            CommonUtil.ExecLog(
                sModuleInfo,
                "Successfully set the value of to text to: %s" % text_value,
                1,
            )
            if context_switched == True:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Context was switched during this action.  Switching back to default Native Context",
                    1,
                )
                context_result = auto_switch_context_and_try("native")
            return "passed"

        except Exception:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Found element, but couldn't write text to it using SendKeys method. Trying SetValue method",
                2,
            )
            # return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

        # This is wrapped in it's own try block because we sometimes get an error
        # from send_keys stating "Parameters were incorrect". However, most devices work only with send_keys
        try:
            Element.set_value(text_value)  # Enter the user specified text
            CommonUtil.ExecLog(
                sModuleInfo,
                "Successfully set the value of to text to: %s" % text_value,
                1,
            )
            if context_switched == True:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Context was switched during this action.  Switching back to default Native Context",
                    1,
                )
                context_result = auto_switch_context_and_try("native")
            return "passed"

        except Exception:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Still could not write text to it. Both SendKeys and Set_value method did not work",
                3,
            )
            if context_switched == True:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Context was switched during this action.  Switching back to default Native Context",
                    1,
                )
                context_result = auto_switch_context_and_try("native")
            errMsg = "Failed to enter text"
            return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    except Exception:
        errMsg = "Could not find element."
        if context_switched == True:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Context was switched during this action.  Switching back to default Native Context",
                1,
            )
            context_result = auto_switch_context_and_try("native")
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Pickerwheel_Appium(data_set):
    """ Write text to a pickerwheel """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    # Find text from action line
    text_value = (
        ""  # Initialize as empty string in case user wants to pass an empty string
    )
    try:
        for each in data_set:
            if each[1] == "action":
                text_value = each[2]
            else:
                continue
    except:
        errMsg = "Error while looking for action line"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Enter text into element
    try:
        Element = LocateElement.Get_Element(data_set, appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "failed"
        else:

            # This is wrapped in it's own try block because we sometimes get an error from send_keys stating "Parameters were incorrect". However, most devices work only with send_keys
            try:
                Element.set_value(text_value)  # Enter the user specified text
            except Exception:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Found element, but couldn't write text to it. Trying another method",
                    2,
                )

            # Complete the action
            try:
                # appium_driver.hide_keyboard() # Remove keyboard
                # CommonUtil.TakeScreenShot(sModuleInfo)  # Capture screen
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully set the value of to text to: %s" % text_value,
                    1,
                )
                return "passed"
            except Exception:
                errMsg = "Found element, but couldn't write text to it"
                return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
    except Exception:
        errMsg = "Could not find element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Clear_And_Enter_Text_ADB(data_set, serial=""):
    """ Enter string via adb"""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    device_platform = str(appium_driver.capabilities["platformName"].strip().lower())

    if device_platform != "android":
        CommonUtil.ExecLog(
            sModuleInfo,
            "Connected device is not Android.  Skipping this as pass.  This action is only for Android ",
            2,
        )
        return "passed"

    # Parse data set
    try:
        text_to_enter = data_set[0][2]

        if text_to_enter == "":
            CommonUtil.ExecLog(sModuleInfo, "Could not find string value", 3)
            return "failed"

    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    try:
        if appium_details[device_id]["type"] == "android":
            CommonUtil.ExecLog(sModuleInfo, "Entering your string via adb", 1)
            Delet_Text = ""
            # number of char to delete.  We can put this as element parameter in future for more flexiblity
            for x in range(0, 50):
                Delet_Text = "KEYCODE_DEL " + Delet_Text

            if serial != "":
                serial = (
                    "-s %s" % serial
                )  # Prepare serial number with command line switch
            # deleting existing text by going to end of line and clicking delete multiple times
            subprocess.check_output(
                "adb %s shell input keyevent 123" % (serial),
                shell=True,
                encoding="utf-8",
            )
            subprocess.check_output(
                "adb %s shell input keyevent %s" % (serial, Delet_Text),
                shell=True,
                encoding="utf-8",
            )
            # enters the string
            subprocess.check_output(
                "adb %s shell input text '%s'" % (serial, text_to_enter),
                shell=True,
                encoding="utf-8",
            )  # Enter password
            time.sleep(0.5)
            result = "passed"

        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Did not find any android device connected", 3
            )
            result = "failed"

        if result in passed_tag_list:
            # CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(
                sModuleInfo, "Successfully entered text with adb shell", 1
            )
            appium_driver.hide_keyboard()  # Remove keyboard
            # CommonUtil.TakeScreenShot(sModuleInfo)  # Capture screen
            CommonUtil.ExecLog(sModuleInfo, "Successfully hid keyboard", 1)

            return "passed"
        else:
            # CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Could not text with adb shell", 3)
            return "failed"

    except Exception:
        errMsg = "Could not enter string via adb."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Clear_And_Enter_Text_Appium(data_set):
    """ Write text to an element """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    # Find text from action line
    text_value = (
        ""  # Initialize as empty string in case user wants to pass an empty string
    )
    try:
        for each in data_set:
            if each[1] == "action":
                text_value = each[2]
            else:
                continue
    except:
        errMsg = "Error while looking for action line"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    # Enter text into element
    try:
        Element = LocateElement.Get_Element(data_set, appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "failed"
        else:
            try:
                # Enter text into element
                Element.click()  # Set focus to textbox
                Element.clear()  # Remove any text already existing

                if str(appium_details[device_id]["type"]).lower() == "ios":
                    Element.set_value(
                        text_value
                    )  # Work around for IOS issue in Appium v1.6.4 where send_keys() doesn't work
            except Exception:
                errMsg = "Found element, but couldn't write text to it"
                return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

            # This is wrapped in it's own try block because we sometimes get an error from send_keys stating "Parameters were incorrect". However, most devices work only with send_keys
            try:
                if str(appium_details[device_id]["type"]).lower() != "ios":
                    Element.send_keys(text_value)  # Enter the user specified text
            except Exception:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Found element, but couldn't write text to it. Trying another method",
                    2,
                )
                """try:
                    Element.set_value(text_value) # Enter the user specified text
                except Exception:
                    errMsg = "Found element, but couldn't write text to it. Giving up"
                    return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)"""

            # Complete the action
            try:
                # appium_driver.hide_keyboard() # Remove keyboard
                # CommonUtil.TakeScreenShot(sModuleInfo)  # Capture screen
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully set the value of to text to: %s" % text_value,
                    1,
                )
                return "passed"
            except Exception:
                errMsg = "Found element, but couldn't write text to it"
                return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
    except Exception:
        errMsg = "Could not find element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Hide_Keyboard(data_set):
    """ 
    This action is used to hide keyboard:
    hide keyboard             appium action           hide


     """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    device_platform = str(appium_driver.capabilities["platformName"].strip().lower())

    if device_platform != "android":
        CommonUtil.ExecLog(
            sModuleInfo,
            "Connected device is not Android.  Skipping this as pass.  This action is only for Android ",
            2,
        )
        return "passed"

    try:
        if appium_driver.is_keyboard_shown():
            appium_driver.hide_keyboard()  # Remove keyboard
            # CommonUtil.TakeScreenShot(sModuleInfo)  # Capture screen
        return "passed"
    except Exception:
        errMsg = "Unable to hide your keyboard"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Android_Keystroke_Key_Mapping(keystroke, hold_key=False):
    """ Provides a friendly interface to invoke key events """
    # Keycodes: https://developer.android.com/reference/android/view/KeyEvent.html

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Sanitize input
    keystroke = keystroke.strip()
    keystroke = keystroke.lower()
    keystroke = keystroke.replace("_", " ")

    try:
        if keystroke == "return" or keystroke == "enter":
            key = 66
        elif keystroke == "go back" or keystroke == "back":
            key = 4
        elif keystroke == "spacebar":
            key = 62
        elif keystroke == "backspace":
            key = 67
        elif (
            keystroke == "call"
        ):  # Press call connect, or starts phone program if not already started
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
        elif keystroke in (
            "app switch",
            "task switch",
            "overview",
            "recents",
        ):  # Task switcher / overview screen
            key = 187
        elif keystroke == "page down":
            key = 93
        elif keystroke == "page up":
            key = 92
        elif "raw=" in keystroke:
            key = int(keystroke.split("=")[1])
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unsupported key event: %s" % keystroke, 3)
            return "failed"

        if hold_key:
            appium_driver.long_press_keycode(key)  # About 0.5s hold, not configurable
        else:
            appium_driver.press_keycode(key)  # driver.keyevent() is depreciated

        return "passed"
    except Exception as e:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def iOS_Keystroke_Key_Mapping(keystroke):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    CommonUtil.ExecLog(sModuleInfo, "IOS key events not yet supported" % keystroke, 3)
    return "failed"

    try:
        if keystroke == "return" or keystroke == "enter":
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
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Keystroke_Appium(data_set):
    """ Send physical or virtual key press or long key press event

    You can find all the available keyevent from Android Development page:
    https://developer.android.com/reference/android/view/KeyEvent.html

    Example: To perform a TAB key stroke, you can search  for TAB on the website mentioned above and locate KEYCODE_TAB.
    You will notice that it has a Constant Value: 61. To perform TAB key press:

    Field	    Sub Field	     Value
    keypress	appium action	 raw=61

    Field	    Sub Field	     Value
    keypress	appium action	 power

    Below are some of the commonly used actions which we have converted to make it easier to read.

    Example:
    "return", "enter", "go back", "back", "spacebar", "backspace", "call", "end call", "home", "mute", "volume down",
    "volume up", "wake", "power", "app switch", "task switch", "overview", "recents", "page down", "page up"

    To perform a long press on the specified key code you have to add "long press " at starting of value. The action
    will hold the key for about 0.5 seconds which is not configurable.

    Example:

    Field	    Sub Field	     Value
    keypress	appium action	 long press raw=61

    Field	    Sub Field	     Value
    keypress	appium action	 long press power

    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    # Parse data set
    try:
        keystroke_value = ""
        for left, _, right in data_set:
            if "keypress" in left.lower():
                if "long press" in right.lower():
                    hold_key = True
                    keystroke_value = right.replace("long press", "")
                elif "longpress" in right.lower():
                    hold_key = True
                    keystroke_value = right.replace("longpress", "")
                else:
                    hold_key = False
                    keystroke_value = right

        if keystroke_value == "":
            CommonUtil.ExecLog(sModuleInfo, "Could not find keystroke value", 3)
            return "failed"

    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    try:
        # Execute the correct key stroke handler for the dependency
        if appium_details[device_id]["type"] == "android":
            result = Android_Keystroke_Key_Mapping(keystroke_value, hold_key)
        elif appium_details[device_id]["type"] == "ios":
            result = iOS_Keystroke_Key_Mapping(keystroke_value)
        else:
            result = "failed"

        if result in passed_tag_list:
            # CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(
                sModuleInfo,
                "Successfully entered keystroke for the element with given parameters and values",
                1,
            )
            return "passed"
        else:
            # CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(
                sModuleInfo,
                "Could not enter keystroke for the element with given parameters and values",
                3,
            )
            return "failed"

    except Exception:
        errMsg = "Could not enter keystroke."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


# Validating text from an element given information regarding the expected text
@logger
def Validate_Text_Appium(data_set):
    """

    @sreejoy, this will need your review 

    This needs more time to fix.
    Should be a lot more simple design
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    data_set = [data_set]
    try:
        for each_step_data_item in data_set[0]:
            if (
                "parameter" in each_step_data_item[1]
                or each_step_data_item[1] == "element parameter"
            ) and each_step_data_item[2] == "":
                Element = appium_driver.find_elements_by_xpath(
                    "//*[@%s]" % each_step_data_item[0]
                )
            if (
                "parameter" in each_step_data_item[1]
                or each_step_data_item[1] == "element parameter"
            ) and each_step_data_item[2] != "":
                Element = LocateElement.Get_Element(data_set[0], appium_driver)
                Element = [Element]

        if Element == "failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "failed"

        # Get the 'action' parameter and 'value' from step data
        for each_step_data_item in data_set[0]:
            if each_step_data_item[1] == "action":
                expected_text_data = each_step_data_item[2].split(
                    "||"
                )  # Split the separator in case multiple string provided in the same data_set
                validation_type = each_step_data_item[0]

        # Get the string for a single and multiple element(s)
        list_of_element_text = []
        list_of_element = []
        if len(Element) == 0:
            return False
        elif len(Element) == 1:
            for each_text in Element:
                list_of_element = each_text.text  # Extract the text element
                list_of_element_text.append(list_of_element)
        elif len(Element) > 1:
            for each_text in Element:
                list_of_element = each_text.text.split(
                    "\n"
                )  # Extract the text elements
                list_of_element_text.append(list_of_element[0])
        else:
            return "failed"

        # Extract only the visible element(s)
        visible_list_of_element_text = []
        for each_text_item in list_of_element_text:
            if each_text_item != "":
                visible_list_of_element_text.append(each_text_item)

        # Validate the partial text/string provided in the step data with the text obtained from the device
        if validation_type == "validate partial text":
            actual_text_data = visible_list_of_element_text
            CommonUtil.ExecLog(
                sModuleInfo, ">>>>>> Expected Text: %s" % expected_text_data, 0
            )
            #             print (">>>>>> Expected Text: %s" %expected_text_data)
            CommonUtil.ExecLog(
                sModuleInfo, ">>>>>>>> Actual Text: %s" % actual_text_data, 0
            )
            #             print (">>>>>>>> Actual Text: %s" %actual_text_data)
            for each_actual_text_data_item in actual_text_data:
                if (
                    expected_text_data[0] in each_actual_text_data_item
                ):  # index [0] used to remove the unicode 'u' from the text string
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Validate the text element %s using partial match."
                        % visible_list_of_element_text,
                        0,
                    )
                    return "passed"
                else:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Unable to validate the text element %s. Check the text element(s) in step_data(s) and/or in screen text."
                        % visible_list_of_element_text,
                        3,
                    )
                    return "failed"

        # Validate the full text/string provided in the step data with the text obtained from the device
        if validation_type == "validate full text":
            actual_text_data = visible_list_of_element_text
            CommonUtil.ExecLog(
                sModuleInfo, ">>>>>> Expected Text: %s" % expected_text_data, 0
            )
            #             print (">>>>>> Expected Text: %s" %expected_text_data)
            CommonUtil.ExecLog(
                sModuleInfo, ">>>>>>>> Actual Text: %s" % actual_text_data, 0
            )
            #             print (">>>>>>>> Actual Text: %s" %actual_text_data)
            if (
                expected_text_data[0] == actual_text_data[0]
            ):  # index [0] used to remove the unicode 'u' from the text string
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Validate the text element %s using complete match."
                    % visible_list_of_element_text,
                    0,
                )
                return "passed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Unable to validate the text element %s. Check the text element(s) in step_data(s) and/or in screen text."
                    % visible_list_of_element_text,
                    3,
                )
                return "failed"

        # Validate all the text/string provided in the step data with the text obtained from the device
        if validation_type == "validate screen text":
            CommonUtil.ExecLog(
                sModuleInfo, ">>>>>> Expected Text: %s" % expected_text_data, 0
            )
            #             print (">>>>>> Expected Text: %s" %expected_text_data)
            CommonUtil.ExecLog(
                sModuleInfo,
                ">>>>>>>> Actual Text: %s" % visible_list_of_element_text,
                0,
            )
            #             print (">>>>>>>> Actual Text: %s" %visible_list_of_element_text)
            i = 0
            for x in range(0, len(visible_list_of_element_text)):
                if (
                    visible_list_of_element_text[x] == expected_text_data[i]
                ):  # Validate the matching string
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "The text element '%s' has been validated by using complete match."
                        % visible_list_of_element_text[x],
                        1,
                    )
                    i += 1
                    return "passed"
                else:
                    visible_elem = [
                        ve for ve in visible_list_of_element_text[x].split()
                    ]
                    expected_elem = [ee for ee in expected_text_data[i].split()]
                    for elem in visible_elem:  # Validate the matching word
                        if elem in expected_elem:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Validate the text element '%s' using element match."
                                % elem,
                                1,
                            )
                            return "passed"
                        else:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Unable to validate the text element '%s'. Check the text element(s) in step_data(s) and/or in screen text."
                                % elem,
                                1,
                            )
                            return "failed"
                    if visible_elem[0] in expected_elem:
                        i += 1

        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Incorrect validation type. Please check step data", 3
            )
            return "failed"

    except Exception:
        errMsg = "Could not compare text as requested."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_program_names(search_name):
    """ Find Package and Activity name based on wildcard match """
    # Android only
    # Tested as working on v4.4.4, v5.1, v6.0.1
    # Note: Some programs require the very first activity name in order to launch the program. This may be a splash screen.
    # Alternative method to obtain activity name: Android-sdk/build-tools/aapt dumb badging program.apk| grep -i activity. This extracts it from the apk directly

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # @logger
    # def find_activity(secs):
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
    serial = ""
    if device_serial != "":
        serial = "-s %s" % device_serial

    # Find package name for the program that's already installed
    try:
        if adbOptions.is_android_connected(device_serial) == False:
            CommonUtil.ExecLog(
                sModuleInfo, "Could not detect any connected Android devices", 3
            )
            return "", ""  # Failure handling in calling function

        cmd = "adb %s shell pm list packages" % serial
        res = subprocess.check_output(
            cmd, shell=True, encoding="utf-8"
        )  # Get list of installed packages on device
        res = str(res).replace("\\r", "")  # Remove \r text if any
        res = str(res).replace("\\n", "\n")  # replace \n text with line feed
        res = str(res).replace("\r", "")  # Remove \r carriage return if any
        ary = res.split("\n")  # Split into list

        package_name = ""
        package_list = []
        for line in ary:  # For each package
            if search_name.lower() in line.lower():
                package_list.append(line.replace("package", "").replace(":", ""))

        if len(package_list) == 0:
            CommonUtil.ExecLog(
                sModuleInfo, "Did not find installed package: %s" % search_name, 3
            )
            return "", ""
        elif len(package_list) > 1:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Found more than one packages. Will use the first found. Please specify a more accurate package name. Found packages: %s"
                % package_list,
                2,
            )
        package_name = package_list[0]  # Save first package found

        # Get activity name
        cmd = "adb %s shell pm dump %s" % (serial, package_name)
        res = subprocess.check_output(cmd, shell=True, encoding="utf-8")
        res = str(res).replace("\\r", "")  # Remove \r text if any
        res = str(res).replace("\\n", "\n")  # replace \n text with line feed
        res = str(res).replace("\r", "")  # Remove \r carriage return if any
        p = re.compile("MAIN:.*?\s+([\w\.]+)/([\w\.]+)", re.S)
        m = p.search(str(res))
        try:
            if m.group(1) != "" and m.group(2) != "":
                return m.group(1), m.group(2)
        except:
            pass  # Error handling by calling function

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

        return (
            "",
            "",
        )  # Nothing found if we get here. Error handling handled by calling function

    except:
        result = CommonUtil.Exception_Handler(sys.exc_info())
        return result, ""


@logger
def device_information(data_set):
    """ Returns the requested device information """
    # This is the sequential action interface for much of the adbOptions.py and iosOptions.py, which provides direct device access via their standard comman line tools
    # Note: This function does not require an Appium instance, so it can be called without calling launch_application() first

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    # Parse data set
    try:

        if device_id:
            dep = appium_details[device_id]["type"]
        else:  # In case this was invoked without setting up appium, try to figure out connected device type. This could be useful if user just wants to reboot the phone
            if adbOptions.is_android_connected(device_serial):
                dep = "android"
            else:
                dep = "ios"
        cmd = ""
        shared_var = ""

        for row in data_set:  # Check each row
            if row[1] == "action":  # If this is the action row
                cmd = row[0].lower().strip()  # Save the command type
                shared_var = row[2]  # Save the name of the shared variable
                break

        if cmd == "":
            CommonUtil.ExecLog(
                sModuleInfo, "Action's Field contains incorrect information", 3
            )
            return "failed"
        if shared_var == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Action's Value contains incorrect information. Expected Shared Variable, or string",
                3,
            )
            return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(),
            None,
            "Error when trying to read Field and Value for action on device '%s' with appium details: %s"
            % (device_id, str(appium_details)),
        )

    # Ensure device is connected
    if dep == "android":
        if adbOptions.is_android_connected(device_serial) == False:
            CommonUtil.ExecLog(
                sModuleInfo, "Could not detect any connected Android devices", 3
            )
            return "failed"

    # Get device information
    try:
        if cmd == "imei":
            if dep == "android":
                output = adbOptions.get_device_imei_info(device_serial)
            elif dep == "ios":
                output = iosOptions.get_ios_imei(device_serial)
        elif cmd == "version":
            if dep == "android":
                output = adbOptions.get_android_version(device_serial)
            elif dep == "ios":
                output = iosOptions.get_ios_version(device_serial)
        elif cmd == "model name":
            if dep == "android":
                output = adbOptions.get_device_model(device_serial)
            elif dep == "ios":
                output = iosOptions.get_product_name(device_serial)
        elif cmd == "phone name":
            if dep == "ios":
                output = iosOptions.get_phone_name(device_serial)
        elif cmd == "serial no":
            if dep == "android":
                output = adbOptions.get_device_serial_no(device_serial)
        elif cmd == "storage":
            if dep == "android":
                output = adbOptions.get_device_storage(device_serial)
        elif cmd == "reboot":
            # If asterisk, then assume one or more attached and reset them all
            if shared_var == "*":
                if dep == "android":
                    output = adbOptions.reset_all_android()

            # Anything else, try to figure out what it is
            else:
                if (
                    shared_var in appium_details
                ):  # If user provided device name, get the associated serial number
                    shared_var = appium_details[shared_var]["serial"]
                elif adbOptions.is_android_connected(
                    shared_var
                ):  # Check if the specified device is connected via serial
                    pass
                else:  # No serial or name provided, and the string provided is not a connected device, just try to connect to the first device and reset it
                    shared_var = ""

                # Reset this one device
                if dep == "android":
                    output = adbOptions.reset_android(shared_var)

            shared_var = ""  # Unset this, so we don't create a shared variable with it
            if output in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Failed to reboot device", 3)
                return "failed"

        elif cmd == "wake":
            if dep == "android":
                if (
                    shared_var in appium_details
                ):  # If user provided device name, get the associated serial number
                    shared_var = appium_details[shared_var]["serial"]
                elif adbOptions.is_android_connected(
                    shared_var
                ):  # Check if the specified device is connected via serial
                    pass
                else:  # No serial or name provided, and the string provided is not a connected device, just try to connect to the first device and reset it
                    shared_var = ""

                output = adbOptions.wake_android(shared_var)
                shared_var = ""

            if output in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Failed to wake device", 3)
                return "failed"
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Action's Field contains incorrect information", 3
            )
            return "failed"

        if output in failed_tag_list or output == "":
            CommonUtil.ExecLog(
                sModuleInfo, "Could not find the device info about '%s'" % (cmd), 3
            )
            return "failed"

        # Save the output to the user specified shared variable
        if shared_var != "":
            Shared_Resources.Set_Shared_Variables(shared_var, output)
            CommonUtil.ExecLog(
                sModuleInfo, "Saved %s [%s] as %s" % (cmd, str(output), shared_var), 1
            )
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def set_device_password(data_set):
    """ Saves the device password to shared variables for use in unlocking the phone """
    # Caveat: Only allows one password stored at a time

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    # Parse data set
    try:
        password = data_set[0][2].strip()  # Read password from Value field
        if password != "":
            Shared_Resources.Set_Shared_Variables("device_password", password)
            CommonUtil.ExecLog(
                sModuleInfo, "Device password saved as: %s" % password, 1
            )
            return "passed"
        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Password cannot be blank. Expected Value field of action row to be a PIN or PASSWORD",
                3,
            )
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error when trying to read Field and Value for action"
        )


@logger
def switch_device(data_set):
    """ When multiple devices are connected, switches focus to one in particular given the serial number """
    # Device will be set as default until this function is called again
    # Not needed when only one device is connected

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    # Parse data set
    try:
        ID = data_set[0][2].lower().strip()  # Read password from Value field
        if ID != "":
            global device_serial, appium_details, appium_driver, device_id

            # Get information from dictionary, and update global variables
            device_serial = appium_details[ID]["serial"]
            appium_driver = appium_details[ID]["driver"]
            device_id = ID

            # Update shared variables, for anything that requires accessing that information
            Shared_Resources.Set_Shared_Variables(
                "device_id", device_id, protected=True
            )  # Save device id, because functions outside this file may require it
            CommonUtil.set_screenshot_vars(
                Shared_Resources.Shared_Variable_Export()
            )  # Get all the shared variables, and pass them to CommonUtil

            CommonUtil.ExecLog(sModuleInfo, "Switched focus to: %s" % ID, 1)
            return "passed"
        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Serial number cannot be blank. Expected Value field of action row to be a serial number or UUID of the device connected via USB",
                3,
            )
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error when trying to read Field and Value for action"
        )


@logger
def package_information(data_set):
    """ Performs serveral actions on a package """
    # Note: Appium doens't have an API that allows us to execute anything we want, so this is the solution
    # Format is package, element parameter, PACKAGE_NAME | COMMAND, action, SHARED_VAR_NAME

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    # Parse data set
    try:
        package_name = ""
        shared_var = ""
        cmd = ""
        value = ""
        for row in data_set:
            if row[1] == "element parameter":
                package_name = row[2].strip()
            elif row[1] == "action":
                cmd = row[0].strip().lower().replace("  ", "")
                shared_var = row[2].strip()  # Not used for all commands

        if package_name == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Full or partial package name missing. Expected Value field to contain it",
                3,
            )
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error when trying to read Value for action"
        )

    # Get package name (if given partially)
    try:
        package_name, activity_name = get_program_names(
            package_name
        )  # Get package name
        if package_name in ("", "failed"):
            return "failed"  # get_program_names() logs the error
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error trying to get package name"
        )

    # Perform action
    try:
        if cmd == "package version":
            if shared_var == "":
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Shared Variable name expected in Value field on action row",
                    3,
                )
                return "failed"
            value = adbOptions.get_package_version(package_name, device_serial)
            result = Shared_Resources.Set_Shared_Variables(shared_var, value)
        elif cmd == "package installed":
            value = (
                package_name  # Store package name in shared variables, if user wants it
            )
            if shared_var != "":
                result = Shared_Resources.Set_Shared_Variables(
                    shared_var, value
                )  # Optional
            result = "passed"  # Do nothing. If the package is not installed, get_program_names() above will fail and return

        # Check result
        if result in failed_tag_list or result == "":
            CommonUtil.ExecLog(sModuleInfo, "Error trying to execute mobile program", 3)
            return "failed"

        CommonUtil.ExecLog(sModuleInfo, "%s was successful" % cmd, 1)
        if shared_var != "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Value '%s' saved to Shared Variable '%s'" % (value, shared_var),
                1,
            )
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error trying to execute mobile program"
        )


@logger
def minimize_appilcation(data_set):
    """ Hides the foreground application by pressing the home key """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    try:
        appium_driver.press_keycode(3)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(),
            None,
            "Error trying to minimize application by sending home key press",
        )


@logger
def maximize_appilcation(data_set):
    """ Displays the original program that was launched by appium """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    try:
        appium_driver.launch_app()
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error trying to maximize application"
        )


@logger
def serial_in_devices(serial, devices):
    """ Displays the original program that was launched by appium """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        for device in devices:
            if devices[device]["id"] == serial or str(device).lower() == serial.lower():
                return True
        return False
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error trying to maximize application"
        )


@logger
def Handle_Mobile_Alert(data_set):
    # accepts browser alert
    """
    this works for both ios and Android
    handle alert   appium action     get text = my_variable 
    handle alert   appium action     send text = my text to send to alert   
    handle alert   appium action     accept, pass, yes, ok (any of these would work)
    handle alert   appium action     reject, fail, no, cancel (any of these would work)
     
      
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    try:
        choice = None
        for row in data_set:
            if row[0].strip().lower() == "handle alert":
                choice = row[2]

        choice_lower = choice.lower()
        if (
            choice_lower == "accept"
            or choice == "pass"
            or choice == "yes"
            or choice == "ok"
            or choice == "allow"
        ):
            try:
                appium_driver.switch_to_alert().accept()
                CommonUtil.ExecLog(sModuleInfo, "Mobile alert accepted", 1)
                return "passed"
            except Exception:
                CommonUtil.ExecLog(sModuleInfo, "Mobile alert not found", 2)
                return "passed"

        elif (
            choice_lower == "reject"
            or choice == "fail"
            or choice == "no"
            or choice == "cancel"
            or choice == "dont allow"
        ):
            try:
                appium_driver.switch_to_alert().dismiss()
                CommonUtil.ExecLog(sModuleInfo, "Mobile alert rejected", 1)
                return "passed"
            except Exception:
                CommonUtil.ExecLog(sModuleInfo, "Mobile alert not found", 2)
                return "passed"

        elif "get text" in choice:
            try:
                alert_text = appium_driver.switch_to_alert().text
                appium_driver.switch_to_alert().accept()
                variable_name = (choice.split("="))[1]
                result = Shared_Resources.Set_Shared_Variables(
                    variable_name, alert_text
                )
                if result in failed_tag_list:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Value of Variable '%s' could not be saved!!!" % variable_name,
                        3,
                    )
                    return "failed"
                else:
                    Shared_Resources.Show_All_Shared_Variables()
                    return "passed"

            except Exception:
                CommonUtil.ExecLog(
                    sModuleInfo, "Mobile alert not found.  Unable to collect text", 3
                )
                return "failed"

        elif "send text" in choice:
            try:
                text_to_send = (choice.split("="))[1]
                appium_driver.switch_to_alert().send_keys(text_to_send)
                appium_driver.switch_to_alert().accept()
                return "passed"

            except Exception:
                CommonUtil.ExecLog(
                    sModuleInfo, "Unable to send text to alert pop up", 3
                )
                return "failed"

        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Wrong Step Data.  Please review the action help document",
                3,
            )
            return "failed"

    except Exception:
        ErrorMessage = "Failed to handle alert"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)


@logger
def Switch_Context(data_set):
    # switches context between native and webview
    """
    this works for both ios and Android
    switch context   appium action     native
    or 
    switch context   appium action     webview  (it will get the first webview)
    or 
    switch context    appium action    name_of_context

     
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    try:
        choice = None
        for row in data_set:
            if row[0].strip().lower() == "switch context":
                choice = row[2]

        choice = choice.strip()  # dont lower this

        try:
            all_contexts = appium_driver.contexts
            CommonUtil.ExecLog(
                sModuleInfo, "All available contexts are: %s" % all_contexts, 1
            )
            for each in all_contexts:

                if "NATIVE_APP" in each and choice == "native":
                    appium_driver.switch_to.context(each)
                    current_context = appium_driver.context
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Successfully switched context to: %s" % current_context,
                        1,
                    )
                    return "passed"

                elif choice == "webview" and "WEBVIEW" in each:
                    appium_driver.switch_to.context(each)
                    current_context = appium_driver.context
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Successfully switched context to: %s" % current_context,
                        1,
                    )
                    return "passed"

                else:
                    appium_driver.switch_to.context(choice)
                    current_context = appium_driver.context
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Successfully switched context to: %s" % current_context,
                        1,
                    )
                    return "passed"
            CommonUtil.ExecLog(sModuleInfo, "Could not switch to any other context", 3)
            return "failed"

        except Exception:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Unable to switch context requested: %s.  Please view log to see what are all the available contexts"
                % choice,
                3,
            )
            return "failed"

    except Exception:
        ErrorMessage = "Failed to handle alert"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)


@logger
def Save_Attribute_appium(step_data):
    # switches context between native and webview
    """
    this works for both ios and Android
    *** Enter attribute of element that you are trying to locate.  Example, class, ID ****    element parameter     *** Enter the value of the attribute that you are trying to locate. ***
     *** Attribute name that you are trying to save.  Example "value"***                      save parameter    *** Your variable.  please do not use spaces.  To recall your variable in other action use   %|your_variable|%   ****
    save attribute                                                                            appium action    save attribute   
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    skip_or_not = filter_optional_action_and_step_data(step_data, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    try:
        Element = LocateElement.Get_Element(step_data, appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "failed"
        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Target element was found. We will attempt to extract the attribute value that you provided",
                1,
            )

        for each_step_data_item in step_data:
            if "save parameter" in each_step_data_item[1]:
                variable_name = each_step_data_item[2]
                attribute_name = each_step_data_item[0]
                break
        try:
            attribute_value = Element.get_attribute(attribute_name)
        except Exception as supported_attribute:
            CommonUtil.ExecLog(sModuleInfo, str(supported_attribute), 3)
            return CommonUtil.Exception_Handler(sys.exc_info())

        CommonUtil.ExecLog(
            sModuleInfo,
            "Your attribute %s was found and value is %s"
            % (attribute_name, attribute_value),
            1,
        )
        if attribute_value == "":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to save attribute value as it is empty", 3
            )
            return "failed"

        result = Shared_Resources.Set_Shared_Variables(variable_name, attribute_value)

        if result in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Value of Variable '%s' could not be saved!!!" % variable_name,
                3,
            )
            return "failed"
        else:
            Shared_Resources.Show_All_Shared_Variables()
            CommonUtil.ExecLog(
                sModuleInfo, "Value of Variable '%s' was saved" % variable_name, 1
            )
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def save_attribute_values_appium(step_data):
    """
    This action will expect users to provide a parent element under which they are expecting
    to collect multiple objects.  Users can provide certain constrain to search their elements
    Sample data:

    resource-id                      element parameter      android:id/list

    attributes                       target parameter       resource-id="com.whatsapp:id/conversations_row_contact_name",
                                                            return="text",
                                                            return_contains="J",
                                                            return_contains="A",
                                                            return_does_not_contain="John",
                                                            return_does_not_contain="Abraham"

    attributes                       target parameter       class="com.whatsapp:id/conversations_row_date",
                                                            return="text",
                                                            return_does_not_contain="yesterday"

    inset                            scroll parameter       15

    duration                         scroll parameter       6.5

    positon                          scroll parameter       60

    direction                        scroll parameter       up

    exact                            scroll parameter       360,1800,360,240

    adb                              scroll parameter       True

    max scroll                        scroll parameter       25

    delay for loading                scroll parameter       2

    adjust scroll                    scroll parameter       +65

    adjust fluctuation               scroll parameter       6

    text                             end parameter          No more suggestions

    save attribute values in list    selenium action        list_name

    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    skip_or_not = filter_optional_action_and_step_data(step_data, sModuleInfo)
    if not skip_or_not:
        return "passed"
    global appium_driver
    try:
        Element = LocateElement.Get_Element(step_data, appium_driver)
        if Element == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "failed"

        target_index = 0
        target = []
        input_param = {"inset": "0", "direction": "up", "exact": "", "position": "50", "adb": False, "Element": Element, "adjust": ""}
        elementH, elementW, elementX, elementY = Element.size["height"], Element.size["width"], Element.location["x"], Element.location["y"]
        if input_param["direction"] == "up":
            input_param["duration"] = elementH * 3.2  # Swipe 3.2 pixel per millisecond
        elif input_param["direction"] == "down":
            input_param["duration"] = elementH * 3.2
        elif input_param["direction"] == "left":
            input_param["duration"] = elementW * 3.2
        elif input_param["direction"] == "right":
            input_param["duration"] = elementW * 3.2

        delay = 0.0
        adjust_fluctuation = 5
        end_parameter = []
        max_swipe = float('inf')
        try:
            for left, mid, right in step_data:
                left = left.strip().lower()
                mid = mid.strip().lower()
                right = right.strip()
                if "target parameter" in mid:
                    target.append([[], [], [], []])
                    temp = right.strip(",").split(",")
                    data = []
                    for each in temp:
                        data.append(each.strip().split("="))
                    for i in range(len(data)):
                        for j in range(len(data[i])):
                            data[i][j] = data[i][j].strip()
                            if j == 1:
                                data[i][j] = data[i][j].strip('"')  # do not add another strip here. dont need to strip inside quotation mark

                    for Left, Right in data:
                        if Left == "return":
                            target[target_index][1] = Right
                        elif Left == "return_contains":
                            target[target_index][2].append(Right)
                        elif Left == "return_does_not_contain":
                            target[target_index][3].append(Right)
                        else:
                            target[target_index][0].append((Left, 'element parameter', Right))

                    target_index = target_index + 1
                elif left == "save attribute values in list":
                    variable_name = right.strip()
                elif mid == "scroll parameter":
                    if left == "inset":
                        input_param["inset"] = right.strip()
                    elif left == "direction":
                        input_param["direction"] = right.lower().strip()
                    elif left == "exact":
                        input_param["exact"] = right.lower().strip().replace(" ", "")
                    elif left == "position":
                        input_param["position"] = right.lower().strip()
                    elif left == "duration":
                        input_param["duration"] = round(float(right.lower().strip()) * 1000)
                    elif left == "adb":
                        input_param["adb"] = True if right.strip().lower() in ("true", "yes", "ok") else False
                    elif left == "delay for loading":
                        delay = float(right.strip())
                    elif left == "adjust pixel":
                        input_param["adjust"] = right.strip()
                    elif left == "adjust fluctuation":
                        adjust_fluctuation = int(right.strip())
                    elif left == "max scroll":
                        max_swipe = int(right.strip())
                elif mid == "end parameter":
                    end_parameter.append((left, "element parameter", right))

        except:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to parse data. Please write data in correct format", 3
            )
            return "failed"

        ii = 0
        final = []
        init_once_only = True
        first_swipe_done = False

        while ii < max_swipe:
            # start = time.time()
            all_elements = []
            for each in target:
                all_elements.append(LocateElement.Get_Element(each[0], Element, return_all_elements=True))
            # print("Capturing all_elements = ", time.time()-start, "sec")
            # start = time.time()
            variable_value_size = []
            for each in all_elements:
                variable_value_size.append(len(each))

            variable_value = []
            for i in range(len(all_elements)):
                variable_value.append([])

            if init_once_only:  # Initiate these values once per scroll
                init_once_only = False
                del_range, temp_variable_value = [], []
                
                final = []
                upper_bound_touched, lower_bound_touched = [], []
                for i in range(len(all_elements)):
                    final.append([])
                    upper_bound_touched.append(False)
                    lower_bound_touched.append(False)
                    del_range.append([])
                    temp_variable_value.append([])

            i = 0   # j->i because inserting values column by column
            for branch in all_elements:
                search_by_attribute = target[i][1]
                for elem in branch:
                    try:
                        Attribute_value = elem.get_attribute(search_by_attribute)
                    except:
                        Attribute_value = None
                    variable_value[i].append(Attribute_value)
                i = i + 1
            pre_values_temp = copy.deepcopy(variable_value)

            for T in range(len(all_elements)):

                if first_swipe_done and variable_value == pre_values:   # Checking if end reached
                    CommonUtil.ExecLog(sModuleInfo, "Reached to the end. Stopped scrolling", 1)
                    break   # Stop scrolling. End reached!

                if first_swipe_done and del_range[T]:   # If end is not reached dont delete anything. Add everything
                    final[T] += temp_variable_value[T]
                    del_range[T], temp_variable_value[T] = [], []

                if input_param["direction"] == "up":    # Checking if the first element of current page touched the edge
                    upper_bound_touched[T] = all_elements[T][0].location["y"] - Element.location["y"] < adjust_fluctuation
                elif input_param["direction"] == "down":    # Need to fix
                    lower_bound_touched[T] = Element.location["y"] + Element.size["height"] - all_elements[T][-1].location["y"] - all_elements[T][-1].size["height"] < adjust_fluctuation
                elif input_param["direction"] == "left":
                    upper_bound_touched[T] = all_elements[T][0].location["x"] - Element.location["x"] < adjust_fluctuation
                elif input_param["direction"] == "right":   # Need to fix
                    lower_bound_touched[T] = Element.location["x"] + Element.size["width"] - all_elements[T][-1].location["x"] - all_elements[T][-1].size["width"] < adjust_fluctuation

                # If last element of previous page and first element of the current page touched the edge and they are same delete that item
                if first_swipe_done and pre_values[T][len(pre_values[T])-1] == variable_value[T][0] and lower_bound_touched[T] and upper_bound_touched[T]:
                    CommonUtil.ExecLog("", "Found '" + str(variable_value[T][0]) + "' in previous page. So deleting now", 2)
                    del variable_value[T][0]

                # on the last scroll many elements can be duplicated. putting them in a separate list than the main element
                elif first_swipe_done:
                    for i in range(len(pre_values[T])):
                        if pre_values[T][i] == variable_value[T][0]:
                            for j in range(len(pre_values[T])-i):
                                if pre_values[T][i+j] != variable_value[T][j]:
                                    break
                            else:
                                del_range[T] = [jj for jj in range(0, len(pre_values[T])-i)]
                                temp_variable_value[T] = copy.deepcopy(variable_value[T])
                            break

                if input_param["direction"] == "up":    # Checking if the last element of previous page touched the edge
                    lower_bound_touched[T] = Element.location["y"] + Element.size["height"] - all_elements[T][-1].location["y"] - all_elements[T][-1].size["height"] < adjust_fluctuation
                elif input_param["direction"] == "down":    # Need to fix
                    upper_bound_touched = all_elements[T][0].location["y"] - Element.location["y"] < adjust_fluctuation
                elif input_param["direction"] == "left":
                    lower_bound_touched[T] = Element.location["x"] + Element.size["width"] - all_elements[T][-1].location["x"] - all_elements[T][-1].size["width"] < adjust_fluctuation
                elif input_param["direction"] == "right":   # Need to fix
                    upper_bound_touched[T] = all_elements[T][0].location["x"] - Element.location["x"] < adjust_fluctuation

                if not del_range[T]:
                    final[T] += variable_value[T]
            else:
                pre_values = copy.deepcopy(pre_values_temp)
                # print("Calculation = ", time.time() - start, "sec")
                End_Elem = LocateElement.Get_Element(end_parameter, appium_driver) if end_parameter else "failed"
                if End_Elem != "failed":
                    CommonUtil.ExecLog("", "End Element found. Stopped scrolling", 1)
                    break  # Stop scrolling. End reached!
                swipe_handler_android(save_att_data_set=input_param)
                CommonUtil.ExecLog("", "Delaying " + str(delay) + " sec after scroll", 1)
                time.sleep(delay)
                ii += 1
                CommonUtil.ExecLog("", "Scrolled " + str(ii) + " times", 1)
                first_swipe_done = True
                continue
            break
        # start = time.time()
        for T in range(len(all_elements)):  # Delete multiple duplicates created for last page scrolling
            if first_swipe_done and variable_value == pre_values:
                if del_range[T]:
                    for i in del_range[T]:
                        CommonUtil.ExecLog("", "Found '" + str(temp_variable_value[T][0]) + "' in previous page. So deleting now", 2)
                        del temp_variable_value[T][0]
                    final[T] += temp_variable_value[T]
            else:
                if del_range[T]:
                    final[T] += temp_variable_value[T]

        # Filtering the elements with return_contains and return_does_not_contain
        final_size = 0
        for i in final:
            final_size = max(final_size, len(i))
        for i in range(len(final)):
            if len(final[i]) < final_size:
                for j in range(final_size - len(final[i])):
                    final[i].append(None)
        final = list(map(list, zip(*final)))

        for j in range(len(final[0])):
            for i in range(len(final)):
                for search_contain in target[j][2]:
                    if not isinstance(search_contain, type(final[i][j])) or search_contain in final[i][j] or len(search_contain) == 0:
                        break
                else:
                    if target[j][2]:
                        final[i][j] = None
                for search_doesnt_contain in target[j][3]:
                    if isinstance(search_doesnt_contain, type(final[i][j])) and search_doesnt_contain in final[i][j] and len(search_doesnt_contain) != 0:
                        final[i][j] = None
                        break

        # print("Searching =", time.time() - start, "sec")

        return Shared_Resources.Set_Shared_Variables(variable_name, final)
    # com.android.vending for play_store and com.android.contacts for contact
    # com.whatsapp for whatsapp
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def if_element_exists(data_set):
    """ Click on an element """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    skip_or_not = filter_optional_action_and_step_data(data_set, sModuleInfo)
    if skip_or_not == False:
        return "passed"

    try:
        variable_name = ""
        boolean = ""

        for left, mid, right in data_set:
            if "action" in mid:
                value, variable_name = right.split("=")
                value = value.strip()
                variable_name = variable_name.strip()

        Element = LocateElement.Get_Element(data_set, appium_driver)
        if Element in failed_tag_list:
            Shared_Resources.Set_Shared_Variables(variable_name, "false")
        else:
            Shared_Resources.Set_Shared_Variables(variable_name, value)
        return "passed"
    except Exception:
        errMsg = (
            "Failed to parse data/locate element. Data format: variableName = value"
        )
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def filter_optional_action_and_step_data(data_set, sModuleInfo):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        CommonUtil.ExecLog(
            sModuleInfo, "Checking to see if we need to skip this action based on OS", 1
        )
        device_platform = str(
            appium_driver.capabilities["platformName"].strip().lower()
        )
        CommonUtil.ExecLog(
            sModuleInfo, "Currently running with %s" % device_platform, 1
        )

        for row in data_set:
            if row[0].strip().lower() == "platform":
                os_to_run_on = row[2].strip().lower()
                if device_platform != os_to_run_on:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "[SKIP] This action has been marked as optional and only intended for the platform '%s'"
                        % os_to_run_on,
                        1,
                    )
                    return False
                else:
                    return True

        return True
    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Unable to skip optional action based on OS", 2)
        return True


@logger
def auto_switch_context_and_try(native_web):

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        choice = native_web
        all_contexts = appium_driver.contexts
        CommonUtil.ExecLog(
            sModuleInfo, "All available contexts are: %s" % all_contexts, 1
        )
        if len(all_contexts) == 1:
            CommonUtil.ExecLog(sModuleInfo, "There is only one context", 2)
            return "failed"

        for each in all_contexts:

            if "NATIVE_APP" in each and choice == "native":
                appium_driver.switch_to.context(each)
                current_context = appium_driver.context
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully switched context to: %s" % current_context,
                    1,
                )
                return "passed"

            elif choice == "webview" and "WEBVIEW" in each:
                appium_driver.switch_to.context(each)
                current_context = appium_driver.context
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully switched context to: %s" % current_context,
                    1,
                )
                return "passed"

        CommonUtil.ExecLog(sModuleInfo, "Could not switch to any other context", 2)
        return "failed"

    except Exception:
        CommonUtil.ExecLog(
            sModuleInfo,
            "Unable to switch context requested: %s.  Please view log to see what are all the available contexts"
            % choice,
            3,
        )
        return "failed"
