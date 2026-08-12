import hashlib
import os
import base64
import asyncio
import requests
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel

from Framework.Utilities import ConfigModule, CommonUtil


router = APIRouter(prefix="/linux", tags=["linux"])

SCREENSHOT_PATH = "linux_screen.png"

class InspectorResponse(BaseModel):
    """Response model for the /inspector endpoint."""
    status: Literal["ok", "error"] = "ok"
    ui_xml: str | None = None
    screenshot: str | None = None  # Base64 encoded image
    error: str | None = None


class LinuxWindowInfo(BaseModel):
    """A single top-level window belonging to an application."""

    id: str
    title: str
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0


class LinuxAppInfo(BaseModel):
    """Basic application metadata exposed by /apps."""

    pid: str
    name: str
    windows: list[LinuxWindowInfo] = []


@router.get("/inspect")
def inspect(app_name: str | None = None, window_id: str | None = None):
    """Get the Linux UI DOM and screenshot.

    `window_id` optionally pins the screenshot to a specific top-level
    window of the app (an app may have multiple windows; see /linux/apps).
    """
    from Framework.Built_In_Automation.Desktop.Linux import BuiltInFunctions
    if not BuiltInFunctions.is_atspi_available():
        return InspectorResponse(status="error", error=BuiltInFunctions.atspi_unavailable_message())

    try:
        # Determine app name
        target_app = app_name
        if not target_app:
            target_app = BuiltInFunctions.get_latest_app_name()

        if not target_app:
             return InspectorResponse(status="error", error="No application specified and no latest app found.")

        # Capture UI
        xml_content = BuiltInFunctions.get_ui_tree(target_app, window_id=window_id)
        if not xml_content:
             return InspectorResponse(status="error", error=f"Failed to get UI tree for app: {target_app}")

        # Capture Screenshot
        full_screenshot_path = os.path.abspath(SCREENSHOT_PATH)

        screenshot_base64 = None
        if BuiltInFunctions.capture_screenshot(full_screenshot_path, target_app, window_id=window_id):
            try:
                with open(full_screenshot_path, 'rb') as img_file:
                    screenshot_bytes = img_file.read()
                    screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            except Exception:
                pass

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


@router.get("/apps", response_model=list[LinuxAppInfo])
def get_apps():
    """Return available Linux applications visible to AT-SPI."""
    from Framework.Built_In_Automation.Desktop.Linux import BuiltInFunctions
    if not BuiltInFunctions.is_atspi_available():
        return []

    try:
        apps = []
        raw_apps = BuiltInFunctions._get_atspi_apps()
        # raw_apps: {pid: name}
        for pid, name in raw_apps.items():
            if name:
                windows = [
                    LinuxWindowInfo(**w)
                    for w in BuiltInFunctions.get_windows_for_pid(pid)
                ]
                apps.append(LinuxAppInfo(pid=str(pid), name=name, windows=windows))

        return sorted(apps, key=lambda app: app.name.lower())
    except Exception:
        return []


async def upload_linux_ui_dump():
    """Continuously upload Linux UI dump if changed."""
    from Framework.Built_In_Automation.Desktop.Linux import BuiltInFunctions
    if not BuiltInFunctions.is_atspi_available():
        return

    prev_xml_hash = ""
    while True:
        try:
            target_app = BuiltInFunctions.get_latest_app_name()
            if target_app:
                xml_content = BuiltInFunctions.get_ui_tree(target_app)
                if xml_content:
                    new_xml_hash = hashlib.sha256(xml_content.encode('utf-8')).hexdigest()
                    
                    if prev_xml_hash != new_xml_hash:
                        prev_xml_hash = new_xml_hash
                        
                        url = ConfigModule.get_config_value("Authentication", "server_address").strip() + "/node_ai_contents/"
                        apiKey = ConfigModule.get_config_value("Authentication", "api-key").strip()
                        
                        res = requests.post(
                            url,
                            headers={"X-Api-Key": apiKey},
                            json={
                                "dom_linux": {"dom": xml_content},
                                "node_id": CommonUtil.MachineInfo().getLocalUser().lower(),
                                "app_name": target_app # Extra info might be useful
                            }
                        )
                        if res.ok:
                            CommonUtil.ExecLog("", "Linux UI dump uploaded successfully", iLogLevel=1)
        except Exception as e:
            CommonUtil.ExecLog("", f"Error uploading Linux UI dump: {str(e)}", iLogLevel=3)
        
        await asyncio.sleep(5)
