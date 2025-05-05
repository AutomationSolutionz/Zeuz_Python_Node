import pathlib
import time
import keyboard
import pyautogui
import os
import sys
import inspect
from colorama import init as colorama_init
from colorama import Fore
import traceback

from rich import print
from rich.text import Text
from rich.tree import Tree

colorama_init(autoreset=True)

import configparser
import requests
import json
import xml.etree.ElementTree as ET

new_line = True
import clr, System

screen_title = "ZeuZ Windows Inspector"
os.system("title " + screen_title)
dll_path = os.getcwd().split("Apps")[0] + "Framework" + os.sep + "windows_dll_files" + os.sep
clr.AddReference(dll_path + "UIAutomationClient")
clr.AddReference(dll_path + "UIAutomationTypes")
clr.AddReference(dll_path + "UIAutomationProvider")
clr.AddReference( "System.Windows.Forms")
x, y = -1, -1
path_priority = 0
from System.Windows.Automation import *

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
def Authenticate(xml_str, window_name, path):
    global server, api_key
    config = configparser.ConfigParser()
    config.read("..\..\Framework\settings.conf")
    try: api_key = config.get("Authentication", "api-key").strip()
    except: api_key = ""
    try: server = config.get("Authentication", "server_address").strip()
    except: server = ""

    try:
        url = server + "/" if server[-1] != "/" else server
        url += "ai_record_single_action/"
        content = json.dumps({
            'page_src': xml_str,
            "action_type": "windows",
            "exact_path": {"path": path, "priority": path_priority},
            "window_name": window_name
        })
        headers = {
            "X-Api-Key": api_key,
        }

        r = requests.request("POST", url, headers=headers, data=content, verify=False)
        response = r.json()
        if response["info"] == "success":
            r.ok and print("Content successfully sent to AI Engine\n")
        else:
            ExecLog("", response["info"], 3)
    except:
        traceback.print_exc()
        print("Could not upload Element identifiers xml")
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
        Remove_coordinate(each)


def Remove_zeuz_aiplugin(root):
    zeuz_aiplugins = root.findall(".//*[@zeuz='aiplugin']")
    min_ = min([float(i.attrib["area"]) for i in zeuz_aiplugins])
    for i in zeuz_aiplugins:
        if min_ != float(i.attrib["area"]) : del i.attrib["zeuz"]



def Remove_attribs(root):
    for each in root:
        att = each.attrib
        if "found" in att: del att["found"]
        if "area" in att: del att["area"]
        if "pattern_list" in att: del att["pattern_list"]
        if "Value" in att: del att["Value"]
        Remove_attribs(each)


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
        elif child.findall(".//*[@zeuz='aiplugin']"):
            temp = tree.add(f"[yellow]{create_tag(child)}", guide_style="red")
            printTree(child, temp)
        else:
            tree.add(f"[white]{create_tag(child)}", guide_style="red")


def create_index(index_trace: dict, xmlElem):
    NameE = xmlElem.attrib["Name"]
    ClassE = xmlElem.attrib["ClassName"]
    AutomationE = xmlElem.attrib["AutomationId"]
    LocalizedControlTypeE = xmlElem.attrib["LocalizedControlType"]

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


def create_path(index_trace: dict, xmlElem, window_cond=False):
    NameE = xmlElem.attrib["Name"]
    ClassE = xmlElem.attrib["ClassName"]
    AutomationE = xmlElem.attrib["AutomationId"]
    LocalizedControlTypeE = xmlElem.attrib["LocalizedControlType"]

    if window_cond:
        config = configparser.ConfigParser()
        config.read("..\..\Framework\settings.conf")
        try: window_name = config.get("Inspector", "Window")
        except: window_name = ""
        if window_name and window_name.lower() in NameE.lower():
            s_name = '**name="%s"' % window_name
            return s_name + ">" + "\n" if new_line else ""
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

    if s_name_control not in index_trace:
        return s_name_control + ">" + "\n" if new_line else ""
    return s_name_control + ',index="%s">' % (index_trace[s_name_control] + 1) + "\n" if new_line else ""


findall_time = 0; findall_count = 0; each_findall_time = []


def exact_path_maker(xmlElem, pathList:list, areaList=None, window_cond=False):
    global path
    index_trace = {}

    if window_cond:
        pathList = [create_path(index_trace, xmlElem, window_cond)]

    branch_count = -1
    path_till_now = pathList[-1]
    for each_child in xmlElem:
        if "found" in each_child.attrib:
            path_ = create_path(index_trace, each_child, window_cond)
            if len(pathList) + branch_count >= len(pathList):
                pathList += [path_till_now + path_]
            else:
                pathList[len(pathList) + branch_count] += path_
            if "area" in each_child.attrib:
                areaList.append(float(each_child.attrib["area"]))
            exact_path_maker(each_child, pathList, areaList)
            branch_count += 1
        create_index(index_trace, each_child)

    if window_cond:
        sortIndex = [i[0] for i in sorted(enumerate(areaList), key=lambda x: x[1])]
        for i in sortIndex:
            print(f"\n======== COPY Exact Path. Element Area = {areaList[i]} ========")
            print(pathList[i])
            path = pathList[sortIndex[0]]


findall_time = 0; findall_count = 0; each_findall_time = []
def create_tree(xmlELem, ParentElement, level):
    try:
        path = ""
        global xml_str, findall_time, findall_count
        start = time.perf_counter()
        child_elements = ParentElement.FindAll(TreeScope.Children, Condition.TrueCondition)
        temp_findall_time = time.perf_counter()-start
        global each_findall_time
        each_findall_time += [[temp_findall_time/child_elements.Count if child_elements.Count>0 else -1, temp_findall_time, child_elements.Count]]
        findall_time += temp_findall_time
        findall_count += 1
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
                create_tree(xmlChildElem, each_child, level + 1)

                if not xmlChildElem.findall(".//*[@zeuz='aiplugin']"):
                    xmlChildElem.set("zeuz", "aiplugin")

                    area = (float(right) - float(left)) * (float(bottom) - float(top))
                    xmlChildElem.set("area", f"{area}")

                    pattern_list = [Automation.PatternName(i) for i in each_child.GetSupportedPatterns()]
                    xmlChildElem.set("pattern_list", f"{pattern_list}")

                    if "Value" in pattern_list:
                        try: Value = str(each_child.GetCurrentPattern(ValuePattern.Pattern).Current.Value)
                        except: Value = ""
                        xmlChildElem.set("Value", Value)


            elif level >= No_of_level_to_skip:
                xmlChildElem = ET.SubElement(xmlELem, 'div', **attribs)
                create_tree(xmlChildElem, each_child, level + 1)

    except Exception:
        traceback.print_exc()
        return

def pause():
    if debugger_is_active():
        input("Press Enter to Continue")
    else:
        os.system('pause')
    print("Hover over the Element and press control")

def inspect():
    path = ""; xml_str = ""; findall_time = 0; findall_count = 0
    keyboard.wait("ctrl")
    x, y = pyautogui.position()
    print(f"x = {x}, y = {y}")
    return x, y


class WindowsInspector:
    def __init__(self):
        self.x = -1
        self.y = -1
        self.path_priority = 0
        self.paths = []
        self.xml_str = ""
        self.window_name = ""
        self.findall_time = 0
        self.findall_count = 0
        self.each_findall_time = []
        self.auth = None
        self.new_line = True
        self.No_of_level_to_skip = 0
        
        config = configparser.ConfigParser()
        config.read("..\..\Framework\settings.conf")
        try:
            self.No_of_level_to_skip = int(config.get("Inspector", "No_of_level_to_skip"))
            if self.No_of_level_to_skip < 0:
                self.No_of_level_to_skip = 0
        except:
            self.No_of_level_to_skip = 0

    def create_tag(self, elem):
        s = "<"
        for i in elem.attrib:
            s = s + i + '="' + elem.attrib[i] + '" '
        s = s[:-1] + ">"
        return s

    def printTree(self, root, tree):
        for child in root:
            if child.get('zeuz') == "aiplugin":
                tree.add(f"[bold green]{self.create_tag(child)}", guide_style="red")
            elif child.findall(".//*[@zeuz='aiplugin']"):
                temp = tree.add(f"[yellow]{self.create_tag(child)}", guide_style="red")
                self.printTree(child, temp)
            else:
                tree.add(f"[white]{self.create_tag(child)}", guide_style="red")

    def create_index(self, index_trace: dict, xmlElem):
        NameE = xmlElem.attrib["Name"]
        ClassE = xmlElem.attrib["ClassName"]
        AutomationE = xmlElem.attrib["AutomationId"]
        LocalizedControlTypeE = xmlElem.attrib["LocalizedControlType"]

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

    def create_path(self, index_trace: dict, xmlElem, window_cond=False):
        NameE = xmlElem.attrib["Name"]
        ClassE = xmlElem.attrib["ClassName"]
        AutomationE = xmlElem.attrib["AutomationId"]
        LocalizedControlTypeE = xmlElem.attrib["LocalizedControlType"]

        if window_cond:
            config = configparser.ConfigParser()
            config.read("..\..\Framework\settings.conf")
            try: window_name = config.get("Inspector", "Window")
            except: window_name = ""
            if window_name and window_name.lower() in NameE.lower():
                s_name = '**name="%s"' % window_name
                return s_name + ">" + "\n" if self.new_line else ""
            else:
                s_name = 'name="%s"' % NameE
        else:
            s_name = 'name="%s"' % NameE

        s = 'automationid="%s"' % AutomationE
        if AutomationE and s not in index_trace:
            return s + ">" + "\n" if self.new_line else ""

        if NameE and s_name not in index_trace:
            return s_name + ">" + "\n" if self.new_line else ""
        s_name_control = 'name="%s",control="%s"' % (NameE, LocalizedControlTypeE)
        if NameE and LocalizedControlTypeE and s_name_control not in index_trace:
            return s_name_control + ">" + "\n" if self.new_line else ""
        s_class = 'class="%s"' % ClassE
        if ClassE and s_class not in index_trace:
            return s_class + ">" + "\n" if self.new_line else ""
        s = 'name="%s",class="%s"' % (NameE, ClassE)
        if NameE and ClassE and s not in index_trace:
            return s + ">" + "\n" if self.new_line else ""

        if s_name_control not in index_trace:
            return s_name_control + ">" + "\n" if self.new_line else ""
        return s_name_control + ',index="%s">' % (index_trace[s_name_control] + 1) + "\n" if self.new_line else ""

    def exact_path_maker(self, xmlElem, pathList:list, areaList:list, window_cond=False):
        index_trace = {}

        if window_cond:
            pathList = [self.create_path(index_trace, xmlElem, window_cond)]

        branch_count = -1
        path_till_now = pathList[-1]
        for each_child in xmlElem:
            if "found" in each_child.attrib:
                path_ = self.create_path(index_trace, each_child, window_cond)
                if len(pathList) + branch_count >= len(pathList):
                    pathList += [path_till_now + path_]
                else:
                    pathList[len(pathList) + branch_count] += path_
                if "area" in each_child.attrib:
                    areaList.append(float(each_child.attrib["area"]))
                self.exact_path_maker(each_child, pathList, areaList)
                branch_count += 1
            self.create_index(index_trace, each_child)

        if window_cond:
            sortIndex = [i[0] for i in sorted(enumerate(areaList), key=lambda x: x[1])]
            for i in sortIndex:
                print(f"\n======== COPY Exact Path. Element Area = {areaList[i]} ========")
                print(pathList[i])
                self.paths = [{
                    "path": pathList[i],
                    "area": int(areaList[i])
                } for i in sortIndex]

    def create_tree(self, xmlELem, ParentElement, level):
        try:
            start = time.perf_counter()
            child_elements = ParentElement.FindAll(TreeScope.Children, Condition.TrueCondition)
            temp_findall_time = time.perf_counter()-start
            self.each_findall_time += [[temp_findall_time/child_elements.Count if child_elements.Count>0 else -1, temp_findall_time, child_elements.Count]]
            self.findall_time += temp_findall_time
            self.findall_count += 1
            
            if child_elements.Count == 0:
                return

            for each_child in child_elements:
                elem_name = self._sanitize_text(each_child.Current.Name)
                elem_automationid = self._sanitize_text(each_child.Current.AutomationId)
                elem_class = self._sanitize_text(each_child.Current.ClassName)
                elem_control = self._sanitize_text(each_child.Current.LocalizedControlType)
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
                if self._found(each_child):
                    attribs["found"] = "True"
                    xmlChildElem = ET.SubElement(xmlELem, 'div', **attribs)
                    self.create_tree(xmlChildElem, each_child, level + 1)

                    if not xmlChildElem.findall(".//*[@zeuz='aiplugin']"):
                        xmlChildElem.set("zeuz", "aiplugin")

                        area = (float(right) - float(left)) * (float(bottom) - float(top))
                        xmlChildElem.set("area", f"{area}")

                        pattern_list = [Automation.PatternName(i) for i in each_child.GetSupportedPatterns()]
                        xmlChildElem.set("pattern_list", f"{pattern_list}")

                        if "Value" in pattern_list:
                            try: Value = str(each_child.GetCurrentPattern(ValuePattern.Pattern).Current.Value)
                            except: Value = ""
                            xmlChildElem.set("Value", Value)

                elif level >= self.No_of_level_to_skip:
                    xmlChildElem = ET.SubElement(xmlELem, 'div', **attribs)
                    self.create_tree(xmlChildElem, each_child, level + 1)

        except Exception:
            traceback.print_exc()
            return

    def Remove_coordinate(self, root):
        for each in root:
            att = each.attrib
            del att["Left"]; del att["Right"]; del att["Top"]; del att["Bottom"];
            self.Remove_coordinate(each)

    def Remove_zeuz_aiplugin(self, root):
        zeuz_aiplugins = root.findall(".//*[@zeuz='aiplugin']")
        min_ = min([float(i.attrib["area"]) for i in zeuz_aiplugins])
        for i in zeuz_aiplugins:
            if min_ != float(i.attrib["area"]) : del i.attrib["zeuz"]

    def Remove_attribs(self, root):
        for each in root:
            att = each.attrib
            if "found" in att: del att["found"]
            if "area" in att: del att["area"]
            if "pattern_list" in att: del att["pattern_list"]
            if "Value" in att: del att["Value"]
            self.Remove_attribs(each)

    def get_element_at_position(self, x, y):
        """Get the element at the specified coordinates"""
        self.x = x
        self.y = y
        
        windows = AutomationElement.RootElement.FindAll(TreeScope.Children, Condition.TrueCondition)
        if windows.Count == 0:
            return None, None
            
        for window in windows:
            if window.Current.Name.strip() in ("Annotation - Zoom"): 
                continue
            if self._found(window):
                window_name = self._sanitize_text(window.Current.Name)
                window_automationid = self._sanitize_text(window.Current.AutomationId)
                window_class = self._sanitize_text(window.Current.ClassName)
                window_control = self._sanitize_text(window.Current.LocalizedControlType)
                try:
                    pid = window.Current.ProcessId
                except:
                    pid = ""
                    
                attribs = {
                    "Name": window_name,
                    "AutomationId": window_automationid,
                    "LocalizedControlType": window_control,
                    "ClassName": window_class,
                    "pid": str(pid),
                }
                root = ET.Element("body", **attribs)
                return root, window
                
        return None, None
    
    def clear_tree(self, root):
        self.Remove_zeuz_aiplugin(root)
        self.Remove_attribs(root)
        ET.indent(root, "")
        self.xml_str = ET.tostring(root).decode().encode('ascii', 'ignore').decode()

    def inspect_element(self, x, y):
        """Main inspection function that can be called from UI"""
        root, window = self.get_element_at_position(x, y)
        if root is None or window is None:
            return lambda: None
            
        self.window_name = self._sanitize_text(window.Current.Name)
        self.create_tree(root, window, 0)
        try: 
            ET.indent(root)
        except AttributeError: 
            pass
            
        self.xml_str = ET.tostring(root).decode().encode('ascii', 'ignore').decode()
        
        with open("Element.xml", "w") as f:
            f.write(self.xml_str)
            
        self.Remove_coordinate(root)
        
        tree = Tree(f"[cyan]{self.create_tag(root)}", guide_style="red")
        self.printTree(root, tree)
        print(tree)
        
        self.exact_path_maker(root, [], [], True)
        
        def cleanup():
            self.Remove_zeuz_aiplugin(root)
            self.Remove_attribs(root)
            ET.indent(root, "")
            self.xml_str = ET.tostring(root).decode().encode('ascii', 'ignore').decode()
        
        return cleanup
        
    def _found(self, Element):
        """Check if element is at current coordinates"""
        try:
            left = Element.Current.BoundingRectangle.Left
            right = Element.Current.BoundingRectangle.Right
            bottom = Element.Current.BoundingRectangle.Bottom
            top = Element.Current.BoundingRectangle.Top
            if left <= self.x <= right and top <= self.y <= bottom:
                return True
            return False
        except Exception:
            print(sys.exc_info())
            return False
            
    def _sanitize_text(self, text):
        """Sanitize XML text"""
        return (text.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace('"', "&quot;")
                   .replace("'", "&apos;"))

def main():
    inspector = WindowsInspector()
    try:
        
        while True:
            pause()
            x, y = inspect()
            
            print("Searching for the Element identifier")
            cleanup = inspector.inspect_element(x, y)
            cleanup()
            Authenticate(inspector.xml_str, inspector.window_name, inspector.paths[0]["path"])
            
    except:
        traceback.print_exc()

if __name__ == "__main__":
    main()