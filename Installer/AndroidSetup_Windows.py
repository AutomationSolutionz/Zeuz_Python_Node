# Copyright 2017, Automation Solutionz

import subprocess
from subprocess import PIPE, Popen
import shutil
import os, os.path, win32api, win32con, win32gui
from os.path import expanduser
import sys
import getpass
import time
from clint.textui import progress
import platform
import requests
import psutil
import inspect
import ctypes
from ctypes.wintypes import HWND, UINT, WPARAM, LPARAM, LPVOID  # this belongs to registry editor

# from builtins import True
LRESULT = LPARAM  # synonymous.  This belongs to registry
import winreg as winreg

# Import local modules
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))  # Set the path, so the can find the modules
import webbrowser
import winshell
from win32com.client import Dispatch

# since nothing is able to refresh the command line calling directly, we will define the npm full path
global npm_path
global PATH_VAR
global appium_path
global Android_Home_Dir
global Android_Tools_Dir
global Android_Tools_bin_Dir
global Android_Build_Tools_Dir
global Downloaded_Path
global Temp_Tools_Dir
global current_script_path
global installer_jdk_file_part_1
global installer_jdk_file_part_2
global installer_jdk_file_part_3
global installer_jdk_file_name
global install_node_file

npm_path = os.environ["ProgramW6432"] + os.sep + "nodejs"
appium_path = os.getenv('APPDATA') + os.sep + "npm" + os.sep + "appium"
# Android_Home_Dir  =  expanduser("~")+os.sep + "AppData" + os.sep +  "Local" + os.sep + "Android" + os.sep + "Sdk"

Android_Home_Dir = (expanduser("~") + os.sep + "AppData" + os.sep + "Local" + os.sep + "Android" + os.sep + "Sdk")
Android_Tools_bin_Dir = Android_Home_Dir + os.sep + "tools" + os.sep + "bin"
Android_Tools_Dir = Android_Home_Dir + os.sep + "tools"
Android_Platform_Tools_Dir = Android_Home_Dir + os.sep + "platform-tools"
# - not needed anymore with new android Android_Build_Tools_Dir = Android_Home_Dir + os.sep + "build-tools"
Downloaded_Path = expanduser("~") + os.sep + "Downloads"
Temp_Tools_Dir = expanduser("~") + os.sep + "Downloads" + os.sep + "tools"
logfile = "TestNode_Android_Logs.log"

current_script_path = '%s' % (sys.path[0])
# Updated Oct 26, 2019
installer_jdk_file_part_1 = "jdk-8u231-windows-x64.sfx.part1.exe"
installer_jdk_file_part_2 = "jdk-8u231-windows-x64.sfx.part2.rar"
installer_jdk_file_part_3 = "jdk-8u231-windows-x64.sfx.part3.rar"
installer_jdk_file_name = r"jdk-8u231-windows-x64.exe"
install_node_file = 'node-v14.17.1-x64.msi'


def Android_SDK_PATH(Android_Home_Dir):
    try:
        # set android home path

        print("Setting ANDROID_HOME to Environmental variable\n")
        # Android_Home_Dir = (expanduser("~")+os.sep + "AppData" + os.sep +  "Local"+os.sep + "Android" + os.sep +"Sdk")
        Android_Tools_bin_Dir = Android_Home_Dir + os.sep + "tools" + os.sep + "bin"
        Android_Tools_Dir = Android_Home_Dir + os.sep + "tools"
        Android_Platform_Tools_Dir = Android_Home_Dir + os.sep + "platform-tools"

        Add_To_Path("ANDROID_HOME", Android_Home_Dir)
        # set tools to path

        print("Setting tools dir to PATH\n")
        Add_To_Path("PATH", Android_Tools_Dir)
        # set tools bin to path

        print("Setting tools bin dir to PATH\n")
        Add_To_Path("PATH", Android_Tools_bin_Dir)
        # set platforms_tools

        print("Setting platform-tools dir to PATH\n")
        Add_To_Path("PATH", Android_Platform_Tools_Dir)

        # ANT_HOME
        # print("Setting ANT_HOME to Environmental variable\n")
        # ANT_HOME = Downloaded_Path + os.sep + 'apache-ant-1.10.7' + os.sep + 'bin'
        # Add_To_Path("ANT_HOME", ANT_HOME)
        # # M2_HOME
        #
        # print("Setting M2_HOME to Environmental variable\n")
        # M2_HOME = Downloaded_Path + os.sep + "apache-maven-3.6.2"
        # Add_To_Path("M2_HOME", M2_HOME)
        # # M2
        #
        # print("Setting maven to Environmental variable\n")
        # M2 = Downloaded_Path + os.sep + "apache-maven-3.6.2" + os.sep + "bin"
        # Add_To_Path("M2", M2)
        # # M2 to PATH
        #
        # print("Setting maven to PATH\n")
        # M2 = Downloaded_Path + os.sep + "apache-maven-3.6.2" + os.sep + "bin"
        # Add_To_Path("PATH", M2)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Get_Home_Dir():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmodulename(__file__)
    try:
        home_dir = expanduser("~")
        return home_dir
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Download_File(base_url, file_name, md5=False):
    try:
        print("Downloading from: %s\n" % (base_url + file_name))

        file_url = base_url + file_name
        download_path = Get_Home_Dir() + os.sep + 'Downloads' + os.sep + file_name
        '''
        some times files gets corrpt and we need to re-download
        if os.path.isfile(download_path):
            #print "already downloading... skipping download"
            print("already downloading... skipping download")
            return download_path
        '''
        r = requests.get(file_url, stream=True)
        path = download_path
        with open(path, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()
        f.close()
        print("Download completed")
        return download_path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        return False


def Unzip_All_folders_files(zip_file_location, destination_folder):
    try:

        from zipfile import ZipFile
        # Create a ZipFile Object and load sample.zip in it
        with ZipFile(zip_file_location, 'r') as zipObj:
            # Extract all the contents of zip file in different directory
            zipObj.extractall(destination_folder)
            print("\n Unzipped: %s Successfully in the folder: %s\n" % (zip_file_location, destination_folder))
            return True
        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        return False


def Get_Current_Logged_User():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmodulename(__file__)
    try:
        # works on all platoform
        current_user_name = getpass.getuser()
        return current_user_name
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Add_To_Path(PATH_NAME, value):
    try:
        print("Adding path: '%s' to windows system environment with value: %s\n" % (PATH_NAME, value))  # Print to terminal window, and log file
        result_path_check = Check_If_in_Path(PATH_NAME, value)
        if result_path_check == True:
            return True

        Update_Sys_Env_Variable(PATH_NAME, value)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Check_If_in_Path(PATH_NAME, value):
    print("Checking if %s is already in %s" % (value, PATH_NAME))
    try:
        try:
            # we will always set the path in run time just to be on the same side
            if PATH_NAME == "PATH":
                current_value = os.environ['PATH']
                path_list = current_value.split(";")
                if value not in path_list:
                    os.environ['PATH'] += ';' + value
            else:
                os.environ[PATH_NAME] = value
        except:
            pass
        reg_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
        try:
            system_environment_variables = winreg.QueryValueEx(reg_key, PATH_NAME)[0]
        except:
            print("Value = '%s' is not found.  We will add it." % value)
            return False
        if value in system_environment_variables:
            print("Value = '%s' already exists under %s" % (value, PATH_NAME))
            return True
        else:
            print("Value = '%s' is not found.  We will add it." % value)
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print("Environmental Variable provided '%s' does not exists" % (PATH_NAME))
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Update_Sys_Env_Variable(PATH_NAME, my_value):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_ALL_ACCESS)
        try:
            value, _ = winreg.QueryValueEx(key, PATH_NAME)
        except WindowsError as e:
            # in case the PATH variable is undefined
            print("Env Variable WindowsError Exception: {}".format(e))
            value = ''
        if PATH_NAME != "PATH":
            value = my_value
        else:
            # we always append PATH
            value_list = value.split(";")
            if my_value in value_list:
                print("Already there")
                return True
            else:
                value = value + ";" + my_value
        # write it back
        winreg.SetValueEx(key, PATH_NAME, 0, winreg.REG_EXPAND_SZ, value)
        winreg.CloseKey(key)

        # notify the system about the changes
        win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')
        # we will add python path again to be on the safe side
        try:
            if PATH_NAME == "PATH":
                current_value = os.environ['PATH']
                path_list = current_value.split(";")
                if my_value not in value_list:
                    os.environ['PATH'] += ';' + my_value
            else:
                os.environ[PATH_NAME] = my_value
        except:
            True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print("Environmental Variable provided '%s' does not exists" % (PATH_NAME))
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Auto_locate_Android_Studio():
    try:
        android_where_output_str = ""
        Android_where = r"where adb"
        android_where_output_raw = subprocess.run(Android_where, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        android_where_output_bytes = android_where_output_raw.stdout
        android_where_output_str = str(android_where_output_bytes, 'utf-8')
        if android_where_output_str != "":
            print("\nFound adb under: %s\n" % android_where_output_str)
            Android_Home_Dir = (android_where_output_str.split("platform-tools")[0].rstrip(os.sep))
            Android_SDK_PATH(Android_Home_Dir)
            return True
        elif os.path.exists(expanduser("~") + os.sep + "AppData" + os.sep + "Local" + os.sep + "Android" + os.sep + "Sdk") == True:
            print("\nFound Android under default path: %s " % (expanduser("~") + os.sep + "AppData" + os.sep + "Local" + os.sep + "Android" + os.sep + "Sdk"))
            Android_Home_Dir = (expanduser("~") + os.sep + "AppData" + os.sep + "Local" + os.sep + "Android" + os.sep + "Sdk")
            Android_SDK_PATH(Android_Home_Dir)
            return True
        else:
            print("\nZeuZ will download a light version of Android SDK for Appium to work in the default Android Studio location: %s\n" % (expanduser("~") + os.sep + "AppData" + os.sep + "Local" + os.sep + "Android"))
            zip_file_name = "Android.zip"
            base_url = "https://github.com/AutomationSolutionz/InstallerHelperFiles/raw/master/Windows/"
            destination_folder = (expanduser("~") + os.sep + "AppData" + os.sep + "Local")
            zip_downloaded_file = Download_File(base_url, zip_file_name, md5=False)
            if zip_downloaded_file == False:
                print("\n Unable to download Android SDK of ZeuZ Version\n")
                return False
            unzip_status = Unzip_All_folders_files(zip_downloaded_file, destination_folder)
            Android_Home_Dir = (expanduser("~") + os.sep + "AppData" + os.sep + "Local" + os.sep + "Android" + os.sep + "Sdk")
            Android_SDK_PATH(Android_Home_Dir)
            return unzip_status


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def detect_admin():
    # Windows only - Return True if program run as admin

    import subprocess
    if sys.platform == 'win32':
        command = 'net session >nul 2>&1'  # This command can only be run by admin
        try:
            output = subprocess.check_output(command, shell=True)  # Causes an exception if we can't run
        except:
            return False
    return True


def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True,
        encoding='utf8'
    )
    return process.communicate()[0]


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def Check_Pre_Req():
    admin_check = is_admin()
    if admin_check == False:
        print("")
        print("Unable to elevate current action to run as admin.\n")  # Print to terminal window, and log file
        return False
    else:
        print("Admin check pass\n")

    if os.name != 'nt':
        print("This installer must be run on Windows\n")  # Print to terminal window, and log file
        return False
    if sys.version_info[:2] != (3, 8):
        print("32bit Python v3.8 must be installed\n")  # Print to terminal window, and log file
        return False
    if platform.architecture()[0] != '32bit':
        print("32bit Python v3.8 must be installed\n")  # Print to terminal window, and log file
        return False
    # if 'setuptools' not in cmdline("easy_install --version"):
    #     print("'easy_install' is not installed or not in the PATH.\n",True) # Print to terminal window, and log file
    #     return False
    if 'pip' not in cmdline("pip --version"):
        print("pip is not installed, or not in your PATH variable.\n")  # Print to terminal window, and log file
        return False

    print("Pre-requirements verified successfully\n")

    return True


def Kill_Process(name):
    this_proc = os.getpid()
    for proc in psutil.process_iter():
        procd = proc.as_dict(attrs=['pid', 'name'])
        if name in str(procd['name']) and procd['pid'] != this_proc:
            proc.kill()


def Delete_File(file_path):
    try:
        print("Deleting file: %s\n" % file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            if os.path.exists(file_path) == False:
                print("\tDeleted successfully\n")
                return True
            else:
                print("\tWe could not delete the file\n")
                return False
        else:
            print("file does not exits")
            print("\tFile was not found\n")
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Delete_Folder(src_folder):
    try:
        print("Deleting folder: %s\n" % src_folder)
        if os.path.exists(src_folder) == False:
            print("Source folder does not exists")
            print("\tSource folder does not exists\n")
            return True
        if os.path.exists(src_folder) == True:
            print("Existing folder found.. will delete")
            print("\tExisting folder found.. will delete\n")
            shutil.rmtree(src_folder)
            if os.path.exists(src_folder) == True:
                print("\tWe tried to delete the folder but could not delete\n")
                return False
            else:
                print("\tFolder found and successfully deleted\n")
                return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Move_and_Overwrite_Folder(src_folder, des_folder):
    try:
        print("\tMoving from %s to %s\n" % (src_folder, des_folder))
        if os.path.exists(src_folder) == False:
            print("Source folder does not exists...Unable to copy")
            return False
        if os.path.exists(des_folder) == True:
            print("Existing folder found.. will delete")
            Delete_Folder(des_folder)

        print("moving folders..")
        print(shutil.move(src_folder, des_folder))
        return des_folder
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Copy_and_Overwrite_Folder(src_folder, des_folder):
    try:
        if os.path.exists(src_folder) == False:
            print("Source folder does not exists...Unable to copy")
            return False
        if os.path.exists(des_folder) == True:
            print("Existing folder found.. will delete")
            shutil.rmtree(des_folder)
        print("Copying folders.. from: %s to %s" % ((src_folder, des_folder)))
        print(shutil.copytree(src_folder, des_folder))
        return des_folder
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("Unable to copy and overwrite folder and its content")
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Install_JDK():
    '''
    This function will first check if you have java/JRE/JDK installed.  If you have, we are gonna skip installer.  If you
    don't have java installed or if you don't have java set in path, we will install a known latest version that we have in our repo.
    '''
    try:
        print("Validating if JDK is installed...\n")  # Print to terminal window, and log file
        base_url = "https://github.com/AutomationSolutionz/InstallerHelperFiles/raw/master/Windows/"
        check_JDK = Check_If_JDK_Installed()
        print(check_JDK)
        if check_JDK == False:
            print("JDK was not installed  We will download and install known stable version of JDK \n")  # Print to terminal window, and log file
            # Download 3 parts of installer
            print("part 1 of 3")
            print("Downloading JDK part 1 of 3 \n")
            java_installer_path_1 = Download_File(base_url, installer_jdk_file_part_1)
            print("part 2 of 3")
            print("Downloading JDK part 2 of 3 \n")
            java_installer_path_2 = Download_File(base_url, installer_jdk_file_part_2)
            print("part 3 of 3")
            print("Downloading JDK part 3 of 3 \n")
            java_installer_path_3 = Download_File(base_url, installer_jdk_file_part_3)

            # extracting file
            print("Please wait while we extracting files silently...\n")  # Print to terminal window, and log file
            silent_extract_command = "%s /s" % (Downloaded_Path + os.sep + installer_jdk_file_part_1)
            print("Extracting files silently with command '%s'" % silent_extract_command)
            os.system(silent_extract_command)
            print("JDK Extraction completed\n")
            print("Extracting completed")

            print("We are installing java silently, please wait...")

            jdk_exe_path = current_script_path + os.sep + installer_jdk_file_name
            silent_installer_command = "%s /s" % jdk_exe_path
            print("Installing JDK silently from command '%s'.\nThis will take some time...\n" % silent_installer_command)  # Print to terminal window, and log file

            os.system(silent_installer_command)
            # this will set all paths as well
            Check_If_JDK_Installed()
            print("Cleaning up temp JDK installer files...\n")  # Print to terminal window, and log file
            print("Cleaning up temp JDK installer files...")
            Delete_File(Downloaded_Path + os.sep + installer_jdk_file_part_1)
            Delete_File(Downloaded_Path + os.sep + installer_jdk_file_part_2)
            Delete_File(Downloaded_Path + os.sep + installer_jdk_file_part_3)
            Delete_File(current_script_path + os.sep + installer_jdk_file_name)
            # setting java path
            JAVA_PATH()
            print("JDK Install completed\n")
            return True
        else:
            print("JDK is already installed\n")
            print("JDK is already installed")
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Check_If_JDK_Installed():
    try:
        try:
            java_check = subprocess.check_call(["javac", "-version"], stderr=subprocess.STDOUT)
            print("JDK is installed")
            result = JAVA_PATH()
            if result == False:
                return False
            else:
                return True
        except:
            print("JDK is not found in path")
            print("We will check if JDK was installed.  If found, we will set all the PATH")
            result = JAVA_PATH()
            if result == True:
                return True
            else:
                return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def JAVA_PATH():
    try:
        print("We will check default location to see if we can locate JDK\n")
        java_path_64 = r'C:\Program Files\Java'
        java_path_32 = r'C:\Program Files (x86)\Java'
        if (os.path.isdir(java_path_64)):
            java_path_default = java_path_64
        elif (os.path.isdir(java_path_32)):
            java_path_default = java_path_32
        else:

            print("\tWe couldnt find java installed in default Program Files directory\n")
            return False
        print("\tFound java installed in: %s\n" % java_path_default)

        java_list = list(filter(os.path.isdir, [os.path.join(java_path_default, f) for f in os.listdir(java_path_default)]))
        for each in java_list:
            if "jdk" in each:
                print("We found JDK in default program files path.  We will set javac to the path\n")
                javac_path = each + os.sep + "bin"
                print("Setting JAVA_HOME to Environment\n")
                Add_To_Path("JAVA_HOME", each)
                print("Adding Java bin to PATH\n")
                Add_To_Path("PATH", javac_path)
                return True

        print("\tJDK is not found in the default program files path\n")
        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Android_SDK(upgrade=False):
    try:
        sdk_check = Check_If_ANDROID_SDK_Installed()
        if sdk_check == False:
            print("Please Download and Install Android Studio from https://developer.android.com/studio/")
            print("\nSet the environment variables accordingly")
            webbrowser.open_new('https://developer.android.com/studio/')
            return False
        else:
            print("Android SDK for ZeuZ is already Installed.\n")  # Print to terminal window, and log file
            # setting SDK paths
            Android_SDK_PATH()
            # we need to  investigate this further
            # Upgrade_Android_SDK()
            return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Check_If_ANDROID_SDK_Installed():
    try:
        if (os.path.isdir(Android_Home_Dir) and os.path.isdir(Android_Tools_Dir) and os.path.isdir(Android_Platform_Tools_Dir)):

            print("Android SDK for zeuz is setup \n")

            return True
        else:
            print("Android SDK for zeuz is not found\n")

            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Upgrade_Android_SDK():
    try:
        # upgrade SDK
        Kill_Process("adb.exe")
        if Check_If_ANDROID_SDK_Installed():
            # remove any old tools file
            if os.path.exists(Temp_Tools_Dir) == True:
                print("Existing folder found.. will delete: %s\n" % Temp_Tools_Dir)

                shutil.rmtree(Temp_Tools_Dir)

            result = Copy_and_Overwrite_Folder(Android_Tools_Dir, Temp_Tools_Dir)
            if result == False:
                print("Unable to locate android tools dir under: %s" % Android_Tools_Dir)

            sdkmanager_temp = Temp_Tools_Dir + os.sep + 'bin' + os.sep + 'sdkmanager.bat'
            print("Upgrading android SDK Tool")
            upgrade_command = '"%s" --sdk_root= "%s" --update' % (sdkmanager_temp, Android_Home_Dir)
            print(os.system(upgrade_command))
            print("Cleaning up...")
            if os.path.exists(Temp_Tools_Dir) == True:
                shutil.rmtree(Temp_Tools_Dir)
            print("Successfully setup Android for Appium")
        else:
            print("Please install Android SDK first before upgrading")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Install_NodeJS(upgrade=False):
    try:
        # delete npm folder because it causes problem if exists before installing nodejs
        npm_Path = os.path.join(os.getenv('APPDATA'), "npm")
        if os.path.exists(npm_Path):
            print("Removing npm folder %s\n" % npm_Path)
            shutil.rmtree(npm_Path)

        print("Installing NodeJS ...and other pre-req\n")
        base_url = "https://nodejs.org/dist/v14.17.1/"
        installer_path = Download_File(base_url, install_node_file)
        print("Installing NodeJS silently from: %s\n" % installer_path)
        command = 'msiexec.exe /i "%s"  /passive' % (installer_path)
        os.system(command)
        print("Adding nodejs to the path\n")
        Add_To_Path("PATH", npm_path)
        print("Cleaning up nodejs installation file %s\n" % installer_path)
        # time.sleep(2)
        os.remove(installer_path)
        print("adding NPM to python current path\n")
        os.environ['PATH'] += ';' + npm_path
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Install_Appium(upgrade=False):
    try:
        # check if NPM is installed
        # print "Checking pre-req for Appium installer"
        print("Checking pre-req for Appium installer\n")

        npm_check = Check_If_NPM_Installed()
        if npm_check == False:
            print("Installing: NPM\n")  # Print to terminal window, and log file
            print("NodeJS is not installed.  We will install it\n")
            # print "NodeJS is not installed.  We will install it"
            Install_NodeJS()

            print("Installing appium via NPM\n")  # Print to terminal window, and log file
            # print "Installing appium via NPM"

            appium_installer = 'npm install -g appium'
            # print "Installing appium... This may take several minutes"

            print("Installing appium... This may take several minutes\n")  # Print to terminal window, and log file
            Installer_Result = subprocess.check_call(appium_installer, shell=True)
            # print "Adding appium to the path"
            print("Adding appium to the path\n")
            Add_To_Path("PATH", appium_path)
            # print "Completed appium installer..."
            print("Completed appium installer...\n")
            return True
        else:
            check_appium = Check_If_Appium_Installed()
            if check_appium == True:
                return True

            print("Installing: Appium\n")  # Print to terminal window, and log file
            appium_installer = 'npm install -g appium'
            # print "Installing appium... This may take several minutes"
            print("Installing appium... This may take several minutes\n")  # Print to terminal window, and log file
            Installer_Result = subprocess.check_call(appium_installer, shell=True)
            print("Adding appium to the path\n")
            # print "Adding appium to the path"
            Add_To_Path("PATH", appium_path)
            print("Completed appium installer...\n")
            return True
            # print "Completed appium installer..."
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Check_If_NPM_Installed():
    try:
        try:
            # print "Checking if NPM is installed..."
            print("Checking if NPM is installed...\n")
            npm_check = subprocess.check_output(["node", "-v"], stderr=subprocess.STDOUT)
            print("NPM version: %s is installed\n" % npm_check.strip())  # Print to terminal window, and log file

            return True
        except:
            print("NPM is not installed")
            # print "NPM is not installed"
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Check_If_Appium_Installed():
    try:
        try:
            # print "Checking if Appium is installed..."
            print("Checking if Appium is installed...\n")
            appium_check = "False"
            appium_check = subprocess.check_output(["where", "appium"], stderr=subprocess.STDOUT)
            print("Appium is installed %s\n" % appium_check.strip())

            return True
        except:
            print("Appium is not installed")
            print("Checking to see if we can locate appium in appdata folder\n")

            if (os.path.isdir(appium_path)):
                print("found in appdata folder.  setting it to path\n")
                Add_To_Path("PATH", appium_path)
                print("Added appium to your path..\n")
                return True
            else:
                print("Appium is not found under appdata folder\n")
                return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print(Error_Detail)
        print("\tAn error occurred. See log for more details: %s\n" % Error_Detail)
        return False


def Create_UI_Automator_Shortcut():
    try:
        # this function will create a short cut on user's desktop for UI Automator
        desktop = winshell.desktop()
        path = os.path.join(desktop, "UIAutomatorAndroidZeuZ.lnk")
        target = Android_Tools_bin_Dir + os.sep + "uiautomatorviewer.bat"

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.save()
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print("\tUnable to create short cut for UI AUtomator: %s\n" % Error_Detail)
        return False


def Create_Android_UI_Inspector_Shortcut():
    try:
        # this function will create a short cut on user's desktop for UI Automator
        desktop = winshell.desktop()
        path = os.path.join(desktop, "UIAutomatorAndroidZeuZ.lnk")
        target = Android_Tools_bin_Dir + os.sep + "uiautomatorviewer.bat"

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.save()
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print("\tUnable to create short cut for UI AUtomator: %s\n" % Error_Detail)
        return False


def pre_installer():
    try:
        import platform
        import traceback
        import subprocess
        import sys
        try:
            from pip._internal.operations import freeze
        except ImportError:
            # pip < 10.0
            from pip.operations import freeze
        # NULL output device for disabling print output of pip installs
        try:
            from subprocess import DEVNULL  # py3k
        except ImportError:
            import os
            DEVNULL = open(os.devnull, 'wb')

        req_list = [
            "requests",
            # "colorama",
        ]
        freeze_list = freeze.freeze()
        alredy_installed_list = []
        for p in freeze_list:
            name = p.split("==")[0]
            if "@" not in name:
                # '@' symbol appears in some python modules in Windows
                alredy_installed_list.append(str(name).lower())

        # installing any missing modules
        installed = False
        error = False
        for module_name in req_list:
            if module_name.lower() not in alredy_installed_list:
                try:
                    print("module_installer: Installing module: %s" % module_name)
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "--trusted-host=pypi.org", "--trusted-host=files.pythonhosted.org", module_name], stderr=DEVNULL, stdout=DEVNULL, )
                    print("module_installer: Installed missing module: %s" % module_name)
                    installed = True
                except:
                    print("module_installer: Failed to install module: %s" % module_name)
                    error = True

        if not installed and not error:
            print("All required modules are already installed. Continuing...\n")
    except:
        traceback.print_exc()
        print("Failed to install missing modules...\n")


def windows_android_installer():
    if sys.platform == 'win32':
        if not detect_admin():
            try:
                os.system('powershell -command Start-Process "python \'%s\'" -Verb runAs' % sys.argv[0].split(os.sep)[-1])  # Re-run this program with elevated permissions to admin
                quit()  # Exit this program, the elevated program should run
            except Exception as e: # If admin access is not given
                print(e)

    print("1. Please note that if you have duplicate JDK or newer than 1.8 JAVA Appium will not work.\n")
    print("2. You must be logged in as Admin.  If you don't run as admin, appium installer will NOT WORK.\n")
    print("3. If you have spaces in your user name, Appium will not work.  Create new user with admin permission with no spaces.\n")
    print("4. Make sure you uninstall all other Java versions and remove any java version from Environmental Variable.\n")
    print("5. We will download a known JDK version (JDK 1.8) that is compatible and install it for you.\n")
    print("6. If you have an older Android Studio. Make sure you upgrade it to latest before running this.\n")
    Java_Installer = Install_JDK()

    if Java_Installer == False:
        print("\nWe were unable to install JDK 1.8. Please install JDK 1.8 manually and run again")

        return False

    Android_Studio = Auto_locate_Android_Studio()

    if Android_Studio == False:
        print("\nAndroid Studio is not installed.")
        print("1. Download and Install Android Studio.")
        print("2. You must run Android Studio once. It will download additional tools for Appium to work.")
        print("3. Quit this installer and close all other programs.")
        print("4. Run Android Studio and start a blank project.")
        print("5. Wait for all Android Studio components to finish download and install.")
        print("6. You must Quit ZeuZ Node Installer and Re-Run Android Setup.")
        print("If you still have issues with installer, please contact help@zeuz.ai")
        return False
    else:
        # create a shortcut ui automator
        try:
            print("\nCreating short cut for android UIAutomatorViewer")
            from pyshortcuts import make_shortcut
            import winshell
            from win32com.client import Dispatch
            Android_UI_Inspection = (expanduser("~") + os.sep + "AppData" + os.sep + "Local" + os.sep + "Android" + os.sep + "Sdk" + os.sep + "tools" + os.sep + "bin" + os.sep + "uiautomatorviewer.bat")
            target_exe_path = Android_UI_Inspection
            # current_script_path = '%s'%(sys.path[0])
            # UiAutomator_Icon_Path = (current_script_path.split('Zeuz_Node')[0])+os.sep+"images"+os.sep+"androidInsep.ico"
            shortcut_name = "AndroidUIInspector"
            startin = winshell.desktop()
            shell = Dispatch('WScript.Shell')
            shortcut_file = os.path.join(winshell.desktop(), shortcut_name + '.lnk')
            shortcut = shell.CreateShortCut(shortcut_file)
            shortcut.Targetpath = target_exe_path
            shortcut.WorkingDirectory = startin
            # shortcut.IconLocation = UiAutomator_Icon_Path
            shortcut.save()
            print("\nSuccessfully created short cut for android UIAutomatorViewer\n")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
            print("\tUnable to create short cut for UI AUtomator: %s\n" % Error_Detail)

    Appium_Install_Result = Install_Appium()
    if Appium_Install_Result == False:
        print("\nWe were unable to install Appium.")
        print("\n1. Make sure you do not have duplicate java installer.  Appium works only with JDK 1.8")
        print("\nIf you still have issues with installer, please contact help@zeuz.ai")
        return False


if __name__ == "__main__":
    pre_installer()
    if os.name == "nt":
        windows_android_installer()
    elif platform.system() == "Darwin":
        print("Currently this script is only for Windows")
    elif platform.system() == "Linux":
        print("Currently this script is only for Windows")
    else:
        print("Currently this script is only for Windows")


    input("Press ENTER to exit")
