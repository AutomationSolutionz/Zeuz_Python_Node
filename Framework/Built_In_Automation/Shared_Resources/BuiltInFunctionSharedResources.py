# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

# shared_variables

import inspect,sys,time
import string
import random
from Framework.Utilities import CommonUtil
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list
from datetime import datetime
from dateutil.relativedelta import relativedelta

global shared_variables
shared_variables = {}
protected_variables = [] # Used to ensure internally used shared variables can't be overwritten by step data


def Set_Shared_Variables(key, value, protected = False):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables, protected_variables
        if key == '' or key == None or value == '' or value == None:  # if input is invalid
            return "failed"
        else: # Valid input
            if protected: protected_variables.append(key) # Add to list of protected variables
            else: # Check if user is trying to overwrite a protected variable
                if key in protected_variables: # If we find a match, exit with failure
                    CommonUtil.ExecLog(sModuleInfo, "Error: You tried to overwrite protected variable '%s'. Please choose a different variable name." % key, 3)
                    return 'failed'
            
            # Good to proceed
            shared_variables[key] = value
            CommonUtil.ExecLog(sModuleInfo, "Variable value of '%s' is set as: %s" % (key, value), 0)
            return "passed"
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Set_List_Shared_Variables(list_name, key, value, protected = False):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables, protected_variables
        if key == '' or key == None or value == '' or value == None or list_name == '' or list_name == None:  # if input is invalid
            return "failed"
        else: # Valid input
            if protected: protected_variables.append(key) # Add to list of protected variables
            else: # Check if user is trying to overwrite a protected variable
                if key in protected_variables: # If we find a match, exit with failure
                    CommonUtil.ExecLog(sModuleInfo, "Error: You tried to overwrite protected variable '%s'. Please choose a different variable name." % key, 3)
                    return 'failed'
            
            # Good to proceed
            if list_name in shared_variables:
                shared_variables[list_name][key] = value
                CommonUtil.ExecLog(sModuleInfo, "In List '%s' Variable value of '%s' is set as: %s" % (list_name, key, value), 0)
                return "passed"
            else: #create dict if now available
                shared_variables[list_name] = {}
                shared_variables[list_name][key] = value
                CommonUtil.ExecLog(sModuleInfo,
                                   "In List '%s' Variable value of '%s' is set as: %s" % (list_name, key, value), 0)
                return "passed"
    except:
        CommonUtil.Exception_Handler(sys.exc_info())

def Append_List_Shared_Variables(key, value, protected = False):
    ''' Creates and appends a python list variable '''
    
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables, protected_variables
        
        # Verify input
        key = key.strip()
        value = value.strip()
        if key == '' or value == '':
            return 'failed'

        # Check if protected
        if protected: protected_variables.append(key) # Add to list of protected variables
        else: # Check if user is trying to overwrite a protected variable
            if key in protected_variables: # If we find a match, exit with failure
                CommonUtil.ExecLog(sModuleInfo, "Error: You tried to overwrite protected variable '%s'. Please choose a different variable name." % key, 3)
                return 'failed'
            
        # Create list if non-existent
        if not key in shared_variables:
            CommonUtil.ExecLog(sModuleInfo, "Creating new list", 0)
            shared_variables[key] = []

        if key in shared_variables and shared_variables[key] == {}: #if initialized as a dict through "Initialize List" action, convert it to list
            shared_variables[key] = []
        
        # Append list
        shared_variables[key].append(value)
        CommonUtil.ExecLog(sModuleInfo, "Appending list %s with %s. Now is: %s" % (str(key), str(value), str(shared_variables[key])), 0)
        return 'passed'
            
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Get_Shared_Variables(key):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if key == '' or key == None:  # if input is invalid
            return "failed"
        else:
            if key in shared_variables:
                value = shared_variables[key]
                CommonUtil.ExecLog(sModuleInfo, "Variable value of '%s' is: %s" % (str(key), value), 0)
                return value
            else:
                CommonUtil.ExecLog(sModuleInfo, "No Such variable named '%s' found in shared variables" % key, 3)
                return "failed"
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Get_List_from_Shared_Variables(list_name):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if list_name == '' or list_name == None:  # if input is invalid
            return "failed"
        else:
            if list_name in shared_variables:
                list = shared_variables[list_name]
                CommonUtil.ExecLog(sModuleInfo, "List: " + list_name + " is: " + str(list), 1)
                return list
            else:
                CommonUtil.ExecLog(sModuleInfo, "List named %s does not exist on shared variables" % list_name, 3)
                return "failed"
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Remove_From_Shared_Variables(key):
    ''' Remove if a variable already exists and return the value or false '''

    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if key == '' or key == None:  # if input is invalid
            return "failed"
        else:  # Valid input
            return shared_variables.pop(key,"failed")
    except:
        CommonUtil.Exception_Handler(sys.exc_info())



def Test_Shared_Variables(key):
    ''' Test if a variable already exists and return true or false '''

    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if key == '' or key == None:  # if input is invalid
            return "failed"
        else:  # Valid input
            if key in shared_variables:  # Test if key/variable exists
                CommonUtil.ExecLog(sModuleInfo, "Variable %s exists" % key, 0)
                return True
            else:
                CommonUtil.ExecLog(sModuleInfo, "No Such variable named '%s' found in shared variables" % key, 0)
                return False
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Show_All_Shared_Variables():
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if len(shared_variables) > 0:
            CommonUtil.ExecLog(sModuleInfo, "##Shared Variable Fields with Value##", 1)
            for each in shared_variables:
                CommonUtil.ExecLog(sModuleInfo, "%s : %s" % (each, shared_variables[each]), 1)
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Handle_Step_Data_Variables(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        changed_step_data = []
        for dataset in step_data:
            changed_dataset = []
            for row in dataset:
                changed_row = []
                for each in row:
                    if each == True or each == False or each == '':
                        changed_row.append(each)
                    else:
                        if '|%' in each:
                            replaced_value = get_previous_response_variables_in_strings(each)
                            if replaced_value in failed_tag_list:
                                CommonUtil.ExecLog(sModuleInfo, "Step Data Format Not Appropriate", 3)
                                return 'failed'
                            else:
                                changed_row.append(replaced_value)
                        else:
                            changed_row.append(each)
                changed_dataset.append(changed_row)
            changed_step_data.append(changed_dataset)
        return changed_step_data
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def get_previous_response_variables_in_strings(step_data_string_input):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get previous response variables in strings", 0)
    try:
        changed = False
        input = step_data_string_input
        all_parse = input.split('%|')
        output = ''
        for each in all_parse:
            if '|%' in each:
                changed = True
                parts = each.split('|%')
                if str(parts[0]).startswith('random_string'):
                    full_string = str(parts[0])
                    random_string = ''
                    if '(' in full_string:
                        temp = full_string.split('(')
                        params = temp[1].split(')')[0]
                        if ',' in params:
                            list_of_params = params.split(',')
                            random_string = random_string_generator(list_of_params[0].strip(),
                                                                    int(list_of_params[1].strip()))
                        else:
                            if params.strip() == '':
                                random_string = random_string_generator()
                            else:
                                random_string = random_string_generator(params.strip())
                    else:
                        return "failed"

                    if random_string in failed_tag_list:
                        return "failed"

                    output += random_string
                    CommonUtil.ExecLog(sModuleInfo, 'Replacing variable "%s" with its value "%s"' % (parts[0], random_string), 0)
                elif str(parts[0]).lower().startswith('today') or str(parts[0]).startswith('currentEpochTime'):
                    replaced_string = save_built_in_time_variable(str(parts[0]))
                    if replaced_string in failed_tag_list:
                        CommonUtil.ExecLog(sModuleInfo, "No such date variable named '%s', user formats like %%|today|%% , %%|today + 1d|%% , %%|today - 3m|%% , %%|today + 1w|%%, %%|today + 2y|%% , %%|currentEpochTime|%% etc." % parts[0], 3)
                        return "failed"
                    output += str(save_built_in_time_variable(str(parts[0])))
                    CommonUtil.ExecLog(sModuleInfo, 'Replacing variable "%s" with its value "%s"' % (parts[0], replaced_string), 0)
                else:
                    var_value = Get_Shared_Variables(parts[0])
                    if var_value == 'failed':
                        CommonUtil.ExecLog(sModuleInfo, "No such variable named '%s' in shared variables list" % parts[0], 3)
                        return "failed"
                    else:
                        output += str(var_value)
                        CommonUtil.ExecLog(sModuleInfo, 'Replacing variable "%s" with its value "%s"' % (parts[0], var_value), 0)
                output += parts[1]
            else:
                output += each
        if changed == True:
            CommonUtil.ExecLog(sModuleInfo, "Input string is changed by variable substitution", 0)
            CommonUtil.ExecLog(sModuleInfo, "Input string before change: %s" % input, 0)
            CommonUtil.ExecLog(sModuleInfo, "Input string after change: %s" % output, 0)

        return output

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def random_string_generator(pattern='nluc', size=10):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: random string generator", 0)
    try:
        pattern = pattern.lower().strip()
        punctuation = '`~!@#$%^&.'
        chars = ''
        for index in range(0, len(pattern)):
            if pattern[index] == 'n':
                chars += string.digits
            if pattern[index] == 'l':
                chars += string.ascii_lowercase
            if pattern[index] == 'u':
                chars += string.uppercase
            if pattern[index] == 'c':
                chars += punctuation

        if chars == '':
            return 'failed'
        else:
            return ''.join(random.choice(chars) for _ in range(size))
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Validating text from an element given information regarding the expected text
def Compare_Variables(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Variables", 0)
    try:
        pass_count = 0
        fail_count = 0
        variable_list1 = []
        variable_list2 = []
        result = []
        modifier = False
        for each_step_data_item in step_data[0]:
            if each_step_data_item[1] == "compare" or each_step_data_item[1] == "element parameter":
                if '%|' in each_step_data_item[0].strip():
                    previous_name = each_step_data_item[0].strip()
                    new_name = get_previous_response_variables_in_strings(each_step_data_item[0].strip())
                    tuple1 = ('Variable',"'%s'"%previous_name,new_name)
                else:
                    tuple1 = ('Text','',each_step_data_item[0].strip())
                variable_list1.append(tuple1)

                if '%|' in each_step_data_item[2].strip():
                    previous_name = each_step_data_item[2].strip()
                    new_name = get_previous_response_variables_in_strings(each_step_data_item[2].strip())
                    tuple2 = ('Variable',"'%s'"%previous_name,new_name)
                else:
                    tuple2 = ('Text','',each_step_data_item[2].strip())
                variable_list2.append(tuple2)
            elif each_step_data_item[1] == "action": # Action line
                if each_step_data_item[2].strip().lower() == 'is in':
                    CommonUtil.ExecLog(sModuleInfo, "Using 'is in' instead of exact match", 1)
                    modifier = True# Changes how we compare

        for i in range(0,len(variable_list1)):
            if modifier == False and variable_list1[i][2] == variable_list2[i][2]: # Straight up compare
                result.append(True)
                pass_count+=1
            elif modifier and variable_list1[i][2] in variable_list2[i][2]: # Var 1 is IN var 2, if modifier set
                result.append(True)
                pass_count+=1
            elif modifier and variable_list2[i][2] in variable_list1[i][2]: # Var 2 is IN var 1 (Whichever way the user made it), if modifier set
                result.append(True)
                pass_count+=1
            else:
                result.append(False)
                fail_count+=1

        CommonUtil.ExecLog(sModuleInfo,"###Variable Comaparison Results###",1)
        CommonUtil.ExecLog(sModuleInfo,"Matched Variables: %d"%pass_count,1)
        CommonUtil.ExecLog(sModuleInfo, "Not Matched Variables: %d" % fail_count, 1)

        for i in range(0, len(variable_list1)):
            if result[i] == True:
                CommonUtil.ExecLog(sModuleInfo,"Item %d. %s %s - %s :: %s %s - %s : Matched"%(i+1,variable_list1[i][0],variable_list1[i][1],variable_list1[i][2],variable_list2[i][0],variable_list2[i][1],variable_list2[i][2]),1)
            else:
                CommonUtil.ExecLog(sModuleInfo, "Item %d. %s %s - %s :: %s %s - %s : Not Matched" % (i + 1, variable_list1[i][0], variable_list1[i][1], variable_list1[i][2], variable_list2[i][0],variable_list2[i][1], variable_list2[i][2]),3)

        if fail_count > 0:
            CommonUtil.ExecLog(sModuleInfo,"Error: %d item(s) did not match"%fail_count,3)
            return "failed"
        else:
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Validating text from an element given information regarding the expected text
def Compare_Lists(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Lists", 0)
    try:
        pass_count = 0
        fail_count = 0
        extra_count = 0
        variable_list1 = []
        variable_list2 = []
        result = []
        taken = []
        list1_name = ''
        list2_name = ''
        ignore_extra = True
        both_list = False
        for each_step_data_item in step_data[0]:
            if each_step_data_item[1] == "compare" or each_step_data_item[1] == "element parameter":
                list1_name = each_step_data_item[0]
                list2_name = each_step_data_item[2]
            if each_step_data_item[1] == "action":
                if str(each_step_data_item[2]).lower().strip().startswith('exact match'):
                    ignore_extra = False

        if list1_name == '' or list2_name == '':
            CommonUtil.ExecLog(sModuleInfo,"Error parsing data set. Expected Field and Value fields to be set",3)
            return "failed"

        list1 = Get_List_from_Shared_Variables(list1_name)
        list2 = Get_List_from_Shared_Variables(list2_name)

        if list1 in failed_tag_list or list2 in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Error converting Shared Variable in Field or Value fields to strings",3)
            return "failed"

        if isinstance(list1,list) and isinstance(list2,list): #if both are list not dict
            both_list = True
            variable_list1 = list1
            variable_list2 = list2
            for each in list1:
                if each in list2:
                    pass_count+=1
                else:
                    fail_count+=1
        else: #if both are dict
            for key in list1:
                if key in list2:
                    if key not in taken:
                        new_tuple = (key,list1[key])
                        variable_list1.append(new_tuple)
                        new_tuple = (key,list2[key])
                        variable_list2.append(new_tuple)
                        taken.append(key)
                        if str(list1[key]).lower().strip() == str(list2[key]).lower().strip():
                            pass_count+=1
                            result.append('pass')
                        else:
                            fail_count+=1
                            result.append('fail')
                else:
                    if key not in taken:
                        new_tuple = (key,list1[key])
                        variable_list1.append(new_tuple)
                        new_tuple = (key,'N/A')
                        variable_list2.append(new_tuple)
                        extra_count += 1
                        result.append('extra')
                        taken.append(key)

            for key in list2:
                if key in list1:
                    if key not in taken:
                        new_tuple = (key,list1[key])
                        variable_list1.append(new_tuple)
                        new_tuple = (key,list2[key])
                        variable_list2.append(new_tuple)
                        taken.append(key)
                        if str(list1[key]).lower().strip() == str(list2[key]).lower().strip():
                            pass_count+=1
                            result.append('pass')
                        else:
                            fail_count+=1
                            result.append('fail')
                else:
                    if key not in taken:
                        new_tuple = (key,'N/A')
                        variable_list1.append(new_tuple)
                        new_tuple = (key,list2[key])
                        variable_list2.append(new_tuple)
                        extra_count += 1
                        result.append('extra')
                        taken.append(key)

        CommonUtil.ExecLog(sModuleInfo,"###Comaparison Results of List '%s' and List '%s'###"%(list1_name,list2_name),1)
        CommonUtil.ExecLog(sModuleInfo,"Matched Variables: %d"%pass_count,1)
        CommonUtil.ExecLog(sModuleInfo, "Not Matched Variables: %d" % fail_count, 1)
        CommonUtil.ExecLog(sModuleInfo, "Extra Variables: %d" % extra_count, 1)

        if not both_list:
            for i in range(0, len(variable_list1)):
                if result[i] == 'pass':
                    CommonUtil.ExecLog(sModuleInfo,"Item %d. Variable Name : %s :: %s - %s : Matched"%(i+1,variable_list1[i][0],variable_list1[i][1],variable_list2[i][1]),1)
                elif result[i] == 'fail':
                    CommonUtil.ExecLog(sModuleInfo, "Item %d. Variable Name : %s :: %s - %s : Not Matched" % (i + 1, variable_list1[i][0], variable_list1[i][1], variable_list2[i][1]), 1)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Item %d. Variable Name : %s :: %s - %s : Extra" % (i + 1, variable_list1[i][0], variable_list1[i][1], variable_list2[i][1]), 1)


        if fail_count > 0:
            CommonUtil.ExecLog(sModuleInfo,"Error: %d item(s) did not match"%fail_count,3)
            return "failed"
        else:
            if extra_count > 0 and ignore_extra == False:
                CommonUtil.ExecLog(sModuleInfo, "Error: %d item(s) extra found" % extra_count, 3)
                return "failed"
            else:
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Method to initialize an empty list
def Initialize_List(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Initialize_List", 0)
    try:
        if ((len(step_data) != 1)):
            CommonUtil.ExecLog(sModuleInfo,
                               "Error parsing data set. Too many rows. Expected only the action row.",
                               3)
            return "failed"
        else:
            list_name = str(step_data[0][0][2]).lower().strip()
            new_list = {}
            result = Set_Shared_Variables(list_name,new_list)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Could not initialize empty list named %s"%list_name,3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"Successfully initialized empty list named %s"%list_name, 0)
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Clean_Up_Shared_Variables():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: clean up shared variables", 0)
    try:
        global shared_variables
        shared_variables = {}
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Shared_Variable_Export():
    ''' Exports all shared variables if for some reason modules can't use the functions herein '''
    return shared_variables

def save_built_in_time_variable(string):
    input = str(string).lower().strip()
    sign = ""
    number = 0
    parameter = ""
    if input == "currentepochtime":
        return int(time.time())
    elif input.startswith("today"):
        if input.lower().strip() == "today":
            return datetime.today().strftime('%Y-%m-%d')
        elif "+" in input:
            l = input.split("+")
            if len(l) > 2: #problem with input
                return "failed"
            else:
                sign = "plus"
                st = str(l[1]).strip()
                parameter = st[-1]
                number = int(st[:-1])
        elif "-" in input:
            l = input.split("-")
            if len(l) > 2: #problem with input
                return "failed"
            else:
                sign = "minus"
                st = str(l[1]).strip()
                parameter = st[-1]
                number = int(st[:-1])
        else:
            return "failed"

        if sign != "" and parameter != "":
            if sign == "minus":
                number*=-1
            if parameter == "d":
                return (datetime.today() + relativedelta(days=number)).strftime('%Y-%m-%d')
            elif parameter == "w":
                return (datetime.today() + relativedelta(days=number*7)).strftime('%Y-%m-%d')
            elif parameter == "m":
                return (datetime.today() + relativedelta(months=number)).strftime('%Y-%m-%d')
            elif parameter == "y":
                return (datetime.today() + relativedelta(years=number)).strftime('%Y-%m-%d')
            else:
                return "failed"