import json
import pprint

def check_if_disabled(action):
    if action['action_disabled'] == 'false':
        return True
    else:
        return False

def selected_locust_action(action):
    all_locust_actions = ['locust config','assign locust user','assign locust task']
    locust_actions =  [ac[0] for ac in action['step_actions'] if ac[0] in all_locust_actions]
    if(locust_actions):
        return locust_actions[0]
    else:
        return False

        

variable_value = None


def main(input_json_file_path):
    actions = json.load(open(input_json_file_path))
    
    for action in actions:
        locust_action = selected_locust_action(action)
        if(check_if_disabled(action) == False and locust_action):
                step_actions = action['step_actions']
                if(locust_action == 'locust config'):
                    for sa in step_actions:
                        if('swarm' in sa[0].strip()):
                            swarm = sa[2].strip()
                        if('spawn' in sa[0].strip()):
                            spawn = sa[2].strip()
                        if('locust config' in sa[0].strip()):
                            variable_name = sa[2].strip()
                            variable_value = {
                                "locust_config": {
                                    "swarm": swarm,
                                    "spawn": spawn
                                },
                                "users": {}
                            }
                if(locust_action == 'assign locust user'):
                    for sa in step_actions:
                        if('type' in sa[0].strip()):
                            user_type = sa[2].strip()
                        if('name' in sa[0].strip()):
                            name = sa[2].strip()
                        if('host' in sa[0].strip()):
                            host = sa[2].strip()
                        if('wait_time' in sa[0].strip()):
                            wait_time = sa[2].strip()
                        if('locust user' in sa[0].strip()):
                            variable_name = sa[2].strip()
                            variable_value['users'][name] = {'type':user_type,'wait_time' : wait_time,'host':host,'tasks':[]}
                    
                # ## Locust User

                # # Locust Task
                if(locust_action == 'assign locust task'):
                    for sa in step_actions:
                        if('action' in sa[0].strip()):
                            http_method = sa[2].strip()
                        if('data' in sa[0].strip()):
                            data = sa[2].strip()
                        if('name' in sa[0].strip()):
                            name = sa[2].strip()
                        if('locust task' in sa[0].strip()):
                            variable_name = sa[2].strip()
                            variable_value['users'][name]['tasks'].append({'action':http_method,'data':data,'name':name}) 
                # # Locust Config
    pprint.pprint(variable_value)


if __name__ == '__main__':
    main(input_json_file_path="/home/sakib/Documents/Zeuz/Locust/de/Zeuz_Python_Node/Framework/Built_In_Automation/Performance_Testing/json_to_zeuz_json/sample.json")