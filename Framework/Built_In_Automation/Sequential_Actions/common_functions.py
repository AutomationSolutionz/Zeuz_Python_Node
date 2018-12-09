'''
    Common Functions
    Function: Contains functions common to all modules, and helper functions for Sequential Actions
    
    Caveat: Functions common to multiple Built In Functions must have action names that are unique, because we search the common functions first, regardless of the module name passed by the user 
'''

import inspect, sys, time, collections
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr
from Framework.Built_In_Automation.Sequential_Actions.sequential_actions import actions, action_support
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list, skipped_tag_list # Allowed return strings, used to normalize pass/fail
from Framework.Built_In_Automation.Shared_Resources import LocateElement
from Framework import MainDriverApi
import datetime
from datetime import timedelta
months = ["Unknown",
          "January",
          "Febuary",
          "March",
          "April",
          "May",
          "Jun",
          "July",
          "August",
          "September",
          "October",
          "November",
          "December"]

unmask_characters={
    '{{1}}':'(',
    '{{2}}':')',
    '{{3}}':'[',
    '{{4}}':']',
    '{{5}}':',',
    '{{6}}':'#',
    '{{7}}':"'",
    '{{8}}':'%',
    '{{9}}':'|'
}

def unmask_string(givenText):
    for e in unmask_characters.keys():
        givenText=givenText.replace(e,unmask_characters[e])
    return givenText

def unmask_step_data(step_data):
    '''
    unmasks the special characters sent from servers
    :param step_data:
    :return: new step data
    '''
    try:
        new_step_data = []  # Create empty list that will contain the data sets
        for data_set in step_data:  # For each data set within step data
            new_data_set = []  # Create empty list that will have new data appended
            for row in data_set:  # For each row of the data set
                new_row = []
                for each in row:
                    new_row.append(unmask_string(each))
                new_data_set.append(tuple(new_row))  # Append list as tuple to data set list
            new_step_data.append(new_data_set)  # Append data set to step data
        return new_step_data  # Step data is now clean and in the same format as it arrived in
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def sanitize(step_data):
    ''' Sanitize step data Field and Sub-Field '''
    ''' Usage:
            Is to be used to allow users flexibility in their step data input, but allow the program to find key words
            :valid_chars: By default this function removes all characters. Specifying a string of characters here will skip removing them
            :clean_whitespace_only: If your function uses several characters, you can set this to True, to only clean up white space
            If the user surrounds their input with double quotes, all sanitizing will be skipped, and the surrounding quotes will be removed
    '''
    
    try:
        # Set columns in the step data to sanitize (default is Field and Sub-Field only)
        column = [0,1,2]

        
        # Invalid character list (space and underscore hare handle separately)
        invalid_chars = '!"#$%&\'()*+,-./:;<=>?@[\]^`{|}~'
    
        # Adjust invalid character list, based on function input
    
        new_step_data = [] # Create empty list that will contain the data sets
        for data_set in step_data: # For each data set within step data
            new_data_set = [] # Create empty list that will have new data appended
            for row in data_set: # For each row of the data set
                new_row = list(row) # Copy tuple of row as list, so we can change it
                for i in column: # Sanitize the specified columns
                    if str(new_row[i])[:1] == '"' and str(new_row[i])[-1:] == '"': # String is within double quotes, indicating it should not be changed
                        new_row[i] = str(new_row[i])[1:len(new_row[i]) - 1] # Remove surrounding quotes
                        continue # Do not change string
    
                    new_row[i] = new_row[i].replace('  ', ' ') # Double space to single space
                    new_row[i] = new_row[i].strip() # Remove leading and trailing whitespace
                new_data_set.append(tuple(new_row)) # Append list as tuple to data set list
            new_step_data.append(new_data_set) # Append data set to step data
        return new_step_data # Step data is now clean and in the same format as it arrived in
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def verify_step_data(step_data):
    ''' Verify step data is valid '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Verifying Step Data", 1)
    
    try:
        data_set_index = 0
        for data_set in step_data:
            data_set_index += 1
            module_test = False
            field_text = False
            
            # Check each data set
            if len(data_set) == 0:
                CommonUtil.ExecLog(sModuleInfo, "Data set %d cannot be empty" % data_set_index, 3)
                return 'failed'
            
            # Check each row
            action = False # used to ensure there is an action for each data set
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
                    action = True
                    if 'custom' in row[1]: continue # Skip custom actions - they do not require a module
                    for action_index in actions:
                        if actions[action_index]['module'] in row[1]: # If one of the modules is in the Sub-Field
                            module_name = actions[action_index]['module'] # Save this for the "Field" check below
                            module_test = True # Flag it's good
                            break
                    if module_test == False:
                        CommonUtil.ExecLog(sModuleInfo, "Sub-Field for data set %d is missing a module name: %s" % (data_set_index, str(row)), 3)
                        return 'failed'
                
                # Make sure Field has a valid action call
                if 'action' in row[1] and 'loop' in row[1]: # Loop action, do not check because there could be different formats
                    continue
                elif 'custom' in row[1]:# Skip custom actions - they do not execute like other actions
                    continue
                elif 'action' in row[1] and 'conditional' not in row[1]: # Only apply to actions rows
                    for action_index in actions:
                        if (actions[action_index]['name'] == row[0] and actions[action_index]['module'] == module_name) or (actions[action_index]['name'] == row[0] and actions[action_index]['module'] == 'common') or str(row[0]).startswith('%|'): # If one of the action names in the Field
                            field_text = True # Flag it's good
                            break
                    if field_text == False:
                        CommonUtil.ExecLog(sModuleInfo, "Field for data set %d contains invalid data: %s" % (data_set_index, str(row)), 3)
                        return 'failed'
                    
                # Make sure recall result row contains valid commands and shared variables
                elif row[1] == 'result':
                    if row[0].strip().lower() not in ('store', 'recall'):
                        CommonUtil.ExecLog(sModuleInfo, "Field for data set %d contains invalid data: %s - expected either 'recall' or 'store'" % (data_set_index, str(row)), 3)
                        return 'failed'
                    elif row[0].strip().lower() == 'recall' and '%|' not in row[2].strip():
                        CommonUtil.ExecLog(sModuleInfo, "Field for data set %d contains invalid data: %s - expected Shared Variable in the proper format. Eg: %%|VAR|%%" % (data_set_index, str(row)), 3)
                        return 'failed'
                    
            # Make sure each data set has an action row
            if action == False:
                CommonUtil.ExecLog(sModuleInfo, "Data set %d is missing an action line, or it's misspelled" % data_set_index, 3)
                return 'failed'

        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def check_action_types(module, step_data):
    ''' Check for a specific module in the step data type and return true/false '''
    # To be used when we don't have a dependency, and need to know the type of actions the user have specified
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    for data_set in step_data:
        for row in data_set:
            subfield = row[1].lower()
            if module in subfield:
                return True
    return False


def adjust_element_parameters(step_data, platforms):
    ''' Strip out element parameters that do not match the dependency '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)
    
    # Get saved dependency and verify if we have the correct dependency
    if sr.Test_Shared_Variables('dependency') == False: # No dependency at all
        if check_action_types('Mobile', step_data) == True:
            CommonUtil.ExecLog(sModuleInfo, "No dependency set - functions may not work properly if step data contains platform names", 3)
            return 'failed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Not a mobile Test Case", 0)
            return step_data # Return unmodified
    else: # Have dependency
        dependency = sr.Get_Shared_Variables('dependency') # Save locally
        if 'Mobile' not in dependency: # We have a dependency, but not a mobile, so we don't need to do anything
            if check_action_types('Mobile', step_data) == False: # No mobile actions in step data
                CommonUtil.ExecLog(sModuleInfo, "Not a mobile Test Case", 0)
                return step_data
            else: # Mobile actions in step data
                CommonUtil.ExecLog(sModuleInfo, "Mobile (Appium) actions found in Step Data, but no Mobile dependency set", 3)
                return 'failed' # Return unmodified
    
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
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    function = ''
    module = ''
    try:
        action_list = action_sub_field.split(' ') # Split sub-field, so we can get moudle name from step data
        if action_list > 1: # Should be at least two words in the sub-field
            # Find the function matching the module (decide later if we need it or not)
            for item in action_list: # Loop through split string
                for action_index in actions:
                    if actions[action_index]['module'] == item: # Found the matching module
                        module = item # Save it
                        break
                if module != '': break

            # Check if this action is a common action, so we can modify the module accordingly
            for i in actions:
                for j in actions[i]: # For each entry in the sub-dictionary
                    if actions[i]['module'] == 'common' and actions[i]['name'] == action_name:
                        # Now we'll overwrite the module with the common module, and continue as normal
                        original_module = module
                        module = 'common' # Set module as common
                        function = actions[i]['function'] # Save function
                        return module, function, original_module # Return module and function name

            for i in actions: # For each dictionary in the dictionary
                for j in actions[i]: # For each entry in the sub-dictionary
                    if actions[i]['module'] == module and actions[i]['name'] == action_name: # Module and action name match
                        function = actions[i]['function'] # Save function
                        return module, function, '' # Return module and function name
            
            CommonUtil.ExecLog(sModuleInfo, "Could not find module or action_name is invalid", 3)
            return '','','' # Should never get here if verify_step_data() works properly
        # Not enough words in the Sub-Field
        else:
            return '','','' # Error handled in calling function
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def shared_variable_to_value(data_set):
    ''' Look for any Shared Variable strings in step data, convert them into their values, and return '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    new_data = [] # Rebuild the data_set with the new variable (because it's a list of tuples which we can't update)

    try:
        for row in data_set:
            if row[1] == 'action':
                if row[0] == 'compare variable': #for compare variable don't replace.. we will need the variable name
                    return data_set
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
# How it works: We do not require the user to specify "common" in the action row. They just use whatever module they 
# built the rest of the data set with, so as to make it easy for them. When action_handler() gets the data set, it
# first searches the actions dictionary for any common actions that match the name provided by the user. If found,
# it will remove the module the user specified, replace it with the "common" module, and continue as normal.

def step_result(data_set):
    ''' Returns passed/failed in the standard format, when the user specifies it in the step data '''
    
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

def step_exit(data_set):
    ''' Exits a Test Step wtih passed/failed in the standard format, when the user specifies it in the step data '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    try:
        action_value = ''
        for row in data_set:
            if row[0] == 'step exit' and row[1] == 'action':
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
        CommonUtil.ExecLog(sModuleInfo, "Sleeping for %d seconds" % seconds, 1)
        time.sleep(seconds)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Wait_For_Element(data_set):
    ''' Continuously monitors an element for a specified amount of time and returns pass when it's state is changed '''
    # Handles two types:
    # wait: Wait for element to appear/available
    # wait disable: Wait for element to disappear/hide
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Get webdriver
    if sr.Test_Shared_Variables('common_driver'):
        common_driver = sr.Get_Shared_Variables('common_driver')
    else:
        CommonUtil.ExecLog(sModuleInfo, "Could not dynamically locate correct driver. You either did not initiate it with a valid action that populates it, or you called this function with a module name that doesn't support this function", 3)
        return 'failed' 
    
    try:
        wait_for_element_to_disappear = False
        
        # Find the wait time from the data set
        for row in data_set:
            if row[1] == "action":
                if row[0] == 'wait disable': wait_for_element_to_disappear = True
                timeout_duration = int(row[2])
       
        # Check for element every second 
        end_time = time.time() + timeout_duration # Time at which we should stop looking
        for i in range(timeout_duration): # Keep testing element until this is reached (likely never hit due to timeout below)
            # Wait and then test if we are over our alloted time limit
            if time.time() >= end_time: # Keep testing element until this is reached (ensures we wait exactly the specified amount of time)
                break
            time.sleep(1)

            # Test if element exists or not
            Element = LocateElement.Get_Element(data_set, common_driver, wait_enable = False)
            
            # Check if element exists or not, depending on the type of wait the user wanted
            if wait_for_element_to_disappear == False: # Wait for it to appear
                if Element not in failed_tag_list: # Element found
                    CommonUtil.ExecLog(sModuleInfo, "Found element", 1)
                    return 'passed'
                else: # Element not found, keep waiting
                    CommonUtil.ExecLog(sModuleInfo, "Element does not exist. Sleep and try again - %d" % i, 0)
            else: # Wait for it to be removed/hidden/disabled
                if Element in failed_tag_list: # Element removed
                    CommonUtil.ExecLog(sModuleInfo, "Element disappeared", 1)
                    return 'passed'
                else: # Element found, keep waiting
                    CommonUtil.ExecLog(sModuleInfo, "Element still exists. Sleep and try again - %d" % i, 0)

        # Element status not changed after time elapsed, to exit with failure        
        CommonUtil.ExecLog(sModuleInfo, "Wait for element failed", 3)
        return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Save_Text(data_set):
    ''' Save the text from the given element to shared variables under the variable name provided '''
     
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Get webdriver
    if sr.Test_Shared_Variables('common_driver'):
        common_driver = sr.Get_Shared_Variables('common_driver')
    else:
        CommonUtil.ExecLog(sModuleInfo, "Could not dynamically locate correct driver. You either did not initiate it with a valid action that populates it, or you called this function with a module name that doesn't support this function", 3)
        return 'failed' 

    # Parse data set
    try:
        variable_name = ''
        for row in data_set:
            if row[1] == 'action':
                variable_name = row[2] # Save action Value as the shared variable name
        if variable_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Missing variable name to save text as from Value field on action line", 3)
            return 'failed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Find element
    Element = LocateElement.Get_Element(data_set, common_driver)
    if Element in failed_tag_list:
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
        return "failed" 
        
    try:
        # !!! Seems like a really round about way of just removing \n. Why not use replace()?
        list_of_element_text = Element.text.split('\n') # Split multi-line text
        visible_list_of_element_text = ""
        for each_text_item in list_of_element_text: # For each line of text
            if each_text_item != "":
                #visible_list_of_element_text+=each_text_item # Append each line into one string
                tmp = [c for c in each_text_item if 0 < ord(c) < 127] # Strip any binary characters
                visible_list_of_element_text += ''.join(tmp) # Append each line into one string

        result = sr.Set_Shared_Variables(variable_name, visible_list_of_element_text) # Save element text into shared variable using name given by user
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Value of Variable '%s' could not be saved" % variable_name, 3)
            return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Element text saved", 1)
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error reading and saving element text")

def Compare_Variables(data_set):
    ''' Compare shared variables / strings to eachother '''
    # Compares two variables from Field and Value on any line that is not the action line
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    return sr.Compare_Variables([data_set])

def Initialize_List(data_set):
    ''' Prepares an empty list in shared variables '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    return sr.Initialize_List([data_set])

def Initialize_Dict(data_set):
    ''' Prepares an empty dict in shared variables '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    return sr.Initialize_Dict([data_set])

def Compare_Lists_or_Dicts(data_set):
    ''' Compare two lists stored in shared variables '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    return sr.Compare_Lists_or_Dicts([data_set])

def Save_Variable(data_set):
    ''' Assign a value to a variable stored in shared variables '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    variable_name = ''
    variable_value = ''
    for each in data_set:
        if each[1] == 'element parameter':
            variable_name = each[0]
            variable_value = each[2]
    if variable_name != '' and variable_value != '':
        return sr.Set_Shared_Variables(variable_name,variable_value)
    else:
        return 'failed'
def Save_Current_Time(data_set):
    ''' Assign a value to a variable stored in shared variables '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    variable_name = ''
    variable_value = ''
    time=''
    now_hour=0.00
    now = datetime.datetime.now()
    for each in data_set:
        if each[1] == 'element parameter':
            variable_name = each[0]
            if(now.hour>=12):
                time="PM"
            else:
                time="AM"

            if(now.hour >12):
                now_hour=now.hour-12
            else:
                now_hour=now.hour

            variable_value = str(months[now.month])+" "+str(now.day)+", "+str(now.year)+", "+str(now_hour)+":"+str(now.minute)+" "+time
            print variable_value
    if variable_name != '' and variable_value != '':
        return sr.Set_Shared_Variables(variable_name,variable_value)
    else:
        return 'failed'

    
def delete_all_shared_variables(data_set):
    ''' Delete all shared variables - Wrapper for Clean_Up_Shared_Variables() '''
    # To delete only one, use the action "save variable", and set it to an empty string
    # Takes no inputs
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    try:
        return sr.Clean_Up_Shared_Variables()
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def append_list_shared_variable(data_set):
    ''' Creates and appends a python list variable '''
    # Note: List is created if it doesn't already exist
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    try:
        # Parse data set
        tmp = data_set[0][2].strip() # Get key and value from Value field and clean them
        shared_var = tmp.split('=')[0].strip() # Get variable name
        tmp = tmp.replace(shared_var, '').strip().replace('=', '', 1)
        values = tmp.split(',') # Get values (could be several)
        
        # Append all values
        for value in values:
            result = sr.Append_List_Shared_Variables(shared_var, value.strip())
        return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def append_dict_shared_variable(data_set):
    ''' Creates and appends a python dict variable '''
    # Note: List is created if it doesn't already exist

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    try:
        # Parse data set
        tmp = data_set[0][2].strip()  # Get key and value from Value field and clean them
        shared_var = tmp.split('=')[0].strip()  # Get variable name
        tmp = tmp.replace(shared_var, '').strip().replace('=', '', 1)
        values = tmp.split(',')  # Get values (could be several)

        # Append all values
        for value in values:
            k = ''
            v = ''
            value = str(value).split(":")
            k=str(value[0]).strip()
            v=str(value[1]).strip()
            value = collections.OrderedDict()
            value[k] = v
            result = sr.Append_Dict_Shared_Variables(shared_var, value)
        return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def insert_list_into_another_list(data_set):
    ''' Creates and appends a python list variable '''
    # Note: List is created if it doesn't already exist

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    try:
        # Parse data set
        tmp = data_set[0][2].strip()  # Get key and value from Value field and clean them
        tmp = tmp.split('=')  # Get variable name
        parent_list_name = tmp[0].strip()
        if ";" in str(tmp[1]): #direct initialization parent_list = [[a,b,c],[x,y,z]]
            parent_list_splitted_by_semicolon = str(tmp[1]).strip().split(";")
            for each_split in parent_list_splitted_by_semicolon:
                child_list_raw = each_split.strip().split(",")
                child_list = []
                for element in child_list_raw:
                    child_list.append(element.strip())
                result = sr.Append_List_Shared_Variables(parent_list_name, child_list, value_as_list=True)
                if result in failed_tag_list:
                    return result
        else: #normal insert parent_list = [list1,list2]
            all_child_list_names = tmp[1].strip().split(",")

            for child_list_name in all_child_list_names:
                if not sr.Test_Shared_Variables(child_list_name):
                    CommonUtil.ExecLog(sModuleInfo, "List named %s not found in shared variables" % child_list_name, 3)
                    return "failed"
                child_list = sr.Get_Shared_Variables(child_list_name)
                # Append all values
                result = sr.Append_List_Shared_Variables(parent_list_name, child_list,value_as_list=True)
                if result in failed_tag_list:
                    return result
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def insert_dict_into_another_dict(data_set):
    ''' Creates and appends a python list variable '''
    # Note: List is created if it doesn't already exist

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    try:
        # Parse data set
        tmp = data_set[0][2].replace(' ', '').strip()  # Get key and value from Value field and clean them
        tmp = tmp.split('=')  # Get variable name
        parent_dict_name = tmp[0].strip()
        all_child_dict_names = tmp[1].strip().split(",")

        for child_dict_name in all_child_dict_names:
            splitted_text = str(child_dict_name).split(":")
            key = str(splitted_text[0]).strip()
            dict_name = str(splitted_text[1]).strip()

            if not sr.Test_Shared_Variables(dict_name):
                CommonUtil.ExecLog(sModuleInfo, "Dict named %s not found in shared variables" % dict_name, 3)
                return "failed"
            child_dict = sr.Get_Shared_Variables(dict_name)
            # Append all values
            result = sr.Append_Dict_Shared_Variables(key, child_dict,parent_dict=parent_dict_name)
            if result in failed_tag_list:
                return result
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())



def sequential_actions_settings(data_set):
    ''' Test Step front end for modifying certain variables used by Sequential Actions '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    try:
        # Parse data set
        tmp = data_set[0][2].replace(' ', '').strip() # Get key and value from Value field and clean them
        shared_var = tmp.split('=')[0].strip().lower() # Retrieve variable name
        value = tmp.replace(shared_var + '=', '').strip() # Retrieve value for variable
        
        # Verify this is a real variable (should be set somewhere else)
        if not sr.Test_Shared_Variables(shared_var):
            CommonUtil.ExecLog(sModuleInfo,"The variable name specified (%s) is not a valid Sequential Action variable" % str(shared_var), 3)
            return 'failed'
        
        # Save variable - all functions that use this variable will now use the new value
        CommonUtil.ExecLog(sModuleInfo,"Changing Sequential Action setting of %s from %s to %s" % (str(shared_var), str(sr.Get_Shared_Variables(shared_var)), str(value)), 1)
        return sr.Set_Shared_Variables(shared_var, value)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def print_shared_variables():
    for each in sr.shared_variables:
        print each + " : " +str(sr.shared_variables[each])


def set_server_variable(data_set):
    #can set multiple server variable with one action
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        run_id = sr.Get_Shared_Variables('run_id')

        for row in data_set:
            if str(row[1]).strip().lower() == 'element parameter':
                key = str(row[0]).strip()
                value = str(row[2]).strip()
                #call main driver to send var to server
                MainDriverApi.set_server_variable(run_id,key,value)

        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def get_server_variable(data_set):
    # can get multiple server variable with one action
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        run_id = sr.Get_Shared_Variables('run_id')

        for row in data_set:
            if str(row[1]).strip().lower() == 'element parameter':
                key = str(row[0]).strip()

                dict = MainDriverApi.get_server_variable(run_id,key)
                for key in dict:
                    sr.Set_Shared_Variables(key, dict[key])
                    CommonUtil.ExecLog(sModuleInfo, "Got server variable %s='%s'" % (key, dict[key]), 1)

        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def get_server_variable_and_wait(data_set):
    # can get multiple server variable with one action
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        run_id = sr.Get_Shared_Variables('run_id')

        key=''
        wait_time=5
        for row in data_set:
            if str(row[1]).strip().lower() == 'element parameter':
                key = str(row[0]).strip()
            if str(row[1]).strip().lower() == 'action':
                wait_time = int(str(row[2]).strip())

        i = 1
        dict = {}
        while i <= wait_time:
            CommonUtil.ExecLog(sModuleInfo,"Waiting for server variable '%s'"%key,1)
            dict = MainDriverApi.get_server_variable(run_id,key)
            try:
                if key in dict and dict[key] != 'null':
                    break
                else:
                    time.sleep(1)
            except:
                pass
            i+=1

        if key in dict and dict[key] != 'null':
            sr.Set_Shared_Variables(key, dict[key])
            CommonUtil.ExecLog(sModuleInfo, "Got server variable %s='%s'" % (key, dict[key]), 1)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Couldn't get server variable %s again" % (key), 3)
            return "failed"

        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def get_all_server_variable(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        run_id = sr.Get_Shared_Variables('run_id')

        dict = MainDriverApi.get_all_server_variable(run_id)
        for key in dict:
            sr.Set_Shared_Variables(key, dict[key])
            CommonUtil.ExecLog(sModuleInfo, "Got server variable %s='%s'" % (key, dict[key]), 1)
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def start_timer(data_set):
    ''' Test Step front end for modifying certain variables used by Sequential Actions '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    try:
        # Parse data set
        try:
            seconds = int(str(data_set[0][2]).strip())  # Get no. of seconds for timer
        except:
            seconds = 0

        CommonUtil.ExecLog(sModuleInfo, "Starting timer", 1)

        if seconds>=0:
            return sr.Set_Shared_Variables("timer", datetime.datetime.now() - timedelta(seconds=seconds))
        else:
            return sr.Set_Shared_Variables("timer", datetime.datetime.now() + timedelta(seconds=abs(seconds)))
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def wait_for_timer(data_set):
    ''' Test Step front end for modifying certain variables used by Sequential Actions '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function Start", 0)

    try:
        seconds_to_wait = int(str(data_set[0][2]).strip())
        # Parse data set
        start_time = sr.Get_Shared_Variables("timer")
        if start_time in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Timer wasn't started, please start timer first",3)

        delta = datetime.datetime.now() - start_time
        delta = int(delta.total_seconds())

        if delta>seconds_to_wait:
            CommonUtil.ExecLog(sModuleInfo, "Timer have expired before the execution was completed", 3)
            return "failed"

        sleep_time = seconds_to_wait - delta
        CommonUtil.ExecLog(sModuleInfo, "%d seconds remaining for timer"%sleep_time, 1)
        CommonUtil.ExecLog(sModuleInfo, "Will wait for %d seconds"%sleep_time, 1)
        time.sleep(sleep_time)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())