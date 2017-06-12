'''
    Common Functions
    Function: Contains functions common to all modules 
'''

import inspect, sys, time
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr

# Allowed return strings, used to normalize pass/fail
passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True','1','Success','success','SUCCESS',True]
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE','0',False]
skipped_tag_list=['skip','SKIP','Skip','skipped','SKIPPED','Skipped']

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
        for data_set in step_data:
            for row in data_set:
                if len(row[0]) == 0:
                    CommonUtil.ExecLog(sModuleInfo, "Data Set Field is empty", 3)
                    return 'failed'
                elif len(row[1]) == 0:
                    CommonUtil.ExecLog(sModuleInfo, "Data Set Sub-Field is empty", 3)
                    return 'failed'
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def adjust_element_parameters(step_data):
    ''' Strip out element parameters that do not match the dependency '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Adjusting element parameters", 1)
    
    # List of supported mobile platforms - must be lower case
    platforms = ('android', 'ios')
    
    # Get saved dependency
    if sr.Test_Shared_Variables('dependency') == False: # No dependency
        CommonUtil.ExecLog(sModuleInfo, "No dependency set - functions may not work properly if step data contains platform names", 2)
        return step_data # Return unmodified
    dependency = sr.Get_Shared_Variables('dependency')
    print dependency
    
    new_step_data = [] # Create empty list that will contain the data sets
    for data_set in step_data: # For each data set within step data
        new_data_set = [] # Create empty list that will have new data appended
        for row in data_set: # For each row of the data set
            new_row = list(row) # Copy tuple of row as list, so we can change it
            
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

