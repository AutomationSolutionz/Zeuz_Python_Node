#Android Debug Bridge (ADB) options to get the android devices info connected via usb/wi-fi

import subprocess, inspect
from AutomationFW.CoreFrameWork import CommonUtil

#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
local_run = True
#local_run = False

def start_adb_server():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb start server", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Starting adb server", 1, local_run)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to start adb server", 3, local_run)
        return "ADB shell command failed"

def kill_adb_server():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb kill-server", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Killing adb server", 1, local_run)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to kill adb server", 3, local_run)
        return "ADB shell command failed"


def get_android_version():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell getprop ro.build.version.release", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1, local_run)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get android version", 3, local_run)
        return "ADB shell command failed"
    
def get_device_model():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell getprop ro.product.model", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1, local_run)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get device model/name", 3, local_run)
        return "ADB shell command failed"
    
def get_device_imei_info():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell dumpsys iphonesubinfo", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1, local_run)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get device IMEI info", 3, local_run)
        return "ADB shell command failed"

def get_devices():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb devices", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1, local_run)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get devices", 3, local_run)
        return "ADB shell command failed"

def get_android_sdk():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell getprop ro.build.version.sdk", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1, local_run)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get android sdk", 3, local_run)
        return "ADB shell command failed"
    
def install_app(apk_path):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb install %s"%apk_path, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Installed app located %s"%apk_path, 1, local_run)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to install app located %s"%apk_path, 3, local_run)
        return "ADB shell command failed"

def connect_device_via_wifi(device_ip):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb tcpip 5555", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Target device set to listen for a TCP/IP connection on port 5555.", 1, local_run)
        output = subprocess.check_output("adb connect %s"%device_ip, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Conncted to device via wifi", 1, local_run)
        output = subprocess.check_output("adb devices", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1, local_run)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to connect device via wifi", 3, local_run)
        return "ADB shell command failed"

def take_screenshot(image_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        #output = subprocess.check_output("adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > %s/%s.png"%(folder_path,image_name), shell=True)
        os.system("adb shell screencap -p /sdcard/%s.png"%image_name)
        os.system("adb pull /sdcard/%s.png"%image_name)
        CommonUtil.ExecLog(sModuleInfo, "Screenshot taken as %s.png"%image_name, 1, local_run)
        return "Screen shot taken"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to take screenshot", 3, local_run)
        return "ADB shell command failed"

def record_screen(folder_path,video_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        os.system("adb shell screenrecord /sdcard/%s.mp4"%(video_name), shell=True)
        os.system("adb pull /sdcard/%s.mp4"%image_name)
        CommonUtil.ExecLog(sModuleInfo, "Screen recorded as %s.mp4"%video_name, 1, local_run)
        return "Screen recorded"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to record", 3, local_run)
        return "ADB shell command failed"

def get_imei_id():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell dumpsys iphonesubinfo", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Got device IMEI id", 1, local_run)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get device id", 3, local_run)
        return "ADB shell command failed"