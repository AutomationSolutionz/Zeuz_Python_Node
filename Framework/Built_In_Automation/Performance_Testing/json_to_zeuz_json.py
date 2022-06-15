import json,pprint,os

# Check if action is disabled
def check_if_disabled(action):
    if action.get('action_disabled') == 'false':
        return True
    else:
        return False
# Check if the action is a locust action
def selected_locust_action(action):
    all_locust_actions = ['locust config','assign locust user','assign locust task']
    locust_actions =  [ac[0] for ac in action['Action data'] if ac[0] in all_locust_actions]
    if(locust_actions):
        return locust_actions[0]
    else:
        return False

# Get the values for the action paramteres
def get_values(step_actions,action_val_map):
    data = dict()
    for sa in step_actions:
        variable_name = action_val_map.get(sa[0])
        if(variable_name):
            variable_value = sa[2]
            data[variable_name] = variable_value
    return data

def convert_json(input_json_file_path,output_json_file_path):
    input_json_file_path = os.path.dirname(os.path.realpath(__file__)) + '/' + input_json_file_path
    output_json_file_path = os.path.dirname(os.path.realpath(__file__)) + '/' + output_json_file_path
    input_json_data = json.load(open(input_json_file_path))
    testcase = input_json_data["TestCases"]
    steps = testcase[0]["Steps"]
    actions = []
    for step in steps:
        actions = actions + step["Step actions"]
    all_locusts = dict()
    for action in actions:
        locust_action = selected_locust_action(action)
        if(check_if_disabled(action) == False and locust_action):
                step_actions = action['Action data']
                if(locust_action == 'locust config'):
                    params = get_values(step_actions,{'swarm':'swarm','spawn':'spawn','locust config':'variable_name'})
                    all_locusts[params['variable_name']] = ({"locust_config": {"swarm": params['swarm'],"spawn": params['spawn']},"users": {}})
                if(locust_action == 'assign locust user'):
                    params = get_values(step_actions,{'type':'type','name':'name','host':'host','wait_time':'wait_time','assign locust user':'variable_name'})
                    all_locusts[params['variable_name']]['users'][params['name']] = {'type':params['type'],'wait_time' : params['wait_time'],'host':params['host'],'tasks':[]}

                if(locust_action == 'assign locust task'):
                    params = get_values(step_actions,{'action':'http_method','data':'data','name':'name','assign locust task':'variable_name'})
                    all_locusts[params['variable_name']]['users'][params['name']]['tasks'].append({'action': 'client.' + params['http_method'],'data':params['data'],'name':params['name']}) 
    
    pprint.pprint(all_locusts)

    with open(output_json_file_path, "w") as outfile:
        json.dump(all_locusts,outfile,indent=4 )

if __name__ == '__main__':
    convert_json(input_json_file_path="sample2.json",output_json_file_path="sample_zeuz_json.json")
