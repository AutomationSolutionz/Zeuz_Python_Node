# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

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

top_path = os.path.dirname(os.getcwd())
drivers_path = os.path.join(top_path, "Drivers")
sys.path.append(drivers_path)

MODULE_NAME = inspect.getmodulename(__file__)

"""Constants"""
PROGRESS_TAG = "In-Progress"
PASSED_TAG = "Passed"
SKIPPED_TAG = "Skipped"
WARNING_TAG = "Warning"
FAILED_TAG = "Failed"
NOT_RUN_TAG = "Not Run"
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
    "Failed",
    "failed",
    "FAILED",
    "false",
    "False",
    "FALSE",
    "0",
]
skipped_tag_list = ["skip", "SKIP", "Skip", "skipped", "SKIPPED", "Skipped"]
device_info = {}
# if other linked machine failed in a linked run
failed_due_to_linked_fail = False


# writes all logs to server
def write_all_logs_to_server(all_logs_list):
    i = 0
    for all_logs in all_logs_list:
        while i < 5:
            try:
                r = RequestFormatter.Post("all_log_execution", {"all_logs": all_logs})
                if r == 1:
                    break
                i += 1
                time.sleep(1)
            except:
                i += 1
                time.sleep(1)
    return r


# send_email_report_after_exectution
def send_email_report_after_exectution(run_id, project_id, team_id):
    return RequestFormatter.Get(
        "send_email_report_after_excecution_api",
        {"run_id": run_id, "project_id": project_id, "team_id": team_id},
    )


# returns all drivers
def get_all_drivers_list():
    return RequestFormatter.Get("get_all_drivers_api")


# returns all latest versions
def get_latest_zeuz_versions():
    return RequestFormatter.Get("get_latest_zeuz_versions_api")


# returns all runids assigned to a machine, NEEDS IMPROVEMENT
def get_all_run_ids(Userid, sModuleInfo):

    all_run = []
    try:
        wait_time = 5
        end_time = datetime.now() + timedelta(seconds=wait_time)
        while datetime.now() <= end_time:
            all_run = RequestFormatter.Get("get_all_submitted_run_of_a_machine_api", {"machine_name": Userid})

            if len(all_run) == 0:
                CommonUtil.ExecLog(sModuleInfo, "Error while fetching test run", 2)
                CommonUtil.ExecLog(sModuleInfo, "Trying again to fetch test run", 1)
                time.sleep(1)
            else:
                return all_run

        CommonUtil.ExecLog(
            sModuleInfo,
            "Couldn't get the test run deployed on this machine, please try again",
            3,
        )
        return all_run

    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        CommonUtil.ExecLog(
            sModuleInfo,
            "Couldn't get the test run deployed on this machine, please try again",
            3,
        )
        return all_run


# returns device serial set from server
def get_device_order(Userid):
    # return RequestFormatter.Get(
    #     "get_machine_device_order_api", {"machine_name": Userid}  # old one
    #     # "get_machine_device_info_api", {"machine_name": Userid}     # new one
    # )

    res = RequestFormatter.Get(
        "get_machine_device_order_api", {"machine_name": Userid}  # old one
        # "get_machine_device_info_api", {"machine_name": Userid}     # new one
    )
    return res

# returns device serial also browserstack info set from server
def get_device_order_and_browserstack_info(Userid):
    # return RequestFormatter.Get(
    #     # "get_machine_device_order_api", {"machine_name": Userid}  # old one
    #     "get_machine_device_info_api", {"machine_name": Userid}     # new one
    # )

    res = RequestFormatter.Get(
        # "get_machine_device_order_api", {"machine_name": Userid}  # old one
        "get_machine_device_info_api", {"machine_name": Userid}     # new one
    )
    return res

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


# get all server variable
def get_all_remote_config(run_id):
    return RequestFormatter.Get("get_all_remote_config_api", {"run_id": run_id})


# get all server variable
def delete_all_server_variable(run_id):
    return RequestFormatter.Get(
        "delete_all_runid_server_variable_api", {"run_id": run_id}
    )


# returns all dependencies of test cases of a run id
def get_all_dependencies(project_id, team_id, run_description):
    dependency_list = RequestFormatter.Get(
        "get_all_dependency_based_on_project_and_team_api",
        {"project_id": project_id, "team_id": team_id},
    )
    final_dependency = get_final_dependency_list(dependency_list, run_description)
    return final_dependency


# returns all runtime parameters of test cases of a run id
def get_all_runtime_parameters(run_id):
    run_params_list = RequestFormatter.Get(
        "get_all_run_parameters_based_on_project_and_team_api", {"run_id": run_id}
    )
    final_run_params = get_run_params_list(run_params_list)
    return final_run_params


def update_machine_info_on_server(run_id):
    RequestFormatter.Get(
        "update_machine_info_based_on_run_id_api",
        {"run_id": run_id, "options": {"status": PROGRESS_TAG}},
    )
# updates current runid status on server database


def update_test_env_results_on_server(run_id):
    sTestSetStartTime = datetime.fromtimestamp(time.time()).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    RequestFormatter.Get(
        "update_test_env_results_based_on_run_id_api",
        {
            "options": {
                "status": PROGRESS_TAG,
                "teststarttime": str(sTestSetStartTime),
            },
            "run_id": run_id,
        },
    )


# returns all automated test cases of a runid
def get_all_automated_test_cases_in_run_id(run_id, tester_id):
    return RequestFormatter.Get(
        "get_all_automated_test_cases_based_on_run_id_api",
        {"run_id": run_id, "tester_id": tester_id},
    )


# checks if a step of a test case is the verification point of that test case
def check_if_step_is_verification_point(run_id, tc_id, step_sequence):
    return RequestFormatter.Get(
        "if_failed_at_verification_point_api",
        {"run_id": run_id, "tc_id": tc_id, "step_sequence": step_sequence},
    )


# if run is cancelled then it can be called, it cleans up the runid from database
def cleanup_runid_from_server(run_id):
    RequestFormatter.Get("clean_up_run_api", {"run_id": run_id})


# checks if this test case is a copy of another test case
def check_if_test_case_is_copied(run_id, test_case):
    return RequestFormatter.Get(
        "is_test_case_copied_api", {"run_id": run_id, "test_case": test_case}
    )


def get_debug_steps(run_id):
    return RequestFormatter.Get("get_debug_steps_api", {"run_id": run_id})


def send_debug_data(run_id, key, value):
    return RequestFormatter.Get(
        "send_debug_data_api", {"run_id": run_id, "key": key, "value": value}
    )

# returns test case details needed to run the test case
def get_test_case_details(run_id, test_case):
    return RequestFormatter.Get(
        "get_test_case_detail_api", {"run_id": run_id, "test_case": test_case}
    )


# updates current test case status on server database
def update_test_case_progress_on_server(run_id, test_case, sTestCaseStartTime):
    return RequestFormatter.Get(
        "test_case_results_update_returns_index_api",
        {
            "run_id": run_id,
            "test_case": test_case,
            "options": {"status": PROGRESS_TAG, "teststarttime": sTestCaseStartTime},
        },
    )


# returns all steps of a test case
def get_all_steps_of_a_test_case(run_id, test_case):
    return RequestFormatter.Get(
        "test_step_fetch_for_test_case_run_id_api",
        {"run_id": run_id, "test_case": test_case},
    )


# returns step_id of a test step
def get_step_id_of_a_test_step(stepname):
    return RequestFormatter.Get(
        "test_step_id_fetch_from_step_name_api", {"stepname": stepname}
    )


# returns screen cature settings of a test step
def get_screen_capture_settings_of_a_test_step(step_id):
    return RequestFormatter.Get(
        "screen_capture_fetch_for_test_step_api", {"step_id": step_id}
    )


# returns test step details needed to run the test step
def get_step_meta_data_of_a_step(run_id, test_case, StepSeq):
    return RequestFormatter.Get(
        "get_step_meta_data_api",
        {"run_id": run_id, "test_case": test_case, "step_seq": StepSeq},
    )


# if a test case is failed it returns the fail reason
def get_fail_reason_of_a_test_case(run_id, test_case):
    return RequestFormatter.Get(
        "get_failed_reason_test_case_api", {"run_id": run_id, "test_case": test_case}
    )


# updates current test case status on server database after the test case is run
def update_test_case_status_after_run_on_server(
    run_id, test_case, test_case_after_dict
):
    RequestFormatter.Get(
        "test_case_results_update_returns_index_api",
        {"run_id": run_id, "test_case": test_case, "options": test_case_after_dict},
    )


# returns current status of the runid
def get_status_of_runid(run_id):
    return RequestFormatter.Get("get_status_of_a_run_api", {"run_id": run_id})


# updates current test step status on server database
def update_test_step_status(
    run_id, test_case, current_step_id, current_step_sequence, Dict
):
    RequestFormatter.Get(
        "test_step_results_update_returns_index_api",
        {
            "run_id": run_id,
            "tc_id": test_case,
            "step_id": current_step_id,
            "test_step_sequence": current_step_sequence,
            "options": Dict,
        },
    )


# updates current test case result(like pass/fail etc.) on server database
def update_test_case_result_on_server(run_id, sTestSetEndTime, TestSetDuration):
    RequestFormatter.Get(
        "update_test_env_results_based_on_run_id_api",
        {
            "options": {
                "status": COMPLETE_TAG,
                "testendtime": sTestSetEndTime,
                "duration": TestSetDuration,
            },
            "run_id": run_id,
        },
    )
    RequestFormatter.Get(
        "update_machine_info_based_on_run_id_api",
        {"run_id": run_id, "options": {"status": COMPLETE_TAG, "email_flag": True}},
    )

dbadfxb = 1
# returns step data of a test step in a test case
def get_test_step_data(run_id, test_case, current_step_sequence, sModuleInfo):
    try:
        wait_time = 5
        end_time = datetime.now() + timedelta(seconds=wait_time)
        global dbadfxb
        while datetime.now() <= end_time:
            response = RequestFormatter.Get(
                "get_test_step_data_based_on_test_case_run_id_api",
                {
                    "run_id": run_id,
                    "test_case": test_case,
                    "step_sequence": current_step_sequence,
                },
            )
            dbadfxb += 1
            if "status" not in response or response["status"] in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Error while fetching step data: " + response["message"],
                    2,
                )
                CommonUtil.ExecLog(sModuleInfo, "Trying again to fetch step data", 1)

            else:
                return response["step_data"]

            time.sleep(1)

        CommonUtil.ExecLog(sModuleInfo, "Couldn't get step data, returning failed", 3)
        return "failed"
    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        CommonUtil.ExecLog(sModuleInfo, "Couldn't get step data, returning failed", 3)
        return "failed"


# updates current test step result(like pass/fail etc.) on server database
def update_test_step_results_on_server(
    run_id, test_case, current_step_id, current_step_sequence, after_execution_dict
):
    RequestFormatter.Get(
        "test_step_results_update_returns_index_api",
        {
            "run_id": run_id,
            "tc_id": test_case,
            "step_id": current_step_id,
            "test_step_sequence": current_step_sequence,
            "options": after_execution_dict,
        },
    )


# checks if the user has permission to run test or not
def check_user_permission_to_run_test(sModuleInfo, Userid):
    r = RequestFormatter.Get("get_valid_machine_name_api", {"machine_name": Userid})
    if not r:
        CommonUtil.ExecLog(
            sModuleInfo, "User don't have permission to run the tests", 3
        )
        return "You Don't Have Permission"
    else:
        return "passed"


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
                return "failed"
            else:
                time.sleep(1)
        except:
            pass

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# gets run time parameters
def get_run_params_list(run_params):
    run_para = []
    for each in run_params:
        m_ = {}
        m_.update({"field": each[0]})
        m_.update({"name": each[1]})
        m_.update({"value": each[2]})
        run_para.append(m_)
    return run_para


# uploads zip file to server
def upload_zip(server_id, port_id, temp_folder, run_id, file_name, base_path=False):
    """
    :param server_id: the location of the server
    :param port_id: the port it will listen on
    :param temp_folder: the logfiles folder
    :param run_id: respective run_id
    :param file_name: zipfile name for the run
    :param base_path: base_path for file save
    :return:
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    url_link = server_id + ":" + str(port_id) + "/Home/UploadZip/"
    if not url_link.startswith("http") or not url_link.startswith("https"):
        url_link = "http://" + url_link

    total_file_path = (
        temp_folder + os.sep + run_id.replace(":", "-") + os.sep + file_name
    )

    i = 0
    while i < 5:
        try:
            fileObj = open(total_file_path, "rb")
            file_list = {"docfile": fileObj}
            data_list = {
                "run_id": run_id,
                "file_name": file_name,
                "base_path": base_path,
            }
            r = requests.post(url_link, files=file_list, data=data_list, verify=False)
            if r.status_code == 200:
                CommonUtil.ExecLog(
                    "",
                    "Uploaded logs and screenshots as zip file to server",
                    4,
                    False,
                )
                break
            else:
                # CommonUtil.ExecLog(
                #     sModuleInfo,
                #     "Failed to upload zip file to server... retrying %d." % i+1,
                #     4,
                #     False,
                # )
                time.sleep(2)
                i += 1
        except:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Failed to upload zip file to server... retrying %s." % str(i+1),
                4,
                False,
            )
            time.sleep(2)
            i += 1


# returns dependency list
def get_final_dependency_list(dependency_list, run_description):
    dependency_list_final = {}
    run_description = run_description.split("|")
    for each in run_description:
        if ":" not in each:
            continue
        for eachitem in dependency_list:
            current_dependency = eachitem[0]
            for eachitemlist in eachitem[1]:
                if each.split(":")[1].strip() == eachitemlist:
                    current_item = each.split(":")[1].strip()
                    dependency_list_final.update({current_dependency: current_item})
    return dependency_list_final


def download_single_attachment(sModuleInfo, download_url, f, retry):
    try:
        if retry == 4:
            CommonUtil.ExecLog(sModuleInfo, "An attachment couldn't be downloaded. Downloading the remaining ones", 3)
            return False
        with requests.get(download_url, stream=True, verify=False) as r:
            shutil.copyfileobj(r.raw, f)
        time.sleep(0.5)
        return True
    except:
        time.sleep(0.5)
        return download_single_attachment(download_url, f, retry+1)


# downloads attachments for a test step
def download_attachments_for_test_case(sModuleInfo, run_id, test_case, temp_ini_file, test_case_attachments, test_step_attachments):
    try:
        log_file_path = ConfigModule.get_config_value(
            "sectionOne", "temp_run_file_path", temp_ini_file
        )
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
    test_step_attachments = []
    test_case_folder = (
        log_file_path
        + os.sep
        + (run_id.replace(":", "-") + os.sep + test_case.replace(":", "-"))
    )
    ConfigModule.add_config_value("sectionOne", "test_case", test_case, temp_ini_file)
    ConfigModule.add_config_value("sectionOne", "test_case_folder", test_case_folder, temp_ini_file)
    log_folder = test_case_folder + os.sep + "Log"
    ConfigModule.add_config_value("sectionOne", "log_folder", log_folder, temp_ini_file)
    screenshot_folder = test_case_folder + os.sep + "screenshots"
    ConfigModule.add_config_value("sectionOne", "screen_capture_folder", screenshot_folder, temp_ini_file)

    # Store the attachments for each test case separately inside
    # AutomationLog/attachments/TEST-XYZ
    home = str(Path(log_file_path) / "attachments" / test_case.replace(":", "-"))
    ConfigModule.add_config_value("sectionOne", "download_folder", home, temp_ini_file)

    # create_test_case_folder
    test_case_folder = ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_ini_file)
    FL.CreateFolder(test_case_folder)

    # FL.CreateFolder(Global.TCLogFolder + os.sep + "ProductLog")
    log_folder = ConfigModule.get_config_value("sectionOne", "log_folder", temp_ini_file)
    FL.CreateFolder(log_folder)

    # FL.CreateFolder(Global.TCLogFolder + os.sep + "Screenshots")
    # creating ScreenShot File
    screen_capture_folder = ConfigModule.get_config_value("sectionOne", "screen_capture_folder", temp_ini_file)
    FL.CreateFolder(screen_capture_folder)

    # creating the download folder
    download_folder = ConfigModule.get_config_value("sectionOne", "download_folder", temp_ini_file)

    FL.DeleteFolder(ConfigModule.get_config_value("sectionOne", "download_folder", temp_ini_file))
    FL.CreateFolder(download_folder)
    file_specific_steps = {}
    if ConfigModule.get_config_value("RunDefinition", "local_run") == "True":
        return {}
    for each in test_case_attachments:
        CommonUtil.ExecLog(sModuleInfo, "Attachment download for test case %s started" % test_case, 1)
        m = each[1] + "." + each[2]  # file name
        f = open(download_folder + "/" + m, "wb")

        download_url = (
            ConfigModule.get_config_value("Authentication", "server_address")
            + ":"
            + str(ConfigModule.get_config_value("Authentication", "server_port"))
        )

        if not download_url.startswith("http") or not download_url.startswith("https"):
            download_url = "https://" + download_url

        download_url += "/static" + each[0]

        # Use request streaming to efficiently download files
        download_single_attachment(sModuleInfo, download_url, f, 1)

        # f.write(urllib.request.urlopen(download_url).read())
        file_specific_steps.update({m: download_folder + "/" + m})
        f.close()
    if test_case_attachments:
        CommonUtil.ExecLog(
            sModuleInfo, "Attachment download for test case %s finished" % test_case, 1
        )
    for each in test_step_attachments:
        CommonUtil.ExecLog(
            sModuleInfo,
            "Attachment download for steps in test case %s started" % test_case,
            1,
        )
        m = each[1] + "." + each[2]  # file name
        if _platform == "win32":
            sep = "\\"
        else:
            sep = "/"
        if not os.path.exists(download_folder + sep + str(each[3])):
            FL.CreateFolder(download_folder + sep + str(each[3]))
        f = open(download_folder + sep + str(each[3]) + sep + m, "wb")
        f.write(
            urllib.request.urlopen(
                "http://"
                + ConfigModule.get_config_value("Authentication", "server_address")
                + ":"
                + str(ConfigModule.get_config_value("Authentication", "server_port"))
                + "/static"
                + each[0]
            ).read()
        )
        file_specific_steps.update({m: download_folder + sep + str(each[3]) + sep + m})
        f.close()
    if test_step_attachments:
        CommonUtil.ExecLog(
            sModuleInfo,
            "Attachment download for steps in test case %s finished" % test_case,
            1,
        )

    return file_specific_steps

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
        # current_driver = all_step_info[StepSeq-1]["step_driver_type"]
        current_driver = "Built_In_Driver"
        print("DRIVER: {}".format(current_driver))

        try:
            current_driver = "Drivers." + current_driver
            module_name = importlib.import_module(current_driver)  # get module
            print("STEP DATA and VARIABLES")
            # get step name
            if all_step_info[StepSeq-1]["step_function"]:
                step_name = all_step_info[StepSeq-1]["step_function"].strip()
            else:
                step_name = current_step_name

            # step_name = step_name.lower().replace(" ", "_")
            step_name = "sequential_actions"
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
                return "Failed"

            try:
                simple_queue = queue.Queue()
                screen_capture = "Desktop"      # No need of screen capture. Need to delete this

                # run in thread
                if (
                    ConfigModule.get_config_value("RunDefinition", "threading")
                    in passed_tag_list
                ):
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

                    CommonUtil.ExecLog(
                        sModuleInfo, "Starting Test Step Thread..", 1
                    )  # add log

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
                        CommonUtil.ExecLog(
                            sModuleInfo, "Test Step Thread Ended..", 1
                        )
                    except queue.Empty:
                        # Global.DefaultTestStepTimeout
                        ErrorMessage = (
                            "Test Step didn't return after %d seconds" % step_time
                        )
                        CommonUtil.Exception_Handler(
                            sys.exc_info(), None, ErrorMessage
                        )
                        sStepResult = "Failed"
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
                                    CommonUtil.ExecLog(
                                        sModuleInfo, "Thread is still alive", 2
                                    )
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
                sStepResult = "Failed"

            # get step result
            if sStepResult in passed_tag_list:
                sStepResult = "PASSED"
            elif sStepResult in failed_tag_list:
                sStepResult = "FAILED"
            elif sStepResult in skipped_tag_list:
                sStepResult = "SKIPPED"
            elif sStepResult.upper() == CANCELLED_TAG.upper():
                sStepResult = "CANCELLED"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo, "sStepResult not an acceptable type", 3
                )
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Acceptable pass string(s): %s" % passed_tag_list,
                    3,
                )
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Acceptable fail string(s): %s" % failed_tag_list,
                    3,
                )
                sStepResult = "FAILED"
            q.put(sStepResult)
        except Exception as e:
            print("### Exception : {}".format(e))
            CommonUtil.Exception_Handler(sys.exc_info())
            sStepResult = "Failed"

        return sStepResult
    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        return "Failed"


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
    executor,
    debug_info,
    is_linked="",
    performance=False
):

    StepSeq = 1
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
        if debug_info["debug_clean"] == "YES":
            cleanup_drivers_during_debug = True

    # clean up shared variables and teardown drivers
    if cleanup_drivers_during_debug:
        cleanup_driver_instances()
        shared.Clean_Up_Shared_Variables()
    if not debug_steps:
        debug_steps = []

    if not debug_actions:
        debug_actions = []

    # performance testing
    if performance:
        StepSeq = 2
        sTestStepResultList.append("PASSED")

    # all_step_meta_data = Response["step_meta_data"]
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
            dict["Action name"] = action_info["action_name"]
            all_action_Info.append(dict)
        all_step_dataset.append(all_action_data_set)
        all_action_info.append(all_action_Info)
    # loop through the steps
    while StepSeq <= Stepscount:

        # check if debug step
        if debug and debug_steps:
            if str(StepSeq) not in debug_steps:
                StepSeq += 1
                continue

        # check if already failed
        if already_failed:
            always_run = all_step_info[StepSeq - 1]["always_run"]  # get always run info
            if not always_run:  # check if always run is false
                StepSeq += 1
                continue

        # get step info
        current_step_name = all_step_info[StepSeq - 1]["step_name"]
        current_step_id = all_step_info[StepSeq - 1]["step_id"]
        current_step_sequence = all_step_info[StepSeq - 1]["step_sequence"]

        # add config value
        ConfigModule.add_config_value(
            "sectionOne",
            "sTestStepExecLogId",
            run_id + "|" + test_case + "|" + str(current_step_id) + "|" + str(current_step_sequence),
            temp_ini_file,
        )

        # add log
        log_line = "STEP #%d: %s" % (StepSeq, current_step_name)
        print("-"*len(log_line))
        CommonUtil.ExecLog(sModuleInfo, log_line, 4)
        print("-"*len(log_line))

        test_steps_data = all_step_dataset[StepSeq-1]
        test_action_info = all_action_info[StepSeq-1]
        try:
            test_case_continue = all_step_info[StepSeq - 1]["continue_on_fail"]
            step_time = all_step_info[StepSeq - 1]["step_time"]
            if str(step_time) != "" and step_time != None:
                step_time = int(step_time)
            else:
                step_time = 59
        except:
            test_case_continue = False
            step_time = 59

        # get step start time
        TestStepStartTime = time.time()
        sTestStepStartTime = datetime.fromtimestamp(TestStepStartTime).strftime("%Y-%m-%d %H:%M:%S")
        WinMemBegin = CommonUtil.PhysicalAvailableMemory()  # get available memory

        if ConfigModule.get_config_value("RunDefinition", "local_run") == "False":
            # make test step run dictionary
            Dict = {
                "teststepsequence": current_step_sequence,
                "status": PROGRESS_TAG,
                "stepstarttime": sTestStepStartTime,
                "logid": ConfigModule.get_config_value(
                    "sectionOne", "sTestStepExecLogId", temp_ini_file
                ),
                "start_memory": WinMemBegin,
                "testcaseresulttindex": "Dont NEED",
            }
            # executor.submit(update_test_step_status, run_id, test_case, current_step_id, current_step_sequence, Dict)

        # check if machine failed
        is_failed_result = ""
        if is_linked == "yes":
            is_failed_result = check_if_other_machines_failed_in_linked_run()

        # check step result
        if is_failed_result in failed_tag_list or test_steps_data in failed_tag_list:
            sStepResult = "Failed"
        else:
            # run driver for step and get result
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
        sTestStepEndTime = datetime.fromtimestamp(TestStepEndTime).strftime("%Y-%m-%d %H:%M:%S")
        WinMemEnd = CommonUtil.PhysicalAvailableMemory()  # get available memory
        TestStepDuration = CommonUtil.FormatSeconds(int(TestStepEndTime - TestStepStartTime))
        TestStepMemConsumed = WinMemBegin - WinMemEnd  # get memory consumed

        """ Run cancelled feature is disabled for now. maybe implement it later"""
        run_cancelled = ""
        # if ConfigModule.get_config_value("RunDefinition", "local_run") == "False":
        #     run_cancelled = get_status_of_runid(run_id)

        # add result of each step to a list;
        # for a test case to pass all steps should pass;
        # at least one Failed makes it 'Fail' else 'Warning' or 'Blocked';
        run_cancelled = ""
        # if ConfigModule.get_config_value("RunDefinition", "local_run") == "False":
        #     run_cancelled = get_status_of_runid(run_id)

        # append step result
        if sStepResult:
            sTestStepResultList.append(sStepResult.upper())
        else:
            sTestStepResultList.append("FAILED")
            CommonUtil.ExecLog(
                sModuleInfo, "sStepResult : %s" % sStepResult, 1
            )  # add log
            sStepResult = "Failed"

        # step dictionary after execution
        after_execution_dict = {
            "stepstarttime": sTestStepStartTime,
            "stependtime": sTestStepEndTime,
            "end_memory": WinMemEnd,
            "duration": TestStepDuration,
            "memory_consumed": TestStepMemConsumed,
            "logid": ConfigModule.get_config_value("sectionOne", "sTestStepExecLogId", temp_ini_file)
        }

        # add/print logs for step result

        if sStepResult.upper() == PASSED_TAG.upper():
            # Step Passed
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Passed" % current_step_name, 1
            )
            after_execution_dict.update({"status": PASSED_TAG})

        elif sStepResult.upper() == SKIPPED_TAG.upper():
            # Step Passed
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Skipped" % current_step_name, 1
            )
            after_execution_dict.update({"status": SKIPPED_TAG})

        elif sStepResult.upper() == WARNING_TAG.upper():
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Warning" % current_step_name, 2
            )
            after_execution_dict.update({"status": WARNING_TAG})

            if not test_case_continue:
                already_failed = True
                StepSeq += 1
                CommonUtil.CreateJsonReport(stepInfo=after_execution_dict)
                continue

        elif sStepResult.upper() == NOT_RUN_TAG.upper():
            # Step has Warning, but continue running next test step for this test case
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Not Run" % current_step_name, 2
            )
            after_execution_dict.update({"status": NOT_RUN_TAG})

        elif sStepResult.upper() == FAILED_TAG.upper():

            # step failed, if linked test case notify other test cases via setting server variable named 'is_failed'
            global failed_due_to_linked_fail

            if is_linked == "yes" and not failed_due_to_linked_fail:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    str(test_case)
                    + " failed in linked run.. Notifying other linked machines",
                    3,
                )

                # set server variables
                set_server_variable(run_id, "is_failed", "yes")
                set_server_variable(
                    run_id,
                    "failed_machine",
                    (CommonUtil.MachineInfo().getLocalUser()).lower(),
                )
                set_server_variable(run_id, "failed_test_case", str(test_case))

            # Step has a Critical failure, fail the test step and test case. go to next test case

            CommonUtil.ExecLog(
                sModuleInfo, "%s%s" % (current_step_name, CommonUtil.to_dlt_from_fail_reason), 3
            )  # add log

            after_execution_dict.update({"status": FAILED_TAG})  # dictionary update

            # check if set for continue
            if not test_case_continue and ConfigModule.get_config_value("RunDefinition", "local_run") == "False":
                # run_cancelled = get_status_of_runid(run_id)
                if run_cancelled == "Cancelled":
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Test Run status is Cancelled. Exiting the current Test Case...%s"
                        % test_case,
                        2,
                    )  # add log
                already_failed = True
                StepSeq += 1
                CommonUtil.CreateJsonReport(stepInfo=after_execution_dict)
                continue

        elif sStepResult.upper() == BLOCKED_TAG.upper():
            # Step is Blocked, Block the test step and test case. go to next test case
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Blocked" % current_step_name, 3
            )
            after_execution_dict.update({"status": BLOCKED_TAG})

        elif sStepResult.upper() == CANCELLED_TAG.upper():
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Cancelled" % current_step_name, 3
            )
            after_execution_dict.update({"status": CANCELLED_TAG})
            cleanup_runid_from_server(run_id)
            CommonUtil.CreateJsonReport(stepInfo=after_execution_dict)
            return "pass"

        else:
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Cancelled" % current_step_name, 3
            )
            after_execution_dict.update({"status": CANCELLED_TAG})
            cleanup_runid_from_server(run_id)
            CommonUtil.CreateJsonReport(stepInfo=after_execution_dict)
            return "pass"

        CommonUtil.CreateJsonReport(stepInfo=after_execution_dict)
        if ConfigModule.get_config_value("RunDefinition", "local_run") == "False":
            # run_cancelled = get_status_of_runid(run_id)     # Response = "In-Progress"
            if run_cancelled == "Cancelled":
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Test Run status is Cancelled. Exiting the current Test Case...%s"
                    % test_case,
                    2,
                )
                sTestStepResultList[len(sTestStepResultList) - 1] = CANCELLED_TAG
                break
        StepSeq += 1
    return sTestStepResultList


# from the returned step results, it finds out the test case result
def calculate_test_case_result(sModuleInfo, TestCaseID, run_id, sTestStepResultList, testcase_info):
    if "BLOCKED" in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Blocked", 3)
        sTestCaseStatus = "Blocked"
    elif "CANCELLED" in sTestStepResultList or "Cancelled" in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Cancelled", 3)
        sTestCaseStatus = "Cancelled"
    elif "FAILED" in sTestStepResultList:
        step_index = 0
        for each in sTestStepResultList:
            if each == "FAILED":
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
            if each not in skipped_tag_list:
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
def write_log_file_for_test_case(
    sTestCaseStatus,
    test_case,
    run_id,
    sTestCaseEndTime,
    TestCaseDuration,
    temp_ini_file,
    send_log_file_only_for_fail=True,
):
    # upload the test case status before uploading log file, because there can be error while uploading log file, so we dont want to lose the important test case status
    # test_case_after_dict = {
    #     "status": sTestCaseStatus,
    #     "testendtime": sTestCaseEndTime,
    #     "duration": TestCaseDuration,
    # }
    # update_test_case_status_after_run_on_server(run_id, test_case, test_case_after_dict)

    # if settings checked, then send log file or screenshots, otherwise don't send
    if sTestCaseStatus not in passed_tag_list or (
        sTestCaseStatus in passed_tag_list and not send_log_file_only_for_fail
    ):
        local_run_settings = ConfigModule.get_config_value("RunDefinition", "local_run")
        if local_run_settings == False or local_run_settings == "False":
            # FL.RenameFile(ConfigModule.get_config_value('sectionOne','log_folder'), 'temp.log',TCID+'.log')
            TCLogFile = FL.ZipFolder(
                ConfigModule.get_config_value(
                    "sectionOne", "test_case_folder", temp_ini_file
                ),
                ConfigModule.get_config_value(
                    "sectionOne", "test_case_folder", temp_ini_file
                )
                + ".zip",
            )
            # Delete the folder
            FL.DeleteFolder(
                ConfigModule.get_config_value(
                    "sectionOne", "test_case_folder", temp_ini_file
                )
            )

            # upload will go here.
            upload_zip(
                ConfigModule.get_config_value("Authentication", "server_address"),
                ConfigModule.get_config_value("Authentication", "server_port"),
                ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file),
                run_id,
                ConfigModule.get_config_value("sectionOne", "test_case", temp_ini_file) + ".zip",
                ConfigModule.get_config_value("Advanced Options", "_file_upload_path"),
            )
            TCLogFile = (
                os.sep
                + ConfigModule.get_config_value("Advanced Options", "_file_upload_path")
                + os.sep
                + run_id.replace(":", "-")
                + "/"
                + ConfigModule.get_config_value(
                    "sectionOne", "test_case", temp_ini_file
                )
                + ".zip"
            )
            FL.DeleteFile(
                ConfigModule.get_config_value(
                    "sectionOne", "test_case_folder", temp_ini_file
                )
                + ".zip"
            )
        else:
            TCLogFile = ""
        # upload the log file ID
    #     test_case_after_dict = {"logid": TCLogFile}
    # executor = CommonUtil.GetExecutor()
    # executor.submit(update_test_case_status_after_run_on_server, run_id, test_case, test_case_after_dict)


# run a test case of a runid
def start_sending_log_to_server(run_id, temp_ini_file):
    local_run_settings = ConfigModule.get_config_value("RunDefinition", "local_run")
    # if local_run_settings == False or local_run_settings == 'False':
    #     current_log_file = os.path.join(ConfigModule.get_config_value('sectionOne', 'log_folder', temp_ini_file),
    #                                     'temp.log')
    #     lines_seen = set()
    #     for line in open(current_log_file, 'r'):
    #         if line not in lines_seen:
    #             lines_seen.add(line)
    #             send_debug_data(run_id, "log", line)
    #     FL.DeleteFile(current_log_file)
    # all_log = list(lines_seen)
    # all_log = "###".join(all_log)
    # print all_log
    # send_debug_data(run_id,"log",all_log)


def start_sending_shared_var_to_server(run_id):
    try:
        shared_resource = shared.Shared_Variable_Export()
        for key in shared_resource:
            if key == "selenium_driver":
                value = "Selenium Driver Instance"
            elif key == "appium_driver":
                value = "Appium Driver Instance"
            else:
                value = shared_resource[key]
            try:
                send_debug_data(run_id, "var-" + key, value)
            except:
                continue
    except:
        return True


def start_sending_step_result_to_server(run_id, debug_steps, sTestStepResultList):
    try:
        for i in range(0, len(debug_steps)):
            send_debug_data(run_id, "result-" + debug_steps[i], sTestStepResultList[i])
    except:
        return True


def cleanup_driver_instances():  # cleans up driver(selenium, appium) instances
    try:  # if error happens. we don't care, main driver should not stop, pass in exception

        if shared.Test_Shared_Variables("selenium_driver"):
            import Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions as Selenium
            driver = shared.Remove_From_Shared_Variables("selenium_driver")
            if driver not in failed_tag_list:
                Selenium.Tear_Down_Selenium()
        if shared.Test_Shared_Variables("appium_driver"):
            import Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions as Appium
            driver = shared.Remove_From_Shared_Variables("appium_driver")
            if driver not in failed_tag_list:
                Appium.teardown_appium()

    except:
        pass


def run_test_case(
    TestCaseID,
    sModuleInfo,
    run_id,
    final_dependency,
    final_run_params,
    temp_ini_file,
    is_linked,
    testcase_info,
    executor,
    debug_info,
    send_log_file_only_for_fail=True,
    performance=False,
    browserDriver=None,
):
    shared.Set_Shared_Variables("run_id", run_id)
    test_case = str(TestCaseID).replace("#", "no")
    ConfigModule.add_config_value("sectionOne", "sTestStepExecLogId", "MainDriver", temp_ini_file)
    file_specific_steps = download_attachments_for_test_case(
        sModuleInfo, run_id, test_case, temp_ini_file,
        testcase_info["testcase_attachments_links"], testcase_info["step_attachments"]
    )
    TestCaseName = testcase_info["title"]
    log_line = "# EXECUTING TEST CASE : %s :: %s #" % (test_case, TestCaseName)
    print("#"*(len(log_line)))
    CommonUtil.ExecLog("", log_line, 4, False)
    print("#"*(len(log_line)))

    # get test case start time
    TestCaseStartTime = time.time()
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
        executor,
        debug_info,
        is_linked,
        performance
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

    TCLogFile = (
            os.sep
            + ConfigModule.get_config_value("Advanced Options", "_file_upload_path")
            + os.sep
            + run_id.replace(":", "-")
            + "/"
            + ConfigModule.get_config_value("sectionOne", "test_case", temp_ini_file)
            + ".zip"
    )
    after_execution_dict = {
        "teststarttime": datetime.fromtimestamp(TestCaseStartTime).strftime("%Y-%m-%d %H:%M:%S"),
        "logid": TCLogFile,
        "testendtime": sTestCaseEndTime,
        "duration": TestCaseDuration,
        "status": sTestCaseStatus,
        "failreason": ""
    }
    CommonUtil.CreateJsonReport(TCInfo=after_execution_dict)

    debug = True if run_id.startswith("debug") else False
    # if str(run_id).startswith("debug"):
    #     debug = True
    #     debug_steps = debug_info["debug_steps"]
    #     str_list = str(debug_steps).split("-")
    #     debug_steps = str_list[0]
    #     debug_steps = str(debug_steps[1:-1]).split(",")
    #
    # if debug and ConfigModule.get_config_value("RunDefinition", "local_run") == "False":
    #     CommonUtil.Join_Thread_and_Return_Result("screenshot")  # Let the capturing screenshot end in thread
    #     executor.submit(cleanup_runid_from_server, run_id)
    #     executor.submit(start_sending_log_to_server, run_id, temp_ini_file)
    #     executor.submit(start_sending_shared_var_to_server, run_id)
    #     executor.submit(start_sending_step_result_to_server, run_id, debug_steps, sTestStepResultList)
    #     executor.submit(send_debug_data, run_id, "finished", "yes")

    if not debug:  # if normal run, then write log file and cleanup driver instances
        CommonUtil.Join_Thread_and_Return_Result("screenshot")  # Let the capturing screenshot end in thread
        cleanup_driver_instances()  # clean up drivers
        shared.Clean_Up_Shared_Variables()  # clean up shared variables
        if ConfigModule.get_config_value("RunDefinition", "local_run") == "False":
            # executor.submit(
            #     write_log_file_for_test_case,
            #     sTestCaseStatus,
            #     test_case,
            #     run_id,
            #     sTestCaseEndTime,
            #     TestCaseDuration,
            #     temp_ini_file,
            #     send_log_file_only_for_fail,
            # )
            write_log_file_for_test_case(
                sTestCaseStatus,
                test_case,
                run_id,
                sTestCaseEndTime,
                TestCaseDuration,
                temp_ini_file,
                send_log_file_only_for_fail,
            )

    if sTestStepResultList[-1] == CANCELLED_TAG:
        return CANCELLED_TAG
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

def update_fail_reasons_of_test_cases(run_id, TestCaseID):
    try:
        for test_case in TestCaseID:
            try:
                FailReason = get_fail_reason_of_a_test_case(run_id, test_case[0])
            except Exception:
                CommonUtil.Exception_Handler(sys.exc_info())
                FailReason = ""
            test_case_after_dict = {"failreason": FailReason}
            update_test_case_status_after_run_on_server(
                run_id, test_case[0], test_case_after_dict
            )
    except:
        pass


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


def get_all_run_id_info(Userid, sModuleInfo):
    # response = requests.get(RequestFormatter.form_uri("getting_json_data_api"), {"machine_name": Userid}).json()
    # # response = RequestFormatter.Get("getting_json_data_api", {"machine_name": Userid})
    # for _ in range(15):
    #     if response["found"]:
    #         break
    #     else:
    #         time.sleep(2)
    #         response = requests.get(RequestFormatter.form_uri("getting_json_data_api"), {"machine_name": Userid}).json()
    # else:
    #     CommonUtil.ExecLog(sModuleInfo, "Could not get run information", 3)
    #     return False

    path = "D:\\Zeuz Node\\ZeuzPythonNode\\Projects\\Sample_Amazon_Testing\\RequiredFormatOf_TestCase.json"
    with open(path, "r") as f:
        Json_data = json.load(f)
        if isinstance(Json_data, str):
            Json_data = json.loads(Json_data)
    with open(path, "w") as f:
        json.dump(Json_data, f, indent=2)
    return Json_data

    # path = os.path.abspath(__file__).split("Framework")[0]/Path("tests")/Path("test_cases_data.json")
    # with open(path, "w") as f:
    #     json.dump(response["json"], f, indent=2)
    # return response["json"]


def upload_json_report(Userid, temp_ini_file, run_id):
    # path = os.path.join(os.path.abspath(__file__).split("Framework")[0])/Path("AutomationLog")/Path("execution_log.json")
    path = ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file) / Path(run_id.replace(":", "-"))
    zip_path = path / Path("execution_log.zip")
    path = path / Path("execution_log.json")
    json_report = CommonUtil.get_all_logs(json=True)
    with open(path, "w") as f:
        json.dump(json_report, f, indent=2)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(path, arcname="execution_log.json")
    FL.DeleteFile(path)

    if ConfigModule.get_config_value("RunDefinition", "local_run") == "False":
        for i in range(720):    # 1 hour
            res = requests.get(RequestFormatter.form_uri("is_copied_api/"), {"runid": run_id}, verify=False)
            r = res.json()
            if r["flag"]:
                break
            time.sleep(5)
        else:
            print("Run history was not created in server so couldn't upload the report for run_id '%s'." % run_id +
                  "Get the report from below path-\n" + path)
            return

        with open(zip_path, "rb") as fzip:
            for i in range(5):
                res = requests.post(
                    RequestFormatter.form_uri("create_report_log_api/"),
                    files={"file": fzip},
                    data={"machine_name": Userid},
                    verify=False)
                if res.status_code == 200:
                    res_json = res.json()
                    if isinstance(res_json, dict) and 'message' in res_json and res_json["message"]:
                        print("Successfully Uploaded json report to server")
                    else:
                        print("Could not Upload json report to server")
                    break
                time.sleep(1)
            else:
                print("Could not Upload json report to server")


# main function
def main(device_dict, user_info_object, all_run_id_info):

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

    # Get all run_id, set, test case, step, action info together with the new api
    # all_run_id_info = get_all_run_id_info(Userid, sModuleInfo)
    # if not all_run_id_info:
    #     return "failed"

    if len(all_run_id_info) == 0:
        CommonUtil.ExecLog("", "No Test Run Schedule found for the current user : %s" % Userid, 2)
        return False

    executor = CommonUtil.GetExecutor()
    for run_id_info in all_run_id_info:
        run_id = run_id_info["run_id"]
        run_cancelled = ""
        debug_info = ""
        CommonUtil.clear_all_logs()

        # Write testcase json
        path = ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file) / Path(run_id.replace(":", "-"))
        FL.CreateFolder(path)
        path = path / Path("test_cases_data.json")
        with open(path, "w") as f:
            json.dump(all_run_id_info, f, indent=2)

        # Start websocket server if we're in debug mode.
        if run_id.lower().startswith("debug"):
            print("[LIVE LOG] Connecting to Live Log service")
            ws.connect()
            print("[LIVE LOG] Connected to Live Log service")

        device_order = run_id_info["device_info"]
        final_dependency = run_id_info["dependency_list"]
        is_linked = run_id_info["is_linked"]
        final_run_params_from_server = run_id_info["run_time"]
        if not run_id.startswith("debug"):
            rem_config = {
                "threading": run_id_info["threading"] if "threading" in run_id_info else False,
                "local_run": run_id_info["local_run"] if "local_run" in run_id_info else False,
                "take_screenshot": run_id_info["take_screenshot"] if "take_screenshot" in run_id_info else True,
                "upload_log_file_only_for_fail": run_id_info["upload_log_file_only_for_fail"] if "upload_log_file_only_for_fail" in run_id_info else False,
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
        driver_list = ['Built_In_Selenium_Driver', 'Built_In_RestApi', 'Built_In_Appium_Driver', 'Built_In_Selenium',
                       'Built_In_Driver', 'deepak', 'Built_In_Appium', 'Built_In_NET_Win', 'Jarvis']
        final_run_params = {}
        for param in final_run_params_from_server:
            final_run_params[param] = CommonUtil.parse_value_into_object(list(final_run_params_from_server[param].items())[0][1])
        send_log_file_only_for_fail = ConfigModule.get_config_value("RunDefinition", "upload_log_file_only_for_fail")
        send_log_file_only_for_fail = False if send_log_file_only_for_fail.lower() == "false" else True

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
            return "pass"

        CommonUtil.all_logs_json = all_run_id_info
        cnt = 1
        for testcase_info in all_testcases_info:
            performance_test_case = False
            if testcase_info["automatability"].lower() == "performance":
                performance_test_case = True
            test_case_no = testcase_info["testcase_no"]
            test_case_name = testcase_info["title"]
            set_device_info_according_to_user_order(device_order, device_dict, test_case_no, test_case_name, user_info_object, Userid)

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
                # run test case (not performance)
                run_cancelled = run_test_case(
                    test_case_no,
                    sModuleInfo,
                    run_id,
                    final_dependency,
                    final_run_params,
                    temp_ini_file,
                    is_linked,
                    testcase_info,
                    executor,
                    debug_info,
                    send_log_file_only_for_fail,
                )
                CommonUtil.clear_all_logs()  # clear logs
                if run_cancelled == CANCELLED_TAG:
                    break

                print("Executed %s test cases" % cnt)
                cnt += 1
        # calculate elapsed time of runid
        sTestSetEndTime = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
        TestSetEndTime = time.time()
        TimeDiff = TestSetEndTime - TestSetStartTime
        TimeInSec = int(TimeDiff)
        TestSetDuration = CommonUtil.FormatSeconds(TimeInSec)

        after_execution_dict = {
            "setendtime": sTestSetEndTime,
            "duration": TestSetDuration
        }
        CommonUtil.CreateJsonReport(setInfo=after_execution_dict)
        CommonUtil.ExecLog("", "Test Set Completed", 4, False)

        ConfigModule.add_config_value("sectionOne", "sTestStepExecLogId", "MainDriver", temp_ini_file)

        if run_cancelled == CANCELLED_TAG:
            CommonUtil.ExecLog(sModuleInfo, "Test Set Cancelled by the User", 1)  # add log
        elif not run_id.startswith("debug"):
            upload_json_report(Userid, temp_ini_file, run_id)
            # executor.submit(upload_json_report)
            """ Need to know what to do with the below functions """
            # executor.submit(update_test_case_result_on_server, run_id, sTestSetEndTime, TestSetDuration)
            # executor.submit(send_email_report_after_exectution, run_id, project_id, team_id)
            # executor.submit(update_fail_reasons_of_test_cases, run_id, TestCaseLists)

        # Close websocket connection.
        if run_id.lower().startswith("debug"):
            ws.close()
            print("[LIVE LOG] Disconnected from Live Log service")

    return "pass"


if __name__ == "__main__":
    main()
