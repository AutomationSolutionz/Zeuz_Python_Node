# -*- coding: utf-8 -*-
"""
Playwright Element Locator Module

This module provides element location functionality using Playwright's native
Locator API while reusing the query building logic from LocateElement.py.

Key Features:
- Native Playwright Locator API (lazy evaluation, auto-wait)
- Supports all existing element parameter formats
- Supports Playwright-native selectors (test-id, role, text, etc.)
- Preserves Playwright's speed advantage
"""

import sys
import inspect
import re

from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list

MODULE_NAME = inspect.getmodulename(__file__)


async def Get_Element(step_data, page, return_all=False, element_wait=None, frame_locator=None):
    """
    Get element using Playwright's native Locator API.

    This function parses the same step_data format as LocateElement.Get_Element()
    but uses Playwright's Locator API for execution, preserving auto-wait and
    lazy evaluation benefits.

    Args:
        step_data: List of (left, mid, right) tuples - standard Zeuz format
        page: Playwright Page object
        return_all: If True, return list of all matching ElementHandles
        element_wait: Override default wait timeout (in seconds)
        frame_locator: Optional frame locator for iframe context

    Returns:
        Locator | List[ElementHandle] | "zeuz_failed"

    Example:
        step_data = [
            ("id", "element parameter", "submit-btn"),
            ("click", "playwright action", "click"),
        ]
        locator = Get_Element(step_data, page)
        locator.click()  # Auto-waits for element
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        # Parse all parameters from step_data
        params = _parse_element_params(step_data)

        # Check for get parameter (retrieve saved element)
        if params.get('get_parameter'):
            result = sr.parse_variable(params['get_parameter'])
            if result not in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Returning saved element '{params['get_parameter']}' from shared variables",
                    1,
                )
                return result
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Element '{params['get_parameter']}' not found in shared variables",
                    3,
                )
                return "zeuz_failed"

        # Build the locator
        locator = _build_locator(page, step_data, params, frame_locator)

        if locator is None:
            CommonUtil.ExecLog(sModuleInfo, "Could not build locator from step data", 3)
            return "zeuz_failed"

        # Set timeout if specified
        if element_wait is not None:
            timeout = int(float(element_wait) * 1000)
        elif params.get('wait') is not None:
            timeout = int(float(params['wait']) * 1000)
        else:
            # Get default from shared variables
            default_wait = sr.Get_Shared_Variables("element_wait")
            if default_wait not in failed_tag_list:
                timeout = int(float(default_wait) * 1000)
            else:
                timeout = 10000  # Default 10 seconds

        # Apply visibility filter if not allowing hidden
        if not params.get('allow_hidden'):
            # Filter to visible elements only
            locator = locator.locator("visible=true")

        # Apply index if specified
        if params.get('index') is not None:
            index = params['index']
            locator = locator.nth(index)

        # Log the locator being used
        CommonUtil.ExecLog(sModuleInfo, f"Playwright locator: {locator}", 5)

        # Save if requested
        if params.get('save_parameter'):
            sr.Set_Shared_Variables(params['save_parameter'], locator)
            CommonUtil.ExecLog(
                sModuleInfo,
                f"Saved element to variable '{params['save_parameter']}'",
                1,
            )

        # Return all elements if requested
        if return_all:
            try:
                elements = await locator.all()
                CommonUtil.ExecLog(sModuleInfo, f"Found {len(elements)} elements", 1)
                return elements
            except Exception as e:
                CommonUtil.ExecLog(sModuleInfo, f"Error getting all elements: {e}", 3)
                return "zeuz_failed"

        # Check if element exists (with timeout)
        try:
            count = await locator.count()
            if count == 0:
                CommonUtil.ExecLog(sModuleInfo, "No elements found matching locator", 3)
                return "zeuz_failed"
            elif count > 1 and params.get('index') is None:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Found {count} elements. Returning first. Consider using index parameter.",
                    2,
                )
        except Exception:
            pass  # Count might fail, but locator might still work with auto-wait

        return locator

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _parse_element_params(step_data):
    """
    Parse element parameters from step data.

    Returns dict with:
        - index: Element index (int or None)
        - allow_hidden: Whether to include hidden elements (bool)
        - save_parameter: Variable name to save element (str or None)
        - get_parameter: Variable name to retrieve element (str or None)
        - wait: Custom wait timeout in seconds (float or None)
        - element_params: List of element parameter tuples
        - parent_params: List of parent parameter tuples
        - And other parameter lists...
    """
    params = {
        'index': None,
        'allow_hidden': False,
        'save_parameter': None,
        'get_parameter': None,
        'wait': None,
        'element_params': [],
        'parent_params': [],
        'child_params': [],
        'sibling_params': [],
        'unique_params': [],
        'shadow_root_params': [],
    }

    for left, mid, right in step_data:
        left_lower = left.strip().lower()
        mid_lower = mid.strip().lower()
        right_stripped = right.strip()

        # Save parameter
        if mid_lower == "save parameter":
            if right_stripped != "ignore":
                params['save_parameter'] = left.strip()

        # Get parameter
        elif mid_lower == "get parameter":
            if right_stripped.startswith("%|") and right_stripped.endswith("|%"):
                params['get_parameter'] = right_stripped.strip("%").strip("|")

        # Optional parameters
        elif mid_lower == "optional parameter":
            if left_lower in ("allow hidden", "allow disable"):
                params['allow_hidden'] = right_stripped.lower() in ("yes", "true", "ok", "1")
            elif left_lower == "wait":
                params['wait'] = float(right_stripped)

        # Element parameters
        elif mid_lower == "element parameter":
            if left_lower == "index":
                try:
                    params['index'] = int(right_stripped)
                except ValueError:
                    pass
            else:
                params['element_params'].append((left.strip(), right_stripped))

        # Unique parameter
        elif mid_lower == "unique parameter":
            params['unique_params'].append((left.strip(), right_stripped))

        # Parent parameters (including numbered: parent 2 parameter)
        elif "parent" in mid_lower and "parameter" in mid_lower:
            params['parent_params'].append((left.strip(), mid.strip(), right_stripped))

        # Child parameters
        elif "child" in mid_lower and "parameter" in mid_lower:
            params['child_params'].append((left.strip(), mid.strip(), right_stripped))

        # Sibling parameters
        elif "sibling" in mid_lower and "parameter" in mid_lower:
            params['sibling_params'].append((left.strip(), mid.strip(), right_stripped))

        # Shadow root parameters
        elif mid_lower.startswith("sr"):
            params['shadow_root_params'].append((left.strip(), mid.strip(), right_stripped))

    return params


def _build_locator(page, step_data, params, frame_locator=None):
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
    """

    # Use frame locator if provided, otherwise use page
    base_locator = frame_locator if frame_locator else page

    # Strategy 1: Check for Playwright-native selectors (fastest path)
    for left, right in params['element_params']:
        left_lower = left.lower()

        # Test ID selectors
        if left_lower in ("test-id", "testid", "data-testid", "data-test-id"):
            return base_locator.get_by_test_id(right)

        # Role selector
        if left_lower == "role":
            # Check if there's a name parameter too
            name = None
            for l, r in params['element_params']:
                if l.lower() in ("name", "role name", "aria-label"):
                    name = r
                    break
            if name:
                return base_locator.get_by_role(right, name=name)
            return base_locator.get_by_role(right)

        # Text selectors
        if left_lower == "text":
            return base_locator.get_by_text(right, exact=True)
        if left_lower == "*text":
            return base_locator.get_by_text(right, exact=False)
        if left_lower == "**text":
            # Case-insensitive partial match
            return base_locator.get_by_text(re.compile(re.escape(right), re.IGNORECASE))

        # Label selector
        if left_lower == "label":
            return base_locator.get_by_label(right)

        # Placeholder selector
        if left_lower == "placeholder":
            return base_locator.get_by_placeholder(right)

        # Alt text selector
        if left_lower in ("alt", "alt text", "alt-text"):
            return base_locator.get_by_alt_text(right)

        # Title selector
        if left_lower == "title" and "parameter" not in params.get('mid', ''):
            return base_locator.get_by_title(right)

        # Direct xpath
        if left_lower == "xpath":
            return base_locator.locator(f"xpath={right}")

        # Direct CSS selector
        if left_lower in ("css", "css selector", "css_selector"):
            return base_locator.locator(right)

    # Strategy 2: Check for unique parameters
    for left, right in params['unique_params']:
        left_lower = left.lower()

        if left_lower == "id":
            return base_locator.locator(f"#{right}")
        elif left_lower == "name":
            return base_locator.locator(f"[name='{right}']")
        elif left_lower == "class":
            return base_locator.locator(f".{right}")
        elif left_lower == "tag":
            return base_locator.locator(right)

    # Strategy 3: Build xpath from element/parent/child parameters
    xpath = _build_xpath_from_params(step_data, params)
    if xpath:
        CommonUtil.ExecLog(
            "_build_locator",
            f"Built xpath from parameters: {xpath}",
            5
        )
        return base_locator.locator(f"xpath={xpath}")

    # Strategy 4: Simple element parameters as xpath
    if params['element_params']:
        xpath_parts = []
        tag = "*"

        for left, right in params['element_params']:
            left_lower = left.lower()

            if left_lower == "tag":
                tag = right
            elif left_lower == "id":
                xpath_parts.append(f"@id='{right}'")
            elif left_lower == "name":
                xpath_parts.append(f"@name='{right}'")
            elif left_lower == "class":
                xpath_parts.append(f"contains(@class,'{right}')")
            elif left_lower.startswith("*"):
                # Partial match
                attr = left_lower[1:]
                xpath_parts.append(f"contains(@{attr},'{right}')")
            elif left_lower.startswith("**"):
                # Case-insensitive partial match
                attr = left_lower[2:]
                xpath_parts.append(
                    f"contains(translate(@{attr},'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{right.lower()}')"
                )
            elif left_lower not in ("index", "text", "*text", "**text"):
                # Generic attribute
                xpath_parts.append(f"@{left}='{right}'")

        if xpath_parts:
            xpath = f"//{tag}[{' and '.join(xpath_parts)}]"
            return base_locator.locator(f"xpath={xpath}")
        elif tag != "*":
            return base_locator.locator(tag)

    return None


def _build_xpath_from_params(step_data, params):
    """
    Build complex xpath from element/parent/child/sibling parameters.

    This reuses the logic from LocateElement._construct_query() but simplified
    for the most common cases.
    """
    try:
        # Import the existing query builder for complex cases
        from Framework.Built_In_Automation.Shared_Resources import LocateElement

        # Filter step_data to only include element-related rows
        element_rows = []
        for left, mid, right in step_data:
            mid_lower = mid.strip().lower().replace(" ", "")
            if any(x in mid_lower for x in [
                "elementparameter", "parentparameter", "childparameter",
                "siblingparameter", "uniqueparameter", "precedingparameter",
                "followingparameter"
            ]):
                element_rows.append((left, mid, right))

        if not element_rows:
            return None

        # Use existing query builder
        # Temporarily set driver_type to selenium for xpath generation
        original_driver_type = getattr(LocateElement, 'driver_type', None)
        LocateElement.driver_type = "selenium"

        try:
            xpath, query_type = LocateElement._construct_query(element_rows)
            if xpath and query_type in ("xpath", "css"):
                return xpath
        finally:
            if original_driver_type is not None:
                LocateElement.driver_type = original_driver_type

    except Exception as e:
        CommonUtil.ExecLog(
            "_build_xpath_from_params",
            f"Error building xpath: {e}",
            2
        )

    return None


def handle_shadow_dom(page, shadow_params, element_params):
    """
    Handle Shadow DOM element location.

    Playwright supports automatic shadow DOM piercing with the >> selector.

    Args:
        page: Playwright Page object
        shadow_params: List of shadow root parameters
        element_params: Final element parameters

    Returns:
        Locator for element inside shadow DOM
    """
    sModuleInfo = "handle_shadow_dom"

    try:
        # Build a chain of selectors using Playwright's shadow-piercing >>
        # Sort shadow params by their index (sr 1, sr 2, etc.)
        sorted_params = sorted(shadow_params, key=lambda x: _extract_sr_index(x[1]))

        selector_parts = []

        for left, mid, right in sorted_params:
            left_lower = left.lower()
            if left_lower == "tag":
                selector_parts.append(right)
            elif left_lower == "id":
                selector_parts.append(f"#{right}")
            elif left_lower == "class":
                selector_parts.append(f".{right}")
            else:
                selector_parts.append(f"[{left}='{right}']")

        # Add final element
        for left, right in element_params:
            left_lower = left.lower()
            if left_lower == "tag":
                selector_parts.append(right)
            elif left_lower == "id":
                selector_parts.append(f"#{right}")
            elif left_lower == "class":
                selector_parts.append(f".{right}")
            else:
                selector_parts.append(f"[{left}='{right}']")

        # Join with >> for shadow DOM piercing
        full_selector = " >> ".join(selector_parts)
        CommonUtil.ExecLog(sModuleInfo, f"Shadow DOM selector: {full_selector}", 5)

        return page.locator(full_selector)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


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


async def wait_for_element(step_data, page, state="visible", timeout=None):
    """
    Wait for element to reach a specific state.

    Args:
        step_data: Standard step data format
        page: Playwright Page object
        state: One of "attached", "detached", "visible", "hidden"
        timeout: Timeout in milliseconds

    Returns:
        "passed" | "zeuz_failed"
    """
    sModuleInfo = "wait_for_element"

    try:
        locator = await Get_Element(step_data, page)
        if locator == "zeuz_failed":
            return "zeuz_failed"

        if timeout is None:
            default_wait = sr.Get_Shared_Variables("element_wait")
            if default_wait not in failed_tag_list:
                timeout = int(float(default_wait) * 1000)
            else:
                timeout = 10000

        locator.wait_for(state=state, timeout=timeout)
        CommonUtil.ExecLog(sModuleInfo, f"Element reached state: {state}", 1)
        return "passed"

    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, f"Wait for element failed: {e}", 3)
        return "zeuz_failed"
