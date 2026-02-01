import asyncio
import base64
import hashlib
import os
import shutil
import subprocess
import base64
import json
from typing import Literal, Optional
import asyncio
import socket
import xml.etree.ElementTree as ET
import zipfile
import plistlib

import requests
from androguard.core.apk import APK
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

import sys
import logging
from Framework.Utilities import CommonUtil, ConfigModule
from settings import ZEUZ_NODE_DOWNLOADS_DIR

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Framework', 'Built_In_Automation', 'Mobile', 'CrossPlatform', 'Appium'))
ADB_PATH = "adb"  # Ensure ADB is in PATH
UI_XML_PATH = "ui.xml"
SCREENSHOT_PATH = "screen.png"
IOS_SCREENSHOT_PATH = "ios_screen.png"
IOS_XML_PATH = "ios_ui.xml"

router = APIRouter(prefix="/mobile", tags=["mobile"])


def is_wda_running(port: int) -> bool:
    """Check if WebDriverAgent is running on given port."""
    try:
        response = requests.get(f"http://localhost:{port}/status", timeout=1)
        return response.status_code == 200
    except:
        return False


class InspectorResponse(BaseModel):
    """Response model for the /inspector endpoint."""
    status: Literal["ok", "error"] = "ok"
    ui_xml: str | None = None
    screenshot: str | None = None  # Base64 encoded image
    bundle_identifier: str | None = None
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
    """Get list of booted iOS simulators only."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "-j"],
            capture_output=True, text=True, check=True
        )
        
        devices_data = json.loads(result.stdout)
        ios_devices = []
        
        for runtime, devices in devices_data.get("devices", {}).items():
            for device in devices:
                # Only return booted devices
                if device.get("isAvailable", False) and device.get("state") == "Booted":
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
        with open(UI_XML_PATH, "r") as xml_file:
            xml_content = xml_file.read()

        # Read and encode screenshot
        with open(SCREENSHOT_PATH, "rb") as img_file:
            screenshot_bytes = img_file.read()
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        return InspectorResponse(
            status="ok", ui_xml=xml_content, screenshot=screenshot_base64
        )
    except Exception as e:
        return InspectorResponse(status="error", error=str(e))



@router.post("/ios/start-services")
def start_ios_services():
    try:
        ios_devices = get_ios_devices()
        if not ios_devices:
            return {"status": "error", "error": "No booted iOS simulators"}
        
        device_udid = ios_devices[0].udid
        
        # Check if WDA is already running
        wda_port = 8100
        tries = 0
        while tries < 20:
            if not is_wda_running(wda_port):
                break
            wda_port += 2
            tries += 1
        
        if tries >= 20:
            return {"status": "error", "error": "No available WDA ports"}
        
        result = subprocess.run(
            ["xcrun", "simctl", "launch", device_udid, "com.facebook.WebDriverAgentRunner.xctrunner"],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            return {"status": "error", "error": f"Failed to launch WDA."}
        
        return {"status": "ok", "port": wda_port}
            
    except Exception as e:
        logging.exception("Failed to start iOS services")
        return {"status": "error", "error": "Failed to start iOS services"}


def extract_bundle_id_from_xml(xml_content: str) -> str | None:
    try:
        root = ET.fromstring(xml_content)
        return root.get('bundleId')
    except Exception:
        return None


@router.get("/ios/inspect")
def inspect_ios(device_udid: str | None = None):
    """Get iOS simulator screenshot and XML hierarchy."""
    try:
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
        
        capture_ios_ui_dump(device_udid)
        capture_ios_screenshot(device_udid)
        
        with open(IOS_XML_PATH, 'r', encoding='utf-8') as xml_file:
            xml_content = xml_file.read()
        
        # Extract bundle identifier from XML content
        bundle_id = extract_bundle_id_from_xml(xml_content)
            
        with open(IOS_SCREENSHOT_PATH, 'rb') as img_file:
            screenshot_bytes = img_file.read()
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
        return InspectorResponse(
            status="ok",
            ui_xml=xml_content,
            screenshot=screenshot_base64,
            bundle_identifier=bundle_id
        )
    except Exception as e:
        return InspectorResponse(
            status="error",
            error=str(e)
        )


@router.get("/dump/driver")
def dump_driver():
    """Dump the current driver."""
    from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions import (
        appium_driver,
    )

    if appium_driver is None:
        return
    return appium_driver.page_source


def run_adb_command(command):
    """Run an ADB command and return the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
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
        from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions import (
            appium_driver,
        )

        if appium_driver is None:
            return
        page_src = appium_driver.page_source
        with open(UI_XML_PATH, "w") as xml_file:
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
        from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions import (
            appium_driver,
        )

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
    try:
        screenshot_path = os.path.abspath(IOS_SCREENSHOT_PATH)
        
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
            
        result = subprocess.run(
            ["xcrun", "simctl", "io", device_udid, "screenshot", "--type=png", screenshot_path],
            capture_output=True, text=True, check=True
        )
        
        if not os.path.exists(screenshot_path):
            raise Exception("Screenshot file was not created")
            
        return True
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to capture iOS screenshot: {e.stderr}")
    except Exception as e:
        raise Exception(f"Failed to capture iOS screenshot: {str(e)}")


def get_real_ios_hierarchy(device_udid: str):
    try:
        import requests
        
        wda_port = 8100
        tries = 0
        
        while tries < 20:
            try:
                wda_url = f"http://localhost:{wda_port}"
                
                # Quick status check
                status_response = requests.get(f"{wda_url}/status", timeout=1)
                if status_response.status_code != 200:
                    wda_port += 2
                    tries += 1
                    continue
                
                # existing sessions first
                sessions_response = requests.get(f"{wda_url}/sessions", timeout=1)
                if sessions_response.status_code == 200:
                    sessions = sessions_response.json()
                    if sessions and len(sessions) > 0:
                        session_id = sessions[0]['id']
                        source_response = requests.get(f"{wda_url}/session/{session_id}/source", timeout=3)
                        if source_response.status_code == 200:
                            return source_response.text
                
                # direct source
                source_response = requests.get(f"{wda_url}/source", timeout=2)
                if source_response.status_code == 200:
                    return source_response.text
                    
            except:
                wda_port += 2
                tries += 1
                continue
                
    except:
        pass
        
    return None


def capture_ios_ui_dump(device_udid: str):
    real_hierarchy = get_real_ios_hierarchy(device_udid)
    if real_hierarchy:
        try:
            import json
            json_data = json.loads(real_hierarchy)
            xml_content = json_data.get("value", real_hierarchy)
        except:
            xml_content = real_hierarchy
            
        with open(IOS_XML_PATH, 'w', encoding='utf-8') as xml_file:
            xml_file.write(xml_content)
        return
    
    # Fallback to Appium driver
    try:
        from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions import appium_driver
        if appium_driver is not None:
            page_src = appium_driver.page_source
            with open(IOS_XML_PATH, 'w', encoding='utf-8') as xml_file:
                xml_file.write(page_src)
            return
    except:
        pass


async def upload_android_ui_dump():
    prev_xml_hash = ""
    while True:
        try:
            capture_ui_dump()
            try:
                with open(UI_XML_PATH, "r") as xml_file:
                    xml_content = xml_file.read()
                    xml_content = xml_content.replace(
                        "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>",
                        "",
                        1,
                    )
                    new_xml_hash = hashlib.sha256(
                        xml_content.encode("utf-8")
                    ).hexdigest()
                    # Don't upload if the content hasn't changed
                    if prev_xml_hash == new_xml_hash:
                        await asyncio.sleep(5)
                        continue
                    prev_xml_hash = new_xml_hash

            except FileNotFoundError:
                await asyncio.sleep(5)
                continue
            url = (
                ConfigModule.get_config_value(
                    "Authentication", "server_address"
                ).strip()
                + "/node_ai_contents/"
            )
            apiKey = ConfigModule.get_config_value("Authentication", "api-key").strip()
            res = requests.post(
                url,
                headers={"X-Api-Key": apiKey},
                json={
                    "dom_mob": {"dom": xml_content},
                    "node_id": CommonUtil.MachineInfo().getLocalUser().lower(),
                },
            )
            if res.ok:
                CommonUtil.ExecLog("", "UI dump uploaded successfully", iLogLevel=1)
        except Exception as e:
            CommonUtil.ExecLog("", f"Error uploading UI dump: {str(e)}", iLogLevel=3)
        await asyncio.sleep(5)


async def upload_ios_ui_dump():
    prev_xml_hash = ""
    while True:
        try:
            ios_devices = get_ios_devices()
            if not ios_devices:
                await asyncio.sleep(5)
                continue
            
            device_udid = ios_devices[0].udid
            capture_ios_ui_dump(device_udid)
            
            try:
                with open(IOS_XML_PATH, 'r', encoding='utf-8') as xml_file:
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
            CommonUtil.ExecLog("", f"Error uploading iOS UI dump: {str(e)}", iLogLevel=3)
        await asyncio.sleep(5)
        
        
@router.post("/apk-upload")
def handle_apk_upload(file: UploadFile = File(...)):
    dir_path = f"{ZEUZ_NODE_DOWNLOADS_DIR}/apk"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    filename = file.filename or "uploaded.apk"
    file_path = os.path.join(dir_path, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "APK uploaded successfully", "filename": filename}


def get_package_name(file_path: str) -> str | None:
    """Extract package name from APK using androguard."""
    try:
        apk = APK(file_path)
        return apk.get_package()
    except Exception:
        return None


@router.post("/apk-install")
def handle_apk_install(filename: str, serial: str):
    dir_path = f"{ZEUZ_NODE_DOWNLOADS_DIR}/apk"
    file_path = os.path.join(dir_path, filename)
    if not os.path.exists(file_path):
        return {"message": "APK not found", "filename": filename}
    package_name = get_package_name(file_path)
    try:
        subprocess.run([ADB_PATH, "-s", serial, "install", file_path], check=True)
        return {"message": "APK installed successfully", "filename": filename, "package_name": package_name}
    except Exception as e:
        return {"message": f"Error installing APK: {str(e)}", "filename": filename, "package_name": package_name}


@router.get("/package-installed")
def check_package_installed(package_name: str, serial: str | None = None):
    """Check if an android package is installed on the device."""
    try:
        device_flag = f"-s {serial}" if serial else ""
        result = run_adb_command(
            f"{ADB_PATH} {device_flag} shell pm list packages {package_name}".strip()
        )
        if result.startswith("Error:"):
            return {"installed": False, "package_name": package_name, "error": result}
        
        # pm list packages returns lines like "package:com.example.app"
        # Check if the exact package is in the output
        installed_packages = [line.replace("package:", "") for line in result.split("\n") if line.startswith("package:")]
        is_installed = package_name in installed_packages
        
        return {"installed": is_installed, "package_name": package_name}
    except Exception as e:
        return {"installed": False, "package_name": package_name, "error": str(e)}


@router.post("/ios/app-upload")
def handle_ios_app_upload(file: UploadFile = File(...)):
    dir_path = f"{ZEUZ_NODE_DOWNLOADS_DIR}/ios-app"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        
    filename = file.filename or "uploaded.app"
    filepath = os.path.join(dir_path, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"message": "App uploaded successfully", "filename": filename}


def normalized_ios_app_path(file_path: str) -> Optional[str]:
    """
    ensure that we ended up with a .app directory even if user provided .ipa
    """
    if not os.path.exists(file_path):
        return None
    
    # if already .app
    if file_path.endswith(".app") and os.path.isdir(file_path):
        return file_path
    
    # .ipa, so we have to extract to get .app
    if file_path.endswith(".ipa"):
        extract_dir = file_path.replace(".ipa", "_extracted")
        zip_path = file_path.replace(".ipa", ".zip")

        # copy instead of rename to avoid breaking original file
        shutil.copy(file_path, zip_path)
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
            
        payload_dir = os.path.join(extract_dir, "Payload")
        if not os.path.isdir(payload_dir):
            return None
        
        for item in os.listdir(payload_dir):
            if item.endswith(".app"):
                return os.path.join(payload_dir, item)
        
        return None
    
    # extract zip because 'test.app' is not a file, so browser zip that before send to me
    if file_path.endswith(".app.zip") or file_path.endswith(".zip"):
        extract_dir = file_path + "_extracted"
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        # search recursively for .app folder so it will pick very first .app folder
        for root, dirs, files in os.walk(extract_dir):
            for d in dirs:
                if d.endswith(".app") and os.path.isdir(os.path.join(root, d)):
                    return os.path.join(root, d)

        return None

    return None


def extract_bundle_id_from_app(app_path: str) -> Optional[str]:
    """
    Reads CFBundleIdentifier from Info.plist inside .app bundle
    """
    info_plist_path = os.path.join(app_path, "Info.plist")

    if not os.path.exists(info_plist_path):
        return None
    
    try:
        with open(info_plist_path, "rb") as f:
            plist_data = plistlib.load(f)
            return plist_data.get("CFBundleIdentifier")
    except Exception:
        return None


@router.post("/ios/app-install")
def handle_ios_app_install(filename: str, sim_udid: str):
    """
    handling the ios app installation in the simolator
    """
    dirpath = f"{ZEUZ_NODE_DOWNLOADS_DIR}/ios-app"
    filepath = os.path.join(dirpath, filename)
    if not os.path.exists(filepath):
        return {"message": "App not found", "filename": filename}
    
    app_path = normalized_ios_app_path(filepath)
    if not app_path:
        return {"message": "Failed to normalize .app", "filename": filename}
    
    bundle_id = extract_bundle_id_from_app(app_path)
    
    try:
        # uninstall if already exists
        try:
            subprocess.run(
                ["xcrun", "simctl", "uninstall", sim_udid, bundle_id],
                capture_output=True, text=True, timeout=30
            )
        except:
            pass  # Ignore uninstall errors
        
        # Install the app
        result = subprocess.run(
            ["xcrun", "simctl", "install", sim_udid, app_path],
            capture_output=True, text=True, check=True, timeout=120
        )
        
        # Verify installation
        verify_result = subprocess.run(
            ["xcrun", "simctl", "get_app_container", sim_udid, bundle_id],
            capture_output=True, text=True, timeout=30
        )
        
        if verify_result.returncode != 0:
            return {
                "message": f"App installed but verification failed: {verify_result.stderr}",
                "filename": filename,
                "bundle_id": bundle_id,
            }
        
        return {
            "message": "App installed successfully",
            "filename": filename,
            "bundle_id": bundle_id,
        }
    except subprocess.CalledProcessError as e:
        return {
            "message": f"Error installing app: {e.stderr or str(e)}",
            "filename": filename,
            "bundle_id": bundle_id,
        }


@router.get("/ios/bundle-installed")
def is_ios_app_installed(sim_udid: str, bundle_id: str):
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "get_app_container", sim_udid, bundle_id],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            list_result = subprocess.run(
                ["xcrun", "simctl", "listapps", sim_udid],
                capture_output=True, text=True, timeout=10
            )
            
            if list_result.returncode == 0:
                return {"installed": bundle_id in list_result.stdout}
            
            return {"installed": True}
        
        return {"installed": False}
    except Exception as e:
        return {"installed": False, "error": str(e)}