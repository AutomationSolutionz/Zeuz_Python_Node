# Playwright Implementation Guide

> **Version:** 1.0
> **Last Updated:** 2026-02-04
> **Prerequisites:** Read ARCHITECTURE.md first
> **Status:** Implementation Guide

---

## Table of Contents

1. [Overview](#1-overview)
2. [Design Decisions](#2-design-decisions)
3. [File Structure](#3-file-structure)
4. [Element Location Strategy](#4-element-location-strategy)
5. [Parameter Mapping](#5-parameter-mapping)
6. [Action Implementations](#6-action-implementations)
7. [Browser Management](#7-browser-management)
8. [Playwright-Specific Features](#8-playwright-specific-features)
9. [Migration Guide](#9-migration-guide)
10. [Testing](#10-testing)

---

## 1. Overview

### Why Playwright?

| Aspect | Selenium | Playwright |
|--------|----------|------------|
| Speed | Slower (HTTP protocol) | Faster (WebSocket/CDP) |
| Auto-wait | Manual (WebDriverWait) | Built-in |
| Selectors | xpath, css | xpath, css + text=, role=, test-id |
| Shadow DOM | Manual traversal | Automatic piercing |
| Multiple browsers | Separate drivers | Single API |

### Goals

1. **Same step data format** - Just change `selenium action` → `playwright action`
2. **Full Playwright speed** - Use native Locator API, not polling
3. **All parameters supported** - use js, delay, offset, etc.
4. **Shared utilities** - Use existing framework utilities

### What Changes

| Component | Approach |
|-----------|----------|
| BuiltInFunctions.py | New file for Playwright |
| action_declarations | New playwright.py |
| LocateElement.py | Add Playwright support OR create PlaywrightLocator.py |
| sequential_actions.py | Add playwright module loading |
| Query building | Reuse existing xpath/css building |
| Execution | Use Playwright native Locator API |

---

## 2. Design Decisions

### Decision 1: Separate Module (Not Flag)

**Choice:** Create new `playwright action` type, not add flag to selenium actions.

**Rationale:**
- Clean separation of concerns
- Native Playwright features preserved
- Easier maintenance
- Follows existing pattern (selenium vs appium)

### Decision 2: Native Locator API

**Choice:** Use Playwright's Locator API with built-in auto-wait.

**Rationale:**
- Preserves Playwright speed advantage
- Built-in retry logic
- No manual polling loops needed

```python
# WRONG - Loses Playwright benefits
elements = page.locator(selector).all()  # Eager evaluation
while not elements:
    time.sleep(0.1)  # Manual polling
    elements = page.locator(selector).all()

# CORRECT - Native Playwright
locator = page.locator(selector)  # Lazy evaluation
locator.click()  # Auto-waits, auto-retries
```

### Decision 3: Query Building Shared

**Choice:** Reuse xpath/css query building from LocateElement.py

**Rationale:**
- Same step data format works
- No duplication of complex logic
- Only execution differs

### Decision 4: Sync API (Not Async)

**Choice:** Use `playwright.sync_api` to match framework's synchronous patterns.

**Rationale:**
- Framework is synchronous
- Simpler integration
- Matches existing function signatures

---

## 3. File Structure

### New Files to Create

```
Framework/Built_In_Automation/
├── Web/
│   └── Playwright/
│       ├── __init__.py
│       ├── BuiltInFunctions.py      # Main actions (NEW)
│       └── locator.py               # Playwright element location (NEW)
│
└── Sequential_Actions/
    └── action_declarations/
        └── playwright.py            # Action declarations (NEW)
```

### Files to Modify

```
Framework/Built_In_Automation/
├── Sequential_Actions/
│   ├── sequential_actions.py        # Add playwright loading
│   └── action_declarations/
│       └── info.py                  # Register playwright module
│
└── Shared_Resources/
    └── LocateElement.py             # Optional: Add playwright driver type
```

---

## 4. Element Location Strategy

### Option A: Native PlaywrightLocator (Recommended)

Create `Web/Playwright/locator.py` that:
1. Reuses query building from LocateElement.py
2. Uses Playwright's native Locator API
3. Preserves auto-wait functionality

```python
# Web/Playwright/locator.py

from Framework.Built_In_Automation.Shared_Resources import LocateElement
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr
from Framework.Utilities import CommonUtil

def Get_Element(step_data, page, return_all=False):
    """
    Get element using Playwright's native Locator API.

    Args:
        step_data: Standard step data format
        page: Playwright Page object
        return_all: If True, return all matching elements

    Returns:
        Locator | List[Locator] | "zeuz_failed"
    """
    sModuleInfo = "PlaywrightLocator.Get_Element"

    try:
        # Parse parameters using existing logic
        params = _parse_element_params(step_data)

        # Check for saved element
        if params.get('get_parameter'):
            return sr.parse_variable(params['get_parameter'])

        # Build locator
        locator = _build_locator(page, step_data, params)

        if locator is None:
            return "zeuz_failed"

        # Apply index if specified
        if params.get('index') is not None:
            locator = locator.nth(params['index'])

        # Apply visibility filter
        if not params.get('allow_hidden'):
            locator = locator.locator('visible=true')

        # Save if requested
        if params.get('save_parameter'):
            sr.Set_Shared_Variables(params['save_parameter'], locator)

        if return_all:
            return locator.all()

        return locator

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _parse_element_params(step_data):
    """Parse element parameters from step data."""
    params = {
        'index': None,
        'allow_hidden': False,
        'save_parameter': None,
        'get_parameter': None,
        'wait': None,
    }

    for left, mid, right in step_data:
        left = left.strip().lower()
        mid = mid.strip().lower()
        right = right.strip()

        if mid == "save parameter":
            params['save_parameter'] = left
        elif mid == "get parameter":
            if right.startswith("%|") and right.endswith("|%"):
                params['get_parameter'] = right.strip("%").strip("|")
        elif mid == "optional parameter":
            if left == "allow hidden":
                params['allow_hidden'] = right.lower() in ("yes", "true", "ok")
            elif left == "wait":
                params['wait'] = float(right)
        elif mid == "element parameter":
            if left == "index":
                params['index'] = int(right)

    return params


def _build_locator(page, step_data, params):
    """Build Playwright locator from step data."""

    # Check for direct selectors first
    for left, mid, right in step_data:
        left = left.strip().lower()
        mid = mid.strip().lower()

        if mid == "element parameter":
            # Direct Playwright selectors (fast path)
            if left == "xpath":
                return page.locator(f"xpath={right}")
            elif left == "css" or left == "css selector":
                return page.locator(right)
            elif left == "test-id" or left == "testid" or left == "data-testid":
                return page.get_by_test_id(right)
            elif left == "role":
                return page.get_by_role(right)
            elif left == "text":
                return page.get_by_text(right, exact=True)
            elif left == "*text":
                return page.get_by_text(right, exact=False)
            elif left == "placeholder":
                return page.get_by_placeholder(right)
            elif left == "label":
                return page.get_by_label(right)
            elif left == "alt":
                return page.get_by_alt_text(right)
            elif left == "title":
                return page.get_by_title(right)

    # Fall back to xpath built from LocateElement
    # Use existing query building logic
    xpath_query, query_type = LocateElement._construct_query(step_data)

    if xpath_query and query_type == "xpath":
        return page.locator(f"xpath={xpath_query}")
    elif xpath_query and query_type == "css":
        return page.locator(xpath_query)

    return None
```

### Option B: Extend LocateElement.py

Add Playwright as another driver type in existing LocateElement.py.

```python
# In LocateElement.py _driver_type()
def _driver_type(query_debug):
    driver_string = str(generic_driver)
    # ... existing checks ...
    elif "playwright" in driver_string.lower() or "Page" in driver_string:
        return "playwright"
```

```python
# In LocateElement.py _get_xpath_or_css_element()
elif driver_type == "playwright":
    # Use Playwright locator
    if css_xpath == "xpath":
        locator = generic_driver.locator(f"xpath={element_query}")
    else:
        locator = generic_driver.locator(element_query)

    # Playwright has built-in wait, but we can set timeout
    if element_wait:
        locator = locator.first  # Force evaluation with timeout

    all_matching_elements = locator.all()
```

**Note:** Option B loses some Playwright benefits (lazy evaluation). Option A recommended.

---

## 5. Parameter Mapping

### Complete Selenium → Playwright Mapping

#### Browser Options

| Selenium Parameter | Playwright Equivalent | Notes |
|--------------------|----------------------|-------|
| `add argument` | `args: [...]` | Browser launch args |
| `add extension` | **NOT SUPPORTED** | Playwright limitation |
| `add experimental option` | Varies | Map specific options |
| `page load strategy: eager` | `wait_until="domcontentloaded"` | |
| `page load strategy: none` | `wait_until="commit"` | |
| `resolution` | `viewport: {width, height}` | |
| `debugger address` | `connect_over_cdp()` | Connect to existing |
| `wait time to page load` | `timeout` option | |
| `headless` | `headless: true/false` | |

#### Element Interaction

| Selenium Parameter | Playwright Equivalent | Notes |
|--------------------|----------------------|-------|
| `use js` | `force: true` | Bypasses actionability |
| `use js` (for value) | `evaluate()` | JS execution |
| `delay` | `type(text, delay=ms)` | Typing delay |
| `clear` | `locator.clear()` or `fill("")` | Clear field |
| `offset` | `click(position={x, y})` | Click position |
| `allow hidden` | `force: true` | Include hidden |
| `wait` | `timeout=ms` | Action timeout |

#### Click Variations

| Selenium | Playwright |
|----------|------------|
| `click` | `locator.click()` |
| `double click` | `locator.dblclick()` |
| `right click` | `locator.click(button="right")` |
| `click (use js=true)` | `locator.click(force=True)` |
| `click (offset=x,y)` | `locator.click(position={"x": x, "y": y})` |

#### Text Input

| Selenium | Playwright |
|----------|------------|
| `text (clear=true)` | `locator.fill(text)` |
| `text (clear=false)` | `locator.type(text)` |
| `text (delay=0.1)` | `locator.type(text, delay=100)` |
| `text (use js=true)` | `locator.evaluate("el => el.value = 'text'")` |
| `keystroke keys` | `locator.press("Tab")` |
| `keystroke chars` | `locator.type("chars")` |

#### Validation

| Selenium | Playwright |
|----------|------------|
| `validate text` | `expect(locator).to_have_text()` |
| `if element exists` | `locator.count() > 0` |
| `get attribute` | `locator.get_attribute(name)` |
| `get text` | `locator.text_content()` |

#### Navigation

| Selenium | Playwright |
|----------|------------|
| `navigate back` | `page.go_back()` |
| `navigate forward` | `page.go_forward()` |
| `navigate refresh` | `page.reload()` |
| `go to link` | `page.goto(url)` |
| `get current url` | `page.url` |

#### Scroll

| Selenium | Playwright |
|----------|------------|
| `scroll (direction=up)` | `page.mouse.wheel(0, -delta)` |
| `scroll (direction=down)` | `page.mouse.wheel(0, delta)` |
| `scroll to element` | `locator.scroll_into_view_if_needed()` |
| `scroll to element (use js)` | `locator.evaluate("el => el.scrollIntoView()")` |

#### Windows/Tabs

| Selenium | Playwright |
|----------|------------|
| `switch window/tab (title)` | Find page by title in `context.pages` |
| `switch window/tab (index)` | `context.pages[index]` |
| `open new tab` | `context.new_page()` |
| `close tab` | `page.close()` |

#### IFrames

| Selenium | Playwright |
|----------|------------|
| `switch iframe` | `page.frame_locator(selector)` |
| `switch to default` | Use main `page` object |

#### Alerts

| Selenium | Playwright |
|----------|------------|
| `handle alert accept` | `page.on("dialog", lambda d: d.accept())` |
| `handle alert dismiss` | `page.on("dialog", lambda d: d.dismiss())` |
| `handle alert get text` | `dialog.message` |
| `handle alert send text` | `dialog.accept(text)` |

#### Select/Dropdown

| Selenium | Playwright |
|----------|------------|
| `select by visible text` | `locator.select_option(label=text)` |
| `select by value` | `locator.select_option(value=val)` |
| `select by index` | `locator.select_option(index=idx)` |

#### Checkbox/Radio

| Selenium | Playwright |
|----------|------------|
| `check` | `locator.check()` |
| `uncheck` | `locator.uncheck()` |
| `check (use js=true)` | `locator.check(force=True)` |

#### Drag and Drop

| Selenium | Playwright |
|----------|------------|
| `drag and drop` | `source.drag_to(target)` |
| `drag and drop (offset)` | `page.mouse.move()`, `drag()`, `drop()` |

#### Screenshot

| Selenium | Playwright |
|----------|------------|
| `take screenshot` | `page.screenshot(path=path)` |
| `take screenshot (fullscreen)` | `page.screenshot(full_page=True)` |
| `element screenshot` | `locator.screenshot(path=path)` |

#### JavaScript

| Selenium | Playwright |
|----------|------------|
| `execute javascript` | `page.evaluate(script)` |
| `execute javascript (on element)` | `locator.evaluate(script)` |

### Unsupported Features

| Feature | Reason | Workaround |
|---------|--------|------------|
| `add extension` (CRX) | Playwright limitation | Use Chrome with CDP |
| `add encoded extension` | Playwright limitation | Use Chrome with CDP |
| `capture network log` (Selenium way) | Different API | Use `page.on("response")` |

---

## 6. Action Implementations

### Template for All Actions

```python
# Web/Playwright/BuiltInFunctions.py

import sys
import inspect
import time
from playwright.sync_api import sync_playwright, Page, Locator

from Framework.Utilities import CommonUtil
from Framework.Utilities.decorators import logger
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list
from . import locator as PlaywrightLocator

MODULE_NAME = inspect.getmodulename(__file__)

# Global state
playwright_instance = None
browser = None
context = None
current_page = None
playwright_details = {}  # {"page_id": {"page": Page, "context": Context}}
```

### Core Actions Implementation

#### Open Browser

```python
@logger
def Open_Browser(step_data):
    """
    Open browser with Playwright.

    Example:
        Field               Sub Field           Value
        go to link          input parameter     https://example.com
        browser             input parameter     chrome
        headless            optional parameter  false
        resolution          optional parameter  1920,1080
        open browser        playwright action   open browser
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global playwright_instance, browser, context, current_page

    try:
        # Parse parameters
        url = None
        browser_name = "chromium"
        headless = True
        viewport = {"width": 1920, "height": 1080}
        args = []
        timeout = 30000

        for left, mid, right in step_data:
            left = left.strip().lower()
            mid = mid.strip().lower()
            right = right.strip()

            if mid == "input parameter":
                if left in ("go to link", "url"):
                    url = right
                elif left == "browser":
                    browser_name = right.lower()
            elif mid == "optional parameter":
                if left == "headless":
                    headless = right.lower() in ("true", "yes", "1")
                elif left == "resolution":
                    w, h = right.split(",")
                    viewport = {"width": int(w), "height": int(h)}
                elif left in ("add argument", "arg"):
                    args.append(right)
                elif left == "timeout":
                    timeout = int(float(right) * 1000)

        # Launch Playwright
        playwright_instance = sync_playwright().start()

        # Select browser
        if browser_name in ("chrome", "chromium"):
            browser = playwright_instance.chromium.launch(
                headless=headless,
                args=args,
            )
        elif browser_name == "firefox":
            browser = playwright_instance.firefox.launch(headless=headless)
        elif browser_name in ("webkit", "safari"):
            browser = playwright_instance.webkit.launch(headless=headless)
        else:
            CommonUtil.ExecLog(sModuleInfo, f"Unknown browser: {browser_name}", 3)
            return "zeuz_failed"

        # Create context and page
        context = browser.new_context(viewport=viewport)
        context.set_default_timeout(timeout)
        current_page = context.new_page()

        # Navigate if URL provided
        if url:
            current_page.goto(url, wait_until="domcontentloaded")
            CommonUtil.ExecLog(sModuleInfo, f"Navigated to: {url}", 1)

        # Save to shared variables
        sr.Set_Shared_Variables("playwright_page", current_page)
        sr.Set_Shared_Variables("playwright_context", context)
        sr.Set_Shared_Variables("playwright_browser", browser)

        CommonUtil.ExecLog(sModuleInfo, "Browser opened successfully", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
```

#### Click Element

```python
@logger
def Click_Element(step_data):
    """
    Click an element.

    Example:
        Field               Sub Field           Value
        id                  element parameter   submit-btn
        use js              optional parameter  false
        offset              optional parameter  10,5
        click               playwright action   click
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        # Parse parameters
        use_js = False
        offset = None
        double_click = False
        right_click = False

        for left, mid, right in step_data:
            left = left.strip().lower()
            mid = mid.strip().lower()
            right_val = right.strip()

            if mid == "optional parameter":
                if left == "use js":
                    use_js = right_val.lower() in ("true", "yes", "1")
                elif left == "offset":
                    x, y = right_val.split(",")
                    offset = {"x": float(x), "y": float(y)}
            elif mid == "action":
                if "double" in left:
                    double_click = True
                elif "right" in left:
                    right_click = True

        # Get element
        locator = PlaywrightLocator.Get_Element(step_data, current_page)
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # Build click options
        click_options = {}
        if use_js:
            click_options["force"] = True
        if offset:
            click_options["position"] = offset

        # Perform click
        if double_click:
            locator.dblclick(**click_options)
        elif right_click:
            click_options["button"] = "right"
            locator.click(**click_options)
        else:
            locator.click(**click_options)

        CommonUtil.ExecLog(sModuleInfo, "Click performed successfully", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
```

#### Enter Text

```python
@logger
def Enter_Text(step_data):
    """
    Enter text in a field.

    Example:
        Field               Sub Field           Value
        id                  element parameter   username
        text                action              my_username
        delay               optional parameter  0.1
        clear               optional parameter  true
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        # Parse parameters
        text_value = ""
        delay = 0
        use_js = False
        clear = True

        for left, mid, right in step_data:
            left = left.strip().lower()
            mid = mid.strip().lower()
            right_val = right.strip()

            if mid == "action":
                text_value = right  # Don't strip - preserve whitespace
            elif mid == "optional parameter":
                if left == "delay":
                    delay = float(right_val)
                elif left == "use js":
                    use_js = right_val.lower() in ("true", "yes", "1")
                elif left == "clear":
                    clear = right_val.lower() not in ("false", "no", "0")

        # Get element
        locator = PlaywrightLocator.Get_Element(step_data, current_page)
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # Enter text
        if use_js:
            # Use JavaScript to set value
            locator.evaluate(f"el => el.value = `{text_value}`")
            locator.dispatch_event("input")
            locator.dispatch_event("change")
        elif clear:
            # fill() clears and types
            locator.fill(text_value)
        else:
            # type() appends
            if delay > 0:
                locator.type(text_value, delay=int(delay * 1000))
            else:
                locator.type(text_value)

        CommonUtil.ExecLog(sModuleInfo, f"Entered text: {text_value[:50]}...", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
```

#### Validate Text

```python
@logger
def Validate_Text(step_data):
    """
    Validate element contains expected text.

    Example:
        Field               Sub Field           Value
        id                  element parameter   message
        validate text       action              Success!
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global current_page

    try:
        expected_text = ""
        partial_match = False

        for left, mid, right in step_data:
            left = left.strip().lower()
            mid = mid.strip().lower()

            if mid == "action":
                if left.startswith("*"):
                    partial_match = True
                expected_text = right

        # Get element
        locator = PlaywrightLocator.Get_Element(step_data, current_page)
        if locator == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # Get actual text
        actual_text = locator.text_content()

        # Compare
        if partial_match:
            if expected_text.lower() in actual_text.lower():
                CommonUtil.ExecLog(sModuleInfo, f"Text validated (partial): {expected_text}", 1)
                return "passed"
        else:
            if expected_text == actual_text:
                CommonUtil.ExecLog(sModuleInfo, f"Text validated: {expected_text}", 1)
                return "passed"

        CommonUtil.ExecLog(
            sModuleInfo,
            f"Text validation failed. Expected: '{expected_text}', Got: '{actual_text}'",
            3
        )
        return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
```

#### Tear Down

```python
@logger
def Tear_Down(step_data):
    """
    Close browser and clean up.

    Example:
        Field               Sub Field           Value
        tear down           playwright action   tear down
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global playwright_instance, browser, context, current_page

    try:
        if current_page:
            current_page.close()
        if context:
            context.close()
        if browser:
            browser.close()
        if playwright_instance:
            playwright_instance.stop()

        current_page = None
        context = None
        browser = None
        playwright_instance = None

        CommonUtil.ExecLog(sModuleInfo, "Browser closed successfully", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
```

---

## 7. Browser Management

### Multi-Page Support

```python
# Global tracking
playwright_pages = {}  # {"page_id": page}
current_page_id = None

def switch_page(page_id):
    """Switch to a different page/tab."""
    global current_page, current_page_id
    if page_id in playwright_pages:
        current_page = playwright_pages[page_id]
        current_page_id = page_id
        current_page.bring_to_front()
```

### Connect to Existing Browser

```python
def connect_to_browser(cdp_url):
    """Connect to existing browser via CDP."""
    global playwright_instance, browser, context, current_page

    playwright_instance = sync_playwright().start()
    browser = playwright_instance.chromium.connect_over_cdp(cdp_url)
    context = browser.contexts[0]
    current_page = context.pages[0]
```

---

## 8. Playwright-Specific Features

### Features Available Only in Playwright

These can be exposed as new action types:

#### Tracing

```python
@logger
def Start_Tracing(step_data):
    """Start Playwright trace recording."""
    context.tracing.start(screenshots=True, snapshots=True)
    return "passed"

@logger
def Stop_Tracing(step_data):
    """Stop tracing and save."""
    path = "trace.zip"
    for left, mid, right in step_data:
        if mid == "input parameter" and left == "path":
            path = right
    context.tracing.stop(path=path)
    return "passed"
```

#### Video Recording

```python
# In Open_Browser, add:
context = browser.new_context(
    record_video_dir="videos/",
    viewport=viewport
)
```

#### Network Interception

```python
@logger
def Intercept_Network(step_data):
    """Intercept and modify network requests."""

    def handle_route(route):
        # Modify request or response
        route.continue_()

    current_page.route("**/*", handle_route)
    return "passed"
```

#### API Testing

```python
@logger
def API_Request(step_data):
    """Make API request using Playwright's request context."""
    api_context = context.request
    response = api_context.get(url)
    return "passed"
```

---

## 9. Migration Guide

### For Users: Migrating from Selenium to Playwright

#### Step 1: Change Action Type Only

```
# Before (Selenium)
Field               Sub Field           Value
id                  element parameter   submit-btn
click               selenium action     click

# After (Playwright)
Field               Sub Field           Value
id                  element parameter   submit-btn
click               playwright action   click
```

#### Step 2: No Other Changes Needed

All parameters work the same:
- `element parameter` ✅
- `parent parameter` ✅
- `optional parameter` ✅
- `use js` ✅
- `delay` ✅
- `offset` ✅

#### Step 3: Optional - Use Playwright-Specific Selectors

```
# Playwright-native selectors (faster)
Field               Sub Field           Value
test-id             element parameter   submit-btn
click               playwright action   click

# Or
Field               Sub Field           Value
role                element parameter   button
text                element parameter   Submit
click               playwright action   click
```

### Exceptions

| Selenium Feature | Migration Notes |
|------------------|-----------------|
| `add extension` | Not supported - use Chrome CDP if needed |
| Network logging (old way) | Use new `intercept network` action |

---

## 10. Testing

### Unit Tests Location

```
tests/
├── test_playwright_locator.py
├── test_playwright_actions.py
└── test_playwright_browser.py
```

### Test Pattern

```python
# tests/test_playwright_actions.py

import pytest
from unittest.mock import MagicMock, patch

def test_click_element():
    """Test Click_Element action."""
    from Framework.Built_In_Automation.Web.Playwright import BuiltInFunctions

    # Mock page and locator
    mock_page = MagicMock()
    mock_locator = MagicMock()
    mock_page.locator.return_value = mock_locator

    # Set global page
    BuiltInFunctions.current_page = mock_page

    step_data = [
        ("id", "element parameter", "submit-btn"),
        ("click", "playwright action", "click"),
    ]

    with patch.object(BuiltInFunctions.PlaywrightLocator, 'Get_Element', return_value=mock_locator):
        result = BuiltInFunctions.Click_Element(step_data)

    assert result == "passed"
    mock_locator.click.assert_called_once()
```

---

## Appendix: Action Declarations

### playwright.py

```python
# action_declarations/playwright.py

declarations = (
    # Browser Management
    {"name": "open browser", "function": "Open_Browser", "screenshot": "none"},
    {"name": "go to link", "function": "Go_To_Link", "screenshot": "none"},
    {"name": "tear down", "function": "Tear_Down", "screenshot": "none"},
    {"name": "close browser", "function": "Tear_Down", "screenshot": "none"},

    # Navigation
    {"name": "navigate", "function": "Navigate", "screenshot": "web"},
    {"name": "get current url", "function": "Get_Current_URL", "screenshot": "none"},

    # Click Actions
    {"name": "click", "function": "Click_Element", "screenshot": "web"},
    {"name": "double click", "function": "Click_Element", "screenshot": "web"},
    {"name": "right click", "function": "Click_Element", "screenshot": "web"},
    {"name": "hover", "function": "Hover_Element", "screenshot": "web"},

    # Text Actions
    {"name": "text", "function": "Enter_Text", "screenshot": "web"},
    {"name": "enter text", "function": "Enter_Text", "screenshot": "web"},
    {"name": "keystroke", "function": "Keystroke", "screenshot": "web"},

    # Validation
    {"name": "validate text", "function": "Validate_Text", "screenshot": "web"},
    {"name": "if element exists", "function": "If_Element_Exists", "screenshot": "web"},
    {"name": "save attribute", "function": "Save_Attribute", "screenshot": "web"},

    # Select/Checkbox
    {"name": "select", "function": "Select_Option", "screenshot": "web"},
    {"name": "deselect", "function": "Deselect_Option", "screenshot": "web"},
    {"name": "check", "function": "Check_Element", "screenshot": "web"},
    {"name": "uncheck", "function": "Uncheck_Element", "screenshot": "web"},

    # Scroll
    {"name": "scroll", "function": "Scroll", "screenshot": "web"},
    {"name": "scroll to element", "function": "Scroll_To_Element", "screenshot": "web"},

    # Windows/Tabs
    {"name": "switch window", "function": "Switch_Window", "screenshot": "web"},
    {"name": "switch tab", "function": "Switch_Window", "screenshot": "web"},
    {"name": "open new tab", "function": "Open_New_Tab", "screenshot": "web"},
    {"name": "close tab", "function": "Close_Tab", "screenshot": "web"},

    # Frames
    {"name": "switch iframe", "function": "Switch_IFrame", "screenshot": "web"},

    # Alerts
    {"name": "handle alert", "function": "Handle_Alert", "screenshot": "web"},

    # Drag & Drop
    {"name": "drag and drop", "function": "Drag_And_Drop", "screenshot": "web"},

    # Screenshot
    {"name": "take screenshot", "function": "Take_Screenshot", "screenshot": "none"},

    # JavaScript
    {"name": "execute javascript", "function": "Execute_JavaScript", "screenshot": "web"},

    # Upload
    {"name": "upload file", "function": "Upload_File", "screenshot": "web"},

    # Playwright-Specific
    {"name": "start tracing", "function": "Start_Tracing", "screenshot": "none"},
    {"name": "stop tracing", "function": "Stop_Tracing", "screenshot": "none"},
    {"name": "intercept network", "function": "Intercept_Network", "screenshot": "none"},
)
```

---

## Implementation Checklist

### Phase 1: Core Setup
- [ ] Create `Web/Playwright/` directory
- [ ] Create `__init__.py`
- [ ] Create `locator.py` with `Get_Element()`
- [ ] Create `BuiltInFunctions.py` with imports
- [ ] Create `action_declarations/playwright.py`
- [ ] Update `sequential_actions.py` to load playwright
- [ ] Update `action_declarations/info.py`

### Phase 2: Basic Actions
- [ ] `Open_Browser`
- [ ] `Go_To_Link`
- [ ] `Tear_Down`
- [ ] `Click_Element`
- [ ] `Enter_Text`
- [ ] `Validate_Text`
- [ ] `If_Element_Exists`

### Phase 3: Navigation & Validation
- [ ] `Navigate`
- [ ] `Get_Current_URL`
- [ ] `Save_Attribute`
- [ ] `Hover_Element`
- [ ] `Double_Click`
- [ ] `Right_Click`

### Phase 4: Forms
- [ ] `Select_Option`
- [ ] `Deselect_Option`
- [ ] `Check_Element`
- [ ] `Uncheck_Element`
- [ ] `Upload_File`

### Phase 5: Advanced
- [ ] `Switch_Window`
- [ ] `Open_New_Tab`
- [ ] `Close_Tab`
- [ ] `Switch_IFrame`
- [ ] `Handle_Alert`
- [ ] `Scroll`
- [ ] `Scroll_To_Element`
- [ ] `Drag_And_Drop`
- [ ] `Execute_JavaScript`
- [ ] `Take_Screenshot`
- [ ] `Keystroke`

### Phase 6: Playwright-Specific
- [ ] `Start_Tracing`
- [ ] `Stop_Tracing`
- [ ] `Intercept_Network`

### Phase 7: Testing
- [ ] Unit tests for locator
- [ ] Unit tests for each action
- [ ] Integration tests
