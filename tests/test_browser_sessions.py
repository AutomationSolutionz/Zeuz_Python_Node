import asyncio
import base64
import json
import struct
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

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

    result = asyncio.run(
        playwright_bif._activate_browser_session_for_action(
            [("session", "optional parameter", "buyer")],
            "Hover_Over_Element",
        )
    )

    assert result == "passed"
    assert playwright_bif.current_page is page
    assert playwright_bif.context is context
    assert playwright_bif.browser is browser
    assert playwright_bif.current_page_id == "buyer"
    assert sr.Get_Shared_Variables("playwright_frame") is frame
    assert sr.Get_Shared_Variables("active_web_driver_type") == "playwright"


def test_playwright_missing_explicit_session_fails_non_create_action():
    result = asyncio.run(
        playwright_bif._activate_browser_session_for_action(
            [("session", "optional parameter", "missing")],
            "Validate_Text",
        )
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
    page.locator.return_value.count = AsyncMock(return_value=2)
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


def test_playwright_uses_shared_cft_pair_for_selenium_attachment(monkeypatch):
    monkeypatch.setattr(playwright_bif.CommonUtil, "ExecLog", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        playwright_bif.CommonUtil,
        "set_screenshot_vars",
        lambda *args, **kwargs: None,
    )
    normalize = playwright_bif.ChromeForTesting.normalize_version_and_channel
    assert normalize("138.0.7204.92") == ("138.0.7204.92", "Stable")
    for channel in ("Stable", "Beta", "Dev", "Canary"):
        assert normalize(channel.lower()) == (None, channel)

    chrome_bin = Path("/cache/chrome")
    driver_bin = Path("/cache/chromedriver")
    cft = MagicMock()
    cft.setup_chrome_for_testing.return_value = (chrome_bin, driver_bin)
    monkeypatch.setattr(playwright_bif, "ChromeForTesting", lambda: cft)

    async def run_inline(function, *args):
        return function(*args)

    monkeypatch.setattr(playwright_bif.asyncio, "to_thread", run_inline)
    monkeypatch.setattr(playwright_bif, "get_debug_port", lambda session_name: 9250)

    page = MagicMock()
    context = MagicMock()
    context.pages = []
    context.new_page = AsyncMock(return_value=page)
    browser = MagicMock()
    context.browser = browser
    browser.new_context = AsyncMock(return_value=context)
    playwright = MagicMock()
    playwright.devices = {
        "Test Phone": {
            "default_browser_type": "chromium",
            "viewport": {"width": 390, "height": 844},
            "device_scale_factor": 2,
            "is_mobile": True,
            "has_touch": True,
            "user_agent": "Test Phone",
        }
    }
    playwright.chromium.launch = AsyncMock(return_value=browser)
    playwright.chromium.launch_persistent_context = AsyncMock(return_value=context)
    starter = MagicMock()
    starter.start = AsyncMock(return_value=playwright)
    monkeypatch.setattr(playwright_bif, "async_playwright", lambda: starter)
    extension_args = [
        "--disable-features=DisableLoadExtensionCommandLineSwitch",
        f"--disable-extensions-except={selenium_bif.aiplugin_path},{selenium_bif.ai_recorder_path}",
        f"--load-extension={selenium_bif.aiplugin_path},{selenium_bif.ai_recorder_path}",
        "--allow-running-insecure-content",
    ]
    prepare_extensions = MagicMock()
    monkeypatch.setattr(selenium_bif.CommonUtil, "debug_status", True)
    monkeypatch.setattr(
        selenium_bif.ConfigModule,
        "get_config_value",
        lambda section, key, *args: "true"
        if (section, key) == ("Inspector", "ai_plugin")
        else "",
    )
    monkeypatch.setattr(selenium_bif, "set_extension_variables", prepare_extensions)
    sr.Set_Shared_Variables("dependency", {"Browser": "Chrome"})

    result = asyncio.run(
        playwright_bif.Open_Browser(
            [
                ("chrome:version", "optional parameter", "138.0.7204.92"),
                ("add argument", "chromium option", "['--disable-gpu']"),
                (
                    "add experimental option",
                    "chromium option",
                    "{'prefs': {'profile.test': 1}, "
                    "'excludeSwitches': ['disable-popup-blocking'], "
                    "'mobileEmulation': {'deviceName': 'Test Phone'}}",
                ),
                (
                    "set preference",
                    "chrome option",
                    "{'download.prompt_for_download': False}",
                ),
                ("page load strategy", "chromium option", "normal"),
                ("wait for element", "optional parameter", "17"),
                (
                    "capabilities",
                    "shared capability",
                    "{'acceptInsecureCerts': True, "
                    "'proxy': {'httpProxy': 'proxy.test:8080'}}",
                ),
            ]
        )
    )

    assert result == "passed"
    cft.setup_chrome_for_testing.assert_called_once_with("138.0.7204.92", None)
    launch_options = playwright.chromium.launch_persistent_context.await_args.kwargs
    assert launch_options["executable_path"] == str(chrome_bin)
    assert launch_options["headless"] is False
    assert "--disable-gpu" in launch_options["args"]
    assert launch_options["ignore_default_args"] == ["--disable-popup-blocking"]
    assert launch_options["ignore_https_errors"] is True
    assert launch_options["viewport"] == {"width": 390, "height": 844}
    assert launch_options["proxy"] == {"server": "http://proxy.test:8080"}
    assert set(selenium_bif.DEFAULT_CHROMIUM_ARGUMENTS + tuple(extension_args)) <= set(
        launch_options["args"]
    )
    prepare_extensions.assert_called_once_with()
    playwright.chromium.launch.assert_not_awaited()
    session = browser_utils.get_browser_session("default")
    assert session["driver_path"] == str(driver_bin)
    assert session["playwright_wait_until"] == "load"
    assert sr.Get_Shared_Variables("element_wait") == 17
    user_data_dir = playwright.chromium.launch_persistent_context.await_args.args[0]
    preferences = json.loads(
        (Path(user_data_dir) / "Default" / "Preferences").read_text()
    )
    assert preferences["profile"]["test"] == 1
    assert preferences["download"]["prompt_for_download"] is False
    assert asyncio.run(playwright_bif.Open_Browser([])) == "passed"
    cft.setup_chrome_for_testing.assert_called_once()
    playwright.chromium.launch_persistent_context.assert_awaited_once()

    selenium_driver = object()
    attach = MagicMock(return_value=selenium_driver)
    monkeypatch.setattr(playwright_bif, "connect_selenium_to_playwright", attach)
    assert selenium_bif._ensure_selenium_session("default", session) == "passed"
    attach.assert_called_once_with(port=9250, driver_path=str(driver_bin))
    playwright_bif._cleanup_chrome_profile(user_data_dir)


def test_playwright_unpacks_crx_and_encoded_extensions(monkeypatch, tmp_path):
    monkeypatch.setattr(
        playwright_bif.ChromeExtensionDownloader,
        "CHROME_EXTENSIONS_DIR",
        tmp_path / "cache",
    )
    zip_path = tmp_path / "extension.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("manifest.json", '{"manifest_version": 3, "name": "Test"}')
    crx_payload = b"Cr24" + struct.pack("<II", 3, 0) + zip_path.read_bytes()
    crx_path = tmp_path / "extension.crx"
    crx_path.write_bytes(crx_payload)

    extension_dirs = playwright_bif._unpack_playwright_extensions(
        [crx_path],
        [base64.b64encode(crx_payload).decode()],
    )

    assert len(extension_dirs) == 1
    assert (Path(extension_dirs[0]) / "manifest.json").is_file()


def test_playwright_supports_selenium_debugger_address(monkeypatch):
    monkeypatch.setattr(playwright_bif.CommonUtil, "ExecLog", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        playwright_bif.CommonUtil,
        "set_screenshot_vars",
        lambda *args, **kwargs: None,
    )
    cft_factory = MagicMock(side_effect=AssertionError("CfT should not be resolved"))
    monkeypatch.setattr(playwright_bif, "ChromeForTesting", cft_factory)
    page = MagicMock()
    context = MagicMock()
    context.pages = [page]
    browser = MagicMock()
    browser.contexts = [context]
    playwright = MagicMock()
    playwright.chromium.connect_over_cdp = AsyncMock(return_value=browser)
    starter = MagicMock()
    starter.start = AsyncMock(return_value=playwright)
    monkeypatch.setattr(playwright_bif, "async_playwright", lambda: starter)
    sr.Set_Shared_Variables("dependency", {"Browser": "Chrome"})

    result = asyncio.run(
        playwright_bif.Open_Browser(
            [
                (
                    "debugger address",
                    "chromium option",
                    "127.0.0.1:9333",
                )
            ]
        )
    )

    assert result == "passed"
    cft_factory.assert_not_called()
    playwright.chromium.connect_over_cdp.assert_awaited_once_with(
        "http://127.0.0.1:9333"
    )
    assert browser_utils.get_browser_session("default")["remote_debugging_port"] == 9333


def test_playwright_restores_non_cft_browser_launches(monkeypatch):
    monkeypatch.setattr(playwright_bif.CommonUtil, "ExecLog", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        playwright_bif.CommonUtil,
        "set_screenshot_vars",
        lambda *args, **kwargs: None,
    )
    installer = MagicMock(return_value=True)
    monkeypatch.setattr(
        playwright_bif.PlaywrightUtils,
        "ensure_playwright_browser_installed",
        installer,
    )
    cft_factory = MagicMock(side_effect=AssertionError("CfT should not be resolved"))
    monkeypatch.setattr(playwright_bif, "ChromeForTesting", cft_factory)
    monkeypatch.setattr(playwright_bif, "get_debug_port", lambda session_name: 9250)

    async def run_inline(function, *args):
        return function(*args)

    monkeypatch.setattr(playwright_bif.asyncio, "to_thread", run_inline)

    launches = {}
    for requested_browser, browser_type_name in (
        ("FirefoxHeadless", "firefox"),
        ("webkit", "webkit"),
        ("safari", "webkit"),
        ("edge", "chromium"),
    ):
        sr.shared_variables.clear()
        playwright_bif.current_page = None
        playwright_bif.current_page_id = None
        playwright_bif.context = None
        playwright_bif.browser = None

        page = MagicMock()
        context = MagicMock()
        context.pages = []
        context.new_page = AsyncMock(return_value=page)
        browser = MagicMock()
        browser.new_context = AsyncMock(return_value=context)
        playwright = MagicMock()
        for name in ("chromium", "firefox", "webkit"):
            getattr(playwright, name).launch = AsyncMock(return_value=browser)
        starter = MagicMock()
        starter.start = AsyncMock(return_value=playwright)
        monkeypatch.setattr(playwright_bif, "async_playwright", lambda: starter)

        result = asyncio.run(
            playwright_bif.Open_Browser(
                [("browser", "input parameter", requested_browser)]
            )
        )

        assert result == "passed"
        launch = getattr(playwright, browser_type_name).launch
        launch.assert_awaited_once()
        launches[requested_browser] = launch.await_args.kwargs
        session = browser_utils.get_browser_session("default")
        assert session["selenium_cdp_supported"] is False
        assert session["driver_path"] is None

    assert installer.call_args_list[0].args[1] == "firefox"
    assert installer.call_args_list[1].args[1] == "webkit"
    assert installer.call_args_list[2].args[1] == "safari"
    assert installer.call_args_list[3].args[1] == "edge"
    assert launches["FirefoxHeadless"]["headless"] is True
    assert launches["edge"]["channel"] == "msedge"
    cft_factory.assert_not_called()
