import hashlib
import json
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


def _safe_get_value(ui_element) -> str:
    """Safely get a ValuePattern value when available."""
    try:
        from System.Windows.Automation import ValuePattern
        return str(ui_element.GetCurrentPattern(ValuePattern.Pattern).Current.Value)
    except Exception:
        return ""


def _safe_get_bool(current, attr_name: str) -> bool | None:
    """Safely get a boolean attribute value from a UIAutomation element."""
    try:
        val = getattr(current, attr_name)
        if val is None:
            return None
        return bool(val)
    except Exception:
        return None


def _norm_text(value: str, max_len: int) -> str:
    """Normalize whitespace and truncate text."""
    if not value:
        return ""
    return " ".join(value.split())[:max_len]


def _sanitize_path_value(value: str) -> str:
    """Sanitize values for element_path segments (no quotes)."""
    if not value:
        return ""
    return value.replace("\"", " ").replace("'", " ").strip()


def _get_pattern_names(ui_element) -> set[str]:
    try:
        patterns = ui_element.GetSupportedPatterns()
        if not patterns:
            return set()
        return {p.ProgrammaticName.lower() for p in patterns}
    except Exception:
        return set()


def _is_action_element(localized_control: str, pattern_names: set[str]) -> bool:
    if pattern_names:
        for token in (
            "invokepattern",
            "togglepattern",
            "selectionitempattern",
            "expandcollapsepattern",
            "valuepattern",
            "rangevaluepattern",
            "scrollitempattern",
        ):
            if any(token in name for name in pattern_names):
                return True

    action_controls = {
        "button",
        "hyperlink",
        "edit",
        "combobox",
        "list item",
        "checkbox",
        "radio button",
        "menu item",
        "tab item",
        "slider",
        "spinner",
        "tree item",
        "menu",
        "toolbar",
        "split button",
    }
    return localized_control in action_controls


def _is_text_element(localized_control: str, name_value: str) -> bool:
    if not name_value:
        return False
    text_controls = {"text", "header", "label", "title bar"}
    return localized_control in text_controls or len(name_value) >= 3


def _element_path_key(info: dict) -> tuple[str, str, str, str]:
    return (
        info.get("name", ""),
        info.get("automation_id", ""),
        info.get("class_name", ""),
        info.get("localized_control", "") or info.get("control_type", ""),
    )


def _element_path_segment(info: dict, index: int | None) -> str:
    parts: list[str] = []
    name_val = _sanitize_path_value(info.get("name", ""))
    if name_val:
        parts.append(f'Name="{name_val}"')
    auto_val = _sanitize_path_value(info.get("automation_id", ""))
    if auto_val:
        parts.append(f'AutomationId="{auto_val}"')
    class_val = _sanitize_path_value(info.get("class_name", ""))
    if class_val:
        parts.append(f'ClassName="{class_val}"')
    control_val = _sanitize_path_value(info.get("localized_control", ""))
    if control_val:
        parts.append(f'LocalizedControlType="{control_val}"')
    elif info.get("control_type"):
        control_type_val = _sanitize_path_value(info.get("control_type", ""))
        if control_type_val:
            parts.append(f'ControlType="{control_type_val}"')
    if index is not None:
        parts.append(f"index={index}")
    if not parts:
        parts.append('Name=""')
    return ",".join(parts) + ">"


def _get_label_from_labeled_by(current) -> str | None:
    try:
        labeled_by = getattr(current, "LabeledBy", None)
        if labeled_by is None:
            return None
        label_name = getattr(labeled_by.Current, "Name", "")
        return label_name.strip() or None
    except Exception:
        return None


def _get_nearest_heading(ancestor_stack: list[dict]) -> str | None:
    for info in reversed(ancestor_stack):
        localized = info.get("localized_control", "")
        name_val = info.get("name", "")
        if not name_val:
            continue
        if "header" in localized or "title" in localized or localized == "heading":
            return _norm_text(name_val, 80) or None
    return None


def _build_page_map_for_app(app_name: str, max_depth: int = 50) -> tuple[list[dict], str] | None:
    """Build a page_map_json + page_map for a Windows app, using element_path semantics."""
    window = _find_window_by_name(app_name)
    if window is None:
        return None

    _, TreeScope, Condition, _ = _get_automation_imports()
    nodes: list[dict] = []
    seen_texts: set[str] = set()

    def build_info(ui_element, current) -> dict:
        return {
            "name": _safe_get_attr(current, "Name"),
            "automation_id": _safe_get_attr(current, "AutomationId"),
            "class_name": _safe_get_attr(current, "ClassName"),
            "control_type": _safe_get_attr(current, "ControlType"),
            "localized_control": _safe_get_attr(current, "LocalizedControlType").lower(),
            "value": _safe_get_value(ui_element),
            "framework_id": _safe_get_attr(current, "FrameworkId"),
            "access_key": _safe_get_attr(current, "AccessKey"),
            "accelerator_key": _safe_get_attr(current, "AcceleratorKey"),
            "process_id": _safe_get_attr(current, "ProcessId"),
            "native_window_handle": _safe_get_attr(current, "NativeWindowHandle"),
        }

    def in_viewport_from_current(current) -> bool:
        is_offscreen = _safe_get_bool(current, "IsOffscreen")
        if is_offscreen is True:
            return False
        try:
            rect = current.BoundingRectangle
            if rect.Right <= 0 or rect.Bottom <= 0:
                return False
        except Exception:
            return False
        return True

    def traverse(parent, parent_path: str, depth: int, ancestor_stack: list[dict]):
        if depth > max_depth:
            return
        try:
            child_elements = parent.FindAll(TreeScope.Children, Condition.TrueCondition)
        except Exception:
            return
        if not child_elements or child_elements.Count == 0:
            return

        key_counts: dict[tuple[str, str, str, str], int] = {}
        child_infos: list[tuple] = []
        for i in range(child_elements.Count):
            child = child_elements[i]
            try:
                current = child.Current
            except Exception:
                continue
            info = build_info(child, current)
            key = _element_path_key(info)
            key_counts[key] = key_counts.get(key, 0) + 1
            child_infos.append((child, current, info, key))

        key_indices: dict[tuple[str, str, str, str], int] = {}
        for child, current, info, key in child_infos:
            index = key_indices.get(key, 0)
            key_indices[key] = index + 1
            seg_index = index if key_counts[key] > 1 else None
            segment = _element_path_segment(info, seg_index)
            path = parent_path + segment

            localized_control = info.get("localized_control", "")
            if not localized_control:
                localized_control = (info.get("control_type", "").split(".")[-1] or "").lower()
            name_value = info.get("name", "")
            pattern_names = _get_pattern_names(child)
            is_action = _is_action_element(localized_control, pattern_names)
            is_text = _is_text_element(localized_control, name_value)
            in_viewport = in_viewport_from_current(current)

            if is_action:
                node = {
                    "node_type": "action",
                    "role": localized_control or info.get("control_type") or "",
                    "attributes": {
                        "Name": name_value or "",
                        "AutomationId": info.get("automation_id") or "",
                        "ClassName": info.get("class_name") or "",
                        "Value": info.get("value") or "",
                        "IsEnabled": _safe_get_bool(current, "IsEnabled"),
                        "IsOffscreen": _safe_get_bool(current, "IsOffscreen"),
                        "HasKeyboardFocus": _safe_get_bool(current, "HasKeyboardFocus"),
                        "IsKeyboardFocusable": _safe_get_bool(current, "IsKeyboardFocusable"),
                        "IsPassword": _safe_get_bool(current, "IsPassword"),
                    },
                    "in_viewport": in_viewport,
                    "xpath": path,
                }
                nodes.append(node)
            elif is_text:
                text_value = _norm_text(name_value, 150)
                if text_value and text_value not in seen_texts and len(text_value) >= 5:
                    seen_texts.add(text_value)
                    kind = "heading" if "header" in localized_control or "title" in localized_control else (localized_control or "text")
                    nodes.append({
                        "node_type": "text",
                        "kind": kind,
                        "text": text_value,
                        "in_viewport": in_viewport,
                        "xpath": path,
                    })

            traverse(child, path, depth + 1, ancestor_stack + [info])

    traverse(window, "", 0, [])

    page_map_json: list[dict] = []
    for idx, node in enumerate(nodes):
        xpath = node.get("xpath")
        if xpath:
            page_map_json.append({"idx": idx, "xpath": xpath})

    full_keys = ["Name", "AutomationId", "Value"]
    abbrev_keys = {
        "ClassName": "C",
    }

    def format_attr_value(value) -> str:
        if value is None:
            return ""
        if isinstance(value, bool):
            return "true" if value else "false"
        return _norm_text(str(value), 120)

    def format_attr_block(attributes: dict) -> str:
        if not attributes:
            return ""
        parts = []
        for key in full_keys:
            if key not in attributes:
                continue
            formatted = format_attr_value(attributes.get(key))
            if formatted == "":
                continue
            label = "Automation" if key == "AutomationId" else key
            parts.append(f"{label}='{formatted}'")
        for key, abbrev in abbrev_keys.items():
            if key not in attributes:
                continue
            formatted = format_attr_value(attributes.get(key))
            if formatted == "":
                continue
            parts.append(f"[{abbrev}='{formatted}']")
        return " ".join(parts) if parts else ""

    def format_bool_list(attributes: dict, vp_marker: str) -> str:
        order = ["IsEnabled", "IsOffscreen", "HasKeyboardFocus", "IsKeyboardFocusable", "IsPassword"]
        values = []
        for key in order:
            val = attributes.get(key)
            if val is None:
                values.append("")
            elif isinstance(val, bool):
                values.append("true" if val else "false")
            else:
                values.append(str(val))
        values.append(vp_marker)
        return "[" + ", ".join(values) + "]"

    lines = [
        "# Page Map (windows ui elements, in document order)",
        "# Format: Name='..' Automation='..' Value='..' [C='ClassName'] [IsEnabled, IsOffscreen, HasKeyboardFocus, IsKeyboardFocusable, IsPassword, V| -]",
    ]
    for idx, node in enumerate(nodes):
        if node.get("node_type") == "text":
            kind = (node.get("kind") or "text").upper()
            vp = "V" if node.get("in_viewport") else "-"
            lines.append(f"  {vp} [{idx}] [{kind}] \"{node.get('text', '')}\"")
        else:
            parts = [f"[{idx}]", (node.get("role") or "").upper()]
            attr_block = format_attr_block(node.get("attributes", {}))
            if attr_block:
                parts.append(attr_block)
            vp = "V" if node.get("in_viewport") else "-"
            bool_list = format_bool_list(node.get("attributes", {}), vp)
            parts.append(bool_list)
            lines.append("  " + "  ".join(parts))

    return page_map_json, "\n".join(lines)


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
        "AutomationId", "Name", "ClassName", "ControlType", "LocalizedControlType", "Value",
        "IsEnabled", "BoundingRectangle", "IsOffscreen", "NativeWindowHandle", "ProcessId",
        "HasKeyboardFocus", "AcceleratorKey", "IsPassword", "AccessKey", "FrameworkId", "IsKeyboardFocusable", "LabeledBy",
    ]

    for i in range(child_elements.Count):
        each_child = child_elements[i]
        try:
            current = each_child.Current
            attribs = {}
            for attr in attrs_to_extract:
                if attr == "Value":
                    attribs[attr] = _xml_escape(_safe_get_value(each_child))
                else:
                    attribs[attr] = _xml_escape(_safe_get_attr(current, attr))

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

    prev_payload_hash = ""
    while True:
        try:
            if _TARGET_APP_NAME and (time.time() - _TARGET_APP_SET_TIME) > 8 * 3600:
                _TARGET_APP_NAME = None

            target_app = _TARGET_APP_NAME

            if target_app:
                xml_content = await asyncio.to_thread(_get_ui_tree_xml_for_upload, target_app)
                page_map_data = await asyncio.to_thread(_build_page_map_for_app, target_app)
                if xml_content and page_map_data:
                    page_map_json, page_map = page_map_data
                    payload = {
                        "dom": xml_content,
                        "page_map": page_map,
                        "page_map_json": page_map_json,
                    }
                    payload_hash = hashlib.sha256(
                        json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
                    ).hexdigest()

                    if prev_payload_hash != payload_hash:
                        prev_payload_hash = payload_hash

                        output_dir = os.path.join(os.getcwd(), "AutomationLog", "windows_page_map")
                        os.makedirs(output_dir, exist_ok=True)
                        try:
                            with open(os.path.join(output_dir, "dom_win.xml"), "w", encoding="utf-8") as f:
                                f.write(xml_content)
                            with open(os.path.join(output_dir, "page_map.txt"), "w", encoding="utf-8") as f:
                                f.write(page_map)
                            with open(os.path.join(output_dir, "page_map.json"), "w", encoding="utf-8") as f:
                                json.dump(page_map_json, f, ensure_ascii=True, indent=2)
                        except Exception as e:
                            CommonUtil.ExecLog("", f"Error writing windows page map files: {str(e)}", iLogLevel=3)

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
                                "dom_win": payload,
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
