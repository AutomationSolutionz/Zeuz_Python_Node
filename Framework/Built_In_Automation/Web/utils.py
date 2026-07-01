import hashlib
import inspect
import socket
import sys

from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from playwright.async_api import Browser, BrowserContext, Frame, Page
from selenium.webdriver import Chrome, Firefox, Edge, Safari



def initialize_browser_sessions():
    """
    Checks if `browser_sessions` shared variable is already initialized.
    If not, initializes it as an empty dictionary.
    """
    
    if sr.Test_Shared_Variables("browser_sessions") == False:
        sr.Set_Shared_Variables("browser_sessions", {})


def get_browser_sessions() -> dict:
    """Return the browser session registry, initializing it when needed."""

    if sr.Test_Shared_Variables("browser_sessions") == False:
        initialize_browser_sessions()

    browser_sessions = sr.Get_Shared_Variables("browser_sessions", log=False)
    if not isinstance(browser_sessions, dict):
        browser_sessions = {}
        sr.Set_Shared_Variables("browser_sessions", browser_sessions)

    return browser_sessions


def extract_session_name(step_data) -> str | None:
    """Return the optional browser session name from Zeuz step data."""

    if not step_data:
        return None

    for left, mid, right in step_data:
        left_l = left.replace(" ", "").replace("_", "").replace("-", "").lower()
        if left_l == "session" and mid.strip().lower() == "optional parameter":
            session_name = right.strip()
            return session_name or None

    return None


def remove_browser_session(session_name: str) -> dict | None:
    """Remove and return a browser session from the shared registry."""

    browser_sessions = get_browser_sessions()
    removed = browser_sessions.pop(session_name, None)
    sr.Set_Shared_Variables("browser_sessions", browser_sessions)
    return removed


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def get_debug_port(session_name: str, start: int = 9222, stop: int = 9322) -> int:
    """Pick an available CDP port, preferring a stable session-name hash."""

    used_ports = {
        session.get("remote_debugging_port")
        for session in get_browser_sessions().values()
        if isinstance(session, dict) and session.get("remote_debugging_port")
    }

    port_range = stop - start + 1
    port_hash = int(hashlib.md5(session_name.encode()).hexdigest(), 16)
    first = start + (port_hash % port_range)
    candidates = list(range(first, stop + 1)) + list(range(start, first))

    for port in candidates:
        if port not in used_ports and not is_port_in_use(port):
            return port

    raise RuntimeError(f"No available remote debugging port in range {start}-{stop}")


def create_browser_session(
    session_name: str = "default",
    selenium_driver: Chrome | Firefox | Edge | Safari | None = None,
    playwright_page: Page | None = None,
    playwright_browser: Browser | None = None,
    playwright_context: BrowserContext | None = None,
    playwright_frame: Frame | None = None,
    remote_debugging_port: int | None = None,
    playwright_instance = None,
) -> dict:
    """
    Creates a new browser session with the given parameters.
    Replaces the session if it already exists with the given name.
    
    Args:
        session_name (str): The name of the session.
        selenium_driver (Chrome | Firefox | Edge | Safari): The Selenium WebDriver instance.
        playwright_page (Page): The Playwright Page instance.
        playwright_browser (Browser): The Playwright Browser instance.
        playwright_context (BrowserContext): The Playwright BrowserContext instance.
        playwright_frame (Frame): The Playwright Frame instance.
    """
    
    browser_sessions = get_browser_sessions()
    browser_sessions[session_name] = {
        "selenium_driver": selenium_driver,
        "playwright_page": playwright_page,
        "playwright_browser": playwright_browser,
        "playwright_context": playwright_context,
        "playwright_frame": playwright_frame,
        "playwright_instance": playwright_instance,
        "remote_debugging_port": remote_debugging_port,
    }
    sr.Set_Shared_Variables("browser_sessions", browser_sessions)

    return browser_sessions[session_name]


def get_browser_session(session_name: str) -> dict:
    """
    Returns the browser session with the given name.
    
    Args:
        session_name (str): The name of the session.
    
    Returns:
        dict: The browser session with the given name.
    """
    
    browser_sessions = get_browser_sessions()
    return browser_sessions.get(session_name, {})


def _find_session_name_by_object(key: str, value) -> str | None:
    """Return the session name that owns the given browser object."""

    if value is None:
        return None

    for name, session in get_browser_sessions().items():
        if isinstance(session, dict) and session.get(key) is value:
            return name

    return None


def _resolve_browser_session_name(step_data=None) -> str | None:
    """Resolve the browser session to hydrate for custom Python code."""

    session_name = extract_session_name(step_data)
    if session_name:
        return session_name

    active_type = sr.shared_variables.get("active_web_driver_type")
    if active_type == "playwright":
        session_name = _find_session_name_by_object(
            "playwright_page", sr.shared_variables.get("playwright_page")
        )
        if session_name:
            return session_name
    elif active_type == "selenium":
        session_name = _find_session_name_by_object(
            "selenium_driver", sr.shared_variables.get("selenium_driver")
        )
        if session_name:
            return session_name

    session_name = _find_session_name_by_object(
        "playwright_page", sr.shared_variables.get("playwright_page")
    )
    if session_name:
        return session_name

    session_name = _find_session_name_by_object(
        "selenium_driver", sr.shared_variables.get("selenium_driver")
    )
    if session_name:
        return session_name

    if "default" in get_browser_sessions():
        return "default"

    return None


def _set_browser_shared_variables(session: dict):
    """Hydrate canonical browser shared variables from a session."""

    if session.get("selenium_driver") is not None:
        sr.Set_Shared_Variables(
            "selenium_driver", session["selenium_driver"], print_variable=False
        )
    if session.get("playwright_page") is not None:
        sr.Set_Shared_Variables(
            "playwright_page", session["playwright_page"], print_variable=False
        )
    if session.get("playwright_context") is not None:
        sr.Set_Shared_Variables(
            "playwright_context", session["playwright_context"], print_variable=False
        )
    if session.get("playwright_browser") is not None:
        sr.Set_Shared_Variables(
            "playwright_browser", session["playwright_browser"], print_variable=False
        )
    if session.get("playwright_frame") is not None:
        sr.Set_Shared_Variables(
            "playwright_frame", session["playwright_frame"], print_variable=False
        )


def _restore_active_web_driver_type(previous_active_type):
    if previous_active_type:
        sr.Set_Shared_Variables(
            "active_web_driver_type",
            previous_active_type,
            print_variable=False,
        )
    else:
        sr.Remove_From_Shared_Variables("active_web_driver_type")


def _align_selenium_to_playwright_page(session: dict):
    selenium_driver = session.get("selenium_driver")
    playwright_page = session.get("playwright_page")
    target_url = getattr(playwright_page, "url", None)

    if not selenium_driver or not target_url:
        return

    try:
        current_handle = selenium_driver.current_window_handle
        for handle in selenium_driver.window_handles:
            selenium_driver.switch_to.window(handle)
            if selenium_driver.current_url == target_url:
                return
        selenium_driver.switch_to.window(current_handle)
    except Exception:
        pass


async def _align_playwright_to_selenium_window(session_name: str, session: dict):
    selenium_driver = session.get("selenium_driver")
    playwright_context = session.get("playwright_context")

    if not selenium_driver or not playwright_context:
        return

    try:
        target_url = selenium_driver.current_url
    except Exception:
        return

    if not target_url:
        return

    try:
        for page in playwright_context.pages:
            if page.url == target_url:
                session["playwright_page"] = page
                sessions = get_browser_sessions()
                if session_name in sessions:
                    sessions[session_name]["playwright_page"] = page
                    sr.Set_Shared_Variables(
                        "browser_sessions", sessions, print_variable=False
                    )
                return
    except Exception:
        pass


async def hydrate_browser_compatibility_globals(step_data=None):
    """
    Populate canonical Selenium/Playwright shared variables for custom Python.

    This uses the existing lazy CDP bridge in the Selenium and Playwright action
    modules. It intentionally does not create user-facing convenience aliases.
    """

    sModuleInfo = "hydrate_browser_compatibility_globals : Web.utils"
    session_name = _resolve_browser_session_name(step_data)
    if not session_name:
        return "passed"

    session = get_browser_session(session_name)
    if not isinstance(session, dict) or not session:
        CommonUtil.ExecLog(
            sModuleInfo, f"Browser session '{session_name}' not found", 2
        )
        return "zeuz_failed"

    previous_active_type = sr.shared_variables.get("active_web_driver_type")

    try:
        if session.get("playwright_page") and not session.get("selenium_driver"):
            if session.get("selenium_cdp_supported") is False:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Selenium compatibility is only supported for Chromium Playwright sessions: {session_name}",
                    2,
                )
            else:
                from Framework.Built_In_Automation.Web.Selenium import (
                    BuiltInFunctions as SeleniumBuiltInFunctions,
                )

                result = SeleniumBuiltInFunctions._ensure_selenium_session(
                    session_name, session
                )
                if inspect.isawaitable(result):
                    result = await result
                if result in ("zeuz_failed", "failed", False):
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        f"Could not hydrate Selenium globals for browser session '{session_name}'",
                        2,
                    )

        session = get_browser_session(session_name)
        if session.get("selenium_driver") and not session.get("playwright_page"):
            if session.get("remote_debugging_port"):
                from Framework.Built_In_Automation.Web.Playwright import (
                    BuiltInFunctions as PlaywrightBuiltInFunctions,
                )

                result = await PlaywrightBuiltInFunctions._ensure_playwright_session(
                    session_name, session
                )
                if result in ("zeuz_failed", "failed", False):
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        f"Could not hydrate Playwright globals for browser session '{session_name}'",
                        2,
                    )
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Playwright compatibility requires a remote debugging port for session '{session_name}'",
                    2,
                )

        session = get_browser_session(session_name)
        if isinstance(session, dict):
            _align_selenium_to_playwright_page(session)
            await _align_playwright_to_selenium_window(session_name, session)

        if isinstance(session, dict):
            _set_browser_shared_variables(session)

        _restore_active_web_driver_type(previous_active_type)

        CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export())
        return "passed"
    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        _restore_active_web_driver_type(previous_active_type)
        return "zeuz_failed"
