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


def create_browser_session(
    session_name: str = "default",
    selenium_driver: Chrome | Firefox | Edge | Safari | None = None,
    playwright_page: Page | None = None,
    playwright_browser: Browser | None = None,
    playwright_context: BrowserContext | None = None,
    playwright_frame: Frame | None = None
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
    
    if sr.Test_Shared_Variables("browser_sessions") == False:
        initialize_browser_sessions()
    
    browser_sessions = sr.Get_Shared_Variables("browser_sessions")
    browser_sessions[session_name] = {
        "selenium_driver": selenium_driver,
        "playwright_page": playwright_page,
        "playwright_browser": playwright_browser,
        "playwright_context": playwright_context,
        "playwright_frame": playwright_frame
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
    
    if sr.Test_Shared_Variables("browser_sessions") == False:
        initialize_browser_sessions()
    
    browser_sessions = sr.Get_Shared_Variables("browser_sessions")
    return browser_sessions.get(session_name, {})
