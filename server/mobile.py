import hashlib
import os
import subprocess
import base64
import time
from typing import Literal

# modification to suppress appium logs at startup
import sys
from contextlib import contextmanager

import requests
from fastapi import APIRouter
from pydantic import BaseModel

from Framework.Utilities import ConfigModule, CommonUtil

ADB_PATH = "adb"  # Ensure ADB is in PATH
UI_XML_PATH = "ui.xml"
SCREENSHOT_PATH = "screen.png"

router = APIRouter(prefix="/mobile", tags=["mobile"])


class InspectorResponse(BaseModel):
    """Response model for the /inspector endpoint."""

    status: Literal["ok", "error"] = "ok"
    ui_xml: str | None = None
    screenshot: str | None = None  # Base64 encoded image
    error: str | None = None


class DeviceInfo(BaseModel):
    """Model for device information."""
    serial: str
    status: str
    # model: str | None = None
    # product: str | None = None

@router.get("/devices", response_model=list[DeviceInfo])
def get_devices():
    """Get list of connected Android devices."""
    try:
        # Get list of devices
        devices_output = run_adb_command(f"{ADB_PATH} devices -l")
        devices = []
        
        # Parse adb devices output
        for line in devices_output.split('\n')[1:]:  # Skip first line (header)
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    serial = parts[0]
                    status = parts[1]
                    # model = run_adb_command(f"{ADB_PATH} -s {serial} shell getprop ro.product.model")
                    # product = run_adb_command(f"{ADB_PATH} -s {serial} shell getprop ro.product.name")

                    devices.append(DeviceInfo(
                        serial=serial,
                        status=status
                    ))
                        
        return devices
    except Exception as e:
        return []

@router.get("/inspect")
def inspect():
    """Get the Mobile DOM and screenshot."""
    try:
        # Capture UI and screenshot
        capture_ui_dump()
        capture_screenshot()

        # Read XML file
        with open(UI_XML_PATH, 'r') as xml_file:
            xml_content = xml_file.read()
            
        # Read and encode screenshot
        with open(SCREENSHOT_PATH, 'rb') as img_file:
            screenshot_bytes = img_file.read()
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
        return InspectorResponse(
            status="ok",
            ui_xml=xml_content,
            screenshot=screenshot_base64
        )
    except Exception as e:
        return InspectorResponse(
            status="error",
            error=str(e)
        )

@router.get("/dump/driver")
def dump_driver():
    """Dump the current driver."""
    from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions import appium_driver
    if appium_driver is None:
        return
    return appium_driver.page_source


def run_adb_command(command):
    """Run an ADB command and return the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"


def capture_ui_dump():
    """Capture the current UI hierarchy from the device"""
    out = run_adb_command(f"{ADB_PATH} shell uiautomator dump /sdcard/ui.xml")
    if out.startswith("Error:"):
        from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions import appium_driver
        if appium_driver is None:
            return
        page_src = appium_driver.page_source
        with open(UI_XML_PATH, 'w') as xml_file:
            xml_file.write(page_src)
    else:
        out = run_adb_command(f"{ADB_PATH} pull /sdcard/ui.xml {UI_XML_PATH}")
        if out.startswith("Error:"):
            return


def capture_screenshot():
    """Capture the current UI hierarchy from the device"""
    out = run_adb_command(f"{ADB_PATH} shell screencap -p /sdcard/screen.png")
    if out.startswith("Error:"):
        from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions import appium_driver
        if appium_driver is None:
            return
        full_screenshot_path = os.path.join(os.getcwd(), SCREENSHOT_PATH)
        appium_driver.save_screenshot(full_screenshot_path)
    else:
        out = run_adb_command(f"{ADB_PATH} pull /sdcard/screen.png {SCREENSHOT_PATH}")
        if out.startswith("Error:"):
            return


def upload_android_ui_dump():
    prev_xml_hash = ""
    while True:
        try:
            capture_ui_dump()
            try:
                with open(UI_XML_PATH, 'r') as xml_file:
                    xml_content = xml_file.read()
                    xml_content = xml_content.replace("<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>", "", 1)
                    new_xml_hash = hashlib.sha256(xml_content.encode('utf-8')).hexdigest()
                    # Don't upload if the content hasn't changed
                    if prev_xml_hash == new_xml_hash:
                        time.sleep(5)
                        continue
                    prev_xml_hash = new_xml_hash

            except FileNotFoundError:
                time.sleep(5)
                continue
            url = ConfigModule.get_config_value("Authentication", "server_address").strip() + "/node_ai_contents/"
            apiKey = ConfigModule.get_config_value("Authentication", "api-key").strip()
            res = requests.post(
                url,
                headers={"X-Api-Key": apiKey},
                json={
                    "dom_mob": {"dom": xml_content},
                    "node_id": CommonUtil.MachineInfo().getLocalUser().lower()
                })
            if res.ok:
                CommonUtil.ExecLog("", "UI dump uploaded successfully", iLogLevel=1)
        except Exception as e:
            CommonUtil.ExecLog("", f"Error uploading UI dump: {str(e)}", iLogLevel=3)
        time.sleep(5)


#modification here to stop appium logs at startup
@contextmanager
def suppress_stdout():
    """Temporarily suppress print statements"""
    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    try:
        yield
    finally:
        sys.stdout.close()
        sys.stdout = old_stdout

def quiet_upload_android_ui_dump():
    """Run first cycle with stdout suppressed, then continue normally"""

    with suppress_stdout():
        try:
            capture_ui_dump()
            capture_screenshot()
        finally:
            pass

    # now continue with normal infinite loop
    upload_android_ui_dump()
