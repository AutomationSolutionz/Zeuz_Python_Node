
import requests,json

#GLOBAL VARS
#set server address
web_server_address = '127.0.0.1'
#set server port
web_server_port = '8000'
#set username
username = 'sreejoy'
#set project name
project = 'QA'
#set team name
team = 'QA'
#set the set name that you want to run
set = 'REST Server Automation'

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
    dict = {
        'set': set,
        'username': username,
        'project': project,
        'team': team
    }
    print "1. Deploy and Get Result"
    print "2. Deploy and Get RunID only"
    print "ENTER YOUR CHOICE:"
    choice = raw_input()
    if str(choice).strip() == '1':
        print Get("deploy_from_api_and_get_result",dict)
    elif str(choice).strip() == '2':
        print Get("deploy_from_api_only",dict)
    else:
        print "Invalid Choice"

