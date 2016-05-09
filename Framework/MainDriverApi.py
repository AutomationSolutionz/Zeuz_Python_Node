import inspect,os,time,sys,urllib2,Queue,importlib
from datetime import datetime
from Utilities import ConfigModule,FileUtilities as FL,CommonUtil,RequestFormatter
top_path=os.path.dirname(os.getcwd())
drivers_path=os.path.join(top_path,'Drivers')
sys.path.append(drivers_path)
import Drivers
'''Constants'''
PROGRESS_TAG = 'In-Progress'
passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True',True,1,'1','Success','success','SUCCESS']
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE',False,0,'0']


def get_final_dependency_list(dependency_list,run_description):
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


def get_run_params_list(run_params):
    run_para=[]
    for each in run_params:
        m_ = {}
        m_.update({'field': each[0]})
        m_.update({'name': each[1]})
        m_.update({'value': each[2]})
        run_para.append(m_)
    return run_para


def main():
    print "MainDriver is starting"
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    temp_ini_file = os.path.join(os.path.join(FL.get_home_folder(), os.path.join('Desktop',os.path.join('AutomationLog',ConfigModule.get_config_value('Temp', '_file')))))
    ConfigModule.add_config_value('sectionOne', 'sTestStepExecLogId', sModuleInfo, temp_ini_file)
    Userid = (CommonUtil.MachineInfo().getLocalUser()).lower()
    r = RequestFormatter.Get('get_valid_machine_name_api',{'machine_name':Userid})
    if not r:
        CommonUtil.ExecLog(sModuleInfo, "User don't have permission to run the tests", 3)
        return "You Don't Have Permission"
    driver_list = RequestFormatter.Get('get_all_drivers_api')
    TestRunLists = RequestFormatter.Get('get_all_submitted_run_of_a_machine_api',{'machine_name':Userid})
    if len(TestRunLists) > 0:
        print "Running Test cases from Test Set : ", TestRunLists[0:len(TestRunLists)]
        CommonUtil.ExecLog(sModuleInfo, "Running Test cases from Test Set : %s" % TestRunLists[0:len(TestRunLists)], 1)

    else:
        print "No Test Run Schedule found for the current user :", Userid
        CommonUtil.ExecLog(sModuleInfo, "No Test Run Schedule found for the current user : %s" % Userid, 2)
        return False
    for TestRunID in TestRunLists:
        project_id = TestRunID[3]
        team_id = int(TestRunID[4])
        run_description = TestRunID[1]
        run_id=TestRunID[0]
        dependency_list = RequestFormatter.Get('get_all_dependency_based_on_project_and_team_api',{'project_id':project_id,'team_id':team_id})
        final_dependency = get_final_dependency_list(dependency_list,run_description)
        run_params_list = RequestFormatter.Get('get_all_run_parameters_based_on_project_and_team_api',{'run_id':run_id})
        final_run_params = get_run_params_list(run_params_list)
        update_run_time_status=RequestFormatter.Get('update_machine_info_based_on_run_id_api',{'run_id':run_id,'options':{'status':PROGRESS_TAG}})
        sTestSetStartTime = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        test_env_result_status_time_update=RequestFormatter.Get('update_test_env_results_based_on_run_id_api',{'options':{'status':PROGRESS_TAG,'teststarttime':str(sTestSetStartTime),'run_id':run_id}})
        TestCaseLists=RequestFormatter.Get('get_all_automated_test_cases_based_on_run_id_api',{'run_id':run_id})
        if len(TestCaseLists) > 0:
            print "Running Test cases from list : ", TestCaseLists[0:len(TestCaseLists)]
            CommonUtil.ExecLog(sModuleInfo, "Running Test cases from list : %s" % TestCaseLists[0:len(TestCaseLists)],1)
            print "Total number of test cases ", len(TestCaseLists)
        else:
            print "No test cases found for the current user :", Userid
            CommonUtil.ExecLog(sModuleInfo, "No test cases found for the current user : %s" % Userid, 2)
            return False
        for TestCaseID in TestCaseLists:
            test_case=TestCaseID[0]
            copy_status=False
            while not copy_status:
                copy_status=RequestFormatter.Get('is_test_case_copied_api',{'run_id':run_id,'test_case':test_case})
                if copy_status:
                    CommonUtil.ExecLog(sModuleInfo,"Gathering data for test case %s is completed" % (test_case),1)
                else:
                    print "Gathering data for test case %s"%(test_case)
            ConfigModule.add_config_value('sectionOne', 'sTestStepExecLogId', "MainDriver", temp_ini_file)
            StepSeq = 1
            test_case_type = TestCaseID[1]
            CommonUtil.ExecLog(sModuleInfo,"-------------*************--------------",1)
            CommonUtil.ExecLog(sModuleInfo,"Creating Automation Log for test case: %s"%test_case,1)
            try:
                log_file_path = ConfigModule.get_config_value('sectionOne', 'temp_run_file_path', temp_ini_file)
            except Exception, e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
                print Error_Detail
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

            #creating the download folder
            download_folder = ConfigModule.get_config_value('sectionOne', 'download_folder', temp_ini_file)

            #test case attachements
            test_case_attachments=RequestFormatter.Get('get_test_case_attachments_api',{'run_id':run_id,'test_case':test_case})
            test_step_attachments=RequestFormatter.Get('get_test_step_attachments_for_test_case_api',{'run_id':run_id,'test_case':test_case})
            FL.DeleteFolder(ConfigModule.get_config_value('sectionOne', 'download_folder', temp_ini_file))
            FL.CreateFolder(download_folder)
            file_specific_steps={}
            for each in test_case_attachments:
                CommonUtil.ExecLog(sModuleInfo,"Attachment download for test case %s started"%test_case,1)
                m = each[1] + '.' + each[2]  # file name
                f = open(download_folder + '/' + m, 'wb')
                f.write(urllib2.urlopen('http://' + ConfigModule.get_config_value('Server', 'server_address') + ':' + str(ConfigModule.get_config_value('Server', 'server_port')) + '/static' + each[0]).read())
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
                f.write(urllib2.urlopen('http://' + ConfigModule.get_config_value('Server', 'server_address') + ':' + str(ConfigModule.get_config_value('Server', 'server_port')) + '/static' + each[0]).read())
                file_specific_steps.update({m: download_folder + '/' + str(each[3]) + '/' + m})
                f.close()
            if test_step_attachments:
                CommonUtil.ExecLog(sModuleInfo, "Attachment download for steps in test case %s finished" % test_case, 1)
            test_case_detail=RequestFormatter.Get('get_test_case_detail_api',{'run_id':run_id,'test_case':test_case})
            TestCaseName=test_case_detail[0][1]
            CommonUtil.ExecLog(sModuleInfo, "-------------*************--------------", 1)
            CommonUtil.ExecLog(sModuleInfo, "Running Test case id : %s :: %s" % (test_case, TestCaseName), 1)

            sTestCaseStartTime = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            test_case_result_index=RequestFormatter.Get('test_case_results_update_returns_index_api',{'run_id':run_id,'test_case':test_case,'options':{'status':PROGRESS_TAG,'teststarttime':sTestCaseStartTime}})
            TestStepsList=RequestFormatter.Get('test_step_fetch_for_test_case_run_id_api',{'run_id':run_id,'test_case':test_case})
            Stepscount=len(TestStepsList)
            while StepSeq <= Stepscount:
                current_step_name=TestStepsList[StepSeq - 1][1]
                current_step_id=TestStepsList[StepSeq-1][0]
                current_step_sequence=TestStepsList[StepSeq-1][2]
                CommonUtil.ExecLog(sModuleInfo, "Step : %s" % current_step_name, 1)
                step_meta_data=RequestFormatter.Get('get_step_meta_data_api',{'run_id':run_id,'test_case':test_case,'step_seq':StepSeq})
                continue_value=filter(lambda x: x[0]=='continue' and x[1]=='point',step_meta_data)
                if continue_value:
                    if continue_value[0][2]=='yes':
                        test_case_continue=True
                    else:
                        test_case_continue = False
                else:
                    test_case_continue=False
                ConfigModule.add_config_value('sectionOne', 'sTestStepExecLogId',run_id + "|" + test_case + "|" + str(current_step_id) + "|" + str(StepSeq), temp_ini_file)
                sTestStepStartTime=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
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
                test_step_status_index=RequestFormatter.Get('test_step_results_update_returns_index_api',{'run_id':run_id,'tc_id':test_case,'step_id':current_step_id,'test_step_sequence':current_step_sequence,'options':Dict})
                test_steps_data=RequestFormatter.Get('get_test_step_data_based_on_test_case_run_id_api',{'run_id':run_id,'test_case':test_case,'step_sequence':current_step_sequence,'step_iteration':StepSeq})
                CommonUtil.ExecLog(sModuleInfo, "steps data for #%d: %s" % (StepSeq, str(test_steps_data)), 1)
                step_time = filter(lambda x:x[0]=='estimated' and x[1]=='time',step_meta_data)
                if step_time:
                    step_time=int(step_time[0][2])
                else:
                    step_time=0
                auto_generated_image_name = ('_').join(current_step_name.split(" ")) + '_started.png'
                CommonUtil.TakeScreenShot(str(auto_generated_image_name))
                try:
                    q = Queue.Queue()
                    current_driver=TestStepsList[StepSeq-1][3]
                    if current_driver in driver_list:
                        module_name = importlib.import_module(current_driver)
                        step_name = current_step_name
                        step_name = step_name.lower().replace(' ', '_')
                        functionTocall = getattr(module_name, step_name)
                        simple_queue=Queue.Queue()
                        sStepResult = functionTocall(final_dependency,final_run_params,test_steps_data, file_specific_steps, simple_queue)
                        if sStepResult in passed_tag_list:
                            sStepResult = 'PASSED'
                        if sStepResult in failed_tag_list:
                            sStepResult = 'FAILED'
                        q.put(sStepResult)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Driver is not enlisted. Execution of test step failed", 3)
                        sStepResult="Failed"
                except Exception,e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Exception occurred in test step : %s" % Error_Detail, 3)
                    sStepResult = "Failed"
                StepSeq+=1

if __name__=='__main__':
    main()