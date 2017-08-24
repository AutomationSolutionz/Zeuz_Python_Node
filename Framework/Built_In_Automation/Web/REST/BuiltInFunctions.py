# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
'''
Created on April 10, 2017

@author: Built_In_Automation Solutionz Inc.
'''

import sys
import os
import requests


sys.path.append("..")

import ast
import time
import inspect
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources

requests.packages.urllib3.disable_warnings()

from Framework.Utilities import CommonUtil
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list, skipped_tag_list


'============================= Sequential Action Section Begins=============================='


# Method to get the element step data from the original step_data
def Get_Element_Step_Data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get Element Step Data", 1)
    try:
        element_step_data = []
        for each in step_data:
            if (each[1] == "action" or each[1] == "conditional action"):
                #CommonUtil.ExecLog(sModuleInfo, "Not a part of element step data", 2)
                continue
            else:
                element_step_data.append(each)

        return element_step_data

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Handles actions for the sequential logic, based on the input from the mentioned function
def Action_Handler(action_step_data, action_row):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Action_Handler", 1)
    try:
        action_name = action_row[0]
        if action_name == "save response":
            result = Get_Response(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name == "compare variable":
            result = Compare_Variables(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name == "compare list":
            result = Compare_Lists(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name == "sleep":
            result = Sleep(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name == "initialize list":
            result = Initialize_List(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name == "step result":
            result = Step_Result(action_step_data)
            if result in failed_tag_list: # Convert user specified pass/fail into standard result
                return 'failed'
            elif result in passed_tag_list:
                return 'passed'
            elif result in skipped_tag_list:
                return 'skipped'
        elif action_name == "insert into list":
            result = Insert_Into_List(action_step_data)
            if result == "failed":
                return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"The action you entered is incorrect. Please provide accurate information on the data set(s).",3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def Initialize_List(data_set):
    ''' Temporary wrapper until we can convert everything to use just data_set and not need the extra [] '''
    return Shared_Resources.Initialize_List([data_set])

#Validating text from an element given information regarding the expected text
def Compare_Lists(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Lists", 1)
    try:
        element_step_data = Get_Element_Step_Data(step_data)
        if ((element_step_data == []) or (element_step_data == "failed")):
            return "failed"
        else:
            return Shared_Resources.Compare_Lists([step_data])
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Validating text from an element given information regarding the expected text
def Compare_Variables(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Variables", 1)
    try:
        element_step_data = Get_Element_Step_Data(step_data)
        if ((element_step_data == []) or (element_step_data == "failed")):
            return "failed"
        else:
            return Shared_Resources.Compare_Variables([step_data])
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to return dictonaries from string
def get_value_as_list(data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get value as list", 1)
    try:
        return ast.literal_eval(data)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to save rest call parameters
def save_fields_from_rest_call(result_dict, fields_to_be_saved):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: save fields from rest call", 1)
    try:
        fields_to_be_saved = fields_to_be_saved.split(",")
        if fields_to_be_saved[0].lower().strip() == 'all':
            for each in result_dict:
                field = each.strip()
                Shared_Resources.Set_Shared_Variables(field,result_dict[field])
            CommonUtil.ExecLog(sModuleInfo, "All response fields are saved", 1)
        elif fields_to_be_saved[0].lower().strip() == 'none':
            CommonUtil.ExecLog(sModuleInfo, "No response fields are saved", 1)
            return
        else:
            which_are_saved = []
            for each in fields_to_be_saved:
                field = each.strip()
                if field in result_dict:
                    which_are_saved.append(field)
                    Shared_Resources.Set_Shared_Variables(field, result_dict[field])

            CommonUtil.ExecLog(sModuleInfo, "%s response fields are saved"%(", ".join(str(x) for x in which_are_saved)),1)

        Shared_Resources.Show_All_Shared_Variables()
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def insert_fields_from_rest_call_into_list(result_dict, fields_to_be_saved, list_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: save fields from rest call", 1)
    try:
        fields_to_be_saved = fields_to_be_saved.split(",")
        if fields_to_be_saved[0].lower().strip() == 'all':
            for each in result_dict:
                field = each.strip()
                Shared_Resources.Set_List_Shared_Variables(list_name, field,result_dict[field])
            CommonUtil.ExecLog(sModuleInfo, "All response fields are saved", 1)
        elif fields_to_be_saved[0].lower().strip() == 'none':
            CommonUtil.ExecLog(sModuleInfo, "No response fields are saved", 1)
            return
        else:
            which_are_saved = []
            for each in fields_to_be_saved:
                field = each.strip()
                if field in result_dict:
                    which_are_saved.append(field)
                    Shared_Resources.Set_List_Shared_Variables(list_name, field, result_dict[field])

            CommonUtil.ExecLog(sModuleInfo, "%s response fields are saved"%(", ".join(str(x) for x in which_are_saved)),1)

        Shared_Resources.Show_All_Shared_Variables()
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Inserting a field into a list of shared variables
def Insert_Into_List(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Insert_Into_List", 1)
    try:
        fields_to_be_saved = ''
        for row in step_data:
            if row[1] == 'action':
                fields_to_be_saved = row[2]


        if len(step_data) == 1: #will have to test #saving direct input string data
            list_name = ''
            key = ''
            value = ''
            full_input_key_value_name = ''

            for each_step_data_item in step_data:
                if each_step_data_item[1]=="action":
                    full_input_key_value_name = each_step_data_item[2]

            temp_list = full_input_key_value_name.split(',')
            if len(temp_list) == 1:
                CommonUtil.ExecLog(sModuleInfo,
                                   "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                                   3)
                return "failed"
            else:
                list_name = temp_list[0].split(':')[1].strip()
                key = temp_list[1].split(':')[1].strip()
                value = temp_list[2].split(':')[1].strip()

            result = Shared_Resources.Set_List_Shared_Variables(list_name,key, value)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "In list '%s' Value of Variable '%s' could not be saved!!!"%(list_name, key), 3)
                return "failed"
            else:
                Shared_Resources.Show_All_Shared_Variables()
                return "passed"



        else:
            element_step_data = Get_Element_Step_Data(step_data)

            returned_step_data_list = Validate_Step_Data(element_step_data)

            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:

                    list_name = ''
                    key = ''
                    for each_step_data_item in step_data:
                        if each_step_data_item[1] == "action":
                            key = each_step_data_item[2]

                    # get list name from full input_string

                    temp_list = key.split(',')
                    if len(temp_list) == 1:
                        CommonUtil.ExecLog(sModuleInfo,
                                           "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                                           3)
                        return "failed"
                    else:
                        list_name = str(temp_list[0]).split(':')[1].strip()

                    fields_to_be_saved = ''
                    for i in range(1, len(temp_list)):
                        fields_to_be_saved += temp_list[i]
                        if i != len(temp_list)-1:
                            fields_to_be_saved+=","

                    return_result = handle_rest_call(returned_step_data_list, fields_to_be_saved, True, list_name)



                    return return_result
                except Exception:
                    return CommonUtil.Exception_Handler(sys.exc_info())


    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to handle rest calls
def handle_rest_call(data, fields_to_be_saved, save_into_list = False, list_name = ""):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: handle rest call", 1)
    try:
        Shared_Resources.Set_Shared_Variables('status_code', 0) # Reset this shared variable, so we do not get confused with any previous run
        url = data[0]
        method = data[1]
        body = data[2]
        headers = data[3]
        temp = get_value_as_list(body)
        if temp not in failed_tag_list:
            body = temp

        headers = get_value_as_list(headers)

        CommonUtil.ExecLog(sModuleInfo,"Calling %s method"%method,1)
        CommonUtil.ExecLog(sModuleInfo, "URL: %s" % url, 1)
        CommonUtil.ExecLog(sModuleInfo, "body: %s" % body, 1)
        CommonUtil.ExecLog(sModuleInfo, "headers %s" % headers, 1)

        if method.lower().strip() == 'post':
            result = requests.post(url,json=body,headers=headers,verify=False)
        elif method.lower().strip() == 'put':
            result = requests.put(url, json=body, headers=headers, verify=False)
        elif method.lower().strip() == 'get':
            result = requests.get(url, json=body, headers=headers, verify=False)
        elif method.lower().strip() == 'delete':
            result = requests.delete(url, json=body, headers=headers, verify=False)
        else:
            return "failed"
        status_code = int(result.status_code)
        Shared_Resources.Set_Shared_Variables('status_code',result.status_code)
        CommonUtil.ExecLog(sModuleInfo,'Post Call returned status code: %d'%status_code,1)
        try:
            if result.json():
                '''if status_code >=400:
                    CommonUtil.ExecLog(sModuleInfo,'Post Call Returned Bad Response',3)
                    return "failed"
                else:'''
                CommonUtil.ExecLog(sModuleInfo, 'Post Call Returned Response Successfully', 1)
                CommonUtil.ExecLog(sModuleInfo,"Received Response: %s"%result.json(),1)
                if not save_into_list:
                    save_fields_from_rest_call(result.json(), fields_to_be_saved)
                else:
                    if list_name == "":
                        CommonUtil.ExecLog(sModuleInfo,"List name not defined!",3)
                        return "failed"
                    insert_fields_from_rest_call_into_list(result.json(), fields_to_be_saved, list_name)
                return "passed"
        except Exception:
            CommonUtil.ExecLog(sModuleInfo,"REST Call did not respond in json format",1)
            CommonUtil.ExecLog(sModuleInfo,"Saving REST Call Response Text", 1)
            response_text = result.text
            Shared_Resources.Set_Shared_Variables('response_text', response_text)
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to get responses
def Get_Response(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get_Response", 1)
    try:
        fields_to_be_saved = ''
        for row in step_data:
            if row[1] == 'action':
                fields_to_be_saved = row[2]

        element_step_data = Get_Element_Step_Data(step_data)

        returned_step_data_list = Validate_Step_Data(element_step_data)

        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
            return "failed"
        else:
            try:
                return_result = handle_rest_call(returned_step_data_list, fields_to_be_saved)
                return return_result
            except Exception:
                return CommonUtil.Exception_Handler(sys.exc_info())
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Get_Element(returned_step_data_list, fields_to_be_saved):
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        CommonUtil.ExecLog(sModuleInfo, "Function: Get_Response", 1)
        try:
            return_result = handle_rest_call(returned_step_data_list, fields_to_be_saved)
            return return_result
        except Exception:
            return CommonUtil.Exception_Handler(sys.exc_info())

# Method to sleep for a particular duration
def Sleep(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Sleep", 1)
    try:
            tuple = step_data[0]
            seconds = int(tuple[2])
            CommonUtil.ExecLog(sModuleInfo, "Sleeping for %s seconds" % seconds, 1)
            time.sleep(seconds)
            return "passed"
            # return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Method to return pass or fail for the step outcome
def Step_Result(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Step_Result", 1)
    try:
        if ((1 < len(step_data) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            result = "failed"
        else:
            step_result = step_data[0][2]
            if step_result == 'pass':
                result = "passed"
            elif step_result == 'skip':
                result = 'skipped'
            elif step_result == 'fail':
                result = "failed"

        return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

# Performs a series of action or conditional logical action decisions based on user input
def Sequential_Actions(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Sequential_Actions", 1)
    try:
        for each in step_data:
            logic_row = []
            for row in each:
                # finding what to do for each dataset
                # if len(row)==5 and row[1] != "":     ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement
                if row[1] == "element parameter" or row[1] == 'compare':  ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement
                    continue

                elif row[1] == "action":
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row", 1)
                    if row[0] == 'compare variable':
                        result = Action_Handler(each, row)
                    else:
                        new_data_set = Shared_Resources.Handle_Step_Data_Variables([each])
                        if new_data_set in failed_tag_list:
                            return 'failed'
                        result = Action_Handler(new_data_set[0], row)
                    if result in failed_tag_list:
                        return "failed"
                    elif result in skipped_tag_list:
                        return "skipped"

                # If middle column = optional action, call action handler, but always return a pass
                elif row[1] == "optional action":
                    CommonUtil.ExecLog(sModuleInfo,"Checking the optional action to be performed in the action row: %s" % str(
                                               row), 1)
                    result = Action_Handler(each, row[0])  # Pass data set, and action_name to action handler
                    if result == 'failed':
                        CommonUtil.ExecLog(sModuleInfo, "Optional action failed. Returning pass anyway", 2)
                    result = 'passed'

                elif row[1] == "body" or row[1] == "header" or row[1] == "headers":
                    continue
                elif row[1]=="conditional action":
                    CommonUtil.ExecLog(sModuleInfo, "Checking the logical conditional action to be performed in the conditional action row", 1)
                    logic_decision=""
                    logic_row.append(row)
                    if len(logic_row)==2:
                        #element_step_data = each[0:len(step_data[0])-2:1]
                        element_step_data = Shared_Resources.Handle_Step_Data_Variables([each])
                        element_step_data = Get_Element_Step_Data(element_step_data[0])
                        returned_step_data_list = Validate_Step_Data(element_step_data)
                        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                            return "failed"
                        else:
                            try:
                                Element = Get_Element(returned_step_data_list, "all")
                                if Element == 'failed':
                                    logic_decision = "false"
                                else:
                                    logic_decision = "true"
                            except Exception, errMsg:
                                errMsg = "Could not find element in the by the criteria..."
                                return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
                    else:
                        continue

                    for conditional_steps in logic_row:
                        if logic_decision in conditional_steps:
                            print conditional_steps[2]
                            list_of_steps = conditional_steps[2].split(",")
                            for each_item in list_of_steps:
                                data_set_index = int(each_item) - 1
                                cond_result = Sequential_Actions([step_data[data_set_index]])
                                if cond_result == "failed":
                                    return "failed"
                                elif cond_result == "skipped":
                                    return "skipped"
                            return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                       "The sub-field information is incorrect. Please provide accurate information on the data set(s).",
                                       3)
                    return "failed"




        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


'===================== ===x=== Sequential Action Section Ends ===x=== ======================'


'============================= Validation Section Begins =============================='


# Validation of step data passed on by the user
def Validate_Step_Data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Step_Data", 1)
    try:
        method = ""
        url = ""
        body = "{"
        headers = "{"
        plain_body_text = False
        for each in step_data:
            if each[1].lower().strip() == "element parameter":
                element_parameter = each[0]
                if element_parameter.lower().strip() == 'method':
                    method = each[2]
                elif element_parameter.lower().strip() == 'url':
                    url = each[2]
            elif each[1].lower().strip() == 'body':
                if each[0].lower().strip() == 'plain text':
                    body = each[2]
                    plain_body_text = True
                else:
                    if body == "{":
                           body+="'%s' : '%s'"%(each[0], each[2])
                    else:
                           body += ", '%s' : '%s'" % (each[0], each[2])

            elif each[1].lower().strip() == 'header' or each[1].lower().strip() == 'headers':
                if headers == "{":
                   headers+="'%s' : '%s'"%(each[0], each[2])
                else:
                    headers += ", '%s' : '%s'" % (each[0], each[2])

        headers += "}"
        if not plain_body_text:
            body += "}"


        validated_data = (url, method, body, headers)
        return validated_data

    except Exception:
        errMsg = "Could not find the new page element requested. "
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

