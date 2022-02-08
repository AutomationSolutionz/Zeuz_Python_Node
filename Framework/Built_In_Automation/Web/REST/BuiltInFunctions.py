# -*- coding: utf-8 -*-
"""
REST API actions.
"""

import os
from pathlib import Path
import sys
from typing import Tuple, Union
import requests
import ast
import time
import inspect

# Suppress the InsecureRequestWarning since we use verify=False parameter.
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

sys.path.append("..")

from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as Shared_Resources,
)

requests.packages.urllib3.disable_warnings()

from Framework.Utilities import CommonUtil
from Framework.Utilities.decorators import logger, deprecated
from Framework.Utilities.CommonUtil import (
    passed_tag_list,
    failed_tag_list,
    skipped_tag_list,
)

count = 1
index = 1
all_val = []

"============================= Sequential Action Section Begins=============================="


MODULE_NAME = inspect.getmodulename(__file__)


# Method to get the element step data from the original step_data
def Get_Element_Step_Data(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        element_step_data = []
        for each in step_data:
            if each[1] == "action" or each[1] == "conditional action":
                # CommonUtil.ExecLog(sModuleInfo, "Not a part of element step data", 2)
                continue
            else:
                element_step_data.append(each)

        return element_step_data

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Handles actions for the sequential logic, based on the input from the mentioned function
def Action_Handler(action_step_data, action_row):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        action_name = action_row[0]
        if action_name == "save response":
            result = Get_Response(action_step_data)
            if result == "zeuz_failed":
                return "zeuz_failed"
        elif action_name == "compare variable":
            result = Compare_Variables(action_step_data)
            if result == "zeuz_failed":
                return "zeuz_failed"
        elif action_name == "compare list":
            result = Compare_Lists(action_step_data)
            if result == "zeuz_failed":
                return "zeuz_failed"
        elif action_name == "sleep":
            result = Sleep(action_step_data)
            if result == "zeuz_failed":
                return "zeuz_failed"
        elif action_name == "initialize list":
            result = Initialize_List(action_step_data)
            if result == "zeuz_failed":
                return "zeuz_failed"
        elif action_name == "step result":
            result = Step_Result(action_step_data)
            if (
                result in failed_tag_list
            ):  # Convert user specified pass/fail into standard result
                return "zeuz_failed"
            elif result in passed_tag_list:
                return "passed"
            elif result in skipped_tag_list:
                return "skipped"
        elif action_name == "insert into list":
            result = Insert_Into_List(action_step_data)
            if result == "zeuz_failed":
                return "zeuz_failed"
        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "The action you entered is incorrect. Please provide accurate information on the data set(s).",
                3,
            )
            return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
@deprecated
def Initialize_List(data_set):
    """ Temporary wrapper until we can convert everything to use just data_set and not need the extra [] """
    return Shared_Resources.Initialize_List([data_set])


# Validating text from an element given information regarding the expected text
@logger
def Compare_Lists(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        element_step_data = Get_Element_Step_Data(step_data)
        if (element_step_data == []) or (element_step_data == "zeuz_failed"):
            return "zeuz_failed"
        else:
            return Shared_Resources.Compare_Lists([step_data])
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Validating text from an element given information regarding the expected text
@logger
def Compare_Variables(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        element_step_data = Get_Element_Step_Data(step_data)
        if (element_step_data == []) or (element_step_data == "zeuz_failed"):
            return "zeuz_failed"
        else:
            return Shared_Resources.Compare_Variables([step_data])
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


def get_all_val(x, target):
    global all_val
    for key, value in list(x.items()):
        if str(key) == target:
            all_val.append(value)
        else:
            if isinstance(value, dict):
                get_all_val(value, target)
            elif isinstance(value, list):
                for each in value:
                    if isinstance(each, str) or isinstance(each, str):
                        if str(key) == target:
                            all_val.append(each)
                    else:
                        get_all_val(each, target)
            else:
                continue


def get_val(x, target):
    global count, index
    for key, value in list(x.items()):
        if str(key) == target:
            if count == index:
                return value
            else:
                count += 1
                continue
        else:
            if isinstance(value, dict):
                result = get_val(value, target)
                if not result:
                    continue
                else:
                    if count == index:
                        return result
                    else:
                        count += 1
                        continue
            elif isinstance(value, list):
                for each in value:
                    if isinstance(each, str) or isinstance(each, str):
                        if str(key) == target:
                            if count == index:
                                return each
                            else:
                                count += 1
                                continue
                        else:
                            continue
                    else:
                        result = get_val(each, target)
                        if not result:
                            continue
                        else:
                            if count == index:
                                return result
                            else:
                                count += 1
                                continue
            else:
                continue
    return False


@logger
def search_val(x, target, target_val, key=""):
    if isinstance(x, list):
        for each in x:
            if isinstance(each, str):
                if str(key) == target and str(each) == target_val:
                    return True
                else:
                    continue
            elif isinstance(each, list) or isinstance(each, dict):
                result = search_val(each, target, target_val, key)
                if result:
                    return True

    elif isinstance(x, dict):
        for key, value in x.items():
            # if isinstance(value, str):
            if str(key) == target and str(value) == target_val:
                return True
            elif isinstance(value, list) or isinstance(value, dict):
                result = search_val(value, target, target_val, key)
                if result:
                    return True
    else:
        return False


@logger
def search_val_wrapper(x, target, target_val, equal=True):
    target_val = target_val.replace("[[", "(")
    target_val = target_val.replace("]]", ")")
    result = search_val(x, target, target_val)
    if equal:
        return result
    else:
        return not result


# Method to save rest call parameters
def save_fields_from_rest_call(result_dict, fields_to_be_saved):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        global index, count
        fields_to_be_saved = fields_to_be_saved.split(",")
        if fields_to_be_saved[0].lower().strip() == "all":
            for each in result_dict:
                field = each.strip()
                Shared_Resources.Set_Shared_Variables(field, result_dict[field])
            CommonUtil.ExecLog(sModuleInfo, "All response fields are saved", 1)
        elif fields_to_be_saved[0].lower().strip() == "none":
            CommonUtil.ExecLog(sModuleInfo, "No response fields are saved", 1)
            return
        else:
            which_are_saved = []
            for each in fields_to_be_saved:
                field = each.strip()
                i = 1
                temp_field = ""
                multiple = False
                if "-" in field:
                    l = field.split("-")
                    if len(l) == 2:
                        try:
                            i = int(l[1].strip())
                            temp_field = l[0].strip()
                            multiple = True
                        except:
                            i = 1

                if multiple:
                    index = i
                    count = 1
                    value_to_be_saved = get_val(result_dict, temp_field)
                else:
                    index = 1
                    count = 1
                    value_to_be_saved = get_val(result_dict, field)
                if not value_to_be_saved:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Couldn't find  response field, ignoring it %s" % field,
                        2,
                    )
                else:
                    which_are_saved.append(field)
                    Shared_Resources.Set_Shared_Variables(field, value_to_be_saved)

            CommonUtil.ExecLog(
                sModuleInfo,
                "%s response fields are saved"
                % (", ".join(str(x) for x in which_are_saved)),
                1,
            )

        # Shared_Resources.Show_All_Shared_Variables()
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def insert_fields_from_rest_call_into_list(result_dict, fields_to_be_saved, list_name):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        global index, count, all_val
        fields_to_be_saved = fields_to_be_saved.split(",")
        if fields_to_be_saved[0].lower().strip() == "all":
            for each in result_dict:
                field = each.strip()
                Shared_Resources.Set_List_Shared_Variables(
                    list_name, field, result_dict[field]
                )
            CommonUtil.ExecLog(sModuleInfo, "All response fields are saved", 1)
        elif fields_to_be_saved[0].lower().strip() == "none":
            CommonUtil.ExecLog(sModuleInfo, "No response fields are saved", 1)
            return
        else:
            which_are_saved = []
            for each in fields_to_be_saved:
                field = each.strip()
                i = 1
                temp_field = ""
                multiple = False
                if "-" in field:
                    l = field.split("-")
                    if len(l) == 2:
                        try:
                            i = l[1].strip()
                            if i == "all":
                                i = 0  # 0 for all
                            else:
                                i = int(i)
                            temp_field = l[0].strip()
                            multiple = True
                        except:
                            i = 1

                if multiple:
                    if i == 0:
                        index = 0
                        all_val = []
                        get_all_val(result_dict, temp_field)
                    else:
                        index = i
                        count = 1
                        value_to_be_saved = get_val(result_dict, temp_field)
                else:
                    index = 1
                    count = 1
                    value_to_be_saved = get_val(result_dict, field)

                if index == 0:  # save all into list
                    which_are_saved.append(temp_field)
                    Shared_Resources.Set_Shared_Variables(
                        list_name, []
                    )  # initializes the list
                    for each in all_val:
                        value_as_list = False
                        if isinstance(each, list):
                            value_as_list = True
                        Shared_Resources.Append_List_Shared_Variables(
                            list_name, each, value_as_list=value_as_list
                        )
                else:
                    if not value_to_be_saved:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Couldn't find  response field, ignoring it %s" % field,
                            2,
                        )
                    else:
                        which_are_saved.append(field)
                        Shared_Resources.Set_Shared_Variables("list_name")
                        Shared_Resources.Set_List_Shared_Variables(
                            list_name, field, value_to_be_saved
                        )

            CommonUtil.ExecLog(
                sModuleInfo,
                "%s response fields are saved"
                % (", ".join(str(x) for x in which_are_saved)),
                1,
            )

        Shared_Resources.Show_All_Shared_Variables()
    except Exception as e:
        print(e)
        return CommonUtil.Exception_Handler(sys.exc_info())


# Inserting a field into a list of shared variables
@logger
def Insert_Into_List(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        fields_to_be_saved = ""
        for row in step_data:
            if row[1] == "action":
                fields_to_be_saved = row[2]

        if len(step_data) == 1:  # will have to test #saving direct input string data
            list_name = ""
            key = ""
            value = ""
            full_input_key_value_name = ""

            for each_step_data_item in step_data:
                if each_step_data_item[1] == "action":
                    full_input_key_value_name = each_step_data_item[2]

            temp_list = full_input_key_value_name.split(",")
            if len(temp_list) == 1:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                    3,
                )
                return "zeuz_failed"
            else:
                list_name = temp_list[0].split(":")[1].strip()
                key = temp_list[1].split(":")[1].strip()
                value = temp_list[2].split(":")[1].strip()

            result = Shared_Resources.Set_List_Shared_Variables(list_name, key, value)
            if result in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "In list '%s' Value of Variable '%s' could not be saved!!!"
                    % (list_name, key),
                    3,
                )
                return "zeuz_failed"
            else:
                # Shared_Resources.Show_All_Shared_Variables()
                return "passed"

        else:
            element_step_data = Get_Element_Step_Data(step_data)

            returned_step_data_list = Validate_Step_Data(element_step_data)

            if (returned_step_data_list == []) or (returned_step_data_list == "zeuz_failed"):
                return "zeuz_failed"
            else:
                try:

                    list_name = ""
                    key = ""
                    for each_step_data_item in step_data:
                        if each_step_data_item[1] == "action":
                            key = each_step_data_item[2]

                    # get list name from full input_string

                    temp_list = key.split(",")
                    if len(temp_list) == 1:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                            3,
                        )
                        return "zeuz_failed"
                    else:
                        list_name = str(temp_list[0]).split(":")[1].strip()

                    fields_to_be_saved = ""
                    for i in range(1, len(temp_list)):
                        fields_to_be_saved += temp_list[i]
                        if i != len(temp_list) - 1:
                            fields_to_be_saved += ","

                    return_result = handle_rest_call(
                        returned_step_data_list, fields_to_be_saved, True, list_name
                    )

                    return return_result
                except Exception:
                    return CommonUtil.Exception_Handler(sys.exc_info())

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def search_condition_wrapper(data, condition_string):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        parse_list = str(condition_string).split("(")
        condition_string_list = []
        conditions = []
        lists = []
        search_area = data
        if len(parse_list) < 2:
            CommonUtil.ExecLog(
                sModuleInfo,
                "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                3,
            )
            return "zeuz_failed"
        list_name = parse_list[0].strip()
        parse_list = parse_list[1].strip().split(")")
        all_condition = parse_list[0].strip()
        all_condition = all_condition.split("&&")

        for each in all_condition:
            condition_string_list.append(each.strip())

        list_name = list_name.split(".")

        for each in list_name:
            lists.append(each.strip())

        for each in lists:
            if each in search_area:
                search_area = search_area[each]
            else:
                CommonUtil.ExecLog(sModuleInfo, "%s not found in response" % each, 3)
                return "zeuz_failed"

        for each in condition_string_list:
            equal = True
            key_val_list = []
            if "==" in each:
                equal = True
                key_val_list = each.split("==")
            elif "!=" in each:
                equal = False
                key_val_list = each.split("!=")
            else:
                CommonUtil.ExecLog(
                    sModuleInfo, "== or != pattern not found in condition", 3
                )
                return "zeuz_failed"

            key = key_val_list[0].strip()
            value = key_val_list[1].strip()
            conditions.append((key, value, equal))

        result = True
        if len(conditions) == 0:
            CommonUtil.ExecLog(sModuleInfo, "No condition is provived in step data", 3)
            return "zeuz_failed"
        else:
            if isinstance(search_area, dict):
                for each in conditions:
                    key = each[0]
                    value = each[1]
                    equal = each[2]
                    if key in list(search_area.keys()):
                        if equal:
                            result = result and (str(search_area[key]) == value)
                        else:
                            result = result and (str(search_area[key]) != value)
                    else:
                        CommonUtil.ExecLog(
                            sModuleInfo, "%s not found in response" % key, 3
                        )
                        return "zeuz_failed"
            elif isinstance(search_area, list):
                for data in search_area:
                    list_result = True
                    for each in conditions:
                        key = each[0].replace("[[", "(")
                        key = key.replace("]]", ")")
                        value = each[1].replace("[[", "(")
                        value = value.replace("]]", ")")
                        if isinstance(data, dict):
                            if key in list(data.keys()):
                                if equal:
                                    list_result = list_result and (
                                        str(data[key]) == value
                                    )
                                else:
                                    list_result = list_result and (
                                        str(data[key]) != value
                                    )
                            else:
                                CommonUtil.ExecLog(
                                    sModuleInfo, "%s not found in response" % key, 3
                                )
                                return "zeuz_failed"
                        else:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                                3,
                            )
                            return "zeuz_failed"
                    result = list_result
                    if result:
                        break
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                    3,
                )
                return "zeuz_failed"

        return result

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


KEY_ZEUZ_API_SESSIONS = "zeuz_api_sessions"
def get_session(session_name: Union[str, None] = None) -> Union[requests.Request, requests.Session]:
    """
    Fetches either an old session or creates a new session if it does not exist
    with the provided `session_name`. A value of `None` means, we won't return
    any session - we'll simply return the top level `requests` module.
    """

    # This dictionary contains a mapping between session names and session objects.
    # Whenever a session with a new name is requested, it must first be created and
    # then inserted in this dictionary, and afterwards use the newly created
    # session. The default is the `None` session, which means there's no session and
    # every request with the `None` session will be sent as a one-off request.
    sessions: Union[requests.Request, requests.Session] = Shared_Resources.Get_Shared_Variables(KEY_ZEUZ_API_SESSIONS, log=False)

    if sessions == "zeuz_failed":
        Shared_Resources.Set_Shared_Variables(
            KEY_ZEUZ_API_SESSIONS,
            { None: requests },
            print_variable=False
        )
        sessions = Shared_Resources.Get_Shared_Variables(KEY_ZEUZ_API_SESSIONS, log=False)

    if session_name not in sessions:
        sessions[session_name] = requests.Session()

        Shared_Resources.Set_Shared_Variables(
            KEY_ZEUZ_API_SESSIONS,
            sessions,
            print_variable=False
        )

    return sessions[session_name]


ENV_ZEUZ_NODE_CLIENT_CERT = "ZEUZ_NODE_CLIENT_CERT"
def get_client_certificate() -> Union[str, Tuple[str, str], None]:
    """
    Gets the client-side certificate if there's any.

    Location to the certificate(s) file(s) is resolved in the following way:

    1. Checks for `ZEUZ_NODE_CLIENT_CERT` environment variable which should
       point to the directory containing the certificate(s).
    2. Tries to search for a `certificates` folder in the current `PYTHON PATH`.

    If there are multiple type of certificates, they're resolved according to
    the following priorities - 1 being the highest (pick first):

    1. If there's a ".pem" file, it'll take the highest priority as the only
       certificate file.
    2. If there's a pair of ".cert" and ".key" files, pick them.
    3. If there's a pair of ".crt" and ".key" files, pick them.
    4. If there's a pair of ".cer" and ".key" files, pick them.
    5. Otherwise we pick nothing and return `None`.

    **NOTE**: `requests` module supports loading only **UNENCRYPTED** files.
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    certificates_dir: Path = None
    try:
        env_value = os.environ[ENV_ZEUZ_NODE_CLIENT_CERT]
        certificates_dir = Path(env_value)
        if not certificates_dir.exists():
            CommonUtil.ExecLog(
                sModuleInfo,
                f'The directory "{env_value}" specified by the environment variable "ZEUZ_NODE_CLIENT_CERT" does not exist.\n'
                f'Trying to locate certificates from "{Path.cwd() / "certificates"}" dir.',
                3,
            )
            raise Exception(f"{env_value} does not exist.")
    except:
        # Try to find inside the "certificates" folder.
        certificates_dir = Path.cwd() / "certificates"

    def get_len(pattern: str) -> int:
        return len(list(certificates_dir.glob(pattern)))

    if get_len("*.pem") > 0:
        str(next(certificates_dir.glob("*.pem")))
    elif get_len("*.key") > 0:
        cert_file_exts = ["cert", "crt", "cer"]
        for cfe in cert_file_exts:
            cfe_name = f"*.{cfe}"
            if get_len(cfe_name) > 0:
                return (
                    str(next(certificates_dir.glob(cfe_name))),
                    str(next(certificates_dir.glob("*.key"))),
                )

    return None


# Method to handle rest calls
def handle_rest_call(
    data,
    fields_to_be_saved,
    save_into_list=False,
    list_name="",
    search=False,
    search_key="",
    search_value="",
    equal=True,
    condition="",
    apply_condition=False,
    save_cookie=False,
    wait_for_response_code=0,
    timeout=None,
    files=None,
    session_name=None,
    allow_redirects=True,
):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        global index, count
        Shared_Resources.Set_Shared_Variables(
            "status_code", 0, print_variable=False, pretty=False
        )  # Reset this shared variable, so we do not get confused with any previous run
        url = data[0]
        method = data[1]
        body = data[2]
        headers = data[3]
        payload = data[4]

        # Parse header into proper object.
        headers = CommonUtil.parse_value_into_object(headers)

        # Parse body into proper object unless it is not GraphQL.
        temp = CommonUtil.parse_value_into_object(body)
        if temp not in failed_tag_list:
            body = temp

        CommonUtil.ExecLog(sModuleInfo, "HTTP method: %s\nURL: %s\nBODY: %s\nHEADERS: %s" % (method, url, body, headers), 5)
        if payload:
            CommonUtil.ExecLog(sModuleInfo, "PAYLOAD: %s" % payload, 1)

        request_count = 1
        if wait_for_response_code != 0:
            request_count = 3

        count = 0

        # Decide whether we should use a Session object or a one-off request.
        session = get_session(session_name)

        # Get client-side certificates if it exists in the
        # `ZEUZ_NODE_CLIENT_CERT` or `PYTHON PATH`.
        cert = get_client_certificate()

        result = None
        status_code = 1  # dummy value
        if CommonUtil.load_testing:
            start_counter = time.perf_counter()
        while count < request_count:
            method = method.lower().strip()
            if method in ("post", "put"):
                if files is not None:
                    headers["Content-Type"] = "multipart/form-data"

                if "Content-Type" in headers:
                    content_header = headers["Content-Type"]
                    if content_header == "application/json":
                        result = session.request(
                            method=method,
                            url=url,
                            json=body,
                            headers=headers,
                            verify=False,
                            cert=cert,
                            timeout=timeout,
                            allow_redirects=allow_redirects,
                        )
                    elif content_header == "multipart/form-data":
                        # delete the header itself before making the request, as you also need to
                        # set a boundary
                        del headers["Content-Type"]
                        if files:
                            result = session.request(
                                method=method,
                                url=url,
                                files=files,
                                headers=headers,
                                verify=False,
                                cert=cert,
                                timeout=timeout,
                                allow_redirects=allow_redirects,
                            )
                        else:
                            result = session.request(
                                method=method,
                                url=url,
                                data=body,
                                headers=headers,
                                verify=False,
                                cert=cert,
                                timeout=timeout,
                                allow_redirects=allow_redirects,
                            )
                    elif content_header == "application/x-www-form-urlencoded":
                        result = session.request(
                            method=method,
                            url=url,
                            data=body,
                            headers=headers,
                            verify=False,
                            cert=cert,
                            timeout=timeout,
                            allow_redirects=allow_redirects,
                        )
                    else:
                        result = session.request(
                            method=method,
                            url=url,
                            json=body,
                            data=payload,
                            headers=headers,
                            verify=False,
                            cert=cert,
                            timeout=timeout,
                            allow_redirects=allow_redirects,
                        )
                else:
                    result = session.request(
                        method=method,
                        url=url,
                        json=body,
                        data=payload,
                        headers=headers,
                        verify=False,
                        cert=cert,
                        timeout=timeout,
                        allow_redirects=allow_redirects,
                    )
            elif method in ("get", "head"):
                result = session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    verify=False,
                    cert=cert,
                    timeout=timeout,
                    allow_redirects=allow_redirects,
                )
            elif method == "delete":
                result = session.request(
                    method=method,
                    url=url,
                    json=body,
                    headers=headers,
                    verify=False,
                    cert=cert,
                    timeout=timeout,
                    allow_redirects=allow_redirects,
                )
            else:
                return "zeuz_failed"
            status_code = int(result.status_code)

            if request_count > 1:
                if status_code != wait_for_response_code:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "HTTP Status Code %d did not match with Expected Status Code %d, retrying again."
                        % (status_code, wait_for_response_code),
                        2,
                    )

                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "HTTP Response:\n%s" % result.text,
                        2,
                    )
                    time.sleep(2)
                else:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "HTTP Status Code %d matched with Expected Status Code %d"
                        % (status_code, wait_for_response_code),
                        1,
                    )
                    break
            count += 1
        if CommonUtil.load_testing:
            end_counter = time.perf_counter()
            runtime = round(end_counter-start_counter, 6)
            CommonUtil.performance_report["endpoint"] = result.url
            CommonUtil.performance_report["data"].append(
                {
                    "status": status_code,
                    "message": result.text,
                    "runtime": runtime
                }
            )
            CommonUtil.performance_report["individual_stats"] = {
                "slowest": max(runtime, CommonUtil.performance_report["individual_stats"]["slowest"]),
                "fastest": min(runtime, CommonUtil.performance_report["individual_stats"]["fastest"]),
            }
            if str(status_code) in CommonUtil.performance_report["status_counts"]:
                CommonUtil.performance_report["status_counts"][str(status_code)] += 1
            else:
                CommonUtil.performance_report["status_counts"][str(status_code)] = 1

        if wait_for_response_code != 0 and status_code != wait_for_response_code:
            CommonUtil.ExecLog(
                sModuleInfo,
                "'Response' HTTP status code %d did not match with 'Expected' HTTP status code %d."
                % (status_code, wait_for_response_code),
                3,
            )
            CommonUtil.ExecLog(
                sModuleInfo,
                "HTTP Response:\n%s" % result.text,
                3,
            )
            return "zeuz_failed"

        Shared_Resources.Set_Shared_Variables("status_code", result.status_code, print_variable=False)
        Shared_Resources.Set_Shared_Variables("http_status_code", result.status_code)
        Shared_Resources.Set_Shared_Variables("http_response_headers", result.headers)
        try:
            if result.json():
                Shared_Resources.Set_Shared_Variables("rest_response", result.json(), print_variable=False)
                Shared_Resources.Set_Shared_Variables("http_response", result.json())
                CommonUtil.ExecLog(sModuleInfo, "HTTP Request successful.", 1)

                # if save cookie option enabled then push cookie into shared variables, if cookie var name is 'id' then you can reference it later with %|id|%
                if save_cookie:
                    all_cookies = requests.utils.dict_from_cookiejar(result.cookies)
                    for each in list(all_cookies.keys()):
                        Shared_Resources.Set_Shared_Variables(each, all_cookies[each])

                if search:
                    if apply_condition:
                        search_result = search_condition_wrapper(
                            result.json(), condition
                        )
                        if search_result in passed_tag_list:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                'Condition "%s" is TRUE in response' % (condition),
                                1,
                            )
                            return "passed"
                        else:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                'Condition "%s" is FALSE in response' % (condition),
                                3,
                            )
                            return "zeuz_failed"
                    else:
                        search_result = search_val_wrapper(
                            result.json(), search_key, search_value, equal
                        )
                        if equal:
                            if search_result in passed_tag_list:
                                CommonUtil.ExecLog(
                                    sModuleInfo,
                                    'Got "%s":"%s" in response'
                                    % (search_key, search_value),
                                    1,
                                )
                                return "passed"
                            else:
                                CommonUtil.ExecLog(
                                    sModuleInfo,
                                    'Couldnt Get "%s":"%s" in response'
                                    % (search_key, search_value),
                                    3,
                                )
                                return "zeuz_failed"
                        else:
                            if search_result in passed_tag_list:
                                CommonUtil.ExecLog(
                                    sModuleInfo,
                                    'No "%s":"%s" in response'
                                    % (search_key, search_value),
                                    1,
                                )
                                return "passed"
                            else:
                                CommonUtil.ExecLog(
                                    sModuleInfo,
                                    'Got "%s":"%s" in response'
                                    % (search_key, search_value),
                                    3,
                                )
                                return "zeuz_failed"
                else:
                    if not save_into_list:
                        save_fields_from_rest_call(result.json(), fields_to_be_saved)
                    else:
                        if list_name == "":
                            CommonUtil.ExecLog(sModuleInfo, "List name not defined!", 3)
                            return "zeuz_failed"
                        insert_fields_from_rest_call_into_list(
                            result.json(), fields_to_be_saved, list_name
                        )
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "HTTP Request did not respond in json format", 1)
                response_text = result.json()
                CommonUtil.ExecLog(sModuleInfo, "Received Response", 1)
                try:
                    # try to save as dict
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Trying to convert HTTP Request response text to json",
                        1,
                    )
                    json_of_response = ast.literal_eval(response_text)
                    Shared_Resources.Set_Shared_Variables(
                        "rest_response", json_of_response, print_variable=False
                    )
                    Shared_Resources.Set_Shared_Variables(
                        "http_response", json_of_response
                    )
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "REST Call Response Text converted to json and saved in 'http_response' shared variable",
                        1,
                    )
                except:
                    # save the text
                    response_text = result.text
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "REST Call Response Text couldn't be converted to json",
                        2,
                    )
                    Shared_Resources.Set_Shared_Variables(
                        "rest_response", response_text, print_variable=False
                    )
                    Shared_Resources.Set_Shared_Variables(
                        "http_response", CommonUtil.parse_value_into_object(response_text)
                    )
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "REST Call Response Text saved in 'http_response' shared variable",
                        1,
                    )
                return "passed"
        except Exception:
            CommonUtil.ExecLog(
                sModuleInfo, "REST Call did not respond in json format", 1
            )
            response_text = result.text
            CommonUtil.ExecLog(
                sModuleInfo, "REST Call response is: %s" % str(response_text), 1
            )
            try:
                # try to save as dict
                CommonUtil.ExecLog(
                    sModuleInfo, "Trying to convert REST Call Response Text to json", 1
                )
                json_of_response = ast.literal_eval(response_text)
                Shared_Resources.Set_Shared_Variables("rest_response", json_of_response, print_variable=False)
                Shared_Resources.Set_Shared_Variables("http_response", json_of_response)
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "REST Call Response Text converted to json and saved in 'http_response' shared variable",
                    1,
                )
            except:
                # save the text
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "REST Call Response Text couldn't be converted to json",
                    2,
                )
                Shared_Resources.Set_Shared_Variables("rest_response", response_text, print_variable=False)
                Shared_Resources.Set_Shared_Variables("http_response", response_text)
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "REST Call Response Text saved in 'http_response' shared variable",
                    1,
                )
            return "passed"
    except requests.Timeout:
        CommonUtil.ExecLog(sModuleInfo, f"Request '{url}' timed out after {timeout} seconds.", 3)
        return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Get Response Wrapper Normal
def Get_Response_Wrapper(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        return Get_Response(step_data)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Get Response Wrapper With Cookie
def Get_Response_Wrapper_With_Cookie(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        return Get_Response(step_data, True)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to get responses
@logger
def Get_Response(step_data, save_cookie=False):
    try:
        wait_for_response_code = 0
        fields_to_be_saved = ""
        timeout = None
        files = None
        session_name = None
        allow_redirects = True
        for left, mid, right in step_data:
            left = left.lower()

            if mid == "action":
                fields_to_be_saved = right
            elif "wait for status code" in left:
                wait_for_response_code = int(right)
            elif "timeout" in left:
                timeout = float(right.strip())
            elif "file" in left:
                files = CommonUtil.parse_value_into_object(right)
            elif "session" in left:
                # Allow the user to specify a session name. All requests under
                # the same session name will be sent from the same Session
                # object. Which means, it will share cookies and other session
                # related data automatically among all the requests in that
                # session.
                session_name = right.strip()
            elif "allow redirect" in left:
                allow_redirects = True if "true" in right.lower() else False

        element_step_data = Get_Element_Step_Data(step_data)

        returned_step_data_list = Validate_Step_Data(element_step_data)

        if (returned_step_data_list == []) or (returned_step_data_list == "zeuz_failed"):
            return "zeuz_failed"
        else:
            try:
                return_result = handle_rest_call(
                    returned_step_data_list,
                    fields_to_be_saved,
                    save_cookie=save_cookie,
                    wait_for_response_code=wait_for_response_code,
                    timeout=timeout,
                    files=files,
                    session_name=session_name,
                    allow_redirects=allow_redirects,
                )
                return return_result
            except Exception:
                return CommonUtil.Exception_Handler(sys.exc_info())
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to search responses, if certain key value pair exists in REST response
@logger
def Search_Response(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        fields_to_be_saved = ""
        key = ""
        value = ""
        equal = True
        condition = ""
        apply_condition = False
        for row in step_data:
            if row[1] == "action":
                key_value_pair = row[2]
                if "(" in key_value_pair and ")" in key_value_pair:
                    apply_condition = True
                    condition = key_value_pair
                else:
                    l = str(key_value_pair).split("==")
                    if len(l) == 2:
                        equal = True
                        key = l[0].strip()
                        value = l[1].strip()
                        if key == "" or value == "":
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Error in key value step data for search response.. Try 'key == value' format...",
                                3,
                            )
                            return "zeuz_failed"
                    else:
                        l = str(key_value_pair).split("!=")
                        if len(l) == 2:
                            equal = False
                            key = l[0].strip()
                            value = l[1].strip()
                            if key == "" or value == "":
                                CommonUtil.ExecLog(
                                    sModuleInfo,
                                    "Error in key value step data for search response.. Try 'key != value' format...",
                                    3,
                                )
                                return "zeuz_failed"
                        else:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "Error in key value step data for search response.. Try 'key == value' format...",
                                3,
                            )
                            return "zeuz_failed"

        element_step_data = Get_Element_Step_Data(step_data)

        returned_step_data_list = Validate_Step_Data(element_step_data)

        if (returned_step_data_list == []) or (returned_step_data_list == "zeuz_failed"):
            return "zeuz_failed"
        else:
            try:
                return_result = handle_rest_call(
                    returned_step_data_list,
                    fields_to_be_saved,
                    search=True,
                    search_key=key,
                    search_value=value,
                    equal=equal,
                    condition=condition,
                    apply_condition=apply_condition,
                )
                return return_result
            except Exception:
                return CommonUtil.Exception_Handler(sys.exc_info())
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Get_Element(returned_step_data_list, fields_to_be_saved):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        return_result = handle_rest_call(returned_step_data_list, fields_to_be_saved)
        return return_result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to sleep for a particular duration
@logger
def Sleep(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        tuple = step_data[0]
        seconds = int(tuple[2])
        CommonUtil.ExecLog(sModuleInfo, "Sleeping for %s seconds" % seconds, 1)
        time.sleep(seconds)
        return "passed"
        # return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to return pass or fail for the step outcome
@logger
def Step_Result(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if 1 < len(step_data) >= 5:
            CommonUtil.ExecLog(
                sModuleInfo,
                "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                3,
            )
            result = "zeuz_failed"
        else:
            step_result = step_data[0][2]
            if step_result == "pass":
                result = "passed"
            elif step_result == "skip":
                result = "skipped"
            elif step_result == "fail":
                result = "zeuz_failed"

        return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Performs a series of action or conditional logical action decisions based on user input
@logger
def Sequential_Actions(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        for each in step_data:
            logic_row = []
            for row in each:
                # finding what to do for each dataset
                # if len(row)==5 and row[1] != "":     ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement
                if (
                    row[1] == "element parameter" or row[1] == "compare"
                ):  ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement
                    continue

                elif row[1] == "action":
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Checking the action to be performed in the action row",
                        1,
                    )
                    if row[0] == "compare variable":
                        result = Action_Handler(each, row)
                    else:
                        new_data_set = Shared_Resources.Handle_Step_Data_Variables(
                            [each]
                        )
                        if new_data_set in failed_tag_list:
                            return "zeuz_failed"
                        result = Action_Handler(new_data_set[0], row)
                    if result in failed_tag_list:
                        return "zeuz_failed"
                    elif result in skipped_tag_list:
                        return "skipped"

                # If middle column = optional action, call action handler, but always return a pass
                elif row[1] == "optional action":
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Checking the optional action to be performed in the action row: %s"
                        % str(row),
                        1,
                    )
                    result = Action_Handler(
                        each, row[0]
                    )  # Pass data set, and action_name to action handler
                    if result == "zeuz_failed":
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Optional action failed. Returning pass anyway",
                            2,
                        )
                    result = "passed"

                elif row[1] == "body" or row[1] == "header" or row[1] == "headers":
                    continue
                elif row[1] == "conditional action":
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Checking the logical conditional action to be performed in the conditional action row",
                        1,
                    )
                    logic_decision = ""
                    logic_row.append(row)
                    if len(logic_row) == 2:
                        # element_step_data = each[0:len(step_data[0])-2:1]
                        element_step_data = Shared_Resources.Handle_Step_Data_Variables(
                            [each]
                        )
                        element_step_data = Get_Element_Step_Data(element_step_data[0])
                        returned_step_data_list = Validate_Step_Data(element_step_data)
                        if (returned_step_data_list == []) or (
                            returned_step_data_list == "zeuz_failed"
                        ):
                            return "zeuz_failed"
                        else:
                            try:
                                Element = Get_Element(returned_step_data_list, "all")
                                if Element == "zeuz_failed":
                                    logic_decision = "false"
                                else:
                                    logic_decision = "true"
                            except Exception as errMsg:
                                errMsg = (
                                    "Could not find element in the by the criteria..."
                                )
                                return CommonUtil.Exception_Handler(
                                    sys.exc_info(), None, errMsg
                                )
                    else:
                        continue

                    for conditional_steps in logic_row:
                        if logic_decision in conditional_steps:
                            print(conditional_steps[2])
                            list_of_steps = conditional_steps[2].split(",")
                            for each_item in list_of_steps:
                                data_set_index = int(each_item) - 1
                                cond_result = Sequential_Actions(
                                    [step_data[data_set_index]]
                                )
                                if cond_result == "zeuz_failed":
                                    return "zeuz_failed"
                                elif cond_result == "skipped":
                                    return "skipped"
                            return "passed"
                else:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "The sub-field information is incorrect. Please provide accurate information on the data set(s).",
                        3,
                    )
                    return "zeuz_failed"

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


"===================== ===x=== Sequential Action Section Ends ===x=== ======================"


"============================= Validation Section Begins =============================="


# Validation of step data passed on by the user
def Validate_Step_Data(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        method = ""
        url = ""
        body = None
        temp_body = "{"
        headers = "{"
        plain_body_text = False
        payload = ""
        graphql_dict = dict()

        for each in step_data:
            if "graphql" in each[1]:
                graphql_dict[each[0].strip()] = CommonUtil.parse_value_into_object(each[2])
            elif each[1].lower().strip() == "element parameter":
                element_parameter = each[0].lower().strip()
                if element_parameter == "method":
                    method = each[2]
                elif element_parameter == "url":
                    url = each[2]
                elif element_parameter == "payload":
                    payload = """%s""" % str(each[2])
            elif each[1].lower().strip() == "body":
                if each[0].lower().strip() == "plain text":
                    temp_body = each[2]
                    plain_body_text = True
                else:
                    if temp_body == "{":
                        temp_body += '"%s" : "%s"' % (each[0], each[2])
                    else:
                        temp_body += ', "%s" : "%s"' % (each[0], each[2])

            elif each[1].lower().strip() in ("header", "headers"):
                if headers == "{":
                    headers += '"%s" : "%s"' % (each[0], each[2])
                else:
                    headers += ', "%s" : "%s"' % (each[0], each[2])

        headers += "}"
        if not plain_body_text:
            temp_body += "}"

        # If its a GraphQL request, we should take body as raw.
        if graphql_dict:
            body = graphql_dict
        else:
            body = temp_body

        validated_data = (url, method, body, headers, payload)
        return validated_data

    except Exception:
        errMsg = "Could not find the new page element requested. "
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_data_from_list(input_list, identifier):
    try:
        for id in str(identifier).strip().split("."):
            if id.isdigit():
                index = int(id)
            else:
                index = id
            input_list = input_list[id]
        return input_list
    except:
        return ""


# Inserting a field into a list of shared variables
@logger
def Insert_Tuple_Into_List(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        list_name = ""
        iterate_over = ""
        result_list = []
        fields = ""
        for row in step_data:
            if row[0] == "list name":
                list_name = str(row[2]).strip()
            elif row[0] == "iterate over":
                iterate_over = str(row[2]).strip()
            elif row[1] == "action":
                fields = str(row[2]).strip()

        data = Validate_Step_Data(step_data)
        handle_rest_call(data, "none")
        if iterate_over.startswith("rest_response"):
            var = iterate_over.split(".")
            iterate_over = Shared_Resources.Get_Shared_Variables("rest_response")
            i = 1
            while i < len(var):
                if var[i].isdigit():
                    index = int(var[i])
                else:
                    index = var[i]
                iterate_over = iterate_over[index]
                i += 1

        for data in iterate_over:
            each_tuple = []
            for field in fields.split(","):
                each_tuple.append(get_data_from_list(data, field))
            result_list.append(each_tuple)

        Shared_Resources.Set_Shared_Variables(list_name, result_list)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
