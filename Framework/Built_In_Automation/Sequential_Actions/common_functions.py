"""
    Common Functions
    Function: Contains functions common to all modules, and helper functions for Sequential Actions

    Caveat: Functions common to multiple Built In Functions must have action names that are unique, because we search the common functions first, regardless of the module name passed by the user
"""

import inspect, sys, time, collections, ftplib, os, ast, copy, csv, yaml
from pathlib import Path
from imap_tools import MailBox
import re
from typing import List

try:
    import xlwings as xw
except:
    pass
global sr
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from Framework.Built_In_Automation.Sequential_Actions.sequential_actions import (
    actions,
    action_support,
)
from Framework.Utilities.CommonUtil import (
    passed_tag_list,
    failed_tag_list,
    skipped_tag_list,
)  # Allowed return strings, used to normalize pass/fail
from Framework.Utilities.decorators import logger, deprecated
from Framework.Built_In_Automation.Shared_Resources import LocateElement
from Framework import MainDriverApi
from Framework.Utilities import FileUtilities
import datetime, random
import datefinder
import traceback
import json
from datetime import timedelta
from .utility import send_email, check_latest_received_email, delete_mail, save_mail
import re

months = [
    "Unknown",
    "January",
    "Febuary",
    "March",
    "April",
    "May",
    "Jun",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

unmask_characters = {
    "{{1}}": "(",
    "{{2}}": ")",
    "{{3}}": "[",
    "{{4}}": "]",
    "{{5}}": ",",
    "{{6}}": "#",
    "{{7}}": "'",
    "{{8}}": "%",
    "{{9}}": "|",
}

programming_logic_keywords = ["if else", "while loop", "for loop", "loop settings"]


MODULE_NAME = inspect.getmodulename(__file__)


def unmask_string(givenText):
    for e in list(unmask_characters.keys()):
        givenText = givenText.replace(e, unmask_characters[e])
    return givenText


def unmask_step_data(step_data):
    """
    unmasks the special characters sent from servers
    :param step_data:
    :return: new step data
    """
    try:
        new_step_data = []  # Create empty list that will contain the data sets
        for data_set in step_data:  # For each data set within step data
            new_data_set = []  # Create empty list that will have new data appended
            for row in data_set:  # For each row of the data set
                new_row = []
                for each in row:
                    new_row.append(unmask_string(each))
                new_data_set.append(
                    tuple(new_row)
                )  # Append list as tuple to data set list
            new_step_data.append(new_data_set)  # Append data set to step data
        return new_step_data  # Step data is now clean and in the same format as it arrived in
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def sanitize(step_data):
    """ Sanitize step data Field and Sub-Field """
    """ Usage:
            Is to be used to allow users flexibility in their step data input, but allow the program to find key words
            :valid_chars: By default this function removes all characters. Specifying a string of characters here will skip removing them
            :clean_whitespace_only: If your function uses several characters, you can set this to True, to only clean up white space
            If the user surrounds their input with double quotes, all sanitizing will be skipped, and the surrounding quotes will be removed
    """

    try:
        # Set columns in the step data to sanitize (default is Field and Sub-Field only)
        column = [0, 1, 2]

        # Invalid character list (space and underscore hare handle separately)
        invalid_chars = "!\"#$%&'()*+,-./:;<=>?@[\]^`{|}~"

        # Adjust invalid character list, based on function input

        new_step_data = []  # Create empty list that will contain the data sets
        for data_set in step_data:  # For each data set within step data
            new_data_set = []  # Create empty list that will have new data appended
            for row in data_set:  # For each row of the data set
                new_row = list(row)  # Copy tuple of row as list, so we can change it
                # for i in column:  # Sanitize the specified columns
                #     if (
                #         str(new_row[i])[:1] == '"' and str(new_row[i])[-1:] == '"'
                #     ):  # String is within double quotes, indicating it should not be changed
                #         # new_row[i] = str(new_row[i])[
                #         #     1 : len(new_row[i]) - 1
                #         # ]  # Remove surrounding quotes
                #         continue  # Do not change string

                    # new_row[i] = new_row[i].replace("  ", " ")  # Double space to single space
                    # new_row[i] = new_row[i].strip()  # Remove leading and trailing whitespace
                new_data_set.append(
                    tuple(new_row)
                )  # Append list as tuple to data set list
            new_step_data.append(new_data_set)  # Append data set to step data
        return new_step_data  # Step data is now clean and in the same format as it arrived in
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def verify_step_data(step_data):
    """ Verify step data is valid """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        data_set_index = 0
        for data_set in step_data:
            data_set_index += 1
            module_test = False
            field_text = False

            # Check each data set
            if len(data_set) == 0:
                CommonUtil.ExecLog(
                    sModuleInfo, "Data set %d cannot be empty" % data_set_index, 3
                )
                return "zeuz_failed"

            # Check each row
            action = False  # used to ensure there is an action for each data set
            for row in data_set:
                if len(row[0]) == 0:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Field for data set %d cannot empty: %s"
                        % (data_set_index, str(row)),
                        3,
                    )
                    return "zeuz_failed"
                elif len(row[1]) == 0:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Sub-Field for data set %d cannot empty: %s"
                        % (data_set_index, str(row)),
                        3,
                    )
                    return "zeuz_failed"
                elif (
                    str(row[1]).lower().strip() not in action_support
                ):  # Check against list of allowed Sub-Fields
                    if (
                        "action" not in row[1]
                        and str(row[1]).strip().lower()
                        not in programming_logic_keywords
                    ):  #!!! Temporary until module handling is all moved into it's own function
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Sub-Field for data set %d contains invalid data: %s"
                            % (data_set_index, str(row)),
                            3,
                        )
                        return "zeuz_failed"

                # Make sure Sub-Field has a module name
                if "action" in row[1]:  # Only apply to actions rows
                    action = True
                    if "custom" in row[1] or "conditional" in row[1] or "loop action":
                        continue  # Skip custom actions - they do not require a module
                    for action_index in actions:
                        if (
                            actions[action_index]["module"] in row[1]
                        ):  # If one of the modules is in the Sub-Field
                            module_name = actions[action_index][
                                "module"
                            ]  # Save this for the "Field" check below
                            module_test = True  # Flag it's good
                            break
                    if module_test == False:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Sub-Field for data set %d is missing a module name: %s"
                            % (data_set_index, str(row)),
                            3,
                        )
                        return "zeuz_failed"

                # Make sure Field has a valid action call
                if (
                    "action" in row[1]
                ):  # Loop action, do not check because there could be different formats
                    continue
                elif str(row[1]).lower().strip() in programming_logic_keywords:
                    action = True
                    continue
                elif (
                    "custom" in row[1]
                ):  # Skip custom actions - they do not execute like other actions
                    continue
                elif (
                    "action" in row[1] and "conditional" not in row[1]
                ):  # Only apply to actions rows
                    for action_index in actions:
                        if (
                            (
                                actions[action_index]["name"] == row[0]
                                and actions[action_index]["module"] == module_name
                            )
                            or (
                                actions[action_index]["name"] == row[0]
                                and actions[action_index]["module"] == "common"
                            )
                            or str(row[0]).startswith("%|")
                        ):  # If one of the action names in the Field
                            field_text = True  # Flag it's good
                            break
                    if field_text == False:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Field for data set %d contains invalid data: %s"
                            % (data_set_index, str(row)),
                            3,
                        )
                        return "zeuz_failed"

                # Make sure recall result row contains valid commands and shared variables
                elif row[1] == "result":
                    if row[0].strip().lower() not in ("store", "recall"):
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Field for data set %d contains invalid data: %s - expected either 'recall' or 'store'"
                            % (data_set_index, str(row)),
                            3,
                        )
                        return "zeuz_failed"
                    elif (
                        row[0].strip().lower() == "recall"
                        and "%|" not in row[2].strip()
                    ):
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Field for data set %d contains invalid data: %s - expected Shared Variable in the proper format. Eg: %%|VAR|%%"
                            % (data_set_index, str(row)),
                            3,
                        )
                        return "zeuz_failed"

            # Make sure each data set has an action row
            if action == False:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Data set %d is missing an action line, or it's misspelled"
                    % data_set_index,
                    3,
                )
                return "zeuz_failed"

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def check_action_types(module, step_data):
    """ Check for a specific module in the step data type and return true/false """
    # To be used when we don't have a dependency, and need to know the type of actions the user have specified

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    for data_set in step_data:
        for row in data_set:
            subfield = row[1].lower()
            if module in subfield:
                return True
    return False


def adjust_element_parameters(step_data, platforms):
    """ Strip out element parameters that do not match the dependency """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Get saved dependency and verify if we have the correct dependency
    if sr.Test_Shared_Variables("dependency") == False:  # No dependency at all
        if check_action_types("Mobile", step_data) == True:
            CommonUtil.ExecLog(
                sModuleInfo,
                "No dependency set - functions may not work properly if step data contains platform names",
                3,
            )
            return "zeuz_failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Not a mobile Test Case", 0)
            return step_data  # Return unmodified
    else:  # Have dependency
        dependency = sr.Get_Shared_Variables("dependency")  # Save locally
        if "Mobile" not in dependency:  # We have a dependency, but not a mobile, so we don't need to do anything
            if check_action_types("Mobile", step_data) == False:  # No mobile actions in step data
                CommonUtil.ExecLog(sModuleInfo, "Not a mobile Test Case", 0)
                return step_data
            else:  # Mobile actions in step data
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Mobile (Appium) actions found in Step Data, but no Mobile dependency set",
                    3,
                )
                return "zeuz_failed"  # Return unmodified

    new_step_data = []  # Create empty list that will contain the data sets
    for data_set in step_data:  # For each data set within step data
        new_data_set = []  # Create empty list that will have new data appended
        for row in data_set:  # For each row of the data set
            new_row = list(row)  # Copy tuple of row as list, so we can change it

            # Special handling of "id"
            for id_adj_row in data_set:  # Find if this is an appium test step
                if "appium" in id_adj_row[1]:  # Yes, so adjust
                    if new_row[0] == "id" and dependency["Mobile"].lower() == "android":  # If user specifies id, they likely mean "resource-id"
                        new_row[0] = "resource-id"
                        new_row[2] = "*" + new_row[2]
                    elif new_row[0] == "id" and dependency["Mobile"].lower() == "ios":
                        new_row[0] = "accessibility id"  # If user specifies id, they likely mean "resource-id"
                    elif new_row[0] == "text or name" and dependency["Mobile"].lower() == "android":  # If user specifies id, they likely mean "resource-id"
                        new_row[0] = "text"
                    elif new_row[0] == "text or name" and dependency["Mobile"].lower() == "ios":
                        new_row[0] = "name"  # If user specifies id, they likely mean "resource-id"

            # Remove any element parameter that doesn't match the dependency
            if dependency["Mobile"].lower() in new_row[1]:  # If dependency matches this Sub-Field, then save it
                new_row[1] = (
                    new_row[1]
                    .replace(dependency["Mobile"].lower(), "")
                    .replace("  ", " ")
                    .strip()
                )  # Remove word and clean up spaces
                new_data_set.append(tuple(new_row))  # Append list as tuple to data set list
            else:  # This dependency doesn't match. Figure out if this is an element parameter we don't want, or any other row we do want
                b = False
                for p in platforms:  # For each platform
                    if p in new_row[1]:  # If one of the platforms matches (we already found the one we want above, so this is for anything we don't want), then we don't want it
                        b = True
                if b == False:  # This row did not match unwanted platforms, so we keep it
                    new_data_set.append(tuple(new_row))  # Append list as tuple to data set list

        new_step_data.append(new_data_set)  # Append data set to step data

    return new_step_data  # Return cleaned step_data that contains only the element paramters we are interested in


def get_module_and_function(action_name, action_sub_field):
    """ Function to split module from the action name, and with the action name tries to find the corrosponding function name """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    function = ""
    module = ""
    try:
        action_list = action_sub_field.split(
            " "
        )  # Split sub-field, so we can get moudle name from step data
        if len(action_list) > 1:  # Should be at least two words in the sub-field
            # Find the function matching the module (decide later if we need it or not)
            for item in action_list:  # Loop through split string
                for action_index in actions:
                    if (
                        actions[action_index]["module"] == item
                    ):  # Found the matching module
                        module = item  # Save it
                        break
                if module != "":
                    break

            # Check if this action is a common action, so we can modify the module accordingly
            for i in actions:
                if (
                    actions[i]["module"] == "common"
                    and actions[i]["name"] == action_name
                ):
                    # Now we'll overwrite the module with the common module, and continue as normal
                    original_module = module
                    module = "common"  # Set module as common
                    function = actions[i]["function"]  # Save function
                    screenshot = actions[i]["screenshot"]  # Save screenshot
                    return (
                        module,
                        function,
                        original_module,
                        screenshot,
                    )  # Return module and function name

            for i in actions:  # For each dictionary in the dictionary
                if (
                    actions[i]["module"] == module
                    and actions[i]["name"] == action_name
                ):  # Module and action name match
                    function = actions[i]["function"]  # Save function
                    screenshot = actions[i]["screenshot"]  # Save screenshot
                    return (
                        module,
                        function,
                        "",
                        screenshot,
                    )  # Return module and function name

            CommonUtil.ExecLog(
                sModuleInfo, "Could not find module or action_name is invalid", 3
            )
            return (
                "",
                "",
                "",
                "",
            )  # Should never get here if verify_step_data() works properly
        # Not enough words in the Sub-Field
        else:
            return "", "", "", ""  # Error handled in calling function
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def shared_variable_to_value(data_set):
    """ Look for any Shared Variable strings in step data, convert them into their values, and return """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    new_data = []  # Rebuild the data_set with the new variable (because it's a list of tuples which we can't update)

    skip_conversion_of_shared_variable_for_actions = [
        "if element exists",
        "optional loop settings",   # Dont delete this. this parameter should be dynamically captured with new data
        "loop settings",            # Dont delete this. this is older dataset. let it perform how it was designed
        "get parameter",            # This is selenium/appium object, need to retrieve in its non-string actual datatype
        "for loop action"
    ]

    try:
        for row in data_set:
            if str(row[1]).strip().lower() in skip_conversion_of_shared_variable_for_actions:
                new_data.append(row)
                continue
            data_row = list(row)
            for i in range(3):  # For each field (Field, Sub-Field, Value)
                while "%|" in data_row[i] and "|%" in data_row[i]:
                    CommonUtil.ExecLog(sModuleInfo, "Shared Variable: %s" % row[i], 0)
                    data_row[i] = sr.get_previous_response_variables_in_strings(data_row[i])
                    if data_row[i] == "zeuz_failed":
                        return "zeuz_failed"
            new_data.append(tuple(data_row))
        return new_data
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


### *********************************** Begin common built in functions *************************************** ###
# These functions are common with more than one of the BuiltInFunctions.py files (Selenium, Appium, REST, etc)
# How it works: We do not require the user to specify "common" in the action row. They just use whatever module they
# built the rest of the data set with, so as to make it easy for them. When action_handler() gets the data set, it
# first searches the actions dictionary for any common actions that match the name provided by the user. If found,
# it will remove the module the user specified, replace it with the "common" module, and continue as normal.


def step_result(data_set):
    """ Returns passed/failed in the standard format, when the user specifies it in the step data """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        action_value = ""
        for row in data_set:
            if row[0] == "step result" and row[1] == "action":
                action_value = row[2]
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())

    if (
        action_value in failed_tag_list
    ):  # Convert user specified pass/fail into standard result
        return "zeuz_failed"
    elif action_value in skipped_tag_list:
        return "skipped"
    elif action_value in passed_tag_list:
        return "passed"
    else:
        CommonUtil.ExecLog(sModuleInfo, "Step Result action has invalid VALUE", 3)
        return "zeuz_failed"


def step_exit(data_set):
    """ Exits a Test Step wtih passed/failed in the standard format, when the user specifies it in the step data """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        action_value = ""
        for row in data_set:
            if row[0] == "step exit" and row[1] == "action":
                action_value = row[2]
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())

    if (
        action_value in failed_tag_list
    ):  # Convert user specified pass/fail into standard result
        return "zeuz_failed"
    elif action_value in skipped_tag_list:
        return "skipped"
    elif action_value in passed_tag_list:
        return "passed"
    else:
        CommonUtil.ExecLog(sModuleInfo, "Step Result action has invalid VALUE", 3)
        return "zeuz_failed"


@logger
def Sleep(data_set):
    """ Sleep a specific number of seconds """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        seconds = float(data_set[0][2])
        print(f"Sleeping for {seconds} seconds")
        CommonUtil.ExecLog(sModuleInfo, f"Sleeping for {seconds} seconds", 1)
        time.sleep(seconds)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Wait_For_Element(data_set):
    """ Continuously monitors an element for a specified amount of time and returns pass when it's state is changed """
    # Handles two types:
    # wait: Wait for element to appear/available
    # wait disable: Wait for element to disappear/hide

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Get webdriver
    if sr.Test_Shared_Variables("common_driver"):
        common_driver = sr.Get_Shared_Variables("common_driver")
    else:
        CommonUtil.ExecLog(
            sModuleInfo,
            "Could not dynamically locate correct driver. You either did not initiate it with a valid action that populates it, or you called this function with a module name that doesn't support this function",
            3,
        )
        return "zeuz_failed"

    try:
        wait_for_element_to_disappear = False
        timeout_duration = None
        for row in data_set:
            if row[1] == "action":
                if row[0] == "wait disable":
                    wait_for_element_to_disappear = True
                timeout_duration = float(row[2])

        if not wait_for_element_to_disappear:
            Element = LocateElement.Get_Element(data_set, common_driver, element_wait=timeout_duration)
            if Element not in failed_tag_list:  # Element found
                CommonUtil.ExecLog(sModuleInfo, "Element appeared", 1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Element did not appear", 3)
                return "zeuz_failed"

        else:
            start = time.time()
            while time.time() <= start + timeout_duration:
                Element = LocateElement.Get_Element(data_set, common_driver, element_wait=2.0)
                if Element in failed_tag_list:  # Element removed
                    CommonUtil.ExecLog(sModuleInfo, "Element disappeared", 1)
                    return "passed"
                time.sleep(timeout_duration/10)
            CommonUtil.ExecLog(sModuleInfo, "Element did not disappear", 3)
            return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Save_Text(data_set):
    """ Save the text from the given element to shared variables under the variable name provided """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Get webdriver
    if sr.Test_Shared_Variables("common_driver"):
        common_driver = sr.Get_Shared_Variables("common_driver")
    else:
        CommonUtil.ExecLog(
            sModuleInfo,
            "Could not dynamically locate correct driver. You either did not initiate it with a valid action that populates it, or you called this function with a module name that doesn't support this function",
            3,
        )
        return "zeuz_failed"

    # Parse data set
    try:
        variable_name = ""
        for row in data_set:
            if row[1] == "action":
                variable_name = row[2]  # Save action Value as the shared variable name
        if variable_name == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Missing variable name to save text as from Value field on action line",
                3,
            )
            return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error parsing data set"
        )

    # Find element
    Element = LocateElement.Get_Element(data_set, common_driver)
    if Element in failed_tag_list:
        CommonUtil.ExecLog(
            sModuleInfo, "Unable to locate your element with given data.", 3
        )
        return "zeuz_failed"

    try:
        # !!! Seems like a really round about way of just removing \n. Why not use replace()?
        list_of_element_text = Element.text.split("\n")  # Split multi-line text
        visible_list_of_element_text = ""
        for each_text_item in list_of_element_text:  # For each line of text
            if each_text_item != "":
                # visible_list_of_element_text+=each_text_item # Append each line into one string
                tmp = [
                    c for c in each_text_item if 0 < ord(c) < 127
                ]  # Strip any binary characters
                visible_list_of_element_text += "".join(
                    tmp
                )  # Append each line into one string

        result = sr.Set_Shared_Variables(
            variable_name, visible_list_of_element_text
        )  # Save element text into shared variable using name given by user
        if result in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Value of Variable '%s' could not be saved" % variable_name,
                3,
            )
            return "zeuz_failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Element text saved", 1)
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error reading and saving element text"
        )


@deprecated
@logger
def Compare_Variables(data_set):
    """ Compare shared variables / strings to each other """
    # Compares two variables from Field and Value on any line that is not the action line
    return sr.Compare_Variables([data_set])


@deprecated
@logger
def Compare_Partial_Variables(data_set):
    """ Compare shared variables / strings to eachother """
    # Compares two variables partially from Field and Value on any line that is not the action line
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    return sr.Compare_Partial_Variables([data_set])


@logger
def save_into_variable(data_set):
    """Save variable with native python type.

    Can also create/append/update a str, list or dictionary from the given data.

    Accepts any valid Python representation or JSON data.

    Args:
        data_set:
          data               | element parameter  | valid JSON string
          operation          | element parameter  | save/update
          extra operation    | optional parameter | length/no duplicate/ascending sort/descending sort
          save into variable | common action      | variable_name

    Returns:
        "passed" if success.
        "zeuz_failed" otherwise.
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:

        operation = "save"
        extra_operation = None
        variable_value = None
        variable_name = None

        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if "extra operation" in left:
                    extra_operation = right.strip().lower()
                elif "operation" in left:
                    operation = right.strip().lower()
                elif "data" in left:
                    variable_value = CommonUtil.parse_value_into_object(right)
                elif "action" in mid:
                    variable_name = right.strip()
        except:
            CommonUtil.ExecLog(sModuleInfo, "Failed to parse data.", 1)
            traceback.print_exc()
            return "zeuz_failed"

        if operation == "save":
            # Noop.
            pass
        elif operation == "append":
            var = sr.Get_Shared_Variables(variable_name)
            if (type(var), type(variable_value)) == (list, str):
                var += [variable_value]
            elif type(var) in (list, str):
                var += variable_value
            elif type(var) == dict:
                var.update(variable_value)
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"Invalid data type for 'append': {type(var)}. Must be either str, list or dict.",
                    1,
                )
                return "zeuz_failed"

            variable_value = var
        else:
            CommonUtil.ExecLog(
                sModuleInfo, f"Invalid operation. Supported operations: save/append", 1,
            )
            return "zeuz_failed"

        try:
            if extra_operation:
                if "length" in extra_operation:
                    variable_value = len(variable_value)
                elif "no duplicate" in extra_operation:
                    variable_value = list(set(variable_value))
                elif "sort" in extra_operation or "shuffle" in extra_operation:
                    variable_value = sort_list(variable_value, extra_operation)
                elif "sum" in extra_operation:
                    s = 0
                    for i in variable_value:
                        try:
                            if isinstance(i, float) or isinstance(i, str) and "." in i:
                                s += float(i)
                            else:
                                s += int(i)
                        except:
                            continue
                    variable_value = s
        except:
            CommonUtil.ExecLog(
                    sModuleInfo, f"Failed to perform extra action.", 3,
            )
            return "zeuz_failed"

        sr.Set_Shared_Variables(variable_name, variable_value)

        return "passed"
    except:
        CommonUtil.ExecLog(sModuleInfo, "Failed to save variable.", 3)
        return "zeuz_failed"


def sort_list(variable_value, extra_operation):
    dictionary = True if isinstance(variable_value, dict) else False
    index = 0
    for i in variable_value:
        if isinstance(i, list):
            variable_value[index] = sort_list(i, extra_operation)
        elif isinstance(i, dict):
            variable_value[index] = sort_list(i, extra_operation)
        else:
            try:
                return_when_error = variable_value
                if dictionary and (isinstance(variable_value[i], list) or isinstance(variable_value[i], dict)):
                    variable_value[i] = sort_list(variable_value[i], extra_operation)
                elif dictionary:
                    pass
                else:
                    if "descending" in extra_operation:
                        variable_value = sorted(variable_value, reverse=True)
                    elif "shuffle" in extra_operation:
                        random.shuffle(variable_value)
                    else:
                        variable_value = sorted(variable_value)
                    break
            except TypeError:
                CommonUtil.ExecLog(
                    "",
                    "Skipping the list %s\n" % str(variable_value) +
                    "Items inside your list should be of same datatype. Example:\n" +
                    "<list of numbers> [1,2,4,3.5]\n" +
                    "<list of strings> ['apple','cat','20.5']\n" +
                    "<list of lists> [ [1,2,4,3.5], ['apple','cat','20.5'] ]\n" +
                    "Above is a 2 Dimensional list but you can provide any n Dimensional list but the unit lists should have items of same datatype\n" +
                    "<list of dicts> [ {'name':'John', 'id':20}, {'name':'Mike', 'id':10} ]",
                    2
                )
                return return_when_error

        index += 1
    return variable_value


@logger
@deprecated
def Initialize_List(data_set):
    """ Prepares an empty list in shared variables """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    return sr.Initialize_List([data_set])


@logger
def Randomize_List(data_set):
    """ Prepares an empty list in shared variables """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    return sr.Randomize_List([data_set])


@logger
@deprecated
def Initialize_Dict(data_set):
    """ Prepares an empty dict in shared variables """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    return sr.Initialize_Dict([data_set])


@logger
@deprecated
def Compare_Lists_or_Dicts(data_set):
    """ Compare two lists stored in shared variables """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, 'Use our new improved action "Compare Data"', 2)
    return sr.Compare_Lists_or_Dicts([data_set])


nested, datatype1, datatype2 = False, "", ""


@logger
def New_Compare_Variables(step_data):
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
        check_subset = False
        global nested, datatype1, datatype2
        nested, datatype1, datatype2 = False, "", ""

        for left, mid, right in step_data:
            mid = mid.strip().lower()
            if mid in ("compare", "element parameter"):
                list1_name = left
                list2_name = right
            elif "action" in mid:
                action_type = right.strip().lower()
                if action_type == "exact match":
                    match_by_index = True
                if action_type == "ignore list order":
                    match_by_index = False
                # if action_type.startswith("ignore extra items"):  # Check exclusion is turned off. will turn on in future if needed
                #     check_exclusion = True
                if action_type == "subset":
                    check_subset = True

        list1 = CommonUtil.parse_value_into_object(list1_name)
        list2 = CommonUtil.parse_value_into_object(list2_name)

        try: list1_str = json.dumps(CommonUtil.parse_value_into_object(list1), indent=2, sort_keys=True)
        except: list1_str = str(list1)
        try: list2_str = json.dumps(CommonUtil.parse_value_into_object(list2), indent=2, sort_keys=True)
        except: list2_str = str(list2)

        datatype1 = get_datatype(list1)
        datatype2 = get_datatype(list2)

        if check_subset:
            list1 = CommonUtil.parse_value_into_object(list1_name)
            list2 = CommonUtil.parse_value_into_object(list2_name)
            if type(list1) == str and type(list2) == str:
                if list1 == list2:
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 1)
                    CommonUtil.ExecLog(sModuleInfo, "RIGHT str is equal to the LEFT str", 1)
                    return "passed"
                elif list1 in list2:
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 1)
                    CommonUtil.ExecLog(sModuleInfo, "LEFT str is a subset of RIGHT str", 1)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 3)
                    CommonUtil.ExecLog(sModuleInfo, "LEFT str is not a subset of RIGHT str", 3)
                    return "zeuz_failed"

            if not (type(list1).__name__ in ("list", "tuple") and type(list2).__name__ in ("list", "tuple")):
                CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 3)
                CommonUtil.ExecLog(sModuleInfo, "To check subset both the variable should be list or tuple or str", 3)
                return "zeuz_failed"
            elif list1 == list2:
                CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 1)
                CommonUtil.ExecLog(sModuleInfo, "RIGHT list is equal to the LEFT list", 1)
                return "passed"
            elif all(x in list2 for x in list1):
                CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 1)
                CommonUtil.ExecLog(sModuleInfo, "LEFT list is a subset of RIGHT list", 1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 3)
                CommonUtil.ExecLog(sModuleInfo, "LEFT list is not a subset of RIGHT list", 3)
                return "zeuz_failed"

        found_list = []
        not_found_list1 = []
        not_found_list2 = []

        if (isinstance(list1, list) or isinstance(list1, tuple)) and (isinstance(list2, list) or isinstance(list2, tuple)):
            both_list = True
            variable_list1 = list1
            variable_list2 = list2
            if (len(list1) and type(list1[0]).__name__ in ("list", "tuple")) or (len(list2) and type(list2[0]).__name__ in ("list", "tuple")):
                nested = True

            results = compare_list_tuple(list1, list2, check_exclusion, match_by_index)
            if check_exclusion:  # Check exclusion is turned off. will turn on in future if needed
                if nested and results == "not found":
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 3)
                    CommonUtil.ExecLog(sModuleInfo, "All items of RIGHT list is not found in the LEFT list", 3)
                    return "zeuz_failed"
                elif nested and results == "all found":
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 1)
                    CommonUtil.ExecLog(sModuleInfo, "All items of RIGHT list is found in the LEFT list", 1)
                    return "passed"
                elif isinstance(results, list):
                    found_list = results
                else:
                    print("invalid from check exclusion")
            elif not match_by_index:
                if nested and results == "not found":
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 3)
                    CommonUtil.ExecLog(sModuleInfo, "All items of LEFT list and RIGHT list did not match", 3)
                    return "zeuz_failed"
                elif nested and results == "all found":
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 1)
                    CommonUtil.ExecLog(sModuleInfo, "All items of LEFT list and RIGHT list matched", 1)
                    return "passed"
                elif nested and results == "2nd list larger":
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 3)
                    CommonUtil.ExecLog(sModuleInfo, "Somewhere inside RIGHT list has more items than LEFT list", 3)
                    return "zeuz_failed"
                elif nested and results == "1st list larger":
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 3)
                    CommonUtil.ExecLog(sModuleInfo, "Somewhere inside LEFT list has more items than RIGHT list", 3)
                    return "zeuz_failed"
                elif isinstance(results, tuple):
                    found_list, not_found_list1, not_found_list2 = results
                else:
                    print("invalid from not match by index")
            else:
                if results == "not matched":
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 3)
                    CommonUtil.ExecLog(sModuleInfo, "LEFT list and RIGHT list did not match", 3)
                    return "zeuz_failed"
                elif results == "all matched":
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 1)
                    CommonUtil.ExecLog(sModuleInfo, "All items of LEFT list and RIGHT list did matched", 1)
                    return "passed"
                elif isinstance(results, tuple):
                    found_list, not_found_list1, not_found_list2, pass_count, fail_count = results
        elif isinstance(list1, dict) and isinstance(list2, dict):  # if both are dict
            for key in list1:
                if key in list2:
                    if key not in taken:
                        new_tuple = (key, list1[key])
                        variable_list1.append(new_tuple)
                        new_tuple = (key, list2[key])
                        variable_list2.append(new_tuple)
                        taken.append(key)
                        if str(list1[key]).lower().strip() == str(list2[key]).lower().strip():
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
                        if str(list1[key]).lower().strip() == str(list2[key]).lower().strip():
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
        else:
            if not match_by_index:
                if str(list1) == str(list2):
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1, datatype2, list2), 1)
                    CommonUtil.ExecLog(sModuleInfo, "LEFT and RIGHT value matched", 1)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1, datatype2, list2), 3)
                    CommonUtil.ExecLog(sModuleInfo, "LEFT and RIGHT value did not match", 3)
                    return "zeuz_failed"
            else:
                if list1 == list2:
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1, datatype2, list2), 1)
                    CommonUtil.ExecLog(sModuleInfo, "LEFT and RIGHT value matched", 1)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1, datatype2, list2), 3)
                    CommonUtil.ExecLog(sModuleInfo, "LEFT and RIGHT value did not match", 3)
                    return "zeuz_failed"
        """ Below code is useless now"""
        if nested:
            pass
        else:
            if check_exclusion: # Check exclusion is turned off. will turn on in future if needed
                if len(found_list) > 0:
                    CommonUtil.ExecLog(
                        sModuleInfo, "Match found for items: %s" % found_list, 3
                    )
                    return "zeuz_failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "No match found", 1)
                    return "passed"
            try: list1_str = json.dumps(CommonUtil.parse_value_into_object(list1), indent=2, sort_keys=True)
            except: list1_str = str(list1)
            try: list2_str = json.dumps(CommonUtil.parse_value_into_object(list2), indent=2, sort_keys=True)
            except: list2_str = str(list2)

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
                    if match_by_index:
                        if list1 == list2:
                            CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 1)
                            CommonUtil.ExecLog(sModuleInfo, "LEFT and RIGHT value matched", 1)
                            return "passed"
                        else:
                            CommonUtil.ExecLog(sModuleInfo, "LEFT (%s):\n%s\n\nRIGHT (%s):\n%s" % (datatype1, list1_str, datatype2, list2_str), 3)
                            CommonUtil.ExecLog(sModuleInfo, "LEFT and RIGHT value did not match", 3)
                            return "zeuz_failed"
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Right now we only support 'exact match' for dictionary comparison", 3)
                        return "zeuz_failed"


            else:
                if len(not_found_list1) > 0 or len(not_found_list2) > 0:
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (Simple list):\n%s\n\nRIGHT (Simple list):\n%s" % (list1_str, list2_str), 3)
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "LEFT list and RIGHT list did not match.\n" +
                        "Not matched items  (LEFT list): %s\nNot matched items (RIGHT list): %s"
                        % (str(not_found_list1), str(not_found_list2)), 3)
                    return "zeuz_failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "LEFT (Simple list):\n%s\n\nRIGHT (Simple list):\n%s" % (list1_str, list2_str), 1)
                    CommonUtil.ExecLog(sModuleInfo, "LEFT list and RIGHT list matched.", 1)
                    return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def compare_list_tuple(list1, list2, check_exclusion, match_by_index):
    found_list, not_found_list1, not_found_list2, pass_count, fail_count = [], [], [], 0, 0
    global nested
    if check_exclusion: # Check exclusion is turned off. will turn on in future if needed
        if nested and len(list1) != len(list2):
            pass
        for each2 in list2:
            if isinstance(each2, list) or isinstance(each2, tuple):
                nested = True
                for each1 in list1:
                    found_status = compare_list_tuple(each1, each2, check_exclusion, match_by_index)
                    if found_status == "not found":
                        return "not found"
                    elif found_status == "all found":
                        return "all found"
            elif nested and each2 not in list1:
                return "not found"
            elif not nested and each2 in list1:
                found_list.append(each2)
        if nested:
            return "all found"
        else:
            return found_list

    elif not match_by_index:
        if nested and len(list1) != len(list2):
            if len(list2) > len(list1):
                return "2nd list larger"
            elif len(list1) > len(list2):
                return "1st list larger"
        for each1 in list1:
            if isinstance(each1, list) or isinstance(each1, tuple):
                nested = True
                for each2 in list2:
                    found_status = compare_list_tuple(each1, each2, check_exclusion, match_by_index)
                    if found_status == "not found":
                        continue
                    if found_status == "all found":
                        return "all found"
                    if found_status == "2nd list larger":
                        return "2nd list larger"
                    if found_status == "1st list larger":
                        return "1st list larger"
                else:
                    return "not found"
            elif nested and str(each1).strip().lower() not in [str(i).strip().lower() for i in list2]:
                return "not found"
            elif not nested and str(each1).strip().lower() in [str(i).strip().lower() for i in list2]:
                found_list.append(each1)
                pass_count += 1
            elif not nested:
                not_found_list1.append(each1)
                fail_count += 1
        for each2 in list2:
            if isinstance(each2, list) or isinstance(each2, tuple):
                nested = True
                for each1 in list1:
                    found_status = compare_list_tuple(each2, each1, check_exclusion, match_by_index)
                    if found_status == "not found":
                        continue
                    if found_status == "all found":
                        return "all found"
                    if found_status == "2nd list larger":
                        return "2nd list larger"
                    if found_status == "1st list larger":
                        return "1st list larger"
                else:
                    return "not found"
            elif nested and str(each2).strip().lower() not in [str(i).strip().lower() for i in list1]:
                return "not found"
            elif not nested and str(each2).strip().lower() not in [str(i).strip().lower() for i in list1]:
                not_found_list2.append(each2)
        if nested:
            return "all found"
        else:
            return found_list, not_found_list1, not_found_list2

    else:
        if (len(list1) and type(list1[0]).__name__ in ("list", "tuple")) or (len(list2) and type(list2[0]).__name__ in ("list", "tuple")):
            nested = True  # Maybe its not needed here in exact match
        if type(list1).__name__ in ("list", "tuple"):
            list1 = get_list(list1)
        if type(list2).__name__ in ("list", "tuple"):
            list2 = get_list(list2)
        if list1 == list2:
            return "all matched"
        else:
            return "not matched"

        """ Old method removed """
        # for cnt in range(len(list1)):
        #     if list1[cnt] == list2[cnt]:
        #         found_list.append(list1[cnt])
        #         pass_count += 1
        #     else:
        #         not_found_list2.append(list1[cnt])
        #         not_found_list1.append(list2[cnt])
        #         fail_count += 1
        # return found_list, not_found_list1, not_found_list2, pass_count, fail_count


def get_list(value):
    if isinstance(value, tuple) or isinstance(value, list):
        for cnt in range(len(value)):
            if isinstance(value[cnt], tuple) or isinstance(value[cnt], list):
                value[cnt] = get_list(value[cnt])
            if isinstance(value[cnt], tuple):
                value[cnt] = list(value[cnt])
    return value


def get_datatype(value):
    datatype = ""
    each = type(value).__name__
    if each not in ("list", "tuple"):
        return each
    while True:
        each = type(value).__name__
        if each in ("list", "tuple"):
            datatype += each + " of "
            try: value = value[0]
            except: return datatype[:-4]
        else:
            return datatype[:-4]



@logger
@deprecated
def Save_Variable(data_set):
    """ Assign a value to a variable stored in shared variables """
    variable_name = ""
    variable_value = ""
    for each in data_set:
        if each[1] == "element parameter" or "parameter" in each[1]:
            variable_name = each[0]
            variable_value = each[2]
    if variable_name != "" and variable_value != "":
        return sr.Set_Shared_Variables(variable_name, variable_value)
    else:
        return "zeuz_failed"


@logger
def save_length(data_set):
    """Save the length/size of a given value into a variable."""

    variable_name = ""
    value = ""
    for each in data_set:
        if "parameter" in each[1]:
            variable_name = each[0]
            value = each[2]

    value = CommonUtil.parse_value_into_object(value)

    try:
        value_length = len(value)
        return sr.Set_Shared_Variables(variable_name, value_length)
    except:
        return "zeuz_failed"


@logger
def Save_Current_Time(data_set):
    """ Assign a value to a variable stored in shared variables """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    variable_name = ""
    variable_value = ""
    time = ""
    now_hour = 0.00
    now = datetime.datetime.now()
    for each in data_set:
        if each[1] == "element parameter":
            variable_name = each[0]
            if now.hour >= 12:
                time = "PM"
            else:
                time = "AM"

            if now.hour > 12:
                now_hour = now.hour - 12
            else:
                now_hour = now.hour

            variable_value = (
                str(months[now.month])
                + " "
                + str(now.day)
                + ", "
                + str(now.year)
                + ", "
                + str(now_hour)
                + ":"
                + str(now.minute)
                + " "
                + time
            )
            print(variable_value)
    if variable_name != "" and variable_value != "":
        return sr.Set_Shared_Variables(variable_name, variable_value)
    else:
        return "zeuz_failed"


@logger
def delete_all_shared_variables(data_set):
    """ Delete all shared variables - Wrapper for Clean_Up_Shared_Variables() """
    # To delete only one, use the action "save variable", and set it to an empty string
    # Takes no inputs

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        return sr.Clean_Up_Shared_Variables()
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
@deprecated
def append_list_shared_variable(data_set):
    """ Creates and appends a python list variable """
    # Note: List is created if it doesn't already exist

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        # Parse data set
        tmp = data_set[0][
            2
        ].strip()  # Get key and value from Value field and clean them
        shared_var = tmp.split("=")[0].strip()  # Get variable name
        tmp = tmp.replace(shared_var, "").strip().replace("=", "", 1)

        separator = ","
        if "|,|" in tmp:
            separator = "|,|"
        values = tmp.split(separator)  # Get values (could be several)

        # Append all values
        for value in values:
            result = sr.Append_List_Shared_Variables(shared_var, value.strip())
        return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
@deprecated
def append_dict_shared_variable(data_set):
    """ Creates and appends a python dict variable """
    # Note: List is created if it doesn't already exist

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        # Parse data set
        tmp = data_set[0][
            2
        ].strip()  # Get key and value from Value field and clean them
        shared_var = tmp.split("=")[0].strip()  # Get variable name
        tmp = tmp.replace(shared_var, "").strip().replace("=", "", 1)
        values = tmp.split(",")  # Get values (could be several)

        # Append all values
        for value in values:
            k = ""
            v = ""
            separator = ":"
            if "|:|" in value:
                separator = "|:|"
            value = str(value).split(separator)
            k = str(value[0]).strip()
            v = str(value[1]).strip()
            value = collections.OrderedDict()
            value[k] = v
            result = sr.Append_Dict_Shared_Variables(shared_var, value)
        return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

@deprecated
@logger
def save_dict_value_by_key(data_set):
    """ Gets the value of a key in a dictionary and saves it in a shared variable """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(
        sModuleInfo,
        "You can access any index of list or dictionary using python syntax.\n" +
        " Use our other action 'Save variable - number string list dictionary'",
        2)
    try:
        # Split the data into left and right side (just like variable assignment x = y)
        left_side, right_side = data_set[0][2].split("=", 1)

        # Name of the shared variable where the value will be stored
        variable_name = left_side.strip()

        # Split the dictionary and the key
        _dict, _key = right_side.strip().rsplit("|", 1)

        # Strip any unnecessary white spaces
        _dict = _dict.strip()
        _key = _key.strip()

        # Convert _dict string into an actual dictionary
        # https://stackoverflow.com/a/21154138/1941132
        _dict = ast.literal_eval(_dict)

        # Find the value of the key present in the dictionary
        variable_value = _dict[_key]

        # Store it into shared variables
        return sr.Set_Shared_Variables(variable_name, variable_value)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def save_key_value_from_dict_list(data_set):
    """
    From a list of dictionaries, return the value of another key in the dictionary
    that matches the given key value pair

    my_val = %|my_dict|% | %|key_to_match|% |equals| %|value_to_match|% | %|key_to_return|%
    my_val = my_dict | key_to_match == value_to_match | key_to_return
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        # Split the data into left and right side (just like variable assignment x = y)
        left_side, right_side = data_set[0][2].split("=", 1)

        # Name of the shared variable where the value will be stored
        variable_name = left_side.strip()

        # Split the list of dictionary and the key-value pair
        list_of_dict, key_and_val, key_to_return = right_side.strip().split("|", 2)

        # Split the key value pair
        key_to_match, val_to_match = key_and_val.split("==", 1)

        # Strip any unnecessary white spaces
        list_of_dict = list_of_dict.strip()
        key_to_match = key_to_match.strip()
        val_to_match = val_to_match.strip()
        key_to_return = key_to_return.strip()

        # Convert list_of_dict string into an actual list
        # https://stackoverflow.com/a/21154138/1941132
        list_of_dict = ast.literal_eval(list_of_dict)

        variable_value = None

        for each in list_of_dict:
            if (
                key_to_match in each
                and each[key_to_match] == val_to_match
                and key_to_return in each
            ):
                variable_value = each[key_to_return]
                break

        if variable_value:
            # Store it into shared variables
            return sr.Set_Shared_Variables(variable_name, variable_value)
        else:
            return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def extract_date(data_set):
    """
    Parse date from a given string and save it into a variable

    Action format:
    parse date          common action           variable_name = %|string_containing_date|%
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        variable_name = None
        variable_value = None
        date_format = None

        for row in data_set:
            if "action" in row[1]:
                # Split the data into left and right side (just like variable assignment x = y)
                variable_name, str_containing_date = data_set[0][2].split("=", 1)

                # Strip any unnecessary white spaces
                variable_name = variable_name.strip()
                str_containing_date = str_containing_date.strip()

                # Extract the date and convert it into datetime object
                extracted_date = datefinder.find_dates(str_containing_date).__next__()
            elif "parameter" in row[1]:
                date_format = row[2]

        if not date_format:
            variable_value = str(extracted_date)
        else:
            variable_value = extracted_date.strftime(date_format)

        # Store it into shared variables
        return sr.Set_Shared_Variables(variable_name, variable_value)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
@deprecated
def insert_list_into_another_list(data_set):
    """ Creates and appends a python list variable """
    # Note: List is created if it doesn't already exist

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        # Parse data set
        tmp = data_set[0][
            2
        ].strip()  # Get key and value from Value field and clean them
        tmp = tmp.split("=",1)  # Get variable name
        parent_list_name = tmp[0].strip()
        if ";" in str(tmp[1]):  # direct initialization parent_list = [[a,b,c],[x,y,z]]
            parent_separator = ";"
            if "|;|" in str(tmp[1]):
                parent_separator = "|;|"
            parent_list_splitted_by_semicolon = (
                str(tmp[1]).strip().split(parent_separator)
            )
            for each_split in parent_list_splitted_by_semicolon:
                separator = ","
                if "|,|" in each_split:
                    separator = "|,|"
                child_list_raw = each_split.strip().split(separator)
                child_list = []
                for element in child_list_raw:
                    child_list.append(element.strip())
                result = sr.Append_List_Shared_Variables(
                    parent_list_name, child_list, value_as_list=True
                )
                if result in failed_tag_list:
                    return result
        else:  # normal insert parent_list = [list1,list2]
            separator = ","
            if "|,|" in str(tmp[1]):
                separator = "|,|"
            all_child_list_names = str(tmp[1]).strip().split(separator)

            for child_list_name in all_child_list_names:
                if not sr.Test_Shared_Variables(child_list_name):
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "List named %s not found in shared variables" % child_list_name,
                        3,
                    )
                    return "zeuz_failed"
                child_list = sr.Get_Shared_Variables(child_list_name)
                # Append all values
                result = sr.Append_List_Shared_Variables(
                    parent_list_name, child_list, value_as_list=True
                )
                if result in failed_tag_list:
                    return result
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
@deprecated
def insert_dict_into_another_dict(data_set):
    """ Creates and appends a python list variable """
    # Note: List is created if it doesn't already exist

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        # Parse data set
        tmp = (
            data_set[0][2].replace(" ", "").strip()
        )  # Get key and value from Value field and clean them
        tmp = tmp.split("=")  # Get variable name
        parent_dict_name = tmp[0].strip()
        separator = ","
        if "|,|" in str(tmp[1]):
            separator = "|,|"
        all_child_dict_names = tmp[1].strip().split(separator)

        for child_dict_name in all_child_dict_names:
            separator = ":"
            if "|:|" in str(child_dict_name):
                separator = "|:|"
            splitted_text = str(child_dict_name).split(separator)
            key = str(splitted_text[0]).strip()
            dict_name = str(splitted_text[1]).strip()

            if not sr.Test_Shared_Variables(dict_name):
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Dict named %s not found in shared variables" % dict_name,
                    3,
                )
                return "zeuz_failed"
            child_dict = sr.Get_Shared_Variables(dict_name)
            # Append all values
            result = sr.Append_Dict_Shared_Variables(
                key, child_dict, parent_dict=parent_dict_name
            )
            if result in failed_tag_list:
                return result
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def sequential_actions_settings(data_set):
    """ Test Step front end for modifying certain variables used by Sequential Actions """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        # Parse data set
        tmp = (
            data_set[0][2].replace(" ", "").strip()
        )  # Get key and value from Value field and clean them
        shared_var = tmp.split("=")[0].strip().lower()  # Retrieve variable name
        value = tmp.replace(shared_var + "=", "").strip()  # Retrieve value for variable

        # Verify this is a real variable (should be set somewhere else)
        if not sr.Test_Shared_Variables(shared_var):
            CommonUtil.ExecLog(
                sModuleInfo,
                "The variable name specified (%s) is not a valid Sequential Action variable"
                % str(shared_var),
                3,
            )
            return "zeuz_failed"

        # Save variable - all functions that use this variable will now use the new value
        CommonUtil.ExecLog(
            sModuleInfo,
            "Changing Sequential Action setting of %s from %s to %s"
            % (str(shared_var), str(sr.Get_Shared_Variables(shared_var)), str(value)),
            1,
        )
        return sr.Set_Shared_Variables(shared_var, value)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def print_shared_variables():
    for each in sr.shared_variables:
        print(each + " : " + str(sr.shared_variables[each]))


@logger
def set_server_variable(data_set):
    # can set multiple server variable with one action
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        run_id = sr.Get_Shared_Variables("run_id")

        for row in data_set:
            if (
                str(row[1]).strip().lower() == "element parameter"
                or "parameter" in str(row[1]).strip().lower()
            ):
                key = str(row[0]).strip()
                value = str(row[2]).strip()
                # call main driver to send var to server
                MainDriverApi.set_server_variable(run_id, key, value)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def get_server_variable(data_set):
    # can get multiple server variable with one action
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        run_id = sr.Get_Shared_Variables("run_id")

        for row in data_set:
            if (
                str(row[1]).strip().lower() == "element parameter"
                or "parameter" in str(row[1]).strip().lower()
            ):
                key = str(row[0]).strip()

                dict = MainDriverApi.get_server_variable(run_id, key)
                for key in dict:
                    sr.Set_Shared_Variables(key, dict[key])
                    CommonUtil.ExecLog(
                        sModuleInfo, "Got server variable %s='%s'" % (key, dict[key]), 1
                    )

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def get_server_variable_and_wait(data_set):
    # can get multiple server variable with one action
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        run_id = sr.Get_Shared_Variables("run_id")

        key = ""
        wait_time = 5
        for row in data_set:
            if (
                str(row[1]).strip().lower() == "element parameter"
                or "parameter" in str(row[1]).strip().lower()
            ):
                key = str(row[0]).strip()
            if str(row[1]).strip().lower() == "action":
                wait_time = int(str(row[2]).strip())

        i = 1
        dict = {}
        CommonUtil.ExecLog(sModuleInfo, "Waiting for server variable '%s'" % key, 1)
        while i <= wait_time:
            dict = MainDriverApi.get_all_server_variable(run_id)
            try:
                if key in dict and dict[key] != "null":
                    break
                elif (
                    "is_failed" in dict
                    and dict["is_failed"] != "null"
                    and dict["is_failed"] == "yes"
                ):
                    failed_machine = ""
                    if "failed_machine" in dict:
                        failed_machine = dict["failed_machine"]
                    if (
                        failed_machine
                        == (CommonUtil.MachineInfo().getLocalUser()).lower()
                    ):
                        continue

                    MainDriverApi.failed_due_to_linked_fail = True
                    failed_test_case = ""
                    if "failed_test_case" in dict:
                        failed_test_case = dict["failed_test_case"]

                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Linked test case '%s' failed in machine '%s'.. Test Case Failed..."
                        % (failed_test_case, failed_machine),
                        3,
                    )
                    return "zeuz_failed"
                else:
                    time.sleep(1)
            except:
                pass
            i += 1

        if key in dict and dict[key] != "null":
            sr.Set_Shared_Variables(key, dict[key])
            CommonUtil.ExecLog(
                sModuleInfo, "Got server variable %s='%s'" % (key, dict[key]), 1
            )
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Couldn't get server variable %s again" % (key), 3
            )
            return "zeuz_failed"

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def get_all_server_variable(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        run_id = sr.Get_Shared_Variables("run_id")

        dict = MainDriverApi.get_all_server_variable(run_id)
        for key in dict:
            sr.Set_Shared_Variables(key, dict[key])
            CommonUtil.ExecLog(
                sModuleInfo, "Got server variable %s='%s'" % (key, dict[key]), 1
            )
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def start_timer(data_set):
    """ Test Step front end for modifying certain variables used by Sequential Actions """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        # Parse data set
        try:
            seconds = int(str(data_set[0][2]).strip())  # Get no. of seconds for timer
        except:
            seconds = 0

        CommonUtil.ExecLog(sModuleInfo, "Starting timer", 1)

        if seconds >= 0:
            return sr.Set_Shared_Variables(
                "timer", datetime.datetime.now() - timedelta(seconds=seconds)
            )
        else:
            return sr.Set_Shared_Variables(
                "timer", datetime.datetime.now() + timedelta(seconds=abs(seconds))
            )
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def wait_for_timer(data_set):
    """ Test Step front end for modifying certain variables used by Sequential Actions """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        seconds_to_wait = int(str(data_set[0][2]).strip())
        # Parse data set
        start_time = sr.Get_Shared_Variables("timer")
        if start_time in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo, "Timer wasn't started, please start timer first", 3
            )

        delta = datetime.datetime.now() - start_time
        delta = int(delta.total_seconds())

        if delta > seconds_to_wait:
            CommonUtil.ExecLog(
                sModuleInfo, "Timer have expired before the execution was completed", 3
            )
            return "zeuz_failed"

        sleep_time = seconds_to_wait - delta
        CommonUtil.ExecLog(
            sModuleInfo, "%d seconds remaining for timer" % sleep_time, 1
        )
        CommonUtil.ExecLog(sModuleInfo, "Will wait for %d seconds" % sleep_time, 1)
        time.sleep(sleep_time)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
@deprecated
def create_3d_list(data_set):
    """ Creates and appends a python list variable """
    # Note: List is created if it doesn't already exist

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        # Parse data set
        tmp = data_set[0][
            2
        ].strip()  # Get key and value from Value field and clean them
        tmp = tmp.split("=",1)  # Get variable name
        parent_list_name = tmp[0].strip()
        if ";;" in str(tmp[1]):
            major_parent_separator = ";;"
            if "|;;|" in str(tmp[1]):
                major_parent_separator = "|;;|"
            a_3d_list_splitted_by_semicolon = (
                str(tmp[1]).strip().split(major_parent_separator)
            )
            for each_2d_list in a_3d_list_splitted_by_semicolon:
                a_2d_list = []
                if ";" in str(
                    each_2d_list
                ):  # direct initialization parent_list = [[a,b,c],[x,y,z]]
                    parent_separator = ";"
                    if "|;|" in str(each_2d_list):
                        parent_separator = "|;|"
                    parent_list_splitted_by_semicolon = (
                        str(each_2d_list).strip().split(parent_separator)
                    )
                    for each_split in parent_list_splitted_by_semicolon:
                        separator = ","
                        if "|,|" in each_split:
                            separator = "|,|"
                        child_list_raw = each_split.strip().split(separator)
                        child_list = []
                        for element in child_list_raw:
                            child_list.append(element.strip())
                        a_2d_list.append(child_list)
                else:
                    separator = ","
                    if "|,|" in each_2d_list:
                        separator = "|,|"
                    child_list_raw = each_2d_list.strip().split(separator)
                    child_list = []
                    for element in child_list_raw:
                        child_list.append(element.strip())
                    a_2d_list.append(child_list)
                result = sr.Append_List_Shared_Variables(
                    parent_list_name, a_2d_list, value_as_list=True
                )
                if result in failed_tag_list:
                    return result
        else:
            a_2d_list = []
            if ";" in str(
                tmp[1]
            ):  # direct initialization parent_list = [[a,b,c],[x,y,z]]
                parent_separator = ";"
                if "|;|" in str(tmp[1]):
                    parent_separator = "|;|"
                parent_list_splitted_by_semicolon = (
                    str(tmp[1]).strip().split(parent_separator)
                )
                for each_split in parent_list_splitted_by_semicolon:
                    separator = ","
                    if "|,|" in each_split:
                        separator = "|,|"
                    child_list_raw = each_split.strip().split(separator)
                    child_list = []
                    for element in child_list_raw:
                        child_list.append(element.strip())
                    a_2d_list.append(child_list)
            else:
                separator = ","
                if "|,|" in str(tmp[1]):
                    separator = "|,|"
                child_list_raw = str(tmp[1]).strip().split(separator)
                child_list = []
                for element in child_list_raw:
                    child_list.append(element.strip())
                a_2d_list.append(child_list)
            result = sr.Append_List_Shared_Variables(
                parent_list_name, a_2d_list, value_as_list=True
            )
            if result in failed_tag_list:
                return result

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def download_ftp_file(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        ftp_srv = ""
        ftp_usr = ""
        ftp_pass = ""
        file_to_download = ""
        local_file_path = ""

        for row in data_set:
            if str(row[0]).strip().lower() == "ftp server":
                ftp_srv = str(row[2]).strip()
            elif str(row[0]).strip().lower() == "ftp user":
                ftp_usr = str(row[2]).strip()
            elif str(row[0]).strip().lower() == "ftp password":
                ftp_pass = str(row[2]).strip()
            elif str(row[0]).strip().lower() == "file to download":
                file_to_download = str(row[2]).strip()
            elif str(row[0]).strip().lower() == "local file path":
                local_file_path = str(row[2]).strip()

        if ftp_usr == "" or ftp_srv == "" or ftp_pass == "" or file_to_download == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "FTP server info not given properly, please see action help",
                3,
            )
            return "zeuz_failed"

        if local_file_path == "":
            local_file_path = FileUtilities.get_home_folder()
            file_name = file_to_download.split("/")[-1:][0]
            local_file_path = local_file_path + os.sep + file_name
            CommonUtil.ExecLog(
                sModuleInfo,
                "Local file path not given, downloading the ftp file in the root directory path '%s'"
                % str(local_file_path),
                2,
            )
        elif "/" not in local_file_path and "\\" not in local_file_path:
            local_file_path = FileUtilities.get_home_folder() + os.sep + local_file_path
            CommonUtil.ExecLog(
                sModuleInfo,
                "Local file path not given, downloading the ftp file in the root directory path '%s'"
                % str(local_file_path),
                2,
            )

        ftp = ftplib.FTP(ftp_srv)
        ftp.login(ftp_usr, ftp_pass)

        files = [(file_to_download, local_file_path)]

        for file_ in files:
            with open(file_[1], "wb") as f:
                ftp.retrbinary("RETR " + file_[0], f.write)
        ftp.quit()

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def send_mail(data_set):
    """
    This is the action to send a mail

    Example:
    Field	            Sub Field	            Value
    smtp server         element parameter	    smtp.gmail.com
    smtp port           element parameter       587
    sender email        element parameter       sender@gmail.com
    sender password     element parameter       sender_pass
    receiver email      element parameter       receiver@gmail.com
    subject             element parameter       mail_subject
    body                element parameter       main content
    send mail           common action           send mail
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        smtp_server = ""
        smtp_port = ""
        sender_email = ""
        sender_password = ""
        receiver_email = ""
        subject = ""
        body = ""

        for row in data_set:
            if str(row[0]).strip().lower() == "smtp server":
                smtp_server = str(row[2]).strip()
            elif str(row[0]).strip().lower() == "smtp port":
                smtp_port = str(row[2]).strip()
            elif str(row[0]).strip().lower() == "sender email":
                sender_email = str(row[2]).strip()
            elif str(row[0]).strip().lower() == "sender password":
                sender_password = str(row[2]).strip()
            elif str(row[0]).strip().lower() == "receiver email":
                receiver_email = str(row[2]).strip()
            elif str(row[0]).strip().lower() == "subject":
                subject = str(row[2]).strip()
            elif str(row[0]).strip().lower() == "body":
                body = str(row[2]).strip()

        if (
            smtp_server == ""
            or smtp_port == ""
            or sender_email == ""
            or sender_password == ""
        ):
            CommonUtil.ExecLog(
                sModuleInfo,
                "SMTP server info not given properly, please see action help",
                3,
            )
            return "zeuz_failed"

        # Function to send email
        send_email(
            smtp_server,
            smtp_port,
            sender_email,
            sender_password,
            receiver_email,
            subject,
            body,
        )

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def check_latest_mail(data_set):
    """
    This is the action to check sender's name, mail and subject of the latest mail

    Example:
    Field	                Sub Field	            Value
    imap host               element parameter	    imap.gmail.com
    imap port               element parameter       993
    imap user               element parameter       user@gmail.com
    imap password           element parameter       user_pass
    select mailbox          element parameter       INBOX
    subject to check        element parameter       mail_subject
    sender mail to check    element parameter       sender@gmail.com
    sender name to check    optional parameter      Sender Name
    check latest mail       common action           check latest mail
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        imap_host = ""
        imap_port = ""
        imap_user = ""
        imap_pass = ""
        select_mailbox = ""
        subject_to_check = ""
        sender_mail_to_check = ""
        sender_name_to_check = ""

        for left, mid, right in data_set:
            left = left.lower()
            right = right.strip()
            if "imap host" in left:
                imap_host = right
            elif "imap port" in left:
                imap_port = right
            elif  "imap user" in left:
                imap_user = right
            elif "imap password" in left:
                imap_pass = right
            elif "select mailbox" in left:
                select_mailbox = right
            elif "subject to check" in left:
                subject_to_check = right
            elif "sender mail to check" in left:
                sender_mail_to_check = right
            elif "sender name to check" in left:
                sender_name_to_check = right


        if imap_host == "" or imap_port == "" or imap_user == "" or imap_pass == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "please provide the imap credentials for your mail server, see action help",
                3,
            )
            return "zeuz_failed"
        if not subject_to_check and not sender_mail_to_check and not sender_name_to_check:
            CommonUtil.ExecLog(
                sModuleInfo,
                "One of the following 3 parameters is required: subject, sender name, email body",
                3,
            )
            return "zeuz_failed"
        # Function to send email
        result = check_latest_received_email(
            imap_host,
            imap_port,
            imap_user,
            imap_pass,
            select_mailbox,
            subject_to_check,
            sender_mail_to_check,
            sender_name_to_check
        )

        if result:
            CommonUtil.ExecLog(sModuleInfo, "Email parameters matched", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Email parameters didn't match", 3)
            return "zeuz_failed"
            return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def validate_schema(data_set):
    """Validates a given JSON/Python object against a given JSON schema."""

    from jsonschema import validate, draft7_format_checker

    try:
        schema = None
        data = None
        variable_name = None

        for left, mid, right in data_set:
            if "action" in mid:
                variable_name = right.strip()
            elif "schema" in left:
                schema = right.strip()
            elif "data" in left:
                data = right.strip()

        try:
            data = CommonUtil.parse_value_into_object(data)
            schema = CommonUtil.parse_value_into_object(schema)

            validate(
                instance=data,
                schema=schema,
                format_checker=draft7_format_checker,
            )
        except Exception as e:
            sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
            CommonUtil.ExecLog(
                sModuleInfo,
                "Schema validation failed.\n%s" % e,
                3,
            )
            return CommonUtil.Exception_Handler(sys.exc_info())

        sr.Set_Shared_Variables(variable_name, True, print_variable=True)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

@deprecated
@logger
def write_into_single_cell_in_excel(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Try our new action named 'Write into excel'", 2)
    try:
        sheet_name = ""
        column = ""
        column_number = ""
        value = ""
        excel_file_path = ""

        for left, mid, right in data_set:
            left = left.lower()
            right = right.strip()
            if "sheet name" in left:
                sheet_name = right
            elif "column name" in left:
                column = right
            elif "column number" in left:
                column_number = right
            elif "text to write" in left:
                value = right
            elif "excel file path" in left:
                excel_file_path = right
                # Expand ~ (home directory of user) to absolute path.
                if "~" in excel_file_path:
                    excel_file_path = Path(os.path.expanduser(excel_file_path))
                excel_file_path = Path(excel_file_path)

        if (
            sheet_name == ""
            or column == ""
            or column_number == ""
            or excel_file_path == ""
        ):
            CommonUtil.ExecLog(
                sModuleInfo,
                "Excel file info not given properly, please see action help",
                3,
            )
            return "zeuz_failed"

        wb = xw.Book(excel_file_path)
        sheet = wb.sheets[sheet_name]
        cell_value = "%s%s" % (column, column_number)
        sheet.range(cell_value).value = value
        wb.save(excel_file_path)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

@logger
def excel_write(data_set):
    """
    Action to write data into Excel file. To write hundreds of rows and column only one action is enough

    Example 1:
    Field	            Sub Field	        Value
    file path           element parameter	F:\Automation Solutionz\a.xlsx
    sheet name          element parameter	Sheet1
    starting cell       element parameter	E2
    expand              optional parameter	right
    write into excel    common action   	["Expand to right",1.1021,"10.101"]

    Example 2:
    Field	            Sub Field	        Value
    file path           element parameter	F:\Automation Solutionz\a.xlsx
    sheet name          element parameter	Sheet1
    starting cell       element parameter	E4
    expand              optional parameter	down
    write into excel    common action   	["Exapand down",1.10,"10.01"]

    Example 3:
    Field	            Sub Field	        Value
    file path           element parameter	F:\Automation Solutionz\a.xlsx
    sheet name          element parameter	Sheet1
    starting cell       element parameter	F9
    write into excel    common action   	Hello world

    Example 4:
    Field	            Sub Field	        Value
    file path           element parameter	F:\Automation Solutionz\a.xlsx
    sheet name          element parameter	Sheet1
    starting cell       element parameter	F13
    write into excel    common action   	[["Name","Dept","Salary"],["Mike","Marketing","1050.55 dollar"],
                                            ["Fred","Sales",1040],["John","Developer",1040.55]]

    Example 5:
    Field	            Sub Field	        Value
    file path           element parameter	F:\Automation Solutionz\a.xlsx
    sheet name          element parameter	Sheet1
    starting cell       element parameter	F9
    write into excel    common action   	%|Excel_variable|%
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        sheet_name = ""
        cell = ""
        expand = "right"
        value = ""
        excel_file_path = ""

        for left, mid, right in data_set:
            left = left.lower()
            right = right.strip()
            if "sheet name" in left:
                sheet_name = right
            elif "starting cell" in left:
                cell = right
            elif "expand" in left:
                expand = right
            elif "write into excel" in left:
                value = right
                value = CommonUtil.parse_value_into_object(value)
                # print("......1......", type(value), ".......", value)
            elif "file path" in left:
                excel_file_path = right
                # Expand ~ (home directory of user) to absolute path.
                if "~" in excel_file_path:
                    excel_file_path = Path(os.path.expanduser(excel_file_path))
                excel_file_path = Path(excel_file_path)

        if (
            sheet_name == ""
            or cell == ""
            or excel_file_path == ""
        ):
            CommonUtil.ExecLog(
                sModuleInfo,
                "Excel file info not given properly, please see action help",
                3,
            )
            return "zeuz_failed"

        if expand.lower() == "down":
            Transpose_condition = True
        else:
            expand = "right"
            Transpose_condition = False

        wb = xw.Book(excel_file_path)
        sheet = wb.sheets[sheet_name]
        sheet.range(cell).options(transpose=Transpose_condition).value = value
        # print(type(sheet.range(cell).value),".....",sheet.range(cell).value)
        wb.save(excel_file_path)

        CommonUtil.ExecLog(
            sModuleInfo,
            "Excel Data has been written successfully starting from %s cell and expanded to %s" % (cell, expand),
            1,
        )
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def run_macro_in_excel(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        macro_name = ""
        excel_file_path = ""

        for row in data_set:
            if str(row[0]).strip().lower() == "macro name":
                macro_name = str(row[2]).strip()
            elif str(row[0]).strip().lower() == "excel file path":
                excel_file_path = str(row[2]).strip()

        if macro_name == "" or excel_file_path == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Excel file info not given properly, please see action help",
                3,
            )
            return "zeuz_failed"

        wb = xw.Book(excel_file_path)
        app = wb.app
        macro_path = macro_name
        macro_vba = app.macro(macro_path)
        macro_vba()
        wb.save(excel_file_path)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def excel_read(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        filepath = None
        sheet_name = None
        var_name = None
        cell_range = None
        expand = None
        structure_of_variable = None
        key_reference = None

        for left, mid, right in data_set:
            left = left.lower()
            if "file path" in left:
                filepath = right.strip()

                # Expand ~ (home directory of user) to absolute path.
                if "~" in filepath:
                    filepath = Path(os.path.expanduser(filepath))

                filepath = Path(filepath)
            if "sheet name" in left:
                sheet_name = right.strip()
            if "expand" in left:
                expand = right.strip()
            if "cell range" in left:
                cell_range = right.strip()
            if "read from excel" in left:
                var_name = right.strip()
            if "structure of variable" in left:
                structure_of_variable = right.lower().strip()
                if structure_of_variable not in ("dictionary", "list of lists"):
                    CommonUtil.ExecLog(sModuleInfo, "Only 'list of lists' and 'dictionary' avaliable", 3)
                    return "zeuz_failed"
            if "key reference" in left:
                key_reference = right.lower().strip().replace(" ", "")
                if key_reference not in ("row1", "column1"):
                    CommonUtil.ExecLog(sModuleInfo, "Currently we only support Column 1 and Row 1", 3)
                    return "zeuz_failed"

        wb = xw.Book(filepath)
        sheet = wb.sheets[sheet_name]
        if key_reference is None:
            key_reference = "row1"
        if expand:
            # expand can be 'table', 'down' and 'right'
            cell_data = sheet.range(cell_range).expand(expand).value
        else:
            cell_data = sheet.range(cell_range).value

        if structure_of_variable == "dictionary":
            data_dict = {}
            if key_reference == "row1":
                row_data = list(map(list, zip(*cell_data)))
                for cells in row_data:
                    data_dict[cells[0]] = cells[1:]
            elif key_reference == "column1":
                for cells in cell_data:
                    data_dict[cells[0]] = cells[1:] 
            cell_data = data_dict

        # Save into shared variables
        sr.Set_Shared_Variables(var_name, cell_data)

        # Save file so that we don't see the "Want to save" dailog.
        wb.save()
        wb.close()

        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def excel_comparison(data_set):
    """Compares the given range of data from an excel sheet with another
      data source.

    Args:
        data_set: List[List[str]]

    Returns:
        "passed" if successful.
        "zeuz_failed" otherwise.
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        filepath = None
        sheet_name = None
        var_name = None
        cell_range = None
        expand = None
        compare_variable = None
        write_to = None

        for left, mid, right in data_set:
            left = left.lower()
            if "file path" in left:
                filepath = right.strip()

                # Expand ~ (home directory of user) to absolute path.
                if "~" in filepath:
                    filepath = Path(os.path.expanduser(filepath))

                filepath = Path(filepath)
            if "sheet name" in left:
                sheet_name = right.strip()
            if "expand" in left:
                expand = right.strip()
            if "cell range" in left:
                cell_range = right.strip()
            if "compare variable" in left:
                compare_variable = right.strip()
            if "write to" in left:
                write_to = right.strip()
            if "excel comparison" in left:
                var_name = right.strip()

        wb = xw.Book(str(filepath))
        sheet = wb.sheets[sheet_name]

        if expand:
            # expand can be 'table', 'down' and 'right'
            cell_data = sheet.range(cell_range).expand(expand).value
        else:
            cell_data = sheet.range(cell_range).value

        result = list()

        # Get value from shared variables.
        value = sr.Get_Shared_Variables(compare_variable)

        if type(value) == type(cell_data) == list:
            for (src, dst) in zip(cell_data, value):
                # try converting to the type of excel value
                try:
                    type_name = type(src)
                    dst = type_name(dst)
                except:
                    pass
                result.append([src == dst])
        elif type(value) != list:
            dst = value
            for src in cell_data:
                result.append([src == dst])

        # Write the resulting difference to excel.
        sheet.range(write_to).value = result

        # Save into shared variables.
        sr.Set_Shared_Variables(var_name, result)

        # Save workbook.
        wb.save()
        wb.close()

        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
@deprecated
def get_excel_table(data_set):
    """DEPRECATED. Will be removed in a future release"""
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        sheet_name = ""
        first_cell_location = ""
        excel_file_path = ""
        var_name = ""

        for row in data_set:
            if str(row[0]).strip().lower() == "sheet name":
                sheet_name = str(row[2]).strip()
            elif str(row[0]).strip().lower() == "first cell location":
                first_cell_location = str(row[2]).strip()
            elif str(row[0]).strip().lower() == "excel file path":
                excel_file_path = str(row[2]).strip()
            elif (
                str(row[0]).strip().lower() == "variable name where data will be saved"
            ):
                var_name = str(row[2]).strip()

        if (
            sheet_name == ""
            or first_cell_location == ""
            or var_name == ""
            or excel_file_path == ""
        ):
            CommonUtil.ExecLog(
                sModuleInfo,
                "Excel file info not given properly, please see action help",
                3,
            )
            return "zeuz_failed"

        wb = xw.Book(excel_file_path)
        sheet = wb.sheets[sheet_name]
        rng2 = sheet.range(first_cell_location).options(expand="table")

        value = rng2.value
        sr.Set_Shared_Variables(var_name, value)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def split_string(data_set):
    """Splits a given string based on the given expression.

    Store the result (index 0 or 1) of the split in "variableName".

    Args:
        data_set: List[List[str]]

          index                     input parameter         0 or 1
          split expression          input parameter         abc
          source string             input parameter         hello abc world
          split string              common action           variableName

    Returns:
        "passed" if successful.
        "zeuz_failed" otherwise.
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        var_name = ""
        split_expression = ""
        source_string = ""

        for left, _, right in data_set:
            left = left.lower()
            if "split string" in left:
                var_name = right.strip()
            if "source string" in left:
                # Do not strip(), we do not know if it is desirable by user.
                source_string = right
            if "split expression" in left:
                split_expression = right

        # Validate data format.
        if "" in (var_name, split_expression, source_string):
            CommonUtil.ExecLog(sModuleInfo, "Invalid/missing data format.", 3)
            return "zeuz_failed"
        source_string = CommonUtil.parse_value_into_object(source_string)
        if type(source_string) != str:
            CommonUtil.ExecLog(sModuleInfo, "Got a %s object to split. Converting it to string before splitting" % type(source_string).__name__, 2)
            source_string = str(source_string)
        result = source_string.split(split_expression)

        # Save into shared variables.
        sr.Set_Shared_Variables(var_name, result)

        CommonUtil.ExecLog(
            sModuleInfo,
            "Split successfully\nString: \"%s\"\nSplit expression: \"%s\"" % (source_string, split_expression),
            1)
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def save_text_from_file_into_variable(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        import PyPDF2
        text_file_path = ""
        var_name = ""
        var_value = ""

        for row in data_set:
            if str(row[0]).strip().lower() == "text file path":
                text_file_path = str(row[2]).strip()
            elif (
                str(row[0]).strip().lower() == "variable name where data will be saved"
            ):
                var_name = str(row[2]).strip()

        if text_file_path == "" or var_name == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "Text file info not given properly, please see action help",
                3,
            )
            return "zeuz_failed"

        if "/" not in text_file_path and "\\" not in text_file_path:
            text_file_path = FileUtilities.get_home_folder() + os.sep + text_file_path

        if text_file_path.endswith("pdf"):
            pdfFileObj = open(text_file_path, "rb")
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            no_of_page = pdfReader.numPages

            i = 0
            while i < no_of_page:
                pageObj = pdfReader.getPage(i)
                var_value += pageObj.extractText()
                i += 1
        else:
            with open(text_file_path, "r") as file:
                data = file.read()
                var_value += data

        sr.Set_Shared_Variables(var_name, var_value)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def voice_command_response(step_data):
    """
    this action is used to communicate with voice activated device such as Alex.  the computer will speak out the wakeup word(s) such as
    (example: Alexa) followed by some commands (example: what is today's date).

    It will then listen for Alexa device to say something, and convert the sound to text

    voice command response        common action         <variable of  output text>
    wakeup command                input parameter        Alexa
    voice command                 input parameter        What is today's date
    voice name                    optional parameter     default
    voice speed                   optional parameter     140
    voice language                optional parameter     EN
    microphone number             optional parameter     1


    voice_command, voice_wakeup_command, voice_speed = '140', voice_name = 'default', microphone_number = '1'
    ****** This action needs more work to set voice name and language
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        import pyttsx3
        import speech_recognition

        recognizer = speech_recognition.Recognizer()
        engine = pyttsx3.init()

        # collecting data
        var_name = False
        voice_wakeup_command = False
        voice_command = False
        microphone_number = "1"
        voice_speed = "140"
        voice_name = "default"

        for each_step_data_item in step_data:
            if each_step_data_item[0].strip() == "voice command response":
                var_name = each_step_data_item[2].strip()
            if each_step_data_item[0].strip() == "wakeup command":
                voice_wakeup_command = each_step_data_item[2].strip()
            if each_step_data_item[0].strip() == "voice command":
                voice_command = each_step_data_item[2].strip()
            if each_step_data_item[0].strip() == "voice name":
                voice_name = each_step_data_item[2].strip()
            if each_step_data_item[0].strip() == "voice speed":
                voice_speed = each_step_data_item[2].strip()
            if each_step_data_item[0].strip() == "voice language":
                voice_language = each_step_data_item[2].strip()
            if each_step_data_item[0].strip() == "microphone number":
                microphone_number = each_step_data_item[2].strip()

        # data validation for mendatory fields
        if var_name == False:
            CommonUtil.ExecLog(sModuleInfo, "variable name cannot be missing", 3)
            return "zeuz_failed"
        if var_name == "":
            CommonUtil.ExecLog(sModuleInfo, "variable name cannot be missing", 3)
            return "zeuz_failed"
        if voice_wakeup_command == False:
            CommonUtil.ExecLog(sModuleInfo, "Voice wakeup command cannot be empty", 3)
            return "zeuz_failed"
        if voice_command == False:
            voice_command.ExecLog(sModuleInfo, "Voice command cannot be empty", 3)
            return "zeuz_failed"

        engine.setProperty("rate", int(voice_speed))
        microphone = speech_recognition.Microphone(
            device_index=int(microphone_number)
        )  # Adjust microphone index if you have more than 1
        # check that recognizer and microphone arguments are appropriate type
        if not isinstance(recognizer, speech_recognition.Recognizer):
            CommonUtil.ExecLog(sModuleInfo, "Unable to initialize voice recorder", 3)
            return "zeuz_failed"
        if not isinstance(microphone, speech_recognition.Microphone):
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to initialize microphone for voice recorder", 3
            )
            return "zeuz_failed"
        with microphone as source:
            CommonUtil.ExecLog(
                sModuleInfo, "Waking up and speaking to voice commands", 1
            )
            recognizer.adjust_for_ambient_noise(
                source
            )  # analyze the audio source for 1 second and adjust the recognizer sensitivity to ambient noise
            engine.say(voice_wakeup_command)
            engine.runAndWait()
            engine.say(voice_command)
            engine.runAndWait()
            audio = recognizer.listen(source)  # record audio
        CommonUtil.ExecLog(
            sModuleInfo, "Communicating with google speech to text converter...", 1
        )
        voice_to_text_result = "Not able to translate voice to text"
        try:
            voice_to_text_result = recognizer.recognize_google(audio)
        except speech_recognition.RequestError:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Google speech to text converter API was unreachable or unresponsive",
                3,
            )
            return "zeuz_failed"
        except speech_recognition.UnknownValueError:
            CommonUtil.ExecLog(
                sModuleInfo, "Google speech to text could not translate", 3
            )
            return "zeuz_failed"
        CommonUtil.ExecLog(
            sModuleInfo,
            "Your speech to text from %s was translated to be: %s"
            % (voice_wakeup_command, voice_to_text_result),
            1,
        )

        sr.Set_Shared_Variables(var_name, voice_to_text_result)
        return "passed"
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = (
            (str(exc_type).replace("type ", "Error Type: "))
            + ";"
            + "Error Message: "
            + str(exc_obj)
            + ";"
            + "File Name: "
            + fname
            + ";"
            + "Line: "
            + str(exc_tb.tb_lineno)
        )
        CommonUtil.ExecLog(
            sModuleInfo,
            "Unable to communicate or record the response from voice activated device.  Error: %s"
            % (Error_Detail),
            3,
        )
        return "zeuz_failed"


# Gloabal variable actions
@logger
def get_global_list_variable(data_set):
    # get the global list variable content
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        run_id = sr.Get_Shared_Variables("run_id")

        for row in data_set:
            if (
                str(row[1]).strip().lower() == "element parameter"
                or "parameter" in str(row[1]).strip().lower()
            ):
                key = str(row[0]).strip()

                value = MainDriverApi.get_global_list_variable(key)
                sr.Set_Shared_Variables(key, value)
                CommonUtil.ExecLog(
                    sModuleInfo, "Got global variable %s='%s'" % (key, value), 1
                )
                # for key in dict:
                #     sr.Set_Shared_Variables(key, dict[key])
                #     CommonUtil.ExecLog(sModuleInfo, "Got server variable %s='%s'" % (key, dict[key]), 1)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def append_to_global_list_variable(data_set):
    # append an item to global list variable
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        run_id = sr.Get_Shared_Variables("run_id")

        for row in data_set:
            if (
                str(row[1]).strip().lower() == "element parameter"
                or "parameter" in str(row[1]).strip().lower()
            ):
                key = str(row[0]).strip()
                value = str(row[2]).strip()
                # call main driver to send var to server
                MainDriverApi.append_to_global_list_variable(key, value)
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"append value : {value} to global variable {key} complete",
                    1,
                )

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def remove_item_from_global_list_variable(data_set):
    # remove an item from a global list variable
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        run_id = sr.Get_Shared_Variables("run_id")

        for row in data_set:
            if (
                str(row[1]).strip().lower() == "element parameter"
                or "parameter" in str(row[1]).strip().lower()
            ):
                key = str(row[0]).strip()
                value = str(row[2]).strip()
                # call main driver to send var to server
                MainDriverApi.remove_item_from_global_list_variable(key, value)
                CommonUtil.ExecLog(
                    sModuleInfo,
                    f"remove value : {value} from global variable {key} complete",
                    1,
                )

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def save_variable_by_list_difference(data_set):
    import ast

    """ save a variable by comparing two lists, here compare means set difference """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    saved_variable_name = ""
    variable1 = ""
    variable2 = ""
    variable_value = ""
    for each in data_set:
        if each[1] == "element parameter":
            if each[0] == "Variable1":
                variable1 = each[2]
            elif each[0] == "Variable2":
                variable2 = each[2]
            else:
                saved_variable_name = each[2]

    if variable1 and variable2:
        variable1_list = set(ast.literal_eval(variable1))
        variable2_list = set(ast.literal_eval(variable2))
        variable_value = list(variable1_list - variable2_list)[0]
        return sr.Set_Shared_Variables(saved_variable_name, variable_value)
    else:
        return "zeuz_failed"

@logger
def validate_list_order(data_set):
    """ To validate whether a list is in ascending or in descending order
    Example 1:
    Field	             Sub Field	            Value
    order type           element parameter	    ascending
    validate order       common action  	    [1,2,3.5]

    Example 2:
    Field	             Sub Field	            Value
    order type           element parameter	    descending
    validate order       common action  	    %|var|%

    Example 3:
    Field	             Sub Field	            Value
    order type           element parameter	    descending
    case sensitivity     optional parameter     False
    validate order       common action  	    ["c","A","3","t"]
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    case_sensitivity = True
    order_type = ""
    ignore = []
    for left, mid, right in data_set:
        left = left.strip().lower()
        right = right.strip()
        if left == "validate order":
            try:
                value = right
                value = CommonUtil.parse_value_into_object(value)
            except:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Couldn't parse your list",
                    3,
                )
                return "zeuz_failed"
        elif left == "case sensitivity":
            case_sensitivity = False if right.lower() == "false" else True
        elif left == "order type":
            order_type = right.lower()
        elif left == "ignore items":
            ign = CommonUtil.parse_value_into_object(right)
            if isinstance(ign, list):
                ignore += ign
            else:
                ignore.append(ign)

    if not isinstance(value, list):
        CommonUtil.ExecLog(
            sModuleInfo,
            'This action works only for simple lists. Such as [1, 2.5, 3] or ["c","a","t"]',
            3
        )
        return "zeuz_failed"
    if ignore:
        msg = 'Ignoring following items:'
        for each in ignore:
            msg += "\n" + str(each) + " " + str(type(each))
            i = 0
            while True:
                if i >= len(value):
                    break
                if value[i] == each:
                    del value[i]
                    i -= 1
                i += 1
        CommonUtil.ExecLog("", msg, 1)
    actual_val = copy.deepcopy(value)
    if isinstance(value[0], str) and not case_sensitivity:
        try:
            for i in range(len(value)):
                value[i] = value[i].lower()
        except:
            CommonUtil.ExecLog(
                sModuleInfo,
                'Please provide a simple list of numbers or list of strings.Such as [1, 2.5, 3] or ["c","a","t"]',
                3
            )
            return "zeuz_failed"

    if order_type not in ("ascending", "descending"):
        CommonUtil.ExecLog(
            sModuleInfo,
            "Order type should be provided between 'ascending' or 'descending' Taking 'ascending' by default ",
            2
        )
        order_type = "ascending"

    try:
        if order_type == "ascending":
            val_index = sorted(enumerate(value), key=lambda x: x[1], reverse=False)
            sorted_value = [i[1] for i in val_index]
            if sorted_value == value:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    'Your list is in ascending order',
                    1
                )
                return "passed"
            else:
                order = "descending" if sorted(value, reverse=True) == value else "random"
                if order == "descending":
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        'Your list is not in ascending order. Its in descending order',
                        3
                    )
                else:
                    Actual_sorted = [actual_val[i[0]] for i in val_index]
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        'Your list is not in ascending order. Its in random order\n' +
                        'The following list will be in ascending order for case sensitivity = %s\n%s' % (case_sensitivity, Actual_sorted),
                        3
                    )
                return "zeuz_failed"
        elif order_type == "descending":
            val_index = sorted(enumerate(value), key=lambda x: x[1], reverse=True)
            sorted_value = [i[1] for i in val_index]

            if sorted_value == value:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    'Your list is in descending order',
                    1
                )
                return "passed"
            else:
                order = "ascending" if sorted(value, reverse=False) == value else "random"
                if order == "ascending":
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        'Your list is not in descending order. Its in ascending order',
                        3
                    )
                else:
                    Actual_sorted = [actual_val[i[0]] for i in val_index]
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        'Your list is not in descending order. Its in random order\n' +
                        'The following list will be in descending order for case sensitivity = %s\n%s' % (case_sensitivity, Actual_sorted),
                        3
                    )
                return "zeuz_failed"
    except:
        CommonUtil.ExecLog(
            sModuleInfo,
            'Please provide a simple list of numbers or list of strings.Such as [1, 2.5, 3] or ["c","a","t"]',
            3
        )
        return "zeuz_failed"

@logger
def execute_python_code(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    inp, out_var, main_function, Code, filepath_code = "", "", "", "", ""

    for left, mid, right in data_set:
        left = left.strip().lower()
        if left == "file path":
            filepath = right.strip()
            # Expand ~ (home directory of user) to absolute path.
            if "~" in filepath:
                filepath = Path(os.path.expanduser(filepath))
            filepath = Path(filepath)
            with open(filepath, "r") as file:
                filepath_code = file.read()
        elif left == "input data":
            inp = right
        elif left == "output variable":
            out_var = right.strip()
        elif left == "main function":
            main_function = right.strip().split("(")[0]
        elif left == "execute python code":
            Code = right

    Code = filepath_code if filepath_code else Code
    try: exec(Code, globals())
    except: return CommonUtil.Exception_Handler(sys.exc_info())

    if main_function:
        code = main_function + "(" + inp + ")"
        try: out_val = eval(code)
        except: return CommonUtil.Exception_Handler(sys.exc_info())
        if out_var:
            CommonUtil.ExecLog(sModuleInfo, "Executed '%s' function and captured the return value into '%s' variable" % (main_function, out_var), 1)
            return sr.Set_Shared_Variables(out_var, out_val)
        CommonUtil.ExecLog(sModuleInfo, "Executed '%s' function and did not capture any return value" % main_function, 1)
    else:
        CommonUtil.ExecLog(sModuleInfo, "Executed the python code which was provided", 1)

    return "passed"


@logger
def csv_read(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        filepath = None
        delimiter = ","
        delimiter_support = {
            "comma": ",",
            "semicolon": ";",
            "dot": ".",
            "colon": ":",
            "dash": "-",
            "space": " ",
            "tab": "\t",
            "pipe": "|",
            "asterisk": "*",
            "plus": "+",
            "slash": "/",
            "backslash": "\\",
        }
        var_name = ""
        structure = "list of dictionaries"
        allowed_list = None
        map_key_names = None
        Integer, Float, Bool = [], [], []
        for left, _, right in data_set:
            left = left.lower().strip()
            if "file path" == left:
                filepath = right.strip()
                # Expand ~ (home directory of user) to absolute path.
                if "~" in filepath:
                    filepath = Path(os.path.expanduser(filepath))
                filepath = Path(filepath)
            elif "delimiter" == left:
                right = right.strip()
                if right in delimiter_support:
                    delimiter = delimiter_support[right]
                else:
                    delimiter = right
            elif "structure of the variable" == left:
                pass    # "list of dictionaries" for now. Will implement more structures in future
            elif "allowed list" == left:
                allowed_list = CommonUtil.parse_value_into_object(right.strip())
                if isinstance(allowed_list, str):
                    allowed_list = [allowed_list]
                if not isinstance(allowed_list, list):
                    allowed_list = None
                    CommonUtil.ExecLog(sModuleInfo, "Did not get 'Allowed list' as a list. Ignoring this parameter", 2)
            elif "map key names" == left:
                map_key_names = CommonUtil.parse_value_into_object(right.strip())
                if not isinstance(map_key_names, dict):
                    map_key_names = None
                    CommonUtil.ExecLog(sModuleInfo, "Did not get 'Map key names' as a dictionary. Ignoring this parameter", 2)
            elif "convert" in left:
                fields = CommonUtil.parse_value_into_object(right.strip())
                if "int" in left:
                    if isinstance(fields, str):
                        Integer.append(fields)
                    elif isinstance(fields, list):
                        Integer += fields
                elif "float" in left:
                    if isinstance(fields, str):
                        Float.append(fields)
                    elif isinstance(fields, list):
                        Float += fields
                elif "bool" in left:
                    if isinstance(fields, str):
                        Bool.append(fields)
                    elif isinstance(fields, list):
                        Bool += fields
                elif "str" in left:
                    pass    # every field is already in string in csv
            elif "read from csv" == left:
                var_name = right.strip()

        with open(filepath, "r") as csv_file:
            if structure == "list of dictionaries":
                csv_read_data = csv.DictReader(csv_file, delimiter=delimiter)
                # data_to_save = [line for line in csv_read_data]
                if csv_read_data.fieldnames[0].startswith("\u00ef\u00bb\u00bf"):
                    csv_read_data.fieldnames[0] = csv_read_data.fieldnames[0][3:]
                data_to_save = []
                not_exist = []
                for line in csv_read_data:
                    if allowed_list is not None:
                        temp = {}
                        for i in line:
                            if i in allowed_list:
                                temp[i] = line[i]
                        line = temp
                    if map_key_names is not None:
                        for i in map_key_names:
                            if i in line:
                                line[map_key_names[i]] = line.pop(i)
                    if Integer:
                        for i in Integer:
                            if i in line:
                                try:
                                    line[i] = int(line[i])
                                except:
                                    CommonUtil.ExecLog("", "Could not convert '%s' into integer of '%s' key. Keeping as it is" % (line[i], i), 2)
                            elif i not in not_exist:
                                not_exist.append(i)
                                CommonUtil.ExecLog("", "'%s' key does not exist for converting to integer", 2)
                    if Float:
                        for i in Float:
                            if i in line:
                                try:
                                    line[i] = float(line[i])
                                except:
                                    CommonUtil.ExecLog("", "Could not convert '%s' into float of '%s' key. Keeping as it is" % (line[i], i), 2)
                            elif i not in not_exist:
                                not_exist.append(i)
                                CommonUtil.ExecLog("", "'%s' key does not exist for converting to float" % i, 2)
                    if Bool:
                        for i in Bool:
                            if i in line:
                                try:
                                    val = line[i].strip().lower()
                                    if val == "true":
                                        line[i] = True
                                    elif val == "false":
                                        line[i] = False
                                    else:
                                        CommonUtil.ExecLog("", "Could not convert '%s' into boolean of '%s' key. Keeping as it is" % (line[i], i), 2)
                                except:
                                    CommonUtil.ExecLog("", "Could not convert '%s' into boolean of '%s' key. Keeping as it is" % (line[i], i), 2)
                            elif i not in not_exist:
                                not_exist.append(i)
                                CommonUtil.ExecLog("", "'%s' key does not exist for converting to boolean" % i, 2)
                    data_to_save.append(line)
        CommonUtil.ExecLog(sModuleInfo, "Extracted CSV data with '%s' delimiter and saved data as %s format" % (delimiter, structure), 1)
        sr.Set_Shared_Variables(var_name, data_to_save)
        return "passed"

    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def csv_write(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        filepath = None
        value = ""
        structure = "list of lists"
        for left, _, right in data_set:
            left = left.lower().strip()
            if "file path" == left:
                filepath = right.strip()
                # Expand ~ (home directory of user) to absolute path.
                if "~" in filepath:
                    filepath = Path(os.path.expanduser(filepath))
                filepath = Path(filepath)
            elif "structure of the variable" == left:
                pass    # "list of dictionaries" for now. Will implement more structures in future
            elif "write into csv" == left:
                value = right.strip()

        with open(filepath, "w", newline='') as csv_file:
            if structure == "list of lists":
                value = CommonUtil.parse_value_into_object(value)
                if not (type(value) == list and type(value[0]) == list):
                    CommonUtil.ExecLog(sModuleInfo, "The structure of the value is not 'list of lists'", 3)
                    return "zeuz_failed"
                writer = csv.writer(csv_file)
                writer.writerows(value)
                # for each in value:
                #     writer.writerow(each)

        CommonUtil.ExecLog(sModuleInfo, "Data successfully writen in CSV file", 1)
        return "passed"

    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def yaml_read(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        filepath = None
        var_name = ""
        for left, _, right in data_set:
            left = left.lower().strip()
            if "file path" == left:
                filepath = right.strip()
                # Expand ~ (home directory of user) to absolute path.
                if "~" in filepath:
                    filepath = Path(os.path.expanduser(filepath))
                filepath = Path(filepath)
            elif "read from yaml" == left:
                var_name = right.strip()

        with open(filepath) as yaml_file:
            data_to_save = yaml.load(yaml_file, Loader=yaml.FullLoader)

        CommonUtil.ExecLog(sModuleInfo, "Extracted yaml data successfully", 1)
        return sr.Set_Shared_Variables(var_name, data_to_save)

    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def yaml_write(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        filepath = None
        value = ""
        for left, _, right in data_set:
            left = left.lower().strip()
            if "file path" == left:
                filepath = right.strip()
                # Expand ~ (home directory of user) to absolute path.
                if "~" in filepath:
                    filepath = Path(os.path.expanduser(filepath))
                filepath = Path(filepath)
            elif "write into yaml" == left:
                value = CommonUtil.parse_value_into_object(right)

        with open(filepath, 'w') as yaml_file:
            yaml.dump(value, yaml_file, sort_keys=False)

        CommonUtil.ExecLog(sModuleInfo, "yaml data was written successfully", 1)
        return "passed"

    except:
        return CommonUtil.Exception_Handler(sys.exc_info())

@logger
def text_write(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        filepath = None
        value = ""
        line_no = None
        operation = "overwrite"
        for left, _, right in data_set:
            left = left.lower().strip()
            if "file path" == left:
                filepath = right.strip()

            elif "line no" == left:
                line_no = CommonUtil.parse_value_into_object(right.strip())
            elif "write into text file" == left:
                value = right
            elif "operation" == left:
                Right = right.strip().lower()
                if Right == "append":
                    operation = Right
                elif Right in ("overwrite", "rewrite", "new"):
                    pass
                else:
                    CommonUtil.ExecLog(sModuleInfo, 'We only support "New", "Overwrite" and "Append" operations', 3)
                    return "zeuz_failed"

        # Expand ~ (home directory of user) to absolute path.
        if "~" in filepath:
            filepath = Path(os.path.expanduser(filepath))

        filepath = Path(filepath)

        if line_no is not None:
            with open(filepath) as text_file:
                lines = text_file.readlines()
            if not value.endswith("\n"):
                value = value + "\n"
            lines[line_no] = value
            with open(filepath, "w") as text_file:
                text_file.writelines(lines)
            CommonUtil.ExecLog(sModuleInfo, "%s no line of %s was changed with the given text successfully" % (str(line_no), str(filepath)), 1)

        elif operation == "append":
            exist = os.path.exists(filepath)
            with open(filepath, 'a') as text_file:
                text_file.write(value)
            if exist:
                CommonUtil.ExecLog(sModuleInfo, "Appended the given text into: %s" % str(filepath), 1)
            else:
                CommonUtil.ExecLog(sModuleInfo, "The file does not exist so creating a new file into: %s" % str(filepath), 1)

        elif operation == "overwrite":
            exist = os.path.exists(filepath)
            with open(filepath, 'w') as text_file:
                text_file.write(value)
            if exist:
                CommonUtil.ExecLog(sModuleInfo, "Overwritten the given text into: %s" % str(filepath), 1)
            else:
                CommonUtil.ExecLog(sModuleInfo, "The file does not exist so creating a new file into: %s" % str(filepath), 1)

        return "passed"

    except:
        return CommonUtil.Exception_Handler(sys.exc_info())

@logger
def modify_datetime(data_set):
    """
    This action allows you to modify the date and time of a given datetime 
    object or today's date.
    """
    
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    from datetime import datetime, timedelta
    from dateutil import parser

    data = None
    var_name = None
    date_format = None

    fields = ["years", "months", "days", "hours", "minutes", "seconds"]

    def perform_mod(op, val, t):
        """
        op: one of the "fields" values.
        t: datetime object
        val: value to set.
        """

        try:
            converted_val = int(val)

            if val[0] in ("+", "-",):
                # Convert years and months to days, since timedelta does not
                # support them.
                # WARNING: This does not take into account the differences
                # of days in different months (28, 29, 30, 31). It also does
                # not take into account whether the year is a leap year.
                if op == "months":
                    converted_val *= 30
                    op = "days"
                elif op == "years":
                    converted_val *= 365
                    op = "days"

                # A relative change of datetime is requested
                delta = timedelta(**{op: converted_val})
                t += delta
            else:
                # A fixed change of datetime is requested
                t = t.replace(**{op[:-1]: converted_val})

        except:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Failed to modify the '%s' of the given datetime: '%s'\n"
                "Invalid value: %s" % (t, t, val),
                3
            )
            traceback.print_exc()

        return t

    for left, mid, right in data_set:
        left = left.strip().lower()

        if "data" in left:
            if right.strip().lower() == "today":
                data = datetime.today()
            else:
                data = parser.parse(right.strip())
            continue
        if "action" in mid:
            var_name = right.strip()
            continue
        if "format" in left:
            date_format = right
            continue

        right = right.strip()
        if left in fields:
            data = perform_mod(left, right, data)

    if date_format:
        data = data.strftime(date_format)
    else:
        data = str(data)

    CommonUtil.ExecLog(sModuleInfo, "Modified datetime. New value: %s" % data, 1)
    return sr.Set_Shared_Variables(var_name, data)


@logger
def replace_string(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        src_str = ""
        old_value = ""
        new_value = ""
        var_name = None

        for left, mid, right in data_set:
            left = left.lower().strip()
            if "source" in left:
                src_str = CommonUtil.parse_value_into_object(right)
                if type(src_str) != str:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Got a %s object to split. Converting it to string before splitting" % type(src_str).__name__,
                        2)
                    src_str = str(src_str)
            elif "find" in left:
                old_value = CommonUtil.parse_value_into_object(right)
            elif "replace with" in left:
                new_value = CommonUtil.parse_value_into_object(right)
            elif "action" in mid:
                var_name = right

        result_str = src_str.replace(old_value, new_value)

        CommonUtil.ExecLog(sModuleInfo, "Replaced '%s' with '%s'" % (old_value, new_value), 1)
        return sr.Set_Shared_Variables(var_name, result_str)

    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def delete_mail_action(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        imap_host = ""
        imap_user = ""
        select_mailbox = ""
        imap_pass = ""
        subject_to_check = ""
        body = ""
        sender_email = ""
        rcvremail = ""
        flagged_email =""
        check_email =""
        exact_date = ""
        after_date = ""
        before_date = ""

        for left, mid, right in data_set:
            left = left.lower()
            right = right.strip()

            if "imap host" in left:
                imap_host = right
            elif "imap user" in left:
                imap_user = right

            elif "inbox" in left:
                select_mailbox = right

            elif "imap pass" in left:
                imap_pass = right

            elif "subject" in left:
                subject_to_check = right
            elif "text" in left:
                body = right
            elif "sender email" in left:
                sender_email = right
            elif "receiver email" in left:
                rcvremail = right
            elif "flagged email" in left:
                flagged_email = right
            elif "checked email" in left:
                check_email = right
            elif "exact date" in left:
                exact_date = right
            elif "after date" in left:
                after_date = right
            elif "before date" in left:
                before_date = right

        if imap_host == "" or imap_user == "" or imap_pass == ""  or select_mailbox == "" :
            CommonUtil.ExecLog(
                sModuleInfo,
                "please provide the imap credentials for your mail server, see action help",
                3,
            )

            return "zeuz_failed"
        result = delete_mail(
            imap_host,
            imap_user,
            select_mailbox,
            imap_pass,
            subject_to_check,
            body,
            sender_email,
            rcvremail,
            flagged_email,
            check_email,
            exact_date,
            after_date,
            before_date
        )
        print(result)

        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def save_mail_action(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        imap_host = ""
        imap_user = ""
        select_mailbox = ""
        imap_pass = ""
        subject_to_check = ""
        body = ""
        sender_email = ""
        rcvremail = ""
        flagged_email =""
        check_email =""
        exact_date = ""
        after_date = ""
        before_date = ""
        variable_name = None

        for left, mid, right in data_set:

            left = left.lower()
            right = right.strip()

            if "imap host" in left:
                imap_host = right
            elif "imap user" in left:
                imap_user = right

            elif "inbox" in left:
                select_mailbox = right

            elif "imap pass" in left:
                imap_pass = right

            elif "subject" in left:
                subject_to_check = right
            elif "text" in left:
                body = right
            elif "sender email" in left:
                sender_email = right
            elif "receiver email" in left:
                rcvremail = right
            elif "flagged email" in left:
                flagged_email = right
            elif "checked email" in left:
                check_email = right
            elif "exact date" in left:
                exact_date = right
            elif "after date" in left:
                after_date = right
            elif "before date" in left:
                before_date = right
            elif "action" in mid:
                variable_name = right.strip()

        if imap_host == "" or imap_user == "" or imap_pass == ""  or select_mailbox == "" :
            CommonUtil.ExecLog(
                sModuleInfo,
                "please provide the imap credentials for your mail server, see action help",
                3,
            )
        if variable_name =="":
            CommonUtil.ExecLog(
                sModuleInfo,
                "please provide variable name",
                3,
            )
            return "zeuz_failed"
        result = save_mail(
            imap_host,
            imap_user,
            select_mailbox,
            imap_pass,
            subject_to_check,
            body,
            sender_email,
            rcvremail,
            flagged_email,
            check_email,
            exact_date,
            after_date,
            before_date
        )

        CommonUtil.ExecLog(
            sModuleInfo,
            str(result),
            1,
        )
        variable_value = result

        sr.Set_Shared_Variables(variable_name, variable_value)
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def search_and_save_text(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        variable_name = None
        data = None
        user_given_data = None

        for left, mid, right in data_set:
            left = left.strip().lower()
            if "pattern to match" in left:
                user_given_data = right
            elif "data" in left:
                data = CommonUtil.parse_value_into_object(right)
            elif "action" in mid:
               variable_name = right.strip()

        variable_value = re.findall(user_given_data, data)
        sr.Set_Shared_Variables(variable_name, variable_value)
        return "passed"

    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def custom_step_duration(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        for left, mid, right in data_set:
            if "action" in mid:
               value = right.strip()
        dot = value.count(".")
        if dot == 0:
            value += ".000"
        elif dot != 1:
            CommonUtil.ExecLog(sModuleInfo, "Please provide in valid time format- HH:MM:SS.mmm", 3)
            return "zeuz_failed"
        else:
            value = value.split(".")
            value = value[0] + "." + str(round(float("." + value[-1]), 3))[2:]
            value += "0" * (3-len(value.split(".")[-1]))
        colon = 2 - value.count(":")
        if colon < 0:
            CommonUtil.ExecLog(sModuleInfo, "Please provide in valid time format- HH:MM:SS.mmm", 3)
            return "zeuz_failed"
        for i in range(colon):
            value = "00:" + value
        CommonUtil.custom_step_duration = value
        CommonUtil.ExecLog(sModuleInfo, "%s is set as step duration" % value, 1)
        return "passed"

    except:
        return CommonUtil.Exception_Handler(sys.exc_info())

