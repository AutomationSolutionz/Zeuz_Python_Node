'''
    Common Functions
    Function: Contains functions common to all modules 
'''

import inspect, sys, time
from Framework.Utilities import CommonUtil

# Allowed return strings, used to normalize pass/fail
passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True','1','Success','success','SUCCESS',True]
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE','0',False]
skipped_tag_list=['skip','SKIP','Skip','skipped','SKIPPED','Skipped']

def sanitize(step_data):
    ''' Sanitize step data Field and Sub-Field '''
    # Needs to be updated to allow underscores in certain areas, and to handle more types of invalid data
    
    new_step_data = [] # Create empty list that will contain the data sets
    for data_set in step_data: # For each data set within step data
        new_data_set = [] # Create empty list that will have new data appended
        for row in data_set: # For each row of the data set
            new_row = list(row) # Copy tuple of row as list, so we can change it
            for i in range(0, 2): # For first 2 fields (Field, Sub-Field)
                new_row[i] = new_row[i].replace('  ', ' ') # Double space to single space
                new_row[i] = new_row[i].replace('_', ' ') # Replace underscore with single space
                new_row[i] = new_row[i].strip() # Remove leading and trailing whitespace
                new_row[i] = new_row[i].lower() # Convert to lower case
            new_data_set.append(new_row) # Append list as tuple to data set list
        new_step_data.append(new_data_set) # Append data set to step data
    return step_data # Step data is now clean and in the same format as it arrived in


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


def step_result(data_set):
    ''' Process what the user specified as the outcome with step result '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Verifying step data", 1)
    
    # Parse data set
    try:
        action_value = ''
        for row in data_set: # Find required data
            if row[0] == 'step result':
                action_value = row[2]
        if action_value == '':
            CommonUtil.ExecLog(sModuleInfo,"Could not find step result", 3)
            return 'failed'
    except Exception:
        errMsg = "Unable to parse data set"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    if action_value in failed_tag_list: # Convert user specified pass/fail into standard result
        result = 'failed'
    elif action_value in passed_tag_list:
        result = 'passed'
    elif action_value in skipped_tag_list:
        result = 'skipped'
    return result


