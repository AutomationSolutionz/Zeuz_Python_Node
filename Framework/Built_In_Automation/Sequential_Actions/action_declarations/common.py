declarations = (
    { "name": "step result",                                 "function": "step_result",                           "screenshot": "none" },
    { "name": "sleep",                                       "function": "Sleep",                                 "screenshot": "none" },
    { "name": "wait",                                        "function": "Wait_For_Element",                      "screenshot": "none" },
    { "name": "wait disable",                                "function": "Wait_For_Element",                      "screenshot": "none" },
    { "name": "save text",                                   "function": "Save_Text",                             "screenshot": "none" },
    { "name": "compare variable",                            "function": "Compare_Variables",                     "screenshot": "none" },
    { "name": "compare list",                                "function": "Compare_Lists_or_Dicts",                "screenshot": "none" },
    { "name": "compare dictionary",                          "function": "Compare_Lists_or_Dicts",                "screenshot": "none" },
    { "name": "save variable",                               "function": "Save_Variable",                         "screenshot": "none" },
    { "name": "delete shared variables",                     "function": "delete_all_shared_variables",           "screenshot": "none" },
    { "name": "settings",                                    "function": "sequential_actions_settings",           "screenshot": "none" },
    { "name": "step exit",                                   "function": "step_exit",                             "screenshot": "none" },
    { "name": "save time",                                   "function": "Save_Current_Time",                     "screenshot": "none" },
    { "name": "create or append list into list",             "function": "insert_list_into_another_list",         "screenshot": "none" },
    { "name": "validate order",                              "function": "validate_list_order",                   "screenshot": "none" },
    { "name": "create or append dictionary into dictionary", "function": "insert_dict_into_another_dict",         "screenshot": "none" },
    { "name": "create list",                                 "function": "Initialize_List",                       "screenshot": "none" },
    { "name": "create dictionary",                           "function": "Initialize_Dict",                       "screenshot": "none" },
    { "name": "create or append list",                       "function": "append_list_shared_variable",           "screenshot": "none" },
    { "name": "create or append dictionary",                 "function": "append_dict_shared_variable",           "screenshot": "none" },
    { "name": "set server variable",                         "function": "set_server_variable",                   "screenshot": "none" },
    { "name": "get server variable",                         "function": "get_server_variable",                   "screenshot": "none" },
    { "name": "get all server variable",                     "function": "get_all_server_variable",               "screenshot": "none" },
    { "name": "start timer",                                 "function": "start_timer",                           "screenshot": "none" },
    { "name": "wait for timer",                              "function": "wait_for_timer",                        "screenshot": "none" },
    { "name": "get server variable and wait",                "function": "get_server_variable_and_wait",          "screenshot": "none" },
    { "name": "randomize list",                              "function": "Randomize_List",                        "screenshot": "none" },
    { "name": "create 3d list",                              "function": "create_3d_list",                        "screenshot": "none" },
    { "name": "download ftp file",                           "function": "download_ftp_file",                     "screenshot": "none" },
    { "name": "save text from file into variable",           "function": "save_text_from_file_into_variable",     "screenshot": "none" },
    { "name": "compare partial variable",                    "function": "Compare_Partial_Variables",             "screenshot": "none" },
    { "name": "save value from dictionary by key",           "function": "save_dict_value_by_key",                "screenshot": "none" },
    { "name": "save key value from dict list",               "function": "save_key_value_from_dict_list",         "screenshot": "none" },
    { "name": "extract date",                                "function": "extract_date",                          "screenshot": "none" },
    { "name": "voice command response",                      "function": "voice_command_response",                "screenshot": "none" },
    { "name": "compare partial variables",                   "function": "Compare_Partial_Variables",             "screenshot": "none" },
    { "name": "save variable by list difference",            "function": "save_variable_by_list_difference",      "screenshot": "none" },
    { "name": "split string",                                "function": "split_string",                          "screenshot": "none" },
    { "name": "create/append to list or dictionary",         "function": "save_into_variable",                    "screenshot": "none" },
    { "name": "save into variable",                          "function": "save_into_variable",                    "screenshot": "none" },
    { "name": "save length",                                 "function": "save_length",                           "screenshot": "none" },
    { "name": "validate schema",                             "function": "validate_schema",                       "screenshot": "none" },

    # Mail actions
    { "name": "send mail",                                   "function": "send_mail",                             "screenshot": "none" },
    { "name": "check latest mail",                           "function": "check_latest_mail",                     "screenshot": "none" },

    # Global Variable Actions
    { "name": "get global list variable",                    "function": "get_global_list_variable",              "screenshot": "none" },
    { "name": "append to global list variable",              "function": "append_to_global_list_variable",        "screenshot": "none" },
    { "name": "remove item from global list variable",       "function": "remove_item_from_global_list_variable", "screenshot": "none" },

    # Excel actions
    { "name": "write into single cell in excel",             "function": "write_into_single_cell_in_excel",       "screenshot": "none" },
    { "name": "run macro in excel",                          "function": "run_macro_in_excel",                    "screenshot": "none" },
    { "name": "get excel table",                             "function": "get_excel_table",                       "screenshot": "none" },
    { "name": "write into excel",                            "function": "excel_write",                           "screenshot": "none" },
    { "name": "excel comparison",                            "function": "excel_comparison",                      "screenshot": "none" },
    { "name": "read from excel",                             "function": "excel_read",                            "screenshot": "none" },
)

module_name = "common"

for dec in declarations:
    dec["module"] = module_name
