import asyncio

from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from Framework.Built_In_Automation.Sequential_Actions import sequential_actions as sa
from Framework.Built_In_Automation.Web.Playwright import BuiltInFunctions as pw


class FakePage:
    def __init__(self):
        self.url = "https://example.test/current"
        self.viewport_size = {"width": 1000, "height": 800}
        self.evaluated = []
        self.keyboard = FakeKeyboard()
        self.mouse = FakeMouse()

    async def evaluate(self, script, arg=None):
        self.evaluated.append((script, arg))
        return "page-result"

    async def set_viewport_size(self, size):
        self.viewport_size = size


class FakeKeyboard:
    def __init__(self):
        self.calls = []

    async def press(self, key):
        self.calls.append(("press", key))

    async def type(self, text, **kwargs):
        self.calls.append(("type", text, kwargs))


class FakeMouse:
    def __init__(self):
        self.calls = []

    async def wheel(self, delta_x, delta_y):
        self.calls.append(("wheel", delta_x, delta_y))

    async def click(self, x, y):
        self.calls.append(("click", x, y))


class FakeLocator:
    def __init__(self, text=""):
        self.text = text
        self.evaluated = []
        self.files = None
        self.calls = []
        self.wait_calls = []

    async def inner_text(self):
        return self.text

    async def text_content(self):
        return self.text

    async def inner_html(self):
        return self.text

    async def input_value(self):
        return self.text

    async def evaluate(self, script, arg=None, **kwargs):
        self.evaluated.append((script, arg, kwargs))
        return "locator-result"

    async def get_attribute(self, name):
        self.calls.append(("get_attribute", name))
        return "attr-result"

    async def is_checked(self):
        self.calls.append(("is_checked",))
        return False

    async def is_visible(self):
        self.calls.append(("is_visible",))
        return True

    async def is_enabled(self):
        self.calls.append(("is_enabled",))
        return True

    async def is_disabled(self):
        self.calls.append(("is_disabled",))
        return False

    async def select_option(self, **kwargs):
        self.calls.append(("select_option", kwargs))

    async def set_input_files(self, file_path, **kwargs):
        self.files = file_path
        self.calls.append(("set_input_files", file_path, kwargs))

    async def bounding_box(self, **kwargs):
        self.calls.append(("bounding_box", kwargs))
        return {"x": 10, "y": 20, "width": 200, "height": 30}

    async def click(self, **kwargs):
        self.calls.append(("click", kwargs))

    async def fill(self, text, **kwargs):
        self.calls.append(("fill", text, kwargs))

    async def press(self, key, **kwargs):
        self.calls.append(("press", key, kwargs))

    async def type(self, text, **kwargs):
        self.calls.append(("type", text, kwargs))

    async def hover(self, **kwargs):
        self.calls.append(("hover", kwargs))

    async def wait_for(self, **kwargs):
        self.wait_calls.append(kwargs)

    async def count(self):
        self.calls.append(("count",))
        return 1


def setup_function():
    sr.shared_variables.clear()
    pw.current_page = FakePage()
    pw.context = None
    pw.browser = None
    pw.current_page_id = "default"


def test_get_current_url_saves_to_selenium_action_row_value():
    result = pw.Get_Current_URL(
        [("get current url", "selenium action", "current_url")]
    )

    assert result == "passed"
    assert sr.Get_Shared_Variables("current_url") == "https://example.test/current"


def test_validate_full_text_uses_visible_line_matching(monkeypatch):
    locator = FakeLocator("Header\nSuccess\nFooter")

    async def fake_get_element(*args, **kwargs):
        return locator

    monkeypatch.setattr(pw.PlaywrightLocator, "Get_Element", fake_get_element)

    result = asyncio.run(
        pw.Validate_Text(
            [
                ("id", "element parameter", "message"),
                ("validate full text", "selenium action", "Success"),
            ]
        )
    )

    assert result == "passed"


def test_upload_file_accepts_selenium_action_row_path(monkeypatch, tmp_path):
    upload_file = tmp_path / "upload.txt"
    upload_file.write_text("data")
    locator = FakeLocator()

    async def fake_get_element(*args, **kwargs):
        return locator

    monkeypatch.setattr(pw.PlaywrightLocator, "Get_Element", fake_get_element)

    result = asyncio.run(
        pw.upload_file(
            [
                ("id", "element parameter", "file-input"),
                ("upload file", "selenium action", str(upload_file)),
            ]
        )
    )

    assert result == "passed"
    assert locator.files == str(upload_file)


def test_execute_javascript_supports_variable_and_elem(monkeypatch):
    locator = FakeLocator()

    async def fake_get_element(*args, **kwargs):
        return locator

    monkeypatch.setattr(pw.PlaywrightLocator, "Get_Element", fake_get_element)

    result = asyncio.run(
        pw.execute_javascript(
            [
                ("id", "element parameter", "target"),
                ("variable", "optional parameter", "js_result"),
                ("execute javascript", "selenium action", "return $elem.textContent"),
            ]
        )
    )

    assert result == "passed"
    assert sr.Get_Shared_Variables("js_result") == "locator-result"
    assert "return el.textContent" in locator.evaluated[0][0]


def test_click_uses_lazy_locator_and_wait_timeout(monkeypatch):
    locator = FakeLocator()
    calls = []

    async def fake_get_element(*args, **kwargs):
        calls.append(kwargs)
        return locator

    monkeypatch.setattr(pw.PlaywrightLocator, "Get_Element", fake_get_element)

    result = asyncio.run(
        pw.Click_Element(
            [
                ("id", "element parameter", "save"),
                ("wait", "optional parameter", "2"),
                ("click", "playwright action", "click"),
            ]
        )
    )

    assert result == "passed"
    assert calls[0]["resolve"] is False
    assert locator.calls[-1] == ("click", {"timeout": 2000})


def test_enter_text_uses_lazy_locator_and_wait_timeout(monkeypatch):
    locator = FakeLocator()
    calls = []

    async def fake_get_element(*args, **kwargs):
        calls.append(kwargs)
        return locator

    monkeypatch.setattr(pw.PlaywrightLocator, "Get_Element", fake_get_element)

    result = asyncio.run(
        pw.Enter_Text_In_Text_Box(
            [
                ("id", "element parameter", "name"),
                ("wait", "optional parameter", "3"),
                ("clear", "optional parameter", "false"),
                ("text", "playwright action", "Alice"),
            ]
        )
    )

    assert result == "passed"
    assert calls[0]["resolve"] is False
    assert ("type", "Alice", {"timeout": 3000}) in locator.calls


def test_upload_file_passes_wait_timeout(monkeypatch, tmp_path):
    upload_file = tmp_path / "upload.txt"
    upload_file.write_text("data")
    locator = FakeLocator()
    calls = []

    async def fake_get_element(*args, **kwargs):
        calls.append(kwargs)
        return locator

    monkeypatch.setattr(pw.PlaywrightLocator, "Get_Element", fake_get_element)

    result = asyncio.run(
        pw.upload_file(
            [
                ("id", "element parameter", "file-input"),
                ("wait", "optional parameter", "4"),
                ("upload file", "selenium action", str(upload_file)),
            ]
        )
    )

    assert result == "passed"
    assert calls[0]["resolve"] is False
    assert locator.calls[-1] == ("set_input_files", str(upload_file), {"timeout": 4000})


def test_keystroke_keys_uses_lazy_locator_and_async_delay(monkeypatch):
    locator = FakeLocator()
    get_element_calls = []
    sleep_calls = []

    async def fake_get_element(*args, **kwargs):
        get_element_calls.append(kwargs)
        return locator

    async def fake_sleep(delay):
        sleep_calls.append(delay)

    monkeypatch.setattr(pw.PlaywrightLocator, "Get_Element", fake_get_element)
    monkeypatch.setattr(pw.asyncio, "sleep", fake_sleep)

    result = asyncio.run(
        pw.Keystroke_For_Element(
            [
                ("id", "element parameter", "search"),
                ("delay", "optional parameter", "0.25"),
                ("keystroke keys", "playwright action", "Tab,2"),
            ]
        )
    )

    assert result == "passed"
    assert get_element_calls[0]["resolve"] is False
    assert locator.calls == [("press", "Tab", {}), ("press", "Tab", {})]
    assert sleep_calls == [0.25, 0.25]


def test_validate_text_uses_lazy_locator(monkeypatch):
    locator = FakeLocator("Header\nSuccess\nFooter")
    calls = []

    async def fake_get_element(*args, **kwargs):
        calls.append(kwargs)
        return locator

    monkeypatch.setattr(pw.PlaywrightLocator, "Get_Element", fake_get_element)

    result = asyncio.run(
        pw.Validate_Text(
            [
                ("id", "element parameter", "message"),
                ("validate full text", "playwright action", "Success"),
            ]
        )
    )

    assert result == "passed"
    assert calls[0]["resolve"] is False
    assert ("count",) not in locator.calls


def test_select_uses_lazy_locator(monkeypatch):
    locator = FakeLocator()
    calls = []

    async def fake_get_element(*args, **kwargs):
        calls.append(kwargs)
        return locator

    monkeypatch.setattr(pw.PlaywrightLocator, "Get_Element", fake_get_element)

    result = asyncio.run(
        pw.Select_Deselect(
            [
                ("id", "element parameter", "country"),
                ("select by value", "playwright action", "US"),
            ]
        )
    )

    assert result == "passed"
    assert calls[0]["resolve"] is False
    assert locator.calls == [("select_option", {"value": "US"})]


def test_check_uncheck_uses_lazy_locator(monkeypatch):
    locator = FakeLocator()
    calls = []

    async def fake_get_element(*args, **kwargs):
        calls.append(kwargs)
        return locator

    monkeypatch.setattr(pw.PlaywrightLocator, "Get_Element", fake_get_element)

    result = asyncio.run(
        pw.check_uncheck(
            [
                ("id", "element parameter", "agree"),
                ("check", "playwright action", "check"),
            ]
        )
    )

    assert result == "passed"
    assert calls[0]["resolve"] is False
    assert locator.calls == [("is_checked",), ("click", {})]


def test_scroll_to_element_uses_lazy_locator_without_default_extra_delay(monkeypatch):
    locator = FakeLocator()
    calls = []
    sleep_calls = []

    async def fake_get_element(*args, **kwargs):
        calls.append(kwargs)
        return locator

    async def fake_sleep(delay):
        sleep_calls.append(delay)

    monkeypatch.setattr(pw.PlaywrightLocator, "Get_Element", fake_get_element)
    monkeypatch.setattr(pw.asyncio, "sleep", fake_sleep)

    result = asyncio.run(
        pw.scroll_to_element(
            [
                ("id", "element parameter", "footer"),
                ("scroll to element", "playwright action", "scroll to element"),
            ]
        )
    )

    assert result == "passed"
    assert calls[0]["resolve"] is False
    assert sleep_calls == []
    assert locator.evaluated[-1][0] == "el => el.scrollIntoView(true)"


def test_slider_bar_uses_lazy_locator(monkeypatch):
    locator = FakeLocator()
    calls = []

    async def fake_get_element(*args, **kwargs):
        calls.append(kwargs)
        return locator

    monkeypatch.setattr(pw.PlaywrightLocator, "Get_Element", fake_get_element)

    result = asyncio.run(
        pw.slider_bar(
            [
                ("id", "element parameter", "volume"),
                ("slider bar", "playwright action", "25"),
            ]
        )
    )

    assert result == "passed"
    assert calls[0]["resolve"] is False
    assert locator.calls == [("bounding_box", {})]
    assert pw.current_page.mouse.calls == [("click", 60.0, 35.0)]


def test_if_element_exists_uses_resolved_lookup(monkeypatch):
    locator = FakeLocator()
    calls = []

    async def fake_get_element(*args, **kwargs):
        calls.append(kwargs)
        return locator

    monkeypatch.setattr(pw.PlaywrightLocator, "Get_Element", fake_get_element)

    result = asyncio.run(
        pw.if_element_exists(
            [
                ("id", "element parameter", "maybe"),
                ("if element exists", "playwright action", "if element exists"),
            ]
        )
    )

    assert result == "passed"
    assert "resolve" not in calls[0]
    assert ("count",) in locator.calls


def test_wait_for_element_uses_single_lazy_wait(monkeypatch):
    calls = []

    async def fake_wait_for_element(*args, **kwargs):
        calls.append(kwargs)
        return "passed"

    monkeypatch.setattr(pw.PlaywrightLocator, "wait_for_element", fake_wait_for_element)

    result = asyncio.run(
        pw.Wait_For_Element(
            [
                ("id", "element parameter", "ready"),
                ("state", "input parameter", "attached"),
                ("wait for element", "playwright action", "5"),
            ]
        )
    )

    assert result == "passed"
    assert calls == [{"state": "attached", "timeout": 5000, "frame_locator": None}]


def test_legacy_wait_with_playwright_driver_routes_to_playwright_wait():
    sr.Set_Shared_Variables("BROWSER_DRIVER", "playwright")
    data_set = [("wait", "selenium action", "150")]

    action_subfield = sa.get_browser_driver_routing("selenium action", data_set)
    action_name = sa.normalize_legacy_playwright_action_name("wait", action_subfield)
    module, function, original_module, screenshot = sa.common.get_module_and_function(
        action_name,
        action_subfield,
    )

    assert (module, function, original_module, screenshot) == (
        "playwright",
        "Wait_For_Element",
        "",
        "web",
    )


def test_legacy_wait_with_selenium_driver_keeps_common_wait_route():
    sr.Set_Shared_Variables("BROWSER_DRIVER", "selenium")
    data_set = [("wait", "selenium action", "150")]

    action_subfield = sa.get_browser_driver_routing("selenium action", data_set)
    action_name = sa.normalize_legacy_playwright_action_name("wait", action_subfield)
    module, function, original_module, screenshot = sa.common.get_module_and_function(
        action_name,
        action_subfield,
    )

    assert (module, function, original_module, screenshot) == (
        "common",
        "Wait_For_Element",
        "selenium",
        "none",
    )


def test_legacy_wait_defaults_to_visible_with_action_timeout(monkeypatch):
    calls = []

    async def fake_wait_for_element(*args, **kwargs):
        calls.append(kwargs)
        return "passed"

    monkeypatch.setattr(pw.PlaywrightLocator, "wait_for_element", fake_wait_for_element)

    result = asyncio.run(
        pw.Wait_For_Element(
            [
                ("id", "element parameter", "ready"),
                ("wait", "selenium action", "150"),
            ]
        )
    )

    assert result == "passed"
    assert calls == [{"state": "visible", "timeout": 150000, "frame_locator": None}]


def test_legacy_wait_with_allow_hidden_waits_for_attached(monkeypatch):
    calls = []

    async def fake_wait_for_element(*args, **kwargs):
        calls.append(kwargs)
        return "passed"

    monkeypatch.setattr(pw.PlaywrightLocator, "wait_for_element", fake_wait_for_element)

    result = asyncio.run(
        pw.Wait_For_Element(
            [
                ("id", "element parameter", "ready"),
                ("allow hidden", "optional parameter", "yes"),
                ("wait", "selenium action", "10"),
            ]
        )
    )

    assert result == "passed"
    assert calls == [{"state": "attached", "timeout": 10000, "frame_locator": None}]


def test_legacy_wait_disable_defaults_to_hidden_with_action_timeout(monkeypatch):
    calls = []

    async def fake_wait_for_element(*args, **kwargs):
        calls.append(kwargs)
        return "passed"

    monkeypatch.setattr(pw.PlaywrightLocator, "wait_for_element", fake_wait_for_element)

    result = asyncio.run(
        pw.Wait_For_Element(
            [
                ("id", "element parameter", "ready"),
                ("wait disable", "playwright action", "7"),
            ]
        )
    )

    assert result == "passed"
    assert calls == [{"state": "hidden", "timeout": 7000, "frame_locator": None}]


def test_legacy_wait_disable_with_allow_hidden_waits_for_detached(monkeypatch):
    calls = []

    async def fake_wait_for_element(*args, **kwargs):
        calls.append(kwargs)
        return "passed"

    monkeypatch.setattr(pw.PlaywrightLocator, "wait_for_element", fake_wait_for_element)

    result = asyncio.run(
        pw.Wait_For_Element(
            [
                ("id", "element parameter", "ready"),
                ("allow hidden", "optional parameter", "yes"),
                ("wait disable", "selenium action", "3"),
            ]
        )
    )

    assert result == "passed"
    assert calls == [{"state": "detached", "timeout": 3000, "frame_locator": None}]


def test_explicit_state_overrides_legacy_wait_default(monkeypatch):
    calls = []

    async def fake_wait_for_element(*args, **kwargs):
        calls.append(kwargs)
        return "passed"

    monkeypatch.setattr(pw.PlaywrightLocator, "wait_for_element", fake_wait_for_element)

    result = asyncio.run(
        pw.Wait_For_Element(
            [
                ("id", "element parameter", "ready"),
                ("state", "input parameter", "detached"),
                ("wait disable", "selenium action", "3"),
            ]
        )
    )

    assert result == "passed"
    assert calls == [{"state": "detached", "timeout": 3000, "frame_locator": None}]


def test_explicit_state_overrides_allow_hidden_state_mapping(monkeypatch):
    calls = []

    async def fake_wait_for_element(*args, **kwargs):
        calls.append(kwargs)
        return "passed"

    monkeypatch.setattr(pw.PlaywrightLocator, "wait_for_element", fake_wait_for_element)

    result = asyncio.run(
        pw.Wait_For_Element(
            [
                ("id", "element parameter", "ready"),
                ("allow hidden", "optional parameter", "yes"),
                ("state", "input parameter", "visible"),
                ("wait", "selenium action", "4"),
            ]
        )
    )

    assert result == "passed"
    assert calls == [{"state": "visible", "timeout": 4000, "frame_locator": None}]


def test_resize_window_accepts_selenium_element_parameter_rows():
    result = asyncio.run(
        pw.resize_window(
            [
                ("width", "element parameter", "50%"),
                ("height", "element parameter", "25%"),
                ("resize window", "selenium action", "resize window"),
            ]
        )
    )

    assert result == "passed"
    assert pw.current_page.viewport_size == {"width": 500, "height": 200}
