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
    r = RequestFormatter.Get('login_api',user_info_object)
    print "Authentication check for user='%s', project='%s', team='%s'"%(username,project,team)
    if r:
        print "Authentication Successful"
        machine_object=update_machine(dependency_collection())
        if machine_object['registered']:
            tester_id=machine_object['name']
            RunAgain = RunProcess(tester_id)
            if RunAgain == True:
                Login()
        else:
            return False
    else:
        print "Authentication Failed"
        return False
def RunProcess(sTesterid):
    while (1):
        try:
            r=RequestFormatter.Get('is_run_submitted_api',{'machine_name':sTesterid})
            if r['run_submit']:
                PreProcess()
                value = MainDriverApi.main()
                print "updating db with parameter"
                if value == "pass":
                    break
                print "Successfully updated db with parameter"
            else:
                time.sleep(3)
                if r['update']:
                    _r=RequestFormatter.Get('update_machine_with_time_api',{'machine_name':sTesterid})
        except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
            print Error_Detail
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
            print "Machine is registered as online with name: %s"%(r['name'])
        else:
            print "Machine is not registered as online"
        return r
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print Error_Detail

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
            print ",".join(missing_list)+" missing from the configuration file - settings.conf"
            return False
        else:
            print "All the dependency present in the configuration file - settings.conf"
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
        print Error_Detail

if __name__=='__main__':
    Login()

