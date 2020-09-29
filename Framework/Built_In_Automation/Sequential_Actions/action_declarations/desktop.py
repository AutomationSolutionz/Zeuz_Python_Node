declarations = (
    { "name": "click",                "function": "Click_Element",              "screenshot": "desktop" },
    { "name": "double click",         "function": "Click_Element",              "screenshot": "desktop" },
    { "name": "hover",                "function": "move_mouse",                 "screenshot": "desktop" },
    { "name": "text",                 "function": "Enter_Text",                 "screenshot": "desktop" },
    { "name": "close program",        "function": "close_program",              "screenshot": "desktop" },
    { "name": "launch program",       "function": "launch_program",             "screenshot": "desktop" },
    { "name": "check",                "function": "check_for_element",          "screenshot": "desktop" },
    { "name": "teardown",             "function": "teardown",                   "screenshot": "desktop" },
    { "name": "drag",                 "function": "Drag_Element",               "screenshot": "desktop" },
    { "name": "listbox",              "function": "navigate_listbox",           "screenshot": "desktop" },
    { "name": "hotkey",               "function": "execute_hotkey",             "screenshot": "desktop" },
    { "name": "click on coordinates", "function": "click_on_coordinates",       "screenshot": "desktop" },
    { "name": "move mouse cursor",    "function": "move_mouse_cursor",          "screenshot": "desktop" },
    { "name": "wait gui",             "function": "Wait_For_Element_Pyautogui", "screenshot": "desktop" },
    { "name": "wait disable gui",     "function": "Wait_For_Element_Pyautogui", "screenshot": "desktop" },
)

module_name = "desktop"

for dec in declarations:
    dec["module"] = module_name
