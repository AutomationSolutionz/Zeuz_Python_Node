import time
import keyboard
import autoit
import pyautogui
import os
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
xml_str = ""
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

def _found2(Element):
    try:
        left = Element.Left
        right = Element.Right
        bottom = Element.Bottom
        top = Element.Top
        if left <= x <= right and top <= y <= bottom:
            return True
        return False
    except Exception:
        print(sys.exc_info())
        return False

def create_index2(index_trace: dict, element):
    NameE = element.Name
    ClassE = element.ClassName
    AutomationE = element.AutomationId
    LocalizedControlTypeE = element.LocalizedControlType

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

def create_path2(index_trace: dict, element):
    NameE = element.Name
    ClassE = element.ClassName
    AutomationE = element.AutomationId
    LocalizedControlTypeE = element.LocalizedControlType

    s_name = 'name="%s"' % NameE
    if NameE and s_name not in index_trace:
        return s_name + ">" + "\n" if new_line else ""
    s_name_control = 'name="%s",control="%s"' % (NameE, LocalizedControlTypeE)
    if NameE and LocalizedControlTypeE and s_name_control not in index_trace:
        return s_name_control + ">" + "\n" if new_line else ""
    s = 'automationid="%s"' % AutomationE
    if AutomationE and s not in index_trace:
        return s + ">" + "\n" if new_line else ""
    s_class = 'class="%s"' % ClassE
    if ClassE and s_class not in index_trace:
        return s_class + ">" + "\n" if new_line else ""
    s = 'name="%s",class="%s"' % (NameE, ClassE)
    if NameE and ClassE and s not in index_trace:
        return s + ">" + "\n" if new_line else ""

    if NameE and s in index_trace:
        return s_name + ">" + ',index="%s">' % (index_trace[s_name] + 1) + "\n" if new_line else ""
    if ClassE and s in index_trace:
        return s_class + ">" + ',index="%s">' % (index_trace[s_class] + 1) + "\n" if new_line else ""

    # if s_name not in index_trace:
    #     return s_name + ">" + "\n" if new_line else ""
    if s_name_control not in index_trace:
        return s_name_control + ">" + "\n" if new_line else ""
    return s_name_control + ',index="%s">' % (index_trace[s_name_control] + 1) + "\n" if new_line else ""


def _child_search2(ParentElement):
    try:
        path = ""
        child_elements = ParentElement.children
        if len(child_elements) == 0:
            return path

        index_trace = {}
        for each_child in child_elements:
            if _found(each_child):
                path += create_path(index_trace, each_child)
                # path += 'name="%s",control="%s",automationid="%s",class="%s">\n' % (NameE, LocalizedControlTypeE, AutomationE, ClassE)
                temp = _child_search(each_child)
                if temp:
                    return path + temp
            create_index(index_trace, each_child)

        return path

    except Exception:
        Exception_Handler(sys.exc_info())
        return ""

class node():
    def __init__(self, element):
        self.Name = element.Current.Name
        self.ClassName = element.Current.ClassName
        self.AutomationId = element.Current.AutomationId
        self.LocalizedControlType = element.Current.LocalizedControlType

        try:
            self.Left = element.Current.BoundingRectangle.Left
            self.Right = element.Current.BoundingRectangle.Right
            self.Bottom = element.Current.BoundingRectangle.Bottom
            self.Top = element.Current.BoundingRectangle.Top
        except:
            self.Left = -1
            self.Right = -1
            self.Bottom = -1
            self.Top = -1

        self.parent = None      # Implement it later
        self.children = []

def copy_tree2(Children, ParentElement):
    try:
        Children.append(node(ParentElement))
        Node = Children[-1]
        child_elements = ParentElement.FindAll(TreeScope.Children, Condition.TrueCondition)
        if child_elements.Count == 0:
            return
        for each_child in child_elements:
            copy_tree(Node.children, each_child)
    except:
        Exception_Handler(sys.exc_info())

global_root = None
def close(e):
    global x,y
    x = e.x
    y = e.y
    global_root.quit()
def showPIL(pilImage):
    root = tkinter.Tk()
    global global_root
    global_root = root
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    print(w,h)
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set()
    # root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
    root.bind("<Escape>", close, root)
    root.bind("<ButtonPress>", close, root)

    canvas = tkinter.Canvas(root,width=w,height=h)
    canvas.pack()
    canvas.configure(background='black')
    imgWidth, imgHeight = pilImage.size
    if imgWidth > w or imgHeight > h:
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
        pilImage = pilImage.resize((imgWidth,imgHeight), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(pilImage)
    imagesprite = canvas.create_image(w/2,h/2,image=image)
    root.mainloop()

def main2():
    try:
        global x, y
        print("Press enter to inspect")
        # time.sleep(5)
        start = time.time()
        Root = node(AutomationElement.RootElement)
        all_windows = AutomationElement.RootElement.FindAll(TreeScope.Children, Condition.TrueCondition)
        if all_windows.Count == 0:
            return
        print("Enter between 1-%s to select a window" % all_windows.Count)
        for i in range(len(all_windows)):
            print("%s. %s" % (i+1, all_windows[i].Current.Name))
        dur = time.time() - start
        idx = input()
        start = time.time()
        try:
            idx = int(idx.strip())
        except:
            return Exception_Handler(sys.exc_info())
        window = all_windows[idx-1]
        window_name = window.Current.Name
        Root.children.append(node(window))
        all_elements = window.FindAll(TreeScope.Children, Condition.TrueCondition)
        if all_elements.Count != 0:
            for each_child in all_elements:
                copy_tree(Root.children[0].children, each_child)
        print("time taken for copy = %s" % (time.time() - start + dur))
        autoit.win_activate(window_name)
        time.sleep(0.5)
        ImageName = "ss.png"
        image = ImageGrab_Mac_Win.grab()
        autoit.win_activate(screen_title)
        # image.save(ImageName, format="PNG")
        # image = Image.open(ImageName)
        showPIL(image)
        print("tkinter close")
        print("************ YOUR Exact Path *************")
        if x>=0 and y>=0:
            res = _child_search(Root)[:-2] + "\n"
            print(res)
    except:
        Exception_Handler(sys.exc_info())

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

def create_path(index_trace: dict, element):
    NameE = element.Current.Name
    ClassE = element.Current.ClassName
    AutomationE = element.Current.AutomationId
    LocalizedControlTypeE = element.Current.LocalizedControlType

    s_name = 'name="%s"' % NameE
    if NameE and s_name not in index_trace:
        return s_name + ">" + "\n" if new_line else ""
    s_name_control = 'name="%s",control="%s"' % (NameE, LocalizedControlTypeE)
    if NameE and LocalizedControlTypeE and s_name_control not in index_trace:
        return s_name_control + ">" + "\n" if new_line else ""
    s = 'automationid="%s"' % AutomationE
    if AutomationE and s not in index_trace:
        return s + ">" + "\n" if new_line else ""
    s_class = 'class="%s"' % ClassE
    if ClassE and s_class not in index_trace:
        return s_class + ">" + "\n" if new_line else ""
    s = 'name="%s",class="%s"' % (NameE, ClassE)
    if NameE and ClassE and s not in index_trace:
        return s + ">" + "\n" if new_line else ""

    global path_priority
    path_priority = 2
    if NameE and s in index_trace:
        return s_name + ">" + ',index="%s">' % (index_trace[s_name] + 1) + "\n" if new_line else ""
    if ClassE and s in index_trace:
        return s_class + ">" + ',index="%s">' % (index_trace[s_class] + 1) + "\n" if new_line else ""

    # if s_name not in index_trace:
    #     return s_name + ">" + "\n" if new_line else ""
    if s_name_control not in index_trace:
        return s_name_control + ">" + "\n" if new_line else ""
    return s_name_control + ',index="%s">' % (index_trace[s_name_control] + 1) + "\n" if new_line else ""


element_plugin = False
findall_time = 0; findall_count = 0
def _child_search(ParentElement, parenthesis=1):
    try:
        path = ""
        global xml_str, element_plugin, findall_time, findall_count
        start = time.perf_counter()
        child_elements = ParentElement.FindAll(TreeScope.Children, Condition.TrueCondition)
        findall_time += time.perf_counter()-start
        findall_count += 1
        if child_elements.Count == 0:
            return path

        index_trace = {}
        temp = ""
        found = False
        for each_child in child_elements:
            elem_name = each_child.Current.Name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;").replace(r"\Automation_Solutionz\Zeuz_Node\Public_Node\Zeuz_Python_Node\Apps\W", "xyz")
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
            xml_str += "\n" + "  "*parenthesis + '<div Name="%s" AutomationId="%s" ClassName="%s" LocalizedControlType="%s"' % \
            (elem_name, elem_automationid, elem_class, elem_control) + ' Left="%s" Right="%s" Top="%s" Bottom="%s">' % (left, right, top, bottom)
            if _found(each_child) and not found:
                path += create_path(index_trace, each_child)
                found = True
                if not element_plugin:
                    xml_len = len(xml_str)
            if not temp:
                temp = _child_search(each_child, parenthesis+1)
            else:
                _child_search(each_child, parenthesis+1)
            if not found:
                create_index(index_trace, each_child)
            xml_str += "\n" + "  "*parenthesis + "</div>"

        if found and not element_plugin:
            xml_str = xml_str[:xml_len-1] + ' zeuz="aiplugin"' + xml_str[xml_len-1:]
            element_plugin = True
        return path + temp

    except Exception:
        print(sys.exc_info())
        return ""

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
        del att["Left"]; del att["Right"]; del att["Top"]; del att["Bottom"]
        Remove_coordinate(each)


def main():
    try:
        global x, y, path_priority, element_plugin, auth, path, xml_str, findall_time, findall_count
        auth_thread = Authenticate()
        while True:
            os.system('pause')
            print("Hover over the Element and press control")
            path = ""; xml_str = ""; path_priority = 0; element_plugin = False; findall_time = 0; findall_count = 0
            keyboard.wait("ctrl")
            x, y = pyautogui.position()

            print("Searching for the Element identifier")

            start = time.perf_counter()
            windows = AutomationElement.RootElement.FindAll(TreeScope.Children, Condition.TrueCondition)
            if windows.Count == 0:
                return
            for window in windows:
                if _found(window):
                    window_name = window.Current.Name
                    xml_str += '<body Window="%s">' % window_name
                    path = create_path({}, window)
                    break
            else:
                print("No window found in that coordinate")
                return
            path += _child_search(window)[:-2] + "\n"
            xml_str += "\n" + "</body>"

            xml_str = xml_str.encode('ascii', 'ignore').decode()        # ignore characters which are not ascii presentable

            print("************* Exact Path *************")
            print(path)
            # print("************* path_priority *************")
            # print("Path priority =", path_priority, "\n\n")
            with open("Element.xml", "w") as f:
                f.write(xml_str)
            element_time = round(time.perf_counter()-start, 3)
            sibling_time = 0
            try: autoit.win_activate(screen_title)
            except: pass
            sibling = pyautogui.confirm('Do you want SIBLING?')
            root = ET.fromstring(xml_str)
            if sibling.strip().lower() == "ok":
                print("Hover over the SIBLING and press control")
                keyboard.wait("ctrl")
                x, y = pyautogui.position()
                start = time.perf_counter()
                sibling_search(root)
                sibling_time = round(time.perf_counter() - start, 3)
            start = time.perf_counter()
            Remove_coordinate(root)
            Remove_coordinate_time = round(time.perf_counter() - start, 3)
            xml_str = ET.tostring(root).decode()
            with open("Sibling.xml", "w") as f:
                f.write(xml_str)

            start = time.perf_counter()
            Upload(auth_thread, window_name)
            Upload_time = round(time.perf_counter()-start, 3)

            print("\nElement searching time =", element_time, "sec")
            print("Sibling searching time =", sibling_time, "sec")
            print("Coordinate remove time =", Remove_coordinate_time, "sec")
            print("Uploading to API  time =", Upload_time, "sec")
            print("start_findall time =", round(findall_time, 3), "sec", "Findall count =", findall_count)

    except:
        Exception_Handler(sys.exc_info())
        xml_str = ""
        path_priority = 0
        element_plugin = False

if __name__ == "__main__":
    main()
