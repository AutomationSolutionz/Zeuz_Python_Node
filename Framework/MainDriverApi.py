# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
import concurrent.futures
import copy
import json
import inspect
import os
import time
import sys
from typing import Any, Dict
from urllib.parse import urlparse
import urllib.request, urllib.error, urllib.parse
import queue
import shutil
import importlib
import requests
import zipfile
from multiprocessing.pool import ThreadPool
from urllib3.exceptions import InsecureRequestWarning
import pyperclip
# Suppress the InsecureRequestWarning since we use verify=False parameter.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
import threading
import subprocess
from pathlib import Path, PurePosixPath
from sys import platform as _platform
from datetime import datetime
from datetime import timedelta
import pytz
from threading import Timer
from Framework.attachment_db import AttachmentDB, GlobalAttachment
from Framework.Built_In_Automation import Shared_Resources
from .Utilities import ConfigModule, FileUtilities as FL, CommonUtil, RequestFormatter
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as shared,
)
from settings import PROJECT_ROOT
from reporting import junit_report

from jinja2 import Environment, FileSystemLoader
from genson import SchemaBuilder
import selenium

from rich.style import Style
from rich.table import Table
from rich.console import Console
from rich.box import ASCII_DOUBLE_HEAD, DOUBLE
from rich.padding import Padding
from jinja2 import Environment, FileSystemLoader
from time import sleep

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
# TODO: remove, need alternative
def set_server_variable(run_id, key, value):
    return RequestFormatter.Get(
        "set_server_variable_api", {"run_id": run_id, "var_name": key, "var_val": value}
    )


# gets server variable
# TODO: remove, need alternative
def get_server_variable(run_id, key):
    return RequestFormatter.Get(
        "get_server_variable_api", {"run_id": run_id, "var_name": key}
    )


# get global list variable
# TODO: remove, need alternative
def get_global_list_variable(name):
    return RequestFormatter.Get(
        "set_or_get_global_server_list_variable_api", {"name": name}
    )


# append to global list variable
# TODO: remove, need alternative
def append_to_global_list_variable(name, value):
    return RequestFormatter.Get(
        "append_value_to_global_server_list_variable_api",
        {"name": name, "value": value},
    )


# remove item from global list variable
# TODO: remove, need alternative
def remove_item_from_global_list_variable(name, value):
    return RequestFormatter.Get(
        "delete_global_server_list_variable_by_value_api",
        {"name": name, "value": value},
    )


# get all server variable
# TODO: remove, need alternative
def get_all_server_variable(run_id):
    return RequestFormatter.Get("get_all_server_variable_api", {"run_id": run_id})


# if run is cancelled then it can be called, it cleans up the runid from database
# TODO: remove, unnecessary
def cleanup_runid_from_server(run_id):
    RequestFormatter.Get("clean_up_run_api", {"run_id": run_id})


# returns current status of the runid
# TODO: remove, unnecessary
def get_status_of_runid(run_id):
    return RequestFormatter.Get("get_status_of_a_run_api", {"run_id": run_id})


# TODO: Remove
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
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        log_file_path = ConfigModule.get_config_value(
            "sectionOne", "temp_run_file_path", temp_ini_file
        )
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

    run_id_folder = str(Path(log_file_path)/run_id.replace(":", "-"))
    test_case_folder = str(Path(run_id_folder)/CommonUtil.current_session_name/test_case.replace(":", "-"))

    # TODO: Use pathlib for following items
    # create test_case_folder
    ConfigModule.add_config_value("sectionOne", "test_case", test_case, temp_ini_file)
    ConfigModule.add_config_value("sectionOne", "test_case_folder", test_case_folder, temp_ini_file)
    CommonUtil.ExecLog(sModuleInfo, f"Creating folder: {test_case_folder}", 5)
    FL.CreateFolder(test_case_folder)

    # create log_folder for browser console error logs
    log_folder = test_case_folder + os.sep + "Log"
    ConfigModule.add_config_value("sectionOne", "log_folder", log_folder, temp_ini_file)
    CommonUtil.ExecLog(sModuleInfo, f"Creating folder: {log_folder}", 5)
    FL.CreateFolder(log_folder)

    # create screenshot_folder
    screenshot_folder = test_case_folder + os.sep + "screenshots"
    ConfigModule.add_config_value("sectionOne", "screen_capture_folder", screenshot_folder, temp_ini_file)
    CommonUtil.ExecLog(sModuleInfo, f"Creating folder: {screenshot_folder}", 5)
    FL.CreateFolder(screenshot_folder)

    # performance report folder
    performance_report = test_case_folder + os.sep + "performance_report"
    ConfigModule.add_config_value("sectionOne", "performance_report", performance_report, temp_ini_file)
    CommonUtil.ExecLog(sModuleInfo, f"Creating folder: {performance_report}", 5)
    FL.CreateFolder(performance_report)

    # TODO: we'll be breaking internal server compatibility anyway
    # ! This will be unnecessary
    if float(server_version.split(".")[0]) >= 7:
        # json report folder
        json_report = test_case_folder + os.sep + "json_report"
        ConfigModule.add_config_value("sectionOne", "json_report", json_report, temp_ini_file)
        CommonUtil.ExecLog(sModuleInfo, f"Creating folder: {json_report}", 5)
        FL.CreateFolder(json_report)

    # create where attachments from selenium browser will be
    # downloaded
    # ? Why are we keeping two separate download folders?
    zeuz_download_folder = test_case_folder + os.sep + "zeuz_download_folder"
    CommonUtil.ExecLog(sModuleInfo, f"Creating folder: {zeuz_download_folder}", 5)
    FL.CreateFolder(zeuz_download_folder)
    initial_download_folder = run_id_folder + os.sep + "initial_download_folder"
    CommonUtil.ExecLog(sModuleInfo, f"Creating folder: {initial_download_folder}", 5)
    FL.CreateFolder(initial_download_folder)
    ConfigModule.add_config_value("sectionOne", "initial_download_folder", initial_download_folder, temp_ini_file)
    shared.Set_Shared_Variables("zeuz_download_folder", zeuz_download_folder)

    # ? Can't we run the above folder creation codes only once when
    # the node starts or when main driver is called for the first
    # time?

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
    test_steps_data,
    test_action_info,
    debug_actions=None
):
    try:
        q = queue.Queue()  # define queue

        # get step driver
        current_driver = all_step_info[StepSeq-1]["step_driver_type"]
        # current_driver = "Built_In_Driver"
        try:
            current_driver = "Drivers." + current_driver
            # if CommonUtil.step_module_name is None:
            module_name = importlib.import_module(current_driver)  # get module
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
                            test_steps_data,
                            test_action_info,
                            simple_queue,
                            debug_actions,
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
                        test_steps_data,
                        test_action_info,
                        simple_queue,
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
        attachment_path = Path(ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file)) / "attachments"
        tc_attachment_list = []
        for tc_attachment in testcase_info['attachments']:
            var_name = PurePosixPath(tc_attachment["path"]).name
            path = str(attachment_path / tc_attachment["id"] / var_name)
            tc_attachment_list.append(var_name)
            shared.Set_Shared_Variables(var_name, path, attachment_var=True)

        all_step_info = testcase_info["steps"]
        all_step_dataset, all_action_info, step_attachment_list = [], [], []
        for step_info in all_step_info:
            all_Action_info = step_info["actions"]
            all_action_data_set, all_action_Info = [], []
            for action_info in all_Action_info:
                action_dataset = action_info["step_actions"]
                all_action_data_set.append(action_dataset)
                Dict = {}
                Dict["Action disabled"] = action_info["action_disabled"]
                Dict["Action name"] = action_info["action_name"]
                all_action_Info.append(Dict)
            all_step_dataset.append(all_action_data_set)
            all_action_info.append(all_action_Info)

            step_attachments = step_info['attachments']
            step_attachment_list = []
            for attachment in step_attachments:
                attachment_name = PurePosixPath(attachment["path"]).name
                path = str(attachment_path / f"STEP-{attachment['id']}" / attachment_name)
                step_attachment_list.append(attachment_name)
                shared.Set_Shared_Variables(attachment_name, path, attachment_var=True)

        while StepSeq <= Stepscount:
            CommonUtil.custom_step_duration = ""
            this_step = all_step_info[StepSeq - 1]
            if debug and debug_steps:
                if str(StepSeq) not in debug_steps:
                    StepSeq += 1
                    CommonUtil.step_index += 1
                    continue

            # check if already failed
            if already_failed:
                if this_step["always_run"]:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Step-%s is set as 'Always run' so executing this step" % (CommonUtil.step_index + 1),
                        2,
                    )
                # TODO: Revisit the todo on the right
                elif "run_on_fail" in this_step and this_step["run_on_fail"]:     # Todo: Remove the 1st condition when all servers are updated
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Step-%s is set as 'Run on fail' and the test case has already failed so executing this step" % (CommonUtil.step_index + 1),
                        2,
                    )
                else:
                    StepSeq += 1
                    CommonUtil.step_index += 1
                    continue

            elif not already_failed and "run_on_fail" in this_step and this_step["run_on_fail"]:     # Todo: Remove the 2nd condition when all servers are updated
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Step-%s is set as 'Run on fail' and the test case has not failed yet so skipping this step" % (CommonUtil.step_index + 1),
                    2,
                )
                StepSeq += 1
                CommonUtil.step_index += 1
                continue

            CommonUtil.current_step_name = current_step_name = this_step["step_name"]
            CommonUtil.current_step_id = current_step_id = this_step["step_id"]
            CommonUtil.current_step_sequence = current_step_sequence = this_step["step_sequence"]
            shared.Set_Shared_Variables("zeuz_current_step_name", current_step_name, print_variable=False, pretty=False)
            shared.Set_Shared_Variables("zeuz_current_step_sequence", current_step_sequence, print_variable=False, pretty=False)
            shared.Set_Shared_Variables("zeuz_total_step_count", len(all_step_info), print_variable=False, pretty=False)

            shared.Set_Shared_Variables("zeuz_current_step", this_step, print_variable=False, pretty=False)

            ConfigModule.add_config_value(
                "sectionOne",
                "sTestStepExecLogId",
                run_id + "|" + test_case + "|" + str(current_step_id) + "|" + str(current_step_sequence),
                temp_ini_file,
            )
            CommonUtil.current_step_no = str(current_step_sequence)
            _color = "yellow"
            # _style = Style(color="yellow", blink=False, bold=True)
            table = Table(border_style=_color, box=ASCII_DOUBLE_HEAD, expand=False)
            table.add_column(
                f"ID",
                justify="center",
                style=_color,
                max_width=5,
            )
            table.add_column(
                f"STEP #{StepSeq}",
                justify="center",
                style=_color,
                max_width=40,
            )
            table.add_column(
                f"Always run",
                justify="center",
                style=_color,
                min_width=6,
                max_width=6,
            )
            table.add_column(
                f"Type",
                justify="center",
                style=_color,
                max_width=6,
            )
            table.add_row(
                f"{this_step['step_id']}",
                f"{current_step_name}",
                f"{this_step['always_run']}",
                "global" if this_step['type'] == "linked" else "local",
                style=_color,
            )
            # width_pad = CommonUtil.max_char // 2 - (max(len(current_step_name), 6) + 4) // 2
            # table = Padding(table, (0, width_pad))
            rich_print(table)

            test_steps_data = all_step_dataset[StepSeq-1]
            test_action_info = all_action_info[StepSeq-1]
            CommonUtil.all_step_dataset = all_step_dataset
            CommonUtil.all_action_info = all_action_info

            # FIXME: If either one of run on fail or step time throws an
            # exception, both values will be set to a default value. So it has
            # the possibility to ignore one of the other correct values.
            try:
                test_case_continue = this_step["continue_on_fail"]
                step_time = this_step["step_time"]
                if str(step_time) != "" and step_time is not None:
                    step_time = int(step_time)
                else:
                    step_time = 59
            except:
                test_case_continue = False
                step_time = 59

            # get step start time
            TestStepStartTime = time.perf_counter()
            sTestStepStartTime = datetime.fromtimestamp(TestStepStartTime, tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S.%f")
            WinMemBegin = CommonUtil.PhysicalAvailableMemory()  # get available memory

            if StepSeq in CommonUtil.disabled_step or not this_step['step_enable']:
                CommonUtil.ExecLog(sModuleInfo, "STEP-%s is disabled" % StepSeq, 2)
                sStepResult = "skipped"
            elif CommonUtil.testcase_exit:
                CommonUtil.ExecLog(sModuleInfo, "STEP-%s is skipped" % StepSeq, 2)
                sStepResult = "skipped"
            else:
                sStepResult = call_driver_function_of_test_step(
                    sModuleInfo,
                    all_step_info,
                    StepSeq,
                    step_time,
                    current_step_name,
                    test_steps_data,
                    test_action_info,
                    debug_actions,
                )

            TestStepEndTime = time.perf_counter()
            sTestStepEndTime = datetime.fromtimestamp(TestStepEndTime, tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S.%f")
            WinMemEnd = CommonUtil.PhysicalAvailableMemory()  # get available memory
            CommonUtil.step_perf.append({
                "id": current_step_id,
                "name": current_step_name,
                "sequence": current_step_sequence,
                "runtime": round(TestStepEndTime - TestStepStartTime, 5),
                "time_stamp": CommonUtil.get_timestamp(),
                "status": sStepResult,
            })
            if CommonUtil.custom_step_duration:
                TestStepDuration = CommonUtil.custom_step_duration
                CommonUtil.custom_step_duration = ""
            else:
                sec = TestStepEndTime - TestStepStartTime
                hours, remainder = sec // 3600, sec % 3600
                minutes, seconds = remainder // 60, remainder % 60
                TestStepDuration = "%02d:%02d:%s" % (hours, minutes, round(seconds, 3))
            TestStepMemConsumed = WinMemBegin - WinMemEnd  # get memory consumed
            # for i in step_attachment_list: shared.Remove_From_Shared_Variables(i, attachment_var=True)  # Cleanup step_attachment variables

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
            with concurrent.futures.ThreadPoolExecutor() as executor:
                thr = executor.submit(upload_step_report, run_id, test_case, this_step["step_sequence"], this_step["step_id"], after_execution_dict)
                CommonUtil.SaveThread("step_report", thr)

            StepSeq += 1
            CommonUtil.step_index += 1

            if CommonUtil.run_cancel == CANCELLED_TAG:
                CommonUtil.ExecLog(sModuleInfo, "Test Run status is Cancelled. Exiting the current Test Case...%s" % test_case, 2)
                CommonUtil.run_cancelled = True
                break

        for i in tc_attachment_list: shared.Remove_From_Shared_Variables(i, attachment_var=True)   # Cleanup tc_attachment variables
        CommonUtil.show_log = True
        return sTestStepResultList
    except:
        CommonUtil.Exception_Handler(sys.exc_info())
        raise Exception


# from the returned step results, it finds out the test case result
def calculate_test_case_result(sModuleInfo, TestCaseID, run_id, sTestStepResultList, testcase_info):
    if CommonUtil.testcase_exit:
        CommonUtil.ExecLog(sModuleInfo, f"Test Case {CommonUtil.testcase_exit}", 1)
        return CommonUtil.testcase_exit
    elif "BLOCKED" in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Blocked", 3)
        return "Blocked"
    elif "CANCELLED" in sTestStepResultList or "Cancelled" in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Cancelled", 3)
        return "Cancelled"
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
        return sTestCaseStatus

    elif "WARNING" in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Contain Warning(s)", 2)
        return "Failed"
    elif "NOT RUN" in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Contain Not Run Steps", 2)
        return "Failed"
    elif all([i == "SKIPPED" for i in sTestStepResultList]):
        CommonUtil.ExecLog(sModuleInfo, "Test Case Skipped", 1)
        return "Skipped"
    elif "PASSED" in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Passed", 1)
        return "Passed"
    else:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Status Unknown", 2)
        return "Unknown"


# writes the log file for a test case
def zip_and_delete_tc_folder_old(
    sTestCaseStatus,
    temp_ini_file,
    send_log_file_only_for_fail=True,
):
    # if settings checked, then send log file or screenshots, otherwise don't send
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    if sTestCaseStatus not in passed_tag_list or sTestCaseStatus in passed_tag_list and not send_log_file_only_for_fail:
        if ConfigModule.get_config_value("RunDefinition", "local_run") == "False":
            FL.ZipFolder(
                ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file),
                ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file) + ".zip",
            )
    path = ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file)
    CommonUtil.ExecLog(sModuleInfo, f"Deleting folder: {path}", 5)
    FL.DeleteFolder(path)


# writes the log file for a test case
def zip_and_delete_tc_folder(
    run_id,
    TestCaseID,
    sTestCaseStatus,
    temp_ini_file,
    send_log_file_only_for_fail=True,

):
    # if settings checked, then send log file or screenshots, otherwise don't send
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    if sTestCaseStatus not in passed_tag_list or sTestCaseStatus in passed_tag_list and not send_log_file_only_for_fail:
        if ConfigModule.get_config_value("RunDefinition", "local_run") == "False":
            all_steps = CommonUtil.all_logs_json[CommonUtil.runid_index]["test_cases"][CommonUtil.tc_index]["steps"]
            for step in all_steps:
                json_filename = Path(ConfigModule.get_config_value("sectionOne", "json_report", temp_ini_file))/(str(step["step_sequence"])+".json")
                with open(json_filename, "w", encoding="utf-8") as f:
                    json.dump(step, f)

            zip_name = run_id.replace(":", "-") + "_" + TestCaseID.replace(":", "-") + ".zip"
            FL.ZipFolder(
                ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file),
                str(Path(ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file)).parent/zip_name),
            )
    # Delete the folder
    path = ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file)
    CommonUtil.ExecLog(sModuleInfo, f"Deleting folder: {path}", 5)
    FL.DeleteFolder(path)


def cleanup_driver_instances():  # cleans up driver(selenium, appium) instances
    try:  # if error happens. we don't care, main driver should not stop, pass in exception
        import Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions as Selenium
        try:
            Selenium.Tear_Down_Selenium()
        except:
            pass
        if shared.Test_Shared_Variables("appium_details"):
            import Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions as Appium
            driver = shared.Remove_From_Shared_Variables("appium_details")
            if driver not in failed_tag_list:
                Appium.teardown_appium()
    except:
        pass


def advanced_float(text:str) -> float:
    try:
        return float(text)
    except:
        import re
        nums = re.findall(r"-?\d+\.?\d*", text)
        if len(nums) == 0:
            raise ValueError(f"could not convert string to float: '{text}'")
        num = nums[0]
        num = num[:-1] if num.endswith('.') else num
        return float(num)


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
        shared.shared_variables.update({
            "clipboard_paste": pyperclip.paste,
            "clipboard_set": pyperclip.copy,
            "num": advanced_float,
            "urlparse": urlparse,
        })
        shared.Set_Shared_Variables("zeuz_window_auto_switch", "on")

    except:
        CommonUtil.Exception_Handler(sys.exc_info())
        raise Exception


def send_to_bigquery(execution_log, metrics):
    # Skip sending to gcp if credentials not available in environment.
    if "GCP_BIGQUERY_ACTIONS_TABLE_ID" not in os.environ:
        return
    from google.cloud import bigquery

    client = bigquery.Client()

    # Table identifiers - these should be coming from zeuz server.
    actions_table_id = os.environ["GCP_BIGQUERY_ACTIONS_TABLE_ID"]
    steps_table_id = os.environ["GCP_BIGQUERY_STEPS_TABLE_ID"]
    browser_perf_table_id = os.environ["GCP_BIGQUERY_BROWSER_PERF_TABLE_ID"]
    test_cases_table_id = os.environ["GCP_BIGQUERY_TEST_CASES_TABLE_ID"]

    run_id = execution_log["run_id"]
    tc_id = execution_log["test_cases"][0]["testcase_no"]

    steps = metrics["node"]["steps"]
    actions = metrics["node"]["actions"]
    test_cases = metrics["node"]["test_cases"]
    for i in range(len(test_cases)):
        test_cases[i]['tc_title'] = execution_log["test_cases"][i]["title"]
    try:
        browser_perf = metrics["browser_performance"]["default"]
    except:
        browser_perf = list()

    # A dict of step id to step name
    step_names = {}
    for step in steps:
        step_names[step["id"]] = step["name"]


    def send(table, rows, msg):
        errors = client.insert_rows_json(table, rows)
        if len(errors) == 0:
            print(f"Sent {msg} metrics report to BigQuery")
        else:
            print(f"Encountered errors while inserting rows for {msg}: {errors}")


    def send_actions_metrics():
        if actions:
            for action in actions:
                action["run_id"] = run_id
                action["tc_id"] = tc_id
                action["step_name"] = step_names[action["step_id"]]

            send(actions_table_id, actions, "actions")


    def send_steps_metrics():
        for step in steps:
            step["run_id"] = run_id
            step["tc_id"] = tc_id
            step["step_id"] = step["id"]
            del step["id"]
            step["step_name"] = step["name"]
            del step["name"]
            step["step_sequence"] = step["sequence"]
            del step["sequence"]

        send(steps_table_id, steps, "step")


    def send_test_case_metrics():
        send(test_cases_table_id, test_cases, "test case")


    def send_browser_perf_metrics():
        if len(browser_perf) == 0:
            return

        for entry in browser_perf:
            entry["run_id"] = run_id

        send(browser_perf_table_id, browser_perf, "browser perf")


    send_actions_metrics()
    send_steps_metrics()
    send_test_case_metrics()
    send_browser_perf_metrics()


def check_test_skip(run_id, tc_num, skip_remaining=True) -> bool:
    if run_id not in CommonUtil.skip_testcases:
        return False
    if skip_remaining and 'skip remaining' in CommonUtil.skip_testcases[run_id]:
        return True
    if tc_num in CommonUtil.skip_testcases[run_id]:
        return True
    ranges = [i for i in CommonUtil.skip_testcases[run_id] if type(i) == range]
    if len(ranges) == 0:
        return False

    target = CommonUtil.tc_nums[run_id].index(tc_num)
    for rang in ranges:
        start = CommonUtil.tc_nums[run_id].index(rang.start) if rang.start in CommonUtil.tc_nums[run_id] else None
        end = CommonUtil.tc_nums[run_id].index(rang.stop) if rang.stop in CommonUtil.tc_nums[run_id] else None
        if start is None and end is None:
            continue
        if start is None and target <= end:
            continue
        if end is None and start <= target:
            return True
        if start is not None and end is not None and start <= target <= end:
            return True

    return False


def run_test_case(
    TestCaseID,
    sModuleInfo,
    run_id,
    temp_ini_file,
    testcase_info,
    debug_info,
    rerun_on_fail,
    server_version,
    send_log_file_only_for_fail=True,
    performance=False,
    browserDriver=None,
):
    try:
        TestCaseStartTime = time.time()
        test_case = str(TestCaseID).replace("#", "no")
        CommonUtil.current_tc_no = test_case
        CommonUtil.current_tc_name = testcase_info['title']
        CommonUtil.load_testing = False
        CommonUtil.clear_performance_metrics()
        CommonUtil.global_sleep = {"selenium":{}, "appium":{}, "windows":{}, "desktop":{}}

        # Added this two global variable in CommonUtil to save log information and save filepath of test case report
        CommonUtil.error_log_info = ""
        ConfigModule.add_config_value("sectionOne", "sTestStepExecLogId", sModuleInfo, temp_ini_file)
        create_tc_log_ss_folder(run_id, test_case, temp_ini_file, server_version)
        set_important_variables()
        TestCaseName = testcase_info["title"]
        shared.Set_Shared_Variables("zeuz_current_tc", testcase_info, print_variable=False, pretty=False)
        if not CommonUtil.debug_status or not shared.Test_Shared_Variables("zeuz_prettify_limit"):
            shared.Set_Shared_Variables("zeuz_prettify_limit", 500)
            CommonUtil.prettify_limit = 500

        shared.Set_Shared_Variables("zeuz_attachments_dir", (Path(temp_ini_file).parent/"attachments").__str__())
        if not shared.Test_Shared_Variables("element_wait"):
            shared.Set_Shared_Variables("element_wait", 10)

        _color = "white"
        # danger_style = Style(color=_color, blink=False, bold=True)
        table = Table(border_style=_color, box=DOUBLE, expand=False, padding=1)
        table.add_column(test_case, justify="center", style=_color, max_width=40)
        table.add_row(TestCaseName, style=_color)
        # width_pad = CommonUtil.max_char//2 - (max(len(TestCaseName), len(test_case)) + 4)//2
        # table = Padding(table, (0, width_pad))
        rich_print(table)

        sTestCaseStartTime = datetime.fromtimestamp(TestCaseStartTime, tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")

        tc_num = int(TestCaseID.split('-')[1])
        # get test case start time
        if performance and browserDriver:
            shared.Set_Shared_Variables("selenium_driver", browserDriver)

        sTestCaseStatus = None
        if check_test_skip(run_id, tc_num):
            sTestStepResultList = ['SKIPPED' for i in range(len(testcase_info['steps']))]
        else:
            sTestStepResultList = run_all_test_steps_in_a_test_case(
                testcase_info,
                test_case,
                sModuleInfo,
                run_id,
                temp_ini_file,
                debug_info,
                performance
            )
            if check_test_skip(run_id, tc_num, False):
                CommonUtil.ExecLog(sModuleInfo, "Test Case Skipped", 1)
                sTestCaseStatus = 'Skipped'

        ConfigModule.add_config_value(
            "sectionOne",
            "sTestStepExecLogId",
            run_id + "|" + test_case + "|" + "none" + "|" + "none",
            temp_ini_file,
        )

        # get test case end time
        TestCaseEndTime = time.time()
        sTestCaseEndTime = datetime.fromtimestamp(TestCaseEndTime, tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")

        # Decide if Test Case Pass/Failed
        if sTestCaseStatus is None:
            sTestCaseStatus = calculate_test_case_result(sModuleInfo, test_case, run_id, sTestStepResultList, testcase_info)

        #Writing error information in a text file
        if sTestCaseStatus == "Failed" or sTestCaseStatus == "Blocked":
            test_case_folder2 = ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file)
            with open(test_case_folder2 + '/logerror.txt', 'w') as f:
                f.write(CommonUtil.error_log_info)


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
            "teststarttime": sTestCaseStartTime,
            "testendtime": sTestCaseEndTime,
            "duration": TestCaseDuration,
            "status": sTestCaseStatus,
            "failreason": ""
        }
        CommonUtil.test_case_perf.append({
            "run_id": run_id,
            "tc_id": TestCaseID,
            "status": sTestCaseStatus,
            "runtime": float(TimeDiff),
            "errors": json.dumps(CommonUtil.tc_error_logs),
            "time_stamp": CommonUtil.get_timestamp(),
        })
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

        metrics = {
            "run_id": run_id,
            "tc_id": TestCaseID,
            "browser_performance": CommonUtil.browser_perf,
            "node": {
                "actions": CommonUtil.action_perf,
                "steps": CommonUtil.step_perf,
                "test_cases": CommonUtil.test_case_perf,
                "performance_test": CommonUtil.perf_test_perf,
                "api_performance_data": CommonUtil.api_performance_data,
            }
        }

        # Saves test case results in same run-id
        test_results = {} if not shared.Test_Shared_Variables("zeuz_session_test_results") or type(shared.Get_Shared_Variables("zeuz_session_test_results")) != dict else shared.Get_Shared_Variables("zeuz_session_test_results")
        if run_id not in test_results:  # Cleanup previous run_id results
            test_results = {
                run_id: [{
                    "tc_id": TestCaseID,
                    "result": sTestCaseStatus,
                }]
            }
        else:
            test_results[run_id].append({
                "tc_id": TestCaseID,
                "result": sTestCaseStatus,
            })
        shared.Set_Shared_Variables("zeuz_session_test_results", test_results, protected=True, print_variable=False)

        after_execution_dict["metrics"] = metrics
        CommonUtil.CreateJsonReport(TCInfo=after_execution_dict)
        CommonUtil.clear_logs_from_report(send_log_file_only_for_fail, rerun_on_fail, sTestCaseStatus)

        if not CommonUtil.debug_status:
            try:
                send_to_bigquery(CommonUtil.all_logs_json[0], metrics)
            except:
                pass
        try:
            CommonUtil.clear_performance_metrics()
        except:
            pass

        if CommonUtil.debug_status:
            send_dom_variables()
        else:
            CommonUtil.Join_Thread_and_Return_Result("screenshot")
            if str(shared.Get_Shared_Variables("zeuz_auto_teardown")).strip().lower() not in ("off", "no", "false", "disable"):
                cleanup_driver_instances()
            shared.Clean_Up_Shared_Variables(run_id)

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
        sTestCaseEndTime = datetime.fromtimestamp(TestCaseEndTime, tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        TimeDiff = TestCaseEndTime - TestCaseStartTime
        TimeInSec = int(TimeDiff)
        TestCaseDuration = CommonUtil.FormatSeconds(TimeInSec)
        sTestCaseStatus = "Blocked"
        after_execution_dict = {
            "teststarttime": datetime.fromtimestamp(TestCaseStartTime, tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S"),
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


def send_dom_variables():
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        variables = []
        max_threshold = 30000
        for var_name in shared.shared_variables:
            var_value = shared.shared_variables[var_name]
            try:
                if len(json.dumps(var_value)) > max_threshold:
                    builder = SchemaBuilder()
                    builder.add_object(var_value)
                    variables.append({
                        "type": "json_schema",
                        "variable_name": var_name,
                        "variable_value": builder.to_schema(),
                        "description": "",
                    })
                else:
                    variables.append({
                        "type": "json_object",
                        "variable_name": var_name,
                        "variable_value": var_value,
                        "description": "",
                    })
            except (json.decoder.JSONDecodeError, TypeError):
                # CommonUtil.Exception_Handler(sys.exc_info())
                variables.append({
                    "type": f"non_json: {str(type(var_value))}",
                    "variable_name": var_name,
                    "variable_value": "",
                    "description": "",
                })
            except Exception as e:
                CommonUtil.ExecLog(sModuleInfo, e.msg, 2)

        if shared.Test_Shared_Variables('selenium_driver'):
            try:
                selenium_driver = shared.Get_Shared_Variables("selenium_driver")
                dom = selenium_driver.execute_script("""
                    var html = document.createElement('html');
                    html.setAttribute('zeuz','aiplugin');
                    var myString = document.documentElement.outerHTML;
                    html.innerHTML = myString;
                    
                    var elements = html.getElementsByTagName('head');
                    while (elements[0])
                        elements[0].parentNode.removeChild(elements[0])
    
                    var elements = html.getElementsByTagName('link');
                    while (elements[0])
                        elements[0].parentNode.removeChild(elements[0])
    
                    var elements = html.getElementsByTagName('script');
                    while (elements[0])
                        elements[0].parentNode.removeChild(elements[0])
    
                    var elements = html.getElementsByTagName('style');
                    while (elements[0])
                        elements[0].parentNode.removeChild(elements[0])
                    
                    // AI model works better on indented dom, so not removing indentation.
                    // var result = html.outerHTML.replace(/\s+/g, ' ').replace(/>\s+</g, '><');

                    //The following code removes non-unicode characters except newline and tab
                    var result = html.outerHTML.replace(/[\x00-\x08\x0B-\x1F\x7F]/g, '');
                    return result;""")
            except selenium.common.exceptions.JavascriptException as e:
                CommonUtil.ExecLog(sModuleInfo, e.msg, 2)
                dom = ""
            except Exception as e:
                CommonUtil.ExecLog(sModuleInfo, e.msg, 2)
                dom = None
        else:
            dom = None

        data = {
            "variables": variables,
            "dom_web": {"dom": dom},
            "node_id": shared.Get_Shared_Variables('node_id')
        }
        res = RequestFormatter.request("post",
            RequestFormatter.form_uri("node_ai_contents/"),
            data=json.dumps(data),
            verify=False
        )
        if res.status_code == 500:
            CommonUtil.ExecLog(sModuleInfo, res.json()["info"], 2)
        elif res.status_code == 404:
            CommonUtil.ExecLog(sModuleInfo, 'The chatbot API does not exist, server upgrade needed', 2)
        return
    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, e.msg, 2)


def set_device_info_according_to_user_order(device_order, device_dict,  test_case_no, test_case_name, user_info_object, Userid, **kwargs):
    # Need to set device_info for browserstack here
    global device_info
    shared.Set_Shared_Variables("device_order", device_order)
    if isinstance(device_order, list):
        try:
            # FIXME: The device info needs to be fixed for deploy v3
            for each in device_order:
                device_order_val = str(each[0])
                device_no_val = str(each[1])
                original_dict = device_dict
                device_info["device " + device_order_val] = original_dict[
                    "device " + device_no_val
                ]
        except:
            pass

    # Todo: check the device_order if it is mobile or web (reimagine after deploy v3)
    elif "web" in device_order:
        CommonUtil.ExecLog("set_device_info_according_to_user_order", "found web from new device_info", 1)
    elif "mobile" in device_order:
        if "local" in device_order["mobile"]:
            pass
        elif "browser_stack" in device_order["mobile"]:
            project = f"PROJECT:{user_info_object['project_id']} & TEAM:{user_info_object['team_id']}"
            # build = f"{test_case_no} : {test_case_name}"
            build = kwargs['run_id']
            # Todo: session_name will be the run_id of the test case. So, we can reference with our zeuz better
            # session_name = kwargs['run_id']
            session_name = f"{test_case_no} : {test_case_name}"
            # Fixme: Currently only one device will run. Need to optimize for parallel test on multiple device.
            device_info = {
                # set URL of the application under test. URL should be unique for each test case
                "app": device_order["mobile"]["browser_stack"]["app"],

                # specify device and os for testing
                "deviceName": device_order["mobile"]["browser_stack"]["environments"][0]["deviceName"],
                "platformVersion": device_order["mobile"]["browser_stack"]["environments"][0]["platformVersion"],

                # set other browserstack capabilities updated in appium v2
                "bstack:options": {
                    # "userName": os.environ.get("browser_stack_user"),
                    "userName": device_order["mobile"]["browser_stack"]["username"],
                    # "accessKey": os.environ.get("browser_stack_key"),
                    "accessKey": device_order["mobile"]["browser_stack"]["access_key"],
                    "projectName": project,
                    "buildName": build,
                    "sessionName": session_name
                }
            }

        elif "aws" in device_order["mobile"]:
            device_info = {
                "aws device 1": {}
            }
    # Todo: remove this section. Changing this for new device_info.
    # elif "browser_stack" in device_order and device_order["browser_stack"]:
    #     project ["project"]
    #     team ["team"]
    #
    #     project = "PROJECT:'" + project + "'  TEAM:'" + team + "'"
    #     build = test_case_no + " :: " + test_case_name
    #     name = Userid + " :: " + datetime.now().strftime("%d %B %Y %A %H:%M:%S")
    #     device_info = {
    #         "browserstack device 1": {
    #             "basic": {
    #                 "browserstack.user": device_order["browser_stack"]["1"]["username"],
    #                 "browserstack.key": device_order["browser_stack"]["1"]["access_key"],
    #                 # "app": "bs://227d1bd74c601618c44b1a10b36f80caf11e497a",
    #                 "app": device_order["browser_stack"]["1"]["app_url"],
    #
    #                 "device": device_order["browser_stack"]["1"]["device"],
    #                 "os_version": device_order["browser_stack"]["1"]["os_version"],
    #
    #                 "project": project,  # zeuz project + team name
    #                 "build": build,  # test case no + test case name
    #                 "name": name  # Userid + datetime
    #             },
    #             "other": {
    #                 "app_name": device_order["browser_stack"]["1"]["app_name"],
    #             },
    #
    #         }
    #     }
    # Todo: remove this section. Changing this for new device_info.
    # elif "aws" in device_order:
    #     device_info = {
    #         "aws device 1": {}
    #     }
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

    shared.Set_Shared_Variables("device_info", device_info, protected=True)


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
    # is_linked,
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
        # file.write(str(is_linked) + "\n")
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

def upload_step_report(run_id: str, tc_id: str, step_seq: int, step_id: int, execution_detail: dict):
    try:
        if CommonUtil.debug_status:
            return
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        res = RequestFormatter.request(
            "post",
            RequestFormatter.form_uri("create_step_report/"),
            data={
                "execution_report": json.dumps({
                    "run_id": run_id,
                    "tc_id": tc_id,
                    "step_sequence": step_seq,
                    "step_id": step_id,
                    "execution_detail": execution_detail,
                })
            },
            verify=False
        )
        duration = round(res.elapsed.total_seconds(), 2)
        # if res.status_code == 200:
        #     CommonUtil.ExecLog(sModuleInfo, f"Successfully uploaded the step report [{duration} sec]", 1)
        if res.status_code == 500:
            CommonUtil.ExecLog(sModuleInfo, f"Failed to upload step report  [{duration} sec]\n{res.json()}", 3)
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def upload_reports_and_zips(temp_ini_file, run_id):
    try:
        if CommonUtil.debug_status:
            return
        Userid = (CommonUtil.MachineInfo().getLocalUser()).lower()
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        zip_dir = Path(ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file))/run_id.replace(":", "-")/CommonUtil.current_session_name

        if ConfigModule.get_config_value("RunDefinition", "local_run") == "False" and CommonUtil.run_cancel != CANCELLED_TAG:
            # FL.ZipFolder(str(zip_path), str(zip_path) + ".zip")

            tc_report = copy.deepcopy(CommonUtil.all_logs_json)
            tc_report[CommonUtil.runid_index]["machine_name"] = Userid

            for testcase in tc_report[CommonUtil.runid_index]["test_cases"]:
                for step in testcase["steps"]:
                    # if "actions" in step:
                    #     del step["actions"]
                    if "log" in step:
                        del step["log"]
            perf_report_html = None
            processed_tc_id = None
            if CommonUtil.processed_performance_data:
                env = Environment(loader=FileSystemLoader('../reporting/html_templates'))
                template = env.get_template('pref_report.html')
                html = template.render(CommonUtil.processed_performance_data)
                # Save the rendered HTML to a file
                processed_tc_id = CommonUtil.processed_performance_data["tc_id"].replace(":", "-")
                file_name = CommonUtil.processed_performance_data["tc_id"].replace(":", "-") + ".html"
                with open(zip_dir / file_name, "w", encoding="utf-8") as file:
                    file.write(html)
                    CommonUtil.ExecLog(sModuleInfo, "Performance report template generated successfully!", 1)
                CommonUtil.processed_performance_data.clear()
                perf_report_html = open(zip_dir / file_name, 'rb')

            for _ in range(5):
                try:
                    if perf_report_html is None:
                        res = RequestFormatter.request(
                            "post",
                            RequestFormatter.form_uri("create_report_log_api/"),
                            data={"execution_report": json.dumps(tc_report)},
                            verify=False
                        )
                    else:
                        res = RequestFormatter.request("post",
                        RequestFormatter.form_uri("create_report_log_api/"),
                        data={
                            "execution_report": json.dumps(tc_report),
                            "processed_tc_id":processed_tc_id
                        },
                        files=[("file",perf_report_html)],
                        verify=False)

                    if res.status_code == 200:
                        CommonUtil.ExecLog(sModuleInfo, f"Successfully uploaded the execution report of run_id {run_id}", 1)
                        break
                    else:
                        CommonUtil.ExecLog(sModuleInfo, f"Failed to upload the execution report of run_id {run_id}\nStatus: {res.json()}\nRetrying...", 3)
                    time.sleep(4)
                except:
                    CommonUtil.Exception_Handler(sys.exc_info())
                    time.sleep(4)
            else:
                try:
                    ## Create a folder in failed_upload directory with run_id
                    failed_upload_dir = Path(temp_ini_file).parent / 'failed_uploads'
                    os.makedirs(failed_upload_dir, exist_ok=True)

                    failed_run_id_dir = failed_upload_dir / run_id
                    os.makedirs(failed_run_id_dir, exist_ok=True)

                    ## Create a files subfolder files in the run_id folder
                    if perf_report_html:
                        failed_files_dir = failed_run_id_dir / "files"
                        os.makedirs(failed_files_dir, exist_ok=True)

                        ## Move the perf_report_html.name to that
                        failed_upload_filename = os.path.basename(perf_report_html.name)
                        shutil.copy(perf_report_html.name, os.path.join(failed_files_dir,failed_upload_filename))
                    else:
                        failed_upload_filename = None

                    failed_report_json = {
                        "run_id": run_id,
                        "method": "POST",
                        "URL": "create_report_log_api",
                        "execution_report": json.dumps(tc_report),
                        "processed_tc_id": processed_tc_id,
                        "perf_filepath" : failed_upload_filename
                    }

                    failed_report_json_path = failed_run_id_dir / "report.json"
                    with open(failed_report_json_path, 'w') as file:
                        file.write(json.dumps(failed_report_json))
                except:
                    CommonUtil.ExecLog(sModuleInfo, "Could not save the report to retry later of run_id '%s'" % run_id, 3)
                CommonUtil.ExecLog(sModuleInfo, "Could not Upload the report to server of run_id '%s'" % run_id, 3)

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
            CommonUtil.ExecLog(sModuleInfo, "Uploading %s logs-screenshots of %s testcases of %s from:\n%s" % (CommonUtil.current_session_name, len(zip_files), size, str(zip_dir)), 5)

            for _ in range(5):
                try:
                    files_list = []
                    for zips in opened_zips:
                        files_list.append(("file",zips))
                    res = RequestFormatter.request("post", 
                        RequestFormatter.form_uri("save_log_and_attachment_api/"),
                        files=files_list,
                        data={"machine_name": Userid},
                        verify=False)
                    if res.status_code == 200:
                        try:
                            res_json = res.json()
                        except:
                            continue
                        if isinstance(res_json, dict) and 'message' in res_json and res_json["message"]:
                            CommonUtil.ExecLog(sModuleInfo, "Successfully Uploaded logs-screenshots to server of run_id '%s'" % run_id, 1)
                        else:
                            CommonUtil.ExecLog(sModuleInfo, f"Could not Upload logs-screenshots to server of run_id '{run_id}'\n\nResponse Text = {res.text}", 3)
                        break
                except:
                    pass

                time.sleep(4)
            else:
                CommonUtil.ExecLog(sModuleInfo, "Could not Upload logs-screenshots to server of run_id '%s'" % run_id, 3)

        with open(zip_dir / "execution_log_old_format.json", "w", encoding="utf-8") as f:
            json.dump(CommonUtil.get_all_logs(json=True), f, indent=2)

        if CommonUtil.run_cancel != CANCELLED_TAG:
            # Create a standard report format to be consumed by other tools.
            junit_report_path = zip_dir / "junitreport.xml"
            junit_report.process(CommonUtil.all_logs_json, str(junit_report_path))
        return zip_dir
    except:
        CommonUtil.Exception_Handler(sys.exc_info())

def retry_failed_report_upload():
    while True:
        try:
            sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
            failed_report_dir = PROJECT_ROOT / 'AutomationLog' / 'failed_uploads'
            os.makedirs(failed_report_dir, exist_ok=True)
            folders = [entry.name for entry in failed_report_dir.iterdir() if entry.is_dir()]

            if folders == []:
                return
            else:
                for folder in folders:
                    report_json_path = failed_report_dir / folder / 'report.json'
                    report_json = json.load(open(report_json_path))
                    if not report_json.get('perf_filepath'):
                        res = RequestFormatter.request("post", 
                            RequestFormatter.form_uri("create_report_log_api/"),
                            data={"execution_report": report_json.get('execution_report')},
                            verify=False)
                    else:
                        res = RequestFormatter.request("post", 
                                    RequestFormatter.form_uri("create_report_log_api/"),
                                    data={"execution_report": report_json.get('execution_report'),
                                        "processed_tc_id":report_json.get('processed_tc_id')

                                        },
                                    files=[("file",open(failed_report_dir / folder / 'files' /report_json.get('perf_filepath'),'rb'))],
                                    verify=False)
                        
                        if res.status_code == 200:
                            CommonUtil.ExecLog(sModuleInfo, f"Successfully uploaded the execution report of run_id {report_json.get('run_id')}", 1)
                            shutil.rmtree(failed_report_dir / folder)
                        else:
                            CommonUtil.ExecLog(sModuleInfo, f"Unabel to upload the execution report of run_id {report_json.get('run_id')}", 1)
        except Exception as e:
            CommonUtil.ExecLog(sModuleInfo, str(e), 3)
            pass
        
        sleep(120)




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
    all_sessions = []
    start = 0
    for i in range(session_num):
        temp = copy.deepcopy(run_id_info)
        temp["test_cases"] = testcases[start:start+len_list[i]]
        all_sessions.append(temp)
        start += len_list[i]
    return all_sessions


def download_attachment(attachment_info: Dict[str, Any]):
    """
    Downloads a given attachment into the 'attachments' folder.

    Benchmark for downloading large files: bigfile.zip (575.2 MB)

    chunk size               | time (seconds)
    ----------------------------------------------
    1 byte                   | 56.872249603271484
    1 KB   (1024)            | 7.789804697036743
    512 KB (512*1024)        | 0.2882239818572998
    1 MB   (1024*1024)       | 0.51566481590271
    8 MB   (8*1024*1024)     | 0.46999025344848633
    1 GB   (1024*1024*1024)  | 0.6988034248352051
    shutil.copyfileobj       | 0.6343142986297607

    We can see that 512KB is the ideal chunk size for large file downloads.
    """

    # assumes that the last segment after the / represents the file name
    # if url is abc/xyz/file.txt, the file name will be file.txt
    url = attachment_info["url"]
    file_name_start_pos = url.rfind("/") + 1
    file_name = url[file_name_start_pos:]
    file_path = attachment_info["download_dir"] / file_name

    r = RequestFormatter.request("get", url, stream=True)
    if r.status_code == requests.codes.ok:
        with open(file_path, 'wb') as f:
            for data in r.iter_content(chunk_size=512*1024):
                f.write(data)

    # Return the hash of the file and the path where its stored.
    return {
        "hash": attachment_info["attachment"]["hash"],
        "path": file_path,
    }


def download_attachments(testcase_info):
    """Download test case and step attachments for the given test case."""
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
    attachment_path = Path(ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file)) / "attachments"
    attachment_db_path = Path(ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file)) / "attachments_db"

    url_prefix = ConfigModule.get_config_value("Authentication", "server_address") + "/static"
    urls = []

    db = AttachmentDB(attachment_db_path)

    def download_or_copy(attachment):
        """
        Puts the given attachment to the "to be downloaded" list or if its found
        in the attachment db, it'll copy it from the db to the "attachments"
        folder.
        """

        download_dir = attachment_path
        if "tc_folder" in attachment["path"]:
            download_dir = attachment_path / attachment["id"]
        elif "step_folder" in attachment["path"]:
            download_dir = attachment_path / f"STEP-{attachment['id']}"
        elif "global_folder" in attachment["path"]:
            download_dir = attachment_path / "global"

        if not download_dir.exists():
            CommonUtil.ExecLog(sModuleInfo, f"Creating folder: {download_dir}", 5)

        download_dir.mkdir(parents=True, exist_ok=True)

        entry = db.exists(attachment["hash"])
        to_append = {
            "url": url_prefix + attachment["path"],
            "download_dir": download_dir,
            "attachment": attachment,
        }
        if entry is None:
            urls.append(to_append)
        else:
            try:
                shutil.copyfile(str(entry["path"]), download_dir / Path(attachment["path"]).name)
            except:
                # If copy fails, the file either does not exist or we don't have
                # permission. Download the file again and remove from db.
                urls.append(to_append)
                db.remove(entry["hash"])

    # Test case attachments
    for attachment in testcase_info["attachments"]:
        download_or_copy(attachment)

    # Step attachments
    for step in testcase_info["steps"]:
        for attachment in step["attachments"]:
            download_or_copy(attachment)

    results = ThreadPool(4).imap_unordered(download_attachment, urls)
    for r in results:
        CommonUtil.ExecLog(sModuleInfo, f"Downloaded: {r}", 5)

        # Copy into the attachments db.
        attachment_path_in_db = attachment_db_path / r["path"].name

        put = db.put(attachment_path_in_db, r["hash"])
        if put:
            # If entry is successful, we copy the downloaded attachment to the
            # db directory.
            try:
                shutil.copyfile(r["path"], put["path"])
            except:
                # If copying the attachment fails, we remove the entry.
                db.remove(r["hash"])


# main function
def main(device_dict, all_run_id_info):
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

        if len(all_run_id_info) == 0:
            CommonUtil.ExecLog("", "No Test Run Schedule found for the current user : %s" % Userid, 2)
            return False

        CommonUtil.runid_index = 0
        for run_id_info in all_run_id_info:
            run_id_info["base_path"] = ConfigModule.get_config_value("Advanced Options", "_file_upload_path")
            run_id = run_id_info["run_id"]
            server_version = run_id_info["server_version"]

            CommonUtil.ExecLog(
                "",
                f"Server version = {server_version}",
                4,
                False,
            )
            debug_info = ""
            CommonUtil.clear_all_logs()

            CommonUtil.run_cancelled = False
            # Todo: This thread is required to cancel in step level when run-cancel is pressed. Remove comment when needed
            # thr = executor.submit(check_run_cancel, run_id)
            # CommonUtil.SaveThread("run_cancel", thr)

            # Write testcase json
            path = ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file) / Path(run_id.replace(":", "-"))
            CommonUtil.ExecLog(sModuleInfo, f"Creating folder: {path}", 5)
            FL.CreateFolder(path)

            if run_id.lower().startswith("debug"):
                CommonUtil.debug_status = True
            else:
                CommonUtil.debug_status = False
                shared.Clean_Up_Shared_Variables(run_id)

            # Todo: set the device_order for all the device from run_id_info["device_info"] or "temp/device_info.json" file
            # string_device_order = run_id_info["device_info"]
            device_order = run_id_info["device_info"]
            # or
            # with open(PROJECT_ROOT / "temp/device_info_in_node_v2.json", "r") as device_info_file:
            #     device_order = json.load(device_info_file)

            if isinstance(device_order, dict):
                if device_order["deploy_target"] == "browser_stack":
                    platform_name, platform_version, device_name, device_type = device_order["values"].split(':')
                    app_name, app_url = device_order["app_info"].split('+')
                    formated_device_order = {
                        "mobile": {
                            "browser_stack": {
                                "username": device_order['username'],
                                "access_key": device_order['access_key'],
                                "platformName": platform_name,
                                "appName": app_name,
                                "app": app_url,
                                "environments": [
                                    {
                                        "platformVersion": platform_version,
                                        "deviceName": device_name,
                                        "deviceType": device_type
                                    }
                                ]
                            }
                        }
                    }
                    device_order = formated_device_order

            runtime_settings = run_id_info["runtime_settings"]
            if not CommonUtil.debug_status:
                rem_config = {
                    "threading": runtime_settings["threading"],
                    "local_run": runtime_settings["local_run"],
                    "take_screenshot": runtime_settings["take_screenshot"],
                    "upload_log_file_only_for_fail": runtime_settings["upload_log_file_only_for_fail"],
                    # "rerun_on_fail": runtime_settings["rerun_on_fail"] if "rerun_on_fail" in runtime_settings else False,
                    "rerun_on_fail": False,     # Turning off rerun until its completed
                    "window_size_x": runtime_settings["window_size_x"] if runtime_settings["window_size_x"] != 0 else "",
                    "window_size_y": runtime_settings["window_size_y"] if runtime_settings["window_size_y"] != 0 else "",
                }
                # if ConfigModule.get_config_value("RunDefinition", "local_run") == "True":
                #     rem_config["local_run"] = True
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
                    shared.Clean_Up_Shared_Variables(run_id)
            driver_list = ["Not needed currently"]

            final_dependency = run_id_info["dependency_list"]
            shared.Set_Shared_Variables("dependency", final_dependency, protected=True)

            final_run_params_from_server = run_id_info["run_time"]
            final_run_params = {}
            for param in final_run_params_from_server:
                final_run_params[param] = CommonUtil.parse_value_into_object(list(final_run_params_from_server[param].items())[1][1])

            if final_run_params != {}:
                shared.Set_Shared_Variables("run_time_params", final_run_params, protected=True)
                for run_time_params_name in final_run_params:
                    shared.Set_Shared_Variables(run_time_params_name, final_run_params[run_time_params_name])

            if not shared.Test_Shared_Variables("zeuz_auto_teardown"):
                shared.Set_Shared_Variables("zeuz_auto_teardown", "on")

            if not CommonUtil.debug_status and str(shared.Get_Shared_Variables("zeuz_auto_teardown")).strip().lower() not in ("off", "no", "false", "disable"):
                cleanup_driver_instances()

            if not shared.Test_Shared_Variables("zeuz_collect_browser_log"):
                shared.Set_Shared_Variables("zeuz_collect_browser_log", "on")

            shared.Set_Shared_Variables("run_id", run_id)
            shared.Set_Shared_Variables("node_id", CommonUtil.MachineInfo().getLocalUser())

            send_log_file_only_for_fail = ConfigModule.get_config_value("RunDefinition", "upload_log_file_only_for_fail")
            send_log_file_only_for_fail = False if send_log_file_only_for_fail.lower() == "false" else True
            rerun_on_fail = ConfigModule.get_config_value("RunDefinition", "rerun_on_fail")
            rerun_on_fail = False if rerun_on_fail.lower() == "false" else True
            CommonUtil.upload_on_fail, CommonUtil.rerun_on_fail = send_log_file_only_for_fail, rerun_on_fail
            global_attachment = GlobalAttachment()
            shared.Set_Shared_Variables("global_attachments", global_attachment)

            all_testcases_info = run_id_info["test_cases"]
            TestSetStartTime = time.time()
            i = 0
            while i < len(all_testcases_info):
                if all_testcases_info[i]["automatability"] != "Automated" and all_testcases_info[i]["automatability"] != "Performance":
                    CommonUtil.ExecLog("", all_testcases_info[i]["testcase_no"] + " is not automated so skipping", 2)
                    del all_testcases_info[i]
                    i -= 1
                i += 1
            if len(all_testcases_info) > 0:
                # CommonUtil.ExecLog("", "Total number of Automated test cases
                # %s" % len(all_testcases_info), 4, False)
                pass
            else:
                CommonUtil.ExecLog("", "No Automated test cases found in this deployment: %s" % Userid, 2)
                CommonUtil.runid_index += 1
                return "pass"
            num_of_tc = len(all_testcases_info)
            cnt = 1

            # TODO: This is not needed anymore since the server controls exactly
            # how many test cases are sent in each session and node simply needs
            # to execute the test cases and upload the reports.
            max_tc_in_single_session = 50    # Todo: make it 25
            all_sessions = split_testcases(run_id_info, max_tc_in_single_session)
            session_cnt = 1

            for each_session in all_sessions:
                CommonUtil.current_session_name = "session_" + str(session_cnt)
                CommonUtil.all_logs_json = [each_session]
                CommonUtil.tc_index = 0
                all_testcases_info = each_session["test_cases"]
                if run_id not in CommonUtil.tc_nums:
                    CommonUtil.tc_nums[run_id] = []
                for i in [int(i['testcase_no'].split('-')[-1]) for i in all_testcases_info]:
                    i not in CommonUtil.tc_nums[run_id] and CommonUtil.tc_nums[run_id].append(i)

                for testcase_info in all_testcases_info:
                    performance_test_case = False
                    if testcase_info["automatability"].lower() == "performance":
                        performance_test_case = True
                    test_case_no = testcase_info["testcase_no"]
                    test_case_name = testcase_info["title"]
                    user_info_object = {
                        "project_id": run_id_info["project_id"],
                        "team_id": str(run_id_info["team_id"]),
                    }
                    set_device_info_according_to_user_order(device_order, device_dict, test_case_no, test_case_name, user_info_object, Userid, run_id=run_id)
                    CommonUtil.disabled_step = []
                    CommonUtil.testcase_exit = ""

                    # Download test case and step attachments
                    download_attachments(testcase_info)

                    if performance_test_case:
                        # get performance test info
                        try:
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
                                # is_linked,
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
                        except Exception as e:
                            CommonUtil.ExecLog(sModuleInfo, e, 3)
                            run_test_case(
                                test_case_no,
                                sModuleInfo,
                                run_id,
                                temp_ini_file,
                                testcase_info,
                                debug_info,
                                rerun_on_fail,
                                server_version,
                                send_log_file_only_for_fail,
                            )
                            CommonUtil.clear_all_logs()  # clear logs
                            if CommonUtil.run_cancel == CANCELLED_TAG:
                                break
                            cnt += 1


                    else:
                        run_test_case(
                            test_case_no,
                            sModuleInfo,
                            run_id,
                            temp_ini_file,
                            testcase_info,
                            debug_info,
                            rerun_on_fail,
                            server_version,
                            send_log_file_only_for_fail,
                        )
                        CommonUtil.clear_all_logs()  # clear logs
                        if CommonUtil.run_cancel == CANCELLED_TAG:
                            break

                        cnt += 1
                    CommonUtil.tc_index += 1

                # calculate elapsed time of runid
                sTestSetEndTime = datetime.fromtimestamp(time.time(), tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
                TestSetEndTime = time.time()
                TimeDiff = TestSetEndTime - TestSetStartTime
                TimeInSec = int(TimeDiff)
                TestSetDuration = CommonUtil.FormatSeconds(TimeInSec)

                after_execution_dict = {
                    "status": "Complete",
                    "teststarttime": datetime.fromtimestamp(TestSetStartTime, tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S"),
                    "testendtime": sTestSetEndTime,
                    "duration": TestSetDuration
                }
                CommonUtil.CreateJsonReport(setInfo=after_execution_dict)

                CommonUtil.generate_time_based_performance_report(each_session)

                # Complete all step_reports and then send tc report
                if "step_report" in CommonUtil.all_threads:
                    for t in CommonUtil.all_threads["step_report"]:
                        t.result()
                    del CommonUtil.all_threads["step_report"]
                upload_reports_and_zips(temp_ini_file, run_id)

                session_cnt += 1
                CommonUtil.ExecLog(sModuleInfo, "Execution time = %s sec" % round(TimeDiff, 3), 5)

            ConfigModule.add_config_value("sectionOne", "sTestStepExecLogId", "MainDriver", temp_ini_file)

            if CommonUtil.run_cancel == CANCELLED_TAG:
                CommonUtil.ExecLog(sModuleInfo,"Test Set Cancelled by the User", 5)
            elif not CommonUtil.debug_status:

                from shutil import copytree

                # If node is running in device farm, copy the logs and reports to the expected directory.
                if "DEVICEFARM_LOG_DIR" in os.environ:
                    log_dir = Path(os.environ["DEVICEFARM_LOG_DIR"])
                    zeuz_log_dir = Path(ConfigModule.get_config_value(
                        "sectionOne", "test_case_folder", temp_ini_file
                    )).parent

                    copytree(str(zeuz_log_dir), str(log_dir))

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
                pass
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
            if ConfigModule.get_config_value("RunDefinition", "local_run") == "True":
                input("[Local run] Press any key to finish")

            break   # Todo: remove this after server side multiple run-id problem is fixed

        return "pass"
    except:
        CommonUtil.debug_code_error(sys.exc_info())
        return None




if __name__ == "__main__":
    main()
