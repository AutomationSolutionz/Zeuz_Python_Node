import time
import keyboard
import autoit
import pyautogui
import os
import sys
import inspect
from colorama import init as colorama_init
from colorama import Fore

#Importing rich library to print in an organized manner
from rich import print
from rich.text import Text
from rich.tree import Tree

# Initialize colorama for the current platform
colorama_init(autoreset=True)

from PIL import ImageGrab as ImageGrab_Mac_Win
from PIL import Image, ImageTk
import configparser
import requests
import json
import concurrent.futures
import xml.etree.ElementTree as ET

new_line = True
import clr, System
import tkinter
executor = concurrent.futures.ThreadPoolExecutor()

screen_title = "ZeuZ Windows Inspector"
os.system("title " + screen_title)
dll_path = os.getcwd().split("Apps")[0] + "Framework" + os.sep + "windows_dll_files" + os.sep
clr.AddReference(dll_path + "UIAutomationClient")
clr.AddReference(dll_path + "UIAutomationTypes")
clr.AddReference(dll_path + "UIAutomationProvider")
clr.AddReference( "System.Windows.Forms")
x, y = -1, -1
path_priority = 0
path = ""
from System.Windows.Automation import *

# Suppress the InsecureRequestWarning since we use verify=False parameter.
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

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


def _found(Element):
    try:
        left = Element.Current.BoundingRectangle.Left
        right = Element.Current.BoundingRectangle.Right
        bottom = Element.Current.BoundingRectangle.Bottom
        top = Element.Current.BoundingRectangle.Top
        if left <= x <= right and top <= y <= bottom:
            return True
        return False
    except Exception:
        print(sys.exc_info())
        return False

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

def Upload(auth_thread, window_name):
    try:
        global auth
        if not auth:
            auth = auth_thread.result().json()["token"]
        Authorization = 'Bearer ' + auth
        url = server + "/" if server[-1] != "/" else server
        url += "api/contents/"
        content = json.dumps({
            'html': xml_str,
            "exact_path": {"path": path, "priority": path_priority},
            "window_name": window_name
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
    except:
        Exception_Handler(sys.exc_info())
        ExecLog("", "Could not upload Element identifiers xml", 3)
        try: print(response)
        except: pass


def sibling_found(each):
    try:
        left = float(each.attrib["Left"])
        right = float(each.attrib["Right"])
        top = float(each.attrib["Top"])
        bottom = float(each.attrib["Bottom"])
        if left <= x <= right and top <= y <= bottom:
            return True
        return False
    except Exception:
        print(sys.exc_info())
        return False


def sibling_search(ParentElement):
    if len(ParentElement) == 0:
        ParentElement.set("zeuz-sibling", "aiplugin-sibling")
        return
    for each in ParentElement:
        if sibling_found(each):
            sibling_search(each)
            return


def Remove_coordinate(root):
    for each in root:
        att = each.attrib
        del att["Left"]; del att["Right"]; del att["Top"]; del att["Bottom"];
        if "found" in att: del att["found"]
        Remove_coordinate(each)


def debugger_is_active() -> bool:
    """Return if the debugger is currently active"""
    gettrace = getattr(sys, 'gettrace', lambda : None)
    return gettrace() is not None


config = configparser.ConfigParser()
config.read("..\..\Framework\settings.conf")
try:
    No_of_level_to_skip = int(config.get("Inspector", "No_of_level_to_skip"))
    if No_of_level_to_skip < 0:
        No_of_level_to_skip = 0
except:
    No_of_level_to_skip = 0

def create_tag(elem):
    s = "<"
    for i in elem.attrib:
        s = s + i + '="' + elem.attrib[i] + '" '
    s = s[:-1] + ">"
    return s


def printTree(root,tree):
    for child in root:
        if child.get('zeuz') == "aiplugin":
            tree.add(f"[bold green]{create_tag(child)}", guide_style="red")
            return
        elif child.findall(".//*[@zeuz='aiplugin']"):
            temp = tree.add(f"[yellow]{create_tag(child)}", guide_style="red")
            printTree(child, temp)
        else:
            tree.add(f"[white]{create_tag(child)}", guide_style="red")


def create_index(index_trace: dict, element):
    NameE = element.Current.Name
    ClassE = element.Current.ClassName
    AutomationE = element.Current.AutomationId
    LocalizedControlTypeE = element.Current.LocalizedControlType

    s = 'automationid="%s"' % AutomationE
    if s in index_trace: index_trace[s] += 1
    else: index_trace[s] = 0

    s = 'name="%s"' % NameE
    if s in index_trace: index_trace[s] += 1
    else: index_trace[s] = 0

    s = 'name="%s",control="%s"' % (NameE, LocalizedControlTypeE)
    if s in index_trace: index_trace[s] += 1
    else: index_trace[s] = 0

    s = 'class="%s"' % ClassE
    if s in index_trace: index_trace[s] += 1
    else: index_trace[s] = 0

    s = 'name="%s",class="%s"' % (NameE, ClassE)
    if s in index_trace: index_trace[s] += 1
    else: index_trace[s] = 0

def create_path(index_trace: dict, element, window_cond=False):
    NameE = element.Current.Name
    ClassE = element.Current.ClassName
    AutomationE = element.Current.AutomationId
    LocalizedControlTypeE = element.Current.LocalizedControlType

    if window_cond:
        config = configparser.ConfigParser()
        config.read("..\..\Framework\settings.conf")
        try: window_name = config.get("Inspector", "Window")
        except: window_name = ""
        if window_name:
            s_name = '**name="%s"' % window_name
        else:
            s_name = 'name="%s"' % NameE
    else:
        s_name = 'name="%s"' % NameE

    s = 'automationid="%s"' % AutomationE
    if AutomationE and s not in index_trace:
        return s + ">" + "\n" if new_line else ""

    if NameE and s_name not in index_trace:
        return s_name + ">" + "\n" if new_line else ""
    s_name_control = 'name="%s",control="%s"' % (NameE, LocalizedControlTypeE)
    if NameE and LocalizedControlTypeE and s_name_control not in index_trace:
        return s_name_control + ">" + "\n" if new_line else ""
    s_class = 'class="%s"' % ClassE
    if ClassE and s_class not in index_trace:
        return s_class + ">" + "\n" if new_line else ""
    s = 'name="%s",class="%s"' % (NameE, ClassE)
    if NameE and ClassE and s not in index_trace:
        return s + ">" + "\n" if new_line else ""

    global path_priority
    path_priority = 2
    if NameE and s in index_trace:
        return s_name + ',index="%s">' % (index_trace[s_name] + 1) + "\n" if new_line else ""
    if ClassE and s in index_trace:
        return s_class + ',index="%s">' % (index_trace[s_class] + 1) + "\n" if new_line else ""

    # if s_name not in index_trace:
    #     return s_name + ">" + "\n" if new_line else ""
    if s_name_control not in index_trace:
        return s_name_control + ">" + "\n" if new_line else ""
    return s_name_control + ',index="%s">' % (index_trace[s_name_control] + 1) + "\n" if new_line else ""


element_plugin = False
findall_time = 0; findall_count = 0; each_findall_time = []


def exact_path_maker(xmlElem, pathList:list, window_cond=False):
    NameE = xmlElem.attrib["Name"]
    ClassE = xmlElem.attrib["ClassName"]
    AutomationE = xmlElem.attrib["AutomationId"]
    LocalizedControlTypeE = xmlElem.attrib["LocalizedControlType"]

    index_trace = {}

    if window_cond:
        config = configparser.ConfigParser()
        config.read("..\..\Framework\settings.conf")
        try: window_name = config.get("Inspector", "Window")
        except: window_name = ""
        if window_name:
            s_name = '**name="%s"' % window_name
        else:
            s_name = 'name="%s"' % NameE
        window_cond = False
    else:
        s_name = 'name="%s"' % NameE

    s = 'automationid="%s"' % AutomationE
    if AutomationE and s not in index_trace:
        return s + ">" + "\n" if new_line else ""

    if NameE and s_name not in index_trace:
        return s_name + ">" + "\n" if new_line else ""
    s_name_control = 'name="%s",control="%s"' % (NameE, LocalizedControlTypeE)
    if NameE and LocalizedControlTypeE and s_name_control not in index_trace:
        return s_name_control + ">" + "\n" if new_line else ""
    s_class = 'class="%s"' % ClassE
    if ClassE and s_class not in index_trace:
        return s_class + ">" + "\n" if new_line else ""
    s = 'name="%s",class="%s"' % (NameE, ClassE)
    if NameE and ClassE and s not in index_trace:
        return s + ">" + "\n" if new_line else ""

    global path_priority
    path_priority = 2
    if NameE and s in index_trace:
        return s_name + ',index="%s">' % (index_trace[s_name] + 1) + "\n" if new_line else ""
    if ClassE and s in index_trace:
        return s_class + ',index="%s">' % (index_trace[s_class] + 1) + "\n" if new_line else ""

    # if s_name not in index_trace:
    #     return s_name + ">" + "\n" if new_line else ""
    if s_name_control not in index_trace:
        return s_name_control + ">" + "\n" if new_line else ""
    return s_name_control + ',index="%s">' % (index_trace[s_name_control] + 1) + "\n" if new_line else ""


element_plugin = False
findall_time = 0; findall_count = 0; each_findall_time = []


def create_tree(xmlELem, ParentElement, level):
    try:
        path = ""
        global xml_str, element_plugin, findall_time, findall_count
        start = time.perf_counter()
        child_elements = ParentElement.FindAll(TreeScope.Children, Condition.TrueCondition)
        temp_findall_time = time.perf_counter()-start
        global each_findall_time
        each_findall_time += [[temp_findall_time/child_elements.Count if child_elements.Count>0 else -1, temp_findall_time, child_elements.Count]]
        findall_time += temp_findall_time
        findall_count += 1
        # child_elements.Count>0 and temp_findall_time/child_elements.Count>2.5
        if child_elements.Count == 0:
            return

        found = False
        for each_child in child_elements:
            elem_name = each_child.Current.Name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
            elem_automationid = each_child.Current.AutomationId.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
            elem_class = each_child.Current.ClassName.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
            elem_control = each_child.Current.LocalizedControlType.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
            try:
                left = str(each_child.Current.BoundingRectangle.Left)
                right = str(each_child.Current.BoundingRectangle.Right)
                bottom = str(each_child.Current.BoundingRectangle.Bottom)
                top = str(each_child.Current.BoundingRectangle.Top)
            except:
                left, right, top, bottom = "", "", "", ""

            attribs = {
                "Name": elem_name,
                "AutomationId": elem_automationid,
                "LocalizedControlType": elem_control,
                "ClassName": elem_class,
                "Left": left,
                "Right": right,
                "Top": top,
                "Bottom": bottom,
            }
            if _found(each_child):
                attribs["found"] = "True"
                xmlChildElem = ET.SubElement(xmlELem, 'div', **attribs)
                ret = create_tree(xmlChildElem, each_child, level + 1)
                if not xmlChildElem.findall(".//*[@zeuz='aiplugin']"):
                    xmlChildElem.set("zeuz", "aiplugin")
            elif level >= No_of_level_to_skip:
                xmlChildElem = ET.SubElement(xmlELem, 'div', **attribs)
                create_tree(xmlChildElem, each_child, level + 1)

    except Exception:
        Exception_Handler(sys.exc_info())
        return


def main():
    try:
        global x, y, path_priority, element_plugin, auth, path, findall_time, findall_count, list_path
        auth_thread = Authenticate()

        while True:
            if debugger_is_active():
                pass
                # input("Press Enter to Continue")
            else:
                os.system('pause')
            print("Hover over the Element and press control")
            path = ""; xml_str = ""; path_priority = 0; element_plugin = False; findall_time = 0; findall_count = 0
            # keyboard.wait("ctrl")
            x, y = pyautogui.position()
            x = 988; y = 1052
            print(f"x = {x}, y = {y}")  # Todo: change it

            print("Searching for the Element identifier")

            start = time.perf_counter()
            windows = AutomationElement.RootElement.FindAll(TreeScope.Children, Condition.TrueCondition)
            if windows.Count == 0:
                return
            for window in windows:
                if window.Current.Name.strip() in ("Annotation - Zoom"): continue
                if _found(window):
                    window_name = window.Current.Name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
                    window_automationid = window.Current.AutomationId.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
                    window_class = window.Current.ClassName.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
                    window_control = window.Current.LocalizedControlType.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
                    try:
                        pid = window.Current.ProcessId
                    except:
                        pid = ""
                    attribs = {
                        "Name": window_name,
                        "AutomationId": window_automationid,
                        "LocalizedControlType": window_class,
                        "ClassName": window_control,
                        "pid": str(pid),
                    }
                    root = ET.Element("body", **attribs)
                    create_path({}, window, True)
                    break
            else:
                print("No window found in that coordinate")
                return

            create_tree(root, window, 0)

            Remove_coordinate(root)
            tree = Tree(f"[cyan]{create_tag(root)}", guide_style="red")  # root of rich tree python
            printTree(root, tree)
            print(tree)

            path = exact_path_maker(root, [], True)

            xml_str = xml_str.encode('ascii', 'ignore').decode()        # ignore characters which are not ascii presentable

            print("======== COPY Exact Path ========")
            print(path)
            print("============= COPY ==============")
            # print("************* path_priority *************")
            # print("Path priority =", path_priority, "\n\n")
            with open("Element.xml", "w") as f:
                f.write(xml_str)
            element_time = round(time.perf_counter()-start, 3)
            sibling_time = 0
            try: autoit.win_activate(screen_title)
            except: pass
            root = ET.fromstring(xml_str)

            config = configparser.ConfigParser()
            config.read("..\..\Framework\settings.conf")
            try:
                sibling = config.get("Inspector", "sibling")
            except:
                sibling = ""
            if sibling.strip().lower() not in ("false", "off", "disabled", "no") and pyautogui.confirm('Do you want SIBLING?').strip().lower() == "ok":
                print("Hover over the SIBLING and press control")
                keyboard.wait("ctrl")
                x, y = pyautogui.position()
                start = time.perf_counter()
                sibling_search(root)
                sibling_time = round(time.perf_counter() - start, 3)
            start = time.perf_counter()
            Remove_coordinate_time = round(time.perf_counter() - start, 3)
            xml_str = ET.tostring(root).decode()
            tree = Tree(f"[cyan]{create_tag(root)}", guide_style="red")  # root of rich tree python
            printTree(root, tree)
            print(tree)
            with open("Sibling.xml", "w") as f:
                f.write(xml_str)

            start = time.perf_counter()
            Upload(auth_thread, window_name)
            Upload_time = round(time.perf_counter()-start, 3)

            # print("\nElement searching time =", element_time, "sec")
            # print("Sibling searching time =", sibling_time, "sec")
            # print("Coordinate remove time =", Remove_coordinate_time, "sec")
            # print("Uploading to API  time =", Upload_time, "sec")
            # print("start_findall time =", round(findall_time, 3), "sec", "Findall count =", findall_count)
            # print("each__findall_time (Each_Element_find_time, finall_time, child_count)")
            from operator import itemgetter
            global each_findall_time
            each_findall_time = sorted(each_findall_time, key=itemgetter(0), reverse=True)
            # for i in each_findall_time:
            #     print(i)
            # break

    except:
        Exception_Handler(sys.exc_info())
        xml_str = ""
        path_priority = 0
        element_plugin = False


if __name__ == "__main__":
    main()