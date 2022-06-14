from Framework.Utilities.decorators import logger, deprecated
import inspect,sys,random
from Framework.Utilities import CommonUtil, ConfigModule
import traceback
global sr
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr

MODULE_NAME = inspect.getmodulename(__file__)

@logger
def locust_config(data_set):
    """
    Save locust configuration to a variable
    Args:
        data_set:
          swarm              | input parameter    | integer
          spawn              | input parameter    | integer
          locust config      | performance action | variable_name

    Returns:
        "passed" if success.
        "zeuz_failed" otherwise.
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        locust_var = losust_var_name = swarm = spawn = None
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if mid.strip().lower() == "input parameter":
                    if "swarm" == left:
                        swarm = float(right.strip().lower())
                    elif "spawn" == left:
                        spawn = float(right.strip().lower())
                elif "action" == mid.strip().lower():
                    if "locust config" == left:
                        losust_var_name = right.strip()
            if None in [losust_var_name,swarm,spawn]: 
                CommonUtil.ExecLog(sModuleInfo,  f"dataset is inaccurate", 3)
                return "zeuz_failed"
            locust_var = {
                            "locust_config": {
                                "swarm": swarm,
                                "spawn": spawn
                            },
                            "users": {}
                    }    
        except:
            CommonUtil.ExecLog(sModuleInfo, "Failed to parse data.", 1)
            traceback.print_exc()
            return "zeuz_failed"
        sr.Set_Shared_Variables(losust_var_name, locust_var)
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
        locust_var = losust_var_name = name = user_type = wait_time = host = None
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if mid.strip().lower() == "input parameter":
                    if "name" == left:
                        name = right.strip().lower()
                    if "type" == left:
                        user_type = right.strip().lower()
                    elif "wait_time" == left:
                        wait_time = right.strip().lower()
                    elif "host" == left:
                        host = right.strip().lower()
                elif mid.strip().lower() == "action":
                    if "assign locust user" == left:
                        losust_var_name = right.strip()
            if None in [losust_var_name,name,user_type,wait_time,host]: 
                CommonUtil.ExecLog(sModuleInfo,  f"dataset is inaccurate", 3)
                return "zeuz_failed"
            locust_var = sr.Get_Shared_Variables(losust_var_name,log=False)
            locust_var['users'][name] = {'type':user_type,'wait_time' : wait_time,'host':host,'tasks':[]}
        except:
            CommonUtil.ExecLog(sModuleInfo, "Failed to parse data.", 1)
            traceback.print_exc()
            return "zeuz_failed"
        sr.Set_Shared_Variables(losust_var_name, locust_var)
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
        locust_var = locust_var_name = action = data = name = task_name = None
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if mid.strip().lower() == "input parameter":
                    if "action" == left.strip():
                        action = right.strip().lower()
                    elif "data" == left.strip():
                        data = right.strip().lower()
                    elif "name" == left.strip():
                        name = right.strip().lower()
                    elif "task name" == left:
                        task_name = right.strip().lower()
                elif mid.strip().lower() == "action":
                    if "assign locust task" == left:
                        locust_var_name = right.strip()
            if None in [locust_var_name,action,data,name,task_name]:
                CommonUtil.ExecLog(sModuleInfo,  f"dataset is inaccurate", 3)
                return "zeuz_failed"
            locust_var = sr.Get_Shared_Variables(locust_var_name,log=False)
            locust_var['users'][name]['tasks'].append({'action':action,'data':data,'name':task_name}) 
        except:
            CommonUtil.ExecLog(sModuleInfo, "Failed to parse data.", 1)
            traceback.print_exc()
            return "zeuz_failed"
        sr.Set_Shared_Variables(locust_var_name, locust_var)
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())