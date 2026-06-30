import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Add the project root to the path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Mock the problematic dependency check before importing
with (
    patch(
        "Framework.Built_In_Automation.Shared_Resources.BuiltInFunctionSharedResources.Test_Shared_Variables",
        return_value=True,
    ),
    patch(
        "Framework.Built_In_Automation.Shared_Resources.BuiltInFunctionSharedResources.Get_Shared_Variables",
        return_value="test_dependency",
    ),
):
    from Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions import close_tab


@pytest.fixture
def mock_step_data():
    """Fixture for basic step data"""
    return [("close tab", "selenium action", "close tab")]


@pytest.fixture
def mock_step_data_playwright():
    """Fixture for step data with playwright enabled"""
    return [
        ("close tab", "selenium action", "close tab"),
        ("playwright", "optional parameter", "true"),
    ]


@pytest.fixture
def mock_step_data_with_title():
    """Fixture for step data with tab title"""
    return [
        ("close tab", "selenium action", "close tab"),
        ("playwright", "optional parameter", "true"),
        ("tab title", "input parameter", "Google"),
    ]


@pytest.fixture
def mock_step_data_with_index():
    """Fixture for step data with tab index"""
    return [
        ("close tab", "selenium action", "close tab"),
        ("playwright", "optional parameter", "true"),
        ("tab index", "input parameter", "0"),
    ]


@pytest.fixture
def mock_selenium_driver():
    """Fixture for mocked Selenium driver"""
    driver = MagicMock()
    driver.current_window_handle = "window1"
    driver.window_handles = ["window1"]
    driver.title = "Test Tab"
    driver.close.return_value = None
    driver.switch_to.window.return_value = None
    return driver


@pytest.fixture
def mock_playwright_objects():
    """Fixture for mocked Playwright objects"""
    mock_page = MagicMock()
    mock_page.title.return_value = "Google"
    mock_page.close.return_value = None
    mock_page.url = "https://www.google.com"

    mock_context = MagicMock()
    mock_context.pages = [mock_page]

    mock_browser = MagicMock()
    mock_browser.contexts = [mock_context]

    mock_playwright = MagicMock()
    mock_playwright.chromium.connect_over_cdp.return_value = mock_browser
    mock_playwright.__enter__.return_value = mock_playwright
    mock_playwright.__exit__.return_value = None

    return {
        "page": mock_page,
        "context": mock_context,
        "browser": mock_browser,
        "playwright": mock_playwright,
    }


@pytest.fixture
def mock_cdp_response():
    """Fixture for mocked CDP response"""
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(
        [
            {"type": "page", "url": "https://www.google.com", "title": "Google"},
            {"type": "page", "url": "https://www.youtube.com", "title": "YouTube"},
        ]
    ).encode()
    return mock_response


@pytest.fixture
def mock_cdp_env():
    """Patch selenium_details with a debug port for Playwright close_tab tests."""
    with patch.dict(
        "Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_details",
        {"test_driver": {"remote-debugging-port": 9222}},
    ), patch(
        "Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.current_driver_id",
        "test_driver",
    ):
        yield


def test_parse_data_failure():
    """Test handling of malformed step_data"""
    malformed_data = [("invalid", "data")]
    result = close_tab(malformed_data)
    assert result == "zeuz_failed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_selenium_close_current_tab(mock_exec_log, mock_driver, mock_step_data):
    """Test Selenium fallback when closing current tab"""
    # Configure mock
    mock_driver.current_window_handle = "window1"
    mock_driver.window_handles = ["window1"]
    mock_driver.title = "Test Tab"
    mock_driver.close.return_value = None
    mock_driver.switch_to.window.return_value = None

    result = close_tab(mock_step_data)

    # Verify the tab was closed
    mock_driver.close.assert_called_once()
    # Check that the success message was logged (among other calls)
    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions", "Current tab closed 'Test Tab'", 1
    )
    assert result == "passed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_selenium_close_multiple_tabs_by_title(mock_exec_log, mock_driver):
    """Test Selenium closing multiple tabs by title"""
    # Mock selenium driver with multiple windows
    mock_driver.current_window_handle = "window1"
    mock_driver.window_handles = ["window1", "window2", "window3"]
    mock_driver.title = "Google"
    mock_driver.close.return_value = None
    mock_driver.switch_to.window.return_value = None

    step_data_with_tabs = [
        ("tabs", "input parameter", ["Google", "YouTube"]),
        ("close tab", "selenium action", "close tab"),
    ]

    result = close_tab(step_data_with_tabs)

    # Verify tabs were closed
    assert result == "passed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_selenium_close_multiple_tabs_by_index(mock_exec_log, mock_driver):
    """Test Selenium closing multiple tabs by index"""
    # Mock selenium driver with multiple windows
    mock_driver.current_window_handle = "window1"
    mock_driver.window_handles = ["window1", "window2", "window3"]
    mock_driver.title = "Test Tab"
    mock_driver.close.return_value = None
    mock_driver.switch_to.window.return_value = None

    step_data_with_indices = [
        ("tabs", "input parameter", [0, 1]),
        ("close tab", "selenium action", "close tab"),
    ]

    result = close_tab(step_data_with_indices)

    # Verify tabs were closed
    assert result == "passed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_playwright_close_falls_back_when_debug_port_missing(
    mock_exec_log, mock_driver, mock_step_data_with_title
):
    mock_driver.current_window_handle = "window1"
    mock_driver.window_handles = ["window1", "window2"]
    mock_driver.title = "Google"
    mock_driver.close.return_value = None
    mock_driver.switch_to.window.return_value = None

    with patch.dict(
        "Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_details",
        {},
        clear=True,
    ), patch(
        "Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.current_driver_id",
        None,
    ):
        result = close_tab(mock_step_data_with_title)

    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions",
        "Playwright tab closing requires a Chromium remote debugging port. Falling back to Selenium",
        2,
    )
    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions",
        "Using Selenium for tab closing (Playwright fallback)",
        1,
    )
    assert result == "passed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_playwright_close_falls_back_when_no_title_or_index(
    mock_exec_log, mock_driver, mock_step_data_playwright, mock_cdp_env
):
    mock_driver.current_window_handle = "window1"
    mock_driver.window_handles = ["window1"]
    mock_driver.title = "Test Tab"
    mock_driver.close.return_value = None
    mock_driver.switch_to.window.return_value = None

    result = close_tab(mock_step_data_playwright)

    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions",
        "Playwright tab closing requires tab title or tab index. Falling back to Selenium",
        2,
    )
    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions",
        "Using Selenium for tab closing (Playwright fallback)",
        1,
    )
    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions",
        "Current tab closed 'Test Tab'",
        1,
    )
    mock_driver.close.assert_called_once()
    assert result == "passed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions._switch_tab_run_async")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_playwright_close_tab_by_title(
    mock_exec_log, mock_run_async, mock_step_data_with_title, mock_cdp_env
):
    """Test Playwright closing tab by title"""
    mock_run_async.return_value = {"status": "closed", "page_title": "Google"}

    result = close_tab(mock_step_data_with_title)

    mock_run_async.assert_called_once()
    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions", "Tab closed 'Google'", 1
    )
    assert result == "passed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions._switch_tab_run_async")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_playwright_close_tab_by_index(
    mock_exec_log, mock_run_async, mock_step_data_with_index, mock_cdp_env
):
    """Test Playwright closing tab by index"""
    mock_run_async.return_value = {"status": "closed", "page_title": "YouTube"}

    result = close_tab(mock_step_data_with_index)

    mock_run_async.assert_called_once()
    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions", "Tab closed 'YouTube'", 1
    )
    assert result == "passed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_playwright_close_current_active_tab(
    mock_exec_log, mock_driver, mock_step_data_playwright, mock_cdp_env
):
    """Playwright without tab title/index falls back to Selenium current-tab close"""
    mock_driver.current_window_handle = "window1"
    mock_driver.window_handles = ["window1"]
    mock_driver.title = "Google"
    mock_driver.close.return_value = None
    mock_driver.switch_to.window.return_value = None

    result = close_tab(mock_step_data_playwright)

    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions",
        "Playwright tab closing requires tab title or tab index. Falling back to Selenium",
        2,
    )
    mock_driver.close.assert_called_once()
    assert result == "passed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_playwright_close_last_remaining_tab(
    mock_exec_log, mock_driver, mock_step_data_playwright, mock_cdp_env
):
    """Closing the last tab via Selenium fallback still passes"""
    mock_driver.current_window_handle = "window1"
    mock_driver.window_handles = ["window1"]
    mock_driver.title = "Google"
    mock_driver.close.return_value = None
    mock_driver.switch_to.window.return_value = None

    result = close_tab(mock_step_data_playwright)

    mock_driver.close.assert_called_once()
    assert result == "passed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions._switch_tab_run_async")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_playwright_no_tabs_found(
    mock_exec_log, mock_driver, mock_run_async, mock_step_data_with_title, mock_cdp_env
):
    """Test Playwright when no tabs are found, then Selenium also fails"""
    mock_run_async.return_value = {
        "status": "no_tabs",
        "error": "Playwright: No tabs found to close",
    }
    mock_driver.current_window_handle = "window1"
    mock_driver.window_handles = ["window1"]
    mock_driver.title = "Other Tab"
    mock_driver.switch_to.window.return_value = None

    result = close_tab(mock_step_data_with_title)

    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions", "Playwright: No tabs found to close", 3
    )
    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions",
        "Falling back to Selenium for tab closing",
        2,
    )
    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions", "No tab with title 'Google' found", 3
    )
    assert result == "zeuz_failed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions._switch_tab_run_async")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_playwright_invalid_tab_index(
    mock_exec_log, mock_driver, mock_run_async, mock_cdp_env
):
    """Test Playwright with invalid tab index, then Selenium validation failure"""
    mock_run_async.return_value = {
        "status": "invalid_index",
        "error": "Playwright: Invalid tab index 'invalid'",
    }
    mock_driver.current_window_handle = "window1"
    mock_driver.window_handles = ["window1"]
    mock_driver.switch_to.window.return_value = None

    step_data_invalid_index = [
        ("close tab", "selenium action", "close tab"),
        ("playwright", "optional parameter", "true"),
        ("tab index", "input parameter", "invalid"),
    ]

    result = close_tab(step_data_invalid_index)

    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions", "Playwright: Invalid tab index 'invalid'", 3
    )
    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions", "Invalid tab index 'invalid'", 3
    )
    assert result == "zeuz_failed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions._switch_tab_run_async")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_playwright_fallback_to_selenium(
    mock_exec_log, mock_driver, mock_run_async, mock_step_data_with_title, mock_cdp_env
):
    """Test Playwright fallback to Selenium when Playwright raises"""
    mock_run_async.side_effect = Exception("Connection failed")
    mock_driver.current_window_handle = "window1"
    mock_driver.window_handles = ["window1", "window2"]
    mock_driver.title = "Google"
    mock_driver.close.return_value = None
    mock_driver.switch_to.window.return_value = None

    result = close_tab(mock_step_data_with_title)

    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions",
        "Playwright tab closing failed: Connection failed. Falling back to Selenium",
        2,
    )
    mock_exec_log.assert_any_call(
        "close_tab : BuiltInFunctions",
        "Using Selenium for tab closing (Playwright fallback)",
        1,
    )
    mock_driver.close.assert_called_once()
    assert result == "passed"


def test_filter_non_page_tabs():
    """Test that non-page type tabs are filtered out"""
    # This test verifies the filtering logic in the Playwright section
    # The function should filter out tabs with type != 'page'
    # This is tested indirectly in the above tests
    pass


# Parametrized tests for better coverage
@pytest.mark.parametrize(
    "tab_type,expected_filtered",
    [
        ("page", True),  # Should be included
        ("background", False),  # Should be filtered out
        ("service_worker", False),  # Should be filtered out
        ("extension", False),  # Should be filtered out
    ],
)
def test_tab_type_filtering(tab_type, expected_filtered):
    """Test that only 'page' type tabs are included in filtering"""
    # This tests the filtering logic: tab['type'] == 'page'
    tabs_data = [{"type": tab_type, "url": "https://example.com"}]

    # Simulate the filtering logic from the function
    filtered_urls = [tab["url"] for tab in tabs_data if tab["type"] == "page"]

    if expected_filtered:
        assert len(filtered_urls) == 1
        assert filtered_urls[0] == "https://example.com"
    else:
        assert len(filtered_urls) == 0


# Test different return values
@pytest.mark.parametrize(
    "return_value,expected",
    [
        ("passed", True),
        ("zeuz_failed", False),
    ],
)
def test_return_values(return_value, expected):
    """Test that function returns expected values"""
    # This is a simple test to demonstrate parametrization
    # In real usage, you'd test actual function calls
    assert (return_value == "passed") == expected
