'''
    Sequential Actions - Main Functions
    Function: Handles incoming step data and distributes it to the specified functions
'''

import inspect, sys
from Framework.Utilities import CommonUtil
import common_functions # Functions that are common to all modules
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr


# Dictionary of supported actions and their respective modules
actions = {
    0  : {'module': 'selenium', 'name': 'click', 'function': 'Click_Element'},
    1  : {'module': 'selenium', 'name': 'open browser', 'function': 'open_browser'},
    2  : {'module': 'appium', 'name': 'click', 'function': 'Click_Element'},
    3  : {'module': 'appium', 'name': 'launch', 'function': 'launch_application'},
    4  : {'module': 'appium', 'name': 'teardown', 'function': 'teardown'},
}
# List of support for the actions
action_support = [
    'element parameter',
    'reference parameter',
    'relation type',
    'element parameter 1 of 2',
    'element parameter 2 of 2',
]

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


def Sequential_Actions(step_data):
    ''' Main Sequential Actions function - Performs logical decisions based on user input '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Starting Sequential Actions", 1)
    
    # Prepare step data for processing
    step_data = common_functions.sanitize(step_data) # Sanitize Field and Sub-Field
    step_data = shared_variable_to_value(step_data) # Convert shared variables into their values for all step data
    
    try:            
        for each in step_data: # For each data set within step data
            logic_row=[] # Holds conditional actions
            for row in each: # For each row of the data set
                action_name = row[1] # Get Sub-Field
                
                # Don't process these suport items right now, but also don't fail
                if action_name in action_support:
                    continue

                # If middle column = action, call action handler, but always return a pass
                elif "optional action" in action_name:
                    CommonUtil.ExecLog(sModuleInfo, "Checking the optional action to be performed in the action row: %s" % str(row), 1)
                    result = Action_Handler(each, row) # Pass data set, and action_name to action handler
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
                        return Conditional_Action_Handler(step_data, each, row, logic_row) # Pass step_data, and current iteration of data set to decide which data sets will be processed next
                
                # If middle column = action, call action handler
                elif "action" in action_name: # Must be last, since it's a single word that also exists in other action types
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row: %s" % str(row), 1)
                    result = Action_Handler(each, row) # Pass data set, and action_name to action handler
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

def Action_Handler(action_step_data, action_row):
    ''' Finds the appropriate function for the requested action in the step data and executes it '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Action_Handler", 1)
    
    # Split data set row into the usable parts
    action_name = action_row[0]
    action_subfield = action_row[1]
    action_value = action_row[2]
    
    try:
        if action_name == "step result": # Result from step data the user wants to specify (passed/failed)
            if action_value in common_functions.failed_tag_list: # Convert user specified pass/fail into standard result
                return 'failed'
            elif action_value in common_functions.passed_tag_list:
                return 'passed'
            else:
                CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information on the data set(s).", 3)
                return 'failed'
        else:
            module, function = get_module_and_function(action_name, action_subfield) # New, get the module to execute
            CommonUtil.ExecLog(sModuleInfo, "Function identified as %s in %s" % (function, module), 1)
    
            if module and function: # New, make sure we have a function
                result = load_sa_modules(module)
                if result == 'failed':
                    CommonUtil.ExecLog(sModuleInfo, "Can't find module for %s" % module, 3)
                    return 'failed'
                
                run_function = getattr(eval(module), function) # create a function we can use
                result = run_function(action_step_data) # Execute function, providing all step data
                return result
            else:
                CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information on the data set(s).", 3)
                return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

 

def get_module_and_function(action_name, action_sub_field):
    ''' Function to split module from the action name, and with the action name tries to find the corrosponding function name '''
    
    try:
        action_list = action_sub_field.split(' ') # Split sub-field, so we can get moudle name from step data
        if action_list > 1: # Should be at least two words in the sub-field
            module = action_list[0] # Save first word which is the module name
            exit = 0
            function = ''
            for i in actions: # For each dictionary in the dictionary
                if exit == 1: break # Exit if we found what we are looking for
                for j in actions[i]: # For each entry in the sub-dictionary
                    if actions[i]['module'] == module and actions[i]['name'] == action_name: # Module and action name match
                        function = actions[i]['function'] # Save function
                        exit = 1 # Exit for loop
                        break

            return module, function # Return module and function name
        else:
            return '','' # Error handled in calling function
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def shared_variable_to_value(step_data): #!!! Should be moved to Shared_Variable.py
    ''' Look for any Shared Variable strings in step data, convert them into their values, and return '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    try:
        for each in step_data: # For each data set within step data
            for row in each: # For each row of the data set
                for i in range(0, 3): # For each field (Field, Sub-Field, Value)
                    if row[i] != False:
                        if "%|" in row[i] and "|%" in row[i]: # If string contains these characters, it's a shared variable
                            CommonUtil.ExecLog(sModuleInfo, "Shared Variable: %s" % row[i], 1)
                            row[i] = row[i].replace("%|", "") # Strip special variable characters
                            row[i] = row[i].replace("|%", "")
                            row[i] = sr.Get_Shared_Variables(row[i]) # Get the string for this shared variable
                            if row[i] == 'failed':
                                CommonUtil.ExecLog(sModuleInfo, "Invalid shared variable", 3)
                                return "failed"
        return step_data
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

