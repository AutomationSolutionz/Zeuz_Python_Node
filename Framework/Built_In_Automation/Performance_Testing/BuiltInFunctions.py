import json
import os
import traceback
import inspect,sys,random
import subprocess
from jinja2 import Environment, FileSystemLoader

from settings import performance_report_dir, temp_ini_file, attachments_DIR
from Framework.Utilities.decorators import logger, deprecated
from Framework.Utilities import CommonUtil, ConfigModule
global sr
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr

MODULE_NAME = inspect.getmodulename(__file__)


def get_run_id(json_file_path):
    """
    Gets the run_id for the current session.
    If there is no run_id then the default is `no_run_id`.
    """
    Userid = (CommonUtil.MachineInfo().getLocalUser()).lower()

    with open(json_file_path, "r") as f:
        all_run_id_info = json.load(f)

    if len(all_run_id_info) == 0:
        CommonUtil.ExecLog("", "No Test Run Schedule found for the current user : %s" % Userid, 2)
        return "no_run_id"
    run_id = all_run_id_info[0]["run_id"].replace(":", "-")
    return run_id


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
    attachment_json_file = attachments_DIR.glob("*.zeuz.json").__next__()

    try:
        locust_var = losust_var_name = swarm = spawn = run_time = autostart = autoquit = None
        html = ConfigModule.get_config_value("sectionOne", "performance_report", temp_ini_file) + os.sep + get_run_id(json_file_path=attachment_json_file) + ".html"
        csv = ConfigModule.get_config_value("sectionOne", "performance_report", temp_ini_file) + os.sep + get_run_id(json_file_path=attachment_json_file)
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if mid.strip().lower() in ["element parameter", "input parameter"]:
                    if "swarm" == left:
                        swarm = int(right.strip().lower())
                    elif "spawn" == left:
                        spawn = int(right.strip().lower())
                    elif "run time" == left:
                        run_time = right.strip().lower()
                    elif "autostart" == left and right in ("True", "true", "Yes", "yes", "Y", "y"):
                        autostart = True
                    elif "autoquit" == left and right in ("True", "true", "Yes", "yes", "Y", "y"):
                        autoquit = True
                    elif "html" == left:
                        # Todo: change to the performance directory
                        # html = performance_report_dir + os.sep + "".join([right.replace(" ", "_"), ".html"])
                        html = html.replace(".html", "") + "".join(["_", right.replace(" ", "_"), ".html"])
                    elif "csv" == left:
                        csv = csv + "_" + right.replace(" ", "_")
                elif "action" == mid.strip().lower():
                    if "locust config" == left:
                        losust_var_name = right.strip()
            if None in [losust_var_name, swarm, spawn]:
                CommonUtil.ExecLog(sModuleInfo,  f"dataset is inaccurate", 3)
                return "zeuz_failed"
            locust_var = {
                            "locust_config": {
                                "swarm": swarm,
                                "spawn": spawn,
                                "run_time": run_time,
                                "autostart": autostart,
                                "autoquit": autoquit,
                                "html": html,
                                "csv": csv
                            },
                            "task_sets": {},
                            "users": {}
                    }    
        except:
            CommonUtil.Exception_Handler(sModuleInfo, "Failed to parse data.", 3)
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
                if mid.strip().lower() == "optional parameter":
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
            return "zeuz_failed"
        sr.Set_Shared_Variables(locust_var_name, locust_var)
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def load_jinja_template_and_generate_locust_py(jinja_template_dir="", jinja_file_path="",
                                               jinja2_template_variable=None, output_file_path=""):
    """
    Loads the jinja template and generate the locust python file using the variable parameter
    Also saves the python file to the given output_file_path.
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    file_loader = FileSystemLoader(jinja_template_dir)
    env = Environment(loader=file_loader)
    jinja_template = env.get_template(jinja_file_path)
    template_string = jinja_template.render(PERF_VARIABLE=jinja2_template_variable)
    print(template_string)

    # write locust python file
    with open(output_file_path, "w") as output_file:
        output_file.write(template_string)
    CommonUtil.ExecLog(sModuleInfo, "Passed", 1)


@logger
def run_performance_test(data_set):
    """
    This function will perform at the last for building the locust python file and running it.
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        locust_var_name = None
        # Todo: output file needs to renamed each time by either run_id or debug_id
        locust_output_file = f"{os.path.dirname(os.path.realpath(__file__))}{os.sep}locust_files{os.sep}run_locust_python_file.py"
        jinja2_temp_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep + "templates"
#
        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if mid.strip().lower() == "action":
                    if "run performance test" == left:
                        locust_var_name = right.strip()
        except Exception as e:
            CommonUtil.ExecLog(sModuleInfo, "Failed to parse data.", 3)
            return "zeuz_failed"

        locust_var = sr.Get_Shared_Variables(locust_var_name, log=False)
        locust_var_config = locust_var.get('locust_config')
        # Load templates folder and then load the template file then render the template
        load_jinja_template_and_generate_locust_py(jinja_template_dir=jinja2_temp_dir,
                                                   jinja_file_path="performance_template.txt",
                                                   jinja2_template_variable=locust_var,
                                                   output_file_path=locust_output_file)

        # Todo: Run the locust python file
        command = ["locust", "-f", locust_output_file,
                   "-u", str(locust_var_config.get('swarm')),
                   "-r", str(locust_var_config.get('spawn')),
                   "-t", locust_var_config.get('run_time'),
                   "--autostart" if locust_var_config.get('autostart') else "",
                   "--autoquit" if locust_var_config.get('autoquit') else "", "1" if locust_var_config.get('autoquit') else "",
                   "--html", locust_var_config.get('html'),
                   "--csv", locust_var_config.get('csv'),
                   "--csv-full-history"]
        print(" ".join(command))
        sp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        # rtrn = sp.wait()
        out, err = sp.communicate()
        print(out)
        print(err)

        return "passed"

    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, e, 3)
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def generate_performance_test(data_set):
    """
    This function will perform at the last for building the locust python file.
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        locust_var_name = None
        # Todo: output file needs to be renamed each time by either run_id or debug_id
        locust_output_file = f"{os.path.dirname(os.path.realpath(__file__))}{os.sep}locust_files{os.sep}gen_locust_python_file.py"
        jinja2_temp_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep + "templates"

        try:
            for left, mid, right in data_set:
                left = left.strip().lower()
                if mid.strip().lower() == "action":
                    if "generate performance test" == left:
                        locust_var_name = right.strip()
        except Exception as e:
            CommonUtil.ExecLog(sModuleInfo, "Failed to parse data.", 3)
            return "zeuz_failed"

        locust_var = sr.Get_Shared_Variables(locust_var_name, log=False)
        # Load templates folder and then load the template file then render the template
        load_jinja_template_and_generate_locust_py(jinja_template_dir=jinja2_temp_dir,
                                                   jinja_file_path="performance_template.txt",
                                                   jinja2_template_variable=locust_var,
                                                   output_file_path=locust_output_file)

        return "passed"

    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, e, 3)
        return CommonUtil.Exception_Handler(sys.exc_info())


# @logger
# def run_performance_test(data_set):
#     """
#     This is a test function
#     """
#     sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
#
#     try:
#         print("executed the code from run_performace_t")
#         return "passed"
#
#     except Exception as e:
#         CommonUtil.ExecLog(sModuleInfo, e, 3)
#         return CommonUtil.Exception_Handler(sys.exc_info())
