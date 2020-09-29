declarations = (
    # Database actions
    { "name": "connect to db",              "function": "connect_to_db", "screenshot": "none" },
    { "name": "select query",               "function": "db_select",     "screenshot": "none" },
    { "name": "insert update delete query", "function": "db_non_query",  "screenshot": "none" },
    { "name": "select from db", "function": "select_from_db",  "screenshot": "none" },
    { "name": "insert into db", "function": "insert_into_db",  "screenshot": "none" },
    { "name": "delete from db", "function": "delete_from_db",  "screenshot": "none" },
    { "name": "update into db", "function": "update_into_db",  "screenshot": "none" },
)

module_name = "database"

for dec in declarations:
    dec["module"] = module_name
