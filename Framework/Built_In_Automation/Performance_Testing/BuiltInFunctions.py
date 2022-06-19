import os
from jinja2 import Environment, FileSystemLoader
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
                if mid.strip().lower() in ["element parameter","input parameter"]:
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
                            "task_sets": {},
                            "users": {}
                    }    
        except:
            CommonUtil.Exception_Handler(sModuleInfo, "Failed to parse data.", 3)
            traceback.print_exc()
            return "zeuz_failed"
        sr.Set_Shared_Variables(losust_var_name, locust_var)
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def assign_locust_user(data_set):
    """
    Add Locust user configuration to the existing locust variable
    This action provides that data to creates a user class into locust file
    Args:
        data_set:
          wait_time          | input parameter    | between(int,int)
          host               | input parameter    | url of host
          name               | input parameter    | user/class name Case sensitive
          type               | input parameter    | type of user/class
          assign locust user | performance action | existing locust variable name
    Returns:
        "passed" if success.
        "zeuz_failed" otherwise.
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        locust_var = losust_var_name = user_name = user_type = wait_time = host = None
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if mid.strip().lower() in ["element parameter","input parameter"]:
                    if "user name" == left:
                        user_name = right.strip()
                    if "type" == left:
                        user_type = right.strip().lower()
                        user_type = 'HttpUser' if user_type == 'httpuser' else "User" if user_type == "user" else None
                    elif "wait_time" == left:
                        wait_time = right.strip().lower()
                    elif "host" == left:
                        host = right.strip().lower()
                elif mid.strip().lower() == "action":
                    if "assign locust user" == left:
                        losust_var_name = right.strip()
            if None in [losust_var_name,user_name,user_type,wait_time,host]: 
                CommonUtil.ExecLog(sModuleInfo,  f"dataset is inaccurate", 3)
                return "zeuz_failed"
                
            locust_var = sr.Get_Shared_Variables(losust_var_name,log=False)
            locust_var['users'][user_name] = {'type':user_type,'wait_time' : wait_time,'host':host,'tasks':[],'user_task_sets':[]}
        except:
            CommonUtil.Exception_Handler(sModuleInfo, "Failed to parse data.", 3)
            traceback.print_exc()
            return "zeuz_failed"
        sr.Set_Shared_Variables(losust_var_name, locust_var)
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def assign_locust_taskset(data_set):
    """
    Add Locust user configuration to the existing locust variable
    This action provides that data to creates a user class into locust file
    Args:
        data_set:
          wait_time          | input parameter    | between(int,int)
          host               | input parameter    | url of host
          name               | input parameter    | user/class name Case sensitive
          type               | input parameter    | type of user/class
          assign locust user | performance action | existing locust variable name
    Returns:
        "passed" if success.
        "zeuz_failed" otherwise.
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        locust_var = losust_var_name = taskset_name = user_names =  None
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if mid.strip().lower() in ["element parameter","input parameter"]:
                    if "taskset name" == left:
                        taskset_name = right.strip()
                    if "user name" == left:
                        user_names = [un.strip() for un in right.strip().split(',')]
                    elif "sequential" == left:
                        sequential = right.strip().lower() in ("true", "yes", "ok", "enable")
                elif mid.strip().lower() == "action":
                    if "assign locust taskset" == left:
                        losust_var_name = right.strip()
            if None in [losust_var_name,taskset_name]: 
                CommonUtil.ExecLog(sModuleInfo,  f"dataset is inaccurate", 3)
                return "zeuz_failed"
            locust_var = sr.Get_Shared_Variables(losust_var_name,log=False)
            locust_var['task_sets'][taskset_name] = {'sequential':sequential,'tasks':[]}
            for user_name in user_names:
                locust_var['users'][user_name]['user_task_sets'].append(taskset_name)
        except:
            CommonUtil.Exception_Handler(sModuleInfo, "Failed to parse data.", 3)
            traceback.print_exc()
            return "zeuz_failed"
        sr.Set_Shared_Variables(losust_var_name, locust_var)
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def assign_locust_task(data_set):
    """
    Add task configuration to the existing locust user
    This action provides that data to define the tasks performed by locust user/class
    Args:
        data_set:
          action             | input parameter    | get/post etc
          data               | input parameter    | url of endpoint
          task name          | input parameter    | string
          name               | input parameter    | existing user/class name Case sensitive
          assign locust task | performance action | existing locust variable name
    Returns:
        "passed" if success.
        "zeuz_failed" otherwise.
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        locust_var = locust_var_name = action = url = user_name = task_name = taskset_name = weight = None
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if mid.strip().lower() in ["element parameter","input parameter"]:
                    if "action" == left.strip():
                        action = right.strip().lower()
                    elif "url" == left.strip():
                        url = right.strip().lower()
                    elif "user name" == left.strip():
                        user_name = right.strip()
                    elif "taskset name" == left.strip():
                        taskset_name = right.strip()
                    elif "task name" == left:
                        task_name = right.strip().lower()
                if mid.strip().lower() == "parameter":
                    if "weight" == left.strip():
                        weight = right.strip().lower()
                elif mid.strip().lower() == "action":
                    if "assign locust task" == left:
                        locust_var_name = right.strip()
            if None in [locust_var_name,action,url,task_name]:
                CommonUtil.ExecLog(sModuleInfo,  f"dataset is inaccurate", 3)
                return "zeuz_failed"
            if sum(x is not None for x in [user_name,taskset_name]) != 1:
                CommonUtil.ExecLog(sModuleInfo,  f"either user name or taskset name should be given", 3)
                return "zeuz_failed"
            locust_var = sr.Get_Shared_Variables(locust_var_name,log=False)
            task_data = {'action':action,'url':url,'name':task_name,'weight':weight}
            if user_name:
                locust_var['users'][user_name]['tasks'].append(task_data) 
            elif(taskset_name):
                locust_var['task_sets'][taskset_name]['tasks'].append(task_data)
        except:
            CommonUtil.Exception_Handler(sModuleInfo, "Failed to parse data.", 3)
            traceback.print_exc()
            return "zeuz_failed"
        sr.Set_Shared_Variables(locust_var_name, locust_var)
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


# @logger
# def run_performance_test(data_set):
#     """
#     This function will perform at the last for building the locust python file and running it.
#     """
#     sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
#
#     try:
#         locust_var_name = None
#         locust_output_file = f"{os.getcwd()}{os.sep}locust_files{os.sep}locust_python_file.py"
#
#         try:
#             for left, mid, right in data_set:
#                 left = left.strip().lower()
#                 if mid.strip().lower() == "action":
#                     if "run performance test" == left:
#                         locust_var_name = right.strip()
#         except Exception as e:
#             CommonUtil.ExecLog(sModuleInfo, "Failed to parse data.", 3)
#             traceback.print_exc()
#             return "zeuz_failed"
#
#         # Todo: Run the locust python file and run it
#         # Load templates folder and then load the template file then render the template
#         file_loader = FileSystemLoader('templates')
#         env = Environment(loader=file_loader)
#         jinja_template = env.get_template("performance_template.txt")
#         template_string = jinja_template.render(PERF_VARIABLE=sr.Get_Shared_Variables(locust_var_name, log=False))
#         print(template_string)
#
#         # write python file
#         with open(locust_output_file, "w") as output_file:
#             output_file.write(template_string)
#
#         return "passed"
#
#     except Exception as e:
#         CommonUtil.ExecLog(sModuleInfo, e, 3)
#         return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def generate_performance_test(data_set):
    """
    This function will perform at the last for building the locust python file.
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        locust_var_name = None
        locust_output_file = f"{os.path.dirname(os.path.realpath(__file__))}{os.sep}locust_files{os.sep}locust_python_file.py"
        jinja2_temp_dir = f"{os.getcwd()}{os.sep}templates"
        jinja2_temp_dir2 = os.path.dirname(os.path.realpath(__file__)) + os.sep + "templates"

        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if mid.strip().lower() == "action":
                    if "generate performance test" == left:
                        locust_var_name = right.strip()
        except Exception as e:
            CommonUtil.ExecLog(sModuleInfo, "Failed to parse data.", 3)
            traceback.print_exc()
            return "zeuz_failed"

        # Todo: Generate the locust python file and run it
        # Load templates folder and then load the template file then render the template
        # file_loader = FileSystemLoader("E:\\Z_github_dev\\zeuz_node\\Zeuz_Python_Node\\Framework\\Built_In_Automation\\Performance_Testing\\templates")
        file_loader = FileSystemLoader(jinja2_temp_dir2)
        env = Environment(loader=file_loader)
        jinja_template = env.get_template("performance_template.txt")
        template_string = jinja_template.render(PERF_VARIABLE=sr.Get_Shared_Variables(locust_var_name, log=False))
        print(template_string)

        # write python file
        with open(locust_output_file, "w") as output_file:
            output_file.write(template_string)

        return "passed"

    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, e, 3)
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def run_performance_test(data_set):
    """
    This is a test function
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        print("executed the code from run_performace_t")
        return "passed"

    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, e, 3)
        return CommonUtil.Exception_Handler(sys.exc_info())
