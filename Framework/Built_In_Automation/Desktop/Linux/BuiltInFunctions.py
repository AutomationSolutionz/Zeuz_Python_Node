import re
import inspect
import time
import subprocess
import sys
import os
import glob
from typing import List, Tuple, Optional, Any, Callable

import pyatspi
from pyatspi.action import Action
from pyatspi.editabletext import EditableText, Text
from pyatspi.Accessibility import Accessible

from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources
from Framework.Utilities.decorators import logger



class Collection: ...
class Component: ...
class Document: ...
class Hypertext: ...
class Image: ...
class Selection: ...
class Table: ...
class TableCell: ...
class Value: ...
DataSet = List[Tuple[str, str, str]]

def getInterface(iface_func: Callable, obj: Any) -> Any: ...

class Accessible:
    def __init__(self): ...

    def get_child_at_index(self, index: int) -> 'Accessible': ...
    def get_attributes_as_array(self) -> List[str]: ...
    def get_application(self) -> Optional['Accessible']: ...
    def get_child_count(self) -> int: ...
    def get_index_in_parent(self) -> int: ...
    def get_localized_role_name(self) -> str: ...
    def get_relation_set(self) -> Any: ...
    def get_role(self) -> int: ...
    def get_role_name(self) -> str: ...
    def get_state_set(self) -> Any: ...
    def get_description(self) -> Optional[str]: ...
    def get_object_locale(self) -> str: ...
    def get_name(self) -> Optional[str]: ...
    def get_parent(self) -> Optional['Accessible']: ...
    def set_cache_mask(self, mask: int) -> None: ...
    def clear_cache(self) -> None: ...
    def get_id(self) -> str: ...
    def get_toolkit_name(self) -> str: ...
    def get_toolkit_version(self) -> str: ...
    def get_atspi_version(self) -> str: ...

    def __getitem__(self, index: int) -> 'Accessible': ...
    def __len__(self) -> int: ...
    def __bool__(self) -> bool: ...
    def __str__(self) -> str: ...
    def isEqual(self, other: 'Accessible') -> bool: ...

    # Properties
    childCount: int
    description: Optional[str]
    objectLocale: str
    name: Optional[str]
    parent: Optional['Accessible']
    id: str
    toolkitName: str
    toolkitVersion: str
    atspiVersion: str

    # Query interfaces
    def queryAction(self) -> Action: ...
    def queryCollection(self) -> Collection: ...
    def queryComponent(self) -> Component: ...
    def queryDocument(self) -> Document: ...
    def queryEditableText(self) -> EditableText: ...
    def queryHyperlink(self) -> Any: ...
    def queryHypertext(self) -> Hypertext: ...
    def queryImage(self) -> Image: ...
    def querySelection(self) -> Selection: ...
    def queryTable(self) -> Table: ...
    def queryTableCell(self) -> TableCell: ...
    def queryText(self) -> Text: ...
    def queryValue(self) -> Value: ...


MODULE_NAME = inspect.getmodulename(__file__) or "BuiltInFunctions"
ui_xml_strings = [] # needed for generating XML tree


def convert_data_set_to_dict(data_set: DataSet) -> dict[str, str]:
    """ Convert data set to dictionary for easier access """
    data_dict = {}
    for item in data_set:
        if len(item) == 3:
            key, _, value = item
            data_dict[key.strip()] = value
        else:
            CommonUtil.ExecLog(MODULE_NAME, f"Invalid item in data set: {item}", 3)
    return data_dict


def simulate_keyboard_typing(app_name: str, node: Accessible, text: str) -> bool:
    action_iface = node.queryAction()
    if action_iface and action_iface.nActions > 0:
        for i in range(action_iface.nActions):
            action_name = action_iface.getName(i)
            if "activate" in action_name.lower():
                action_iface.doAction(i)
                try:
                    app_window = subprocess.run(['xdotool', 'search', '--name', app_name], capture_output=True, text=True).stdout.strip().split('\n')[0]
                    if app_window:
                        subprocess.run(['xdotool', 'windowactivate', app_window], capture_output=True)
                    else:
                        CommonUtil.ExecLog(MODULE_NAME, f"Application window for '{app_name}' not found.", 3)
                        return False
                except:
                    pass
                
                time.sleep(0.2)
                subprocess.run(['xdotool', 'type', '--delay', '50', text], capture_output=True)                
                return True
        else:
            return False
    else:
        return False


def get_attributes(accessible):
    attrs = accessible.getAttributes()
    attr_str = ''
    if attrs:
        for attr in attrs:
            if ':' in attr:
                key, value = attr.split(':', 1)
                safe_value = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                attr_str += f' {key}="{safe_value}"'
    return attr_str

def get_extended_info(accessible):
    info_str = ''
    try:
        description = accessible.description
        if description:
            safe_desc = description.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
            info_str += f' description="{safe_desc}"'
    except Exception:
        pass
    try:
        state_set = accessible.getStateSet()
        states = [pyatspi.stateToString(s) or "" for s in state_set.getStates()]
        if states:
            info_str += f' states="{",".join(states)}"'
    except Exception:
        pass
    try:
        action_iface = accessible.queryAction()
        if action_iface and action_iface.nActions > 0:
            actions = [action_iface.getName(i) for i in range(action_iface.nActions)]
            info_str += f' actions="{",".join(actions)}"'
    except Exception:
        pass
    return info_str

def get_position_info(accessible):
    position_str = ''
    try:
        component_iface = accessible.queryComponent()
        if component_iface:
            x, y = component_iface.getPosition(pyatspi.DESKTOP_COORDS)
            position_str += f' x="{x}" y="{y}"'
            width, height = component_iface.getSize()
            position_str += f' width="{width}" height="{height}"'
    except Exception:
        pass
    
    return position_str

def dump_node(node: Accessible, indent_level=0, path=[], recursive=True) -> list[str] | None:
    global ui_xml_strings
    if not recursive:
        ui_xml_strings = []
    if not node:
        return

    indent = "  " * indent_level
    role = node.get_role_name().replace(' ', '_')
    name = node.name or ""
    safe_name = (name.replace('&', '&amp;')
                 .replace('<', '&lt;')
                 .replace('>', '&gt;')
                 .replace('"', '&quot;'))

    attributes = get_attributes(node) + get_extended_info(node)
    position_info = get_position_info(node)
    path_str = '.'.join(map(str, path))
    path_attr = f' path="{path_str}"'

    iface_attrs = ""
    text_content_attr = ""

    try:
        text_iface = node.queryText()
        if text_iface:
            try:
                raw_text = text_iface.getText(0, -1).strip()
                raw_text = raw_text.strip('\ufffc')
                if raw_text:
                    safe_text = (raw_text.replace('&', '&amp;')
                                    .replace('<', '&lt;')
                                    .replace('>', '&gt;')
                                    .replace('"', '&quot;'))
                    text_content_attr = f' text="{safe_text}"'
            except Exception:
                pass
    except NotImplementedError:
        pass

    try:
        if node.queryEditableText():
            iface_attrs += ' editable_text_iface="true"'
    except NotImplementedError:
        pass

    child_count = node.childCount
    if child_count > 0:
        ui_xml_strings.append(f'{indent}<{role} name="{safe_name}"{attributes}{path_attr}{position_info}{iface_attrs}{text_content_attr}>')
        for i in range(child_count):
            child = node.get_child_at_index(i)
            if recursive:
                dump_node(child, indent_level + 1, path + [i])
        ui_xml_strings.append(f'{indent}</{role}>')
    else:
        ui_xml_strings.append(f'{indent}<{role} name="{safe_name}"{attributes}{path_attr}{position_info}{iface_attrs}{text_content_attr}/>')
    if not recursive:
        return ui_xml_strings


def get_ui_tree(app_keyword) -> str | None:
    global ui_xml_strings
    desktop = pyatspi.Registry.getDesktop(0)
    target_app = None

    for app in desktop:
        if app and app_keyword in app.name.lower():
            target_app = app
            break

    if target_app:
        for i in range(desktop.childCount):
            if desktop.getChildAtIndex(i) == target_app:
                break
        ui_xml_strings = ['<?xml version="1.0" encoding="UTF-8"?>']
        dump_node(target_app, 0, path=[])
        return '\n'.join(ui_xml_strings)
    else:
        CommonUtil.ExecLog(MODULE_NAME, f"Error: Application matching '{app_keyword}' not found.", 3)
        return None


def get_paths_by_text(xml_content: str, search_text: str, exact_match=True, case_sensitive=True) -> list[str]:
    content_to_search = xml_content

    if not case_sensitive:
        search_text = search_text.lower()
        content_to_search = content_to_search.lower()

    if exact_match:
        pattern = re.compile(r'text="{}"\s+[^>]*?path="([^"]+)"|path="([^"]+)"[^>]*?text="{}"'.format(
            re.escape(search_text), re.escape(search_text), re.escape(search_text)))
    else:
        pattern = re.compile(r'text="[^"]*{}[^"]*"[^>]*?path="([^"]+)"|path="([^"]+)"[^>]*?text="[^"]*{}[^"]*"'.format(
            re.escape(search_text), re.escape(search_text)))
    
    matches = pattern.findall(content_to_search)
    paths = []
    for match in matches:
        path = match[0] if match[0] else match[1]
        if path and path not in paths:
            paths.append(path)
    
    return paths


def get_parent_path_from_paths(paths: list[str]) -> str | None:
    """
    Sometimes multiple paths are returned for the same element. 
    They may have parent child relation. It is good idea to use 
    the parent. Parents path is always shorter and it is prefix 
    of child's path If they are not related, then return None.
    """
    if not paths:
        return None
    
    paths.sort(key=lambda x: len(x))
    parent_path = paths[0]
    for path in paths[1:]:
        if not path.startswith(parent_path):
            return None
    return parent_path


def get_path_appname_from_dataset(
        data_dict: dict[str, str], 
        wait_time=Shared_Resources.Get_Shared_Variables("element_wait")
    ) -> tuple[str | None, str | None]:
    path, app_name = data_dict.get("path"), data_dict.get("app_name")
    wait_time = float(data_dict.get("wait", wait_time) or str(wait_time or 10))
    text = data_dict.get("text", "").strip()
    start_time = time.time()
    if not path and text:
        while True:
            ui_tree = get_ui_tree(app_name)
            if not ui_tree:
                CommonUtil.ExecLog("", "UI tree not found for app_name: %s" % app_name, 3)
                return None, app_name
            paths = get_paths_by_text(ui_tree, text)
            CommonUtil.ExecLog("", "Found paths: %s" % paths, 1)
            if len(paths) == 0:
                if time.time() < start_time + wait_time:
                    time.sleep(0.5)
                    continue
                else:
                    CommonUtil.ExecLog("", "No elements found with text: %s" % text, 3)
                    return None, app_name
            if len(paths) == 1:
                return paths[0], app_name
            else:
                path = get_parent_path_from_paths(paths)
                return path, app_name
    return path, app_name


@logger
def get_node(data_dict: dict[str, str], wait_time=Shared_Resources.Get_Shared_Variables("element_wait")) -> Accessible | None:
    """ Get element using path_string from dataset """
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    start_time = time.time()
    if not data_dict:
        CommonUtil.ExecLog(sModuleInfo, "Data set is empty", 3)
        return None
    try:
        path, app_name = get_path_appname_from_dataset(data_dict)
        if not path:
            CommonUtil.ExecLog(sModuleInfo, "No path found in the dataset", 3)
            return None
        if not app_name:
            CommonUtil.ExecLog(sModuleInfo, "No app_name found in the dataset", 3)
            return None
        path = path.strip().replace(" ", ".") # support for space separated paths

        desktop = pyatspi.Registry.getDesktop(0)
        target_app = None
        for app in desktop:
            if app and app.name and app_name in app.name.lower():
                target_app = app
                break
        if not target_app:
            CommonUtil.ExecLog(sModuleInfo, "No application found with name: %s" % app_name, 3)
            return None
        try:
            indices = [int(i) for i in path.strip().split('.')]
        except ValueError:
            CommonUtil.ExecLog(sModuleInfo, "Invalid path string: %s" % path, 3)
            return None
            
        node = target_app
        for i, index in enumerate(indices):
            if index >= len(node):
                current_path = ".".join(map(str, indices[:i]))
                CommonUtil.ExecLog(sModuleInfo, "Index %d out of bounds at %s" % (index, current_path), 3)
                return None
            node = node[index]

        if not node:
            CommonUtil.ExecLog(sModuleInfo, "No element found at the specified path", 3)
            return None
        return node
    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, f"Error while getting node: {e}", 3)
        return None


def click_element_by_node(node: Accessible | None) -> str:
    """ Click using node, first get the element then click"""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    if node is None:
        CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
        return "zeuz_failed"

    while node:
        try:
            action_iface = node.queryAction()
            if action_iface and action_iface.nActions > 0:
                click_action_index: int = -1
                for i in range(action_iface.nActions):
                    action_name: str = action_iface.getName(i)
                    if action_name in ["click", "jump", "press", "open", "activate", "select", "clickAncestor"]:
                        click_action_index = i
                        break
                
                if click_action_index >= 0:
                    action_name: str = action_iface.getName(click_action_index)
                    action_iface.doAction(click_action_index)
                    CommonUtil.ExecLog(sModuleInfo, f"Clicked element using action: {action_name}", 1)
                    return "passed"
                else:
                    node = node.parent
                    continue
            else:
                node = node.parent
                continue
        except NotImplementedError:
            node = node.parent
            continue
        except Exception as e:
            CommonUtil.ExecLog(sModuleInfo, f"Failed to click element: {e}", 3)
    return "zeuz_failed"


@logger
def click_element(data_set: DataSet):
    """ Click using element, first get the element then click"""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    data_dict = convert_data_set_to_dict(data_set)
    node = get_node(data_dict)
    if node is None:
        CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
        return "zeuz_failed"

    try:
        return click_element_by_node(node)
    except NotImplementedError:
        CommonUtil.ExecLog(sModuleInfo, "This node does not support the Action interface.", 3)
        return "zeuz_failed"
    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, f"Failed to click element: {e}", 3)
        return "zeuz_failed"


def enter_text_in_node(app_name: str, node: Accessible | None, text: str) -> str:
    """ Enter text using node, first get the element then enter text"""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    if node is None:
        CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
        return "zeuz_failed"

    while node:
        try:
            editable_iface = node.queryEditableText()
            if editable_iface:
                editable_iface.setTextContents(text)
                CommonUtil.ExecLog(sModuleInfo, f"Entering text: {text}", 1)
                return "passed"
            elif simulate_keyboard_typing(app_name, node, text):
                return "passed"
            else:
                node = node.parent
                continue
        except NotImplementedError:
            if simulate_keyboard_typing(app_name, node, text):
                return "passed"
            node = node.parent
            continue
        except Exception as e:
            CommonUtil.ExecLog(sModuleInfo, f"Failed enter text: {e}", 3)
    return "zeuz_failed"


@logger
def enter_text(data_set: DataSet):
    """ Enter text using element, first get the element then enter text"""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    data_dict = convert_data_set_to_dict(data_set)
    app_name = data_dict.get("app_name", "").strip()
    text = data_dict.get("text", "").strip()
    if not text:
        CommonUtil.ExecLog(sModuleInfo, "No text provided to enter", 3)
        return "zeuz_failed"
    if not app_name:
        CommonUtil.ExecLog(sModuleInfo, "No app_name provided to enter text", 3)
        return "zeuz_failed"
    node = get_node(data_dict)
    if node is None:
        CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
        return "zeuz_failed"

    try:
        return enter_text_in_node(app_name, node, text)
    except NotImplementedError:
        CommonUtil.ExecLog(sModuleInfo, "This node does not support the Action interface.", 3)
        return "zeuz_failed"
    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, f"Failed to enter text: {e}", 3)
        return "zeuz_failed"


def find_matched_app_name(app_name: str) -> Optional[str]:
    available_apps = set()
    
    try:
        desktop_files = glob.glob("/usr/share/applications/*.desktop")
        for desktop_file in desktop_files:
            app_name = os.path.basename(desktop_file).replace('.desktop', '')
            available_apps.add(app_name)
    except Exception:
        pass
    available_apps = sorted(list(available_apps))

    user_lower = app_name.lower()
    for app in available_apps:
        if app.lower() == user_lower:
            return app
    for app in available_apps:
        if app.lower().startswith(user_lower):
            return app
    for app in available_apps:
        if user_lower in app.lower():
            return app
    user_clean = user_lower.replace('-', '').replace('_', '').replace(' ', '')
    for app in available_apps:
        app_clean = app.lower().replace('-', '').replace('_', '').replace(' ', '')
        if app_clean == user_clean or user_clean in app_clean:
            return app
    return None


@logger
def open_app(data_set: DataSet):
    """ Open application using element, first get the element then open app"""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    data_dict = convert_data_set_to_dict(data_set)
    app_name = data_dict.get("app_name", "").strip()

    best_match = find_matched_app_name(app_name)

    if best_match:
        if best_match != app_name:
            CommonUtil.ExecLog(MODULE_NAME, f"Best match found: {best_match} for {app_name}", 1)        
        try:
            # if args:
            #     command = f"nohup {app_name} {' '.join(args)} >/dev/null 2>&1 &"
            # else:
            command = f"nohup {app_name} >/dev/null 2>&1 &"
            exit_code = os.system(command)
            if exit_code == 0:
                CommonUtil.ExecLog(sModuleInfo, f"Successfully launched '{app_name}'", 1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, f"Failed to launch '{app_name}' (exit code: {exit_code})", 3)
                return "zeuz_failed"

        except Exception as e:
            CommonUtil.ExecLog(sModuleInfo, f"Error launching '{app_name}': {e}", 3)
            return "zeuz_failed"
    else:
        CommonUtil.ExecLog(MODULE_NAME, f"No matching application found for '{app_name}'", 3)


@logger
def wait_for_element(data_set: DataSet):
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    data_dict = convert_data_set_to_dict(data_set)
    try:
        timeout_duration = 10
        appear_condition = True
        for left, mid, right in data_set:
            if mid.strip().lower() == "action":
                if left.strip().lower() == "wait to disappear":
                    appear_condition = False
                timeout_duration = int(right.strip())

        end_time = time.time() + timeout_duration
        while time.time() <= end_time:
            node = get_node(data_dict, 0)
            if appear_condition and node:  # Element found
                CommonUtil.ExecLog(sModuleInfo, "Found element", 1)
                return "passed"
            elif not appear_condition and not node:  # Element removed
                CommonUtil.ExecLog(sModuleInfo, "Element disappeared", 1)
                return "passed"
            time.sleep(1)

        CommonUtil.ExecLog(sModuleInfo, "Wait for element failed", 3)
        return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def get_attribute_value(tag_str: str, attr_name: str) -> str | None:
    pattern = rf'{attr_name}="(.*?)"'
    match = re.search(pattern, tag_str)
    return match.group(1) if match else None


@logger
def save_attribute(data_set: DataSet):
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    data_dict = convert_data_set_to_dict(data_set)
    try:
        variable_name = ""
        field = "value"
        for left, mid, right in data_set:
            if mid.strip().lower() == "save parameter":
                field = left.replace(" ", "").lower()
                field2 = left.strip()
                variable_name = right.strip()

        node = get_node(data_dict)
        if node is None:
            return "zeuz_failed"
        tag_str = (dump_node(node, recursive=False) or ["", ""])[0]
        actual_text = get_attribute_value(tag_str, field)

        if actual_text is None:
            CommonUtil.ExecLog(sModuleInfo, f"Attribute '{field}' not found in the element", 3)
            return "zeuz_failed"

        Shared_Resources.Set_Shared_Variables(variable_name, actual_text)
        CommonUtil.ExecLog(sModuleInfo, f"Text '{actual_text}' is saved in the variable '{variable_name}'", 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")