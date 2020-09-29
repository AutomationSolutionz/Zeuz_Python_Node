declarations = (
    # Database actions
    { "name": "connect to db",              "function": "connect_to_db", },
    { "name": "select query",               "function": "db_select", },
    { "name": "insert update delete query", "function": "db_non_query", },
)

module_name = "database"

for dec in declarations:
    dec["module"] = module_name
    dec["screenshot"] = "none" # none of the db actions will have screenshots
