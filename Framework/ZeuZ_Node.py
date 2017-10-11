# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import os,sys,time
sys.path.append(os.path.dirname(os.getcwd()))
from Utilities import ConfigModule,RequestFormatter,CommonUtil,FileUtilities
import MainDriverApi


'''Constants'''
AUTHENTICATION_TAG='Authentication'
USERNAME_TAG='username'
PASSWORD_TAG='password'
PROJECT_TAG='project'
TEAM_TAG='team'

exit_script = False # Used by Zeuz Node GUI to exit script
temp_ini_file = os.path.join(os.path.join(FileUtilities.get_home_folder(), os.path.join('Desktop',os.path.join('AutomationLog',ConfigModule.get_config_value('Temp', '_file')))))

def Login():
    username=ConfigModule.get_config_value(AUTHENTICATION_TAG,USERNAME_TAG)
    password=ConfigModule.get_config_value(AUTHENTICATION_TAG,PASSWORD_TAG)
    project=ConfigModule.get_config_value(AUTHENTICATION_TAG,PROJECT_TAG)
    team=ConfigModule.get_config_value(AUTHENTICATION_TAG,TEAM_TAG)
    #form payload object
    user_info_object={
        'username':username,
        'password':password,
        'project':project,
        'team':team
    }
    
    # Iniitalize GUI Offline call
    CommonUtil.set_exit_mode(False)
    global exit_script
    exit_script = False # Reset exit variable

    while True:
        # Test to ensure server is up before attempting to login
        try:
            r = False
            r = RequestFormatter.Head('login_api')
        except: # Occurs when server is down
            r = False 
            
        # Login to server
        if r != False: # Server is up
            try:
                r = RequestFormatter.Get('login_api',user_info_object)
                CommonUtil.ExecLog('', "Authentication check for user='%s', project='%s', team='%s'"%(username,project,team), 4, False)
                if r:
                    CommonUtil.ExecLog('', "Authentication Successful", 4, False)
                    machine_object=update_machine(dependency_collection())
                    if machine_object['registered']:
                        tester_id=machine_object['name']
                        RunAgain = RunProcess(tester_id)
                        #if RunAgain == True:
                        #    Login()
                        if RunAgain == False:
                            break # Exit login
                    else:
                        return False
                else:
                    CommonUtil.ExecLog('', "Authentication Failed", 4, False)
                    return False
            except Exception, e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                CommonUtil.ExecLog('', Error_Detail, 4, False)
                CommonUtil.ExecLog('', "Error logging in, waiting 60 seconds before trying again", 4, False)
                time.sleep(60)
        
        # Server down, wait and retry
        else:
            CommonUtil.ExecLog('', "Server down, waiting 60 seconds before trying again", 4, False)
            time.sleep(60)
    CommonUtil.ExecLog('', "Zeuz Node Offline", 4, False)

def disconnect_from_server():
    ''' Exits script - Used by Zeuz Node GUI '''
    global exit_script
    exit_script = True
    CommonUtil.set_exit_mode(True) # Tell Sequential Actions to exit
    
def RunProcess(sTesterid):
    while (1):
        try:
            if exit_script: return False

            r=RequestFormatter.Get('is_run_submitted_api',{'machine_name':sTesterid})
            if r['run_submit']:
                PreProcess()
                value = MainDriverApi.main()
                CommonUtil.ExecLog('', "updating db with parameter", 4, False)
                if value == "pass":
                    if exit_script: return False
                    break
                CommonUtil.ExecLog('', "Successfully updated db with parameter", 4, False)
            else:
                time.sleep(3)
                if r['update']:
                    _r=RequestFormatter.Get('update_machine_with_time_api',{'machine_name':sTesterid})
        except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
            CommonUtil.ExecLog('', Error_Detail, 4, False)
            break # Exit back to login() - In some circumstances, this while loop will get into a state when certain errors occur, where nothing runs, but loops forever. This stops that from happening 
    return True
def PreProcess():
    current_path = os.path.join(FileUtilities.get_home_folder(), os.path.join('Desktop', 'AutomationLog'))
    retVal = FileUtilities.CreateFolder(current_path, forced=False)
    if retVal:
        # now save it in the global_config.ini
        TEMP_TAG = 'Temp'
        file_name = ConfigModule.get_config_value(TEMP_TAG, '_file')
        current_path_file = os.path.join(current_path, file_name)
        FileUtilities.CreateFile(current_path_file)
        ConfigModule.clean_config_file(current_path_file)
        ConfigModule.add_section('sectionOne', current_path_file)
        ConfigModule.add_config_value('sectionOne', 'temp_run_file_path', current_path, current_path_file)


def update_machine(dependency):
    try:
        #Get Local Info object
        oLocalInfo = CommonUtil.MachineInfo()

        local_ip = oLocalInfo.getLocalIP()
        testerid = (oLocalInfo.getLocalUser()).lower()

        product_='ProductVersion'
        branch=ConfigModule.get_config_value(product_,'branch')
        version=ConfigModule.get_config_value(product_,'version')
        productVersion= branch+":"+version

        project=ConfigModule.get_config_value(AUTHENTICATION_TAG,PROJECT_TAG)
        team=ConfigModule.get_config_value(AUTHENTICATION_TAG,TEAM_TAG)
        if not dependency:
            dependency=""
        _d={}
        for x in dependency:
            t = []
            for i in x[1]:
                _t=['name','bit','version']
                __t={}
                for index,_i in enumerate(i):
                    __t.update({_t[index]:_i})
                if __t:
                    t.append(__t)
            _d.update({x[0]:t})
        dependency=_d
        update_object={
            'machine_name':testerid,
            'local_ip':local_ip,
            'productVersion':productVersion,
            'dependency':dependency,
            'project':project,
            'team':team
        }
        r=RequestFormatter.Get('update_automation_machine_api',update_object)
        if r['registered']:
            CommonUtil.ExecLog('', "Machine is registered as online with name: %s"%(r['name']), 4, False)
        else:
            CommonUtil.ExecLog('', "Machine is not registered as online", 4, False)
        return r
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog('', Error_Detail, 4, False)

def dependency_collection():
    try:
        dependency_tag='Dependency'
        dependency_option=ConfigModule.get_all_option(dependency_tag)
        project=ConfigModule.get_config_value(AUTHENTICATION_TAG,PROJECT_TAG)
        team=ConfigModule.get_config_value(AUTHENTICATION_TAG,TEAM_TAG)
        r=RequestFormatter.Get('get_all_dependency_name_api',{'project':project,'team':team})
        obtained_list=[x.lower() for x in r]
        #print "Dependency: ",dependency_list
        missing_list=list(set(obtained_list)-set(dependency_option))
        #print missing_list
        if missing_list:
            CommonUtil.ExecLog('', ",".join(missing_list)+" missing from the configuration file - settings.conf", 4, False)
            return False
        else:
            CommonUtil.ExecLog('', "All the dependency present in the configuration file - settings.conf", 4, False)
            final_dependency=[]
            for each in r:
                temp=[]
                each_dep_list=ConfigModule.get_config_value(dependency_tag,each).split(",")
                #print each_dep_list
                for each_item in each_dep_list:
                    if each_item.count(":")==2:
                        name,bit,version=each_item.split(":")

                    else:
                        name=each_item.split(":")[0]
                        bit=0
                        version=''
                        #print name,bit,version
                    temp.append((name,bit,version))
                final_dependency.append((each,temp))
            return  final_dependency
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog('', Error_Detail, 4, False)

def get_team_names():
    ''' Retrieve all teams user has access to '''
    
    try:
        username=ConfigModule.get_config_value(AUTHENTICATION_TAG,USERNAME_TAG)
        password=ConfigModule.get_config_value(AUTHENTICATION_TAG,PASSWORD_TAG)
    
        user_info_object = {
            USERNAME_TAG: username,
            PASSWORD_TAG: password
        }
    
        r = RequestFormatter.Get('get_user_teams_api', user_info_object)
        teams = [x[0] for x in r] # Convert into a simple list
        return teams
    except:
        CommonUtil.ExecLog('', "Error retrieving team names", 4, False)

def get_project_names(team):
    ''' Retrieve projects for given team '''
    
    try:
        username=ConfigModule.get_config_value(AUTHENTICATION_TAG,USERNAME_TAG)
        password=ConfigModule.get_config_value(AUTHENTICATION_TAG,PASSWORD_TAG)
    
        user_info_object = {
            USERNAME_TAG: username,
            PASSWORD_TAG: password,
            TEAM_TAG: team
        }
    
        r = RequestFormatter.Get('get_user_projects_api', user_info_object)
        projects = [x[0] for x in r] # Convert into a simple list
        return projects
    except:
        CommonUtil.ExecLog('', "Error retrieving project names", 4, False)

if __name__=='__main__':
    Login()

