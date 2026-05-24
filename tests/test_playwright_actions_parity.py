import asyncio

from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from Framework.Built_In_Automation.Web.Playwright import BuiltInFunctions as pw


class FakePage:
    def __init__(self):
        self.url = "https://example.test/current"
        self.viewport_size = {"width": 1000, "height": 800}
        self.evaluated = []

    async def evaluate(self, script, arg=None):
        self.evaluated.append((script, arg))
        return "page-result"

    async def set_viewport_size(self, size):
        self.viewport_size = size


class FakeLocator:
    def __init__(self, text=""):
        self.text = text
        self.evaluated = []
        self.files = None

    async def inner_text(self):
        return self.text

    async def text_content(self):
        return self.text

    async def evaluate(self, script, arg=None):
        self.evaluated.append((script, arg))
        return "locator-result"

    async def set_input_files(self, file_path):
        self.files = file_path

    async def bounding_box(self):
        return {"x": 10, "y": 20, "width": 200, "height": 30}


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
