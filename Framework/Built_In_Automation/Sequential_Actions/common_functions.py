'''
    Common Functions
    Function: Contains functions common to all modules 
'''

import inspect, sys, time
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr
from Framework.Built_In_Automation.Sequential_Actions.sequential_actions import actions, action_support
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list, skipped_tag_list # Allowed return strings, used to normalize pass/fail

def sanitize(step_data, valid_chars = '', clean_whitespace_only = False, column = ''):
    ''' Sanitize step data Field and Sub-Field '''
    ''' Usage:
            Is to be used to allow users flexibility in their step data input, but allow the program to find key words
            :valid_chars: By default this function removes all characters. Specifying a string of characters here will skip removing them
            :clean_whitespace_only: If your function uses several characters, you can set this to True, to only clean up white space
            If the user surrounds their input with double quotes, all sanitizing will be skipped, and the surrounding quotes will be removed
    '''
    
    # Set columns in the step data to sanitize (default is Field and Sub-Field only)
    if column == '': # By default, sanitize the first and second columns (Field and Sub-Field)
        column = [0,1]
    else:
        column = str(column).replace(' ', '') # Remove spaces
        column = column.split(',') # Put into list
        column = map(int, column) # Convert numbers in list into integers, so they can be used to address tuple elements
    
    # Invalid character list (space and underscore hare handle separately)
    invalid_chars = '!"#$%&\'()*+,-./:;<=>?@[\]^`{|}~'

    # Adjust invalid character list, based on function input
    for j in range(len(valid_chars)): # For each valid character
        invalid_chars = invalid_chars.replace(valid_chars[j], '') # Remove valid character from invalid character list

    new_step_data = [] # Create empty list that will contain the data sets
    for data_set in step_data: # For each data set within step data
        new_data_set = [] # Create empty list that will have new data appended
        for row in data_set: # For each row of the data set
            new_row = list(row) # Copy tuple of row as list, so we can change it
            for i in column: # Sanitize the specified columns
                if str(new_row[i])[:1] == '"' and str(new_row[i])[-1:] == '"': # String is within double quotes, indicating it should not be changed
                    new_row[i] = str(new_row[i])[1:len(new_row[i]) - 1] # Remove surrounding quotes
                    continue # Do not change string
                
                if clean_whitespace_only == False:
                    for j in range(0,len(invalid_chars)): # For each invalid character (allows us to only remove those the user hasn't deemed valid)
                        new_row[i] = new_row[i].replace(invalid_chars[j], '') # Remove invalid character
                        new_row[i] = new_row[i].lower() # Convert to lower case
                    if '_' not in valid_chars: new_row[i] = new_row[i].replace('_', ' ') # Underscore to space (unless user wants to keep it)

                new_row[i] = new_row[i].replace('  ', ' ') # Double space to single space
                new_row[i] = new_row[i].strip() # Remove leading and trailing whitespace
            new_data_set.append(tuple(new_row)) # Append list as tuple to data set list
        new_step_data.append(new_data_set) # Append data set to step data
    return new_step_data # Step data is now clean and in the same format as it arrived in


def verify_step_data(step_data):
    ''' Verify step data is valid '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Verifying Step Data", 1)
    
    try:
        data_set_index = 0
        for data_set in step_data:
            data_set_index += 1
            module_test = False
            field_text = True # !!! This should be set to false, but we are not using this for now
            
            # Check each data set
            if len(data_set) == 0:
                CommonUtil.ExecLog(sModuleInfo, "Data set %d cannot be empty" % data_set_index, 3)
                return 'failed'
            
            # Check each row
            for row in data_set:
                if len(row[0]) == 0:
                    CommonUtil.ExecLog(sModuleInfo, "Field for data set %d cannot empty: %s" % (data_set_index, str(row)), 3)
                    return 'failed'
                elif len(row[1]) == 0:
                    CommonUtil.ExecLog(sModuleInfo, "Sub-Field for data set %d cannot empty: %s" % (data_set_index, str(row)), 3)
                    return 'failed'
                elif row[1] not in action_support: # Check against list of allowed Sub-Fields
                    if 'action' not in row[1]: #!!! Temporary until module handling is all moved into it's own function
                        CommonUtil.ExecLog(sModuleInfo, "Sub-Field for data set %d contains invalid data: %s" % (data_set_index, str(row)), 3)
                        return 'failed'
                        
                # Make sure Sub-Field has a module name
                if 'action' in row[1]: # Only apply to actions rows
                    for action_index in actions:
                        if actions[action_index]['module'] in row[1]: # If one of the modules is in the Sub-Field
                            module_test = True # Flag it's good
                            break
                    if module_test == False:
                        CommonUtil.ExecLog(sModuleInfo, "Sub-Field for data set %d is missing a module name: %s" % (data_set_index, str(row)), 3)
                        return 'failed'
                
                # Make sure Field has a valid action call
                if 'action' in row[1]: # Only apply to actions rows
                    for action_index in actions:
                        if actions[action_index]['name'] == row[0]: # If one of the action names in the Field
                            field_text = True # Flag it's good
                            break
                    if field_text == False:
                        CommonUtil.ExecLog(sModuleInfo, "Field for data set %d contains invalid data: %s" % (data_set_index, str(row)), 3)
                        return 'failed'

        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def adjust_element_parameters(step_data):
    ''' Strip out element parameters that do not match the dependency '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)
    
    # List of supported mobile platforms - must be lower case
    platforms = ('android', 'ios')
    
    # Get saved dependency
    if sr.Test_Shared_Variables('dependency') == False: # No dependency at all
        CommonUtil.ExecLog(sModuleInfo, "No dependency set - functions may not work properly if step data contains platform names", 2)
        return step_data # Return unmodified
    else: # Have dependency
        dependency = sr.Get_Shared_Variables('dependency') # Save locally
        if 'Mobile' not in dependency: # We have a dependency, but not a mobile, so we don't need to do anything
            CommonUtil.ExecLog(sModuleInfo, "No mobile dependency set - Can't verify element data", 0)
            return step_data # Return unmodified
            
    
    new_step_data = [] # Create empty list that will contain the data sets
    for data_set in step_data: # For each data set within step data
        new_data_set = [] # Create empty list that will have new data appended
        for row in data_set: # For each row of the data set
            new_row = list(row) # Copy tuple of row as list, so we can change it

            # Special handling of "id"
            for id_adj_row in data_set: # Find if this is an appium test step
                if 'appium' in id_adj_row[1]: # Yes, so adjust
                    if new_row[0] == 'id' and dependency['Mobile'].lower() == 'android': new_row[0] = 'resource-id' # If user specifies id, they likely mean "resource-id"
                    if new_row[0] == 'id' and dependency['Mobile'].lower() == 'ios': new_row[0] = 'accessibility id' # If user specifies id, they likely mean "resource-id" 
            
            # Remove any element parameter that doesn't match the dependency
            if dependency['Mobile'].lower() in new_row[1]: # If dependency matches this Sub-Field, then save it
                new_row[1] = new_row[1].replace(dependency['Mobile'].lower(),'').replace('  ', ' ').strip() # Remove word and clean up spaces 
                new_data_set.append(tuple(new_row)) # Append list as tuple to data set list
            else: # This dependency doesn't match. Figure out if this is an element parameter we don't want, or any other row we do want
                b = False
                for p in platforms: # For each platform
                    if p in new_row[1]: # If one of the platforms matches (we already found the one we want above, so this is for anything we don't want), then we don't want it 
                        b = True
                if b == False: # This row did not match unwanted platforms, so we keep it
                    new_data_set.append(tuple(new_row)) # Append list as tuple to data set list

        new_step_data.append(new_data_set) # Append data set to step data

    return new_step_data # Return cleaned step_data that contains only the element paramters we are interested in

def get_module_and_function(action_name, action_sub_field):
    ''' Function to split module from the action name, and with the action name tries to find the corrosponding function name '''
    
    function = ''
    module = ''
    try:
        
        action_list = action_sub_field.split(' ') # Split sub-field, so we can get moudle name from step data
        if action_list > 1: # Should be at least two words in the sub-field

            # Check if this action is a common action, so we can modify the module accordingly
            for i in actions:
                for j in actions[i]: # For each entry in the sub-dictionary
                    if actions[i]['module'] == 'common' and actions[i]['name'] == action_name:
                        module = 'common' # Set module as common
                        function = actions[i]['function'] # Save function
                        return module, function, action_list[0] # Return module and function name

            # Not a common function, so find the function matching the module
            module = action_list[0] # Module should be first item
            for i in actions: # For each dictionary in the dictionary
                for j in actions[i]: # For each entry in the sub-dictionary
                    if actions[i]['module'] == module and actions[i]['name'] == action_name: # Module and action name match
                        function = actions[i]['function'] # Save function
                        return module, function, '' # Return module and function name
        
        # Not enough words in the Sub-Field
        else:
            return '','' # Error handled in calling function
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def shared_variable_to_value(data_set):
    ''' Look for any Shared Variable strings in step data, convert them into their values, and return '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    new_data = [] # Rebuild the data_set with the new variable (because it's a list of tuples which we can't update)

    try:
        for row in data_set: # For each row of the data set
            data_row = list(row) # Convert row which is a tuple to a list, so we can update it if we need to
            for i in range(0, 3): # For each field (Field, Sub-Field, Value)
                if row[i] != False: # !!!! Probbly not needed
                    while "%|" in data_row[i] and "|%" in data_row[i]: # If string contains these characters, it's a shared variable
                        CommonUtil.ExecLog(sModuleInfo, "Shared Variable: %s" % row[i], 0)
                        data_row[i] = sr.get_previous_response_variables_in_strings(data_row[i])# replace just the variable name with it's value (has to be in string format)
            new_data.append(tuple(data_row)) # Convert row from list to tuple, and append to new data_set
        return new_data # Return parsed data_set
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


### *********************************** Begin common built in functions *************************************** ### 
# These functions are common with more than one of the BuiltInFunctions.py files (Selenium, Appium, REST, etc)

def step_result(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        action_value = ''
        for row in data_set:
            if row[0] == 'step result' and row[1] == 'action':
                action_value = row[2]
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())
    
    if action_value in failed_tag_list: # Convert user specified pass/fail into standard result
        return 'failed'
    elif action_value in skipped_tag_list:
        return 'skipped'
    elif action_value in passed_tag_list:
        return 'passed'
    else:
        CommonUtil.ExecLog(sModuleInfo, "Step Result action has invalid VALUE", 3)
        return 'failed'

def Sleep(data_set):
    ''' Sleep a specific number of seconds '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    try:
        seconds = int(data_set[0][2])
        CommonUtil.ExecLog(sModuleInfo, "Sleeping for %s seconds" % seconds, 1)
        time.sleep(seconds)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
