import asyncio
from unittest.mock import MagicMock

from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from Framework.Built_In_Automation.Web import utils as browser_utils
from Framework.Built_In_Automation.Web.Playwright import BuiltInFunctions as playwright_bif

sr.Set_Shared_Variables("dependency", {"Browser": "chrome"})
from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as selenium_bif  # noqa: E402


def setup_function():
    sr.shared_variables.clear()
    selenium_bif.selenium_driver = None
    selenium_bif.current_driver_id = None
    selenium_bif.selenium_details = {}
    playwright_bif.current_page = None
    playwright_bif.current_page_id = None
    playwright_bif.context = None
    playwright_bif.browser = None
    playwright_bif.playwright_details = {}


def test_selenium_session_activation_selects_driver():
    driver = MagicMock()
    browser_utils.create_browser_session(
        session_name="admin",
        selenium_driver=driver,
        remote_debugging_port=9231,
    )

    result = selenium_bif._activate_browser_session_for_action(
        [("session", "optional parameter", "admin")],
        "Click_Element",
    )

    assert result == "passed"
    assert selenium_bif.selenium_driver is driver
    assert selenium_bif.current_driver_id == "admin"
    assert sr.Get_Shared_Variables("selenium_driver") is driver
    assert sr.Get_Shared_Variables("active_web_driver_type") == "selenium"
    assert selenium_bif.selenium_details["admin"]["remote-debugging-port"] == 9231


def test_selenium_missing_explicit_session_fails_non_create_action():
    result = selenium_bif._activate_browser_session_for_action(
        [("session", "optional parameter", "missing")],
        "Click_Element",
    )

    assert result == "zeuz_failed"


def test_selenium_missing_explicit_session_allowed_for_browser_creation():
    result = selenium_bif._activate_browser_session_for_action(
        [("session", "optional parameter", "new_user")],
        "Go_To_Link",
    )

    assert result == "passed"


def test_playwright_session_activation_selects_page_and_frame():
    page = MagicMock()
    context = MagicMock()
    browser = MagicMock()
    frame = MagicMock()
    selenium_driver = MagicMock()
    browser_utils.create_browser_session(
        session_name="buyer",
        selenium_driver=selenium_driver,
        playwright_page=page,
        playwright_context=context,
        playwright_browser=browser,
        playwright_frame=frame,
    )

    result = playwright_bif._activate_browser_session_for_action(
        [("session", "optional parameter", "buyer")],
        "Hover_Over_Element",
    )

    assert result == "passed"
    assert playwright_bif.current_page is page
    assert playwright_bif.context is context
    assert playwright_bif.browser is browser
    assert playwright_bif.current_page_id == "buyer"
    assert sr.Get_Shared_Variables("playwright_frame") is frame
    assert sr.Get_Shared_Variables("active_web_driver_type") == "playwright"


def test_playwright_missing_explicit_session_fails_non_create_action():
    result = playwright_bif._activate_browser_session_for_action(
        [("session", "optional parameter", "missing")],
        "Validate_Text",
    )

    assert result == "zeuz_failed"


def test_remove_browser_session_updates_registry():
    browser_utils.create_browser_session("temp", selenium_driver=MagicMock())

    removed = browser_utils.remove_browser_session("temp")

    assert removed is not None
    assert browser_utils.get_browser_session("temp") == {}


def test_selenium_global_teardown_preserves_playwright_owned_sessions(monkeypatch):
    selenium_driver = MagicMock()
    context = MagicMock()
    browser = MagicMock()
    browser_utils.create_browser_session(
        session_name="playwright_session",
        selenium_driver=selenium_driver,
        playwright_page=MagicMock(),
        playwright_context=context,
        playwright_browser=browser,
    )
    monkeypatch.setattr(
        "Framework.Utilities.CommonUtil.Join_Thread_and_Return_Result",
        lambda key: [],
    )

    result = selenium_bif.Tear_Down_Selenium([])

    assert result == "passed"
    assert browser_utils.get_browser_session("playwright_session")
    context.close.assert_not_called()
    browser.close.assert_not_called()


def test_playwright_switch_iframe_uses_index_parameter_after_default_reset():
    frame_locator = MagicMock()
    indexed_frame_locator = MagicMock()
    frame_locator.nth.return_value = indexed_frame_locator
    page = MagicMock()
    page.frame_locator.return_value = frame_locator
    playwright_bif.current_page = page
    playwright_bif.current_page_id = "default"
    browser_utils.create_browser_session(
        session_name="default",
        playwright_page=page,
        playwright_context=MagicMock(),
        playwright_browser=MagicMock(),
    )

    result = asyncio.run(
        playwright_bif.switch_iframe(
            [
                ("index", "iframe parameter", "default content"),
                ("index", "iframe parameter", "1"),
                ("switch iframe", "playwright action", "switch iframe"),
            ]
        )
    )

    assert result == "passed"
    page.frame_locator.assert_called_once_with("iframe")
    frame_locator.nth.assert_called_once_with(1)
    assert sr.Get_Shared_Variables("playwright_frame") is indexed_frame_locator
    assert browser_utils.get_browser_session("default")["playwright_frame"] is indexed_frame_locator
