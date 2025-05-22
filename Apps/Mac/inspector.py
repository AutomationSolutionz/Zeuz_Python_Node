import sys
import os
from textwrap import dedent
import requests
import json
from configobj import ConfigObj
from pathlib import Path
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
        self.xml_path: str = ""

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
                rich_print(f"Captured at x={point.x}, y={point.y}")
                self.x, self.y = round(point.x), round(point.y)
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
        response = requests.get(url).json()
        print('url', url)
        print('response', response)
        if response["status"] == "ok":
            self.response = response["ui_xml"]
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
    
    def run(self):
        while True:
            # input("Press any key to start capturing...")
            self.wait_for_control_press()
            self.get_frontmost_app()
            self.get_server_port()
            self.get_dump()
            if not self.page_src:
                continue

            time.sleep(0.2)
                

def main():
    inspector = Inspector()
    inspector.run()

if __name__ == "__main__":
    main()
