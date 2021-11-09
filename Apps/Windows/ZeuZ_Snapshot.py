import time
import keyboard
import autoit
import pyautogui
import os
import platform
import sys
import inspect
from colorama import Fore
from PIL import ImageGrab as ImageGrab_Mac_Win
from PIL import Image, ImageTk
import configparser
import requests
import json
import concurrent.futures
import xml.etree.ElementTree as ET

executor = concurrent.futures.ThreadPoolExecutor()

screen_title = "ZeuZ Snapshot"
os.system("title " + screen_title)

def ExecLog(sModuleInfo, sDetails, iLogLevel):
    if iLogLevel == 1:
        status = "Passed"
        line_color = Fore.GREEN
    elif iLogLevel == 2:
        status = "Warning"
        line_color = Fore.YELLOW
    elif iLogLevel == 3:
        status = "Error"
        line_color = Fore.RED
    else:
        return
    info = f"{sModuleInfo}\t\n"
    print(line_color + f"{status.upper()} - {info}{sDetails}")

def Exception_Handler(exec_info):
    sModuleInfo_Local = inspect.currentframe().f_code.co_name + " : " + inspect.getmodulename(__file__)
    exc_type, exc_obj, exc_tb = exec_info
    Error_Type = (
        (str(exc_type).replace("type ", ""))
        .replace("<", "")
        .replace(">", "")
        .replace(";", ":")
    )
    Error_Message = str(exc_obj)
    File_Name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    Function_Name = os.path.split(exc_tb.tb_frame.f_code.co_name)[1]
    Line_Number = str(exc_tb.tb_lineno)
    Error_Detail = (
        "Error Type ~ %s: Error Message ~ %s: File Name ~ %s: Function Name ~ %s: Line ~ %s"
        % (Error_Type, Error_Message, File_Name, Function_Name, Line_Number)
    )
    sModuleInfo = Function_Name + ":" + File_Name
    ExecLog(sModuleInfo, "Following exception occurred: %s" % (Error_Detail), 3)

server = ""
api_key = ""
auth = ""
def Authenticate():
    global server, api_key
    config = configparser.ConfigParser()
    config.read("..\..\Framework\settings.conf")
    try: api_key = config.get("Authentication", "api-key")
    except: api_key = ""
    try: server = config.get("Authentication", "server_address")
    except: server = ""
    while not server or not api_key:
        server = input("Provide Server Address: ")
        api_key = input("Provide API-Key: ")

    if not auth:
        url = server + "/" if server[-1] != "/" else server
        url += "api/auth/token/verify?api_key=" + api_key
        return executor.submit(requests.get, url, verify=False)


def Upload(auth_thread, window):
    global auth
    if not auth:
        auth = auth_thread.result().json()["token"]
    Authorization = 'Bearer ' + auth
    url = server + "/" if server[-1] != "/" else server
    url += "api/contents/"
    content = json.dumps({
        'html': xml_str,
        "exact_path": {"path": path, "priority": path_priority},
        "window_name": window.Current.Name
    })

    payload = json.dumps({
        "content": content,
        "source": "windows"
    })
    headers = {
        'Authorization': Authorization,
        'Content-Type': 'application/json'

    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    response = response.json()
    del response["content"]
    print(response)


def main():
    try:
        global x, y, path_priority, element_plugin, auth, path, xml_str, findall_time, findall_count
        auth_thread = Authenticate()
        snap_program_path = os.path.join(os.environ['SystemRoot'], 'SysNative' if platform.architecture()[0] == '32bit' else 'System32', "SnippingTool.exe /clip")
        while True:
            os.system('pause')
            os.system(snap_program_path)
            from PIL import ImageGrab
            sFilePath = "ZeuZ_snap.png"
            if os.path.isfile(sFilePath):
                os.remove(sFilePath)
            ImageGrab.grabclipboard().save(sFilePath, 'PNG')
            test_case = pyautogui.prompt("Please copy the test case id from link and paste it here")
            # Upload(auth_thread, window)

    except:
        Exception_Handler(sys.exc_info())
        xml_str = ""
        path_priority = 0
        element_plugin = False

if __name__ == "__main__":
    main()
