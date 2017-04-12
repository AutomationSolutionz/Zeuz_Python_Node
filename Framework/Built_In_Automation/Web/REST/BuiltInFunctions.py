
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
from Framework.Utilities import CommonUtil

requests.packages.urllib3.disable_warnings()
global saved_response
saved_response = {}

'============================= Sequential Action Section Begins=============================='


# Method to get the element step data from the original step_data
def Get_Element_Step_Data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get Element Step Data", 1)
    try:
        element_step_data = []
        for each in step_data[0]:
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
            fields_to_be_saved = action_row[2]
            result = Get_Response(action_step_data, fields_to_be_saved)
            if result == "failed":
                return "failed"
        elif action_name == "sleep":
            result = Sleep(action_step_data)
            if result == "failed":
                return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"The action you entered is incorrect. Please provide accurate information on the data set(s).",3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to get previous response variables
#if we want the variable 'access_token', then we will have to use %access_token% in step data
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
                output += saved_response[parts[0]]
                CommonUtil.ExecLog(sModuleInfo,'Replacing variable "%s" with its value "%s"'%(parts[0],saved_response[parts[0]]),1)
                output += parts[1]
            else:
                output += each
        if changed == True:
            CommonUtil.ExecLog(sModuleInfo,"Input string is changed by variable substitution",1)
            CommonUtil.ExecLog(sModuleInfo, "Input string before change: %s"%input, 1)
            CommonUtil.ExecLog(sModuleInfo, "Input string after change: %s"%output, 1)

        return output

    except Exception:
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
        global saved_response
        if fields_to_be_saved[0].lower().strip() == 'all':
            for each in result_dict:
                field = each.strip()
                saved_response[field] = result_dict[field]
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
                    saved_response[field] = result_dict[field]

            CommonUtil.ExecLog(sModuleInfo, "%s response fields are saved"%(", ".join(str(x) for x in which_are_saved)),1)


        if len(saved_response) > 0:
            CommonUtil.ExecLog(sModuleInfo, "SavedResponse Saved Fields with Value##", 1)
            for each in saved_response:
                CommonUtil.ExecLog(sModuleInfo,"%s : %s"%(each,saved_response[each]),1)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to handle rest calls
def handle_rest_call(data, fields_to_be_saved):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: handle rest call", 1)
    try:
        url = get_previous_response_variables_in_strings(data[0])
        method = get_previous_response_variables_in_strings(data[1])
        body = get_previous_response_variables_in_strings(data[2])
        headers = get_previous_response_variables_in_strings(data[3])
        body = get_value_as_list(body)
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
        else:
            return "failed"
        status_code = int(result.status_code)
        CommonUtil.ExecLog(sModuleInfo,'Post Call returned status code: %d'%status_code,1)
        if status_code >=400:
            CommonUtil.ExecLog(sModuleInfo,'Post Call Returned Bad Response',3)
            return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, 'Post Call Returned Response Successfully', 1)
            CommonUtil.ExecLog(sModuleInfo,"Received Response: %s"%result.json(),1)
            save_fields_from_rest_call(result.json(), fields_to_be_saved)
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to get responses
def Get_Response(step_data, fields_to_be_saved):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get_Response", 1)
    try:
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



# Method to sleep for a particular duration
def Sleep(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Sleep", 1)
    try:
            tuple = step_data[0][0]
            seconds = int(tuple[2])
            CommonUtil.ExecLog(sModuleInfo, "Sleeping for %s seconds" % seconds, 1)
            time.sleep(seconds)
            return "passed"
            # return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to return pass or fail for the step outcome
def Step_Result(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Step_Result", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
            result = "failed"
        else:
            step_result = step_data[0][0][2]
            if step_result == 'pass':
                result = "passed"
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
                if row[1] == "element parameter":  ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement
                    continue

                elif row[1] == "action":
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row", 1)
                    result = Action_Handler([each], row)
                    if result == [] or result == "failed":
                        return "failed"

                elif row[1] == "body" or row[1] == "header" or row[1] == "headers":
                    continue

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
        for each in step_data:
            if each[1].lower().strip() == "element parameter":
                element_parameter = each[0]
                if element_parameter.lower().strip() == 'method':
                    method = each[2]
                elif element_parameter.lower().strip() == 'url':
                    url = each[2]
            elif each[1].lower().strip() == 'body':
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
        body += "}"


        validated_data = (url, method, body, headers)
        return validated_data
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find the new page element requested.  Error: %s" % (Error_Detail), 3)
        return "failed"


'===================== ===x=== Validation Section Ends ===x=== ======================'

def get_saved_response():
    return saved_response
