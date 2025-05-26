# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
"""
    Created on May 15, 2016

    @author: Built_In_Automation Solutionz Inc.
    Name: Built In Functions - Selenium
    Description: Sequential Actions for controlling Web Browsers - All main Web Browsers supported on Linux/Windows/Mac
"""

#########################
#                       #
#        Modules        #
#                       #
#########################
import platform
import sys, os, time, inspect, shutil, subprocess, json
import socket
import requests
import psutil
import inspect
import sys
import inspect
#import CommonUtil
from pathlib import Path
sys.path.append("..")
from selenium import webdriver
if "linux" in platform.system().lower():
    from xvfbwrapper import Xvfb
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.opera import OperaDriverManager
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, WebDriverException,\
    SessionNotCreatedException, TimeoutException, NoSuchFrameException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from playwright.sync_api import Locator
from playwright.sync_api import sync_playwright
import selenium

from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

from Framework.Utilities import CommonUtil, ConfigModule
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as Shared_Resources,
)
from Framework.Utilities.decorators import logger, deprecated
from Framework.Built_In_Automation.Shared_Resources import LocateElement
from Framework.Utilities.CommonUtil import (
    passed_tag_list,
    failed_tag_list,
    skipped_tag_list,
)
from Framework.AI.NLP import binary_classification
from settings import temp_ini_file

#########################
#                       #
#    Global Variables   #
#                       #
#########################

playwright_browser = None
playwright_page = None
MODULE_NAME = inspect.getmodulename(__file__)

temp_config = os.path.join(
    os.path.join(
        os.path.abspath(__file__).split("Framework")[0],
        os.path.join(
            "AutomationLog", ConfigModule.get_config_value("Advanced Options", "_file")
        ),
    )
)
temp_config = str(Path(os.path.abspath(__file__).split("Framework")[0])/"AutomationLog"/ConfigModule.get_config_value("Advanced Options", "_file"))
aiplugin_path = str(Path(os.path.abspath(__file__).split("Framework")[0])/"Apps"/"Web"/"aiplugin")
ai_recorder_path = str(Path(os.path.abspath(__file__).split("Framework")[0])/"Apps"/"Web"/"AI_Recorder_2"/"dist")
ai_recorder_public_path = str(Path(os.path.abspath(__file__).split("Framework")[0])/"Apps"/"Web"/"AI_Recorder_2"/"public")

# Disable WebdriverManager SSL verification.
os.environ['WDM_SSL_VERIFY'] = '0'

current_driver_id = None
selenium_driver = None
selenium_details = {}
default_x, default_y = 1920, 1080
vdisplay = None
initial_download_folder = None

browser_map = {
    "Microsoft Edge Chromium": 'microsoftedge',
    "Chrome": "chrome",
    "FireFox": "firefox",
    "Opera": "opera",
    "ChromeHeadless": "chrome",
    "FirefoxHeadless": "firefox",
    "EdgeChromiumHeadless": "microsoftedge",
    "Safari": "safari"
}
options_map = {
    "Microsoft Edge Chromium": "edge",
    "Chrome": "chrome",
    "FireFox": "firefox",
    "Opera": "opera",
    "ChromeHeadless": "chrome",
    "FirefoxHeadless": "firefox",
    "EdgeChromiumHeadless": "edge",
    "Safari": "safari"
}

from typing import Literal, TypedDict, Any, Union, NotRequired
Dataset = list[tuple[str, str, str]]
ReturnType = Literal["passed", "zeuz_failed"]

class DefaultChromiumArguments(TypedDict):
    add_argument: list[str]
    add_experimental_option: dict[str, Any]
    add_extension: list[str]
    add_encoded_extension: list[str]
    page_load_strategy: NotRequired[Literal["normal", "eager", "none"]]

class FirefoxArguments(TypedDict):
    add_argument: list[str]
    set_preference: dict[str, Any]

class SafariArguments(TypedDict):
    add_argument: list[str]

class BrowserOptions(TypedDict):
    capabilities: dict[str,Any]
    chrome: DefaultChromiumArguments
    edge: DefaultChromiumArguments
    firefox: FirefoxArguments
    safari: SafariArguments

from selenium.webdriver.common.options import ArgOptions

# JavaScript for collecting First Contentful Paint value.
JS_FCP = '''
return performance.getEntriesByName("first-contentful-paint")[0].startTime
'''

# JavaScript for collecting Largest Contentful Paint value.
JS_LCP = '''
var args = arguments;
const po = new PerformanceObserver(list => {
    const entries = list.getEntries();
    const entry = entries[entries.length - 1];
    // Process entry as the latest LCP candidate
    // LCP is accurate when the renderTime is available.
    // Try to avoid this being false by adding Timing-Allow-Origin headers!
    const accurateLCP = entry.renderTime ? true : false;
    // Use startTime as the LCP timestamp. It will be renderTime if available, or loadTime otherwise.
    const largestPaintTime = entry.startTime;
    // Send the LCP information for processing.

    console.log("[ZeuZ Node] Largest Contentful Paint: ", largestPaintTime);
    args[0](largestPaintTime);
});
po.observe({ type: 'largest-contentful-paint', buffered: true });
'''

# if Shared_Resources.Test_Shared_Variables('selenium_driver'): # Check if driver is already set in shared variables
#    selenium_driver = Shared_Resources.Get_Shared_Variables('selenium_driver') # Retreive appium driver

# Recall dependency, if not already set
dependency = None
if Shared_Resources.Test_Shared_Variables("dependency"):  # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables("dependency")  # Retreive appium driver
else:
    raise ValueError("No dependency set - Cannot run")

@logger
def get_driver():
    return selenium_driver
@logger
def find_exe_in_path(exe):
    """ Search the path for an executable """

    try:
        path = os.getenv("PATH")  # Linux/Windows path

        if ";" in path:  # Windows delimiter
            dirs = path.split(";")
        elif ":" in path:  # Linux delimiter
            dirs = path.split(":")
        else:
            return "zeuz_failed"

        for directory in dirs:  # Try each directory
            filename = os.path.join(directory, exe)  # Create full path
            if os.path.isfile(filename):  # If it exists, return it and stop
                return filename

        # No matches
        return "zeuz_failed"

    except Exception:
        errMsg = "Error searching PATH"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def find_appium():
    """ Do our very best to find the appium executable """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Expected locations
    appium_list = [
        "/usr/bin/appium",
        os.path.join(str(os.getenv("HOME")), ".linuxbrew/bin/appium"),
        os.path.join(str(os.getenv("ProgramFiles")), "APPIUM", "Appium.exe"),
        os.path.join(
            str(os.getenv("USERPROFILE")), "AppData", "Roaming", "npm", "appium.cmd"
        ),
        os.path.join(str(os.getenv("ProgramFiles(x86)")), "APPIUM", "Appium.exe"),
    ]  # getenv() must be wrapped in str(), so it doesn't fail on other platforms

    # Try to find the appium executable
    appium_binary = ""

    for binary in appium_list:
        if os.path.exists(binary):
            appium_binary = binary
            break

    # Try to find the appium executable in the PATH variable
    if appium_binary == "":  # Didn't find where appium was installed
        CommonUtil.ExecLog(sModuleInfo, "Searching PATH for appium", 0)
        for exe in ("appium", "appium.exe", "appium.bat", "appium.cmd"):
            result = find_exe_in_path(exe)  # Get path and search for executable with in
            if result != "zeuz_failed":
                appium_binary = result
                break

    # Verify if we have the binary location
    if appium_binary == "":  # Didn't find where appium was installed
        CommonUtil.ExecLog(
            sModuleInfo, "Appium not found. Trying to locate via which", 0
        )
        try:
            appium_binary = subprocess.check_output(
                "which appium", encoding="utf-8", shell=True
            ).strip()
        except:
            pass

        if appium_binary == "":  # Didn't find where appium was installed
            appium_binary = "appium"  # Default filename of appium, assume in the PATH
            CommonUtil.ExecLog(
                sModuleInfo, "Appium still not found. Assuming it's in the PATH.", 2
            )
        else:
            CommonUtil.ExecLog(sModuleInfo, "Found appium: %s" % appium_binary, 1)
    else:  # Found appium's path
        CommonUtil.ExecLog(sModuleInfo, "Found appium: %s" % appium_binary, 1)

    return appium_binary


@logger
def start_appium_server():
    """Starts the external Appium server.

    Returns appium_port on success.
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    appium_binary = find_appium()

    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    try:
        appium_port = 4723
        tries = 0
        while is_port_in_use(appium_port) and tries < 20:
            appium_port += 2

        if tries >= 20:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Failed to find a free port for running appium after 20 tries.",
                1,
            )
            return "zeuz_failed"

        try:
            appium_server = None
            if (
                sys.platform == "win32"
            ):  # We need to open appium in it's own command dos box on Windows
                cmd = (
                    'start "Appium Server" /wait /min cmd /c %s --allow-insecure chromedriver_autodownload -p %d'
                    % (appium_binary, appium_port)
                )  # Use start to execute and minimize, then cmd /c will remove the dos box when appium is killed
                appium_server = subprocess.Popen(
                    cmd, shell=True
                )  # Needs to run in a shell due to the execution command
            elif sys.platform == "darwin":
                appium_server = subprocess.Popen(
                    "%s --allow-insecure chromedriver_autodownload -p %s"
                    % (appium_binary, str(appium_port)),
                    shell=True,
                )
            elif sys.platform == "linux" or sys.platform == "linux2":
                appium_server = subprocess.Popen(
                    "%s --allow-insecure chromedriver_autodownload -p %s"
                    % (appium_binary, str(appium_port)),
                    shell=True,
                )
            else:
                try:

                    appium_binary_path = os.path.normpath(appium_binary)
                    appium_binary_path = os.path.abspath(
                        os.path.join(appium_binary_path, os.pardir)
                    )
                    env = {"PATH": str(appium_binary_path)}
                    appium_server = subprocess.Popen(
                        "%s --allow-insecure chromedriver_autodownload -p %s"
                        % (appium_binary, str(appium_port)),
                        shell=True,
                        env=env,
                    )
                except:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Couldn't launch appium server, please do it manually by typing 'appium &' in the terminal",
                        2,
                    )
        except Exception as returncode:  # Couldn't run server
            return CommonUtil.Exception_Handler(
                sys.exc_info(),
                None,
                "Couldn't start Appium server. May not be installed, or not in your PATH: %s"
                % returncode,
            )

        # Wait for server to startup and return
        CommonUtil.ExecLog(
            sModuleInfo,
            "Waiting for server to start on port %d: %s" % (appium_port, appium_binary),
            0,
        )
        maxtime = time.time() + 10  # Maximum time to wait for appium server
        while True:  # Dynamically wait for appium to start by polling it
            if time.time() > maxtime:
                break  # Give up if max time was hit
            try:  # If this works, then stop waiting for appium
                r = requests.get(
                    "http://localhost:%d/sessions" % appium_port
                )  # Poll appium server
                if r.status_code:
                    break
            except:
                time.sleep(0.1) # sleep for 0.1 sec before retrying.

        if appium_server:
            CommonUtil.ExecLog(sModuleInfo, "Server started", 1)
            return appium_port
        else:
            CommonUtil.ExecLog(sModuleInfo, "Server failed to start", 3)
            return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error starting Appium server"
        )


@logger
def Open_Electron_App(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    global selenium_details
    global current_driver_id

    try:
        desktop_app_path = ""
        driver_id = ""
        for left, _, right in data_set:
            left = left.replace(" ", "").replace("_", "").replace("-", "").lower()
            if "windows" in left and platform.system() == "Windows":
                desktop_app_path = right.strip()
            elif "mac" in left and platform.system() == "Darwin":
                desktop_app_path = right.strip()
            elif "linux" in left and platform.system() == "Linux":
                desktop_app_path = right.strip()
            elif left == "driverid":
                driver_id = right.strip()

        if not desktop_app_path:
            CommonUtil.ExecLog(sModuleInfo, "You did not provide an Electron app path for %s OS" % platform.system(), 3)
            return "zeuz_failed"

        if not driver_id:
            driver_id = "default"

        desktop_app_path = CommonUtil.path_parser(desktop_app_path)
        electron_chrome_path = ConfigModule.get_config_value("Selenium_driver_paths", "electron_chrome_path")
        if not electron_chrome_path:
            electron_chrome_path = ChromeDriverManager().install()

        try:
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            opts = Options()
            opts.binary_location = desktop_app_path
            selenium_driver = webdriver.Chrome(opts, Service())
            selenium_driver.implicitly_wait(0.5)
            CommonUtil.ExecLog(sModuleInfo, "Started Electron App", 1)
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())

        except Exception:
            return CommonUtil.Exception_Handler(sys.exc_info())

        if driver_id in selenium_details:
            pass    # we need to decide later based on the situation
        else:
            selenium_details[driver_id] = {"driver": selenium_driver}
        current_driver_id = driver_id
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())

@logger
def use_xvfb_or_headless(callback):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    if platform.system() == "Linux":
        try:
            global vdisplay
            vdisplay = Xvfb(width=1920, height=1080, colordepth=16)
            vdisplay.start()
        except:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Failed to initialize xvfb. "
                "Perhaps xvfb is not installed?\n"
                "For apt-get: `sudo apt-get install xvfb`\n"
                "For yum: `sudo yum install xvfb`.\n"
                "Falling back to headless mode.",
                2,
            )
            callback()
    else:
        callback()


def set_extension_variables():
    try:
        url = ConfigModule.get_config_value("Authentication", "server_address").strip()
        apiKey = ConfigModule.get_config_value("Authentication", "api-key").strip()
        jwtKey = CommonUtil.jwt_token.strip()
        metaData = {
            "testNo": CommonUtil.current_tc_no,
            "testName": CommonUtil.current_tc_name,
            "stepNo": CommonUtil.current_step_sequence,
            "stepName": CommonUtil.current_step_name,
            "url": url,
            "apiKey": apiKey,
            "jwtKey": jwtKey,
            "nodeId": Shared_Resources.Get_Shared_Variables('node_id'),
        }
        with open(Path(aiplugin_path) / "data.json", "w") as file:
            json.dump(metaData, file, indent=4)

    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Could not load inspector extension")

    try:
        with open(Path(ai_recorder_path) / "background" / "data.json", "w") as file:
            json.dump(metaData, file, indent=4)
        with open(Path(ai_recorder_public_path) / "background" / "data.json", "w") as file:
            json.dump(metaData, file, indent=4)

    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Could not load recorder extension")


def generate_options(browser: str, browser_options:BrowserOptions):
    """ Adds capabilities and options for Browser/WebDriver """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    chromium_condition = browser in ("android", "chrome", "chromeheadless", "microsoft edge chromium", "edgechromiumheadless")
    msg = ""
    if chromium_condition:
        b = "edge" if "edge" in browser else "chrome"
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.edge.options import Options as EdgeOptions
        options = ChromeOptions() if b == "chrome" else EdgeOptions()
        # from selenium.webdriver.chromium.options import ChromiumOptions
        # options = ChromiumOptions()
        if browser == "android":
            mobile_emulation = {"deviceName": "Pixel 2 XL"}
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        for argument in browser_options[b]["add_argument"]:
            options.add_argument(argument)
        for key, val in browser_options[b]["add_experimental_option"].items():
            options.add_experimental_option(key, val)
        for extension in browser_options[b]["add_extension"]:
            options.add_extension(extension)
        for extension in browser_options[b]["add_encoded_extension"]:
            options.add_encoded_extension(extension)
        if "page_load_strategy" in browser_options[b]:
            options.page_load_strategy = browser_options[b]["page_load_strategy"]
        if "debugger_address" in browser_options[b]:
            # When debugger_address is mentioned, the Service() object should be ignored by default
            # Users need to remove experimental options by setting it to {}
            options.debugger_address = browser_options[b]["debugger_address"]
            msg += f"Debugger address: {options.debugger_address}\n"
        msg += (
            f"Experimental_options: {json.dumps(options.experimental_options, indent=2)}\n"
            f"Extensions: {json.dumps(options.extensions, indent=2)}\n"
        )
    elif browser in ("firefox", "firefoxheadless"):
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        options = FirefoxOptions()
        for argument in browser_options["firefox"]["add_argument"]:
            options.add_argument(argument)
        for key, val in browser_options["firefox"]["set_preference"].items():
            options.set_preference(key, val)
        if "page_load_strategy" in browser_options["firefox"]:
            options.page_load_strategy = browser_options["firefox"]["page_load_strategy"]
        msg += (
            f"Preferences: {json.dumps(options.preferences, indent=2)}\n"
        )
    elif "safari" in browser:
        from selenium.webdriver.safari.options import Options as SafariOptions
        options = SafariOptions()
        for argument in browser_options["safari"]["add_argument"]:
            options.add_argument(argument)
        if "page_load_strategy" in browser_options["safari"]:
            options.page_load_strategy = browser_options["safari"]["page_load_strategy"]
    else:
        from selenium.webdriver.common.options import ArgOptions
        return ArgOptions()

    if "headless" in browser:
        def headless():
            arg = "--headless=new" if "chrome" in browser else "--headless"
            options.add_argument(arg)
        use_xvfb_or_headless(headless)

    for key, value in browser_options["capabilities"].items():
        options.set_capability(key, value)

    # On Debug run open inspector with credentials
    if (
        CommonUtil.debug_status and
        ConfigModule.get_config_value("Inspector", "ai_plugin").strip().lower() in ("true", "on", "enable", "yes", "on_debug") and
        browser in ("chrome", "microsoft edge chromium")
    ):
        set_extension_variables()
        options.add_argument(f"load-extension={aiplugin_path},{ai_recorder_path}")
        # This is for running extension on a http server to call a https request
        options.add_argument("--allow-running-insecure-content")

    msg += (
        f"Capabilities: {json.dumps(options.capabilities, indent=2)}\n" +
        f"Arguments: {json.dumps(options.arguments, indent=2)}\n" +
        f"Page load strategy: {options.page_load_strategy}\n"
    )
    CommonUtil.ExecLog(sModuleInfo, msg, 5)
    return options


@logger
def Open_Browser(browser, browser_options: BrowserOptions):
    """ Launch browser from options and service object """
    try:
        global selenium_driver
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        browser = browser.lower().strip()
        
        if browser == "ios":
            appium_port = start_appium_server()
            if appium_port == "zeuz_failed":
                return "zeuz_failed"

            capabilities = {
                "platformName": "iOS",
                "automationName": "XCUITest",
                "browserName": "Safari"
            }

            from appium import webdriver as appiumdriver
            from appium.options.android import UiAutomator2Options
            capabilities_options = UiAutomator2Options().load_capabilities(capabilities)
            selenium_driver = appiumdriver.Remote("http://localhost:%d" % appium_port, options=capabilities_options)
            return "passed"

        options = generate_options(browser, browser_options)
        
        if browser in ("android", "chrome", "chromeheadless"):
            from selenium.webdriver.chrome.service import Service
            service = Service()
            selenium_driver = webdriver.Chrome(service=service, options=options)

            import requests
            from playwright.sync_api import sync_playwright

            response = requests.get("http://localhost:9222/json/version")
            ws_url = response.json()["webSocketDebuggerUrl"]

            playwright = sync_playwright().start()
            pw_browser = playwright.chromium.connect_over_cdp(ws_url)
            context = pw_browser.contexts[0]
            page = context.pages[0]

            Shared_Resources.Set_Shared_Variables("playwright_browser", pw_browser)
            Shared_Resources.Set_Shared_Variables("playwright_context", context)
            Shared_Resources.Set_Shared_Variables("playwright_page", page)

        elif browser in ("microsoft edge chromium", "edgechromiumheadless"):
            from selenium.webdriver.edge.service import Service
            service = Service()
            selenium_driver = webdriver.Edge(service=service, options=options)

        elif browser in ("firefox", "firefoxheadless"):
            from selenium.webdriver.firefox.service import Service
            service = Service()
            selenium_driver = webdriver.Firefox(service=service, options=options)

        elif "safari" in browser:
            from selenium.webdriver.safari.service import Service
            service = Service()
            selenium_driver = webdriver.Safari(service=service, options=options)

        else:
            CommonUtil.ExecLog(sModuleInfo, f"You did not select a valid browser: {browser}", 3)
            return "zeuz_failed"

        CommonUtil.ExecLog(sModuleInfo, f"Started {browser} browser", 1)
        Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
        CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())



'''
@logger
def Open_Browser(browser, browser_options: BrowserOptions):
    """ Launch browser from options and service object """
    try:
        global selenium_driver
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        browser = browser.lower().strip()
        if browser == "ios":
            # Finds the appium binary and starts the server.
            appium_port = start_appium_server()

            if appium_port == "zeuz_failed":
                return "zeuz_failed"

            capabilities = {
                "platformName": "iOS",
                "automationName": "XCUITest",
                "browserName": "Safari"
            }

            from appium import webdriver as appiumdriver
            from appium.options.android import UiAutomator2Options
            capabilities_options = UiAutomator2Options().load_capabilities(capabilities)
            selenium_driver = appiumdriver.Remote("http://localhost:%d" % appium_port, options=capabilities_options)
            return "passed"

        options = generate_options(browser, browser_options)
        if browser in ("android", "chrome", "chromeheadless"):
            from selenium.webdriver.chrome.service import Service
            service = Service()
            selenium_driver = webdriver.Chrome(
                service=service,
                options=options,
            )

        elif browser in ("microsoft edge chromium", "edgechromiumheadless"):
            from selenium.webdriver.edge.service import Service
            service = Service()
            selenium_driver = webdriver.Edge(
                service=service,
                options=options,
            )

        elif browser in ("firefox", "firefoxheadless"):
            from selenium.webdriver.firefox.service import Service
            service = Service()
            selenium_driver = webdriver.Firefox(
                service=service,
                options=options,
            )

        elif "safari" in browser:
            from selenium.webdriver.safari.service import Service
            service = Service()
            selenium_driver = webdriver.Safari(
                service=service,
                options=options,
            )
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "You did not select a valid browser: %s" % browser, 3
            )
            return "zeuz_failed"

        CommonUtil.ExecLog(sModuleInfo, f"Started {browser} browser", 1)
        Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
        CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

'''
'''
@logger
def Go_To_Link_V2(step_data):
    from selenium.webdriver.chrome.options import Options

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    
    global dependency
    global selenium_driver
    global selenium_details
    global current_driver_id
    
    url = None
    driver_tag = "default"
    page_load_timeout_sec = 120
    options = Options()
    page_load_strategy = "normal"

    for left, _, right in step_data:
        left = left.strip().lower()
        if "add argument" == left:
            options.add_argument(right.strip())
            CommonUtil.ExecLog(sModuleInfo, "Added argument: " + right.strip(), 1)
        elif "add extension" == left:
            filepath = CommonUtil.path_parser(right.strip())
            options.add_extension(filepath)
            CommonUtil.ExecLog(sModuleInfo, "Added extension: " + filepath, 1)
        elif 'add experimental option' in left:
            options.add_experimental_option(eval(right.split(",",1)[0].strip()),eval(right.split(",",1)[1].strip()))
            CommonUtil.ExecLog(sModuleInfo, "Added experimental option: " + right.strip(), 1)
        elif "set capability" in left:
            options.set_capability(eval(right.split(",",1)[0].strip()),eval(right.split(",",1)[1].strip()))
            CommonUtil.ExecLog(sModuleInfo, "Added capability: " + right.strip(), 1)
        elif "go to link v2" == left:
            url = right.strip() if right.strip() != "" else None
        elif "driver tag" == left:
            driver_tag = right.strip()
        elif "wait for element" == left:
            Shared_Resources.Set_Shared_Variables("element_wait", float(right.strip()))
        elif "page load timeout" == left:
            page_load_timeout_sec = float(right.strip())
        elif "page load strategy" == left:
            page_load_strategy = right.strip()
            options.page_load_strategy = page_load_strategy


    if driver_tag in selenium_details.keys():
        selenium_driver = selenium_details[driver_tag]["driver"]
    else:
        if Shared_Resources.Test_Shared_Variables("dependency"):
            dependency = Shared_Resources.Get_Shared_Variables("dependency")
        else:
            raise ValueError("No dependency set - Cannot run")
        
        dependency_browser = dependency["Browser"].lower()
        if 'headless' in dependency_browser:
            options.add_argument("--headless")
            CommonUtil.ExecLog(sModuleInfo, "Added headless argument", 1)

        if "chrome" in dependency_browser:
            selenium_driver = webdriver.Chrome(options=options)
        elif "firefox" in dependency_browser:
            selenium_driver = webdriver.Firefox(options=options)
        
        selenium_driver.set_page_load_timeout(page_load_timeout_sec)
        selenium_details[driver_tag] = dict()
        selenium_details[driver_tag]["driver"] = selenium_driver
        current_driver_id = selenium_driver
        Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
        
        # Handle headless mode window maximize
        if '--headless' in options.arguments and '--start-maximized' in options.arguments:
            selenium_driver.set_window_size(default_x, default_y)

    if url:
        selenium_driver.get(url)

    selenium_driver.maximize_window()
    Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
    CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
    return "passed"
'''    

def parse_and_verify_datatype(left:str, right:str):
    val = CommonUtil.parse_value_into_object(right)
    if left == "addargument":
        if isinstance(val, list) and all(isinstance(item, str) for item in val):
            return val
        raise ValueError("Argument must be list of strings. Example: ['--ignore-ssl-errors', '--no-sandbox']")
    
    if left == "addextension": 
        if isinstance(val, list) and all(isinstance(item, str) for item in val):
            return val
        raise ValueError("Extensions must be list of strings. Example: ['path/to/ex1.crx', 'path/to/ex2.crx']")
    
    if left == "addencodedextension":
        if isinstance(val, list) and all(isinstance(item, str) for item in val):
            return val
        raise ValueError("Encoded_extenions must be list of strings. Example: ['ex1_encoded_str', 'ex2_encoded_str']")
    
    elif left == "addexperimentaloption":
        if isinstance(val, dict):
            return val
        raise ValueError('Experimental_option must be dictionary. Example: {"mobileEmulation":{"deviceName": "Pixel 2 XL"}}')

    elif left == "setpreference":
        if isinstance(val, dict):
            return val
        raise ValueError('Preference must be dictionary. Example: {"security.mixed_content.block_active_content": False}')


@logger
def Go_To_Link(dataset: Dataset) -> ReturnType:
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        window_size_X = None
        window_size_Y = None

        global initial_download_folder
        initial_download_folder = download_dir = ConfigModule.get_config_value("sectionOne", "initial_download_folder", temp_config)
        apps = "application/pdf;text/plain;application/text;text/xml;application/xml;application/xlsx;application/csv;application/zip"
        default_chromium_arguments = {
            "add_argument": [
                "--ignore-certificate-errors",
                "--ignore-ssl-errors",
                "--zeuz_pid_finder",
                "--remote-debugging-port=9222",     # Required for playright
                # "--no-sandbox"
            ],
            "add_experimental_option": {
                "prefs": {
                    # "profile.default_content_settings.popups": 0,
                    "download.default_directory": download_dir,
                    "download.prompt_for_download": False,
                    # "download.directory_upgrade": True,
                    # 'safebrowsing.enabled': 'false'
                }
            },
            "add_extension": [],
            "add_encoded_extension": [],
            # "page_load_strategy": "normal"
        }
        browser_options: BrowserOptions = {
            "capabilities": {
                "unhandledPromptBehavior": "ignore",
                # "goog:loggingPrefs": {"performance": "ALL"},
            },
            "chrome": default_chromium_arguments,
            "edge": default_chromium_arguments,
            "firefox": {
                "add_argument": [],
                "set_preference": {
                    "browser.download.folderList": 2,
                    "browser.download.manager.showWhenStarting": False,
                    "browser.download.dir": download_dir,
                    "browser.helperApps.neverAsk.saveToDisk": apps,
                    "browser.download.useDownloadDir": True,
                    "browser.download.manager.closeWhenDone": True,
                    "security.mixed_content.block_active_content": False,
                }
            },
            "safari": {
                "add_argument": [],
            }
        } # type: ignore
        # Open browser and create driver if user has not already done so
        global dependency
        global selenium_driver
        global selenium_details
        global current_driver_id
        if Shared_Resources.Test_Shared_Variables("dependency"):
            dependency = Shared_Resources.Get_Shared_Variables("dependency")
        else:
            raise ValueError("No dependency set - Cannot run")

        page_load_timeout_sec = 120
        web_link = None     # None is for Open_Empty_Browser
        if dependency["Browser"] in options_map:
            browser = options_map[dependency["Browser"]]
        else:
            browser = None
        driver_id = ""
        for left, mid, right in dataset:
            left = left.replace(" ", "").replace("_", "").replace("-", "").lower()
            if left == "gotolink":
                web_link = right.strip()
            elif left == "driverid":
                driver_id = right.strip()
            elif left in ("waittimetoappearelement", "waitforelement"):
                Shared_Resources.Set_Shared_Variables("element_wait", float(right.strip()))
            elif left == "waittimetopageload":
                page_load_timeout_sec = int(right.strip())
            elif left == "resolution":
                resolution = right.split(",")
                window_size_X = int(resolution[0])
                window_size_Y = int(resolution[1])

            # Capabilities are WebDriver attribute common across different browser
            elif mid.strip().lower() == "shared capability":
                browser_options["capabilities"] = CommonUtil.parse_value_into_object(right)
            # Options are browser specific.
            elif (
                browser is not None and (
                    mid.strip().lower() == "chromium option" and
                    browser in ("chrome", "edge") or 
                    browser == mid.split(" ")[0].strip().lower()
                )
            ):
                if left == "addargument":
                    browser_options[browser]["add_argument"] = parse_and_verify_datatype(left, right)
                elif left == "addexperimentaloption":
                    browser_options[browser]["add_experimental_option"] = parse_and_verify_datatype(left, right)
                elif left == "addextension":
                    browser_options[browser]["add_extension"] = parse_and_verify_datatype(left, right)
                elif left == "addencodedextension":
                    browser_options[browser]["add_encoded_extension"] = parse_and_verify_datatype(left, right)
                elif left == "setpreference":
                    browser_options[browser]["set_preference"] = parse_and_verify_datatype(left, right)
                elif left == "pageloadstrategy":
                    browser_options[browser]["page_load_strategy"] = right.strip()
                elif left == "debuggeraddress":
                    browser_options[browser]["debugger_address"] = right.strip()

        if not driver_id:
            if len(selenium_details.keys()) == 0:
                driver_id = "default"
            elif current_driver_id is not None:
                driver_id = current_driver_id
            else:
                driver_id = list(selenium_details.keys())[0]

        if driver_id not in selenium_details or selenium_details[driver_id]["driver"].capabilities["browserName"].strip().lower() != browser_map[dependency["Browser"]]:
            if driver_id in selenium_details and selenium_details[driver_id]["driver"].capabilities["browserName"].strip().lower() != browser_map[dependency["Browser"]]:
                Tear_Down_Selenium()    # If dependency is changed then teardown and relaunch selenium driver
            CommonUtil.ExecLog(sModuleInfo, "Browser not previously opened, doing so now", 1)
            
            if Open_Browser(dependency["Browser"], browser_options) == "zeuz_failed":
                return "zeuz_failed"

            if not window_size_X and not window_size_Y:
                selenium_driver.maximize_window()
            else:
                selenium_driver.set_window_size(window_size_X, window_size_Y)

            selenium_details[driver_id] = {"driver": Shared_Resources.Get_Shared_Variables("selenium_driver")}

        else:
            selenium_driver = selenium_details[driver_id]["driver"]
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
        current_driver_id = driver_id
    except Exception:
        ErrorMessage = "failed to open browser"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)

    # Set timeout
    selenium_driver.set_page_load_timeout(page_load_timeout_sec)

    # Open URL in browser
    try:
        if web_link is not None:
            try:
                selenium_driver.get(web_link)
            except TimeoutException as e:
                CommonUtil.ExecLog(sModuleInfo, "Maximum page load time reached. Loading and proceeding", 2)

            selenium_driver.implicitly_wait(0.5)  # Wait for page to load
            CommonUtil.ExecLog(sModuleInfo, "Successfully opened your link with driver_id='%s': %s" % (driver_id, web_link), 1)
        
    except WebDriverException as e:
        browser = selenium_driver.capabilities["browserName"].strip().lower()
        if (browser in ("chrome", "edge") and e.msg.lower().startswith("chrome not reachable")) or (browser == "firefox" and e.msg.lower().startswith("tried to run command without establishing a connection")):
            CommonUtil.ExecLog(sModuleInfo, "Browser not found. trying to restart the browser", 2)
            # If the browser is closed but selenium instance is on, relaunch selenium_driver
            if Shared_Resources.Test_Shared_Variables("dependency"):
                dependency = Shared_Resources.Get_Shared_Variables("dependency")
            result = Open_Browser(dependency["Browser"], browser_options)
        else:
            result = "zeuz_failed"

        if result == "zeuz_failed":
            ErrorMessage = "failed to open your link with driver_id='%s: %s" % (driver_id, web_link)
            return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)
        try:
            selenium_details[driver_id] = {"driver": Shared_Resources.Get_Shared_Variables("selenium_driver")}
            selenium_driver.get(web_link)
            selenium_driver.implicitly_wait(0.5)
            CommonUtil.ExecLog(sModuleInfo, "Successfully opened your link with driver_id='%s': %s" % (driver_id, web_link), 1)
        except Exception:
            ErrorMessage = "failed to open your link: %s" % (web_link)
            return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)
    except Exception:
        ErrorMessage = "failed to open your link: %s" % (web_link)
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)

    return "passed"


@logger
def Handle_Browser_Alert(step_data):
    # accepts browser alert
    """
    wait           optional parameter  5.0
    handle alert   selenium action     get text = my_variable
    handle alert   selenium action     send text = my text to send to alert
    handle alert   selenium action     accept, pass, yes, ok (any of these would work)
    handle alert   selenium action     reject, fail, no, cancel (any of these would work)
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    wait = 5.0
    choice, choice_lower = "", ""
    try:
        for left, mid, right in step_data:
            left = left.lower()
            if "handle alert" in left:
                choice = right
                choice_lower = right.strip().lower()
            elif "wait" in left:
                wait = float(right.strip())

    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Failed to parse data", 3)
        return "zeuz_failed"

    try:
        CommonUtil.ExecLog("", "Waiting %s seconds max for the alert box to appear" % str(wait), 1)
        WebDriverWait(selenium_driver, wait).until(EC.alert_is_present())
        time.sleep(2)
    except TimeoutException:
        CommonUtil.ExecLog(sModuleInfo, "Waited %s seconds but no alert box appeared" % str(wait), 3)
        return "zeuz_failed"

    try:
        if choice_lower in ("accept", "pass", "yes", "ok"):
            Alert(selenium_driver).accept()
            CommonUtil.ExecLog(sModuleInfo, "Browser alert accepted", 1)
            return "passed"

        elif choice_lower in ("reject", "decline", "dismiss", "fail", "no", "cancel"):
            Alert(selenium_driver).dismiss()
            CommonUtil.ExecLog(sModuleInfo, "Browser alert rejected", 1)
            return "passed"

        elif choice_lower.replace(" ", "").replace("_", "").startswith("gettext"):
            alert_text = Alert(selenium_driver).text
            Alert(selenium_driver).accept()
            variable_name = (choice.split("="))[1].strip()
            return Shared_Resources.Set_Shared_Variables(variable_name, alert_text)

        elif choice_lower.replace(" ", "").replace("_", "").startswith("sendtext"):
            text_to_send = (choice.split("="))[1].strip()
            Alert(selenium_driver).send_keys(text_to_send)
            Alert(selenium_driver).accept()
            return "passed"

        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Wrong Step Data. The following are valid data --\n" +
                "1. (handle alert, selenium action, ok)" +
                "2. (handle alert, selenium action, cancel)" +
                "3. (handle alert, selenium action, get text = var_name)" +
                "4. (handle alert, selenium action, send text = some text)",
                3,
            )
            return "zeuz_failed"

    except Exception:
        ErrorMessage = "Failed to handle alert"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)

@logger
def save_screenshot(driver, path):
    """
    Take the screenshot of the whole web page
    :param driver: selenium driver
    :param path: where to save the screenshot
    :return: None
    """
    # Ref: https://stackoverflow.com/a/52572919
    import time

    original_size = driver.get_window_size()
    required_width = driver.execute_script(
        "return document.body.parentNode.scrollWidth"
    )
    required_height = driver.execute_script(
        "return document.body.parentNode.scrollHeight"
    )
    driver.set_window_size(required_width, required_height)
    time.sleep(2)
    # driver.save_screenshot(path)  # has scrollbar
    driver.find_element("xpath","//body").screenshot(path)  # avoids scrollbar
    time.sleep(2)
    driver.set_window_size(original_size["width"], original_size["height"])


@logger
def take_screenshot_selenium(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        filename_format = "%Y_%m_%d_%H-%M-%S"
        fullscreen = False

        for left, mid, right in data_set:
            if "take screenshot web" in left:
                if "default" not in right:
                    filename_format = right.strip()
            if "fullscreen" in left:
                fullscreen = right.lower().strip() == "true"

        screenshot_folder = ConfigModule.get_config_value(
            "sectionOne", "screen_capture_folder", temp_config
        )
        filename = time.strftime(filename_format) + ".png"
        screenshot_path = str(Path(screenshot_folder) / Path(filename))

        if fullscreen:
            save_screenshot(selenium_driver, screenshot_path)
        else:
            selenium_driver.save_screenshot(screenshot_path)

        # Save the screenshot's name into a variable
        Shared_Resources.Set_Shared_Variables("zeuz_screenshot", filename)
    except Exception:
        errMsg = "Failed to take screenshot"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

def Change_Attribute_Value(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        change_value = ""
        attribute_name = ""
        global selenium_driver
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"
        for left, mid, right in step_data:
            mid = mid.strip().lower()
            left = left.strip().lower()
            if "input parameter" in mid:
                attribute_name = left
                change_value = right

        selenium_driver.execute_script(f"arguments[0].{attribute_name} = `{change_value}`;", Element)
        CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of the attribute to: %s" % change_value, 1)
        return "passed"
    except Exception:
        errMsg = "Could not find your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

@logger
def capture_network_log(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        global selenium_driver

        def process_browser_log_entry(entry):
            response = json.loads(entry["message"])["message"]
            return response

        variable_name = None
        mode = None
        for left, _, right in step_data:
            if left.lower().strip() == "capture network log":
                mode = right.lower().strip()
            if left.lower().strip() == "save":
                variable_name = right.lower().strip()
        if not mode or ( mode == 'stop' and variable_name == None):
            CommonUtil.ExecLog(sModuleInfo, "Wrong data set provided.", 3)
            return "zeuz_failed"

        if mode == 'start':
            selenium_driver.get_log("performance")
            CommonUtil.ExecLog(sModuleInfo, "Started collecting network logs", 1    )
        if mode == 'stop':
            browser_log = selenium_driver.get_log("performance")
            events = [process_browser_log_entry(entry) for entry in browser_log]
            Shared_Resources.Set_Shared_Variables(variable_name, events)
            return "passed"
    except Exception:
        errMsg = "Could not collect network logs. Make sure logging is enabled at browser startup"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

@logger
def Enter_Text_In_Text_Box(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        delay = 0
        text_value = ""
        use_js = False
        clear = True
        global selenium_driver
        use_playwright = False
        
        # Check if Playwright should be used
        for left, mid, right in step_data:
            if left.strip().lower() == "driver" and right.strip().lower() in ("playwright"):
                use_playwright = True
                break

        if use_playwright:
            
            page = Shared_Resources.Get_Shared_Variables("playwright_page")
                
            # Extract values from step_data
            for left, mid, right in step_data:
                mid = mid.strip().lower()
                left = left.strip().lower()
                if mid == "action":
                    text_value = right
                elif left == "delay":
                    delay = float(right.strip())
                elif left == "clear":
                    clear = False if right.strip().lower() in ("no", "false") else True

            # Locate the element using Playwright
            Element = LocateElement.Get_Element(step_data, page)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                return "zeuz_failed"
            
            if isinstance(Element, list):
                if len(Element) > 0:
                    Element = Element[0]  # Take the first item
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Element is an empty list.", 3)
                    return "zeuz_failed"

            if not isinstance(Element, (str, Locator)):
                CommonUtil.ExecLog(sModuleInfo, f"Unsupported element type: {type(Element)}", 3)
                return "zeuz_failed"

            # Prepare the locator
            locator = Element if isinstance(Element, Locator) else page.locator(Element)

            if clear:
                locator.fill("")

            if delay == 0:
                locator.fill(text_value)
            else:
                for c in text_value:
                    locator.type(c, delay=delay * 1000)
            
            CommonUtil.ExecLog(sModuleInfo, "Successfully set the value in Playwright to: %s" % text_value, 1)
            return "passed"
        
        # Default to Selenium if Playwright is not used
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"
        
        # Process other parameters (delay, clear, use js) in step_data
        for left, mid, right in step_data:
            mid = mid.strip().lower()
            left = left.strip().lower()
            if mid == "action":
                text_value = right
            elif left == "delay":
                delay = float(right.strip())
            elif left == "use js":
                use_js = right.strip().lower() in ("true", "yes", "1")
            elif left == "clear":
                clear = False if right.strip().lower() in ("no", "false") else True
        
        if use_js:  # Use js will automatically clear the field and then enter text
            try:
                selenium_driver.execute_script("arguments[0].click();", Element)
            except:
                CommonUtil.ExecLog(sModuleInfo, "Entering text without clicking the element", 2)
            selenium_driver.execute_script(f"arguments[0].value = `{text_value}`;", Element)
            selenium_driver.execute_script("arguments[0].dispatchEvent(new Event('input', {'bubbles': true}))", Element)
            selenium_driver.execute_script("arguments[0].dispatchEvent(new Event('change', {'bubbles': true}))", Element)
            selenium_driver.execute_script("arguments[0].click();", Element)
        else:
            try:
                Element = handle_clickability_and_click(step_data, Element)
            except:
                CommonUtil.ExecLog(sModuleInfo, "Entering text without clicking the element", 2)
            if clear:
                if selenium_driver.capabilities['browserName'] == "Safari":
                    Element.clear()
                else:
                    if sys.platform == "darwin":
                        Element.send_keys(Keys.COMMAND, "a")
                    else:
                        Element.send_keys(Keys.CONTROL, "a")
                    Element.send_keys(Keys.DELETE)
                    try:
                        Element.clear()  # some cases it works .. so adding it here just in case
                    except:
                        pass
            if delay == 0:
                Element.send_keys(text_value)
            else:
                for c in text_value:
                    Element.send_keys(c)
                    time.sleep(delay)
            try:
                Element.click()
            except:  # Sometimes text field can be unclickable after entering text
                pass
        
        CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of text to: %s" % text_value, 1)
        return "passed"
    except Exception:
        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

'''
@logger
def Enter_Text_In_Text_Box(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        delay = 0
        text_value = ""
        use_js = False
        clear = True
        global selenium_driver
        use_playwright = False
        
        # Check if Playwright should be used
        for left, mid, right in step_data:
            if left.strip().lower() == "driver" and right.strip().lower() in ("playwright"):
                use_playwright = True
                break

        if use_playwright:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                response = requests.get("http://localhost:9222/json/version")
                ws_url = response.json()["webSocketDebuggerUrl"]

                browser = p.chromium.connect_over_cdp(ws_url)  # Connect to existing browser session
                page = browser.contexts[0].pages[0]  # Get the first page
                
                # Extract values from step_data
                for left, mid, right in step_data:
                    mid = mid.strip().lower()
                    left = left.strip().lower()
                    if mid == "action":
                        text_value = right
                    elif left == "delay":
                        delay = float(right.strip())
                    elif left == "clear":
                        clear = False if right.strip().lower() in ("no", "false") else True

                # Locate the element using Playwright
                Element = LocateElement.Get_Element(step_data, page)
                if Element == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                    return "zeuz_failed"
                
                if isinstance(Element, list):
                    if len(Element) > 0:
                        Element = Element[0]  # Take the first item
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Element is an empty list.", 3)
                        return "zeuz_failed"

                if not isinstance(Element, (str, Locator)):
                    CommonUtil.ExecLog(sModuleInfo, f"Unsupported element type: {type(Element)}", 3)
                    return "zeuz_failed"

                # Prepare the locator
                locator = Element if isinstance(Element, Locator) else page.locator(Element)

                if clear:
                    locator.fill("")

                if delay == 0:
                    locator.fill(text_value)
                else:
                    for c in text_value:
                        locator.type(c, delay=delay * 1000)
                
                CommonUtil.ExecLog(sModuleInfo, "Successfully set the value in Playwright to: %s" % text_value, 1)
                return "passed"
        
        # Default to Selenium if Playwright is not used
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"
        
        # Process other parameters (delay, clear, use js) in step_data
        for left, mid, right in step_data:
            mid = mid.strip().lower()
            left = left.strip().lower()
            if mid == "action":
                text_value = right
            elif left == "delay":
                delay = float(right.strip())
            elif left == "use js":
                use_js = right.strip().lower() in ("true", "yes", "1")
            elif left == "clear":
                clear = False if right.strip().lower() in ("no", "false") else True
        
        if use_js:  # Use js will automatically clear the field and then enter text
            try:
                selenium_driver.execute_script("arguments[0].click();", Element)
            except:
                CommonUtil.ExecLog(sModuleInfo, "Entering text without clicking the element", 2)
            selenium_driver.execute_script(f"arguments[0].value = `{text_value}`;", Element)
            selenium_driver.execute_script("arguments[0].dispatchEvent(new Event('input', {'bubbles': true}))", Element)
            selenium_driver.execute_script("arguments[0].dispatchEvent(new Event('change', {'bubbles': true}))", Element)
            selenium_driver.execute_script("arguments[0].click();", Element)
        else:
            try:
                Element = handle_clickability_and_click(step_data, Element)
            except:
                CommonUtil.ExecLog(sModuleInfo, "Entering text without clicking the element", 2)
            if clear:
                if selenium_driver.capabilities['browserName'] == "Safari":
                    Element.clear()
                else:
                    if sys.platform == "darwin":
                        Element.send_keys(Keys.COMMAND, "a")
                    else:
                        Element.send_keys(Keys.CONTROL, "a")
                    Element.send_keys(Keys.DELETE)
                    try:
                        Element.clear()  # some cases it works .. so adding it here just in case
                    except:
                        pass
            if delay == 0:
                Element.send_keys(text_value)
            else:
                for c in text_value:
                    Element.send_keys(c)
                    time.sleep(delay)
            try:
                Element.click()
            except:  # Sometimes text field can be unclickable after entering text
                pass
        
        CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of text to: %s" % text_value, 1)
        return "passed"
    except Exception:
        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
'''

@logger
def Keystroke_For_Element(data_set):
    """Send a keystroke or string to an element or wherever the cursor is located."""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver

    # Playwright key mapping
    playwright_key_mapping = {
        "CTRL": "Control",
        "CMD": "Meta",
        "PLUS": "Equal",  # Playwright uses "Equal" for the plus sign
        "MINUS": "Minus",
        "DASH": "Minus",
        "ESC": "Escape",
        "ENTER": "Enter",
        "TAB": "Tab",
        "SPACE": "Space",
        "SHIFT": "Shift",
        "ALT": "Alt",
    }

    # Parse the data set
    try:
        stype = ""  # keys/chars
        get_element = False  # Use element
        key_count = 1  # Default number of button presses
        use_playwright = False

        for row in data_set:
            if row[1] == "action":
                if row[0] == "keystroke keys":  # Keypress
                    stype = "keys"
                    keystroke_value = row[2]
                    if "," in keystroke_value:  # If user supplied a number of presses
                        keystroke_value = keystroke_value.replace(" ", "")
                        keystroke_value, key_count = keystroke_value.split(",")
                        key_count = int(key_count)
                elif row[0] == "keystroke chars":  # String
                    stype = "chars"
                    keystroke_value = row[2]
            elif row[1] == "element parameter":
                get_element = True
            elif row[0].strip().lower() == "driver" and row[2].strip().lower() == "playwright":
                use_playwright = True

        if stype == "":
            CommonUtil.ExecLog(sModuleInfo, "Field contains incorrect data", 3)
            return "zeuz_failed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Playwright path
    if use_playwright:
        try:
            import requests
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                response = requests.get("http://localhost:9222/json/version")
                ws_url = response.json()["webSocketDebuggerUrl"]
                browser = p.chromium.connect_over_cdp(ws_url)
                page = browser.contexts[0].pages[0]

                if get_element:
                    element = LocateElement.Get_Element(data_set, page)
                    if element in failed_tag_list:
                        CommonUtil.ExecLog(sModuleInfo, "Failed to locate element", 3)
                        return "zeuz_failed"
                else:
                    element = page

                if stype == "keys":
                    for _ in range(key_count):
                        if "+" in keystroke_value:
                            combo = keystroke_value.upper().split("+")
                            # Check if key exists in the mapping
                            key1 = playwright_key_mapping.get(combo[0], combo[0])
                            key2 = playwright_key_mapping.get(combo[1], combo[1])
                            if key1 and key2:
                                page.keyboard.down(key1)
                                page.keyboard.press(key2)
                                page.keyboard.up(key1)
                        else:
                            key = playwright_key_mapping.get(keystroke_value.upper(), keystroke_value.upper())
                            if key:
                                page.keyboard.press(key)
                            else:
                                CommonUtil.ExecLog(sModuleInfo, f"Invalid key: {keystroke_value}", 3)
                                return "zeuz_failed"
                else:
                    if get_element:
                        element.type(keystroke_value)
                    else:
                        page.keyboard.type(keystroke_value)

                CommonUtil.ExecLog(sModuleInfo, f"Sent '{keystroke_value}' to Playwright", 1)
                return "passed"
        except Exception:
            return CommonUtil.Exception_Handler(sys.exc_info(), None, "Playwright keystroke failed")

    # Selenium path
    try:
        if get_element:
            Element = LocateElement.Get_Element(data_set, selenium_driver)
            if Element in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Failed to locate element", 3)
                return "zeuz_failed"
        else:
            Element = ActionChains(selenium_driver)

        if stype == "keys":
            keystroke_value = keystroke_value.upper()
            convert = {
                "CTRL": "CONTROL",
                "PLUS": "ADD",
                "MINUS": "SUBTRACT",
                "DASH": "SUBTRACT",
                "CMD": "COMMAND",
            }
            for key in convert:
                keystroke_value = keystroke_value.replace(key, convert[key])

            if "+" in keystroke_value:
                hotkey_list = keystroke_value.split("+")
                for i in range(len(hotkey_list)):
                    if hotkey_list[i] in list(dict(Keys.__dict__).keys())[2:-2]:
                        Element.key_down(getattr(Keys, hotkey_list[i]))
                    else:
                        Element.key_down(hotkey_list[i])
                for i in reversed(range(len(hotkey_list))):
                    if hotkey_list[i] in list(dict(Keys.__dict__).keys())[2:-2]:
                        Element.key_up(getattr(Keys, hotkey_list[i]))
                    else:
                        Element.key_up(hotkey_list[i])
                Element.perform()
                result = "passed"
            else:
                get_keystroke_value = getattr(Keys, keystroke_value)
                result = Element.send_keys(get_keystroke_value * key_count)
                if not get_element:
                    Element.perform()
        else:
            result = Element.send_keys(keystroke_value)
            if not get_element:
                Element.perform()

        if result not in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Successfully sent %s: %s %d times" % (stype, keystroke_value, key_count),
                1,
            )
            return "passed"
        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Error sending keystroke %s: %s %d times"
                % (stype, keystroke_value, key_count),
                3,
            )
            return "zeuz_failed"

    except:
        return CommonUtil.Exception_Handler(
            sys.exc_info(),
            None,
            f"Error sending keystroke {stype}: {keystroke_value}",
        )


@logger
def execute_javascript(data_set):
    """Executes the JavaScript code.

    Args:
        data_set:
          id/class/etc       | element parameter  | button_id     ; optional row
          variable           | optional parameter | var_name      ; store result into variable
          execute javascript | selenium action    | js_code_here  ; example: $elem.click();

    Returns:
        "passed" if the given script execution is successful.
        "zeuz_failed" otherwise.
    """

    try:
        Element = False
        var_name = None
        script_to_exec = None

        for left, mid, right in data_set:
            left = left.lower().strip()
            mid = mid.lower().strip()
            right = right.strip()

            if "element parameter" in mid:
                Element = True
            if "variable" == left:
                var_name = right
            if "javascript" in left:
                script_to_exec = right

        # Element parameter is provided to use Zeuz Node's element finding approach.
        if Element:
            Element = LocateElement.Get_Element(data_set, selenium_driver)
            # Replace "$elem" with "arguments[0]". For convenience only.
            script_to_exec = script_to_exec.replace("$elem", "arguments[0]")
            # Execute the script.
            result = selenium_driver.execute_script(script_to_exec, Element)
        else:
            result = selenium_driver.execute_script(script_to_exec, None)

        if var_name:
            return Shared_Resources.Set_Shared_Variables(var_name, result)
        else:
            return "passed"
    except Exception:
        errMsg = "Make sure element parameter is provided in the action."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


def handle_clickability_and_click(dataset, Element:selenium.webdriver.remote.webelement.WebElement):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    wait_clickable = Shared_Resources.Get_Shared_Variables("element_wait")
    # for left, mid, right in dataset:
    #     if mid.strip().lower() == "option":
    #         left = left.strip().lower()
    #         if "wait" in left and "clickable" in left:
    #             wait_clickable = int(right.strip())
    # if not wait_clickable:
    #     Element.click()     # no need of try except here. we need to return the exact exception upto this point
    # else:
    log_flag = True
    log_flag2 = True
    first = True
    start = time.perf_counter()
    stale_i = 0
    while True:
        try:
            Element.click()
            if not first:
                CommonUtil.ExecLog(sModuleInfo, "Element has become clickable after %s seconds" % round(time.perf_counter() - start, 2), 2)
            return Element
        except ElementClickInterceptedException:
            first = False
            if log_flag:
                CommonUtil.ExecLog(sModuleInfo, "Click is Intercepted. Waiting %s seconds max for the element to become clickable" % wait_clickable, 2)
                log_flag = False
        except StaleElementReferenceException:
            first = False
            if log_flag2:
                CommonUtil.ExecLog(sModuleInfo, "Element is stale. Waiting %s seconds max for the element to become clickable" % wait_clickable, 2)
                log_flag2 = False
            Element = LocateElement.Get_Element(dataset, selenium_driver)  # Element may need to be relocated in stale
            if stale_i == 0:
                stale_i += 1
                continue
        if time.perf_counter() > start + wait_clickable:
            raise Exception     # not StaleElementReferenceException. we don't want js to perform click

@logger
def Click_and_Download(data_set):
    """ Click and download attachments from web and save it to specific destinations"""
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver, playwright_page

    driver_type = "selenium"
    wait_download = 20
    filepath = ""
    automate_firefox = False
    click_dataset = []
    use_existing = False

    try:
        for left, mid, right in data_set:
            l = left.replace(" ", "").replace("_", "").lower()
            if l == "waitfordownload":
                wait_download = float(right.strip())
            elif l in ("folderpath", "directory", "filepath", "file", "folder") and mid.strip().lower() == "optional parameter":
                filepath = CommonUtil.path_parser(right.strip())
            elif l == "automatefirefoxsavewindow" and mid.strip().lower() == "optional parameter":
                automate_firefox = right.strip().lower() in ("accept", "yes", "ok", "true")
            elif l == "driver" and mid.strip().lower() == "optional parameter":
                driver_type = right.strip().lower()
            elif l == "useexistingsession" and mid.strip().lower() == "optional parameter":
                use_existing = right.strip().lower() in ("yes", "true", "ok", "accept")
            else:
                click_dataset.append((left, mid, right))
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    try:
        if driver_type == "playwright":
            if use_existing:
                try:
                    import requests
                    response = requests.get("http://localhost:9222/json/version")
                    ws_url = response.json()["webSocketDebuggerUrl"]
                    browser = p.chromium.connect_over_cdp(ws_url)
                    page = browser.contexts[0].pages[0]
                except Exception:
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, "Failed to connect over CDP to existing browser session")
            else:
                page = playwright_page

            if Click_Element(click_dataset) == "zeuz_failed":
                 return "zeuz_failed"

            with page.expect_download(timeout=wait_download * 1000) as download_info:
                CommonUtil.ExecLog(sModuleInfo, f"Waiting up to {wait_download}s for download to begin", 1)
            download = download_info.value
            download_path = filepath or os.path.join(initial_download_folder, download.suggested_filename)
            download.save_as(download_path)
            CommonUtil.ExecLog(sModuleInfo, f"Downloaded file saved to {download_path}", 1)
            return "passed"

        else:  # Selenium block
            if selenium_driver.capabilities["browserName"].strip().lower() not in ("chrome", "microsoftedge", "firefox"):
                CommonUtil.ExecLog(sModuleInfo, "This action was made for Chrome, MS Edge and Firefox. Other browsers won't download files in Zeuz_Download_Folder", 2)

            if Click_Element(click_dataset) == "zeuz_failed":
                return "zeuz_failed"

            # Firefox download window handling for Selenium (same as existing logic)
            # ... [existing Firefox automate block remains unchanged] ...

            # Wait for file to download
            CommonUtil.ExecLog(sModuleInfo, f"Download started. Will wait max {wait_download} seconds...", 1)
            s = time.perf_counter()
            ext = {"firefox": ".part", "opera": ".opera"}.get(
                selenium_driver.capabilities["browserName"].strip().lower(), ".crdownload")

            while True:
                try:
                    ld = os.listdir(initial_download_folder)
                    if ld and all(not f.endswith((".tmp", ext)) for f in ld):
                        CommonUtil.ExecLog(sModuleInfo, f"Download finished in {round(time.perf_counter() - s, 2)} seconds", 1)
                        break
                    if time.perf_counter() - s > wait_download:
                        CommonUtil.ExecLog(sModuleInfo, f"Download did not finish in {wait_download} seconds", 2)
                        break
                except:
                    CommonUtil.Exception_Handler(sys.exc_info())
                    time.sleep(2)

            time.sleep(3)

            if filepath:
                all_source_dir = [os.path.join(initial_download_folder, f) for f in os.listdir(initial_download_folder)
                                  if os.path.isfile(os.path.join(initial_download_folder, f))]
                new_path = filepath
                for file_to_be_moved in all_source_dir:
                    file_name = Path(file_to_be_moved).name
                    if "." not in os.path.basename(new_path) and not os.path.exists(new_path):
                        Path(new_path).mkdir(parents=True, exist_ok=True)
                    elif "." in os.path.basename(new_path) and not os.path.exists(new_path):
                        Path(os.path.dirname(new_path)).mkdir(parents=True, exist_ok=True)
                    shutil.move(file_to_be_moved, new_path)

                    final_path = os.path.join(new_path, file_name) if "." not in os.path.basename(new_path) else new_path
                    if os.path.isfile(final_path):
                        CommonUtil.ExecLog(sModuleInfo, f"File '{file_name}' is moved to '{final_path}'", 1)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "File failed to move", 3)
                        return "zeuz_failed"

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

# Method to right click on element; step data passed on by the user
@logger
def Right_Click_Element(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    use_playwright = False

    try:
        # Detect Playwright usage
        for left, mid, right in step_data:
            if left.strip().lower() == "driver" and right.strip().lower() == "playwright":
                use_playwright = True
                break

        if use_playwright:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                response = requests.get("http://localhost:9222/json/version")
                ws_url = response.json()["webSocketDebuggerUrl"]
                browser = p.chromium.connect_over_cdp(ws_url)
                page = browser.contexts[0].pages[0]

                # Locate element with Playwright
                Element = LocateElement.Get_Element(step_data, page)
                if isinstance(Element, list):
                    if len(Element) > 0:
                        Element = Element[0]  # Use the first element
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Element list is empty.", 3)
                        return "zeuz_failed"
                if Element == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                    return "zeuz_failed"

                if isinstance(Element, list) and len(Element) > 0:
                    Element = Element[0]

                locator = Element if isinstance(Element, Locator) else page.locator(Element)

                locator.click(button="right")
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully right clicked the element using Playwright",
                    1,
                )
                return "passed"

        # Default to Selenium
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element != "zeuz_failed":
            try:
                ActionChains(selenium_driver).context_click(Element).perform()
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully right clicked the element with given parameters and values",
                    1,
                )
                return "passed"
            except Exception:
                try:
                    element_attributes = Element.get_attribute("outerHTML")
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                    errMsg = "Could not right click your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                except:
                    return CommonUtil.Exception_Handler(sys.exc_info())
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to double click on element; step data passed on by the user
@logger
def Double_Click_Element(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    use_playwright = False

    try:
        # Detect Playwright usage
        for left, mid, right in step_data:
            if left.strip().lower() == "driver" and right.strip().lower() == "playwright":
                use_playwright = True
                break

        if use_playwright:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                response = requests.get("http://localhost:9222/json/version")
                ws_url = response.json()["webSocketDebuggerUrl"]
                browser = p.chromium.connect_over_cdp(ws_url)
                page = browser.contexts[0].pages[0]

                # Locate element with Playwright
                Element = LocateElement.Get_Element(step_data, page)
                if Element == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                    return "zeuz_failed"

                if isinstance(Element, list) and len(Element) > 0:
                    Element = Element[0]

                if isinstance(Element, Locator):
                    locator = Element
                elif isinstance(Element, str):
                    locator = page.locator(Element)
                else:
                    CommonUtil.ExecLog(sModuleInfo, f"Unsupported element type: {type(Element)}", 3)
                    return "zeuz_failed"

                locator.dblclick()
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully double clicked the element using Playwright",
                    1,
                )
                return "passed"

        # Default to Selenium
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element != "zeuz_failed":
            try:
                ActionChains(selenium_driver).double_click(Element).perform()
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully double clicked the element with given parameters and values",
                    1,
                )
                return "passed"
            except Exception:
                try:
                    element_attributes = Element.get_attribute("outerHTML")
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                    errMsg = "Could not double click your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                except:
                    return CommonUtil.Exception_Handler(sys.exc_info())
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

'''
# Method to hover over element; step data passed on by the user
@logger
def Hover_Over_Element(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element != "zeuz_failed":
            try:
                hov = ActionChains(selenium_driver).move_to_element(Element)
                hov.perform()
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully hovered over the element with given parameters and values",
                    1,
                )
                return "passed"
            except Exception:
                try:
                    element_attributes = Element.get_attribute("outerHTML")
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                    errMsg = "Could not select/hover your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                except:
                    return CommonUtil.Exception_Handler(sys.exc_info())
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
'''
@logger
def Hover_Over_Element(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver

    use_playwright = False
    for left, mid, right in step_data:
        if left.strip().lower() == "driver" and right.strip().lower() == "playwright":
            use_playwright = True
            break

    try:
        if use_playwright:
            import requests
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                response = requests.get("http://localhost:9222/json/version")
                ws_url = response.json()["webSocketDebuggerUrl"]
                browser = p.chromium.connect_over_cdp(ws_url)
                context = browser.contexts[0]
                page = context.pages[-1]  # Assuming last page is in use

                element = LocateElement.Get_Element(step_data, page)
                if element != "zeuz_failed":
                    element.hover()
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Successfully hovered over the element with given parameters and values using Playwright",
                        1,
                    )
                    return "passed"
                else:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Unable to locate your element with given data using Playwright.",
                        3,
                    )
                    return "zeuz_failed"
        else:
            Element = LocateElement.Get_Element(step_data, selenium_driver)
            if Element != "zeuz_failed":
                try:
                    hov = ActionChains(selenium_driver).move_to_element(Element)
                    hov.perform()
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Successfully hovered over the element with given parameters and values",
                        1,
                    )
                    return "passed"
                except Exception:
                    try:
                        element_attributes = Element.get_attribute("outerHTML")
                        CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                        errMsg = "Could not select/hover your element."
                        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                    except:
                        return CommonUtil.Exception_Handler(sys.exc_info())
            else:
                CommonUtil.ExecLog(
                    sModuleInfo, "Unable to locate your element with given data.", 3
                )
                return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def get_element_info(dataset):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        variable_name = None
        new_ds = []
        for each_step_data_item in dataset:
            if "action" == each_step_data_item[1].strip().lower():
                variable_name = each_step_data_item[2].strip()
            else:
                new_ds.append(each_step_data_item)

        if variable_name is None:
            CommonUtil.ExecLog(sModuleInfo, "Variable name should be mentioned. Example: (text, save parameter, var_name)", 3)
            return "zeuz_failed"

        Element = LocateElement.Get_Element(new_ds, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"
        else:
            Shared_Resources.Set_Shared_Variables(variable_name, {"size": Element.size, "location": Element.location})
            return "passed"
    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, e, 3)
        return "zeuz_failed"


@logger
def Save_Attribute(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        variable_name = None
        attribute_name = None
        new_ds = []
        use_playwright = False

        for each_step_data_item in step_data:
            if each_step_data_item[1].strip().lower() == "driver" and each_step_data_item[2].strip().lower() == "playwright":
                use_playwright = True
            elif "save parameter" == each_step_data_item[1].strip().lower():
                variable_name = each_step_data_item[2].strip()
                attribute_name = each_step_data_item[0].strip().lower()
            else:
                new_ds.append(each_step_data_item)

        if variable_name is None or attribute_name is None:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Variable name and attribute should be mentioned. Example: (text, save parameter, var_name)",
                3,
            )
            return "zeuz_failed"

        # Playwright flow
        if use_playwright:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                response = requests.get("http://localhost:9222/json/version")
                ws_url = response.json()["webSocketDebuggerUrl"]
                browser = p.chromium.connect_over_cdp(ws_url)
                page = browser.contexts[0].pages[0]

                Element = LocateElement.Get_Element(new_ds, page)
                if Element == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                    return "zeuz_failed"

                # If it's a list, grab the first item
                if isinstance(Element, list):
                    if len(Element) > 0:
                        Element = Element[0]
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Element is an empty list.", 3)
                        return "zeuz_failed"


                # Get attribute
                if attribute_name == "text":
                    attribute_value = Element.text_content()
                elif attribute_name == "tag":
                    attribute_value = Element.evaluate("el => el.tagName.toLowerCase()")
                elif attribute_name == "checked":
                    attribute_value = Element.is_checked()
                else:
                    attribute_value = Element.get_attribute(attribute_name)

        # Selenium flow
        else:
            Element = LocateElement.Get_Element(new_ds, selenium_driver)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                return "zeuz_failed"

            if attribute_name == "text":
                attribute_value = Element.text
            elif attribute_name == "tag":
                attribute_value = Element.tag_name
            elif attribute_name == "checked":
                attribute_value = Element.is_selected()
            else:
                attribute_value = Element.get_attribute(attribute_name)

        result = Shared_Resources.Set_Shared_Variables(variable_name, attribute_value)
        if result in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Value of Variable '{variable_name}' could not be saved!!!",
                3,
            )
            return "zeuz_failed"
        else:
            return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())



@logger
def save_attribute_values_in_list(step_data):
    """
    This action will expect users to provide a parent element under which they are expecting
    to collect multiple objects.  Users can provide certain constrain to search their elements
    Sample data:

    aria-label                       element parameter      Calendar

    attributes                       target parameter       data-automation="productItemName",
                                                            class="S58f2saa25a3w1",
                                                            return="text",
                                                            return_contains="128GB",
                                                            return_does_not_contain="Windows 10",
                                                            return_does_not_contain="Linux"

    attributes                       target parameter       class="productPricingContainer_3gTS3",
                                                            return="text",
                                                            return_does_not_contain="99.99"

    save attribute values in list    selenium action        list_name

    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        # this is the parent object.  If the user wants to search the entire page, they can
        # provide tag = html
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"

        all_elements = []
        target_index = 0
        target = []
        paired = True

        try:
            for left, mid, right in step_data:
                left = left.strip().lower()
                mid = mid.strip().lower()
                right = right.strip()
                if "target parameter" in mid:
                    target.append([[], [], [], []])
                    temp = right.strip(",").split(',\n')
                    data = []
                    for each in temp:
                        data.append(each.strip().split("=", 1))
                    for i in range(len(data)):
                        for j in range(len(data[i])):
                            data[i][j] = data[i][j].strip()
                            if j == 1:
                                data[i][j] = CommonUtil.strip1(data[i][j], '"')   # dont add another strip here. dont need to strip inside quotation mark

                    for Left, Right in data:
                        if Left == "return":
                            target[target_index][1] = Right
                        elif Left == "return_contains":
                            target[target_index][2].append(Right)
                        elif Left == "return_does_not_contain":
                            target[target_index][3].append(Right)   
                        elif Left.replace(" ", "").replace("_", "") in ("allowhidden", "allowdisable"):
                            target[target_index][0].append(("allow hidden", "optional parameter", Right))
                        else:
                            target[target_index][0].append((Left, "element parameter", Right))

                    target_index = target_index + 1
                elif left == "save attribute values in list":
                    variable_name = right
                elif left == "paired":
                    paired = False if right.lower() == "no" else True

        except:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to parse data. Please write data in correct format", 3
            )
            return "zeuz_failed"

        for each in target:
            all_elements.append(LocateElement.Get_Element(each[0], Element, return_all_elements=True))

        variable_value_size = 0
        for each in all_elements:
            variable_value_size = max(variable_value_size, len(each))

        variable_value = []
        for i in range(variable_value_size):
            variable_value.append([])

        i = 0
        for each in all_elements:
            search_by_attribute = target[i][1]
            j = 0
            for elem in each:
                if search_by_attribute == "text":
                    Attribute_value = elem.text
                elif search_by_attribute == 'tag':
                    Attribute_value = elem.tag_name
                elif search_by_attribute == "checked":
                    Attribute_value = str(elem.is_selected())
                else:
                    Attribute_value = elem.get_attribute(search_by_attribute)
                try:
                    for search_contain in target[i][2]:
                        if not isinstance(search_contain, type(Attribute_value)) or search_contain in Attribute_value or len(search_contain) == 0:
                            break
                    else:
                        if target[i][2]:
                            Attribute_value = None

                    for search_doesnt_contain in target[i][3]:
                        if isinstance(search_doesnt_contain, type(Attribute_value)) and search_doesnt_contain in Attribute_value and len(search_doesnt_contain) != 0:
                            Attribute_value = None
                except:
                    CommonUtil.ExecLog(
                        sModuleInfo, "Couldn't search by return_contains and return_does_not_contain", 2
                    )
                variable_value[j].append(Attribute_value)
                j = j + 1
            i = i + 1
        if target_index == 1:
            variable_value = list(map(list, zip(*variable_value)))[0]
        elif not paired:
            variable_value = list(map(list, zip(*variable_value)))

        return Shared_Resources.Set_Shared_Variables(variable_name, variable_value)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Extract_Table_Data(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        use_playwright = False
        variable_name = ""
        _row = ""
        _column = ""

        for left, mid, right in step_data:
            if left.strip().lower() == "driver" and right.strip().lower() in ("playwright"):
                use_playwright = True
            left = left.strip().lower()
            right = right.strip()
            mid = mid.strip().lower()
            if left == "extract table data":
                variable_name = right
            elif "row" in left and mid == "optional parameter":
                _row = right.replace(" ", "")
            elif "column" in left and mid == "optional parameter":
                _column = right.replace(" ", "")

        if use_playwright:
            Element = LocateElement.Get_Element(step_data, playwright_page)
        else:
            Element = LocateElement.Get_Element(step_data, selenium_driver)

        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"

        variable_value = []

        if use_playwright:
            tag_name = Element.evaluate("e => e.tagName.toLowerCase()")
            if tag_name != "tbody":
                CommonUtil.ExecLog(sModuleInfo, 'Tag name of the Element is not "tbody"', 2)

            all_tr = Element.query_selector_all("tr")
            for row in all_tr:
                all_td = row.query_selector_all("td")
                td_data = [td.text_content().strip() for td in all_td]
                variable_value.append(td_data)

        else:
            if Element.tag_name != "tbody":
                CommonUtil.ExecLog(sModuleInfo, 'Tag name of the Element is not "tbody"', 2)

            all_tr = Element.find_elements("tag name", "tr")
            for row in all_tr:
                all_td = row.find_elements("tag name", "td")
                td_data = [td.get_property("textContent").strip() for td in all_td]
                variable_value.append(td_data)

        if _row and "," not in _row and "-" not in _row:
            try:
                int(_row)
                variable_value = [variable_value[int(_row)]]
            except:
                variable_value = eval("variable_value[%s]" % _row)

        if _column and "," not in _column and "-" not in _column:
            try:
                int(_column)
                variable_value = [[i[int(_column)]] for i in variable_value]
            except:
                variable_value = [eval("i[%s]" % _column) for i in variable_value]

        return Shared_Resources.Set_Shared_Variables(variable_name, variable_value)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())



@logger
def save_web_elements_in_list(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        has_element = False
        all_elements = []
        target_index = 0
        target = []
        # paired = True
        try:
            for left, mid, right in step_data:
                left = left.strip().lower()
                mid = mid.strip().lower()
                right = right.strip()
                if not has_element and mid in ("element parameter", "parent parameter", "unique parameter", "child parameter", "sibling parameter"):
                    has_element = True
                elif "target parameter" in mid:
                    target.append([[], [], [], []])
                    temp = right.strip(",").split(",")
                    data = []
                    for each in temp:
                        if each.strip("\n").startswith("return_contains"):
                            data.append(["return_contains", each.split("return_contains")[1].strip()[1:-1].split("=")])
                        elif each.strip("\n").startswith("return_does_not_contain"):
                            data.append(["return_does_not_contain", each.split("return_does_not_contain")[1].strip()[1:-1].split("=")])
                        else:
                            data.append(each.strip().split("="))
                    for i in range(len(data)):
                        for j in range(len(data[i])):
                            if isinstance(data[i][j], str):
                                data[i][j] = data[i][j].strip()
                            if j == 1:
                                if isinstance(data[i][j], list):
                                    data[i][j][0], data[i][j][1] = data[i][j][0].strip().strip('"'), data[i][j][1].strip().strip('"')
                                elif isinstance(data[i][j], str):
                                    data[i][j] = data[i][j].strip('"')  # dont add another strip here. dont need to strip inside quotation mark

                    for Left, Right in data:
                        if Left == "return_contains":
                            target[target_index][2].append(Right)
                        elif Left == "return_does_not_contain":
                            target[target_index][3].append(Right)
                        else:
                            target[target_index][0].append((Left, 'element parameter', Right))

                    target_index = target_index + 1
                elif left == "save web elements in list":
                    variable_name = right
                # elif left == "paired":
                #     paired = False if right.lower() == "no" else True

            if has_element:
                Element = LocateElement.Get_Element(step_data, selenium_driver)
                if Element == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                    return "zeuz_failed"
            else:
                Element = selenium_driver
        except:
            CommonUtil.ExecLog(sModuleInfo, "Unable to parse data. Please write data in correct format", 3)
            return "zeuz_failed"

        for each in target:
            all_elements.append(LocateElement.Get_Element(each[0], Element, return_all_elements=True))

        cnt = 0
        while cnt < target_index:
            if target[cnt][2]:
                count, to_del = 0, []
                for elem in all_elements[cnt]:
                    for each in target[cnt][2]:
                        if each[0] == "text" and each[1] in elem.text:
                            break
                    else:
                        for each in target[cnt][2]:
                            if each[0] == "tag" and each[1] in elem.tag_name:
                                break
                        else:
                            for each in target[cnt][2]:
                                if each[0] not in ("text", "tag") and elem.get_attribute(each[0]) is None:
                                    break
                            else:
                                for each in target[cnt][2]:
                                    if each[0] not in ("text", "tag") and each[1] in elem.get_attribute(each[0]):
                                        break
                                else:
                                    to_del.append(count)
                    count += 1
                all_elements[cnt] = CommonUtil.Delete_from_list(all_elements[cnt], to_del)
                # Using this function to delete in O(N) complexity
            if target[cnt][3]:
                count, to_del = 0, []
                for elem in all_elements[cnt]:
                    for each in target[cnt][3]:
                        if each[0] == "text" and each[1] in elem.text:
                            to_del.append(count)
                            break
                    else:
                        for each in target[cnt][3]:
                            if each[0] == "tag" and each[1] in elem.tag_name:
                                to_del.append(count)
                                break
                        else:
                            for each in target[cnt][3]:
                                if each[0] not in ("text", "tag") and elem.get_attribute(each[0]) is None:
                                    to_del.append(count)
                                    break
                            else:
                                for each in target[cnt][3]:
                                    if each[0] not in ("text", "tag") and each[1] in elem.get_attribute(each[0]):
                                        to_del.append(count)
                                        break

                    count += 1
                all_elements[cnt] = CommonUtil.Delete_from_list(all_elements[cnt], to_del)

            cnt += 1

        if target_index == 1:
            return Shared_Resources.Set_Shared_Variables(variable_name, all_elements[0])
        else:
            return Shared_Resources.Set_Shared_Variables(variable_name, all_elements)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

'''
# Validating text from an element given information regarding the expected text
@logger
def Validate_Text(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        ignore_case = False
        zeuz_ai = None
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"
        for each_step_data_item in step_data:
            if each_step_data_item[1] == "action":
                expected_text_data = each_step_data_item[2]
                validation_type = each_step_data_item[0]
            elif each_step_data_item[1].strip().lower() in ("optional parameter") and each_step_data_item[0] == "ignore case":
                ignore_case = True if each_step_data_item[2].strip().lower() in ("yes", "true", "ok") else False
            elif each_step_data_item[1].strip().lower() == "text classifier offset":
                zeuz_ai = [each_step_data_item[0].strip(), float(each_step_data_item[2])]
        # expected_text_data = step_data[0][len(step_data[0]) - 1][2]
        if ignore_case:
            expected_text_data = expected_text_data.lower()
            list_of_element_text = Element.text.lower().split("\n")
        else:
            list_of_element_text = Element.text.split("\n")
        visible_list_of_element_text = []
        for each_text_item in list_of_element_text:
            if each_text_item != "":
                visible_list_of_element_text.append(each_text_item)

        # if step_data[0][len(step_data[0])-1][0] == "validate partial text":
        if zeuz_ai is not None:
            """{
                "binary_classification":{
                    "expected_category":"success",
                    "confidence": 0.7
                }
             }
             """
            message = " ".join(visible_list_of_element_text)
            labels = [zeuz_ai[0]]
            confidence = zeuz_ai[1]
            return binary_classification(message, labels, confidence)["status"]

        elif validation_type == "validate partial text":
            actual_text_data = visible_list_of_element_text
            CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1)
            CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1)
            for each_actual_text_data_item in actual_text_data:
                if expected_text_data in each_actual_text_data_item:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "The text has been validated by a partial match.",
                        1,
                    )
                    return "passed"
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to validate using partial match.", 3
            )
            return "zeuz_failed"
        # if step_data[0][len(step_data[0])-1][0] == "validate full text":
        elif validation_type == "validate full text":
            actual_text_data = visible_list_of_element_text
            CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1)
            CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1)
            if expected_text_data in actual_text_data:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "The text has been validated by using complete match.",
                    1,
                )
                return "passed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo, "Unable to validate using complete match.", 3
                )
                return "zeuz_failed"

        else:
            CommonUtil.ExecLog(sModuleInfo, "Incorrect validation type. Please check step data", 3)
            return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
'''


def generate_scroll_offset(direction: str, pixel: int) -> str:
    if direction == "down":
        return f"0,{pixel}"
    elif direction == "up":
        return f"0,-{pixel}"
    elif direction == "left":
        return f"-{pixel},0"
    elif direction == "right":
        return f"{pixel},0"
    else:
        return "0,0"

# Method to scroll down a page
@logger
def Scroll(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        Element = None
        get_element = False
        scroll_direction = ""
        offset = ""
        pixel = 750
        for left, mid, right in step_data:
            mid = mid.strip().lower()
            if "action" in mid:
                scroll_direction = right.strip().lower()
            elif mid == "element parameter":
                get_element = True
            elif left.strip().lower() == "pixels":
                pixel = int(right.strip().lower())

        if get_element:
            Element = LocateElement.Get_Element(step_data, selenium_driver)

        offset = generate_scroll_offset(scroll_direction, pixel)

        CommonUtil.ExecLog(sModuleInfo, f"Scrolling {scroll_direction}", 1)
        selenium_driver.execute_script(f"{'arguments[0]' if Element is not None else 'window'}.scrollBy({offset})")
        time.sleep(2)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to scroll to view an element
@logger
def scroll_to_element(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    method = "js"
    alignToTop = 'true'
    additional_scroll = 0.1
    direction = ""
    
    # Parse step_data
    for left, mid, right in step_data:
        left = left.lower().strip()
        right = right.strip().lower()
        if left == "use js":
            method = "js" if right in ("true", "yes", "1") else "action chain"
        elif left == "align to top":
            alignToTop = "true" if right in ("true", "yes", "1") else "false"
        elif "additional scroll" in left:
            additional_scroll = float(right)
            if "up" in left:
                direction = "up"
            elif "down" in left:
                direction = "down"
            elif "left" in left:
                direction = "left"
            elif "right" in left:
                direction = "right"

    # Check if Playwright is to be used
    use_playwright = any(left.strip().lower() == "driver" and right.strip().lower() == "playwright" for left, mid, right in step_data)

    if use_playwright:
        from playwright.sync_api import sync_playwright
        import requests

        try:
            with sync_playwright() as p:
                response = requests.get("http://localhost:9222/json/version")
                ws_url = response.json()["webSocketDebuggerUrl"]

                browser = p.chromium.connect_over_cdp(ws_url)
                page = browser.contexts[0].pages[0]

                # Use selector to locate element
                selector = LocateElement.Get_Selector(step_data)
                if not selector:
                    CommonUtil.ExecLog(sModuleInfo, "Selector not found in step_data", 3)
                    return "zeuz_failed"

                locator = page.locator(selector)
                locator.scroll_into_view_if_needed()

                # Handle additional scroll
                if direction and additional_scroll > 0:
                    size = page.viewport_size
                    pixel_amount = round(size["height" if direction in ("up", "down") else "width"] * additional_scroll)
                    offset = generate_scroll_offset(direction, pixel_amount)
                    CommonUtil.ExecLog(sModuleInfo, f"Doing additional scroll in {direction} direction", 1)
                    page.evaluate(f"window.scrollBy({offset})")

                browser.close()
            return "passed"
        except Exception:
            return CommonUtil.Exception_Handler(sys.exc_info())

    # Selenium fallback
    scroll_element = LocateElement.Get_Element(step_data, selenium_driver)
    if scroll_element == "zeuz_failed":
        CommonUtil.ExecLog(sModuleInfo, "Element to which instructed to scroll not found", 3)
        return "zeuz_failed"

    try:
        if method == "js":
            selenium_driver.execute_script(f"arguments[0].scrollIntoView({alignToTop});", scroll_element)
        else:
            ActionChains(selenium_driver).move_to_element(scroll_element).perform()

        if direction and additional_scroll > 0:
            time.sleep(1)
            size = selenium_driver.get_window_size()
            pixel_amount = round(size["height" if direction in ("up", "down") else "width"] * additional_scroll)
            offset = generate_scroll_offset(direction, pixel_amount)
            CommonUtil.ExecLog(sModuleInfo, f"Doing additional scroll in {direction} direction", 1)
            selenium_driver.execute_script(f"window.scrollBy({offset})")
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

    return "passed"


scroll_to_top_code = ''' var pre_x = window.pageXOffset;
var pre_y = window.pageYOffset;
window.scrollTo(window.pageXOffset,0); return [pre_x, pre_y, window.pageXOffset, window.pageYOffset]
'''

# Method to scroll to view an element
@logger
def scroll_to_top(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        pre_x, pre_y, x, y = selenium_driver.execute_script(scroll_to_top_code)
        CommonUtil.ExecLog(
            sModuleInfo,
            f"Scrolled to top of the html.\npre_x, pre_y, x, y = [{pre_x}, {pre_y}, {x}, {y}]",
            1 if (x,y) == (0,0) else 2,
        )
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to return pass or fail for the step outcome
@logger
def Navigate(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        if 1 < len(step_data) >= 2:
            CommonUtil.ExecLog(sModuleInfo, "Please provide only single row of data", 3)
            return "zeuz_failed"
        else:
            navigate = step_data[0][2]
            if navigate == "back":
                selenium_driver.back()
                CommonUtil.ExecLog(sModuleInfo, "Performing browser back", 1)
            elif navigate == "forward":
                selenium_driver.forward()
                CommonUtil.ExecLog(sModuleInfo, "Performing browser forward", 1)
            elif navigate == "refresh":
                selenium_driver.refresh()
                CommonUtil.ExecLog(sModuleInfo, "Performing browser refresh", 1)
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Value invalid. Only 'back', 'forward', 'refresh' allowed",
                    3,
                )
                return "zeuz_failed"
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Select_Deselect(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    use_playwright = False

    for left, mid, right in step_data:
        if left.strip().lower() == "driver" and right.strip().lower() in ("playwright"):
            use_playwright = True
            break

    try:
        if use_playwright:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                response = requests.get("http://localhost:9222/json/version")
                ws_url = response.json()["webSocketDebuggerUrl"]
                browser = p.chromium.connect_over_cdp(ws_url)
                page = browser.contexts[0].pages[0]

                Element = LocateElement.Get_Element(step_data, page)
                if Element == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                    return "zeuz_failed"
                if isinstance(Element, list):
                    if len(Element) > 0:
                        Element = Element[0]
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Element is an empty list.", 3)
                        return "zeuz_failed"

                for each in step_data:
                    if each[1] == "action":
                        action = each[0].lower()
                        value = each[2]
                        if action == "select by value":
                            Element.select_option(value=value)
                        elif action == "select by visible text":
                            Element.select_option(label=value)
                        elif action == "select by index":
                            Element.select_option(index=int(value))
                        elif action == "deselect all":
                            # Playwright does not support deselect all directly
                            Element.evaluate("el => { Array.from(el.options).forEach(o => o.selected = false); el.dispatchEvent(new Event('change')); }")
                        elif action == "deselect by value":
                            Element.evaluate(f"el => {{ Array.from(el.options).filter(o => o.value === '{value}').forEach(o => o.selected = false); el.dispatchEvent(new Event('change')); }}")
                        elif action == "deselect by visible text":
                            Element.evaluate(f"el => {{ Array.from(el.options).filter(o => o.label === '{value}').forEach(o => o.selected = false); el.dispatchEvent(new Event('change')); }}")
                        elif action == "deselect by index":
                            Element.evaluate(f"el => {{ el.options[{int(value)}].selected = false; el.dispatchEvent(new Event('change')); }}")
                        else:
                            CommonUtil.ExecLog(sModuleInfo, f"Unknown action '{action}'", 3)
                            return "zeuz_failed"
                        return "passed"
        else:
            Element = LocateElement.Get_Element(step_data, selenium_driver)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                return "zeuz_failed"
            if isinstance(Element, list):
                if len(Element) > 0:
                    Element = Element[0]
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Element is an empty list.", 3)
                    return "zeuz_failed"

            for each in step_data:
                if each[1] == "action":
                    selected_Element = Select(Element)
                    action = each[0].lower()
                    value = each[2]
                    if action == "deselect all":
                        selected_Element.deselect_all()
                    elif action == "deselect by visible text":
                        selected_Element.deselect_by_visible_text(value)
                    elif action == "deselect by value":
                        selected_Element.deselect_by_value(value)
                    elif action == "deselect by index":
                        selected_Element.deselect_by_index(int(value))
                    elif action == "select by index":
                        selected_Element.select_by_index(int(value))
                    elif action == "select by value":
                        selected_Element.select_by_value(value)
                    elif action == "select by visible text":
                        selected_Element.select_by_visible_text(value)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, f"Invalid action '{action}'", 3)
                        return "zeuz_failed"
                    return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Tear_Down_Selenium(step_data=[]):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    global selenium_details
    global current_driver_id
    try:
        driver_id = ""
        for left, mid, right in step_data:
            left = left.replace(" ", "").replace("_", "").replace("-", "").lower()
            if left == "driverid":
                driver_id = right.strip()

        if not driver_id:
            CommonUtil.Join_Thread_and_Return_Result("screenshot")  # Let the capturing screenshot end in thread
            for driver in selenium_details:
                try:
                    selenium_details[driver]["driver"].quit()
                    CommonUtil.ExecLog(sModuleInfo, "Teared down driver_id='%s'" % driver, 1)
                except:
                    errMsg = "Unable to tear down driver_id='%s'. may already been killed" % driver
                    CommonUtil.ExecLog(sModuleInfo, errMsg, 2)
                    CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
            Shared_Resources.Remove_From_Shared_Variables("selenium_driver")
            selenium_details = {}
            selenium_driver = None

        elif driver_id not in selenium_details:
            CommonUtil.ExecLog(sModuleInfo, "Driver_id='%s' not found. So could not tear down" % driver_id, 2)

        else:
            try:
                selenium_details[driver_id]["driver"].quit()
                CommonUtil.ExecLog(sModuleInfo, "Teared down driver_id='%s'" % driver_id, 1)
            except:
                CommonUtil.ExecLog(sModuleInfo, "Unable to tear down driver_id='%s'. may already been killed" % driver_id, 2)
            del selenium_details[driver_id]
            if selenium_details:
                for driver in selenium_details:
                    selenium_driver = selenium_details[driver]["driver"]
                    Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
                    CommonUtil.ExecLog(sModuleInfo, "Current driver is set to driver_id='%s'" % driver, 1)
                    current_driver_id = driver
                    break
            else:
                Shared_Resources.Remove_From_Shared_Variables("selenium_driver")
                selenium_driver = None
                current_driver_id = driver_id

        global vdisplay
        if vdisplay:
            vdisplay.stop()
            vdisplay = None

        return "passed"
    except Exception:
        errMsg = "Unable to tear down selenium browsers. may already be killed"
        # return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
        CommonUtil.ExecLog(sModuleInfo, errMsg, 2)
        return "passed"


@logger
def Switch_Browser(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    global selenium_details
    global current_driver_id
    try:
        driver_id = ""
        for left, mid, right in step_data:
            left = left.replace(" ", "").replace("_", "").replace("-", "").lower()
            if left == "driverid":
                driver_id = right.strip()

        if not driver_id:
            driver_id = "default"

        if driver_id not in selenium_details:
            CommonUtil.ExecLog(sModuleInfo, "Driver_id='%s' not found. So could not Switch" % driver_id, 3)
            return "zeuz_failed"
        else:
            selenium_driver = selenium_details[driver_id]["driver"]
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
            current_driver_id = driver_id
            CommonUtil.ExecLog(sModuleInfo, "Current driver is set to driver_id='%s'" % driver_id, 1)

        return "passed"
    except Exception:
        errMsg = "Unable to tear down selenium browsers. may already be killed"
        # return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
        CommonUtil.ExecLog(sModuleInfo, errMsg, 2)
        return "passed"


@logger
def Get_Current_URL(step_data):
    """
    This action saves the current URL the browser is in by inspecting the address bar.

    get current url         selenium action     <saves the current url by inspecting the address bar of the browser>

    :param step_data: Action data set
    :return: string: "Current URL saved in a variable named '%s'" or "zeuz_failed" depending on the outcome
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        var_name = ""
        use_playwright = False

        for left, mid, right in step_data:
            if mid.strip().lower() == "action":
                var_name = right.strip()
            if left.strip().lower() == "driver" and right.strip().lower() == "playwright":
                use_playwright = True

        if use_playwright:
            try:
                import requests
                from playwright.sync_api import sync_playwright

                with sync_playwright() as p:
                    response = requests.get("http://localhost:9222/json/version")
                    ws_url = response.json()["webSocketDebuggerUrl"]
                    browser = p.chromium.connect_over_cdp(ws_url)
                    page = browser.contexts[0].pages[0]

                    current_url = page.url
                    Shared_Resources.Set_Shared_Variables(var_name, current_url)
                    CommonUtil.ExecLog(sModuleInfo, "Current URL saved in a variable named '%s'" % var_name, 1)
                    return "passed"
            except Exception:
                errMsg = "Unable to save current URL using Playwright"
                CommonUtil.ExecLog(sModuleInfo, errMsg, 2)
                return "zeuz_failed"
        else:
            current_url = selenium_driver.current_url
            Shared_Resources.Set_Shared_Variables(var_name, current_url)
            CommonUtil.ExecLog(sModuleInfo, "Current URL saved in a variable named '%s'" % var_name, 1)
            return "passed"

    except Exception:
        errMsg = "Unable to save current URL"
        CommonUtil.ExecLog(sModuleInfo, errMsg, 2)
        return "zeuz_failed"


'''
# Method to open a new tab
@logger
def open_new_tab(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        time.sleep(2)
        CommonUtil.ExecLog(sModuleInfo, "Opening New Tab in Browser", 1)
        selenium_driver.execute_script("""window.open("");""")
        selenium_driver.switch_to.window(selenium_driver.window_handles[-1])

        CommonUtil.ExecLog(sModuleInfo, "New Tab Opened Successfully in Browser", 1)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
'''

@logger
def switch_window_or_tab(step_data):
    """
    This action will switch tab/window in browser. Basically window and tabs are same in selenium.

    Example 1:
    Field	                    Sub Field	        Value
    *window title               input parameter	    googl
    switch window/tab           selenium action 	switch window or frame


    Example 2:
    Field	                    Sub Field	        Value
    window title                input parameter	    google
    switch window/tab           selenium action 	switch window or frame

    Example 3:
    Field	                    Sub Field	        Value
    window index                input parameter	    9
    switch window/tab           selenium action 	switch window or frame

    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        window_title_condition = False
        window_index_condition = False
        partial_match = False
        for left, mid, right in step_data:
            left = left.lower().strip()
            if left in ("window title", "tab title"):
                switch_by_title = right
                window_title_condition = True
            elif left in ("*window title", "*tab title"):
                switch_by_title = right
                partial_match = True
                window_title_condition = True
            elif left in ("window index", "tab index"):
                switch_by_index = right.strip()
                window_index_condition = True
                window_title_condition = False

    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Unable to parse data. Maintain correct format writen in document", 3)
        return "zeuz_failed"

    try:
        if window_title_condition:
            all_windows = selenium_driver.window_handles
            current_window = selenium_driver.current_window_handle
            window_handles_found = False
            Tries = 3
            for Try in range(Tries):
                for each in all_windows:
                    selenium_driver.switch_to.window(each)
                    if (partial_match and switch_by_title.lower() in selenium_driver.title.lower()) or (
                            not partial_match and switch_by_title.lower() == selenium_driver.title.lower()):
                        window_handles_found = True
                        CommonUtil.ExecLog(sModuleInfo, "Tab switched to '%s'" % selenium_driver.title, 1)
                        break
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Couldn't find the title. Trying again after 1 second delay", 2)
                    time.sleep(1)
                    continue  # only executed if the inner loop did not break
                break  # only executed if the inner loop did break

            if not window_handles_found:
                selenium_driver.switch_to.window(current_window)
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "unable to find the title among the tabs. If you want to match partially please use '*tab title'",
                    3)
                return "zeuz_failed"

        elif window_index_condition:
            window_index = int(switch_by_index)
            window_to_switch = selenium_driver.window_handles[window_index]
            selenium_driver.switch_to.window(window_to_switch)
            CommonUtil.ExecLog(sModuleInfo, f"Tab switched to index {switch_by_index} title {selenium_driver.title}", 1)

        return "passed"
    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Unable to switch your tab", 3)
        return CommonUtil.Exception_Handler(sys.exc_info())
'''
@logger
def close_tab(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver

    use_playwright = False
    try:
        close_tabs = []
        for left, mid, right in step_data:
            left = left.lower().strip()
            if left == "driver" and right.strip().lower() == "playwright":
                use_playwright = True
            elif left == "tabs":
                close_tabs = [i.strip().lower() if type(i) == str else i for i in CommonUtil.parse_value_into_object(right)]
    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Unable to parse data. Maintain correct format written in document", 3)
        return "zeuz_failed"

    if use_playwright:
        try:
            import requests
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                response = requests.get("http://localhost:9222/json/version")
                ws_url = response.json()["webSocketDebuggerUrl"]
                browser = p.chromium.connect_over_cdp(ws_url)
                context = browser.contexts[0]
                pages = context.pages

                if close_tabs:
                    if isinstance(close_tabs[0], str):  # Matching by title
                        for pg in pages:
                            if pg.title().strip().lower() in close_tabs:
                                pg.close()
                                CommonUtil.ExecLog(sModuleInfo, f"Tab closed '{pg.title()}'", 1)
                    else:  # Matching by index
                        for i in close_tabs:
                            title = pages[i].title()
                            pages[i].close()
                            CommonUtil.ExecLog(sModuleInfo, f"Tab closed '{title}'", 1)
                else:
                    # Close current tab (last one focused)
                    title = pages[-1].title()
                    pages[-1].close()
                    CommonUtil.ExecLog(sModuleInfo, f"Current tab closed '{title}'", 1)

                return "passed"
        except Exception:
            CommonUtil.ExecLog(sModuleInfo, "Error closing tab with Playwright", 3)
            return CommonUtil.Exception_Handler(sys.exc_info())
    else:
        try:
            window_handles_found = False
            if len(close_tabs) > 1 and isinstance(close_tabs[0], str):
                current_window = selenium_driver.current_window_handle
                for each in selenium_driver.window_handles:
                    selenium_driver.switch_to.window(each)
                    if selenium_driver.title.strip().lower() in close_tabs:
                        title = selenium_driver.title
                        selenium_driver.close()
                        window_handles_found = True
                        CommonUtil.ExecLog(sModuleInfo, "Tab closed '%s'" % title, 1)
                if window_handles_found:
                    if current_window in selenium_driver.window_handles:
                        selenium_driver.switch_to.window(current_window)
                    else:
                        selenium_driver.switch_to.window(selenium_driver.window_handles[-1])

            elif len(close_tabs) > 1:
                current_window = selenium_driver.current_window_handle
                for each in [selenium_driver.window_handles[i] for i in close_tabs]:
                    selenium_driver.switch_to.window(each)
                    title = selenium_driver.title
                    selenium_driver.close()
                    CommonUtil.ExecLog(sModuleInfo, f"Tab closed '{title}'", 1)
                if current_window in selenium_driver.window_handles:
                    selenium_driver.switch_to.window(current_window)
                else:
                    selenium_driver.switch_to.window(selenium_driver.window_handles[-1])

            else:
                title = selenium_driver.title
                selenium_driver.close()
                CommonUtil.ExecLog(sModuleInfo, f"Current tab closed '{title}'", 1)
                selenium_driver.switch_to.window(selenium_driver.window_handles[-1])

            return "passed"
        except Exception:
            CommonUtil.ExecLog(sModuleInfo, "Unable to switch or close your tab", 3)
            return CommonUtil.Exception_Handler(sys.exc_info())
'''


@logger
def close_tab(step_data):
    """
    This action will switch tab/window in browser. Basically window and tabs are same in selenium.

    Example 1:
    Field	                    Sub Field	        Value
    close tab                   selenium action 	close tab

    Example 2:
    Field	                    Sub Field	        Value
    tab title                   input parameter	    ['Zeuz', 'Google']
    close tab                   selenium action 	close tab

    Example 3:
    Field	                    Sub Field	        Value
    tab index                   input parameter	    [0,1,-1]
    close tab                   selenium action 	close tab

    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        close_tabs = []
        for left, mid, right in step_data:
            left = left.lower().strip()
            if left in ("tabs"):
                close_tabs = [i.strip().lower() if type(i) == str else i for i in CommonUtil.parse_value_into_object(right)]

    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Unable to parse data. Maintain correct format writen in document", 3)
        return "zeuz_failed"

    try:
        window_handles_found = False
        if len(close_tabs) > 1 and type(close_tabs[0]) == str:
            current_window = selenium_driver.current_window_handle
            for each in selenium_driver.window_handles:
                selenium_driver.switch_to.window(each)
                if selenium_driver.title.strip().lower() in close_tabs:
                    title = selenium_driver.title
                    selenium_driver.close()
                    window_handles_found = True
                    CommonUtil.ExecLog(sModuleInfo, "Tab closed '%s'" % title, 1)
            if window_handles_found:
                if current_window in selenium_driver.window_handles:
                    selenium_driver.switch_to.window(current_window)
                else:
                    selenium_driver.switch_to.window(selenium_driver.window_handles[-1])

        elif len(close_tabs) > 1:
            current_window = selenium_driver.current_window_handle
            for each in [selenium_driver.window_handles[i] for i in close_tabs]:
                selenium_driver.switch_to.window(each)
                title = selenium_driver.title
                selenium_driver.close()
                CommonUtil.ExecLog(sModuleInfo, f"Tab closed '{title}'", 1)
            if current_window in selenium_driver.window_handles:
                selenium_driver.switch_to.window(current_window)
            else:
                selenium_driver.switch_to.window(selenium_driver.window_handles[-1])

        else:
            title = selenium_driver.title
            selenium_driver.close()
            CommonUtil.ExecLog(sModuleInfo, f"Current tab closed '{title}'", 1)
            selenium_driver.switch_to.window(selenium_driver.window_handles[-1])

        return "passed"
    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Unable to switch your tab", 3)
        return CommonUtil.Exception_Handler(sys.exc_info())

@logger
def switch_iframe(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    use_playwright = False

    try:
        for left, mid, right in step_data:
            if left.strip().lower() == "driver" and right.strip().lower() == "playwright":
                use_playwright = True
                break

        if use_playwright:
            from playwright.sync_api import sync_playwright
            response = requests.get("http://localhost:9222/json/version")
            ws_url = response.json()["webSocketDebuggerUrl"]

            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(ws_url)
                page = browser.contexts[0].pages[0]

                for left, mid, right in step_data:
                    left = left.lower().strip()
                    mid = mid.lower().strip()
                    right = right.strip()

                    if "default" in right.lower():
                        page.goto(page.url)
                        CommonUtil.ExecLog(sModuleInfo, "Exited all iframes and switched to default content", 1)
                    elif left == "index":
                        idx = int(right)
                        frames = page.frames
                        if -len(frames) <= idx < len(frames):
                            frame = frames[idx]
                            page = frame.page
                            CommonUtil.ExecLog(sModuleInfo, f"Switched to frame index {idx}", 1)
                        else:
                            CommonUtil.ExecLog(sModuleInfo, f"Iframe index {idx} is out of range", 3)
                            return "zeuz_failed"
                    else:
                        try:
                            iframe_data = [(left, "element parameter", right)]
                            element = LocateElement.Get_Element(iframe_data, page)

                            if isinstance(element, list):
                                element = element[0]

                            if isinstance(element, str):
                                frame_locator = page.frame_locator(element)
                            elif isinstance(element, Locator):
                                frame_locator = element
                            else:
                                CommonUtil.ExecLog(sModuleInfo, f"Unsupported element type: {type(element)}", 3)
                                return "zeuz_failed"

                            element_handles = frame_locator.element_handles()
                            if not element_handles:
                                raise Exception("Iframe not found")

                            frame = element_handles[0].content_frame()
                            if not frame:
                                raise Exception("Failed to get frame context")

                            page = frame.page
                            CommonUtil.ExecLog(sModuleInfo, "Iframe switched using locator", 1)
                        except Exception as e:
                            CommonUtil.ExecLog(sModuleInfo, f"Error: {str(e)}", 3)
                            return "zeuz_failed"

        # Default: Selenium flow
        for left, mid, right in step_data:
            left = left.lower().strip()
            mid = mid.lower().strip()
            right = right.strip()

            if "action" in mid and left == "switch iframe":
                continue
            elif left == "index" and "default" in right.lower():
                selenium_driver.switch_to.default_content()
                CommonUtil.ExecLog(sModuleInfo, "Exited all iframes and switched to default content", 1)
            elif left == "index":
                idx = int(right)
                tag = "iframe" if "iframe" in mid else "frame"
                for _ in range(5):
                    elements = selenium_driver.find_elements(By.TAG_NAME, tag)
                    if -len(elements) <= idx < len(elements):
                        selenium_driver.switch_to.frame(idx)
                        CommonUtil.ExecLog(sModuleInfo, f"Switched to {tag} index {idx}", 1)
                        break
                    CommonUtil.ExecLog(sModuleInfo, f"{tag.capitalize()} index = {idx} not found. Retrying...", 2)
                    time.sleep(2)
                else:
                    CommonUtil.ExecLog(sModuleInfo, f"Index out of range. Total {len(elements)} {tag}s found.", 3)
                    return "zeuz_failed"
            elif "default" in right.lower():
                iframe_data = [(left, "element parameter", right)]
                if left != "xpath":
                    tag = "iframe" if "iframe" in mid else "frame"
                    iframe_data.append(("tag", "element parameter", tag))
                element = LocateElement.Get_Element(iframe_data, selenium_driver)
                selenium_driver.switch_to.frame(element)
                CommonUtil.ExecLog(sModuleInfo, "Iframe switched using selector", 1)
            else:
                iframe_data = [(left, "element parameter", right)]
                if left != "xpath":
                    tag = "iframe" if "iframe" in mid else "frame"
                    iframe_data.append(("tag", "element parameter", tag))
                element = LocateElement.Get_Element(iframe_data, selenium_driver)
                selenium_driver.switch_to.frame(element)
                CommonUtil.ExecLog(sModuleInfo, "Iframe switched using selector", 1)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
    

# Method to upload file
@logger
def upload_file(step_data):

    """
    This action will use normal element search parameters to locate the upload button
    You can upload the attachment to your test case and use the name as a variable for reference

    Example 1:
    Field                        Sub Field            Value
    id                           element parameter    fileUPload
    upload file                  selenium action      %|log.rtf|%

    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        file_name = ""
        for each in step_data:
            if each[1] == "action":
                file_name = str(each[2]).strip()

        if file_name == "":
            CommonUtil.ExecLog(sModuleInfo, "File name can't be empty!", 3)
            return "zeuz_failed"
        elif not os.path.exists(file_name):
            CommonUtil.ExecLog(
                sModuleInfo,
                "File '%s' can't be found.. please give a valid file path" % file_name,
                3,
            )
            return "zeuz_failed"

        upload_button = LocateElement.Get_Element(step_data, selenium_driver)
        if upload_button in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find the element with given data", 3)
            return "zeuz_failed"

        upload_button.send_keys(file_name)
        CommonUtil.ExecLog(sModuleInfo, "Uploaded the file: %s successfully."%file_name, 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _gui_upload(path_name, pid=None):
    # Todo: Implement PID to activate the window and focus that at front
    import pyautogui
    time.sleep(3)
    pyautogui.hotkey("alt", "a")
    time.sleep(0.5)
    pyautogui.write(path_name)
    time.sleep(1)
    pyautogui.hotkey("enter")


@logger
def upload_file_through_window(step_data):
    """
    Purpose: Sometimes there are some upload window to upload one or more files which is out of selenium's scope.
    This action automate that upload window with microsoft System API and pyautogui GUI API

    Code detail:
    The upload API is searched by their pid
    The main problem is there are multiple process which open while when launching driver having multiple pid. but we need to find out the main browsers pid
    Firefox driver provides the pid inside capabilities
    For Chrome and Opera we added a custom args named "--zeuz_pid_finder" and searched in the psutil which process contains that arg and get the pid of that process
    For MS Edge browser We extracted selenium.title and searched in Microsoft System API with that window title and fetch all the pids with that window title.
    Also we had extracted all the pids from psutil having "--test-type=webdriver" arg and then matched the pids with previous one to find the genuin pid

    In windows, firstly we try to automate with Microsoft System API. If anything fails in between then we switch to GUI method
    In Mac and Linux, we automate only with GUI
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    all_file_path = []
    pid = ""
    import pyautogui
    if "headless" in dependency:
        CommonUtil.ExecLog(sModuleInfo, "This action will not work on headless browsers", 3)
        return "zeuz_failed"
    try:
        for left, mid, right in step_data:
            left = left.strip().lower()
            l = left.replace(" ", "").replace("_", "").lower()
            if l in ("filepath", "directory"):
                path = CommonUtil.path_parser(right.strip())
                if os.path.isdir(path) or os.path.isfile(path):
                    all_file_path.append(path)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Could not find any directory or file with the path: %s" % path, 3)

        if len(all_file_path) == 0:
            CommonUtil.ExecLog(sModuleInfo, "Could not find any valid filepath or directory", 3)
            return "zeuz_failed"

        path_name = '"' + '" "'.join(all_file_path) + '"'
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing dataset")

    try:
        if platform.system() == "Darwin":
            path_name = path_name[1:-1]
            time.sleep(3)
            pyautogui.hotkey("/")
            time.sleep(5)
            pyautogui.hotkey("command", "a")
            time.sleep(0.5)
            pyautogui.write(path_name)
            time.sleep(0.5)
            pyautogui.hotkey("enter")
            time.sleep(2)
            pyautogui.hotkey("enter")

        # window_ds = ("*window", "element parameter", selenium_driver.title)
        elif platform.system() == "Windows":
            if selenium_driver.capabilities["browserName"].lower() == "firefox":
                pid = str(selenium_driver.capabilities["moz:processID"])
            elif selenium_driver.capabilities["browserName"].lower() == "chrome":
                for process in psutil.process_iter():
                    if process.name() == 'chrome.exe' and '--test-type=webdriver' in process.cmdline() and "--zeuz_pid_finder" in process.cmdline():
                        pid = str(process.pid)
            elif selenium_driver.capabilities["browserName"].lower() == "opera":
                for process in psutil.process_iter():
                    if process.name() == 'opera.exe' and '--test-type=webdriver' in process.cmdline() and "--zeuz_pid_finder" in process.cmdline():
                        pid = str(process.pid)
            elif selenium_driver.capabilities["browserName"].lower() == "microsoftedge":
                for process in psutil.process_iter():
                    if process.name() == 'msedge.exe' and '--test-type=webdriver' in process.cmdline() and "--zeuz_pid_finder" in process.cmdline():
                        pid = str(process.pid)
            from Framework.Built_In_Automation.Desktop.Windows.BuiltInFunctions import Click_Element, Enter_Text_In_Text_Box, Save_Attribute, get_pids_from_title

            """ We may need the following codes when deprecated msedge selenium stops working """
            # time.sleep(3)
            # if selenium_driver.capabilities["browserName"].lower() == "msedge": # Msedge browser only exists in windows
            #     win_pids = get_pids_from_title(selenium_driver.title)
            #     if len(win_pids) == 0:
            #         CommonUtil.ExecLog(sModuleInfo, "Could not find the pid for msedge. Switching to GUI method", 2)
            #         _gui_upload(path_name)
            #         CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
            #         return "passed"
            #     if len(win_pids) > 1:
            #         psutil_pids = []
            #         for process in psutil.process_iter():
            #             if process.name() == 'msedge.exe' and '--test-type=webdriver' in process.cmdline():
            #                 psutil_pids.append(process.pid)
            #         for i in win_pids:
            #             if i in psutil_pids:
            #                 pid = str(i)
            #                 break
            #         else:
            #             pid = str(win_pids[0])
            #     else:
            #         pid = str(win_pids[0])

            if selenium_driver.capabilities["browserName"].lower() not in ("firefox", "chrome", "opera", "microsoftedge"):
                win_pids = get_pids_from_title(selenium_driver.title)
                if len(win_pids) == 0:
                    CommonUtil.ExecLog(sModuleInfo, "Could not find the pid for browser. Switching to GUI method", 2)
                    _gui_upload(path_name)
                    CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
                    return "passed"
                if len(win_pids) > 1:
                    psutil_pids = []
                    for process in psutil.process_iter():
                        if '--test-type=webdriver' in process.cmdline():
                            psutil_pids.append(process.pid)
                    for i in win_pids:
                        if i in psutil_pids:
                            pid = str(i)
                            break
                    else:
                        pid = str(win_pids[0])
                else:
                    pid = str(win_pids[0])

            if not pid:
                CommonUtil.ExecLog(sModuleInfo, "Could not find the PID for browser. Switching to GUI method", 2)
                _gui_upload(path_name)
                CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
                return "passed"

            window_ds = ("window pid", "element parameter", pid)
            save_attribute_ds = [
                window_ds,
                ("wait", "optional parameter", "20"),
                ("AutomationId", "element parameter", "1090"),
                ("Name", "save parameter", "ZeuZ_uPLOad_W1N_F1LE__OR_FOLdeR_87138131"),
                ("save attribute", "windows action", "save attribute"),
            ]
            if Save_Attribute(save_attribute_ds) == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find the Textbox. Switching to GUI method", 2)
                _gui_upload(path_name)
                CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
                return "passed"
            file_or_folder = Shared_Resources.Get_Shared_Variables("ZeuZ_uPLOad_W1N_F1LE__OR_FOLdeR_87138131")
            if "file name" in file_or_folder.lower():
                id = "1148"
            elif "folder" in file_or_folder.lower():
                id = "1152"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Invalid Upload type. file_or_folder = '%s'" % file_or_folder, 3)
                return "zeuz_failed"

            enter_text_ds = [
                window_ds,
                ("wait", "optional parameter", "20"),
                ("LocalizedControlType", "element parameter", "edit"),
                ("AutomationId", "element parameter", id),
                ("text", "windows action", path_name),
            ]
            if Enter_Text_In_Text_Box(enter_text_ds) == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find the Open button. Switching to GUI method", 2)
                _gui_upload(path_name)
                CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
                return "passed"

            click_ds = [
                window_ds,
                ("wait", "optional parameter", "20"),
                ("AutomationId", "element parameter", "1"),
                ("Name", "element parameter", "Open"),
                ("LocalizedControlType", "element parameter", "button"),
                ("click", "windows action", "click"),
            ]
            if Click_Element(click_ds) == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find the Open button. Switching to GUI method (pressing Enter)", 2)
                time.sleep(1)
                pyautogui.hotkey("enter")
                CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
                return "passed"

        # elif platform.system() == "Linux":
        #     _gui_upload(path_name)
        else:
            _gui_upload(path_name[0:-1])

        CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
        return "passed"

    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        CommonUtil.ExecLog(sModuleInfo, "Could not find the Textbox. Switching to GUI method", 2)
        _gui_upload(path_name)
        CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
        return "passed"


# Method to upload file
def get_offsets(location: str, Element: WebElement) -> tuple[int]:
    location = location.replace(" ", "")
    location = location.split(",")
    x = float(location[0])
    y = float(location[1])

    height_width = Element.size

    ele_width = int((height_width)["width"])
    ele_height = int((height_width)["height"])

    total_x_offset = int((ele_width // 2) * (x / 100))
    total_y_offset = int((ele_height // 2) * (y / 100))

    return total_x_offset, total_y_offset


@logger
def drag_and_drop(dataset):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    from time import sleep
    try:
        source = []
        destination = []
        destination_offset = None
        delay = None
        param_dict = {"elementparameter": "element parameter", "parentparameter": "parent parameter", "siblingparameter": "sibling parameter", "childparameter": "child parameter","optionalparameter": "optional parameter"}
        for left, mid, right in dataset:
            if mid.startswith("src") or mid.startswith("source"):
                mid = mid.replace("src", "").replace(" ", "").replace("source", "")
                for param in param_dict:
                    if param == mid:
                        source.append((left, param_dict[param], right))
            elif mid.startswith("dst") or mid.startswith("destination"):
                mid = mid.replace("dst", "").replace(" ", "").replace("destination", "")
                for param in param_dict:
                    if param == mid:
                        destination.append((left, param_dict[param], right))
            elif left.strip().lower() in ("wait", "allow disable", "allow hidden") and mid == "option":
                source.append((left, mid, right))
                destination.append((left, mid, right))
            elif left.strip().lower() == "destination offset" and mid.strip().lower() == 'optional parameter':
                destination_offset = right
            elif left.strip().lower() == "delay":
                delay = float(right.strip())

        if not source:
            CommonUtil.ExecLog(sModuleInfo, 'Please provide source element with "src element parameter", "src parent parameter" etc. Example:\n'+
               "(id, src element parameter, file)", 3)
            return "zeuz_failed"

        if not destination:
            CommonUtil.ExecLog(sModuleInfo, 'Please provide Destination element with "dst element parameter", "dst parent parameter" etc. Example:\n'+
               "(id, dst element parameter, table)", 3)
            return "zeuz_failed"

        source_element = LocateElement.Get_Element(source, selenium_driver)
        if source_element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Source Element is not found", 3)
            return "zeuz_failed"

        destination_element = LocateElement.Get_Element(destination, selenium_driver)
        if destination_element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Destination Element is not found", 3)
            return "zeuz_failed"

        if destination_offset:
            x, y = get_offsets(destination_offset, destination_element)
            if delay is not None:
                """ This line of code was not tested, just keeping here"""
                ActionChains(selenium_driver).click_and_hold(source_element).move_to_element_with_offset(destination_element, x, y).pause(delay).release().perform()
            else:
                ActionChains(selenium_driver).click_and_hold(source_element).move_to_element_with_offset(destination_element, x, y).release().perform()

        else:
            if delay is not None:
                ActionChains(selenium_driver).click_and_hold(source_element).move_to_element(destination_element).pause(delay).release(destination_element).perform()
            else:
                ActionChains(selenium_driver).drag_and_drop(source_element, destination_element).perform()

        CommonUtil.ExecLog(sModuleInfo, "Drag and drop completed from source to destination", 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to upload file
@logger
def playwright(dataset):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:

        from playwright.sync_api import sync_playwright
        devtools_url = selenium_driver.command_executor._url.replace('http://', 'ws://') + '/devtools/browser'
        with sync_playwright() as p:
            # browser = p.chromium.connect(browserURL=devtools_url)
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            page = browser.contexts[0].pages[0]

            # source = page.locator("//div[contains(text(), 'abcd')]")
            # dest = page.locator('(//div[@class="fc-timegrid-bg-harness"][1]/div)[1]')
            # source.drag_to(dest)
            #
            # source = page.locator("//div[contains(text(), 'Wolfgang Donna')]")
            # dest = page.locator('//span[contains(text(), "abcd")]/parent::div')
            # source.drag_to(dest)

            fileChooserPromise = page.wait_for_event('filechooser')
            # await page.getByText('Upload file').click();
            # fileChooser = await fileChooserPromise;
            # await fileChooser.setFiles(path.join(__dirname, 'myfile.pdf'));


        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())



@logger
def check_uncheck_all(data_set):
    """ Check or uncheck all elements of a common attribute """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver

    use_js = False
    target = []
    command = "check"
    try:
        for left, mid, right in data_set:
            left = left.lower().strip()
            mid = mid.lower().strip()
            if "use js" == left:
                use_js = right.strip().lower() in ("true", "yes", "ok")
            elif "target parameter" == mid:
                target.append((left, "element parameter", right))
            elif "check uncheck all" == left:
                command = "uncheck" if "uncheck" in right.lower() else "check"
            elif "allow hidden" == left:
                target.append((left, "option", right))

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    Element = LocateElement.Get_Element(data_set, selenium_driver)
    if Element == "zeuz_failed":
        CommonUtil.ExecLog(sModuleInfo, "Could not find the parent element", 3)
        return "zeuz_failed"

    all_elements = LocateElement.Get_Element(target, Element, return_all_elements=True)
    if not all_elements:
        CommonUtil.ExecLog("", "No target was found", 3)
        return "zeuz_failed"

    for i in range(len(all_elements)):
        th = "th"
        if i + 1 == 1:
            th = "st"
        elif i + 1 == 2:
            th = "nd"
        elif i + 1 == 3:
            th = "rd"
        if command == "check" and all_elements[i].is_selected():
            CommonUtil.ExecLog("", str(i + 1) + th + " target is already checked so skipped it", 1)
            continue
        if command == "uncheck" and not all_elements[i].is_selected():
            CommonUtil.ExecLog("", str(i + 1) + th + " target is already unchecked so skipped it", 1)
            continue

        try:
            if use_js:
                selenium_driver.execute_script("arguments[0].click();", all_elements[i])
                if command == "check":
                    CommonUtil.ExecLog("", str(i + 1) + th + " target is checked successfully using Java Script", 1)
                else:
                    CommonUtil.ExecLog("", str(i + 1) + th + " target is unchecked successfully using Java Script", 1)
            else:
                try:
                    all_elements[i].click()
                    if command == "check":
                        CommonUtil.ExecLog("", str(i + 1) + th + " target is checked successfully", 1)
                    else:
                        CommonUtil.ExecLog("", str(i + 1) + th + " target is unchecked successfully", 1)

                except ElementClickInterceptedException:
                    try:
                        selenium_driver.execute_script("arguments[0].click();", all_elements[i])
                        if command == "check":
                            CommonUtil.ExecLog("", str(i + 1) + th + " target is checked successfully using Java Script", 1)
                        else:
                            CommonUtil.ExecLog("", str(i + 1) + th + " target is unchecked successfully using Java Script", 1)
                    except:
                        if command == "check":
                            CommonUtil.ExecLog("", str(i + 1) + th + " target couldn't be checked so skipped it", 3)
                        else:
                            CommonUtil.ExecLog("", str(i + 1) + th + " target couldn't be unchecked so skipped it", 3)
        except:
            if command == "check":
                CommonUtil.ExecLog("", str(i + 1) + th + " target couldn't be checked so skipped it", 3)
            else:
                CommonUtil.ExecLog("", str(i + 1) + th + " target couldn't be unchecked so skipped it", 3)

    return "passed"

@logger
def check_uncheck(data_set):
    """ Check or uncheck all elements of a common attribute """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver

    use_js = False
    command = "check"
    try:
        for left, mid, right in data_set:
            left = left.lower().strip()
            if "use js" == left:
                use_js = right.strip().lower() in ("true", "yes", "ok")
            elif "check uncheck" == left:
                command = "uncheck" if "uncheck" in right.lower() else "check"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    Element = LocateElement.Get_Element(data_set, selenium_driver)
    if Element == "zeuz_failed":
        CommonUtil.ExecLog(sModuleInfo, "Could not find the element", 3)
        return "zeuz_failed"

    if command == "check" and Element.is_selected():
        CommonUtil.ExecLog(sModuleInfo, "The element is already checked so skipped it", 1)
        return "passed"
    elif command == "uncheck" and not Element.is_selected():
        CommonUtil.ExecLog(sModuleInfo, "The element is already unchecked so skipped it", 1)
        return "passed"
    try:
        if use_js:
            selenium_driver.execute_script("arguments[0].click();", Element)
            if command == "check":
                CommonUtil.ExecLog(sModuleInfo, "The element is checked successfully using Java Script", 1)
            else:
                CommonUtil.ExecLog(sModuleInfo, "The element is unchecked successfully using Java Script", 1)
            return "passed"
        else:
            try:
                handle_clickability_and_click(data_set, Element)
                if command == "check":
                    CommonUtil.ExecLog(sModuleInfo, "The element is checked successfully", 1)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "The element is unchecked successfully", 1)
                return "passed"
            except ElementClickInterceptedException:
                try:
                    selenium_driver.execute_script("arguments[0].click();", Element)
                    if command == "check":
                        CommonUtil.ExecLog(sModuleInfo, "The element is checked successfully using Java Script", 1)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "The element is unchecked successfully using Java Script", 1)
                    return "passed"
                except:
                    if command == "check":
                        CommonUtil.ExecLog(sModuleInfo, "The element couldn't be checked", 3)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "The element couldn't be unchecked", 3)
                    return "zeuz_failed"
    except:
        if command == "check":
            CommonUtil.ExecLog(sModuleInfo, "The element couldn't be checked", 3)
        else:
            CommonUtil.ExecLog(sModuleInfo, "The element couldn't be unchecked", 3)
        return "zeuz_failed"


def insert(string, str_to_insert, index):
    return string[:index] + str_to_insert + string[index:]



@logger
def multiple_check_uncheck(data_set):
    """ Check or uncheck multiple web elements """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver

    use_js = False
    inside = False
    allow_hidden = ""
    try:
        for left, mid, right in data_set:
            left = left.lower().strip()
            mid = mid.lower().strip()
            if "use js" == left:
                use_js = right.strip().lower() in ("true", "yes", "ok")
            elif "allow hidden" == left:
                allow_hidden = right
            elif "target parameter" == mid:
                targets = []
                temp = right.strip()
                i = 0
                while True:
                    if i >= len(temp):
                        break
                    if temp[i] == "(":
                        inside = True
                        temp = insert(temp, "\"", i+1)
                    elif inside and temp[i] == ",":
                        temp = insert(temp, "\"", i+1)
                        temp = insert(temp, "\"", i)
                        i += 1
                    if temp[i] == ")":
                        inside = False
                        temp = insert(temp, "\"", i)
                        i += 1
                    i += 1
                temp = insert(temp, "[", 0)
                temp = insert(temp, "]", len(temp))
                temp = CommonUtil.parse_value_into_object(temp)
                for Left, Mid, Right in temp:
                    targets.append((Left.strip().lower(), Mid.strip(), Right.strip().lower()))
                    # Stripped Mid if any trailing spaces exists need to use asterisk

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    Element = LocateElement.Get_Element(data_set, selenium_driver)
    if Element == "zeuz_failed":
        CommonUtil.ExecLog(sModuleInfo, "Could not find the parent element", 3)
        return "zeuz_failed"

    element_params = []
    for left, mid, right in targets:
        if allow_hidden:
            element_params.append([("allow hidden", "option", allow_hidden), (left, "element parameter", mid)])
        else:
            element_params.append([(left, "element parameter", mid)])

    all_elements = []
    for i in element_params:
        all_elements.append(LocateElement.Get_Element(i, Element))

    for i in range(len(all_elements)):
        if all_elements[i] == "zeuz_failed":
            CommonUtil.ExecLog("", str(targets[i]) + " was not found so skipped it", 3)
            continue
        if targets[i][2] == "check" and all_elements[i].is_selected():
            CommonUtil.ExecLog("", str(targets[i]) + " is already checked so skipped it", 1)
            continue
        if targets[i][2] == "uncheck" and not all_elements[i].is_selected():
            CommonUtil.ExecLog("", str(targets[i]) + " is already unchecked so skipped it", 1)
            continue

        try:
            if use_js:
                selenium_driver.execute_script("arguments[0].click();", all_elements[i])
                if targets[i][2] == "check":
                    CommonUtil.ExecLog("", str(targets[i]) + " is checked successfully using Java Script", 1)
                else:
                    CommonUtil.ExecLog("", str(targets[i]) + " is unchecked successfully using Java Script", 1)
            else:
                try:
                    all_elements[i].click()
                    if targets[i][2] == "check":
                        CommonUtil.ExecLog("", str(targets[i]) + " is checked successfully", 1)
                    else:
                        CommonUtil.ExecLog("", str(targets[i]) + " is unchecked successfully", 1)
                except ElementClickInterceptedException:
                    try:
                        selenium_driver.execute_script("arguments[0].click();", all_elements[i])
                        if targets[i][2] == "check":
                            CommonUtil.ExecLog("", str(targets[i]) + " is checked successfully using Java Script", 1)
                        else:
                            CommonUtil.ExecLog("", str(targets[i]) + " is unchecked successfully using Java Script", 1)
                    except:
                        if targets[i][2] == "check":
                            CommonUtil.ExecLog("", str(targets[i]) + " couldn't be checked so skipped it", 3)
                        else:
                            CommonUtil.ExecLog("", str(targets[i]) + " couldn't be unchecked so skipped it", 3)
        except:
            if targets[i][2] == "check":
                CommonUtil.ExecLog("", str(targets[i]) + " couldn't be checked so skipped it", 3)
            else:
                CommonUtil.ExecLog("", str(targets[i]) + " couldn't be unchecked so skipped it", 3)

    return "passed"


@logger
def slider_bar(data_set):
    """Set certain value to a slider bar
    you must provide a number between 0 - 100
     """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        value = ""

        for left, mid, right in data_set:
            if "action" in mid:
                value = int(right.strip())
        # if value not in range(0, 100):
        #     CommonUtil.ExecLog(sModuleInfo, "Failed to parse data/locate element. You must provide a number between 0-100", 3)
        #     return "zeuz_failed"
        Element = LocateElement.Get_Element(data_set, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find the element", 3)
            return "zeuz_failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, f"Moving the slider by %{value} ", 1)
            move = ActionChains(selenium_driver)
            height_width = Element.size
            ele_width = int((height_width)["width"])
            ele_height = int((height_width)["height"])
            x_cord_to_tap = ((value/100) * ele_width)
            y_cord_to_tap = (ele_height/2)

            move.move_to_element_with_offset(Element, x_cord_to_tap, y_cord_to_tap).click().perform()
            CommonUtil.ExecLog(sModuleInfo, f"Successfully set the slider to %{value}", 1)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def resize_window(step_data):
    """Action to resize window size"""
    """
    width          element parameter   50%
    height         element parameter   70%
    resize window  selenium action     resize window
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        window_size = selenium_driver.get_window_size()
        CommonUtil.ExecLog(sModuleInfo, f"Current window size is {window_size}", 1)
        for left, mid, right in step_data:
            left = left.lower().strip()
            right = right.lower().strip()
            if 'element parameter' in mid.lower():
                for dim in ['width','height']:
                    if left.lower().strip() == dim:
                        right = right.replace('%','').strip()
                        try:
                            right = float(right)
                            window_size[dim] = window_size[dim] * right/100
                        except:
                            CommonUtil.ExecLog(sModuleInfo, f"Enter valid size for {dim}", 3)
                            return CommonUtil.Exception_Handler(sys.exc_info())
        selenium_driver.set_window_size(window_size['width'],window_size['height'])
        CommonUtil.ExecLog(sModuleInfo, f"Successfully set the new window size to {window_size}", 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error resizing window")

@deprecated
@logger
def if_element_exists(data_set):
    """ if an element found, save a value to a variable """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        variable_name = ""
        value = ""

        for left, mid, right in data_set:
            if "action" in mid:
                value, variable_name = right.split("=")
                value = value.strip()
                variable_name = variable_name.strip()

        Element = LocateElement.Get_Element(data_set, selenium_driver)
        if Element in failed_tag_list:
            Shared_Resources.Set_Shared_Variables(variable_name, "false")
        else:
            Shared_Resources.Set_Shared_Variables(variable_name, value)
        return "passed"
    except Exception:
        errMsg = (
            "Failed to parse data/locate element. Data format: variableName = value"
        )
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

 # The @logger decorator logs the entry and exit of the action as well
 # as its run time.

    
def open_new_tab(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        use_playwright = False
        for left, mid, right in step_data:
            if left.strip().lower() == "driver" and right.strip().lower() == "playwright":
                use_playwright = True
                break

        time.sleep(2)
        CommonUtil.ExecLog(sModuleInfo, "Opening New Tab in Browser", 1)

        if use_playwright:
            try:
                import requests
                from playwright.sync_api import sync_playwright

                with sync_playwright() as p:
                    response = requests.get("http://localhost:9222/json/version")
                    ws_url = response.json()["webSocketDebuggerUrl"]
                    browser = p.chromium.connect_over_cdp(ws_url)
                    context = browser.contexts[0]
                    page = context.new_page()  # Open new tab
                    page.bring_to_front()

                CommonUtil.ExecLog(sModuleInfo, "New Tab Opened Successfully in Browser using Playwright", 1)
                return "passed"
            except Exception:
                return CommonUtil.Exception_Handler(sys.exc_info(), None, "Unable to open new tab using Playwright")
        else:
            selenium_driver.execute_script("""window.open("");""")
            selenium_driver.switch_to.window(selenium_driver.window_handles[-1])
            CommonUtil.ExecLog(sModuleInfo, "New Tab Opened Successfully in Browser using Selenium", 1)
            return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Failed to open new tab")


'''
def Go_To_Link(dataset: Dataset) -> ReturnType:
    global playwright_browser, playwright_page  # Ensure these variables are accessible

    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        web_link = None
        browser_type = "chromium"  # Default browser

        # Extract necessary values from dataset
        for left, mid, right in dataset:
            left = left.replace(" ", "").replace("_", "").replace("-", "").lower()
            if left == "gotolink":
                web_link = right.strip()
            elif left == "browser":
                browser_type = right.strip().lower()

        if playwright_browser is None:  # Prevent multiple launches
            playwright = sync_playwright().start()  # Start Playwright session
            
            if browser_type == "firefox":
                playwright_browser = playwright.firefox.launch(headless=False)
            elif browser_type == "webkit":
                playwright_browser = playwright.webkit.launch(headless=False)
            else:
                playwright_browser = playwright.chromium.launch(headless=False)

            playwright_page = playwright_browser.new_page()
        
        if web_link:
            playwright_page.goto(web_link, timeout=120000)  # Open URL with 120s timeout
            CommonUtil.ExecLog(sModuleInfo, f"Successfully opened {web_link}", 1)

        # Store for later use
        Shared_Resources.Set_Shared_Variables("playwright_page", playwright_page)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Failed to open browser")
'''
'''
def Enter_Text_In_Text_Box(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        delay = 0
        text_value = ""
        use_js = False
        clear = True

        # Get the Playwright page object
        global playwright_page  # Assuming you store the page globally
        if not playwright_page:
            CommonUtil.ExecLog(sModuleInfo, "Playwright page is not initialized.", 3)
            return "zeuz_failed"

        # Locate the element using Playwright
        Element = LocateElement.Get_Element(step_data, playwright_page)  # Pass Playwright page
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"

        for left, mid, right in step_data:
            mid = mid.strip().lower()
            left = left.strip().lower()
            if mid == "action":
                text_value = right
            elif left == "delay":
                delay = float(right.strip())
            elif left == "use js":
                use_js = right.strip().lower() in ("true", "yes", "1")
            elif left == "clear":
                clear = False if right.strip().lower() in ("no", "false") else True

        if use_js:
            # Click the element using JavaScript
            Element.evaluate("el => el.click()")
            # Set the text value using JavaScript
            Element.evaluate(f"el => el.value = `{text_value}`")
            # Dispatch input and change events
            Element.evaluate("el => el.dispatchEvent(new Event('input', {'bubbles': true}))")
            Element.evaluate("el => el.dispatchEvent(new Event('change', {'bubbles': true}))")
            # Click again to ensure focus
            Element.evaluate("el => el.click()")
        else:
            # Click the element before entering text
            Element.click()
            if clear:
                Element.fill("")  # Clears the existing text
            if delay == 0:
                Element.fill(text_value)
            else:
                for c in text_value:
                    Element.type(c, delay=delay * 1000)  # Playwright uses milliseconds

        CommonUtil.ExecLog(sModuleInfo, f"Successfully set the text to: {text_value}", 1)
        return "passed"
    except Exception:
        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
'''
'''
def Click_Element(data_set, retry=0):
    """ Click using element or location with both Selenium and Playwright """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    use_js = False
    use_playwright = False
    global selenium_driver
    
    try:
        # Check if Playwright should be used
        for left, mid, right in data_set:
            if left.strip().lower() == "driver" and right.strip().lower() == "playwright":
                use_playwright = True
                break
        
        if use_playwright:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                response = requests.get("http://localhost:9222/json/version")
                ws_url = response.json()["webSocketDebuggerUrl"]
                
                browser = p.chromium.connect_over_cdp(ws_url)
                page = browser.contexts[0].pages[0]

                # Locate element using Playwright
                Element = LocateElement.Get_Element(data_set, page)
                if Element == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                    return "zeuz_failed"
                
                if isinstance(Element, list) and len(Element) > 0:
                    Element = Element[0]
                
                if not isinstance(Element, (str, Locator)):
                    CommonUtil.ExecLog(sModuleInfo, f"Unsupported element type: {type(Element)}", 3)
                    return "zeuz_failed"
                
                locator = Element if isinstance(Element, Locator) else page.locator(Element)

                # Handle click using Playwright
                if use_js:
                    page.evaluate("arguments[0].click();", locator)
                else:
                    locator.click()

                CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1)
                return "passed"
        
        # Default to Selenium if Playwright is not used

        location = ""  # Initialize location with empty string

        for left, mid, right in data_set:
            mid = mid.strip().lower()
            left = left.strip().lower()
            if "use js" in mid:
                use_js = right.strip().lower() in ("true", "yes", "1")
            elif mid == "location":
                location = right.strip()

        Element = LocateElement.Get_Element(data_set, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"

        for left, mid, right in data_set:
            mid = mid.strip().lower()
            left = left.strip().lower()
            if "use js" in mid:
                use_js = right.strip().lower() in ("true", "yes", "1")

        # Handle click using Selenium
        if location == "":
            try:
                if use_js:
                    selenium_driver.execute_script("arguments[0].click();", Element)
                else:
                    handle_clickability_and_click(data_set, Element)
                CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1)
                return "passed"
            except ElementClickInterceptedException:
                try:
                    selenium_driver.execute_script("arguments[0].click();", Element)
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Your element is overlapped with another sibling element. Clicked the element successfully by executing JavaScript",
                        2
                    )
                    return "passed"
                except Exception:
                    try:
                        element_attributes = Element.get_attribute("outerHTML")
                        CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                        errMsg = "Could not click and hold your element."
                        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                    except:
                        return CommonUtil.Exception_Handler(sys.exc_info())
            except StaleElementReferenceException:
                if retry == 5:
                    CommonUtil.ExecLog(sModuleInfo, "Could not perform click because javascript of the element is not fully loaded", 3)
                    return "zeuz_failed"
                CommonUtil.ExecLog("", "Javascript of the element is not fully loaded. Trying again after 1 second delay", 2)
                time.sleep(1)
                return Click_Element(data_set, retry + 1)

            except Exception:
                try:
                    element_attributes = Element.get_attribute("outerHTML")
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                    errMsg = "Could not click and hold your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                except:
                    return CommonUtil.Exception_Handler(sys.exc_info())

        # Click using location in Selenium
        else:
            try:
                total_x_offset, total_y_offset = get_offsets(location, Element)
                actions = ActionChains(selenium_driver)  # Create actions object
                actions.move_to_element_with_offset(Element, total_x_offset, total_y_offset)  # Move to coordinates (referrenced by body at 0,0)
                actions.click()  # Click action
                actions.perform()  # Perform all actions
                CommonUtil.ExecLog(sModuleInfo, "Click on location successful", 1)
                return "passed"
            except Exception:
                return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error clicking location")

    except Exception:
        errMsg = "Error performing click action."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
'''

def Click_Element(data_set, retry=0):
    """ Click using element or location with both Selenium and Playwright """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    use_js = False
    use_playwright = False
    global selenium_driver

    try:
        # Check if Playwright should be used
        for left, mid, right in data_set:
            if left.strip().lower() == "driver" and right.strip().lower() == "playwright":
                use_playwright = True
                break
        
        # Playwright flow
        if use_playwright:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                response = requests.get("http://localhost:9222/json/version")
                ws_url = response.json()["webSocketDebuggerUrl"]
                
                browser = p.chromium.connect_over_cdp(ws_url)
                page = browser.contexts[0].pages[0]

                # Locate element using Playwright
                Element = LocateElement.Get_Element(data_set, page)
                if Element == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                    return "zeuz_failed"
                
                if isinstance(Element, list) and len(Element) > 0:
                    Element = Element[0]
                
                if not isinstance(Element, (str, Locator)):
                    CommonUtil.ExecLog(sModuleInfo, f"Unsupported element type: {type(Element)}", 3)
                    return "zeuz_failed"
                
                locator = Element if isinstance(Element, Locator) else page.locator(Element)

                # Handle click using Playwright
                if use_js:
                    page.evaluate("arguments[0].click();", locator)
                else:
                    locator.click()

                CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1)
                return "passed"
        
        # Default to Selenium if Playwright is not used
        location = ""  # Initialize location with empty string

        for left, mid, right in data_set:
            mid = mid.strip().lower()
            left = left.strip().lower()
            if "use js" in mid:
                use_js = right.strip().lower() in ("true", "yes", "1")
            elif mid == "location":
                location = right.strip()

        Element = LocateElement.Get_Element(data_set, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"

        for left, mid, right in data_set:
            mid = mid.strip().lower()
            left = left.strip().lower()
            if "use js" in mid:
                use_js = right.strip().lower() in ("true", "yes", "1")

        # Handle click using Selenium
        if location == "":
            try:
                if use_js:
                    selenium_driver.execute_script("arguments[0].click();", Element)
                else:
                    handle_clickability_and_click(data_set, Element)
                CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1)
                return "passed"
            except ElementClickInterceptedException:
                try:
                    selenium_driver.execute_script("arguments[0].click();", Element)
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Your element is overlapped with another sibling element. Clicked the element successfully by executing JavaScript",
                        2
                    )
                    return "passed"
                except Exception:
                    try:
                        element_attributes = Element.get_attribute("outerHTML")
                        CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                        errMsg = "Could not click and hold your element."
                        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                    except:
                        return CommonUtil.Exception_Handler(sys.exc_info())
            except StaleElementReferenceException:
                if retry == 5:
                    CommonUtil.ExecLog(sModuleInfo, "Could not perform click because javascript of the element is not fully loaded", 3)
                    return "zeuz_failed"
                CommonUtil.ExecLog("", "Javascript of the element is not fully loaded. Trying again after 1 second delay", 2)
                time.sleep(1)
                return Click_Element(data_set, retry + 1)

            except Exception:
                try:
                    element_attributes = Element.get_attribute("outerHTML")
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                    errMsg = "Could not click and hold your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                except:
                    return CommonUtil.Exception_Handler(sys.exc_info())

        # Click using location in Selenium
        else:
            try:
                total_x_offset, total_y_offset = get_offsets(location, Element)
                actions = ActionChains(selenium_driver)  # Create actions object
                actions.move_to_element_with_offset(Element, total_x_offset, total_y_offset)  # Move to coordinates (referenced by body at 0,0)
                actions.click()  # Click action
                actions.perform()  # Perform all actions
                CommonUtil.ExecLog(sModuleInfo, "Click on location successful", 1)
                return "passed"
            except Exception:
                return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error clicking location")

    except Exception:
        errMsg = "Error performing click action."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

'''
def Validate_Text(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        # Check if Playwright should be used
        use_playwright = False
        for each_step_data_item in step_data:
            if each_step_data_item[1].strip().lower() == "driver" and each_step_data_item[2].strip().lower() == "playwright":
                use_playwright = True
                break

        # If using Playwright
        if use_playwright:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                response = requests.get("http://localhost:9222/json/version")
                ws_url = response.json()["webSocketDebuggerUrl"]
                browser = p.chromium.connect_over_cdp(ws_url)
                page = browser.contexts[0].pages[0]

                # Locate element using Playwright
                Element = LocateElement.Get_Element(step_data, page)
                if Element == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                    return "zeuz_failed"

                text = Element.text_content()
        else:
            # Use Selenium if Playwright is not used
            Element = LocateElement.Get_Element(step_data, selenium_driver)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                return "zeuz_failed"
            
            text = Element.text

        ignore_case = False
        zeuz_ai = None
        expected_text_data = None
        validation_type = None

        for each_step_data_item in step_data:
            if each_step_data_item[1] == "action":
                expected_text_data = each_step_data_item[2]
                validation_type = each_step_data_item[0]
            elif each_step_data_item[1].strip().lower() == "optional parameter" and each_step_data_item[0] == "ignore case":
                ignore_case = True if each_step_data_item[2].strip().lower() in ("yes", "true", "ok") else False
            elif each_step_data_item[1].strip().lower() == "text classifier offset":
                zeuz_ai = [each_step_data_item[0].strip(), float(each_step_data_item[2])]

        if ignore_case:
            expected_text_data = expected_text_data.lower()
            text = text.lower()

        # If AI-based validation
        if zeuz_ai is not None:
            message = text
            labels = [zeuz_ai[0]]
            confidence = zeuz_ai[1]
            return binary_classification(message, labels, confidence)["status"]

        # Partial text validation
        elif validation_type == "validate partial text":
            if expected_text_data in text:
                CommonUtil.ExecLog(sModuleInfo, "The text has been validated by partial match.", 1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Unable to validate using partial match.", 3)
                return "zeuz_failed"

        # Full text validation
        elif validation_type == "validate full text":
            if expected_text_data == text:
                CommonUtil.ExecLog(sModuleInfo, "The text has been validated by complete match.", 1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Unable to validate using complete match.", 3)
                return "zeuz_failed"
        
        else:
            CommonUtil.ExecLog(sModuleInfo, "Incorrect validation type. Please check step data", 3)
            return "zeuz_failed"
        
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
'''

@logger
def Validate_Text(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        use_playwright = any(
            left.strip().lower() == "driver" and right.strip().lower() == "playwright"
            for left, mid, right in step_data
        )
        driver = (
            Shared_Resources.Get_Shared_Variables("playwright_page")
            if use_playwright
            else Shared_Resources.Get_Shared_Variables("selenium_driver")
        )

        if not driver:
            CommonUtil.ExecLog(sModuleInfo, "Driver (Playwright or Selenium) is not found in shared variables.", 3)
            return "zeuz_failed"

        Element = LocateElement.Get_Element(step_data, driver)
        if not Element or Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"

        text = Element.text_content() or "" if use_playwright else Element.text or ""

        ignore_case = False
        zeuz_ai = None
        expected_text_data = None
        validation_type = None

        for item in step_data:
            if item[1] == "action":
                expected_text_data = item[2]
                validation_type = item[0]
            elif item[1].strip().lower() == "optional parameter" and item[0].strip().lower() == "ignore case":
                ignore_case = item[2].strip().lower() in ("yes", "true", "ok")
            elif item[1].strip().lower() == "text classifier offset":
                zeuz_ai = [item[0].strip(), float(item[2])]

        if ignore_case:
            expected_text_data = expected_text_data.lower()
            text = text.lower()

        if zeuz_ai is not None:
            message = text
            labels = [zeuz_ai[0]]
            confidence = zeuz_ai[1]
            return binary_classification(message, labels, confidence)["status"]

        if validation_type == "validate partial text":
            if expected_text_data in text:
                CommonUtil.ExecLog(sModuleInfo, "The text has been validated by partial match.", 1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Unable to validate using partial match.", 3)
                return "zeuz_failed"

        elif validation_type == "validate full text":
            if expected_text_data == text:
                CommonUtil.ExecLog(sModuleInfo, "The text has been validated by complete match.", 1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Unable to validate using complete match.", 3)
                return "zeuz_failed"

        else:
            CommonUtil.ExecLog(sModuleInfo, "Incorrect validation type. Please check step data.", 3)
            return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

