import re
import inspect
import time
import subprocess
import sys
import os
import glob
import difflib
import xml.etree.ElementTree as ET
from typing import List, Literal, Tuple, Optional, Any, Callable

from Framework.module_installer import install_missing_modules

try:
    import pyatspi
    from pyatspi.action import Action
    from pyatspi.editabletext import EditableText, Text
except ImportError:
    install_missing_modules(["python3-pyatspi==1.19.0", "pygobject==3.50.1"])
    try:
        import pyatspi
        from pyatspi.action import Action
        from pyatspi.editabletext import EditableText, Text
    except ImportError:
        sys.stderr.write(
            "Error: system dependency is not installed. Install them by running Installer/setup_linux_inspector.sh.\n"
        )
        sys.exit(1)

try:
    from Xlib import X, display as xlib_display
    from Xlib.ext import composite as xlib_composite  # noqa: F401  registers ext methods
    from Xlib.error import XError
except ImportError:
    install_missing_modules(["python-xlib==0.33"])
    try:
        from Xlib import X, display as xlib_display
        from Xlib.ext import composite as xlib_composite  # noqa: F401
        from Xlib.error import XError
    except ImportError:
        sys.stderr.write(
            "Error: python-xlib is not installed. Install it by running Installer/setup_linux_inspector.sh.\n"
        )
        sys.exit(1)

from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as Shared_Resources,
)
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

    def get_child_at_index(self, index: int) -> "Accessible": ...
    def get_attributes_as_array(self) -> List[str]: ...
    def get_application(self) -> Optional["Accessible"]: ...
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
    def get_parent(self) -> Optional["Accessible"]: ...
    def set_cache_mask(self, mask: int) -> None: ...
    def clear_cache(self) -> None: ...
    def get_id(self) -> str: ...
    def get_toolkit_name(self) -> str: ...
    def get_toolkit_version(self) -> str: ...
    def get_atspi_version(self) -> str: ...

    def __getitem__(self, index: int) -> "Accessible": ...
    def __len__(self) -> int: ...
    def __bool__(self) -> bool: ...
    def __str__(self) -> str: ...
    def isEqual(self, other: "Accessible") -> bool: ...

    # Properties
    childCount: int
    description: Optional[str]
    objectLocale: str
    name: Optional[str]
    parent: Optional["Accessible"]
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
ui_xml_strings = []  # needed for generating XML tree
LATEST_APP_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "latest_app.txt"
)


def save_latest_app_name(app_name: str):
    """Save the latest used application name to a file."""
    try:
        with open(LATEST_APP_FILE, "w") as f:
            f.write(app_name)
    except Exception as e:
        CommonUtil.ExecLog(MODULE_NAME, f"Failed to save latest app name: {e}", 3)


def get_latest_app_name() -> str | None:
    """Get the latest used application name from the file."""
    try:
        if os.path.exists(LATEST_APP_FILE):
            with open(LATEST_APP_FILE, "r") as f:
                return f.read().strip()
    except Exception as e:
        CommonUtil.ExecLog(MODULE_NAME, f"Failed to get latest app name: {e}", 3)
    return None


def get_windows_for_pid(pid: int | str) -> list[dict]:
    """Return visible windows owned by `pid` as a list of
    {"id": str, "title": str, "x": int, "y": int, "width": int, "height": int}.
    """
    windows = []
    try:
        res = subprocess.run(
            ["xdotool", "search", "--onlyvisible", "--pid", str(pid)],
            capture_output=True,
            text=True,
        )
        for wid in [l.strip() for l in res.stdout.splitlines() if l.strip()]:
            try:
                title = subprocess.run(
                    ["xdotool", "getwindowname", wid],
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                geom_out = subprocess.run(
                    ["xdotool", "getwindowgeometry", "--shell", wid],
                    capture_output=True,
                    text=True,
                ).stdout
                geom = {}
                for line in geom_out.splitlines():
                    if "=" in line:
                        k, v = line.split("=", 1)
                        geom[k.strip()] = v.strip()
                windows.append(
                    {
                        "id": wid,
                        "title": title,
                        "x": int(geom.get("X", 0)),
                        "y": int(geom.get("Y", 0)),
                        "width": int(geom.get("WIDTH", 0)),
                        "height": int(geom.get("HEIGHT", 0)),
                    }
                )
            except Exception:
                continue
    except Exception as e:
        CommonUtil.ExecLog(MODULE_NAME, f"Error getting windows for pid {pid}: {e}", 3)
    return windows


def _get_window_id_for_app(app_name: str | None, window_id: str | None = None) -> str | None:
    """Return a window id for the requested app name, or None if not found.

    - If `window_id` is given, it is used directly (caller already picked a specific window).
    - If app_name is provided, tries to find the best visible window matching that name:
      an exact (case-insensitive) title match wins; otherwise the largest matching window.
    - Falls back to the active window using xdotool if no app_name was resolved or found.
    """
    if window_id:
        return window_id.strip()

    try:
        if app_name:
            # try matching by exec command (from desktop file) or by process name (pgrep)
            try:
                app_key, matched_name, exec_cmd = find_best_app_match(app_name) or (
                    None,
                    None,
                    None,
                )
            except Exception:
                app_key, matched_name, exec_cmd = (None, None, None)

            candidates: list[dict] = []
            if exec_cmd:
                for pid in get_process_ids(exec_cmd):
                    candidates.extend(get_windows_for_pid(pid))

            if not candidates:
                # try matching by pid for processes that match app_name
                for pid in get_process_ids(app_name):
                    candidates.extend(get_windows_for_pid(pid))

            if not candidates:
                # last resort: scan all visible windows and keep those whose
                # title contains app_name (case-insensitive)
                res = subprocess.run(
                    ["xdotool", "search", "--onlyvisible", "--name", ".*"],
                    capture_output=True,
                    text=True,
                )
                for wid in [l.strip() for l in res.stdout.splitlines() if l.strip()]:
                    try:
                        name = subprocess.run(
                            ["xdotool", "getwindowname", wid],
                            capture_output=True,
                            text=True,
                        ).stdout.strip()
                        if app_name.lower() in name.lower():
                            candidates.extend(get_windows_for_pid(
                                subprocess.run(
                                    ["xdotool", "getwindowpid", wid],
                                    capture_output=True,
                                    text=True,
                                ).stdout.strip() or "0"
                            ) or [{"id": wid, "title": name, "width": 0, "height": 0}])
                    except Exception:
                        continue

            if candidates:
                # prefer an exact (case-insensitive) title match
                for c in candidates:
                    if c["title"].strip().lower() == app_name.strip().lower():
                        return c["id"]
                # otherwise pick the largest window by area (the main window)
                largest = max(candidates, key=lambda c: c["width"] * c["height"])
                return largest["id"]
        # fallback to active window
        res = subprocess.run(
            ["xdotool", "getactivewindow"], capture_output=True, text=True
        )
        winid = res.stdout.strip()
        if winid:
            CommonUtil.ExecLog(
                MODULE_NAME, f"Selected window id {winid} for app '{app_name}'", 1
            )
            CommonUtil.ExecLog(
                MODULE_NAME, f"Trying xwd/convert capture for window id: {winid}", 1
            )
            return winid
    except Exception as e:
        CommonUtil.ExecLog(MODULE_NAME, f"Window lookup error: {e}", 3)
    return None


def _get_toplevel_window(d, winid: str):
    """Walk up the window tree to the child-of-root ancestor of `winid`.

    Compositors only redirect top-level (child-of-root) windows, so capturing
    via XComposite on a descendant window (e.g. a toolkit's internal drawing
    surface) fails with BadMatch. xdotool sometimes resolves to such a
    descendant, so resolve the actual top-level before using composite.
    """
    win = d.create_resource_object("window", int(winid))
    root = d.screen().root
    current = win
    while True:
        tree = current.query_tree()
        parent = tree.parent
        if parent is None or parent.id == root.id:
            return current
        current = parent


def _capture_via_composite(file_path: str, winid: str) -> bool:
    """Capture a window's pixels via the XComposite offscreen pixmap.

    A running compositor (mutter/kwin/picom/xfwm4 etc.) redirects every
    top-level window to an offscreen pixmap; we ask the server for that
    pixmap and read it directly, so anything stacked above the target
    window does NOT appear in the result, and we never have to steal focus.

    Returns False whenever this path can't be used (no compositor running,
    Composite extension absent, deps missing, X errors) so the caller can
    fall back to a different strategy.
    """
    try:
        from PIL import Image
    except ImportError as e:
        CommonUtil.ExecLog(MODULE_NAME, f"Composite capture skipped: {e}", 4)
        return False

    d = None
    pixmap = None
    try:
        d = xlib_display.Display()
        if not d.has_extension("Composite"):
            return False
        d.composite_query_version()

        win = _get_toplevel_window(d, winid)
        geom = win.get_geometry()
        w, h = geom.width, geom.height
        if w <= 0 or h <= 0:
            return False

        # Fails (e.g. BadMatch) when no compositor has redirected the window.
        pixmap = win.composite_name_window_pixmap()
        raw = pixmap.get_image(0, 0, w, h, X.ZPixmap, 0xFFFFFFFF)

        # ZPixmap on a 24/32-bit truecolor visual lays bytes out as B,G,R,X
        # in memory; "BGRX" tells Pillow to drop the pad byte and produce RGB.
        img = Image.frombuffer("RGB", (w, h), raw.data, "raw", "BGRX", 0, 1)

        # Align the screenshot with the AT-SPI accessibility tree: the toplevel
        # window's pixmap may include decorations (e.g. title bar) that the
        # AT-SPI frame's coordinates exclude, so crop to the frame's bounds.
        frame_geom = _get_frame_geometry_for_window(winid)
        if frame_geom:
            crop_left = frame_geom["x"] - geom.x
            crop_top = frame_geom["y"] - geom.y
            crop_right = crop_left + frame_geom["width"]
            crop_bottom = crop_top + frame_geom["height"]
            if (
                0 <= crop_left < crop_right <= w
                and 0 <= crop_top < crop_bottom <= h
            ):
                img = img.crop((crop_left, crop_top, crop_right, crop_bottom))

        img.save(file_path)

        return os.path.exists(file_path) and os.path.getsize(file_path) > 0
    except XError as e:
        CommonUtil.ExecLog(MODULE_NAME, f"Composite capture X error: {e}", 4)
        return False
    except Exception as e:
        CommonUtil.ExecLog(MODULE_NAME, f"Composite capture failed: {e}", 4)
        return False
    finally:
        try:
            if pixmap is not None:
                pixmap.free()
        except Exception:
            pass
        try:
            if d is not None:
                d.close()
        except Exception:
            pass


def _capture_via_xwd_raise(file_path: str, winid: str) -> bool:
    """Fallback: raise the window, then capture screen pixels with xwd.

    Used when no compositor is running (so XComposite can't help) or the
    composite path failed. Steals focus as a side effect.
    """
    try:
        subprocess.run(["xdotool", "windowraise", winid], capture_output=True)
        subprocess.run(
            ["xdotool", "windowactivate", "--sync", winid], capture_output=True
        )
        time.sleep(0.25)

        p1 = subprocess.Popen(
            ["xwd", "-silent", "-id", winid],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        p2 = subprocess.Popen(
            ["convert", "xwd:-", file_path],
            stdin=p1.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        if p1.stdout:
            p1.stdout.close()
        _, err = p2.communicate()
        p1.wait()

        if (
            p2.returncode == 0
            and os.path.exists(file_path)
            and os.path.getsize(file_path) > 0
        ):
            return True

        CommonUtil.ExecLog(
            MODULE_NAME,
            f"xwd/convert capture failed: {err.decode(errors='replace').strip()}",
            3,
        )
    except FileNotFoundError as e:
        CommonUtil.ExecLog(
            MODULE_NAME,
            f"Required command not found ({e.filename}). Install xwd (x11-apps), xdotool, and ImageMagick.",
            3,
        )
    except Exception as e:
        CommonUtil.ExecLog(MODULE_NAME, f"xwd/convert screenshot failed: {e}", 3)

    return False


def capture_screenshot(file_path: str, app_name: str | None = None, window_id: str | None = None) -> bool:
    """Capture a screenshot of the application's window (X11 only).

    Tries the XComposite extension first, which reads the compositor's
    offscreen pixmap and is unaffected by other windows on top. Falls back
    to raising the window and capturing on-screen pixels with xwd if the
    composite path is unavailable (no compositor, missing deps, or X error).

    If `window_id` is given, that specific window is captured directly
    (useful when an app has multiple top-level windows).
    """
    desired_app = app_name or get_latest_app_name()

    winid = _get_window_id_for_app(desired_app, window_id=window_id)
    if not winid:
        CommonUtil.ExecLog(
            MODULE_NAME,
            f"Could not resolve a window for app '{desired_app}'",
            3,
        )
        return False

    if _capture_via_composite(file_path, winid):
        return True
    return _capture_via_xwd_raise(file_path, winid)


def convert_data_set_to_dict(data_set: DataSet) -> dict[str, str]:
    """Convert data set to dictionary for easier access.

    Records `exact_<key>` / `case_sensitive_<key>` flags from `*`/`**` prefixes
    so downstream matchers can apply fuzzy / case-insensitive matching uniformly.
    """
    data_dict = {}
    for item in data_set:
        if len(item) == 3:
            key, _, value = item
            if key.startswith("**"):
                clean = key[2:].strip()
                data_dict[clean] = value
                data_dict["exact_" + clean] = "false"
                data_dict["case_sensitive_" + clean] = "false"
            elif key.startswith("*"):
                clean = key[1:].strip()
                data_dict[clean] = value
                data_dict["exact_" + clean] = "false"
            else:
                data_dict[key.strip()] = value
        else:
            CommonUtil.ExecLog(MODULE_NAME, f"Invalid item in data set: {item}", 3)
    return data_dict


# Mid-column values that should NOT be treated as element selectors.
_NON_ELEMENT_MIDS = {
    "action",
    "save parameter",
    "optional parameter",
    "click parameter",
    "scroll parameter",
    "loop action",
    "loop settings",
    "optional loop settings",
    "optional loop condition",
    "optional loop control",
    "common action",
}

# Mid-column values that select an element role within the locator.
_ELEMENT_ROLES = ("element", "parent", "sibling", "child", "unique")

# Locator attribute keys recognized by find_paths_by_attrs (besides path/text).
# Maps user-facing key name -> XML attribute name (or "__role__" for the tag).
_ATTR_ALIASES = {
    "name": "name",
    "role": "__role__",
    "type": "__role__",
    "control type": "__role__",
    "controltype": "__role__",
    "description": "description",
    "desc": "description",
    "states": "states",
    "state": "states",
    "actions": "actions",
    "action attr": "actions",
    "class": "class",
    "toolkit class": "class",
    "id": "id",
    "automation id": "id",
    "automationid": "id",
    "x": "x",
    "y": "y",
    "width": "width",
    "height": "height",
}

# Numeric attributes that should be compared with int equality.
_NUMERIC_ATTRS = {"x", "y", "width", "height"}

# Multi-token attributes that should match if the criterion appears as a token.
_TOKEN_ATTRS = {"states", "actions"}


def split_data_set_by_role(data_set: DataSet) -> dict[str, DataSet]:
    """Bucket dataset rows by mid-column 'X parameter' prefix.

    Rows whose mid is in `_NON_ELEMENT_MIDS` are skipped (they belong to the
    action itself, not the element selector). Unknown mids default to
    'element' for backwards compatibility with datasets that omit the mid.
    """
    groups: dict[str, DataSet] = {role: [] for role in _ELEMENT_ROLES}
    for left, mid, right in data_set:
        mid_l = (mid or "").strip().lower()
        if mid_l in _NON_ELEMENT_MIDS:
            continue
        role = "element"
        for candidate in _ELEMENT_ROLES:
            if mid_l.startswith(candidate):
                role = candidate
                break
        groups[role].append((left, mid, right))
    return groups


def _normalize_attr_key(raw_key: str) -> str | None:
    """Map a user-facing dataset key to a normalized XML attribute name."""
    cleaned = raw_key.strip().lower()
    if cleaned in _ATTR_ALIASES:
        return _ATTR_ALIASES[cleaned]
    return None


def _matches_one_criterion(
    elem_value: str | None,
    target_value: str,
    fuzzy: bool,
    case_insensitive: bool,
    token_split: bool,
    numeric: bool,
) -> bool:
    if elem_value is None:
        return False
    target = target_value.strip()
    if numeric:
        try:
            return int(float(elem_value)) == int(float(target))
        except Exception:
            return False
    if token_split:
        tokens = [t.strip() for t in elem_value.split(",") if t.strip()]
        if case_insensitive:
            return target.lower() in [t.lower() for t in tokens]
        return target in tokens
    if case_insensitive:
        elem_value = elem_value.lower()
        target = target.lower()
    if fuzzy:
        return target in elem_value
    return elem_value == target


def _build_criteria_from_dict(data_dict: dict[str, str]) -> list[tuple]:
    """Build matcher criteria tuples from a flattened element dict.

    Returns a list of (xml_attr, target_value, fuzzy, case_insensitive,
    token_split, numeric). 'text' is included as a special pseudo-attribute
    that maps to the XML 'text' attribute.
    """
    criteria: list[tuple] = []
    text_value = data_dict.get("text", "").strip()
    if text_value:
        fuzzy = data_dict.get("exact_text", "true").lower() == "false"
        ci = data_dict.get("case_sensitive_text", "true").lower() == "false"
        criteria.append(("text", text_value, fuzzy, ci, False, False))

    for raw_key, value in data_dict.items():
        if raw_key in (
            "text",
            "path",
            "app_name",
            "wait",
            "index",
        ):
            continue
        if raw_key.startswith("exact_") or raw_key.startswith("case_sensitive_"):
            continue
        if not value or not str(value).strip():
            continue
        attr = _normalize_attr_key(raw_key)
        if not attr:
            continue
        fuzzy = data_dict.get("exact_" + raw_key, "true").lower() == "false"
        ci = data_dict.get("case_sensitive_" + raw_key, "true").lower() == "false"
        token_split = attr in _TOKEN_ATTRS
        numeric = attr in _NUMERIC_ATTRS
        criteria.append((attr, str(value).strip(), fuzzy, ci, token_split, numeric))
    return criteria


def find_paths_by_attrs(
    xml_content: str,
    criteria: list[tuple],
    ancestor_path: str | None = None,
) -> list[str]:
    """Walk the AT-SPI XML dump and return paths whose elements match all criteria.

    Each criterion is a tuple (xml_attr, target, fuzzy, case_insensitive,
    token_split, numeric). xml_attr can be the special "__role__" to match
    against the tag name (which encodes the AT-SPI role).
    """
    if not criteria:
        return []
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        CommonUtil.ExecLog(MODULE_NAME, f"XML parse error in matcher: {e}", 3)
        return []

    matches: list[str] = []
    for elem in root.iter():
        path = elem.get("path", "")
        if not path:
            continue
        if ancestor_path and not (
            path == ancestor_path or path.startswith(ancestor_path + ".")
        ):
            continue
        ok = True
        for attr, target, fuzzy, ci, token_split, numeric in criteria:
            if attr == "__role__":
                actual: str | None = elem.tag
            else:
                actual = elem.get(attr)
            if not _matches_one_criterion(actual, target, fuzzy, ci, token_split, numeric):
                ok = False
                break
        if ok:
            matches.append(path)
    return matches


def _node_at_path(target_app: Accessible, path_str: str) -> Accessible | None:
    """Walk dot-separated child indices from target_app to the requested node."""
    try:
        indices = [int(i) for i in path_str.strip().split(".")]
    except ValueError:
        return None
    node: Accessible | None = target_app
    for index in indices:
        if node is None or index >= len(node):
            return None
        node = node[index]
    return node


def _find_app(app_name: str | None) -> Accessible | None:
    if not app_name:
        return None
    desktop = pyatspi.Registry.getDesktop(0)
    keyword = app_name.strip().lower()
    for app in desktop:
        if app and app.name and keyword in app.name.lower():
            return app
    return None


def _get_atspi_apps() -> dict[int, str]:
    """Return {pid: name} for all apps currently in the AT-SPI2 desktop tree."""
    try:
        desktop = pyatspi.Registry.getDesktop(0)
        result: dict[int, str] = {}
        for app in desktop:
            if app and app.name:
                try:
                    result[app.get_process_id()] = app.name
                except Exception:
                    pass
        return result
    except Exception:
        return {}


def _discover_atspi_app_name(
    launched_name: str,
    before: dict[int, str],
    timeout: float = 10.0,
    poll_interval: float = 0.5,
) -> str | None:
    """
    Poll AT-SPI2 until a new app appears (identified by a PID not in `before`).
    Returns the AT-SPI2 name of that app.
    If multiple new apps appear simultaneously, similarity to `launched_name` breaks the tie.
    Falls back to name-similarity across all running apps if no new PID appears within timeout.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        current = _get_atspi_apps()
        new_apps = {pid: name for pid, name in current.items() if pid not in before}
        if new_apps:
            if len(new_apps) == 1:
                return next(iter(new_apps.values()))
            return max(
                new_apps.values(),
                key=lambda n: difflib.SequenceMatcher(
                    None, launched_name.lower(), n.lower()
                ).ratio(),
            )
        time.sleep(poll_interval)
    # No new PID appeared (e.g. app was already running): fall back to name similarity
    current = _get_atspi_apps()
    if current:
        return max(
            current.values(),
            key=lambda n: difflib.SequenceMatcher(
                None, launched_name.lower(), n.lower()
            ).ratio(),
        )
    return None


def simulate_keyboard_typing(
    app_name: str | None, node: Accessible | None, text: str
) -> bool:
    if node:
        action_iface = node.queryAction()
        if action_iface and action_iface.nActions > 0:
            for i in range(action_iface.nActions):
                action_name = action_iface.getName(i)
                if "activate" in action_name.lower():
                    action_iface.doAction(i)
    try:
        if app_name:
            app_window = (
                subprocess.run(
                    ["xdotool", "search", "--name", app_name],
                    capture_output=True,
                    text=True,
                )
                .stdout.strip()
                .split("\n")[0]
            )
            if app_window:
                subprocess.run(
                    ["xdotool", "windowactivate", app_window], capture_output=True
                )
            else:
                CommonUtil.ExecLog(
                    MODULE_NAME, f"Application window for '{app_name}' not found.", 3
                )
                return False
    except:
        pass

    time.sleep(0.2)
    subprocess.run(["xdotool", "type", "--delay", "50", text], capture_output=True)
    return True


def get_attributes(accessible):
    attrs = accessible.getAttributes()
    attr_str = ""
    if attrs:
        for attr in attrs:
            if ":" in attr:
                key, value = attr.split(":", 1)
                safe_value = (
                    value.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace('"', "&quot;")
                )
                attr_str += f' {key}="{safe_value}"'
    return attr_str


def get_extended_info(accessible):
    info_str = ""
    try:
        description = accessible.description
        if description:
            safe_desc = (
                description.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )
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
    """Return position string for XML with coordinates relative to:
    - 'desktop' (default): absolute coordinates using DESKTOP_COORDS
    - 'app': relative to the application's window origin
    - 'parent': relative to the immediate parent's origin

    If computing a relative coordinate fails, falls back to desktop coordinates.
    """
    position_str = ""
    try:
        component_iface = accessible.queryComponent()
        if component_iface:
            # Get absolute (desktop) position first
            x_abs, y_abs = component_iface.getPosition(pyatspi.DESKTOP_COORDS)
            width, height = component_iface.getSize()
            x, y = x_abs, y_abs

            position_str += f' x="{x}" y="{y}"'
            position_str += f' width="{width}" height="{height}"'
    except Exception:
        pass

    return position_str


def dump_node(
    node: Accessible, indent_level=0, path=[], recursive=True
) -> list[str] | None:
    global ui_xml_strings
    if not recursive:
        ui_xml_strings = []
    if not node:
        return

    indent = "  " * indent_level
    role = node.get_role_name().replace(" ", "_")
    name = node.name or ""
    safe_name = (
        name.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

    attributes = get_attributes(node) + get_extended_info(node)
    position_info = get_position_info(node)
    path_str = ".".join(map(str, path))
    path_attr = f' path="{path_str}"'

    iface_attrs = ""
    text_content_attr = ""

    try:
        text_iface = node.queryText()
        if text_iface:
            try:
                raw_text = text_iface.getText(0, -1).strip()
                raw_text = raw_text.strip("\ufffc")
                if raw_text:
                    safe_text = (
                        raw_text.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace('"', "&quot;")
                    )
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
        ui_xml_strings.append(
            f'{indent}<{role} name="{safe_name}"{attributes}{path_attr}{position_info}{iface_attrs}{text_content_attr}>'
        )
        for i in range(child_count):
            child = node.get_child_at_index(i)
            if recursive:
                dump_node(child, indent_level + 1, path + [i], recursive=recursive)
        ui_xml_strings.append(f"{indent}</{role}>")
    else:
        ui_xml_strings.append(
            f'{indent}<{role} name="{safe_name}"{attributes}{path_attr}{position_info}{iface_attrs}{text_content_attr}/>'
        )
    if not recursive:
        return ui_xml_strings


def _get_window_geometry(window_id: str) -> dict | None:
    """Return {x, y, width, height} for an X window id via xdotool, or None."""
    try:
        geom_out = subprocess.run(
            ["xdotool", "getwindowgeometry", "--shell", window_id],
            capture_output=True,
            text=True,
        ).stdout
        geom = {}
        for line in geom_out.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                geom[k.strip()] = v.strip()
        if not geom:
            return None
        return {
            "x": int(geom.get("X", 0)),
            "y": int(geom.get("Y", 0)),
            "width": int(geom.get("WIDTH", 0)),
            "height": int(geom.get("HEIGHT", 0)),
        }
    except Exception:
        return None


def _find_frame_by_geometry(target_app: Accessible, geometry: dict) -> Accessible | None:
    """Find a top-level frame of `target_app` whose extents match `geometry`."""
    best_match = None
    best_diff = None
    for i in range(target_app.childCount):
        frame = target_app.get_child_at_index(i)
        if not frame:
            continue
        try:
            component_iface = frame.queryComponent()
            if not component_iface:
                continue
            x, y = component_iface.getPosition(pyatspi.DESKTOP_COORDS)
            width, height = component_iface.getSize()
        except Exception:
            continue

        diff = (
            abs(x - geometry["x"])
            + abs(y - geometry["y"])
            + abs(width - geometry["width"])
            + abs(height - geometry["height"])
        )
        if diff == 0:
            return frame
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_match = frame

    return best_match


def _get_frame_geometry_for_window(window_id: str) -> dict | None:
    """Find the AT-SPI frame matching `window_id` and return its desktop-coords geometry.

    Used to align captured screenshots with the AT-SPI accessibility tree, whose
    coordinates may differ from the X11 window's geometry by the window
    decoration (title bar) offset.
    """
    geometry = _get_window_geometry(window_id)
    if not geometry:
        return None

    desktop = pyatspi.Registry.getDesktop(0)
    best_frame = None
    best_diff = None
    for app in desktop:
        if not app:
            continue
        frame = _find_frame_by_geometry(app, geometry)
        if not frame:
            continue
        try:
            component_iface = frame.queryComponent()
            x, y = component_iface.getPosition(pyatspi.DESKTOP_COORDS)
            width, height = component_iface.getSize()
        except Exception:
            continue
        diff = (
            abs(x - geometry["x"])
            + abs(y - geometry["y"])
            + abs(width - geometry["width"])
            + abs(height - geometry["height"])
        )
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_frame = {"x": x, "y": y, "width": width, "height": height}

    return best_frame


def get_ui_tree(app_keyword, window_id: str | None = None) -> str | None:
    global ui_xml_strings
    desktop = pyatspi.Registry.getDesktop(0)
    keyword = (app_keyword or "").strip().lower()

    matching_apps = [app for app in desktop if app and keyword and keyword in app.name.lower()]

    target_app = matching_apps[0] if matching_apps else None
    dump_target = target_app

    if window_id and matching_apps:
        geometry = _get_window_geometry(window_id)
        if geometry:
            best_frame = None
            best_diff = None
            for app in matching_apps:
                frame = _find_frame_by_geometry(app, geometry)
                if not frame:
                    continue
                try:
                    component_iface = frame.queryComponent()
                    x, y = component_iface.getPosition(pyatspi.DESKTOP_COORDS)
                    width, height = component_iface.getSize()
                except Exception:
                    continue
                diff = (
                    abs(x - geometry["x"])
                    + abs(y - geometry["y"])
                    + abs(width - geometry["width"])
                    + abs(height - geometry["height"])
                )
                if best_diff is None or diff < best_diff:
                    best_diff = diff
                    best_frame = frame
                    target_app = app

            if best_frame is not None:
                dump_target = best_frame

    if target_app:

        ui_xml_strings = ['<?xml version="1.0" encoding="UTF-8"?>']
        dump_node(dump_target, 0, path=[])
        return "\n".join(ui_xml_strings)
    else:
        CommonUtil.ExecLog(
            MODULE_NAME, f"Error: Application matching '{app_keyword}' not found.", 3
        )
        return None


def get_paths_by_text(
    xml_content: str, search_text: str, exact_match=True, case_sensitive=True
) -> list[str]:
    content_to_search = xml_content

    if not case_sensitive:
        search_text = search_text.lower()
        content_to_search = content_to_search.lower()

    if exact_match:
        pattern = re.compile(
            r'text="{}"\s+[^>]*?path="([^"]+)"|path="([^"]+)"[^>]*?text="{}"'.format(
                re.escape(search_text), re.escape(search_text), re.escape(search_text)
            )
        )
    else:
        pattern = re.compile(
            r'text="[^"]*{}[^"]*"[^>]*?path="([^"]+)"|path="([^"]+)"[^>]*?text="[^"]*{}[^"]*"'.format(
                re.escape(search_text), re.escape(search_text)
            )
        )

    matches = pattern.findall(content_to_search)
    paths = []
    for match in matches:
        path = match[0] if match[0] else match[1]
        if path and path not in paths:
            paths.append(path)

    return sorted(paths)


def get_parent_path_from_paths(paths: list[str]) -> list[str]:
    """
    Sometimes multiple paths are returned for the same element.
    They may have parent-child relations. This function identifies
    all parent paths by removing children whose parent exists in the list.

    Returns a list of parent paths (paths that are not prefixes of any other path).
    """
    if not paths:
        return []

    # Sort by length to process shorter (potential parent) paths first
    sorted_paths = sorted(set(paths), key=lambda x: len(x))
    parents = []

    for i, path in enumerate(sorted_paths):
        # Check if this path is a parent of any other path
        is_parent = False
        for j in range(i + 1, len(sorted_paths)):
            # Check if sorted_paths[j] starts with path followed by a dot
            # This ensures "0.0.0" doesn't match "0.0.0.1" incorrectly
            if sorted_paths[j].startswith(path + "."):
                is_parent = True
                break

        # If this path is not a parent of any remaining path, it's a leaf or standalone parent
        if not is_parent:
            parents.append(path)

    return parents

@logger
def get_path_appname_from_dataset(
    data_dict: dict[str, str],
    wait_time=Shared_Resources.Get_Shared_Variables("element_wait", False),
    ancestor_path: str | None = None,
) -> tuple[str | None, str | None]:
    """Resolve (path, app_name) from a flattened element dict.

    Honors the path directly when supplied. Otherwise builds a criteria list
    from any combination of supported attributes (text, name, role, description,
    states, actions, class, id, x/y/width/height) and walks the AT-SPI dump.
    When `ancestor_path` is provided, the search is restricted to descendants
    of that path (used by parent/sibling resolution).
    """
    path = data_dict.get("path")
    app_name = data_dict.get("app_name")
    if app_name:
        save_latest_app_name(app_name)
    else:
        app_name = get_latest_app_name()
    if wait_time == "zeuz_failed" or not wait_time:
        wait_time = 10
    wait_time = float(data_dict.get("wait", wait_time) or wait_time)
    index_raw = (data_dict.get("index") or "0").strip()
    if not index_raw.isdigit():
        raise ValueError("Index must be an integer.")
    index = int(index_raw)

    if path:
        return path, app_name

    criteria = _build_criteria_from_dict(data_dict)
    if not criteria:
        return None, app_name

    start_time = time.time()
    while True:
        ui_tree = get_ui_tree(app_name)
        if not ui_tree:
            CommonUtil.ExecLog("", "UI tree not found for app_name: %s" % app_name, 3)
            return None, app_name
        paths = find_paths_by_attrs(ui_tree, criteria, ancestor_path=ancestor_path)
        if not paths:
            if time.time() < start_time + wait_time:
                time.sleep(0.5)
                continue
            CommonUtil.ExecLog(
                "", "No elements found matching criteria: %s" % data_dict, 3
            )
            return None, app_name
        if len(paths) == 1:
            return paths[0], app_name
        parent_paths = get_parent_path_from_paths(paths)
        CommonUtil.ExecLog("", "Found paths: %s" % parent_paths, 1)
        if not parent_paths:
            return None, app_name
        if index >= len(parent_paths):
            CommonUtil.ExecLog(
                "",
                f"Index {index} out of range; only {len(parent_paths)} matches",
                3,
            )
            return None, app_name
        return parent_paths[index], app_name


@logger
def get_node(
    data_dict: dict[str, str],
    wait_time=Shared_Resources.Get_Shared_Variables("element_wait", False),
    ancestor_path: str | None = None,
) -> Accessible | None:
    """Resolve an Accessible from a flattened element dict.

    Supports any combination of locator attributes (text, name, role, description,
    states, actions, class, id, x/y/width/height) plus an explicit `path`. When
    `ancestor_path` is supplied the search is restricted to descendants.
    """
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    if not data_dict:
        CommonUtil.ExecLog(sModuleInfo, "Data set is empty", 3)
        return None
    try:
        path, app_name = get_path_appname_from_dataset(
            data_dict, wait_time=wait_time, ancestor_path=ancestor_path
        )
        if not path:
            CommonUtil.ExecLog(sModuleInfo, "No path found in the dataset", 3)
            return None
        if not app_name:
            CommonUtil.ExecLog(sModuleInfo, "No app_name found in the dataset", 3)
            return None
        path = path.strip().replace(" ", ".")  # support for space-separated paths

        target_app = _find_app(app_name)
        if not target_app:
            CommonUtil.ExecLog(
                sModuleInfo, "No application found with name: %s" % app_name, 3
            )
            return None
        node = _node_at_path(target_app, path)
        if not node:
            CommonUtil.ExecLog(
                sModuleInfo, "No element found at the specified path: %s" % path, 3
            )
            return None
        return node
    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, f"Error while getting node: {e}", 3)
        return None


def _node_path_string(node: Accessible | None) -> str | None:
    """Compute the dot-path of a node relative to its application."""
    if node is None:
        return None
    indices: list[int] = []
    current = node
    try:
        while True:
            parent = current.parent
            if parent is None:
                break
            try:
                idx = current.get_index_in_parent()
            except Exception:
                idx = -1
                for i in range(len(parent)):
                    if parent[i] == current:
                        idx = i
                        break
                if idx < 0:
                    return None
            indices.append(idx)
            current = parent
            try:
                if current.get_role() == pyatspi.ROLE_APPLICATION:
                    break
            except Exception:
                break
    except Exception:
        return None
    indices.reverse()
    return ".".join(str(i) for i in indices)


def resolve_node(
    data_set: DataSet,
    wait_time=Shared_Resources.Get_Shared_Variables("element_wait", False),
) -> Accessible | None:
    """Resolve the target Accessible honoring mid-column parent/sibling/child grouping.

    Falls back to plain element resolution when no parent/sibling/child rows are
    present, preserving backwards compatibility with existing test cases.
    """
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    if not data_set:
        return None

    groups = split_data_set_by_role(data_set)
    common_dict = convert_data_set_to_dict(data_set)
    app_name = common_dict.get("app_name", "").strip()
    if app_name:
        save_latest_app_name(app_name)
    else:
        app_name = get_latest_app_name() or ""

    parent_path: str | None = None
    if groups["parent"]:
        parent_dict = convert_data_set_to_dict(groups["parent"])
        if "app_name" not in parent_dict and app_name:
            parent_dict["app_name"] = app_name
        parent_node = get_node(parent_dict, wait_time=wait_time)
        if parent_node is None:
            CommonUtil.ExecLog(sModuleInfo, "Parent element not found", 3)
            return None
        parent_path = _node_path_string(parent_node)

    element_dict = convert_data_set_to_dict(groups["element"]) if groups["element"] else common_dict
    if "app_name" not in element_dict and app_name:
        element_dict["app_name"] = app_name

    if groups["sibling"]:
        sibling_dict = convert_data_set_to_dict(groups["sibling"])
        if "app_name" not in sibling_dict and app_name:
            sibling_dict["app_name"] = app_name

        if parent_path:
            sibling_node = get_node(
                sibling_dict, wait_time=wait_time, ancestor_path=parent_path
            )
            if sibling_node is None:
                CommonUtil.ExecLog(sModuleInfo, "Sibling element not found", 3)
                return None
            target_node = get_node(
                element_dict, wait_time=wait_time, ancestor_path=parent_path
            )
            if target_node is None:
                return None
        else:
            # No explicit parent: find the sibling's parent in the tree and
            # search for the element among that parent's descendants.
            ui_tree = get_ui_tree(app_name)
            if not ui_tree:
                CommonUtil.ExecLog(
                    sModuleInfo, "UI tree not found for app_name: %s" % app_name, 3
                )
                return None
            sibling_criteria = _build_criteria_from_dict(sibling_dict)
            sibling_paths = find_paths_by_attrs(ui_tree, sibling_criteria)
            if not sibling_paths:
                CommonUtil.ExecLog(sModuleInfo, "Sibling element not found", 3)
                return None
            target_node = None
            for sibling_path in sibling_paths:
                if "." not in sibling_path:
                    continue
                candidate_parent = sibling_path.rsplit(".", 1)[0]
                target_node = get_node(
                    element_dict, wait_time=0, ancestor_path=candidate_parent
                )
                if target_node is not None:
                    parent_path = candidate_parent
                    break
            if target_node is None:
                CommonUtil.ExecLog(
                    sModuleInfo, "Element not found among siblings", 3
                )
                return None
    else:
        target_node = get_node(
            element_dict, wait_time=wait_time, ancestor_path=parent_path
        )
        if target_node is None:
            return None

    if groups["child"]:
        child_dict = convert_data_set_to_dict(groups["child"])
        if "app_name" not in child_dict and app_name:
            child_dict["app_name"] = app_name
        child_anchor = _node_path_string(target_node)
        if child_anchor is None:
            CommonUtil.ExecLog(sModuleInfo, "Could not derive child anchor path", 3)
            return None
        child_node = get_node(
            child_dict, wait_time=wait_time, ancestor_path=child_anchor
        )
        if child_node is None:
            CommonUtil.ExecLog(sModuleInfo, "Child element not found", 3)
            return None
        return child_node

    return target_node


# --- AT-SPI helpers (state, action, mouse synth) -----------------------------

# Click-shaped Action interface names recognized across toolkits.
# AT-SPI dumps in this repo use Press / Toggle / ShowMenu / SetFocus / Increase /
# Decrease (case sensitive); _action_index() lower-cases names before lookup so
# this set is lower-case too. ShowMenu is included because clicking a menu_item
# whose only action is ShowMenu should open its popup.
_CLICK_ACTION_NAMES = {
    "click", "jump", "press", "open", "activate", "select",
    "clickancestor", "link.open", "showmenu",
}
_CHECK_ACTION_NAMES = {"toggle", "press", "click", "check", "activate", "select"}
_UNCHECK_ACTION_NAMES = {"toggle", "press", "click", "uncheck", "activate", "select"}
_STATE_CHECKED = {"checked", "selected", "pressed", "armed"}
_STATE_VISIBLE = {"visible", "showing"}
_STATE_HIDDEN = {"hidden", "offscreen", "defunct", "invisible"}

_BUTTON_MAP = {
    "left": "1", "primary": "1", "1": "1",
    "middle": "2", "center": "2", "2": "2",
    "right": "3", "secondary": "3", "3": "3",
}


def _node_app_name(node: Accessible | None) -> str | None:
    if node is None:
        return None
    try:
        app_acc = node.get_application()
        if app_acc and getattr(app_acc, "name", None):
            return app_acc.name
    except Exception:
        return None
    return None


def _node_state_names(node: Accessible | None) -> set[str]:
    if node is None:
        return set()
    try:
        state_set = node.getStateSet()
    except Exception:
        try:
            state_set = node.get_state_set()
        except Exception:
            return set()
    states: set[str] = set()
    try:
        for state in state_set.getStates():
            states.add((pyatspi.stateToString(state) or str(state)).strip().lower())
    except Exception:
        pass
    return states


def _is_node_checked(node: Accessible | None) -> bool:
    return bool(_node_state_names(node) & _STATE_CHECKED)


def _is_node_visible(node: Accessible | None) -> bool:
    if node is None:
        return False
    states = _node_state_names(node)
    if states & _STATE_HIDDEN:
        return False
    rect = _node_rect(node)
    return bool(rect and rect[2] > 0 and rect[3] > 0)


def _node_rect(node: Accessible | None) -> tuple[int, int, int, int] | None:
    if node is None:
        return None
    try:
        comp = node.queryComponent()
        if not comp:
            return None
        get_extents = getattr(comp, "getExtents", None)
        if get_extents:
            x, y, w, h = get_extents(pyatspi.DESKTOP_COORDS)
        else:
            x, y = comp.getPosition(pyatspi.DESKTOP_COORDS)
            w, h = comp.getSize()
        return int(x), int(y), int(w), int(h)
    except Exception:
        return None


def _action_index(node: Accessible | None, names: set[str]) -> int:
    """Return the first action index whose name (case-insensitive) is in `names`."""
    if node is None:
        return -1
    try:
        iface = node.queryAction()
        if not iface or iface.nActions <= 0:
            return -1
        for i in range(iface.nActions):
            if iface.getName(i).strip().lower() in names:
                return i
    except Exception:
        return -1
    return -1


def _perform_action(node: Accessible | None, names: set[str], climb: bool = True) -> bool:
    """Try to invoke an Action interface entry whose name matches `names`,
    optionally climbing to ancestors when the leaf has no matching action."""
    current = node
    while current is not None:
        idx = _action_index(current, names)
        if idx >= 0:
            try:
                current.queryAction().doAction(idx)
                return True
            except Exception:
                return False
        if not climb:
            return False
        try:
            current = current.parent
        except Exception:
            return False
    return False


def _grab_focus(node: Accessible | None) -> bool:
    if node is None:
        return False
    try:
        comp = node.queryComponent()
        if comp and hasattr(comp, "grabFocus"):
            return bool(comp.grabFocus())
    except Exception:
        return False
    return False


def _atspi_mouse_move(coords: tuple[int, int]) -> bool:
    try:
        pyatspi.Registry.generateMouseEvent(coords[0], coords[1], "abs")
        return True
    except Exception:
        return False


def _atspi_mouse_click(
    coords: tuple[int, int], button: str = "1", click_count: int = 1, delay: float = 0.05
) -> bool:
    try:
        pyatspi.Registry.generateMouseEvent(coords[0], coords[1], "abs")
        for _ in range(max(1, click_count)):
            pyatspi.Registry.generateMouseEvent(
                coords[0], coords[1], f"b{button}c"
            )
            if delay > 0:
                time.sleep(delay)
        return True
    except Exception:
        return False


def _atspi_mouse_drag(
    src: tuple[int, int], dst: tuple[int, int], button: str = "1"
) -> bool:
    try:
        pyatspi.Registry.generateMouseEvent(src[0], src[1], "abs")
        pyatspi.Registry.generateMouseEvent(src[0], src[1], f"b{button}p")
        pyatspi.Registry.generateMouseEvent(dst[0], dst[1], "abs")
        pyatspi.Registry.generateMouseEvent(dst[0], dst[1], f"b{button}r")
        return True
    except Exception:
        return False


def _parse_int(value: str | None, default: int) -> int:
    try:
        return int(float((value or "").strip()))
    except Exception:
        return default


def _parse_float(value: str | None, default: float) -> float:
    try:
        return float((value or "").strip())
    except Exception:
        return default


def _parse_offset(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    try:
        parts = [p.strip() for p in value.replace(";", ",").split(",")]
        if len(parts) < 2:
            return None
        return int(float(parts[0])), int(float(parts[1]))
    except Exception:
        return None


def _parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    v = value.strip().lower()
    if v in ("true", "yes", "y", "1", "on", "checked", "check"):
        return True
    if v in ("false", "no", "n", "0", "off", "unchecked", "uncheck"):
        return False
    return None


def _parse_click_options(data_set: DataSet) -> dict[str, Any]:
    """Parse optional click parameter rows: type, button, click count, offset, delay, method."""
    opts: dict[str, Any] = {
        "button": "1", "click_count": 1, "offset": None,
        "delay": 0.05, "method": "auto",
    }
    for left, mid, right in data_set:
        left_l = left.strip().lower()
        mid_l = (mid or "").strip().lower()
        right_v = (right or "").strip()
        right_l = right_v.lower()
        if mid_l in _NON_ELEMENT_MIDS or "parameter" not in mid_l and mid_l != "action":
            pass  # parsing happens regardless of mid for action-row keywords
        if left_l == "type":
            if "double click" in right_l:
                opts["click_count"] = 2
            elif "right click" in right_l:
                opts["button"] = "3"
            elif "middle click" in right_l:
                opts["button"] = "2"
        elif left_l in ("button", "click button", "mouse button"):
            opts["button"] = _BUTTON_MAP.get(right_l, opts["button"])
        elif left_l in ("click count", "clicks", "count"):
            opts["click_count"] = max(1, _parse_int(right_v, opts["click_count"]))
        elif left_l == "offset":
            opts["offset"] = _parse_offset(right_v)
        elif left_l in ("delay", "click delay"):
            opts["delay"] = max(0.0, _parse_float(right_v, opts["delay"]))
        elif left_l in ("method", "click method", "click using"):
            opts["method"] = right_l
    return opts


def click_element_by_node(
    node: Accessible | None, options: dict[str, Any] | None = None
) -> Literal["passed", "zeuz_failed"]:
    """Click an Accessible: prefer AT-SPI Action interface, climb to ancestors
    when the leaf has no click-shaped action, then fall back to AT-SPI mouse
    synthesis, then xdotool."""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    if node is None:
        CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
        return "zeuz_failed"

    options = options or _parse_click_options([])
    button = str(options.get("button") or "1")
    click_count = int(options.get("click_count") or 1)
    offset = options.get("offset")
    delay = float(options.get("delay") or 0.05)
    method = str(options.get("method") or "auto").lower()

    original_node = node

    # Stage 1 — AT-SPI Action interface (only when a plain left single-click).
    if method not in ("xdotool", "gui", "mouse") and button == "1" and click_count == 1 and not offset:
        current = node
        while current is not None:
            idx = _action_index(current, _CLICK_ACTION_NAMES)
            if idx >= 0:
                try:
                    iface = current.queryAction()
                    name = iface.getName(idx)
                    iface.doAction(idx)
                    CommonUtil.ExecLog(
                        sModuleInfo, f"Clicked element using action: {name}", 1
                    )
                    return "passed"
                except Exception as e:
                    CommonUtil.ExecLog(
                        sModuleInfo, f"Action '{idx}' failed, falling back: {e}", 2
                    )
                    break
            try:
                current = current.parent
            except Exception:
                break

    # Stage 2 — coord-based clicks (AT-SPI mouse → xdotool).
    coords = get_node_center_coords(original_node, offset=offset)
    if coords:
        app_name = _node_app_name(original_node)
        _activate_window_for_app(app_name)
        if method != "xdotool" and _atspi_mouse_click(
            coords, button=button, click_count=click_count, delay=delay
        ):
            CommonUtil.ExecLog(
                sModuleInfo, f"Clicked element using AT-SPI mouse at: {coords}", 1
            )
            return "passed"
        if click_coords_with_xdotool(
            coords, app_name=app_name, button=button,
            click_count=click_count, delay=delay,
        ):
            CommonUtil.ExecLog(
                sModuleInfo, f"Clicked element using xdotool at: {coords}", 1
            )
            return "passed"
    CommonUtil.ExecLog(sModuleInfo, "All click strategies failed", 3)
    return "zeuz_failed"


def get_node_center_coords(
    node: Accessible | None, offset: tuple[int, int] | None = None
) -> tuple[int, int] | None:
    """Compute desktop-coord click point. With `offset`, returns top-left + offset."""
    rect = _node_rect(node)
    if not rect:
        return None
    x, y, w, h = rect
    if w <= 0 or h <= 0:
        return None
    if offset:
        return x + offset[0], y + offset[1]
    return int(x + w / 2), int(y + h / 2)


def _activate_window_for_app(app_name: str | None) -> bool:
    """Activate/raise the window owned by `app_name`. Returns True on success or
    when no app was specified (treat as 'use whatever is focused')."""
    if not app_name:
        return True
    try:
        winid = _get_window_id_for_app(app_name)
        if not winid:
            CommonUtil.ExecLog(
                MODULE_NAME, f"Could not find a window for app '{app_name}'", 3
            )
            return False
        activated = False
        try:
            subprocess.run(
                ["xdotool", "windowactivate", "--sync", winid], capture_output=True
            )
            activated = True
        except Exception:
            try:
                subprocess.run(["xdotool", "windowactivate", winid], capture_output=True)
                activated = True
            except Exception:
                activated = False
        try:
            subprocess.run(["xdotool", "windowraise", winid], capture_output=True)
        except Exception:
            pass
        try:
            if subprocess.run(["which", "wmctrl"], capture_output=True, text=True).returncode == 0:
                subprocess.run(["wmctrl", "-i", "-a", winid], capture_output=True)
                activated = True
        except Exception:
            pass
        for _ in range(5):
            try:
                active = subprocess.run(
                    ["xdotool", "getactivewindow"], capture_output=True, text=True
                ).stdout.strip()
                if active and active == winid:
                    activated = True
                    break
            except Exception:
                pass
            time.sleep(0.1)
        if not activated:
            CommonUtil.ExecLog(
                MODULE_NAME,
                f"Failed to activate/raise window {winid} for app '{app_name}'",
                3,
            )
        return activated
    except Exception as e:
        CommonUtil.ExecLog(MODULE_NAME, f"Window activation failed: {e}", 3)
        return False


def _xdotool_move(coords: tuple[int, int], app_name: str | None = None) -> bool:
    if not _activate_window_for_app(app_name):
        return False
    try:
        subprocess.run(
            ["xdotool", "mousemove", "--sync", str(coords[0]), str(coords[1])],
            check=True, capture_output=True,
        )
        return True
    except Exception as e:
        CommonUtil.ExecLog(MODULE_NAME, f"xdotool mouse move failed: {e}", 3)
        return False


def _xdotool_click(button: str = "1", click_count: int = 1, delay: float = 0.05) -> bool:
    try:
        for _ in range(max(1, click_count)):
            subprocess.run(["xdotool", "click", str(button)], check=True, capture_output=True)
            if delay > 0:
                time.sleep(delay)
        return True
    except Exception as e:
        CommonUtil.ExecLog(MODULE_NAME, f"xdotool click failed: {e}", 3)
        return False


def _xdotool_drag(
    src: tuple[int, int], dst: tuple[int, int],
    app_name: str | None = None, duration: float = 0.3, button: str = "1",
) -> bool:
    if not _xdotool_move(src, app_name=app_name):
        return False
    try:
        subprocess.run(["xdotool", "mousedown", str(button)], check=True, capture_output=True)
        time.sleep(max(0.0, duration))
        subprocess.run(
            ["xdotool", "mousemove", "--sync", str(dst[0]), str(dst[1])],
            check=True, capture_output=True,
        )
        subprocess.run(["xdotool", "mouseup", str(button)], check=True, capture_output=True)
        return True
    except Exception as e:
        CommonUtil.ExecLog(MODULE_NAME, f"xdotool drag failed: {e}", 3)
        return False


def _xdotool_scroll(direction: str = "down", scroll_count: int = 1) -> bool:
    button = {"up": "4", "down": "5", "left": "6", "right": "7"}.get(direction, "5")
    return _xdotool_click(button=button, click_count=max(1, scroll_count), delay=0.02)


def click_coords_with_xdotool(
    coords: tuple[int, int],
    app_name: str | None = None,
    button: str = "1",
    click_count: int = 1,
    delay: float = 0.05,
) -> bool:
    """Click absolute coords via xdotool, activating the named app window first."""
    if not _xdotool_move(coords, app_name=app_name):
        return False
    time.sleep(0.05)
    return _xdotool_click(button=button, click_count=click_count, delay=delay)


@logger
def click_element_xdotool(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    """Click an element using xdotool by computing coordinates from the resolved node."""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    options = _parse_click_options(data_set)
    node = resolve_node(data_set)
    if node is None:
        CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
        return "zeuz_failed"

    coords = get_node_center_coords(node, offset=options.get("offset"))
    if not coords:
        CommonUtil.ExecLog(sModuleInfo, "Could not determine coordinates for node", 3)
        return "zeuz_failed"

    app_name = _node_app_name(node)
    if not app_name:
        CommonUtil.ExecLog(
            sModuleInfo, "No application context found for xdotool click; aborting", 3
        )
        return "zeuz_failed"
    if click_coords_with_xdotool(
        coords, app_name=app_name,
        button=str(options.get("button") or "1"),
        click_count=int(options.get("click_count") or 1),
        delay=float(options.get("delay") or 0.05),
    ):
        CommonUtil.ExecLog(sModuleInfo, f"Clicked element using xdotool at: {coords}", 1)
        return "passed"
    return "zeuz_failed"


@logger
def click_element(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    """Click an element. Variants (right click, double click, offset) are passed
    as extra rows in the dataset:

      ("type", "optional parameter", "double click" | "right click" | "middle click")
      ("button", "optional parameter", "1" | "2" | "3")
      ("click count", "optional parameter", "1" | "2" | "3")
      ("offset", "optional parameter", "x,y")
      ("delay", "optional parameter", "<seconds>")
      ("method", "optional parameter", "auto" | "xdotool" | "gui")

    The same single declaration covers single, double, triple, right, and middle
    click — Action interface is preferred only for plain left single clicks.
    """
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    options = _parse_click_options(data_set)
    node = resolve_node(data_set)
    if node is None:
        CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
        return "zeuz_failed"

    try:
        if str(options.get("method") or "").lower() in ("xdotool", "gui"):
            return click_element_xdotool(data_set)
        return click_element_by_node(node, options)
    except NotImplementedError:
        CommonUtil.ExecLog(
            sModuleInfo, "This node does not support the Action interface.", 3
        )
        return "zeuz_failed"
    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, f"Failed to click element: {e}", 3)
        return "zeuz_failed"


# --- New actions (accessibility-first) ---------------------------------------


def _parse_desired_check(data_set: DataSet) -> bool:
    """Determine the desired checked state for check/uncheck actions."""
    desired = True
    for left, mid, right in data_set:
        left_l = left.strip().lower()
        mid_l = (mid or "").strip().lower()
        right_l = (right or "").strip().lower()
        if "action" in mid_l and left_l in ("check", "uncheck", "check uncheck"):
            if "uncheck" in left_l or "uncheck" in right_l:
                desired = False
            elif "check" in left_l or "check" in right_l:
                desired = True
            parsed = _parse_bool(right_l)
            if parsed is not None:
                desired = parsed
        elif left_l in ("state", "desired state", "checked"):
            parsed = _parse_bool(right_l)
            if parsed is not None:
                desired = parsed
    return desired


@logger
def check_uncheck(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    """Check/uncheck a toggle. Reads the StateSet, only acts when the current
    state differs, prefers the AT-SPI Action interface (`Toggle`/`Press`),
    then falls back to a click. Verifies the post-action state.
    """
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    desired = _parse_desired_check(data_set)
    node = resolve_node(data_set)
    if node is None:
        CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
        return "zeuz_failed"

    states = _node_state_names(node)
    if states and _is_node_checked(node) == desired:
        CommonUtil.ExecLog(sModuleInfo, "Element already in requested state", 1)
        return "passed"

    names = _CHECK_ACTION_NAMES if desired else _UNCHECK_ACTION_NAMES
    performed = _perform_action(node, names, climb=False)
    if not performed:
        opts = _parse_click_options(data_set)
        opts["button"] = "1"
        opts["click_count"] = 1
        performed = click_element_by_node(node, opts) == "passed"
    if not performed:
        CommonUtil.ExecLog(sModuleInfo, "Could not change element state", 3)
        return "zeuz_failed"

    time.sleep(0.1)
    final_states = _node_state_names(node)
    if final_states and _is_node_checked(node) != desired:
        CommonUtil.ExecLog(
            sModuleInfo, "Element state did not match requested state", 3
        )
        return "zeuz_failed"
    CommonUtil.ExecLog(sModuleInfo, "Element state changed", 1)
    return "passed"


def _absolute_coords_from_dict(data_dict: dict[str, str]) -> tuple[int, int] | None:
    x_value = data_dict.get("x") or data_dict.get("left")
    y_value = data_dict.get("y") or data_dict.get("top")
    if x_value is not None and y_value is not None:
        try:
            return int(float(x_value)), int(float(y_value))
        except Exception:
            return None
    return _parse_offset(data_dict.get("coordinates") or data_dict.get("coords"))


def _grouped_data_set(data_set: DataSet, prefixes: tuple[str, ...]) -> DataSet:
    """Pull rows whose left column begins with any of the given prefixes (e.g.
    'src', 'dst'), stripping the prefix so the residual key looks like a regular
    locator attribute. A bare 'dst' / 'src' row maps to a `path` attribute."""
    out: DataSet = []
    norm = tuple(p.lower() for p in prefixes)
    for left, mid, right in data_set:
        left_s = left.strip()
        left_l = left_s.lower()
        for p in norm:
            if left_l == p:
                out.append(("path", mid or "element parameter", right))
                break
            if left_l.startswith(p + " "):
                out.append((left_s[len(p):].strip(), mid or "element parameter", right))
                break
            if left_l.startswith(p + "_"):
                out.append((left_s[len(p) + 1:].strip(), mid or "element parameter", right))
                break
    return out


def _grouped_dict(data_set: DataSet, prefixes: tuple[str, ...]) -> dict[str, str]:
    grouped = _grouped_data_set(data_set, prefixes)
    d = convert_data_set_to_dict(grouped)
    common = convert_data_set_to_dict(data_set)
    if "app_name" not in d and common.get("app_name"):
        d["app_name"] = common["app_name"]
    return d


def _resolve_endpoint(
    data_dict: dict[str, str], offset: tuple[int, int] | None = None
) -> tuple[Accessible | None, tuple[int, int] | None]:
    """Resolve a drag/drop or hover endpoint as either an Accessible+coords pair
    (when a locator was supplied) or absolute coords (when only x/y were)."""
    coords = _absolute_coords_from_dict(data_dict)
    if coords is not None:
        return None, coords
    if not _build_criteria_from_dict(data_dict) and not data_dict.get("path"):
        return None, None
    node = get_node(data_dict)
    return node, get_node_center_coords(node, offset=offset)


@logger
def hover_over_element(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    """Hover over an element or coords. AT-SPI mouse synthesis preferred."""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    data_dict = convert_data_set_to_dict(data_set)
    options = _parse_click_options(data_set)
    duration = max(0.0, _parse_float(data_dict.get("duration"), 0.3))
    node, coords = _resolve_endpoint(data_dict, offset=options.get("offset"))
    if not coords:
        node = resolve_node(data_set)
        coords = get_node_center_coords(node, offset=options.get("offset"))
    if not coords:
        CommonUtil.ExecLog(sModuleInfo, "Could not resolve hover coordinates", 3)
        return "zeuz_failed"
    app_name = _node_app_name(node) or data_dict.get("app_name")
    if _atspi_mouse_move(coords):
        time.sleep(duration)
        CommonUtil.ExecLog(sModuleInfo, "Hovered using AT-SPI mouse", 1)
        return "passed"
    if _xdotool_move(coords, app_name=app_name):
        time.sleep(duration)
        CommonUtil.ExecLog(sModuleInfo, "Hovered using xdotool", 1)
        return "passed"
    CommonUtil.ExecLog(sModuleInfo, "Hover failed", 3)
    return "zeuz_failed"


@logger
def drag_and_drop_element(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    """Drag from a source locator (or absolute coords) to a destination.

    Accepts `src ...` and `dst ...` (or `source`/`destination`/`target`) prefix
    rows. AT-SPI mouse press/release sequence preferred; falls back to xdotool.
    """
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    src_dict = _grouped_dict(data_set, ("src", "source"))
    dst_dict = _grouped_dict(data_set, ("dst", "dest", "destination", "target"))
    if not src_dict:
        src_dict = convert_data_set_to_dict(data_set)
    if not dst_dict:
        CommonUtil.ExecLog(
            sModuleInfo, "Destination element or coordinates are required", 3
        )
        return "zeuz_failed"

    options = _parse_click_options(data_set)
    src_node, src_coords = _resolve_endpoint(src_dict, offset=options.get("offset"))
    _dst_node, dst_coords = _resolve_endpoint(dst_dict)
    if not src_coords:
        CommonUtil.ExecLog(sModuleInfo, "Could not resolve source coordinates", 3)
        return "zeuz_failed"
    if not dst_coords:
        CommonUtil.ExecLog(sModuleInfo, "Could not resolve destination coordinates", 3)
        return "zeuz_failed"

    app_name = _node_app_name(src_node) or src_dict.get("app_name")
    button = str(options.get("button") or "1")
    duration = _parse_float(convert_data_set_to_dict(data_set).get("duration"), 0.3)
    if _atspi_mouse_drag(src_coords, dst_coords, button=button):
        CommonUtil.ExecLog(sModuleInfo, "Dragged using AT-SPI mouse events", 1)
        return "passed"
    if _xdotool_drag(src_coords, dst_coords, app_name=app_name, duration=duration, button=button):
        CommonUtil.ExecLog(sModuleInfo, "Dragged using xdotool", 1)
        return "passed"
    CommonUtil.ExecLog(sModuleInfo, "Drag and drop failed", 3)
    return "zeuz_failed"


def _scroll_node_into_view(node: Accessible | None) -> bool:
    if node is None:
        return False
    try:
        comp = node.queryComponent()
    except Exception:
        return False
    if not comp:
        return False
    for type_name in (
        "SCROLL_ANYWHERE", "SCROLL_TOP_LEFT", "SCROLL_BOTTOM_RIGHT",
        "SCROLL_TOP_EDGE", "SCROLL_BOTTOM_EDGE",
    ):
        scroll_type = getattr(pyatspi, type_name, None)
        if scroll_type is None:
            continue
        try:
            if hasattr(comp, "scrollTo") and comp.scrollTo(scroll_type):
                return True
        except Exception:
            continue
    return False


def _parse_scroll_options(data_set: DataSet) -> dict[str, Any]:
    opts = {"direction": "down", "scroll_count": 1, "max_try": 50, "delay": 0.1}
    for left, mid, right in data_set:
        left_l = left.strip().lower()
        mid_l = (mid or "").strip().lower()
        right_v = (right or "").strip()
        right_l = right_v.lower()
        if "scroll parameter" in mid_l or "optional parameter" in mid_l:
            if left_l == "direction" and right_l in ("up", "down", "left", "right"):
                opts["direction"] = right_l
            elif left_l in ("scroll count", "count"):
                opts["scroll_count"] = max(1, _parse_int(right_v, opts["scroll_count"]))
            elif left_l in ("max try", "max tries", "retries"):
                opts["max_try"] = max(1, _parse_int(right_v, opts["max_try"]))
            elif left_l == "delay":
                opts["delay"] = max(0.0, _parse_float(right_v, opts["delay"]))
    return opts


@logger
def scroll_to_element(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    """Scroll a target element into view. Tries the AT-SPI Component.scrollTo
    interface first, then falls back to mouse-wheel scrolls under the container.

    With only an element locator, scrolls that element into view. With an
    explicit `desired ...` group plus a container locator, scrolls the container
    until the desired element becomes visible.
    """
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    desired_dict = _grouped_dict(data_set, ("desired", "target", "dst", "destination"))
    container_dict = convert_data_set_to_dict(data_set)
    options = _parse_scroll_options(data_set)

    if not desired_dict:
        node = resolve_node(data_set)
        if node and (_is_node_visible(node) or _scroll_node_into_view(node)):
            CommonUtil.ExecLog(sModuleInfo, "Element visible / scrolled into view", 1)
            return "passed"
        CommonUtil.ExecLog(sModuleInfo, "Element not found for scrolling", 3)
        return "zeuz_failed"

    desired_node = get_node(desired_dict, wait_time=0)
    if desired_node and (_is_node_visible(desired_node) or _scroll_node_into_view(desired_node)):
        CommonUtil.ExecLog(sModuleInfo, "Desired element visible / scrolled in", 1)
        return "passed"

    container_node = get_node(container_dict, wait_time=0) if container_dict else None
    container_coords = get_node_center_coords(container_node)
    _dataset_app_name = container_dict.get("app_name") or desired_dict.get("app_name")
    if _dataset_app_name:
        save_latest_app_name(_dataset_app_name)
    app_name = _node_app_name(container_node) or _dataset_app_name or get_latest_app_name()
    if container_coords:
        _xdotool_move(container_coords, app_name=app_name)
    for _ in range(int(options["max_try"])):
        if container_coords:
            _xdotool_scroll(options["direction"], int(options["scroll_count"]))
        desired_node = get_node(desired_dict, wait_time=0)
        if desired_node and _is_node_visible(desired_node):
            CommonUtil.ExecLog(sModuleInfo, "Scrolled to desired element", 1)
            return "passed"
        time.sleep(float(options["delay"]))
    CommonUtil.ExecLog(sModuleInfo, "Could not scroll to desired element", 3)
    return "zeuz_failed"


@logger
def swap(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    """Swipe/scroll a container element in a given direction."""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    data_dict = convert_data_set_to_dict(data_set)
    options = _parse_scroll_options(data_set)
    node = get_node(data_dict)
    if node is None:
        CommonUtil.ExecLog(sModuleInfo, "Container element not found", 3)
        return "zeuz_failed"
    coords = get_node_center_coords(node)
    if coords is None:
        CommonUtil.ExecLog(sModuleInfo, "Could not get element coordinates", 3)
        return "zeuz_failed"
    _dataset_app_name = data_dict.get("app_name")
    if _dataset_app_name:
        save_latest_app_name(_dataset_app_name)
    app_name = _node_app_name(node) or _dataset_app_name or get_latest_app_name()
    if not _xdotool_move(coords, app_name=app_name):
        CommonUtil.ExecLog(sModuleInfo, "Could not position mouse on element", 3)
        return "zeuz_failed"
    _xdotool_scroll(options["direction"], int(options["scroll_count"]))
    CommonUtil.ExecLog(sModuleInfo, f"Swiped {options['direction']}", 1)
    return "passed"


@logger
def select_item(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    """Select a child item via the parent's AT-SPI Selection interface, falling
    back to a click on the item itself."""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    node = resolve_node(data_set)
    if node is None:
        CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
        return "zeuz_failed"
    parent = None
    try:
        parent = node.parent
    except Exception:
        parent = None
    if parent is not None:
        try:
            sel = parent.querySelection()
            if sel is not None:
                idx = -1
                try:
                    idx = node.get_index_in_parent()
                except Exception:
                    for i in range(len(parent)):
                        if parent[i] == node:
                            idx = i
                            break
                if idx >= 0:
                    try:
                        sel.selectChild(idx)
                        CommonUtil.ExecLog(
                            sModuleInfo, f"Selected child index {idx} via Selection", 1
                        )
                        return "passed"
                    except Exception:
                        pass
        except (NotImplementedError, Exception):
            pass
    return click_element_by_node(node)


@logger
def set_value(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    """Set a numeric value via AT-SPI Value interface, with Increase/Decrease
    Action fallback for elements that expose those instead."""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    data_dict = convert_data_set_to_dict(data_set)
    raw = data_dict.get("value") or data_dict.get("text") or ""
    if raw == "":
        CommonUtil.ExecLog(sModuleInfo, "No value provided", 3)
        return "zeuz_failed"
    try:
        target = float(str(raw).strip())
    except Exception:
        CommonUtil.ExecLog(sModuleInfo, f"Value must be numeric, got: {raw}", 3)
        return "zeuz_failed"
    node = resolve_node(data_set)
    if node is None:
        CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
        return "zeuz_failed"
    try:
        v_iface = node.queryValue()
        if v_iface is not None:
            v_iface.currentValue = target
            CommonUtil.ExecLog(sModuleInfo, f"Set value to {target} via Value iface", 1)
            return "passed"
    except (NotImplementedError, AttributeError):
        pass
    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, f"Value interface failed: {e}", 2)

    try:
        current = float(node.queryValue().currentValue)
    except Exception:
        current = 0.0
    direction = "Increase" if target > current else "Decrease"
    steps = int(abs(target - current))
    for _ in range(max(1, steps)):
        if not _perform_action(node, {direction.lower()}, climb=False):
            CommonUtil.ExecLog(
                sModuleInfo, f"No {direction} action and no Value iface", 3
            )
            return "zeuz_failed"
    CommonUtil.ExecLog(sModuleInfo, f"Adjusted value via {direction} action", 1)
    return "passed"


@logger
def go_to_desktop(data_set: DataSet | None = None) -> Literal["passed", "zeuz_failed"]:
    """Show the desktop (minimize/hide all windows). Tries wmctrl first, then
    common keyboard shortcuts via xdotool."""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    commands = [
        ["wmctrl", "-k", "on"],
        ["xdotool", "key", "super+d"],
        ["xdotool", "key", "ctrl+alt+d"],
    ]
    for cmd in commands:
        try:
            res = subprocess.run(cmd, capture_output=True)
            if res.returncode == 0:
                CommonUtil.ExecLog(
                    sModuleInfo, f"Switched to desktop via {' '.join(cmd)}", 1
                )
                return "passed"
        except FileNotFoundError:
            continue
        except Exception:
            continue
    CommonUtil.ExecLog(sModuleInfo, "Could not switch to desktop", 3)
    return "zeuz_failed"


def enter_text_in_node(
    app_name: str, node: Accessible | None, text: str
) -> Literal["passed", "zeuz_failed"]:
    """Enter text into a node. Grabs focus before EditableText.setTextContents
    (some toolkits drop the change otherwise) and climbs to ancestors when the
    leaf has no EditableText interface."""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    if node is None:
        CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
        return "zeuz_failed"

    current = node
    while current:
        try:
            editable_iface = current.queryEditableText()
            if editable_iface:
                _grab_focus(current)
                editable_iface.setTextContents(text)
                CommonUtil.ExecLog(sModuleInfo, f"Entered text: {text}", 1)
                return "passed"
            if simulate_keyboard_typing(app_name, current, text):
                return "passed"
            current = current.parent
            continue
        except NotImplementedError:
            if simulate_keyboard_typing(app_name, current, text):
                return "passed"
            current = current.parent
            continue
        except Exception as e:
            CommonUtil.ExecLog(sModuleInfo, f"Failed enter text: {e}", 3)
            return "zeuz_failed"
    return "zeuz_failed"


@logger
def enter_text(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    """Enter text into the resolved element."""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    data_dict = convert_data_set_to_dict(data_set)
    app_name = data_dict.get("app_name", "").strip()
    if app_name:
        save_latest_app_name(app_name)
    else:
        app_name = get_latest_app_name() or ""
    # The element locator uses `text=` for matching; the value to type comes from
    # the action row (mid="action"). Pull that explicitly so the locator's text
    # criterion stays distinct from the input value.
    text_to_type = ""
    for left, mid, right in data_set:
        if (mid or "").strip().lower() == "action" and left.strip().lower() == "text":
            text_to_type = (right or "").strip()
            break
    if not text_to_type:
        text_to_type = data_dict.get("text", "").strip()
    if not text_to_type:
        CommonUtil.ExecLog(sModuleInfo, "No text provided to enter", 3)
        return "zeuz_failed"
    if not app_name:
        CommonUtil.ExecLog(sModuleInfo, "No app_name provided to enter text", 3)
        return "zeuz_failed"
    node = resolve_node(data_set)
    if node is None:
        CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
        return "zeuz_failed"

    try:
        return enter_text_in_node(app_name, node, text_to_type)
    except NotImplementedError:
        CommonUtil.ExecLog(
            sModuleInfo, "This node does not support the Action interface.", 3
        )
        return "zeuz_failed"
    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, f"Failed to enter text: {e}", 3)
        return "zeuz_failed"


def parse_desktop_file(desktop_file: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse a desktop file to extract Name and Exec command."""
    name = None
    exec_cmd = None

    try:
        with open(desktop_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("Name=") and not line.startswith("Name["):
                    name = line[5:]
                elif line.startswith("Exec="):
                    exec_cmd = line[5:]
                    # Remove common exec field codes (%f, %F, %u, %U, etc.)
                    exec_cmd = (
                        exec_cmd.replace("%f", "")
                        .replace("%F", "")
                        .replace("%u", "")
                        .replace("%U", "")
                    )
                    exec_cmd = (
                        exec_cmd.replace("%d", "")
                        .replace("%D", "")
                        .replace("%n", "")
                        .replace("%N", "")
                    )
                    exec_cmd = (
                        exec_cmd.replace("%i", "")
                        .replace("%c", "")
                        .replace("%k", "")
                        .replace("%v", "")
                    )
                    exec_cmd = exec_cmd.strip()

                # Stop if we found both
                if name and exec_cmd:
                    break
    except Exception:
        pass

    return name, exec_cmd


def find_best_app_match(user_input: str) -> Optional[Tuple[str, str, str]]:
    """Find the best matching application and return (key, name, exec_cmd)."""
    apps = {}

    try:
        desktop_files = glob.glob("/usr/share/applications/*.desktop")
        for desktop_file in desktop_files:
            name, exec_cmd = parse_desktop_file(desktop_file)
            if name and exec_cmd:
                # Use the desktop file basename as the key for matching
                key = os.path.basename(desktop_file).replace(".desktop", "")
                apps[key] = (name, exec_cmd)
    except Exception:
        pass

    user_lower = user_input.lower()

    for key, (name, exec_cmd) in apps.items():
        if key.lower() == user_lower:
            return key, name, exec_cmd

    for key, (name, exec_cmd) in apps.items():
        if name.lower() == user_lower:
            return key, name, exec_cmd

    return None


@logger
def open_app(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    """Open application using element, first get the element then open app"""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    data_dict = convert_data_set_to_dict(data_set)
    app_name = data_dict.get("open app", "").strip()
    if not app_name:
        app_name = data_dict.get("app_name", "").strip()

    _, matched_app, exec_cmd = find_best_app_match(app_name) or (None, None, None)

    before_apps = _get_atspi_apps()

    def _record_launch(launched: str):
        atspi_name = _discover_atspi_app_name(launched, before_apps)
        if atspi_name and atspi_name.lower() != launched.lower():
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Accessibility tree name resolved to: '{atspi_name}'",
                1,
            )
        save_latest_app_name(atspi_name or launched)

    if matched_app:
        if matched_app != app_name:
            CommonUtil.ExecLog(
                MODULE_NAME, f"Best match found: {matched_app} for {app_name}", 1
            )
        try:
            command = f"nohup {exec_cmd} >/dev/null 2>&1 &"
            exit_code = os.system(command)
            if exit_code == 0:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Successfully launched '{app_name}' with command: {command}",
                    1,
                )
                _record_launch(app_name)
                return "passed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Failed to launch '{app_name}' (exit code: {exit_code})",
                    3,
                )
                return "zeuz_failed"

        except Exception as e:
            CommonUtil.ExecLog(sModuleInfo, f"Error launching '{app_name}': {e}", 3)
            return "zeuz_failed"
    else:
        try:
            command = f"nohup {app_name} >/dev/null 2>&1 &"
            exit_code = os.system(command)
            if exit_code == 0:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Successfully launched '{app_name}' with command: {command}",
                    1,
                )
                _record_launch(app_name)
                return "passed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Failed to launch '{app_name}' (exit code: {exit_code})",
                    3,
                )
                return "zeuz_failed"
        except Exception as e:
            CommonUtil.ExecLog(sModuleInfo, f"Error launching '{app_name}': {e}", 3)
            return "zeuz_failed"


def get_process_ids(app_name: str) -> List[str]:
    """Get process ID of the application by name"""
    try:
        process_ids = (
            subprocess.run(["pgrep", "-f", app_name], capture_output=True, text=True)
            .stdout.strip()
            .splitlines()
        )
        return [pid for pid in process_ids if pid.isdigit()]
    except Exception as e:
        CommonUtil.ExecLog(
            MODULE_NAME, f"Error getting process ID for '{app_name}': {e}", 3
        )
        return []


@logger
def close_app(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    """Close application using element, first get the element then close app"""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    data_dict = convert_data_set_to_dict(data_set)
    app_name = data_dict.get("app_name", "").strip()
    if app_name:
        save_latest_app_name(app_name)
    else:
        app_name = get_latest_app_name() or ""

    app_key, matched_app, exec_cmd = find_best_app_match(app_name) or (None, None, None)
    if app_key:
        app_key = app_key.split(".")[-1]

    if matched_app:
        if matched_app != app_name:
            CommonUtil.ExecLog(
                MODULE_NAME, f"Best match found: {matched_app} for {app_name}", 1
            )
        try:
            # get the process ID of the application
            process_ids = get_process_ids(matched_app)
            if not process_ids and exec_cmd:
                process_ids = get_process_ids(exec_cmd)
                if not process_ids and app_key:
                    process_ids = get_process_ids(app_key)
                    if not process_ids:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            f"No running process found for Name: '{app_name}', Key: '{app_key}', Command: '{exec_cmd}'",
                            3,
                        )
                        return "zeuz_failed"

            # kill the process
            for pid in process_ids:
                command = f"kill -9 {pid}"
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Closing application '{matched_app}' with command: {command}",
                    1,
                )
                exit_code = os.system(command)
                if exit_code != 0:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        f"Failed to close application '{matched_app}' with PID {pid} (exit code: {exit_code})",
                        3,
                    )
                    return "zeuz_failed"
            if process_ids:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Successfully closed application '{matched_app}' with PIDs: {', '.join(process_ids)}",
                    1,
                )
                return "passed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo, f"No running process found for '{matched_app}'", 3
                )
                return "zeuz_failed"

        except Exception as e:
            CommonUtil.ExecLog(sModuleInfo, f"Error launching '{app_name}': {e}", 3)
            return "zeuz_failed"
    else:
        CommonUtil.ExecLog(
            MODULE_NAME, f"No matching application found for '{app_name}'", 3
        )
        return "zeuz_failed"


@logger
def wait_for_element(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME
    try:
        timeout_duration = 10
        appear_condition = True
        for left, mid, right in data_set:
            if (mid or "").strip().lower() != "action":
                continue
            left_l = left.strip().lower()
            if left_l == "wait to disappear":
                appear_condition = False
            right_v = (right or "").strip()
            parsed_timeout = _parse_int(right_v, -1)
            if parsed_timeout > 0:
                timeout_duration = parsed_timeout

        end_time = time.time() + timeout_duration
        while time.time() <= end_time:
            node = resolve_node(data_set, wait_time=0)
            if appear_condition and node:
                CommonUtil.ExecLog(sModuleInfo, "Found element", 1)
                return "passed"
            if not appear_condition and not node:
                CommonUtil.ExecLog(sModuleInfo, "Element disappeared", 1)
                return "passed"
            time.sleep(1)

        CommonUtil.ExecLog(sModuleInfo, "Wait for element failed", 3)
        return "zeuz_failed"

    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, f"Error while waiting for element: {e}", 3)
        return "zeuz_failed"


def get_attribute_value(tag_str: str, attr_name: str) -> str | None:
    pattern = rf'{attr_name}="(.*?)"'
    match = re.search(pattern, tag_str)
    return match.group(1) if match else None


@logger
def save_attribute(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    try:
        variable_name = ""
        field = "value"
        for left, mid, right in data_set:
            if (mid or "").strip().lower() == "save parameter":
                field = left.replace(" ", "").lower()
                variable_name = (right or "").strip()

        node = resolve_node(data_set)
        if node is None:
            return "zeuz_failed"
        tag_str = (dump_node(node, recursive=False) or ["", ""])[0]
        actual_text = get_attribute_value(tag_str, field)

        if actual_text is None:
            CommonUtil.ExecLog(
                sModuleInfo, f"Attribute '{field}' not found in the element", 3
            )
            return "zeuz_failed"

        Shared_Resources.Set_Shared_Variables(variable_name, actual_text)
        CommonUtil.ExecLog(
            sModuleInfo,
            f"Text '{actual_text}' is saved in the variable '{variable_name}'",
            1,
        )
        return "passed"
    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, f"Error while saving attribute: {e}", 3)
        return "zeuz_failed"


def is_valid_hotkey(hotkey: str) -> bool:
    """
    Validates hotkey: all lowercase, only modifiers + known keys.
    """
    MODIFIERS = {"ctrl", "alt", "shift", "super", "meta"}
    KEYS = {
        "return",
        "enter",
        "tab",
        "escape",
        "esc",
        "backspace",
        "delete",
        "up",
        "down",
        "left",
        "right",
        "home",
        "end",
        "page_up",
        "page_down",
        "insert",
        "space",
        *(f"f{i}" for i in range(1, 13)),
    }
    parts = hotkey.split("+")
    if not parts:
        return False

    *mods, key = parts
    if any(mod not in MODIFIERS for mod in mods):
        return False

    return key in KEYS or (len(key) == 1 and key.isalnum())


def send_hotkey(hotkey: str) -> bool:
    """
    Sends a lowercase hotkey (e.g., 'ctrl+a', 'alt+f4') using xdotool.
    """
    hotkey = hotkey.lower()

    if not is_valid_hotkey(hotkey):
        CommonUtil.ExecLog(
            MODULE_NAME, f"Invalid hotkey: {hotkey}. Space is not allowed", 3
        )
        return False

    try:
        subprocess.run(["xdotool", "key", hotkey], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        CommonUtil.ExecLog(
            MODULE_NAME, f"Error sending hotkey '{hotkey}': {e.stderr.decode()}", 3
        )
        return False


@logger
def send_keystroke(data_set: DataSet) -> Literal["passed", "zeuz_failed"]:
    """Insert characters - mainly key combinations and single key presses."""
    frame = inspect.currentframe()
    sModuleInfo = (frame.f_code.co_name if frame else "unknown") + " : " + MODULE_NAME

    keystroke_value = ""
    keystroke_char = ""
    for left, mid, right in data_set:
        left = left.strip().lower()
        if "action" in mid.lower():
            if left == "keystroke keys":
                keystroke_value = right.strip().lower()
            elif left == "keystroke chars":
                keystroke_char = right.strip().lower()

    if keystroke_value == "" and keystroke_char == "":
        CommonUtil.ExecLog(sModuleInfo, "Invalid action found", 3)
        return "zeuz_failed"

    if keystroke_value != "" and keystroke_char != "":
        CommonUtil.ExecLog(
            sModuleInfo,
            "Both keystroke keys and characters are provided, only one is supported",
            3,
        )
        return "zeuz_failed"

    success = True
    if keystroke_char != "":
        success = simulate_keyboard_typing(None, None, keystroke_char)
    else:
        key_combinations = keystroke_value.split(",")
        for hotkey in key_combinations:
            success_tem = send_hotkey(hotkey.strip())
            if not success:
                CommonUtil.ExecLog(
                    sModuleInfo, f"Failed to send hotkey: {hotkey.strip()}", 3
                )
            success = success and success_tem
    if success:
        return "passed"
    else:
        CommonUtil.ExecLog(sModuleInfo, "Failed to send some or all keystroke", 3)
        return "zeuz_failed"
