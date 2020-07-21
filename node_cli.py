# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import os, sys, time, os.path, base64, signal
from getpass import getpass

from Framework.module_installer import install_missing_modules
from utils import input_with_timeout, TimeoutExpired

# Append correct paths so that it can find the configuration files and other modules
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "Framework"))
# Move to Framework directory, so all modules can be seen
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "Framework"))

from Framework.Utilities import (
    ConfigModule,
    RequestFormatter,
    CommonUtil,
    FileUtilities,
    All_Device_Info,
)
from Framework import MainDriverApi

sys.path.append("..")


def signal_handler(sig, frame):
    print("Disconnecting from server...")
    disconnect_from_server()
    sys.exit(0)


def password_hash(encrypt, key, pw):
    """ Encrypt, decrypt password and encode in plaintext """
    # This is just an obfuscation technique, so the password is not immediately seen by users
    # Zeuz_Node.py has a similar function that will need to be updated if this is changed

    try:
        from node_gui import pass_encode

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

if not os.path.exists(
    os.path.join(
        os.path.realpath(__file__).split("node_cli.py")[0],
        os.path.join("AutomationLog"),
    )
):
    os.mkdir(
        os.path.join(
            os.path.realpath(__file__).split("node_cli.py")[0],
            os.path.join("AutomationLog"),
        )
    )


# temp_ini_file = os.path.join(os.path.join(FileUtilities.get_home_folder(), os.path.join('Desktop',os.path.join('AutomationLog',ConfigModule.get_config_value('Advanced Options', '_file')))))

temp_ini_file = os.path.join(
    os.path.join(
        os.path.realpath(__file__).split("node_cli.py")[0],
        os.path.join(
            "AutomationLog", ConfigModule.get_config_value("Advanced Options", "_file")
        ),
    )
)


def zeuz_authentication_prompts_for_cli():
    prompts = ["server_address", "username", "password"]
    for prompt in prompts:
        if prompt == "password":
            value = getpass()
            ConfigModule.add_config_value(
                AUTHENTICATION_TAG, prompt, password_hash(False, "zeuz", value)
            )
        else:
            try:
                value = input_with_timeout(f"{prompt.capitalize()} : ", 60)
            except TimeoutExpired:
                print("Sorry, times up. Login again with the previous inputs")
                break
            else:
                ConfigModule.add_config_value(AUTHENTICATION_TAG, prompt, str(value))


def Login(cli=False):
    install_missing_modules()
    username = ConfigModule.get_config_value(AUTHENTICATION_TAG, USERNAME_TAG)
    password = ConfigModule.get_config_value(AUTHENTICATION_TAG, PASSWORD_TAG)
    server_name = ConfigModule.get_config_value(AUTHENTICATION_TAG, "server_address")

    if password == "YourUserNameGoesHere":
        password = password
    else:
        password = pass_decode("zeuz", password)
    project = ConfigModule.get_config_value(AUTHENTICATION_TAG, PROJECT_TAG)
    team = ConfigModule.get_config_value(AUTHENTICATION_TAG, TEAM_TAG)

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
    exit_script = False  # Reset exit variable

    while True:
        processing_test_case = False
        if exit_script:
            break
        # Test to ensure server is up before attempting to login
        r = check_server_online()

        # Login to server
        if r != False:  # Server is up
            try:
                default_team_and_project = RequestFormatter.UpdatedGet(
                    "get_default_team_and_project_api", {"username": username}
                )

                if not default_team_and_project:
                    CommonUtil.ExecLog(
                        "",
                        "Default team and project catching Failed. Username incorrect",
                        4,
                        False,
                    )
                    break
                user_info_object["project"] = default_team_and_project["project_name"]
                user_info_object["team"] = default_team_and_project["team_name"]
                r = RequestFormatter.Get("login_api", user_info_object)
                CommonUtil.ExecLog(
                    "",
                    f"Authentication check for user='{username}', "
                    f"project='{user_info_object['project']}', team='{user_info_object['team']}', server='{server_name}'",
                    4,
                    False,
                )
                if r:
                    CommonUtil.ExecLog("", "Authentication Successful", 4, False)
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
                            RequestFormatter.Get(
                                "send_machine_time_zone_api", time_zone_object
                            )
                            # end
                        except Exception as e:
                            CommonUtil.ExecLog(
                                "", "Time zone settings failed {}".format(e), 4, False
                            )
                        RunAgain = RunProcess(tester_id)
                        if RunAgain == False:
                            break  # Exit login
                    else:
                        return False
                elif (
                    r == {} or r == False
                ):  # Server should send "False" when user/pass is wrong
                    CommonUtil.ExecLog(
                        "",
                        "Authentication Failed. Username or password incorrect",
                        4,
                        False,
                    )

                    if cli:
                        zeuz_authentication_prompts_for_cli()
                        Login(cli=True)

                    break
                else:  # Server likely sent nothing back or RequestFormatter.Get() caught an exception
                    CommonUtil.ExecLog(
                        "",
                        "Login attempt incomplete, waiting 60 seconds before trying again ",
                        4,
                        False,
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
            if cli:
                zeuz_authentication_prompts_for_cli()
                Login(cli=True)

            time.sleep(60)
    CommonUtil.ExecLog(
        "", "Zeuz Node Offline", 4, False
    )  # GUI relies on this exact text. GUI must be updated if this is changed
    processing_test_case = False


def disconnect_from_server():
    """ Exits script - Used by Zeuz Node GUI """
    global exit_script
    exit_script = True
    CommonUtil.set_exit_mode(True)  # Tell Sequential Actions to exit


def RunProcess(sTesterid):
    etime = time.time() + (30 * 60)  # 30 minutes
    while 1:
        try:
            if exit_script:
                return False
            if time.time() > etime:
                return True  # Timeout reached, re-login. We do this because after about 3-4 hours this function will hang, and thus not be available for deployment

            r = RequestFormatter.Get(
                "is_run_submitted_api", {"machine_name": sTesterid}
            )
            if r and "run_submit" in r and r["run_submit"]:
                processing_test_case = True
                CommonUtil.ExecLog(
                    "",
                    "**************************\n* STARTING NEW TEST CASE *\n**************************",
                    4,
                    False,
                )
                PreProcess()
                value = MainDriverApi.main(device_dict)
                CommonUtil.ExecLog("", "updating db with parameter", 4, False)
                if value == "pass":
                    if exit_script:
                        return False
                    break
                CommonUtil.ExecLog(
                    "", "Successfully updated db with parameter", 4, False
                )
            else:
                time.sleep(3)
                if r and "update" in r and r["update"]:
                    _r = RequestFormatter.Get(
                        "update_machine_with_time_api", {"machine_name": sTesterid}
                    )
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


def PreProcess():
    # current_path = os.path.join(FileUtilities.get_home_folder(), os.path.join('Desktop', 'AutomationLog'))
    current_path = os.path.join(
        os.path.realpath(__file__).split("node_cli.py")[0],
        os.path.join("AutomationLog"),
    )

    retVal = FileUtilities.CreateFolder(current_path, forced=False)
    if retVal:
        # now save it in the global_config.ini
        TEMP_TAG = "Advanced Options"
        file_name = ConfigModule.get_config_value(TEMP_TAG, "_file")
        current_path_file = os.path.join(current_path, file_name)
        FileUtilities.CreateFile(current_path_file)
        ConfigModule.clean_config_file(current_path_file)
        ConfigModule.add_section("sectionOne", current_path_file)
        ConfigModule.add_config_value(
            "sectionOne", "temp_run_file_path", current_path, current_path_file
        )


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
                "",
                "Machine is registered as online with name: %s" % (r["name"]),
                4,
                False,
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
    try:
        dependency_tag = "Dependency"
        dependency_option = ConfigModule.get_all_option(dependency_tag)
        project = default_team_and_project["project_name"]
        team = default_team_and_project["team_name"]
        r = RequestFormatter.Get(
            "get_all_dependency_name_api", {"project": project, "team": team}
        )
        obtained_list = [x.lower() for x in r]
        # print "Dependency: ",dependency_list
        missing_list = list(set(obtained_list) - set(dependency_option))
        # print missing_list
        if missing_list:
            CommonUtil.ExecLog(
                "",
                ",".join(missing_list)
                + " missing from the configuration file - settings.conf",
                4,
                False,
            )
            return False
        else:
            CommonUtil.ExecLog(
                "",
                "All the dependency present in the configuration file - settings.conf",
                4,
                False,
            )
            final_dependency = []
            for each in r:
                temp = []
                each_dep_list = ConfigModule.get_config_value(
                    dependency_tag, each
                ).split(",")
                # print each_dep_list
                for each_item in each_dep_list:
                    if each_item.count(":") == 2:
                        name, bit, version = each_item.split(":")

                    else:
                        name = each_item.split(":")[0]
                        bit = 0
                        version = ""
                        # print name,bit,version
                    temp.append((name, bit, version))
                final_dependency.append((each, temp))
            return final_dependency
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


def check_server_online():
    try:  # Check if we have a connection, if not, exit. If user has a wrong address or no address, RequestFormatter will go into a failure loop
        r = RequestFormatter.Head("login_api")
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


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    print("Press Ctrl-C to disconnect and quit.")

    arg_options = [arg for arg in sys.argv[1:] if arg.startswith("--")]

    if "--logout" in arg_options:
        ConfigModule.remove_config_value(AUTHENTICATION_TAG, "server_address")

    Login(cli=True)
