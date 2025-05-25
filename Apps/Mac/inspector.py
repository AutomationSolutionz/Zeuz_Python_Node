import sys
import os
from textwrap import dedent
import requests
import json
from configobj import ConfigObj
from pathlib import Path
import traceback
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

print(f"Python Version: {sys.version}")
print(f"Python Path: {sys.executable}")
print(f"Current file path: {os.path.abspath(__file__)}")

from rich import print as rich_print
from rich.text import Text
from rich.tree import Tree
from colorama import Fore, init as colorama_init
colorama_init(autoreset=True)

import ctypes
import objc
from Foundation import NSObject
from Quartz import (
    CoreGraphics, 
    CGEventSourceFlagsState, 
    kCGEventSourceStateHIDSystemState, 
    kCGEventFlagMaskControl, 
    CGWindowListCopyWindowInfo, 
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID
)
from AppKit import NSEvent, NSControlKeyMask
import time

import xml.etree.ElementTree as ET

# AXUIElement types
AXUIElementRef = objc.objc_object

# Load the AX API
ApplicationServices = objc.loadBundle("ApplicationServices",
    globals(),
    bundle_path="/System/Library/Frameworks/ApplicationServices.framework"
)
# AX, _ = objc.loadBundleFunctions(ApplicationServices, globals(), [
#     ("AXUIElementCreateApplication", b"^{__AXUIElement=}(i)")
# ])

AX = objc.loadBundleFunctions(ApplicationServices, globals(), [
    ("AXUIElementCreateSystemWide", b"^{__AXUIElement=}"),
    ("kAXFocusedUIElementAttribute", b"^{__CFString=}"),
    ("AXUIElementCopyAttributeValue", b"i^{__AXUIElement=}^{__CFString=}^@"),
    ("AXUIElementCopyAttributeNames", b"i^{__AXUIElement=}^{__CFArray=}"),
    ("AXUIElementCopyElementAtPosition", b"i^{__AXUIElement=}dd^@"),
    ("AXUIElementCreateApplication", b"^{__AXUIElement=}" + b"i")
])

settings_conf_path = str(Path(__file__).parent.parent.parent / "Framework" / "settings.conf")
print(f"Settings config path: {settings_conf_path}")

def get_mouse_position():
    event = CoreGraphics.CGEventCreate(None)
    loc = CoreGraphics.CGEventGetLocation(event)
    x, y = round(loc.x), round(loc.y)
    return x, y


class App:
    def __init__(self, name: str, bundle_id: str, pid: int, window_title: str):
        self.name = name
        self.bundle_id = bundle_id
        self.pid = pid
        self.window_title = window_title
    
    def __str__(self):
        return Fore.GREEN + dedent(f"""
        App(
            name={self.name},
            bundle_id={self.bundle_id},
            pid={self.pid},
            window_title={self.window_title},
        )""")

class Inspector:
    def __init__(self):
        self.x: int = -1
        self.y: int = -1
        self.app: App = App(name="", bundle_id="", pid=-1, window_title="")
        self.xml_str: str = ""
        self.xml_tree: ET.ElementTree = None

        self.server_address: str = "http://127.0.0.1"
        self.server_path: str = "/api/v1/mac/dump/driver"
        self.server_port: int = 18100
        self.page_src: str = ""
    def wait_for_control_press(self):
        print("Hover over the element and press ⌃ Control key...")
        while True:
            flags = CGEventSourceFlagsState(kCGEventSourceStateHIDSystemState)
            if flags & kCGEventFlagMaskControl:
                point = NSEvent.mouseLocation()
                height = NSScreen.mainScreen().frame().size.height
                x = round(point.x)
                y = round(height - point.y)
                rich_print(f"Captured at x={x}, y={y}")
                self.x, self.y = x, y
                return
            time.sleep(0.1)

    def get_frontmost_app(self):
        window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
        for window in window_list:
            if window.get("kCGWindowLayer") == 0 and window.get("kCGWindowOwnerName"):
                app_name = window["kCGWindowOwnerName"]
                pid = window["kCGWindowOwnerPID"]
                app = NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
                bundle_id = app.bundleIdentifier()
                window_title = window.get("kCGWindowName", "")
                self.app = App(name=app_name, bundle_id=bundle_id, pid=pid, window_title=window_title)
                print(self.app)
                break
    
    def get_server_port(self):
        config = ConfigObj(settings_conf_path)
        self.server_port =  config["server"]["port"]
    
    def get_dump(self):
        url = f"{self.server_address}:{self.server_port}{self.server_path}"
        try:
            response = requests.get(url).json()
        except requests.exceptions.ConnectionError:
            print(Fore.RED + "Failed to connect to the server. Please launch the Zeuz Node first and launch an app")
            return
        if response["status"] == "ok":
            self.page_src = response["ui_xml"]
            print(Fore.GREEN + f"Successfully got dump from appium driver")
        elif response["status"] == "not_found":
            print(Fore.GREEN + f"You have not launched any app yet. Launch app with the following action:")
            action = [
                {
                    "action_name":f"Launch {self.app.name}",
                    "action_disabled":"true",
                    "step_actions":[
                        ["macos app bundle id","element parameter",self.app.bundle_id],
                        ["launch","appium action","launch"]
                    ]
                }
            ]
            print(Fore.CYAN + json.dumps(action, indent=4))
            self.page_src = ""
        else:
            print(Fore.RED + f"Error: {response['error']}")
            self.page_src = ""

    def render_tree(self):
        print('rendertree')
        if not self.page_src:
            return

        root = ET.fromstring(self.page_src)
        tree = Tree(f"[bold green]{self.app.name} ({self.app.bundle_id})")
        self.xml_tree = tree

        def check_bounding_box(element):
            if element.attrib.get('x') and element.attrib.get('y') and element.attrib.get('width') and element.attrib.get('height'):
                x = int(element.attrib.get('x'))
                y = int(element.attrib.get('y'))
                width = int(element.attrib.get('width'))
                height = int(element.attrib.get('height'))
                if (self.x >= x and 
                    self.x <= x + width and 
                    self.y >= y and 
                    self.y <= y + height
                ):
                    return True
            return False

        def get_attribute_string(element):
            ignore = ['x', 'y', 'width', 'height']
            return " ".join([f'{k}="{v}"' for k, v in element.attrib.items() if k not in ignore])

        def set_single_zeuz_apiplugin(root):
            elements = root.findall(".//*[@zeuz='aiplugin']")
            if len(elements) > 1:
                element_areas = []
                for element in elements:
                    width = int(element.attrib.get('width', 0))
                    height = int(element.attrib.get('height', 0))
                    area = width * height
                    element_areas.append((element, area))
                
                element_areas.sort(key=lambda x: x[1])
                for element, _ in element_areas[1:]:
                    del element.attrib['zeuz']
        
        def remove_coordinates(node):
            remove = ['x', 'y', 'width', 'height']
            for child in node:
                for attrib in list(child.attrib):
                    if attrib in remove:
                        del child.attrib[attrib]
                remove_coordinates(child)

        def build_tree(element, parent_tree):
            element_tag = element.tag
            ignore = ['x', 'y', 'width', 'height']
            element_attribs = get_attribute_string(element)
            element_coords = f"x={element.attrib.get('x', '')}, y={element.attrib.get('y', '')}, w={element.attrib.get('width', '')}, h={element.attrib.get('height', '')}"
            recorded_coords = f"self.x={self.x}, self.y={self.y}"

            if check_bounding_box(element):
                if not any(check_bounding_box(child) for child in element):
                    area = int(element.attrib.get('width', '1')) * int(element.attrib.get('height', '1'))
                    label = f"[bold blue]{element_tag}: [green]{element_attribs} [dim]({element_coords} Area: {area} {recorded_coords})"
                    element.set('zeuz', 'aiplugin')
                else:
                    label = f"[bold blue]{element_tag}: [yellow]{element_attribs}"

            else:
                label = f"[bold]{element_tag}: {element_attribs}"
            node = parent_tree.add(label)

            for child in element:
                if check_bounding_box(child):
                    build_tree(child, node)
                else:
                    node.add(f"[bold]{child.tag}: {get_attribute_string(child)}")

        build_tree(root, tree)
        set_single_zeuz_apiplugin(root)
        rich_print(tree)
        remove_coordinates(root)
        self.xml_str = ET.tostring(root).decode().encode('ascii', 'ignore').decode()


        ''' Comment out the below code to check if tree contains single zeuz apiplugin '''
        # tree2 = Tree(f"[bold green]{self.app.name} ({self.app.bundle_id})")
        # build_tree(root, tree2)
        # rich_print(tree2)
    def send_to_server(self):
        config = ConfigObj(settings_conf_path)
        api_key = config["Authentication"]["api-key"].strip()
        server = config["Authentication"]["server_address"].strip()

        if not api_key or not server:
            print(Fore.RED + "API key or server address is not set. Please launch the Zeuz Node first and login")
            return
        url = f"{self.server_address}:{self.server_port}{self.server_path}"
        try:
            url = server + "/" if server[-1] != "/" else server
            url += "ai_record_single_action/"
            print(url)
            content = json.dumps({
                'page_src': self.xml_str,
                "action_type": "android",
            })
            headers = {
                "X-Api-Key": api_key,
            }

            r = requests.request("POST", url, headers=headers, data=content, verify=False)
            response = r.json()
            if response["info"] == "success":
                r.ok and print("Element sent. You can " + Fore.GREEN + "'Add by AI' " + Fore.RESET + "from server")
            else:
                print(Fore.RED + response["info"])
        except:
            traceback.print_exc()
            print(Fore.RED + "Failed to send content to AI Engine")
            return

    def run(self):
        while True:
            input("Press any key to start capturing...")
            self.wait_for_control_press()
            self.get_frontmost_app()
            self.get_server_port()
            if self.server_port == 0:
                print(Fore.RED + "Server port is not set. Please launch the Zeuz Node first and launch an app")
                continue
            self.get_dump()
            if not self.page_src:
                continue
            self.render_tree()
            self.send_to_server()

            time.sleep(0.2)
                

def main():
    inspector = Inspector()
    inspector.run()

if __name__ == "__main__":
    main()
