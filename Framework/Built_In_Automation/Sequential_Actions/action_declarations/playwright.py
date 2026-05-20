"""
Playwright Action Declarations

Defines all available Playwright actions for the Zeuz Node framework.
Users can switch from Selenium to Playwright by changing "selenium action" to "playwright action"
in their test steps while keeping all other parameters the same.

Author: Zeuz/AutomationSolutionz
"""

declarations = (
    # Browser Management
    { "name": "open browser",                  "function": "Open_Browser",               "screenshot": "web" },
    { "name": "go to link",                    "function": "Go_To_Link",                 "screenshot": "web" },
    { "name": "tear down browser",             "function": "Tear_Down_Playwright",       "screenshot": "none" },
    { "name": "teardown",                      "function": "Tear_Down_Playwright",       "screenshot": "none" },
    { "name": "switch browser",                "function": "Switch_Browser",             "screenshot": "none" },

    # Click Actions
    { "name": "click",                         "function": "Click_Element",              "screenshot": "web" },
    { "name": "double click",                  "function": "Double_Click_Element",       "screenshot": "web" },
    { "name": "right click",                   "function": "Right_Click_Element",        "screenshot": "web" },
    { "name": "hover",                         "function": "Hover_Over_Element",         "screenshot": "web" },

    # Text Input
    { "name": "text",                          "function": "Enter_Text_In_Text_Box",     "screenshot": "web" },
    { "name": "keystroke keys",                "function": "Keystroke_For_Element",      "screenshot": "web" },
    { "name": "keystroke chars",               "function": "Keystroke_For_Element",      "screenshot": "web" },

    # Validation
    { "name": "validate full text",            "function": "Validate_Text",              "screenshot": "web" },
    { "name": "validate partial text",         "function": "Validate_Text",              "screenshot": "web" },
    { "name": "if element exists",             "function": "if_element_exists",          "screenshot": "web" },

    # Element Information
    { "name": "save attribute",                "function": "Save_Attribute",             "screenshot": "web" },
    { "name": "change attribute value",        "function": "Change_Attribute_Value",       "screenshot": "web" },
    { "name": "get element info",              "function": "get_element_info",           "screenshot": "web" },
    { "name": "extract table data",            "function": "Extract_Table_Data",         "screenshot": "web" },

    # Navigation
    { "name": "navigate",                      "function": "Navigate",                   "screenshot": "web" },
    { "name": "get current url",               "function": "Get_Current_URL",            "screenshot": "none" },

    # Scrolling
    { "name": "scroll",                        "function": "Scroll",                     "screenshot": "web" },
    { "name": "scroll to element",             "function": "scroll_to_element",          "screenshot": "web" },
    { "name": "scroll element to top",         "function": "scroll_to_element",          "screenshot": "web" },
    { "name": "scroll to top",                 "function": "scroll_to_top",              "screenshot": "web" },

    # Lists / attributes
    { "name": "save attribute values in list", "function": "save_attribute_values_in_list", "screenshot": "web" },
    { "name": "save web elements in list",     "function": "save_web_elements_in_list",     "screenshot": "web" },

    # Selection (Dropdowns/Checkboxes)
    { "name": "select by visible text",        "function": "Select_Deselect",            "screenshot": "web" },
    { "name": "deselect by visible text",      "function": "Select_Deselect",            "screenshot": "web" },
    { "name": "select by value",               "function": "Select_Deselect",            "screenshot": "web" },
    { "name": "deselect by value",             "function": "Select_Deselect",            "screenshot": "web" },
    { "name": "select by index",               "function": "Select_Deselect",            "screenshot": "web" },
    { "name": "deselect by index",             "function": "Select_Deselect",            "screenshot": "web" },
    { "name": "deselect all",                  "function": "Select_Deselect",            "screenshot": "web" },
    { "name": "check uncheck",                 "function": "check_uncheck",              "screenshot": "web" },
    { "name": "multiple check uncheck",        "function": "multiple_check_uncheck",        "screenshot": "web" },

    # Window/Tab Management
    { "name": "switch window",                 "function": "switch_window_or_tab",       "screenshot": "web" },
    { "name": "switch window or frame",        "function": "switch_window_or_tab",       "screenshot": "web" },
    { "name": "switch window/tab",             "function": "switch_window_or_tab",       "screenshot": "web" },
    { "name": "open new tab",                  "function": "open_new_tab",               "screenshot": "web" },
    { "name": "close tab",                     "function": "close_tab",                  "screenshot": "web" },

    # iframe Handling
    { "name": "switch iframe",                 "function": "switch_iframe",              "screenshot": "web" },

    # Alerts/Dialogs
    { "name": "handle alert",                  "function": "Handle_Browser_Alert",       "screenshot": "desktop" },

    # Drag and Drop
    { "name": "drag and drop",                 "function": "drag_and_drop",              "screenshot": "web" },

    # Screenshots
    { "name": "take screenshot web",           "function": "take_screenshot_playwright", "screenshot": "web" },

    # JavaScript
    { "name": "execute javascript",            "function": "execute_javascript",         "screenshot": "web" },

    # File Upload
    { "name": "upload file",                   "function": "upload_file",                "screenshot": "web" },

    # Window Management
    { "name": "resize window",                 "function": "resize_window",              "screenshot": "web" },

    # Wait Actions
    { "name": "wait for element",              "function": "Wait_For_Element",           "screenshot": "web" },

    # Tracing/Performance (Playwright-specific)
    { "name": "start tracing",                 "function": "Start_Tracing",              "screenshot": "none" },
    { "name": "stop tracing",                  "function": "Stop_Tracing",               "screenshot": "none" },

    # Network Interception (Playwright-specific)
    { "name": "intercept network",             "function": "Intercept_Network",          "screenshot": "none" },
)  # yapf: disable

module_name = "playwright"

for dec in declarations:
    dec["module"] = module_name
