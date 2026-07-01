import asyncio

from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
    LocateElement,
)


class FakeLocator:
    def __init__(self, name="root", count=1, texts=None, text="", stats=None):
        self.name = name
        self._count = count
        self.texts = texts or []
        self.text = text
        self.stats = stats if stats is not None else {"wait": 0, "count": 0}
        self.filtered = False
        self.nth_index = None
        self.queries = []
        self.children = {}

    def locator(self, query):
        self.queries.append(query)
        child = self.children.get(query)
        if child:
            return child
        return FakeLocator(f"{self.name}.locator({query})", self._count, self.texts, self.text, self.stats)

    def filter(self, **kwargs):
        filtered = FakeLocator(f"{self.name}.filter", self._count, self.texts, self.text, self.stats)
        filtered.filtered = kwargs.get("visible") is True
        return filtered

    @property
    def first(self):
        text = self.texts[0] if self.texts else self.text
        first = FakeLocator(f"{self.name}.first", min(self._count, 1), self.texts, text, self.stats)
        first.filtered = self.filtered
        return first

    def nth(self, index):
        text = self.texts[index] if 0 <= index < len(self.texts) else self.text
        nth = FakeLocator(f"{self.name}.nth({index})", 1, self.texts, text, self.stats)
        nth.nth_index = index
        nth.filtered = self.filtered
        nth.queries = self.queries
        nth.children = self.children
        return nth

    async def wait_for(self, state="visible", timeout=None):
        self.stats["wait"] += 1
        if self._count == 0:
            raise TimeoutError("not found")

    async def count(self):
        self.stats["count"] += 1
        return self._count

    async def all(self):
        return [self.nth(i) for i in range(self._count)]

    async def text_content(self):
        return self.text


class FakePage:
    def __init__(self, locator_result=None):
        self.locator_result = locator_result or FakeLocator()
        self.queries = []
        self.children = {}

    def locator(self, query):
        self.queries.append(query)
        return self.children.get(query, self.locator_result)


def run(coro):
    return asyncio.run(coro)


def setup_function():
    sr.shared_variables.clear()
    sr.Set_Shared_Variables("element_wait", 1)
    LocateElement.driver_type = None


def test_normal_playwright_action_returns_lazy_visible_first_locator():
    fake_locator = FakeLocator(count=2)
    page = FakePage(fake_locator)

    result = run(
        LocateElement.Get_Element(
            [
                ("tag", "element parameter", "button"),
                ("click", "playwright action", "click"),
            ],
            page,
        )
    )

    assert result.name.endswith(".filter.first")
    assert result.filtered is True
    assert fake_locator.stats == {"wait": 0, "count": 0}


def test_conditional_non_action_lookup_resolves_and_fails_on_no_match():
    fake_locator = FakeLocator(count=0)
    page = FakePage(fake_locator)

    result = run(
        LocateElement.Get_Element(
            [("tag", "element parameter", "missing")],
            page,
        )
    )

    assert result == "zeuz_failed"
    assert fake_locator.stats["wait"] == 1


def test_return_all_elements_resolves_all_locators():
    fake_locator = FakeLocator(count=2)

    result = run(
        LocateElement.Get_Element(
            [("tag", "element parameter", "button")],
            FakePage(fake_locator),
            return_all_elements=True,
        )
    )

    assert len(result) == 2
    assert fake_locator.stats["wait"] == 1


def test_parent_locator_scopes_search():
    parent = FakeLocator("parent", count=1)

    result = run(
        LocateElement.Get_Element(
            [("tag", "element parameter", "span")],
            parent,
            return_all_elements=True,
        )
    )

    assert parent.queries == ["xpath=//span"]
    assert len(result) == 1


def test_allow_hidden_skips_visible_filter_for_lazy_action():
    fake_locator = FakeLocator(count=2)

    result = run(
        LocateElement.Get_Element(
            [
                ("tag", "element parameter", "button"),
                ("allow hidden", "optional parameter", "yes"),
                ("click", "playwright action", "click"),
            ],
            FakePage(fake_locator),
        )
    )

    assert result.name.endswith(".first")
    assert ".filter" not in result.name
    assert result.filtered is False


def test_relationship_rows_use_shared_query_builder_for_playwright():
    page = FakePage(FakeLocator(count=1))

    run(
        LocateElement.Get_Element(
            [
                ("tag", "element parameter", "input"),
                ("type", "element parameter", "password"),
                ("id", "parent parameter", "login-form"),
                ("text", "child parameter", "Required"),
                ("click", "playwright action", "click"),
            ],
            page,
        )
    )

    assert page.queries == ['xpath=//input[@type="password"][descendant::*[text()="Required"]][(ancestor::*[@id="login-form"])[last()]]']


def test_index_handling_resolves_nth_locator():
    fake_locator = FakeLocator(count=4)

    result = run(
        LocateElement.Get_Element(
            [
                ("tag", "element parameter", "button"),
                ("index", "element parameter", "2"),
            ],
            FakePage(fake_locator),
        )
    )

    assert result.nth_index == 2


def test_text_filter_matches_normalized_nbsp_text():
    page = FakePage(FakeLocator(count=0))
    page.children["xpath=//div"] = FakeLocator(count=2, texts=["Hello\xa0World", "Other"])

    result = run(
        LocateElement.Get_Element(
            [
                ("tag", "element parameter", "div"),
                ("text", "element parameter", "Hello World"),
                ("text filter", "optional parameter", "true"),
            ],
            page,
        )
    )

    assert result.text == "Hello\xa0World"


def test_save_and_get_shared_variable():
    saved = run(
        LocateElement.Get_Element(
            [
                ("tag", "element parameter", "button"),
                ("saved_button", "save parameter", "yes"),
                ("click", "playwright action", "click"),
            ],
            FakePage(FakeLocator()),
        )
    )

    result = run(
        LocateElement.Get_Element(
            [("saved_button", "get parameter", "%|saved_button|%")],
            FakePage(FakeLocator()),
        )
    )

    assert result is saved


def test_raw_xpath_and_css():
    page = FakePage(FakeLocator())

    run(LocateElement.Get_Element([("xpath", "element parameter", "//button")], page))
    run(LocateElement.Get_Element([("css selector", "element parameter", "button.save")], page))

    assert page.queries == ["xpath=//button", "button.save"]


def test_unique_parameter_takes_precedence_over_raw_xpath():
    page = FakePage(FakeLocator())

    run(
        LocateElement.Get_Element(
            [
                ("id", "unique parameter", "primary"),
                ("xpath", "element parameter", "//button[@id='secondary']"),
            ],
            page,
        )
    )

    assert page.queries == ['[id="primary"]']


def test_shadow_dom_rows_build_locator_chain():
    host = FakeLocator("host", count=1)
    page = FakePage(FakeLocator())
    page.children['xpath=//*[@id="host"]'] = host

    result = run(
        LocateElement.Get_Element(
            [
                ("id", "sr 1 element parameter", "host"),
                ("tag", "element parameter", "button"),
                ("data-action", "element parameter", "save"),
            ],
            page,
            return_all_elements=True,
        )
    )

    assert page.queries == ['xpath=//*[@id="host"]']
    assert host.queries == ['button[data-action="save"]']
    assert len(result) == 1


def test_shared_playwright_frame_scope_for_page_driver():
    frame = FakeLocator("frame", count=1)
    sr.Set_Shared_Variables("playwright_frame", frame)

    run(
        LocateElement.Get_Element(
            [("tag", "element parameter", "button")],
            FakePage(FakeLocator()),
            return_all_elements=True,
        )
    )

    assert frame.queries == ["xpath=//button"]
