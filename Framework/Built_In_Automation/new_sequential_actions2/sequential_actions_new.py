'''
    Sequential Actions - Main Functions
    Function: Handles incoming step data and distributes it to the specified functions
'''

import inspect, sys
from Framework.Utilities import CommonUtil
import common_functions as common # Functions that are common to all modules
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr


# Dictionary of supported actions and their respective modules
actions = { # Numbers are arbitrary, and are not used anywhere. Name and module must be lower case.
    200: {'module': 'appium', 'name': 'step result', 'function': 'step_result'},
    100: {'module': 'appium', 'name': 'click', 'function': 'Click_Element_Appium'},
    101: {'module': 'appium', 'name': 'text', 'function': 'Enter_Text_Appium'},
    102: {'module': 'appium', 'name': 'wait', 'function': 'Wait_For_New_Element'},
    103: {'module': 'appium', 'name': 'tap', 'function': 'Tap_Appium'},
    104: {'module': 'appium', 'name': 'validate full text', 'function': 'Validate_Text'},
    105: {'module': 'appium', 'name': 'validate partial text', 'function': 'Validate_Text'},
    106: {'module': 'appium', 'name': 'save text', 'function': 'Save_Text'},
    107: {'module': 'appium', 'name': 'compare variable', 'function': 'Compare_Variables'},
    108: {'module': 'appium', 'name': 'initialize list', 'function': 'Initialize_List'},
    109: {'module': 'appium', 'name': 'compare list', 'function': 'Compare_Lists'},
    110: {'module': 'appium', 'name': 'insert into list', 'function': 'Insert_Into_List'},
    111: {'module': 'appium', 'name': 'install', 'function': 'install_application'},
    112: {'module': 'appium', 'name': 'launch', 'function': 'launch_application'},
    113: {'module': 'appium', 'name': 'get location', 'function': 'get_element_location_by_id'},
    114: {'module': 'appium', 'name': 'sleep', 'function': 'Sleep'},
    115: {'module': 'appium', 'name': 'swipe', 'function': 'swipe_handler'},
    116: {'module': 'appium', 'name': 'close', 'function': 'close_application'},
    117: {'module': 'appium', 'name': 'uninstall', 'function': 'uninstall_application'},
    118: {'module': 'appium', 'name': 'teardown', 'function': 'teardown_appium'},
    119: {'module': 'appium', 'name': 'keypress', 'function': 'Keystroke_Appium'},
    120: {'module': 'appium', 'name': 'tap location', 'function': 'tap_location'},
}

# List of support for the actions
action_support = [
    'element parameter',
    'reference parameter',
    'relation type',
    'element parameter 1 of 2',
    'element parameter 2 of 2',
]

# Recall dependency, if not already set
dependency = 'Android' #{'Mobile OS':'Android'} #!!! Will be updated by sequential_actions_appium() in the future
if sr.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
    dependency = sr.Get_Shared_Variables('dependency') # Retreive appium driver


def load_sa_modules(module): # Load module "AS" must match module name we get from step data (See actions variable above)
    ''' Dynamically loads modules when needed '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Dynamically loading module %s" % module, 1)
    
    if module == 'appium':
        global appium
        from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions as appium
    elif module == 'selenium':
        global selenium
        from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as selenium
    elif module == 'rest':
        global rest
        from Framework.Built_In_Automation.Web.REST import BuiltInFunctions as rest
    else:
        CommonUtil.ExecLog(sModuleInfo, "Invalid sequential actions module: %s" % module, 3)
        return 'failed'
    return 'passed'


def Sequential_Actions(step_data, dependency = '', file_attachment = ''):
    ''' Main Sequential Actions function - Performs logical decisions based on user input '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Starting Sequential Actions", 1)
    
    # Prepare step data for processing
    if common.verify_step_data(step_data) in common.failed_tag_list: # Verify step data is in correct format
        CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
        return "failed"
    step_data = common.sanitize(step_data) # Sanitize Field and Sub-Field
    
    try:            
        for data_set in step_data: # For each data set within step data
            logic_row=[] # Holds conditional actions
            for row in data_set: # For each row of the data set
                action_name = row[1] # Get Sub-Field
                
                # Don't process these suport items right now, but also don't fail
                if action_name in action_support:
                    continue

                # If middle column = action, call action handler, but always return a pass
                elif "optional action" in action_name:
                    CommonUtil.ExecLog(sModuleInfo, "Checking the optional action to be performed in the action row: %s" % str(row), 1)
                    result = Action_Handler(data_set, row) # Pass data set, and action_name to action handler
                    if result == 'failed':
                        CommonUtil.ExecLog(sModuleInfo, "Optional action failed. Returning pass anyway", 2)
                    result = 'passed'
                    
                # If middle column = conditional action, evaluate data set
                elif "conditional action" in action_name:
                    CommonUtil.ExecLog(sModuleInfo, "Checking the logical conditional action to be performed in the conditional action row: %s" % str(row), 1)
                    logic_row.append(row)
                    
                    # Only run this when we have two conditional actions for this data set (a true and a false preferably)
                    if len(logic_row) == 2:
                        CommonUtil.ExecLog(sModuleInfo, "Found 2 conditional actions - moving ahead with them", 1)
                        return Conditional_Action_Handler(step_data, data_set, row, logic_row) # Pass step_data, and current iteration of data set to decide which data sets will be processed next
                
                # If middle column = action, call action handler
                elif "action" in action_name: # Must be last, since it's a single word that also exists in other action types
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row: %s" % str(row), 1)
                    result = Action_Handler(data_set, row) # Pass data set, and action_name to action handler
                    if result == [] or result == "failed": # Check result of action handler
                        return "failed"
                
                # Middle column not listed above, so data set is wrong
                else:
                    CommonUtil.ExecLog(sModuleInfo, "The sub-field information is incorrect. Please provide accurate information on the data set(s).", 3)
                    return "failed"                 
        
        # No failures, return pass
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

 

def Conditional_Action_Handler(step_data, each, row, logic_row):
    ''' Process conditional actions, called only by Sequential_Actions() '''
     
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    module = row[1].split(' ')[0]    
    if module:
        Get_Element_Step_Data_Appium = getattr(eval(module), 'Get_Element_Step_Data_Appium')
        element_step_data = Get_Element_Step_Data_Appium([each]) # Pass data set as a list, and get back anything that's not an "action" or "conditional action"
        Validate_Step_Data = getattr(eval(module), 'Validate_Step_Data')
        returned_step_data_list = Validate_Step_Data(element_step_data) # Make sure the element step data we got back from above is good
        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")): # Element step data is bad, so fail
            CommonUtil.ExecLog(sModuleInfo, "Element data is bad: %s" % str(element_step_data), 3)
            return "failed"
        else: # Element step data is good, so continue
            # Check if element from data set exists on device
            try:
                Get_Element_Appium = getattr(eval(module), 'Get_Element_Appium')
                Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                if Element == 'failed': # Element doesn't exist, proceed with the step data following the fail/false path
                    logic_decision = "false"
                else: # Any other return means we found the element, proceed with the step data following the pass/true pass
                    logic_decision = "true"
            except Exception: # Element doesn't exist, proceed with the step data following the fail/false path
                CommonUtil.ExecLog(sModuleInfo, "Could not find element in the by the criteria...", 3)
                logic_decision = "false"
                return CommonUtil.Exception_Handler(sys.exc_info())
                         
            # Process the path as defined above (pass/fail)
            for conditional_steps in logic_row: # For each conditional action from the data set
                CommonUtil.ExecLog(sModuleInfo, "Processing conditional action: %s" % str(conditional_steps), 1)
                if logic_decision in conditional_steps: # If we have a result from the element check above (true/false)
                    list_of_steps = conditional_steps[2].split(",") # Get the data set numbers for this conditional action and put them in a list
                    for each_item in list_of_steps: # For each data set number we need to process before finishing
                        CommonUtil.ExecLog(sModuleInfo, "Processing conditional step %s" % str(each_item), 1)
                        data_set_index = int(each_item) - 1 # data set number, -1 to offset for data set numbering system
                        result = Sequential_Actions([step_data[data_set_index]]) # Recursively call this function until all called data sets are complete
                    return result # Return only the last result of the last row of the last data set processed - This should generally be a "step result action" command
    else:
        CommonUtil.ExecLog(sModuleInfo, "The conditional action you entered is incorrect. Please provide accurate information on the data set(s).", 3)
        return "failed"

    # Shouldn't get here, but just in case
    return 'passed'

def Action_Handler(_data_set, action_row):
    ''' Finds the appropriate function for the requested action in the step data and executes it '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Action_Handler", 1)

    # Split data set row into the usable parts
    action_name = action_row[0]
    action_subfield = action_row[1]
    action_value = action_row[2]

    # Get module and function for this action    
    module, function = get_module_and_function(action_name, action_subfield) # New, get the module to execute
    CommonUtil.ExecLog(sModuleInfo, "Function identified as function: %s in module: %s" % (function, module), 1)

    if module in common.failed_tag_list or module == '' or function == '': # New, make sure we have a function
        CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information on the data set(s).", 3)
        if function == '': # A little more information for the user
            CommonUtil.ExecLog(sModuleInfo, "You probably didn't add the module as part of the action. Eg: appium action", 2)
        return "failed"

    # Strip the "optional" keyword, and module, so functions work properly (result of optional action is handled by sequential_actions)
    data_set = []
    for row in _data_set:
        new_row = list(row)
        if 'optional' in row[1]:
            new_row[1] = new_row[1].replace('optional', '').strip()
        if module in row[1]:
            new_row[1] = new_row[1].replace(module, '').strip()
        data_set.append(tuple(new_row))

    # Convert shared variables to their string equivelent
    data_set = shared_variable_to_value(data_set)
    if data_set in common.failed_tag_list:
        return 'failed'

    try:
        if action_name == "step result": # Result from step data the user wants to specify (passed/failed)
            if action_value in common.failed_tag_list: # Convert user specified pass/fail into standard result
                return 'failed'
            elif action_value in common.passed_tag_list:
                return 'passed'
            else:
                CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information on the data set(s).", 3)
                return 'failed'
        else:
            result = load_sa_modules(module) # Load the appropriate module
            if result == 'failed':
                CommonUtil.ExecLog(sModuleInfo, "Can't find module for %s" % module, 3)
                return 'failed'
            
            CommonUtil.ExecLog(sModuleInfo, "Executing %s with data set %s" % (function, str(data_set)), 1)
            run_function = getattr(eval(module), function) # create a reference to the function
            result = run_function(data_set) # Execute function, providing all rows in the data set
            return result # Return result to sequential_actions()

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
 

def get_module_and_function(action_name, action_sub_field):
    ''' Function to split module from the action name, and with the action name tries to find the corrosponding function name '''
    
    try:
        action_list = action_sub_field.split(' ') # Split sub-field, so we can get moudle name from step data
        if action_list > 1: # Should be at least two words in the sub-field
            module = action_list[0] # Save first word which is the module name
            _exit = 0
            function = ''
            for i in actions: # For each dictionary in the dictionary
                if _exit == 1: break # Exit if we found what we are looking for
                for j in actions[i]: # For each entry in the sub-dictionary
                    if actions[i]['module'] == module and actions[i]['name'] == action_name: # Module and action name match
                        function = actions[i]['function'] # Save function
                        _exit = 1 # Exit for loop
                        break

            return module, function # Return module and function name
        else:
            return '','' # Error handled in calling function
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def shared_variable_to_value(data_set): #!!! Should be moved to Shared_Variable.py
    ''' Look for any Shared Variable strings in step data, convert them into their values, and return '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    new_data = [] # Rebuild the data_set with the new variable (because it's a list of tuples which we can't update)

    try:
        for row in data_set: # For each row of the data set
            data_row = list(row) # Convert row which is a tuple to a list, so we can update it if we need to
            for i in range(0, 3): # For each field (Field, Sub-Field, Value)
                if row[i] != False: # !!!! Probbly not needed
                    while "%|" in data_row[i] and "|%" in data_row[i]: # If string contains these characters, it's a shared variable
                        CommonUtil.ExecLog(sModuleInfo, "Shared Variable: %s" % row[i], 1)
                        left_index = data_row[i].index('%|') # Get index of left marker
                        right_index = data_row[i].index('|%') # Get index of right marker
                        var = data_row[i][left_index:right_index + 2] # Copy entire shared variable
                        var_clean = var[2:len(var)-2] # Remove markers
                        data_row[i] = data_row.replace(var, sr.Get_Shared_Variables(var_clean)) # Get the string for this shared variable 
                        if data_row[i] == 'failed':
                            CommonUtil.ExecLog(sModuleInfo, "Invalid shared variable", 3)
                            return "failed"
            new_data.append(tuple(data_row)) # Convert row from list to tuple, and append to new data_set
        return new_data
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


if __name__ == '__main__':
    step_data = [ [ ( 'app_activity' , 'element parameter' , 'com.assetscience.recell.device.android.prodiagnostics.gui.aftersalesRMA.AftersalesRMAPairingActivity' , False , False , '' ) , ( 'launch' , 'appium action' , 'com.assetscience.vodafone.prod' , False , False , '' ) ] ]
    Sequential_Actions(step_data)

