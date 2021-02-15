# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

# Android Debug Bridge (ADB) options to get the android devices info connected via usb/wi-fi
__author__ = "minar"
import subprocess, inspect, os, sys, re, math, time
from Framework.Utilities import CommonUtil
from Framework.Utilities.decorators import logger
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)


MODULE_NAME = inspect.getmodulename(__file__)


@logger
def start_adb_server():
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        output = subprocess.check_output(
            "adb start server", shell=True, encoding="utf-8"
        )
        CommonUtil.ExecLog(sModuleInfo, "Starting adb server", 0)
        return output

    except Exception:
        errMsg = "Unable to start adb server"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def kill_adb_server():
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        output = subprocess.check_output(
            "adb kill-server", shell=True, encoding="utf-8"
        )
        CommonUtil.ExecLog(sModuleInfo, "Killing adb server", 0)
        return output

    except Exception:
        errMsg = "Unable to kill adb server"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_android_version(serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s shell getprop ro.build.version.release" % serial,
            shell=True,
            encoding="utf-8",
        )
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        output_clean = str(output.strip())
        return output_clean

    except Exception:
        errMsg = "Unable to get android version"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_device_model(serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s shell getprop ro.product.model" % serial,
            shell=True,
            encoding="utf-8",
        )
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output.strip()

    except Exception:
        errMsg = "Unable to get device model"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_device_name(serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s shell getprop ro.product.name" % serial,
            shell=True,
            encoding="utf-8",
        )
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output

    except Exception:
        errMsg = "Unable to get device name"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_work_profile():
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        adb_output = subprocess.check_output(
            "adb shell pm list users", shell=True, encoding="utf-8"
        )

        users = str(adb_output).split("UserInfo")
        work_profile = "zeuz_failed"

        for user in users:
            if "Work profile" in user:
                s = user.split("{")[1]
                chunks = s.split(":")
                work_profile = int(chunks[0])
        return work_profile

    except Exception:
        errMsg = "Unable to get work profile"
        return "zeuz_failed"


@logger
def get_device_serial_no(serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s get-serialno" % serial, shell=True, encoding="utf-8"
        )
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output.strip()

    except Exception:
        errMsg = "Unableto get device serial no"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_package_version(package, serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s shell pm dump %s" % (serial, package), shell=True, encoding="utf-8"
        )
        storageList = output.splitlines()  #
        for lines in storageList:
            if (
                "versionName" in lines
            ):  # Find first instance of this, should be the version we need
                line1 = lines
        output1 = line1.split("=")[1]  # Version is on right side of equals sign
        CommonUtil.ExecLog(
            sModuleInfo, "Read %s has version %s" % (package, output1), 0
        )
        return output1.strip()

    except Exception:
        errMsg = "Unable to get package version"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_device_storage(serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s shell df /data" % serial, shell=True, encoding="utf-8"
        )
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        storageList = " ".join(output.split())
        storageList = storageList.split(" ")
        storage = storageList[6]
        storage = storage.replace("G", "")
        storage = float(storage)
        final_storage = 0
        exp = 2
        while True:
            gb = math.pow(2, exp)
            if storage < gb:
                final_storage = gb
                break
            exp += 1
        final_storage = int(final_storage)
        return final_storage

    except Exception:
        errMsg = "Unableto get device storage"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_device_manufacturer(serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s shell getprop ro.product.manufacturer" % serial,
            shell=True,
            encoding="utf-8",
        )
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output

    except Exception:
        errMsg = "Unable to get device manufacturer."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_device_imei_info(serial=""):
    """ Returns the device's IMEI """
    # Output: IMEI as a string

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s shell dumpsys iphonesubinfo" % serial, shell=True, encoding="utf-8"
        )
        # Use dumpsys (Below Android v6)
        if output != "":
            output = output.split("\n")[2]
            output = output.split(" ")[5].strip()

        # Use service call (Above Android v6)
        else:
            output = subprocess.check_output(
                "adb shell service call iphonesubinfo 1" % serial,
                shell=True,
                encoding="utf-8",
            )
            output = output.split(
                " "
            )  # Contains hex output, and characters that need to be removed
            tmp = ""
            for val in output:
                if "'" in val:
                    tmp += val  # Look for values that have a single quote, they are the ones with a portion of the IMEI

            chars = "\r\n.')"
            output = tmp.translate(None, chars)  # Remove characters we don't want

        if len(output) != 14 and len(output) != 15:
            CommonUtil.ExecLog(
                sModuleInfo, "Could not read the IMEI from the device", 3
            )
            return "zeuz_failed"

        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output

    except Exception:
        errMsg = "Error while trying to read IMEI from the device"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_device_summary():
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        output = subprocess.check_output("adb devices -l", shell=True, encoding="utf-8")
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output

    except Exception:
        errMsg = "Unable to get device summary"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_device_complete_info():
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        output = subprocess.check_output("adb devices -l", shell=True, encoding="utf-8")
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output

    except Exception:
        errMsg = "Unable to get device complete info"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_devices():
    """ Retrieves a list of connected devices in the format of "SERIAL_NO STATE" and returns as a list """
    # State may be "device" if connected and we can talk to it, or "unauthorized" if we can't talk to it

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        # Get list of connected devices
        output = subprocess.check_output("adb devices", shell=True, encoding="utf-8")

        # Cleanup data
        output = output.replace("\r", "")
        output = output.replace("\t", " ")
        output = output.split("\n")
        output.pop(0)  # Remove "list of..." string
        output = [
            line for line in output if line != "" and "*" not in line
        ]  # Probably better to look for two word line which only contains 'device', but this works for now

        # Return as list
        CommonUtil.ExecLog(sModuleInfo, "Connected devices: %s" % str(output), 0)
        return output

    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get devices", 3)
        return []


@logger
def is_android_connected(serial=""):
    """ Return True/False if at least one device is connected """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    devices = get_devices()

    if devices != []:
        if serial == "":
            return True  # No device specified, and we have at least one
        for device in devices:
            if serial.lower() == device.lower().split(" ")[0]:
                CommonUtil.ExecLog(sModuleInfo, "Android connected", 0)
                return True
        CommonUtil.ExecLog(
            sModuleInfo,
            "Android connected, but either not authorized or provided serial number not found in list. Ensure USB debugging is enabled in developer options, and that you authorized this computer to connect to it.",
            2,
        )
        return False
    else:
        CommonUtil.ExecLog(sModuleInfo, "No Android connected", 0)
        return False


@logger
def get_android_sdk(serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s shell getprop ro.build.version.sdk" % serial,
            shell=True,
            encoding="utf-8",
        )
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output

    except Exception:
        errMsg = "Unable to get android sdk"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def install_app(apk_path, serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s install -r %s" % (serial, apk_path), shell=True, encoding="utf-8"
        )
        CommonUtil.ExecLog(sModuleInfo, "Installed app located %s" % apk_path, 0)
        return output

    except Exception:
        errMsg = "Unable to install app located %s" % apk_path
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def uninstall_app(package, serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s uninstall %s" % (serial, package), shell=True, encoding="utf-8"
        )  # Install and overwrite (-r) if package is already installed
        CommonUtil.ExecLog(sModuleInfo, "Uninstalled app located %s" % package, 0)
        return "passed"

    except Exception:
        errMsg = "Unable to install app located %s" % package
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def connect_device_via_wifi(device_ip):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        output = subprocess.check_output("adb tcpip 5555", shell=True, encoding="utf-8")
        CommonUtil.ExecLog(
            sModuleInfo,
            "Target device set to listen for a TCP/IP connection on port 5555.",
            0,
        )
        output = subprocess.check_output(
            "adb connect %s" % device_ip, shell=True, encoding="utf-8"
        )
        CommonUtil.ExecLog(sModuleInfo, "Conncted to device via wifi", 0)
        output = subprocess.check_output("adb devices", shell=True, encoding="utf-8")
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output

    except Exception:
        errMsg = "Unable to connect device via wifi"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def take_screenshot(image_name, serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        # output = subprocess.check_output("adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > %s/%s.png"%(folder_path,image_name), shell=True)
        os.system("adb %s shell screencap -p /sdcard/%s.png" % (serial, image_name))
        os.system("adb %s pull /sdcard/%s.png" % (serial, image_name))
        CommonUtil.ExecLog(sModuleInfo, "Screenshot taken as %s.png" % image_name, 0)
        return "Screen shot taken"

    except Exception:
        errMsg = "Unable to take screenshot"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def record_screen(folder_path, video_name, serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        os.system(
            "adb %s shell screenrecord /sdcard/%s.mp4" % (serial, video_name),
            shell=True,
        )
        os.system("adb %s pull /sdcard/%s.mp4" % (serial, video_name))
        CommonUtil.ExecLog(sModuleInfo, "Screen recorded as %s.mp4" % video_name, 0)
        return "Screen recorded"

    except Exception:
        errMsg = "Unable to record"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_device_battery_info(serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s shell dumpsys battery" % serial, shell=True, encoding="utf-8"
        )
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output

    except Exception:
        errMsg = "Unable to get device battery info"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_device_wifi_info(serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s shell dumpsys wifi" % serial, shell=True, encoding="utf-8"
        )
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output

    except Exception:
        errMsg = "Unable to get device wifi info"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_device_cpu_info(serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s shell dumpsys cpuinfo" % serial, shell=True, encoding="utf-8"
        )
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output

    except Exception:
        errMsg = "Unable to get device CPU info"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_package_name(serial=""):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        output = subprocess.check_output(
            "adb %s shell pm list packages" % serial, shell=True, encoding="utf-8"
        )
        CommonUtil.ExecLog(
            sModuleInfo, "Getting Packages Name of Installed Applications", 0
        )
        return output

    except Exception:
        errMsg = "Unable to get Packages Name"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def wake_android(serial=""):
    """ Sends the wakeup keypress and a swipe up gesture to try to unlock the device and get it to a usable state for automation """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        # Get screen size, and calculate swipe gesture to get to home screen
        output = subprocess.check_output(
            "adb %s shell wm size" % serial, shell=True, encoding="utf-8"
        )  # Need size for swipe calculation
        m = re.search("(\d+)x(\d+)", output)  # Find w and h using regular expression
        w, h = (m.group(1), m.group(2))  # Save w and h
        spos = int(int(h) * 0.7)  # Calculate 70% of height as starting position
        epos = int(int(h) * 0.1)  # Calculate 10% of height as ending position
        centre = int(int(w) / 2)  # Calculate centre of screen horizontally

        # Wake device and send swipe gesture
        subprocess.check_output(
            "adb %s shell input keyevent KEYCODE_WAKEUP" % serial,
            shell=True,
            encoding="utf-8",
        )  # Send wakeup command (puts us on lock screen)
        subprocess.check_output(
            "adb %s shell input touchscreen swipe %d %d %d %d"
            % (serial, centre, spos, centre, epos),
            shell=True,
            encoding="utf-8",
        )  # Send vertical swipe command (takes us to home screen)
        CommonUtil.ExecLog(sModuleInfo, "Waking device", 0)

        # If there is a password, handle it
        # output = detect_foreground_android(serial.replace('-s ', ''))  # Check if we are on the password screen
        # if output == 'Bouncer':
        #     output = unlock_android(serial.replace('-s ', ''))
        #     if output == "zeuz_failed":
        #         return "zeuz_failed"

        return "passed"

    except Exception:
        errMsg = "Unable to wake device"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def unlock_android(serial=""):
    """ Attempt to enter password for locked phone """
    # Caveat 1: Only works if device has PIN or PASSWORD, not if they use a pattern, or pattern as a fingerprint backup
    # Caveat 2: Only works if the user connects USB and unlocks the phone. Then, if the phone is locked, we still have an ADB connection, and can work with it.

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        lock_status = ""
        if serial != "":
            serial_with_id = "-s %s" % serial
        subprocess.check_output(
            "adb %s shell svc power stayon usb" % (serial_with_id),
            shell=True,
            encoding="utf-8",
        )  # Wakeup device
        lock_status = check_if_device_is_unlocked(serial="")
        if lock_status == True:
            CommonUtil.ExecLog(
                sModuleInfo, "Device is already unlocked. No action is needed", 1
            )
            return "passed"

        # Get password
        if (
            sr.Test_Shared_Variables("device_password") == False
        ):  # Make sure user stored password in shared variables
            CommonUtil.ExecLog(
                sModuleInfo, "Can't unlock phone - no password specified.", 3
            )
            return "zeuz_failed"
        password = sr.Get_Shared_Variables(
            "device_password"
        )  # Read device password from shared variables
        # Unlock phone

        CommonUtil.ExecLog(sModuleInfo, "Attempting to unlock using adb", 1)
        subprocess.check_output(
            "adb %s shell svc power stayon usb" % (serial_with_id),
            shell=True,
            encoding="utf-8",
        )  # Wakeup device
        time.sleep(0.5)
        subprocess.check_output(
            "adb %s shell input keyevent 82" % (serial_with_id),
            shell=True,
            encoding="utf-8",
        )  # Wakeup device
        time.sleep(0.5)
        subprocess.check_output(
            "adb %s shell input keyevent 82" % (serial_with_id),
            shell=True,
            encoding="utf-8",
        )  # Wakeup device
        time.sleep(0.5)
        CommonUtil.ExecLog(
            sModuleInfo, "Serial number of the device used - %s" % serial_with_id, 1
        )
        subprocess.check_output(
            "adb %s shell input text %s" % (serial_with_id, password),
            shell=True,
            encoding="utf-8",
        )  # Enter password
        time.sleep(0.5)
        subprocess.check_output(
            "adb %s shell input keyevent KEYCODE_ENTER" % serial_with_id,
            shell=True,
            encoding="utf-8",
        )  # Press ENTER key
        time.sleep(2)  # Give time for foreground to switch and unlock to complete

        # Unlock phone

        lock_status = check_if_device_is_unlocked(serial)
        if lock_status == True:
            CommonUtil.ExecLog(sModuleInfo, "Successfully unlocked your device", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "We could not unlock using adb, we will try with uiautomator",
                1,
            )
            Enter_Password_UIAutomator(password, serial)

            lock_status = check_if_device_is_unlocked(serial)
            if lock_status == True:
                CommonUtil.ExecLog(sModuleInfo, "Successfully unlocked your device", 1)
                return "passed"

            CommonUtil.ExecLog(sModuleInfo, "We could not unlock your device", 3)
            return "zeuz_failed"

    except Exception:
        errMsg = "Unable to unlock device"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Enter_Password_UIAutomator(password, serial=""):
    """ This function can evolve a lot more. For time being we are just looking for button with text and clicking for UNLOCKING only"""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:

        # click buttons
        if serial != "":  # Prepare serial number with command line switch
            from uiautomator import (
                Device,
            )  # putting it here for now as this module was missing before.  We can move it at the top after some time

            d = Device(serial)
            serial_with_id = "-s %s" % serial
        else:
            from uiautomator import device as d

            serial_with_id = ""

        button_list = list(password)

        subprocess.check_output(
            "adb %s shell input keyevent 82" % (serial_with_id),
            shell=True,
            encoding="utf-8",
        )  # Wakeup device
        time.sleep(0.5)
        subprocess.check_output(
            "adb %s shell input keyevent 82" % (serial_with_id),
            shell=True,
            encoding="utf-8",
        )  # Get to Unlock window
        time.sleep(0.5)

        for each_button in button_list:

            d(text=each_button).click()

        subprocess.check_output(
            "adb %s shell input keyevent KEYCODE_ENTER" % serial_with_id,
            shell=True,
            encoding="utf-8",
        )  # Press ENTER key.  Note all phones do not require
        CommonUtil.ExecLog(sModuleInfo, "Successfully entered your password", 1)
        return "passed"

    except Exception:
        errMsg = "Unable to unlock device"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def unlock_android_app(serial=""):
    """ Attempt to enter password for locked app.  It is up to the user to put proper logic to figure out if the app is password protected.  
    We will assume user have already checked that"""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        # Get password
        if (
            sr.Test_Shared_Variables("device_password") == False
        ):  # Make sure user stored password in shared variables
            CommonUtil.ExecLog(
                sModuleInfo, "Can't unlock phone - no password specified.", 3
            )
            return "zeuz_failed"
        password = sr.Get_Shared_Variables(
            "device_password"
        )  # Read device password from shared variables
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        # Unlock app
        subprocess.check_output(
            "adb %s shell input keyevent 82" % (serial), shell=True, encoding="utf-8"
        )  # Wakeup device
        time.sleep(1)
        CommonUtil.ExecLog(
            sModuleInfo, "Serial number of the device used - %s" % serial, 1
        )
        subprocess.check_output(
            "adb %s shell input text %s" % (serial, password),
            shell=True,
            encoding="utf-8",
        )  # Enter password
        time.sleep(0.5)
        subprocess.check_output(
            "adb %s shell input keyevent KEYCODE_ENTER" % serial,
            shell=True,
            encoding="utf-8",
        )  # Press ENTER key
        time.sleep(2)  # Give time for foreground to switch and unlock to complete
    except Exception:
        errMsg = "Unable to unlock app"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def check_if_device_is_unlocked(serial=""):
    # if device is locked, current focused window always shows "StatusBar" only
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch

        subprocess.check_output(
            "adb %s shell input keyevent 82" % (serial), shell=True, encoding="utf-8"
        )  # Wakeup device and bring it unlock window
        time.sleep(1)
        output = subprocess.check_output(
            "adb %s exec-out uiautomator dump /dev/tty" % serial,
            shell=True,
            encoding="utf-8",
        )

        if "EMERGENCY" in output or "emergency_call_button" in output:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Device is currently locked. We will proceed with unlock ",
                2,
            )
            return False
        else:
            CommonUtil.ExecLog(sModuleInfo, "Device is currently unlocked ", 1)
            return True
    except Exception:
        errMsg = "Unable to determine if device is locked or not"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


# @logger
# def detect_foreground_android(serial=''):
#     ''' Return whatever has the foreground '''
#
#     sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
#     try:
#         if serial != '': serial = '-s %s' % serial  # Prepare serial number with command line switch
#         output = subprocess.check_output("adb %s shell dumpsys window windows" % serial,
#                                          shell=True, encoding='utf-8')  # Get list of windows
#         p = re.compile('CurrentFocus=.*?\s+([\w\.]+)/([\w\.]+)',
#                        re.MULTILINE)  # Find CurrentFocus line, and return package/activity
#         m = p.search(output)  # Perform regex
#         return str(m.group(1))  # Return package/activity
#     except Exception:
#         errMsg = "Error detecting foreground application"
#         return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def swipe_android(x_start, y_start, x_end, y_end, duration=1000, serial=""):
    """ Sends a swipe gesture to a device """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        CommonUtil.ExecLog(
            sModuleInfo,
            "Sending swipe gesture to %d %d %d %d %d ms"
            % (x_start, y_start, x_end, y_end, duration),
            0,
        )
        subprocess.check_output(
            "adb %s shell input touchscreen swipe %d %d %d %d %d"
            % (serial, x_start, y_start, x_end, y_end, duration),
            shell=True,
            encoding="utf-8",
        )  # Send swipe gesture
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error while performing swipe gesture"
        )


@logger
def reset_android(serial=""):
    """ Resets the specified device, or the only device connected """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        CommonUtil.ExecLog(sModuleInfo, "Resetting device %s" % serial, 0)
        if serial != "":
            serial = (
                "-s %s" % serial
            )  # Prepend the command line switch to add the serial number
        subprocess.check_output(
            "adb %s reboot" % serial, shell=True, encoding="utf-8"
        )  # Send reset
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error while resetting device"
        )


@logger
def reset_all_android():
    """ Resets all connected devices """

    try:
        # Get list of all connected devices
        devices = get_devices()

        # For each device, reset it
        for serial in devices:
            reset_android(str(serial.split(" ")[0]).strip())  # Send reset
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error while resetting devices"
        )


@logger
def execute_program(package_name, serial=""):
    """ Executes an Android program """

    try:
        if serial != "":
            serial = "-s %s" % serial  # Prepare serial number with command line switch
        cmd = "adb %s shell monkey -p %s -c android.intent.category.LAUNCHER 1" % (
            serial,
            package_name,
        )
        subprocess.check_output(cmd, shell=True, encoding="utf-8")
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error executing Android program"
        )
