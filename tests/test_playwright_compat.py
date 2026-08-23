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
