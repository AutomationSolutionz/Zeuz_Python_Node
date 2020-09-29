declarations = (
    { "name": "update", "function": "update_element", "screenshot": "none" },
    { "name": "add",    "function": "add_element",    "screenshot": "none" },
    { "name": "read",   "function": "read_element",   "screenshot": "none" },
    { "name": "delete", "function": "delete_element", "screenshot": "none" },
)

module_name = "xml"

for dec in declarations:
    dec["module"] = module_name
