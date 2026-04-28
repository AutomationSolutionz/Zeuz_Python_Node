import hashlib
import os
import sys
import asyncio
import requests
import time
import xml.etree.ElementTree as ET
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel

from Framework.Utilities import ConfigModule, CommonUtil


router = APIRouter(prefix="/windows", tags=["windows"])

_TARGET_APP_NAME: str | None = None
_TARGET_APP_SET_TIME: float = 0.0

_HOTKEY = "ctrl+shift+i"


class InspectorResponse(BaseModel):
    """Response model for the /inspect endpoint."""
    status: Literal["ok", "error"] = "ok"
    ui_xml: str | None = None
    error: str | None = None


class AppInfo(BaseModel):
    """Model for an active application/window."""
    name: str
    pid: int
    class_name: str
    automation_id: str


def _xml_escape(value: str) -> str:
    """Escape special characters for XML attributes."""
    return (
        value
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


_automation_loaded = False


def _get_automation_imports():
    """Lazily import UIAutomation types (only available on Windows with pythonnet).

    Mirrors the clr setup from Framework/Built_In_Automation/Desktop/Windows/BuiltInFunctions.py.
    """
    global _automation_loaded
    if not _automation_loaded:
        import clr
        dll_path = os.getcwd().split("Framework")[0] + "Framework" + os.sep + "windows_dll_files" + os.sep
        clr.AddReference(dll_path + "UIAutomationClient")
        clr.AddReference(dll_path + "UIAutomationTypes")
        clr.AddReference(dll_path + "UIAutomationProvider")
        _automation_loaded = True

    from System.Windows.Automation import (
        AutomationElement,
        TreeScope,
        Condition,
        TreeWalker,
    )
    return AutomationElement, TreeScope, Condition, TreeWalker


def _safe_get_attr(current, attr_name: str) -> str:
    """Safely get an attribute value from a UIAutomation element's Current property."""
    try:
        val = getattr(current, attr_name)
        if val is None:
            return ""
        return str(val)
    except Exception:
        return ""


def _build_element_tree(xml_parent, ui_element, max_depth: int = 50, _depth: int = 0):
    """Recursively build an ET tree from a UIAutomation element."""
    if _depth > max_depth:
        return

    _, TreeScope, Condition, _ = _get_automation_imports()
    try:
        child_elements = ui_element.FindAll(TreeScope.Children, Condition.TrueCondition)
    except Exception:
        return

    attrs_to_extract = [
        "AutomationId", "Name", "ClassName", "ControlType", "LocalizedControlType",
        "IsEnabled", "BoundingRectangle", "IsOffscreen", "NativeWindowHandle", "ProcessId",
        "HasKeyboardFocus", "AcceleratorKey", "IsPassword", "AccessKey", "FrameworkId", "IsKeyboardFocusable", "LabeledBy",
    ]

    for i in range(child_elements.Count):
        each_child = child_elements[i]
        try:
            current = each_child.Current
            attribs = {attr: _xml_escape(_safe_get_attr(current, attr)) for attr in attrs_to_extract}

            # Add coordinates separately
            try:
                rect = current.BoundingRectangle
                attribs.update({
                    "Left": str(rect.Left),
                    "Right": str(rect.Right),
                    "Top": str(rect.Top),
                    "Bottom": str(rect.Bottom),
                })
            except Exception:
                attribs.update({"Left": "", "Right": "", "Top": "", "Bottom": ""})

            # Add supported patterns
            try:
                patterns = each_child.GetSupportedPatterns()
                attribs["pattern_list"] = ",".join([p.ProgrammaticName for p in patterns]) if patterns else ""
            except Exception:
                attribs["pattern_list"] = ""

            xml_child = ET.SubElement(xml_parent, "div", **attribs)
            _build_element_tree(xml_child, each_child, max_depth, _depth + 1)
        except Exception:
            continue


def _remove_coordinates(root):
    """Remove Left/Right/Top/Bottom attributes from all elements. Matches inspector's Remove_coordinate()."""
    for each in root:
        att = each.attrib
        for key in ("Left", "Right", "Top", "Bottom"):
            att.pop(key, None)
        _remove_coordinates(each)


def _find_window_by_name(app_name: str):
    """Find the top-level window element matching app_name (case-insensitive substring match)."""
    AutomationElement, TreeScope, Condition, _ = _get_automation_imports()
    root = AutomationElement.RootElement
    windows = root.FindAll(TreeScope.Children, Condition.TrueCondition)

    app_lower = app_name.lower()
    for i in range(windows.Count):
        try:
            win = windows[i]
            win_name = win.Current.Name or ""
            if app_lower in win_name.lower():
                return win
        except Exception:
            continue
    return None


def _get_ui_tree(app_name: str) -> ET.Element | None:
    """Build the UI tree as an ET Element matching ZeuZ_Windows_Inspector format.

    Returns a <body> root with Name, AutomationId, LocalizedControlType, ClassName, pid.
    Children are <div> elements with the same attributes plus Left/Right/Top/Bottom.
    """
    window = _find_window_by_name(app_name)
    if window is None:
        return None

    current = window.Current
    attribs = {
        "Name": _xml_escape(_safe_get_attr(current, "Name")),
        "AutomationId": _xml_escape(_safe_get_attr(current, "AutomationId")),
        "LocalizedControlType": _xml_escape(_safe_get_attr(current, "LocalizedControlType")),
        "ClassName": _xml_escape(_safe_get_attr(current, "ClassName")),
        "pid": _safe_get_attr(current, "ProcessId"),
    }
    root = ET.Element("body", **attribs)
    _build_element_tree(root, window)
    return root


def _get_ui_tree_xml(app_name: str) -> str | None:
    """Get the full UI tree of a window as XML string (with coordinates, for /inspect)."""
    root = _get_ui_tree(app_name)
    if root is None:
        return None
    try:
        ET.indent(root)
    except AttributeError:
        pass
    return ET.tostring(root, encoding="unicode")


def _get_ui_tree_xml_for_upload(app_name: str) -> str | None:
    """Get the UI tree XML for upload (without coordinates, matching inspector's uploaded version)."""
    root = _get_ui_tree(app_name)
    if root is None:
        return None
    _remove_coordinates(root)
    try:
        ET.indent(root, "")
    except AttributeError:
        pass
    return ET.tostring(root, encoding="unicode")



def _wait_hotkey_and_capture(app_name: str) -> str | None:
    """Block until user presses the hotkey, then immediately capture the UI tree.

    This runs in a thread so the menu stays open (no focus change).
    """
    import keyboard
    keyboard.wait(_HOTKEY)
    return _get_ui_tree_xml(app_name)


def _get_active_apps() -> list[AppInfo]:
    """Return all top-level windows (active apps) from the UIAutomation tree."""
    AutomationElement, TreeScope, Condition, _ = _get_automation_imports()
    root = AutomationElement.RootElement
    windows = root.FindAll(TreeScope.Children, Condition.TrueCondition)

    apps: list[AppInfo] = []
    for i in range(windows.Count):
        try:
            win = windows[i]
            name = win.Current.Name or ""
            # Skip empty-named windows (usually invisible system windows)
            if not name.strip():
                continue
            apps.append(AppInfo(
                name=name,
                pid=win.Current.ProcessId,
                class_name=win.Current.ClassName or "",
                automation_id=win.Current.AutomationId or "",
            ))
        except Exception:
            continue
    return apps


@router.get("/inspect")
async def inspect(app_name: str):
    """Get the Windows UI DOM (XML tree) for a given application.

    Args:
        app_name: Name (or substring) of the target application window. Required.
    """
    global _TARGET_APP_NAME, _TARGET_APP_SET_TIME
    _TARGET_APP_NAME = app_name
    _TARGET_APP_SET_TIME = time.time()

    if sys.platform != "win32":
        return InspectorResponse(status="error", error="This endpoint is only available on Windows")

    try:
        xml_content = await asyncio.to_thread(_get_ui_tree_xml, app_name)
        if not xml_content:
            return InspectorResponse(
                status="error",
                error=f"No window found matching '{app_name}'. Use /apps to list active windows.",
            )
        return InspectorResponse(status="ok", ui_xml=xml_content)
    except Exception as e:
        return InspectorResponse(status="error", error=str(e))



@router.get("/snapshot")
async def snapshot(app_name: str):
    """Wait for hotkey press, then capture and return the UI tree.

    The request blocks until the user presses the hotkey (Ctrl+Shift+I).
    This allows capturing menus/popups that disappear on focus change.

    Args:
        app_name: Name (or substring) of the target application window.
    """
    if sys.platform != "win32":
        return InspectorResponse(status="error", error="This endpoint is only available on Windows")

    try:
        xml_content = await asyncio.to_thread(_wait_hotkey_and_capture, app_name)
        if not xml_content:
            return InspectorResponse(
                status="error",
                error=f"No window found matching '{app_name}'. Use /apps to list active windows.",
            )
        return InspectorResponse(status="ok", ui_xml=xml_content)
    except Exception as e:
        return InspectorResponse(status="error", error=str(e))


@router.get("/apps", response_model=list[AppInfo])
async def get_apps():
    """Return all opened/active application windows."""
    if sys.platform != "win32":
        return []

    try:
        return await asyncio.to_thread(_get_active_apps)
    except Exception:
        return []


async def upload_windows_ui_dump():
    """Continuously upload Windows UI dump if changed.

    Only runs on Windows. Uploads to the server with key 'dom_windows'.
    """
    global _TARGET_APP_NAME, _TARGET_APP_SET_TIME

    if sys.platform != "win32":
        return

    prev_xml_hash = ""
    while True:
        try:
            if _TARGET_APP_NAME and (time.time() - _TARGET_APP_SET_TIME) > 8 * 3600:
                _TARGET_APP_NAME = None

            target_app = _TARGET_APP_NAME

            if target_app:
                xml_content = await asyncio.to_thread(_get_ui_tree_xml_for_upload, target_app)
                if xml_content:
                    new_xml_hash = hashlib.sha256(xml_content.encode("utf-8")).hexdigest()

                    if prev_xml_hash != new_xml_hash:
                        prev_xml_hash = new_xml_hash

                        url = (
                            ConfigModule.get_config_value("Authentication", "server_address").strip()
                            + "/node_ai_contents/"
                        )
                        apiKey = ConfigModule.get_config_value("Authentication", "api-key").strip()

                        res = await asyncio.to_thread(
                            requests.post,
                            url,
                            headers={"X-Api-Key": apiKey},
                            json={
                                "dom_win": {"dom": xml_content},
                                "node_id": CommonUtil.MachineInfo().getLocalUser().lower(),
                                "app_name": target_app,
                            },
                            timeout=10,
                        )
                        if res.ok:
                            CommonUtil.ExecLog("", "Windows UI dump uploaded successfully", iLogLevel=1)
        except Exception as e:
            CommonUtil.ExecLog("", f"Error uploading Windows UI dump: {str(e)}", iLogLevel=3)

        await asyncio.sleep(5)
