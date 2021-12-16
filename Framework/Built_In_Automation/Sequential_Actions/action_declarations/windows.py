declarations = (
    { "name": "click",           "function": "Click_Element",          "screenshot": "desktop" },
    { "name": "right click",     "function": "Right_Click_Element",    "screenshot": "desktop" },
    { "name": "check uncheck",   "function": "Check_uncheck",          "screenshot": "desktop" },
    { "name": "drag and drop",   "function": "Drag_and_Drop_Element",  "screenshot": "desktop" },
    { "name": "double click",    "function": "Double_Click_Element",   "screenshot": "desktop" },
    { "name": "hover",           "function": "Hover_Over_Element",     "screenshot": "desktop" },
    { "name": "keystroke keys",  "function": "Keystroke_For_Element",  "screenshot": "desktop" },
    { "name": "keystroke chars", "function": "Keystroke_For_Element",  "screenshot": "desktop" },
    { "name": "text",            "function": "Enter_Text_In_Text_Box", "screenshot": "desktop" },
    { "name": "Desktop",         "function": "go_to_desktop",          "screenshot": "desktop" },
    { "name": "open app",        "function": "Run_Application",        "screenshot": "desktop" },
    { "name": "close app",       "function": "Close_Application",      "screenshot": "desktop" },
    { "name": "validate text",   "function": "Validate_Text",          "screenshot": "desktop" },
    { "name": "save attribute",  "function": "Save_Attribute",         "screenshot": "desktop" },
    { "name": "wait to appear",  "function": "wait_for_element",       "screenshot": "desktop" },
    { "name": "wait to disappear","function": "wait_for_element",      "screenshot": "desktop" },
    { "name": "scroll to element","function": "Scroll_to_element",     "screenshot": "desktop" },
    { "name": "swipe",            "function": "Swipe",                 "screenshot": "desktop" },
    { "name": "save attribute values in list","function": "save_attribute_values_in_list","screenshot": "desktop" },
) # yapf: disable

module_name = "windows"

for dec in declarations:
    dec["module"] = module_name
