# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

#Android Debug Bridge (ADB) options to get the android devices info connected via usb/wi-fi
__author__='minar'
import subprocess, inspect, os, sys, re
from Framework.Utilities import CommonUtil

def start_adb_server():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb start server", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Starting adb server", 1)
        return output

    except Exception:
        errMsg = "Unable to start adb server"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def kill_adb_server():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb kill-server", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Killing adb server", 1)
        return output

    except Exception:
        errMsg = "Unable to kill adb server"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


def get_android_version():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell getprop ro.build.version.release", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output

    except Exception:
        errMsg = "Unable to get android version"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_device_model():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell getprop ro.product.model", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output

    except Exception:
        errMsg = "Unable to get device model"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_device_name():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell getprop ro.product.name", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output

    except Exception:
        errMsg = "Unableto get device name"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_device_manufacturer():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell getprop ro.product.manufacturer", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output

    except Exception:
        errMsg = "Unable to get device manufacturer."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_device_imei_info():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell dumpsys iphonesubinfo", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output

    except Exception:
        errMsg = "Unable to get device IMEI info"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_device_summary():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb devices -l", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output

    except Exception:
        errMsg = "Unable to get device summary"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_device_complete_info():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb devices -l", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output

    except Exception:
        errMsg = "Unable to get device complete info"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_devices():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb devices", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output

    except Exception:
        errMsg = "Unable to get devices"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_android_sdk():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell getprop ro.build.version.sdk", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output

    except Exception:
        errMsg = "Unable to get android sdk"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def install_app(apk_path):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb install %s"%apk_path, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Installed app located %s"%apk_path, 1)
        return output

    except Exception:
        errMsg = "Unable to install app located %s"%apk_path
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def connect_device_via_wifi(device_ip):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb tcpip 5555", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Target device set to listen for a TCP/IP connection on port 5555.", 1)
        output = subprocess.check_output("adb connect %s"%device_ip, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Conncted to device via wifi", 1)
        output = subprocess.check_output("adb devices", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output

    except Exception:
        errMsg = "Unable to connect device via wifi"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def take_screenshot(image_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        #output = subprocess.check_output("adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > %s/%s.png"%(folder_path,image_name), shell=True)
        os.system("adb shell screencap -p /sdcard/%s.png"%image_name)
        os.system("adb pull /sdcard/%s.png"%image_name)
        CommonUtil.ExecLog(sModuleInfo, "Screenshot taken as %s.png"%image_name, 1)
        return "Screen shot taken"

    except Exception:
        errMsg = "Unable to take screenshot"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def record_screen(folder_path,video_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        os.system("adb shell screenrecord /sdcard/%s.mp4"%(video_name), shell=True)
        os.system("adb pull /sdcard/%s.mp4"%video_name)
        CommonUtil.ExecLog(sModuleInfo, "Screen recorded as %s.mp4"%video_name, 1)
        return "Screen recorded"

    except Exception:
        errMsg = "Unable to record"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_device_battery_info():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell dumpsys battery", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output

    except Exception:
        errMsg = "Unable to get device battery info"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
       
def get_device_wifi_info():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell dumpsys wifi", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output

    except Exception:
        errMsg = "Unable to get device wifi info"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def get_device_cpu_info():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell dumpsys cpuinfo", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output

    except Exception:
        errMsg = "Unable to get device CPU info"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def get_package_name():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell pm list packages", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Getting Packages Name of Installed Applications", 1)
        return output

    except Exception:
        errMsg = "Unable to get Packages Name"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
def wake_android():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell wm size", shell=True) # Need size for swipe calculation
        m = re.search('(\d+)x(\d+)', output) # Find w and h using regular expression
        w, h = (m.group(1), m.group(2)) # Save w and h
        spos = int(int(h) * 0.7) # Calculate 70% of height as starting position
        epos = int(int(h) * 0.1) # Calculate 10% of height as ending position
        centre = int(int(w) / 2) # Calculate centre of screen horizontally
        output = subprocess.check_output("adb shell input keyevent KEYCODE_WAKEUP", shell=True) # Send wakeup command (puts us on lock screen)
        output = subprocess.check_output("adb shell input touchscreen swipe %d %d %d %d" % (centre, spos, centre, epos), shell=True) # Send vertical swipe command (takes us to home screen)
        CommonUtil.ExecLog(sModuleInfo, "Waking device", 1)
        return output

    except Exception:
        errMsg = "Unable to wake device"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
