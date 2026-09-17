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


def test_playwright_module_loads():
    assert sequential_actions.load_sa_modules("playwright") == "passed"
    assert sequential_actions.playwright is playwright_actions


def test_review_routing_and_selenium_ownership(monkeypatch):
    monkeypatch.setattr(playwright_actions.sr, "Test_Shared_Variables", lambda name: name == "dependency")
    monkeypatch.setattr(playwright_actions.sr, "Get_Shared_Variables", lambda name, **_: {"Browser": "Chrome"})
    from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as selenium

    values = {"zeuz_browser_driver": "playwright", "zeuz_active_browser_backend": "playwright"}
    monkeypatch.setattr(sequential_actions.sr, "Get_Shared_Variables", lambda name, **_: values.get(name))
    monkeypatch.setattr(sequential_actions.sr, "Set_Shared_Variables", lambda name, value, **_: values.__setitem__(name, value))
    monkeypatch.setattr(sequential_actions.sr, "Shared_Variable_Export", lambda: values)
    screenshots = []
    monkeypatch.setattr(sequential_actions.CommonUtil, "set_screenshot_vars", lambda values: screenshots.append(values.copy()))
    driver = object()
    monkeypatch.setattr(selenium, "selenium_details", {"web": {"driver": driver}})
    monkeypatch.setattr(selenium, "selenium_driver", None)
    monkeypatch.setattr(selenium, "current_driver_id", None)
    for backend in ("selenium", "playwright"):
        for subfield in ("selenium action", "playwright action"):
            assert sequential_actions._route_playwright_action("click", subfield, [
                ("browser driver", "optional parameter", backend)
            ]) == backend + " action"
    assert selenium.Switch_Browser([("driver_id", "optional parameter", "web")]) == "passed"
    assert values["zeuz_browser_backends"] == {"web": "selenium"}
    assert screenshots[-1]["common_driver"] is driver
    assert screenshots[-1]["zeuz_active_browser_backend"] == "selenium"
    assert sequential_actions._route_playwright_action("switch browser", "selenium action", [
        ("driver_id", "optional parameter", "web")
    ]) == "selenium action"


def test_review_extension_failure_and_xpath_case(monkeypatch):
    monkeypatch.setattr(playwright_actions.sr, "Test_Shared_Variables", lambda name: name == "dependency")
    monkeypatch.setattr(playwright_actions.sr, "Get_Shared_Variables", lambda name, **_: {"Browser": "Chrome"})
    from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as selenium

    monkeypatch.setattr(selenium, "ChromeExtensionDownloader", lambda **_: SimpleNamespace(
        setup_chrome_extension_download=lambda **_: None))
    assert selenium.parse_and_verify_datatype("addextension", repr(["a" * 32])) == []
    assert LocateElement._construct_query([("XPath", "element parameter", "//button")]) == ("//button", "xpath")


def test_review_text_classifier_and_image_paste(monkeypatch):
    import pyperclip
    from Framework.AI import NLP

    seen = []
    element = SimpleNamespace(inner_text=lambda: "  success  \n\nnext", focus=lambda: seen.append("focus"),
                              evaluate=lambda script, value: seen.append(value))
    monkeypatch.setattr(playwright_actions, "_element", lambda *_args, **_: element)
    monkeypatch.setattr(NLP, "binary_classification", lambda message, labels, confidence: seen.append(
        (message, labels, confidence)) or {"status": "passed"})
    assert playwright_actions.Validate_Text([
        ("validate full text", "action", "unused"), ("success", "text classifier offset", "0.8")
    ]) == "passed"
    assert seen[-1] == ("success   next", ["success"], 0.8)
    def failed_press(combo):
        seen.append(combo)
        raise RuntimeError("paste failed")
    monkeypatch.setattr(playwright_actions, "get_page", lambda: SimpleNamespace(
        keyboard=SimpleNamespace(press=failed_press), evaluate=lambda _: True))
    monkeypatch.setattr(pyperclip, "paste", lambda: "fallback")
    assert playwright_actions.Keystroke_For_Element([
        ("id", "element parameter", "input"), ("keystroke keys", "action", "CTRL+V"),
        ("paste image", "optional parameter", "true")
    ]) == "passed"
    assert seen[-3:] == ["focus", "Meta+v", "fallback"]


def test_review_network_static_filters(monkeypatch):
    logs = []
    state = {"capturing_network": True, "network": [
        {"url": "https://example.test/" + suffix, "status": 200, "method": "GET", "mimeType": mime}
        for suffix, mime in [("a.txt", "text/plain"), ("a.webp", ""), ("a.eot", ""),
                             ("image?id=1", "image/png"), ("font", "application/x-font-ttf"),
                             ("api", "application/json")]
    ]}
    monkeypatch.setattr(playwright_actions, "_state", lambda: state)
    monkeypatch.setattr(playwright_actions.sr, "Set_Shared_Variables", lambda _, value: logs.extend(value))
    assert playwright_actions.capture_network_log([
        ("capture network log", "action", "stop"), ("save", "input parameter", "logs")
    ]) == "passed"
    assert [item["url"] for item in logs] == ["https://example.test/api"]


def test_review_clipboard_variable_and_multiple_tabs(monkeypatch, tmp_path):
    image = tmp_path / "image.png"
    image.write_bytes(b"image bytes")
    captured = []
    context = SimpleNamespace(pages=[], grant_permissions=lambda *args, **kwargs: None)
    state = {"context": context}
    class Page:
        url = "https://example.test"
        def __init__(self, title):
            self.name = title
        def title(self):
            return self.name
        def close(self):
            context.pages.remove(self)
        def evaluate(self, script, value):
            captured.append(value)
    pages = [Page(name) for name in ("first", "second", "third")]
    context.pages = pages.copy()
    monkeypatch.setattr(playwright_actions, "_state", lambda: state)
    monkeypatch.setattr(playwright_actions, "get_page", lambda: pages[0])
    monkeypatch.setattr(playwright_actions, "_wire_page", lambda *_: None)
    monkeypatch.setattr(playwright_actions, "_set_active", lambda *_: None)
    monkeypatch.setattr(playwright_actions.sr, "Get_Shared_Variables", lambda name: str(image))
    for value in (str(image), "image_variable"):
        assert playwright_actions.copy_image_into_browser([
            ("image variable", "input parameter", value)
        ]) == "passed"
        assert captured[-1] == {"data": "aW1hZ2UgYnl0ZXM=", "mime": "image/png"}
    assert playwright_actions.close_tab([("tabs", "optional parameter", "[0, 2]")]) == "passed"
    assert context.pages == [pages[1]]
    context.pages = pages.copy()
    assert playwright_actions.close_tab([("tabs", "optional parameter", "['first', 'third']")]) == "passed"
    assert context.pages == [pages[1]]


def test_review_electron_ports(monkeypatch):
    import socket
    monkeypatch.setattr(playwright_actions.sr, "Test_Shared_Variables", lambda name: name == "dependency")
    monkeypatch.setattr(playwright_actions.sr, "Get_Shared_Variables", lambda name, **_: {"Browser": "Chrome"})
    from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as selenium

    sockets, ports, closed = [], [], []
    def launch(**kwargs):
        port = int(next(arg.split("=", 1)[1] for arg in kwargs["options"].arguments
                        if arg.startswith("--remote-debugging-port=")))
        sock = socket.socket()
        sockets.append(sock)
        sock.bind(("127.0.0.1", port))
        ports.append(port)
        return SimpleNamespace(implicitly_wait=lambda _: None, quit=lambda: closed.append(port))
    monkeypatch.setenv("WDM_ARCHITECTURE", "x64")
    monkeypatch.setattr(selenium.webdriver, "Chrome", launch)
    monkeypatch.setattr(selenium, "ChromeDriverManager", lambda **_: SimpleNamespace(install=lambda: "/tmp/chromedriver"))
    monkeypatch.setattr(selenium.ConfigModule, "get_config_value", lambda *_: "/tmp/chromedriver")
    monkeypatch.setattr(selenium, "_publish_active_browser", lambda: None)
    monkeypatch.setattr(selenium.Shared_Resources, "Set_Shared_Variables", lambda *_: None)
    monkeypatch.setattr(selenium.CommonUtil, "set_screenshot_vars", lambda *_: None)
    monkeypatch.setattr(selenium, "selenium_details", {})
    monkeypatch.setattr(selenium, "selenium_driver", None)
    monkeypatch.setattr(selenium, "current_driver_id", None)
    try:
        for driver_id in ("one", "two", "one"):
            assert selenium.Open_Electron_App([
                (selenium.platform.system().lower(), "input parameter", "/tmp/electron"),
                ("driverid", "optional parameter", driver_id)
            ]) == "passed"
            assert selenium.selenium_details[driver_id]["remote-debugging-port"] == ports[-1]
            assert selenium.selenium_details[driver_id]["driver"] is selenium.selenium_driver
        assert ports[0] != ports[1]
        assert closed == [ports[0]]
    finally:
        for sock in sockets:
            sock.close()


def test_review_browser_action_parity(page, monkeypatch):
    context = page.context.browser.new_context()
    tab = context.new_page()
    monkeypatch.setattr(playwright_actions, "get_page", lambda: tab)
    monkeypatch.setattr(playwright_actions, "get_driver", lambda: tab)
    saved = {}
    monkeypatch.setattr(playwright_actions.sr, "Set_Shared_Variables", lambda name, value: saved.__setitem__(name, value) or "passed")
    monkeypatch.setattr(playwright_actions.sr, "Get_Shared_Variables", lambda *_args, **_: 0)
    try:
        tab.set_content('''<input id="text" readonly><input id="check" type="checkbox" style="pointer-events:none">
            <div id="root"><span class="item" value="one">keep</span><span class="item" value="two">drop</span></div>
            <table><tr><th>heading</th></tr><tr><td>cell</td></tr></table>
            <div style="height:2000px"></div><div id="bottom">bottom</div><div style="height:2000px"></div>
            <script>window.events=[]; document.querySelector('#text').addEventListener('input', () => events.push('input'));
            document.querySelector('#text').addEventListener('change', () => events.push('change'));</script>''')
        text = "  text ` ${literal}  "
        assert playwright_actions.Enter_Text_In_Text_Box([
            ("id", "element parameter", "text"), ("text", "action", text), ("use js", "optional parameter", "true")
        ]) == "passed"
        assert tab.locator("#text").input_value() == text
        assert tab.evaluate("events") == ["input", "change"]
        assert playwright_actions.check_uncheck([
            ("id", "element parameter", "check"), ("check uncheck", "action", "check"), ("use js", "optional parameter", "yes")
        ]) == "passed"
        assert tab.locator("#check").is_checked()
        assert playwright_actions._return_attribute(tab.locator("#check"), "checked") == "True"
        assert playwright_actions._return_attribute(tab.locator(".item").first, "tag") == "span"
        assert playwright_actions._return_attribute(tab.locator(".item").first, "value") == "one"
        rows = [("id", "element parameter", "root"),
                ("attributes", "target parameter", 'class="item", return="text", return_contains="keep"'),
                ("attributes", "target parameter", 'class="item", return="value"'),
                ("save attribute values in list", "action", "values")]
        assert playwright_actions.save_attribute_values_in_list(rows) == "passed"
        assert saved["values"] == [["keep", "one"], [None, "two"]]
        assert playwright_actions.save_attribute_values_in_list(rows + [("paired", "optional parameter", "no")]) == "passed"
        assert saved["values"] == [["keep", None], ["one", "two"]]
        assert playwright_actions.save_web_elements_in_list([
            ("id", "element parameter", "root"),
            ("attributes", "target parameter", 'class="item", return_contains(text="keep"), return_does_not_contain(value="two")'),
            ("save web elements in list", "action", "elements")
        ]) == "passed"
        assert [element.inner_text() for element in saved["elements"]] == ["keep"]
        assert playwright_actions.Extract_Table_Data([
            ("tag", "element parameter", "table"), ("extract table data", "action", "table")
        ]) == "passed"
        assert saved["table"] == [[], ["cell"]]
        rows = [("id", "element parameter", "bottom"), ("scroll element to top", "action", ""),
                ("additional scroll", "optional parameter", "0")]
        assert playwright_actions.scroll_to_element(rows) == "passed"
        assert abs(tab.locator("#bottom").bounding_box()["y"]) < 1
        assert playwright_actions.scroll_to_element(rows + [("align to top", "optional parameter", "false")]) == "passed"
        box = tab.locator("#bottom").bounding_box()
        assert abs(box["y"] + box["height"] - tab.evaluate("innerHeight")) < 1
        # The synchronous click completes because the next action handles its dialog immediately.
        state = {}
        monkeypatch.setattr(playwright_actions, "_state", lambda: state)
        monkeypatch.setattr(playwright_actions.CommonUtil, "current_action_no", "1")
        monkeypatch.setattr(playwright_actions.sr, "Get_Shared_Variables", lambda *_args, **_: [[], [
            ("handle alert", "action", "send text=answer")]])
        tab.on("dialog", lambda dialog: playwright_actions._on_dialog(state, dialog))
        assert tab.evaluate("prompt('question')") == "answer"
        assert playwright_actions.Handle_Browser_Alert([("handle alert", "action", "get text=alert")]) == "passed"
        assert saved["alert"] == "question"
    finally:
        context.close()


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

        def goto(self, url, **kwargs):
            self.url = url
            self.wait_until = kwargs["wait_until"]

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
    assert page.wait_until == "load"
    assert state["frame"] is None
    assert state["frame_stack"] == []


def test_go_to_link_navigates_hash_route(monkeypatch):
    class Page:
        url = "https://example.test/#/login"

        def goto(self, url, **kwargs):
            self.gotos.append(url)
            self.goto_wait_until = kwargs["wait_until"]
            self.url = url

        def reload(self, **kwargs):
            self.reload_wait_until = kwargs["wait_until"]

    page = Page()
    page.gotos = []
    state = {
        "page": page,
        "frame": None,
        "frame_stack": [],
        "wait_until": "load",
        "wired_pages": {id(page)},
    }
    monkeypatch.setattr(playwright_actions, "_launch", lambda _rows: state)
    monkeypatch.setattr(playwright_actions, "_set_active", lambda _driver_id: None)

    assert playwright_actions.Go_To_Link([
        ("go to link", "playwright action", page.url),
    ]) == "passed"
    assert page.gotos == [page.url]
    assert page.goto_wait_until == "load"
    assert page.reload_wait_until == "load"


def test_open_new_tab_makes_new_page_active(monkeypatch):
    old_page = object()
    new_page = SimpleNamespace(on=lambda *_args: None)
    state = {
        "page": old_page,
        "frame": object(),
        "frame_stack": [object()],
        "context": SimpleNamespace(new_page=lambda: new_page),
        "wired_pages": set(),
        "page_listener": True,
        "capturing_network": False,
        "downloads": [],
    }
    active_pages = []
    monkeypatch.setattr(playwright_actions, "_state", lambda: state)
    monkeypatch.setattr(
        playwright_actions,
        "_set_active",
        lambda _driver_id: active_pages.append(state["page"]),
    )

    assert playwright_actions.open_new_tab([
        ("open new tab", "playwright action", "open new tab"),
    ]) == "passed"
    assert state["page"] is new_page
    assert state["frame"] is None
    assert active_pages == [new_page]


def test_reused_browser_applies_element_wait(monkeypatch):
    state = {"page": object()}
    shared = {}
    monkeypatch.setattr(playwright_actions._browser_state, "playwright_details", {"default": state})
    monkeypatch.setattr(playwright_actions, "_set_active", lambda _driver_id: None)
    monkeypatch.setattr(
        playwright_actions.sr,
        "Get_Shared_Variables",
        lambda name, **_kwargs: {"Browser": "Chrome"}
        if name == "dependency"
        else None,
    )
    monkeypatch.setattr(
        playwright_actions.sr,
        "Set_Shared_Variables",
        lambda name, value, **_kwargs: shared.__setitem__(name, value),
    )

    assert playwright_actions._launch([
        ("wait time to appear element", "optional parameter", "60"),
    ]) is state
    assert shared["element_wait"] == 60.0


def test_go_to_link_v2_retains_driver_tag(monkeypatch):
    monkeypatch.setattr(
        playwright_actions.sr,
        "Test_Shared_Variables",
        lambda name: name == "dependency",
    )
    monkeypatch.setattr(
        playwright_actions.sr,
        "Get_Shared_Variables",
        lambda name, **_: {"Browser": "Chrome"} if name == "dependency" else None,
    )
    from Framework.Built_In_Automation.Web.Selenium import (
        BuiltInFunctions as selenium_actions,
    )

    driver = SimpleNamespace(
        set_page_load_timeout=lambda _timeout: None,
        maximize_window=lambda: None,
    )
    monkeypatch.setattr(selenium_actions.webdriver, "Chrome", lambda **_kwargs: driver)
    monkeypatch.setattr(selenium_actions, "selenium_details", {})
    monkeypatch.setattr(selenium_actions, "current_driver_id", None)
    monkeypatch.setattr(
        selenium_actions.Shared_Resources, "Set_Shared_Variables", lambda *_args: None
    )
    monkeypatch.setattr(
        selenium_actions.Shared_Resources, "Shared_Variable_Export", lambda: {}
    )
    monkeypatch.setattr(selenium_actions.CommonUtil, "ExecLog", lambda *_args: None)
    monkeypatch.setattr(
        selenium_actions.CommonUtil, "set_screenshot_vars", lambda *_args: None
    )

    assert selenium_actions.Go_To_Link_V2.__wrapped__([
        ("driver tag", "optional parameter", "checkout"),
    ]) == "passed"
    assert selenium_actions.current_driver_id == "checkout"
    assert selenium_actions.selenium_details["checkout"]["driver"] is driver


def test_selenium_style_page_up_key(monkeypatch):
    pressed = []
    monkeypatch.setattr(
        playwright_actions,
        "get_page",
        lambda: SimpleNamespace(keyboard=SimpleNamespace(press=pressed.append)),
    )

    assert playwright_actions.Keystroke_For_Element([
        ("keystroke keys", "selenium action", "PAGE_UP"),
    ]) == "passed"
    assert pressed == ["PageUp"]


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
    shared = {}
    monkeypatch.setattr(playwright_actions._browser_state, "_playwright", SimpleNamespace(chromium=Chromium()))
    monkeypatch.setattr(playwright_actions._browser_state, "playwright_details", {})
    monkeypatch.setattr(
        playwright_actions.sr,
        "Get_Shared_Variables",
        lambda name, **_: {"Browser": "Chrome"} if name == "dependency" else None,
    )
    monkeypatch.setattr(playwright_actions, "_attach_selenium_bridge", lambda *_args: None)
    monkeypatch.setattr(playwright_actions, "_set_active", lambda *_args: None)
    monkeypatch.setattr(
        playwright_actions.sr,
        "Set_Shared_Variables",
        lambda name, value, **_kwargs: shared.__setitem__(name, value),
    )
    monkeypatch.setattr(
        "Framework.Built_In_Automation.Web.Selenium.utils.ChromeForTesting",
        ChromeForTesting,
    )

    playwright_actions._launch([
        ("chrome:version", "optional parameter", "beta"),
        ("wait time to appear element", "optional parameter", "60"),
    ])

    assert captured["version"] is None
    assert captured["channel"] == "Beta"
    assert captured["launch"]["executable_path"] == "/tmp/chrome"
    assert "channel" not in captured["launch"]
    assert shared["element_wait"] == 60.0


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


def test_network_capture_does_not_read_unfinished_response_body(monkeypatch):
    class Response:
        request = SimpleNamespace(timing={"responseEnd": -1})

        def body(self):
            raise AssertionError("unfinished response body must not be read")

    state = {
        "capturing_network": True,
        "network": [
            {
                "url": "https://example.com/events",
                "status": 200,
                "method": "GET",
                "mimeType": "text/event-stream",
                "type": "eventsource",
                "timestamp": 1,
                "_response": Response(),
            }
        ],
    }
    saved = {}
    monkeypatch.setattr(playwright_actions, "_state", lambda: state)
    monkeypatch.setattr(
        playwright_actions.sr,
        "Set_Shared_Variables",
        lambda name, value: saved.__setitem__(name, value),
    )

    assert playwright_actions.capture_network_log(
        [
            ("capture network log", "playwright action", "stop"),
            ("include response body", "input parameter", "true"),
            ("save", "element parameter", "browser_network_log"),
        ]
    ) == "passed"
    assert saved["browser_network_log"][0]["body"] == "Unavailable"
    assert state["network"] == []


def test_cdp_capture_releases_sessions_on_start_and_stop_errors(monkeypatch):
    class Session:
        detached = False

        def on(self, *args):
            pass

        def remove_listener(self, *args):
            pass

        def send(self, method, params=None):
            if method == "Network.enable":
                raise RuntimeError("page closed during capture startup")

        def detach(self):
            self.detached = True

    session = Session()
    page = object()
    state = {
        "browser": SimpleNamespace(browser_type=SimpleNamespace(name="chromium")),
        "context": SimpleNamespace(pages=[page], new_cdp_session=lambda _: session),
        "network": [],
    }
    monkeypatch.setattr(playwright_actions, "_state", lambda: state)
    # Bypass the standard action guard to assert both the exception and cleanup.
    with pytest.raises(RuntimeError, match="page closed"):
        playwright_actions.capture_network_log.__wrapped__([
            ("capture network log", "playwright action", "start"),
        ])
    assert session.detached
    assert state["capturing_network"] is False
    assert not state.get("network_sessions")

    session.detached = False
    state["network_sessions"] = {page: session}
    with pytest.raises(ValueError):
        playwright_actions.capture_network_log.__wrapped__([
            ("capture network log", "playwright action", "stop"),
            ("include status code", "input parameter", "invalid"),
        ])
    assert session.detached
    assert not state.get("network_sessions")


def test_cdp_capture_reuses_browser_without_retaining_network_objects(page, monkeypatch):
    from collections import Counter
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html>Capture test</html>")

        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.send_response(307 if self.path == "/redirect" else 201)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            if self.path == "/redirect":
                self.send_header("Location", "/payload")
            self.end_headers()
            self.wfile.write(b'"' + b"x" * 65536 + b'"')

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    context = page.context.browser.new_context()
    state = {
        "browser": context.browser, "context": context, "network": [],
        "capturing_network": False, "downloads": [],
    }
    saved = {}
    monkeypatch.setattr(playwright_actions, "_state", lambda: state)
    monkeypatch.setattr(playwright_actions._browser_state, "playwright_details", {"default": state})
    monkeypatch.setattr(playwright_actions.sr, "Set_Shared_Variables", lambda k, v: saved.__setitem__(k, v))
    start = [("capture network log", "playwright action", "start")]
    stop = [
        ("capture network log", "playwright action", "stop"),
        ("include response body", "input parameter", "true"),
        ("include status code", "input parameter", "200-399"),
        ("include request method", "input parameter", "POST"),
        ("filter domain", "input parameter", "127.0.0.1,localhost"),
        ("save", "element parameter", "captured"),
    ]
    try:
        tab = context.new_page()
        playwright_actions._wire_page(state, tab)
        tab.goto(f"http://127.0.0.1:{server.server_port}")
        tab.evaluate("localStorage.setItem('login', 'retained')")
        tab.evaluate("""url => {
            const frame = document.createElement('iframe');
            frame.src = url;
            document.body.appendChild(frame);
        }""", f"http://localhost:{server.server_port}/frame")
        tab.frame_locator("iframe").locator("body").wait_for()
        child = tab.frames[1]

        def counts():
            objects = Counter(type(obj).__name__ for obj in tab._impl_obj._connection._objects.values())
            return {key: objects[key] for key in ("Request", "Response", "CDPSession")}

        baseline = counts()
        for _ in range(5):
            assert playwright_actions.capture_network_log(start) == "passed"
            tab.evaluate("""async () => {
                for (let i = 0; i < 50; i++) {
                    await (await fetch('/payload', {method: 'POST', body: 'p'.repeat(32768)})).text();
                }
                await (await fetch('/redirect', {method: 'POST'})).text();
                await (await fetch('/ignored')).text();
            }""")
            child.evaluate("async () => await (await fetch('/payload', {method: 'POST'})).text()")
            assert playwright_actions.capture_network_log(stop) == "passed"
            logs = saved["captured"]
            assert len(logs) == 53
            assert any("localhost" in item["url"] for item in logs)
            assert sum(item["status"] == 307 for item in logs) == 1
            assert all(item["body"] == '"' + "x" * 65536 + '"' for item in logs if item["status"] == 201)
            assert all(not key.startswith("_") for item in logs for key in item)
            assert state["network"] == []
            assert not state.get("network_sessions")
            assert not state.get("network_listeners")
            assert counts() == baseline

        # No capture listeners means requests made between tests stay unreported.
        tab.evaluate("async () => await (await fetch('/payload', {method: 'POST'})).text()")
        assert counts() == baseline

        # A skipped stop action or repeated start must also release the session.
        assert playwright_actions.capture_network_log(start) == "passed"
        assert playwright_actions.capture_network_log(start) == "passed"
        assert playwright_actions.cleanup_network_captures() == "passed"
        assert counts() == baseline
        assert not tab.is_closed()
        assert tab.evaluate("localStorage.getItem('login')") == "retained"
    finally:
        playwright_actions.cleanup_network_captures()
        context.close()
        server.shutdown()
        server.server_close()
        thread.join()


def test_testcase_exception_cleans_capture_on_action_worker(monkeypatch):
    from Framework import MainDriverApi

    detached_on = []
    session = SimpleNamespace(
        send=lambda *_: None,
        detach=lambda: detached_on.append(threading.get_ident()),
    )
    state = {"network": ["unfinished"], "network_sessions": {"page": session}}
    sequential_actions._run_action_with_timeout(
        lambda _: setattr(playwright_actions._browser_state, "playwright_details", {"default": state}), []
    )
    monkeypatch.setattr(MainDriverApi.CommonUtil, "Exception_Handler", lambda *_: None)
    monkeypatch.setattr(MainDriverApi.CommonUtil, "CreateJsonReport", lambda **_: None)
    monkeypatch.setattr(MainDriverApi.ConfigModule, "get_config_value", lambda *_: "")

    def fail_before_steps():
        raise RuntimeError("test failed before completing network capture")

    monkeypatch.setattr(MainDriverApi.CommonUtil, "clear_performance_metrics", fail_before_steps)
    assert MainDriverApi.run_test_case(
        "TEST-1", "capture cleanup test", "run", "unused.ini", {"title": "capture"},
        {}, False, "8.0.0",
    ) == "passed"
    assert len(detached_on) == 1
    assert detached_on[0] != threading.get_ident()
    assert state["network"] == []
    assert state["capturing_network"] is False


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


def test_visible_disabled_element_is_located_and_its_live_value_saved(monkeypatch):
    element = SimpleNamespace(
        is_visible=lambda: True,
        is_enabled=lambda: False,
        locator=lambda _selector: SimpleNamespace(count=lambda: 0),
        get_attribute=lambda _name: None,
        input_value=lambda: "user@example.test",
    )
    matches = SimpleNamespace(count=lambda: 1, nth=lambda _index: element)
    root = SimpleNamespace(locator=lambda _selector: matches)
    saved = {}

    def save(name, value, **_kwargs):
        saved[name] = value
        return "passed"

    monkeypatch.setattr(LocateElement.sr, "Set_Shared_Variables", save)
    monkeypatch.setattr(
        playwright_actions,
        "_element",
        lambda rows: LocateElement._playwright_get_element(rows, root, element_wait=0),
    )

    rows = [("id", "element parameter", "disabled")]
    assert LocateElement._playwright_get_element(rows, root, element_wait=0) is element
    assert playwright_actions.Save_Attribute([
        *rows,
        ("value", "save parameter", "user_email"),
    ]) == "passed"
    assert saved["user_email"] == "user@example.test"


def test_invalid_index_falls_back_only_for_one_visible_candidate(monkeypatch):
    warnings = []

    def root_with(elements):
        matches = SimpleNamespace(
            count=lambda: len(elements),
            nth=lambda index: elements[index],
        )
        return SimpleNamespace(locator=lambda _selector: matches)

    def candidate():
        return SimpleNamespace(
            is_visible=lambda: True,
            locator=lambda _selector: SimpleNamespace(count=lambda: 0),
        )

    monkeypatch.setattr(LocateElement.sr, "Set_Shared_Variables", lambda *_args: None)
    monkeypatch.setattr(
        LocateElement.CommonUtil,
        "ExecLog",
        lambda _module, message, level: warnings.append((message, level)),
    )
    rows = [
        ("class", "element parameter", "item"),
        ("index", "element parameter", "5"),
    ]
    only = candidate()

    assert LocateElement._playwright_get_element(
        rows, root_with([only]), element_wait=0
    ) is only
    assert warnings == [("Index 5 is invalid; returning the only visible element", 2)]
    assert LocateElement._playwright_get_element(
        rows, root_with([candidate(), candidate()]), element_wait=0
    ) == "zeuz_failed"


def test_text_filter_returns_only_matching_elements(monkeypatch):
    wanted = SimpleNamespace(text="Wanted")
    unwanted = SimpleNamespace(text="Other")
    monkeypatch.setattr(LocateElement, "_construct_query", lambda _rows: ("*", "css"))
    monkeypatch.setattr(
        LocateElement,
        "_get_xpath_or_css_element",
        lambda *_args: [wanted, unwanted],
    )
    monkeypatch.setattr(LocateElement.CommonUtil, "ExecLog", lambda *_args: None)

    assert LocateElement.text_filter(
        [
            ("tag", "element parameter", "div"),
            ("text", "element parameter", "Wanted"),
        ],
        "",
        0,
        True,
    ) == [wanted]


def test_uncapped_dom_and_teardown_use_browser_worker(monkeypatch):
    monkeypatch.setattr(sequential_actions, "_action_worker", None)
    monkeypatch.setattr(sequential_actions, "_get_action_timeout", lambda: 0)
    monkeypatch.setattr(sequential_actions, "load_testing", False)
    monkeypatch.setattr(sequential_actions.CommonUtil, "load_testing", False)
    monkeypatch.setattr(playwright_actions, "_publish_selenium_bridge", lambda _: None)
    calls = []

    def record(value):
        calls.append((value, threading.get_ident()))
        return value

    def setup(_):
        playwright_actions._browser_state.current_driver_id = "test"
        playwright_actions._browser_state.playwright_details = {"test": {
            "page": SimpleNamespace(evaluate=lambda _: record("dom")),
            "context": SimpleNamespace(close=lambda: record("context")),
            "browser": SimpleNamespace(close=lambda: record("browser")),
        }}
        return threading.get_ident()

    setup._zeuz_thread_affine = True
    owner = sequential_actions._run_action_with_timeout(setup, [])
    assert owner != threading.get_ident()
    assert sequential_actions._run_action_with_timeout(playwright_actions.get_dom, []) == "dom"
    assert sequential_actions._run_action_with_timeout(playwright_actions.Tear_Down_Selenium, []) == "passed"
    assert calls == [(name, owner) for name in ("dom", "context", "browser")]


@pytest.mark.parametrize("value", ["yes", "true", "ok", "1", "enable", "enabled"])
def test_legacy_locator_options(monkeypatch, value):
    monkeypatch.setattr(LocateElement, "_driver_type", lambda _: "selenium")
    monkeypatch.setattr(LocateElement, "_switch", lambda _: None)
    monkeypatch.setattr(LocateElement, "_construct_query", lambda *_: ("//div", "xpath"))
    seen = []
    monkeypatch.setattr(LocateElement, "_get_xpath_or_css_element",
                        lambda *args: seen.append(args[4]) or "zeuz_failed")
    monkeypatch.setattr(LocateElement, "text_filter", lambda *_: "filtered")
    driver = SimpleNamespace(find_elements=lambda *_: [])
    for option in ("allow hidden", "allow disable"):
        assert LocateElement.Get_Element([
            ("tag", "element parameter", "div"),
            (option, "optional parameter", value),
            ("text filter", "optional parameter", value),
        ], driver, element_wait=0) == "filtered"
        assert seen[-1] == option


@pytest.mark.parametrize("mode,wanted,actual,matched", [
    ("text", "Hello World", "Hello\xa0World", True),
    ("text", "Hello\xa0World", "Hello World", True),
    ("text", "Hello World", "prefix Hello\xa0World", False),
    ("*text", "Hello World", "prefix Hello\xa0World", True),
    ("*text", "hello World", "Hello\xa0World", False),
    ("**text", "hello world", "prefix HELLO\xa0WORLD", True),
    ("text", "Hello World", "Hello  World", False),
    ("text", "Hello World", "Hello\nWorld", False),
])
def test_text_filter_backend_parity(monkeypatch, mode, wanted, actual, matched):
    element = SimpleNamespace(text=actual, inner_text=lambda: actual)
    monkeypatch.setattr(LocateElement, "_construct_query", lambda *_: ("//div", "xpath"))
    monkeypatch.setattr(LocateElement, "_get_xpath_or_css_element", lambda *_: [element])
    def candidates(rows, *_args, **_kwargs):
        assert (mode, "element parameter", wanted) not in rows
        assert ("text", "parent parameter", "Parent") in rows
        return [element]
    monkeypatch.setattr(LocateElement, "_playwright_get_element", candidates)
    rows = [("tag", "element parameter", "div"),
            (mode, "element parameter", wanted), ("text", "parent parameter", "Parent")]
    for root in (None, object()):
        assert LocateElement.text_filter(rows, "", 0, True, playwright_root=root) == (
            [element] if matched else [])


@pytest.mark.parametrize("name", ["css", "css selector", "css_selector"])
def test_raw_css_locator_names(name):
    assert LocateElement._construct_query([
        (name, "element parameter", ".target"),
    ]) == (".target", "css")


def test_text_clears_then_presses_sequentially_with_delay(monkeypatch):
    events = []
    element = SimpleNamespace(
        get_attribute=lambda _name: "password",
        clear=lambda: events.append("clear"),
        press_sequentially=lambda value, **options: events.append((value, options)),
    )
    monkeypatch.setattr(playwright_actions, "_element", lambda _rows: element)

    assert playwright_actions.Enter_Text_In_Text_Box([
        ("id", "element parameter", "password"),
        ("delay", "optional parameter", "0.05"),
        ("text", "playwright action", "secret"),
    ]) == "passed"
    assert events == ["clear", ("secret", {"delay": 50})]


@pytest.mark.parametrize(
    "option",
    [
        ("clear", "optional parameter", "false"),
        ("append", "optional parameter", "true"),
    ],
)
def test_text_preserves_existing_value_when_requested(monkeypatch, option):
    events = []
    element = SimpleNamespace(
        get_attribute=lambda _name: "text",
        clear=lambda: events.append("clear"),
        press_sequentially=lambda value, **options: events.append((value, options)),
    )
    monkeypatch.setattr(playwright_actions, "_element", lambda _rows: element)

    assert playwright_actions.Enter_Text_In_Text_Box([
        ("id", "element parameter", "name"),
        option,
        ("text", "playwright action", "more"),
    ]) == "passed"
    assert events == [("more", {})]


def test_file_inputs_work_through_text_and_locator_free_upload(monkeypatch, tmp_path):
    file_path = tmp_path / "upload.txt"
    file_path.write_text("content")
    text_uploads = []
    text_input = SimpleNamespace(
        get_attribute=lambda _name: "file",
        set_input_files=text_uploads.append,
    )
    monkeypatch.setattr(playwright_actions, "_element", lambda _rows: text_input)

    assert playwright_actions.Enter_Text_In_Text_Box([
        ("id", "element parameter", "file"),
        ("text", "playwright action", str(file_path)),
    ]) == "passed"
    assert text_uploads == [str(file_path)]

    upload_files = []
    upload_input = SimpleNamespace(set_input_files=upload_files.append)
    selectors = []
    page = SimpleNamespace(
        locator=lambda selector: selectors.append(selector)
        or SimpleNamespace(first=upload_input)
    )
    monkeypatch.setattr(playwright_actions, "get_driver", lambda: page)
    monkeypatch.setattr(
        playwright_actions,
        "_element",
        lambda _rows: pytest.fail("locator-free upload must select the first file input"),
    )

    assert playwright_actions.upload_file([
        ("upload file", "playwright action", str(file_path)),
    ]) == "passed"
    assert selectors == ["input[type=file]"]
    assert upload_files == [str(file_path)]


def test_drag_and_drop_requires_both_locators(monkeypatch):
    errors = []
    monkeypatch.setattr(
        playwright_actions,
        "_fail",
        lambda message: errors.append(message) or "zeuz_failed",
    )
    monkeypatch.setattr(
        playwright_actions,
        "_element",
        lambda _rows: pytest.fail("missing locators must fail before lookup"),
    )

    assert playwright_actions.drag_and_drop([
        ("id", "dst element parameter", "target"),
    ]) == "zeuz_failed"
    assert playwright_actions.drag_and_drop([
        ("id", "src element parameter", "source"),
    ]) == "zeuz_failed"
    assert errors == [
        "Please provide a source element locator",
        "Please provide a destination element locator",
    ]


def test_drag_and_drop_optional_subfields_pass_step_validation():
    assert sequential_actions.common.verify_step_data([[
        ("id", "src element parameter", "source"),
        ("wait", "src optional parameter", "10"),
        ("id", "dst element parameter", "target"),
        ("wait", "dst optional parameter", "10"),
        ("drag and drop", "selenium action", ""),
    ]]) == "passed"


def test_drag_and_drop_uses_native_offset_and_shared_locator_options(monkeypatch):
    class Source:
        def drag_to(self, target, **options):
            dragged.append((target, options))

    class Target:
        def bounding_box(self):
            return {"width": 200, "height": 100}

    source, target = Source(), Target()
    located, dragged = [], []
    monkeypatch.setattr(
        playwright_actions,
        "_element",
        lambda rows: located.append(rows) or (source if len(located) == 1 else target),
    )

    assert playwright_actions.drag_and_drop([
        ("id", "src element parameter", "source"),
        ("text", "src child parameter", " Assets"),
        ("id", "dst element parameter", "target"),
        ("wait", "option", "2"),
        ("allow hidden", "optional option", "true"),
        ("destination offset", "optional parameter", "50,-100"),
    ]) == "passed"

    assert located == [
        [
            ("id", "element parameter", "source"),
            ("text", "child parameter", " Assets"),
            ("wait", "optional parameter", "2"),
            ("allow hidden", "optional parameter", "true"),
        ],
        [
            ("id", "element parameter", "target"),
            ("wait", "optional parameter", "2"),
            ("allow hidden", "optional parameter", "true"),
        ],
    ]
    assert dragged == [(target, {"target_position": {"x": 150, "y": 0}})]


def test_drag_and_drop_delay_releases_mouse(monkeypatch):
    events = []
    source = SimpleNamespace(hover=lambda: events.append("source hover"))
    target = SimpleNamespace(
        hover=lambda **options: events.append(("target hover", options))
    )
    elements = iter((source, target))
    page = SimpleNamespace(
        mouse=SimpleNamespace(
            down=lambda: events.append("mouse down"),
            up=lambda: events.append("mouse up"),
        ),
        wait_for_timeout=lambda milliseconds: events.append(("wait", milliseconds)),
    )
    monkeypatch.setattr(playwright_actions, "_element", lambda _rows: next(elements))
    monkeypatch.setattr(playwright_actions, "get_page", lambda: page)

    assert playwright_actions.drag_and_drop([
        ("id", "src element parameter", "source"),
        ("id", "dst element parameter", "target"),
        ("delay", "optional parameter", "0.25"),
    ]) == "passed"
    assert events == [
        "source hover",
        "mouse down",
        ("target hover", {}),
        ("target hover", {}),
        ("wait", 250),
        "mouse up",
    ]


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


def test_text_filter_fallback_preserves_normal_lookup(page, monkeypatch):
    saved = {}
    monkeypatch.setattr(LocateElement.sr, "Set_Shared_Variables", lambda key, value: saved.__setitem__(key, value))
    test_page = page.context.browser.new_page()
    try:
        test_page.set_content('''
            <section><button id="nbsp">Hello&nbsp;World</button>
            <button id="exact">Hello World</button>
            <button id="partial">prefix HELLO&nbsp;WORLD suffix</button>
            <button id="hidden-text" hidden>Hello&nbsp;World</button></section>
        ''')
        option = ("text filter", "optional parameter", "enabled")
        text = ("text", "element parameter", "Hello World")
        def locate(rows, **kwargs):
            return LocateElement.Get_Element(rows, test_page, element_wait=0, **kwargs)

        # A successful exact lookup must not broaden to include the NBSP candidate.
        assert locate([("tag", "element parameter", "button"), text, option]).get_attribute("id") == "exact"
        rows = [("id", "element parameter", "nbsp"), text]
        assert locate(rows) == "zeuz_failed"
        assert locate(rows + [option]).get_attribute("id") == "nbsp"
        # Selenium returns an empty list directly, without invoking its fallback.
        assert locate(rows + [option], return_all_elements=True) == []
        assert locate([("id", "element parameter", "partial"), text, option]) == "zeuz_failed"
        assert locate([("id", "element parameter", "partial"),
                       ("**text", "element parameter", "hello world"), option]).get_attribute("id") == "partial"
        # Raw CSS takes precedence over text in the normal Selenium query.
        assert locate([("css", "element parameter", "#partial"), text, option]).get_attribute("id") == "partial"
        for value in ("1", "enable", "enabled"):
            assert locate([("id", "element parameter", "hidden-text"), text, option,
                           ("allow hidden", "optional parameter", value)]).get_attribute("id") == "hidden-text"
        test_page.set_content('<div><button id="first">Hello&nbsp;World</button>'
                              '<button id="second">Hello&nbsp;World</button></div>')
        indexed = [("tag", "element parameter", "button"), text, option,
                   ("index", "element parameter", "-1"), ("chosen", "save parameter", "")]
        assert locate(indexed).get_attribute("id") == "second"
        assert saved["chosen"].get_attribute("id") == "second"
        assert saved["zeuz_element"].get_attribute("id") == "second"
    finally:
        test_page.close()


def test_evaluator_text_does_not_reselect_existing_user(page, monkeypatch):
    saved = {}

    def save(name, value, **_kwargs):
        saved[name] = value
        return "passed"

    monkeypatch.setattr(playwright_actions.sr, "Set_Shared_Variables", save)
    monkeypatch.setattr(playwright_actions.sr, "Get_Shared_Variables", lambda *_: 0)
    test_page = page.context.browser.new_page()
    monkeypatch.setattr(playwright_actions, "get_driver", lambda: test_page)
    try:
        test_page.set_content(
            '<div id="evaluators"><button class="user-tags" style="white-space:pre">Existing Test User </button></div>'
        )
        assert test_page.locator("button").inner_text().endswith(" ")
        assert playwright_actions.save_attribute_values_in_list([
            ("id", "element parameter", "evaluators"),
            ("attributes", "target parameter", 'tag="button", return="text"'),
            ("save attribute values in list", "action", "existing"),
        ]) == "passed"
        # Match Selenium's observed whitespace handling using synthetic names.
        assert saved["existing"] == ["Existing Test User"]
        wanted = ["New Test User", "Existing Test User"]
        assert [name for name in wanted if name not in saved["existing"]] == ["New Test User"]
        assert playwright_actions.Save_Attribute([
            ("tag", "element parameter", "button"),
            ("text", "save parameter", "name"),
        ]) == "passed"
        assert saved["name"] == "Existing Test User"
        for mode in ("validate full text", "validate partial text"):
            assert playwright_actions.Validate_Text([
                ("tag", "element parameter", "button"),
                (mode, "action", "Existing Test User"),
            ]) == "passed"
    finally:
        test_page.close()


def test_missing_validation_element_logs_locator_failure(monkeypatch):
    logs = []
    root = SimpleNamespace(locator=lambda _selector: SimpleNamespace(count=lambda: 0))
    monkeypatch.setattr(LocateElement.CommonUtil, "ExecLog", lambda *args: logs.append(args))
    monkeypatch.setattr(
        playwright_actions, "_element",
        lambda rows: LocateElement._playwright_get_element(rows, root, element_wait=0),
    )
    assert playwright_actions.Validate_Text([
        ("tag", "element parameter", "button"),
        ("*text", "element parameter", "Existing Test User"),
        ("validate partial text", "action", "Existing Test User"),
    ]) == "zeuz_failed"
    assert any("Unable to locate" in message and "matches=0" in message and level == 3
               for _module, message, level in logs)


def test_hidden_disabled_frame_and_shadow(page):
    disabled = LocateElement.Get_Element(
        [("id", "element parameter", "disabled")],
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
