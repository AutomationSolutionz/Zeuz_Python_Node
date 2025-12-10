import hashlib
import os
import subprocess
import base64
import json
from typing import Literal
import asyncio

import requests
from fastapi import APIRouter
from pydantic import BaseModel

from Framework.Utilities import ConfigModule, CommonUtil

ADB_PATH = "adb"  # Ensure ADB is in PATH
UI_XML_PATH = "ui.xml"
SCREENSHOT_PATH = "screen.png"
IOS_SCREENSHOT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ios_screen.png")

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
    name: str | None = None


class IOSDeviceInfo(BaseModel):
    """Model for iOS device information."""
    udid: str
    name: str
    state: str
    runtime: str
    device_type: str

@router.get("/devices", response_model=list[DeviceInfo])
def get_devices():
    """Get list of connected Android devices."""
    try:
        # Get list of devices
        devices_output = run_adb_command(f"{ADB_PATH} devices -l")
        devices = []

        # Parse adb devices output
        index = 1
        for line in devices_output.split("\n")[1:]:  # Skip first line (header)
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    serial = parts[0]
                    status = parts[1]
                    name = f"device {index}"
                    index += 1
                    # model = run_adb_command(f"{ADB_PATH} -s {serial} shell getprop ro.product.model")
                    # product = run_adb_command(f"{ADB_PATH} -s {serial} shell getprop ro.product.name")

                    devices.append(DeviceInfo(serial=serial, status=status, name=name))

        return devices
    except Exception as e:
        return []


@router.get("/ios/devices", response_model=list[IOSDeviceInfo])
def get_ios_devices():
    """Get list of available iOS simulators."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "-j"],
            capture_output=True, text=True, check=True
        )
        
        devices_data = json.loads(result.stdout)
        ios_devices = []
        
        for runtime, devices in devices_data.get("devices", {}).items():
            for device in devices:
                if device.get("isAvailable", False):
                    ios_devices.append(IOSDeviceInfo(
                        udid=device["udid"],
                        name=device["name"],
                        state=device["state"],
                        runtime=runtime,
                        device_type=device.get("deviceTypeIdentifier", "Unknown")
                    ))
        
        return ios_devices
    except Exception as e:
        return []


@router.get("/inspect")
def inspect(device_serial: str | None = None):
    """Get the Mobile DOM and screenshot."""
    try:
        # Capture UI and screenshot
        capture_ui_dump(device_serial=device_serial)
        capture_screenshot(device_serial=device_serial)

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


@router.get("/ios/inspect")
def inspect_ios(device_udid: str | None = None):
    """Get iOS simulator screenshot and XML hierarchy."""
    try:
        # Get first booted device if none specified
        if not device_udid:
            ios_devices = get_ios_devices()
            if not ios_devices:
                return InspectorResponse(
                    status="error",
                    error="No iOS simulators available"
                )
            
            # Find first booted device
            booted_devices = [d for d in ios_devices if d.state == "Booted"]
            if not booted_devices:
                return InspectorResponse(
                    status="error",
                    error="No booted iOS simulators found. Please start an iOS simulator."
                )
            device_udid = booted_devices[0].udid
        
        # Capture screenshot
        capture_ios_screenshot(device_udid)
        
        # Read and encode screenshot
        with open(IOS_SCREENSHOT_PATH, 'rb') as img_file:
            screenshot_bytes = img_file.read()
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
        return InspectorResponse(
            status="ok",
            ui_xml=None,  # XML hierarchy will be implemented later
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


def capture_ui_dump(device_serial: str | None = None):
    """Capture the current UI hierarchy from the device"""
    device_flag = f"-s {device_serial}" if device_serial else ""
    out = run_adb_command(
        f"{ADB_PATH} {device_flag} shell uiautomator dump /sdcard/ui.xml".strip()
    )
    if out.startswith("Error:"):
        from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions import appium_driver
        if appium_driver is None:
            return
        page_src = appium_driver.page_source
        with open(UI_XML_PATH, 'w') as xml_file:
            xml_file.write(page_src)
    else:
        out = run_adb_command(
            f"{ADB_PATH} {device_flag} pull /sdcard/ui.xml {UI_XML_PATH}"
        )
        if out.startswith("Error:"):
            return


def capture_screenshot(device_serial: str | None = None):
    """Capture the current UI hierarchy from the device"""
    device_flag = f"-s {device_serial}" if device_serial else ""
    out = run_adb_command(
        f"{ADB_PATH} {device_flag} shell screencap -p /sdcard/screen.png".strip()
    )
    if out.startswith("Error:"):
        from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions import appium_driver
        if appium_driver is None:
            return
        full_screenshot_path = os.path.join(os.getcwd(), SCREENSHOT_PATH)
        appium_driver.save_screenshot(full_screenshot_path)
    else:
        out = run_adb_command(
            f"{ADB_PATH} {device_flag} pull /sdcard/screen.png {SCREENSHOT_PATH}"
        )
        if out.startswith("Error:"):
            return


def capture_ios_screenshot(device_udid: str):
    """Capture screenshot from iOS simulator."""
    try:
        # Use absolute path
        screenshot_path = os.path.abspath(IOS_SCREENSHOT_PATH)
        
        # Remove existing file if it exists
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
            
        result = subprocess.run(
            ["xcrun", "simctl", "io", device_udid, "screenshot", "--type=png", screenshot_path],
            capture_output=True, text=True, check=True
        )
        
        # Verify file was created
        if not os.path.exists(screenshot_path):
            raise Exception("Screenshot file was not created")
            
        return True
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to capture iOS screenshot: {e.stderr}")
    except Exception as e:
        raise Exception(f"Failed to capture iOS screenshot: {str(e)}")


def run_xcrun_command(command):
    """Run an xcrun command and return the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"


async def upload_android_ui_dump():
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
                        await asyncio.sleep(5)
                        continue
                    prev_xml_hash = new_xml_hash

            except FileNotFoundError:
                await asyncio.sleep(5)
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
        await asyncio.sleep(5)
