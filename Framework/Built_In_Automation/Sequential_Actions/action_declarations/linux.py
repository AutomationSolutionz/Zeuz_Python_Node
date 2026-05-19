declarations = (
    { "name": "open app",         "function": "open_app",                "screenshot": "desktop" },
    { "name": "close app",        "function": "close_app",               "screenshot": "desktop" },
    { "name": "click",            "function": "click_element",           "screenshot": "desktop" },
    { "name": "check",            "function": "check_uncheck",           "screenshot": "desktop" },
    { "name": "uncheck",          "function": "check_uncheck",           "screenshot": "desktop" },
    { "name": "hover",            "function": "hover_over_element",      "screenshot": "desktop" },
    { "name": "drag and drop",    "function": "drag_and_drop_element",   "screenshot": "desktop" },
    { "name": "scroll to element","function": "scroll_to_element",       "screenshot": "desktop" },
    { "name": "swap",             "function": "swap",                    "screenshot": "desktop" },
    { "name": "select",           "function": "select_item",             "screenshot": "desktop" },
    { "name": "set value",        "function": "set_value",               "screenshot": "desktop" },
    { "name": "go to desktop",    "function": "go_to_desktop",           "screenshot": "desktop" },
    { "name": "text",             "function": "enter_text",              "screenshot": "desktop" },
    { "name": "wait to appear",   "function": "wait_for_element",        "screenshot": "desktop" },
    { "name": "wait to disappear","function": "wait_for_element",        "screenshot": "desktop" },
    { "name": "save attribute",   "function": "save_attribute",          "screenshot": "desktop" },
    { "name": "keystroke keys",   "function": "send_keystroke",          "screenshot": "desktop" },
    { "name": "keystroke chars",  "function": "send_keystroke",          "screenshot": "desktop" },
)

module_name = "linux"

for dec in declarations:
    dec["module"] = module_name
