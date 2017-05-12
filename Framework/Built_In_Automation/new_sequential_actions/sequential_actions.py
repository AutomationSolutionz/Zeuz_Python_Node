import inspect, sys
from Framework.Utilities import CommonUtil
from common_functions import *
import appium

# Dictionary of supported actions and their respective modules
actions = {
    'selenium'  : 'click',
    'selenium'  : 'open browser',
    'appium'    : 'click',
    'appium'    : 'tap',
    'appium'    : 'launch',
}

# List of support for the actions
action_support = [
    'element parameter',
    'reference parameter',
    'relation type',
    'element parameter 1 of 2',
    'element parameter 2 of 2',
]

def Sequential_Actions(step_data):
    ''' Main Sequential Actions function - Performs logical decisions based on user input '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Starting Sequential Actions", 1)
    
    # Prepare step data for processing
    step_data = sanitize(step_data) # Sanitize Field and Sub-Field
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
     
    element_step_data = Get_Element_Step_Data_Appium([each]) # Pass data set as a list, and get back anything that's not an "action" or "conditional action"
    returned_step_data_list = Validate_Step_Data(element_step_data) # Make sure the element step data we got back from above is good
    if ((returned_step_data_list == []) or (returned_step_data_list == "failed")): # Element step data is bad, so fail
        CommonUtil.ExecLog(sModuleInfo, "Element data is bad: %s" % str(element_step_data), 3)
        return "failed"
    else: # Element step data is good, so continue
        # Check if element from data set exists on device
        try:
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
 
    # Shouldn't get here, but just in case
    return 'passed'

def Action_Handler(action_step_data, action_row):
    ''' Finds the appropriate function for the requested action in the step data and executes it '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Action_Handler", 1)
    
    # Split data set row into the usable parts
    action_name = action_row[0]
    action_value = action_row[1]
    
    try:
        if action_name == "step result": # Result from step data the user wants to specify (passed/failed)
            if action_value in failed_tag_list: # Convert user specified pass/fail into standard result
                return 'failed'
            elif action_value in passed_tag_list:
                return 'passed'
            else:
                CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information on the data set(s).", 3)
                return 'failed'
        else:
            module, function = split_action_name(action_name) # New, get the module and function to execute
            CommonUtil.ExecLog(sModuleInfo, "Identified %s and %s" % (module, function), 1)
    
            if module and function: # New, make sure we have a function
                run_function = getattr(module, function) # create a function we can use
                result = run_function(action_step_data) # Execute function, providing all step data
                return result
            else:
                CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information on the data set(s).", 3)
                return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

 

def split_action_name(action_name):
    ''' Function to split module and function name from the action name, and verify it exists '''
    
    try:
        action_list = action_name.split(' ')
        if len(action_list) == 3: # Optional action - we don't include the optional in the output because it's not needed
            module = action_list[0]
            function = action_list[2]
        elif len(action_list) == 2: # Regular action
            module = action_list[0]
            function = action_list[1]
        else:
            return '', '' # Failed message will be taken care of in calling function
    
        return module, function # Return function associated with this action for this file
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def shared_variable_to_value(step_data): #!!! Should be moved to CommonUtil
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
                            row[i] = Shared_Resources.Get_Shared_Variables(row[i]) # Get the string for this shared variable
                            if row[i] == 'failed':
                                CommonUtil.ExecLog(sModuleInfo, "Invalid shared variable", 3)
                                return "failed"
        return step_data
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

