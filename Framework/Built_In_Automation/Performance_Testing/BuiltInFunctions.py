from Framework.Utilities.decorators import logger, deprecated
import inspect,sys,random
from Framework.Utilities import CommonUtil, ConfigModule
import traceback
global sr
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr

MODULE_NAME = inspect.getmodulename(__file__)

@logger
def locust_config(data_set):
    """-Comment Needs to be updated!!!!
    Save variable with native python type.

    Can also create/append/update a str, list or dictionary from the given data.

    Accepts any valid Python representation or JSON data.

    Args:
        data_set:
          data               | element parameter  | valid JSON string
          operation          | element parameter  | save/update
          extra operation    | optional parameter | length/no duplicate/ascending sort/descending sort
          save into variable | common action      | variable_name

    Returns:
        "passed" if success.
        "zeuz_failed" otherwise.
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        variable_value = None
        variable_name = None
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if "swarm" in left:
                    swarm = float(right.strip().lower())
                elif "spawn" in left:
                    spawn = float(right.strip().lower())
                elif "action" in mid and 'locust config' in left:
                    variable_value = {
                        "locust_config": {
                            "swarm": swarm,
                            "spawn": spawn
                        },
                        "users": {}
                    }
                    variable_name = right.strip()
        except:
            CommonUtil.ExecLog(sModuleInfo, "Failed to parse data.", 1)
            traceback.print_exc()
            return "zeuz_failed"
        sr.Set_Shared_Variables(variable_name, variable_value)
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def assign_locust_user(data_set):
    """-Comment Needs to be updated!!!!
    Save variable with native python type.

    Can also create/append/update a str, list or dictionary from the given data.

    Accepts any valid Python representation or JSON data.

    Args:
        data_set:
          data               | element parameter  | valid JSON string
          operation          | element parameter  | save/update
          extra operation    | optional parameter | length/no duplicate/ascending sort/descending sort
          save into variable | common action      | variable_name

    Returns:
        "passed" if success.
        "zeuz_failed" otherwise.
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        variable_value = None
        variable_name = None
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if "user title" in left:
                    user_title = right.strip().lower()
                if "type" in left:
                    user_type = right.strip().lower()
                elif "wait_time" in left:
                    wait_time = right.strip().lower()
                elif "host" in left:
                    host = right.strip().lower()
                elif "assign locust user" in left:
                    variable_name = right.strip()
                    locust_var = sr.Get_Shared_Variables(variable_name)
                    locust_var['users'][user_title] = {'type':user_type,'wait_time' : wait_time,'host':host,'tasks':[]}
                    variable_value = locust_var
        except:
            CommonUtil.ExecLog(sModuleInfo, "Failed to parse data.", 1)
            traceback.print_exc()
            return "zeuz_failed"
        sr.Set_Shared_Variables(variable_name, variable_value)
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())

def assign_locust_task(data_set):
    """-Comment Needs to be updated!!!!
    Save variable with native python type.

    Can also create/append/update a str, list or dictionary from the given data.

    Accepts any valid Python representation or JSON data.

    Args:
        data_set:
          data               | element parameter  | valid JSON string
          operation          | element parameter  | save/update
          extra operation    | optional parameter | length/no duplicate/ascending sort/descending sort
          save into variable | common action      | variable_name

    Returns:
        "passed" if success.
        "zeuz_failed" otherwise.
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        variable_value = None
        variable_name = None
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if "action" in left:
                    action = right.strip().lower()
                elif "data" in left:
                    data = right.strip().lower()
                elif "name" in left:
                    name = right.strip().lower()
                elif "user title" in left:
                    user_title = right.strip().lower()
                elif "assign locust task" in left:
                    variable_name = right.strip()
                    locust_var = sr.Get_Shared_Variables(variable_name)
                    locust_var['users'][user_title]['tasks'].append({'action':action,'data':data,'name':name}) 
                    variable_value = locust_var
        except:
            CommonUtil.ExecLog(sModuleInfo, "Failed to parse data.", 1)
            traceback.print_exc()
            return "zeuz_failed"
        sr.Set_Shared_Variables(variable_name, variable_value)
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())