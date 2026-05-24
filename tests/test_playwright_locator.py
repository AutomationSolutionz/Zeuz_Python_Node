import asyncio

from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from Framework.Built_In_Automation.Web.Playwright import locator as playwright_locator


class FakeLocator:
    def __init__(self, name="root", count=1, total_count=None, texts=None, text=""):
        self.name = name
        self._count = count
        self._total_count = count if total_count is None else total_count
        self.texts = texts
        self.text = text
        self.filtered = False
        self.nth_index = None
        self.wait_calls = []
        self.queries = []

    def locator(self, query):
        self.queries.append(query)
        return FakeLocator(f"{self.name}.locator({query})", self._count, self._total_count, self.texts, self.text)

    def filter(self, **kwargs):
        filtered = FakeLocator(f"{self.name}.filter", self._count, self._total_count, self.texts, self.text)
        filtered.filtered = kwargs.get("visible") is True
        return filtered

    @property
    def first(self):
        text = self.texts[0] if self.texts else self.text
        first = FakeLocator(f"{self.name}.first", min(self._count, 1), self._total_count, self.texts, text)
        first.filtered = self.filtered
        return first

    def nth(self, index):
        text = self.texts[index] if self.texts and 0 <= index < len(self.texts) else self.text
        nth = FakeLocator(f"{self.name}.nth({index})", 1, self._total_count, self.texts, text)
        nth.nth_index = index
        nth.filtered = self.filtered
        return nth

    async def wait_for(self, state="visible", timeout=None):
        self.wait_calls.append((state, timeout))
        if self._count == 0:
            raise TimeoutError("not found")

    async def count(self):
        return self._count

    async def all(self):
        return [self.nth(i) for i in range(self._count)]

    async def text_content(self):
        return self.text

    async def inner_text(self):
        return self.text

    async def evaluate(self, script):
        return '<button id="save">Save</button>'


class FakePage:
    def __init__(self, locator_result):
        self.locator_result = locator_result
        self.queries = []

    def locator(self, query):
        self.queries.append(query)
        return self.locator_result


def setup_function():
    sr.shared_variables.clear()
    sr.Set_Shared_Variables("element_wait", 1)


def test_parser_preserves_numbered_relationship_and_shadow_rows():
    params = playwright_locator._parse_element_params(
        [
            ("tag", "element parameter", "button"),
            ("class", "parent 2 parameter", "panel"),
            ("id", "sr 1 element parameter", "shadow-host"),
            ("wait", "optional parameter", "3"),
        ]
    )

    assert params["element_params"] == [("tag", "button")]
    assert params["parent_params"] == [("class", "parent 2 parameter", "panel")]
    assert params["shadow_root_params"] == [("id", "sr 1 element parameter", "shadow-host")]
    assert ("id", "sr 1 element parameter", "shadow-host") not in params["locator_rows"]
    assert params["wait"] == 3


def test_legacy_query_matches_selenium_for_tag_and_text():
    params = playwright_locator._parse_element_params(
        [
            ("tag", "element parameter", "button"),
            ("text", "element parameter", "Save"),
        ]
    )

    query, query_type = playwright_locator._build_legacy_query(params["locator_rows"])

    assert query_type == "xpath"
    assert query == '//button[text()="Save"]'


def test_legacy_query_preserves_parent_child_sibling_rows():
    params = playwright_locator._parse_element_params(
        [
            ("tag", "element parameter", "input"),
            ("type", "element parameter", "password"),
            ("id", "parent parameter", "login-form"),
            ("text", "child parameter", "Required"),
        ]
    )

    query, query_type = playwright_locator._build_legacy_query(params["locator_rows"])

    assert query_type == "xpath"
    assert "input" in query
    assert '[@type="password"]' in query
    assert 'ancestor::*[@id="login-form"]' in query
    assert 'descendant::*[text()="Required"]' in query


def test_resolve_single_returns_first_for_multiple_matches():
    params = playwright_locator._parse_element_params(
        [("tag", "element parameter", "button")]
    )
    root = FakeLocator(count=3)

    result = asyncio.run(playwright_locator._resolve_single(root, params, 1000, "test"))

    assert isinstance(result, FakeLocator)
    assert result.name.endswith(".filter.first")
    assert result.filtered is True


def test_resolve_single_honors_index_after_visibility_filter():
    params = playwright_locator._parse_element_params(
        [
            ("tag", "element parameter", "button"),
            ("index", "element parameter", "2"),
        ]
    )
    root = FakeLocator(count=4)

    result = asyncio.run(playwright_locator._resolve_single(root, params, 1000, "test"))

    assert isinstance(result, FakeLocator)
    assert result.nth_index == 2
    assert result.filtered is True


def test_get_element_uses_legacy_xpath_and_saves_shared_variables():
    fake_locator = FakeLocator(count=2)
    page = FakePage(fake_locator)

    result = asyncio.run(
        playwright_locator.Get_Element(
            [
                ("tag", "element parameter", "button"),
                ("text", "element parameter", "Save"),
                ("saved_button", "save parameter", "yes"),
            ],
            page,
        )
    )

    assert result.name.endswith(".filter.first")
    assert page.queries == ['xpath=//button[text()="Save"]']
    assert sr.Get_Shared_Variables("saved_button") is result
    assert sr.Get_Shared_Variables("zeuz_element") is result


def test_get_element_accepts_selenium_return_all_elements_keyword():
    fake_locator = FakeLocator(count=2)
    page = FakePage(fake_locator)

    result = asyncio.run(
        playwright_locator.Get_Element(
            [("tag", "element parameter", "button")],
            page,
            return_all_elements=True,
        )
    )

    assert len(result) == 2
    assert page.queries == ["xpath=//button"]


def test_unique_parameter_takes_precedence_over_raw_xpath_like_selenium():
    fake_locator = FakeLocator(count=1)
    page = FakePage(fake_locator)

    result = playwright_locator._build_locator(
        page,
        [
            ("id", "unique parameter", "primary"),
            ("xpath", "element parameter", "//button[@id='secondary']"),
        ],
        playwright_locator._parse_element_params(
            [
                ("id", "unique parameter", "primary"),
                ("xpath", "element parameter", "//button[@id='secondary']"),
            ]
        ),
    )

    assert result.query_type == "unique"
    assert page.queries == ['xpath=//*[@id="primary"]']


def test_shadow_dom_builder_uses_sr_rows_and_css_query_chain():
    params = playwright_locator._parse_element_params(
        [
            ("id", "sr 1 element parameter", "host"),
            ("tag", "element parameter", "button"),
            ("data-action", "element parameter", "save"),
        ]
    )
    page = FakePage(FakeLocator())

    result = playwright_locator._build_shadow_dom_locator(page, params)

    assert result.query_type == "shadow css"
    assert result.query == 'xpath=//*[@id="host"] >> button[data-action="save"]'


def test_raw_xpath_ignores_additional_constraints_like_selenium():
    fake_locator = FakeLocator(count=1)
    page = FakePage(fake_locator)
    params = playwright_locator._parse_element_params(
        [
            ("xpath", "element parameter", "//button[@id='save']"),
            ("text", "element parameter", "Ignored"),
        ]
    )

    result = playwright_locator._build_locator(page, params["all_rows"], params)

    assert result.query_type == "xpath"
    assert page.queries == ["xpath=//button[@id='save']"]


def test_allow_hidden_does_not_apply_visible_filter():
    params = playwright_locator._parse_element_params(
        [
            ("tag", "element parameter", "button"),
            ("allow hidden", "optional parameter", "yes"),
        ]
    )
    root = FakeLocator(count=2)

    result = asyncio.run(playwright_locator._resolve_single(root, params, 1000, "test"))

    assert isinstance(result, FakeLocator)
    assert result.filtered is False


def test_resolve_single_negative_index():
    params = playwright_locator._parse_element_params(
        [
            ("tag", "element parameter", "button"),
            ("index", "element parameter", "-1"),
        ]
    )
    root = FakeLocator(count=4)

    result = asyncio.run(playwright_locator._resolve_single(root, params, 1000, "test"))

    assert isinstance(result, FakeLocator)
    assert result.nth_index == 3


def test_shadow_dom_rejects_duplicate_sr_indices():
    params = playwright_locator._parse_element_params(
        [
            ("id", "sr 1 element parameter", "host-a"),
            ("class", "sr 1 element parameter", "host-b"),
            ("tag", "element parameter", "button"),
        ]
    )
    page = FakePage(FakeLocator())

    assert playwright_locator._build_shadow_dom_locator(page, params) is None


def test_shadow_dom_rejects_text_selector():
    params = playwright_locator._parse_element_params(
        [
            ("text", "sr 1 element parameter", "Host"),
            ("tag", "element parameter", "button"),
        ]
    )
    page = FakePage(FakeLocator())

    assert playwright_locator._build_shadow_dom_locator(page, params) is None


def test_text_filter_matches_normalized_nbsp_text():
    page = FakePage(FakeLocator(count=2, texts=["Hello\xa0World", "Other"]))

    result = asyncio.run(
        playwright_locator._text_filter(
            [
                ("tag", "element parameter", "div"),
                ("text", "element parameter", "Hello World"),
            ],
            page,
            None,
            {"allow_hidden": False, "index": None, "sibling_params": []},
            1000,
            False,
        )
    )

    assert isinstance(result, FakeLocator)
    assert result.text == "Hello\xa0World"
