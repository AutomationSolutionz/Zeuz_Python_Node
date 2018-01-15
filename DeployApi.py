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

def form_uri(resource_path):
    global web_server_address,web_server_port
    base_server_address = 'http://%s:%s/' % (str(web_server_address), str(web_server_port))
    return base_server_address+resource_path+'/'

def Get(resource_path,payload={}):
    try:
        req = requests.get(form_uri(resource_path),params=json.dumps(payload), timeout=100000).json()
        return req
    except: return {}


if __name__ == '__main__':
    while True:
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
            dict = {
                'set': set,
                'username': username,
                'project': project,
                'team': team
            }
            if set == '':
                print "Set name can't be empty"
            else:
                result = {}
                if str(choice).strip() == '1':
                    result = Get("deploy_from_api_and_get_result",dict)
                elif str(choice).strip() == '2':
                    result = Get("deploy_from_api_only", dict)

                if result == {}:
                    print "Please Enter Valid Test Set Name from %s"%web_server_address
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
                    print converted_to_string_dict
        elif str(choice).strip() == '3':
            break
        else:
            print "Invalid Choice"


