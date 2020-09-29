declarations = (
    # Database actions
    { "name": "connect to db",              "function": "connect_to_db", "screenshot": "none" },
    { "name": "select query",               "function": "db_select",     "screenshot": "none" },
    { "name": "insert update delete query", "function": "db_non_query",  "screenshot": "none" },
)

module_name = "database"

for dec in declarations:
    dec["module"] = module_name
