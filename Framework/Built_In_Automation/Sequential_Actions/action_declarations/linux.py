declarations = (
    { "name": "open app",        "function": "open_app",                "screenshot": "desktop" },
    { "name": "click",           "function": "click_element",           "screenshot": "desktop" },
    { "name": "text",            "function": "enter_text",              "screenshot": "desktop" },
    { "name": "wait to appear",  "function": "wait_for_element",        "screenshot": "desktop" },
    { "name": "wait to disappear","function": "wait_for_element",       "screenshot": "desktop" },
    { "name": "save attribute",  "function": "save_attribute",          "screenshot": "desktop" },
    { "name": "keystroke keys",  "function": "send_keystroke",  "screenshot": "desktop" },
)

module_name = "linux"

for dec in declarations:
    dec["module"] = module_name
