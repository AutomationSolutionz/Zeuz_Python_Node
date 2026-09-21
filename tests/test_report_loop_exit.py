"""Report-name fallback loops must observe results from conditional children."""
import shutil

import pytest

from Framework.Built_In_Automation.Sequential_Actions import sequential_actions as sa


@pytest.mark.parametrize("backend", ["selenium", "playwright", "if else"])
@pytest.mark.parametrize("outcome,control,expected_clicks,expected_result", [
    ("passed", "exit loop and continue", 1, "passed"),
    ("zeuz_failed", "exit loop and continue", 0, "passed"),
    ("passed", "exit loop and fail", 1, "zeuz_failed"),
    ("zeuz_failed", "exit loop and fail", 0, "zeuz_failed"),
    ("passed", "continue to next iter", 3, "passed"),
    ("zeuz_failed", "continue to next iter", 0, "passed"),
    ("skipped", "exit loop and continue", 0, "passed"),
    ("disabled", "exit loop and continue", 3, "passed"),
])
def test_report_loop_observes_executed_child(
    monkeypatch, backend, outcome, control, expected_clicks, expected_result,
    browser_page=None,
):
    # Same relative references as the logs: loop -> conditional -> attribute,
    # Python action, click. The watched attribute is executed by the conditional.
    child_actions = "next to next+1, next+4"
    conditional = (
        [("if True", "if else", child_actions)] if backend == "if else" else
        [("true", backend + " conditional action", child_actions)]
    )
    if outcome == "skipped":
        conditional = [("if False", "if else", child_actions)]
    watched_status = "fail" if outcome == "zeuz_failed" else "pass"
    data = [
        [("for reportName in ['Report', 'Report', 'Report']", "for loop action", "next to next+2"),
         ("loop type", "optional parameter", "action"),
         (control, "optional loop control", "if next+1 " + watched_status)],
        conditional,
        [("save attribute", "selenium action", "href")],
        [("execute python code", "common action", "report_name_matched = True")],
        [], [],
        [("click", "selenium action", "click")],
    ]
    info = [{"Action name": str(i), "Action disabled": False} for i in range(len(data))]
    info[2]["Action disabled"] = outcome == "disabled"
    values = {sa.CommonUtil.dont_prettify_on_server[0]: data}
    iterations = []

    def save(key, value, **kwargs):
        values[key] = value
        if key == "reportName":
            iterations.append(value)
    for name, value in {
        "current_step_no": "1", "current_step_sequence": 1,
        "current_action_no": "1", "current_tc_no": "TEST-report-loop",
        "runid_index": 0, "tc_index": 0, "debug_status": False,
        "performance_testing": True,
        "all_logs_json": [{"test_cases": [{"steps": [{}]}]}],
        "all_step_dataset": [data], "all_action_info": [info],
    }.items():
        monkeypatch.setattr(sa.CommonUtil, name, value)
    monkeypatch.setattr(sa.CommonUtil, "ExecLog", lambda *a, **kw: None)
    monkeypatch.setattr(sa.sr, "test_action_info", info)
    monkeypatch.setattr(sa.sr, "shared_variables", values)
    monkeypatch.setattr(sa.sr, "Set_Shared_Variables", save)
    monkeypatch.setattr(sa.sr, "Get_Shared_Variables", lambda key, **kw: values.get(key, "zeuz_failed"))
    monkeypatch.setattr(sa.sr, "get_previous_response_variables_in_strings", lambda value: value)
    monkeypatch.setattr(sa.common, "shared_variable_to_value", lambda rows: rows)
    monkeypatch.setattr(sa.common, "unmask_step_data", lambda rows: rows)
    monkeypatch.setattr(sa.common, "adjust_element_parameters", lambda rows, platforms: rows)
    monkeypatch.setattr(sa, "load_sa_modules", lambda module: "passed")
    monkeypatch.setattr(sa, "_route_playwright_action", lambda name, subfield, rows: subfield)
    monkeypatch.setattr(sa, "_run_action_with_timeout", lambda fn, rows: fn(rows))
    monkeypatch.setattr(sa, "_get_conditional_element", lambda args: object())
    calls = []

    def action(rows, row):
        calls.append(row[0])
        if browser_page is not None and row[0] == "click":
            from Framework.Built_In_Automation.Web.Playwright import BuiltInFunctions as pw
            monkeypatch.setattr(pw, "get_driver", lambda: browser_page)
            return pw.Click_Element([
                ("id", "element parameter", "report"),
                ("wait", "optional parameter", "0.2"),
                ("click", "action", "click"),
            ])
        return outcome if row[0] == "save attribute" else "passed"

    monkeypatch.setattr(sa, "Action_Handler", action)
    result, _ = sa.for_loop_action(data, 0)
    assert result == expected_result
    assert calls.count("click") == expected_clicks
    expected_iterations = 3 if outcome in ("skipped", "disabled") or control == "continue to next iter" else 1
    assert calls.count("save attribute") == (0 if outcome in ("skipped", "disabled") else expected_iterations)
    assert len(iterations) == expected_iterations


def test_report_loop_does_not_click_again_under_loading_curtain(monkeypatch):
    if not shutil.which("google-chrome"):
        pytest.skip("System Chrome is unavailable")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as manager:
        browser = manager.chromium.launch(channel="chrome", headless=True)
        try:
            page = browser.new_page()
            page.set_default_timeout(300)
            page.set_content('''
                <button id="report" onclick="window.clicks++; document.querySelector('#curtain').hidden = false">Report</button>
                <div id="curtain" hidden style="position:fixed;inset:0;z-index:10;background:white">Loading</div>
                <script>window.clicks = 0;</script>
            ''')
            test_report_loop_observes_executed_child(
                monkeypatch, "playwright", "passed", "exit loop and continue", 1, "passed",
                browser_page=page,
            )
            assert page.evaluate("window.clicks") == 1
            assert page.locator("#curtain").is_visible()
        finally:
            browser.close()
