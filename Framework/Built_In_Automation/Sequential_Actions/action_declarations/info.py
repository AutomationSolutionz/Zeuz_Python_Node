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
    "search element parameter",
    "target parameter",
    "desired element parameter",
    "desired parent parameter",
    "desired sibling parameter",
    "desired child parameter",
    "src element parameter", "src parent parameter", "src sibling parameter", "src child parameter",
    "source element parameter", "source parent parameter", "source sibling parameter", "source child parameter",
    "dst element parameter", "dst parent parameter", "dst sibling parameter", "dst child parameter",
    "destination element parameter", "destination parent parameter", "destination sibling parameter", "destination child parameter",
    "optional parameter",
    "iframe parameter",
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
    "input parameter",
    "output parameter",
    "custom action",
    "unique parameter",
    "save parameter",
    "get parameter",
    "loop settings",
    "optional loop settings",
    "attribute constrain",
    "optional option",
    "graphql",
    "shared capability"
)

# List of supported mobile platforms - must be lower case
supported_platforms = ("android", "ios")
