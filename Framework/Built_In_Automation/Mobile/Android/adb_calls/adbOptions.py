# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

#Android Debug Bridge (ADB) options to get the android devices info connected via usb/wi-fi
__author__='minar'
import subprocess, inspect, os, sys, re, math, time
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr

def start_adb_server():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb start server", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Starting adb server", 0)
        return output

    except Exception:
        errMsg = "Unable to start adb server"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def kill_adb_server():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb kill-server", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Killing adb server", 0)
        return output

    except Exception:
        errMsg = "Unable to kill adb server"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def get_android_version(serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output = subprocess.check_output("adb %s shell getprop ro.build.version.release" % serial, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 0)
        return output.strip()

    except Exception:
        errMsg = "Unable to get android version"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_device_model(serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output = subprocess.check_output("adb %s shell getprop ro.product.model" % serial, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 0)
        return output.strip()

    except Exception:
        errMsg = "Unable to get device model"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_device_name(serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output = subprocess.check_output("adb %s shell getprop ro.product.name" % serial, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 0)
        return output

    except Exception:
        errMsg = "Unableto get device name"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_device_serial_no(serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output = subprocess.check_output("adb %s get-serialno" % serial, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 0)
        return output.strip()

    except Exception:
        errMsg = "Unableto get device serial no"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_device_storage(serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output = subprocess.check_output("adb %s shell df /data" % serial, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        storageList = ' '.join(output.split())
        storageList = storageList.split(" ")
        storage = storageList[6]
        storage = storage.replace('G','')
        storage = float(storage)
        final_storage = 0
        exp = 2
        while True:
            gb = math.pow(2,exp)
            if storage < gb:
                final_storage = gb
                break
            exp+=1
        final_storage = int(final_storage)
        return final_storage

    except Exception:
        errMsg = "Unableto get device storage"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_device_manufacturer(serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output = subprocess.check_output("adb %s shell getprop ro.product.manufacturer" % serial, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 0)
        return output

    except Exception:
        errMsg = "Unable to get device manufacturer."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_device_imei_info(serial = ''):
    ''' Returns the device's IMEI '''
    # Output: IMEI as a string
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output=subprocess.check_output('adb %s shell dumpsys iphonesubinfo' % serial, shell = True)
        # Use dumpsys (Below Android v6)
        if output != '':
            output = output.split("\n")[2]
            output = output.split(' ')[5].strip()
            
        # Use service call (Above Android v6)
        else:
            output=subprocess.check_output('adb shell service call iphonesubinfo 1' % serial, shell = True)
            output=output.split(' ') # Contains hex output, and characters that need to be removed
            tmp = ''
            for val in output:
                if "'" in val: tmp += val # Look for values that have a single quote, they are the ones with a portion of the IMEI
        
            chars = "\r\n.')"
            output = tmp.translate(None, chars) # Remove characters we don't want

        if len(output) != 14 and len(output) != 15:
            CommonUtil.ExecLog(sModuleInfo, "Could not read the IMEI from the device", 3)
            return 'failed'
        
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output

    except Exception:
        errMsg = "Error while trying to read IMEI from the device"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_device_summary():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb devices -l", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 0)
        return output

    except Exception:
        errMsg = "Unable to get device summary"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_device_complete_info():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb devices -l", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 0)
        return output

    except Exception:
        errMsg = "Unable to get device complete info"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_devices():
    ''' Retrieves a list of connected devices in the format of "SERIAL_NO STATE" and returns as a list '''
    # State may be "device" if connected and we can talk to it, or "unauthorized" if we can't talk to it
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        # Get list of connected devices
        output = subprocess.check_output("adb devices", shell=True)
        
        # Cleanup data
        output = output.replace("\r", '')
        output = output.replace("\t", ' ')
        output = output.split("\n")
        output.pop(0) # Remove "list of..." string
        output = [line for line in output if line != '']
        
        # Return as list 
        CommonUtil.ExecLog(sModuleInfo, "Connected devices: %s" % str(output), 0)
        return output

    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get devices", 3)
        return []

def is_android_connected(serial = ''):
    ''' Return True/False if at least one device is connected '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    
    if serial != '': serial = 'device' # If none specified, this is the generic keyword to look for
    
    devices = get_devices()
    
    if devices != []:
        for device in devices:
            if serial in device:
                CommonUtil.ExecLog(sModuleInfo, "Android connected", 0)
                return True
        CommonUtil.ExecLog(sModuleInfo, "Android connected, but not authorized. Ensure USB debugging is enabled in developer options, and that you authorized this computer to connect to it.", 2)
        return False
    else:
        CommonUtil.ExecLog(sModuleInfo, "No Android connected", 0)
        return False
    
def get_android_sdk(serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output = subprocess.check_output("adb %s shell getprop ro.build.version.sdk" % serial, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 0)
        return output

    except Exception:
        errMsg = "Unable to get android sdk"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def install_app(apk_path, serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output = subprocess.check_output("adb %s install %s" % (serial, apk_path), shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Installed app located %s"%apk_path, 0)
        return output

    except Exception:
        errMsg = "Unable to install app located %s"%apk_path
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def connect_device_via_wifi(device_ip):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb tcpip 5555", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Target device set to listen for a TCP/IP connection on port 5555.", 0)
        output = subprocess.check_output("adb connect %s"%device_ip, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Conncted to device via wifi", 0)
        output = subprocess.check_output("adb devices", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 0)
        return output

    except Exception:
        errMsg = "Unable to connect device via wifi"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def take_screenshot(image_name, serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        #output = subprocess.check_output("adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > %s/%s.png"%(folder_path,image_name), shell=True)
        os.system("adb %s shell screencap -p /sdcard/%s.png" % (serial, image_name))
        os.system("adb %s pull /sdcard/%s.png" % (serial, image_name))
        CommonUtil.ExecLog(sModuleInfo, "Screenshot taken as %s.png"%image_name, 0)
        return "Screen shot taken"

    except Exception:
        errMsg = "Unable to take screenshot"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def record_screen(folder_path,video_name, serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        os.system("adb %s shell screenrecord /sdcard/%s.mp4" % (serial, video_name), shell=True)
        os.system("adb %s pull /sdcard/%s.mp4" % (serial, video_name))
        CommonUtil.ExecLog(sModuleInfo, "Screen recorded as %s.mp4"%video_name, 0)
        return "Screen recorded"

    except Exception:
        errMsg = "Unable to record"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_device_battery_info(serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output = subprocess.check_output("adb %s shell dumpsys battery" % serial, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 0)
        return output

    except Exception:
        errMsg = "Unable to get device battery info"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
       
def get_device_wifi_info(serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output = subprocess.check_output("adb %s shell dumpsys wifi" % serial, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 0)
        return output

    except Exception:
        errMsg = "Unable to get device wifi info"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_device_cpu_info(serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output = subprocess.check_output("adb %s shell dumpsys cpuinfo" % serial, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 0)
        return output

    except Exception:
        errMsg = "Unable to get device CPU info"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_package_name(serial = ''):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output = subprocess.check_output("adb %s shell pm list packages" % serial, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Getting Packages Name of Installed Applications", 0)
        return output

    except Exception:
        errMsg = "Unable to get Packages Name"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def wake_android(serial = ''):
    ''' Sends the wakeup keypress and a swipe up gesture to try to unlock the device and get it to a usable state for automation '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        # Get screen size, and calculate swipe gesture to get to home screen
        output = subprocess.check_output("adb %s shell wm size" % serial, shell=True) # Need size for swipe calculation
        m = re.search('(\d+)x(\d+)', output) # Find w and h using regular expression
        w, h = (m.group(1), m.group(2)) # Save w and h
        spos = int(int(h) * 0.7) # Calculate 70% of height as starting position
        epos = int(int(h) * 0.1) # Calculate 10% of height as ending position
        centre = int(int(w) / 2) # Calculate centre of screen horizontally
        
        # Wake device and send swipe gesture
        subprocess.check_output("adb %s shell input keyevent KEYCODE_WAKEUP" % serial, shell=True) # Send wakeup command (puts us on lock screen)
        subprocess.check_output("adb %s shell input touchscreen swipe %d %d %d %d" % (serial, centre, spos, centre, epos), shell=True) # Send vertical swipe command (takes us to home screen)
        CommonUtil.ExecLog(sModuleInfo, "Waking device", 0)
        
        # If there is a password, handle it
        output = detect_foreground_android(serial.replace('-s ', '')) # Check if we are on the password screen
        if output == 'Bouncer':
            output = unlock_android(serial.replace('-s ', ''))
            if output == 'failed':
                return 'failed'
        
        return 'passed'

    except Exception:
        errMsg = "Unable to wake device"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def unlock_android(serial = ''):
    ''' Attempt to enter password for locked phone '''
    # Caveat 1: Only works if device has PIN or PASSWORD, not if they use a pattern, or pattern as a fingerprint backup
    # Caveat 2: Only works if the user connects USB and unlocks the phone. Then, if the phone is locked, we still have an ADB connection, and can work with it.
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        # Get password
        if sr.Test_Shared_Variables('device_password') == False: # Make sure user stored password in shared variables
            CommonUtil.ExecLog(sModuleInfo, "Can't unlock phone - no password specified. Please call the 'device password' action before attempting to unlock", 3)
            return 'failed'
        password = sr.Get_Shared_Variables('device_password') # Read device password from shared variables
        
        # Unlock phone
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        subprocess.check_output("adb %s shell input text %s" % (serial, password), shell=True) # Enter password
        subprocess.check_output("adb %s shell input keyevent KEYCODE_ENTER" % serial, shell=True) # Press ENTER key
        time.sleep(3) # Give time for foreground to switch and unlock to complete

        # Verify success
        output = detect_foreground_android(serial.replace('-s ', '')) # Check if we are still on the password screen
        if output == 'Bouncer': # Password didn't work
            CommonUtil.ExecLog(sModuleInfo, "Unlocking failed. Password may be invalid - %s" % password, 3)
            return 'failed'
        else: # Hopefully, we unlocked and are on the last run program or home screen
            return 'passed'
        
    except Exception:
        errMsg = "Unable to unlock device"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def detect_foreground_android(serial = ''):
    ''' Return whatever has the foreground '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        output = subprocess.check_output("adb %s shell dumpsys window windows" % serial, shell=True) # Get list of windows
        p = re.compile('CurrentFocus=.*?\s+([\w\.]+)/([\w\.]+)', re.MULTILINE) # Find CurrentFocus line, and return package/activity
        m = p.search(output) # Perform regex
        return str(m.group(1)) # Return package/activity
    except Exception:
        errMsg = "Error detecting foreground application"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def swipe_android(x_start, y_start, x_end, y_end, serial = ''):
    ''' Sends a swipe gesture to a device '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if serial != '': serial = '-s %s' % serial # Prepare serial number with command line switch
        CommonUtil.ExecLog(sModuleInfo, "Sending swipe gesture to %d %d %d %d" % (x_start, y_start, x_end, y_end), 0)
        subprocess.check_output("adb %s shell input touchscreen swipe %d %d %d %d 1000" % (serial, x_start, y_start, x_end, y_end), shell=True) # Send swipe gesture
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error while performing swipe gesture")

def reset_android(serial = ''):
    ''' Resets the specified device, or the only device connected '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Resetting device %s" % serial, 0)
        if serial != '': serial = '-s %s' % serial # Prepend the command line switch to add the serial number
        subprocess.check_output("adb %s reboot" % serial, shell=True) # Send reset
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error while performing swipe gesture")

def reset_all_android():
    ''' Resets all connected devices '''
    
    try:
        # Get list of all connected devices
        devices = get_devices()
        
        # For each device, reset it
        for serial in devices:
            reset_android(str(serial.split(' ')[0]).strip()) # Send reset
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error while performing swipe gesture")

