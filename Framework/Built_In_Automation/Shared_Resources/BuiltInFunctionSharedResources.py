# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

# shared_variables

import inspect, sys, time, collections
import string
import random
import re
import json
from Framework.Utilities import CommonUtil
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list
from datetime import datetime
from dateutil.relativedelta import relativedelta
from Framework.Utilities.decorators import logger, deprecated
from .data_collector import DataCollector


global shared_variables
shared_variables = {}
protected_variables = (
    []
)  # Used to ensure internally used shared variables can't be overwritten by step data


MODULE_NAME = inspect.getmodulename(__file__)
data_collector = DataCollector()


def Set_Shared_Variables(key, value, protected=False, allowEmpty=False, print_variable=True):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        global shared_variables, protected_variables
        if not allowEmpty and (
            key == "" or key == None or value == "" or value == None
        ):  # if input is invalid
            return "failed"
        else:  # Valid input
            if protected:
                protected_variables.append(key)  # Add to list of protected variables
            else:  # Check if user is trying to overwrite a protected variable
                if key in protected_variables:  # If we find a match, exit with failure
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Error: You tried to overwrite protected variable '%s'. Please choose a different variable name."
                        % key,
                        3,
                    )
                    return "failed"

            # Good to proceed
            shared_variables[key] = value

            if print_variable:
                CommonUtil.ExecLog(
                    sModuleInfo, "Saved variable: %s" % key, 1,
                    variable={
                        "key": key,
                        "val": CommonUtil.parse_value_into_object(value)
                    }
                )

            # Try to get a pretty print.
            CommonUtil.prettify(key, value)

            return "passed"
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Set_List_Shared_Variables(list_name, key, value, protected=False):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        global shared_variables, protected_variables
        if (
            key == ""
            or key == None
            or value == ""
            or value == None
            or list_name == ""
            or list_name == None
        ):  # if input is invalid
            return "failed"
        else:  # Valid input
            if protected:
                protected_variables.append(key)  # Add to list of protected variables
            else:  # Check if user is trying to overwrite a protected variable
                if key in protected_variables:  # If we find a match, exit with failure
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Error: You tried to overwrite protected variable '%s'. Please choose a different variable name."
                        % key,
                        3,
                    )
                    return "failed"

            # Good to proceed
            if list_name in shared_variables:
                shared_variables[list_name][key] = value

                # Try to get a pretty print.
                CommonUtil.prettify(key, value)

                CommonUtil.ExecLog(
                    sModuleInfo, "Saved variable:\n%s = %s" % (key, value), 0
                )
                return "passed"
            else:  # create dict if now available
                shared_variables[list_name] = collections.OrderedDict()
                shared_variables[list_name][key] = value

                # Try to get a pretty print.
                CommonUtil.prettify(key, value)

                CommonUtil.ExecLog(
                    sModuleInfo, "Saved variable:\n%s = %s" % (key, value), 0
                )
                return "passed"
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Append_List_Shared_Variables(key, value, protected=False, value_as_list=False):
    """ Creates and appends a python list variable """

    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        global shared_variables, protected_variables

        # Verify input
        key = key.strip()
        if not value_as_list:
            value = value.strip()
        if key == "":  # value can be empty
            return "failed"

        # Check if protected
        if protected:
            protected_variables.append(key)  # Add to list of protected variables
        else:  # Check if user is trying to overwrite a protected variable
            if key in protected_variables:  # If we find a match, exit with failure
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Error: You tried to overwrite protected variable '%s'. Please choose a different variable name."
                    % key,
                    3,
                )
                return "failed"

        # Create list if non-existent
        if not key in shared_variables:
            CommonUtil.ExecLog(sModuleInfo, "Creating new list", 0)
            shared_variables[key] = []

        if (
            key in shared_variables and shared_variables[key] == {}
        ):  # if initialized as a dict through "Initialize List" action, convert it to list
            shared_variables[key] = []

        # Append list
        shared_variables[key].append(value)
        CommonUtil.ExecLog(
            sModuleInfo,
            "Appending list %s with %s. Now is: %s"
            % (str(key), str(value), str(shared_variables[key])),
            0,
        )
        return "passed"

    except:
        CommonUtil.Exception_Handler(sys.exc_info())


@deprecated
def Append_Dict_Shared_Variables(key, value, protected=False, parent_dict=""):
    """ Creates and appends a python list variable """

    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        global shared_variables, protected_variables

        # Verify input
        key = key.strip()
        if key == "":
            return "failed"

        # Check if protected
        if protected:
            protected_variables.append(key)  # Add to list of protected variables
        else:  # Check if user is trying to overwrite a protected variable
            if key in protected_variables:  # If we find a match, exit with failure
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Error: You tried to overwrite protected variable '%s'. Please choose a different variable name."
                    % key,
                    3,
                )
                return "failed"

        if parent_dict == "":
            # Create list if non-existent
            if not key in shared_variables:
                CommonUtil.ExecLog(sModuleInfo, "Creating new dict", 0)
                shared_variables[key] = collections.OrderedDict()
            for k in value:
                # Append list
                shared_variables[key][k] = value[k]
        else:
            # Create list if non-existent
            if not parent_dict in shared_variables:
                CommonUtil.ExecLog(sModuleInfo, "Creating new dict", 0)
                shared_variables[parent_dict] = collections.OrderedDict()
            shared_variables[parent_dict][key] = value

        return "passed"

    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Get_Shared_Variables(key, log=True):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        global shared_variables
        if key == "" or key == None:  # if input is invalid
            return "failed"
        else:
            if key in shared_variables:
                value = shared_variables[key]
                # Try to get a pretty print.
                # CommonUtil.prettify(key, value)

                if log:
                    CommonUtil.ExecLog(
                        sModuleInfo, "Accessed variable:\n%s = %s" % (key, value), 0
                    )
                return value
            else:
                if log:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "No Such variable named '%s' found in shared variables" % key,
                        3,
                    )
                return "failed"
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Get_List_from_Shared_Variables(list_name):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        global shared_variables
        if list_name == "" or list_name == None:  # if input is invalid
            return "failed"
        else:
            if list_name in shared_variables:
                value = shared_variables[list_name]

                # Try to get a pretty print.
                # CommonUtil.prettify(list_name, value)

                CommonUtil.ExecLog(
                    sModuleInfo, "Accessed variable:\n%s = %s" % (list_name, value), 0
                )
                return value
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "List named %s does not exist on shared variables" % list_name,
                    3,
                )
                return "failed"
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Remove_From_Shared_Variables(key):
    """ Remove if a variable already exists and return the value or false """

    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        global shared_variables
        if key == "" or key == None:  # if input is invalid
            return "failed"
        else:  # Valid input
            return shared_variables.pop(key, "failed")
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Test_Shared_Variables(key):
    """ Test if a variable already exists and return true or false """

    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        global shared_variables
        if key == "" or key == None:  # if input is invalid
            return "failed"
        else:  # Valid input
            if key in shared_variables:  # Test if key/variable exists
                CommonUtil.ExecLog(sModuleInfo, "Variable %s exists" % key, 0)
                return True
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "No Such variable named '%s' found in shared variables" % key,
                    0,
                )
                return False
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Show_All_Shared_Variables():
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        global shared_variables
        if len(shared_variables) > 0:
            CommonUtil.ExecLog(sModuleInfo, "##Shared Variable Fields with Value##", 1)
            for each in shared_variables:
                CommonUtil.ExecLog(
                    sModuleInfo, "%s : %s" % (each, shared_variables[each]), 1
                )
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Handle_Step_Data_Variables(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        changed_step_data = []
        for dataset in step_data:
            changed_dataset = []
            for row in dataset:
                changed_row = []
                for each in row:
                    if each == True or each == False or each == "":
                        changed_row.append(each)
                    else:
                        if "|%" in each:
                            replaced_value = get_previous_response_variables_in_strings(
                                each
                            )
                            if replaced_value in failed_tag_list:
                                CommonUtil.ExecLog(
                                    sModuleInfo, "Step Data Format Not Appropriate", 3
                                )
                                return "failed"
                            else:
                                changed_row.append(replaced_value)
                        else:
                            changed_row.append(each)
                changed_dataset.append(changed_row)
            changed_step_data.append(changed_dataset)
        return changed_step_data
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def handle_nested_rest_json(result, string):
    if str(string).startswith("rest_response"):
        string = string[13:]
        splitted = string.split("[")
        indexes = []
        for each in splitted:
            if each != "":
                if "]" in each:
                    index = each.split("]")[0]
                    index = index.strip()
                    try:
                        int(index)
                        indexes.append(int(index))
                    except ValueError:
                        indexes.append(str(index))
                else:
                    return "failed"

        ans = result
        for each in indexes:
            try:
                ans = ans[each]
            except ValueError as e:
                return "failed"
        return ans

    else:
        return "failed"


class VariableParser:
    """Helper class for parsing the values of different indices as
          specified in [ ] square brackets of a variable.
    """

    @staticmethod
    def get_number(idx):
        try: return int(idx)
        except: return None
    

    @staticmethod
    def get_string(idx):
        if isinstance(idx, str):
            if idx[0] in ("'", '"'):
                return idx[1:len(idx)-1]

            return None
        return None

    
    @staticmethod
    def get_slice(idx):
        try:
            sp = idx.split(":")
            if len(sp) > 1:
                left, right = sp[0], sp[1]

                try: left = int(left)
                except: left = Get_Shared_Variables(left, log=False)

                try: right = int(right)
                except: right = Get_Shared_Variables(right, log=False)

                if "failed" in (left, right):
                    return None
                else:
                    left = int(left)
                    right = int(right)

                return (left, right)

        except: pass
        return None


    @staticmethod
    def get_variable(idx):
        val = Get_Shared_Variables(idx, log=False)
        return val if val != "failed" else None


def parse_variable(name):
    """Parses a given variable and returns its value.

    The variable can be indexed, similar to how Python's variables are
    indexed - lists and dictionaries with [ ] square brackets.

    If a tilde ~ character is specified in front of the variable name,
    then data collector is run, which collects data from a given
    pattern.

    Patterns:
    
        "_" (underscore) - match all list items.
        "*" (asterisk)   - match all values of dictionaries.
        "*xyz"           - partial match for dictionary keys ending with "xyz"
        "xyz*"           - partial match for dictionary keys starting with "xyz"

    Args:

        name: Variable name with indices specified if necessary.

    Examples:
        
        var
        var["hello"]
        var[hello] - Fetch hello from shared variables.
        var[3]
        var[2:5]
        var[left:right] - Fetch left and right from shared variables.
        var["hello"][3][2:5]

        var{_, *, occurrence, _, line}
        var{_, error*, occurrence, _, line}
        var{_, *error, occurrence, _, line}
        var{_, *, occurrence, _, message}
        var{0, error2, occurrence, 0, message}
        var{_, error1, type}{_, *, type} - Two patterns.
        var{pattern_1}{pattern_2}{pattern_3} - Three patterns.

        var(key1, key2) - Find 'key1' and 'key2' in the data and store their result.
        var(key1, key2)(key3, key4) - Two key patterns.


    Returns:

        Value of the variable at the given index (if specified).
    """

    try:
        # Pattern to match [] {} () brackets.
        pattern = r"[\[\{\(](.*?)[\)\}\]]"
        indices = re.findall(pattern, name)

        # For printing log.
        copy_of_name = name

        if len(indices) == 0:
            # If there are no [ ] style indexing.
            return Get_Shared_Variables(name)

        if "{" in name:
            # Data collector with pattern.
            # Match with the following pattern.
            # var_name{pattern1}{pattern2}{...}

            name = name[: name.find("{")]
            val = Get_Shared_Variables(name, log=False)
            result = []

            for idx in indices:
                result.append(data_collector.collect(idx, val, "pattern"))

            if len(indices) > 1:
                result = list(zip(*result))
            elif len(indices) == 1:
                result = result[0]

            # Print to console.
            CommonUtil.prettify(copy_of_name, result)
            return result
        elif "(" in name:
            # Data collector with keys.
            # Match with the following pattern.
            # var_name(pattern1)(pattern2)(...)

            name = name[: name.find("(")]
            val = Get_Shared_Variables(name, log=False)
            result = []

            for idx in indices:
                result.append(data_collector.collect(idx, val, "key"))

            if len(indices) == 1:
                result = result[0]

            CommonUtil.prettify(copy_of_name, result)
            return result
        elif "[" in name:
            # Otherwise, perform variable indexing.
            # var_name["abc"][xyz][3][2:5]
            
            # Get the variable name part, not the indices with [ ]
            name = name[: name.find("[")]

            # Get the root of the variable.
            val = Get_Shared_Variables(name, log=False)

            if isinstance(val, str):
                val = CommonUtil.parse_value_into_object(val)

            for idx in indices:
                _number     = VariableParser.get_number(idx)
                _string     = VariableParser.get_string(idx)
                _variable   = VariableParser.get_variable(idx)
                _slice      = VariableParser.get_slice(idx)

                if _number is not None:
                    val = val[_number]
                elif _string is not None:
                    val = val[_string]
                elif _variable is not None:
                    val = val[_variable]
                elif _slice is not None:
                    left, right = _slice
                    val = val[left:right]

            # Print to console.
            CommonUtil.prettify(copy_of_name, val)
            return val
    except:
        print("Failed to parse variable")
        return "failed"


def get_previous_response_variables_in_strings(step_data_string_input):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        changed = False
        input = step_data_string_input
        all_parse = input.split("%|")
        output = ""
        for each in all_parse:
            if "|%" in each:
                changed = True
                parts = each.split("|%")

                if str(parts[0]).startswith("random_data"):
                    full_string = str(parts[0])
                    random_string = ""
                    if "(" in full_string:
                        temp = full_string.split("(")
                        params = temp[1].split(")")[0]
                        if isinstance(CommonUtil.parse_value_into_object(params.strip()), list):
                            random_string = str(random.choice(CommonUtil.parse_value_into_object(params.strip())))
                        elif re.search("^\s*\d+\s*-{1}\s*\d+\s*$", params):
                            start, end = params.replace(" ", "").split("-")
                            random_string = str(random.randrange(int(start), int(end), 1))
                        elif "," in params:
                            list_of_params = params.split(",")
                            random_string = random_string_generator(
                                list_of_params[0].strip(),
                                int(list_of_params[1].strip()),
                            )
                        else:
                            if params.strip() == "":
                                random_string = random_string_generator()
                            else:
                                random_string = random_string_generator(params.strip())

                    else:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            'Wrong format provided. The correct for %|random_data()|% is below\n' +
                            '%|random_data( [False , "a", True] )|%\n%|random_string(100-200)|%',
                            3,
                        )
                        return "failed"

                    if random_string in failed_tag_list:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            'Wrong format provided. The correct for %|random_data()|% is below\n' +
                            '%|random_data([False,"a",True])|%\n%|random_string(100-200)|%',
                            3,
                        )
                        return "failed"

                    output += random_string
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        'Replacing variable "%s" with its value "%s"'
                        % (parts[0], random_string),
                        0,
                    )
                elif str(parts[0]).startswith("random_string"):
                    CommonUtil.ExecLog(
                        "",
                        '%|random_string()|% is deprecated and will be deleted soon. Use %|random_data()|% to get updated features',
                        2
                    )
                    full_string = str(parts[0])
                    random_string = ""
                    if "(" in full_string:
                        temp = full_string.split("(")
                        params = temp[1].split(")")[0]
                        if "," in params:
                            list_of_params = params.split(",")
                            random_string = random_string_generator(
                                list_of_params[0].strip(),
                                int(list_of_params[1].strip()),
                            )
                        else:
                            if params.strip() == "":
                                random_string = random_string_generator()
                            else:
                                random_string = random_string_generator(params.strip())
                    else:
                        return "failed"

                    if random_string in failed_tag_list:
                        return "failed"

                    output += random_string
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        'Replacing variable "%s" with its value "%s"'
                        % (parts[0], random_string),
                        0,
                    )
                elif str(parts[0]).startswith("rest_response"):
                    full_string = str(parts[0])
                    result_json = Get_Shared_Variables("rest_response")
                    if result_json in failed_tag_list:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "No such variable named 'rest_response' in shared variables list",
                            3,
                        )
                        return "failed"
                    rest_json_output = handle_nested_rest_json(
                        result_json, str(parts[0])
                    )
                    if rest_json_output in failed_tag_list:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Json indexes are not provided correctly for run_response",
                            3,
                        )
                        return "failed"
                    output += str(rest_json_output)
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        'Replacing variable "%s" with its value "%s"'
                        % (parts[0], rest_json_output),
                        0,
                    )
                elif str(parts[0]).lower().startswith("today") or str(
                    parts[0]
                ).startswith("currentEpochTime"):
                    replaced_string = save_built_in_time_variable(str(parts[0]))
                    if replaced_string in failed_tag_list:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "No such date variable named '%s', user formats like %%|today|%% , %%|today + 1d|%% , %%|today - 3m|%% , %%|today + 1w|%%, %%|today + 2y|%% , %%|currentEpochTime|%% etc."
                            % parts[0],
                            3,
                        )
                        return "failed"
                    output += str(save_built_in_time_variable(str(parts[0])))
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        'Replacing variable "%s" with its value "%s"'
                        % (parts[0], replaced_string),
                        0,
                    )

                elif str(parts[0]).startswith("random_number_in_range"):
                    full_string = str(parts[0])
                    if "(" in full_string:
                        temp = full_string.split("(")
                        params = temp[1].split(")")[0]
                        if "," in params:
                            list_of_params = params.split(",")
                        if len(list_of_params) > 2:
                            return "failed"
                        else:
                            random_string = str(
                                random.randint(
                                    int(list_of_params[0]), int(list_of_params[1])
                                )
                            )
                    else:
                        return "failed"

                    output += random_string
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        'Replacing variable "%s" with its value "%s"'
                        % (parts[0], random_string),
                        0,
                    )

                elif str(parts[0]).startswith("pick_random_element"):
                    full_string = str(parts[0])
                    if "(" in full_string:
                        temp = full_string.split("(")
                        params = temp[1].split(")")[0]
                        if "," in params:
                            list_of_params = params.split(",")
                            rand_str = list_of_params[
                                random.randint(0, len(list_of_params) - 1)
                            ]
                        else:
                            rand_str = params

                    else:
                        return "failed"
                    if len(params) == 0:
                        return "failed"

                    output += rand_str
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        'Replacing variable "%s" with its value "%s"'
                        % (parts[0], rand_str),
                        0,
                    )

                else:
                    var_value = parse_variable(parts[0])
                    if var_value == "failed":
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "No such variable named '%s' in shared variables list"
                            % parts[0],
                            3,
                        )
                        return "failed"
                    else:
                        output += str(var_value)
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            'Replacing variable "%s" with its value "%s"'
                            % (parts[0], var_value),
                            0,
                        )
                output += parts[1]
            else:
                output += each
        if changed == True:
            CommonUtil.ExecLog(
                sModuleInfo, "Input string is changed by variable substitution", 0
            )
            CommonUtil.ExecLog(sModuleInfo, "Input string before change: %s" % input, 0)
            CommonUtil.ExecLog(sModuleInfo, "Input string after change: %s" % output, 0)

        return output

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def random_string_generator(pattern="nluc", size=10):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function: random string generator", 0)
    try:
        pattern = pattern.lower().strip()
        punctuation = "`~!@#$%^&."
        chars = ""
        for index in range(0, len(pattern)):
            if pattern[index] == "n":
                chars += string.digits
            if pattern[index] == "l":
                chars += string.ascii_lowercase
            if pattern[index] == "u":
                chars += string.ascii_uppercase
            if pattern[index] == "c":
                chars += punctuation

        if chars == "":
            return "failed"
        else:
            return "".join(random.choice(chars) for _ in range(size))
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Validating text from an element given information regarding the expected text
def Compare_Variables(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Variables", 0)
    try:
        pass_count = 0
        fail_count = 0
        variable_list1 = []
        variable_list2 = []
        result = []
        modifier = False
        for each_step_data_item in step_data[0]:
            if (
                each_step_data_item[1] == "compare"
                or each_step_data_item[1] == "element parameter"
                or "parameter" in each_step_data_item[1]
            ):
                if "%|" in each_step_data_item[0].strip():
                    previous_name = each_step_data_item[0].strip()
                    new_name = get_previous_response_variables_in_strings(
                        each_step_data_item[0].strip()
                    )
                    tuple1 = ("Variable", "'%s'" % previous_name, new_name)
                else:
                    tuple1 = ("Text", "", each_step_data_item[0].strip())
                variable_list1.append(tuple1)

                if "%|" in each_step_data_item[2].strip():
                    previous_name = each_step_data_item[2].strip()
                    new_name = get_previous_response_variables_in_strings(
                        each_step_data_item[2].strip()
                    )
                    tuple2 = ("Variable", "'%s'" % previous_name, new_name)
                else:
                    tuple2 = ("Text", "", each_step_data_item[2].strip())
                variable_list2.append(tuple2)
            elif each_step_data_item[1] == "action":  # Action line
                if each_step_data_item[2].strip().lower() == "is in":
                    CommonUtil.ExecLog(
                        sModuleInfo, "Using 'is in' instead of exact match", 1
                    )
                    modifier = True  # Changes how we compare

        for i in range(0, len(variable_list1)):
            if (
                modifier == False
                and variable_list1[i][2].strip() == variable_list2[i][2].strip()
            ):  # Straight up compare
                result.append(True)
                pass_count += 1
            elif (
                modifier and variable_list1[i][2] in variable_list2[i][2]
            ):  # Var 1 is IN var 2, if modifier set
                result.append(True)
                pass_count += 1
            elif (
                modifier and variable_list2[i][2] in variable_list1[i][2]
            ):  # Var 2 is IN var 1 (Whichever way the user made it), if modifier set
                result.append(True)
                pass_count += 1
            else:
                result.append(False)
                fail_count += 1

        CommonUtil.ExecLog(sModuleInfo, "### Variable Comparison Results ###", 1)
        CommonUtil.ExecLog(sModuleInfo, "Matched Variables: %d" % pass_count, 1)
        CommonUtil.ExecLog(sModuleInfo, "Not Matched Variables: %d" % fail_count, 2)

        for i in range(0, len(variable_list1)):
            if result[i] == True:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Item %d. %s %s - %s :: %s %s - %s : Matched"
                    % (
                        i + 1,
                        variable_list1[i][0],
                        variable_list1[i][1],
                        variable_list1[i][2],
                        variable_list2[i][0],
                        variable_list2[i][1],
                        variable_list2[i][2],
                    ),
                    1,
                )
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Item %d. %s %s - %s :: %s %s - %s : Not Matched"
                    % (
                        i + 1,
                        variable_list1[i][0],
                        variable_list1[i][1],
                        variable_list1[i][2],
                        variable_list2[i][0],
                        variable_list2[i][1],
                        variable_list2[i][2],
                    ),
                    3,
                )

        if fail_count > 0:
            CommonUtil.ExecLog(
                sModuleInfo, "Error: %d item(s) did not match" % fail_count, 3
            )
            return "failed"
        else:
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Validating partial text from an element given information regarding the expected text


def Compare_Partial_Variables(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Partial_Variables", 0)
    try:
        pass_count = 0
        fail_count = 0
        variable_list1 = []
        variable_list2 = []
        result = []
        # modifier = False
        for each_step_data_item in step_data[0]:
            if (
                each_step_data_item[1] == "compare"
                or each_step_data_item[1] == "element parameter"
                or "parameter" in each_step_data_item[1]
            ):
                if "%|" in each_step_data_item[0].strip():
                    previous_name = each_step_data_item[0].strip()
                    new_name = get_previous_response_variables_in_strings(
                        each_step_data_item[0].strip()
                    )
                    tuple1 = ("Variable", "'%s'" % previous_name, new_name)
                else:
                    tuple1 = ("Text", "", each_step_data_item[0].strip())
                variable_list1.append(tuple1)

                if "%|" in each_step_data_item[2].strip():
                    previous_name = each_step_data_item[2].strip()
                    new_name = get_previous_response_variables_in_strings(
                        each_step_data_item[2].strip()
                    )
                    tuple2 = ("Variable", "'%s'" % previous_name, new_name)
                else:
                    tuple2 = ("Text", "", each_step_data_item[2].strip())
                variable_list2.append(tuple2)

        for i in range(0, len(variable_list1)):
            if (
                variable_list1[i][2] in variable_list2[i][2]
            ):  # Var 1 is IN var 2, if modifier set
                result.append(True)
                pass_count += 1
            elif (
                variable_list2[i][2] in variable_list1[i][2]
            ):  # Var 2 is IN var 1 (Whichever way the user made it), if modifier set
                result.append(True)
                pass_count += 1
            else:
                result.append(False)
                fail_count += 1

        CommonUtil.ExecLog(sModuleInfo, "###Variable Comparison Results###", 1)
        CommonUtil.ExecLog(sModuleInfo, "Matched Partial Variables: %d" % pass_count, 1)
        CommonUtil.ExecLog(sModuleInfo, "Not Matched Variables: %d" % fail_count, 1)

        for i in range(0, len(variable_list1)):
            if result[i] == True:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Item %d. %s %s - %s :: %s %s - %s : Matched"
                    % (
                        i + 1,
                        variable_list1[i][0],
                        variable_list1[i][1],
                        variable_list1[i][2],
                        variable_list2[i][0],
                        variable_list2[i][1],
                        variable_list2[i][2],
                    ),
                    1,
                )
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Item %d. %s %s - %s :: %s %s - %s : Not Matched"
                    % (
                        i + 1,
                        variable_list1[i][0],
                        variable_list1[i][1],
                        variable_list1[i][2],
                        variable_list2[i][0],
                        variable_list2[i][1],
                        variable_list2[i][2],
                    ),
                    3,
                )

        if fail_count > 0:
            CommonUtil.ExecLog(
                sModuleInfo, "Error: %d item(s) did not match" % fail_count, 3
            )
            return "failed"
        else:
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Validating text from an element given information regarding the expected text
def Compare_Lists_or_Dicts(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Lists", 0)
    try:
        pass_count = 0
        fail_count = 0
        extra_count = 0
        variable_list1 = []
        variable_list2 = []
        result = []
        taken = []
        list1_name = ""
        list2_name = ""
        ignore_extra = True
        both_list = False
        match_by_index = False
        check_exclusion = False

        for each_step_data_item in step_data[0]:
            if (
                each_step_data_item[1] == "compare"
                or each_step_data_item[1] == "element parameter"
                or "parameter" in each_step_data_item[1]
            ):
                list1_name = each_step_data_item[0]
                list2_name = each_step_data_item[2]
            if each_step_data_item[1] == "action":
                action_type = str(each_step_data_item[2]).lower().strip()
                if action_type.startswith("exact match"):
                    ignore_extra = False
                if action_type.startswith("match by index"):
                    match_by_index = True
                if action_type.startswith("excludes"):
                    check_exclusion = True

        if list1_name == "" or list2_name == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Error parsing data set. Expected Field and Value fields to be set",
                3,
            )
            return "failed"

        list1 = Get_List_from_Shared_Variables(list1_name)
        list2 = Get_List_from_Shared_Variables(list2_name)

        if list1 in failed_tag_list or list2 in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Error converting Shared Variable in Field or Value fields to strings",
                3,
            )
            return "failed"

        found_list = []
        not_found_list1 = []
        not_found_list2 = []

        if isinstance(list1, list) and isinstance(
            list2, list
        ):  # if both are list not dict
            both_list = True
            variable_list1 = list1
            variable_list2 = list2

            if check_exclusion:
                for each in list2:
                    if each in list1:
                        found_list.append(each)
            elif not match_by_index:
                for each in list1:
                    if each in list2:
                        found_list.append(each)
                        pass_count += 1
                    else:
                        not_found_list1.append(each)
                        fail_count += 1

                for each in list2:
                    if each not in list1:
                        not_found_list2.append(each)
            else:
                for cnt in range(len(list1)):
                    if list1[cnt] == list2[cnt]:
                        found_list.append(list1[cnt])
                        pass_count += 1
                    else:
                        not_found_list2.append(list1[cnt])
                        not_found_list1.append(list2[cnt])
                        fail_count += 1

        else:  # if both are dict
            for key in list1:
                if key in list2:
                    if key not in taken:
                        new_tuple = (key, list1[key])
                        variable_list1.append(new_tuple)
                        new_tuple = (key, list2[key])
                        variable_list2.append(new_tuple)
                        taken.append(key)
                        if (
                            str(list1[key]).lower().strip()
                            == str(list2[key]).lower().strip()
                        ):
                            pass_count += 1
                            result.append("pass")
                        else:
                            fail_count += 1
                            result.append("fail")
                else:
                    if key not in taken:
                        new_tuple = (key, list1[key])
                        variable_list1.append(new_tuple)
                        new_tuple = (key, "N/A")
                        variable_list2.append(new_tuple)
                        extra_count += 1
                        result.append("extra")
                        taken.append(key)

            for key in list2:
                if key in list1:
                    if key not in taken:
                        new_tuple = (key, list1[key])
                        variable_list1.append(new_tuple)
                        new_tuple = (key, list2[key])
                        variable_list2.append(new_tuple)
                        taken.append(key)
                        if (
                            str(list1[key]).lower().strip()
                            == str(list2[key]).lower().strip()
                        ):
                            pass_count += 1
                            result.append("pass")
                        else:
                            fail_count += 1
                            result.append("fail")
                else:
                    if key not in taken:
                        new_tuple = (key, "N/A")
                        variable_list1.append(new_tuple)
                        new_tuple = (key, list2[key])
                        variable_list2.append(new_tuple)
                        extra_count += 1
                        result.append("extra")
                        taken.append(key)

        if check_exclusion:
            if len(found_list) > 0:
                CommonUtil.ExecLog(
                    sModuleInfo, "Match found for items: %s" % found_list, 3
                )
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "No match found", 1)
                return "passed"

        CommonUtil.ExecLog(
            sModuleInfo,
            "###Comparison Results of List '%s' and List '%s'###"
            % (list1_name, list2_name),
            1,
        )
        CommonUtil.ExecLog(sModuleInfo, "Matched Variables: %d" % pass_count, 1)
        CommonUtil.ExecLog(sModuleInfo, "Not Matched Variables: %d" % fail_count, 1)
        CommonUtil.ExecLog(sModuleInfo, "Extra Variables: %d" % extra_count, 1)

        if not both_list:
            for i in range(0, len(variable_list1)):
                if result[i] == "pass":
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Item %d. Variable Name : %s :: %s - %s : Matched"
                        % (
                            i + 1,
                            variable_list1[i][0],
                            variable_list1[i][1],
                            variable_list2[i][1],
                        ),
                        1,
                    )
                elif result[i] == "fail":
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Item %d. Variable Name : %s :: %s - %s : Not Matched"
                        % (
                            i + 1,
                            variable_list1[i][0],
                            variable_list1[i][1],
                            variable_list2[i][1],
                        ),
                        3,
                    )
                else:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Item %d. Variable Name : %s :: %s - %s : Extra"
                        % (
                            i + 1,
                            variable_list1[i][0],
                            variable_list1[i][1],
                            variable_list2[i][1],
                        ),
                        2,
                    )
        else:
            count = len(found_list)
            for i in range(0, len(found_list)):
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Item %d. Matched Element: '%s' found in both list '%s' and list '%s'"
                    % (i + 1, found_list[i], list1_name, list2_name),
                    1,
                )
            for i in range(0, len(not_found_list1)):
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Item %d. Not Matched Element: '%s' found in list '%s' but not in list '%s'"
                    % (count + i + 1, not_found_list1[i], list1_name, list2_name),
                    3,
                )
            count += len(not_found_list1)
            for i in range(0, len(not_found_list2)):
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Item %d. Not Matched Element: '%s' found in list '%s' but not in list '%s'"
                    % (count + i + 1, not_found_list2[i], list2_name, list1_name),
                    3,
                )
        if fail_count > 0:
            CommonUtil.ExecLog(
                sModuleInfo, "Error: %d item(s) did not match" % fail_count, 3
            )
            return "failed"
        else:
            if extra_count > 0 and ignore_extra == False:
                CommonUtil.ExecLog(
                    sModuleInfo, "Error: %d item(s) extra found" % extra_count, 3
                )
                return "failed"
            else:
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to initialize an empty list
def Initialize_List(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function: Initialize_List", 0)
    try:
        if len(step_data) != 1:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Error parsing data set. Too many rows. Expected only the action row.",
                3,
            )
            return "failed"
        else:
            list_name = str(step_data[0][0][2]).lower().strip()
            new_list = []
            result = Set_Shared_Variables(list_name, new_list)
            if result in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Could not initialize empty list named %s" % list_name,
                    3,
                )
                return "failed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully initialized empty list named %s" % list_name,
                    0,
                )
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


##Method to randomize a given list
def Randomize_List(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function: Randomize_List", 0)
    try:
        if len(step_data) != 1:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Error parsing data set. Too many rows. Expected only the action row.",
                3,
            )
            return "failed"
        else:
            original_list_name = str(step_data[0][0][2]).lower().strip()
            if not Test_Shared_Variables(original_list_name):
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "List named '%s' is not found in shared variable"
                    % original_list_name,
                    3,
                )
            original_list = Get_Shared_Variables(original_list_name)
            randomized_list = random.sample(original_list, len(original_list))
            result = Set_Shared_Variables(original_list_name, randomized_list)
            if result in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo, "Could not randomize list named %s" % original_list, 3
                )
                return "failed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully randomized list named %s" % original_list,
                    0,
                )
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to initialize an empty dict
def Initialize_Dict(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function: Initialize_List", 0)
    try:
        if len(step_data) != 1:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Error parsing data set. Too many rows. Expected only the action row.",
                3,
            )
            return "failed"
        else:
            list_name = str(step_data[0][0][2]).lower().strip()
            new_list = collections.OrderedDict()
            result = Set_Shared_Variables(list_name, new_list)
            if result in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Could not initialize empty dict named %s" % list_name,
                    3,
                )
                return "failed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully initialized empty dict named %s" % list_name,
                    0,
                )
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def Clean_Up_Shared_Variables():
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function: clean up shared variables", 0)
    try:
        global shared_variables
        shared_variables = {}
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def Shared_Variable_Export():
    """ Exports all shared variables if for some reason modules can't use the functions herein """
    return shared_variables


def save_built_in_time_variable(string):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:

        sign = ""
        number = 0
        parameter = ""

        datetime_format = "%Y-%m-%d"

        if "(" in string:
            splitted_list = string.split("(")
            string = splitted_list[0]
            datetime_format_user_input = splitted_list[1].split(")")[0]
            datetime_format = generate_datetime_format(datetime_format_user_input)

        input = str(string).lower().strip()

        if input == "currentepochtime":
            return int(time.time())
        elif input.startswith("today"):
            if input.lower().strip() == "today":
                return datetime.today().strftime(datetime_format)
            elif "+" in input:
                l = input.split("+")
                if len(l) > 2:  # problem with input
                    return "failed"
                else:
                    sign = "plus"
                    st = str(l[1]).strip()
                    parameter = st[-1]
                    number = int(st[:-1])
            elif "-" in input:
                l = input.split("-")
                if len(l) > 2:  # problem with input
                    return "failed"
                else:
                    sign = "minus"
                    st = str(l[1]).strip()
                    parameter = st[-1]
                    number = int(st[:-1])
            else:
                return "failed"

            if sign != "" and parameter != "":
                if sign == "minus":
                    number *= -1
                if parameter == "d":
                    return (datetime.today() + relativedelta(days=number)).strftime(
                        datetime_format
                    )
                elif parameter == "w":
                    return (datetime.today() + relativedelta(days=number * 7)).strftime(
                        datetime_format
                    )
                elif parameter == "m":
                    return (datetime.today() + relativedelta(months=number)).strftime(
                        datetime_format
                    )
                elif parameter == "y":
                    return (datetime.today() + relativedelta(years=number)).strftime(
                        datetime_format
                    )
                else:
                    return "failed"
    except Exception as e:
        return CommonUtil.Exception_Handler(
            sys.exc_info(),
            UserMessage="Invalid Date Format, Error: %s Please Read the Action Help"
            % e,
        )


def generate_datetime_format(string):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        datetime_format = string

        datetime_format.strip()
        datetime_format = datetime_format.replace("MMM", "%b")
        datetime_format = datetime_format.replace("DD", "%d")
        datetime_format = datetime_format.replace("MM", "%m")
        datetime_format = datetime_format.replace("YYYY", "%Y")
        datetime_format = datetime_format.replace("YY", "%y")
        datetime_format = datetime_format.replace("HH", "%H")
        datetime_format = datetime_format.replace("hh", "%I")
        datetime_format = datetime_format.replace("mm", "%M")
        datetime_format = datetime_format.replace("SS", "%S")

        return datetime_format
    except Exception:
        CommonUtil.ExecLog(
            sModuleInfo,
            "Invalid datetime format, using the deafult '%Y-%m-%d' format",
            2,
        )
        return "%Y-%m-%d"
