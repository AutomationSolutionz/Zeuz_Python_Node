#Android Debug Bridge (ADB) options to get the android devices info connected via usb/wi-fi
__author__='minar'
import subprocess, inspect, os
from Utilities import CommonUtil

def start_adb_server():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb start server", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Starting adb server", 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to start adb server", 3)
        return "ADB shell command failed"

def kill_adb_server():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb kill-server", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Killing adb server", 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to kill adb server", 3)
        return "ADB shell command failed"


def get_android_version():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell getprop ro.build.version.release", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get android version", 3)
        return "ADB shell command failed"
    
def get_device_model():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell getprop ro.product.model", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get device model", 3)
        return "ADB shell command failed"
    
def get_device_name():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell getprop ro.product.name", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get device name", 3)
        return "ADB shell command failed"
    
def get_device_manufacturer():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell getprop ro.product.manufacturer", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get device manufacturer", 3)
        return "ADB shell command failed"
    
def get_device_imei_info():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell dumpsys iphonesubinfo", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get device IMEI info", 3)
        return "ADB shell command failed"
    
def get_device_summary():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb devices -l", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get device summary", 3)
        return "ADB shell command failed"
    
def get_device_complete_info():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb devices -l", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get device complete info", 3)
        return "ADB shell command failed"

def get_devices():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb devices", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get devices", 3)
        return "ADB shell command failed"

def get_android_sdk():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell getprop ro.build.version.sdk", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get android sdk", 3)
        return "ADB shell command failed"
    
def install_app(apk_path):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb install %s"%apk_path, shell=True)
        CommonUtil.ExecLog(sModuleInfo, "Installed app located %s"%apk_path, 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to install app located %s"%apk_path, 3)
        return "ADB shell command failed"

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
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to connect device via wifi", 3)
        return "ADB shell command failed"

def take_screenshot(image_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        #output = subprocess.check_output("adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > %s/%s.png"%(folder_path,image_name), shell=True)
        os.system("adb shell screencap -p /sdcard/%s.png"%image_name)
        os.system("adb pull /sdcard/%s.png"%image_name)
        CommonUtil.ExecLog(sModuleInfo, "Screenshot taken as %s.png"%image_name, 1)
        return "Screen shot taken"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to take screenshot", 3)
        return "ADB shell command failed"

def record_screen(folder_path,video_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        os.system("adb shell screenrecord /sdcard/%s.mp4"%(video_name), shell=True)
        os.system("adb pull /sdcard/%s.mp4"%video_name)
        CommonUtil.ExecLog(sModuleInfo, "Screen recorded as %s.mp4"%video_name, 1)
        return "Screen recorded"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to record", 3)
        return "ADB shell command failed"

def get_device_battery_info():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell dumpsys battery", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get device battery info", 3)
        return "ADB shell command failed"
       
def get_device_wifi_info():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell dumpsys wifi", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get device wifi info", 3)
        return "ADB shell command failed"
    
def get_device_cpu_info():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output("adb shell dumpsys cpuinfo", shell=True)
        CommonUtil.ExecLog(sModuleInfo, "%s"%output, 1)
        return output
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Unable to get device CPU info", 3)
        return "ADB shell command failed"
