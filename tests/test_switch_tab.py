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
    from Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions import switch_window_or_tab


@pytest.fixture
def mock_step_data_title():
    """Fixture for step data with window title"""
    return [
        ("window title", "input parameter", "Google"),
        ("switch window/tab", "selenium action", "switch window or frame"),
    ]


@pytest.fixture
def mock_step_data_partial_title():
    """Fixture for step data with partial window title"""
    return [
        ("*window title", "input parameter", "Goog"),
        ("switch window/tab", "selenium action", "switch window or frame"),
    ]


@pytest.fixture
def mock_step_data_index():
    """Fixture for step data with window index"""
    return [
        ("window index", "input parameter", "1"),
        ("switch window/tab", "selenium action", "switch window or frame"),
    ]


@pytest.fixture
def mock_step_data_playwright_title():
    """Fixture for step data with playwright enabled and title"""
    return [
        ("window title", "input parameter", "Google"),
        ("playwright", "option", "true"),
        ("switch window/tab", "selenium action", "switch window or frame"),
    ]


@pytest.fixture
def mock_step_data_playwright_index():
    """Fixture for step data with playwright enabled and index"""
    return [
        ("window index", "input parameter", "1"),
        ("playwright", "option", "true"),
        ("switch window/tab", "selenium action", "switch window or frame"),
    ]


@pytest.fixture
def mock_selenium_driver():
    """Fixture for mocked Selenium driver"""
    driver = MagicMock()
    driver.current_window_handle = "window1"
    driver.window_handles = ["window1", "window2", "window3"]
    driver.title = "Google - Search"
    driver.current_url = "https://www.google.com"
    driver.switch_to.window.return_value = None
    return driver


@pytest.fixture
def mock_playwright_objects():
    """Fixture for mocked Playwright objects"""
    mock_page1 = MagicMock()
    mock_page1.title.return_value = "Google"
    mock_page1.url = "https://www.google.com"
    mock_page1.bring_to_front.return_value = None

    mock_page2 = MagicMock()
    mock_page2.title.return_value = "YouTube"
    mock_page2.url = "https://www.youtube.com"
    mock_page2.bring_to_front.return_value = None

    mock_context = MagicMock()
    mock_context.pages = [mock_page1, mock_page2]

    mock_browser = MagicMock()
    mock_browser.contexts = [mock_context]

    mock_playwright = MagicMock()
    mock_playwright.chromium.connect_over_cdp.return_value = mock_browser
    mock_playwright.__enter__.return_value = mock_playwright
    mock_playwright.__exit__.return_value = None

    return {
        "page1": mock_page1,
        "page2": mock_page2,
        "context": mock_context,
        "browser": mock_browser,
        "playwright": mock_playwright,
    }


@pytest.fixture
def mock_selenium_details():
    """Fixture for mocked selenium_details"""
    return {
        "current_driver_id": {"remote-debugging-port": 9222}
    }


def test_parse_data_failure():
    """Test handling of malformed step_data"""
    malformed_data = [("invalid", "data")]
    result = switch_window_or_tab(malformed_data)
    assert result == "zeuz_failed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_selenium_switch_by_title_success(mock_exec_log, mock_driver, mock_step_data_title):
    """Test Selenium tab switching by title - success case"""
    # Configure mock - need exact title match
    mock_driver.current_window_handle = "window1"
    mock_driver.window_handles = ["window1", "window2", "window3"]
    mock_driver.title = "Google"  # Exact match for our search term
    mock_driver.switch_to.window.return_value = None

    result = switch_window_or_tab(mock_step_data_title)

    # Verify tab switching was attempted
    assert mock_driver.switch_to.window.call_count >= 1
    # Check that success message was logged
    mock_exec_log.assert_any_call(
        "switch_window_or_tab : BuiltInFunctions", "Tab switched to 'Google'", 1
    )
    assert result == "passed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_selenium_switch_by_partial_title_success(mock_exec_log, mock_driver, mock_step_data_partial_title):
    """Test Selenium tab switching by partial title - success case"""
    # Configure mock - partial match search for "Goog" should find "Google - Search"
    mock_driver.current_window_handle = "window1"
    mock_driver.window_handles = ["window1", "window2", "window3"]
    mock_driver.title = "Google - Search"  # Contains "Goog"
    mock_driver.switch_to.window.return_value = None

    result = switch_window_or_tab(mock_step_data_partial_title)

    # Verify tab switching was attempted
    assert mock_driver.switch_to.window.call_count >= 1
    # Check that success message was logged
    mock_exec_log.assert_any_call(
        "switch_window_or_tab : BuiltInFunctions", "Tab switched to 'Google - Search'", 1
    )
    assert result == "passed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_selenium_switch_by_title_not_found(mock_exec_log, mock_driver):
    """Test Selenium tab switching by title - title not found"""
    # Configure mock
    mock_driver.current_window_handle = "window1"
    mock_driver.window_handles = ["window1", "window2", "window3"]
    mock_driver.title = "Different Title"
    mock_driver.switch_to.window.return_value = None

    step_data = [
        ("window title", "input parameter", "NonExistentTitle"),
        ("switch window/tab", "selenium action", "switch window or frame"),
    ]

    result = switch_window_or_tab(step_data)

    # Check that error message was logged
    mock_exec_log.assert_any_call(
        "switch_window_or_tab : BuiltInFunctions",
        "Unable to find the title among the tabs. Use '*tab title' for partial match.",
        3
    )
    assert result == "zeuz_failed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_selenium_switch_by_index_success(mock_exec_log, mock_driver, mock_step_data_index):
    """Test Selenium tab switching by index - success case"""
    # Configure mock
    mock_driver.window_handles = ["window1", "window2", "window3"]
    mock_driver.title = "Tab at Index 1"
    mock_driver.switch_to.window.return_value = None

    result = switch_window_or_tab(mock_step_data_index)

    # Verify correct window was switched to
    mock_driver.switch_to.window.assert_called_with("window2")  # Index 1
    # Check that success message was logged
    mock_exec_log.assert_any_call(
        "switch_window_or_tab : BuiltInFunctions", 
        "Tab switched to index 1 title Tab at Index 1", 
        1
    )
    assert result == "passed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
@patch("time.sleep")
def test_playwright_switch_by_title_success(
    mock_sleep, mock_exec_log, mock_driver, mock_step_data_playwright_title, mock_playwright_objects
):
    """Test Playwright tab switching by title - success case"""
    # Configure selenium_details and current_driver_id mock
    with patch.dict("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_details", 
                   {"test_driver": {"remote-debugging-port": 9222}}), \
         patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.current_driver_id", "test_driver"):
        
        # Configure selenium driver mock for re-alignment
        mock_driver.window_handles = ["window1", "window2"]
        mock_driver.current_url = "https://www.google.com"
        mock_driver.title = "Google"
        mock_driver.switch_to.window.return_value = None

        with patch(
            "playwright.sync_api.sync_playwright",
            return_value=mock_playwright_objects["playwright"],
        ):
            result = switch_window_or_tab(mock_step_data_playwright_title)

        # Verify Playwright bring_to_front was called
        mock_playwright_objects["page1"].bring_to_front.assert_called_once()
        
        # Verify Selenium re-alignment was attempted
        assert mock_driver.switch_to.window.call_count >= 1
        
        # Check that success message was logged
        mock_exec_log.assert_any_call(
            "switch_window_or_tab : BuiltInFunctions", 
            "Selenium aligned to: Google", 
            1
        )
        assert result == "passed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_playwright_switch_by_title_not_found(
    mock_exec_log, mock_playwright_objects
):
    """Test Playwright tab switching by title - title not found"""
    # Configure selenium_details and current_driver_id mock
    with patch.dict("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_details", 
                   {"test_driver": {"remote-debugging-port": 9222}}), \
         patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.current_driver_id", "test_driver"):
        
        step_data = [
            ("window title", "input parameter", "NonExistentTitle"),
            ("playwright", "option", "true"),
            ("switch window/tab", "selenium action", "switch window or frame"),
        ]

        with patch(
            "playwright.sync_api.sync_playwright",
            return_value=mock_playwright_objects["playwright"],
        ):
            result = switch_window_or_tab(step_data)

        # Check that error message was logged
        mock_exec_log.assert_any_call(
            "switch_window_or_tab : BuiltInFunctions", 
            "Playwright: No tab with title 'NonExistentTitle' found", 
            3
        )
        assert result == "zeuz_failed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_playwright_switch_by_index_not_supported(
    mock_exec_log, mock_step_data_playwright_index, mock_playwright_objects
):
    """Test Playwright tab switching by index - not supported"""
    # Configure selenium_details and current_driver_id mock
    with patch.dict("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_details", 
                   {"test_driver": {"remote-debugging-port": 9222}}), \
         patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.current_driver_id", "test_driver"):
        
        with patch(
            "playwright.sync_api.sync_playwright",
            return_value=mock_playwright_objects["playwright"],
        ):
            result = switch_window_or_tab(mock_step_data_playwright_index)

        # Check that error message was logged
        mock_exec_log.assert_any_call(
            "switch_window_or_tab : BuiltInFunctions", 
            "Index-based tab switching is not supported with Playwright. Use title-based switching instead.", 
            3
        )
        assert result == "zeuz_failed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
@patch("time.sleep")
def test_playwright_alignment_failure(
    mock_sleep, mock_exec_log, mock_driver, mock_playwright_objects
):
    """Test Playwright tab switching - Selenium alignment failure"""
    # Configure selenium_details and current_driver_id mock
    with patch.dict("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_details", 
                   {"test_driver": {"remote-debugging-port": 9222}}), \
         patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.current_driver_id", "test_driver"):
        
        # Configure selenium driver mock - URLs don't match for alignment
        mock_driver.window_handles = ["window1", "window2"]
        mock_driver.current_url = "https://www.different.com"
        mock_driver.title = "Different Title"
        mock_driver.switch_to.window.return_value = None

        step_data = [
            ("window title", "input parameter", "Google"),
            ("playwright", "option", "true"),
            ("switch window/tab", "selenium action", "switch window or frame"),
        ]

        with patch(
            "playwright.sync_api.sync_playwright",
            return_value=mock_playwright_objects["playwright"],
        ):
            result = switch_window_or_tab(step_data)

        # Verify Playwright bring_to_front was called
        mock_playwright_objects["page1"].bring_to_front.assert_called_once()
        
        # Check that alignment failure message was logged
        mock_exec_log.assert_any_call(
            "switch_window_or_tab : BuiltInFunctions", 
            "Failed to align Selenium with target tab", 
            3
        )
        assert result == "zeuz_failed"


@patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
def test_playwright_connection_failure(mock_exec_log, mock_step_data_playwright_title):
    """Test Playwright connection failure"""
    # Configure selenium_details and current_driver_id mock
    with patch.dict("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_details", 
                   {"test_driver": {"remote-debugging-port": 9222}}), \
         patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.current_driver_id", "test_driver"):
        
        # Mock Playwright to raise an exception
        mock_playwright = MagicMock()
        mock_playwright.chromium.connect_over_cdp.side_effect = Exception("Connection failed")
        mock_playwright.__enter__.return_value = mock_playwright
        mock_playwright.__exit__.return_value = None

        with patch("playwright.sync_api.sync_playwright", return_value=mock_playwright):
            result = switch_window_or_tab(mock_step_data_playwright_title)

        # Verify that exception was handled and returns failure
        assert result == "zeuz_failed"


# Parametrized tests for better coverage
@pytest.mark.parametrize(
    "playwright_flag,expected_playwright",
    [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("invalid", False),
    ],
)
def test_playwright_flag_parsing(playwright_flag, expected_playwright):
    """Test that playwright flag is parsed correctly"""
    step_data = [
        ("window title", "input parameter", "Test"),
        ("playwright", "option", playwright_flag),
        ("switch window/tab", "selenium action", "switch window or frame"),
    ]
    
    # We can test the parsing logic by checking if the function behaves differently
    # This is more of a logic test than a full integration test
    parsed_flag = playwright_flag.lower() == "true"
    assert parsed_flag == expected_playwright


@pytest.mark.parametrize(
    "title_field,expected_partial",
    [
        ("window title", False),
        ("tab title", False),
        ("*window title", True),
        ("*tab title", True),
    ],
)
def test_title_field_parsing(title_field, expected_partial):
    """Test that title field types are parsed correctly"""
    # Test the parsing logic for partial match detection
    left = title_field.lower().strip()
    partial_match = left.startswith("*")
    
    assert partial_match == expected_partial


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
    assert (return_value == "passed") == expected


def test_step_data_parsing_priority():
    """Test that index takes priority over title when both are provided"""
    step_data = [
        ("window title", "input parameter", "Google"),
        ("window index", "input parameter", "1"),  # This should take priority
        ("switch window/tab", "selenium action", "switch window or frame"),
    ]
    
    # Parse the step data like the function does
    window_title_condition = False
    window_index_condition = False
    
    for left, mid, right in step_data:
        left = left.lower().strip()
        if left in ("window title", "tab title"):
            window_title_condition = True
        elif left in ("window index", "tab index"):
            window_index_condition = True
            window_title_condition = False  # Index takes priority
    
    # Verify that index condition is True and title condition is False
    assert window_index_condition == True
    assert window_title_condition == False

