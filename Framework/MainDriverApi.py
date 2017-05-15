# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import inspect,os,time,sys,urllib2,Queue,importlib,requests,threading
from datetime import datetime
from Utilities import ConfigModule,FileUtilities as FL,CommonUtil,RequestFormatter
top_path=os.path.dirname(os.getcwd())
drivers_path=os.path.join(top_path,'Drivers')
sys.path.append(drivers_path)
import Drivers
'''Constants'''
PROGRESS_TAG = 'In-Progress'
PASSED_TAG='Passed'
WARNING_TAG='Warning'
FAILED_TAG='Failed'
NOT_RUN_TAG='Not Run'
BLOCKED_TAG='Blocked'
CANCELLED_TAG='Cancelled'
COMPLETE_TAG='Complete'
passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True','1','Success','success','SUCCESS']
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE','0']


#returns all drivers
def get_all_drivers_list():
    return RequestFormatter.Get('get_all_drivers_api')


#returns all runids assigned to a machine
def get_all_run_ids(Userid):
    return RequestFormatter.Get('get_all_submitted_run_of_a_machine_api',{'machine_name':Userid})


#returns all dependencies of test cases of a run id
def get_all_dependencies(project_id,team_id,run_description):
    dependency_list = RequestFormatter.Get('get_all_dependency_based_on_project_and_team_api',{'project_id': project_id, 'team_id': team_id})
    final_dependency = get_final_dependency_list(dependency_list, run_description)
    return final_dependency


#returns all runtime parameters of test cases of a run id
def get_all_runtime_parameters(run_id):
    run_params_list = RequestFormatter.Get('get_all_run_parameters_based_on_project_and_team_api', {'run_id': run_id})
    final_run_params = get_run_params_list(run_params_list)
    return final_run_params


#updates current runid status on server database
def update_run_id_info_on_server(run_id):
    RequestFormatter.Get('update_machine_info_based_on_run_id_api',{'run_id': run_id, 'options': {'status': PROGRESS_TAG}})
    sTestSetStartTime = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    RequestFormatter.Get('update_test_env_results_based_on_run_id_api', {'options': {'status': PROGRESS_TAG, 'teststarttime': str(sTestSetStartTime)}, 'run_id': run_id})


#returns all automated test cases of a runid
def get_all_automated_test_cases_in_run_id(run_id):
    TestCaseLists = RequestFormatter.Get('get_all_automated_test_cases_based_on_run_id_api', {'run_id': run_id})
    return TestCaseLists


#checks if a step of a test case is the verification point of that test case
def check_if_step_is_verification_point(run_id, datasetid):
    return RequestFormatter.Get('if_failed_at_verification_point_api', {'run_id': run_id, 'data_id': datasetid})


#if run is cancelled then it can be called, it cleans up the runid from database
def cleanup_runid_from_server(run_id):
    RequestFormatter.Get('clean_up_run_api', {'run_id': run_id})


#checks if this test case is a copy of another test case
def check_if_test_case_is_copied(run_id, test_case):
    return RequestFormatter.Get('is_test_case_copied_api', {'run_id': run_id, 'test_case': test_case})


#returns test case details needed to run the test case
def get_test_case_details(run_id, test_case):
    return RequestFormatter.Get('get_test_case_detail_api', {'run_id': run_id, 'test_case': test_case})


#updates current test case status on server database
def update_test_case_progress_on_server(run_id, test_case, sTestCaseStartTime):
    return RequestFormatter.Get('test_case_results_update_returns_index_api',{'run_id': run_id, 'test_case': test_case,'options': {'status': PROGRESS_TAG,'teststarttime': sTestCaseStartTime}})


#returns all steps of a test case
def get_all_steps_of_a_test_case(run_id, test_case):
    return RequestFormatter.Get('test_step_fetch_for_test_case_run_id_api',{'run_id': run_id, 'test_case': test_case})


#returns test step details needed to run the test step
def get_step_meta_data_of_a_step(run_id, test_case, StepSeq):
    return RequestFormatter.Get('get_step_meta_data_api',{'run_id': run_id, 'test_case': test_case, 'step_seq': StepSeq})


#if a test case is failed it returns the fail reason
def get_fail_reason_of_a_test_case(run_id, test_case):
    return RequestFormatter.Get('get_failed_reason_test_case_api', {'run_id': run_id, 'test_case': test_case})


#updates current test case status on server database after the test case is run
def update_test_case_status_after_run_on_server(run_id, test_case, test_case_after_dict):
    RequestFormatter.Get('test_case_results_update_returns_index_api',{'run_id': run_id, 'test_case': test_case,'options': test_case_after_dict})


#returns current status of the runid
def get_status_of_runid(run_id):
    return RequestFormatter.Get('get_status_of_a_run_api', {'run_id': run_id})


#updates current test step status on server database
def update_test_step_status(run_id, test_case, current_step_id, current_step_sequence, Dict):
    RequestFormatter.Get('test_step_results_update_returns_index_api',
                         {'run_id': run_id, 'tc_id': test_case, 'step_id': current_step_id,
                          'test_step_sequence': current_step_sequence, 'options': Dict})


#updates current test case result(like pass/fail etc.) on server database
def update_test_case_result_on_server(run_id, sTestSetEndTime, TestSetDuration):
    RequestFormatter.Get('update_test_env_results_based_on_run_id_api', {'options': {'status': COMPLETE_TAG, 'testendtime': sTestSetEndTime, 'duration': TestSetDuration}, 'run_id': run_id})
    RequestFormatter.Get('update_machine_info_based_on_run_id_api', {'run_id': run_id,'options': {'status': COMPLETE_TAG, 'email_flag': True}})


#returns step data of a test step in a test case
def get_test_step_data(run_id, test_case, current_step_sequence, StepSeq):
    return RequestFormatter.Get('get_test_step_data_based_on_test_case_run_id_api',
                         {'run_id': run_id, 'test_case': test_case,
                          'step_sequence': current_step_sequence, 'step_iteration': StepSeq})


#updates current test step result(like pass/fail etc.) on server database
def update_test_step_results_on_server(run_id, test_case, current_step_id, current_step_sequence, after_execution_dict):
    RequestFormatter.Get('test_step_results_update_returns_index_api',
                         {'run_id': run_id, 'tc_id': test_case, 'step_id': current_step_id,
                          'test_step_sequence': current_step_sequence,
                          'options': after_execution_dict})


#checks if the user has permission to run test or not
def check_user_permission_to_run_test(sModuleInfo, Userid):
    r =  RequestFormatter.Get('get_valid_machine_name_api',{'machine_name':Userid})
    if not r:
        CommonUtil.ExecLog(sModuleInfo, "User don't have permission to run the tests", 3)
        return "You Don't Have Permission"
    else:
        return "passed"


#gets run time parameters
def get_run_params_list(run_params):
    run_para=[]
    for each in run_params:
        m_ = {}
        m_.update({'field': each[0]})
        m_.update({'name': each[1]})
        m_.update({'value': each[2]})
        run_para.append(m_)
    return run_para


#check if a test step has 'continue on fail' feature or not
def check_continue_on_fail_value_of_a_step(step_meta_data):
    continue_value = filter(lambda x: x[0] == 'continue' and x[1] == 'point', step_meta_data)
    if continue_value:
        if continue_value[0][2] == 'yes':
            test_case_continue = True
        else:
            test_case_continue = False
    else:
        test_case_continue = False

    return test_case_continue


#uploads zip file to server
def upload_zip(server_id,port_id,temp_folder,run_id,file_name,base_path=False):
    """
    :param server_id: the location of the server
    :param port_id: the port it will listen on
    :param temp_folder: the logfiles folder
    :param run_id: respective run_id
    :param file_name: zipfile name for the run
    :param base_path: base_path for file save
    :return:
    """
    url_link='http://'+server_id+':'+str(port_id)+"/Home/UploadZip/"
    total_file_path=temp_folder+os.sep+run_id.replace(':','-')+os.sep+file_name
    fileObj=open(total_file_path,'rb')
    file_list={'docfile':fileObj}
    data_list={'run_id':run_id,'file_name':file_name,'base_path':base_path}
    r=requests.post(url_link,files=file_list,data=data_list)
    if r.status_code==200:
        print "Zip File is uploaded to production successfully"
    else:
        print "Zip File is not uploaded to production successfully"


#returns dependency list
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


#downloads attachments for a test step
def download_attachments_for_test_case(sModuleInfo, run_id, test_case, temp_ini_file):
    CommonUtil.ExecLog(sModuleInfo, "-------------*************--------------", 1)
    CommonUtil.ExecLog(sModuleInfo, "Creating Built_In_Automation Log for test case: %s" % test_case, 1)
    try:
        log_file_path = ConfigModule.get_config_value('sectionOne', 'temp_run_file_path', temp_ini_file)
    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())

    test_case_folder = log_file_path + os.sep + (run_id.replace(':', '-') + os.sep + test_case.replace(":", '-'))
    ConfigModule.add_config_value('sectionOne', 'test_case', test_case, temp_ini_file)
    ConfigModule.add_config_value('sectionOne', 'test_case_folder', test_case_folder, temp_ini_file)
    log_folder = test_case_folder + os.sep + 'Log'
    ConfigModule.add_config_value('sectionOne', 'log_folder', log_folder, temp_ini_file)
    screenshot_folder = test_case_folder + os.sep + 'screenshots'
    ConfigModule.add_config_value('sectionOne', 'screen_capture_folder', screenshot_folder, temp_ini_file)

    home = os.path.join(FL.get_home_folder(), os.path.join('Desktop', 'Attachments'))
    ConfigModule.add_config_value('sectionOne', 'download_folder', home, temp_ini_file)

    # create_test_case_folder
    test_case_folder = ConfigModule.get_config_value('sectionOne', 'test_case_folder', temp_ini_file)
    FL.CreateFolder(test_case_folder)

    # FL.CreateFolder(Global.TCLogFolder + os.sep + "ProductLog")
    log_folder = ConfigModule.get_config_value('sectionOne', 'log_folder', temp_ini_file)
    FL.CreateFolder(log_folder)

    # FL.CreateFolder(Global.TCLogFolder + os.sep + "Screenshots")
    # creating ScreenShot File
    screen_capture_folder = ConfigModule.get_config_value('sectionOne', 'screen_capture_folder', temp_ini_file)
    FL.CreateFolder(screen_capture_folder)

    # creating the download folder
    download_folder = ConfigModule.get_config_value('sectionOne', 'download_folder', temp_ini_file)

    # test case attachements
    test_case_attachments = RequestFormatter.Get('get_test_case_attachments_api',
                                                 {'run_id': run_id, 'test_case': test_case})
    test_step_attachments = RequestFormatter.Get('get_test_step_attachments_for_test_case_api',
                                                 {'run_id': run_id, 'test_case': test_case})
    FL.DeleteFolder(ConfigModule.get_config_value('sectionOne', 'download_folder', temp_ini_file))
    FL.CreateFolder(download_folder)
    file_specific_steps = {}
    for each in test_case_attachments:
        CommonUtil.ExecLog(sModuleInfo, "Attachment download for test case %s started" % test_case, 1)
        m = each[1] + '.' + each[2]  # file name
        f = open(download_folder + '/' + m, 'wb')
        f.write(urllib2.urlopen('http://' + ConfigModule.get_config_value('Server', 'server_address') + ':' + str(
            ConfigModule.get_config_value('Server', 'server_port')) + '/static' + each[0]).read())
        file_specific_steps.update({m: download_folder + '/' + m})
        f.close()
    if test_case_attachments:
        CommonUtil.ExecLog(sModuleInfo, "Attachment download for test case %s finished" % test_case, 1)
    for each in test_step_attachments:
        CommonUtil.ExecLog(sModuleInfo, "Attachment download for steps in test case %s started" % test_case, 1)
        m = each[1] + '.' + each[2]  # file name
        if not os.path.exists(download_folder + '/' + str(each[3])):
            FL.CreateFolder(download_folder + '/' + str(each[3]))
        f = open(download_folder + '/' + str(each[3]) + '/' + m, 'wb')
        f.write(urllib2.urlopen('http://' + ConfigModule.get_config_value('Server', 'server_address') + ':' + str(
            ConfigModule.get_config_value('Server', 'server_port')) + '/static' + each[0]).read())
        file_specific_steps.update({m: download_folder + '/' + str(each[3]) + '/' + m})
        f.close()
    if test_step_attachments:
        CommonUtil.ExecLog(sModuleInfo, "Attachment download for steps in test case %s finished" % test_case, 1)


    return file_specific_steps


#call the function of a test step that is in its driver file
def call_driver_function_of_test_step(sModuleInfo, TestStepsList, StepSeq, step_time, driver_list, current_step_name, final_dependency, final_run_params, test_steps_data, file_specific_steps):
    try:
        q = Queue.Queue()
        if TestStepsList[StepSeq - 1][8] != None:
            current_driver = TestStepsList[StepSeq - 1][8]
        else:
            current_driver = TestStepsList[StepSeq - 1][3]
        if current_driver in driver_list:
            try:
                module_name = importlib.import_module(current_driver)
                if TestStepsList[StepSeq - 1][8] != None:
                    step_name = (TestStepsList[StepSeq - 1][7]).strip()
                else:
                    step_name = current_step_name
                step_name = step_name.lower().replace(' ', '_')
                try:
                    # importing functions from driver
                    functionTocall = getattr(module_name, step_name)
                    simple_queue = Queue.Queue()

                    if ConfigModule.get_config_value('RunDefinition', 'Threading') in passed_tag_list:
                        stepThread = threading.Thread(target=functionTocall, args=(
                            final_dependency, final_run_params, test_steps_data, file_specific_steps, simple_queue))
                        CommonUtil.ExecLog(sModuleInfo, "Starting Test Step Thread..", 1)
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
                            CommonUtil.ExecLog(sModuleInfo, "Test Step Thread Ended..", 1)
                        except Queue.Empty:
                            # Global.DefaultTestStepTimeout
                            ErrorMessage = "Test Step didn't return after %d seconds" % step_time
                            CommonUtil.Exception_Handler(sys.exc_info())
                            sStepResult = "Failed"
                            q.put(sStepResult)
                            # Clean up
                            if stepThread.isAlive():
                                CommonUtil.ExecLog(sModuleInfo, "Timeout Error", 3)
                                # stepThread.__stop()
                                try:
                                    stepThread._Thread__stop()
                                    while stepThread.isAlive():
                                        time.sleep(1)
                                        CommonUtil.ExecLog(sModuleInfo, "Thread is still alive", 3)
                                        print
                                except:
                                    CommonUtil.Exception_Handler(sys.exc_info())
                    else:
                        sStepResult = functionTocall(final_dependency, final_run_params, test_steps_data,
                                                     file_specific_steps, simple_queue)
                except:
                    CommonUtil.Exception_Handler(sys.exc_info())
                    sStepResult = "Failed"

                if sStepResult in passed_tag_list:
                    sStepResult = 'PASSED'
                elif sStepResult in failed_tag_list:
                    sStepResult = 'FAILED'
                else:
                    CommonUtil.ExecLog(sModuleInfo, "sStepResult not an acceptable type", 3)
                    CommonUtil.ExecLog(sModuleInfo, "Acceptable pass string(s): %s" % (passed_tag_list), 3)
                    CommonUtil.ExecLog(sModuleInfo, "Acceptable fail string(s): %s" % (failed_tag_list), 3)
                    sStepResult = "FAILED"
                q.put(sStepResult)
            except Exception:
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


#runs all test steps of a test case
def run_all_test_steps_in_a_test_case(Stepscount, test_case, sModuleInfo, run_id, TestStepsList, file_specific_steps, driver_list, final_dependency, final_run_params, test_case_result_index, temp_ini_file):
    StepSeq = 1
    sTestStepResultList = []
    already_failed = False
    while StepSeq <= Stepscount:
        if already_failed == True:
            always_run = TestStepsList[StepSeq - 1][9]
            if always_run != True:
                StepSeq += 1
                continue
        current_step_name = TestStepsList[StepSeq - 1][1]
        current_step_id = TestStepsList[StepSeq - 1][0]
        current_step_sequence = TestStepsList[StepSeq - 1][2]
        CommonUtil.ExecLog(sModuleInfo, "Step : %s" % current_step_name, 1)
        step_meta_data = get_step_meta_data_of_a_step(run_id, test_case, StepSeq)

        test_case_continue = check_continue_on_fail_value_of_a_step(step_meta_data)

        ConfigModule.add_config_value('sectionOne', 'sTestStepExecLogId',
                                      run_id + "|" + test_case + "|" + str(current_step_id) + "|" + str(StepSeq),
                                      temp_ini_file)
        sTestStepStartTime = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        TestStepStartTime = time.time()
        WinMemBegin = CommonUtil.PhysicalAvailableMemory()
        Dict = {
            'teststepsequence': current_step_sequence,
            'status': PROGRESS_TAG,
            'stepstarttime': sTestStepStartTime,
            'logid': ConfigModule.get_config_value('sectionOne', 'sTestStepExecLogId', temp_ini_file),
            'start_memory': WinMemBegin,
            'testcaseresulttindex': test_case_result_index
        }

        update_test_step_status(run_id, test_case, current_step_id, current_step_sequence, Dict)

        test_steps_data = get_test_step_data(run_id, test_case, current_step_sequence, StepSeq)

        CommonUtil.ExecLog(sModuleInfo, "steps data for Step #%d: %s" % (StepSeq, str(test_steps_data)), 1)
        step_time = filter(lambda x: x[0] == 'estimated' and x[1] == 'time', step_meta_data)
        if step_time:
            step_time = int(step_time[0][2])
        else:
            step_time = 0
        auto_generated_image_name = ('_').join(current_step_name.split(" ")) + '_started.png'
        CommonUtil.TakeScreenShot(str(auto_generated_image_name))

        sStepResult = call_driver_function_of_test_step(sModuleInfo, TestStepsList, StepSeq, step_time, driver_list,
                                          current_step_name, final_dependency, final_run_params, test_steps_data,
                                          file_specific_steps)

        sTestStepEndTime = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        TestStepEndTime = time.time()
        WinMemEnd = CommonUtil.PhysicalAvailableMemory()
        # Time it took to run the test step
        TimeDiff = TestStepEndTime - TestStepStartTime
        # TimeInSec = TimeDiff.seconds
        TimeInSec = int(TimeDiff)
        TestStepDuration = CommonUtil.FormatSeconds(TimeInSec)
        TestStepMemConsumed = WinMemBegin - WinMemEnd
        # add result of each step to a list; for a test case to pass all steps should be pass; atleast one Failed makes it 'Fail' else 'Warning' or 'Blocked'
        if sStepResult:
            sTestStepResultList.append(sStepResult.upper())
        else:
            sTestStepResultList.append("FAILED")
            print "sStepResult : ", sStepResult
            CommonUtil.ExecLog(sModuleInfo, "sStepResult : %s" % sStepResult, 1)
            sStepResult = "Failed"
        after_execution_dict = {
            'stependtime': sTestStepEndTime,
            'end_memory': WinMemEnd,
            'duration': TestStepDuration,
            'memory_consumed': TestStepMemConsumed
        }

        if sStepResult.upper() == PASSED_TAG.upper():
            # Step Passed
            CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Passed" % current_step_name, 1)
            after_execution_dict.update({'status': PASSED_TAG})
        elif sStepResult.upper() == WARNING_TAG.upper():
            CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Warning" % current_step_name, 2)
            after_execution_dict.update({'status': WARNING_TAG})
            if not test_case_continue:
                already_failed = True
                StepSeq += 1
                continue
        elif sStepResult.upper() == NOT_RUN_TAG.upper():
            # Step has Warning, but continue running next test step for this test case
            CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Not Run" % current_step_name, 2)
            after_execution_dict.update({'status': NOT_RUN_TAG})
        elif sStepResult.upper() == FAILED_TAG.upper():
            # Step has a Critial failure, fail the test step and test case. go to next test case
            CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Failed Failure" % current_step_name, 3)
            after_execution_dict.update({'status': FAILED_TAG})
            if not test_case_continue:
                update_test_step_results_on_server(run_id, test_case, current_step_id, current_step_sequence, after_execution_dict)
                run_cancelled = get_status_of_runid(run_id)
                if run_cancelled == 'Cancelled':
                    CommonUtil.ExecLog(sModuleInfo,
                                       "Test Run status is Cancelled. Exiting the current Test Case...%s" % test_case,
                                       2)
                already_failed = True
                StepSeq += 1
                continue
        elif sStepResult.upper() == BLOCKED_TAG.upper():
            # Step is Blocked, Block the test step and test case. go to next test case
            CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Blocked" % current_step_name, 3)
            after_execution_dict.update({'status': BLOCKED_TAG})
        elif sStepResult.upper() == CANCELLED_TAG.upper():
            print current_step_name + ": Test Step Cancelled"
            CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Cancelled" % current_step_name, 3)
            after_execution_dict.update({'status': CANCELLED_TAG})
            cleanup_runid_from_server(run_id)
            return "pass"
        else:
            print current_step_name + ": Test Step Cancelled"
            CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Cancelled" % current_step_name, 3)
            after_execution_dict.update({'status': CANCELLED_TAG})
            cleanup_runid_from_server(run_id)
            return "pass"

        update_test_step_results_on_server(run_id, test_case, current_step_id, current_step_sequence, after_execution_dict)
        run_cancelled = get_status_of_runid(run_id)
        if run_cancelled == 'Cancelled':
            CommonUtil.ExecLog(sModuleInfo,
                               "Test Run status is Cancelled. Exiting the current Test Case...%s" % test_case, 2)
            break
        StepSeq+=1

    return sTestStepResultList


#from the returned step results, it finds out the test case result
def calculate_test_case_result(sModuleInfo, TestCaseID, run_id, sTestStepResultList):
    if 'BLOCKED' in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Blocked", 3)
        sTestCaseStatus = "Blocked"
    elif 'FAILED' in sTestStepResultList:
        CommonUtil.ExecLog(sModuleInfo, "Test Case Failed", 3)
        step_index = 1
        for each in sTestStepResultList:
            if each == 'FAILED':
                break
            else:
                step_index += 1
        datasetid = TestCaseID[0] + '_s' + str(step_index)
        status = 11
        if status:
            sTestCaseStatus = 'Failed'
        else:
            sTestCaseStatus = 'Blocked'
        CommonUtil.ExecLog(sModuleInfo, "Test Case " + sTestCaseStatus, 3)
    elif 'WARNING' in sTestStepResultList:
        print "Test Case Contain Warning(s)"
        CommonUtil.ExecLog(sModuleInfo, "Test Case Contain Warning(s)", 2)
        sTestCaseStatus = "Failed"
    elif 'NOT RUN' in sTestStepResultList:
        print "Test Case Contain Not Run Steps"
        CommonUtil.ExecLog(sModuleInfo, "Test Case Contain Warning(s)", 2)
        sTestCaseStatus = "Failed"
    elif 'PASSED' in sTestStepResultList:
        print "Test Case Passed"
        CommonUtil.ExecLog(sModuleInfo, "Test Case Passed", 1)
        sTestCaseStatus = "Passed"
    else:
        print "Test Case Status Unknown"
        CommonUtil.ExecLog(sModuleInfo, "Test Case Status Unknown", 2)
        sTestCaseStatus = "Unknown"

    return sTestCaseStatus


#writes the log file for a test case
def write_log_file_for_test_case(sTestCaseStatus, test_case, run_id, sTestCaseEndTime, TestCaseDuration, FailReason, temp_ini_file):
    local_run_settings = ConfigModule.get_config_value('RunDefinition', 'local_run')
    if local_run_settings == False or local_run_settings == 'False':
        current_log_file = os.path.join(ConfigModule.get_config_value('sectionOne', 'log_folder', temp_ini_file),
                                        'temp.log')
        temp_log_file = os.path.join(ConfigModule.get_config_value('sectionOne', 'log_folder', temp_ini_file),
                                     test_case + '.log')
        lines_seen = set()
        outfile = open(temp_log_file, 'w')
        for line in open(current_log_file, 'r'):
            if line not in lines_seen:
                outfile.write(line)
                lines_seen.add(line)
        outfile.close()
        FL.DeleteFile(current_log_file)
        # FL.RenameFile(ConfigModule.get_config_value('sectionOne','log_folder'), 'temp.log',TCID+'.log')
        TCLogFile = FL.ZipFolder(ConfigModule.get_config_value('sectionOne', 'test_case_folder', temp_ini_file),
                                 ConfigModule.get_config_value('sectionOne', 'test_case_folder',
                                                               temp_ini_file) + ".zip")
        # Delete the folder
        FL.DeleteFolder(ConfigModule.get_config_value('sectionOne', 'test_case_folder', temp_ini_file))

        # upload will go here.
        upload_zip(ConfigModule.get_config_value('Server', 'server_address'),
                   ConfigModule.get_config_value('Server', 'server_port'),
                   ConfigModule.get_config_value('sectionOne', 'temp_run_file_path', temp_ini_file), run_id,
                   ConfigModule.get_config_value('sectionOne', 'test_case', temp_ini_file) + ".zip",
                   ConfigModule.get_config_value('Temp', '_file_upload_path'))
        TCLogFile = os.sep + ConfigModule.get_config_value('Temp', '_file_upload_path') + os.sep + run_id.replace(":",
                                                                                                                  '-') + '/' + ConfigModule.get_config_value(
            'sectionOne', 'test_case', temp_ini_file) + '.zip'
        FL.DeleteFile(ConfigModule.get_config_value('sectionOne', 'test_case_folder', temp_ini_file) + '.zip')
    else:
        TCLogFile = ''

    test_case_after_dict = {
        'status': sTestCaseStatus,
        'testendtime': sTestCaseEndTime,
        'duration': TestCaseDuration,
        'failreason': FailReason,
        'logid': TCLogFile
    }

    update_test_case_status_after_run_on_server(run_id, test_case, test_case_after_dict)


#run a test case of a runid
def run_test_case(TestCaseID, sModuleInfo, run_id, driver_list, final_dependency, final_run_params, temp_ini_file):
    test_case = TestCaseID[0]
    copy_status = False
    print "Gathering data for test case %s" % (test_case)
    while not copy_status:
        copy_status = check_if_test_case_is_copied(run_id, test_case)
        if copy_status:
            CommonUtil.ExecLog(sModuleInfo, "Gathering data for test case %s is completed" % (test_case), 1)

    ConfigModule.add_config_value('sectionOne', 'sTestStepExecLogId', "MainDriver", temp_ini_file)

    file_specific_steps = download_attachments_for_test_case(sModuleInfo, run_id, test_case, temp_ini_file) #downloads attachments

    test_case_detail = get_test_case_details(run_id, test_case)
    TestCaseName = test_case_detail[0][1]
    CommonUtil.ExecLog(sModuleInfo, "-------------*************--------------", 1)
    CommonUtil.ExecLog(sModuleInfo, "Running Test case id : %s :: %s" % (test_case, TestCaseName), 1)

    sTestCaseStartTime = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    TestCaseStartTime = time.time()
    test_case_result_index = update_test_case_progress_on_server(run_id, test_case, sTestCaseStartTime)
    TestStepsList = get_all_steps_of_a_test_case(run_id, test_case)
    Stepscount = len(TestStepsList)

    #runs all test steps in the test case, all test step result is stored in the list named sTestStepResultList
    sTestStepResultList = run_all_test_steps_in_a_test_case(Stepscount, test_case, sModuleInfo, run_id, TestStepsList, file_specific_steps, driver_list, final_dependency, final_run_params, test_case_result_index, temp_ini_file)

    sTestCaseEndTime = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    TestCaseEndTime = time.time()
    # Decide if Test Case Pass/Failed
    sTestCaseStatus = calculate_test_case_result(sModuleInfo, TestCaseID, run_id, sTestStepResultList)

    # Time it took to run the test case
    TimeDiff = TestCaseEndTime - TestCaseStartTime
    TimeInSec = int(TimeDiff)
    TestCaseDuration = CommonUtil.FormatSeconds(TimeInSec)

    # Find Test case failed reason
    try:
        FailReason = get_fail_reason_of_a_test_case(run_id, test_case)
    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        FailReason = ""

    # Zip the folder
    # removing duplicates line from here.
    write_log_file_for_test_case(sTestCaseStatus, test_case, run_id, sTestCaseEndTime, TestCaseDuration, FailReason, temp_ini_file)
    # Update test case result

    run_cancelled = RequestFormatter.Get('get_status_of_a_run_api', {'run_id': run_id})
    if run_cancelled == 'Cancelled':
        print "Test Run status is Cancelled. Exiting the current Test Set... ", run_id
        CommonUtil.ExecLog(sModuleInfo, "Test Run status is Cancelled. Exiting the current Test Set...%s" % run_id, 2)
        return


#main function
def main():
    print "MainDriver is starting"
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    temp_ini_file = os.path.join(os.path.join(FL.get_home_folder(), os.path.join('Desktop',os.path.join('AutomationLog',ConfigModule.get_config_value('Temp', '_file')))))
    ConfigModule.add_config_value('sectionOne', 'sTestStepExecLogId', sModuleInfo, temp_ini_file)
    Userid = (CommonUtil.MachineInfo().getLocalUser()).lower()

    user_permission = check_user_permission_to_run_test(sModuleInfo,Userid)
    if user_permission not in passed_tag_list:
        return user_permission

    driver_list = get_all_drivers_list()
    TestRunLists = get_all_run_ids(Userid)

    if len(TestRunLists) > 0:
        print "Running Test cases from Test Set : ", TestRunLists[0:len(TestRunLists)]
        CommonUtil.ExecLog(sModuleInfo, "Running Test cases from Test Set : %s" % TestRunLists[0:len(TestRunLists)], 1)

    else:
        print "No Test Run Schedule found for the current user :", Userid
        CommonUtil.ExecLog(sModuleInfo, "No Test Run Schedule found for the current user : %s" % Userid, 2)
        return False

    #for each test runid loop continues
    for TestRunID in TestRunLists:
        project_id = TestRunID[3]
        team_id = int(TestRunID[4])
        run_description = TestRunID[1]
        run_id=TestRunID[0]
        final_dependency = get_all_dependencies(project_id,team_id,run_description) #get dependencies
        final_run_params = get_all_runtime_parameters(run_id) #get runtime params
        update_run_id_info_on_server(run_id) #update runid status
        TestSetStartTime = time.time()
        TestCaseLists=get_all_automated_test_cases_in_run_id(run_id)  #get all automated test cases of a runid

        if len(TestCaseLists) > 0:
            print "Running Test cases from list : ", TestCaseLists[0:len(TestCaseLists)]
            CommonUtil.ExecLog(sModuleInfo, "Running Test cases from list : %s" % TestCaseLists[0:len(TestCaseLists)],1)
            print "Total number of test cases ", len(TestCaseLists)
        else:
            print "No test cases found for the current user :", Userid
            CommonUtil.ExecLog(sModuleInfo, "No test cases found for the current user : %s" % Userid, 2)
            return False

        #run each test case in the runid
        for TestCaseID in TestCaseLists:
            run_test_case(TestCaseID, sModuleInfo, run_id, driver_list, final_dependency, final_run_params, temp_ini_file)

        #calculate elapsed time of runid
        sTestSetEndTime = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        TestSetEndTime = time.time()
        TimeDiff=TestSetEndTime-TestSetStartTime
        TimeInSec=int(TimeDiff)
        TestSetDuration = CommonUtil.FormatSeconds(TimeInSec)

        run_cancelled = get_status_of_runid(run_id) #check if run is cancelled
        if run_cancelled == 'Cancelled':
            print "Test Set Cancelled by the User"
            CommonUtil.ExecLog(sModuleInfo, "Test Set Cancelled by the User", 1)
        else:
            update_test_case_result_on_server(run_id, sTestSetEndTime, TestSetDuration) #update runid status on server
        ConfigModule.add_config_value('sectionOne', 'sTestStepExecLogId', "MainDriver", temp_ini_file)
        print "Test Set Completed"
    return "pass"


if __name__=='__main__':
    main()