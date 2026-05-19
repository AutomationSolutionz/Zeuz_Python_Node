import hashlib
import socket

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
