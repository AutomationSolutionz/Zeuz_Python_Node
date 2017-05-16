'''
    Common Functions
    Function: Contains functions common to all modules 
'''

import inspect, sys, time
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources

# Allowed return strings, used to normalize pass/fail
passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True','1','Success','success','SUCCESS',True]
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE','0',False]

def sanitize(step_data):
    ''' Sanitize step data Field and Sub-Field ''' 
    for each in step_data: # For each data set within step data
        for row in each: # For each row of the data set
            for i in range(0, 2): # For first 2 fields (Field, Sub-Field)
                row[i] = row[i].replace('  ', ' ')
                row[i] = row[i].replace('_', ' ')
    return step_data


