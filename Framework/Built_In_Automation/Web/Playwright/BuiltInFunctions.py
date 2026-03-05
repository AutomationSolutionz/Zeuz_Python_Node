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
import sys
import os
import inspect
import time
import re
from pathlib import Path

from playwright.async_api import (
    async_playwright,
    Page,
    Browser,
    BrowserContext,
    Locator,
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError,
)

from Framework.Utilities import CommonUtil
from Framework.Utilities.decorators import logger
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list
from . import locator as PlaywrightLocator
from . import utils as PlaywrightUtils
from settings import ZEUZ_NODE_DOWNLOADS_DIR

def _get_frame_locator():
    """Helper function to get current frame locator from shared variables."""
    try:
        frame_locator = sr.Get_Shared_Variables("playwright_frame")
        if frame_locator in failed_tag_list:
            return None
        return frame_locator
    except:
        # Variable doesn't exist yet
        return None


def connect_selenium_to_playwright(port=9222):
    """Connect Selenium to Playwright browser via CDP"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        
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

# Playwright instances
playwright_instance = None
browser: Browser = None
context: BrowserContext = None
current_page: Page = None

# Multi-page/context support
playwright_details = {}  # {"page_id": {"page": Page, "context": Context, "browser": Browser}}
current_page_id = None

# Default settings
default_timeout = 30000  # 30 seconds
default_viewport = {"width": 1920, "height": 1080}


#########################
#                       #
#   Browser Management  #
#                       #
#########################

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

    Supported browsers: chrome, chromium, firefox, webkit, safari, edge
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global playwright_instance, browser, context, current_page
    global current_page_id, playwright_details, default_timeout

    try:
        # Parse parameters
        url = None
        browser_name = "chromium"
        headless = False
        viewport = default_viewport.copy()
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

            elif mid_l == "optional parameter":
                if left_l == "headless":
                    headless = right_v.lower() in ("true", "yes", "1")
                elif left_l == "resolution":
                    parts = right_v.replace("x", ",").split(",")
                    viewport = {"width": int(parts[0].strip()), "height": int(parts[1].strip())}
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
                elif left_l in ("driver id", "page id", "driver tag", "session"):
                    page_id = right_v    

            elif mid_l == "shared capability":
                # Handle Selenium-style capabilities where possible
                pass

        # Ensure Chrome for Testing is available
        chrome_binary_path, success = PlaywrightUtils.ensure_chromium_downloads(sModuleInfo)
        if not success:
            return "zeuz_failed"

        # Launch Playwright
        CommonUtil.ExecLog(sModuleInfo, f"Launching Playwright with {browser_name} browser", 1)
        playwright_instance = await async_playwright().start()

        # Browser launch options
        launch_options = {
            "headless": headless,
            "slow_mo": slow_mo,
            "devtools": devtools,
        }
        
        # Add remote debugging port for CDP connection
        all_args = args + ["--remote-debugging-port=9222"]
        if all_args:
            launch_options["args"] = all_args
        if downloads_path:
            launch_options["downloads_path"] = downloads_path
        
        # Use Chrome for Testing binary if available
        if chrome_binary_path and browser_name in ("chrome", "chromium"):
            launch_options["executable_path"] = chrome_binary_path
            CommonUtil.ExecLog(sModuleInfo, f"Using Chrome for Testing binary: {chrome_binary_path}", 1)

        # Select and launch browser
        if browser_name in ("chrome", "chromium"):
            browser = await playwright_instance.chromium.launch(**launch_options)
        elif browser_name == "firefox":
            browser = await playwright_instance.firefox.launch(**launch_options)
        elif browser_name in ("webkit", "safari"):
            browser = await playwright_instance.webkit.launch(**launch_options)
        elif browser_name in ("edge", "msedge", "microsoft edge"):
            launch_options["channel"] = "msedge"
            browser = await playwright_instance.chromium.launch(**launch_options)
        elif browser_name == "chrome-beta":
            launch_options["channel"] = "chrome-beta"
            browser = await playwright_instance.chromium.launch(**launch_options)
        else:
            CommonUtil.ExecLog(sModuleInfo, f"Unknown browser '{browser_name}', using chromium", 2)
            browser = await playwright_instance.chromium.launch(**launch_options)

        # Context options
        context_options = {"viewport": viewport}
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

        # Create context and page
        context = await browser.new_context(**context_options)
        context.set_default_timeout(timeout)
        current_page = await context.new_page()
        current_page_id = page_id

        # Store in details
        playwright_details[page_id] = {
            "page": current_page,
            "context": context,
            "browser": browser,
            "playwright": playwright_instance,
        }

        # Navigate if URL provided
        if url:
            await current_page.goto(url, wait_until="domcontentloaded")
            CommonUtil.ExecLog(sModuleInfo, f"Navigated to: {url}", 1)

        # Save to shared variables for compatibility
        sr.Set_Shared_Variables("playwright_page", current_page)
        sr.Set_Shared_Variables("playwright_context", context)
        sr.Set_Shared_Variables("playwright_browser", browser)
        sr.Set_Shared_Variables("element_wait", timeout / 1000)  # In seconds
        
        # Set screenshot variables for CommonUtil.TakeScreenShot()
        CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())

        # Connect Selenium to Playwright via CDP
        selenium_driver = connect_selenium_to_playwright(port=9222)

        # Create browser session
        from Framework.Built_In_Automation.Web.utils import create_browser_session
        
        create_browser_session(
            session_name=page_id,
            selenium_driver=selenium_driver,
            playwright_page=current_page,
            playwright_browser=browser,
            playwright_context=context,
            playwright_frame=None
        )
        CommonUtil.ExecLog(sModuleInfo, f"Created browser session: {page_id}", 5)

        CommonUtil.ExecLog(sModuleInfo, f"Browser opened successfully (page_id: {page_id})", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def Go_To_Link(step_data):
    """
    Navigate to a URL.

    Example:
        Field               Sub Field           Value
        go to link          input parameter     https://example.com
        wait until          optional parameter  networkidle
        go to link          playwright action   go to link

    wait until options: load, domcontentloaded, networkidle, commit
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open. Opening browser with default settings.", 2)
            result = await Open_Browser(step_data)
            if result == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Failed to open browser automatically", 3)
                return "zeuz_failed"

        url = None
        wait_until = "domcontentloaded"
        timeout = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if left_l in ("go to link", "url", "link"):
                    url = right_v
            elif mid_l == "optional parameter":
                if left_l in ("wait until", "wait_until", "waituntil", "wait time"):
                    wait_until = right_v.lower()
                elif left_l == "timeout":
                    timeout = int(float(right_v) * 1000)

        if not url:
            CommonUtil.ExecLog(sModuleInfo, "No URL provided", 3)
            return "zeuz_failed"

        goto_options = {"wait_until": wait_until}
        if timeout:
            goto_options["timeout"] = timeout

        await current_page.goto(url, **goto_options)
        
        # Reset frame context when navigating to a new URL
        sr.Set_Shared_Variables("playwright_frame", None)
        
        CommonUtil.ExecLog(sModuleInfo, f"Navigated to: {url}", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def Tear_Down_Playwright(step_data=None):
    """
    Close browser and clean up Playwright resources.

    Example:
        Field               Sub Field           Value
        tear down           playwright action   tear down
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global playwright_instance, browser, context, current_page
    global playwright_details, current_page_id

    try:
        # Close all tracked pages/contexts
        for page_id, details in playwright_details.items():
            try:
                if details.get("page"):
                    await details["page"].close()
                if details.get("context"):
                    await details["context"].close()
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

        CommonUtil.ExecLog(sModuleInfo, "Browser closed successfully", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Switch_Browser(step_data):
    """
    Switch between multiple browser instances/pages.

    Example:
        Field               Sub Field           Value
        driver id           input parameter     my_page_id
        switch browser      playwright action   switch browser
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page, current_page_id, context

    try:
        target_id = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "input parameter":
                if left_l in ("driver id", "page id", "driver tag"):
                    target_id = right_v

        if not target_id:
            CommonUtil.ExecLog(sModuleInfo, "No driver/page ID provided", 3)
            return "zeuz_failed"

        if target_id not in playwright_details:
            CommonUtil.ExecLog(sModuleInfo, f"Page ID '{target_id}' not found", 3)
            return "zeuz_failed"

        details = playwright_details[target_id]
        current_page = details["page"]
        context = details["context"]
        current_page_id = target_id

        current_page.bring_to_front()

        sr.Set_Shared_Variables("playwright_page", current_page)
        sr.Set_Shared_Variables("playwright_context", context)
        
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
async def Click_Element(step_data):
    """
    Click an element.

    Example 1 - Basic:
        Field               Sub Field           Value
        id                  element parameter   submit-btn
        click               playwright action   click

    Example 2 - With options:
        Field               Sub Field           Value
        id                  element parameter   submit-btn
        use js              optional parameter  true
        offset              optional parameter  10,5
        click               playwright action   click

    Example 3 - Double click:
        Field               Sub Field           Value
        id                  element parameter   item
        double click        playwright action   double click

    Example 4 - Right click:
        Field               Sub Field           Value
        id                  element parameter   item
        right click         playwright action   right click
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        # Parse options
        use_js = False
        offset = None
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

            if mid_l == "optional parameter":
                if left_l == "use js":
                    use_js = right_v.lower() in ("true", "yes", "1")
                elif left_l == "offset":
                    parts = right_v.split(",")
                    offset = {"x": float(parts[0].strip()), "y": float(parts[1].strip())}
                elif left_l == "click count":
                    click_count = int(right_v)
                elif left_l == "modifier":
                    modifiers.append(right_v)
                elif left_l == "delay":
                    delay = int(float(right_v) * 1000)
                elif left_l == "timeout":
                    timeout = int(float(right_v) * 1000)

            elif mid_l == "action":
                if "double" in left_l:
                    double_click = True
                elif "right" in left_l:
                    right_click = True

        # Get element
        locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # Build click options
        click_options = {}
        if use_js:
            click_options["force"] = True
        if offset:
            click_options["position"] = offset
        if modifiers:
            click_options["modifiers"] = modifiers
        if delay:
            click_options["delay"] = delay
        if timeout:
            click_options["timeout"] = timeout
        if click_count > 1:
            click_options["click_count"] = click_count

        # Perform click
        if double_click:
            await locator.dblclick(**{k: v for k, v in click_options.items() if k != "click_count"})
            CommonUtil.ExecLog(sModuleInfo, "Double click performed", 1)
        elif right_click:
            click_options["button"] = "right"
            await locator.click(**click_options)
            CommonUtil.ExecLog(sModuleInfo, "Right click performed", 1)
        else:
            await locator.click(**click_options)
            CommonUtil.ExecLog(sModuleInfo, "Click performed", 1)

        return "passed"

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
        if mid.strip().lower() == "action":
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
        if mid.strip().lower() == "action":
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

        locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        hover_options = {}
        if use_js:
            hover_options["force"] = True
        if offset:
            hover_options["position"] = offset
        if timeout:
            hover_options["timeout"] = timeout

        await locator.hover(**hover_options)
        CommonUtil.ExecLog(sModuleInfo, "Hover performed", 1)
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

    Example 2 - With options:
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

            if mid_l == "action":
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

        locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # Enter text based on options
        if use_js:
            # Use JavaScript to set value directly
            await locator.evaluate(f"el => {{ el.value = `{text_value}`; }}")
            # Trigger events
            await locator.dispatch_event("input")
            await locator.dispatch_event("change")
            CommonUtil.ExecLog(sModuleInfo, f"Text entered via JS: {text_value[:50]}{'...' if len(text_value) > 50 else ''}", 1)
        elif clear:
            # fill() clears and sets value - recommended approach
            fill_options = {}
            if timeout:
                fill_options["timeout"] = timeout
            await locator.fill(text_value, **fill_options)
            CommonUtil.ExecLog(sModuleInfo, f"Text filled: {text_value[:50]}{'...' if len(text_value) > 50 else ''}", 1)
        else:
            # type() appends to existing value
            type_options = {}
            if delay > 0:
                type_options["delay"] = int(delay * 1000)
            if timeout:
                type_options["timeout"] = timeout
            await locator.type(text_value, **type_options)
            CommonUtil.ExecLog(sModuleInfo, f"Text typed: {text_value[:50]}{'...' if len(text_value) > 50 else ''}", 1)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


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

            if mid_l == "action":
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
            "ALT": "Alt",
            "SHIFT": "Shift",
            "ENTER": "Enter",
            "RETURN": "Enter",
            "TAB": "Tab",
            "ESC": "Escape",
            "ESCAPE": "Escape",
            "BACKSPACE": "Backspace",
            "DELETE": "Delete",
            "SPACE": " ",
            "UP": "ArrowUp",
            "DOWN": "ArrowDown",
            "LEFT": "ArrowLeft",
            "RIGHT": "ArrowRight",
            "HOME": "Home",
            "END": "End",
            "PAGEUP": "PageUp",
            "PAGEDOWN": "PageDown",
        }

        if keystroke_type == "keys":
            # Convert key names
            key = keystroke_value.upper()
            if "+" in key:
                # Key combination like Ctrl+A
                parts = key.split("+")
                converted = [key_map.get(p.strip(), p.strip().capitalize()) for p in parts]
                key = "+".join(converted)
            else:
                key = key_map.get(key, keystroke_value)

            if has_element:
                locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
                if locator == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
                    return "zeuz_failed"

                for _ in range(key_count):
                    await locator.press(key)
                    if delay > 0:
                        time.sleep(delay)
            else:
                for _ in range(key_count):
                    await current_page.keyboard.press(key)
                    if delay > 0:
                        time.sleep(delay)

            CommonUtil.ExecLog(sModuleInfo, f"Pressed key: {key} ({key_count} times)", 1)

        elif keystroke_type == "chars":
            type_options = {}
            if delay > 0:
                type_options["delay"] = int(delay * 1000)

            if has_element:
                locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
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
        timeout = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "action":
                if left_l.startswith("**"):
                    partial_match = True
                    case_insensitive = True
                elif left_l.startswith("*"):
                    partial_match = True
                elif "partial" in left_l:
                    partial_match = True
                expected_text = right_v

            elif mid_l == "optional parameter":
                if left_l == "timeout":
                    timeout = int(float(right_v) * 1000)

        locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # Get actual text
        actual_text = await locator.text_content() or ""

        # Compare
        match = False
        if case_insensitive:
            if partial_match:
                match = expected_text.lower() in actual_text.lower()
            else:
                match = expected_text.lower() == actual_text.lower()
        else:
            if partial_match:
                match = expected_text in actual_text
            else:
                match = expected_text == actual_text

        if match:
            CommonUtil.ExecLog(sModuleInfo, f"Text validation passed: '{expected_text}'", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Text validation failed.\nExpected: '{expected_text}'\nActual: '{actual_text}'",
                3
            )
            return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def if_element_exists(step_data):
    """
    Check if an element exists on the page.

    Example:
        Field               Sub Field           Value
        id                  element parameter   optional-element
        if element exists   playwright action   if element exists

    Returns "passed" if element exists, "zeuz_failed" if not.
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        timeout = 1000  # Short timeout for existence check
        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "optional parameter" and left_l == "timeout":
                timeout = int(float(right_v) * 1000)

        locator = await PlaywrightLocator.Get_Element(step_data, current_page, element_wait=timeout/1000, frame_locator=_get_frame_locator())

        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element does not exist", 1)
            return "zeuz_failed"

        try:
            count = await locator.count()
            if count > 0:
                CommonUtil.ExecLog(sModuleInfo, f"Element exists ({count} found)", 1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Element does not exist", 1)
                return "zeuz_failed"
        except Exception:
            CommonUtil.ExecLog(sModuleInfo, "Element does not exist", 1)
            return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def Save_Attribute(step_data):
    """
    Save an element's attribute value to a shared variable.

    Example:
        Field               Sub Field           Value
        id                  element parameter   my-link
        href                input parameter     attribute_name
        my_variable         save parameter      ignore
        save attribute      playwright action   save attribute

    Special attribute names:
        - text: Get text content
        - innertext: Get inner text
        - innerhtml: Get inner HTML
        - outerhtml: Get outer HTML
        - value: Get input value
        - checked: Get checkbox state
        - selected: Get select option state
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        attribute_name = None
        save_variable = None
        save_attribute = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l in ["input parameter", "element parameter"]:
                attribute_name = left.strip()  # Keep original case
            elif mid_l == "save parameter":
                save_variable = right_v
                save_attribute = left_l

        if not attribute_name:
            CommonUtil.ExecLog(sModuleInfo, "No attribute name specified", 3)
            return "zeuz_failed"

        if not save_variable:
            CommonUtil.ExecLog(sModuleInfo, "No save variable specified", 3)
            return "zeuz_failed"

        locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # Get attribute value based on name
        attr_lower = attribute_name.lower()
        if attr_lower == "text":
            value = await locator.text_content()
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
            value = await locator.get_attribute(save_attribute)

        sr.Set_Shared_Variables(save_variable, value)
        CommonUtil.ExecLog(sModuleInfo, f"Saved '{save_attribute}' = '{value}' to '{save_variable}'", 1)
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

        save_variable = None
        for left, mid, right in step_data:
            if mid.strip().lower() == "save parameter":
                save_variable = left.strip()

        locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # Gather element info
        info = {
            "tag_name": await locator.evaluate("el => el.tagName"),
            "text": await locator.text_content(),
            "inner_html": await locator.inner_html(),
            "visible": await locator.is_visible(),
            "enabled": await locator.is_enabled(),
            "bounding_box": await locator.bounding_box(),
        }

        # Get all attributes
        attributes = await locator.evaluate("""el => {
            const attrs = {};
            for (const attr of el.attributes) {
                attrs[attr.name] = attr.value;
            }
            return attrs;
        }""")
        info["attributes"] = attributes

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
def Navigate(step_data):
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

            if mid_l == "action":
                direction = right_v
            elif mid_l == "optional parameter":
                if left_l == "timeout":
                    timeout = int(float(right.strip()) * 1000)

        nav_options = {}
        if timeout:
            nav_options["timeout"] = timeout

        if direction in ("back", "go back"):
            current_page.go_back(**nav_options)
            CommonUtil.ExecLog(sModuleInfo, "Navigated back", 1)
        elif direction in ("forward", "go forward"):
            current_page.go_forward(**nav_options)
            CommonUtil.ExecLog(sModuleInfo, "Navigated forward", 1)
        elif direction in ("refresh", "reload"):
            current_page.reload(**nav_options)
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

        save_variable = None
        for left, mid, right in step_data:
            if mid.strip().lower() == "save parameter":
                save_variable = left.strip()

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
def Scroll(step_data):
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

            if mid_l == "input parameter":
                if left_l == "direction":
                    direction = right_v.lower()
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

        current_page.mouse.wheel(delta_x, delta_y)
        CommonUtil.ExecLog(sModuleInfo, f"Scrolled {direction} by {pixels}px", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
async def scroll_to_element(step_data):
    """
    Scroll an element into view.

    Example:
        Field               Sub Field           Value
        id                  element parameter   footer
        use js              optional parameter  false
        scroll to element   playwright action   scroll to element
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        use_js = False
        align_to_top = True

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "optional parameter":
                if left_l == "use js":
                    use_js = right_v.lower() in ("true", "yes", "1")
                elif left_l == "align to top":
                    align_to_top = right_v.lower() in ("true", "yes", "1")

        locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        if use_js:
            await locator.evaluate(f"el => el.scrollIntoView({str(align_to_top).lower()})")
        else:
            await locator.scroll_into_view_if_needed()

        CommonUtil.ExecLog(sModuleInfo, "Scrolled element into view", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


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

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "action":
                if "deselect" in left_l:
                    is_deselect = True

                if "by value" in left_l or "byvalue" in left_l:
                    select_type = "value"
                elif "by index" in left_l or "byindex" in left_l:
                    select_type = "index"
                elif "by label" in left_l or "by text" in left_l:
                    select_type = "label"

                select_value = right_v

        if not select_value:
            CommonUtil.ExecLog(sModuleInfo, "No selection value provided", 3)
            return "zeuz_failed"

        locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # Build selection option
        if select_type == "value":
            option = {"value": select_value}
        elif select_type == "index":
            option = {"index": int(select_value)}
        else:  # label
            option = {"label": select_value}

        if is_deselect:
            # Playwright doesn't have direct deselect, use JavaScript
            await locator.evaluate(f"""el => {{
                for (const opt of el.options) {{
                    if (opt.{'value' if select_type == 'value' else 'text'} === '{select_value}') {{
                        opt.selected = false;
                    }}
                }}
                el.dispatchEvent(new Event('change'));
            }}""")
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

            if mid_l == "action":
                if "uncheck" in left_l or "uncheck" in right_v:
                    action = "uncheck"
                else:
                    action = "check"
            elif mid_l == "optional parameter":
                if left_l == "use js":
                    use_js = right_v in ("true", "yes", "1")

        locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        options = {}
        if use_js:
            options["force"] = True

        if action == "check":
            await locator.check(**options)
            CommonUtil.ExecLog(sModuleInfo, "Checkbox checked", 1)
        else:
            await locator.uncheck(**options)
            CommonUtil.ExecLog(sModuleInfo, "Checkbox unchecked", 1)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Windows/Tabs       #
#                       #
#########################

@logger
def switch_window_or_tab(step_data):
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
                page_title = page.title()
                if partial_match:
                    if switch_by_title.lower() in page_title.lower():
                        current_page = page
                        page.bring_to_front()
                        sr.Set_Shared_Variables("playwright_page", current_page)
                        CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())
                        CommonUtil.ExecLog(sModuleInfo, f"Switched to tab: {page_title}", 1)
                        return "passed"
                else:
                    if switch_by_title.lower() == page_title.lower():
                        current_page = page
                        page.bring_to_front()
                        sr.Set_Shared_Variables("playwright_page", current_page)
                        CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())
                        CommonUtil.ExecLog(sModuleInfo, f"Switched to tab: {page_title}", 1)
                        return "passed"

            CommonUtil.ExecLog(sModuleInfo, f"No tab found with title: {switch_by_title}", 3)
            return "zeuz_failed"

        elif switch_by_index is not None:
            if 0 <= switch_by_index < len(pages):
                current_page = pages[switch_by_index]
                current_page.bring_to_front()
                sr.Set_Shared_Variables("playwright_page", current_page)
                CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())
                CommonUtil.ExecLog(sModuleInfo, f"Switched to tab index {switch_by_index}: {current_page.title()}", 1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, f"Invalid tab index: {switch_by_index}", 3)
                return "zeuz_failed"

        CommonUtil.ExecLog(sModuleInfo, "No window title or index provided", 3)
        return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def open_new_tab(step_data):
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

        new_page = context.new_page()
        current_page = new_page
        sr.Set_Shared_Variables("playwright_page", current_page)
        CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())

        if url:
            new_page.goto(url)
            CommonUtil.ExecLog(sModuleInfo, f"Opened new tab with URL: {url}", 1)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Opened new blank tab", 1)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def close_tab(step_data):
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

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "input parameter":
                if left_l == "tab title":
                    tab_title = right_v
                elif left_l == "tab index":
                    tab_index = int(right_v)

        pages = context.pages

        if tab_title:
            for page in pages:
                if tab_title.lower() in page.title().lower():
                    page.close()
                    CommonUtil.ExecLog(sModuleInfo, f"Closed tab: {tab_title}", 1)
                    break
            else:
                CommonUtil.ExecLog(sModuleInfo, f"Tab not found: {tab_title}", 3)
                return "zeuz_failed"
        elif tab_index is not None:
            if 0 <= tab_index < len(pages):
                pages[tab_index].close()
                CommonUtil.ExecLog(sModuleInfo, f"Closed tab at index {tab_index}", 1)
            else:
                CommonUtil.ExecLog(sModuleInfo, f"Invalid tab index: {tab_index}", 3)
                return "zeuz_failed"
        else:
            # Close current tab
            if current_page:
                current_page.close()
                CommonUtil.ExecLog(sModuleInfo, "Closed current tab", 1)

        # Switch to remaining tab if available
        pages = context.pages
        if pages:
            current_page = pages[-1]
            sr.Set_Shared_Variables("playwright_page", current_page)
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

    Example 2 - Switch by index:
        Field               Sub Field           Value
        index               input parameter     0
        switch iframe       playwright action   switch iframe

    Example 3 - Switch to default/main:
        Field               Sub Field           Value
        index               input parameter     default content
        switch iframe       playwright action   switch iframe
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        iframe_index = None
        iframe_selector = None
        switch_to_default = False

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l in ("iframe parameter", "frame parameter"):
                iframe_selector = f"[{left}='{right_v}']" if left_l not in ("tag",) else right_v
            elif mid_l == "input parameter":
                if left_l == "index":
                    if right_v.lower() in ("default content", "default", "main"):
                        switch_to_default = True
                    else:
                        iframe_index = int(right_v)

        if switch_to_default:
            # In Playwright, we work with the main page directly
            # Store a flag or reset frame locator
            sr.Set_Shared_Variables("playwright_frame", None)
            CommonUtil.ExecLog(sModuleInfo, "Switched to default content", 1)
            return "passed"

        # Build frame locator
        if iframe_selector:
            frame_locator = current_page.frame_locator(iframe_selector)
        elif iframe_index is not None:
            frame_locator = current_page.frame_locator(f"iframe >> nth={iframe_index}")
        else:
            CommonUtil.ExecLog(sModuleInfo, "No iframe selector or index provided", 3)
            return "zeuz_failed"

        # Store frame locator for subsequent actions
        sr.Set_Shared_Variables("playwright_frame", frame_locator)
        CommonUtil.ExecLog(sModuleInfo, "Switched to iframe", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Alerts/Dialogs     #
#                       #
#########################

@logger
def Handle_Browser_Alert(step_data):
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

            if mid_l == "action":
                action = right_v.lower()
            elif mid_l == "input parameter":
                if left_l in ("prompt text", "text", "send text"):
                    prompt_text = right_v
            elif mid_l == "save parameter":
                save_variable = left.strip()
            elif mid_l == "optional parameter":
                if left_l in ("timeout", "wait"):
                    timeout = int(float(right_v) * 1000)

        # Set up dialog handler
        dialog_info = {"message": None, "handled": False}

        def handle_dialog(dialog):
            dialog_info["message"] = dialog.message
            dialog_info["type"] = dialog.type

            if action in ("accept", "ok", "yes"):
                if prompt_text:
                    dialog.accept(prompt_text)
                else:
                    dialog.accept()
            elif action in ("dismiss", "cancel", "no"):
                dialog.dismiss()
            else:
                dialog.accept()

            dialog_info["handled"] = True

        current_page.on("dialog", handle_dialog)

        # Wait for dialog
        try:
            current_page.wait_for_event("dialog", timeout=timeout)
        except PlaywrightTimeoutError:
            CommonUtil.ExecLog(sModuleInfo, "No alert appeared within timeout", 2)
            current_page.remove_listener("dialog", handle_dialog)
            return "passed"  # Not necessarily a failure

        # Remove listener
        current_page.remove_listener("dialog", handle_dialog)

        # Save text if requested
        if save_variable and dialog_info["message"]:
            sr.Set_Shared_Variables(save_variable, dialog_info["message"])

        CommonUtil.ExecLog(
            sModuleInfo,
            f"Alert handled ({action}): {dialog_info.get('message', 'N/A')}",
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
    Drag and drop an element to a target.

    Example:
        Field               Sub Field           Value
        id                  element parameter   drag-item
        id                  target parameter    drop-zone
        drag and drop       playwright action   drag and drop
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        # Separate source and target parameters
        source_param = None
        target_param = None

        for left, mid, right in step_data:
            mid_l = mid.strip().lower()
            if "element parameter" in mid_l:
                if mid_l.startswith("dst"):
                    target_param = (left, mid, right)
                elif mid_l.startswith("src"):
                    source_param = (left, mid, right)

        # Get source element
        source_locator = await PlaywrightLocator.Get_Element([source_param], current_page, frame_locator=_get_frame_locator())
        if source_locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Source element not found", 3)
            return "zeuz_failed"

        # Get target element
        target_locator = await PlaywrightLocator.Get_Element([target_param], current_page, frame_locator=_get_frame_locator())
        if target_locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Target element not found", 3)
            return "zeuz_failed"

        # Perform drag and drop
        await source_locator.drag_to(target_locator)
        CommonUtil.ExecLog(sModuleInfo, "Drag and drop completed", 1)
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

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "element parameter":
                has_element = True
            elif mid_l == "optional parameter":
                if left_l in ("fullscreen", "full page", "fullpage"):
                    full_page = right_v.lower() in ("true", "yes", "1")
                elif left_l == "path":
                    custom_path = right_v
            elif mid_l == "save parameter":
                save_variable = left.strip()

        # Generate filename
        if custom_path:
            screenshot_path = custom_path
        else:
            timestamp = time.strftime("%Y_%m_%d_%H-%M-%S")
            screenshot_path = f"screenshot_{timestamp}.png"

        # Take screenshot
        if has_element:
            locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
            if locator == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
                return "zeuz_failed"
            await locator.screenshot(path=screenshot_path)
        else:
            await current_page.screenshot(path=screenshot_path, full_page=full_page)

        if save_variable:
            sr.Set_Shared_Variables(save_variable, screenshot_path)

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

            if mid_l == "action":
                js_code = right
            elif mid_l == "element parameter":
                has_element = True
            elif mid_l == "save parameter":
                save_variable = left.strip()

        if not js_code:
            CommonUtil.ExecLog(sModuleInfo, "No JavaScript code provided", 3)
            return "zeuz_failed"

        # Execute JS
        if has_element:
            locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
            if locator == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
                return "zeuz_failed"
            result = await locator.evaluate(js_code)
        else:
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

            if mid_l == "input parameter":
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

        locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        await locator.set_input_files(file_path)
        CommonUtil.ExecLog(sModuleInfo, f"File uploaded: {file_path}", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#    Window Resize      #
#                       #
#########################

@logger
def resize_window(step_data):
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

            if mid_l == "input parameter":
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

        current_page.set_viewport_size({"width": width, "height": height})
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
    Wait for an element to appear/disappear.

    Example 1 - Wait for visible:
        Field               Sub Field           Value
        id                  element parameter   loading-spinner
        wait                input parameter     hidden
        wait for element    playwright action   wait for element

    Example 2 - Wait with timeout:
        Field               Sub Field           Value
        id                  element parameter   results
        timeout             optional parameter  30
        wait for element    playwright action   wait for element

    States: attached, detached, visible, hidden
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        if current_page is None:
            CommonUtil.ExecLog(sModuleInfo, "No browser open", 3)
            return "zeuz_failed"

        state = "visible"
        timeout = None

        for left, mid, right in step_data:
            left_l = left.strip().lower()
            mid_l = mid.strip().lower()
            right_v = right.strip()

            if mid_l == "input parameter":
                if left_l in ("wait", "state"):
                    state = right_v.lower()
            elif left_l == "wait for element":
                timeout = int(right_v)

        if timeout:
            await asyncio.sleep(timeout)

        locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())

        if locator == "zeuz_failed":
            # For hidden/detached states, element not found is actually success
            if state in ("hidden", "detached"):
                CommonUtil.ExecLog(sModuleInfo, f"Element already {state}", 1)
                return "passed"
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # wait_options = {"state": state}
        # if timeout:
        #     wait_options["timeout"] = timeout

        # locator.wait_for(**wait_options)
        CommonUtil.ExecLog(sModuleInfo, f"Element reached state: {state}", 1)
        return "passed"

    except PlaywrightTimeoutError:
        CommonUtil.ExecLog(sModuleInfo, f"Timeout waiting for element to be {state}", 3)
        return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#########################
#                       #
#  Playwright-Specific  #
#                       #
#########################

@logger
def Start_Tracing(step_data):
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

        context.tracing.start(
            screenshots=screenshots,
            snapshots=snapshots,
            sources=sources
        )
        CommonUtil.ExecLog(sModuleInfo, "Tracing started", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Stop_Tracing(step_data):
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

        context.tracing.stop(path=trace_path)
        CommonUtil.ExecLog(sModuleInfo, f"Trace saved to: {trace_path}", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Intercept_Network(step_data):
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
            elif mid_l == "action":
                action = right_v.lower()

        def handle_route(route):
            if action == "abort":
                route.abort()
            elif action == "fulfill":
                fulfill_options = {}
                if response_body:
                    fulfill_options["body"] = response_body
                if response_status:
                    fulfill_options["status"] = response_status
                route.fulfill(**fulfill_options)
            else:
                route.continue_()

        current_page.route(url_pattern, handle_route)
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

            if mid_l == "save parameter":
                save_variable = left.strip()
            elif mid_l == "optional parameter":
                if left_l == "row":
                    row_filter = right_v
                elif left_l == "column":
                    col_filter = right_v

        locator = await PlaywrightLocator.Get_Element(step_data, current_page, frame_locator=_get_frame_locator())
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
        }""")

        if save_variable:
            sr.Set_Shared_Variables(save_variable, table_data)
            CommonUtil.ExecLog(sModuleInfo, f"Table data saved to '{save_variable}' ({len(table_data)} rows)", 1)
        else:
            CommonUtil.ExecLog(sModuleInfo, f"Table data extracted: {len(table_data)} rows", 1)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
