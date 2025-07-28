import re
import inspect
import time

from pyatspi import Accessible
import pyatspi

from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources
from Framework.Utilities.decorators import logger


MODULE_NAME = inspect.getmodulename(__file__)
ui_xml_strings = [] # needed for generating XML tree


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
        states = [pyatspi.stateToString(s) for s in state_set.getStates()]
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

def dump_node(node, indent_level=0, path=[]):
    global ui_xml_strings
    if not node:
        return

    indent = "  " * indent_level
    role = node.getRoleName().replace(' ', '_')
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
            child = node.getChildAtIndex(i)
            dump_node(child, indent_level + 1, path + [i])
        ui_xml_strings.append(f'{indent}</{role}>')
    else:
        ui_xml_strings.append(f'{indent}<{role} name="{safe_name}"{attributes}{path_attr}{position_info}{iface_attrs}{text_content_attr}/>')


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
        data_set: list[tuple[str, str, str]], 
        wait_time=Shared_Resources.Get_Shared_Variables("element_wait")
    ) -> tuple[str | None, str | None]:
    path, app_name = None, None
    for left, mid, right in data_set:
        left = left.replace(" ", "").lower()
        mid = mid.strip().lower()
        if left == "wait": 
            wait_time = float(right.strip())
        elif "app_name" == left:
            app_name = right.strip().lower()
        elif "path" == left:
            path = right.strip()
        elif "text" == left:
            text = right.strip()
    if not path and text:
        while True:
            ui_tree = get_ui_tree(app_name)
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
def get_node(data_set, wait_time=Shared_Resources.Get_Shared_Variables("element_wait")) -> Accessible | None:
    """ Get element using path_string from dataset """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    start_time = time.time()
    if not data_set:
        CommonUtil.ExecLog(sModuleInfo, "Data set is empty", 3)
        return None
    try:
        path, app_name = get_path_appname_from_dataset(data_set)
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


def click_element_by_node(node: Accessible) -> str:
    """ Click using node, first get the element then click"""
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

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
                    if action_name in ["click", "jump", "press", "activate", "select"]:
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
def click_element(data_set):
    """ Click using element, first get the element then click"""
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    node = get_node(data_set)
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