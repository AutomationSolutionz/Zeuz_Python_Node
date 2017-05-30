# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

# shared_variables

import inspect,sys
import string
import random
from Framework.Utilities import CommonUtil


global shared_variables
shared_variables = {}

passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True','1','Success','success','SUCCESS']
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE','0']

def Set_Shared_Variables(key, value):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if key == '' or key == None or value == '' or value == None:  # if input is invalid
            return "failed"
        else:
            shared_variables[key] = value
            CommonUtil.ExecLog(sModuleInfo, "Variable value of '%s' is set as: %s" % (key, value), 1)
            return "passed"
    except:
        CommonUtil.Exception_Handler(sys.exc_info())


def Set_List_Shared_Variables(list_name, key, value):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if key == '' or key == None or value == '' or value == None or list_name == '' or list_name == None:  # if input is invalid
            return "failed"
        else:
            if list_name in shared_variables:
                shared_variables[list_name][key] = value
                CommonUtil.ExecLog(sModuleInfo, "In List '%s' Variable value of '%s' is set as: %s" % (list_name, key, value), 1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo,
                        "List named %s does not exist on shared variables, so cant insert new field to list" % list_name,
                        3)
                return "failed"
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
                CommonUtil.ExecLog(sModuleInfo, "Variable value of '%s' is: %s" % (str(key), value), 1)
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


def Test_Shared_Variables(key):
    ''' Test if a variable already exists and return true or false '''

    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if key == '' or key == None:  # if input is invalid
            return "failed"
        else:  # Valid input
            if key in shared_variables:  # Test if key/variable exists
                CommonUtil.ExecLog(sModuleInfo, "Variable %s exists" % key, 1)
                return True
            else:
                CommonUtil.ExecLog(sModuleInfo, "No Such variable named '%s' found in shared variables" % key, 1)
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
    CommonUtil.ExecLog(sModuleInfo, "Function: get previous response variables in strings", 1)
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
                    CommonUtil.ExecLog(sModuleInfo, 'Replacing variable "%s" with its value "%s"' % (parts[0], random_string), 1)
                else:
                    var_value = Get_Shared_Variables(parts[0])
                    if var_value == 'failed':
                        CommonUtil.ExecLog(sModuleInfo, "No such variable named '%s' in shared variables list" % parts[0], 3)
                        return "failed"
                    else:
                        output += str(var_value)
                        CommonUtil.ExecLog(sModuleInfo, 'Replacing variable "%s" with its value "%s"' % (parts[0], var_value), 1)
                output += parts[1]
            else:
                output += each
        if changed == True:
            CommonUtil.ExecLog(sModuleInfo, "Input string is changed by variable substitution", 1)
            CommonUtil.ExecLog(sModuleInfo, "Input string before change: %s" % input, 1)
            CommonUtil.ExecLog(sModuleInfo, "Input string after change: %s" % output, 1)

        return output

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def random_string_generator(pattern='nluc', size=10):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: random string generator", 1)
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Variables", 1)
    try:
        pass_count = 0
        fail_count = 0
        variable_list1 = []
        variable_list2 = []
        result = []
        for each_step_data_item in step_data[0]:
            if each_step_data_item[1]!="action":
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


        for i in range(0,len(variable_list1)):
            if variable_list1[i][2] == variable_list2[i][2]:
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Lists", 1)
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
        for each_step_data_item in step_data[0]:
            if each_step_data_item[1] == "compare":
                list1_name = each_step_data_item[0]
                list2_name = each_step_data_item[2]
            if each_step_data_item[1] == "action":
                if str(each_step_data_item[2]).lower().strip().startswith('exact match'):
                    ignore_extra = False

        if list1_name == '' or list2_name == '':
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return "failed"

        list1 = Get_List_from_Shared_Variables(list1_name)
        list2 = Get_List_from_Shared_Variables(list2_name)

        if list1 in failed_tag_list or list2 in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return "failed"

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
    CommonUtil.ExecLog(sModuleInfo, "Function: Initialize_List", 1)
    try:
        if ((len(step_data) != 1)):
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
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
                CommonUtil.ExecLog(sModuleInfo,"Successfully initialized empty list named %s"%list_name,1)
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Clean_Up_Shared_Variables():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: clean up shared variables", 1)
    try:
        global shared_variables
        shared_variables = {}
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())