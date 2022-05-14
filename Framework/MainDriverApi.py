# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
import copy
import json
import inspect
import os
import time
import sys
import urllib.request, urllib.error, urllib.parse
import queue
import shutil
import importlib
import requests
import zipfile
from urllib3.exceptions import InsecureRequestWarning
# Suppress the InsecureRequestWarning since we use verify=False parameter.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
import threading
import subprocess
from pathlib import Path
from sys import platform as _platform
from datetime import datetime
from datetime import timedelta
from threading import Timer
from Framework.Built_In_Automation import Shared_Resources
from .Utilities import ConfigModule, FileUtilities as FL, CommonUtil, RequestFormatter
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as shared,
)
from Framework.Utilities import ws
from reporting import junit_report

from rich.style import Style
from rich.table import Table
from rich.console import Console
from rich.box import ASCII_DOUBLE_HEAD, DOUBLE
from rich.padding import Padding

rich_print = Console().print

top_path = os.path.dirname(os.getcwd())
drivers_path = os.path.join(top_path, "Drivers")
sys.path.append(drivers_path)

MODULE_NAME = inspect.getmodulename(__file__)

"""Constants"""
PROGRESS_TAG = "In-Progress"
PASSED_TAG = "Passed"
FAILED_TAG = "zeuz_failed"
BLOCKED_TAG = "Blocked"
CANCELLED_TAG = "Cancelled"
COMPLETE_TAG = "Complete"
passed_tag_list = [
    "Pass",
    "pass",
    "PASS",
    "PASSED",
    "Passed",
    "passed",
    "true",
    "TRUE",
    "True",
    "1",
    "Success",
    "success",
    "SUCCESS",
]
failed_tag_list = [
    "Fail",
    "fail",
    "FAIL",
    "zeuz_failed",
    "false",
    "False",
    "FALSE",
    "0",
]
device_info = {}
# if other linked machine failed in a linked run
failed_due_to_linked_fail = False


# sets server variable
def set_server_variable(run_id, key, value):
    return RequestFormatter.Get(
        "set_server_variable_api", {"run_id": run_id, "var_name": key, "var_val": value}
    )


# gets server variable
def get_server_variable(run_id, key):
    return RequestFormatter.Get(
        "get_server_variable_api", {"run_id": run_id, "var_name": key}
    )


# get global list variable
def get_global_list_variable(name):
    return RequestFormatter.Get(
        "set_or_get_global_server_list_variable_api", {"name": name}
    )


# append to global list variable
def append_to_global_list_variable(name, value):
    return RequestFormatter.Get(
        "append_value_to_global_server_list_variable_api",
        {"name": name, "value": value},
    )


# remove item from global list variable
def remove_item_from_global_list_variable(name, value):
    return RequestFormatter.Get(
        "delete_global_server_list_variable_by_value_api",
        {"name": name, "value": value},
    )


# get all server variable
def get_all_server_variable(run_id):
    return RequestFormatter.Get("get_all_server_variable_api", {"run_id": run_id})



# if run is cancelled then it can be called, it cleans up the runid from database
def cleanup_runid_from_server(run_id):
    RequestFormatter.Get("clean_up_run_api", {"run_id": run_id})


# returns current status of the runid
def get_status_of_runid(run_id):
    return RequestFormatter.Get("get_status_of_a_run_api", {"run_id": run_id})


def check_if_other_machines_failed_in_linked_run():
    # can get multiple server variable with one action
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        run_id = shared.Get_Shared_Variables("run_id")

        dict = get_all_server_variable(run_id)
        try:
            if (
                "is_failed" in dict
                and dict["is_failed"] != "null"
                and dict["is_failed"] == "yes"
            ):
                global failed_due_to_linked_fail

                failed_machine = ""
                if "failed_machine" in dict:
                    failed_machine = dict["failed_machine"]
                if failed_machine == (CommonUtil.MachineInfo().getLocalUser()).lower():
                    return "passed"

                failed_due_to_linked_fail = True

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

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# downloads attachments for a test case
def create_tc_log_ss_folder(run_id, test_case, temp_ini_file, server_version):
    try:
        log_file_path = ConfigModule.get_config_value(
            "sectionOne", "temp_run_file_path", temp_ini_file
        )
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
    test_case_folder = (
        log_file_path +
        os.sep +
        run_id.replace(":", "-") +
        os.sep +
        CommonUtil.current_session_name +
        os.sep +
        test_case.replace(":", "-")
    )
    # create test_case_folder
    ConfigModule.add_config_value("sectionOne", "test_case", test_case, temp_ini_file)
    ConfigModule.add_config_value("sectionOne", "test_case_folder", test_case_folder, temp_ini_file)
    FL.CreateFolder(test_case_folder)

    # create log_folder for browser console error logs
    log_folder = test_case_folder + os.sep + "Log"
    ConfigModule.add_config_value("sectionOne", "log_folder", log_folder, temp_ini_file)
    FL.CreateFolder(log_folder)

    # create screenshot_folder
    screenshot_folder = test_case_folder + os.sep + "screenshots"
    ConfigModule.add_config_value("sectionOne", "screen_capture_folder", screenshot_folder, temp_ini_file)
    FL.CreateFolder(screenshot_folder)

    # performance report folder
    performance_report = test_case_folder + os.sep + "performance_report"
    ConfigModule.add_config_value("sectionOne", "performance_report", performance_report, temp_ini_file)
    FL.CreateFolder(performance_report)

    if float(server_version.split(".")[0]) >= 7:
        # json report folder
        json_report = test_case_folder + os.sep + "json_report"
        ConfigModule.add_config_value("sectionOne", "json_report", json_report, temp_ini_file)
        FL.CreateFolder(json_report)

    # create where attachments from selenium browser will be downloaded
    zeuz_download_folder = test_case_folder + os.sep + "zeuz_download_folder"
    FL.CreateFolder(zeuz_download_folder)
    initial_download_folder = zeuz_download_folder + os.sep + "initial_download_folder"
    FL.CreateFolder(initial_download_folder)
    ConfigModule.add_config_value("sectionOne", "initial_download_folder", initial_download_folder, temp_ini_file)
    shared.Set_Shared_Variables("zeuz_download_folder", zeuz_download_folder)

    # Store the attachments for each test case separately inside
    # AutomationLog/attachments/TEST-XYZ
    download_folder = str(Path(log_file_path) / "attachments" / test_case.replace(":", "-"))
    ConfigModule.add_config_value("sectionOne", "download_folder", download_folder, temp_ini_file)


import ctypes
def terminate_thread(thread):   # To kill running thread
    """Terminates a python thread from another thread.

    :param thread: a threading.Thread instance
    """
    if not thread.is_alive():
        return

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

# call the function of a test step that is in its driver file
def call_driver_function_of_test_step(
    sModuleInfo,
    all_step_info,
    StepSeq,
    step_time,
    current_step_name,
    final_dependency,
    final_run_params,
    test_steps_data,
    test_action_info,
    file_specific_steps,
    debug_actions=None,
):
    try:
        q = queue.Queue()  # define queue

        # get step driver
        current_driver = all_step_info[StepSeq-1]["step_driver_type"]
        # current_driver = "Built_In_Driver"
        print("DRIVER: {}".format(current_driver))

        try:
            current_driver = "Drivers." + current_driver
            # if CommonUtil.step_module_name is None:
            #     module_name = importlib.import_module(current_driver)  # get module
            #     CommonUtil.step_module_name = module_name
            # else:
            #     module_name = CommonUtil.step_module_name
            module_name = importlib.import_module(current_driver)  # get module
            print("STEP DATA and VARIABLES")
            # get step name
            if all_step_info[StepSeq-1]["step_function"]:
                step_name = all_step_info[StepSeq-1]["step_function"].strip()
            else:
                step_name = current_step_name

            step_name = step_name.lower().replace(" ", "_")
            # step_name = "sequential_actions"
            try:
                # importing functions from driver
                functionTocall = getattr(module_name, step_name)
            except Exception as e:
                CommonUtil.Exception_Handler(
                    sys.exc_info(),
                    None,
                    "Could not find function name: %s in Driver/%s.py. Perhaps you need to add a custom driver or add an alias step to the Test Step."
                    % (step_name, current_driver),
                )
                return "zeuz_failed"

            try:
                simple_queue = queue.Queue()
                screen_capture = "Desktop"      # No need of screen capture. Need to delete this

                # run in thread
                if ConfigModule.get_config_value("RunDefinition", "threading") in passed_tag_list:
                    stepThread = threading.Thread(
                        target=functionTocall,
                        args=(
                            final_dependency,
                            final_run_params,
                            test_steps_data,
                            test_action_info,
                            file_specific_steps,
                            simple_queue,
                            screen_capture,     # No need of screen capture. Need to delete this
                            device_info,
                        ),
                    )  # start step thread

                    CommonUtil.ExecLog(sModuleInfo, "Starting Test Step Thread..", 1)  # add log

                    # start thread
                    stepThread.start()

                    # Wait for the Thread to finish or until timeout
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Waiting for Test Step Thread to finish..for (seconds) :%d"
                        % step_time,
                        1,
                    )
                    stepThread.join(float(step_time))

                    try:
                        sStepResult = simple_queue.get_nowait()
                        # Get the return value from the ExecuteTestStep
                        # fn via Queue
                        q.put(sStepResult)
                        CommonUtil.ExecLog(sModuleInfo, "Test Step Thread Ended..", 1)
                    except queue.Empty:
                        # Global.DefaultTestStepTimeout
                        ErrorMessage = "Test Step didn't return after %d seconds" % step_time
                        CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)
                        sStepResult = "zeuz_failed"
                        q.put(sStepResult)

                        # Clean up
                        if stepThread.is_alive():
                            CommonUtil.ExecLog(sModuleInfo, "Timeout Error", 3)
                            # stepThread.__stop()
                            try:
                                # stepThread._Thread__stop()
                                terminate_thread(stepThread)
                                while stepThread.is_alive():
                                    time.sleep(1)
                                    CommonUtil.ExecLog(sModuleInfo, "Thread is still alive", 2)
                            except:
                                CommonUtil.Exception_Handler(sys.exc_info())
                else:
                    # run sequentially
                    sStepResult = functionTocall(
                        final_dependency,
                        final_run_params,
                        test_steps_data,
                        test_action_info,
                        file_specific_steps,
                        simple_queue,
                        screen_capture,     # No need of screen capture. Need to delete this
                        device_info,
                        debug_actions,
                    )
            except:
                CommonUtil.Exception_Handler(sys.exc_info())  # handle exceptions
                sStepResult = "zeuz_failed"

            # get step result
            if sStepResult in passed_tag_list:
                sStepResult = "PASSED"
            elif sStepResult in failed_tag_list:
                sStepResult = "zeuz_failed".upper()
            else:
                CommonUtil.ExecLog(sModuleInfo, "sStepResult not an acceptable type", 3)
                CommonUtil.ExecLog(sModuleInfo, "Acceptable pass string(s): %s" % passed_tag_list, 3)
                CommonUtil.ExecLog(sModuleInfo, "Acceptable fail string(s): %s" % failed_tag_list, 3)
                sStepResult = "zeuz_failed"
            q.put(sStepResult)
        except Exception as e:
            print("### Exception : {}".format(e))
            CommonUtil.Exception_Handler(sys.exc_info())
            sStepResult = "zeuz_failed"

        return sStepResult
    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        return "zeuz_failed"


# runs all test steps of a test case
def run_all_test_steps_in_a_test_case(
    testcase_info,
    test_case,
    sModuleInfo,
    run_id,
    file_specific_steps,
    final_dependency,
    final_run_params,
    temp_ini_file,
    debug_info,
    performance=False
):
    try:
        StepSeq = 1
        CommonUtil.step_index = 0
        sTestStepResultList = []
        already_failed = False

        Stepscount = len(testcase_info["steps"])  # no. of steps
        debug_steps = ""
        debug = False
        cleanup_drivers_during_debug = False
        debug_actions = ""

        if run_id.startswith("debug"):
            debug = True
            debug_steps = debug_info["debug_steps"]
            if "debug_step_actions" in debug_info:
                debug_actions = debug_info["debug_step_actions"]
        if not debug_steps:
            debug_steps = []

        if not debug_actions:
            debug_actions = []

        # performance testing
        if performance:
            StepSeq = 2
            CommonUtil.step_index = 1
            sTestStepResultList.append("PASSED")

        # Creating Testcase attachment variables
        attachment_path = str(Path(ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file)) / "attachments")
        tc_attachment_list = []
        for tc_attachment in testcase_info['testcase_attachments_links']:
            path = str(Path(attachment_path + tc_attachment[0][10:]))
            var_name = tc_attachment[1] + "." + tc_attachment[2] if tc_attachment[2] else tc_attachment[1]
            tc_attachment_list.append(var_name)
            shared.Set_Shared_Variables(var_name, path, attachment_var=True)

        all_step_info = testcase_info["steps"]
        all_step_dataset, all_action_info = [], []
        for step_info in all_step_info:
            all_Action_info = step_info["actions"]
            all_action_data_set, all_action_Info = [], []
            for action_info in all_Action_info:
                action_dataset = action_info["step_actions"]
                all_action_data_set.append(action_dataset)
                dict = {}
                dict["Action disabled"] = True if action_info["action_disabled"] == False else False
                server_version = CommonUtil.all_logs_json[CommonUtil.runid_index]["webserver_version"]
                if float(server_version[:server_version.find(".", 2)]) > 6.0:
                    dict["Action disabled"] = not dict["Action disabled"]
                dict["Action name"] = action_info["action_name"]
                all_action_Info.append(dict)
            all_step_dataset.append(all_action_data_set)
            all_action_info.append(all_action_Info)
        # loop through the steps
        while StepSeq <= Stepscount:

            # check if debug step
            CommonUtil.custom_step_duration = ""
            if debug and debug_steps:
                if str(StepSeq) not in debug_steps:
                    StepSeq += 1
                    CommonUtil.step_index += 1
                    continue

            # check if already failed
            if already_failed:
                if all_step_info[StepSeq - 1]["always_run"]:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Step-%s is set as 'Always run' so executing this step" % (CommonUtil.step_index + 1),
                        2,
                    )
                elif "run_on_fail" in all_step_info[StepSeq - 1] and all_step_info[StepSeq - 1]["run_on_fail"]:     # Todo: Remove the 1st condition when all servers are updated
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Step-%s is set as 'Run on fail' and the test case has already failed so executing this step" % (CommonUtil.step_index + 1),
                        2,
                    )
                else:
                    StepSeq += 1
                    CommonUtil.step_index += 1
                    continue

            elif not already_failed and "run_on_fail" in all_step_info[StepSeq - 1] and all_step_info[StepSeq - 1]["run_on_fail"]:     # Todo: Remove the 2nd condition when all servers are updated
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Step-%s is set as 'Run on fail' and the test case has not failed yet so skipping this step" % (CommonUtil.step_index + 1),
                    2,
                )
                StepSeq += 1
                CommonUtil.step_index += 1
                continue

            # get step info
            current_step_name = all_step_info[StepSeq - 1]["step_name"]
            current_step_id = all_step_info[StepSeq - 1]["step_id"]
            current_step_sequence = all_step_info[StepSeq - 1]["step_sequence"]
            shared.Set_Shared_Variables("zeuz_current_step", all_step_info[StepSeq - 1], print_variable=False, pretty=False)

            step_attachments = all_step_info[StepSeq - 1]['step_attachments']
            step_attachment_list = []
            for attachment in step_attachments:
                path = str(Path(attachment_path + attachment[1][12:]))
                var_name = attachment[2] + "." + attachment[3] if attachment[3] else attachment[2]
                step_attachment_list.append(var_name)
                shared.Set_Shared_Variables(var_name, path, attachment_var=True)

            # add config value
            ConfigModule.add_config_value(
                "sectionOne",
                "sTestStepExecLogId",
                run_id + "|" + test_case + "|" + str(current_step_id) + "|" + str(current_step_sequence),
                temp_ini_file,
            )
            CommonUtil.current_step_no = str(current_step_sequence)
            # add log
            # log_line = "STEP #%d: %s" % (StepSeq, current_step_name)
            # print("-"*len(log_line))
            # CommonUtil.ExecLog(sModuleInfo, log_line, 4)
            # print("-"*len(log_line))

            _color = "yellow"
            # _style = Style(color="yellow", blink=False, bold=True)
            table = Table(border_style=_color, box=ASCII_DOUBLE_HEAD, expand=False)
            table.add_column(f"STEP-{str(StepSeq)}", justify="center", style=_color, max_width=40)
            table.add_row(f"{current_step_name}", style=_color)
            # width_pad = CommonUtil.max_char // 2 - (max(len(current_step_name), 6) + 4) // 2
            # table = Padding(table, (0, width_pad))
            rich_print(table)

            test_steps_data = all_step_dataset[StepSeq-1]
            test_action_info = all_action_info[StepSeq-1]
            try:
                test_case_continue = all_step_info[StepSeq - 1]["continue_on_fail"]
                step_time = all_step_info[StepSeq - 1]["step_time"]
                if str(step_time) != "" and step_time is not None:
                    step_time = int(step_time)
                else:
                    step_time = 59
            except:
                test_case_continue = False
                step_time = 59

            # get step start time
            TestStepStartTime = time.time()
            sTestStepStartTime = datetime.fromtimestamp(TestStepStartTime).strftime("%Y-%m-%d %H:%M:%S.%f")
            WinMemBegin = CommonUtil.PhysicalAvailableMemory()  # get available memory

            if StepSeq in CommonUtil.disabled_step:
                CommonUtil.ExecLog(sModuleInfo, "STEP-%s is disabled" % StepSeq, 2)
                sStepResult = "skipped"
            else:
                sStepResult = call_driver_function_of_test_step(
                    sModuleInfo,
                    all_step_info,
                    StepSeq,
                    step_time,
                    current_step_name,
                    final_dependency,
                    final_run_params,
                    test_steps_data,
                    test_action_info,
                    file_specific_steps,
                    debug_actions,
                )

            TestStepEndTime = time.time()
            sTestStepEndTime = datetime.fromtimestamp(TestStepEndTime).strftime("%Y-%m-%d %H:%M:%S.%f")
            WinMemEnd = CommonUtil.PhysicalAvailableMemory()  # get available memory
            if CommonUtil.custom_step_duration:
                TestStepDuration = CommonUtil.custom_step_duration
                CommonUtil.custom_step_duration = ""
            else:
                sec = TestStepEndTime - TestStepStartTime
                hours, remainder = sec // 3600, sec % 3600
                minutes, seconds = remainder // 60, remainder % 60
                TestStepDuration = "%02d:%02d:%s" % (hours, minutes, round(seconds, 3))
            TestStepMemConsumed = WinMemBegin - WinMemEnd  # get memory consumed
            for i in step_attachment_list: shared.Remove_From_Shared_Variables(i, attachment_var=True)  # Cleanup step_attachment variables

            if sStepResult:
                sTestStepResultList.append(sStepResult.upper())
            else:
                sTestStepResultList.append("zeuz_failed")
                CommonUtil.ExecLog(sModuleInfo, "sStepResult : %s" % sStepResult, 1)  # add log
                sStepResult = "zeuz_failed"

            # step dictionary after execution
            after_execution_dict = {
                "stepstarttime": sTestStepStartTime,
                "stependtime": sTestStepEndTime,
                "end_memory": WinMemEnd,
                "duration": TestStepDuration,
                "memory_consumed": TestStepMemConsumed,
                "logid": ConfigModule.get_config_value("sectionOne", "sTestStepExecLogId", temp_ini_file)
            }

            if sStepResult.upper() == PASSED_TAG.upper():
                # Step Passed
                CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Passed" % current_step_name, 1)
                after_execution_dict.update({"status": PASSED_TAG})

            elif sStepResult.upper() == "SKIPPED":
                CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Skipped" % current_step_name, 2)
                after_execution_dict.update({"status": "Skipped"})

            else:
                CommonUtil.ExecLog(sModuleInfo, "%s%s" % (current_step_name, CommonUtil.to_dlt_from_fail_reason), 3)
                after_execution_dict.update({"status": "Failed"})  # dictionary update

                # check if set for continue
                if not test_case_continue:
                    already_failed = True
                elif test_case_continue and CommonUtil.step_index + 1 < len(all_step_info):
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Step-%s is set as 'Continue on fail' so continuing to next step" % (CommonUtil.step_index + 1),
                        2
                    )

            CommonUtil.CreateJsonReport(stepInfo=after_execution_dict)
            StepSeq += 1
            CommonUtil.step_index += 1

            if CommonUtil.run_cancel == CANCELLED_TAG:
                CommonUtil.ExecLog(sModuleInfo, "Test Run status is Cancelled. Exiting the current Test Case...%s" % test_case, 2)
                CommonUtil.run_cancelled = True
                break

        for i in tc_attachment_list: shared.Remove_From_Shared_Variables(i, attachment_var=True)   # Cleanup tc_attachment variables
        return sTestStepResultList
    except:
        CommonUtil.Exception_Handler(sys.exc_info())
        raise Exception


# from the returned step results, it finds out the test case result
def calculate_test_case_result(sModuleInfo, TestCaseID, run_id, sTestStepResultList, testcase_info):
    if "BLOCKED" in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Blocked", 3)
        sTestCaseStatus = "Blocked"
    elif "CANCELLED" in sTestStepResultList or "Cancelled" in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Cancelled", 3)
        sTestCaseStatus = "Cancelled"
    elif "zeuz_failed".upper() in sTestStepResultList:
        step_index = 0
        for each in sTestStepResultList:
            if each == "zeuz_failed".upper():
                if testcase_info["steps"][step_index]["verify_point"]:
                    sTestCaseStatus = "Failed"
                    break
            step_index += 1
        else:
            sTestCaseStatus = "Blocked"
        CommonUtil.ExecLog(sModuleInfo, "Test Case " + sTestCaseStatus, 3)

    elif "WARNING" in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Contain Warning(s)", 2)
        sTestCaseStatus = "Failed"
    elif "NOT RUN" in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Contain Not Run Steps", 2)
        sTestCaseStatus = "Failed"
    elif "SKIPPED" in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Contain Skipped Step(s)", 1)
        skipped = True
        for each in sTestStepResultList:
            if each != "SKIPPED":
                skipped = False
                break
        if skipped:
            sTestCaseStatus = "Skipped"
            CommonUtil.ExecLog(sModuleInfo, "Test Case Skipped", 1)
        else:
            sTestCaseStatus = "Passed"
            CommonUtil.ExecLog(sModuleInfo, "Test Case Passed", 1)
    elif "PASSED" in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Passed", 1)
        sTestCaseStatus = "Passed"
    else:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Status Unknown", 2)
        sTestCaseStatus = "Unknown"

    return sTestCaseStatus


# writes the log file for a test case
def zip_and_delete_tc_folder_old(
    sTestCaseStatus,
    temp_ini_file,
    send_log_file_only_for_fail=True,
):
    # if settings checked, then send log file or screenshots, otherwise don't send
    if sTestCaseStatus not in passed_tag_list or sTestCaseStatus in passed_tag_list and not send_log_file_only_for_fail:
        if ConfigModule.get_config_value("RunDefinition", "local_run") == "False":
            FL.ZipFolder(
                ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file),
                ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file) + ".zip",
            )
    # Delete the folder
    FL.DeleteFolder(ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file))


# writes the log file for a test case
def zip_and_delete_tc_folder(
    run_id,
    TestCaseID,
    sTestCaseStatus,
    temp_ini_file,
    send_log_file_only_for_fail=True,

):
    # if settings checked, then send log file or screenshots, otherwise don't send
    if sTestCaseStatus not in passed_tag_list or sTestCaseStatus in passed_tag_list and not send_log_file_only_for_fail:
        if ConfigModule.get_config_value("RunDefinition", "local_run") == "False":
            all_steps = CommonUtil.all_logs_json[CommonUtil.runid_index]["test_cases"][CommonUtil.tc_index]["steps"]
            for step in all_steps:
                json_filename = Path(ConfigModule.get_config_value("sectionOne", "json_report", temp_ini_file))/(str(step["step_sequence"])+".json")
                with open(json_filename, "w") as f:
                    json.dump(step, f)

            zip_name = run_id.replace(":", "-") + "_" + TestCaseID.replace(":", "-") + ".zip"
            FL.ZipFolder(
                ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file),
                str(Path(ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file)).parent/zip_name),
            )
    # Delete the folder
    FL.DeleteFolder(ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file))


def cleanup_driver_instances():  # cleans up driver(selenium, appium) instances
    try:  # if error happens. we don't care, main driver should not stop, pass in exception

        if CommonUtil.teardown and shared.Test_Shared_Variables("selenium_driver"):
            import Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions as Selenium
            driver = shared.Remove_From_Shared_Variables("selenium_driver")
            if driver not in failed_tag_list:
                Selenium.Tear_Down_Selenium()
        if shared.Test_Shared_Variables("appium_details"):
            import Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions as Appium
            driver = shared.Remove_From_Shared_Variables("appium_details")
            if driver not in failed_tag_list:
                Appium.teardown_appium()

    except:
        pass


def set_important_variables():
    try:
        for module in CommonUtil.common_modules[:-1]:
            try:
                if module not in shared.shared_variables:
                    exec("import " + module)
                    shared.shared_variables.update({module: eval(module)})
            except:
                continue
        if "sr" not in shared.shared_variables:
            shared.shared_variables.update({"sr": shared})
    except:
        CommonUtil.Exception_Handler(sys.exc_info())
        raise Exception


def run_test_case(
    TestCaseID,
    sModuleInfo,
    run_id,
    final_dependency,
    final_run_params,
    temp_ini_file,
    testcase_info,
    debug_info,
    all_file_specific_steps,
    rerun_on_fail,
    server_version,
    send_log_file_only_for_fail=True,
    performance=False,
    browserDriver=None,
):
    try:
        TestCaseStartTime = time.time()
        shared.Set_Shared_Variables("run_id", run_id)
        test_case = str(TestCaseID).replace("#", "no")
        CommonUtil.current_tc_no = test_case
        CommonUtil.load_testing = False
        ConfigModule.add_config_value("sectionOne", "sTestStepExecLogId", sModuleInfo, temp_ini_file)
        create_tc_log_ss_folder(run_id, test_case, temp_ini_file, server_version)
        set_important_variables()
        file_specific_steps = all_file_specific_steps[TestCaseID] if TestCaseID in all_file_specific_steps else {}
        TestCaseName = testcase_info["title"]
        shared.Set_Shared_Variables("zeuz_current_tc", testcase_info, print_variable=False, pretty=False)

        # log_line = "# EXECUTING TEST CASE : %s :: %s #" % (test_case, TestCaseName)
        # print("#"*(len(log_line)))
        # CommonUtil.ExecLog("", log_line, 4, False)
        # print("#"*(len(log_line)))
        _color = "white"
        # danger_style = Style(color=_color, blink=False, bold=True)
        table = Table(border_style=_color, box=DOUBLE, expand=False, padding=1)
        table.add_column(test_case, justify="center", style=_color, max_width=40)
        table.add_row(TestCaseName, style=_color)
        # width_pad = CommonUtil.max_char//2 - (max(len(TestCaseName), len(test_case)) + 4)//2
        # table = Padding(table, (0, width_pad))
        rich_print(table)

        # get test case start time
        if performance and browserDriver:
            shared.Set_Shared_Variables("selenium_driver", browserDriver)

        # runs all test steps in the test case, all test step result is stored in the list named sTestStepResultList
        sTestStepResultList = run_all_test_steps_in_a_test_case(
            testcase_info,
            test_case,
            sModuleInfo,
            run_id,
            file_specific_steps,
            final_dependency,
            final_run_params,
            temp_ini_file,
            debug_info,
            performance
        )

        ConfigModule.add_config_value(
            "sectionOne",
            "sTestStepExecLogId",
            run_id + "|" + test_case + "|" + "none" + "|" + "none",
            temp_ini_file,
        )

        # get test case end time
        TestCaseEndTime = time.time()
        sTestCaseEndTime = datetime.fromtimestamp(TestCaseEndTime).strftime("%Y-%m-%d %H:%M:%S")

        # Decide if Test Case Pass/Failed
        sTestCaseStatus = calculate_test_case_result(sModuleInfo, test_case, run_id, sTestStepResultList, testcase_info)

        # write locust file for performance testing
        if performance:
            locust_output_file_path = (
                os.getcwd()
                + os.sep
                + "Built_In_Automation"
                + os.sep
                + "Performance_Testing"
                + os.sep
                + "locustFileOutput.txt"
            )
            file = open(locust_output_file_path, "a+")
            file.write(sTestCaseStatus + "-" + str(",".join(sTestStepResultList)) + "\n")
            file.close()

        # Time it took to run the test case
        TimeDiff = TestCaseEndTime - TestCaseStartTime
        TimeInSec = int(TimeDiff)
        TestCaseDuration = CommonUtil.FormatSeconds(TimeInSec)
        after_execution_dict = {
            "teststarttime": datetime.fromtimestamp(TestCaseStartTime).strftime("%Y-%m-%d %H:%M:%S"),
            "testendtime": sTestCaseEndTime,
            "duration": TestCaseDuration,
            "status": sTestCaseStatus,
            "failreason": ""
        }
        if sTestCaseStatus not in passed_tag_list or sTestCaseStatus in passed_tag_list and not send_log_file_only_for_fail:
            TCLogFile = (
                os.sep
                + ConfigModule.get_config_value("Advanced Options", "_file_upload_path")
                + os.sep
                + run_id.replace(":", "-")
                + "/"
                + ConfigModule.get_config_value("sectionOne", "test_case", temp_ini_file)
                + ".zip"
            )
            after_execution_dict["logid"] = TCLogFile
        CommonUtil.CreateJsonReport(TCInfo=after_execution_dict)
        CommonUtil.clear_logs_from_report(send_log_file_only_for_fail, rerun_on_fail, sTestCaseStatus)

        if not CommonUtil.debug_status:  # if normal run, then write log file and cleanup driver instances
            CommonUtil.Join_Thread_and_Return_Result("screenshot")  # Let the capturing screenshot end in thread
            if shared.Get_Shared_Variables("zeuz_auto_teardown").strip().lower() in ("on", "yes", "true", "ok", "enable"):
                cleanup_driver_instances()  # clean up drivers
            shared.Clean_Up_Shared_Variables()  # clean up shared variables
            if ConfigModule.get_config_value("RunDefinition", "local_run") == "False":

                if float(server_version.split(".")[0]) < 7:
                    zip_and_delete_tc_folder_old(
                        sTestCaseStatus,
                        temp_ini_file,
                        send_log_file_only_for_fail
                    )
                else:
                    zip_and_delete_tc_folder(
                        run_id,
                        TestCaseID,
                        sTestCaseStatus,
                        temp_ini_file,
                        send_log_file_only_for_fail
                    )
        return "passed"
    except:
        CommonUtil.Exception_Handler(sys.exc_info())
        TestCaseEndTime = time.time()
        sTestCaseEndTime = datetime.fromtimestamp(TestCaseEndTime).strftime("%Y-%m-%d %H:%M:%S")
        TimeDiff = TestCaseEndTime - TestCaseStartTime
        TimeInSec = int(TimeDiff)
        TestCaseDuration = CommonUtil.FormatSeconds(TimeInSec)
        sTestCaseStatus = "Blocked"
        after_execution_dict = {
            "teststarttime": datetime.fromtimestamp(TestCaseStartTime).strftime("%Y-%m-%d %H:%M:%S"),
            "testendtime": sTestCaseEndTime,
            "duration": TestCaseDuration,
            "status": sTestCaseStatus,
            "failreason": ""
        }
        TCLogFile = (
                os.sep
                + ConfigModule.get_config_value("Advanced Options", "_file_upload_path")
                + os.sep
                + run_id.replace(":", "-")
                + "/"
                + ConfigModule.get_config_value("sectionOne", "test_case", temp_ini_file)
                + ".zip"
        )
        after_execution_dict["logid"] = TCLogFile
        CommonUtil.CreateJsonReport(TCInfo=after_execution_dict)
        return "passed"


def set_device_info_according_to_user_order(device_order, device_dict,  test_case_no, test_case_name, user_info_object, Userid):
    # Need to set device_info for browserstack here
    global device_info
    if isinstance(device_order, list):
        for each in device_order:
            device_order_val = str(each[0])
            device_no_val = str(each[1])
            original_dict = device_dict
            device_info["device " + device_order_val] = original_dict[
                "device " + device_no_val
                ]
    elif "browser_stack" in device_order and device_order["browser_stack"]:
        project = user_info_object["project"]
        team = user_info_object["team"]

        project = "PROJECT:'" + project + "'  TEAM:'" + team + "'"
        build = test_case_no + " :: " + test_case_name
        name = Userid + " :: " + datetime.now().strftime("%d %B %Y %A %H:%M:%S")
        device_info = {
            "browserstack device 1": {
                "basic": {
                    "browserstack.user": device_order["browser_stack"]["1"]["username"],
                    "browserstack.key": device_order["browser_stack"]["1"]["access_key"],
                    # "app": "bs://227d1bd74c601618c44b1a10b36f80caf11e497a",
                    "app": device_order["browser_stack"]["1"]["app_url"],

                    "device": device_order["browser_stack"]["1"]["device"],
                    "os_version": device_order["browser_stack"]["1"]["os_version"],

                    "project": project,  # zeuz project + team name
                    "build": build,  # test case no + test case name
                    "name": name  # Userid + datetime
                },
                "other": {
                    "app_name": device_order["browser_stack"]["1"]["app_name"],
                },

            }
        }
    elif "aws" in device_order:
        device_info = {
            "aws device 1": {}
        }
    elif "local" in device_order:
        device_order = device_order["local"]
        for each in device_order:
            device_order_val = str(each[0])
            device_no_val = str(each[1])
            original_dict = device_dict
            device_info["device " + device_order_val] = original_dict[
                "device " + device_no_val
            ]
    else:
        device_info = {}


def get_performance_testing_data_for_test_case(run_id, TestCaseID):
    return RequestFormatter.Get(
        "get_performance_testing_data_for_test_case_api",
        {"run_id": run_id, "test_case": TestCaseID},
    )


def write_locust_input_file(
    time_period,
    perf_data,
    TestCaseID,
    sModuleInfo,
    run_id,
    driver_list,
    final_dependency,
    final_run_params,
    temp_ini_file,
    is_linked,
    send_log_file_only_for_fail,
):
    try:
        locust_input_file_path = (
            os.getcwd()
            + os.sep
            + "Built_In_Automation"
            + os.sep
            + "Performance_Testing"
            + os.sep
            + "locustFileInput.txt"
        )
        file = open(locust_input_file_path, "w")
        file.write(str(time_period) + "\n")
        file.write(str(TestCaseID) + "\n")
        file.write(str(sModuleInfo) + "\n")
        file.write(str(run_id) + "\n")
        file.write(str(driver_list) + "\n")
        file.write(str(final_dependency) + "\n")
        file.write(str(final_run_params) + "\n")
        file.write(str(temp_ini_file) + "\n")
        file.write(str(is_linked) + "\n")
        file.write(str(send_log_file_only_for_fail) + "\n")
        file.close()
    except:
        pass


def upload_csv_file_info(run_id, test_case):
    try:
        csv_result_input_file_path = os.getcwd() + os.sep + "csvForZeuz_requests.csv"
        file = open(csv_result_input_file_path, "r")
        file.readline()
        result_data = file.readline()
        file.close()
        test_case_result = []
        test_case_result_input_file_path = (
            os.getcwd()
            + os.sep
            + "Built_In_Automation"
            + os.sep
            + "Performance_Testing"
            + os.sep
            + "locustFileOutput.txt"
        )
        file = open(test_case_result_input_file_path, "r")
        data = file.readline()
        while data:
            test_case_result.append(data.strip())
            data = file.readline()
        file.close()
        dict = {
            "run_id": run_id,
            "test_case": test_case,
            "result_data": result_data,
            "test_case_result": test_case_result,
        }
        RequestFormatter.Get("send_performance_data_api", dict)
    except:
        pass


def check_run_cancel(run_id):
    while not CommonUtil.run_cancelled:
        CommonUtil.run_cancel = get_status_of_runid(run_id)
        time.sleep(3)
    # CommonUtil.run_cancelled = False


def upload_json_report_old(Userid, temp_ini_file, run_id):
    try:
        if CommonUtil.debug_status: return
        zip_path = Path(ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file))/run_id.replace(":", "-")/CommonUtil.current_session_name
        path = zip_path / "execution_log.json"
        json_report = CommonUtil.get_all_logs(json=True)
        with open(path, "w") as f:
            json.dump(json_report, f)

        if ConfigModule.get_config_value("RunDefinition", "local_run") == "False" and CommonUtil.run_cancel != CANCELLED_TAG:
            FL.ZipFolder(str(zip_path), str(zip_path) + ".zip")

            with open(str(zip_path) + ".zip", "rb") as fzip:
                size = round(os.stat(str(zip_path) + ".zip").st_size / 1024, 2)
                if size > 1024:
                    size = str(round(size/1024, 2)) + " MB"
                else:
                    size = str(size) + " KB"
                print("Uploading %s report of %s testcases of %s from:\n%s"
                      % (CommonUtil.current_session_name, len(json_report[0]["test_cases"]), size, str(zip_path) + ".zip"))

                headers = RequestFormatter.add_api_key_to_headers({})
                for _ in range(5):
                    try:
                        res = requests.post(
                            RequestFormatter.form_uri("create_report_log_api/"),
                            files={"file": fzip},
                            data={"machine_name": Userid, "file_name": json_report[CommonUtil.runid_index]["file_name"]},
                            verify=False,
                            **headers)
                    except KeyError:
                        res = requests.post(
                            RequestFormatter.form_uri("create_report_log_api/"),
                            files={"file": fzip},
                            data={"machine_name": Userid},
                            verify=False,
                            **headers)
                    if res.status_code == 200:
                        try:
                            res_json = res.json()
                        except:
                            print("Could not Upload json report to server")
                            print("\nResponse Text = " + res.text + "\n")
                            return
                        if isinstance(res_json, dict) and 'message' in res_json and res_json["message"]:
                            print("Successfully Uploaded the report to server of run_id '%s'" % run_id)
                        else:
                            print("Could not Upload the report to server of run_id '%s'" % run_id)
                            print("\nResponse Text = " + res.text + "\n")
                        break
                    time.sleep(1)
                else:
                    print("Could not Upload the report to server of run_id '%s'" % run_id)
            # os.unlink(str(zip_path) + ".zip")     # Removing the zip is skipped because node_manager needs the zip

        with open(path, "w") as f:
            json.dump(json_report, f, indent=2)

        if CommonUtil.run_cancel != CANCELLED_TAG:
            # Create a standard report format to be consumed by other tools.
            junit_report_path = zip_path / "junitreport.xml"
            print("Generating junit4 compatible report.")
            junit_report.process(CommonUtil.all_logs_json, str(junit_report_path))
            print("DONE. Generated junit report at %s" % junit_report_path)
        return zip_path
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def upload_reports_and_zips(Userid, temp_ini_file, run_id):
    try:
        if CommonUtil.debug_status: return
        zip_dir = Path(ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file))/run_id.replace(":", "-")/CommonUtil.current_session_name

        if ConfigModule.get_config_value("RunDefinition", "local_run") == "False" and CommonUtil.run_cancel != CANCELLED_TAG:
            # FL.ZipFolder(str(zip_path), str(zip_path) + ".zip")

            tc_report = copy.deepcopy(CommonUtil.all_logs_json)
            tc_report[CommonUtil.runid_index]["machine_name"] = Userid

            for testcase in tc_report[CommonUtil.runid_index]["test_cases"]:
                for step in testcase["steps"]:
                    if "actions" in step:
                        del step["actions"]
                    if "log" in step:
                        del step["log"]

            with open("report.json", "w") as f:
                f.write(json.dumps({"execution_report": json.dumps(tc_report)}))

            for _ in range(5):
                try:
                    res = requests.post(
                        RequestFormatter.form_uri("create_report_log_api/"),
                        data={"execution_report": json.dumps(tc_report)},
                        verify=False,
                        **RequestFormatter.add_api_key_to_headers({}))
                    if res.status_code == 200:
                        print(f"Successfully uploaded the execution report of run_id {run_id}")
                        break
                    else:
                        print(f"Failed to upload the execution report of run_id {run_id}")
                        print(f"Status: {res.status_code} Response: {res.text}")
                        print("Retrying...")
                    time.sleep(4)
                except:
                    CommonUtil.Exception_Handler(sys.exc_info())
                    time.sleep(4)
            else:
                print("Could not Upload the report to server of run_id '%s'" % run_id)

            zip_files = [os.path.join(zip_dir, f) for f in os.listdir(zip_dir) if f.endswith(".zip")]
            opened_zips = []
            size = 0
            for zip_file in zip_files:
                opened_zips.append(open(str(zip_file), "rb"))
                size += round(os.stat(str(zip_file)).st_size / 1024, 2)

            if size > 1024:
                size = str(round(size/1024, 3)) + " MB"
            else:
                size = str(round(size, 3)) + " KB"
            print("Uploading %s logs-screenshots of %s testcases of %s from:\n%s" % (CommonUtil.current_session_name, len(zip_files), size, str(zip_dir)))

            for _ in range(5):
                try:
                    files_list = []
                    for zips in opened_zips:
                        files_list.append(("file",zips))
                    res = requests.post(
                        RequestFormatter.form_uri("save_log_and_attachment_api/"),
                        files=files_list,
                        data={"machine_name": Userid},
                        verify=False,
                        **RequestFormatter.add_api_key_to_headers({}))
                    if res.status_code == 200:
                        try:
                            res_json = res.json()
                        except:
                            # print("Could not Upload logs-screenshots to server")
                            # print("\nResponse Text = " + res.text + "\n")
                            # break
                            continue
                        if isinstance(res_json, dict) and 'message' in res_json and res_json["message"]:
                            print("Successfully Uploaded logs-screenshots to server of run_id '%s'" % run_id)
                        else:
                            print("Could not Upload logs-screenshots to server of run_id '%s'" % run_id)
                            print("\nResponse Text = " + res.text + "\n")
                        break
                except:
                    pass

                time.sleep(4)
            else:
                print("Could not Upload logs-screenshots to server of run_id '%s'" % run_id)

        with open(zip_dir / "execution_log_old_format.json", "w") as f:
            json.dump(CommonUtil.get_all_logs(json=True), f, indent=2)

        if CommonUtil.run_cancel != CANCELLED_TAG:
            # Create a standard report format to be consumed by other tools.
            junit_report_path = zip_dir / "junitreport.xml"
            print("Generating junit4 compatible report.")
            junit_report.process(CommonUtil.all_logs_json, str(junit_report_path))
            print("DONE. Generated junit report at %s" % junit_report_path)
        return zip_dir
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def split_testcases(run_id_info, max_tc_in_single_session):
    import copy
    from math import ceil, floor
    testcases = run_id_info["test_cases"]
    session_num = (len(testcases)-1)//max_tc_in_single_session + 1
    len_list = []
    higher_num = len(testcases) % session_num
    lower_num = session_num - higher_num
    for _ in range(higher_num):
        len_list.append(ceil(len(testcases)/session_num))
    for _ in range(lower_num):
        len_list.append(floor(len(testcases)/session_num))
    print("We have split %d test cases into %d sessions: %s" % (len(testcases), session_num, str(len_list)))
    all_sessions = []
    start = 0
    for i in range(session_num):
        temp = copy.deepcopy(run_id_info)
        temp["test_cases"] = testcases[start:start+len_list[i]]
        all_sessions.append(temp)
        start += len_list[i]
    return all_sessions


# main function
def main(device_dict, user_info_object):
    try:
        # get module info
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        temp_ini_file = os.path.join(
            os.path.join(
                os.path.abspath(__file__).split("Framework")[0],
                os.path.join(
                    "AutomationLog",
                    ConfigModule.get_config_value("Advanced Options", "_file"),
                ),
            )
        )
        # add temp file to config values
        ConfigModule.add_config_value("sectionOne", "sTestStepExecLogId", sModuleInfo, temp_ini_file)

        # get local machine user id
        Userid = (CommonUtil.MachineInfo().getLocalUser()).lower()

        get_json, all_file_specific_steps = True, {}
        save_path = Path(ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file)) / "attachments"
        cnt = 0
        for i in os.walk(save_path):
            if get_json:
                get_json = False
                json_path = Path(i[0]) / i[2][0]
                folder_list = i[1]
                for j in folder_list:
                    all_file_specific_steps[j] = {}
            else:
                for j in i[2]:
                    all_file_specific_steps[folder_list[cnt]][j] = str(Path(i[0]) / j)
                cnt += 1
        # TODO: Remove all_file_specific_steps at a later period. keeping this only for custom driver purpose
        with open(json_path, "r") as f:
            all_run_id_info = json.loads(f.read())

        if len(all_run_id_info) == 0:
            CommonUtil.ExecLog("", "No Test Run Schedule found for the current user : %s" % Userid, 2)
            return False

        executor = CommonUtil.GetExecutor()
        CommonUtil.runid_index = 0
        for run_id_info in all_run_id_info:
            run_id_info["base_path"] = ConfigModule.get_config_value("Advanced Options", "_file_upload_path")
            run_id = run_id_info["run_id"]
            server_version = run_id_info["release_version"]
            release_name = run_id_info["release_name"]
            release_info = run_id_info["release_info"]
            CommonUtil.ExecLog(
                "",
                "Server version = %s\nServer Release Date = %s\nServer Release Note = %s" % (server_version, release_name, release_info),
                4,
                False,
            )
            debug_info = ""
            CommonUtil.clear_all_logs()

            CommonUtil.run_cancelled = False
            thr = executor.submit(check_run_cancel, run_id)
            CommonUtil.SaveThread("run_cancel", thr)

            # Write testcase json
            path = ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file) / Path(run_id.replace(":", "-"))
            FL.CreateFolder(path)

            # Start websocket server if we're in debug mode.
            if run_id.lower().startswith("debug"):
                # CommonUtil.ExecLog(
                #     "",
                #     "\n********************************\n*    STARTING DEBUG SESSION    *\n********************************",
                #     4,
                #     False,
                # )
                CommonUtil.debug_status = True
                print("[LIVE LOG] Connecting to Live Log service")
                ws.connect()
                print("[LIVE LOG] Connected to Live Log service")
            else:
                # CommonUtil.ExecLog(
                #     "",
                #     "\n******************************\n*    STARTING RUN SESSION    *\n******************************",
                #     4,
                #     False,
                # )
                CommonUtil.debug_status = False
                cleanup_driver_instances()  # clean up drivers
                shared.Clean_Up_Shared_Variables()  # clean up shared variables
            device_order = run_id_info["device_info"]
            final_dependency = run_id_info["dependency_list"]
            is_linked = run_id_info["is_linked"]
            final_run_params_from_server = run_id_info["run_time"]
            if not CommonUtil.debug_status:
                rem_config = {
                    "threading": run_id_info["threading"] if "threading" in run_id_info else False,
                    "local_run": run_id_info["local_run"] if "local_run" in run_id_info else False,
                    "take_screenshot": run_id_info["take_screenshot"] if "take_screenshot" in run_id_info else True,
                    "upload_log_file_only_for_fail": run_id_info["upload_log_file_only_for_fail"] if "upload_log_file_only_for_fail" in run_id_info else True,
                    # "rerun_on_fail": run_id_info["rerun_on_fail"] if "rerun_on_fail" in run_id_info else False,
                    "rerun_on_fail": False,     # Turning off rerun until its completed
                    "window_size_x": run_id_info["window_size_x"] if "window_size_x" in run_id_info else "",
                    "window_size_y": run_id_info["window_size_y"] if "window_size_y" in run_id_info else "",
                }
                if ConfigModule.get_config_value("RunDefinition", "local_run") == "True":
                    rem_config["local_run"] = True
                ConfigModule.remote_config = rem_config
            else:
                rem_config = {
                    "threading": False,
                    "local_run": False,
                    "take_screenshot": True,
                }
                if ConfigModule.get_config_value("RunDefinition", "local_run") == "True":
                    rem_config["local_run"] = True
                ConfigModule.remote_config = rem_config
                debug_info = {"debug_clean": run_id_info["debug_clean"], "debug_steps": run_id_info["debug_steps"]}
                if "debug_step_actions" in run_id_info:
                    debug_info["debug_step_actions"] = run_id_info["debug_step_actions"]
                if run_id_info["debug_clean"] == "YES":
                    cleanup_driver_instances()
                    shared.Clean_Up_Shared_Variables()
            driver_list = ["Not needed currently"]

            final_run_params = {}
            for param in final_run_params_from_server:
                final_run_params[param] = CommonUtil.parse_value_into_object(list(final_run_params_from_server[param].items())[1][1])
                # final_run_params[param] = CommonUtil.parse_value_into_object(list(final_run_params_from_server[param].items())[0][1])
                # final_run_params[param] = CommonUtil.parse_value_into_object(final_run_params_from_server[param]["subfield"])
                # final_run_params[param] = final_run_params_from_server[param].split(":", 1)[1].strip()  # For TD

            send_log_file_only_for_fail = ConfigModule.get_config_value("RunDefinition", "upload_log_file_only_for_fail")
            send_log_file_only_for_fail = False if send_log_file_only_for_fail.lower() == "false" else True
            rerun_on_fail = ConfigModule.get_config_value("RunDefinition", "rerun_on_fail")
            rerun_on_fail = False if rerun_on_fail.lower() == "false" else True
            CommonUtil.upload_on_fail, CommonUtil.rerun_on_fail = send_log_file_only_for_fail, rerun_on_fail
            shared.Set_Shared_Variables("zeuz_auto_teardown", "on")

            all_testcases_info = run_id_info["test_cases"]
            TestSetStartTime = time.time()
            i = 0
            while i < len(all_testcases_info):
                if all_testcases_info[i]["automatability"] != "Automated":
                    CommonUtil.ExecLog("", all_testcases_info[i]["testcase_no"] + " is not automated so skipping", 2)
                    # print(all_testcases_info[i]["testcase_no"] + " is not automated so skipping")
                    del all_testcases_info[i]
                    i -= 1
                i += 1
            if len(all_testcases_info) > 0:
                CommonUtil.ExecLog("", "Total number of Automated test cases %s" % len(all_testcases_info), 4, False)
            else:
                CommonUtil.ExecLog("", "No Automated test cases found for the current user : %s" % Userid, 2)
                CommonUtil.runid_index += 1
                return "pass"
            num_of_tc = len(all_testcases_info)
            cnt = 1

            max_tc_in_single_session = 50    # Todo: make it 25
            all_sessions = split_testcases(run_id_info, max_tc_in_single_session)
            session_cnt = 1
            for each_session in all_sessions:
                CommonUtil.current_session_name = "session_" + str(session_cnt)
                CommonUtil.all_logs_json = [each_session]
                CommonUtil.tc_index = 0
                all_testcases_info = each_session["test_cases"]
                print("Starting %s with %s testcases" % (CommonUtil.current_session_name, len(all_testcases_info)))
                for testcase_info in all_testcases_info:
                    performance_test_case = False
                    if testcase_info["automatability"].lower() == "performance":
                        performance_test_case = True
                    test_case_no = testcase_info["testcase_no"]
                    test_case_name = testcase_info["title"]
                    set_device_info_according_to_user_order(device_order, device_dict, test_case_no, test_case_name, user_info_object, Userid)
                    CommonUtil.disabled_step = []

                    if performance_test_case:
                        # get performance test info
                        perf_data = testcase_info["performance data"]
                        hatch_rate = perf_data["hatch_rate"]
                        no_of_users = perf_data["no_of_users"]
                        time_period = perf_data["time_period"]

                        # write locust input file
                        write_locust_input_file(
                            time_period,
                            perf_data,
                            test_case_no,
                            sModuleInfo,
                            run_id,
                            driver_list,
                            final_dependency,
                            final_run_params,
                            temp_ini_file,
                            is_linked,
                            send_log_file_only_for_fail=send_log_file_only_for_fail,
                        )

                        # check locust file name
                        locustFile = "chromeLocustFile.py"
                        if "Browser" in final_dependency:
                            if final_dependency["Browser"].lower() == "chrome":
                                locustFile = "chromeLocustFile.py"
                            else:
                                locustFile = "firefoxLocustFile.py"
                        else:
                            locustFile = "restLocustFile.py"

                        # get locust file path
                        locust_file_path = (
                            os.getcwd()
                            + os.sep
                            + "Built_In_Automation"
                            + os.sep
                            + "Performance_Testing"
                            + os.sep
                            + locustFile
                        )

                        # make locust query
                        locustQuery = (
                                "locust -f %s --csv=csvForZeuz --no-web --host=http://example.com -c %d -r %d"
                                % (locust_file_path, no_of_users, hatch_rate)
                        )

                        # add log
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Running Performance Test Case %s with total %d users, in a rate %s new users/second and each user will run for %s seconds"
                            % (test_case_no, no_of_users, hatch_rate, time_period),
                            1,
                        )
                        try:
                            def kill(process):
                                return process.kill()  # kill process function
                            process = subprocess.Popen(locustQuery, shell=True)  # locust query process
                            my_timer = Timer(no_of_users * time_period, kill, [process])  # set timer
                            try:
                                my_timer.start()  # start timer
                                stdout, stderr = process.communicate()  # process communicate
                            finally:
                                my_timer.cancel()  # cancel timer
                        except Exception as e:
                            print("exception")
                            pass
                        # add log
                        CommonUtil.ExecLog(sModuleInfo, "Uploading Performance Test Results", 1)
                        if ConfigModule.get_config_value("RunDefinition", "local_run") == "False":
                            # upload info
                            upload_csv_file_info(run_id, test_case_no)
                        # add log
                        CommonUtil.ExecLog(
                            sModuleInfo, "Performance Test Results Uploaded Successfully", 1
                        )
                    else:
                        run_test_case(
                            test_case_no,
                            sModuleInfo,
                            run_id,
                            final_dependency,
                            final_run_params,
                            temp_ini_file,
                            testcase_info,
                            debug_info,
                            all_file_specific_steps,
                            rerun_on_fail,
                            server_version,
                            send_log_file_only_for_fail,
                        )
                        CommonUtil.clear_all_logs()  # clear logs
                        if CommonUtil.run_cancel == CANCELLED_TAG:
                            break
                        print("Executed %s test cases" % cnt)
                        cnt += 1
                    CommonUtil.tc_index += 1

                # calculate elapsed time of runid
                sTestSetEndTime = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
                TestSetEndTime = time.time()
                TimeDiff = TestSetEndTime - TestSetStartTime
                TimeInSec = int(TimeDiff)
                TestSetDuration = CommonUtil.FormatSeconds(TimeInSec)

                after_execution_dict = {
                    "status": "Complete",
                    "teststarttime": datetime.fromtimestamp(TestSetStartTime).strftime("%Y-%m-%d %H:%M:%S"),
                    "testendtime": sTestSetEndTime,
                    "duration": TestSetDuration
                }
                CommonUtil.CreateJsonReport(setInfo=after_execution_dict)

                if float(server_version.split(".")[0]) < 7:
                    upload_json_report_old(Userid, temp_ini_file, run_id)
                else:
                    upload_reports_and_zips(Userid, temp_ini_file, run_id)

                session_cnt += 1

            print("Test set execution time = %s sec for %s testcases" % (round(TimeDiff, 3), num_of_tc))
            # print("Report creation time = %s sec for %s testcases" % (round(CommonUtil.report_json_time, 3), num_of_tc))
            print("Test Set Completed")

            ConfigModule.add_config_value("sectionOne", "sTestStepExecLogId", "MainDriver", temp_ini_file)

            if CommonUtil.run_cancel == CANCELLED_TAG:
                print("Test Set Cancelled by the User")
            elif not CommonUtil.debug_status:

                from distutils.dir_util import copy_tree

                # If node is running in device farm, copy the logs and reports to the expected directory.
                if "DEVICEFARM_LOG_DIR" in os.environ:
                    log_dir = Path(os.environ["DEVICEFARM_LOG_DIR"])
                    zeuz_log_dir = Path(ConfigModule.get_config_value(
                        "sectionOne", "test_case_folder", temp_ini_file
                    )).parent

                    copy_tree(str(zeuz_log_dir), str(log_dir))

                # Telling the node_manager that a run_id is finished
                CommonUtil.node_manager_json(
                    {
                        "state": "complete",
                        "report": {
                            "zip": "Will do later" + ".zip",
                            "directory": "Will do later",
                        }
                    }
                )

                # executor.submit(upload_json_report)

            # Close websocket connection.
            elif CommonUtil.debug_status:
                ws.close()
                print("[LIVE LOG] Disconnected from Live Log service")
            CommonUtil.runid_index += 1

            # Terminating all run_cancel threads after finishing a run_id
            CommonUtil.run_cancel = ""
            CommonUtil.run_cancelled = True
            if "run_cancel" in CommonUtil.all_threads:
                for t in CommonUtil.all_threads["run_cancel"]:
                    t.result()
                    CommonUtil.run_cancelled = True
                del CommonUtil.all_threads["run_cancel"]
            CommonUtil.run_cancelled = False

            break   # Todo: remove this after server side multiple run-id problem is fixed

        return "pass"
    except:
        CommonUtil.debug_code_error(sys.exc_info())
        return None



if __name__ == "__main__":
    main()
