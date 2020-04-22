# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import inspect
import os
import time
import sys
import urllib.request, urllib.error, urllib.parse
import queue
import shutil
import importlib
import requests
import threading
import subprocess
import signal
from sys import platform as _platform
from datetime import datetime
from datetime import timedelta
from threading import Timer
from Framework.Built_In_Automation import Shared_Resources
from .Utilities import ConfigModule, FileUtilities as FL, CommonUtil, RequestFormatter
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as shared

top_path = os.path.dirname(os.getcwd())
drivers_path = os.path.join(top_path, 'Drivers')
sys.path.append(drivers_path)

MODULE_NAME = inspect.getmodulename(__file__)

'''Constants'''
PROGRESS_TAG = 'In-Progress'
PASSED_TAG = 'Passed'
SKIPPED_TAG = 'Skipped'
WARNING_TAG = 'Warning'
FAILED_TAG = 'Failed'
NOT_RUN_TAG = 'Not Run'
BLOCKED_TAG = 'Blocked'
CANCELLED_TAG = 'Cancelled'
COMPLETE_TAG = 'Complete'
passed_tag_list = ['Pass', 'pass', 'PASS', 'PASSED', 'Passed', 'passed', 'true', 'TRUE', 'True', '1', 'Success',
                   'success', 'SUCCESS']
failed_tag_list = ['Fail', 'fail', 'FAIL', 'Failed',
                   'failed', 'FAILED', 'false', 'False', 'FALSE', '0']
skipped_tag_list = ['skip', 'SKIP', 'Skip', 'skipped', 'SKIPPED', 'Skipped']
device_info = {}
# if other linked machine failed in a linked run
failed_due_to_linked_fail = False


# writes all logs to server
def write_all_logs_to_server(all_logs_list):
    i = 0
    for all_logs in all_logs_list:
        while i < 5:
            try:
                r = RequestFormatter.Post('all_log_execution', {
                                          'all_logs': all_logs})
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
    return RequestFormatter.Get('send_email_report_after_excecution_api',
                                {'run_id': run_id, 'project_id': project_id, 'team_id': team_id})


# returns all drivers
def get_all_drivers_list():
    return RequestFormatter.Get('get_all_drivers_api')


# returns all latest versions
def get_latest_zeuz_versions():
    return RequestFormatter.Get('get_latest_zeuz_versions_api')


# returns all runids assigned to a machine, NEEDS IMPROVEMENT
def get_all_run_ids(Userid, sModuleInfo):
    all_run = []
    try:
        wait_time = 5
        end_time = datetime.now() + timedelta(seconds=wait_time)
        while datetime.now() <= end_time:
            all_run = RequestFormatter.Get('get_all_submitted_run_of_a_machine_api', {
                                           'machine_name': Userid})

            if len(all_run) == 0:
                CommonUtil.ExecLog(
                    sModuleInfo, "Error while fetching test run", 2)
                CommonUtil.ExecLog(
                    sModuleInfo, "Trying again to fetch test run", 1)
                time.sleep(1)
            else:
                return all_run

        CommonUtil.ExecLog(
            sModuleInfo, "Couldn't get the test run deployed on this machine, please try again", 3)
        return all_run

    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        CommonUtil.ExecLog(
            sModuleInfo, "Couldn't get the test run deployed on this machine, please try again", 3)
        return all_run


# returns all runids assigned to a machine, NEEDS IMPROVEMENT
def get_device_order(Userid):
    return RequestFormatter.Get('get_machine_device_order_api', {'machine_name': Userid})


# sets server variable
def set_server_variable(run_id, key, value):
    return RequestFormatter.Get('set_server_variable_api', {'run_id': run_id, 'var_name': key, 'var_val': value})


# gets server variable
def get_server_variable(run_id, key):
    return RequestFormatter.Get('get_server_variable_api', {'run_id': run_id, 'var_name': key})


# get global list variable
def get_global_list_variable(name):
    return RequestFormatter.Get('set_or_get_global_server_list_variable_api',{'name': name})


# append to global list variable
def append_to_global_list_variable(name, value):
    return RequestFormatter.Get('append_value_to_global_server_list_variable_api',{'name': name, 'value':value})


# remove item from global list variable
def remove_item_from_global_list_variable(name, value):
    return RequestFormatter.Get('delete_global_server_list_variable_by_value_api',{'name': name, 'value':value})


# get all server variable
def get_all_server_variable(run_id):
    return RequestFormatter.Get('get_all_server_variable_api', {'run_id': run_id})


# get all server variable
def get_all_remote_config(run_id):
    return RequestFormatter.Get('get_all_remote_config_api', {'run_id': run_id})


# get all server variable
def delete_all_server_variable(run_id):
    return RequestFormatter.Get('delete_all_runid_server_variable_api', {'run_id': run_id})


# returns all dependencies of test cases of a run id
def get_all_dependencies(project_id, team_id, run_description):
    dependency_list = RequestFormatter.Get('get_all_dependency_based_on_project_and_team_api',
                                           {'project_id': project_id, 'team_id': team_id})
    final_dependency = get_final_dependency_list(
        dependency_list, run_description)
    return final_dependency


# returns all runtime parameters of test cases of a run id
def get_all_runtime_parameters(run_id):
    run_params_list = RequestFormatter.Get(
        'get_all_run_parameters_based_on_project_and_team_api', {'run_id': run_id})
    final_run_params = get_run_params_list(run_params_list)
    return final_run_params


# updates current runid status on server database
def update_run_id_info_on_server(run_id):
    RequestFormatter.Get('update_machine_info_based_on_run_id_api',
                         {'run_id': run_id, 'options': {'status': PROGRESS_TAG}})
    sTestSetStartTime = datetime.fromtimestamp(
        time.time()).strftime('%Y-%m-%d %H:%M:%S')
    RequestFormatter.Get('update_test_env_results_based_on_run_id_api',
                         {'options': {'status': PROGRESS_TAG, 'teststarttime': str(sTestSetStartTime)},
                          'run_id': run_id})


# returns all automated test cases of a runid
def get_all_automated_test_cases_in_run_id(run_id, tester_id):
    TestCaseLists = RequestFormatter.Get('get_all_automated_test_cases_based_on_run_id_api', {
                                         'run_id': run_id, 'tester_id': tester_id})
    return TestCaseLists


# checks if a step of a test case is the verification point of that test case
def check_if_step_is_verification_point(run_id, tc_id, step_sequence):
    return RequestFormatter.Get('if_failed_at_verification_point_api',
                                {'run_id': run_id, 'tc_id': tc_id, 'step_sequence': step_sequence})


# if run is cancelled then it can be called, it cleans up the runid from database
def cleanup_runid_from_server(run_id):
    RequestFormatter.Get('clean_up_run_api', {'run_id': run_id})


# checks if this test case is a copy of another test case
def check_if_test_case_is_copied(run_id, test_case):
    return RequestFormatter.Get('is_test_case_copied_api', {'run_id': run_id, 'test_case': test_case})


def get_debug_steps(run_id):
    return RequestFormatter.Get('get_debug_steps_api', {'run_id': run_id})


def send_debug_data(run_id, key, value):
    return RequestFormatter.Get('send_debug_data_api', {'run_id': run_id, 'key': key, 'value': value})


# returns test case details needed to run the test case
def get_test_case_details(run_id, test_case):
    return RequestFormatter.Get('get_test_case_detail_api', {'run_id': run_id, 'test_case': test_case})


# updates current test case status on server database
def update_test_case_progress_on_server(run_id, test_case, sTestCaseStartTime):
    return RequestFormatter.Get('test_case_results_update_returns_index_api', {'run_id': run_id, 'test_case': test_case,
                                                                               'options': {'status': PROGRESS_TAG,
                                                                                           'teststarttime': sTestCaseStartTime}})


# returns all steps of a test case
def get_all_steps_of_a_test_case(run_id, test_case):
    return RequestFormatter.Get('test_step_fetch_for_test_case_run_id_api', {'run_id': run_id, 'test_case': test_case})


# returns step_id of a test step
def get_step_id_of_a_test_step(stepname):
    return RequestFormatter.Get('test_step_id_fetch_from_step_name_api', {'stepname': stepname})


# returns screen cature settings of a test step
def get_screen_capture_settings_of_a_test_step(step_id):
    return RequestFormatter.Get('screen_capture_fetch_for_test_step_api', {'step_id': step_id})


# returns test step details needed to run the test step
def get_step_meta_data_of_a_step(run_id, test_case, StepSeq):
    return RequestFormatter.Get('get_step_meta_data_api',
                                {'run_id': run_id, 'test_case': test_case, 'step_seq': StepSeq})


# if a test case is failed it returns the fail reason
def get_fail_reason_of_a_test_case(run_id, test_case):
    return RequestFormatter.Get('get_failed_reason_test_case_api', {'run_id': run_id, 'test_case': test_case})


# updates current test case status on server database after the test case is run
def update_test_case_status_after_run_on_server(run_id, test_case, test_case_after_dict):
    RequestFormatter.Get('test_case_results_update_returns_index_api',
                         {'run_id': run_id, 'test_case': test_case, 'options': test_case_after_dict})


# returns current status of the runid
def get_status_of_runid(run_id):
    return RequestFormatter.Get('get_status_of_a_run_api', {'run_id': run_id})


# updates current test step status on server database
def update_test_step_status(run_id, test_case, current_step_id, current_step_sequence, Dict):
    RequestFormatter.Get('test_step_results_update_returns_index_api',
                         {'run_id': run_id, 'tc_id': test_case, 'step_id': current_step_id,
                          'test_step_sequence': current_step_sequence, 'options': Dict})


# updates current test case result(like pass/fail etc.) on server database
def update_test_case_result_on_server(run_id, sTestSetEndTime, TestSetDuration):
    RequestFormatter.Get('update_test_env_results_based_on_run_id_api', {
        'options': {'status': COMPLETE_TAG, 'testendtime': sTestSetEndTime, 'duration': TestSetDuration},
        'run_id': run_id})
    RequestFormatter.Get('update_machine_info_based_on_run_id_api',
                         {'run_id': run_id, 'options': {'status': COMPLETE_TAG, 'email_flag': True}})


# returns step data of a test step in a test case
def get_test_step_data(run_id, test_case, current_step_sequence, sModuleInfo):
    try:
        wait_time = 5
        end_time = datetime.now() + timedelta(seconds=wait_time)
        while datetime.now() <= end_time:
            response = RequestFormatter.Get('get_test_step_data_based_on_test_case_run_id_api',
                                            {'run_id': run_id, 'test_case': test_case,
                                             'step_sequence': current_step_sequence})

            if 'status' not in response or response['status'] in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo, "Error while fetching step data: " + response['message'], 2)
                CommonUtil.ExecLog(
                    sModuleInfo, "Trying again to fetch step data", 1)
                
            else:
                return response['step_data']
            
            time.sleep(1)

        CommonUtil.ExecLog(
            sModuleInfo, "Couldn't get step data, returning failed", 3)
        return "failed"
    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        CommonUtil.ExecLog(
            sModuleInfo, "Couldn't get step data, returning failed", 3)
        return "failed"


# updates current test step result(like pass/fail etc.) on server database
def update_test_step_results_on_server(run_id, test_case, current_step_id, current_step_sequence, after_execution_dict):
    RequestFormatter.Get('test_step_results_update_returns_index_api',
                         {'run_id': run_id, 'tc_id': test_case, 'step_id': current_step_id,
                          'test_step_sequence': current_step_sequence,
                          'options': after_execution_dict})


# checks if the user has permission to run test or not
def check_user_permission_to_run_test(sModuleInfo, Userid):
    r = RequestFormatter.Get('get_valid_machine_name_api', {
                             'machine_name': Userid})
    if not r:
        CommonUtil.ExecLog(
            sModuleInfo, "User don't have permission to run the tests", 3)
        return "You Don't Have Permission"
    else:
        return "passed"


def check_if_other_machines_failed_in_linked_run():
    # can get multiple server variable with one action
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        run_id = shared.Get_Shared_Variables('run_id')

        dict = get_all_server_variable(run_id)
        try:
            if 'is_failed' in dict and dict['is_failed'] != 'null' and dict['is_failed'] == 'yes':
                global failed_due_to_linked_fail

                failed_machine = ''
                if 'failed_machine' in dict:
                    failed_machine = dict['failed_machine']
                if failed_machine == (CommonUtil.MachineInfo().getLocalUser()).lower():
                    return 'passed'

                failed_due_to_linked_fail = True

                failed_test_case = ''
                if 'failed_test_case' in dict:
                    failed_test_case = dict['failed_test_case']

                CommonUtil.ExecLog(sModuleInfo, "Linked test case '%s' failed in machine '%s'.. Test Case Failed..." % (
                    failed_test_case, failed_machine), 3)
                return "failed"
            else:
                time.sleep(1)
        except:
            pass

        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# gets run time parameters
def get_run_params_list(run_params):
    run_para = []
    for each in run_params:
        m_ = {}
        m_.update({'field': each[0]})
        m_.update({'name': each[1]})
        m_.update({'value': each[2]})
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
    url_link = server_id + ':' + str(port_id) + "/Home/UploadZip/"
    if not url_link.startswith("http") or not url_link.startswith("https"):
        url_link = "http://" + url_link

    total_file_path = temp_folder + os.sep + \
        run_id.replace(':', '-') + os.sep + file_name

    i = 0
    while i < 5:
        try:
            fileObj = open(total_file_path, 'rb')
            file_list = {'docfile': fileObj}
            data_list = {'run_id': run_id,
                         'file_name': file_name, 'base_path': base_path}
            r = requests.post(url_link, files=file_list, data=data_list)
            if r.status_code == 200:
                CommonUtil.ExecLog(
                    sModuleInfo, "Zip File is uploaded to production successfully", 4, False)
                break
            else:
                CommonUtil.ExecLog(
                    sModuleInfo, "Zip File is not uploaded to production successfully. Trying again", 4, False)
                time.sleep(2)
                i += 1
        except:
            CommonUtil.ExecLog(
                sModuleInfo, "Zip File is not uploaded to production successfully. Trying again", 4, False)
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
                    dependency_list_final.update(
                        {current_dependency: current_item})
    return dependency_list_final


# downloads attachments for a test step
def download_attachments_for_test_case(sModuleInfo, run_id, test_case, temp_ini_file):
    CommonUtil.ExecLog(
        sModuleInfo, "-------------*************--------------", 1)
    CommonUtil.ExecLog(
        sModuleInfo, "Creating Built_In_Automation Log for test case: %s" % test_case, 1)
    try:
        log_file_path = ConfigModule.get_config_value(
            'sectionOne', 'temp_run_file_path', temp_ini_file)
    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())

    test_case_folder = log_file_path + os.sep + \
        (run_id.replace(':', '-') + os.sep + test_case.replace(":", '-'))
    ConfigModule.add_config_value(
        'sectionOne', 'test_case', test_case, temp_ini_file)
    ConfigModule.add_config_value(
        'sectionOne', 'test_case_folder', test_case_folder, temp_ini_file)
    log_folder = test_case_folder + os.sep + 'Log'
    ConfigModule.add_config_value(
        'sectionOne', 'log_folder', log_folder, temp_ini_file)
    screenshot_folder = test_case_folder + os.sep + 'screenshots'
    ConfigModule.add_config_value(
        'sectionOne', 'screen_capture_folder', screenshot_folder, temp_ini_file)

    home = os.path.join(FL.get_home_folder(),
                        os.path.join('Desktop', 'Attachments'))
    ConfigModule.add_config_value(
        'sectionOne', 'download_folder', home, temp_ini_file)

    # create_test_case_folder
    test_case_folder = ConfigModule.get_config_value(
        'sectionOne', 'test_case_folder', temp_ini_file)
    FL.CreateFolder(test_case_folder)

    # FL.CreateFolder(Global.TCLogFolder + os.sep + "ProductLog")
    log_folder = ConfigModule.get_config_value(
        'sectionOne', 'log_folder', temp_ini_file)
    FL.CreateFolder(log_folder)

    # FL.CreateFolder(Global.TCLogFolder + os.sep + "Screenshots")
    # creating ScreenShot File
    screen_capture_folder = ConfigModule.get_config_value(
        'sectionOne', 'screen_capture_folder', temp_ini_file)
    FL.CreateFolder(screen_capture_folder)

    # creating the download folder
    download_folder = ConfigModule.get_config_value(
        'sectionOne', 'download_folder', temp_ini_file)

    # test case attachements
    test_case_attachments = RequestFormatter.Get('get_test_case_attachments_api',
                                                 {'run_id': run_id, 'test_case': test_case})
    test_step_attachments = RequestFormatter.Get('get_test_step_attachments_for_test_case_api',
                                                 {'run_id': run_id, 'test_case': test_case})
    FL.DeleteFolder(ConfigModule.get_config_value(
        'sectionOne', 'download_folder', temp_ini_file))
    FL.CreateFolder(download_folder)
    file_specific_steps = {}
    for each in test_case_attachments:
        CommonUtil.ExecLog(
            sModuleInfo, "Attachment download for test case %s started" % test_case, 1)
        m = each[1] + '.' + each[2]  # file name
        f = open(download_folder + '/' + m, 'wb')

        download_url = ConfigModule.get_config_value('Authentication', 'server_address') + ':' + str(
            ConfigModule.get_config_value('Authentication', 'server_port'))

        if not download_url.startswith('http') or not download_url.startswith('https'):
            download_url = 'https://' + download_url

        download_url += '/static' + each[0]

        # Use request streaming to efficiently download files
        with requests.get(download_url, stream=True) as r:
            shutil.copyfileobj(r.raw, f)

        # f.write(urllib.request.urlopen(download_url).read())
        file_specific_steps.update({m: download_folder + '/' + m})
        f.close()
    if test_case_attachments:
        CommonUtil.ExecLog(
            sModuleInfo, "Attachment download for test case %s finished" % test_case, 1)
    for each in test_step_attachments:
        CommonUtil.ExecLog(
            sModuleInfo, "Attachment download for steps in test case %s started" % test_case, 1)
        m = each[1] + '.' + each[2]  # file name
        if _platform == 'win32':
            sep = '\\'
        else:
            sep = '/'
        if not os.path.exists(download_folder + sep + str(each[3])):
            FL.CreateFolder(download_folder + sep + str(each[3]))
        f = open(download_folder + sep + str(each[3]) + sep + m, 'wb')
        f.write(urllib.request.urlopen('http://' + ConfigModule.get_config_value('Authentication', 'server_address') + ':' + str(
            ConfigModule.get_config_value('Authentication', 'server_port')) + '/static' + each[0]).read())
        file_specific_steps.update(
            {m: download_folder + sep + str(each[3]) + sep + m})
        f.close()
    if test_step_attachments:
        CommonUtil.ExecLog(
            sModuleInfo, "Attachment download for steps in test case %s finished" % test_case, 1)

    return file_specific_steps


# call the function of a test step that is in its driver file
def call_driver_function_of_test_step(sModuleInfo, TestStepsList, StepSeq, step_time, driver_list, current_step_name,
                                      final_dependency, final_run_params, test_steps_data, file_specific_steps, debug_actions=None):
    try:
        q = queue.Queue()  # define queue

        # get step driver
        if TestStepsList[StepSeq - 1][8] != None:
            current_driver = TestStepsList[StepSeq - 1][8]
        else:
            current_driver = TestStepsList[StepSeq - 1][3]

        print("@@@@@@@@@@ CURRENT DRIVER: {}".format(current_driver))

        if current_driver in driver_list:
            try:
                module_name = importlib.import_module(current_driver)  # get module
                print("FOUND")
                # get step name
                if TestStepsList[StepSeq - 1][8] != None:
                    step_name = (TestStepsList[StepSeq - 1][7]).strip()
                else:
                    step_name = current_step_name

                # step_id = get_step_id_of_a_test_step(step_name)
                # step_id = step_id[0]
                # will search in the original step not in the alias step for screen capture settings
                step_id = TestStepsList[StepSeq - 1][0]
                step_name = step_name.lower().replace(' ', '_')

                try:
                    # importing functions from driver
                    functionTocall = getattr(module_name, step_name)
                except Exception as e:
                    CommonUtil.Exception_Handler(sys.exc_info(), None,
                                                 "Could not find function name: %s in Driver/%s.py. Perhaps you need to add a custom driver or add an alias step to the Test Step." % (
                                                 step_name, current_driver))
                    sStepResult = "Failed"

                try:
                    simple_queue = queue.Queue()  # another queue (?)

                    try:
                        # get screen capture settings
                        screen_capture = get_screen_capture_settings_of_a_test_step(
                            step_id)
                        if len(screen_capture) > 0:
                            screen_capture = screen_capture[0]
                        else:
                            screen_capture = 'Desktop'
                    except Exception as e:
                        screen_capture = 'Desktop'

                    # run in thread
                    if ConfigModule.get_config_value('RunDefinition', 'threading') in passed_tag_list:
                        stepThread = threading.Thread(target=functionTocall, args=(
                            final_dependency, final_run_params, test_steps_data, file_specific_steps, simple_queue,
                            screen_capture, device_info))  # start step thread

                        CommonUtil.ExecLog(
                            sModuleInfo, "Starting Test Step Thread..", 1)  # add log

                        # start thread
                        stepThread.start()

                        # Wait for the Thread to finish or until timeout
                        CommonUtil.ExecLog(sModuleInfo,
                                           "Waiting for Test Step Thread to finish..for (seconds) :%d" % step_time,
                                           1)
                        stepThread.join(float(step_time))

                        try:
                            sStepResult = simple_queue.get_nowait()
                            # Get the return value from the ExecuteTestStep
                            # fn via Queue
                            q.put(sStepResult)
                            CommonUtil.ExecLog(
                                sModuleInfo, "Test Step Thread Ended..", 1)
                        except queue.Empty:
                            # Global.DefaultTestStepTimeout
                            ErrorMessage = "Test Step didn't return after %d seconds" % step_time
                            CommonUtil.Exception_Handler(
                                sys.exc_info(), None, ErrorMessage)
                            sStepResult = "Failed"
                            q.put(sStepResult)

                            # Clean up
                            if stepThread.isAlive():
                                CommonUtil.ExecLog(
                                    sModuleInfo, "Timeout Error", 3)
                                # stepThread.__stop()
                                try:
                                    stepThread._Thread__stop()
                                    while stepThread.isAlive():
                                        time.sleep(1)
                                        CommonUtil.ExecLog(
                                            sModuleInfo, "Thread is still alive", 3)
                                except:
                                    CommonUtil.Exception_Handler(
                                        sys.exc_info())
                    else:
                        # run sequentially
                        sStepResult = functionTocall(final_dependency, final_run_params, test_steps_data,
                                                     file_specific_steps, simple_queue, screen_capture, device_info, debug_actions)
                except:
                    CommonUtil.Exception_Handler(sys.exc_info())  # handle exceptions
                    sStepResult = "Failed"

                # get step result
                if sStepResult in passed_tag_list:
                    sStepResult = 'PASSED'
                elif sStepResult in failed_tag_list:
                    sStepResult = 'FAILED'
                elif sStepResult in skipped_tag_list:
                    sStepResult = 'SKIPPED'
                elif sStepResult.upper() == CANCELLED_TAG.upper():
                    sStepResult = 'CANCELLED'
                else:
                    CommonUtil.ExecLog(
                        sModuleInfo, "sStepResult not an acceptable type", 3)
                    CommonUtil.ExecLog(
                        sModuleInfo, "Acceptable pass string(s): %s" % passed_tag_list, 3)
                    CommonUtil.ExecLog(
                        sModuleInfo, "Acceptable fail string(s): %s" % failed_tag_list, 3)
                    sStepResult = "FAILED"
                q.put(sStepResult)
            except Exception as e:
                print("### Exception : {}".format(e))
                CommonUtil.Exception_Handler(sys.exc_info())
                sStepResult = "Failed"
        else:
            CommonUtil.ExecLog(sModuleInfo,
                               "Driver %s is not found. Execution of test step failed" % current_driver, 3)
            sStepResult = "FAILED"

        return sStepResult
    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        sStepResult = "Failed"


# runs all test steps of a test case
def run_all_test_steps_in_a_test_case(Stepscount, test_case, sModuleInfo, run_id, TestStepsList, file_specific_steps,
                                      driver_list, final_dependency, final_run_params, test_case_result_index,
                                      temp_ini_file, debug=False, debug_steps='', is_linked='', performance=False, debug_actions=''):

    # define variables
    StepSeq = 1
    sTestStepResultList = []
    already_failed = False

    # Removing mutable default argument problem
    if not debug_steps:
        debug_steps = []

    if not debug_actions:
        debug_actions = []

    # performance testing
    if performance:
        StepSeq = 2
        sTestStepResultList.append("PASSED")

    # loop through the steps
    while StepSeq <= Stepscount:

        # check if debug step
        if debug and debug_steps:
            if str(StepSeq) not in debug_steps:
                StepSeq += 1
                continue

        # check if already failed
        if already_failed is True:
            always_run = TestStepsList[StepSeq - 1][9]  # get always run info
            if always_run != True:  # check if always run is false
                StepSeq += 1
                continue

        # get step info
        current_step_name = TestStepsList[StepSeq - 1][1]
        current_step_id = TestStepsList[StepSeq - 1][0]
        current_step_sequence = TestStepsList[StepSeq - 1][2]

        # add log
        CommonUtil.ExecLog(sModuleInfo, "Step : %s" % current_step_name, 1)

        # get step meta data

        step_meta_data = get_step_meta_data_of_a_step(
            run_id, test_case, StepSeq)  # get meta data from server

        # handle meta data
        try:
            test_case_continue = step_meta_data[0][1]
            step_time = step_meta_data[0][2]
            if str(step_time) != '' and step_time != None:
                step_time = int(step_time)
            else:
                step_time = 59
        except:
            test_case_continue = False
            step_time = 59

        # add config value
        ConfigModule.add_config_value('sectionOne', 'sTestStepExecLogId',
                                      run_id + "|" + test_case + "|" +
                                      str(current_step_id) +
                                      "|" + str(StepSeq),
                                      temp_ini_file)

        # get step start time
        sTestStepStartTime = datetime.fromtimestamp(
            time.time()).strftime('%Y-%m-%d %H:%M:%S')
        TestStepStartTime = time.time()

        WinMemBegin = CommonUtil.PhysicalAvailableMemory()  # get available memory

        # make test step run dictionary
        Dict = {
            'teststepsequence': current_step_sequence,
            'status': PROGRESS_TAG,
            'stepstarttime': sTestStepStartTime,
            'logid': ConfigModule.get_config_value('sectionOne', 'sTestStepExecLogId', temp_ini_file),
            'start_memory': WinMemBegin,
            'testcaseresulttindex': test_case_result_index
        }

        # update test step status
        update_test_step_status(
            run_id, test_case, current_step_id, current_step_sequence, Dict)

        # get test step data
        test_steps_data = get_test_step_data(
            run_id, test_case, current_step_sequence, sModuleInfo)

        # add log
        CommonUtil.ExecLog(sModuleInfo,
                           "********** steps data for Step #%d: %s **********" % (StepSeq, str(test_steps_data)), 1)

        # take screen-shot
        auto_generated_image_name = ('_').join(
            current_step_name.split(" ")) + '_started.png'
        CommonUtil.TakeScreenShot(str(auto_generated_image_name))

        # check if machine failed
        is_failed_result = ''
        if is_linked == 'yes':
            is_failed_result = check_if_other_machines_failed_in_linked_run()

        # check step result
        if is_failed_result in failed_tag_list or test_steps_data in failed_tag_list:
            sStepResult = "Failed"
        else:
            # run driver for step and get result
            sStepResult = call_driver_function_of_test_step(sModuleInfo, TestStepsList, StepSeq, step_time, driver_list,
                                                            current_step_name, final_dependency, final_run_params,
                                                            test_steps_data,
                                                            file_specific_steps, debug_actions)

        # get step end time
        sTestStepEndTime = datetime.fromtimestamp(
            time.time()).strftime('%Y-%m-%d %H:%M:%S')
        TestStepEndTime = time.time()

        WinMemEnd = CommonUtil.PhysicalAvailableMemory()  # get available memory

        # Time it took to run the test step
        TimeDiff = TestStepEndTime - TestStepStartTime

        # TimeInSec = TimeDiff.seconds
        TimeInSec = int(TimeDiff)
        TestStepDuration = CommonUtil.FormatSeconds(TimeInSec)

        TestStepMemConsumed = WinMemBegin - WinMemEnd  # get memory consumed

        # add result of each step to a list;
        # for a test case to pass all steps should pass;
        # at least one Failed makes it 'Fail' else 'Warning' or 'Blocked';

        # append step result
        if sStepResult:
            sTestStepResultList.append(sStepResult.upper())
        else:
            sTestStepResultList.append("FAILED")
            CommonUtil.ExecLog(
                sModuleInfo, "sStepResult : %s" % sStepResult, 1)  # add log
            sStepResult = "Failed"

        # step dictionary after execution
        after_execution_dict = {
            'stependtime': sTestStepEndTime,
            'end_memory': WinMemEnd,
            'duration': TestStepDuration,
            'memory_consumed': TestStepMemConsumed
        }

        # add/print logs for step result

        if sStepResult.upper() == PASSED_TAG.upper():
            # Step Passed
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Passed" % current_step_name, 1)
            after_execution_dict.update({'status': PASSED_TAG})

        elif sStepResult.upper() == SKIPPED_TAG.upper():
            # Step Passed
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Skipped" % current_step_name, 1)
            after_execution_dict.update({'status': SKIPPED_TAG})

        elif sStepResult.upper() == WARNING_TAG.upper():
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Warning" % current_step_name, 2)
            after_execution_dict.update({'status': WARNING_TAG})

            if not test_case_continue:
                already_failed = True
                StepSeq += 1
                continue

        elif sStepResult.upper() == NOT_RUN_TAG.upper():
            # Step has Warning, but continue running next test step for this test case
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Not Run" % current_step_name, 2)
            after_execution_dict.update({'status': NOT_RUN_TAG})

        elif sStepResult.upper() == FAILED_TAG.upper():

            # step failed, if linked test case notify other test cases via setting server variable named 'is_failed'
            global failed_due_to_linked_fail

            if is_linked == 'yes' and not failed_due_to_linked_fail:
                CommonUtil.ExecLog(sModuleInfo, str(
                    test_case) + " failed in linked run.. Notifying other linked machines", 3)

                # set server variables
                set_server_variable(run_id, 'is_failed', 'yes')
                set_server_variable(
                    run_id, 'failed_machine', (CommonUtil.MachineInfo().getLocalUser()).lower())
                set_server_variable(run_id, 'failed_test_case', str(test_case))

            # Step has a Critical failure, fail the test step and test case. go to next test case

            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Failed Failure" % current_step_name, 3)  # add log

            after_execution_dict.update({'status': FAILED_TAG})  # dictionary update

            # check if set for continue
            if not test_case_continue:

                # update step result
                update_test_step_results_on_server(run_id, test_case, current_step_id, current_step_sequence,
                                                   after_execution_dict)

                # get run id status
                run_cancelled = get_status_of_runid(run_id)
                if run_cancelled == 'Cancelled':
                    CommonUtil.ExecLog(sModuleInfo,
                                       "Test Run status is Cancelled. Exiting the current Test Case...%s" % test_case,
                                       2)  # add log
                already_failed = True
                StepSeq += 1
                continue

        elif sStepResult.upper() == BLOCKED_TAG.upper():
            # Step is Blocked, Block the test step and test case. go to next test case
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Blocked" % current_step_name, 3)
            after_execution_dict.update({'status': BLOCKED_TAG})

        elif sStepResult.upper() == CANCELLED_TAG.upper():
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Cancelled" % current_step_name, 3)
            after_execution_dict.update({'status': CANCELLED_TAG})
            cleanup_runid_from_server(run_id)
            return "pass"

        else:
            CommonUtil.ExecLog(
                sModuleInfo, "%s : Test Step Cancelled" % current_step_name, 3)
            after_execution_dict.update({'status': CANCELLED_TAG})
            cleanup_runid_from_server(run_id)
            return "pass"

        # update step results on server
        update_test_step_results_on_server(run_id, test_case, current_step_id, current_step_sequence,
                                           after_execution_dict)

        # get run id status
        run_cancelled = get_status_of_runid(run_id)
        if run_cancelled == 'Cancelled':
            CommonUtil.ExecLog(sModuleInfo,
                               "Test Run status is Cancelled. Exiting the current Test Case...%s" % test_case, 2)
            sTestStepResultList[len(sTestStepResultList)-1] = CANCELLED_TAG
            break
        StepSeq += 1

    return sTestStepResultList


# from the returned step results, it finds out the test case result
def calculate_test_case_result(sModuleInfo, TestCaseID, run_id, sTestStepResultList):
    if 'BLOCKED' in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Blocked", 3)
        sTestCaseStatus = "Blocked"
    elif 'CANCELLED' in sTestStepResultList or 'Cancelled' in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Cancelled", 3)
        sTestCaseStatus = "Cancelled"
    elif 'FAILED' in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Failed", 3)
        step_index = 1
        for each in sTestStepResultList:
            if each == 'FAILED':
                break
            else:
                step_index += 1

        status = check_if_step_is_verification_point(
            run_id, TestCaseID, step_index)

        if status:
            sTestCaseStatus = 'Failed'
        else:
            sTestCaseStatus = 'Blocked'
        CommonUtil.ExecLog(sModuleInfo, "Test Case " + sTestCaseStatus, 3)
    elif 'WARNING' in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Contain Warning(s)", 2)
        sTestCaseStatus = "Failed"
    elif 'NOT RUN' in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Contain Not Run Steps", 2)
        sTestCaseStatus = "Failed"
    elif 'SKIPPED' in sTestStepResultList:
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
    elif 'PASSED' in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Passed", 1)
        sTestCaseStatus = "Passed"
    else:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Status Unknown", 2)
        sTestCaseStatus = "Unknown"

    return sTestCaseStatus


# writes the log file for a test case
def write_log_file_for_test_case(sTestCaseStatus, test_case, run_id, sTestCaseEndTime, TestCaseDuration,
                                 temp_ini_file, send_log_file_only_for_fail=True):
    # upload the test case status before uploading log file, because there can be error while uploading log file, so we dont want to lose the important test case status
    test_case_after_dict = {
        'status': sTestCaseStatus,
        'testendtime': sTestCaseEndTime,
        'duration': TestCaseDuration
    }

    update_test_case_status_after_run_on_server(
        run_id, test_case, test_case_after_dict)

    # if settings checked, then send log file or screenshots, otherwise don't send
    if sTestCaseStatus not in passed_tag_list or (sTestCaseStatus in passed_tag_list and not send_log_file_only_for_fail):
        local_run_settings = ConfigModule.get_config_value(
            'RunDefinition', 'local_run')
        if local_run_settings == False or local_run_settings == 'False':
            # FL.RenameFile(ConfigModule.get_config_value('sectionOne','log_folder'), 'temp.log',TCID+'.log')
            TCLogFile = FL.ZipFolder(ConfigModule.get_config_value('sectionOne', 'test_case_folder', temp_ini_file),
                                     ConfigModule.get_config_value('sectionOne', 'test_case_folder',
                                                                   temp_ini_file) + ".zip")
            # Delete the folder
            FL.DeleteFolder(ConfigModule.get_config_value(
                'sectionOne', 'test_case_folder', temp_ini_file))

            # upload will go here.
            upload_zip(ConfigModule.get_config_value('Authentication', 'server_address'),
                       ConfigModule.get_config_value('Authentication', 'server_port'),
                       ConfigModule.get_config_value(
                           'sectionOne', 'temp_run_file_path', temp_ini_file), run_id,
                       ConfigModule.get_config_value(
                           'sectionOne', 'test_case', temp_ini_file) + ".zip",
                       ConfigModule.get_config_value('Advanced Options', '_file_upload_path'))
            TCLogFile = os.sep + ConfigModule.get_config_value('Advanced Options', '_file_upload_path') + os.sep + run_id.replace(":",
                                                                                                                      '-') + '/' + ConfigModule.get_config_value(
                'sectionOne', 'test_case', temp_ini_file) + '.zip'
            FL.DeleteFile(ConfigModule.get_config_value(
                'sectionOne', 'test_case_folder', temp_ini_file) + '.zip')
        else:
            TCLogFile = ''
        # upload the log file ID
        test_case_after_dict = {
            'logid': TCLogFile
        }

    update_test_case_status_after_run_on_server(
        run_id, test_case, test_case_after_dict)


# run a test case of a runid
def start_sending_log_to_server(run_id, temp_ini_file):
    local_run_settings = ConfigModule.get_config_value(
        'RunDefinition', 'local_run')
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
            if key == 'selenium_driver':
                value = 'Selenium Driver Instance'
            elif key == 'appium_driver':
                value = 'Appium Driver Instance'
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
            send_debug_data(run_id, "result-" +
                            debug_steps[i], sTestStepResultList[i])
    except:
        return True


def cleanup_driver_instances():  # cleans up driver(selenium, appium) instances
    try:  # if error happens. we don't care, main driver should not stop, pass in exception
        import Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions as Selenium
        import Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions as Appium
        if shared.Test_Shared_Variables('selenium_driver') not in failed_tag_list:
            driver = shared.Remove_From_Shared_Variables('selenium_driver')
            if driver not in failed_tag_list:
                Selenium.Tear_Down_Selenium()
        if shared.Test_Shared_Variables('appium_driver') not in failed_tag_list:
            driver = shared.Remove_From_Shared_Variables('appium_driver')
            if driver not in failed_tag_list:
                Appium.teardown_appium()

    except:
        pass


def run_test_case(TestCaseID, sModuleInfo, run_id, driver_list, final_dependency, final_run_params, temp_ini_file, is_linked, send_log_file_only_for_fail=True, performance=False, browserDriver=None):

    # set shared variables for run id
    shared.Set_Shared_Variables('run_id', run_id)

    # test case
    test_case = str(TestCaseID).replace('#', 'no')

    copy_status = False

    # add config value
    ConfigModule.add_config_value(
        'sectionOne', 'sTestStepExecLogId', "MainDriver", temp_ini_file)

    # add log
    CommonUtil.ExecLog(
        sModuleInfo, "Gathering data for test case %s" % (test_case), 4, False)

    retry = 1
    while not copy_status:
        if retry > 100:
            CommonUtil.ExecLog(
                sModuleInfo, "Failed to gather data for test case %s" % test_case, 3)
            return

        # check if test case is copied
        copy_status = check_if_test_case_is_copied(run_id, test_case)
        if copy_status:
            CommonUtil.ExecLog(
                sModuleInfo, "Gathering data for test case %s is completed" % test_case, 1)
            break

        time.sleep(3)
        retry += 1

    # download attachments for test case
    file_specific_steps = download_attachments_for_test_case(sModuleInfo, run_id, test_case,
                                                             temp_ini_file)  # downloads attachments

    # get test case details
    test_case_detail = get_test_case_details(run_id, test_case)
    TestCaseName = test_case_detail[0][1]

    # add log
    CommonUtil.ExecLog(
        sModuleInfo, "-------------*************--------------", 1)
    CommonUtil.ExecLog(sModuleInfo, "Running Test case id : %s :: %s" % (
        test_case, TestCaseName), 1)

    # get test case start time
    sTestCaseStartTime = datetime.fromtimestamp(
        time.time()).strftime('%Y-%m-%d %H:%M:%S')
    TestCaseStartTime = time.time()

    # update test case progress on server
    test_case_result_index = update_test_case_progress_on_server(
        run_id, test_case, sTestCaseStartTime)

    # get all steps of a test case
    TestStepsList = get_all_steps_of_a_test_case(run_id, test_case)

    Stepscount = len(TestStepsList)  # no. of steps

    # set parameters
    debug_steps = ''
    debug = False
    cleanup_drivers_during_debug = False
    debug_actions = ''

    # debug steps
    if str(run_id).startswith("debug"):
        debug_steps = get_debug_steps(run_id)  # get debug steps
        str_list = str(debug_steps).split("-")
        debug_steps = str_list[0]
        cleanup = str_list[1]

        try:
            debug_actions = str_list[2]
        except Exception as e:
            pass

        if cleanup == "YES":
            cleanup_drivers_during_debug = True

        debug_steps = str(debug_steps[1:-1]).split(",")
        if debug_actions:
            debug_actions = str(debug_actions[1:-1]).split(",")
        debug = True

    # if normal run, then write log file and cleanup driver instances
    if not debug or cleanup_drivers_during_debug:
        cleanup_driver_instances()

    # clean up shared variables
    if cleanup_drivers_during_debug:
        shared.Clean_Up_Shared_Variables()

    # set selenium driver shared variables for browser
    if performance and browserDriver:
        shared.Set_Shared_Variables('selenium_driver', browserDriver)

    # runs all test steps in the test case, all test step result is stored in the list named sTestStepResultList
    sTestStepResultList = run_all_test_steps_in_a_test_case(Stepscount, test_case, sModuleInfo, run_id, TestStepsList,
                                                            file_specific_steps, driver_list, final_dependency,
                                                            final_run_params, test_case_result_index, temp_ini_file,
                                                            debug, debug_steps, is_linked, performance, debug_actions)

    # get test case end time
    sTestCaseEndTime = datetime.fromtimestamp(
        time.time()).strftime('%Y-%m-%d %H:%M:%S')
    TestCaseEndTime = time.time()

    # Decide if Test Case Pass/Failed
    sTestCaseStatus = calculate_test_case_result(
        sModuleInfo, test_case, run_id, sTestStepResultList)

    # write locust file for performance testing
    if performance:
        locust_output_file_path = os.getcwd() + os.sep + 'Built_In_Automation' + os.sep + \
            'Performance_Testing' + os.sep + 'locustFileOutput.txt'
        file = open(locust_output_file_path, 'a+')
        file.write(sTestCaseStatus + "-" +
                   str(",".join(sTestStepResultList)) + '\n')
        file.close()

    # Time it took to run the test case
    TimeDiff = TestCaseEndTime - TestCaseStartTime
    TimeInSec = int(TimeDiff)
    TestCaseDuration = CommonUtil.FormatSeconds(TimeInSec)

    # Find Test case failed reason

    # Zip the folder
    # removing duplicates line from here.

    if debug:
        cleanup_runid_from_server(run_id)  # clean run id for debug

    if not debug:  # if normal run, then write log file and cleanup driver instances
        write_log_file_for_test_case(sTestCaseStatus, test_case, run_id, sTestCaseEndTime, TestCaseDuration,
                                     temp_ini_file, send_log_file_only_for_fail=send_log_file_only_for_fail)
        cleanup_driver_instances()  # clean up drivers
        shared.Clean_Up_Shared_Variables()  # clean up shared variables

    if debug:
        if cleanup_drivers_during_debug:
            cleanup_driver_instances()  # clean up drivers
            shared.Clean_Up_Shared_Variables()  # clean up shared variables

        # start sending logs/results to server
        start_sending_log_to_server(run_id, temp_ini_file)  # send logs
        start_sending_shared_var_to_server(run_id)  # send shared variables
        start_sending_step_result_to_server(
            run_id, debug_steps, sTestStepResultList)  # send step result
        send_debug_data(run_id, "finished", "yes")  # send debug data

    # Update test case result
    run_cancelled = RequestFormatter.Get(
        'get_status_of_a_run_api', {'run_id': run_id})  # check if run is cancelled
    if run_cancelled == 'Cancelled':  # add log
        CommonUtil.ExecLog(
            sModuleInfo, "Test Run status is Cancelled. Exiting the current Test Set...%s" % run_id, 2)
        return


def set_device_info_according_to_user_order(device_order, device_dict):
    for each in device_order:
        device_order_val = str(each[0])
        device_no_val = str(each[1])
        original_dict = device_dict
        device_info['device ' +
                    device_order_val] = original_dict['device ' + device_no_val]


def update_fail_reasons_of_test_cases(run_id, TestCaseID):
    try:
        for test_case in TestCaseID:
            try:
                FailReason = get_fail_reason_of_a_test_case(
                    run_id, test_case[0])
            except Exception:
                CommonUtil.Exception_Handler(sys.exc_info())
                FailReason = ""
            test_case_after_dict = {
                'failreason': FailReason
            }
            update_test_case_status_after_run_on_server(
                run_id, test_case[0], test_case_after_dict)
    except:
        pass


def get_performance_testing_data_for_test_case(run_id, TestCaseID):
    return RequestFormatter.Get('get_performance_testing_data_for_test_case_api', {'run_id': run_id, 'test_case': TestCaseID})


def write_locust_input_file(time_period, perf_data, TestCaseID, sModuleInfo, run_id, driver_list, final_dependency, final_run_params,
                            temp_ini_file, is_linked, send_log_file_only_for_fail):
    try:
        locust_input_file_path = os.getcwd() + os.sep + 'Built_In_Automation' + os.sep + \
            'Performance_Testing' + os.sep + 'locustFileInput.txt'
        file = open(locust_input_file_path, 'w')
        file.write(str(time_period) + '\n')
        file.write(str(TestCaseID)+'\n')
        file.write(str(sModuleInfo)+'\n')
        file.write(str(run_id)+'\n')
        file.write(str(driver_list)+'\n')
        file.write(str(final_dependency)+'\n')
        file.write(str(final_run_params)+'\n')
        file.write(str(temp_ini_file)+'\n')
        file.write(str(is_linked)+'\n')
        file.write(str(send_log_file_only_for_fail)+'\n')
        file.close()
    except:
        pass


def upload_csv_file_info(run_id, test_case):
    try:
        csv_result_input_file_path = os.getcwd() + os.sep + 'csvForZeuz_requests.csv'
        file = open(csv_result_input_file_path, 'r')
        file.readline()
        result_data = file.readline()
        file.close()
        test_case_result = []
        test_case_result_input_file_path = os.getcwd() + os.sep + 'Built_In_Automation' + \
            os.sep + 'Performance_Testing' + os.sep + 'locustFileOutput.txt'
        file = open(test_case_result_input_file_path, 'r')
        data = file.readline()
        while data:
            test_case_result.append(data.strip())
            data = file.readline()
        file.close()
        dict = {'run_id': run_id, 'test_case': test_case,
                'result_data': result_data, 'test_case_result': test_case_result}
        RequestFormatter.Get('send_performance_data_api', dict)
    except:
        pass


# main function
def main(device_dict):

    # get module info
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # add log
    CommonUtil.ExecLog(sModuleInfo, "MainDriver is starting", 4, False)

    # get temp file
    temp_ini_file = os.path.join(os.path.join(FL.get_home_folder(), os.path.join('Desktop',
                                                                                 os.path.join('AutomationLog',
                                                                                              ConfigModule.get_config_value(
                                                                                                  'Advanced Options', '_file')))))

    # add temp file to config values
    ConfigModule.add_config_value(
        'sectionOne', 'sTestStepExecLogId', sModuleInfo, temp_ini_file)

    # get local machine user id
    Userid = (CommonUtil.MachineInfo().getLocalUser()).lower()

    # get run definition config value
    send_log_file_only_for_fail = ConfigModule.get_config_value(
        'RunDefinition', 'upload_log_file_only_for_fail')

    # check whether to send log file only for fail
    if send_log_file_only_for_fail == "" or send_log_file_only_for_fail == None:
        send_log_file_only_for_fail = True
    elif send_log_file_only_for_fail.lower() == 'true':
        send_log_file_only_for_fail = True
    elif send_log_file_only_for_fail.lower() == 'false':
        send_log_file_only_for_fail = False
    else:
        send_log_file_only_for_fail = True

    # check user permission to run test
    user_permission = check_user_permission_to_run_test(sModuleInfo, Userid)
    if user_permission not in passed_tag_list:
        return user_permission

    # get drivers list
    driver_list = get_all_drivers_list()

    # get all run ids
    TestRunLists = get_all_run_ids(Userid, sModuleInfo)

    # get device order
    device_order = get_device_order(Userid)

    # set device info according to user order
    set_device_info_according_to_user_order(device_order, device_dict)

    # add log
    if len(TestRunLists) > 0:
        CommonUtil.ExecLog(sModuleInfo, "Running Test cases from Test Set : %s" %
                           TestRunLists[0:len(TestRunLists)], 1)
    else:
        CommonUtil.ExecLog(
            sModuleInfo, "No Test Run Schedule found for the current user : %s" % Userid, 2)
        return False

    # for each test runid loop continues
    for TestRunID in TestRunLists:

        # clear all logs
        CommonUtil.clear_all_logs()

        # get run info
        project_id = TestRunID[3]
        team_id = int(TestRunID[4])
        try:
            is_linked = TestRunID[5]
        except:
            is_linked = ''
        run_description = (TestRunID[1].replace(
            "run_dependency", '')).replace('dependency_filter', '')
        run_id = TestRunID[0]

        # save run id in shared variable

        final_dependency = get_all_dependencies(
            project_id, team_id, run_description)  # get dependencies

        final_run_params_from_server = get_all_runtime_parameters(
            run_id)  # get runtime params

        final_run_params = {}
        for dict in final_run_params_from_server:
            final_run_params[str(dict['field'])] = str(dict['value'])

        update_run_id_info_on_server(run_id)  # update runid status

        TestSetStartTime = time.time()  # test start time

        TestCaseLists = get_all_automated_test_cases_in_run_id(
            run_id, Userid)  # get all automated test cases of a runid

        # get all remote config
        rem_config = get_all_remote_config(run_id)
        ConfigModule.remote_config = rem_config

        # add log
        if len(TestCaseLists) > 0:
            CommonUtil.ExecLog(sModuleInfo, "Running Test cases from list : %s" % TestCaseLists[0:len(TestCaseLists)],
                               1)
            CommonUtil.ExecLog(
                sModuleInfo, "Total number of test cases %s" % len(TestCaseLists), 4, False)
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "No test cases found for the current user : %s" % Userid, 2)
            return False

        # run each test case in the runid
        for TestCaseID in TestCaseLists:

            # check if performance test case

            performance_test_case = False
            if str(TestCaseID[1]).lower() == 'performance':
                performance_test_case = True

            if performance_test_case:

                # get performance test info
                perf_data = get_performance_testing_data_for_test_case(
                    run_id, TestCaseID[0])
                hatch_rate = perf_data['hatch_rate']
                no_of_users = perf_data['no_of_users']
                time_period = perf_data['time_period']

                # write locust input file

                write_locust_input_file(time_period, perf_data, TestCaseID[0], sModuleInfo, run_id, driver_list, final_dependency, final_run_params,
                                        temp_ini_file, is_linked, send_log_file_only_for_fail=send_log_file_only_for_fail)

                # check locust file name
                locustFile = 'chromeLocustFile.py'
                if 'Browser' in final_dependency:
                    if final_dependency['Browser'].lower() == 'chrome':
                        locustFile = 'chromeLocustFile.py'
                    else:
                        locustFile = 'firefoxLocustFile.py'
                else:
                    locustFile = 'restLocustFile.py'

                # get locust file path
                locust_file_path = os.getcwd() + os.sep + 'Built_In_Automation' + os.sep + \
                    'Performance_Testing' + os.sep + locustFile

                # make locust query
                locustQuery = "locust -f %s --csv=csvForZeuz --no-web --host=http://example.com -c %d -r %d" % (
                    locust_file_path, no_of_users, hatch_rate)

                # add log
                CommonUtil.ExecLog(sModuleInfo, "Running Performance Test Case %s with total %d users, in a rate %s new users/second and each user will run for %s seconds" %
                                   (TestCaseID[0], no_of_users, hatch_rate, time_period), 1)

                try:
                    def kill(process): return process.kill()  # kill process function
                    process = subprocess.Popen(locustQuery, shell=True)  # locust query process
                    my_timer = Timer(no_of_users*time_period, kill, [process])  # set timer

                    try:
                        my_timer.start()  # start timer
                        stdout, stderr = process.communicate()  # process communicate
                    finally:
                        my_timer.cancel()  # cancel timer
                except Exception as e:
                    print("exception")
                    pass

                # add log
                CommonUtil.ExecLog(
                    sModuleInfo, "Uploading Performance Test Results", 1)

                # upload info
                upload_csv_file_info(run_id, TestCaseID[0])

                # add log
                CommonUtil.ExecLog(
                    sModuleInfo, "Performance Test Results Uploaded Successfully", 1)

            else:

                # run test case (not performance)
                run_test_case(TestCaseID[0], sModuleInfo, run_id, driver_list, final_dependency, final_run_params,
                              temp_ini_file, is_linked, send_log_file_only_for_fail=send_log_file_only_for_fail)

                all_logs_list = CommonUtil.get_all_logs()  # get all logs
                write_all_logs_to_server(all_logs_list)  # write logs to server
                CommonUtil.clear_all_logs()  # clear logs

        # calculate elapsed time of runid
        sTestSetEndTime = datetime.fromtimestamp(
            time.time()).strftime('%Y-%m-%d %H:%M:%S')
        TestSetEndTime = time.time()
        TimeDiff = TestSetEndTime - TestSetStartTime
        TimeInSec = int(TimeDiff)
        TestSetDuration = CommonUtil.FormatSeconds(TimeInSec)

        run_cancelled = get_status_of_runid(
            run_id)  # check if run is cancelled

        if run_cancelled == 'Cancelled':
            CommonUtil.ExecLog(
                sModuleInfo, "Test Set Cancelled by the User", 1)  # add log
        else:
            # update runid status on server
            update_test_case_result_on_server(
                run_id, sTestSetEndTime, TestSetDuration)

        # add config value
        ConfigModule.add_config_value(
            'sectionOne', 'sTestStepExecLogId', "MainDriver", temp_ini_file)

        # add log
        CommonUtil.ExecLog(sModuleInfo, "Test Set Completed", 4, False)

        # send email report
        send_email_report_after_exectution(run_id, project_id, team_id)

        # update fail reasons
        update_fail_reasons_of_test_cases(run_id, TestCaseLists)

        # for testing, will be done for only main TC in linked test cases
        # delete_all_server_variable(run_id)

    return "pass"


if __name__ == '__main__':
    main()
