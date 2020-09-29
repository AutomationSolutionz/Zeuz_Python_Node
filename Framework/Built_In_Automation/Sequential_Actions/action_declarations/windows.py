declarations = (
    { "name": "click",           "function": "Click_Element",          "screenshot": "desktop" },
    { "name": "right click",     "function": "Right_Click_Element",    "screenshot": "desktop" },
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
    { "name": "save text",       "function": "Save_Text",              "screenshot": "desktop" },
)

module_name = "windows"

for dec in declarations:
    dec["module"] = module_name
