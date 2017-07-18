# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

'''
    :Function: iMobile Device command line options to get the IOS devices info connected via usb/wi-fi
    :Author: Lucas Donkers
    :Date: June, 2017
'''
import subprocess, inspect, sys
from Framework.Utilities import CommonUtil

imobiledevice_path = '/usr/local/bin/' # Install location of iMobileDevice programs

def run_program(cmd):
    ''' Executes a command line program '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        output = subprocess.check_output(imobiledevice_path + cmd, shell=True) # Execute command line program, and return STDOUT
        return output
    except: # If command produced a non-zero return code, return failed
        return CommonUtil.Exception_Handler(sys.exc_info())
    
def get_list_udid():
    ''' Returns a list of UDID's for connected IOS devices '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Started", 0)
    try:
        cmd = 'idevice_id -l'
        output = run_program(cmd)
        if output == None: return ''
        output = output.strip().split("\n")
        return output
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def get_list_device_names(UDID = ''):
    ''' Returns a list of device names '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Started", 0)
    try:
        cmd = 'idevicename'
        if UDID != '': cmd + ' -u' + UDID # User specified id, so append that to the command
        output = run_program(cmd)
        if output == None: return ''
        output = output.strip().split("\n")
        return output
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def get_device_info(UDID = ''):
    ''' Returns list of device information '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Started", 0)
    try:
        cmd = 'ideviceinfo'
        if UDID != '': cmd + ' -u' + UDID # User specified id, so append that to the command
        output = run_program(cmd)
        if output == None: return ''
        output = output.strip().split("\n")
        return output
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def get_list_installed_packages(UDID = ''):
    ''' Returns a list of all installed packages '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Started", 0)
    try:
        cmd = 'ideviceinstaller -l'
        if UDID != '': cmd + ' -u' + UDID # User specified id, so append that to the command
        output = run_program(cmd)
        if output == None: return ''
        output = output.strip().split("\n")
        for i in range(len(output)): # For each package
            output[i] = output[i].split(' ')[0] # Get only the package name, and remove the proper name
        return output
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def take_screenshot(UDID = ''):
    ''' Captures a screenshot of the device, and returns the filename '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Started", 0)
    try:
        cmd = 'idevicescreenshot'
        if UDID != '': cmd + ' -u' + UDID # User specified id, so append that to the command
        output = run_program(cmd)
        if output == None: return ''
        output = output.split(' ')[3] # Get just the filename
        return output
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def ios_reboot(UDID = ''):
    ''' Reboots the device '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Started", 0)
    try:
        cmd = 'idevicediagnostics restart'
        if UDID != '': cmd + ' -u' + UDID # User specified id, so append that to the command
        output = run_program(cmd)
        if output == None: return ''
        output = output.split(' ')[3] # Get just the filename
        return output
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def ios_shutdown(UDID = ''):
    ''' Turns off the device '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Started", 0)
    try:
        cmd = 'idevicediagnostics shutdown'
        if UDID != '': cmd + ' -u' + UDID # User specified id, so append that to the command
        output = run_program(cmd)
        if output == None: return ''
        output = output.split(' ')[3] # Get just the filename
        return output
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def get_ios_imei(UDID = ''):
    ''' Reads the device IMEI '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Started", 0)
    
    try:
        output = get_device_info(UDID) # Get device info in list format
        tmp = ''
        for line in output:
            if 'imei' in line.lower():
                tmp = line
        output = tmp[1].strip()

        if len(output) != 14 and len(output) != 15:
            CommonUtil.ExecLog(sModuleInfo, "Could not read the IMEI from the device", 3)
            return 'failed'
        
        CommonUtil.ExecLog(sModuleInfo, "%s" % output, 0)
        return output
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

