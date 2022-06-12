declarations = (
    { "name": "locust config",                 "function": "locust_config",             "screenshot": "none" },
    { "name": "assign locust user",                 "function": "assign_locust_user",             "screenshot": "none" },
    { "name": "assign locust task",                 "function": "assign_locust_task",             "screenshot": "none" },
) # yapf: disable

module_name = "performance"

for dec in declarations:
    dec["module"] = module_name
