"""Synchronous Playwright counterparts for ZeuZ Selenium actions."""

import ast
import base64
import functools
import inspect
import socket
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from Framework.Built_In_Automation.Shared_Resources import LocateElement
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from Framework.Built_In_Automation.Sequential_Actions.action_declarations.playwright import (
    declarations,
)
from Framework.Utilities import CommonUtil, ConfigModule
from Framework.Utilities.CommonUtil import failed_tag_list


MODULE_NAME = inspect.getmodulename(__file__)
playwright_details = {}
playwright_page = None
current_driver_id = None
_playwright = None


def _log(message, level=1):
    CommonUtil.ExecLog(MODULE_NAME, message, level)


def _fail(message):
    _log(message, 3)
    return "zeuz_failed"


def _rows(data_set):
    return [
        (str(left).strip(), str(middle).strip().lower(), str(right).strip())
        for left, middle, right in data_set
    ]


def _key(value):
    return value.replace(" ", "").replace("_", "").replace("-", "").lower()


def _action(data_set, default=""):
    return next(
        (right for _left, middle, right in _rows(data_set) if "action" in middle),
        default,
    )


def _driver_id(data_set, default=None):
    for left, _middle, right in _rows(data_set):
        if _key(left) in ("driverid", "drivertag"):
            return right or "default"
    return default or current_driver_id or "default"


def _state():
    if current_driver_id not in playwright_details:
        raise RuntimeError(
            "No active Playwright browser. Run 'open browser' or 'go to link' first."
        )
    return playwright_details[current_driver_id]


def get_driver():
    state = _state()
    return state.get("frame") or state["page"]


def get_page():
    return _state()["page"]


def get_dom(_data_set=()):
    return get_page().evaluate("""() => {
        const html = document.documentElement.cloneNode(true);
        html.setAttribute('zeuz', 'aiplugin');
        html.querySelectorAll('head,link,script,style').forEach(node => node.remove());
        return html.outerHTML.replace(/[\\x00-\\x08\\x0B-\\x1F\\x7F]/g, '');
    }""")


def _element(data_set, all_elements=False, root=None):
    return LocateElement.Get_Element(
        data_set, root or get_driver(), return_all_elements=all_elements
    )


def _set_active(driver_id):
    global current_driver_id, playwright_page
    current_driver_id = driver_id
    state = playwright_details[driver_id]
    playwright_page = state["page"]
    sr.Set_Shared_Variables("playwright_page", playwright_page)
    sr.Set_Shared_Variables("common_driver", state.get("frame") or playwright_page)
    _publish_selenium_bridge(state.get("selenium_bridge"))
    sr.Set_Shared_Variables("zeuz_active_browser_backend", "playwright")
    owners = sr.Get_Shared_Variables("zeuz_browser_backends", log=False)
    owners = owners if isinstance(owners, dict) else {}
    owners[driver_id] = "playwright"
    sr.Set_Shared_Variables("zeuz_browser_backends", owners)
    CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())


def _publish_selenium_bridge(driver):
    from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as selenium

    selenium.selenium_driver = driver
    if driver is None:
        sr.Remove_From_Shared_Variables("selenium_driver")
    else:
        sr.Set_Shared_Variables("selenium_driver", driver)


def _free_local_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _selenium_cdp_address(browser_name, debugger, arguments):
    if not any(name in browser_name for name in ("chrome", "edge", "chromium")):
        return None
    if debugger:
        parsed = urlparse(debugger if "://" in debugger else "//" + debugger)
        if not parsed.hostname or not parsed.port:
            raise ValueError(f"Invalid debugger address '{debugger}'")
        return f"{parsed.hostname}:{parsed.port}"

    port = None
    for index, argument in enumerate(arguments):
        if str(argument).startswith("--remote-debugging-port="):
            port = int(str(argument).split("=", 1)[1])
            if port == 0:
                port = _free_local_port()
                arguments[index] = f"--remote-debugging-port={port}"
            break
    if port is None:
        port = _free_local_port()
        arguments.extend(
            [f"--remote-debugging-port={port}", "--remote-debugging-address=127.0.0.1"]
        )
    return f"127.0.0.1:{port}"


def _attach_selenium_bridge(state, browser_name, debugger_address):
    if not debugger_address:
        state["selenium_bridge"] = None
        _log(
            "Selenium execute-python compatibility is unavailable for Playwright Firefox/WebKit",
            2,
        )
        return
    try:
        from selenium import webdriver

        if "edge" in browser_name:
            from selenium.webdriver.edge.options import Options

            options = Options()
            options.debugger_address = debugger_address
            driver = webdriver.Edge(options=options)
        else:
            from selenium.webdriver.chrome.options import Options

            options = Options()
            options.debugger_address = debugger_address
            driver = webdriver.Chrome(options=options)
        state["selenium_bridge"] = driver
        _log("Attached Selenium compatibility bridge to Playwright browser", 1)
    except Exception as error:
        state["selenium_bridge"] = None
        _log(f"Could not attach Selenium compatibility bridge: {error}", 2)


def _close_selenium_bridge(state):
    driver = state.pop("selenium_bridge", None)
    if driver is not None:
        try:
            driver.quit()
        except Exception:
            _log("Unable to close Selenium compatibility bridge", 2)


def _parse(value):
    try:
        return CommonUtil.parse_value_into_object(value)
    except Exception:
        try:
            return ast.literal_eval(value)
        except Exception:
            return value


def _next_alert_instruction():
    try:
        step_data = sr.Get_Shared_Variables("step_data", log=False)
        index = int(CommonUtil.current_action_no)
        if not isinstance(step_data, list) or index >= len(step_data):
            return "dismiss", None
        for left, middle, right in _rows(step_data[index]):
            if left.lower() == "handle alert" and "action" in middle:
                value = right.strip()
                lower = value.lower()
                if lower.startswith("send text"):
                    return "accept", value.split("=", 1)[-1].strip()
                if lower in ("reject", "fail", "no", "cancel", "dismiss"):
                    return "dismiss", None
                return "accept", None
    except Exception:
        pass
    return "dismiss", None


def _on_dialog(state, dialog):
    instruction, prompt = _next_alert_instruction()
    state["dialog"] = {
        "text": dialog.message,
        "type": dialog.type,
        "result": instruction,
    }
    if instruction == "accept":
        dialog.accept(prompt)
    else:
        dialog.dismiss()


def _wire_page(state, page):
    state["page"] = page
    state["frame"] = None
    state["frame_stack"] = []
    wired_pages = state.setdefault("wired_pages", set())
    if id(page) in wired_pages:
        return
    wired_pages.add(id(page))
    page.on("dialog", lambda dialog: _on_dialog(state, dialog))
    page.on("download", lambda download: state["downloads"].append(download))
    page.on(
        "request",
        lambda request: state["network"].append(
            {
                "type": "request",
                "method": request.method,
                "url": request.url,
                "headers": request.headers,
                "post_data": request.post_data,
            }
        )
        if state["capturing_network"]
        else None,
    )
    page.on(
        "response",
        lambda response: state["network"].append(
            {
                "url": response.url,
                "status": response.status,
                "method": response.request.method,
                "mimeType": response.headers.get("content-type", "").split(";", 1)[0],
                "type": response.request.resource_type,
                "timestamp": time.time(),
                "_response": response,
            }
        )
        if state["capturing_network"]
        else None,
    )
    if not state.get("page_listener"):
        page.context.on("page", lambda new_page: _wire_page(state, new_page))
        state["page_listener"] = True


def _launch(data_set):
    from playwright.sync_api import sync_playwright

    global _playwright
    dependency = sr.Get_Shared_Variables("dependency")
    browser_name = str(dependency.get("Browser", "Chrome")).strip().lower()
    if "opera" in browser_name:
        raise RuntimeError("Opera is not supported by Playwright")

    driver_id = _driver_id(data_set, "default")
    if driver_id in playwright_details:
        _set_active(driver_id)
        return playwright_details[driver_id]

    if _playwright is None:
        _playwright = sync_playwright().start()

    headless = "headless" in browser_name
    launch = {"headless": headless}
    context_options = {"accept_downloads": True}
    wait_until = "load"
    url = None
    debugger = None
    firefox_prefs = {}
    arguments = []

    for left, middle, right in _rows(data_set):
        key = _key(left)
        value = _parse(right)
        if key in ("gotolink", "gotolinkv2") and right:
            url = right
        elif key in ("waittimetopageload", "pageloadtimeout"):
            context_options["timeout"] = float(right) * 1000
        elif key == "resolution":
            width, height = (
                int(part.strip())
                for part in right.lower().replace("x", ",").split(",", 1)
            )
            context_options["viewport"] = {"width": width, "height": height}
        elif key in ("addargument", "argument"):
            supplied = value if isinstance(value, list) else [right]
            for argument in supplied:
                if "load-extension" in str(argument) and any(
                    name in browser_name for name in ("chrome", "edge")
                ):
                    _log(
                        "Playwright ignores extension sideloading on branded Chrome/Edge",
                        2,
                    )
                else:
                    arguments.append(argument)
        elif key == "pageloadstrategy":
            wait_until = {
                "normal": "load",
                "eager": "domcontentloaded",
                "none": "commit",
            }.get(right.lower(), "load")
        elif key == "debuggeraddress":
            debugger = right
        elif key in ("proxy", "proxyserver"):
            context_options["proxy"] = (
                value if isinstance(value, dict) else {"server": right}
            )
        elif key == "locale":
            context_options["locale"] = right
        elif key in ("useragent", "user-agent"):
            context_options["user_agent"] = right
        elif key == "permissions":
            context_options["permissions"] = (
                value
                if isinstance(value, list)
                else [part.strip() for part in right.split(",")]
            )
        elif key in ("ignorehttpserrors", "accepthttpscerts"):
            context_options["ignore_https_errors"] = (
                str(right).lower() in CommonUtil.affirmative_words
            )
        elif key == "setpreference" and "firefox" in middle:
            if isinstance(value, dict):
                firefox_prefs.update(value)
        elif key in (
            "addextension",
            "addencodedextension",
            "chromeversion",
            "setcapability",
            "addexperimentaloption",
        ):
            _log(f"Playwright ignores unsupported Selenium option '{left}'", 2)
        elif middle == "shared capability":
            _log(f"Playwright ignores unsupported Selenium capability '{left}'", 2)

    selenium_cdp_address = _selenium_cdp_address(browser_name, debugger, arguments)
    launch["args"] = arguments
    if firefox_prefs:
        launch["firefox_user_prefs"] = firefox_prefs
    state = {
        "browser": None,
        "context": None,
        "page": None,
        "frame": None,
        "backend": "playwright",
        "downloads": [],
        "dialog": None,
        "network": [],
        "capturing_network": False,
        "wait_until": wait_until,
        "selenium_bridge": None,
    }

    if debugger:
        if not any(name in browser_name for name in ("chrome", "edge", "chromium")):
            raise RuntimeError(
                "CDP debugger attachment is only supported for Chromium browsers"
            )
        endpoint = debugger if "://" in debugger else "http://" + debugger
        browser = _playwright.chromium.connect_over_cdp(endpoint)
        context = (
            browser.contexts[0]
            if browser.contexts
            else browser.new_context(**context_options)
        )
    else:
        if "firefox" in browser_name:
            browser_type = _playwright.firefox
        elif "safari" in browser_name or "webkit" in browser_name:
            browser_type = _playwright.webkit
        else:
            browser_type = _playwright.chromium
            launch["channel"] = "msedge" if "edge" in browser_name else "chrome"
        browser = browser_type.launch(**launch)
        context = browser.new_context(
            **{key: value for key, value in context_options.items() if key != "timeout"}
        )
        if "timeout" in context_options:
            context.set_default_navigation_timeout(context_options["timeout"])

    state["browser"], state["context"] = browser, context
    page = context.pages[-1] if context.pages else context.new_page()
    _wire_page(state, page)
    _attach_selenium_bridge(state, browser_name, selenium_cdp_address)
    playwright_details[driver_id] = state
    _set_active(driver_id)
    if url:
        page.goto(url, wait_until=wait_until)
    return state


def Go_To_Link(data_set):
    try:
        state = _launch(data_set)
        _wire_page(state, state["page"])
        _set_active(current_driver_id)
        url = next(
            (
                right
                for left, _middle, right in _rows(data_set)
                if _key(left) in ("gotolink", "gotolinkv2")
            ),
            None,
        )
        if url and state["page"].url != url:
            state["page"].goto(url, wait_until=state["wait_until"])
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Failed to open Playwright browser"
        )


Go_To_Link_V2 = Go_To_Link


def Open_Electron_App(data_set):
    from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as selenium

    return selenium.Open_Electron_App(data_set)


def Tear_Down_Selenium(data_set=()):
    global _playwright, current_driver_id, playwright_page
    try:
        requested = (
            _driver_id(data_set)
            if any(_key(left) == "driverid" for left, _, _ in _rows(data_set))
            else None
        )
        ids = [requested] if requested else list(playwright_details)
        for driver_id in ids:
            state = playwright_details.pop(driver_id, None)
            if not state:
                continue
            try:
                _close_selenium_bridge(state)
                state["context"].close()
            finally:
                state["browser"].close()
        owners = sr.Get_Shared_Variables("zeuz_browser_backends", log=False)
        owners = owners if isinstance(owners, dict) else {}
        for driver_id in ids:
            if owners.get(driver_id) == "playwright":
                owners.pop(driver_id, None)
        sr.Set_Shared_Variables("zeuz_browser_backends", owners)
        if playwright_details:
            _set_active(next(iter(playwright_details)))
        else:
            if _playwright is not None:
                _playwright.stop()
            _playwright = None
            current_driver_id = playwright_page = None
            sr.Remove_From_Shared_Variables("playwright_page")
            _publish_selenium_bridge(None)
        return "passed"
    except Exception:
        _log("Unable to tear down Playwright browsers", 2)
        return "passed"


def Switch_Browser(data_set):
    driver_id = _driver_id(data_set, "default")
    if driver_id not in playwright_details:
        return _fail(f"Driver_id='{driver_id}' not found")
    _set_active(driver_id)
    return "passed"


def Get_Current_URL(data_set):
    name = _action(data_set)
    return (
        sr.Set_Shared_Variables(name, get_page().url)
        if name
        else _fail("Missing variable name")
    )


def Navigate(data_set):
    value = _action(data_set).lower()
    page = get_page()
    if value == "back":
        page.go_back()
    elif value == "forward":
        page.go_forward()
    elif value == "refresh":
        page.reload()
    else:
        return _fail("Only back, forward, and refresh are supported")
    return "passed"


def Click_Element(data_set):
    element = _element(data_set)
    if element in failed_tag_list:
        return "zeuz_failed"
    options = {}
    for left, middle, right in _rows(data_set):
        if (
            middle in ("optional parameter", "optional option")
            and _key(left) == "offset"
        ):
            x, y = (float(part) for part in right.split(",", 1))
            box = element.bounding_box()
            if not box:
                return "zeuz_failed"
            options["position"] = {
                "x": box["width"] / 2 * (1 + x / 100),
                "y": box["height"] / 2 * (1 + y / 100),
            }
        elif _key(left) == "usejs" and right.lower() in CommonUtil.affirmative_words:
            element.evaluate("element => element.click()")
            return "passed"
    element.click(**options)
    return "passed"


def Click_and_Download(data_set):
    timeout = (
        next(
            (
                float(right)
                for left, _, right in _rows(data_set)
                if _key(left) == "waitfordownload"
            ),
            20,
        )
        * 1000
    )
    path = next(
        (
            CommonUtil.path_parser(right)
            for left, middle, right in _rows(data_set)
            if _key(left) in ("folderpath", "directory", "filepath", "file", "folder")
            and middle.startswith("optional")
        ),
        None,
    )
    with get_page().expect_download(timeout=timeout) as info:
        result = Click_Element(data_set)
    if result in failed_tag_list:
        return result
    download = info.value
    if path:
        destination = Path(path)
        if destination.is_dir() or not destination.suffix:
            destination.mkdir(parents=True, exist_ok=True)
            destination /= download.suggested_filename
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
        download.save_as(str(destination))
    return "passed"


def Right_Click_Element(data_set):
    element = _element(data_set)
    if element in failed_tag_list:
        return "zeuz_failed"
    element.click(button="right")
    return "passed"


def Double_Click_Element(data_set):
    element = _element(data_set)
    if element in failed_tag_list:
        return "zeuz_failed"
    element.dblclick()
    return "passed"


def Hover_Over_Element(data_set):
    element = _element(data_set)
    if element in failed_tag_list:
        return "zeuz_failed"
    element.hover()
    return "passed"


_KEYS = {
    "CTRL": "Control",
    "CONTROL": "Control",
    "CMD": "Meta",
    "COMMAND": "Meta",
    "ALT": "Alt",
    "SHIFT": "Shift",
    "ENTER": "Enter",
    "RETURN": "Enter",
    "ESC": "Escape",
    "ESCAPE": "Escape",
    "TAB": "Tab",
    "SPACE": "Space",
    "BACKSPACE": "Backspace",
    "DELETE": "Delete",
    "HOME": "Home",
    "END": "End",
    "UP": "ArrowUp",
    "DOWN": "ArrowDown",
    "LEFT": "ArrowLeft",
    "RIGHT": "ArrowRight",
}


def Keystroke_For_Element(data_set):
    field, value = next(
        (
            (left.lower(), right)
            for left, middle, right in _rows(data_set)
            if "action" in middle
        ),
        ("", ""),
    )
    element = (
        _element(data_set)
        if any("element parameter" in middle for _, middle, _ in _rows(data_set))
        else None
    )
    keyboard = get_page().keyboard
    if "chars" in field:
        element.type(value) if element else keyboard.type(value)
    else:
        key, _, count = value.partition(",")
        combo = "+".join(
            _KEYS.get(part.strip().upper(), part.strip()) for part in key.split("+")
        )
        for _ in range(int(count or 1)):
            element.press(combo) if element else keyboard.press(combo)
    return "passed"


def Enter_Text_In_Text_Box(data_set):
    element = _element(data_set)
    if element in failed_tag_list:
        return "zeuz_failed"
    value = _action(data_set)
    append = any(
        _key(left) == "append" and right.lower() in CommonUtil.affirmative_words
        for left, _, right in _rows(data_set)
    )
    element.type(value) if append else element.fill(value)
    return "passed"


def Validate_Text(data_set):
    element = _element(data_set)
    if element in failed_tag_list:
        return "zeuz_failed"
    name, expected = next(
        (
            (left.lower(), right)
            for left, middle, right in _rows(data_set)
            if "action" in middle
        ),
        ("", ""),
    )
    actual = element.inner_text()
    ignore_case = any(
        _key(left) == "ignorecase" and right.lower() in CommonUtil.affirmative_words
        for left, _, right in _rows(data_set)
    )
    if ignore_case:
        actual, expected = actual.lower(), expected.lower()
    valid = expected in actual if "partial" in name else expected in actual.splitlines()
    return (
        "passed"
        if valid
        else _fail(f"Expected text {expected!r}; actual text {actual!r}")
    )


def Select_Deselect(data_set):
    element = _element(data_set)
    if element in failed_tag_list:
        return "zeuz_failed"
    name, value = next(
        (
            (left.lower(), right)
            for left, middle, right in _rows(data_set)
            if "action" in middle
        ),
        ("", ""),
    )
    if name == "deselect all":
        element.select_option([])
        return "passed"
    if name.startswith("deselect"):
        if "visible text" in name:
            remove = element.locator("option", has_text=value).first.get_attribute(
                "value"
            )
        elif "index" in name:
            remove = element.locator("option").nth(int(value)).get_attribute("value")
        else:
            remove = value
        selected = element.locator("option:checked").evaluate_all(
            "(options, remove) => options.filter(o => o.value !== remove).map(o => o.value)",
            remove,
        )
        element.select_option(selected)
    elif "visible text" in name:
        element.select_option(label=value)
    elif "value" in name:
        element.select_option(value=value)
    elif "index" in name:
        element.select_option(index=int(value))
    else:
        return _fail("Unknown select action")
    return "passed"


def Handle_Browser_Alert(data_set):
    cached = _state().get("dialog")
    if not cached:
        return _fail("No Playwright dialog was captured")
    value = _action(data_set)
    if value.lower().startswith("get text"):
        name = value.split("=", 1)[-1].strip()
        sr.Set_Shared_Variables(name, cached["text"])
    return "passed"


def open_new_tab(data_set):
    state = _state()
    page = state["context"].new_page()
    url = _action(data_set)
    if url and url.lower() not in ("open new tab", "new tab"):
        page.goto(url)
    _set_active(current_driver_id)
    return "passed"


def _find_page(data_set):
    pages = _state()["context"].pages
    for left, _middle, right in _rows(data_set):
        partial = left.strip().startswith("*")
        key = _key(left).lstrip("*")
        if key in ("tabindex", "windowindex", "index"):
            return pages[int(right)]
        if key in ("tabtitle", "windowtitle", "title"):
            return next(
                (
                    page
                    for page in pages
                    if (
                        right.lower() in page.title().lower()
                        if partial
                        else right.lower() == page.title().lower()
                    )
                ),
                None,
            )
        if key in ("url", "taburl", "windowurl"):
            return next(
                (
                    page
                    for page in pages
                    if (right in page.url if partial else right == page.url)
                ),
                None,
            )
    return pages[-1] if pages else None


def switch_window_or_tab(data_set):
    page = _find_page(data_set)
    if page is None:
        return _fail("Requested tab/window was not found")
    _wire_page(_state(), page)
    page.bring_to_front()
    _set_active(current_driver_id)
    return "passed"


def close_tab(data_set):
    state = _state()
    page = _find_page(data_set)
    if page is None:
        return _fail("Requested tab/window was not found")
    page.close()
    if state["context"].pages:
        _wire_page(state, state["context"].pages[-1])
        _set_active(current_driver_id)
    return "passed"


def switch_iframe(data_set):
    state = _state()
    stack = state.setdefault("frame_stack", [])
    command = _action(data_set).strip().lower()
    frame_rows = [
        row
        for row in _rows(data_set)
        if row[1] in ("iframe parameter", "frame parameter")
    ]
    reset = any(
        right.lower() in ("default", "default content", "main", "top")
        for _, _, right in frame_rows
    )
    if reset:
        state["frame"] = None
        stack.clear()
        frame_rows = [
            row
            for row in frame_rows
            if row[2].lower() not in ("default", "default content", "main", "top")
        ]
    indexed = next(
        (
            right
            for left, _, right in frame_rows
            if left.lower() == "index" and right.lstrip("-").isdigit()
        ),
        None,
    )
    if command in ("default", "default content", "main", "top"):
        state["frame"] = None
        stack.clear()
    elif reset and not frame_rows:
        pass
    elif command in ("parent", "parent frame"):
        state["frame"] = stack.pop() if stack else None
    elif command.lstrip("-").isdigit() or indexed is not None:
        index = int(indexed if indexed is not None else command)
        frames = [
            frame for frame in state["page"].frames if frame != state["page"].main_frame
        ]
        try:
            stack.append(state.get("frame"))
            state["frame"] = frames[index]
        except IndexError:
            return _fail(f"Iframe index {index} was not found")
    else:
        frame_name = next(
            (
                right
                for left, _, right in _rows(data_set)
                if _key(left) in ("framename", "iframename", "name")
            ),
            None,
        )
        frame_url = next(
            (
                right
                for left, _, right in _rows(data_set)
                if _key(left) in ("frameurl", "iframeurl", "url")
            ),
            None,
        )
        if frame_name or frame_url:
            stack.append(state.get("frame"))
            state["frame"] = next(
                (
                    frame
                    for frame in state["page"].frames
                    if (not frame_name or frame.name == frame_name)
                    and (not frame_url or frame_url in frame.url)
                ),
                None,
            )
        else:
            locator_rows = [
                (
                    left,
                    "element parameter"
                    if middle in ("iframe parameter", "frame parameter")
                    else middle,
                    right,
                )
                for left, middle, right in _rows(data_set)
                if not (
                    middle in ("iframe parameter", "frame parameter")
                    and right.lower()
                    in ("default", "default content", "main", "top")
                )
            ]
            element = _element(locator_rows, root=state["page"])
            if element in failed_tag_list:
                return "zeuz_failed"
            stack.append(state.get("frame"))
            content_frame = element.content_frame
            state["frame"] = (
                content_frame() if callable(content_frame) else content_frame
            )
        if state["frame"] is None:
            return _fail("Located element is not an iframe")
    sr.Set_Shared_Variables("common_driver", state.get("frame") or state["page"])
    return "passed"


def upload_file(data_set):
    element = _element(data_set)
    if element in failed_tag_list:
        return "zeuz_failed"
    files = _parse(_action(data_set))
    files = (
        [CommonUtil.path_parser(str(path)) for path in files]
        if isinstance(files, list)
        else CommonUtil.path_parser(str(files))
    )
    paths = files if isinstance(files, list) else [files]
    if any(not Path(path).is_file() for path in paths):
        return _fail("One or more upload files were not found")
    element.set_input_files(files)
    return "passed"


def drag_and_drop(data_set):
    source = [
        (left, middle.replace("source ", "").replace("src ", ""), right)
        for left, middle, right in _rows(data_set)
        if "source " in middle or "src " in middle
    ]
    target = [
        (left, middle.replace("destination ", "").replace("dst ", ""), right)
        for left, middle, right in _rows(data_set)
        if "destination " in middle or "dst " in middle
    ]
    src, dst = _element(source), _element(target)
    if src in failed_tag_list or dst in failed_tag_list:
        return "zeuz_failed"
    src.drag_to(dst)
    return "passed"


def get_element_info(data_set):
    element = _element(data_set)
    if element in failed_tag_list:
        return "zeuz_failed"
    name = _action(data_set)
    box = element.bounding_box() or {}
    value = {
        "size": {"width": box.get("width", 0), "height": box.get("height", 0)},
        "location": {"x": box.get("x", 0), "y": box.get("y", 0)},
    }
    return sr.Set_Shared_Variables(name, value)


def Save_Attribute(data_set):
    variable = attribute = None
    clean = []
    for left, middle, right in _rows(data_set):
        if middle == "save parameter":
            attribute, variable = left.lower(), right
        else:
            clean.append((left, middle, right))
    element = _element(clean)
    if element in failed_tag_list or not variable:
        return "zeuz_failed"
    if attribute == "text":
        value = element.inner_text()
    elif attribute == "tag":
        value = element.evaluate("element => element.tagName.toLowerCase()")
    elif attribute == "checked":
        value = element.is_checked()
    else:
        value = element.get_attribute(attribute)
    return sr.Set_Shared_Variables(variable, value)


def _target_specs(data_set):
    specs = []
    for _left, middle, right in _rows(data_set):
        if "target parameter" not in middle:
            continue
        spec = {}
        for item in right.replace(",\n", ",").split(","):
            if "=" in item:
                key, value = item.split("=", 1)
                spec.setdefault(key.strip(), []).append(value.strip().strip('"'))
        specs.append(spec)
    return specs


def save_attribute_values_in_list(data_set):
    parent = _element(data_set)
    if parent in failed_tag_list:
        return "zeuz_failed"
    result = []
    for spec in _target_specs(data_set):
        rows = [
            (key, "element parameter", value[0])
            for key, value in spec.items()
            if not key.startswith("return")
        ]
        values = []
        for element in _element(rows, all_elements=True, root=parent):
            attribute = spec.get("return", ["text"])[0]
            value = (
                element.inner_text()
                if attribute == "text"
                else element.get_attribute(attribute)
            )
            if all(
                part in (value or "") for part in spec.get("return_contains", [])
            ) and not any(
                part in (value or "")
                for part in spec.get("return_does_not_contain", [])
            ):
                values.append(value)
        result.append(values)
    name = next(
        (
            right
            for left, _, right in _rows(data_set)
            if left.lower() == "save attribute values in list"
        ),
        "",
    )
    return sr.Set_Shared_Variables(name, result[0] if len(result) == 1 else result)


def Extract_Table_Data(data_set):
    table = _element(data_set)
    if table in failed_tag_list:
        return "zeuz_failed"
    values = table.locator("tr").evaluate_all(
        "rows => rows.map(r => [...r.querySelectorAll('th,td')].map(c => c.textContent.trim()))"
    )
    row = next(
        (right for left, _, right in _rows(data_set) if "row" in left.lower()), ""
    )
    column = next(
        (right for left, _, right in _rows(data_set) if "column" in left.lower()), ""
    )
    if row:
        values = [values[int(row)]]
    if column:
        values = [[item[int(column)]] for item in values]
    name = next(
        (
            right
            for left, _, right in _rows(data_set)
            if left.lower() == "extract table data"
        ),
        "",
    )
    return sr.Set_Shared_Variables(name, values)


def save_web_elements_in_list(data_set):
    name = _action(data_set)
    has_parent = any(
        middle
        in (
            "element parameter",
            "parent parameter",
            "child parameter",
            "sibling parameter",
        )
        for _, middle, _ in _rows(data_set)
    )
    root = _element(data_set) if has_parent else get_driver()
    if root in failed_tag_list:
        return "zeuz_failed"
    groups = []
    for spec in _target_specs(data_set):
        rows = [
            (key, "element parameter", values[0])
            for key, values in spec.items()
            if not key.startswith("return")
        ]
        elements = _element(rows, all_elements=True, root=root)
        groups.append(elements)
    value = groups[0] if len(groups) == 1 else groups
    return sr.Set_Shared_Variables(name, value)


def take_screenshot_selenium(data_set):
    filename_format = next(
        (
            right
            for left, _, right in _rows(data_set)
            if "take screenshot web" in left.lower() and "default" not in right.lower()
        ),
        "%Y_%m_%d_%H-%M-%S",
    )
    full_page = any(
        "fullscreen" in left.lower() and right.lower() in CommonUtil.affirmative_words
        for left, _, right in _rows(data_set)
    )
    folder = ConfigModule.get_config_value(
        "sectionOne", "screen_capture_folder", str(Path.cwd())
    )
    Path(folder).mkdir(parents=True, exist_ok=True)
    filename = time.strftime(filename_format) + ".png"
    get_page().screenshot(path=str(Path(folder) / filename), full_page=full_page)
    sr.Set_Shared_Variables("zeuz_screenshot", filename)
    return "passed"


def execute_javascript(data_set):
    script = next(
        (right for left, _, right in _rows(data_set) if "javascript" in left.lower()),
        None,
    )
    variable = next(
        (right for left, _, right in _rows(data_set) if left.lower() == "variable"),
        None,
    )
    if script is None:
        return _fail("Missing JavaScript")
    if any("element parameter" in middle for _, middle, _ in _rows(data_set)):
        element = _element(data_set)
        if element in failed_tag_list:
            return "zeuz_failed"
        body = script.replace("$elem", "element").replace("arguments[0]", "element")
        result = element.evaluate(f"element => {{ {body} }}")
    else:
        stripped = script.strip()
        if stripped.startswith("return "):
            script = f"() => ({stripped[7:].rstrip(';')})"
        elif ";" in stripped and "=>" not in stripped:
            script = f"() => {{ {stripped} }}"
        result = get_page().evaluate(script)
    return sr.Set_Shared_Variables(variable, result) if variable else "passed"


def Scroll(data_set):
    direction = _action(data_set).lower()
    pixels = next(
        (int(right) for left, _, right in _rows(data_set) if left.lower() == "pixels"),
        750,
    )
    x = pixels if direction == "right" else -pixels if direction == "left" else 0
    y = pixels if direction == "down" else -pixels if direction == "up" else 0
    element = (
        _element(data_set)
        if any("element parameter" in middle for _, middle, _ in _rows(data_set))
        else None
    )
    (element or get_page()).evaluate(
        "(target, delta) => (target === document ? window : target).scrollBy(delta.x, delta.y)",
        {"x": x, "y": y},
    ) if element else get_page().evaluate(
        "delta => window.scrollBy(delta.x, delta.y)", {"x": x, "y": y}
    )
    return "passed"


def scroll_to_element(data_set):
    element = _element(data_set)
    if element in failed_tag_list:
        return "zeuz_failed"
    element.scroll_into_view_if_needed()
    return "passed"


def scroll_to_top(data_set):
    get_page().evaluate("window.scrollTo(window.scrollX, 0)")
    return "passed"


def check_uncheck(data_set):
    element = _element(data_set)
    if element in failed_tag_list:
        return "zeuz_failed"
    command = _action(data_set).lower()
    element.uncheck() if "uncheck" in command else element.check()
    return "passed"


def check_uncheck_all(data_set):
    parent = _element(data_set)
    if parent in failed_tag_list:
        return "zeuz_failed"
    targets = [
        (left, "element parameter", right)
        for left, middle, right in _rows(data_set)
        if middle == "target parameter"
    ]
    elements = _element(targets, all_elements=True, root=parent)
    uncheck = "uncheck" in _action(data_set).lower()
    for element in elements:
        element.uncheck() if uncheck else element.check()
    return "passed"


def multiple_check_uncheck(data_set):
    parent = _element(data_set)
    if parent in failed_tag_list:
        return "zeuz_failed"
    for _left, middle, right in _rows(data_set):
        if middle != "target parameter":
            continue
        for attribute, value, command in _parse("[" + right + "]"):
            element = _element([(attribute, "element parameter", value)], root=parent)
            if element not in failed_tag_list:
                element.uncheck() if "uncheck" in command.lower() else element.check()
    return "passed"


def slider_bar(data_set):
    element = _element(data_set)
    if element in failed_tag_list:
        return "zeuz_failed"
    value = int(_action(data_set))
    box = element.bounding_box()
    if not box:
        return "zeuz_failed"
    get_page().mouse.click(
        box["x"] + box["width"] * value / 100, box["y"] + box["height"] / 2
    )
    return "passed"


def resize_window(data_set):
    page = get_page()
    size = page.viewport_size or {"width": 1920, "height": 1080}
    for left, middle, right in _rows(data_set):
        if "element parameter" in middle and left.lower() in ("width", "height"):
            size[left.lower()] = round(
                size[left.lower()] * float(right.rstrip("%")) / 100
            )
    page.set_viewport_size(size)
    return "passed"


def Change_Attribute_Value(data_set):
    element = _element(data_set)
    if element in failed_tag_list:
        return "zeuz_failed"
    attribute, value = next(
        (
            (left, right)
            for left, middle, right in _rows(data_set)
            if "input parameter" in middle
        ),
        (None, None),
    )
    if not attribute:
        return _fail("Missing attribute input parameter")
    element.evaluate(
        "(element, pair) => { element[pair.name] = pair.value; element.setAttribute(pair.name, pair.value); }",
        {"name": attribute, "value": value},
    )
    return "passed"


def capture_network_log(data_set):
    state = _state()
    command = _action(data_set).lower()
    if command == "start":
        state["network"] = []
        state["capturing_network"] = True
    else:
        state["capturing_network"] = False
        variable = next(
            (
                right
                for left, _, right in _rows(data_set)
                if _key(left) in ("save", "variable", "variablename", "saveas")
            ),
            None,
        )
        domains = [
            item.strip()
            for left, _, right in _rows(data_set)
            if _key(left) == "filterdomain"
            for item in right.split(",")
        ]
        methods = [
            item.strip().upper()
            for left, _, right in _rows(data_set)
            if _key(left) == "includerequestmethod"
            for item in right.split(",")
        ]
        statuses = set()
        for left, _, right in _rows(data_set):
            if _key(left) != "includestatuscode":
                continue
            for part in right.split(","):
                bounds = [int(item) for item in part.strip().split("-", 1)]
                statuses.update(range(bounds[0], bounds[-1] + 1))
        include_body = any(
            _key(left) == "includeresponsebody"
            and right.lower() in CommonUtil.affirmative_words
            for left, _, right in _rows(data_set)
        )
        static = (
            ".js",
            ".css",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".ico",
            ".woff",
            ".woff2",
            ".ttf",
            ".map",
        )
        logs = []
        for captured in state["network"]:
            if captured.get("type") == "request" or captured["url"].lower().endswith(
                static
            ):
                continue
            if domains and not any(domain in captured["url"] for domain in domains):
                continue
            if methods and captured["method"].upper() not in methods:
                continue
            if statuses and captured["status"] not in statuses:
                continue
            item = dict(captured)
            response = item.pop("_response", None)
            if include_body:
                try:
                    item["body"] = response.body().decode(errors="replace")
                except Exception:
                    item["body"] = "Unavailable"
            logs.append(item)
        if variable:
            sr.Set_Shared_Variables(variable, logs)
    return "passed"


def if_element_exists(data_set):
    value, variable = (part.strip() for part in _action(data_set).split("=", 1))
    sr.Set_Shared_Variables(
        variable, value if _element(data_set) not in failed_tag_list else "false"
    )
    return "passed"


def copy_image_into_browser(data_set):
    path = next(
        (
            right
            for left, _, right in _rows(data_set)
            if _key(left) in ("imagefile", "filepath", "file")
        ),
        "",
    )
    path = CommonUtil.path_parser(path)
    if not path or not Path(path).is_file():
        return _fail("Image file was not found")
    mime = "image/svg+xml" if str(path).lower().endswith(".svg") else "image/png"
    encoded = base64.b64encode(Path(path).read_bytes()).decode()
    try:
        _state()["context"].grant_permissions(
            ["clipboard-read", "clipboard-write"], origin=get_page().url
        )
    except Exception:
        pass
    get_page().evaluate(
        """async ({data, mime}) => {
        const blob = await (await fetch(`data:${mime};base64,${data}`)).blob();
        await navigator.clipboard.write([new ClipboardItem({[mime]: blob})]);
    }""",
        {"data": encoded, "mime": mime},
    )
    return "passed"


Tear_Down_Playwright = Tear_Down_Selenium


def _action_guard(function):
    @functools.wraps(function)
    def guarded(data_set=()):
        try:
            return function(data_set)
        except Exception:
            return CommonUtil.Exception_Handler(sys.exc_info())

    return guarded


# Keep direct calls consistent with Sequential Actions: action errors are results,
# not exceptions escaping into callers.
for _name in {_declaration["function"] for _declaration in declarations}:
    globals()[_name] = _action_guard(globals()[_name])
