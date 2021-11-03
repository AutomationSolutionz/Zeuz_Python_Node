#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
import os
from pathlib import Path
version_path = Path(os.getcwd())/"Framework"/"Version.txt"
with open(version_path, "r"):
    text = version_path.read_text()
    text = text[text.find("=")+1:].split("\n")[0].strip()
    os.system("title " + "ZeuZ Scriptless Automation tool -- " + text)
    print(version_path.read_text())
from Framework.module_installer import install_missing_modules
install_missing_modules()

import sys, time, os.path, base64, signal, argparse, requests, zipfile
from getpass import getpass
from urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm

# Suppress the InsecureRequestWarning since we use verify=False parameter.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

from Framework.Utilities import ConfigModule

PROJECT_ROOT = os.path.abspath(os.curdir)
# Append correct paths so that it can find the configuration files and other modules
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Framework"))

# kill any process that is running  from the same node folder
pid = os.getpid()

pidfile = os.path.abspath(__file__).split("node_cli.py")[0] + 'pid.txt'

try:
    import psutil
    pidfile_read = open(pidfile)
    pidNumber = pidfile_read.read()
    pidNumber = int("".join(pidNumber.split()))
    print("Process ID", pidNumber)
    p = psutil.Process(pidNumber)
    p.terminate()
except:
    True

try:
    f = open(pidfile, "w")
    f.write(str(os.getpid()))
    f.close()
except:
    True



if not os.path.exists(
    os.path.join(
        os.path.abspath(__file__).split("node_cli.py")[0],
        os.path.join("AutomationLog"),
    )
):
    os.mkdir(
        os.path.join(
            os.path.abspath(__file__).split("node_cli.py")[0],
            os.path.join("AutomationLog"),
        )
    )

# Tells node whether it should run a test set/deployment only once and quit.
RUN_ONCE = False
local_run = False

# Move to Framework directory, so all modules can be seen
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Framework"))
sys.path.append("..")

from Framework.Utilities import (
    RequestFormatter,
    CommonUtil,
    FileUtilities as FL,
    All_Device_Info,
    self_updater
)
from Framework import MainDriverApi


temp_ini_file = (
    Path(PROJECT_ROOT)
    / "AutomationLog"
    / ConfigModule.get_config_value("Advanced Options", "_file")
)

import subprocess

def signal_handler(sig, frame):
    print("Disconnecting from server...")
    disconnect_from_server()
    sys.exit(0)


def password_hash(encrypt, key, pw):
    """ Encrypt, decrypt password and encode in plaintext """
    # This is just an obfuscation technique, so the password is not immediately seen by users
    # Zeuz_Node.py has a similar function that will need to be updated if this is changed

    try:
        def pass_encode(key, clear):
            enc = []
            for i in range(len(clear)):
                key_c = key[i % len(key)]
                enc_c = (ord(clear[i]) + ord(key_c)) % 256
                enc.append(enc_c)
            return base64.urlsafe_b64encode(bytes(enc))

        result = pass_encode(key, pw)

        return result
    except Exception as e:
        print("Exception in password {}".format(e))
        print("Error decrypting password. Enter a new password {}".format(e))
        return ""


def detect_admin():
    # Windows only - Return True if program run as admin

    import subprocess as s

    if sys.platform == "win32":
        command = "net session >nul 2>&1"  # This command can only be run by admin
        try:
            output = s.check_output(
                command, shell=True
            )  # Causes an exception if we can't run
        except:
            return False
    return True


# Have user install tzlocal if this fails - we try to do it for them first
try:
    from tzlocal import get_localzone
except:
    import subprocess as s

    print(
        "Module 'tzlocal' is not installed. This is required to start the graphical interface. Please enter the root password to install."
    )

    if sys.platform == "win32":
        try:
            # Elevate permissions
            if not detect_admin():
                os.system(
                    "powershell -command Start-Process \"python '..\\%s'\" -Verb runAs"
                    % sys.argv[0].split(os.sep)[-1]
                )  # Re-run this program with elevated permissions to admin
                sys.exit(
                    1
                )  # exit this instance and let the elevated instance take over

            # Install
            print(s.check_output("pip install tzlocal"))
        except Exception as e:
            print("Failed to install. Please run: pip install tzlocal: ", e)
            input("Press ENTER to exit")
            sys.exit(1)
    elif sys.platform == "linux2":
        print(
            s.Popen(
                "sudo -S pip install tzlocal".split(" "), stdout=s.PIPE, stderr=s.STDOUT
            ).communicate()[0]
        )
    else:
        print("Could not automatically install required modules")
        input("Press ENTER to exit")
        quit()

    try:
        from tzlocal import get_localzone
    except:
        input(
            "Could not install tzlocal. Please do this manually by running: pip install tzlocal as administrator"
        )
        quit()


"""Constants"""
AUTHENTICATION_TAG = "Authentication"
USERNAME_TAG = "username"
PASSWORD_TAG = "password"
PROJECT_TAG = "project"
TEAM_TAG = "team"
device_dict = {}

processing_test_case = (
    False  # Used by Zeuz Node GUI to check if we are in the middle of a run
)
exit_script = False  # Used by Zeuz Node GUI to exit script


def zeuz_authentication_prompts_for_cli():
    prompts = ["server_address", "api-key"]
    values = []
    for prompt in prompts:
        if prompt == "password":
            value = getpass()
            ConfigModule.add_config_value(
                AUTHENTICATION_TAG, prompt, password_hash(False, "zeuz", value)
            )
        else:
            display_text = prompt.replace("_", " ").capitalize()
            value = input(f"{display_text}: ")
            if prompt == "server_address":
                if value[-1] == "/":
                    value = value[:-1]
            ConfigModule.add_config_value(AUTHENTICATION_TAG, prompt, str(value))
        values.append(value)
    return values


def Login(cli=False, run_once=False, log_dir=None):
    username = ConfigModule.get_config_value(AUTHENTICATION_TAG, USERNAME_TAG)
    password = ConfigModule.get_config_value(AUTHENTICATION_TAG, PASSWORD_TAG)
    server_name = ConfigModule.get_config_value(AUTHENTICATION_TAG, "server_address")
    api = ConfigModule.get_config_value(AUTHENTICATION_TAG, "api-key")
    api_flag = True
    if not api or not server_name:
        zeuz_authentication_prompts_for_cli()
        for i in range(30):     # it takes time to save in the file. so lets wait 15 sec
            time.sleep(0.5)
            api = ConfigModule.get_config_value(AUTHENTICATION_TAG, "api-key")
            server_name = ConfigModule.get_config_value(AUTHENTICATION_TAG, "server_address")
            if api and server_name:
                break
    while api and server_name:
        url = '/api/auth/token/verify?api_key=%s' % (api)
        r = RequestFormatter.Get(url)
        if r:
            try:
                token = r['token']
                res = RequestFormatter.Get("/api/user", headers={'Authorization': "Bearer %s" % token})
                info = res[0]
                username = info['username']
                api_flag = False
                ConfigModule.add_config_value(AUTHENTICATION_TAG, "username", username)
                break
            except:
                print("Incorrect API key...")
                server_name, api = zeuz_authentication_prompts_for_cli()
                continue
        else:
            print("Server down. Trying again after 30 seconds")
            time.sleep(30)

    if password == "YourUserNameGoesHere":
        password = password
    else:
        password = pass_decode("zeuz", password)

    # form payload object
    user_info_object = {
        "username": username,
        "password": password,
        "project": "",
        "team": "",
    }

    # Iniitalize GUI Offline call
    CommonUtil.set_exit_mode(False)
    global exit_script
    global processing_test_case

    exit_script = False  # Reset exit variable

    while True:
        if exit_script:
            break

        # if not user_info_object["username"] or not user_info_object["password"]:
        #    break

        # Test to ensure server is up before attempting to login
        r = check_server_online()

        # Login to server
        if r:  # Server is up
            try:
                default_team_and_project = RequestFormatter.UpdatedGet(
                    "get_default_team_and_project_api", {"username": username}
                )

                if not default_team_and_project:
                    CommonUtil.ExecLog(
                        "AUTH FAILED",
                        "Failed to get TEAM and PROJECT information. Incorrect username or password.",
                        3,
                        False,
                    )
                    break
                user_info_object["project"] = default_team_and_project["project_name"]
                user_info_object["team"] = default_team_and_project["team_name"]

                CommonUtil.ExecLog("", f"Authenticating user: {username}", 4, False)

                if api_flag:
                    r = RequestFormatter.Post("login_api", user_info_object)

                if r or (isinstance(r, dict) and r['status'] == 200):
                    CommonUtil.ExecLog(
                        "",
                        f"Authentication successful: USER='{username}', "
                        f"PROJECT='{user_info_object['project']}', TEAM='{user_info_object['team']}', SERVER='{server_name}'",
                        4
                    )
                    ConfigModule.add_config_value("sectionOne", PROJECT_TAG, user_info_object['project'], temp_ini_file)
                    ConfigModule.add_config_value("sectionOne", TEAM_TAG, user_info_object['team'], temp_ini_file)
                    global device_dict
                    device_dict = All_Device_Info.get_all_connected_device_info()
                    machine_object = update_machine(
                        dependency_collection(default_team_and_project),
                        default_team_and_project,
                    )
                    if machine_object["registered"]:
                        tester_id = machine_object["name"]
                        try:
                            # send machine's time zone
                            local_tz = str(get_localzone())
                            time_zone_object = {
                                "time_zone": local_tz,
                                "machine": tester_id,
                            }
                            executor = CommonUtil.GetExecutor()
                            executor.submit(RequestFormatter.Get, "send_machine_time_zone_api", time_zone_object)
                            # RequestFormatter.Get("send_machine_time_zone_api", time_zone_object)
                            # end
                        except Exception as e:
                            CommonUtil.ExecLog("", "Time zone settings failed {}".format(e), 4, False)
                        # Telling the node_manager that the node is ready to deploy
                        CommonUtil.node_manager_json(
                            {
                                "state": "idle",
                                "report": {
                                    "zip": None,
                                    "directory": None,
                                }
                            }
                        )
                        run_again = RunProcess(tester_id, user_info_object, run_once=run_once, log_dir=log_dir)

                        if not run_again:
                            break  # Exit login
                    else:
                        return False
                elif not r:  # Server should send "False" when user/pass is wrong
                    CommonUtil.ExecLog(
                        "",
                        f"Authentication Failed. Username or password incorrect. SERVER='{server_name}'",
                        4,
                        False,
                    )

                    if cli:
                        zeuz_authentication_prompts_for_cli()
                        Login(cli=True)

                    break
                else:  # Server likely sent nothing back or RequestFormatter.Get() caught an exception
                    CommonUtil.ExecLog(
                        "", "Login attempt failed, retrying in 60 seconds...", 4, False,
                    )
                    if cli:
                        zeuz_authentication_prompts_for_cli()
                        Login(cli=True)
                    time.sleep(60)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Error_Detail = (
                    (str(exc_type).replace("type ", "Error Type: "))
                    + ";"
                    + "Error Message: "
                    + str(exc_obj)
                    + ";"
                    + "File Name: "
                    + fname
                    + ";"
                    + "Line: "
                    + str(exc_tb.tb_lineno)
                )
                CommonUtil.ExecLog("", Error_Detail, 4, False)
                CommonUtil.ExecLog(
                    "",
                    "Error logging in, waiting 60 seconds before trying again",
                    4,
                    False,
                )
                time.sleep(60)

        # Server down, wait and retry
        else:
            CommonUtil.ExecLog(
                "",
                "Server down or verify the server address, waiting 60 seconds before trying again",
                4,
                False,
            )
            # if cli:
            #     zeuz_authentication_prompts_for_cli()
            #     Login(cli=True)
            time.sleep(60)

    if run_once:
        print("[OFFLINE]", "Zeuz Node is going offline after running one session, since `--once` or `-o` flag is specified.")
    else:
        CommonUtil.ExecLog("[OFFLINE]", "Zeuz Node Offline", 3)  # GUI relies on this exact text. GUI must be updated if this is changed

    processing_test_case = False


def disconnect_from_server():
    """ Exits script - Used by Zeuz Node GUI """
    global exit_script
    exit_script = True
    CommonUtil.set_exit_mode(True)  # Tell Sequential Actions to exit


def RunProcess(sTesterid, user_info_object, run_once=False, log_dir=None):
    etime = time.time() + (30 * 60)  # 30 minutes
    executor = CommonUtil.GetExecutor()
    while True:
        try:
            if exit_script:
                return False
            if time.time() > etime:
                print("30 minutes over, logging in again")
                return True  # Timeout reached, re-login. We do this because after about 3-4 hours this function will hang, and thus not be available for deployment
            executor.submit(RequestFormatter.Get, "update_machine_with_time_api", {"machine_name": sTesterid})
            # r = RequestFormatter.Get("is_run_submitted_api", {"machine_name": sTesterid})
            r = RequestFormatter.Get(f"is_submitted_api?machine_name={sTesterid}")
            # r = requests.get(RequestFormatter.form_uri("is_submitted_api"), {"machine_name": sTesterid}, verify=False).json()
            Userid = (CommonUtil.MachineInfo().getLocalUser()).lower()
            if r and "found" in r and r["found"]:
                size = round(int(r["file_size"]) / 1024, 2)
                if size > 1024:
                    size = str(round(size / 1024, 2)) + " MB"
                else:
                    size = str(size) + " KB"
                save_path = temp_ini_file.parent / "attachments"
                CommonUtil.ExecLog("", "Downloading dataset and attachments of %s into:\n%s" % (size, str(save_path/"input.zip")), 4)
                save_path.mkdir(parents=True, exist_ok=True)
                headers = RequestFormatter.add_api_key_to_headers({})
                response = requests.get(RequestFormatter.form_uri("getting_json_data_api"), {"machine_name": Userid}, stream=True, verify=False, **headers)
                chunk_size = 4096
                progress_bar = tqdm(total=r["file_size"], unit='B', mininterval=0, unit_scale=True, unit_divisor=1024, leave=False)
                with open(save_path/"input.zip", 'wb') as file:
                    for data in response.iter_content(chunk_size):
                        progress_bar.update(len(data))
                        file.write(data)
                    progress_bar.refresh()
                progress_bar.close()
                z = zipfile.ZipFile(save_path/"input.zip")
                z.extractall(save_path)
                z.close()
                os.unlink(save_path/"input.zip")
                PreProcess(log_dir=log_dir)
                # Telling the node_manager that a run_id is deployed
                CommonUtil.node_manager_json(
                    {
                        "state": "in_progress",
                        "report": {
                            "zip": None,
                            "directory": None,
                        }
                    }
                )
                try:
                    MainDriverApi.main(device_dict, user_info_object)
                except:
                    pass

                if run_once or exit_script:
                    return False
                CommonUtil.ExecLog("", "Successfully updated db with parameter", 4, False)
                break
            else:
                time.sleep(3)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            Error_Detail = (
                (str(exc_type).replace("type ", "Error Type: "))
                + ";"
                + "Error Message: "
                + str(exc_obj)
                + ";"
                + "File Name: "
                + fname
                + ";"
                + "Line: "
                + str(exc_tb.tb_lineno)
            )
            CommonUtil.ExecLog("", Error_Detail, 4, False)
            break  # Exit back to login() - In some circumstances, this while loop will get into a state when certain errors occur, where nothing runs, but loops forever. This stops that from happening
    return True


def PreProcess(log_dir=None):
    current_path_file = temp_ini_file
    ConfigModule.clean_config_file(current_path_file)
    ConfigModule.add_section("sectionOne", current_path_file)

    if not ConfigModule.has_section("Selenium_driver_paths"):
        ConfigModule.add_section("Selenium_driver_paths")
        ConfigModule.add_config_value("Selenium_driver_paths", "chrome_path", "")
        ConfigModule.add_config_value("Selenium_driver_paths", "firefox_path", "")
        ConfigModule.add_config_value("Selenium_driver_paths", "edge_path", "")
        ConfigModule.add_config_value("Selenium_driver_paths", "opera_path", "")
        ConfigModule.add_config_value("Selenium_driver_paths", "ie_path", "")

    # If `log_dir` is not specified, then store all logs inside Zeuz Node's
    # "AutomationLog" folder
    if log_dir is None:
        log_dir = temp_ini_file.parent

    ConfigModule.add_config_value(
        "sectionOne",
        "temp_run_file_path",
        str(log_dir),
        current_path_file,
    )
    ConfigModule.add_config_value("sectionOne", "sTestStepExecLogId", "node_cli", temp_ini_file)


def update_machine(dependency, default_team_and_project_dict):
    try:
        # Get Local Info object
        oLocalInfo = CommonUtil.MachineInfo()

        local_ip = oLocalInfo.getLocalIP()
        testerid = (oLocalInfo.getLocalUser()).lower()

        project = default_team_and_project_dict["project_name"]
        team = default_team_and_project_dict["team_name"]
        if not dependency:
            dependency = ""
        _d = {}
        for x in dependency:
            t = []
            for i in x[1]:
                _t = ["name", "bit", "version"]
                __t = {}
                for index, _i in enumerate(i):
                    __t.update({_t[index]: _i})
                if __t:
                    t.append(__t)
            _d.update({x[0]: t})
        dependency = _d
        available_to_all_project = ConfigModule.get_config_value(
            "Advanced Options", "available_to_all_project"
        )
        allProject = "no"
        if str(available_to_all_project).lower() == "true":
            allProject = "yes"
        update_object = {
            "machine_name": testerid,
            "local_ip": local_ip,
            "dependency": dependency,
            "project": project,
            "team": team,
            "device": device_dict,
            "allProject": allProject,
        }
        r = RequestFormatter.Get("update_automation_machine_api", update_object)
        if r["registered"]:
            CommonUtil.ExecLog(
                "", "Zeuz Node is online: %s" % (r["name"]), 4, False,
            )
        else:
            if r["license"]:
                CommonUtil.ExecLog("", "Machine is not registered as online", 4, False)
            else:
                if "message" in r:
                    CommonUtil.ExecLog("", r["message"], 4, False)
                    CommonUtil.ExecLog(
                        "", "Machine is not registered as online", 4, False
                    )
                else:
                    CommonUtil.ExecLog(
                        "", "Machine is not registered as online", 4, False
                    )
        return r
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = (
            (str(exc_type).replace("type ", "Error Type: "))
            + ";"
            + "Error Message: "
            + str(exc_obj)
            + ";"
            + "File Name: "
            + fname
            + ";"
            + "Line: "
            + str(exc_tb.tb_lineno)
        )
        CommonUtil.ExecLog("", Error_Detail, 4, False)


def dependency_collection(default_team_and_project):
    """ In future we will again fetch this feature of validating dependencies with server and local """
    return False
    # try:
    #     dependency_tag = "Dependency"
    #     dependency_option = ConfigModule.get_all_option(dependency_tag)
    #     project = default_team_and_project["project_name"]
    #     team = default_team_and_project["team_name"]
    #     r = RequestFormatter.Get(
    #         "get_all_dependency_name_api", {"project": project, "team": team}
    #     )
    #     obtained_list = [x.lower() for x in r]
    #     # print "Dependency: ",dependency_list
    #     missing_list = list(set(obtained_list) - set(dependency_option))
    #     # print missing_list
    #     if missing_list:
    #         # CommonUtil.ExecLog(
    #         #     "",
    #         #     ",".join(missing_list)
    #         #     + " missing from the configuration file - settings.conf",
    #         #     4,
    #         #     False,
    #         # )
    #         return False
    #     else:
    #         CommonUtil.ExecLog(
    #             "",
    #             "All the dependency present in the configuration file - settings.conf",
    #             4,
    #             False,
    #         )
    #         final_dependency = []
    #         for each in r:
    #             temp = []
    #             each_dep_list = ConfigModule.get_config_value(
    #                 dependency_tag, each
    #             ).split(",")
    #             # print each_dep_list
    #             for each_item in each_dep_list:
    #                 if each_item.count(":") == 2:
    #                     name, bit, version = each_item.split(":")
    #
    #                 else:
    #                     name = each_item.split(":")[0]
    #                     bit = 0
    #                     version = ""
    #                     # print name,bit,version
    #                 temp.append((name, bit, version))
    #             final_dependency.append((each, temp))
    #         return final_dependency
    # except Exception as e:
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #     Error_Detail = (
    #         (str(exc_type).replace("type ", "Error Type: "))
    #         + ";"
    #         + "Error Message: "
    #         + str(exc_obj)
    #         + ";"
    #         + "File Name: "
    #         + fname
    #         + ";"
    #         + "Line: "
    #         + str(exc_tb.tb_lineno)
    #     )
    #     CommonUtil.ExecLog("", Error_Detail, 4, False)


def check_server_online():
    try:  # Check if we have a connection, if not, exit. If user has a wrong address or no address, RequestFormatter will go into a failure loop
        r = RequestFormatter.Head("")
        return r
    except Exception as e:  # Occurs when server is down
        print("Exception in check_server_online {}".format(e))
        return False


def get_team_names(noerror=False):
    """ Retrieve all teams user has access to """

    try:
        username = ConfigModule.get_config_value(AUTHENTICATION_TAG, USERNAME_TAG)
        password = ConfigModule.get_config_value(AUTHENTICATION_TAG, PASSWORD_TAG)

        if password == "YourUserNameGoesHere":
            password = password
        else:
            password = pass_decode("zeuz", password)
        user_info_object = {USERNAME_TAG: username, PASSWORD_TAG: password}

        if not check_server_online():
            return []

        r = RequestFormatter.Get("get_user_teams_api", user_info_object)
        teams = [x[0] for x in r]  # Convert into a simple list
        return teams
    except:
        if noerror == False:
            CommonUtil.ExecLog("", "Error retrieving team names", 4, False)
        return []


def get_project_names(team):
    """ Retrieve projects for given team """

    try:
        username = ConfigModule.get_config_value(AUTHENTICATION_TAG, USERNAME_TAG)
        password = ConfigModule.get_config_value(AUTHENTICATION_TAG, PASSWORD_TAG)

        if password == "YourUserNameGoesHere":
            password = password
        else:
            password = pass_decode("zeuz", password)

        user_info_object = {
            USERNAME_TAG: username,
            PASSWORD_TAG: password,
            TEAM_TAG: team,
        }

        if not check_server_online():
            return []

        r = RequestFormatter.Get("get_user_projects_api", user_info_object)
        projects = [x[0] for x in r]  # Convert into a simple list
        return projects
    except:
        CommonUtil.ExecLog("", "Error retrieving project names", 4, False)
        return []


# def pwdec(pw):
#     try:
#         chars = [chr(x) for x in range(33, 127)]
#         key = 'zeuz'
#         pw = b64decode(pw)
#         result = ''
#         j = 0
#         for i in pw:
#             value = chr(ord(i) ^ ord(key[j]))
#             if value in chars: result += value
#             else: raise ValueError('') # Windows only, base64 decoding of an invalid string does not cause an exception, so we have to try to check for a bad password
#             j += 1
#             if j == len(key): j = 0
#         return result
#     except Exception as e:
#         print("Exception in password decrypt: {}".format(e))
#         #CommonUtil.ExecLog('', "Error decrypting password. Use the graphical interface to set a new password", 4, False)
#         return ''


def pass_decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc + "========")
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + enc[i] - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

def check_for_updates():
    """Checks for update. If any update is not found the code will continue to login prompts, otherwise it will
    download the newest version of Zeuz Node, install it and restart/quit the terminal.
    """
    try:
        # Just check for updates, and schedule testing to see if updates checking is complete

        print("Checking for software updates")
        self_updater.check_for_updates()

        # No update, do nothing, and thus stop checking
        if self_updater.check_complete in ("check", "noupdate"):
            print("No software updates available")

        # Update check complete, we have an update, start install
        elif self_updater.check_complete[0:6] == "update":
            # Print update notes
            try:
                print("\nUpdate notes:")
                for note in str(self_updater.check_complete[7:]).split(";"):
                    print(note)
                print("*** A new update is available. Automatically installing.")

                update_path = os.path.dirname(
                    os.path.abspath(__file__)
                ).replace(os.sep + "Framework", "")
                self_updater.main(update_path)
            except:
                print("Couldn't install updates")

            try:
                print("*** Update installed. Automatically restarting. ***")
                time.sleep(2)  # Wait a bit, so they can see the message
                subprocess.Popen(
                    'python "%s"'
                    % os.path.abspath(sys.argv[0]).replace(os.sep + "Framework", ""),
                    shell=True,
                )  # Restart zeuz node
                quit()  # Exit this process
            except:
                print("Exception in Restart. Please restart manually")
                time.sleep(2)
                quit()

        # Some error occurred during updating
        elif "error" in self_updater.check_complete:
            print("An error occurred during update")

    except Exception as e:
        print("Exception in CheckUpdates")


def Local_run(log_dir=None):
    try:
        PreProcess(log_dir=log_dir)
        user_info_object = {}
        user_info_object['project'] = ConfigModule.get_config_value("sectionOne", PROJECT_TAG, temp_ini_file)
        user_info_object['team'] = ConfigModule.get_config_value("sectionOne", TEAM_TAG, temp_ini_file)
        device_dict = All_Device_Info.get_all_connected_device_info()
        rem_config = {"local_run": True}
        ConfigModule.remote_config = rem_config
        MainDriverApi.main(device_dict, user_info_object)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = (
            (str(exc_type).replace("type ", "Error Type: "))
            + ";"
            + "Error Message: "
            + str(exc_obj)
            + ";"
            + "File Name: "
            + fname
            + ";"
            + "Line: "
            + str(exc_tb.tb_lineno)
        )
        CommonUtil.ExecLog("", Error_Detail, 4, False)

def command_line_args() -> Path:
    """
    This function handles command line scripts with given arguments.

    Returns:
      `log_dir` - the custom log directory if specified, otherwise `None`.

    Example 1:
    1. python node_cli.py
    2. node_cli.py
    These 2 scripts will skip all kind of actions in this function because they dont have any arguments and will execute
    Login(CLI=true) from __main__

    Example 2:
    1. python node_cli.py --logout
    2. node_cli.py --logout
    3. node_cli.py -l

    These 3 scripts will will execute logout from server and then will execute Login(CLI=true) from __main__ then
    you have to provide server, username, password one by one in the terminal to login

    Example 3:
    1. python node_cli.py --username USER_NAME --password PASS_XYZ --server https://zeuz.zeuz.ai
    2. node_cli.py --logout --username USER_NAME --password PASS_XYZ --server https://zeuz.zeuz.ai
    3. node_cli.py -u USER_NAME -p PASS_XYZ -s https://zeuz.zeuz.ai
    4. python node_cli.py -k YOUR_API_KEY --server https://zeuz.zeuz.ai

    These 3 scripts will will execute logout from server and then will execute Login(CLI=true) from __main__ but you
    don't need to provide server, username, password again. It will execute the login process automatically for you

    Example 3:
    1. python node_cli.py --help
    2. node_cli.py --help
    3. node_cli.py -h

    These 3 scripts will show the documentation for every arguments and will execute sys.exit()

    Example 4:
    1. python node_cli.py --ussssername USER_NAME --password PASS_XYZ --server https://zeuz.zeuz.ai
    2. node_cli.py --u USER_NAME -p PASS_XYZ -s
    3. node_cli.py --logout https://zeuz.zeuz.ai

    Above are some invalid arguments which will show some log/documentation and will execute sys.exit()
    """
    # try:
    parser_object = argparse.ArgumentParser("node_cli parser")
    parser_object.add_argument(
        "-u", "--username", action="store", help="Enter your username", metavar=""
    )
    parser_object.add_argument(
        "-p", "--password", action="store", help="Enter your password", metavar=""
    )
    parser_object.add_argument(
        "-s", "--server", action="store", help="Enter server address", metavar=""
    )
    parser_object.add_argument(
        "-k", "--api_key", action="store", help="Enter api key", metavar=""
    )
    parser_object.add_argument(
        "-n", "--node_id", action="store", help="Enter custom node_id", metavar=""
    )
    parser_object.add_argument(
        "-m", "--max_run_history", action="store", help="How many latest histories do you want to keep", metavar=""
    )
    parser_object.add_argument(
        "-l", "--logout", action="store_true", help="Logout from the server"
    )
    parser_object.add_argument(
        "-a", "--auto_update", action="store_true", help="Updates your Zeuz Node"
    )
    parser_object.add_argument(
        "-r", "--local_run", action="store_true", help="Performs a local run"
    )
    parser_object.add_argument(
        "-o", "--once", action="store_true", help="If specified, this flag tells node to run only one session (test set/deployment) and then quit immediately"
    )
    parser_object.add_argument(
        "-d", "--log_dir", action="store", help="Specify a custom directory for storing Run IDs and logs.", metavar=""
    )
    all_arguments = parser_object.parse_args()

    username = all_arguments.username
    password = all_arguments.password
    server = all_arguments.server
    api = all_arguments.api_key
    node_id = all_arguments.node_id
    max_run_history = all_arguments.max_run_history
    logout = all_arguments.logout
    auto_update = all_arguments.auto_update

    # Check if custom log directory exists, if not, we'll try to create it. If
    # we can't create the custom log directory, we should error out.
    log_dir = None
    try:
        if all_arguments.log_dir:
            log_dir = Path(all_arguments.log_dir.strip())
            log_dir.mkdir(parents=True, exist_ok=True)

            # Try creating a temporary file to see if we have enough permissions
            # to write in the specified log directory.
            touch_file = log_dir / "touch"
            touch_file.touch()
            touch_file.unlink()
    except PermissionError:
        raise Exception(f"ERR: Zeuz Node does not have enough permissions to write to the specified log directory: {log_dir}")
    except:
        raise Exception(f"ERR: Invalid custom log directory, or failed to create directory: {log_dir}")

    global local_run
    local_run = all_arguments.local_run

    global RUN_ONCE
    RUN_ONCE = all_arguments.once

    if server and server[-1] == "/":
        server = server[:-1]

    if auto_update:
        check_for_updates()
    if username or password or server or logout or api:
        if api and server:
            ConfigModule.remove_config_value(AUTHENTICATION_TAG, "api-key")
            ConfigModule.add_config_value(AUTHENTICATION_TAG, "api-key", api)
            ConfigModule.remove_config_value(AUTHENTICATION_TAG, "server_address")
            ConfigModule.add_config_value(AUTHENTICATION_TAG, "server_address", server)
        elif username and password and server:
            ConfigModule.remove_config_value(AUTHENTICATION_TAG, "server_address")
            ConfigModule.add_config_value(AUTHENTICATION_TAG, "username", username)
            ConfigModule.add_config_value(
                AUTHENTICATION_TAG, "password", password_hash(False, "zeuz", password)
            )
            ConfigModule.add_config_value(AUTHENTICATION_TAG, "server_address", server)
        elif logout:
            ConfigModule.remove_config_value(AUTHENTICATION_TAG, "server_address")
            zeuz_authentication_prompts_for_cli()
        else:
            CommonUtil.ExecLog(
                "AUTHENTICATION FAILED",
                "Enter the command line arguments in correct format.  Type -h for help.",
                3,
            )
            sys.exit()  # exit and let the user try again from command line
    if node_id:
        CommonUtil.MachineInfo().setLocalUser(node_id)
    if max_run_history:
        pass

    """argparse module automatically shows exceptions of corresponding wrong arguments
     and executes sys.exit(). So we don't need to use try except"""
    # except:
    #     CommonUtil.ExecLog("\ncommand_line_args : node_cli.py","Did not parse anything from given arguments",4)
    #     sys.exit()

    return log_dir


def Bypass():
    while True:
        user_info_object = {'project': 'zeuz', 'team': 'zeuz'}
        oLocalInfo = CommonUtil.MachineInfo()
        testerid = (oLocalInfo.getLocalUser()).lower()
        print("[Bypass] Zeuz Node is online: %s" % testerid)
        RunProcess(testerid, user_info_object)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    print("Press Ctrl-C to disconnect and quit.")

    """We can use this condition to skip command_line_args() when "python node_cli.py" or "node_cli.py" is executed"""
    # if (len(sys.argv)) > 1:
    try:
        log_dir = command_line_args()
    except Exception as e:
        from colorama import Fore
        print(Fore.RED + str(e))
        print("Exiting...")
        sys.exit(1)

    if local_run:
        Local_run(log_dir=log_dir)
    else:
        # Bypass()
        Login(cli=True, run_once=RUN_ONCE, log_dir=log_dir)
    CommonUtil.ShutdownExecutor()
