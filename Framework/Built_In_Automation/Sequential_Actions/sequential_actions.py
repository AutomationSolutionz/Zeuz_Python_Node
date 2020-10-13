"""
    Sequential Actions - Main Functions
    Function: Handles incoming step data and distributes it to the specified functions
    
    Instructions for adding new functionality
        Adding new actions:
            Add to the actions dictionary - module and name must be lowercase with single spaces, function should be the exact spelling of the function name
            
        Adding new Sub-Field keywords
            Add to the action_suport list - must be lowercase with single spaces
            
        Adding a new dynamically called module
            Add to the load_sa_modules() function, follow same format as other sections
"""

# Dictionary of supported actions and their respective modules
# Rules: Action NAME must be lower case, no underscores, single
# spaces, no trailing whitespace. Module names must match those used
# in load_sa_modules()
# Common module: These are functions that are common to multiple Built
# In Functions, which have special handling. See common_functions.py
# where they are stored for more information.
# Caveat: Modules that are common to more than one built in function
# are listed here as with the module set to "common". If there is a
# "common" function, and another module with the same name created
# here, there may be a conflict, and the wrong function may execute

from .action_declarations.info import actions, action_support, supported_platforms

# Import modules
import inspect, subprocess
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from . import common_functions as common  # Functions that are common to all modules
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from Framework.Built_In_Automation.Shared_Resources import LocateElement
from Framework.Utilities import CommonUtil
from Framework.Utilities.CommonUtil import (
    passed_tag_list,
    failed_tag_list,
)  # Allowed return strings, used to normalize pass/fail


MODULE_NAME = inspect.getmodulename(__file__)

# Recall dependency, if not already set
dependency = None
if sr.Test_Shared_Variables(
    "dependency"
):  # Check if driver is already set in shared variables
    dependency = sr.Get_Shared_Variables("dependency")  # Retreive appium driver

# Initialize bypass data set (need to be global, so separate test cases can access them)
bypass_data_set = []
bypass_row = []
loaded_modules = []
load_testing = False
loop_result_for_load_testing = True
thread_pool = None

# Get node ID and set as a Shared Variable
machineInfo = CommonUtil.MachineInfo()  # Create instance
node_id = machineInfo.getLocalUser()  # Get Username+Node ID
sr.Set_Shared_Variables(
    "node_id", node_id, protected=True
)  # Save as protected shared variable


def load_sa_modules(
    module,
):  # Load module "AS" must match module name we get from step data (See actions variable above)
    """ Dynamically loads modules when needed """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    try:
        global loaded_modules
        loaded_modules.append(
            module
        )  # Save the module name - we need to check it under certain circumstances

        if module == "common":
            pass  # Already imported at top of this file
        elif module == "database":
            global database
            from Framework.Built_In_Automation.Database import (
                BuiltInFunctions as database
            )
        elif module == "appium":
            global appium
            from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium import (
                BuiltInFunctions as appium,
            )
        elif module == "selenium":
            global selenium
            from Framework.Built_In_Automation.Web.Selenium import (
                BuiltInFunctions as selenium,
            )
        elif module == "rest":
            global rest
            from Framework.Built_In_Automation.Web.REST import BuiltInFunctions as rest
        elif module == "utility":
            global utility
            from Framework.Built_In_Automation.Built_In_Utility.CrossPlatform import (
                BuiltInUtilityFunction as utility,
            )
        elif module == "xml":
            global xml
            from Framework.Built_In_Automation.XML import BuiltInFunctions_XML as xml
        elif module == "desktop":
            global desktop
            from Framework.Built_In_Automation.Desktop.CrossPlatform import (
                BuiltInFunctions as desktop,
            )
        elif module == "windows":
            global windows
            from Framework.Built_In_Automation.Desktop.Windows import (
                BuiltInFunctions as windows,
            )
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Invalid sequential actions module: %s" % module, 3
            )
            return "failed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())
    return "passed"


def write_browser_logs():
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if sr.Test_Shared_Variables("selenium_driver"):
            driver = sr.Get_Shared_Variables("selenium_driver")
            for browser_log in driver.get_log("browser"):
                CommonUtil.ExecLog(sModuleInfo, browser_log["message"], 6)
    except Exception as e:
        print("Browser Log Exception: {}".format(e))
        pass


def Sequential_Actions(
    step_data,
    _dependency=None,
    _run_time_params=None,
    _file_attachment=None,
    _temp_q="",
    screen_capture="Desktop",
    _device_info=None,
    debug_actions=None,
):
    """ Main Sequential Actions function - Performs logical decisions based on user input """

    if _device_info is None:
        _device_info = {}
    if _file_attachment is None:
        _file_attachment = {}
    if _run_time_params is None:
        _run_time_params = {}
    if _dependency is None:
        _dependency = {}

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)
    # Initialize
    try:
        # Set dependency, file_attachemnt, run_time_parameters as global variables
        global dependency, file_attachment, device_details, run_time_params
        dependency, file_attachment, device_details, run_time_params = {}, {}, {}, {}
        if _dependency != {}:
            dependency = _dependency  # Save to global variable
            sr.Set_Shared_Variables(
                "dependency", _dependency, protected=True
            )  # Save in Shared Variables

        if _file_attachment != {}:  # If a file attachment was passed
            file_attachment = _file_attachment  # Save as a global variable
            sr.Set_Shared_Variables(
                "file_attachment", _file_attachment, protected=True
            )  # Add entire file attachment dictionary to Shared Variables
            for (
                file_attachment_name
            ) in (
                _file_attachment
            ):  # Add each attachment as it's own Shared Variable, so the user can easily refer to it
                sr.Set_Shared_Variables(
                    file_attachment_name, _file_attachment[file_attachment_name]
                )

        if _run_time_params != {}:
            run_time_params = _run_time_params  # Save to global variable
            sr.Set_Shared_Variables(
                "run_time_params", _run_time_params, protected=True
            )  # Save in Shared Variables
            for (
                run_time_params_name
            ) in (
                run_time_params
            ):  # Add each parameter as it's own Shared Variable, so the user can easily refer to it
                sr.Set_Shared_Variables(
                    run_time_params_name, run_time_params[run_time_params_name]
                )

        if (
            _device_info != {}
        ):  # If any devices and their details were sent by the server, save to shared variable
            device_info = _device_info
            sr.Set_Shared_Variables("device_info", device_info, protected=True)

        # Set screen capture type (desktop/mobile) as shared variable, so TakeScreenShot() can read it
        if screen_capture != None and screen_capture != "None":
            sr.Set_Shared_Variables(
                "screen_capture", screen_capture.lower().strip()
            )  # Save the screen capture type
            CommonUtil.set_screenshot_vars(
                sr.Shared_Variable_Export()
            )  # Get all the shared variables, and pass them to CommonUtil

        # Set default variables (Must be defined here in case anyone destroys all shared variables)
        sr.Set_Shared_Variables(
            "element_wait", 10
        )  # Default time for get_element() to find the element

        # Prepare step data for processing
        step_data = common.unmask_step_data(step_data)
        step_data = common.sanitize(step_data)  # Sanitize Sub-Field
        step_data = common.adjust_element_parameters(
            step_data, supported_platforms
        )  # Parse any mobile platform related fields
        if step_data in failed_tag_list:
            return "failed"
        if common.verify_step_data(step_data) in failed_tag_list:
            return "failed"  # Verify step data is in correct format
    except:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error during Sequential Actions startup"
        )

    # Process step data
    # save the full step data in share variables

    sr.Set_Shared_Variables("step_data", step_data, protected=True)
    result, skip_for_loop = Run_Sequential_Actions(
        [], debug_actions
    )  # empty list means run all, instead of step data we want to send the dataset no's of the step data to run
    write_browser_logs()

    global load_testing, thread_pool
    # finish all thread for load tetsing
    if load_testing:
        thread_pool.shutdown(wait=True)

    return result

deprecateLog = True
def get_data_set_nums(action_value):
    try:
        data_set_nums = []
        global deprecateLog
        if "run" in action_value or "#" in action_value.lower() and deprecateLog:
            deprecateLog = False
            CommonUtil.ExecLog(
                "",
                "remove 'action#', 'run'. This one is older syntax and will be removed on a later period. Try the simple syntax format writen in document",
                2,
            )
            splitted = str(action_value).split(",")
            for each in splitted:
                try:
                    string = str(each).split("#")[1].strip()
                    if string.endswith(")"):
                        string = string[:-1]
                    elif " " in string:
                        string = string.split(" ")[0]
                    data_set_nums.append(int(string) - 1)
                except:
                    pass
        elif "if" in action_value.lower():
            data = action_value.lower().replace("if", "").replace("pass", "").replace("fail", "").replace("ed", "").replace(" ", "")
            data_set_nums.append(int(data)-1)
        else:
            splitted = str(action_value).strip().split(",")
            for each in splitted:
                try:
                    if "-" in each:
                        start, end = each.replace(" ","").split("-")
                        for i in range(int(start), int(end)+1):
                            data_set_nums.append(i-1)
                    elif each.strip().lower() in ("pass", "passed"):
                        data_set_nums.append("p")
                        break
                    elif each.strip().lower() in ("fail", "failed"):
                        data_set_nums.append("f")
                        break
                    else:
                        string = each.strip()
                        data_set_nums.append(int(string)-1)
                except:
                    pass

        return data_set_nums
    except:
        return []


def Handle_Conditional_Action(step_data, data_set_no):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        data_set = step_data[data_set_no]
        next_level_step_data = []
        inner_skip, outer_skip = [], []
        condition_matched = False
        if_exists = False
        data_set = common.shared_variable_to_value(data_set)
        global deprecateLog
        deprecateLog = True
        if data_set in failed_tag_list:
            return "failed"

        for left, _, right in data_set:
            statement = ""
            operator = ""
            operators = {"==": 0, "!=": 0, "<=": 0, ">=": 0, ">": 0, "<": 0}
            statements = ("else if", "else", "if")
            for i in statements:
                if left.lower().find(i) == 0:
                    statement = i
                    break
            for i in operators:
                if i in left:
                    operators[i] += 1
            operators["<"] -= operators["<="]
            operators[">"] -= operators[">="]

            if statement not in statements:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Specify a statement among (if, else if, else) and add a <single space> after that",
                    3,
                )
                return "failed"
            if sum(operators.values()) == 0 and statement != "else":
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Specify an operator among (==, !=, <, >, <=, >=) and add a <single space> before and after the operator",
                    3,
                )
                return "failed"
            elif sum(operators.values()) == 1:
                for i in operators:
                    if operators[i] == 1:
                        operator = i
                        break
            else:
                # need regex to handle more than one operators to separate operator and right/left values
                pass

            try:
                """Actual format: Statement <single space> Lvalue <single space> operator <single space> Rvalue
                Lvalue and Rvalue can have spaces at starting or ending so don't try stripping them. it can manipulate
                their actual values. Suppose, %|XY|% = "Hello " stripping will remove the last space"""

                if statement != "else":
                    Lvalue, Rvalue = left[len(statement + " "):].split(operator)  # remove "if "
                    Lvalue = Lvalue[:-1] if Lvalue[-1] == " " else Lvalue  # remove 1 space before the operator
                    Rvalue = Rvalue[1:] if Rvalue[0] == " " else Rvalue  # remove 1 space after the operator
                    Lvalue, Rvalue = CommonUtil.parse_value_into_object(Lvalue), CommonUtil.parse_value_into_object(Rvalue)
            except:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Couldn't parse Left and Right values",
                    3,
                )
                return "failed"

            def check_operators():
                nonlocal outer_skip, next_level_step_data, condition_matched
                if statement == "else":
                    if not condition_matched:
                        condition_matched = True
                        for i in get_data_set_nums(str(right).strip()):
                            next_level_step_data.append(i)
                        outer_skip += next_level_step_data
                    else:
                        outer_skip += get_data_set_nums(str(right).strip())

                elif operator == "==":
                    if Lvalue == Rvalue and not condition_matched:
                        condition_matched = True
                        for i in get_data_set_nums(str(right).strip()):
                            next_level_step_data.append(i)
                        outer_skip += next_level_step_data
                    else:
                        outer_skip += get_data_set_nums(str(right).strip())
                elif operator == "!=":
                    if Lvalue != Rvalue and not condition_matched:
                        condition_matched = True
                        for i in get_data_set_nums(str(right).strip()):
                            next_level_step_data.append(i)
                        outer_skip += next_level_step_data
                    else:
                        outer_skip += get_data_set_nums(str(right).strip())
                elif operator == "<=":
                    if Lvalue <= Rvalue and not condition_matched:
                        condition_matched = True
                        for i in get_data_set_nums(str(right).strip()):
                            next_level_step_data.append(i)
                        outer_skip += next_level_step_data
                    else:
                        outer_skip += get_data_set_nums(str(right).strip())
                elif operator == ">=":
                    if Lvalue >= Rvalue and not condition_matched:
                        condition_matched = True
                        for i in get_data_set_nums(str(right).strip()):
                            next_level_step_data.append(i)
                        outer_skip += next_level_step_data
                    else:
                        outer_skip += get_data_set_nums(str(right).strip())
                elif operator == "<":
                    if Lvalue < Rvalue and not condition_matched:
                        condition_matched = True
                        for i in get_data_set_nums(str(right).strip()):
                            next_level_step_data.append(i)
                        outer_skip += next_level_step_data
                    else:
                        outer_skip += get_data_set_nums(str(right).strip())
                elif operator == ">":
                    if Lvalue > Rvalue and not condition_matched:
                        condition_matched = True
                        for i in get_data_set_nums(str(right).strip()):
                            next_level_step_data.append(i)
                        outer_skip += next_level_step_data
                    else:
                        outer_skip += get_data_set_nums(str(right).strip())

            if statement == "if":
                if_exists = True
                condition_matched = False
                check_operators()
            elif statement == "else if":
                if not if_exists:
                    CommonUtil.ExecLog(sModuleInfo, "No 'if' statement found. Please define a 'if' statement first", 3)
                    return "failed", []
                check_operators()
            elif statement == "else":
                if not if_exists:
                    CommonUtil.ExecLog(sModuleInfo, "No 'if' statement found. Please define a 'if' statement first", 3)
                    return "failed", []
                check_operators()

        while "f" in outer_skip: outer_skip.remove("f")
        while "p" in outer_skip: outer_skip.remove("p")
        if next_level_step_data == []:
            CommonUtil.ExecLog(
                sModuleInfo,
                "No conditions matched. Skipping action %s" % [i+1 for i in outer_skip],
                2,
            )

        for data_set_index in next_level_step_data:
            if data_set_index in ("p", "f"):
                outer_skip = [i for i in range(len(step_data))]
                CommonUtil.ExecLog(sModuleInfo, "Step Exit called. Stopping Test Step.", 1)
                return "passed" if data_set_index == "p" else "failed", outer_skip
            elif data_set_index >= len(step_data):
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "You did not define action %s. So skipping this action index" % str(data_set_index+1),
                    2
                )
                continue
            elif data_set_index == data_set_no:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "You are running an if else action within another if else action. It may create infinite recursion in some cases",
                    2
                )
            if data_set_index not in inner_skip:
                result, skip = Run_Sequential_Actions(
                    [data_set_index]
                ) # Running
                inner_skip = list(set(inner_skip+skip))
                outer_skip = list(set(outer_skip + inner_skip))
                if result in failed_tag_list:
                    return result, outer_skip

        CommonUtil.ExecLog(sModuleInfo, "Conditional action handled successfully", 1)
        return "passed", outer_skip
    except:
        CommonUtil.ExecLog(sModuleInfo, "Error while handling conditional action", 3)
        return CommonUtil.Exception_Handler(sys.exc_info()), []


def Handle_While_Loop_Action(step_data, data_set_no):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        data_set = step_data[data_set_no]
        loop_this_data_sets = []
        passing_data_sets = []
        failing_data_sets = []
        outer_skip, inner_skip = [], []
        max_no_of_loop = 1
        operand_matching = ""
        var_name, var_value = "", ""
        deprecate_log = True
        global deprecateLog
        deprecateLog = True
        data_set = common.shared_variable_to_value(data_set)
        if data_set in failed_tag_list:
            return "failed", []

        for row in data_set:
            if row[0].strip().lower() == "run actions":
                loop_this_data_sets = get_data_set_nums(row[2].strip())
                outer_skip += loop_this_data_sets
            elif row[0].strip().lower() == "repeat":
                max_no_of_loop = int(row[2].strip())
            elif row[0].strip().lower() == "exit loop":
                value = row[2].strip()
                if "pass" in value.lower():
                    passing_data_sets += get_data_set_nums(value)
                elif "fail" in value.lower():
                    failing_data_sets += get_data_set_nums(value)
                elif "==" in value and "optional loop settings" in row[1].strip().lower():
                    operand_matching = row
                elif "==" in value:
                    boolean_data_list = value.split("==")
                    var_name = boolean_data_list[0].split("%|")[1].split("|%")[0]
                    var_value = boolean_data_list[1].strip().lower()
                if "loop settings" == row[1].strip().lower() and deprecate_log:
                    deprecate_log = False
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Use 'optional loop setting' instead of 'loop settings' to get our updated feature. Try the simple syntax format writen in document",
                        2,
                    )
        if loop_this_data_sets == []:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Loop action step data is invalid, please see action help for more info",
                3,
            )
            return "failed", []

        i = 0
        while i < max_no_of_loop:
            die = False
            for data_set_index in loop_this_data_sets:
                if data_set_index not in inner_skip:
                    if data_set_index >= len(step_data):
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "You did not define action %s. So skipping this action index" % str(data_set_index + 1),
                            2
                        )
                        while data_set_index in loop_this_data_sets: loop_this_data_sets.remove(data_set_index)
                        outer_skip = list(set(outer_skip + [data_set_index]))
                        continue
                    elif data_set_index == data_set_no:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "You are running an Loop action within the same Loop action. It may create infinite recursion in some cases",
                            2
                        )
                    result, skip = Run_Sequential_Actions(
                        [data_set_index]
                    )  # new edit: full step data is passed. [step_data[data_set_index]])
                    # Recursively call this function until all called data sets are complete
                    inner_skip = list(set(inner_skip + skip))
                    outer_skip = list(set(outer_skip + inner_skip))
                else:
                    continue
                if result in passed_tag_list and data_set_index in passing_data_sets:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Loop exit condition satisfied. Action %s passed. Exiting loop" % str(data_set_index+1),
                        1
                    )
                    die = True
                    break
                elif result in failed_tag_list and data_set_index in failing_data_sets:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Loop exit condition satisfied. Action %s failed. Exiting loop" % str(data_set_index+1),
                        1
                    )
                    die = True
                    break
                elif operand_matching != "":
                    operand_matching_2 = operand_matching[2][3:] if operand_matching[2][2] == " " else operand_matching[2][2:]
                    data = [(operand_matching[0], "optional parameter", operand_matching_2)]
                    RandL = common.shared_variable_to_value(data)[0][2]
                    Lvalue, Rvalue = RandL.split("==")
                    Lvalue = Lvalue[:-1] if Lvalue[-1] == " " else Lvalue  # remove 1 space before the operator
                    Rvalue = Rvalue[1:] if Rvalue[0] == " " else Rvalue  # remove 1 space after the operator
                    Lvalue, Rvalue = CommonUtil.parse_value_into_object(Lvalue), CommonUtil.parse_value_into_object(Rvalue)
                    if Lvalue == Rvalue:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Loop exit condition satisfied. Left and Right operands matched. Exiting loop",
                            1,
                        )
                        die = True
                        break
                elif var_name != "" and sr.Test_Shared_Variables(var_name):
                    shared_variable_value = str(sr.Get_Shared_Variables(var_name)).strip().lower()
                    if (shared_variable_value == var_value):
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Loop exit condition satisfied. Left and Right operands matched. Exiting loop",
                            1,
                        )
                        die = True
                        break
            if die:
                break
            i += 1

        CommonUtil.ExecLog(sModuleInfo, "Loop action handled successfully", 1)
        return "passed", outer_skip
    except:
        CommonUtil.ExecLog(sModuleInfo, "Error while handling loop action", 3)
        return "failed", []


def Run_Sequential_Actions(
    data_set_list=None, debug_actions=None
):  # data_set_no will used in recursive conditional action call
    if data_set_list is None:
        data_set_list = []
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        result = "failed"  # Initialize result
        skip = (
            []
        )  # List of data set numbers that have been processed, and need to be skipped, so they are not processed again
        logic_row = []  # Holds conditional actions
        skip_tmp = []  # Temporarily holds skip data sets
        skip_for_loop = []

        step_data = sr.Get_Shared_Variables("step_data")

        if step_data in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo, "Internal Error: Step Data not set in shared variable", 3
            )
            return "failed", skip_for_loop
        if data_set_list == []:  # run the full step data
            for i in range(len(step_data)):
                if debug_actions:
                    if str(i + 1) in debug_actions:
                        data_set_list.append(i)
                else:
                    data_set_list.append(i)

        for dataset_cnt in data_set_list:  # For each data set within step data
            CommonUtil.ExecLog(
                sModuleInfo,
                "\n********** Starting Action #%d **********\n" % (dataset_cnt + 1),
                4,
            )  # Offset by one to make it look proper
            data_set = step_data[dataset_cnt]  # Save data set to variable
            if dataset_cnt in skip:
                continue  # If this data set is in the skip list, do not process it

            if (
                CommonUtil.check_offline()
            ):  # Check if user initiated offline command from GUI
                CommonUtil.ExecLog(
                    sModuleInfo, "User requested Zeuz Node to go offline.", 2
                )
                return "failed", skip_for_loop

            for row in data_set:  # For each row of the data set
                action_name = row[1]  # Get Sub-Field

                # Don't process these suport items right now, but also don't fail
                if (
                    action_name.lower().strip() in action_support
                    and "custom" not in action_name
                ):
                    continue

                # If middle coloumn = bypass action, store the data set for later use if needed
                elif "bypass action" in action_name:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Bypass action found, storing data set for later use",
                        1,
                    )
                    global bypass_data_set, bypass_row
                    bypass_data_set.append(
                        data_set
                    )  # Save this data set - see "action" if block below for further processing
                    bypass_row.append(row)
                    result = "passed"

                # If middle column = action, call action handler, but always return a pass
                elif "optional action" in action_name:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Checking the optional action to be performed in the action row: %s"
                        % str(row),
                        0,
                    )
                    result = Action_Handler(
                        data_set, row
                    )  # Pass data set, and action_name to action handler
                    if result == "failed":
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Optional action failed. Returning pass anyway",
                            2,
                        )
                    result = "passed"

                # If middle column = conditional action, evaluate data set
                elif "conditional action" in action_name or "if else" in action_name:
                    if (
                        action_name.lower().strip() != "conditional action"
                        and action_name.lower().strip() != "if else"
                    ):  # old style conditional action
                        # CommonUtil.ExecLog(sModuleInfo,"Old style conditional action found", 1)
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Checking the logical conditional action to be performed in the conditional action row: %s"
                            % str(row),
                            0,
                        )
                        logic_row.append(
                            row
                        )  # Keep track of the conditional action row, so we can access it later
                        [
                            skip_tmp.append(int(x) - 1)
                            for x in row[2].replace(" ", "").split(",")
                        ]  # Add the processed data sets, executed by the conditional action to the skip list, so we can process the rest of the data sets (do this for both conditional actions)

                        # Only run this when we have two conditional actions for this data set (a true and a false preferably)
                        if len(logic_row) == 2:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Found 2 conditional actions - moving ahead with them",
                                1,
                            )
                            result = Conditional_Action_Handler(
                                data_set, row, logic_row
                            )  # send full data for recursive conditional call

                            CommonUtil.ExecLog(
                                sModuleInfo, "Conditional Actions complete", 1
                            )
                            if result in failed_tag_list:
                                CommonUtil.ExecLog(
                                    sModuleInfo,
                                    "Returned result from Conditional Action Failed",
                                    3,
                                )
                                return result, skip_for_loop
                            logic_row = (
                                []
                            )  # Unset this, so if there is another conditional action in the test step, we can process it
                            skip = skip_tmp  # Add to the skip list, now that processing is complete
                            skip_tmp = []
                    else:
                        result, to_skip = Handle_Conditional_Action(
                            step_data, dataset_cnt
                        )
                        skip += to_skip
                        skip_for_loop += to_skip
                        if result in failed_tag_list:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Returned result from Conditional Action Failed",
                                3,
                            )
                            return result, skip_for_loop
                        break

                # Simulate a while/for loop with the specified data sets
                elif "loop action" in action_name:
                    if action_name.lower().strip() not in (
                        "while loop action",
                        "for loop action",
                    ):  # old style loop action
                        # CommonUtil.ExecLog(sModuleInfo,"Old style loop action found. This will not be supported in 2020, please replace them with new loop actions",2)
                        result, skip_for_loop = Loop_Action_Handler(
                            data_set, row, dataset_cnt
                        )
                        skip = skip_for_loop

                        position_of_loop_action = dataset_cnt
                        set_of_actions_after_loop = range(
                            position_of_loop_action + 1, len(step_data)
                        )  # Collecting actions following the first loop action
                        for follow_cnt in set_of_actions_after_loop:
                            for follow_row in step_data[follow_cnt]:
                                if (
                                    "loop action" in follow_row[1]
                                ):  # Check if the action following the first loop in the set is a loop action
                                    if (
                                        str(follow_cnt + 1) in row[2]
                                    ):  # Check if this loop is being called by the first loop. Done to avoid skipping actions of loops in the step that are located after and outside of the first loop.
                                        for a in (
                                            follow_row[2]
                                            .strip(" nested ")
                                            .strip(" - ")
                                            .split(",")
                                        ):
                                            skip.append(int(a) - 1)
                                elif (
                                    "conditional action" in follow_row[1]
                                ):  # Check if the action following the first loop in the set is a conditional action
                                    if (
                                        str(follow_cnt + 1) in row[2]
                                    ):  # Check if this conditional is being called by the first loop. Done to avoid skipping actions of conditional actions in the step that are located after and outside of the first loop.
                                        for a in (
                                            follow_row[2]
                                            .strip(" nested ")
                                            .strip(" - ")
                                            .split(",")
                                        ):
                                            skip.append(int(a) - 1)

                        """
                        nested_action_skip = []  # skipping the steps that are nested  , we do not want to run them sequencially later
                        for row in data_set:
                            if row[0].lower() == 'nested action':
                                a = map(int, row[2].split(","))
                                for i in a:
                                    nested_action_skip.append(int(i) - 1)  # converting to index format by decreasing by 1 and converting string to number
                        skip = skip + nested_action_skip  #appending the nested actions to skip list  after the loop finish
                        """

                        if result in failed_tag_list:
                            return "failed", skip_for_loop
                elif "loop" in action_name:
                    if "while" in action_name.lower():
                        result, skip_for_loop = Handle_While_Loop_Action(
                            step_data, dataset_cnt
                        )
                    skip = list(set(skip + skip_for_loop))
                    if result in failed_tag_list:
                        return "failed", skip_for_loop
                    break

                # Special custom functions can be executed in a specified file
                elif "custom" in action_name:
                    CommonUtil.ExecLog(sModuleInfo, "Custom Action Start", 2)
                    if (
                        row[0].lower().strip() == "file"
                    ):  # User specified file to run from (only needed once)
                        # Try to find the image file
                        custom_file_name = row[2].strip()
                        if (
                            custom_file_name not in file_attachment
                            and os.path.exists(custom_file_name) == False
                        ):
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Could not find file attachment called %s, and could not find it locally"
                                % custom_file_name,
                                3,
                            )
                            return "failed", skip_for_loop
                        if custom_file_name in file_attachment:
                            custom_file_name = file_attachment[
                                custom_file_name
                            ]  # In file is an attachment, get the full path
                        CommonUtil.ExecLog(
                            sModuleInfo, "Custom file set to %s" % custom_file_name, 0
                        )

                        # Import the module
                        from imp import load_source

                        try:
                            global custom_module  # Need to remember this value between Test Steps
                            custom_mod_name = os.path.splitext(
                                os.path.basename(custom_file_name)
                            )[
                                0
                            ]  # Get module name by removing path and extension
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Importing %s from %s"
                                % (custom_mod_name, custom_file_name),
                                0,
                            )
                            custom_module = load_source(
                                custom_mod_name, custom_file_name
                            )  # Load module user specified
                            CommonUtil.ExecLog(sModuleInfo, "Import successful", 1)
                            result = "passed"
                        except:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Error occurred while importing: %s. It may have a compile error or an import naming issue"
                                % custom_file_name,
                                3,
                            )
                            return "failed", skip_for_loop

                    elif (
                        custom_module != ""
                    ):  # If custom module is set, then we are good to use it
                        # User specified filename already and it's imported, so we can move ahead with executing functions
                        custom_var = ""
                        custom_function = (
                            row[0].strip().replace("()", "").replace(" ", "")
                        )  # Function name, can't have brackets
                        if "=" in custom_function:
                            custom_var, custom_function = custom_function.split(
                                "="
                            )  # If shared variable name included with function, separate them
                        custom_params = (
                            row[2].strip().replace("'", "'")
                        )  # Escape single quotes in the parameters
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Executing function: %s with parameters: %s"
                            % (custom_function, custom_params),
                            0,
                        )
                        try:
                            custom_output = ""
                            exec(
                                "custom_output = custom_module.%s(%s)"
                                % (custom_function, custom_params)
                            )  # Execute the function from the custom module
                            if custom_output != "":
                                sr.Set_Shared_Variables(
                                    custom_var, custom_output
                                )  # Save output to user specified shared variable name
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Function executed successfully: %s"
                                % str(custom_output),
                                1,
                            )
                            result = "passed"
                        except Exception as e:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Failed to execute function %s from the custom module: %s"
                                % (custom_module, e),
                                3,
                            )
                            return "failed", skip_for_loop

                    else:  # Function executed but user didn't specify the file to import
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "No Python file specified for custom function execution. Expected a Data Set in the format of: 'file', 'custom', 'directory/filename'",
                            3,
                        )
                        return "failed", skip_for_loop

                # If middle column = action, call action handler
                elif (
                    "action" in action_name
                ):  # Must be last, since it's a single word that also exists in other action types
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Checking the action to be performed in the action row: %s"
                        % str(row),
                        0,
                    )
                    result = Action_Handler(
                        data_set, row
                    )  # Pass data set, and action_name to action handler
                    if row[0].lower().strip() == "step exit":
                        CommonUtil.ExecLog(
                            sModuleInfo, "Step Exit called. Stopping Test Step.", 1
                        )
                        skip_all = [i for i in range(len(step_data))]
                        return result, skip_all

                    # Check if user wants to store the result for later use
                    stored = False
                    for r in data_set:
                        if (
                            r[0].lower().strip() == "store"
                            and r[1].lower().strip() == "result"
                        ):  # If Field = store and Sub-Field = result
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Storing result for later use. Will not exit if action failed: %s"
                                % result,
                                1,
                            )
                            sr.Set_Shared_Variables(
                                r[2].strip(), result
                            )  # Use the Value as the shared variable name, and save the result
                            stored = True  # In the case of a failed result, skip the return that comes after this

                    # Check result of action handler and use bypass action if specified
                    if stored == False and result in failed_tag_list:
                        if (
                            bypass_data_set != []
                        ):  # User specified a bypass action, so let's try it before we fail
                            action_module = [
                                x for x in loaded_modules if str(x) in str(row[1])
                            ]  # Save module for the original action
                            for i in range(len(bypass_data_set)):
                                bypass_module = [
                                    x
                                    for x in loaded_modules
                                    if str(x) in str(bypass_row[i][1])
                                ]  # Save module for the bypass action
                                if action_module != bypass_module:
                                    CommonUtil.ExecLog(
                                        sModuleInfo,
                                        "Skipping bypass #%d because it's not the same module"
                                        % (i + 1),
                                        1,
                                    )
                                    continue

                                CommonUtil.ExecLog(
                                    sModuleInfo,
                                    "Action failed. Trying bypass #%d" % (i + 1),
                                    1,
                                )
                                result = Action_Handler(
                                    bypass_data_set[i], bypass_row[i]
                                )
                                if (
                                    result in failed_tag_list
                                ):  # This also failed, so chances are first failure was real
                                    continue  # Try the next bypass, if any
                                else:  # Bypass passed, which indicates there was something blocking the element in the first place
                                    CommonUtil.ExecLog(
                                        sModuleInfo,
                                        "Bypass passed. Retrying original action",
                                        1,
                                    )
                                    result = Action_Handler(
                                        data_set, row
                                    )  # Retry failed original data set
                                    if (
                                        result in failed_tag_list
                                    ):  # Still a failure, give up
                                        return "failed", skip_for_loop
                                    break  # No need to process more bypasses
                            if result in failed_tag_list:  # All bypass actions failed
                                CommonUtil.ExecLog(
                                    sModuleInfo, "All bypass actions failed", 3
                                )
                                return "failed", skip_for_loop
                        else:  # Yup, it's a failure, and no bypass specified
                            return "failed", skip_for_loop

                # Middle column not listed above, so data set is wrong
                else:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "The sub-field information is incorrect. Please provide accurate information on the data set(s).",
                        3,
                    )
                    return "failed", skip_for_loop

        # No failures, return result
        return result, skip_for_loop

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def Loop_Action_Handler(data, row, dataset_cnt):
    """ Performs a sub-set of the data set in a loop, similar to a for or while loop """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    try:
        skip = []
        result = True
        nested_loop = False
        nested_double = False
        max_retry = 50  # wil search for any elemnt this amount of time in while loop
        loop_method = None
        ### Create sub-set of step data that we will send to SA for processing
        try:
            if str(row[2]).strip().startswith("nested"):
                nested_loop = True
                row = (row[0], row[1], str(row[2]).split("-")[1])
            elif str(row[2]).strip().startswith("double nested"):
                nested_loop = True
                nested_double = True
                row = (row[0], row[1], str(row[2]).split("-")[1])
            sets = list(
                map(int, row[2].replace(" ", "").split(","))
            )  # Save data sets to loop
            sets = [x - 1 for x in sets]  # Convert data set numbers to array friendly
            new_step_data = []
            for i in sets:
                new_step_data.append(i)  # Create new sub-set with indexes of data sets
        except Exception as e:
            print(e)
            CommonUtil.ExecLog(
                sModuleInfo,
                "Loop format incorrect in Value field. Expected list of data sets. Eg: '2,3,4'",
                3,
            )
            return "failed", skip

        ### Determine loop type
        # Current types: Loop N times || Loop until Data_set #N = true/false
        try:  # Format of Field: true/false/pass/fail NUMBER - Eg: true 2 - If second data set results in true/pass, then stop loop
            loop_type, action_result = (
                row[0].lower().replace(",", " ").replace("  ", " ").split(" ")
            )  # True/False that we want to monitor as the result, and data set number to base output on
            action_result = (
                int(action_result) - 1
            )  # Bring user specified data set number into array format
            action_result = (
                action_result - dataset_cnt - 1
            )  # Calculate data set number of this data set in the new sub-set. -1 Because we are currently on the loop action, and this data set is not included in the sub-set
            if loop_type in passed_tag_list:
                loop_type = "passed"
            elif loop_type in failed_tag_list:
                loop_type = "failed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Loop format incorrect in Field field. Expected Field to contain 'true/false number'. Eg: true 2",
                    3,
                )
                return "failed", skip
            loop_len = 0  # Not used
            loop_method = "exit_on_dataset"
        except:
            try:  # Format of Field: NUMBER - Number of times to run, regardless of result
                loop_len = int(row[0])  # Number of times to loop
                loop_type = ""  # Must be blank
                action_result = ""  # Not used
                loop_method = "exact"
            except:
                try:
                    tmp = (
                        row[0].replace("%", "").replace("|", "").strip()
                    )  # Get shared variable name
                    tmp, action_result = tmp.replace(" ", "").split(
                        ","
                    )  # Split list var with var user wants to store iterations in
                    if sr.Test_Shared_Variables(
                        tmp
                    ):  # User provided a shared variable, which should be a list that we can loop through
                        loop_type = sr.Get_Shared_Variables(
                            tmp
                        )  # Retrieved shared variable value
                        loop_len = len(
                            loop_type
                        )  # Number of list items to cycle through

                        for r in data:
                            if r[0] == "repeat":
                                loop_len = int(str(r[2]).strip())

                        if loop_len == 0:
                            return "passed", skip
                        if action_result == "dictionary":
                            loop_method = "dict"
                            flat_list = (
                                []
                            )  # CONVERT dict to list of (k,v) tuple so that can be indexed easily
                            for key in loop_type:
                                flat_list.append((key, loop_type[key]))
                            loop_type = flat_list
                        else:
                            loop_method = "list"

                        if type(loop_type) not in (list, str):
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Shared Variable found for Loop action, but is not in list/str format, which is required.",
                                3,
                            )
                            return "failed"
                    else:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Could not find a valid loop format in the Field field. Valid formats: 'true/false number', 'number', 'shared variable name'",
                            3,
                        )
                        return "failed"
                except:
                    try:
                        true_or_false = (
                            str(row[0]).lower().strip()
                        )  # Number of times to loop
                        loop_type = ""  # Must be blank
                        action_result = ""  # Not used
                        if true_or_false.startswith("true"):
                            loop_method = "boolean"
                            loop_bool = True
                            try:
                                if "-" in true_or_false:
                                    max_retry = int(true_or_false.split("-")[1].strip())
                            except:
                                pass
                        elif true_or_false.startswith("false"):
                            loop_method = "boolean"
                            loop_bool = False
                            try:
                                if "-" in true_or_false:
                                    max_retry = int(true_or_false.split("-")[1].strip())
                            except:
                                pass
                        else:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Could not find a valid loop format in the Field field. Valid formats: 'true/false number', 'number', 'shared variable name'",
                                3,
                            )
                            return "failed", skip
                    except:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Could not find a valid loop format in the Field field. Valid formats: 'true/false number', 'number', 'shared variable name'",
                            3,
                        )

        def build_subset(new_step_data):
            result = Run_Sequential_Actions(new_step_data)
            if result in passed_tag_list or (
                type(result) == tuple and result[0] in passed_tag_list
            ):
                result = (
                    "passed"  # Make sure the result matches the string we set above
                )
            else:
                global load_testing
                if load_testing:
                    loop_result_for_load_testing = False
                result = "failed"
            return result

        ### Send sub-set to SA until we get our desired value or number of loops
        sub_set_cnt = 1  # Used in counting number of loops
        die = False  # Used to exit parent while loop

        global load_testing
        load_testing = False
        CommonUtil.load_testing = False
        normal_wait_time = 0
        total_time = 0
        distribution = []
        load_testing_interval = 0
        total_thread = 10

        if len(data) > 1 and loop_method == "exact":
            try:
                load_testing = True
                CommonUtil.load_testing = True
                total_range = 0
                total_percentage = 0
                for r in data:
                    if str(r[0]) == "total time":
                        total_time = int(str(r[2]).strip())
                    elif str(r[0]) == "total thread":
                        total_thread = int(str(r[2]).strip())
                    elif str(r[0]) == "show logs":
                        show_log_setting = str(r[2])
                        if show_log_setting in passed_tag_list:
                            CommonUtil.load_testing = False
                    elif str(r[0]) == "range":
                        l = str(r[2]).split(",")
                        start = int(l[0].split("-")[0].strip())
                        end = int(l[0].split("-")[1].strip())
                        percentage = int(l[1].strip())

                        if percentage > 100:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Step data for load testing is incorrect, range percentage can't be greater than 100",
                                3,
                                force_write=True,
                            )
                            return "failed"

                        if start > total_time or end > total_time:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Step data for load testing is incorrect, range start or end time can't be greater than total time",
                                3,
                                force_write=True,
                            )
                            return "failed"

                        distribution.append([start, end, percentage])

                        total_percentage += percentage
                        total_range += end - start

                if total_percentage > 100:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Step data for load testing is incorrect, total percentage of all ranges can't be greater than 100",
                        3,
                        force_write=True,
                    )
                    return "failed"

                # initialize thread pool
                if total_thread > 10:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Please use 'total thread' value with less or equal to 10",
                        3,
                        force_write=True,
                    )
                    return "failed"

                global thread_pool
                thread_pool = ThreadPoolExecutor(max_workers=total_thread)

                total_loop = loop_len

                if total_percentage != 100:
                    normal_wait_time = ((total_time - total_range) * 1.0) / (
                        total_loop * (100 - total_percentage) / 100.0
                    )
                else:
                    normal_wait_time = 0

                handled = 0
                last_time = 0

                i = 0
                while i < len(distribution):
                    start = distribution[i][0]
                    end = distribution[i][1]
                    percentage = distribution[i][2]
                    wait_time = ((end - start) * 1.0) / (
                        total_loop * percentage / 100.0
                    )

                    if distribution[i][0] != last_time:
                        if normal_wait_time == 0:
                            in_this_range = 0
                        else:
                            in_this_range = int((start - last_time) / normal_wait_time)
                        distribution.insert(
                            i, [handled, handled + in_this_range, normal_wait_time]
                        )
                        handled += in_this_range
                        i += 1

                    distribution[i][2] = wait_time
                    distribution[i][0] = handled
                    loop_in_this_range = int(total_loop * percentage / 100.0)
                    distribution[i][1] = handled + loop_in_this_range
                    last_time = end

                    handled += loop_in_this_range

                    i += 1

            except:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Step data for load testing is incorrect, correct format is START-END,"
                    "PERCENTAGE.. like 10-15,20.. That means between 10 to 15 second we "
                    "will iterate 20% of the loop",
                    3,
                    force_write=True,
                )
                return "failed"

        inside_interval = False
        load_testing_count = -1

        while (
            True
        ):  # We control the new sub-set of the step data, so we can examine the output
            CommonUtil.ExecLog(sModuleInfo, "Loop action #%d" % sub_set_cnt, 1)

            if loop_method == "exit_on_dataset":
                for ndc in range(
                    len(new_step_data)
                ):  # For each data set in the sub-set
                    if (
                        CommonUtil.check_offline()
                    ):  # Check if user initiated offline command from GUI
                        CommonUtil.ExecLog(
                            sModuleInfo, "User requested Zeuz Node to go Offline", 2
                        )
                        return "failed", skip

                    # Build the sub-set and execute
                    result = build_subset([new_step_data[ndc]])
                    if result in failed_tag_list:
                        return result, skip

                    # Check if we should exit now or keep going
                    if (
                        ndc == action_result and result == loop_type
                    ):  # If this data set that just returned is the one that we are watching AND it returned the result we want, then exit the loop
                        skip = sets  # Tell SA to skip these data sets that were in the loop once it picks up processing normally
                        die = True  # Exit while loop
                        break  # Stop processing sub-sets
                if die:
                    break  # Stop processing this while loop, and go back to regular SA

            elif loop_method == "exact":
                for ndc in range(
                    len(new_step_data)
                ):  # For each data set in the sub-set
                    # Build the sub-set and execute
                    if load_testing:
                        thread_pool.submit(build_subset, [new_step_data[ndc]])
                        if not loop_result_for_load_testing:
                            return result, skip
                    else:
                        result = build_subset([new_step_data[ndc]])
                        if result in failed_tag_list:
                            return result, skip

                # Check if we hit our set number of loops
                if (
                    sub_set_cnt >= loop_len
                ):  # If we hit out desired number of loops for this loop type, then exit
                    skip = sets  # Tell SA to skip these data sets that were in the loop once it picks up processing normally
                    break  # Stop processing sub-sets and exit while loop

            elif loop_method == "list":
                sr.Set_Shared_Variables(
                    action_result, loop_type[sub_set_cnt - 1]
                )  # Store list element into shared variable name user provided. Their step data should do what they want with it
                list_value = loop_type[sub_set_cnt - 1]
                if nested_loop:
                    i = 0
                    for each in list_value:
                        sr.Set_Shared_Variables(action_result + "_" + str(i), each)
                        i += 1

                for ndc in range(
                    len(new_step_data)
                ):  # For each data set in the sub-set
                    # Build the sub-set and execute
                    result = build_subset(
                        [new_step_data[ndc]]
                    )  # the dataset was conditional then break
                    if result in failed_tag_list:
                        return result, skip
                    if nested_double:
                        break

                # Check if we have processed all the list variables
                if sub_set_cnt >= loop_len:
                    skip = sets  # Tell SA to skip these data sets that were in the loop once it picks up processing normally
                    break  # Stop processing sub-sets and exit while loop

            elif loop_method == "dict":
                sr.Set_Shared_Variables("dict_key", loop_type[sub_set_cnt - 1][0])
                sr.Set_Shared_Variables(
                    "dict_value", loop_type[sub_set_cnt - 1][1]
                )  # Store list element into shared variable name user provided. Their step data should do what they want with it
                dict_value = loop_type[sub_set_cnt - 1][1]

                if nested_loop:
                    for k in dict_value:
                        sr.Set_Shared_Variables(k, dict_value[k])

                for ndc in range(
                    len(new_step_data)
                ):  # For each data set in the sub-set
                    # Build the sub-set and execute
                    result = build_subset([new_step_data[ndc]])
                    if result in failed_tag_list:
                        return result, skip
                    if nested_double:
                        break

                # Check if we have processed all the list variables
                if sub_set_cnt >= loop_len:
                    skip = sets  # Tell SA to skip these data sets that were in the loop once it picks up processing normally
                    break  # Stop processing sub-sets and exit while loop
            elif loop_method == "boolean":
                die = False
                combined_result = True
                for ndc in range(
                    len(new_step_data)
                ):  # For each data set in the sub-set
                    # Build the sub-set and execute
                    result = build_subset([new_step_data[ndc]])

                    if result in passed_tag_list:
                        combined_result = combined_result and True
                    else:
                        combined_result = combined_result and False

                    if loop_bool == True and not combined_result:
                        die = True
                        break

                    if (
                        ndc == len(new_step_data) - 1
                        and loop_bool == False
                        and combined_result
                    ):
                        die = True
                        break

                if die:
                    break

                # Check if we hit our max retry limit
                if (
                    sub_set_cnt >= max_retry
                ):  # If we hit out desired number of loops for this loop type, then exit
                    skip = sets  # Tell SA to skip these data sets that were in the loop once it picks up processing normally
                    break  # Stop processing sub-sets and exit while loop
            sub_set_cnt += 1  # Used for numerical loops only, keep track of how many times we've looped the sub-set

            # for load testing put wait here to achieve desired distribution
            if load_testing:
                load_testing_count += 1
                if inside_interval:
                    if (
                        load_testing_count < distribution[load_testing_interval][1]
                    ):  # current interval running
                        time.sleep(distribution[load_testing_interval][2])
                        # print "sleeping %f"%distribution[load_testing_interval][2]
                        continue
                    else:  # current interval finished
                        load_testing_interval += 1
                        inside_interval = False

                # all special ranges finished or elapsed time is less than the next range then use normal wait time
                if load_testing_interval >= len(distribution):
                    time.sleep(normal_wait_time)
                    # print "sleeping %f" % normal_wait_time
                elif load_testing_count < distribution[load_testing_interval][0]:
                    time.sleep(normal_wait_time)
                    # print "sleeping %f" % normal_wait_time
                else:  # new interval needs to be started
                    inside_interval = True
                    time.sleep(distribution[load_testing_interval][2])
                    # print "sleeping %f" % distribution[load_testing_interval][2]

        if load_testing:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Loop iterated %d times successfully" % sub_set_cnt,
                1,
                force_write=True,
            )

        return result, skip
    except Exception as e:
        return CommonUtil.Exception_Handler(sys.exc_info())


def Conditional_Action_Handler(data_set, row, logic_row):
    """ Process conditional actions, called only by Sequential_Actions() """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    # Get module and dynamically load it
    module = row[1].split(" ")[0]
    load_sa_modules(module)

    # Convert any shared variables into their strings
    data_set = common.shared_variable_to_value(data_set)
    if data_set in failed_tag_list:
        return "failed"

    # Test if data set contains the recall line, and if so, get the saved result from the previous action
    try:
        stored = False
        for row in data_set:
            if (
                row[0].lower().strip() == "recall"
                and row[1].lower().strip() == "result"
            ):  # If Field = recall and Sub-Field = result
                CommonUtil.ExecLog(sModuleInfo, "Recalled result: %s" % str(row[2]), 1)
                stored = True
                result = row[
                    2
                ]  # Retrieve the saved result (already converted from shared variable)
    except:
        errMsg = "Error reading stored result. Perhaps it was not stored, or you failed to include the store result line in your previous action"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    if (
        stored == False
    ):  # Just to be clear, we can't to log that we are using the old method
        CommonUtil.ExecLog(
            sModuleInfo,
            "Could not find the recall result row. It's either missing or mispelled. Trying in different method",
            2,
        )

    if stored == True:  # Use saved result from previous data set
        if result in failed_tag_list:  # Check result from previous action
            logic_decision = "false"
        else:  # Passed / Skipped
            logic_decision = "true"

    # *** Old method of conditional actions in the if statements below. Only kept for backwards compatibility *** #

    elif module == "appium" or module == "selenium":
        try:
            wait = 0
            for left, mid, right in data_set:
                mid = mid.lower()
                left = left.lower()
                if "optional parameter" in mid and "wait" in left:
                    wait = float(right.strip())
            start_time = time.time()
            end_time = start_time + wait
            while True:
                Element = LocateElement.Get_Element(
                    data_set, eval(module).get_driver()
                )  # Get the element object or 'failed'
                if (Element not in failed_tag_list) or (time.time() >= end_time):
                    break
                # time.sleep(0.5)
            if Element in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo, "Conditional Actions could not find the element", 3
                )
                logic_decision = "false"
            else:
                logic_decision = "true"
        except:  # Element doesn't exist, proceed with the step data following the fail/false path
            CommonUtil.ExecLog(
                sModuleInfo, "Conditional Actions could not find the element", 3
            )
            logic_decision = "false"

    elif (
        module == "common" or module == "database"
    ):  # compare variable or list, and based on the result conditional actions will work
        try:
            CommonUtil.ExecLog(
                sModuleInfo,
                "The function has been deprecated and will be removed at a later period.\n" +
                " Use our other action 'if else'",
                2)
            result = common.Compare_Variables(
                data_set
            )  # Get the element object or 'failed'
            if result in failed_tag_list:
                result = common.Compare_Lists_or_Dicts(data_set)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Conditional Actions Result is False, Variable doesn't match with given value",
                        1,
                    )
                    logic_decision = "false"
                else:
                    logic_decision = "true"
            else:
                logic_decision = "true"
        except:  # Element doesn't exist, proceed with the step data following the fail/false path
            CommonUtil.ExecLog(
                sModuleInfo, "Conditional Actions could not find the variable", 3
            )
            logic_decision = "false"

    elif module == "rest":
        Get_Element_Step_Data = getattr(eval(module), "Get_Element_Step_Data")
        element_step_data = Get_Element_Step_Data(
            [data_set]
        )  # Pass data set as a list, and get back anything that's not an "action" or "conditional action"
        Validate_Step_Data = getattr(eval(module), "Validate_Step_Data")
        returned_step_data_list = Validate_Step_Data(
            element_step_data[0]
        )  # Make sure the element step data we got back from above is good
        if (returned_step_data_list == []) or (
            returned_step_data_list == "failed"
        ):  # Element step data is bad, so fail
            CommonUtil.ExecLog(
                sModuleInfo, "Element data is bad: %s" % str(element_step_data), 3
            )
            return "failed"
        else:  # Element step data is good, so continue
            # Check if element from data set exists on device
            try:
                Get_Response = getattr(eval(module), "Get_Response")
                Element = Get_Response(element_step_data[0])
                if (
                    Element == "failed"
                ):  # Element doesn't exist, proceed with the step data following the fail/false path
                    logic_decision = "false"
                else:  # Any other return means we found the element, proceed with the step data following the pass/true pass
                    logic_decision = "true"
            except Exception:  # Element doesn't exist, proceed with the step data following the fail/false path
                CommonUtil.ExecLog(
                    sModuleInfo, "Could not find element in the by the criteria...", 3
                )
                logic_decision = "false"
                return CommonUtil.Exception_Handler(sys.exc_info())

    elif module == "utility":
        Get_Path_Step_Data = getattr(eval(module), "Get_Path_Step_Data")
        element_step_data = Get_Path_Step_Data(
            data_set
        )  # Pass data set as a list, and get back anything that's not an "action" or "conditional action"
        Validate_Path_Step_Data = getattr(eval(module), "Validate_Path_Step_Data")
        returned_step_data_list = Validate_Path_Step_Data(
            [element_step_data[0]]
        )  # Make sure the element step data we got back from above is good
        if (returned_step_data_list == []) or (
            returned_step_data_list == "failed"
        ):  # Element step data is bad, so fail
            CommonUtil.ExecLog(
                sModuleInfo, "Element data is bad: %s" % str(element_step_data), 3
            )
            return "failed"
        else:  # Element step data is good, so continue
            # Check if element from data set exists on device
            try:
                find = getattr(eval(module), "find")
                Element = find(returned_step_data_list[0])
                if Element == False:
                    logic_decision = "false"
                else:
                    logic_decision = "true"
            except Exception:  # Element doesn't exist, proceed with the step data following the fail/false path
                CommonUtil.ExecLog(
                    sModuleInfo, "Could not find element in the by the criteria...", 3
                )
                logic_decision = "false"
                return CommonUtil.Exception_Handler(sys.exc_info())

    # *** Old method of conditional actions in the if statements above. Only kept for backwards compatibility *** #

    else:
        CommonUtil.ExecLog(
            sModuleInfo,
            "Either no module was specified in the Conditional Action line, or it is incorrect",
            3,
        )
        return "failed"

    # Process the path as defined above (pass/fail)
    skip_for_loop = []
    for conditional_steps in logic_row:  # For each conditional action from the data set
        CommonUtil.ExecLog(
            sModuleInfo, "Processing conditional action: %s" % str(conditional_steps), 1
        )
        if (
            logic_decision in conditional_steps
        ):  # If we have a result from the element check above (true/false)
            list_of_steps = conditional_steps[2].split(
                ","
            )  # Get the data set numbers for this conditional action and put them in a list
            for (
                each_item
            ) in (
                list_of_steps
            ):  # For each data set number we need to process before finishing
                if int(each_item) - 1 in skip_for_loop:
                    continue
                if (
                    CommonUtil.check_offline()
                ):  # Check if user initiated offline command from GUI
                    CommonUtil.ExecLog(
                        sModuleInfo, "User requested Zeuz Node to go Offline", 2
                    )
                    return "failed"

                CommonUtil.ExecLog(
                    sModuleInfo, "Processing conditional step %s" % str(each_item), 1
                )
                data_set_index = (
                    int(each_item.strip()) - 1
                )  # data set number, -1 to offset for data set numbering system
                result, skip_for_loop = Run_Sequential_Actions(
                    [data_set_index]
                )  # new edit: full step data is passed. [step_data[data_set_index]]) # Recursively call this function until all called data sets are complete
                if row[0].lower().strip() == "step exit":
                    CommonUtil.ExecLog(
                        sModuleInfo, "Step Exit called. Stopping Test Step.", 1
                    )
                    return result

                if result in failed_tag_list:
                    return result  # Return on any failure
            return result  # Return only the last result of the last row of the last data set processed - This should generally be a "step result action" command

    # Shouldn't get here, but just in case
    return "passed"


def Action_Handler(_data_set, action_row):
    """ Finds the appropriate function for the requested action in the step data and executes it """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    skip_conversion_of_shared_variable_for_actions = ["run actions", "loop settings"]

    # Split data set row into the usable parts
    action_name = action_row[0]
    action_subfield = action_row[1]

    if str(action_name).startswith("%|"):  # if shared variable
        action_name = str(action_name).split("%|")[1][:-2]
        action_name = sr.Get_Shared_Variables(action_name)

    if str(action_subfield).startswith("%|"):  # if shared variable
        action_subfield = str(action_subfield).split("%|")[0][:-2]
        action_subfield = sr.Get_Shared_Variables(action_subfield)

    # Get module and function for this action
    module = ""
    function = ""
    original_module = ""
    module, function, original_module, screenshot = common.get_module_and_function(
        action_name, action_subfield
    )  # New, get the module to execute
    CommonUtil.ExecLog(
        sModuleInfo,
        "Function identified as function: %s in module: %s" % (function, module),
        0,
    )

    sr.Set_Shared_Variables(
        "screen_capture", screenshot.lower().strip()
    )  # Save the screen capture type
    CommonUtil.set_screenshot_vars(
        sr.Shared_Variable_Export()
    )  # Get all the shared variables, and pass them to CommonUtil

    if (
        module in failed_tag_list or module == "" or function == ""
    ):  # New, make sure we have a function
        CommonUtil.ExecLog(
            sModuleInfo,
            "You probably didn't add the module as part of the action. Eg: appium action",
            3,
        )
        return "failed"

    # If this is a common function, try to get the webdriver for it, if there is one, and save it to shared variables. This will allow common functions to work with whichever webdriver they need
    if original_module != "":  # This was identified as a common module
        try:
            result = load_sa_modules(
                original_module
            )  # Load the appropriate module (in case its never been run before this common action has started)
            if result == "failed":
                CommonUtil.ExecLog(
                    sModuleInfo, "Can't find module for %s" % original_module, 3
                )
                return "failed"

            common_driver = eval(original_module).get_driver()  # Get webdriver object
            sr.Set_Shared_Variables(
                "common_driver", common_driver
            )  # Save in shared variable
        except:
            pass  # Not all modules have get_driver, so don't worry if this crashes

    # Strip the "optional" keyword, and module, so functions work properly (result of optional action is handled by sequential_actions)
    data_set = []
    for row in _data_set:
        new_row = list(row)
        if "optional" in row[1]:
            new_row[1] = new_row[1].replace("optional", "").strip()
        if "bypass" in row[1]:
            new_row[1] = new_row[1].replace("bypass", "").strip()
        if module in row[1]:
            new_row[1] = new_row[1].replace(module, "").strip()
        if original_module != "" and original_module in row[1]:
            new_row[1] = new_row[1].replace(original_module, "").strip()
        data_set.append(tuple(new_row))

    # Convert shared variables to their string equivelent
    if action_name not in skip_conversion_of_shared_variable_for_actions:
        data_set = common.shared_variable_to_value(data_set)
        if data_set in failed_tag_list:
            return "failed"

    # Execute the action's function
    try:
        result = load_sa_modules(module)  # Load the appropriate module
        if result == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Can't find module for %s" % module, 3)
            return "failed"

        run_function = getattr(
            eval(module), function
        )  # create a reference to the function
        result = run_function(
            data_set
        )  # Execute function, providing all rows in the data set
        return result  # Return result to sequential_actions()

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
