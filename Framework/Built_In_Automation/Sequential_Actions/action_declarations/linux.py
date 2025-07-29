declarations = (
    { "name": "open app",        "function": "open_app",                "screenshot": "desktop" },
    { "name": "click",           "function": "click_element",           "screenshot": "desktop" },
    { "name": "text",            "function": "enter_text",              "screenshot": "desktop" },
)

module_name = "linux"

for dec in declarations:
    dec["module"] = module_name
