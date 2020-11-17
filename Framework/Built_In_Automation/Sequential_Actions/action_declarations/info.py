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
    "target parameter",
    "end parameter",
    "optional parameter",
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
    "custom action",
    "unique parameter",
    "save parameter",
    "get parameter",
    "loop settings",
    "optional loop settings",
    "attribute constrain",
    "optional option",
    "graphql",
)

# List of supported mobile platforms - must be lower case
supported_platforms = ("android", "ios")
