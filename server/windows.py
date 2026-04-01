import hashlib
import os
import sys
import asyncio
import requests
import time
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel

from Framework.Utilities import ConfigModule, CommonUtil


router = APIRouter(prefix="/windows", tags=["windows"])

_TARGET_APP_NAME: str | None = None
_TARGET_APP_SET_TIME: float = 0.0
_active_ui_requests: dict[str, asyncio.Task] = {}


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


def _dump_element_to_xml(element, indent_level: int = 0, max_depth: int = 30) -> list[str]:
    """Recursively dump a UIAutomation element tree to XML strings."""
    if indent_level > max_depth:
        return []

    lines: list[str] = []
    indent = "  " * indent_level

    try:
        current = element.Current
        control_type = current.LocalizedControlType or "unknown"
        # Sanitize the tag name: replace spaces with underscores
        tag = control_type.replace(" ", "_")
        name = _xml_escape(current.Name or "")
        class_name = _xml_escape(current.ClassName or "")
        automation_id = _xml_escape(current.AutomationId or "")

        attrs = f'name="{name}"'
        if class_name:
            attrs += f' class="{class_name}"'
        if automation_id:
            attrs += f' automation_id="{automation_id}"'

        # Add bounding rectangle if available
        try:
            rect = current.BoundingRectangle
            if rect.Width > 0 or rect.Height > 0:
                attrs += f' x="{int(rect.Left)}" y="{int(rect.Top)}"'
                attrs += f' width="{int(rect.Width)}" height="{int(rect.Height)}"'
        except Exception:
            pass

        # Get children
        _, TreeScope, Condition, _ = _get_automation_imports()
        children = element.FindAll(TreeScope.Children, Condition.TrueCondition)

        if children.Count > 0:
            lines.append(f'{indent}<{tag} {attrs}>')
            for i in range(children.Count):
                child = children[i]
                lines.extend(_dump_element_to_xml(child, indent_level + 1, max_depth))
            lines.append(f'{indent}</{tag}>')
        else:
            lines.append(f'{indent}<{tag} {attrs}/>')

    except Exception:
        pass

    return lines


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


def _get_ui_tree_xml(app_name: str) -> str | None:
    """Get the full UI tree of a window as XML."""
    window = _find_window_by_name(app_name)
    if window is None:
        return None

    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_lines.extend(_dump_element_to_xml(window, indent_level=0))
    return "\n".join(xml_lines)


async def _get_ui_tree_xml_async(app_name: str) -> str | None:
    """Run _get_ui_tree_xml async and avoid concurrent duplicate requests for the same app."""
    if app_name in _active_ui_requests:
        return await _active_ui_requests[app_name]
    
    task = asyncio.create_task(asyncio.to_thread(_get_ui_tree_xml, app_name))
    _active_ui_requests[app_name] = task
    try:
        return await task
    finally:
        _active_ui_requests.pop(app_name, None)


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
        xml_content = await _get_ui_tree_xml_async(app_name)
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
                xml_content = await _get_ui_tree_xml_async(target_app)
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
