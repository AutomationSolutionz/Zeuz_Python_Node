import shutil
import threading
import time
from types import SimpleNamespace

import pytest

from Framework.Built_In_Automation.Sequential_Actions.action_declarations.playwright import (
    declarations,
)
from Framework.Built_In_Automation.Shared_Resources import LocateElement
from Framework.Built_In_Automation.Web.Playwright import (
    BuiltInFunctions as playwright_actions,
)
from Framework.Built_In_Automation.Sequential_Actions import sequential_actions


def test_declaration_parity_and_callables():
    excluded = {
        "click and hold",
        "validate table",
        "validate table row size",
        "validate table column size",
        "playwright",
    }
    from Framework.Built_In_Automation.Sequential_Actions.action_declarations.selenium import (
        declarations as selenium,
    )

    assert len(declarations) == 55
    assert {item["name"] for item in declarations} == {
        item["name"] for item in selenium
    } - excluded
    assert all(
        callable(getattr(playwright_actions, item["function"], None))
        for item in declarations
    )
    assert (
        sum(
            item["module"] == "playwright"
            for item in sequential_actions.actions.values()
        )
        == 55
    )


def test_backend_routing(monkeypatch):
    values = {}
    monkeypatch.setattr(
        sequential_actions.sr,
        "Get_Shared_Variables",
        lambda name, **_: values.get(name, "zeuz_failed"),
    )

    assert (
        sequential_actions._route_playwright_action("click", "selenium action", [])
        == "selenium action"
    )
    assert (
        sequential_actions._route_playwright_action("", "selenium conditional action", [])
        == "selenium conditional action"
    )
    values["zeuz_browser_driver"] = "PlAyWrIgHt"
    assert (
        sequential_actions._route_playwright_action("click", "selenium action", [])
        == "playwright action"
    )
    assert (
        sequential_actions._route_playwright_action("", "selenium conditional action", [])
        == "playwright conditional action"
    )
    assert (
        sequential_actions._route_playwright_action("", "playwright conditional action", [])
        == "playwright conditional action"
    )
    assert (
        sequential_actions._route_playwright_action("click", "playwright action", [])
        == "playwright action"
    )
    assert (
        sequential_actions._route_playwright_action(
            "open electron app", "selenium action", []
        )
        == "selenium action"
    )
    assert (
        sequential_actions._route_playwright_action(
            "open electron app", "playwright action", []
        )
        == "selenium action"
    )
    assert (
        sequential_actions._route_playwright_action(
            "accessibility test", "playwright action", []
        )
        == "selenium action"
    )
    values["zeuz_active_browser_backend"] = "selenium"
    values["zeuz_browser_backends"] = {"electron": "selenium", "web": "playwright"}
    assert (
        sequential_actions._route_playwright_action("click", "selenium action", [])
        == "selenium action"
    )
    assert (
        sequential_actions._route_playwright_action(
            "switch browser",
            "selenium action",
            [("driver_id", "optional parameter", "web")],
        )
        == "playwright action"
    )


def test_routed_common_wait_receives_normalized_action_row(monkeypatch):
    rows = [
        ("*class", "parent parameter", "navbar-expand-lg container-fluid navbar"),
        ("*class", "element parameter", "small-nav"),
        ("wait", "selenium action", "30"),
    ]
    captured = []
    values = {
        "zeuz_browser_driver": "playwright",
        "zeuz_prettify_limit": 500,
        "action_timeout": 5,
    }
    monkeypatch.setattr(
        sequential_actions.sr,
        "Get_Shared_Variables",
        lambda name, **_: values.get(name, "zeuz_failed"),
    )
    monkeypatch.setattr(
        sequential_actions.sr, "Set_Shared_Variables", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(sequential_actions.sr, "Shared_Variable_Export", lambda: {})
    monkeypatch.setattr(sequential_actions, "load_sa_modules", lambda _module: None)
    monkeypatch.setattr(
        sequential_actions,
        "playwright",
        SimpleNamespace(get_driver=lambda: object()),
        raising=False,
    )
    monkeypatch.setattr(
        sequential_actions.common,
        "shared_variable_to_value",
        lambda data_set: data_set,
    )
    monkeypatch.setattr(
        sequential_actions.common,
        "Wait_For_Element",
        lambda data_set: captured.extend(data_set) or "passed",
    )
    monkeypatch.setattr(
        sequential_actions.ConfigModule,
        "get_config_value",
        lambda *_args, **_kwargs: "false",
    )
    monkeypatch.setattr(
        sequential_actions.CommonUtil,
        "TakeScreenShot",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        sequential_actions.CommonUtil,
        "set_screenshot_vars",
        lambda *_args, **_kwargs: None,
    )

    assert sequential_actions.Action_Handler(rows, rows[-1]) == "passed"
    assert ("wait", "action", "30") in captured


def test_selenium_conditional_uses_active_playwright_driver(monkeypatch):
    page = object()
    values = {"zeuz_browser_driver": "playwright"}
    seen = []
    caller_thread = threading.get_ident()
    monkeypatch.setattr(
        sequential_actions.sr,
        "Get_Shared_Variables",
        lambda name, **_: values.get(name, "zeuz_failed"),
    )
    monkeypatch.setattr(sequential_actions, "load_sa_modules", lambda _module: None)
    monkeypatch.setattr(
        sequential_actions,
        "playwright",
        SimpleNamespace(get_driver=lambda: page),
        raising=False,
    )
    monkeypatch.setattr(
        sequential_actions.LocateElement,
        "Get_Element",
        lambda _rows, driver, **_: seen.append(
            (driver, threading.get_ident())
        ) or object(),
    )

    result, _skip = sequential_actions.Conditional_Action_Handler(
        [[
            ("id", "element parameter", "button1"),
            ("true", "selenium conditional action", ""),
        ]],
        0,
    )

    assert result == "passed"
    assert seen[0][0] is page
    assert seen[0][1] != caller_thread


def test_action_worker_keeps_affinity_after_timeout():
    worker = sequential_actions._ActionTimeoutWorker()
    thread_ids = []

    def slow():
        thread_ids.append(threading.get_ident())
        time.sleep(0.05)

    with pytest.raises(TimeoutError):
        worker.run(slow, (), 0.01)
    assert (
        worker.run(lambda: thread_ids.append(threading.get_ident()) or "passed", (), 1)
        == "passed"
    )
    assert len(set(thread_ids)) == 1


def test_switch_iframe_resets_then_selects_locator(monkeypatch):
    frame = object()
    state = {"page": object(), "frame": object(), "frame_stack": [object()]}
    seen = []
    monkeypatch.setattr(playwright_actions, "_state", lambda: state)
    monkeypatch.setattr(
        playwright_actions,
        "_element",
        lambda rows, **_: seen.extend(rows) or SimpleNamespace(content_frame=frame),
    )
    monkeypatch.setattr(
        playwright_actions.sr, "Set_Shared_Variables", lambda *_args, **_kwargs: None
    )

    assert playwright_actions.switch_iframe([
        ("index", "iframe parameter", "default content"),
        ("id", "iframe parameter", "frame_two"),
        ("switch iframe", "playwright action", "switch iframe"),
    ]) == "passed"

    assert state["frame"] is frame
    assert state["frame_stack"] == [None]
    assert ("id", "element parameter", "frame_two") in seen
    assert not any(right == "default content" for _, _, right in seen)


def test_go_to_link_clears_previous_iframe(monkeypatch):
    class Page:
        url = "https://example.test/inside-frame"

        def goto(self, url, **_kwargs):
            self.url = url

    page = Page()
    state = {
        "page": page,
        "frame": object(),
        "frame_stack": [object()],
        "wait_until": "load",
        "wired_pages": {id(page)},
    }
    monkeypatch.setattr(playwright_actions, "_launch", lambda _rows: state)
    monkeypatch.setattr(playwright_actions, "_set_active", lambda _driver_id: None)

    assert playwright_actions.Go_To_Link([
        ("go to link", "playwright action", "https://example.test/login"),
    ]) == "passed"

    assert page.url == "https://example.test/login"
    assert state["frame"] is None
    assert state["frame_stack"] == []


def test_selenium_cdp_address(monkeypatch):
    monkeypatch.setattr(playwright_actions, "_free_local_port", lambda: 32123)
    arguments = []

    assert playwright_actions._selenium_cdp_address(
        "chrome", None, arguments
    ) == "127.0.0.1:32123"
    assert "--remote-debugging-port=32123" in arguments
    assert playwright_actions._selenium_cdp_address(
        "microsoft edge chromium", "http://localhost:9222", []
    ) == "localhost:9222"
    assert playwright_actions._selenium_cdp_address("firefox", None, []) is None


def test_chrome_launch_uses_chrome_for_testing(monkeypatch):
    class Page:
        def __init__(self, context):
            self.context = context
            self.url = "about:blank"

        def on(self, *_args):
            pass

    class Context:
        pages = []

        def on(self, *_args):
            pass

        def new_page(self):
            return Page(self)

    class Browser:
        def new_context(self, **_kwargs):
            return Context()

    class Chromium:
        def launch(self, **kwargs):
            captured["launch"] = kwargs
            return Browser()

    class ChromeForTesting:
        def setup_chrome_for_testing(self, version, channel):
            captured["version"] = version
            captured["channel"] = channel
            return "/tmp/chrome", "/tmp/chromedriver"

    captured = {}
    monkeypatch.setattr(playwright_actions, "_playwright", SimpleNamespace(chromium=Chromium()))
    monkeypatch.setattr(playwright_actions, "playwright_details", {})
    monkeypatch.setattr(
        playwright_actions.sr,
        "Get_Shared_Variables",
        lambda name, **_: {"Browser": "Chrome"} if name == "dependency" else None,
    )
    monkeypatch.setattr(playwright_actions, "_attach_selenium_bridge", lambda *_args: None)
    monkeypatch.setattr(playwright_actions, "_set_active", lambda *_args: None)
    monkeypatch.setattr(
        "Framework.Built_In_Automation.Web.Selenium.utils.ChromeForTesting",
        ChromeForTesting,
    )

    playwright_actions._launch([("chrome:version", "optional parameter", "beta")])

    assert captured["version"] is None
    assert captured["channel"] == "Beta"
    assert captured["launch"]["executable_path"] == "/tmp/chrome"
    assert "channel" not in captured["launch"]


def test_playwright_viewport_uses_runtime_size_or_selenium_default(monkeypatch):
    values = {"window_size_x": "", "window_size_y": ""}
    monkeypatch.setattr(
        playwright_actions.ConfigModule,
        "get_config_value",
        lambda _section, key: values[key],
    )

    assert playwright_actions._configured_viewport() == {"width": 1920, "height": 1080}

    values.update(window_size_x="1440", window_size_y="900")
    assert playwright_actions._configured_viewport() == {"width": 1440, "height": 900}


def test_binary_request_body_does_not_escape_network_listener():
    class Request:
        post_data_buffer = b"\xf1binary"

        @property
        def post_data(self):
            raise UnicodeDecodeError("utf-8", b"\xf1", 0, 1, "invalid byte")

    assert playwright_actions._request_post_data(Request()) == "�binary"


def test_playwright_visibility_accepts_zero_sized_container_with_visible_child():
    class Locator:
        def __init__(self, visible, descendants=0):
            self.visible = visible
            self.descendants = descendants

        def is_visible(self):
            return self.visible

        def locator(self, selector):
            assert selector == ":visible"
            return SimpleNamespace(count=lambda: self.descendants)

    assert LocateElement._playwright_is_visible(Locator(False, descendants=1))
    assert not LocateElement._playwright_is_visible(Locator(False))


def test_selenium_bridge_attach_publish_and_close(monkeypatch):
    from selenium import webdriver

    monkeypatch.setattr(
        playwright_actions.sr,
        "Test_Shared_Variables",
        lambda name: name == "dependency",
    )
    monkeypatch.setattr(
        playwright_actions.sr,
        "Get_Shared_Variables",
        lambda name, **_: {"Browser": "Chrome"} if name == "dependency" else "zeuz_failed",
    )
    from Framework.Built_In_Automation.Web.Selenium import (
        BuiltInFunctions as selenium_actions,
    )

    bridge = SimpleNamespace(quit=lambda: setattr(bridge, "closed", True))
    captured = {}
    monkeypatch.setattr(
        webdriver,
        "Chrome",
        lambda **kwargs: captured.update(kwargs) or bridge,
    )
    monkeypatch.setattr(selenium_actions, "selenium_driver", None)
    monkeypatch.setattr(
        playwright_actions.sr,
        "Set_Shared_Variables",
        lambda name, value, **_: captured.__setitem__(name, value),
    )
    monkeypatch.setattr(
        playwright_actions.sr,
        "Remove_From_Shared_Variables",
        lambda name: captured.pop(name, None),
    )
    state = {}

    playwright_actions._attach_selenium_bridge(
        state, "chrome", "127.0.0.1:32123", "/tmp/chromedriver"
    )
    playwright_actions._publish_selenium_bridge(state["selenium_bridge"])

    assert state["selenium_bridge"] is bridge
    assert captured["options"].debugger_address == "127.0.0.1:32123"
    assert captured["service"].path == "/tmp/chromedriver"
    assert captured["selenium_driver"] is bridge
    assert selenium_actions.selenium_driver is bridge

    playwright_actions._close_selenium_bridge(state)
    assert bridge.closed is True
    assert "selenium_bridge" not in state


@pytest.fixture(scope="module")
def page():
    if not shutil.which("google-chrome"):
        pytest.skip("System Chrome is unavailable")
    from playwright.sync_api import sync_playwright

    manager = sync_playwright().start()
    try:
        browser = manager.chromium.launch(channel="chrome", headless=True)
    except Exception as error:
        manager.stop()
        pytest.skip(f"System Chrome cannot launch: {error}")
    page = browser.new_page()
    page.set_content("""
        <section data-zone="MainArea"><div class="Card Alpha"><button id="SAVE-One">Save now</button></div></section>
        <ul><li class="item">one</li><li class="item">two</li><li class="item">three</li></ul>
        <button id="disabled" disabled>Disabled</button><button id="hidden" hidden>Hidden</button>
        <span id="zero-height" style="display:block;height:0"><span>Visible child</span></span>
        <x-host></x-host>
        <iframe srcdoc="<button id='inside'>Inside</button>"></iframe>
        <script>
          const root = document.querySelector('x-host').attachShadow({mode: 'open'});
          root.innerHTML = '<span class="shadow-target">shadow</span>';
        </script>
    """)
    yield page
    browser.close()
    manager.stop()


@pytest.mark.parametrize(
    "rows, expected",
    [
        ([("id", "element parameter", "SAVE-One")], "Save now"),
        ([("*id", "element parameter", "SAVE")], "Save now"),
        ([("**id", "element parameter", "save-one")], "Save now"),
        ([("text", "element parameter", "Save now")], "Save now"),
        ([("css selector", "element parameter", "#SAVE-One")], "Save now"),
        ([("xpath", "element parameter", "//button[@id='SAVE-One']")], "Save now"),
        (
            [
                ("class", "element parameter", "item"),
                ("index", "element parameter", "-1"),
            ],
            "three",
        ),
        (
            [
                ("data-zone", "parent parameter", "MainArea"),
                ("tag", "element parameter", "button"),
            ],
            "Save now",
        ),
        (
            [
                ("class", "child parameter", "Card Alpha"),
                ("tag", "element parameter", "section"),
            ],
            "Save now",
        ),
    ],
)
def test_locator_grammar(page, rows, expected):
    element = LocateElement.Get_Element(rows, page, element_wait=0.5)
    assert element.inner_text() == expected


def test_hidden_disabled_frame_and_shadow(page):
    assert (
        LocateElement.Get_Element(
            [("id", "element parameter", "disabled")], page, element_wait=0.1
        )
        == "zeuz_failed"
    )
    disabled = LocateElement.Get_Element(
        [
            ("id", "element parameter", "disabled"),
            ("allow disable", "optional parameter", "true"),
        ],
        page,
        element_wait=0.5,
    )
    assert disabled.inner_text() == "Disabled"

    hidden = LocateElement.Get_Element(
        [
            ("id", "element parameter", "hidden"),
            ("allow hidden", "optional parameter", "true"),
        ],
        page,
        element_wait=0.5,
    )
    assert hidden.inner_text() == "Hidden"

    zero_height = LocateElement.Get_Element(
        [("id", "element parameter", "zero-height")], page, element_wait=0.5
    )
    assert zero_height.inner_text() == "Visible child"

    frame = next(frame for frame in page.frames if frame != page.main_frame)
    assert (
        LocateElement.Get_Element(
            [("id", "element parameter", "inside")], frame, element_wait=0.5
        ).inner_text()
        == "Inside"
    )

    shadow = LocateElement.Get_Element(
        [
            ("tag", "sr 1 element parameter", "x-host"),
            ("css selector", "element parameter", ".shadow-target"),
        ],
        page,
        element_wait=0.5,
    )
    assert shadow.inner_text() == "shadow"
