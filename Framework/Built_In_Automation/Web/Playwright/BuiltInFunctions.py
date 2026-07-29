# -*- coding: utf-8 -*-
"""
Playwright Built-In Functions for Zeuz Node

This module provides web automation actions using Playwright as an alternative
to Selenium. All actions follow the same step_data format and parameter patterns
as Selenium actions for seamless migration.

Key Benefits over Selenium:
- Faster execution (WebSocket vs HTTP)
- Built-in auto-wait (no manual WebDriverWait)
- Modern selector support (test-id, role, text)
- Better iframe and shadow DOM handling
- Video recording and tracing support

Usage:
    Change "selenium action" to "playwright action" in test steps.
    All element parameters work identically.

Author: Zeuz/AutomationSolutionz
"""

import asyncio
import hashlib
import json
import shutil
import sys
import os
import inspect
import platform
import tempfile
import time
import base64
from pathlib import Path
from urllib.parse import urlparse
import requests

from playwright.async_api import (
    async_playwright,
    Page,
    Browser,
    BrowserContext,
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError,
)

from Framework.Utilities import CommonUtil, ConfigModule
from Framework.Utilities.decorators import logger
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from Framework.Built_In_Automation.Shared_Resources import LocateElement as PlaywrightLocator
from Framework.Utilities.CommonUtil import failed_tag_list
from Framework.Built_In_Automation.Web.Selenium.utils import (
    ChromeExtensionDownloader,
    ChromeForTesting,
)
from Framework.Built_In_Automation.Web.utils import (
    create_browser_session,
    extract_session_name,
    get_browser_session,
    get_browser_sessions,
    get_debug_port,
    remove_browser_session,
)

def _get_action_timeout(step_data, element_wait=None):
    if element_wait is not None:
        return int(float(element_wait) * 1000)
    for left, mid, right in step_data:
        left_l = str(left).strip().lower()
        mid_l = str(mid).strip().lower()
        if mid_l == "optional parameter" and left_l in ("wait", "timeout"):
            return int(float(str(right).strip()) * 1000)
    default_wait = sr.Get_Shared_Variables("element_wait")
    if default_wait not in failed_tag_list:
        return int(float(default_wait) * 1000)
    return 10000


def _has_chromium_arg(args, arg_names):
    """Return True when Chromium args already include one of the named flags."""

    for arg in args:
        normalized_arg = arg.strip()
        for arg_name in arg_names:
            if normalized_arg == arg_name or normalized_arg.startswith(f"{arg_name}="):
                return True
    return False


def _page_load_wait_until(strategy):
    strategy = str(strategy or "eager").strip().lower()
    try:
        return {
            "normal": "load",
            "eager": "domcontentloaded",
            "none": "commit",
            "load": "load",
            "domcontentloaded": "domcontentloaded",
            "networkidle": "networkidle",
            "commit": "commit",
        }[strategy]
    except KeyError:
        raise ValueError(
            "page load strategy must be normal, eager, none, load, domcontentloaded, networkidle, or commit"
        ) from None


def _write_chrome_preferences(preferences):
    """Write Selenium-style dotted Chrome preferences to a temporary profile."""
    nested_preferences = {}
    for key, value in preferences.items():
        target = nested_preferences
        parts = key.split(".")
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = value

    user_data_dir = Path(tempfile.mkdtemp(prefix="zeuz-playwright-"))
    default_profile = user_data_dir / "Default"
    default_profile.mkdir()
    (default_profile / "Preferences").write_text(json.dumps(nested_preferences))
    return str(user_data_dir)


def _cleanup_chrome_profile(user_data_dir):
    if not user_data_dir:
        return
    profile = Path(user_data_dir)
    if (
        profile.parent == Path(tempfile.gettempdir())
        and profile.name.startswith("zeuz-playwright-")
    ):
        shutil.rmtree(profile, ignore_errors=True)


def _unpack_playwright_extensions(extension_files, encoded_extensions):
    """Cache CRX/base64 extension payloads and return unpacked directories."""
    payloads = [Path(path).read_bytes() for path in extension_files]
    for encoded_extension in encoded_extensions:
        try:
            payloads.append(
                base64.b64decode("".join(encoded_extension.split()), validate=True)
            )
        except Exception:
            raise ValueError("add encoded extension contains invalid base64 data") from None

    if not payloads:
        return []

    downloader = ChromeExtensionDownloader()
    extension_dirs = []
    for payload in payloads:
        cache_dir = (
            downloader.CHROME_EXTENSIONS_DIR
            / "playwright"
            / hashlib.sha256(payload).hexdigest()
        )
        crx_path = cache_dir / "extension.crx"
        unpacked_path = cache_dir / "extension"
        if not (unpacked_path / "manifest.json").exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
            crx_path.write_bytes(payload)
            downloader.extract_extension(crx_path)
        if not (unpacked_path / "manifest.json").exists():
            raise ValueError("Chrome extension does not contain a manifest.json")
        extension_dirs.append(str(unpacked_path))

    return list(dict.fromkeys(extension_dirs))


def _set_active_playwright_session(session_name, session):
    """Update module globals/shared variables for a selected Playwright session."""

    global current_page, current_page_id, context, browser, playwright_instance

    current_page = session.get("playwright_page")
    context = session.get("playwright_context")
    browser = session.get("playwright_browser")
    playwright_instance = session.get("playwright_instance") or playwright_instance
    current_page_id = session_name

    sr.Set_Shared_Variables("playwright_page", current_page)
    sr.Set_Shared_Variables("playwright_context", context)
    sr.Set_Shared_Variables("playwright_browser", browser)
    sr.Set_Shared_Variables("playwright_frame", session.get("playwright_frame"))
    sr.Set_Shared_Variables(
        "playwright_wait_until",
        session.get("playwright_wait_until", "domcontentloaded"),
    )
    sr.Set_Shared_Variables("active_web_driver_type", "playwright")
    if session.get("selenium_driver"):
        sr.Set_Shared_Variables("selenium_driver", session["selenium_driver"])
    CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())


async def _ensure_playwright_session(session_name, existing_session):
    """Activate an existing Playwright session or lazily attach to a Selenium one."""

    global playwright_details

    if existing_session and existing_session.get("playwright_page"):
        _set_active_playwright_session(session_name, existing_session)
        return "passed"

    if not existing_session or not existing_session.get("selenium_driver"):
        return "zeuz_failed"

    port = existing_session.get("remote_debugging_port")
    if not port:
        return "zeuz_failed"

    try:
        from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as SeleniumBuiltInFunctions

        playwright_instance, connected_browser, connected_context, connected_page = await SeleniumBuiltInFunctions.connect_playwright_to_selenium(port=port)
        sessions = get_browser_sessions()
        session = sessions.setdefault(session_name, existing_session)
        session.update({
            "selenium_driver": existing_session.get("selenium_driver"),
            "playwright_page": connected_page,
            "playwright_browser": connected_browser,
            "playwright_context": connected_context,
            "playwright_frame": None,
            "playwright_instance": playwright_instance,
            "remote_debugging_port": port,
        })
        sr.Set_Shared_Variables("browser_sessions", sessions)
        playwright_details[session_name] = {
            "page": connected_page,
            "context": connected_context,
            "browser": connected_browser,
            "playwright": playwright_instance,
            "remote-debugging-port": port,
        }
        _set_active_playwright_session(session_name, session)
        CommonUtil.ExecLog("_ensure_playwright_session", f"Connected Playwright to Selenium session: {session_name}", 1)
        return "passed"
    except Exception as e:
        CommonUtil.ExecLog("_ensure_playwright_session", f"Failed to connect Playwright to Selenium session '{session_name}': {e}", 3)
        return "zeuz_failed"


def _save_current_playwright_frame(frame_locator):
    if current_page_id:
        sessions = get_browser_sessions()
        if current_page_id in sessions:
            sessions[current_page_id]["playwright_frame"] = frame_locator
            sr.Set_Shared_Variables("browser_sessions", sessions)


async def _activate_browser_session_for_action(step_data, function_name=None):
    """Select the requested browser session before running Playwright actions."""

    session_name = extract_session_name(step_data)
    create_or_cleanup_actions = {
        "Open_Browser",
        "Go_To_Link",
        "Tear_Down_Playwright",
    }
    if function_name in create_or_cleanup_actions:
        return "passed"

    if not session_name:
        if current_page is None:
            default_session = get_browser_session("default")
            if default_session and default_session.get("selenium_driver"):
                return await _ensure_playwright_session("default", default_session)
        return "passed"

    existing_session = get_browser_session(session_name)
    result = await _ensure_playwright_session(session_name, existing_session)
    if result in failed_tag_list:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        CommonUtil.ExecLog(sModuleInfo, f"Browser session '{session_name}' not found", 3)
        return "zeuz_failed"

    return "passed"


def connect_selenium_to_playwright(port=9222, driver_path=None):
    """Connect Selenium to Playwright browser via CDP"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = Options()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

        service = Service(executable_path=str(driver_path)) if driver_path else None
        if service:
            CommonUtil.ExecLog(
                "connect_selenium_to_playwright",
                f"Using cached ChromeDriver: {driver_path}",
                1,
            )
        else:
            try:
                response = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=5)
                response.raise_for_status()
                browser_version = (
                    response.json()
                    .get("Browser", "")
                    .split("/", 1)[-1]
                    .strip()
                )
                if browser_version:
                    driver_path = ChromeDriverManager(
                        driver_version=browser_version
                    ).install()
                    service = Service(executable_path=driver_path)
                    CommonUtil.ExecLog(
                        "connect_selenium_to_playwright",
                        f"Using ChromeDriver matching browser version {browser_version}",
                        1,
                    )
            except Exception:
                CommonUtil.ExecLog(
                    "connect_selenium_to_playwright",
                    "Could not resolve matching ChromeDriver for Playwright browser; falling back to Selenium Manager",
                    2,
                )

        if service:
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as SeleniumBuiltInFunctions
        SeleniumBuiltInFunctions.selenium_driver = driver
        
        sr.Set_Shared_Variables("selenium_driver", driver)
        
        CommonUtil.ExecLog("connect_selenium_to_playwright", "Connected Selenium to Playwright", 1)
        return driver
        
    except Exception as e:
        CommonUtil.ExecLog("connect_selenium_to_playwright", f"Failed to connect Selenium to Playwright: {e}", 3)
        return "zeuz_failed"

#########################
#                       #
#    Global Variables   #
#                       #
#########################

MODULE_NAME = inspect.getmodulename(__file__)

temp_config = str(
    Path(os.path.abspath(__file__).split("Framework")[0])
    / "AutomationLog"
    / ConfigModule.get_config_value("Advanced Options", "_file")
)

# Playwright instances
playwright_instance = None
browser: Browser = None
context: BrowserContext = None
current_page: Page = None

# Multi-page/context support
playwright_details = {}  # {"page_id": {"page": Page, "context": Context, "browser": Browser}}
current_page_id = None
network_log_details = {}

# Default settings
default_timeout = 30000  # 30 seconds
default_viewport = {"width": 1920, "height": 1080}


def _compact(value):
    return str(value).replace(" ", "").replace("_", "").replace("-", "").lower()


def _is_action_mid(mid):
    return "action" in str(mid).strip().lower()


def _truthy(value):
    return str(value).strip().lower() in ("true", "yes", "ok", "1", "accept")


def _is_placeholder(value, *placeholders):
    value_l = str(value).strip().lower()
    return not value_l or value_l in placeholders or value_l == "default"


def _has_element_rows(step_data):
    return any(_is_element_parameter_mid(mid) for _, mid, _ in step_data)


def _action_row_value(step_data, *action_names):
    names = {name.strip().lower() for name in action_names}
    for left, mid, right in step_data:
        if _is_action_mid(mid) and (not names or left.strip().lower() in names):
            return str(right)
    return None


def _save_variable_from_action_or_save_parameter(step_data, *action_names):
    save_variable = None
    for left, mid, right in step_data:
        mid_l = str(mid).strip().lower()
        if mid_l == "save parameter":
            save_variable = str(left).strip()
        elif _is_action_mid(mid) and (not action_names or left.strip().lower() in action_names):
            value = str(right).strip()
            if not _is_placeholder(value, left.strip().lower()):
                save_variable = value
    return save_variable


def _screenshot_folder():
    try:
        folder = ConfigModule.get_config_value("sectionOne", "screen_capture_folder", temp_config)
        if folder:
            Path(folder).mkdir(parents=True, exist_ok=True)
            return folder
    except Exception:
        pass
    return os.getcwd()


def _download_folder():
    try:
        folder = sr.Get_Shared_Variables("zeuz_download_folder")
        if folder not in failed_tag_list:
            Path(folder).mkdir(parents=True, exist_ok=True)
            return folder
    except Exception:
        pass
    return os.getcwd()


#########################
#                       #
#   Browser Management  #
#                       #
#########################

async def _handle_playwright_session(step_data):
    """
    Helper function to handle session parameter for Playwright actions.
    
    Args:
        step_data: The step data containing potential session parameter
        
    Returns:
        tuple: (session_name, current_page, current_page_id, context, browser)
        - session_name: The session name found or None
        - current_page: The appropriate page instance
        - current_page_id: The current page ID
        - context: The browser context
        - browser: The browser instance
    """
    global current_page, current_page_id, context, browser
    
    session_name = extract_session_name(step_data)
    
    # If session parameter is provided, switch to that session
    if session_name:
        existing_session = get_browser_session(session_name)
        
        if existing_session and await _ensure_playwright_session(session_name, existing_session) not in failed_tag_list:
            sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
            CommonUtil.ExecLog(sModuleInfo, f"Using existing browser session: {session_name}", 1)
        else:
            sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
            CommonUtil.ExecLog(sModuleInfo, f"Browser session '{session_name}' not found", 3)
            raise ValueError(f"Browser session '{session_name}' not found")
    elif current_page is None:
        default_session = get_browser_session("default")
        if default_session and default_session.get("selenium_driver"):
            await _ensure_playwright_session("default", default_session)
    
    return session_name, current_page, current_page_id, context, browser


@logger
async def Open_Browser(step_data):
    """
    Launch a new browser instance with Playwright.

    Example 1 - Basic:
        Field               Sub Field           Value
        go to link          input parameter     https://example.com
        open browser        playwright action   open browser

    Example 2 - With options:
        Field               Sub Field           Value
        go to link          input parameter     https://example.com
        browser             input parameter     chrome
        headless            optional parameter  false
        resolution          optional parameter  1920,1080
        timeout             optional parameter  60
        add argument        optional parameter  --disable-gpu
        open browser        playwright action   open browser

    Supported browsers: chrome, chromium, chrome-beta
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global playwright_instance, browser, context, current_page
    global current_page_id, playwright_details, default_timeout

    try:
        # Parse parameters
        url = None
        dependency = sr.Get_Shared_Variables("dependency")
        browser_name = "chromium"
        dependency_browser = ""
        if isinstance(dependency, dict) and dependency.get("Browser"):
            dependency_browser = dependency["Browser"].strip().lower()
            browser_name = dependency_browser
        headless = dependency_browser.replace(" ", "") == "chromeheadless"
        headless_explicit = False
        chrome_version = None
        extension_values = []
        encoded_extension_values = []
        chromium_argument_values = []
        experimental_option_values = []
        preference_values = []
        shared_capability_values = []
        debugger_address = None
        page_load_strategy = "eager"
        element_wait = None
        viewport = default_viewport.copy()
        resolution = None
        args = []
        timeout = default_timeout
        slow_mo = 0
        devtools = False
        downloads_path = None
        record_video = False
        video_dir = None
        locale = None
        timezone = None
        geolocation = None
        permissions = []
        color_scheme = None
        page_id = "default"

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "input parameter":
                if left_l in ("go to link", "url", "link"):
                    url = right_v
                elif left_l in ("browser", "browser name"):
                    browser_name = right_v.lower()
                elif _compact(left_l) in ("driverid", "pageid", "drivertag", "session"):
                    page_id = right_v

            elif mid_l == "optional parameter":
                if left_l == "headless":
                    headless_explicit = True
                    headless = right_v.lower() in ("true", "yes", "1")
                elif left_l == "resolution":
                    parts = right_v.replace("x", ",").split(",")
                    resolution = {
                        "width": int(parts[0].strip()),
                        "height": int(parts[1].strip()),
                    }
                    viewport = resolution.copy()
                elif left_l in ("timeout", "wait time to page load", "page load timeout"):
                    timeout = int(float(right_v) * 1000)
                elif left_l in ("add argument", "arg", "argument"):
                    args.append(right_v)
                elif left_l == "slow mo":
                    slow_mo = int(float(right_v))
                elif left_l == "devtools":
                    devtools = right_v.lower() in ("true", "yes", "1")
                elif left_l in ("downloads path", "download folder"):
                    downloads_path = right_v
                elif left_l == "record video":
                    record_video = right_v.lower() in ("true", "yes", "1")
                elif left_l == "video dir":
                    video_dir = right_v
                elif left_l == "locale":
                    locale = right_v
                elif left_l == "timezone":
                    timezone = right_v
                elif left_l == "color scheme":
                    color_scheme = right_v
                elif left_l == "permission":
                    permissions.append(right_v)
                elif _compact(left_l) in ("driverid", "pageid", "drivertag", "session"):
                    page_id = right_v    

            elif mid_l == "shared capability":
                shared_capability_values.append(right_v)

            left_compact = _compact(left_l)
            if left_compact == "chrome:version":
                chrome_version = right_v
            elif mid_l in ("chromium option", "chrome option"):
                if left_compact == "addargument":
                    chromium_argument_values.append(right_v)
                elif left_compact == "addexperimentaloption":
                    experimental_option_values.append(right_v)
                elif left_compact == "addextension":
                    extension_values.append(right_v)
                elif left_compact == "addencodedextension":
                    encoded_extension_values.append(right_v)
                elif left_compact == "setpreference":
                    preference_values.append(right_v)
                elif left_compact == "pageloadstrategy":
                    page_load_strategy = right_v
                elif left_compact == "debuggeraddress":
                    debugger_address = right_v

            if left_compact in (
                "waittimetoappearelement",
                "waitforelement",
                "elementwait",
            ):
                element_wait = float(right_v)

        compact_browser_name = _compact(browser_name)
        if compact_browser_name == "chromeheadless":
            browser_name = "chrome"
            if not headless_explicit:
                headless = True
        elif compact_browser_name in ("chrome", "chromium", "chromebeta"):
            browser_name = "chrome-beta" if compact_browser_name == "chromebeta" else compact_browser_name
        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Playwright only supports Chrome/Chromium; browser '{browser_name}' is not supported",
                3,
            )
            return "zeuz_failed"

        from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as SeleniumBuiltInFunctions

        capabilities = {}
        for value in shared_capability_values:
            parsed = CommonUtil.parse_value_into_object(value)
            if not isinstance(parsed, dict):
                raise ValueError("shared capability must be a dictionary")
            capabilities.update(parsed)

        experimental_options = {}
        for value in experimental_option_values:
            experimental_options.update(
                SeleniumBuiltInFunctions.parse_and_verify_datatype(
                    "addexperimentaloption",
                    value,
                )
            )
        preferences = {}
        for value in preference_values:
            preferences.update(
                SeleniumBuiltInFunctions.parse_and_verify_datatype(
                    "setpreference",
                    value,
                )
            )
        for value in chromium_argument_values:
            args.extend(
                SeleniumBuiltInFunctions.parse_and_verify_datatype(
                    "addargument",
                    value,
                )
            )

        chrome_options = capabilities.get("goog:chromeOptions", {})
        if isinstance(chrome_options, dict):
            args.extend(chrome_options.get("args", []))
            if chrome_options.get("extensions"):
                encoded_extension_values.append(
                    repr(chrome_options["extensions"])
                )
            experimental_options.update(
                {
                    key: value
                    for key, value in chrome_options.items()
                    if key not in ("args", "extensions")
                }
            )
        preferences.update(experimental_options.get("prefs", {}))
        debugger_address = (
            debugger_address
            or experimental_options.get("debuggerAddress")
        )
        page_load_strategy = capabilities.get(
            "pageLoadStrategy",
            page_load_strategy,
        )
        wait_until = _page_load_wait_until(page_load_strategy)

        if (
            not debugger_address
            and chrome_version
            and chrome_version.strip().lower() == "system"
        ):
            CommonUtil.ExecLog(
                sModuleInfo,
                "Playwright requires Chrome for Testing; chrome:version = system is not supported",
                3,
            )
            return "zeuz_failed"

        existing_session = get_browser_session(page_id)
        if existing_session:
            result = await _ensure_playwright_session(page_id, existing_session)
            if result not in failed_tag_list:
                if url:
                    await current_page.goto(url, wait_until=wait_until)
                if element_wait is not None:
                    sr.Set_Shared_Variables("element_wait", element_wait)
                CommonUtil.ExecLog(sModuleInfo, f"Using existing browser session: {page_id}", 1)
                return "passed"

        chrome_channel = "Beta" if browser_name == "chrome-beta" else None
        chrome_bin = driver_bin = None
        if not debugger_address:
            chrome_bin, driver_bin = await asyncio.to_thread(
                lambda: ChromeForTesting().setup_chrome_for_testing(
                    chrome_version,
                    chrome_channel,
                )
            )
        if not debugger_address and (not chrome_bin or not driver_bin):
            CommonUtil.ExecLog(sModuleInfo, "Failed to setup Chrome for Testing browser and driver", 3)
            return "zeuz_failed"

        # Launch Playwright
        CommonUtil.ExecLog(sModuleInfo, f"Launching Playwright with {browser_name} browser", 1)
        playwright_instance = await async_playwright().start()

        # Browser launch options
        launch_options = {
            "headless": headless,
            "slow_mo": slow_mo,
        }
        if chrome_bin:
            launch_options["executable_path"] = str(chrome_bin)
        
        # Add remote debugging port for CDP connection with unique port per session
        if debugger_address:
            debugger_endpoint = (
                debugger_address
                if "://" in debugger_address
                else f"http://{debugger_address}"
            )
            unique_port = urlparse(debugger_endpoint).port
        else:
            debugger_endpoint = None
            unique_port = get_debug_port(page_id)

        extension_files = []
        encoded_extensions = []
        if not debugger_address:
            resolved_chrome_version = next(
                (
                    parent.name
                    for parent in Path(chrome_bin).parents
                    if parent.parent.name == "versions"
                ),
                chrome_version,
            )
            for value in extension_values:
                extension_files.extend(
                    SeleniumBuiltInFunctions.parse_and_verify_datatype(
                        "addextension",
                        value,
                        resolved_chrome_version,
                    )
                )
            for value in encoded_extension_values:
                encoded_extensions.extend(
                    SeleniumBuiltInFunctions.parse_and_verify_datatype(
                        "addencodedextension",
                        value,
                    )
                )
        extension_dirs = _unpack_playwright_extensions(
            extension_files,
            encoded_extensions,
        )

        selenium_browser_name = "chromeheadless" if headless else "chrome"
        zeuz_extension_args = []
        if not debugger_address:
            zeuz_extension_args = (
                SeleniumBuiltInFunctions.get_zeuz_ai_extension_arguments(
                    selenium_browser_name
                )
            )
        extension_args = []
        for argument in zeuz_extension_args:
            if argument.startswith("--load-extension="):
                extension_dirs.extend(argument.split("=", 1)[1].split(","))
            elif not argument.startswith("--disable-extensions-except="):
                extension_args.append(argument)
        extension_dirs = list(dict.fromkeys(extension_dirs))
        if extension_dirs:
            extension_paths = ",".join(extension_dirs)
            if not any(
                argument.startswith(
                    "--disable-features=DisableLoadExtensionCommandLineSwitch"
                )
                for argument in extension_args
            ):
                extension_args.append(
                    "--disable-features=DisableLoadExtensionCommandLineSwitch"
                )
            extension_args.extend(
                (
                    f"--disable-extensions-except={extension_paths}",
                    f"--load-extension={extension_paths}",
                )
            )

        all_args = []
        if not debugger_address:
            all_args = (
                list(SeleniumBuiltInFunctions.DEFAULT_CHROMIUM_ARGUMENTS)
                + args
                + extension_args
                + [f"--remote-debugging-port={unique_port}"]
            )
            if resolution and not _has_chromium_arg(all_args, ("--window-size",)):
                all_args.append(
                    f"--window-size={resolution['width']},{resolution['height']}"
                )
            elif (
                not headless
                and not _has_chromium_arg(
                    all_args,
                    ("--window-size", "--start-maximized", "--kiosk"),
                )
            ):
                all_args.append("--start-maximized")
            if devtools:
                all_args.append("--auto-open-devtools-for-tabs")
            CommonUtil.ExecLog(sModuleInfo, f"Using remote debugging port {unique_port} for session '{page_id}'", 1)
        if all_args:
            launch_options["args"] = all_args
        excluded_switches = experimental_options.get("excludeSwitches", [])
        if excluded_switches:
            launch_options["ignore_default_args"] = [
                switch if switch.startswith("--") else f"--{switch}"
                for switch in excluded_switches
            ]
        proxy = capabilities.get("proxy")
        if isinstance(proxy, dict):
            proxy_server = proxy.get("server") or proxy.get("sslProxy") or proxy.get("httpProxy")
            if proxy_server:
                if "://" not in proxy_server:
                    proxy_server = f"http://{proxy_server}"
                launch_options["proxy"] = {"server": proxy_server}
                no_proxy = proxy.get("noProxy")
                if no_proxy:
                    launch_options["proxy"]["bypass"] = (
                        ",".join(no_proxy) if isinstance(no_proxy, list) else str(no_proxy)
                    )
        downloads_path = downloads_path or preferences.get("download.default_directory")
        if downloads_path:
            launch_options["downloads_path"] = downloads_path

        # Context options. Headed Chromium sessions use the real browser window
        # size so attached Selenium code observes Selenium-like layout behavior.
        if not headless:
            context_options = {"no_viewport": True, "accept_downloads": True}
        else:
            context_options = {"viewport": viewport, "accept_downloads": True}
        if record_video:
            context_options["record_video_dir"] = video_dir or "videos/"
        if locale:
            context_options["locale"] = locale
        if timezone:
            context_options["timezone_id"] = timezone
        if geolocation:
            context_options["geolocation"] = geolocation
        if permissions:
            context_options["permissions"] = permissions
        if color_scheme:
            context_options["color_scheme"] = color_scheme
        if capabilities.get("acceptInsecureCerts") is not None:
            context_options["ignore_https_errors"] = bool(
                capabilities["acceptInsecureCerts"]
            )

        mobile_emulation = experimental_options.get("mobileEmulation")
        if isinstance(mobile_emulation, dict):
            device_name = mobile_emulation.get("deviceName")
            if device_name:
                device = playwright_instance.devices.get(device_name)
                if not device:
                    raise ValueError(f"Unknown Playwright device: {device_name}")
                context_options.pop("no_viewport", None)
                context_options.update(
                    {
                        key: value
                        for key, value in device.items()
                        if key != "default_browser_type"
                    }
                )
            device_metrics = mobile_emulation.get("deviceMetrics", {})
            if device_metrics:
                context_options.pop("no_viewport", None)
                context_options["viewport"] = {
                    "width": device_metrics["width"],
                    "height": device_metrics["height"],
                }
                context_options["device_scale_factor"] = device_metrics.get(
                    "pixelRatio",
                    1,
                )
                context_options["is_mobile"] = device_metrics.get("mobile", True)
                context_options["has_touch"] = device_metrics.get("touch", True)
            if mobile_emulation.get("userAgent"):
                context_options["user_agent"] = mobile_emulation["userAgent"]

        extension_enabled = any(
            argument.startswith("--load-extension=") for argument in all_args
        )
        user_data_dir = (
            _write_chrome_preferences(preferences)
            if preferences and not debugger_address
            else None
        )
        if debugger_address:
            browser = await playwright_instance.chromium.connect_over_cdp(
                debugger_endpoint
            )
            if not browser.contexts:
                raise ValueError(
                    f"No browser context found at debugger address {debugger_address}"
                )
            context = browser.contexts[0]
        elif extension_enabled or user_data_dir:
            context = await playwright_instance.chromium.launch_persistent_context(
                user_data_dir or "",
                **launch_options,
                **context_options,
            )
            browser = context.browser
        else:
            browser = await playwright_instance.chromium.launch(**launch_options)
            context = await browser.new_context(**context_options)

        context.set_default_timeout(timeout)
        current_page = context.pages[0] if context.pages else await context.new_page()
        current_page_id = page_id

        # Store in details
        playwright_details[page_id] = {
            "page": current_page,
            "context": context,
            "browser": browser,
            "playwright": playwright_instance,
            "remote-debugging-port": unique_port,
            "driver-path": str(driver_bin) if driver_bin else None,
            "user-data-dir": user_data_dir,
        }

        # Navigate if URL provided
        if url:
            await current_page.goto(url, wait_until=wait_until)
            CommonUtil.ExecLog(sModuleInfo, f"Navigated to: {url}", 1)

        # Save to shared variables for compatibility
        sr.Set_Shared_Variables("playwright_page", current_page)
        sr.Set_Shared_Variables("playwright_context", context)
        sr.Set_Shared_Variables("playwright_browser", browser)
        sr.Set_Shared_Variables(
            "element_wait",
            element_wait if element_wait is not None else timeout / 1000,
        )
        sr.Set_Shared_Variables("playwright_wait_until", wait_until)
        sr.Set_Shared_Variables("active_web_driver_type", "playwright")
        
        # Set screenshot variables for CommonUtil.TakeScreenShot()
        CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())

        # Create browser session
        session = create_browser_session(
            session_name=page_id,
            selenium_driver=None,
            playwright_page=current_page,
            playwright_browser=browser,
            playwright_context=context,
            playwright_frame=None,
            playwright_instance=playwright_instance,
            remote_debugging_port=unique_port,
        )
        session["selenium_cdp_supported"] = True
        session["driver_path"] = str(driver_bin) if driver_bin else None
        session["playwright_wait_until"] = wait_until
        session["user_data_dir"] = user_data_dir
        sr.Set_Shared_Variables("browser_sessions", get_browser_sessions())
        CommonUtil.ExecLog(sModuleInfo, f"Created browser session: {page_id}", 5)

        CommonUtil.ExecLog(sModuleInfo, f"Browser opened successfully (page_id: {page_id})", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def Open_Electron_App(step_data):
    """
    Launch an Electron desktop app via Playwright's Electron API.

    Example - Basic (per-OS binary paths, like Selenium):
        Field               Sub Field           Value
        windows             input parameter     C:\\Path\\To\\MyApp.exe
        mac                 input parameter     /Applications/MyApp.app/Contents/MacOS/MyApp
        linux               input parameter     /opt/myapp/myapp
        open electron app   playwright action   open electron app

    Example - With optional parameters:
        Field               Sub Field           Value
        mac                 input parameter     /Applications/MyApp.app/Contents/MacOS/MyApp
        session             optional parameter  electron_1
        add argument        optional parameter  --no-sandbox
        cwd                 optional parameter  /tmp/working_dir
        timeout             optional parameter  30
        open electron app   playwright action   open electron app

    Notes:
        - Only the path matching the current OS is used; other rows are ignored.
        - The first Electron BrowserWindow becomes the active page, so subsequent
          element / click / text actions work the same as in a normal browser session.
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global playwright_instance, browser, context, current_page
    global current_page_id, playwright_details

    try:
        desktop_app_path = ""
        driver_id = ""
        args = []
        cwd = None
        env_vars = {}
        timeout = None
        record_video = False
        video_dir = None

        for left, mid, right in step_data:
            left_compact = left.replace(" ", "").replace("_", "").replace("-", "").lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if "windows" in left_compact and platform.system() == "Windows":
                desktop_app_path = right_v
            elif "mac" in left_compact and platform.system() == "Darwin":
                desktop_app_path = right_v
            elif "linux" in left_compact and platform.system() == "Linux":
                desktop_app_path = right_v
            elif left_compact == "driverid":
                driver_id = right_v
            elif left_compact == "session" and mid_l == "optional parameter":
                driver_id = right_v
            elif mid_l == "optional parameter":
                if left_compact in ("addargument", "arg", "argument"):
                    args.append(right_v)
                elif left_compact == "cwd":
                    cwd = right_v
                elif left_compact == "env":
                    # Format: KEY=VALUE
                    if "=" in right_v:
                        k, v = right_v.split("=", 1)
                        env_vars[k.strip()] = v.strip()
                elif left_compact == "timeout":
                    try:
                        timeout = int(float(right_v) * 1000)
                    except ValueError:
                        pass
                elif left_compact == "recordvideo":
                    record_video = right_v.lower() in ("true", "yes", "1")
                elif left_compact == "videodir":
                    video_dir = right_v

        if not desktop_app_path:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"You did not provide an Electron app path for {platform.system()} OS",
                3,
            )
            return "zeuz_failed"

        if not driver_id:
            driver_id = "default"

        desktop_app_path = CommonUtil.path_parser(desktop_app_path)

        # Reserve a debug port for the session even though Playwright drives Electron via CDP automatically.
        electron_port = get_debug_port(driver_id or "electron", start=9230, stop=9320)

        launch_options = {"executable_path": desktop_app_path}
        if args:
            launch_options["args"] = args
        if cwd:
            launch_options["cwd"] = cwd
        if env_vars:
            launch_options["env"] = env_vars
        if timeout:
            launch_options["timeout"] = timeout
        if record_video:
            launch_options["record_video_dir"] = video_dir or "videos/"

        playwright_instance = await async_playwright().start()
        try:
            electron_app = await playwright_instance._electron.launch(**launch_options)
        except Exception:
            return CommonUtil.Exception_Handler(sys.exc_info())

        try:
            current_page = await electron_app.first_window()
        except Exception:
            # Some Electron apps create no visible BrowserWindow at startup.
            current_page = None

        # In Electron there is no BrowserContext we own - bind the app object in its place so
        # downstream session-aware code keeps working.
        context = electron_app.context if hasattr(electron_app, "context") else None
        browser = electron_app  # `browser` slot holds the launched app for teardown.
        current_page_id = driver_id

        playwright_details[driver_id] = {
            "page": current_page,
            "context": context,
            "browser": electron_app,
            "playwright": playwright_instance,
            "remote-debugging-port": electron_port,
        }

        sr.Set_Shared_Variables("playwright_page", current_page)
        sr.Set_Shared_Variables("playwright_context", context)
        sr.Set_Shared_Variables("playwright_browser", electron_app)
        sr.Set_Shared_Variables("active_web_driver_type", "playwright")
        if timeout:
            sr.Set_Shared_Variables("element_wait", timeout / 1000)
        CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())

        create_browser_session(
            session_name=driver_id,
            playwright_page=current_page,
            playwright_browser=electron_app,
            playwright_context=context,
            playwright_frame=None,
            playwright_instance=playwright_instance,
            remote_debugging_port=electron_port,
        )

        CommonUtil.ExecLog(sModuleInfo, "Started Electron App", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def Go_To_Link(step_data):
    """
    Navigate to a URL (and open browser if not already open).

    Example 1 - Basic:
        Field                       Sub Field           Value
        go to link                  input parameter     https://example.com
        go to link                  playwright action   go to link

    Example 2 - Selenium-compatible options:
        Field                       Sub Field           Value
        go to link                  input parameter     https://example.com
        wait time to appear element optional parameter  20
        wait time to page load      optional parameter  60
        resolution                  optional parameter  1920,1080
        wait until                  optional parameter  networkidle
        go to link                  playwright action   go to link

    Options:
        - wait until (load | domcontentloaded | networkidle | commit)
        - timeout / wait time to page load: page load timeout in seconds
        - wait for element / wait time to appear element: element wait timeout
          (seconds) saved to the "element_wait" shared variable so subsequent
          element lookups use it
        - resolution: WIDTHxHEIGHT or WIDTH,HEIGHT (applied to the current page)
        - session: reuse or create a named browser session
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        # Parse session parameter first
        session_name = None
        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "optional parameter" and _compact(left_l) in ("session", "driverid", "driver", "drivertag", "pageid"):
                session_name = right_v
                break

        # Check if session exists and use it
        if session_name:
            existing_session = get_browser_session(session_name)
            if existing_session and await _ensure_playwright_session(session_name, existing_session) not in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, f"Using existing browser session: {session_name}", 1)
            else:
                # Session doesn't exist, open new browser with session name
                CommonUtil.ExecLog(sModuleInfo, f"Session '{session_name}' not found. Opening new browser.", 2)

                # Add session parameter to step_data for Open_Browser
                step_data_with_session = step_data.copy()
                if not any(left.strip().lower() == "session" and mid.strip().lower() == "optional parameter" for left, mid, right in step_data_with_session):
                    step_data_with_session.append(("session", "optional parameter", session_name))

                result = await Open_Browser(step_data_with_session)
                if result == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Failed to open browser for new session", 3)
                    return "zeuz_failed"

        elif current_page is None:
            default_session = get_browser_session("default")
            if default_session and default_session.get("selenium_driver"):
                result = await _ensure_playwright_session("default", default_session)
                if result in failed_tag_list:
                    return result
            else:
                # No session specified and no browser open
                CommonUtil.ExecLog(sModuleInfo, "No browser open. Opening browser with default settings.", 2)
                result = await Open_Browser(step_data)
                if result == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Failed to open browser automatically", 3)
                    return "zeuz_failed"

        url = None
        wait_until = sr.Get_Shared_Variables("playwright_wait_until")
        if wait_until in failed_tag_list:
            wait_until = "domcontentloaded"
        timeout = None
        element_wait_sec = None
        window_size_x = None
        window_size_y = None

        for left, mid, right in step_data:
            left_raw = left.strip()
            left_l = left_raw.lower()
            left_compact = left_l.replace(" ", "").replace("_", "").replace("-", "")
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if left_l in ("go to link", "url", "link"):
                url = right_v
            elif mid_l == "optional parameter":
                if _compact(left_l) in ("session", "driverid", "driver", "drivertag", "pageid"):
                    continue
                if left_l in ("wait until", "wait_until", "waituntil"):
                    wait_until = right_v.lower()
                elif left_compact in ("timeout", "waittimetopageload", "pageloadtimeout"):
                    try:
                        timeout = int(float(right_v) * 1000)
                    except ValueError:
                        pass
                elif left_compact in ("waittimetoappearelement", "waitforelement", "elementwait"):
                    try:
                        element_wait_sec = float(right_v)
                    except ValueError:
                        pass
                elif left_l == "resolution":
                    try:
                        parts = right_v.replace("x", ",").split(",")
                        window_size_x = int(parts[0].strip())
                        window_size_y = int(parts[1].strip())
                    except (ValueError, IndexError):
                        pass
            if (
                mid_l in ("chromium option", "chrome option")
                and left_compact == "pageloadstrategy"
            ):
                wait_until = _page_load_wait_until(right_v)

        if not url:
            CommonUtil.ExecLog(sModuleInfo, "No URL provided", 3)
            return "zeuz_failed"

        if element_wait_sec is not None:
            sr.Set_Shared_Variables("element_wait", element_wait_sec)

        if timeout:
            try:
                current_page.set_default_navigation_timeout(timeout)
                current_page.set_default_timeout(timeout)
            except Exception:
                pass

        if window_size_x and window_size_y:
            try:
                await current_page.set_viewport_size({"width": window_size_x, "height": window_size_y})
            except Exception:
                pass

        goto_options = {"wait_until": wait_until}
        if timeout:
            goto_options["timeout"] = timeout

        try:
            await current_page.goto(url, **goto_options)
        except PlaywrightTimeoutError:
            CommonUtil.ExecLog(sModuleInfo, "Maximum page load time reached. Loading and proceeding", 2)

        # Reset frame context when navigating to a new URL
        sr.Set_Shared_Variables("playwright_frame", None)
        _save_current_playwright_frame(None)

        CommonUtil.ExecLog(sModuleInfo, f"Successfully opened your link: {url}", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "failed to open your link")


@logger
async def Go_To_Link_V2(step_data):
    """Selenium-compatible v2 navigation wrapper."""

    translated = []
    for left, mid, right in step_data:
        left_l = left.strip().lower()
        if left_l == "go to link v2":
            translated.append(("go to link", mid, right))
        elif left_l == "driver tag":
            translated.append(("session", "optional parameter", right))
        elif left_l == "page load timeout":
            translated.append(("wait time to page load", "optional parameter", right))
        elif left_l == "wait for element":
            translated.append(("wait time to appear element", "optional parameter", right))
        elif left_l == "page load strategy":
            translated.append(("wait until", "optional parameter", right))
        else:
            translated.append((left, mid, right))
    return await Go_To_Link(translated)


@logger
async def Tear_Down_Playwright(step_data=None):
    """
    Close browser and clean up Playwright resources.

    Example:
        Field               Sub Field           Value
        tear down           playwright action   tear down
        
    Example with session:
        Field               Sub Field           Value
        session             optional parameter  my_session
        tear down           playwright action   tear down
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global playwright_instance, browser, context, current_page
    global playwright_details, current_page_id

    try:
        # Parse session parameter
        session_name = None
        if step_data:
            for left, mid, right in step_data:
                left_l = left.strip().lower()
                mid_l = mid.strip().lower()
                right_v = right.strip()
                
                if mid_l == "optional parameter" and _compact(left_l) in ("session", "driverid", "driver", "drivertag", "pageid"):
                    session_name = right_v
                    break
        
        # Handle session-specific teardown
        if session_name:
            existing_session = get_browser_session(session_name)
            
            if existing_session and existing_session.get("playwright_page"):
                try:
                    # Close the specific session's page and context
                    session_page = existing_session["playwright_page"]
                    session_context = existing_session["playwright_context"]
                    session_browser = existing_session["playwright_browser"]
                    session_playwright = existing_session.get("playwright_instance")
                    session_selenium = existing_session.get("selenium_driver")
                    
                    if session_page:
                        await session_page.close()
                    if session_context:
                        await session_context.close()
                    if session_browser:
                        await session_browser.close()
                    if session_playwright:
                        await session_playwright.stop()
                    if session_selenium and session_selenium != "zeuz_failed":
                        try:
                            session_selenium.quit()
                        except Exception:
                            pass
                    _cleanup_chrome_profile(existing_session.get("user_data_dir"))
                    
                    CommonUtil.ExecLog(sModuleInfo, f"Teared down session '{session_name}'", 1)
                except Exception:
                    errMsg = f"Unable to tear down session '{session_name}'. may already been killed"
                    CommonUtil.ExecLog(sModuleInfo, errMsg, 2)
                
                remove_browser_session(session_name)
                
                # Remove from playwright_details if present
                if session_name in playwright_details:
                    del playwright_details[session_name]
                
                # If this was the current session, clear globals
                if current_page_id == session_name:
                    current_page = None
                    context = None
                    browser = None
                    current_page_id = None
                    
                    # Try to switch to another available session
                    if playwright_details:
                        for page_id, details in playwright_details.items():
                            current_page = details["page"]
                            context = details["context"]
                            browser = details["browser"]
                            current_page_id = page_id
                            
                            # Update shared variables
                            sr.Set_Shared_Variables("playwright_page", current_page)
                            sr.Set_Shared_Variables("playwright_context", context)
                            sr.Set_Shared_Variables("playwright_browser", browser)
                            
                            CommonUtil.ExecLog(sModuleInfo, f"Switched to session '{page_id}'", 1)
                            break
            else:
                CommonUtil.ExecLog(sModuleInfo, f"Session '{session_name}' not found. Nothing to tear down.", 2)
            return "passed"
        
        # Handle full teardown (backwards compatibility)
        else:
            for session in get_browser_sessions().values():
                if not (isinstance(session, dict) and session.get("playwright_page")):
                    continue
                try:
                    if session.get("selenium_driver") and session.get("selenium_driver") != "zeuz_failed":
                        session["selenium_driver"].quit()
                except Exception:
                    pass

            # Close all tracked pages/contexts
            for page_id, details in list(playwright_details.items()):
                try:
                    if details.get("page"):
                        await details["page"].close()
                    if details.get("context"):
                        await details["context"].close()
                    if details.get("browser"):
                        await details["browser"].close()
                    if details.get("playwright"):
                        await details["playwright"].stop()
                    _cleanup_chrome_profile(details.get("user-data-dir"))
                except Exception:
                    pass

        # Close main instances
            try:
                if current_page and current_page not in [d.get("page") for d in playwright_details.values()]:
                    await current_page.close()
            except Exception:
                pass

            try:
                if context:
                    await context.close()
            except Exception:
                pass

            try:
                if browser:
                    await browser.close()
            except Exception:
                pass

            try:
                if playwright_instance:
                    await playwright_instance.stop()
            except Exception:
                pass

            # Reset all globals
            current_page = None
            context = None
            browser = None
            playwright_instance = None
            playwright_details = {}
            current_page_id = None
            
            # Clear Playwright-backed browser sessions without discarding Selenium-only sessions.
            sessions = get_browser_sessions()
            sessions = {
                name: session
                for name, session in sessions.items()
                if not (isinstance(session, dict) and session.get("playwright_page"))
            }
            sr.Set_Shared_Variables("browser_sessions", sessions)

            CommonUtil.ExecLog(sModuleInfo, "Browser closed successfully", 1)
            return "passed"

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def Switch_Browser(step_data):
    """
    Switch between multiple browser instances/pages.

    Example:
        Field               Sub Field           Value
        driver id           input parameter     my_page_id
        switch browser      playwright action   switch browser
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page, current_page_id, context, browser

    try:
        target_id = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l in ("input parameter", "optional parameter"):
                if _compact(left_l) in ("driverid", "pageid", "drivertag", "session"):
                    target_id = right_v

        if not target_id:
            target_id = "default"

        existing_session = get_browser_session(target_id)
        if existing_session and existing_session.get("playwright_page"):
            _set_active_playwright_session(target_id, existing_session)
            if current_page:
                await current_page.bring_to_front()
            CommonUtil.ExecLog(sModuleInfo, f"Switched to page: {target_id}", 1)
            return "passed"

        if target_id not in playwright_details:
            CommonUtil.ExecLog(sModuleInfo, f"Page ID '{target_id}' not found", 3)
            return "zeuz_failed"

        details = playwright_details[target_id]
        current_page = details["page"]
        context = details["context"]
        browser = details["browser"]
        current_page_id = target_id

        await current_page.bring_to_front()

        sr.Set_Shared_Variables("playwright_page", current_page)
        sr.Set_Shared_Variables("playwright_context", context)
        sr.Set_Shared_Variables("playwright_browser", browser)
        
        # Set screenshot variables for CommonUtil.TakeScreenShot()
        CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())

        CommonUtil.ExecLog(sModuleInfo, f"Switched to page: {target_id}", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Click Actions      #
#                       #
#########################

@logger
async def Click_Element(step_data, retry=0):
    """
    Click an element.

    Example 1 - Basic:
        Field               Sub Field           Value
        id                  element parameter   submit-btn
        click               playwright action   click

    Example 2 - With JS click (forces click via JS .click()):
        Field               Sub Field           Value
        id                  element parameter   submit-btn
        use js              optional parameter  true
        click               playwright action   click

    Example 3 - Click at offset (Selenium-compatible: percent from element center):
        Field               Sub Field           Value
        id                  element parameter   submit-btn
        offset              optional parameter  20,30
        click               playwright action   click

    Example 4 - Double click:
        Field               Sub Field           Value
        id                  element parameter   item
        double click        playwright action   double click

    Example 5 - Right click:
        Field               Sub Field           Value
        id                  element parameter   item
        right click         playwright action   right click
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        # Handle session parameter
        session_name, current_page, current_page_id, context, browser = await _handle_playwright_session(step_data)
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        # Parse options
        use_js = False
        offset_value = ""
        double_click = False
        right_click = False
        click_count = 1
        modifiers = []
        delay = None
        timeout = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            # Skip session parameter - already handled above
            if mid_l == "optional parameter" and left_l == "session":
                continue

            if mid_l == "optional parameter":
                if left_l == "use js":
                    use_js = right_v.lower() in ("true", "yes", "1")
                elif left_l == "offset":
                    offset_value = right_v
                elif left_l == "click count":
                    click_count = int(right_v)
                elif left_l == "modifier":
                    modifiers.append(right_v)
                elif left_l == "delay":
                    delay = int(float(right_v) * 1000)
                elif left_l == "timeout":
                    timeout = int(float(right_v) * 1000)

            elif "action" in mid_l:
                if "double" in left_l:
                    double_click = True
                elif "right" in left_l:
                    right_click = True

        action_timeout = timeout if timeout is not None else _get_action_timeout(step_data)

        # Get element
        locator = await PlaywrightLocator.Get_Element(
            step_data,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
            return "zeuz_failed"

        # Click using offset (Selenium-compatible: percentage of half element size from center)
        if offset_value:
            try:
                box = await locator.bounding_box(timeout=action_timeout)
                if not box:
                    CommonUtil.ExecLog(sModuleInfo, "Cannot determine element bounding box for offset click", 3)
                    return "zeuz_failed"
                parts = offset_value.replace(" ", "").split(",")
                pct_x = float(parts[0])
                pct_y = float(parts[1])
                # Selenium-style: percent of half-size from center, anchored at top-left of element
                offset_x = (box["width"] / 2.0) + (box["width"] / 2.0) * (pct_x / 100.0)
                offset_y = (box["height"] / 2.0) + (box["height"] / 2.0) * (pct_y / 100.0)
                click_options = {"position": {"x": offset_x, "y": offset_y}}
                if modifiers:
                    click_options["modifiers"] = modifiers
                if delay:
                    click_options["delay"] = delay
                if action_timeout is not None:
                    click_options["timeout"] = action_timeout
                if right_click:
                    click_options["button"] = "right"
                if double_click:
                    await locator.dblclick(**click_options)
                else:
                    await locator.click(**click_options)
                CommonUtil.ExecLog(sModuleInfo, "Click on location successful", 1)
                return "passed"
            except Exception:
                return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error clicking location")

        # Build click options
        click_options = {}
        if modifiers:
            click_options["modifiers"] = modifiers
        if delay:
            click_options["delay"] = delay
        if action_timeout is not None:
            click_options["timeout"] = action_timeout
        if click_count > 1:
            click_options["click_count"] = click_count

        # Perform click
        try:
            if double_click:
                await locator.hover(timeout=action_timeout)
                await locator.dblclick(**{k: v for k, v in click_options.items() if k != "click_count"})
                CommonUtil.ExecLog(sModuleInfo, "Double click performed", 1)
            elif right_click:
                click_options["button"] = "right"
                await locator.click(**click_options)
                CommonUtil.ExecLog(sModuleInfo, "Right click performed", 1)
            elif use_js:
                await locator.evaluate("el => el.click()", timeout=action_timeout)
                CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element via JS", 1)
            else:
                await locator.click(**click_options)
                CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1)
            return "passed"
        except PlaywrightTimeoutError:
            # Click intercepted or element not actionable - fall back to JS click (matches Selenium behavior)
            try:
                await locator.evaluate("el => el.click()", timeout=action_timeout)
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Your element is overlapped with another sibling element. Clicked the element successfully by executing JavaScript",
                    2,
                )
                return "passed"
            except Exception:
                return CommonUtil.Exception_Handler(sys.exc_info())
        except PlaywrightError as e:
            err_msg = str(e).lower()
            # Stale element: retry up to 5 times with 1s delay
            if ("stale" in err_msg or "detached" in err_msg) and retry < 5:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Javascript of the element is not fully loaded. Trying again after 1 second delay",
                    2,
                )
                await asyncio.sleep(1)
                return await Click_Element(step_data, retry + 1)
            # Try JS click fallback
            try:
                await locator.evaluate("el => el.click()", timeout=action_timeout)
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Click failed natively; clicked successfully via JavaScript",
                    2,
                )
                return "passed"
            except Exception:
                return CommonUtil.Exception_Handler(sys.exc_info())

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def Double_Click_Element(step_data):
    """
    Double-click an element.

    Example:
        Field               Sub Field           Value
        id                  element parameter   item
        double click        playwright action   double click
    """
    # Reuse Click_Element with double click flag
    modified_step_data = list(step_data)
    # Ensure the action indicates double click
    for i, (left, mid, right) in enumerate(modified_step_data):
        if "action" in mid.strip().lower():
            modified_step_data[i] = ("double click", mid, right)
            break

    return await Click_Element(modified_step_data)


@logger
async def Right_Click_Element(step_data):
    """
    Right-click (context click) an element.

    Example:
        Field               Sub Field           Value
        id                  element parameter   item
        right click         playwright action   right click
    """
    modified_step_data = list(step_data)
    for i, (left, mid, right) in enumerate(modified_step_data):
        if "action" in mid.strip().lower():
            modified_step_data[i] = ("right click", mid, right)
            break

    return await Click_Element(modified_step_data)


@logger
async def Hover_Over_Element(step_data):
    """
    Hover over an element.

    Example:
        Field               Sub Field           Value
        id                  element parameter   menu-item
        hover               playwright action   hover
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        use_js = False
        offset = None
        timeout = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "optional parameter":
                if left_l == "use js":
                    use_js = right_v.lower() in ("true", "yes", "1")
                elif left_l == "offset":
                    parts = right_v.split(",")
                    offset = {"x": float(parts[0].strip()), "y": float(parts[1].strip())}
                elif left_l == "timeout":
                    timeout = int(float(right_v) * 1000)

        action_timeout = timeout if timeout is not None else _get_action_timeout(step_data)

        locator = await PlaywrightLocator.Get_Element(
            step_data,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        hover_options = {}
        if use_js:
            hover_options["force"] = True
        if offset:
            hover_options["position"] = offset
        if action_timeout is not None:
            hover_options["timeout"] = action_timeout

        await locator.hover(**hover_options)
        CommonUtil.ExecLog(sModuleInfo, "Hover performed", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def Click_and_Download(data_set):
    """Click an element and wait for a browser download."""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        wait_download = 20
        target_path = ""
        click_dataset = []
        for left, mid, right in data_set:
            left_c = _compact(left)
            mid_l = mid.strip().lower()
            if left_c == "waitfordownload":
                wait_download = float(right.strip())
            elif left_c in ("folderpath", "directory", "filepath", "file", "folder") and mid_l == "optional parameter":
                target_path = CommonUtil.path_parser(right.strip())
            elif left_c == "automatefirefoxsavewindow":
                continue
            else:
                click_dataset.append((left, mid, right))

        locator = await PlaywrightLocator.Get_Element(
            click_dataset,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"

        CommonUtil.ExecLog(sModuleInfo, f"Download started. Will wait max {wait_download} seconds...", 1)
        async with current_page.expect_download(timeout=int(wait_download * 1000)) as download_info:
            await locator.click(timeout=_get_action_timeout(click_dataset))
        download = await download_info.value

        if target_path:
            parsed_path = Path(target_path)
            if parsed_path.suffix:
                parsed_path.parent.mkdir(parents=True, exist_ok=True)
                save_path = parsed_path
            else:
                parsed_path.mkdir(parents=True, exist_ok=True)
                save_path = parsed_path / download.suggested_filename
        else:
            save_path = Path(_download_folder()) / download.suggested_filename
        await download.save_as(str(save_path))
        CommonUtil.ExecLog(sModuleInfo, f"File downloaded to '{save_path}'", 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Text Input         #
#                       #
#########################

@logger
async def Enter_Text_In_Text_Box(step_data):
    """
    Enter text in a text field.

    Example 1 - Basic:
        Field               Sub Field           Value
        id                  element parameter   username
        text                action              my_username
        text                playwright action   text

    Example 2 - With options (Selenium-compatible):
        Field               Sub Field           Value
        id                  element parameter   username
        text                action              my_username
        delay               optional parameter  0.1
        clear               optional parameter  true
        use js              optional parameter  false
        text                playwright action   text
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        # Handle session parameter
        session_name, current_page, current_page_id, context, browser = await _handle_playwright_session(step_data)
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        text_value = ""
        delay = 0
        use_js = False
        clear = True
        timeout = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()

            # Skip session parameter - already handled above
            if mid_l == "optional parameter" and left_l == "session":
                continue

            if "action" in mid_l:
                text_value = right  # Don't strip - preserve whitespace
            elif mid_l == "optional parameter":
                if left_l == "delay":
                    delay = float(right.strip())
                elif left_l == "use js":
                    use_js = right.strip().lower() in ("true", "yes", "1")
                elif left_l == "clear":
                    clear = right.strip().lower() not in ("false", "no", "0")
                elif left_l == "timeout":
                    timeout = int(float(right.strip()) * 1000)

        action_timeout = timeout if timeout is not None else _get_action_timeout(step_data)

        locator = await PlaywrightLocator.Get_Element(
            step_data,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"

        # Enter text based on options
        if use_js:
            # JS mode mirrors Selenium: click, set value, dispatch input/change events, click again.
            try:
                await locator.evaluate("el => el.click()", timeout=action_timeout)
            except Exception:
                CommonUtil.ExecLog(sModuleInfo, "Entering text without clicking the element", 2)
            # Use JS template-literal so embedded quotes/newlines are preserved (matches Selenium).
            escaped = text_value.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
            await locator.evaluate(f"el => {{ el.value = `{escaped}`; }}", timeout=action_timeout)
            await locator.dispatch_event("input", timeout=action_timeout)
            await locator.dispatch_event("change", timeout=action_timeout)
            try:
                await locator.evaluate("el => el.click()", timeout=action_timeout)
            except Exception:
                pass
            CommonUtil.ExecLog(sModuleInfo, f"Successfully set the value of to text to: {text_value}", 1)
            return "passed"

        # Non-JS path: click first to focus (best-effort), clear if requested, then type/fill.
        try:
            await locator.click(timeout=action_timeout)
        except Exception:
            CommonUtil.ExecLog(sModuleInfo, "Entering text without clicking the element", 2)

        if clear:
            try:
                # Select-all + delete pattern matches Selenium clear logic across platforms.
                if sys.platform == "darwin":
                    await locator.press("Meta+A", timeout=action_timeout)
                else:
                    await locator.press("Control+A", timeout=action_timeout)
                await locator.press("Delete", timeout=action_timeout)
            except Exception:
                pass
            try:
                # fill() always clears first; also handles inputs where Select-All didn't apply.
                fill_options = {}
                if action_timeout is not None:
                    fill_options["timeout"] = action_timeout
                if delay == 0:
                    await locator.fill(text_value, **fill_options)
                else:
                    # Caller wants per-keystroke delay -> type after clearing.
                    type_options = {"delay": int(delay * 1000)}
                    if action_timeout is not None:
                        type_options["timeout"] = action_timeout
                    await locator.type(text_value, **type_options)
            except Exception:
                return CommonUtil.Exception_Handler(sys.exc_info())
        else:
            type_options = {}
            if delay > 0:
                type_options["delay"] = int(delay * 1000)
            if action_timeout is not None:
                type_options["timeout"] = action_timeout
            await locator.type(text_value, **type_options)

        # Some text fields become unclickable after entering text - best-effort click.
        try:
            await locator.click(timeout=action_timeout)
        except Exception:
            pass

        CommonUtil.ExecLog(sModuleInfo, f"Successfully set the value of to text to: {text_value}", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Could not select/click your element.")


@logger
async def Keystroke_For_Element(step_data):
    """
    Send keystrokes to an element or the page.

    Example 1 - Keys to element:
        Field               Sub Field           Value
        id                  element parameter   search-box
        keystroke keys      action              Enter
        keystroke           playwright action   keystroke

    Example 2 - Key combination:
        Field               Sub Field           Value
        id                  element parameter   editor
        keystroke keys      action              Control+a
        keystroke           playwright action   keystroke

    Example 3 - Characters without element:
        Field               Sub Field           Value
        keystroke chars     action              Hello World
        keystroke           playwright action   keystroke

    Supported keys: Enter, Tab, Escape, Backspace, Delete, ArrowUp, ArrowDown,
                   ArrowLeft, ArrowRight, Home, End, PageUp, PageDown,
                   Control, Shift, Alt, Meta, F1-F12, etc.
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        keystroke_type = None  # "keys" or "chars"
        keystroke_value = ""
        key_count = 1
        has_element = False
        delay = 0

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if "action" in mid_l:
                if left_l == "keystroke keys":
                    keystroke_type = "keys"
                    keystroke_value = right_v
                    # Check for count: "Tab,3" means press Tab 3 times
                    if "," in keystroke_value:
                        parts = keystroke_value.rsplit(",", 1)
                        try:
                            key_count = int(parts[1].strip())
                            keystroke_value = parts[0].strip()
                        except ValueError:
                            pass
                elif left_l == "keystroke chars":
                    keystroke_type = "chars"
                    keystroke_value = right  # Don't strip to preserve whitespace

            elif mid_l == "element parameter":
                has_element = True

            elif mid_l == "optional parameter":
                if left_l == "delay":
                    delay = float(right_v)

        if not keystroke_type:
            CommonUtil.ExecLog(sModuleInfo, "No keystroke type specified (keystroke keys or keystroke chars)", 3)
            return "zeuz_failed"

        # Convert common key names
        key_map = {
            "CTRL": "Control",
            "CONTROL": "Control",
            "CMD": "Meta",
            "COMMAND": "Meta",
            "ALT": "Alt",
            "SHIFT": "Shift",
            "PLUS": "+",
            "MINUS": "-",
            "DASH": "-",
            "ENTER": "Enter",
            "RETURN": "Enter",
            "TAB": "Tab",
            "ESC": "Escape",
            "ESCAPE": "Escape",
            "BACKSPACE": "Backspace",
            "DELETE": "Delete",
            "SPACE": " ",
            "UP": "ArrowUp",
            "ARROWUP": "ArrowUp",
            "DOWN": "ArrowDown",
            "ARROWDOWN": "ArrowDown",
            "LEFT": "ArrowLeft",
            "ARROWLEFT": "ArrowLeft",
            "RIGHT": "ArrowRight",
            "ARROWRIGHT": "ArrowRight",
            "HOME": "Home",
            "END": "End",
            "PAGEUP": "PageUp",
            "PAGEDOWN": "PageDown",
            "INSERT": "Insert",
        }

        if keystroke_type == "keys":
            normalized_keystroke = keystroke_value.replace(" ", "").replace("_", "").lower()
            if normalized_keystroke in ("ctrl+v", "control+v", "ctrlv", "controlv", "cmd+v", "cmdv", "command+v", "commandv"):
                try:
                    import pyperclip

                    paste_text = pyperclip.paste()
                    if has_element:
                        locator = await PlaywrightLocator.Get_Element(
                            step_data,
                            current_page,
                        )
                        if locator == "zeuz_failed":
                            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
                            return "zeuz_failed"
                        await locator.evaluate("""(el, text) => {
                            el.focus();
                            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
                            if (setter) setter.call(el, text); else el.value = text;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }""", paste_text)
                    else:
                        await current_page.evaluate("""text => {
                            const el = document.activeElement;
                            if (el && 'value' in el) {
                                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
                                if (setter) setter.call(el, text); else el.value = text;
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        }""", paste_text)
                    CommonUtil.ExecLog(sModuleInfo, "Paste successfully executed via JavaScript with events", 1)
                    return "passed"
                except Exception:
                    CommonUtil.ExecLog(sModuleInfo, "JavaScript paste execution failed. Trying keypress.", 2)

            # Convert key names
            def to_playwright_key(token):
                token = token.strip()
                normalized_token = token.replace(" ", "").replace("_", "").replace("-", "").upper()
                if normalized_token in key_map:
                    return key_map[normalized_token]
                return token if len(token) == 1 else token.capitalize()

            if "+" in keystroke_value:
                # Key combination like Ctrl+A
                parts = keystroke_value.split("+")
                converted = [to_playwright_key(p) for p in parts]
                key = "+".join(converted)
            else:
                key = to_playwright_key(keystroke_value)

            if has_element:
                locator = await PlaywrightLocator.Get_Element(
                    step_data,
                    current_page,
                )
                if locator == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
                    return "zeuz_failed"

                for _ in range(key_count):
                    await locator.press(key)
                    if delay > 0:
                        await asyncio.sleep(delay)
            else:
                for _ in range(key_count):
                    await current_page.keyboard.press(key)
                    if delay > 0:
                        await asyncio.sleep(delay)

            CommonUtil.ExecLog(sModuleInfo, f"Pressed key: {key} ({key_count} times)", 1)

        elif keystroke_type == "chars":
            type_options = {}
            if delay > 0:
                type_options["delay"] = int(delay * 1000)

            if has_element:
                locator = await PlaywrightLocator.Get_Element(
                    step_data,
                    current_page,
                )
                if locator == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
                    return "zeuz_failed"
                await locator.type(keystroke_value, **type_options)
            else:
                await current_page.keyboard.type(keystroke_value, **type_options)

            CommonUtil.ExecLog(sModuleInfo, f"Typed chars: {keystroke_value[:50]}{'...' if len(keystroke_value) > 50 else ''}", 1)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Validation         #
#                       #
#########################

@logger
async def Validate_Text(step_data):
    """
    Validate that an element contains expected text.

    Example 1 - Exact match:
        Field               Sub Field           Value
        id                  element parameter   message
        validate text       action              Success!
        validate text       playwright action   validate text

    Example 2 - Partial match:
        Field               Sub Field           Value
        id                  element parameter   message
        *validate text      action              Success
        validate text       playwright action   validate text

    Example 3 - Case-insensitive partial:
        Field               Sub Field           Value
        id                  element parameter   message
        **validate text     action              success
        validate text       playwright action   validate text
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        expected_text = ""
        partial_match = False
        case_insensitive = False

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if "action" in mid_l:
                if left_l.startswith("**"):
                    partial_match = True
                    case_insensitive = True
                elif left_l.startswith("*"):
                    partial_match = True
                elif "partial" in left_l:
                    partial_match = True
                expected_text = right_v

            elif mid_l == "optional parameter":
                if left_l == "ignore case":
                    case_insensitive = _truthy(right_v)

        locator = await PlaywrightLocator.Get_Element(
            step_data,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # Get visible text, matching Selenium Element.text behavior more closely.
        try:
            actual_text = await locator.inner_text() or ""
        except Exception:
            actual_text = await locator.text_content() or ""
        actual_lines = [line for line in actual_text.split("\n") if line != ""]

        # Compare
        match = False
        if case_insensitive:
            if partial_match:
                match = any(expected_text.lower() in line.lower() for line in actual_lines)
            else:
                match = expected_text.lower() in [line.lower() for line in actual_lines]
        else:
            if partial_match:
                match = any(expected_text in line for line in actual_lines)
            else:
                match = expected_text in actual_lines

        if match:
            CommonUtil.ExecLog(sModuleInfo, f"Text validation passed: '{expected_text}'", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Text validation failed.\nExpected: '{expected_text}'\nActual: '{actual_lines}'",
                3
            )
            return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def if_element_exists(step_data):
    """
    Check whether an element exists (true/false).

    Selenium-compatible form (writes the result to a shared variable, always returns "passed"):
        Field               Sub Field           Value
        id                  element parameter   optional-element
        if element exists   playwright action   true=my_flag

        - If found: shared variable my_flag is set to "true"
        - If not found: shared variable my_flag is set to "false"

    Plain form (no save):
        Field               Sub Field           Value
        id                  element parameter   optional-element
        if element exists   playwright action   if element exists

        - Returns "passed" if found, "zeuz_failed" if not.
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        variable_name = ""
        value = ""
        timeout = 1000  # Short timeout for existence check

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if "action" in mid_l and "=" in right_v:
                try:
                    value_part, var_part = right_v.split("=", 1)
                    value = value_part.strip()
                    variable_name = var_part.strip()
                except ValueError:
                    pass
            elif mid_l == "optional parameter" and left_l == "timeout":
                timeout = int(float(right_v) * 1000)

        locator = await PlaywrightLocator.Get_Element(
            step_data,
            current_page,
            element_wait=timeout / 1000,
        )

        found = False
        if locator != "zeuz_failed":
            try:
                await locator.wait_for(state="attached", timeout=timeout)
                if await locator.count() > 0:
                    found = True
            except Exception:
                found = False

        if variable_name:
            # Selenium-compatible: always returns "passed"; the truthiness lives in the variable.
            sr.Set_Shared_Variables(variable_name, value if found else "false")
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Element {'found' if found else 'not found'} - saved '{value if found else 'false'}' to '{variable_name}'",
                1,
            )
            return "passed"

        if found:
            CommonUtil.ExecLog(sModuleInfo, "Element exists", 1)
            return "passed"
        CommonUtil.ExecLog(sModuleInfo, "Element does not exist", 1)
        return "zeuz_failed"

    except Exception:
        errMsg = "Failed to parse data/locate element. Data format: variableName = value"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
async def Save_Attribute(step_data):
    """
    Save an element's attribute value to a shared variable.

    Selenium-compatible form (recommended):
        Field               Sub Field           Value
        id                  element parameter   my-link
        href                save parameter      my_variable
        save attribute      playwright action   save attribute

    Alternative form (attribute via input parameter):
        Field               Sub Field           Value
        id                  element parameter   my-link
        href                input parameter     attribute_name
        my_variable         save parameter      ignore
        save attribute      playwright action   save attribute

    Special attribute names:
        - text:       text content (Selenium .text)
        - tag:        tag name (Selenium .tag_name)
        - checked:    checkbox/radio selected state
        - innertext:  inner text
        - innerhtml:  inner HTML
        - outerhtml:  outer HTML
        - value:      input value
        - selected:   <option> selected state
        - visible / enabled / disabled
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        attribute_name = None  # Attribute to read (e.g. "text", "href")
        save_variable = None   # Shared variable to write
        # Build a locator-only data set by excluding the save row (mirrors Selenium).
        new_ds = []

        for left, mid, right in step_data:
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "save parameter":
                # Selenium-style: left = attribute, right = variable name.
                # Playwright legacy style: left = variable, right = "ignore".
                if right_v and right_v.lower() not in ("ignore", "n/a", "na", ""):
                    save_variable = right_v
                    if not attribute_name:
                        attribute_name = left.strip()
                else:
                    save_variable = left.strip()
            elif mid_l == "input parameter":
                # Legacy Playwright style: attribute name lives in input parameter
                attribute_name = left.strip()
            else:
                new_ds.append((left, mid, right))

        if not save_variable:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Variable name should be mentioned. Example: (text, save parameter, var_name)",
                3,
            )
            return "zeuz_failed"

        if not attribute_name:
            CommonUtil.ExecLog(sModuleInfo, "No attribute name specified", 3)
            return "zeuz_failed"

        locator = await PlaywrightLocator.Get_Element(
            new_ds,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"

        # Get attribute value based on name
        attr_lower = attribute_name.lower()
        if attr_lower == "text":
            value = await locator.inner_text()
        elif attr_lower == "tag":
            value = (await locator.evaluate("el => el.tagName") or "").lower()
        elif attr_lower == "innertext":
            value = await locator.inner_text()
        elif attr_lower == "innerhtml":
            value = await locator.inner_html()
        elif attr_lower == "outerhtml":
            value = await locator.evaluate("el => el.outerHTML")
        elif attr_lower == "value":
            value = await locator.input_value()
        elif attr_lower == "checked":
            value = await locator.is_checked()
        elif attr_lower == "selected":
            value = await locator.evaluate("el => el.selected")
        elif attr_lower == "visible":
            value = await locator.is_visible()
        elif attr_lower == "enabled":
            value = await locator.is_enabled()
        elif attr_lower == "disabled":
            value = await locator.is_disabled()
        else:
            value = await locator.get_attribute(attribute_name)

        result = sr.Set_Shared_Variables(save_variable, value)
        if result in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Value of Variable '{save_variable}' could not be saved!!!",
                3,
            )
            return "zeuz_failed"
        CommonUtil.ExecLog(sModuleInfo, f"Saved '{attribute_name}' = '{value}' to '{save_variable}'", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def get_element_info(step_data):
    """
    Get detailed information about an element.

    Example:
        Field               Sub Field           Value
        id                  element parameter   my-element
        element_info        save parameter      ignore
        get element info    playwright action   get element info
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        save_variable = _save_variable_from_action_or_save_parameter(step_data, "get element info")

        locator = await PlaywrightLocator.Get_Element(
            step_data,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        box = await locator.bounding_box()
        info = {
            "size": {"width": box["width"], "height": box["height"]} if box else {},
            "location": {"x": box["x"], "y": box["y"]} if box else {},
        }

        if save_variable:
            sr.Set_Shared_Variables(save_variable, info)
            CommonUtil.ExecLog(sModuleInfo, f"Element info saved to '{save_variable}'", 1)
        else:
            CommonUtil.ExecLog(sModuleInfo, f"Element info: {info}", 1)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Navigation         #
#                       #
#########################

@logger
async def Navigate(step_data):
    """
    Navigate browser (back, forward, refresh).

    Example:
        Field               Sub Field           Value
        navigate            action              back
        navigate            playwright action   navigate

    Options: back, forward, refresh, reload
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        direction = "back"
        timeout = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip().lower()

            if "action" in mid_l:
                direction = right_v
            elif mid_l == "optional parameter":
                if left_l == "timeout":
                    timeout = int(float(right.strip()) * 1000)

        nav_options = {}
        if timeout:
            nav_options["timeout"] = timeout

        if direction in ("back", "go back"):
            await current_page.go_back(**nav_options)
            CommonUtil.ExecLog(sModuleInfo, "Navigated back", 1)
        elif direction in ("forward", "go forward"):
            await current_page.go_forward(**nav_options)
            CommonUtil.ExecLog(sModuleInfo, "Navigated forward", 1)
        elif direction in ("refresh", "reload"):
            await current_page.reload(**nav_options)
            CommonUtil.ExecLog(sModuleInfo, "Page reloaded", 1)
        else:
            CommonUtil.ExecLog(sModuleInfo, f"Unknown navigation direction: {direction}", 3)
            return "zeuz_failed"

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Get_Current_URL(step_data):
    """
    Get the current page URL and save to variable.

    Example:
        Field               Sub Field           Value
        current_url         save parameter      ignore
        get current url     playwright action   get current url
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        save_variable = _save_variable_from_action_or_save_parameter(step_data, "get current url")

        url = current_page.url

        if save_variable:
            sr.Set_Shared_Variables(save_variable, url)
            CommonUtil.ExecLog(sModuleInfo, f"Current URL saved to '{save_variable}': {url}", 1)
        else:
            CommonUtil.ExecLog(sModuleInfo, f"Current URL: {url}", 1)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Scroll             #
#                       #
#########################

@logger
async def Scroll(step_data):
    """
    Scroll the page in a direction.

    Example:
        Field               Sub Field           Value
        direction           input parameter     down
        pixel               input parameter     500
        scroll              playwright action   scroll

    Directions: up, down, left, right
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        direction = "down"
        pixels = 300

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if _is_action_mid(mid_l) and left_l == "scroll":
                direction = right_v.lower()
            elif mid_l == "input parameter":
                if left_l == "direction":
                    direction = right_v.lower()
                elif left_l in ("pixel", "pixels", "amount"):
                    pixels = int(right_v)
            elif left_l in ("pixel", "pixels", "amount"):
                pixels = int(right_v)

        # Calculate delta
        delta_x = 0
        delta_y = 0

        if direction == "down":
            delta_y = pixels
        elif direction == "up":
            delta_y = -pixels
        elif direction == "right":
            delta_x = pixels
        elif direction == "left":
            delta_x = -pixels

        if _has_element_rows(step_data):
            locator = await PlaywrightLocator.Get_Element(
                step_data,
                current_page,
            )
            if locator == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
                return "zeuz_failed"
            await locator.evaluate("(el, offset) => el.scrollBy(offset.x, offset.y)", {"x": delta_x, "y": delta_y})
        else:
            await current_page.mouse.wheel(delta_x, delta_y)
        CommonUtil.ExecLog(sModuleInfo, f"Scrolled {direction} by {pixels}px", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def scroll_to_element(step_data):
    """
    Scroll an element into view.

    Example 1 - Basic:
        Field               Sub Field           Value
        id                  element parameter   footer
        scroll to element   playwright action   scroll to element

    Example 2 - Selenium-compatible options:
        Field               Sub Field           Value
        id                  element parameter   footer
        use js              optional parameter  true
        align to top        optional parameter  true
        method              optional parameter  js
        additional scroll   optional parameter  0.1
        scroll to element   playwright action   scroll to element

    Options:
        - use js (true/false): Use element.scrollIntoView() via JS.
        - align to top (true/false): When using JS, align element to top of viewport.
        - method (js | webdriver | action chain): Which scroll mechanism to use.
            * js (default): element.scrollIntoView()
            * webdriver: Playwright's scroll_into_view_if_needed()
            * action chain: Hover the element so it is brought into view by the engine.
        - additional scroll (fraction, e.g. 0.1): After scrolling into view, scroll an
          additional fraction of the viewport in the direction the page just moved.
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        method = "js"
        align_to_top = "true"
        additional_scroll = 0.1
        direction = ""

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip().lower()

            if mid_l == "optional parameter":
                if left_l == "use js":
                    method = "js" if right_v in ("true", "yes", "1") else "action chain"
                elif left_l == "align to top":
                    align_to_top = "true" if right_v in ("true", "yes", "1") else "false"
                elif left_l == "method":
                    method = right_v
                elif "additional scroll" in left_l:
                    try:
                        additional_scroll = float(right_v)
                    except ValueError:
                        additional_scroll = 0.1
                    direction_part = left_l.replace("additional scroll", "").strip()
                    if direction_part in ("up", "down", "left", "right"):
                        direction = direction_part

        locator = await PlaywrightLocator.Get_Element(
            step_data,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element to which instructed to scroll not found", 3)
            return "zeuz_failed"

        top, left_pos = None, None
        if not direction and additional_scroll > 0:
            try:
                top, left_pos = await current_page.evaluate(
                    "() => [window.pageYOffset || document.documentElement.scrollTop,"
                    " window.pageXOffset || document.documentElement.scrollLeft]"
                )
            except Exception:
                top, left_pos = None, None

        if method == "js":
            await locator.evaluate(f"el => el.scrollIntoView({align_to_top})")
        elif method == "webdriver":
            await locator.scroll_into_view_if_needed()
        else:
            # "action chain" -> hover brings element into view in Playwright.
            await locator.hover()

        CommonUtil.ExecLog(sModuleInfo, f"Scrolled to view with method = {method}", 1)

        if (
            not direction
            and additional_scroll > 0
            and top is not None
            and left_pos is not None
        ):
            try:
                new_top, new_left = await current_page.evaluate(
                    "() => [window.pageYOffset || document.documentElement.scrollTop,"
                    " window.pageXOffset || document.documentElement.scrollLeft]"
                )
                if new_top > top:
                    direction = "down"
                elif new_top < top:
                    direction = "up"
                elif new_left > left_pos:
                    direction = "right"
                elif new_left < left_pos:
                    direction = "left"
                else:
                    direction = ""
            except Exception:
                direction = ""

            if (
                method in ("js", "webdriver")
                and (
                    (align_to_top == "true" and direction in ("down", "right"))
                    or (align_to_top == "false" and direction in ("up", "left"))
                )
            ):
                direction = ""

        if direction and additional_scroll > 0:
            viewport = current_page.viewport_size or {"width": 1280, "height": 720}
            axis = "height" if direction in ("up", "down") else "width"
            pixels = round(viewport[axis] * additional_scroll)
            offset = _generate_scroll_offset(direction, pixels)
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Doing additional scroll in {direction} direction, {additional_scroll * 100}% of "
                f"{axis} of html body, ({offset}) pixels",
                1,
            )
            await current_page.evaluate(f"window.scrollBy({offset})")

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _generate_scroll_offset(direction: str, pixel: int) -> str:
    if direction == "down":
        return f"0,{pixel}"
    if direction == "up":
        return f"0,-{pixel}"
    if direction == "left":
        return f"-{pixel},0"
    if direction == "right":
        return f"{pixel},0"
    return "0,0"


_SCROLL_TO_TOP_JS = """
(() => {
    var pre_x = window.pageXOffset;
    var pre_y = window.pageYOffset;
    window.scrollTo(window.pageXOffset, 0);
    return [pre_x, pre_y, window.pageXOffset, window.pageYOffset];
})()
"""


def _is_session_step_row(left, mid):
    return _normalize_step_mid(mid) == "optionalparameter" and left.strip().lower() == "session"


def _normalize_step_mid(mid):
    """Match LocateElement: ignore spaces/newlines in sub-field names."""
    return (
        mid.replace(" ", "")
        .replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
        .lower()
    )


def _is_element_parameter_mid(mid):
    mid_norm = _normalize_step_mid(mid)
    return mid_norm == "elementparameter" or (
        "element" in mid_norm and "parameter" in mid_norm and "target" not in mid_norm
    )


def _is_target_parameter_mid(mid):
    mid_norm = _normalize_step_mid(mid)
    # UI may show only "target" on one line; "parameter" on the next (full name is still one row in data).
    return mid_norm in ("targetparameter", "target") or (
        "target" in mid_norm and "parameter" in mid_norm
    )


def _resolve_list_action_variable_name(left, mid, right, action_key):
    """
    Read shared-variable name from a save-*-in-list action row.

    Zeuz may send the variable in the Value column (right) or Field column (left)
    when the other column repeats the action keyword.
    """
    left_raw = left.strip()
    right_raw = right.strip()
    left_norm = left_raw.lower().replace(" ", "").replace("_", "")
    right_norm = right_raw.lower().replace(" ", "").replace("_", "")
    mid_norm = _normalize_step_mid(mid)

    if left_norm == action_key:
        if right_norm and right_norm != action_key:
            return right_raw
        return None

    if mid_norm in ("playwrightaction", "seleniumaction"):
        if right_norm == action_key and left_norm and left_norm != action_key:
            return left_raw
        if right_norm and right_norm != action_key:
            return right_raw
    return None


async def _require_playwright_page(step_data, sModuleInfo):
    """Activate session from step_data and ensure a page is open."""
    global current_page
    await _handle_playwright_session(step_data)
    if current_page is None:
        CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
        return "zeuz_failed"
    return current_page


async def _read_element_attribute_for_list(locator, attribute_name):
    if attribute_name == "text":
        return await locator.inner_text()
    if attribute_name == "tag":
        tag = await locator.evaluate("el => el.tagName")
        return tag.lower() if tag else ""
    if attribute_name == "checked":
        return str(await locator.is_checked())
    return await locator.get_attribute(attribute_name)


def _apply_return_contains_filter(value, contains_rules):
    if not contains_rules:
        return value
    for rule in contains_rules:
        if (
            not isinstance(rule, type(value))
            or rule in value
            or len(rule) == 0
        ):
            break
    else:
        return None
    return value


def _apply_return_does_not_contain_filter(value, exclude_rules):
    for rule in exclude_rules:
        if (
            isinstance(rule, type(value))
            and rule in value
            and len(rule) != 0
        ):
            return None
    return value


def _target_param_continues_previous_target(right):
    """True when this target-parameter row adds return/filter rules to the prior target."""
    text = right.strip().lower()
    return text.startswith(
        ("return", "return_contains", "return_does_not_contain", "allow hidden", "allowhidden")
    )


def _parse_target_kv_pairs(right, split_on_newline=False, field_hint=None):
    """Parse target parameter value into (key, value) pairs.

    Matches Selenium semantics for both list actions:
      - save_attribute_values_in_list expects bare-string filter values:
            return_contains="128GB" -> ('return_contains', '128GB')
      - save_web_elements_in_list expects (attr, needle) filter pairs:
            return_contains="text=128GB" -> ('return_contains', ('text', '128GB'))

    The shape used depends on whether the value (after quote-stripping) has an
    inner '=', mirroring Selenium's `each.split("=")` behavior on a list of length
    1 vs 2.
    """
    text = right.strip().rstrip(",")
    # UI may use comma-only (one line) or comma+newline (multi-line) separators.
    if split_on_newline and ",\n" in text:
        chunks = text.split(",\n")
    else:
        chunks = text.split(",")
    pairs = []
    hint = (field_hint or "").strip().lower() or "class"
    for chunk in chunks:
        chunk = chunk.strip().rstrip(",")
        if not chunk:
            continue
        if "=" not in chunk:
            if hint:
                # Shorthand: "productItemName" with Field column "class"
                pairs.append((hint, chunk))
            else:
                pairs.append((chunk, ""))
            continue

        key, value = chunk.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key in ("return_contains", "return_does_not_contain"):
            # Strip the wrapping quotes (if any) on the value first; an INNER '='
            # then signals the attr=needle pair form used by save_web_elements_in_list.
            inner = CommonUtil.strip1(value, '"')
            if "=" in inner:
                attr, needle = inner.split("=", 1)
                pairs.append((key, (attr.strip(), needle.strip())))
            else:
                pairs.append((key, inner))
        else:
            pairs.append((key, value))
    return pairs


def _normalize_target_pair_values(pairs):
    normalized = []
    for pair in pairs:
        if len(pair) == 1:
            normalized.append((pair[0].strip(), ""))
            continue
        key, value = pair[0], pair[1]
        key = key.strip() if isinstance(key, str) else key
        if isinstance(value, str):
            value = CommonUtil.strip1(value.strip(), '"')
        elif isinstance(value, tuple) and len(value) == 2:
            value = (
                CommonUtil.strip1(value[0].strip(), '"'),
                CommonUtil.strip1(value[1].strip(), '"'),
            )
        elif isinstance(value, list) and len(value) == 2:
            value = (value[0].strip().strip('"'), value[1].strip().strip('"'))
        normalized.append((key, value))
    pairs[:] = normalized


def _append_target_spec(target_specs, key, value, spec_index):
    spec = target_specs[spec_index]
    if key == "return":
        spec[1] = value
    elif key == "return_contains":
        spec[2].append(value)
    elif key == "return_does_not_contain":
        spec[3].append(value)
    elif key.replace(" ", "").replace("_", "") in ("allowhidden", "allowdisable"):
        spec[0].append(("allow hidden", "optional parameter", value))
    else:
        spec[0].append((key, "element parameter", value))


async def _element_matches_return_contains(elem, rules):
    text = await elem.inner_text()
    tag = (await elem.evaluate("el => el.tagName")).lower()
    for attr, needle in rules:
        if attr == "text" and needle in text:
            return True
        if attr == "tag" and needle in tag:
            return True
        if attr not in ("text", "tag"):
            attr_val = await elem.get_attribute(attr)
            if attr_val is None:
                return False
            if needle in attr_val:
                return True
    return False


async def _element_matches_return_does_not_contain(elem, rules):
    text = await elem.inner_text()
    tag = (await elem.evaluate("el => el.tagName")).lower()
    for attr, needle in rules:
        if attr == "text" and needle in text:
            return True
        if attr == "tag" and needle in tag:
            return True
        if attr not in ("text", "tag"):
            attr_val = await elem.get_attribute(attr)
            if attr_val is None or needle in (attr_val or ""):
                return True
    return False


async def _filter_elements_return_contains(elements, contains_rules):
    if not contains_rules:
        return elements
    filtered = []
    for elem in elements:
        if await _element_matches_return_contains(elem, contains_rules):
            filtered.append(elem)
    return filtered


async def _filter_elements_return_does_not_contain(elements, exclude_rules):
    if not exclude_rules:
        return elements
    return [
        elem
        for elem in elements
        if not await _element_matches_return_does_not_contain(elem, exclude_rules)
    ]


@logger
async def scroll_to_top(step_data):
    """
    Scroll the browser window to the top of the page (vertical offset 0).

    Example:
        Field               Sub Field           Value
        scroll to top       playwright action   scroll to top
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        page = await _require_playwright_page(step_data, sModuleInfo)
        if page == "zeuz_failed":
            return "zeuz_failed"

        pre_x, pre_y, x, y = await page.evaluate(_SCROLL_TO_TOP_JS)
        CommonUtil.ExecLog(
            sModuleInfo,
            f"Scrolled to top of the html.\npre_x, pre_y, x, y = [{pre_x}, {pre_y}, {x}, {y}]",
            1 if (x, y) == (0, 0) else 2,
        )
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def save_attribute_values_in_list(step_data):
    """
    Collect attribute or text values from multiple child element groups under a parent.

    Each target parameter block defines locators plus optional return filters. Results are
    stored in a shared variable as rows (paired) or columns (paired=no).

    Example 1 - Product names and prices:
        Field                               Sub Field           Value
        aria-label                          element parameter   Calendar
        attributes                          target parameter    data-automation="productItemName",
                                                                class="S58f2saa25a3w1",
                                                                return="text"
        attributes                          target parameter    class="productPricingContainer_3gTS3",
                                                                return="text",
                                                                return_does_not_contain="99.99"
        save attribute values in list       playwright action   product_rows

    Example 2 - Unpaired columns:
        Field                               Sub Field           Value
        tag                                 element parameter   html
        class                               target parameter    item, return="text"
        class                               target parameter    price, return="text"
        paired                              optional parameter  no
        save attribute values in list       playwright action   columns_list
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if await _require_playwright_page(step_data, sModuleInfo) == "zeuz_failed":
            return "zeuz_failed"

        parent = await PlaywrightLocator.Get_Element(step_data, current_page)
        if parent == "zeuz_failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"

        targets = []
        variable_name = ""
        paired = True

        try:
            spec_index = -1
            for left, mid, right in step_data:
                if _is_session_step_row(left, mid):
                    continue
                left_l = left.strip().lower()
                right = right.strip()
                if _is_target_parameter_mid(mid):
                    if spec_index >= 0 and _target_param_continues_previous_target(right):
                        pass  # append to current target spec
                    else:
                        targets.append([[], "", [], []])
                        spec_index += 1
                    pairs = _parse_target_kv_pairs(
                        right, split_on_newline=True, field_hint=left_l
                    )
                    _normalize_target_pair_values(pairs)
                    for key, value in pairs:
                        _append_target_spec(targets, key, value, spec_index)
                else:
                    var_candidate = _resolve_list_action_variable_name(
                        left,
                        mid,
                        right,
                        "saveattributevaluesinlist",
                    )
                    if var_candidate:
                        variable_name = var_candidate
                if left_l == "paired":
                    paired = right.lower() != "no"
            if not targets:
                CommonUtil.ExecLog(sModuleInfo, "No target parameter rows found in step data", 3)
                return "zeuz_failed"
            if not variable_name:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "No variable name for save attribute values in list (set action value e.g. product_data)",
                    3,
                )
                return "zeuz_failed"
        except Exception as exc:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Unable to parse data. Please write data in correct format ({exc})",
                3,
            )
            return "zeuz_failed"

        element_groups = []
        for locator_rows, return_attr, contains_rules, exclude_rules in targets:
            elements = await PlaywrightLocator.Get_Element(
                locator_rows,
                parent,
                return_all_elements=True,
            )
            if elements == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Unable to locate target elements.", 3)
                return "zeuz_failed"
            element_groups.append((elements, return_attr, contains_rules, exclude_rules))

        max_len = max((len(group[0]) for group in element_groups), default=0)
        rows = [[] for _ in range(max_len)]

        for elements, return_attr, contains_rules, exclude_rules in element_groups:
            for index, elem in enumerate(elements):
                value = await _read_element_attribute_for_list(elem, return_attr)
                try:
                    value = _apply_return_contains_filter(value, contains_rules)
                    value = _apply_return_does_not_contain_filter(value, exclude_rules)
                except Exception:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Couldn't search by return_contains and return_does_not_contain",
                        2,
                    )
                rows[index].append(value)

        if len(targets) == 1:
            # Match Selenium: one target => flat list of values (all elements), not rows[0] only.
            result = list(map(list, zip(*rows)))[0] if rows else []
        elif not paired:
            result = list(map(list, zip(*rows))) if rows else []
        else:
            result = rows

        return sr.Set_Shared_Variables(variable_name, result)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


_ELEMENT_SCOPE_MIDS = frozenset(
    {
        "element parameter",
        "parent parameter",
        "unique parameter",
        "child parameter",
        "sibling parameter",
    }
)


@logger
async def save_web_elements_in_list(step_data):
    """
    Save Playwright locators for multiple element groups into a shared variable.

    Optional parent scope limits the search. Use return_contains / return_does_not_contain
    in target parameters to filter matched elements before saving.

    Example 1 - Under a container:
        Field                           Sub Field           Value
        id                              element parameter   product-list
        class                           target parameter    item, return_contains=text=Phone
        save web elements in list       playwright action   phone_items

    Example 2 - Whole page (no parent rows):
        Field                           Sub Field           Value
        class                           target parameter    btn-primary
        save web elements in list       playwright action   all_buttons
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if await _require_playwright_page(step_data, sModuleInfo) == "zeuz_failed":
            return "zeuz_failed"

        targets = []
        variable_name = ""
        has_parent_scope = False

        try:
            spec_index = -1
            for left, mid, right in step_data:
                if _is_session_step_row(left, mid):
                    continue
                left = left.strip().lower()
                mid = mid.strip().lower()
                right = right.strip()
                if not has_parent_scope and _is_element_parameter_mid(mid):
                    has_parent_scope = True
                elif _is_target_parameter_mid(mid):
                    if spec_index >= 0 and _target_param_continues_previous_target(right):
                        pass
                    else:
                        targets.append([[], [], [], []])
                        spec_index += 1
                    pairs = _parse_target_kv_pairs(right, field_hint=left)
                    _normalize_target_pair_values(pairs)
                    for key, value in pairs:
                        _append_target_spec(targets, key, value, spec_index)
                else:
                    var_candidate = _resolve_list_action_variable_name(
                        left,
                        mid,
                        right,
                        "savewebelementsinlist",
                    )
                    if var_candidate:
                        variable_name = var_candidate

            if has_parent_scope:
                parent = await PlaywrightLocator.Get_Element(
                    step_data, current_page
                )
                if parent == "zeuz_failed":
                    CommonUtil.ExecLog(
                        sModuleInfo, "Unable to locate your element with given data.", 3
                    )
                    return "zeuz_failed"
            else:
                parent = None
        except Exception:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Unable to parse data. Please write data in correct format",
                3,
            )
            return "zeuz_failed"

        element_lists = []
        for locator_rows, _return_attr, contains_rules, exclude_rules in targets:
            elements = await PlaywrightLocator.Get_Element(
                locator_rows,
                parent or current_page,
                return_all_elements=True,
            )
            if elements == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Unable to locate target elements.", 3)
                return "zeuz_failed"
            elements = await _filter_elements_return_contains(elements, contains_rules)
            elements = await _filter_elements_return_does_not_contain(elements, exclude_rules)
            element_lists.append(elements)

        if len(targets) == 1:
            return sr.Set_Shared_Variables(variable_name, element_lists[0])
        return sr.Set_Shared_Variables(variable_name, element_lists)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _insert_string_targets(string: str, str_to_insert: str, index: int) -> str:
    return string[:index] + str_to_insert + string[index:]


def _parse_multiple_check_targets(target_parameter_value):
    """Parse target parameter string into (locator_key, locator_value, action) tuples."""
    inside = False
    temp = target_parameter_value.strip()
    i = 0
    while i < len(temp):
        if temp[i] == "(":
            inside = True
            temp = _insert_string_targets(temp, '"', i + 1)
        elif inside and temp[i] == ",":
            temp = _insert_string_targets(temp, '"', i + 1)
            temp = _insert_string_targets(temp, '"', i)
            i += 1
        elif temp[i] == ")":
            inside = False
            temp = _insert_string_targets(temp, '"', i)
            i += 1
        i += 1
    temp = _insert_string_targets(temp, "[", 0)
    temp = _insert_string_targets(temp, "]", len(temp))
    parsed = CommonUtil.parse_value_into_object(temp)
    return [
        (row[0].strip().lower(), row[1].strip(), row[2].strip().lower())
        for row in parsed
    ]


async def _toggle_checkbox_target(locator, action, use_js, target_label):
    """Check or uncheck one target; logs and swallows per-target failures like Selenium."""
    try:
        checked = await locator.is_checked()
    except Exception:
        try:
            checked = await locator.evaluate("el => Boolean(el.checked || el.getAttribute('aria-checked') === 'true')")
        except Exception:
            checked = None
    if checked is not None:
        if action == "check" and checked:
            CommonUtil.ExecLog("", f"{target_label} is already checked so skipped it", 1)
            return
        if action == "uncheck" and not checked:
            CommonUtil.ExecLog("", f"{target_label} is already unchecked so skipped it", 1)
            return

    via_js = use_js
    try:
        if use_js:
            await locator.evaluate("el => el.click()")
        else:
            try:
                await locator.click()
            except Exception:
                await locator.evaluate("el => el.click()")
                via_js = True
        verb = "checked" if action == "check" else "unchecked"
        suffix = " using Java Script" if via_js else ""
        CommonUtil.ExecLog("", f"{target_label} is {verb} successfully{suffix}", 1)
    except Exception:
        verb = "checked" if action == "check" else "unchecked"
        CommonUtil.ExecLog("", f"{target_label} couldn't be {verb} so skipped it", 3)


@logger
async def multiple_check_uncheck(data_set):
    """
    Check or uncheck multiple checkbox/radio elements under one parent.

    Each entry in target parameter is (locator field, locator value, check|uncheck).
    Missing targets are skipped; the step still returns passed.

    Example 1 - Basic:
        Field                       Sub Field           Value
        id                          element parameter   form-panel
        target parameter            target parameter    (id, opt-a, check), (id, opt-b, uncheck)
        multiple check uncheck      playwright action   multiple check uncheck

    Example 2 - JavaScript click:
        Field                       Sub Field           Value
        class                       element parameter   options-group
        use js                      optional parameter  true
        allow hidden                optional parameter  yes
        target parameter            target parameter    (name, hidden-opt, check)
        multiple check uncheck      playwright action   multiple check uncheck
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    use_js = False
    allow_hidden = ""
    targets = None

    try:
        for left, mid, right in data_set:
            left = left.lower().strip()
            mid = mid.lower().strip()
            if _is_session_step_row(left, mid):
                continue
            if left == "use js":
                use_js = right.strip().lower() in ("true", "yes", "ok")
            elif left == "allow hidden":
                allow_hidden = right
            elif mid == "target parameter":
                targets = _parse_multiple_check_targets(right)

    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error parsing data set"
        )

    if not targets:
        CommonUtil.ExecLog(sModuleInfo, "No target parameter found in step data", 3)
        return "zeuz_failed"

    try:
        if await _require_playwright_page(data_set, sModuleInfo) == "zeuz_failed":
            return "zeuz_failed"

        parent = await PlaywrightLocator.Get_Element(data_set, current_page)
        if parent == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find the parent element", 3)
            return "zeuz_failed"

        for locator_key, locator_value, action in targets:
            locate_rows = [(locator_key, "element parameter", locator_value)]
            if allow_hidden:
                locate_rows.insert(0, ("allow hidden", "option", allow_hidden))

            locator = await PlaywrightLocator.Get_Element(
                locate_rows, parent
            )
            target_label = str((locator_key, locator_value, action))
            if locator == "zeuz_failed":
                CommonUtil.ExecLog("", f"{target_label} was not found so skipped it", 3)
                continue

            await _toggle_checkbox_target(locator, action, use_js, target_label)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def Change_Attribute_Value(step_data):
    """
    Set a DOM property on the located element via JavaScript (same idea as Selenium).

    The left column of an input parameter row is the property name; the right column is the value.

    Example 1 - Input value:
        Field                       Sub Field           Value
        id                          element parameter   email-field
        value                       input parameter     user@example.com
        change attribute value      playwright action   change attribute value

    Example 2 - Read-only flag:
        Field                       Sub Field           Value
        id                          element parameter   age-input
        readOnly                    input parameter     true
        change attribute value      playwright action   change attribute value
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if await _require_playwright_page(step_data, sModuleInfo) == "zeuz_failed":
            return "zeuz_failed"

        attribute_name = ""
        change_value = ""
        for left, mid, right in step_data:
            if _is_session_step_row(left, mid):
                continue
            if "input parameter" in mid.strip().lower():
                attribute_name = left.strip().lower()
                change_value = right

        locator = await PlaywrightLocator.Get_Element(
            step_data,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"

        await locator.evaluate(
            "(el, payload) => { el[payload.name] = payload.value; }",
            {"name": attribute_name, "value": change_value},
        )
        CommonUtil.ExecLog(
            sModuleInfo,
            f"Successfully set the value of the attribute to: {change_value}",
            1,
        )
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Could not find your element."
        )


#########################
#                       #
#    Select/Dropdown    #
#                       #
#########################

@logger
async def Select_Deselect(step_data):
    """
    Select or deselect options in a dropdown/select element.

    Example 1 - Select by visible text:
        Field               Sub Field           Value
        id                  element parameter   country-select
        select              action              United States
        select              playwright action   select

    Example 2 - Select by value:
        Field               Sub Field           Value
        id                  element parameter   country-select
        select by value     action              US
        select              playwright action   select

    Example 3 - Select by index:
        Field               Sub Field           Value
        id                  element parameter   country-select
        select by index     action              2
        select              playwright action   select
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        select_type = "label"  # label, value, index
        select_value = None
        is_deselect = False
        deselect_all = False

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if "action" in mid_l:
                if "deselect" in left_l:
                    is_deselect = True
                    if "all" in left_l:
                        deselect_all = True

                if "by value" in left_l or "byvalue" in left_l:
                    select_type = "value"
                elif "by index" in left_l or "byindex" in left_l:
                    select_type = "index"
                elif "by label" in left_l or "by text" in left_l:
                    select_type = "label"

                select_value = right_v

        if deselect_all:
            select_value = ""
        elif not select_value:
            CommonUtil.ExecLog(sModuleInfo, "No selection value provided", 3)
            return "zeuz_failed"

        locator = await PlaywrightLocator.Get_Element(
            step_data,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # Build selection option
        if select_type == "value":
            option = {"value": select_value}
        elif select_type == "index" and select_value != "":
            option = {"index": int(select_value)}
        else:  # label
            option = {"label": select_value}

        if is_deselect:
            # Playwright doesn't have direct deselect, use JavaScript
            await locator.evaluate("""(el, data) => {
                for (const opt of el.options) {
                    if (data.all ||
                        (data.type === 'value' && opt.value === data.value) ||
                        (data.type === 'label' && opt.text === data.value) ||
                        (data.type === 'index' && opt.index === Number(data.value))) {
                        opt.selected = false;
                    }
                }
                el.dispatchEvent(new Event('change'));
            }""", {"all": deselect_all, "type": select_type, "value": select_value})
            CommonUtil.ExecLog(sModuleInfo, f"Deselected: {select_value}", 1)
        else:
            await locator.select_option(**option)
            CommonUtil.ExecLog(sModuleInfo, f"Selected: {select_value}", 1)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Checkbox/Radio     #
#                       #
#########################

@logger
async def check_uncheck(step_data):
    """
    Check or uncheck a checkbox/radio button.

    Example:
        Field               Sub Field           Value
        id                  element parameter   agree-checkbox
        check uncheck       action              check
        check               playwright action   check

    Actions: check, uncheck
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        action = "check"
        use_js = False

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip().lower()

            if "action" in mid_l:
                if "uncheck" in left_l or "uncheck" in right_v:
                    action = "uncheck"
                else:
                    action = "check"
            elif mid_l == "optional parameter":
                if left_l == "use js":
                    use_js = right_v in ("true", "yes", "1")

        locator = await PlaywrightLocator.Get_Element(
            step_data,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        await _toggle_checkbox_target(locator, action, use_js, "The element")

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def check_uncheck_all(data_set):
    """Check or uncheck all target elements under a parent element."""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        use_js = False
        target = []
        command = "check"
        for left, mid, right in data_set:
            left_l = left.lower().strip()
            mid_l = mid.lower().strip()
            if left_l == "use js":
                use_js = _truthy(right)
            elif mid_l == "target parameter":
                target.append((left, "element parameter", right))
            elif left_l == "check uncheck all":
                command = "uncheck" if "uncheck" in right.lower() else "check"
            elif left_l == "allow hidden":
                target.append((left, "option", right))

        parent = await PlaywrightLocator.Get_Element(
            data_set,
            current_page,
        )
        if parent == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find the parent element", 3)
            return "zeuz_failed"

        all_elements = await PlaywrightLocator.Get_Element(target, parent, return_all_elements=True)
        if not all_elements or all_elements == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "No target was found", 3)
            return "zeuz_failed"

        for index, element in enumerate(all_elements, start=1):
            suffix = "th"
            if index == 1:
                suffix = "st"
            elif index == 2:
                suffix = "nd"
            elif index == 3:
                suffix = "rd"
            await _toggle_checkbox_target(element, command, use_js, f"{index}{suffix} target")

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def slider_bar(data_set):
    """Set a slider by clicking at a percentage across the element."""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        value = None
        for left, mid, right in data_set:
            if _is_action_mid(mid):
                value = int(right.strip())
        if value is None:
            CommonUtil.ExecLog(sModuleInfo, "Slider value must be provided", 3)
            return "zeuz_failed"

        locator = await PlaywrightLocator.Get_Element(
            data_set,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find the element", 3)
            return "zeuz_failed"

        box = await locator.bounding_box()
        if not box:
            CommonUtil.ExecLog(sModuleInfo, "Could not compute slider size", 3)
            return "zeuz_failed"
        x = box["x"] + (value / 100) * box["width"]
        y = box["y"] + box["height"] / 2
        await current_page.mouse.click(x, y)
        CommonUtil.ExecLog(sModuleInfo, f"Successfully set the slider to %{value}", 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Windows/Tabs       #
#                       #
#########################

@logger
async def switch_window_or_tab(step_data):
    """
    Switch to a different window/tab.

    Example 1 - By title:
        Field               Sub Field           Value
        window title        input parameter     Google
        switch window/tab   playwright action   switch window or tab

    Example 2 - By partial title:
        Field               Sub Field           Value
        *window title       input parameter     Goo
        switch window/tab   playwright action   switch window or tab

    Example 3 - By index:
        Field               Sub Field           Value
        window index        input parameter     1
        switch window/tab   playwright action   switch window or tab
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page, context

    try:
        if context is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser context open", 3)
            return "zeuz_failed"

        switch_by_title = None
        switch_by_index = None
        partial_match = False

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "input parameter":
                if left_l in ("window title", "tab title"):
                    switch_by_title = right_v
                elif left_l in ("*window title", "*tab title"):
                    switch_by_title = right_v
                    partial_match = True
                elif left_l in ("window index", "tab index"):
                    switch_by_index = int(right_v)

        pages = context.pages

        if switch_by_title:
            for page in pages:
                page_title = await page.title()
                if partial_match:
                    if switch_by_title.lower() in page_title.lower():
                        current_page = page
                        await page.bring_to_front()
                        sr.Set_Shared_Variables("playwright_page", current_page)
                        CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())
                        CommonUtil.ExecLog(sModuleInfo, f"Switched to tab: {page_title}", 1)
                        return "passed"
                else:
                    if switch_by_title.lower() == page_title.lower():
                        current_page = page
                        await page.bring_to_front()
                        sr.Set_Shared_Variables("playwright_page", current_page)
                        CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())
                        CommonUtil.ExecLog(sModuleInfo, f"Switched to tab: {page_title}", 1)
                        return "passed"

            CommonUtil.ExecLog(sModuleInfo, f"No tab found with title: {switch_by_title}", 3)
            return "zeuz_failed"

        elif switch_by_index is not None:
            if 0 <= switch_by_index < len(pages):
                current_page = pages[switch_by_index]
                await current_page.bring_to_front()
                sr.Set_Shared_Variables("playwright_page", current_page)
                CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())
                CommonUtil.ExecLog(sModuleInfo, f"Switched to tab index {switch_by_index}: {await current_page.title()}", 1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, f"Invalid tab index: {switch_by_index}", 3)
                return "zeuz_failed"

        CommonUtil.ExecLog(sModuleInfo, "No window title or index provided", 3)
        return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def open_new_tab(step_data):
    """
    Open a new browser tab.

    Example:
        Field               Sub Field           Value
        url                 input parameter     https://example.com
        open new tab        playwright action   open new tab
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page, context

    try:
        if context is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser context open", 3)
            return "zeuz_failed"

        url = None
        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "input parameter" and left_l in ("url", "link", "go to link"):
                url = right_v

        new_page = await context.new_page()
        current_page = new_page
        sr.Set_Shared_Variables("playwright_page", current_page)
        if current_page_id:
            sessions = get_browser_sessions()
            if current_page_id in sessions:
                sessions[current_page_id]["playwright_page"] = current_page
                sr.Set_Shared_Variables("browser_sessions", sessions)
        CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())

        if url:
            await new_page.goto(url)
            CommonUtil.ExecLog(sModuleInfo, f"Opened new tab with URL: {url}", 1)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Opened new blank tab", 1)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def close_tab(step_data):
    """
    Close a browser tab.

    Example 1 - Close current:
        Field               Sub Field           Value
        close tab           playwright action   close tab

    Example 2 - Close by title:
        Field               Sub Field           Value
        tab title           input parameter     Google
        close tab           playwright action   close tab
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page, context

    try:
        if context is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser context open", 3)
            return "zeuz_failed"

        tab_title = None
        tab_index = None
        close_tabs = []

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "input parameter":
                if left_l == "tab title":
                    tab_title = right_v
                elif left_l == "tab index":
                    tab_index = int(right_v)
                elif left_l == "tabs":
                    close_tabs = CommonUtil.parse_value_into_object(right_v)

        pages = context.pages

        if close_tabs:
            for target in close_tabs:
                pages = context.pages
                if isinstance(target, int):
                    if -len(pages) <= target < len(pages):
                        await pages[target].close()
                    else:
                        CommonUtil.ExecLog(sModuleInfo, f"Invalid tab index: {target}", 3)
                        return "zeuz_failed"
                else:
                    target_l = str(target).lower()
                    for page in pages:
                        if target_l in (await page.title()).lower():
                            await page.close()
                            break
                    else:
                        CommonUtil.ExecLog(sModuleInfo, f"Tab not found: {target}", 3)
                        return "zeuz_failed"
        elif tab_title:
            for page in pages:
                if tab_title.lower() in (await page.title()).lower():
                    await page.close()
                    CommonUtil.ExecLog(sModuleInfo, f"Closed tab: {tab_title}", 1)
                    break
            else:
                CommonUtil.ExecLog(sModuleInfo, f"Tab not found: {tab_title}", 3)
                return "zeuz_failed"
        elif tab_index is not None:
            if 0 <= tab_index < len(pages):
                await pages[tab_index].close()
                CommonUtil.ExecLog(sModuleInfo, f"Closed tab at index {tab_index}", 1)
            else:
                CommonUtil.ExecLog(sModuleInfo, f"Invalid tab index: {tab_index}", 3)
                return "zeuz_failed"
        else:
            # Close current tab
            if current_page:
                current_index = pages.index(current_page) if current_page in pages else len(pages) - 1
                await current_page.close()
                CommonUtil.ExecLog(sModuleInfo, "Closed current tab", 1)

        # Switch to remaining tab if available
        pages = context.pages
        if pages:
            if 'current_index' in locals() and current_index > 0 and current_index - 1 < len(pages):
                current_page = pages[current_index - 1]
            elif 'current_index' in locals():
                current_page = pages[0]
            else:
                current_page = pages[-1]
            sr.Set_Shared_Variables("playwright_page", current_page)
            if current_page_id:
                sessions = get_browser_sessions()
                if current_page_id in sessions:
                    sessions[current_page_id]["playwright_page"] = current_page
                    sr.Set_Shared_Variables("browser_sessions", sessions)
            CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    IFrames            #
#                       #
#########################

@logger
async def switch_iframe(step_data):
    """
    Switch to an iframe or back to main content.

    Example 1 - Switch by locator:
        Field               Sub Field           Value
        id                  iframe parameter    my-iframe
        switch iframe       playwright action   switch iframe

    Example 2 - Switch by index (positive or negative):
        Field               Sub Field           Value
        index               iframe parameter    0
        switch iframe       playwright action   switch iframe

    Example 3 - Switch to default/main:
        Field               Sub Field           Value
        index               input parameter     default content
        switch iframe       playwright action   switch iframe

    Example 4 - Nested frames (multiple rows, applied in order):
        Field               Sub Field           Value
        id                  iframe parameter    outer-frame
        id                  iframe parameter    inner-frame
        switch iframe       playwright action   switch iframe

    Behavior notes (Selenium-compatible):
        - Index lookup is retried (up to 5 times, 2s apart) to wait for iframes to load.
        - Negative indexes are supported (-1 = last iframe).
        - If a target cannot be located in the current context, this walks
          back to parent frames and retries.
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        default_aliases = ("default content", "default", "main")
        frame_targets = []
        switch_to_default = False

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()
            right_l = right_v.lower()

            if "action" in mid_l and left_l == "switch iframe":
                continue

            if left_l == "index" and right_l in default_aliases:
                switch_to_default = True
                continue

            if mid_l not in ("iframe parameter", "frame parameter", "input parameter"):
                continue

            if left_l == "index":
                frame_targets.append(
                    {
                        "kind": "index",
                        "mid": mid_l if mid_l in ("iframe parameter", "frame parameter") else "iframe parameter",
                        "left": left_l,
                        "right": right_v,
                    }
                )
            elif mid_l in ("iframe parameter", "frame parameter"):
                frame_targets.append(
                    {
                        "kind": "selector",
                        "mid": mid_l,
                        "left": left_l,
                        "right": right_v,
                    }
                )

        if switch_to_default:
            sr.Set_Shared_Variables("playwright_frame", None)
            _save_current_playwright_frame(None)
            CommonUtil.ExecLog(sModuleInfo, "Exited all iframes and switched to default content", 1)
            if not frame_targets:
                return "passed"

        if not frame_targets:
            CommonUtil.ExecLog(sModuleInfo, "No iframe selector or index provided", 3)
            return "zeuz_failed"

        def _build_selector(target):
            tag_name = "frame" if target["mid"] == "frame parameter" else "iframe"
            left_l = target["left"]
            right_v = target["right"]
            if left_l == "tag":
                return tag_name, right_v
            if left_l == "xpath":
                expr = right_v if right_v.startswith("xpath=") else f"xpath={right_v}"
                return tag_name, expr
            return tag_name, f"{tag_name}[{left_l}='{right_v}']"

        async def _resolve_index(base, tag_name, idx_str):
            try:
                idx = int(idx_str)
            except Exception:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Invalid {tag_name} index '{idx_str}'",
                    3,
                )
                return None, "fatal"
            # Retry to wait for iframes to load (mirrors Selenium 5x2s loop).
            for _ in range(5):
                try:
                    count = await base.locator(tag_name).count()
                except Exception:
                    count = 0
                if count and -count <= idx < count:
                    break
                await asyncio.sleep(2)
            else:
                return None, "not_found"
            log_idx = idx
            if idx < 0:
                idx = count + idx
            CommonUtil.ExecLog(sModuleInfo, f"Iframe switched to index {log_idx}", 1)
            return base.frame_locator(tag_name).nth(idx), "passed"

        async def _resolve_selector(base, target):
            tag_name, selector = _build_selector(target)
            try:
                fl = base.frame_locator(selector)
                # Probe count; Playwright frame_locator does not auto-validate existence here.
                if await base.locator(selector).count() == 0:
                    return None, "not_found"
                CommonUtil.ExecLog(sModuleInfo, "Iframe switched using above Xpath", 1)
                return fl, "passed"
            except Exception:
                return None, "not_found"

        active_stack = []  # list of frame_locators resolved so far
        pending = frame_targets[:]
        unknown_parent_hops = 0
        max_unknown_parent_hops = len(frame_targets) + 5

        def _current_base():
            return active_stack[-1] if active_stack else current_page

        while pending:
            switched = False
            for idx, target in enumerate(pending):
                base = _current_base()
                tag_name = "frame" if target["mid"] == "frame parameter" else "iframe"
                if target["kind"] == "index":
                    fl, status = await _resolve_index(base, tag_name, target["right"])
                else:
                    fl, status = await _resolve_selector(base, target)

                if status == "fatal":
                    return "zeuz_failed"
                if status == "passed":
                    active_stack.append(fl)
                    pending.pop(idx)
                    switched = True
                    unknown_parent_hops = 0
                    break

            if switched:
                continue

            if active_stack:
                # Walk back to parent (mirrors Selenium switch_to.parent_frame()).
                active_stack.pop()
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "No matching frame in current context. Switched to parent frame and retrying",
                    2,
                )
                continue

            if switch_to_default:
                unresolved = [f"{t['left']}={t['right']}" for t in pending]
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Unable to resolve iframe/frame targets: {', '.join(unresolved)}",
                    3,
                )
                return "zeuz_failed"

            unknown_parent_hops += 1
            CommonUtil.ExecLog(
                sModuleInfo,
                "No matching frame in current context. Switched to parent frame and retrying",
                2,
            )
            if unknown_parent_hops > max_unknown_parent_hops:
                unresolved = [f"{t['left']}={t['right']}" for t in pending]
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Unable to resolve iframe/frame targets from current starting context: {', '.join(unresolved)}",
                    3,
                )
                return "zeuz_failed"

        frame_locator = active_stack[-1] if active_stack else None
        sr.Set_Shared_Variables("playwright_frame", frame_locator)
        _save_current_playwright_frame(frame_locator)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Alerts/Dialogs     #
#                       #
#########################

@logger
async def Handle_Browser_Alert(step_data):
    """
    Handle browser alerts/dialogs.

    Example 1 - Accept alert:
        Field               Sub Field           Value
        handle alert        action              accept
        handle alert        playwright action   handle alert

    Example 2 - Dismiss alert:
        Field               Sub Field           Value
        handle alert        action              dismiss
        handle alert        playwright action   handle alert

    Example 3 - Get text and accept:
        Field               Sub Field           Value
        handle alert        action              accept
        alert_text          save parameter      ignore
        handle alert        playwright action   handle alert

    Example 4 - Enter text in prompt:
        Field               Sub Field           Value
        handle alert        action              accept
        prompt text         input parameter     my response
        handle alert        playwright action   handle alert
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        action = "accept"
        prompt_text = None
        save_variable = None
        timeout = 5000

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if "action" in mid_l:
                action = right_v.lower()
                if action.startswith("get text") and "=" in action:
                    save_variable = right_v.split("=", 1)[1].strip()
                    action = "accept"
                elif action.startswith("send text") and "=" in action:
                    prompt_text = right_v.split("=", 1)[1].strip()
                    action = "accept"
            elif mid_l == "input parameter":
                if left_l in ("prompt text", "text", "send text"):
                    prompt_text = right_v
            elif mid_l == "save parameter":
                save_variable = left.strip()
            elif mid_l == "optional parameter":
                if left_l in ("timeout", "wait"):
                    timeout = int(float(right_v) * 1000)

        try:
            dialog = await current_page.wait_for_event("dialog", timeout=timeout)
        except PlaywrightTimeoutError:
            CommonUtil.ExecLog(sModuleInfo, "No alert appeared within timeout", 3)
            return "zeuz_failed"

        message = dialog.message
        if action in ("accept", "pass", "ok", "yes"):
            if prompt_text:
                await dialog.accept(prompt_text)
            else:
                await dialog.accept()
        elif action in ("dismiss", "reject", "fail", "cancel", "no"):
            await dialog.dismiss()
        else:
            await dialog.accept()

        # Save text if requested
        if save_variable and message:
            sr.Set_Shared_Variables(save_variable, message)

        CommonUtil.ExecLog(
            sModuleInfo,
            f"Alert handled ({action}): {message or 'N/A'}",
            1
        )
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Drag & Drop        #
#                       #
#########################

@logger
async def drag_and_drop(step_data):
    """
    Drag and drop a source element to a destination element.

    Example 1 - Basic (src + dst):
        Field               Sub Field               Value
        id                  src element parameter   drag-item
        id                  dst element parameter   drop-zone
        drag and drop       playwright action       drag and drop

    Example 2 - With destination offset and hold delay:
        Field               Sub Field               Value
        id                  src element parameter   drag-item
        id                  dst element parameter   drop-zone
        destination offset  optional parameter      20,0
        delay               optional parameter      0.5
        drag and drop       playwright action       drag and drop

    Supported param prefixes (matches Selenium): src / source / dst / destination.
    Supported scopes: element parameter, parent parameter, child parameter, sibling parameter.

    destination offset: "x,y" as percentage of half the destination's size from its center
                       (e.g. "20,0" = 20% right of center).
    delay: seconds to pause between click-and-hold and release (mouse-step pattern).
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        source = []
        destination = []
        destination_offset = None
        delay = None
        param_dict = {
            "elementparameter": "element parameter",
            "parentparameter": "parent parameter",
            "siblingparameter": "sibling parameter",
            "childparameter": "child parameter",
            "optionalparameter": "optional parameter",
        }

        for left, mid, right in step_data:
            mid_clean = mid.strip().lower()
            left_l = left.strip().lower()
            if mid_clean.startswith("src") or mid_clean.startswith("source"):
                key = mid_clean.replace("src", "", 1) if mid_clean.startswith("src") else mid_clean.replace("source", "", 1)
                key = key.replace(" ", "")
                if key in param_dict:
                    source.append((left, param_dict[key], right))
            elif mid_clean.startswith("dst") or mid_clean.startswith("destination"):
                key = mid_clean.replace("dst", "", 1) if mid_clean.startswith("dst") else mid_clean.replace("destination", "", 1)
                key = key.replace(" ", "")
                if key in param_dict:
                    destination.append((left, param_dict[key], right))
            elif left_l in ("wait", "allow disable", "allow hidden") and mid_clean == "option":
                source.append((left, mid, right))
                destination.append((left, mid, right))
            elif left_l == "destination offset" and mid_clean == "optional parameter":
                destination_offset = right.strip()
            elif left_l == "delay" and mid_clean == "optional parameter":
                try:
                    delay = float(right.strip())
                except ValueError:
                    delay = None

        if not source:
            CommonUtil.ExecLog(
                sModuleInfo,
                'Please provide source element with "src element parameter", "src parent parameter" etc. Example:\n'
                "(id, src element parameter, file)",
                3,
            )
            return "zeuz_failed"

        if not destination:
            CommonUtil.ExecLog(
                sModuleInfo,
                'Please provide Destination element with "dst element parameter", "dst parent parameter" etc. Example:\n'
                "(id, dst element parameter, table)",
                3,
            )
            return "zeuz_failed"

        action_timeout = _get_action_timeout(source)
        target_timeout = _get_action_timeout(destination)
        source_locator = await PlaywrightLocator.Get_Element(
            source,
            current_page,
        )
        if source_locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Source Element is not found", 3)
            return "zeuz_failed"

        target_locator = await PlaywrightLocator.Get_Element(
            destination,
            current_page,
        )
        if target_locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Destination Element is not found", 3)
            return "zeuz_failed"

        if destination_offset or delay is not None:
            # Manual mouse-step path so we can apply offset and/or a hold delay.
            await source_locator.scroll_into_view_if_needed(timeout=action_timeout)
            src_box = await source_locator.bounding_box(timeout=action_timeout)
            await target_locator.scroll_into_view_if_needed(timeout=target_timeout)
            tgt_box = await target_locator.bounding_box(timeout=target_timeout)
            if not src_box or not tgt_box:
                CommonUtil.ExecLog(sModuleInfo, "Could not compute bounding box for drag and drop", 3)
                return "zeuz_failed"

            src_x = src_box["x"] + src_box["width"] / 2
            src_y = src_box["y"] + src_box["height"] / 2

            tgt_center_x = tgt_box["x"] + tgt_box["width"] / 2
            tgt_center_y = tgt_box["y"] + tgt_box["height"] / 2
            if destination_offset:
                try:
                    parts = destination_offset.replace(" ", "").split(",")
                    pct_x = float(parts[0])
                    pct_y = float(parts[1])
                    tgt_x = tgt_center_x + (tgt_box["width"] / 2.0) * (pct_x / 100.0)
                    tgt_y = tgt_center_y + (tgt_box["height"] / 2.0) * (pct_y / 100.0)
                except (ValueError, IndexError):
                    tgt_x, tgt_y = tgt_center_x, tgt_center_y
            else:
                tgt_x, tgt_y = tgt_center_x, tgt_center_y

            await current_page.mouse.move(src_x, src_y)
            await current_page.mouse.down()
            # Intermediate steps help frameworks that listen for dragover events.
            await current_page.mouse.move(tgt_x, tgt_y, steps=10)
            if delay is not None:
                await asyncio.sleep(delay)
            await current_page.mouse.up()
        else:
            await source_locator.drag_to(target_locator, timeout=action_timeout)

        CommonUtil.ExecLog(sModuleInfo, "Drag and drop completed from source to destination", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Screenshot         #
#                       #
#########################

@logger
async def take_screenshot_playwright(step_data):
    """
    Take a screenshot.

    Example 1 - Full page:
        Field               Sub Field           Value
        fullscreen          optional parameter  true
        screenshot_path     save parameter      ignore
        take screenshot     playwright action   take screenshot

    Example 2 - Element only:
        Field               Sub Field           Value
        id                  element parameter   my-element
        take screenshot     playwright action   take screenshot
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        full_page = False
        save_variable = None
        custom_path = None
        has_element = False
        image_type = "jpeg"
        image_quality = CommonUtil.PLAYWRIGHT_AUTO_SCREENSHOT_QUALITY

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if _is_action_mid(mid_l) and left_l == "take screenshot web":
                if not _is_placeholder(right_v, "take screenshot web"):
                    custom_path = time.strftime(right_v) + ".png"
                    image_type = "png"
            elif mid_l == "element parameter":
                has_element = True
            elif mid_l == "optional parameter":
                if left_l in ("fullscreen", "full page", "fullpage"):
                    full_page = right_v.lower() in ("true", "yes", "1")
                elif left_l == "path":
                    custom_path = right_v
                elif left_l in ("format", "type", "image type"):
                    image_type = right_v.lower().replace("jpg", "jpeg")
                elif left_l == "quality":
                    image_quality = int(right_v)
            elif mid_l == "save parameter":
                save_variable = left.strip()

        if image_type not in ("jpeg", "png"):
            CommonUtil.ExecLog(sModuleInfo, f"Unsupported screenshot format '{image_type}'. Use jpeg or png.", 3)
            return "zeuz_failed"

        # Generate filename
        if custom_path:
            screenshot_path = custom_path
            suffix = Path(screenshot_path).suffix.lower()
            if suffix in (".png", ".jpg", ".jpeg"):
                image_type = "png" if suffix == ".png" else "jpeg"
            else:
                screenshot_path = str(Path(screenshot_path).with_suffix(".jpg" if image_type == "jpeg" else ".png"))
        else:
            timestamp = time.strftime("%Y_%m_%d_%H-%M-%S")
            screenshot_path = str(Path(_screenshot_folder()) / f"screenshot_{timestamp}.{'jpg' if image_type == 'jpeg' else 'png'}")

        if not Path(screenshot_path).is_absolute():
            screenshot_path = str(Path(_screenshot_folder()) / screenshot_path)

        screenshot_options = {"path": screenshot_path, "type": image_type}
        if image_type == "jpeg":
            screenshot_options["quality"] = image_quality

        # Take screenshot
        if has_element:
            screenshot_options["timeout"] = _get_action_timeout(step_data)
            locator = await PlaywrightLocator.Get_Element(
                step_data,
                current_page,
            )
            if locator == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
                return "zeuz_failed"
            await locator.screenshot(**screenshot_options)
        else:
            screenshot_options["full_page"] = full_page
            await current_page.screenshot(**screenshot_options)

        if save_variable:
            sr.Set_Shared_Variables(save_variable, screenshot_path)
        sr.Set_Shared_Variables("zeuz_screenshot", Path(screenshot_path).name)

        CommonUtil.ExecLog(sModuleInfo, f"Screenshot saved: {screenshot_path}", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    JavaScript         #
#                       #
#########################

@logger
async def execute_javascript(step_data):
    """
    Execute JavaScript code in the browser.

    Example 1 - Page-level:
        Field               Sub Field           Value
        javascript          action              return document.title
        result              save parameter      ignore
        execute javascript  playwright action   execute javascript

    Example 2 - On element:
        Field               Sub Field           Value
        id                  element parameter   my-element
        javascript          action              el => el.scrollTop = 100
        execute javascript  playwright action   execute javascript
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        js_code = None
        save_variable = None
        has_element = False

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if _is_session_step_row(left, mid):
                continue
            if "javascript" in left_l or (_is_action_mid(mid_l) and left_l == "execute javascript"):
                js_code = right_v
            elif _is_element_parameter_mid(mid):
                has_element = True
            elif mid_l == "save parameter":
                save_variable = left.strip()
            elif mid_l == "optional parameter" and left_l == "variable":
                save_variable = right_v

        if not js_code:
            CommonUtil.ExecLog(sModuleInfo, "No JavaScript code provided", 3)
            return "zeuz_failed"

        action_timeout = _get_action_timeout(step_data)

        # Execute JS
        if has_element:
            locator = await PlaywrightLocator.Get_Element(
                step_data,
                current_page,
            )
            if locator == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
                return "zeuz_failed"
            if "$elem" in js_code:
                element_script = js_code.replace("$elem", "el")
                result = await locator.evaluate(f"el => {{ {element_script} }}", timeout=action_timeout)
            else:
                result = await locator.evaluate(js_code, timeout=action_timeout)
        else:
            if js_code.strip().startswith("return "):
                js_code = f"() => {{ {js_code} }}"
            result = await current_page.evaluate(js_code)

        if save_variable:
            sr.Set_Shared_Variables(save_variable, result)
            CommonUtil.ExecLog(sModuleInfo, f"JS result saved to '{save_variable}': {result}", 1)
        else:
            CommonUtil.ExecLog(sModuleInfo, f"JS executed. Result: {result}", 1)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    File Upload        #
#                       #
#########################

@logger
async def upload_file(step_data):
    """
    Upload a file via file input.

    Example:
        Field               Sub Field           Value
        id                  element parameter   file-input
        file path           input parameter     /path/to/file.pdf
        upload file         playwright action   upload file
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        file_path = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if _is_action_mid(mid_l) and left_l == "upload file" and not _is_placeholder(right_v, "upload file"):
                file_path = right_v
            elif mid_l == "input parameter":
                if left_l in ("file path", "filepath", "file", "path"):
                    file_path = right_v

        if not file_path:
            CommonUtil.ExecLog(sModuleInfo, "No file path provided", 3)
            return "zeuz_failed"

        # Check if file exists
        if not os.path.exists(file_path):
            # Check in attachments
            attachments = sr.Get_Shared_Variables("file_attachment")
            if attachments and file_path in attachments:
                file_path = attachments[file_path]
            else:
                CommonUtil.ExecLog(sModuleInfo, f"File not found: {file_path}", 3)
                return "zeuz_failed"

        action_timeout = _get_action_timeout(step_data)

        locator = await PlaywrightLocator.Get_Element(
            step_data,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        await locator.set_input_files(file_path, timeout=action_timeout)
        CommonUtil.ExecLog(sModuleInfo, f"File uploaded: {file_path}", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def copy_image_into_browser(data_set):
    """Copy a PNG/SVG image into the browser clipboard."""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page, context

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        image_path = ""
        variable_name = ""
        for left, mid, right in data_set:
            left_c = _compact(left)
            right_v = right.strip()
            if left_c == "imagefile":
                image_path = right_v if os.path.exists(right_v) else CommonUtil.path_parser(right_v)
            elif left_c == "imagevariable":
                if os.path.exists(right_v):
                    image_path = right_v
                else:
                    variable_name = right_v

        if not image_path and variable_name:
            image_path = sr.Get_Shared_Variables(variable_name)
        if not image_path:
            CommonUtil.ExecLog(sModuleInfo, "Must provide either 'image file' or 'image variable'", 3)
            return "zeuz_failed"
        if not os.path.exists(image_path):
            CommonUtil.ExecLog(sModuleInfo, f"Image file not found: {image_path}", 3)
            return "zeuz_failed"

        image_l = image_path.lower()
        if image_l.endswith(".svg"):
            mime_type = "image/svg+xml"
        elif image_l.endswith(".png"):
            mime_type = "image/png"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unsupported file format. You can copy only PNG or SVG image.", 2)
            return "zeuz_failed"

        if context:
            try:
                parsed = urlparse(current_page.url)
                origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else None
                await context.grant_permissions(["clipboard-read", "clipboard-write"], origin=origin)
            except Exception:
                pass

        image_b64 = base64.b64encode(Path(image_path).read_bytes()).decode("utf-8")
        success = await current_page.evaluate("""async ({ imageB64, mimeType }) => {
            const byteCharacters = atob(imageB64);
            const byteArrays = [];
            for (let offset = 0; offset < byteCharacters.length; offset += 512) {
                const slice = byteCharacters.slice(offset, offset + 512);
                const byteNumbers = new Array(slice.length);
                for (let i = 0; i < slice.length; i++) byteNumbers[i] = slice.charCodeAt(i);
                byteArrays.push(new Uint8Array(byteNumbers));
            }
            const blob = new Blob(byteArrays, { type: mimeType });
            window.focus();
            await navigator.clipboard.write([new ClipboardItem({ [mimeType]: blob })]);
            return true;
        }""", {"imageB64": image_b64, "mimeType": mime_type})
        if success:
            CommonUtil.ExecLog(sModuleInfo, f"Image copied to clipboard: {image_path}", 1)
            return "passed"
        CommonUtil.ExecLog(sModuleInfo, f"Failed to copy image to clipboard: {image_path}", 3)
        return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Window Resize      #
#                       #
#########################

@logger
async def resize_window(step_data):
    """
    Resize the browser viewport.

    Example:
        Field               Sub Field           Value
        width               input parameter     1280
        height              input parameter     720
        resize window       playwright action   resize window
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        width = None
        height = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l in ("input parameter", "element parameter"):
                if left_l == "width":
                    # Handle percentage
                    if "%" in right_v:
                        # Get current size first
                        current_size = current_page.viewport_size
                        pct = int(right_v.replace("%", "")) / 100
                        width = int(current_size["width"] * pct)
                    else:
                        width = int(right_v)
                elif left_l == "height":
                    if "%" in right_v:
                        current_size = current_page.viewport_size
                        pct = int(right_v.replace("%", "")) / 100
                        height = int(current_size["height"] * pct)
                    else:
                        height = int(right_v)

        if width is None or height is None:
            current_size = current_page.viewport_size
            width = width or current_size["width"]
            height = height or current_size["height"]

        await current_page.set_viewport_size({"width": width, "height": height})
        CommonUtil.ExecLog(sModuleInfo, f"Window resized to {width}x{height}", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Wait Actions       #
#                       #
#########################

@logger
async def Wait_For_Element(step_data):
    """
    Wait for an element to appear/disappear/attach/detach.

    Example 1 - Wait for visible with explicit timeout (seconds):
        Field               Sub Field           Value
        id                  element parameter   results
        wait for element    playwright action   30

    Example 2 - Wait for hidden:
        Field               Sub Field           Value
        id                  element parameter   loading-spinner
        wait                input parameter     hidden
        wait for element    playwright action   wait for element

    Example 3 - Timeout via optional parameter:
        Field               Sub Field           Value
        id                  element parameter   results
        timeout             optional parameter  30
        state               input parameter     visible
        wait for element    playwright action   wait for element

    States: attached, detached, visible, hidden (default: visible)
    Timeout: seconds (defaults to element_wait shared variable, or 10s)
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        inferred_state = "visible"
        explicit_state = None
        timeout_sec = None
        allow_hidden = False

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "input parameter":
                if left_l in ("wait", "state"):
                    explicit_state = right_v.lower()
            elif mid_l == "optional parameter" and left_l == "timeout":
                try:
                    timeout_sec = float(right_v)
                except ValueError:
                    pass
            elif mid_l in ("optional parameter", "option") and left_l == "allow hidden":
                allow_hidden = right_v.lower() in ("yes", "true", "ok", "enable", "enabled", "1")
            elif "action" in mid_l and left_l in ("wait", "wait disable", "wait for element"):
                if left_l == "wait disable":
                    inferred_state = "hidden"
                # Selenium-style: action value carries the timeout in seconds.
                try:
                    timeout_sec = float(right_v)
                except ValueError:
                    pass

        state = explicit_state or inferred_state
        if explicit_state is None and allow_hidden:
            if inferred_state == "visible":
                state = "attached"
            elif inferred_state == "hidden":
                state = "detached"

        if timeout_sec is None:
            default_wait = sr.Get_Shared_Variables("element_wait")
            if default_wait not in failed_tag_list:
                try:
                    timeout_sec = float(default_wait)
                except (TypeError, ValueError):
                    timeout_sec = 10
            else:
                timeout_sec = 10

        timeout_ms = int(timeout_sec * 1000)

        try:
            locator = await PlaywrightLocator.Get_Element(step_data, current_page)
            if locator == "zeuz_failed":
                return "zeuz_failed"
            await locator.wait_for(state=state, timeout=timeout_ms)
            CommonUtil.ExecLog(sModuleInfo, f"Element reached state: {state}", 1)
            return "passed"
        except PlaywrightTimeoutError:
            CommonUtil.ExecLog(sModuleInfo, f"Timeout waiting for element to be {state}", 3)
            return "zeuz_failed"

    except PlaywrightTimeoutError:
        CommonUtil.ExecLog(sModuleInfo, "Timeout waiting for element", 3)
        return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#  Playwright-Specific  #
#                       #
#########################

@logger
async def Start_Tracing(step_data):
    """
    Start Playwright trace recording.

    Example:
        Field               Sub Field           Value
        screenshots         optional parameter  true
        snapshots           optional parameter  true
        start tracing       playwright action   start tracing
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global context

    try:
        if context is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser context open", 3)
            return "zeuz_failed"

        screenshots = True
        snapshots = True
        sources = False

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip().lower()

            if mid_l == "optional parameter":
                if left_l == "screenshots":
                    screenshots = right_v in ("true", "yes", "1")
                elif left_l == "snapshots":
                    snapshots = right_v in ("true", "yes", "1")
                elif left_l == "sources":
                    sources = right_v in ("true", "yes", "1")

        await context.tracing.start(
            screenshots=screenshots,
            snapshots=snapshots,
            sources=sources
        )
        CommonUtil.ExecLog(sModuleInfo, "Tracing started", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def Stop_Tracing(step_data):
    """
    Stop tracing and save trace file.

    Example:
        Field               Sub Field           Value
        path                input parameter     trace.zip
        stop tracing        playwright action   stop tracing
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global context

    try:
        if context is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser context open", 3)
            return "zeuz_failed"

        trace_path = "trace.zip"

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "input parameter" and left_l == "path":
                trace_path = right_v

        await context.tracing.stop(path=trace_path)
        CommonUtil.ExecLog(sModuleInfo, f"Trace saved to: {trace_path}", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def capture_network_log(step_data):
    """Capture request/response metadata and save filtered network logs."""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page, current_page_id, network_log_details

    def parse_status_codes(code_str):
        result = []
        for part in code_str.split(","):
            part = part.strip()
            if "-" in part:
                start, end = map(int, part.split("-"))
                result.extend(range(start, end + 1))
            elif part:
                result.append(int(part))
        return result

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        params = {
            "variable_name": None,
            "mode": None,
            "filter_domains": [],
            "status_filter": [],
            "method_filter": [],
            "include_body": False,
        }
        for left, mid, right in step_data:
            left_l = left.lower().strip()
            if left_l == "capture network log":
                params["mode"] = right.lower().strip()
            elif left_l == "save":
                params["variable_name"] = right.strip()
            elif left_l == "filter domain":
                params["filter_domains"] = [d.strip() for d in right.split(",")]
            elif left_l == "include status code":
                params["status_filter"] = parse_status_codes(right.strip())
            elif left_l == "include request method":
                params["method_filter"] = [m.strip().upper() for m in right.split(",")]
            elif left_l == "include response body":
                params["include_body"] = _truthy(right)

        session_key = current_page_id or "default"
        if params["mode"] == "start":
            requests = {}
            events = []

            async def on_request(request):
                requests[id(request)] = request

            async def on_response(response):
                request = response.request
                entry = {
                    "url": response.url,
                    "status": response.status,
                    "method": request.method,
                    "mimeType": response.headers.get("content-type", ""),
                    "type": request.resource_type,
                    "timestamp": time.time(),
                }
                if params["include_body"]:
                    try:
                        entry["body"] = await response.text()
                    except Exception:
                        entry["body"] = "Unavailable"
                events.append(entry)

            current_page.on("request", on_request)
            current_page.on("response", on_response)
            network_log_details[session_key] = {"events": events, "on_request": on_request, "on_response": on_response}
            CommonUtil.ExecLog(sModuleInfo, "Started collecting network logs...", 1)
            return "passed"

        if params["mode"] == "stop":
            state = network_log_details.pop(session_key, {"events": []})
            try:
                current_page.remove_listener("request", state.get("on_request"))
                current_page.remove_listener("response", state.get("on_response"))
            except Exception:
                pass

            excluded_ext = (".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".webp", ".map", ".txt")
            excluded_mime = ("image/", "font/", "text/css", "application/javascript", "text/javascript", "application/font-", "application/x-font-")
            api_logs = []
            for entry in state.get("events", []):
                url = entry.get("url", "")
                mime_type = entry.get("mimeType", "")
                if any(url.endswith(ext) for ext in excluded_ext) or any(mime_type.startswith(prefix) for prefix in excluded_mime):
                    continue
                if params["filter_domains"]:
                    domain = urlparse(url).netloc
                    if not any(d in domain for d in params["filter_domains"]):
                        continue
                if params["method_filter"] and entry.get("method", "").upper() not in params["method_filter"]:
                    continue
                if params["status_filter"] and entry.get("status") not in params["status_filter"]:
                    continue
                api_logs.append(entry)

            if params["variable_name"]:
                sr.Set_Shared_Variables(params["variable_name"], api_logs)
                CommonUtil.ExecLog(sModuleInfo, f"Saved {len(api_logs)} network events to '{params['variable_name']}'", 1)
            return "passed"

        CommonUtil.ExecLog(sModuleInfo, "Mode must be start or stop", 3)
        return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Could not collect network logs")


@logger
async def Intercept_Network(step_data):
    """
    Set up network request interception.

    Example:
        Field               Sub Field           Value
        url pattern         input parameter     **/api/**
        action              action              abort
        intercept network   playwright action   intercept network

    Actions: abort, continue, fulfill
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        url_pattern = "**/*"
        action = "continue"
        response_body = None
        response_status = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "input parameter":
                if left_l in ("url pattern", "pattern", "url"):
                    url_pattern = right_v
                elif left_l == "response body":
                    response_body = right_v
                elif left_l == "response status":
                    response_status = int(right_v)
            elif "action" in mid_l:
                action = right_v.lower()

        async def handle_route(route):
            if action == "abort":
                await route.abort()
            elif action == "fulfill":
                fulfill_options = {}
                if response_body:
                    fulfill_options["body"] = response_body
                if response_status:
                    fulfill_options["status"] = response_status
                await route.fulfill(**fulfill_options)
            else:
                await route.continue_()

        await current_page.route(url_pattern, handle_route)
        CommonUtil.ExecLog(sModuleInfo, f"Network interception set up for: {url_pattern}", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Table Operations   #
#                       #
#########################

@logger
async def Extract_Table_Data(step_data):
    """
    Extract data from an HTML table.

    Example:
        Field               Sub Field           Value
        id                  element parameter   data-table
        table_data          save parameter      ignore
        extract table data  playwright action   extract table data
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        save_variable = None
        row_filter = None
        col_filter = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if _is_action_mid(mid_l) and left_l == "extract table data" and not _is_placeholder(right_v, "extract table data"):
                save_variable = right_v
            elif mid_l == "save parameter":
                save_variable = left.strip()
            elif mid_l == "optional parameter":
                if left_l == "row":
                    row_filter = right_v
                elif left_l == "column":
                    col_filter = right_v

        action_timeout = _get_action_timeout(step_data)
        locator = await PlaywrightLocator.Get_Element(
            step_data,
            current_page,
        )
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Table element not found", 3)
            return "zeuz_failed"

        # Extract table data using JavaScript
        table_data = await locator.evaluate("""table => {
            const data = [];
            const rows = table.querySelectorAll('tr');
            rows.forEach(row => {
                const rowData = [];
                const cells = row.querySelectorAll('td, th');
                cells.forEach(cell => {
                    rowData.push(cell.textContent.trim());
                });
                if (rowData.length > 0) {
                    data.push(rowData);
                }
            });
            return data;
        }""", timeout=action_timeout)

        if row_filter and "," not in row_filter and "-" not in row_filter:
            try:
                table_data = [table_data[int(row_filter.replace(" ", ""))]]
            except Exception:
                table_data = eval("table_data[%s]" % row_filter.replace(" ", ""))
        if col_filter and "," not in col_filter and "-" not in col_filter:
            try:
                table_data = [[row[int(col_filter.replace(" ", ""))]] for row in table_data]
            except Exception:
                table_data = [eval("row[%s]" % col_filter.replace(" ", "")) for row in table_data]

        if save_variable:
            sr.Set_Shared_Variables(save_variable, table_data)
            CommonUtil.ExecLog(sModuleInfo, f"Table data saved to '{save_variable}' ({len(table_data)} rows)", 1)
        else:
            CommonUtil.ExecLog(sModuleInfo, f"Table data extracted: {len(table_data)} rows", 1)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
