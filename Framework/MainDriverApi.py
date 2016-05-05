import inspect,os
from Utilities import ConfigModule,FileUtilities as FL,CommonUtil,RequestFormatter
'''Constants'''
PROGRESS_TAG = 'In-Progress'


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
        sTestSetStartTime = CommonUtil.TimeStamp('string')
if __name__=='__main__':
    main()