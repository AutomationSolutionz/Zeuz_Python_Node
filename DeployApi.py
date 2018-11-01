import os
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Framework')) # Move to Framework directory, so all modules can be seen
from Framework.Utilities import ConfigModule
import requests,json

#GLOBAL VARS
#set server address
web_server_address = ConfigModule.get_config_value('Server','server_address')
#set server port
web_server_port = ConfigModule.get_config_value('Server','server_port')
#set username
username = ConfigModule.get_config_value('Authentication','username')
#set project name
project = ConfigModule.get_config_value('Authentication','project')
#set team name
team = ConfigModule.get_config_value('Authentication','team')
#set the set name that you want to run
set = ''
dependency = {
    'Browser': ['Chrome','FireFox','IE','Safari','None'],
    'Mobile': ['Android','iOS','Windows','None'],
    'PC': ['Linux','Mac','Windows','None']
}

run_time_params = {}

def form_uri(resource_path):
    global web_server_address,web_server_port
    base_server_address = 'http://%s:%s/' % (str(web_server_address), str(web_server_port))
    return base_server_address+resource_path+'/'

def Get(resource_path,payload={}):
    try:
        req = requests.get(form_uri(resource_path),params=json.dumps(payload), timeout=100000).json()
        return req
    except: return {}


def get_dependency():
    selected_depenency = {}
    for key in dependency:
        print "******************** SELECT DEPENDENCY %s ********************"%(key.upper())
        for i in range(0,len(dependency[key])):
            print '%d. %s'%(i+1,dependency[key][i].upper())
        print "ENTER YOUR CHOICE: "
        choice = int(str(raw_input()).strip())
        selected_depenency[key] = dependency[key][choice-1]
    return selected_depenency


def get_all_run_time_params_from_server():
    dict = {
        'project': project,
        'team': team
    }
    all_run_params = Get('get_run_params_api',dict)
    for param in all_run_params['param_list']:
        run_time_params[param[1]] = []
        for name in all_run_params['param_name_list']:
            if name[0] == param[0]:
                for value in all_run_params['param_value_list']:
                    if param[0] == value[0] and name[1] == value[1]:
                        run_time_params[param[1]].append((name[2],value[3]))

    #print run_time_params

def get_run_time_params_from_user():
    selected_run_param = []
    for key in run_time_params:
        print "******************** SELECT RUN TIME PARAMETER %s ********************" % (key.upper())
        i=0
        while i<len(run_time_params[key]):
            print '%d. %s( %s )' % (i + 1, run_time_params[key][i][0],run_time_params[key][i][1])
            i+=1
        print '%d. NONE' % (i + 1)
        print "ENTER YOUR CHOICE: "
        choice = int(str(raw_input()).strip())
        if choice == i+1: #NONE
            continue
        selected_run_param.append('%s|%s|%s'%(key,run_time_params[key][choice-1][0],run_time_params[key][choice-1][1]))
    ans=  "|||".join(selected_run_param)
    return ans

def get_loop_input():
    print "******************** SELECT LOOP ********************"
    print "1. DON'T RUN IN LOOP"
    print "2. RUN IN LOOP: "
    print "ENTER YOUR CHOICE: "
    choice = int(str(raw_input()).strip())
    if choice == 2:
        print "HOW MANY TIMES?"
        print "ENTER YOUR CHOICE: "
        loop = int(str(raw_input()).strip())
        print "DO YOU WANT TO CLEANUP RUNID AFTER THE RUN?"
        print "ENTER YOUR CHOICE: "
        print "1. YES"
        print "2. NO"
        cleanup = int(str(raw_input()).strip())
        if cleanup == 1: return loop,True
        else: return loop,False
    else: return 1,False

def delete_runid_from_server(all_runid):
    if len(all_runid) == 0: return
    print "DELETING RUNID FROM SERVER"
    all_runid = "|".join(all_runid)
    delete_dict = {
        'run_id_list':all_runid
    }
    Get("cleanup_data_from_api", delete_dict)
    delete_dict = {
        'log_list': all_runid
    }
    Get("delete_log_file_from_api", delete_dict)
    print "RUNID DELETED FROM SERVER"

if __name__ == '__main__':
    while True:
        get_all_run_time_params_from_server()
        print "******************** ZEUZ DEPLOY API ********************"
        print "1. Deploy and Get Result"
        print "2. Deploy and Get RunID only"
        print "3. Exit"
        print "ENTER YOUR CHOICE: "
        choice = raw_input()
        if str(choice).strip() == '1' or str(choice).strip() == '2':
            print "ENTER SET NAME: "
            set = raw_input()
            set = str(set).strip()
            selected_dependency =  get_dependency()
            selected_run_time_params = get_run_time_params_from_user()
            if str(choice).strip() == '1':
                loop,delete_runid = get_loop_input()
            else:
                loop=1
                delete_runid=False
            all_runid = []
            for i in xrange(loop):
                dict = {
                    'set': set,
                    'username': username,
                    'project': project,
                    'team': team,
                    'run_time_param':selected_run_time_params
                }
                for key in selected_dependency:
                    if selected_dependency[key] != 'None':
                        dict[key] = selected_dependency[key]
                if set == '':
                    result = {}
                    result['message'] = 'Test Set Name can not be Empty'
                    result['result'] = 'Cancelled'
                    result['runid'] = ''
                    print result
                else:
                    result = {}
                    if str(choice).strip() == '1':
                        result = Get("deploy_from_api_and_get_result",dict)
                    elif str(choice).strip() == '2':
                        result = Get("deploy_from_api_only", dict)

                    if result == {}:
                        result['message'] = "Invalid Test Set Name"
                        result['result'] = 'Cancelled'
                        result['runid'] = ''
                        if loop == 1:
                            print result
                        else:
                            print "Result of Loop %d : "%(i+1) + str(result)
                    else:
                        converted_to_string_dict = {}
                        for key in result:
                            k = key
                            v = result[key]
                            if isinstance(k,unicode):
                                k = str(k)
                            if isinstance(v,unicode):
                                v = str(v)
                            converted_to_string_dict[k] = v
                        if loop == 1:
                            print converted_to_string_dict
                        else:
                            if delete_runid:
                                all_runid.append(result['runid'])
                            print "Result of Loop %d : " % (i+1) + str(converted_to_string_dict)
            if delete_runid:
                delete_runid_from_server(all_runid)
        elif str(choice).strip() == '3':
            break
        else:
            print "Invalid Choice"


