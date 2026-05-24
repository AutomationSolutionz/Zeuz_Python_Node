# -*- coding: utf-8 -*-
"""
Playwright Element Locator Module

This module resolves the standard Zeuz element step-data format to Playwright
Locator objects. Selenium compatibility is the primary contract: Selenium-style
element parameters are converted through LocateElement.py's query builder, then
executed with Playwright's Locator API.
"""

import inspect
import re
import sys
from dataclasses import dataclass
from typing import Any

from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from Framework.Utilities import CommonUtil
from Framework.Utilities.CommonUtil import failed_tag_list

MODULE_NAME = inspect.getmodulename(__file__)


@dataclass
class LocatorBuildResult:
    locator: Any
    query_type: str
    query: Any


async def Get_Element(
    step_data,
    page,
    return_all=False,
    element_wait=None,
    frame_locator=None,
    parent_locator=None,
    return_all_elements=False,
):
    """
    Resolve Zeuz step-data to a Playwright Locator.

    This function parses the same step_data format as LocateElement.Get_Element()
    but uses Playwright's Locator API for execution, preserving auto-wait and
    lazy evaluation benefits.

    Args:
        step_data: List of (left, mid, right) tuples - standard Zeuz format
        page: Playwright Page object
        return_all: If True, return list of all matching ElementHandles
        element_wait: Override default wait timeout (in seconds)
        frame_locator: Optional frame locator for iframe context
        parent_locator: Optional Locator to scope the search under a container element

    Returns:
        Locator | List[ElementHandle] | "zeuz_failed"

    Example:
        step_data = [
            ("id", "element parameter", "submit-btn"),
            ("click", "playwright action", "click"),
        ]
        locator = Get_Element(step_data, page)
        locator.click()  # Auto-waits for element

    The returned object intentionally mirrors Selenium LocateElement.Get_Element()
    semantics where possible: visible elements are preferred by default, multiple
    matches return the first match unless an index is provided, save/get parameter
    rows use shared variables, and failures return "zeuz_failed".
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        if return_all_elements:
            return_all = True

        params = _parse_element_params(step_data)
        if params.get("parse_error"):
            CommonUtil.ExecLog(sModuleInfo, params["parse_error"], 3)
            return "zeuz_failed"

        if params.get("get_parameter"):
            result = sr.parse_variable(params["get_parameter"])
            result = CommonUtil.ZeuZ_map_code_decoder(result)
            if result not in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Returning saved element '%s' from shared variables" % params["get_parameter"],
                    1,
                )
                return result

            CommonUtil.ExecLog(
                sModuleInfo,
                "Element named '%s' not found in shared variables" % params["get_parameter"],
                3,
            )
            return "zeuz_failed"

        timeout = _resolve_timeout(params, element_wait)
        build_result = _build_locator(page, step_data, params, frame_locator, parent_locator)
        if build_result is None or build_result.locator is None:
            CommonUtil.ExecLog(sModuleInfo, "Could not build locator from step data", 3)
            return "zeuz_failed"

        CommonUtil.ExecLog(
            sModuleInfo,
            f"To locate the Element we used {build_result.query_type}:\n{build_result.query}",
            5,
        )

        if return_all:
            result = await _resolve_all(build_result.locator, params, timeout, sModuleInfo)
            if not result and params.get("text_filter"):
                result = await _text_filter(step_data, page, frame_locator, params, timeout, return_all)
        else:
            result = await _resolve_single(build_result.locator, params, timeout, sModuleInfo)
            if result == "zeuz_failed" and params.get("text_filter"):
                result = await _text_filter(step_data, page, frame_locator, params, timeout, return_all)

        if result not in failed_tag_list:
            if not return_all:
                await _log_outer_html(result, sModuleInfo)
            if params.get("save_parameter"):
                sr.Set_Shared_Variables(params["save_parameter"], result)
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Saved element to variable '%s'" % params["save_parameter"],
                    1,
                )
            sr.Set_Shared_Variables("zeuz_element", result)
            return result

        await _log_frame_hint(page, sModuleInfo)
        return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _parse_element_params(step_data):
    """Parse Zeuz step-data without losing Selenium locator semantics."""

    params = {
        "index": None,
        "allow_hidden": False,
        "allow_disabled": False,
        "save_parameter": None,
        "get_parameter": None,
        "wait": None,
        "text_filter": False,
        "parse_error": None,
        "element_params": [],
        "parent_params": [],
        "child_params": [],
        "sibling_params": [],
        "preceding_params": [],
        "following_params": [],
        "unique_params": [],
        "shadow_root_params": [],
        "locator_rows": [],
        "element_ds": [],
        "all_rows": [],
    }

    for left, mid, right in step_data:
        left_raw = str(left).strip()
        mid_raw = str(mid).strip()
        right_raw = str(right)
        right_stripped = right_raw.strip()
        left_lower = left_raw.lower()
        mid_lower = mid_raw.lower()
        mid_key = _mid_key(mid_raw)
        row = (left_raw, mid_raw, right_raw)
        params["all_rows"].append(row)

        if mid_lower == "save parameter":
            if right_stripped != "ignore":
                params["save_parameter"] = left_raw
            continue

        if mid_lower == "get parameter":
            if right_stripped.startswith("%|") and right_stripped.endswith("|%"):
                params["get_parameter"] = right_stripped.strip("%").strip("|")
            else:
                params["parse_error"] = "Use '%| |%' sign at right column to get variable value"
            continue

        # Optional parameters
        if mid_lower in ("optional parameter", "option"):
            if left_lower == "allow hidden":
                params["allow_hidden"] = _truthy(right_stripped)
            elif left_lower == "allow disable":
                params["allow_disabled"] = _truthy(right_stripped)
            elif left_lower == "wait":
                try:
                    params["wait"] = float(right_stripped)
                except Exception:
                    params["parse_error"] = "Wait optional parameter must be numeric"
            elif left_lower == "text filter":
                params["text_filter"] = _truthy(right_stripped)
            continue

        if mid_lower.startswith("sr"):
            params["shadow_root_params"].append(row)
            continue

        if mid_key == "uniqueparameter":
            params["unique_params"].append((left_raw, right_raw))
            params["locator_rows"].append(row)
            params["element_ds"].append(row)
            continue

        if "parent" in mid_key and "parameter" in mid_key:
            params["parent_params"].append(row)
            params["locator_rows"].append(row)
            params["element_ds"].append(row)
            continue

        if "child" in mid_key and "parameter" in mid_key:
            params["child_params"].append(row)
            params["locator_rows"].append(row)
            params["element_ds"].append(row)
            continue

        if "sibling" in mid_key and "parameter" in mid_key:
            params["sibling_params"].append(row)
            params["locator_rows"].append(row)
            params["element_ds"].append(row)
            continue

        if "preceding" in mid_key and "parameter" in mid_key:
            params["preceding_params"].append(row)
            params["locator_rows"].append(row)
            params["element_ds"].append(row)
            continue

        if "following" in mid_key and "parameter" in mid_key:
            params["following_params"].append(row)
            params["locator_rows"].append(row)
            params["element_ds"].append(row)
            continue

        if mid_key == "elementparameter":
            params["locator_rows"].append(row)
            params["element_ds"].append(row)
            if left_lower == "index":
                try:
                    params["index"] = int(right_stripped)
                except Exception:
                    params["parse_error"] = "Index = 0 is set"
            else:
                params["element_params"].append((left_raw, right_raw))
            continue

        params["element_ds"].append(row)

    return params


def _build_locator(page, step_data, params, frame_locator=None, parent_locator=None):
    """
    Build a Playwright Locator from step data.

    Attempts these strategies in order:
    1. Playwright-native selectors (test-id, role, text, etc.) - fastest
    2. Direct xpath/css if provided
    3. Build xpath from element parameters using existing logic
    
    Args:
        page: Playwright Page object
        step_data: Step data for building xpath
        params: Parsed element parameters
        frame_locator: Optional frame locator for iframe context
        parent_locator: Scope search within this locator (overrides frame when both set).
    """

    # Parent scope wins, then iframe, then full page.
    if parent_locator is not None:
        base_locator = parent_locator
    else:
        base_locator = frame_locator if frame_locator else page

    if params["shadow_root_params"]:
        return _build_shadow_dom_locator(base_locator, params)

    native_locator = _build_native_locator(base_locator, params)
    if native_locator is not None:
        return native_locator

    if params["unique_params"]:
        legacy_locator = _build_legacy_locator(base_locator, params)
        if legacy_locator is not None:
            return legacy_locator

    raw_locator = _build_raw_locator(base_locator, step_data)
    if raw_locator is not None:
        return raw_locator

    legacy_locator = _build_legacy_locator(base_locator, params)
    if legacy_locator is not None:
        return legacy_locator

    return None


def _build_native_locator(base_locator, params):
    """Support explicit Playwright-only selector aliases without overriding Selenium semantics."""

    if _has_relationship_params(params) or params["unique_params"] or len(params["element_params"]) != 1:
        return None

    left, right = params["element_params"][0]
    left_lower = left.lower()
    if left_lower in ("test-id", "testid"):
        return LocatorBuildResult(base_locator.get_by_test_id(right), "playwright test-id", right)
    return None


def _build_raw_locator(base_locator, step_data):
    xpath_rows = []
    css_rows = []
    for left, mid, right in step_data:
        left_lower = str(left).strip().lower()
        mid_key = _mid_key(str(mid))
        if mid_key != "elementparameter":
            continue
        if left_lower == "xpath":
            xpath_rows.append(str(right).strip())
        elif left_lower in ("css", "css selector", "css_selector"):
            css_rows.append(str(right).strip())

    if xpath_rows and not css_rows:
        query = xpath_rows[0]
        return LocatorBuildResult(base_locator.locator(_as_playwright_xpath(query)), "xpath", query)
    if css_rows and not xpath_rows:
        query = css_rows[0]
        return LocatorBuildResult(base_locator.locator(query), "css", query)
    return None


def _build_legacy_locator(base_locator, params):
    query, query_type = _build_legacy_query(params["locator_rows"])
    if not query or not query_type:
        return None

    if query_type == "unique":
        locator = _build_unique_locator(base_locator, query[0], query[1])
        return LocatorBuildResult(locator, query_type, query)
    if query_type == "css":
        return LocatorBuildResult(base_locator.locator(query), query_type, query)
    if query_type == "xpath":
        return LocatorBuildResult(base_locator.locator(_as_playwright_xpath(query)), query_type, query)
    return None


def _build_legacy_query(locator_rows):
    if not locator_rows:
        return None, None

    try:
        from Framework.Built_In_Automation.Shared_Resources import LocateElement

        original_driver_type = getattr(LocateElement, "driver_type", None)
        LocateElement.driver_type = "selenium"
        try:
            return LocateElement._construct_query(locator_rows)
        finally:
            LocateElement.driver_type = original_driver_type
    except Exception as e:
        CommonUtil.ExecLog("_build_legacy_query", f"Error building Selenium-compatible query: {e}", 2)
        return None, None


def _build_unique_locator(base_locator, unique_key, unique_value):
    key = str(unique_key).strip().lower()
    value = str(unique_value).strip()

    if key in ("accessibility id", "accessibility-id", "content-desc", "content desc"):
        return base_locator.locator(_as_playwright_xpath(f"//*[@aria-label={_xpath_literal(value)}]"))
    if key == "id":
        return base_locator.locator(_as_playwright_xpath(f"//*[@id={_xpath_literal(value)}]"))
    if key == "name":
        return base_locator.locator(_as_playwright_xpath(f"//*[@name={_xpath_literal(value)}]"))
    if key == "class":
        klass = _xpath_literal(f" {value} ")
        return base_locator.locator(
            _as_playwright_xpath(f"//*[contains(concat(' ', normalize-space(@class), ' '), {klass})]")
        )
    if key == "tag":
        return base_locator.locator(_as_playwright_xpath(f"//{value}"))
    if key == "css":
        return base_locator.locator(value)
    if key == "xpath":
        return base_locator.locator(_as_playwright_xpath(value))
    if key == "text":
        return base_locator.locator(_as_playwright_xpath(f"//*[text()={_xpath_literal(value)}]"))
    if key == "*text":
        return base_locator.locator(_as_playwright_xpath(f"//*[contains(text(),{_xpath_literal(value)})]"))
    if key.startswith("**"):
        attr = key[2:]
        return base_locator.locator(
            _as_playwright_xpath(
                "//*[contains(translate(@%s,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),%s)]"
                % (attr, _xpath_literal(value.lower()))
            )
        )
    if key.startswith("*"):
        attr = key[1:]
        return base_locator.locator(_as_playwright_xpath(f"//*[contains(@{attr},{_xpath_literal(value)})]"))
    return base_locator.locator(_as_playwright_xpath(f"//*[@{key}={_xpath_literal(value)}]"))


def _build_shadow_dom_locator(base_locator, params):
    try:
        from Framework.Built_In_Automation.Shared_Resources import LocateElement

        shadow_root_params = []
        parent_params = []

        for left, mid, right in params["shadow_root_params"]:
            left_lower = left.strip().lower()
            if "text" in left_lower:
                CommonUtil.ExecLog(
                    "_build_shadow_dom_locator",
                    "Shadow DOM access requires attribute/tag/css selectors; text selectors are not supported",
                    3,
                )
                return None

            words = mid.strip().lower().split()
            if len(words) < 3 or len(words) > 4:
                CommonUtil.ExecLog("_build_shadow_dom_locator", f"Invalid shadow root parameter format: {mid}", 3)
                return None
            idx = int(words[1]) if len(words) == 4 else 1
            param = " ".join(words[-2:])
            normalized_row = [left, param, right]

            if "parent" in param:
                parent_params.append((idx, normalized_row))
            elif "element" in param:
                shadow_root_params.append((idx, normalized_row))
            else:
                CommonUtil.ExecLog(
                    "_build_shadow_dom_locator",
                    "Only shadow root parent parameter and element parameter rows are supported",
                    3,
                )
                return None

        parent_indices = [idx for idx, _ in parent_params]
        shadow_indices = [idx for idx, _ in shadow_root_params]
        if len(parent_indices) != len(set(parent_indices)) or len(shadow_indices) != len(set(shadow_indices)):
            CommonUtil.ExecLog("_build_shadow_dom_locator", "Duplicate shadow root indices found", 3)
            return None

        parent_params.sort(key=lambda item: item[0])
        shadow_root_params.sort(key=lambda item: item[0])
        current = base_locator
        query_parts = []

        for idx, shadow_param in shadow_root_params:
            query_rows = []
            for parent_idx, parent_param in parent_params:
                if parent_idx == idx:
                    query_rows.append(parent_param)
                    break
            query_rows.append(shadow_param)
            if idx == 1:
                host_query, host_query_type = _build_legacy_query(query_rows)
                if host_query_type == "xpath":
                    host_query = _as_playwright_xpath(host_query)
            else:
                host_query = LocateElement.build_css_selector_query(query_rows)
            if not host_query:
                return None
            current = current.locator(host_query)
            host_index = _index_from_rows([shadow_param]) or 0
            current = current.nth(host_index)
            query_parts.append(host_query)

        element_query = LocateElement.build_css_selector_query([list(row) for row in params["element_ds"]])
        if not element_query:
            return None
        query_parts.append(element_query)
        return LocatorBuildResult(current.locator(element_query), "shadow css", " >> ".join(query_parts))
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


async def _resolve_single(locator, params, timeout, sModuleInfo):
    effective_locator = _effective_locator(locator, params)
    state = "attached" if params.get("allow_hidden") else "visible"

    if not await _wait_for_locator(effective_locator, state, timeout):
        await _log_no_match(locator, params, sModuleInfo)
        return "zeuz_failed"

    count = await _safe_count(effective_locator)
    total_count = await _safe_count(locator)
    hidden_count = max(total_count - count, 0) if not params.get("allow_hidden") else 0

    index = params.get("index")
    if count == 0:
        await _log_no_match(locator, params, sModuleInfo)
        return "zeuz_failed"

    if index is None:
        if count > 1:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Found {count} displayed elements. Returning the first displayed element only. Consider providing index",
                2,
            )
        elif hidden_count > 0:
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Found {hidden_count} hidden elements and {count} displayed element. Returning the displayed element only",
                2,
            )
        return _first_locator(effective_locator)

    if count == 1:
        if index not in (-1, 0):
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Found {count} element but provided index {index} is out of range. Returning the only element",
                2,
            )
        return _first_locator(effective_locator)

    resolved_index = index if index >= 0 else count + index
    if 0 <= resolved_index < count:
        CommonUtil.ExecLog(
            sModuleInfo,
            f"Found {count} elements. Returning the element of index {index}",
            1,
        )
        return effective_locator.nth(resolved_index)

    CommonUtil.ExecLog(sModuleInfo, f"Found {count} elements. Index {index} exceeds the number of elements found", 3)
    return "zeuz_failed"


async def _resolve_all(locator, params, timeout, sModuleInfo):
    effective_locator = _effective_locator(locator, params)
    state = "attached" if params.get("allow_hidden") else "visible"
    if not await _wait_for_locator(effective_locator, state, timeout):
        CommonUtil.ExecLog(sModuleInfo, "Found 0 elements", 3)
        return []

    all_locators = await effective_locator.all()
    total_count = await _safe_count(locator)
    displayed_count = len(all_locators)
    hidden_count = max(total_count - displayed_count, 0) if not params.get("allow_hidden") else 0

    if params.get("allow_hidden"):
        CommonUtil.ExecLog(sModuleInfo, f"Found {displayed_count} elements. Returning all of them", 1)
    else:
        CommonUtil.ExecLog(
            sModuleInfo,
            f"Found {hidden_count} hidden elements and {displayed_count} displayed elements. Returning displayed elements only",
            1,
        )
    return all_locators


async def _text_filter(step_data, page, frame_locator, original_params, timeout, return_all):
    sModuleInfo = "text_filter : " + MODULE_NAME

    if original_params["sibling_params"]:
        return "zeuz_failed"

    filters = []
    temp_step_data = []
    for left, mid, right in step_data:
        left_lower = str(left).strip().lower()
        mid_lower = str(mid).strip().lower()
        if left_lower.replace("*", "") == "text" and mid_lower == "element parameter":
            filters.append((left_lower, str(right)))
        else:
            temp_step_data.append((left, mid, right))

    if not filters:
        return "zeuz_failed"

    temp_params = _parse_element_params(temp_step_data)
    temp_params["allow_hidden"] = original_params.get("allow_hidden", False)
    build_result = _build_locator(page, temp_step_data, temp_params, frame_locator)
    if build_result is None:
        return "zeuz_failed"

    CommonUtil.ExecLog(sModuleInfo, "No Element found. Now we are trying to handle &nbsp; and <space>", 1)
    CommonUtil.ExecLog(sModuleInfo, f"To locate the Element we used {build_result.query_type}:\n{build_result.query}", 5)

    candidate_locator = _effective_locator(build_result.locator, temp_params)
    state = "attached" if temp_params.get("allow_hidden") else "visible"
    if not await _wait_for_locator(candidate_locator, state, timeout):
        return "zeuz_failed"

    candidates = await candidate_locator.all()
    matches = []
    similar_texts = []
    for candidate in candidates:
        try:
            text = await candidate.text_content() or ""
        except Exception:
            continue
        if _matches_text_filters(text, filters):
            matches.append(candidate)
        elif _similar_text(text, filters) and text not in similar_texts:
            similar_texts.append(text)

    if return_all:
        CommonUtil.ExecLog(sModuleInfo, f"Returning {len(matches)} elements after applying Text Filter", 1)
        return matches

    if not matches:
        CommonUtil.ExecLog(sModuleInfo, "Found no element after applying Text Filter", 3)
        if similar_texts:
            CommonUtil.ExecLog(sModuleInfo, f"These are the similar texts found in the HTML: {str(similar_texts)[1:-1]}", 3)
        return "zeuz_failed"

    index = original_params.get("index") or 0
    resolved_index = index if index >= 0 else len(matches) + index
    if not 0 <= resolved_index < len(matches):
        CommonUtil.ExecLog(sModuleInfo, f"Found {len(matches)} elements after applying Text Filter. Index out of range", 3)
        return "zeuz_failed"

    CommonUtil.ExecLog(sModuleInfo, f"Found {len(matches)} elements after applying Text Filter. Returning index {index}", 1)
    return matches[resolved_index]


async def wait_for_element(step_data, page, state="visible", timeout=None):
    """Wait for an element to reach a Playwright state."""

    sModuleInfo = "wait_for_element"

    try:
        params = _parse_element_params(step_data)
        if timeout is None:
            timeout = _resolve_timeout(params, None)
        build_result = _build_locator(page, step_data, params)
        if build_result is None:
            CommonUtil.ExecLog(sModuleInfo, "Could not build locator from step data", 3)
            return "zeuz_failed"

        locator = build_result.locator
        if state == "visible" and not params.get("allow_hidden"):
            locator = _effective_locator(locator, params)
        if params.get("index") is not None:
            locator = locator.nth(params["index"])
        else:
            locator = _first_locator(locator)

        await locator.wait_for(state=state, timeout=timeout)
        CommonUtil.ExecLog(sModuleInfo, f"Element reached state: {state}", 1)
        return "passed"
    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, f"Wait for element failed: {e}", 3)
        return "zeuz_failed"


def _effective_locator(locator, params):
    if params.get("allow_hidden"):
        return locator
    return locator.filter(visible=True)


async def _wait_for_locator(locator, state, timeout):
    try:
        await _first_locator(locator).wait_for(state=state, timeout=timeout)
        return True
    except Exception:
        return False


async def _safe_count(locator):
    try:
        return await locator.count()
    except Exception:
        return 0


async def _log_no_match(locator, params, sModuleInfo):
    total_count = await _safe_count(locator)
    if total_count > 0 and not params.get("allow_hidden"):
        CommonUtil.ExecLog(
            sModuleInfo,
            "Found %s hidden elements and no displayed elements. Nothing to return.\n" % total_count
            + 'To get hidden elements add a row ("allow hidden", "optional parameter", "yes")',
            3,
        )
    else:
        CommonUtil.ExecLog(sModuleInfo, "No elements found matching locator", 3)


async def _log_outer_html(locator, sModuleInfo):
    try:
        outer_html = await locator.evaluate("el => el.outerHTML")
        CommonUtil.ExecLog(sModuleInfo, _opening_tag(outer_html), 5)
    except Exception:
        pass


async def _log_frame_hint(page, sModuleInfo):
    try:
        if await page.locator("iframe").count() > 0:
            CommonUtil.ExecLog(sModuleInfo, 'You have Iframes in your Webpage. Try switching Iframe with "Switch Iframe" action', 3)
        elif await page.locator("frame").count() > 0:
            CommonUtil.ExecLog(sModuleInfo, 'You have Frames in your Webpage. Try switching Frame with "Switch Iframe" action', 3)
    except Exception:
        pass


def _resolve_timeout(params, element_wait):
    if element_wait is not None:
        return int(float(element_wait) * 1000)
    if params.get("wait") is not None:
        return int(float(params["wait"]) * 1000)
    default_wait = sr.Get_Shared_Variables("element_wait")
    if default_wait not in failed_tag_list:
        return int(float(default_wait) * 1000)
    return 10000


def _first_locator(locator):
    first = getattr(locator, "first")
    return first() if callable(first) else first


def _has_relationship_params(params):
    return any(
        params[key]
        for key in (
            "parent_params",
            "child_params",
            "sibling_params",
            "preceding_params",
            "following_params",
            "shadow_root_params",
        )
    )


def _index_from_rows(rows):
    for left, mid, right in rows:
        if str(left).strip().lower() == "index" and str(mid).strip().lower() == "element parameter":
            try:
                return int(str(right).strip())
            except Exception:
                return None
    return None


def _matches_text_filters(text, filters):
    normalized_text = text.replace("\xa0", " ")
    for left, value in filters:
        normalized_value = value.replace("\xa0", " ")
        if left.startswith("**") and normalized_value.lower() in normalized_text.lower():
            return True
        if left.startswith("*") and normalized_value in normalized_text:
            return True
        if normalized_value == normalized_text:
            return True
    return False


def _similar_text(text, filters):
    collapsed_text = re.sub(r"\s+", "", text.lower().replace("\xa0", ""))
    for _, value in filters:
        if value.lower().replace("\xa0", "").replace(" ", "") in collapsed_text:
            return True
    return False


def _opening_tag(outer_html):
    i, quote_count = 0, 0
    for i in range(len(outer_html)):
        if outer_html[i] == '"':
            quote_count += 1
        if outer_html[i] == ">" and quote_count % 2 == 0:
            break
    return outer_html[: i + 1]


def _as_playwright_xpath(query):
    query = str(query).strip()
    return query if query.startswith("xpath=") else f"xpath={query}"


def _xpath_literal(value):
    value = str(value)
    if '"' not in value:
        return f'"{value}"'
    if "'" not in value:
        return f"'{value}'"
    parts = value.split('"')
    return "concat(%s)" % ", '\"', ".join(f'"{part}"' for part in parts)


def _mid_key(mid):
    return str(mid).replace(" ", "").lower()


def _truthy(value):
    return str(value).strip().lower() in ("yes", "true", "ok", "1", "enable")


def _extract_sr_index(mid_value):
    """Extract index from 'sr N element parameter' format."""
    try:
        parts = mid_value.lower().split()
        for i, part in enumerate(parts):
            if part == "sr" and i + 1 < len(parts):
                return int(parts[i + 1])
    except (ValueError, IndexError):
        pass
    return 1


# Backwards-compatible alias for code that imported the old helper directly.
def handle_shadow_dom(page, shadow_params, element_params):
    params = {
        "shadow_root_params": shadow_params,
        "element_ds": [(left, "element parameter", right) for left, right in element_params],
    }
    result = _build_shadow_dom_locator(page, params)
    return result.locator if result not in failed_tag_list and result is not None else "zeuz_failed"
