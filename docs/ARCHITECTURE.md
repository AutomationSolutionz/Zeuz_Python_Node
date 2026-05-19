# Zeuz Node Framework - Architecture & Design Document

> **Version:** 1.0
> **Last Updated:** 2026-02-04
> **Purpose:** Comprehensive technical documentation for developers working on the Zeuz Node framework

---

## Table of Contents

1. [Overview](#1-overview)
2. [Directory Structure](#2-directory-structure)
3. [Core Execution Flow](#3-core-execution-flow)
4. [Action System Architecture](#4-action-system-architecture)
5. [Element Location System](#5-element-location-system)
6. [Parameter System](#6-parameter-system)
7. [Shared Variables System](#7-shared-variables-system)
8. [Shared Utilities & Patterns](#8-shared-utilities--patterns)
9. [Module Details](#9-module-details)
10. [Decorators & Logging](#10-decorators--logging)
11. [Return Status System](#11-return-status-system)
12. [Adding New Modules](#12-adding-new-modules)

---

## 1. Overview

### What is Zeuz Node?

Zeuz Node is a **cross-platform test automation execution client** that:
- Connects to Zeuz Server to receive test cases
- Executes automated tests across Web, Mobile, Desktop, API, and Database
- Reports results back to the server

### Supported Platforms

| Platform | Technology | Module Location |
|----------|------------|-----------------|
| Web | Selenium, REST, SOAP | `Web/Selenium/`, `Web/REST/`, `Web/SOAP/` |
| Mobile | Appium (Android/iOS) | `Mobile/CrossPlatform/Appium/` |
| Desktop | PyAutoGUI, Platform-specific | `Desktop/Windows/`, `Desktop/Mac/`, `Desktop/Linux/` |
| Database | ODBC, Native drivers | `Database/` |
| Performance | Locust | `Performance_Testing/` |
| Security | Security scanning | `Security/` |

### Key Technologies

- **Python 3.11+** - Core language
- **Selenium 4.21+** - Web automation
- **Appium 4.2+** - Mobile automation
- **Playwright 1.52+** - Modern web automation (being added)
- **FastAPI** - Local server component
- **PyAutoGUI** - Desktop automation

---

## 2. Directory Structure

```
Zeuz_Python_Node/
├── node_cli.py                    # Main entry point (1,426 lines)
├── settings.py                    # Global configuration
├── pyproject.toml                 # Dependencies (100+)
│
├── Framework/                     # Core automation framework
│   ├── MainDriverApi.py           # Test execution driver (2,197 lines)
│   │
│   ├── Built_In_Automation/       # All automation modules
│   │   ├── Web/
│   │   │   ├── Selenium/
│   │   │   │   ├── BuiltInFunctions.py    # 5,280 lines, 55+ actions
│   │   │   │   └── utils.py               # Chrome utilities
│   │   │   ├── REST/
│   │   │   │   └── BuiltInFunctions.py    # REST API actions
│   │   │   └── SOAP/
│   │   │       └── BuiltInFunctions.py    # SOAP actions
│   │   │
│   │   ├── Mobile/
│   │   │   └── CrossPlatform/
│   │   │       └── Appium/
│   │   │           └── BuiltInFunctions.py  # 20,000+ lines
│   │   │
│   │   ├── Desktop/
│   │   │   ├── Windows/BuiltInFunctions.py
│   │   │   ├── Mac/BuiltInFunctions.py
│   │   │   ├── Linux/BuiltInFunctions.py
│   │   │   └── CrossPlatform/BuiltInFunctions.py
│   │   │
│   │   ├── Database/
│   │   │   └── BuiltInFunctions.py
│   │   │
│   │   ├── Sequential_Actions/           # Action dispatch system
│   │   │   ├── sequential_actions.py     # Main dispatcher
│   │   │   ├── common_functions.py       # 7,500+ lines shared logic
│   │   │   └── action_declarations/      # Action registry
│   │   │       ├── info.py               # Master registry
│   │   │       ├── common.py             # ~100 common actions
│   │   │       ├── selenium.py           # Web actions
│   │   │       ├── appium.py             # Mobile actions
│   │   │       ├── database.py           # DB actions
│   │   │       ├── rest.py               # REST actions
│   │   │       ├── desktop.py            # Desktop actions
│   │   │       └── ...
│   │   │
│   │   └── Shared_Resources/             # Shared utilities
│   │       ├── LocateElement.py          # Element location (1,750 lines)
│   │       ├── BuiltInFunctionSharedResources.py  # Variables (1,477 lines)
│   │       └── data_collector.py
│   │
│   ├── Utilities/                        # Framework utilities
│   │   ├── CommonUtil.py                 # Logging, exceptions
│   │   ├── decorators.py                 # @logger, @deprecated
│   │   ├── ConfigModule.py               # Configuration
│   │   └── FileUtilities.py              # File operations
│   │
│   └── deploy_handler/                   # Server communication
│       ├── long_poll_handler.py          # Receives test cases
│       └── adapter.py                    # Protocol conversion
│
├── Apps/                                 # Supporting applications
│   ├── Web/AI_Recorder_2/                # Browser recorder (React)
│   └── Mobile/                           # Mobile inspectors
│
├── Server/                               # Local FastAPI server
│   └── main.py
│
└── tests/                                # Unit tests
    └── test_*.py
```

---

## 3. Core Execution Flow

### High-Level Flow

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Zeuz Server │────►│ long_poll_handler│────►│     adapter     │
│ (Test Case) │     │ (Receives data)  │     │ (Converts format)│
└─────────────┘     └──────────────────┘     └────────┬────────┘
                                                      │
                                                      ▼
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Results   │◄────│  MainDriverApi   │◄────│ Sequential      │
│   Upload    │     │  (Orchestrates)  │     │ Actions         │
└─────────────┘     └──────────────────┘     └────────┬────────┘
                                                      │
                           ┌──────────────────────────┼──────────────────────────┐
                           ▼                          ▼                          ▼
                    ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
                    │   Selenium  │           │   Appium    │           │   Desktop   │
                    │BuiltInFuncs │           │BuiltInFuncs │           │BuiltInFuncs │
                    └─────────────┘           └─────────────┘           └─────────────┘
```

### Step-by-Step Execution

1. **node_cli.py** - Entry point, handles login/authentication
2. **long_poll_handler.py** - Long-polls server for test cases
3. **adapter.py** - Converts server format to node format
4. **MainDriverApi.py** - Orchestrates test case execution
5. **sequential_actions.py** - Dispatches individual actions
6. **BuiltInFunctions.py** - Executes platform-specific actions
7. **Results uploaded** back to server

### Action Execution Detail

```python
# In sequential_actions.py
def Sequential_Actions(step_data):
    # 1. Validate step data structure
    verify_step_data(step_data)

    # 2. Find action row and determine module
    module, function_name = get_module_and_function(step_data)

    # 3. Load appropriate module
    module_obj = load_sa_modules(module)  # e.g., "selenium" -> Selenium.BuiltInFunctions

    # 4. Get and call the function
    function = getattr(module_obj, function_name)
    result = function(step_data)

    # 5. Return result
    return result  # "passed", "zeuz_failed", or "skipped"
```

---

## 4. Action System Architecture

### Action Declaration Format

Each module has an `action_declarations/*.py` file:

```python
# action_declarations/selenium.py
declarations = (
    {"name": "click", "function": "Click_Element", "screenshot": "web"},
    {"name": "text", "function": "Enter_Text_In_Text_Box", "screenshot": "web"},
    {"name": "go to link", "function": "Go_To_Link", "screenshot": "none"},
    {"name": "validate text", "function": "Validate_Text", "screenshot": "web"},
    # ... 61 total actions
)
```

### Action Declaration Fields

| Field | Description |
|-------|-------------|
| `name` | Action name used in test steps (case-insensitive) |
| `function` | Python function name in BuiltInFunctions.py |
| `screenshot` | Automatic post-action screenshot mode: `"web"`, `"mobile"`, `"desktop"`, `"none"` |
| `module` | Auto-added by loader (e.g., `"selenium"`) |

Automatic post-action screenshots are queued by `CommonUtil.TakeScreenShot()`; the shared worker waits 5 seconds only in debug runs before valid `web`/`mobile`/`desktop` captures, and skips that delayed capture if the run is cancelled during the wait.

### Action Registration (info.py)

```python
# action_declarations/info.py

# All supported parameter types
action_support = [
    "action",
    "optional action",
    "loop action",
    "element parameter",
    "parent parameter",
    "child parameter",
    "sibling parameter",
    "preceding parameter",
    "following parameter",
    "unique parameter",
    "optional parameter",
    "input parameter",
    "save parameter",
    "get parameter",
    "target parameter",
    "iframe parameter",
    "frame parameter",
    "method", "url", "body", "header", "headers",
    "scroll parameter",
    "table parameter",
    "source parameter",
    "custom action",
    "output parameter",
    "loop settings",
    "optional loop settings",
    "fail message",
]

# All modules are aggregated into single registry
actions = {}  # Populated at runtime
```

### Module Loading

```python
# sequential_actions.py
def load_sa_modules(module):
    if module == "selenium":
        from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions
        return BuiltInFunctions
    elif module == "appium":
        from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions
        return BuiltInFunctions
    elif module == "database":
        from Framework.Built_In_Automation.Database import BuiltInFunctions
        return BuiltInFunctions
    # ... etc
```

---

## 5. Element Location System

### File: `Shared_Resources/LocateElement.py` (1,750 lines)

### Main Entry Point

```python
def Get_Element(step_data_set, driver, query_debug=False, return_all_elements=False, element_wait=None):
    """
    Main element location function used by Selenium, Appium, Desktop.

    Args:
        step_data_set: List of (left, mid, right) tuples
        driver: WebDriver/AppiumDriver instance
        query_debug: If True, returns query string instead of element
        return_all_elements: If True, returns list of all matching elements
        element_wait: Override default wait timeout

    Returns:
        WebElement | List[WebElement] | "zeuz_failed"
    """
```

### Driver Type Detection

```python
def _driver_type(query_debug):
    """Detects driver type from driver string representation"""
    driver_string = str(generic_driver)

    if "selenium" in driver_string or "browser" in driver_string:
        return "selenium"
    elif "appium" in driver_string:
        return "appium"
    elif "Element" in driver_string:
        return "xml"
    elif "pyautogui" in driver_string:
        return "pyautogui"
    # NOTE: Add "playwright" here for Playwright support
    return None
```

### Query Building Functions

| Function | Purpose |
|----------|---------|
| `_construct_query()` | Main query builder - handles all parameter combinations |
| `_construct_xpath_list()` | Builds xpath parts as list |
| `_construct_xpath_string_from_list()` | Joins xpath parts |
| `build_css_selector_query()` | Builds CSS selectors |

### Element Parameter Processing

```python
# _construct_query() categorizes parameters:
element_parameter_list = []      # Primary element: id, class, tag, text, xpath, css
parent_parameter_list = []       # Ancestor elements (supports nesting: parent 1, parent 2)
child_parameter_list = []        # Descendant elements
sibling_parameter_list = []      # Sibling elements
preceding_parameter_list = []    # XPath preceding axis
following_parameter_list = []    # XPath following axis
unique_parameter_list = []       # Direct unique selectors
```

### XPath Generation Examples

```python
# Simple element parameter
("id", "element parameter", "submit-btn")
# Generates: //*[@id='submit-btn']

# With parent
("class", "parent parameter", "container")
("id", "element parameter", "submit-btn")
# Generates: //*[@class='container']//*[@id='submit-btn']

# With sibling (complex)
("text", "sibling parameter", "Username")
("class", "parent parameter", "form-group")
("tag", "element parameter", "input")
# Generates: (//[text()='Username']/ancestor::*[@class='form-group'])[last()]//input

# Partial match with *
("*class", "element parameter", "btn")
# Generates: //*[contains(@class,'btn')]

# Case-insensitive with **
("**text", "element parameter", "submit")
# Generates: //*[contains(translate(text(),'ABC...','abc...'),'submit')]
```

### Wait/Retry Loop

```python
def _get_xpath_or_css_element(...):
    # Default wait from shared variables
    if element_wait is None:
        element_wait = int(sr.Get_Shared_Variables("element_wait"))

    end = time.time() + element_wait

    while True:
        # Try to find elements
        all_matching_elements = driver.find_elements(By.XPATH, query)

        # Filter visible elements
        filtered = filter_elements(all_matching_elements, Filter)

        if filtered or time.time() > end:
            break

    # Handle index, return appropriate element
    return filtered[index] if index else filtered[0]
```

### Filter Elements

```python
def filter_elements(all_matching_elements, Filter):
    """Filter elements by visibility"""
    if Filter != "allow hidden":
        return [el for el in all_matching_elements if el.is_displayed()]
    return all_matching_elements
```

### Shadow DOM Support

```python
def shadow_root_elements(shadow_root_ds, element_ds, Filter, element_wait, return_all_elements):
    """
    Traverses nested shadow DOM roots.

    Usage:
        ("tag", "sr 1 element parameter", "my-component")
        ("id", "sr 2 element parameter", "inner-component")
        ("button", "element parameter", "submit")
    """
```

### Platform-Specific Filtering (Appium)

```python
# Parameters can specify Android/iOS values with |*| separator:
str_to_strip = "|*|"

# Example: "resource-id|*|accessibility-id"
# Android uses: resource-id
# iOS uses: accessibility-id

if device_platform == "android":
    value = value.split(str_to_strip)[0].strip()
elif device_platform == "ios":
    value = value.split(str_to_strip)[1].strip()
```

---

## 6. Parameter System

### Step Data Format

All actions receive step_data as a list of 3-tuples:

```python
step_data = [
    ("field_name", "field_type", "value"),
    ("field_name2", "field_type2", "value2"),
    # ...
]

# Example click action:
step_data = [
    ("id", "element parameter", "submit-btn"),
    ("use js", "optional parameter", "true"),
    ("click", "selenium action", "click"),
]
```

### All Supported Parameter Types (23+)

| Parameter Type | Purpose | Example |
|----------------|---------|---------|
| `action` | Primary action to execute | `("click", "selenium action", "click")` |
| `optional action` | Alternative action | |
| `loop action` | Loop control action | |
| `element parameter` | Primary element selector | `("id", "element parameter", "btn")` |
| `parent parameter` | Parent/ancestor element | `("class", "parent parameter", "container")` |
| `parent N parameter` | Nth level parent | `("tag", "parent 2 parameter", "div")` |
| `child parameter` | Child/descendant element | |
| `sibling parameter` | Sibling element | |
| `preceding parameter` | XPath preceding axis | |
| `following parameter` | XPath following axis | |
| `unique parameter` | Unique identifier (id, name) | |
| `optional parameter` | Optional configuration | `("use js", "optional parameter", "true")` |
| `input parameter` | Required input value | `("url", "input parameter", "https://...")` |
| `save parameter` | Save result to variable | `("my_var", "save parameter", "ignore")` |
| `get parameter` | Get saved element | `("element", "get parameter", "%|saved_el|%")` |
| `target parameter` | Secondary target element | |
| `iframe parameter` | IFrame selector | |
| `frame parameter` | Frame selector | |
| `scroll parameter` | Scroll configuration | |
| `table parameter` | Table operation config | |
| `source parameter` | Source element (drag/drop) | |
| `output parameter` | Output specification | |
| `loop settings` | Loop configuration | |
| `fail message` | Custom failure message | |

### Standard Parameter Parsing Pattern

```python
@logger
def Some_Action(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        # Initialize defaults
        use_js = False
        delay = 0
        timeout = None

        # Parse parameters
        for left, mid, right in step_data:
            left = left.strip().lower()
            mid = mid.strip().lower()
            right = right.strip()

            if mid == "action":
                action_value = right
            elif mid == "element parameter":
                # Element handled by LocateElement.Get_Element()
                pass
            elif mid == "optional parameter":
                if left == "use js":
                    use_js = right.lower() in ("true", "yes", "1")
                elif left == "delay":
                    delay = float(right)
                elif left == "timeout":
                    timeout = int(right)
            elif mid == "input parameter":
                if left == "url":
                    url = right
            elif mid == "save parameter":
                save_var = left

        # Get element if needed
        Element = LocateElement.Get_Element(step_data, driver)
        if Element == "zeuz_failed":
            return "zeuz_failed"

        # Perform action
        # ...

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
```

### Boolean Parsing Convention

```python
# Framework-wide boolean detection:
value.strip().lower() in ("true", "yes", "1", "on", "enable", "enabled")    # True
value.strip().lower() in ("false", "no", "0", "off", "disable", "disabled")  # False
```

---

## 7. Shared Variables System

### File: `Shared_Resources/BuiltInFunctionSharedResources.py` (1,477 lines)

### Global Storage

```python
shared_variables = {}          # Main variable store
protected_variables = []       # Cannot be overwritten
attachment_variables = {}      # File attachments
```

### Core Functions

```python
def Set_Shared_Variables(key, value, protected=False, attachment_var=False,
                         print_variable=True, pretty=True, print_raw=False):
    """
    Save a variable to shared storage.

    Args:
        key: Variable name
        value: Any Python value
        protected: If True, cannot be overwritten
        attachment_var: If True, store in attachment_variables
        print_variable: If True, log the variable
    """
    shared_variables[key] = value
    if protected:
        protected_variables.append(key)

def Get_Shared_Variables(key, log=True):
    """
    Retrieve a variable from shared storage.

    Returns:
        The stored value, or "zeuz_failed" if not found
    """
    if key in shared_variables:
        return shared_variables[key]
    return "zeuz_failed"

def Test_Shared_Variables(key):
    """Check if variable exists. Returns True/False."""
    return key in shared_variables
```

### Variable Reference Syntax

Variables can be referenced in step data using `%|variable_name|%`:

```python
# Basic reference
("url", "input parameter", "%|my_url|%")

# Index access
("item", "input parameter", "%|my_list[0]|%")

# Dictionary access
("name", "input parameter", "%|user["name"]|%")

# Slice
("subset", "input parameter", "%|my_list[0:5]|%")

# Nested access
("value", "input parameter", "%|data[0]["items"][2]|%")
```

### Complex Variable Parsing

```python
def parse_variable(name):
    """
    Parse complex variable references.

    Supports:
        var[index]           - List/dict index access
        var["key"]           - Dict key access
        var[start:end]       - Slice
        var{_, *, n, _, field}  - Pattern matching
        var(key1, key2)      - Key matching
    """
```

### Standard Variables Used Across Framework

| Variable | Purpose | Set By |
|----------|---------|--------|
| `selenium_driver` | Active Selenium WebDriver | Selenium.Go_To_Link |
| `appium_driver` | Active Appium driver | Appium.connect_device |
| `element_wait` | Default element wait (seconds) | Framework config |
| `zeuz_screenshot` | Last screenshot path | Screenshot functions |
| `package_name` | Android app package | Appium |
| `device_info` | Device metadata | Appium |
| `zeuz_download_folder` | Download directory | Selenium |

---

## 8. Shared Utilities & Patterns

### CommonUtil.py

#### Logging

```python
def ExecLog(sModuleInfo, message, log_level, variable=None):
    """
    Central logging function.

    Log Levels:
        0 - Trace (verbose)
        1 - Info/Pass (green)
        2 - Warning (yellow)
        3 - Error (red)
        4 - Debug
        5 - Debug verbose
    """
```

#### Exception Handling

```python
def Exception_Handler(exc_info, custom_message=None):
    """
    Standard exception handler. Logs and returns "zeuz_failed".

    Usage:
        except Exception:
            return CommonUtil.Exception_Handler(sys.exc_info())
    """
```

### Return Status Tags

```python
# CommonUtil.py
passed_tag_list = [
    "passed", "pass", "passed ok", "zeuz_passed", "ok", "success", "successful"
]

failed_tag_list = [
    "zeuz_failed", "failed", "fail", "failure", "error", "exception"
]

skipped_tag_list = [
    "skip", "SKIP", "Skip", "skipped", "SKIPPED", "Skipped"
]
```

**All action functions MUST return one of these values.**

### Common Functions (common_functions.py - 7,500+ lines)

#### Variable Operations
- `Save_Variable()` - Save to shared variables
- `Compare_Variables()` - Compare two values
- `Compare_Lists_or_Dicts()` - Deep comparison
- `Initialize_List()` / `Initialize_Dict()` - Create collections
- `append_list_shared_variable()` - Append to list
- `split_string()` / `replace_string()` - String operations

#### Control Flow
- `Sleep()` - Wait for duration
- `Wait_For_Element()` - Wait for element visibility
- `step_result()` - Set step result
- `step_exit()` / `testcase_exit()` - Exit control

#### File Operations
- `Read_text_file()` / `text_write()` - Text files
- `csv_read()` / `csv_write()` - CSV files
- `excel_read()` / `excel_write()` - Excel files
- `yaml_read()` / `yaml_write()` - YAML files

#### Data Processing
- `execute_python_code()` - Dynamic Python execution
- `search_and_save_text()` - Regex text search
- `validate_schema()` - JSON schema validation

---

## 9. Module Details

### Selenium Module (`Web/Selenium/BuiltInFunctions.py`)

**Lines:** 5,280
**Actions:** 55+

#### Global State

```python
current_driver_id = None           # Active driver identifier
selenium_driver = None              # Active WebDriver instance
selenium_details = {}               # All drivers: {"id": {"driver": obj, "remote-debugging-port": 9222}}
```

#### Key Actions

| Action | Function | Description |
|--------|----------|-------------|
| go to link | `Go_To_Link()` | Open browser, navigate to URL |
| click | `Click_Element()` | Click element |
| text | `Enter_Text_In_Text_Box()` | Enter text in field |
| validate text | `Validate_Text()` | Verify element text |
| select/deselect | `Select_Deselect()` | Dropdown operations |
| switch window/tab | `switch_window_or_tab()` | Tab switching |
| execute javascript | `execute_javascript()` | Run JS in browser |
| take screenshot | `take_screenshot_selenium()` | Capture screenshot |
| tear down selenium | `Tear_Down_Selenium()` | Close browser |

#### Common Optional Parameters (Selenium)

| Parameter | Used In | Playwright Equivalent |
|-----------|---------|----------------------|
| `use js` | Click, Text, Checkbox | `force: true` or `evaluate()` |
| `delay` | Text input | `type({delay: ms})` |
| `clear` | Text input | `locator.clear()` |
| `offset` | Click | `click({position: {x, y}})` |
| `allow hidden` | Multiple | `force: true` |
| `wait` | Multiple | `timeout` option |

### Appium Module (`Mobile/CrossPlatform/Appium/BuiltInFunctions.py`)

**Lines:** 20,000+
**Actions:** 100+

#### Platform-Specific Parameters

```python
# Android/iOS selector with |*| separator
("resource-id|*|accessibility-id", "element parameter", "submit|*|submitButton")
```

#### Multi-Device Support

```python
appium_details = {
    "device_1": {"driver": driver1, "serial": "ABC123"},
    "device_2": {"driver": driver2, "serial": "DEF456"},
}
```

### Desktop Module

**Locations:** `Desktop/Windows/`, `Desktop/Mac/`, `Desktop/Linux/`, `Desktop/CrossPlatform/`

Uses PyAutoGUI for image-based element detection.

### Database Module

Supports: PostgreSQL, MySQL, Oracle, Snowflake, SQL Server, ODBC

---

## 10. Decorators & Logging

### File: `Utilities/decorators.py`

### @logger Decorator

```python
def logger(func):
    """
    Logs function entry/exit, execution time, and handles failure detection.

    Usage:
        @logger
        def My_Action(step_data):
            ...

    Behavior:
        - Logs "ENTERING: function_name" at start
        - Logs "EXITING: function_name" at end
        - Logs execution time
        - Detects "zeuz_failed" return and logs error
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        CommonUtil.ExecLog("", f"ENTERING: {func.__name__}", 0)
        start = time.time()

        result = func(*args, **kwargs)

        elapsed = time.time() - start
        CommonUtil.ExecLog("", f"EXITING: {func.__name__} ({elapsed:.2f}s)", 0)

        if result in failed_tag_list:
            CommonUtil.ExecLog("", f"FAILED: {func.__name__}", 3)

        return result
    return wrapper
```

### @deprecated Decorator

```python
def deprecated(message=""):
    """
    Marks function as deprecated with warning.

    Usage:
        @deprecated("Use new_function() instead")
        def old_function():
            ...
    """
```

---

## 11. Return Status System

### Every action function MUST return:

```python
"passed"        # Success - test step passed
"zeuz_failed"   # Failure - test step failed
"skipped"       # Skipped - test step skipped
```

### Pattern

```python
@logger
def My_Action(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        # Action logic
        Element = LocateElement.Get_Element(step_data, driver)

        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # Success
        CommonUtil.ExecLog(sModuleInfo, "Action completed successfully", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
```

---

## 12. Adding New Modules

### Steps to Add a New Module (e.g., Playwright)

#### 1. Create Directory Structure

```
Framework/Built_In_Automation/Web/Playwright/
├── __init__.py
├── BuiltInFunctions.py
└── utils.py (optional)
```

#### 2. Create Action Declarations

```python
# action_declarations/playwright.py
declarations = (
    {"name": "open browser", "function": "Open_Browser", "screenshot": "none"},
    {"name": "click", "function": "Click_Element", "screenshot": "web"},
    {"name": "text", "function": "Enter_Text", "screenshot": "web"},
    # ...
)
```

#### 3. Register Module in info.py

```python
# action_declarations/info.py
from . import playwright  # Add import

# Add to modules list
```

#### 4. Add Module Loading

```python
# sequential_actions.py
def load_sa_modules(module):
    # ... existing modules ...
    elif module == "playwright":
        from Framework.Built_In_Automation.Web.Playwright import BuiltInFunctions
        return BuiltInFunctions
```

#### 5. Implement BuiltInFunctions.py

Follow patterns from existing modules:
- Use `@logger` decorator
- Parse step_data with standard pattern
- Use shared utilities (CommonUtil, Shared_Resources)
- Return "passed"/"zeuz_failed"/"skipped"

---

## Appendix: Quick Reference

### Standard Function Template

```python
@logger
def Action_Name(step_data):
    """
    Action description.

    Example:
        Field               Sub Field           Value
        id                  element parameter   submit-btn
        action_name         selenium action     action_name
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global driver_variable  # if needed

    try:
        # Parse parameters
        for left, mid, right in step_data:
            left = left.strip().lower()
            mid = mid.strip().lower()
            # ...

        # Get element if needed
        Element = LocateElement.Get_Element(step_data, driver)
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # Perform action
        # ...

        CommonUtil.ExecLog(sModuleInfo, "Success message", 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
```

### Import Template

```python
import sys
import inspect
from Framework.Utilities import CommonUtil
from Framework.Utilities.decorators import logger
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
    LocateElement,
)
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list

MODULE_NAME = inspect.getmodulename(__file__)
```
