import regex as re
from . import (
    appium,
    common,
    desktop,
    rest,
    selenium,
    utility,
    windows,
    xml,
    database,
    performance
)

modules = (
    appium,
    common,
    desktop,
    rest,
    selenium,
    utility,
    windows,
    xml,
    database,
    performance
)

# This will be exported and contains all the actions.
actions = {}

action_id = 1
for mod in modules:
    for dec in mod.declarations:
        actions[action_id] = dec
        action_id += 1

# List of Sub-Field keywords, must be all lowercase, and using single spaces - no underscores
action_support = (
    "action",
    "optional action",
    "loop action",
    "element parameter",
    "child parameter",
    "sibling parameter",
    "parent parameter",
    "following parameter",
    "next parameter",
    "preceding parameter",
    "previous parameter",
    "search element parameter",
    "target parameter",
    "desired element parameter", "desired parent parameter", "desired sibling parameter", "desired child parameter",
    "src element parameter", "src parent parameter", "src sibling parameter", "src child parameter",
    "source element parameter", "source parent parameter", "source sibling parameter", "source child parameter",
    "dst element parameter", "dst parent parameter", "dst sibling parameter", "dst child parameter",
    "destination element parameter", "destination parent parameter", "destination sibling parameter", "destination child parameter",
    "optional parameter",
    "optional label",
    "iframe parameter",
    "frame parameter",
    "method",
    "url",
    "body",
    "header",
    "headers",
    "compare",
    "path",
    "value",
    "result",
    "scroll parameter",
    "table parameter",
    "source parameter",
    "input parameter", "parameter",
    "output parameter",
    "custom action",
    "unique parameter",
    "save parameter",
    "get parameter",
    "loop settings",
    "optional loop settings",
    "optional loop condition",
    "optional loop control",
    "attribute constrain",
    "optional option",
    "graphql",
    "shared capability",
    "chrome option", "chrome options", "chrome experimental option", "chrome experimental options",
    "pre sleep", "post sleep", "pre post sleep", "post pre sleep",
    "zoom parameter", "optional zoom parameter", "pan parameter", "optional pan parameter",
    "profile option", "profile options",
    "text classifier offset"
    "fail message",
)
patterns = [
    "^parent \d parameter$",
    "^sibling \d parameter$",
    "^child \d parameter$",
    "^following \d parameter$",
    "^next \d parameter$",
    "^preceding \d parameter$",
    "^previous \d parameter$",

    "^src parent \d parameter$", "^src sibling \d parameter$", "^src child \d parameter$", "^src following \d parameter$", "^src next \d parameter$", "^src preceding \d parameter$", "^src previous \d parameter$",
    "^dst parent \d parameter$", "^dst sibling \d parameter$", "^dst child \d parameter$", "^dst following \d parameter$", "^dst next \d parameter$", "^dst preceding \d parameter$", "^dst previous \d parameter$",
    "^source parent \d parameter$", "^source sibling \d parameter$", "^source child \d parameter$", "^source following \d parameter$", "^source next \d parameter$", "^source preceding \d parameter$", "^source prevoius \d parameter$",
    "^destination parent \d parameter$", "^destination sibling \d parameter$", "^destination child \d parameter$", "^destination following \d parameter$", "^destination next \d parameter$", "^destination preceding \d parameter$","^destination previous \d parameter$",
    "^desired parent \d parameter$", "^desired sibling \d parameter$", "^desired child \d parameter$", "^desired following \d parameter$", "^desired next \d parameter$", "^desired preceding \d parameter$", "^desired previous \d parameter$",

]
# List of supported mobile platforms - must be lower case
supported_platforms = ("android", "ios")

def sub_field_match(text:str)->bool:
    if text in action_support:
        return True
    for pattern in patterns:
        if re.search(pattern, text):
            return True
    return False
'''
parent 1 parameter
'''