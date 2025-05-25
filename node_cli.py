#!/usr/bin/env python3
import os
import socket
import sys
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import platform
import datetime
from dataclasses import dataclass
import os.path
import base64
import signal
import argparse
import json
import time
import threading
from datetime import date
from datetime import datetime as dt

import psutil
import requests
from configobj import ConfigObj
from dotenv import load_dotenv
from colorama import init as colorama_init
from colorama import Fore
from rich.table import Table
from rich.console import Console
from rich import traceback
from urllib3.exceptions import InsecureRequestWarning
import uvicorn

print(
    f"Python {platform.python_version()} ({platform.architecture()[0]}) @ {sys.executable}"
)
print(f"Current file path: {os.path.abspath(__file__)}")


def adjust_python_path():
    """Adjusts the Python path to include the Framework directory."""
    root_dir = Path.cwd()
    framework_dir = root_dir / "Framework"

    automation_log_dir = root_dir / "AutomationLog"
    automation_log_dir.mkdir(exist_ok=True)

    # Append correct paths so that it can find the configuration files and other modules
    sys.path.append(str(framework_dir))

    # Move to Framework directory and add parent to path for module imports
    os.chdir(framework_dir)


def create_config_file():
    settings_conf_path = Path.cwd() / "settings.conf"
    if settings_conf_path.exists():
        return

    today = date.today().strftime("%Y-%m-%d")

    config = ConfigObj()
    config["Authentication"] = {"username": "", "api-key": "", "server_address": ""}
    config["Advanced Options"] = {
        "module_update_interval": 30,
        "log_delete_interval": 7,
        "last_module_update_date": today,
        "last_log_delete_date": today,
        "element_wait": 10,
        "available_to_all_project": False,
        "_file": "temp_config.ini",
        "_file_upload_path": "TestExecutionLog",
        "stop_live_log": False,
    }
    config["Inspector"] = {
        "Window": "",
        "No_of_level_to_skip": 0,
        "ai_plugin": True,
    }
    config["server"] = {"port": 0}
    config.filename = str(settings_conf_path)
    config.write()
    print(f"Created settings.conf at {settings_conf_path}")


adjust_python_path()
create_config_file()


from Framework.module_installer import (  # noqa: E402
    check_min_python_version,
    update_outdated_modules,
    # install_missing_modules,
)

from Framework.deploy_handler import (  # noqa: E402
    long_poll_handler,
    adapter,
)
from Framework.Utilities import ConfigModule  # noqa: E402
from Framework.Utilities import live_log_service  # noqa: E402
from Framework.node_server_state import STATE  # noqa: E402
from server import main as node_server  # noqa: E402


def start_server():
    settings_conf_path = Path.cwd() / "settings.conf"

    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) == 0

    def run():
        try:
            node_server_port = 18100
            tries = 0
            while is_port_in_use(node_server_port) and tries < 99:
                node_server_port += 1
                tries += 1
            config = ConfigObj(str(settings_conf_path))
            config["server"]["port"] = node_server_port
            config.write()
            uvicorn.run(
                node_server.main(),
                host="127.0.0.1",
                port=node_server_port,
                log_level="warning",
            )

        except Exception as e:
            print(f"[WARN] Failed to launch node-server: {str(e)}")

    t = threading.Thread(target=run, daemon=True)
    t.start()


def kill_old_process(pid_file_path: os.PathLike):
    """kill any process that is running  from the same node folder."""
    import psutil

    try:
        with open(pid_file_path, "r") as f:
            pid_number = int(f.read().strip())
            process = psutil.Process(pid_number)
            process.terminate()
            process.wait(
                timeout=10
            )  # Wait for the process to terminate, with a timeout
            print(f"Process with PID {pid_number} terminated.")
    except Exception:
        pass

    try:
        with open(pid_file_path, "w") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass


# Conditionally monkey-patch datetime module to include the `fromisoformat` method.
# TODO: remove this when we upgrade to Python 3.11
def monkeypatch_fromisoformat():
    try:
        import sys

        target_version = (3, 11)
        if sys.version_info < target_version:
            from backports.datetime_fromisoformat import MonkeyPatch  # type: ignore

            MonkeyPatch.patch_fromisoformat()
    except Exception:
        print("WARN: failed to monkeypatch fromisoformat")


def main():
    # Load environment variables from .env file
    load_dotenv()

    traceback.install(show_locals=True, max_frames=1)

    # Suppress the InsecureRequestWarning since we use verify=False parameter.
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)  # type: ignore

    # Disable WebdriverManager SSL verification.
    os.environ["WDM_SSL_VERIFY"] = "0"

    colorama_init(autoreset=True)

    kill_old_process(Path.cwd().parent / "pid.txt")
    check_min_python_version(min_python_version="3.11", show_warning=True)
    update_outdated_modules()
    monkeypatch_fromisoformat()
    start_server()

    # Set the console title to include the version number.
    version_path = Path("Version.txt")
    text = version_path.read_text()
    text = text[text.find("=") + 1 :].split("\n")[0].strip()
    if os.name == "nt":
        os.system(
            f"title Node {text} - 🐍 {platform.python_version()} {platform.architecture()[0]}"
        )


main()

# Tells node whether it should run a test set/deployment only once and quit.
RUN_ONCE = False
local_run = False

from Framework.Utilities import (  # noqa: E402
    RequestFormatter,
    CommonUtil,
    All_Device_Info,
)
from Framework import MainDriverApi  # noqa: E402


TMP_INI_FILE = (
    Path.cwd().parent
    / "AutomationLog"
    / ConfigModule.get_config_value("Advanced Options", "_file")
)


def kill_child_processes():
    try:
        parent = psutil.Process()
        children = parent.children(recursive=True)
        for child in children:
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass
    except Exception:
        pass


def signal_handler(sig, frame):
    print("\n--- SIGINT received, quitting ---\n")
    CommonUtil.run_cancelled = True
    CommonUtil.ShutdownExecutor()
    kill_child_processes()
    os._exit(0)


"""Constants"""
AUTHENTICATION_TAG = "Authentication"
PROJECT_TAG = "project"
TEAM_TAG = "team"
device_dict: dict[str, Any] = {}


def destroy_session():
    """
    Destroy session file.
    """

    # Remove session file if prompted for new authentication
    session_bin_path = Path(RequestFormatter.SESSION_FILE_NAME)
    if session_bin_path.exists():
        try:
            session_bin_path.unlink()
        except Exception:
            print("[ERROR] failed to remove session file")


def zeuz_authentication_prompts_for_cli():
    """
    Prompts user for inputting new credentials.
    """
    destroy_session()
    prompts = ["server_address", "api-key"]
    values = []
    for prompt in prompts:
        display_text = prompt.replace("_", " ").capitalize()
        value = input(f"{display_text}: ")
        if prompt == "server_address":
            value = urlparse(value)
            value = f"{value.scheme}://{value.netloc}"
        ConfigModule.add_config_value(AUTHENTICATION_TAG, prompt, str(value))
        values.append(value)
    return values


@dataclass
class UserData:
    username: str
    email: str
    team_id: int
    project_id: str


def Login(
    server_name: str,
    run_once: bool = False,
    log_dir: os.PathLike | None = None,
):
    console = Console()

    # Login to ZeuZ server.
    user_data = UserData(
        username="admin",
        email="info@automationsolutionz.com",
        project_id="PROJ-17",
        team_id=2,
    )

    # Load session from disk if available.
    session_bin_path = Path(RequestFormatter.SESSION_FILE_NAME)
    load_from_session = session_bin_path.exists()

    RequestFormatter.load_cookies(session_bin_path)

    try:
        if load_from_session:
            data, status_code = RequestFormatter.renew_token()
            if status_code != 200:
                data, status_code = RequestFormatter.login()
                return
        else:
            data, status_code = RequestFormatter.login()

        # # Upon successful login, replace the api key in the settings
        # # file with a dummy value since we don't need it anymore.
        # TODO: Implement api key encryption.
        # ConfigModule.add_config_value(AUTHENTICATION_TAG, "api-key", "dummy")

        if status_code == 200:
            user_data = UserData(
                username=data["user"]["username"],
                email=data["user"]["email"],
                project_id=data["user"]["project_id"],
                team_id=data["user"]["team_id"],
            )

            ConfigModule.add_config_value(
                AUTHENTICATION_TAG, "username", user_data.username
            )
            ConfigModule.add_config_value(
                "sectionOne", PROJECT_TAG, user_data.project_id, TMP_INI_FILE
            )  # type: ignore
            ConfigModule.add_config_value(
                "sectionOne", TEAM_TAG, str(user_data.team_id), TMP_INI_FILE
            )  # type: ignore

            table = Table()
            table.add_column("Authenticated")
            table.add_column("[green]:heavy_check_mark:")

            table.add_row("ZeuZ Server", server_name)
            table.add_row("Username", user_data.username)
            table.add_row("Email", user_data.email)
            table.add_row("Team ID", str(user_data.team_id))
            table.add_row("Project ID", user_data.project_id)

            console.print(table)
        elif status_code == 502:
            print(Fore.YELLOW + "Server offline. Retrying after 60s")
            time.sleep(60)
            return
        else:
            line_color = Fore.RED
            print(line_color + "Incorrect credentials, please try again.")
            # server_name, api = zeuz_authentication_prompts_for_cli()
            # api = api.strip('"')

            # Reset the credentials.
            set_new_credentials(server="", api_key="")
            return
    except ConnectionError:
        print("Failed to connect to the server, retrying after 30s")
        time.sleep(30)
        return

    node_id = CommonUtil.MachineInfo().getLocalUser().lower()
    from Framework.MainDriverApi import retry_failed_report_upload

    # TODO: this needs to be launched separately - outside of this login
    # function because it is not being killed. So everytime we re-log in it
    # creates a new thread and keeps an infinite while loop - which is dangerous
    # for the server, since it'll be bombarded with requests from multiple
    # threads.
    report_thread = threading.Thread(target=retry_failed_report_upload, daemon=True)
    report_thread.start()

    RunProcess(node_id, run_once=run_once, log_dir=log_dir)


def update_machine_info(node_id, should_print=True):
    from tzlocal import get_localzone

    update_machine(
        False,
        should_print,
    )

    local_tz = str(get_localzone())
    RequestFormatter.Get(
        "send_machine_time_zone_api",
        {
            "time_zone": local_tz,
            "machine": node_id,
        },
    )
    RequestFormatter.Get("update_machine_with_time_api", {"machine_name": node_id})


def notify_complete(message="Run completed"):
    title = "ZeuZ Node"
    icon = "zeuz.ico"
    try:
        if sys.platform == "darwin":
            # macOS - Use notifypy
            from notifypy import Notify

            notification = Notify(
                default_notification_title=title,
                default_notification_icon=icon,
            )
            notification.message = message
            # notification.send()
        else:
            # Linux and Windows - Use plyer
            from plyer import notification

            notification.notify(
                title=title,
                message=message,
                app_icon=icon,
                timeout=7,
            )
    except Exception:
        print("Failed to send notification")


def RunProcess(node_id, run_once=False, log_dir=None):
    try:
        # --- START websocket service connections --- #

        def live_log_service_addr():
            server_url = urlparse(
                ConfigModule.get_config_value("Authentication", "server_address")
            )
            if server_url.scheme == "https":
                protocol = "wss"
            else:
                protocol = "ws"
            server_addr = f"{protocol}://{server_url.netloc}"
            return f"{server_addr}/faster/v1/ws/live_log/send/{node_id}"

        def deploy_srv_addr():
            server_url = urlparse(
                ConfigModule.get_config_value("Authentication", "server_address")
            )
            return f"{server_url.scheme}://{server_url.netloc}/zsvc/deploy/v1/next/{node_id}"

        # Connect to the live log service.
        live_log_service.connect(live_log_service_addr())

        # WARNING: For local development only.
        # if "localhost" in host:
        #     deploy_srv_addr = deploy_srv_addr.replace("8000", "8300")

        node_json = None

        from Framework import node_server_state

        def response_callback(response: str):
            node_server_state.STATE.state = "in_progress"
            nonlocal node_json
            nonlocal log_dir
            if log_dir is None:
                log_dir = TMP_INI_FILE.parent
            save_path = Path(log_dir)
            save_path.mkdir(exist_ok=True, parents=True)
            PreProcess(log_dir=log_dir)

            try:
                with open(
                    save_path / "deploy-response.txt", "w", encoding="utf-8"
                ) as f:
                    f.write(response)
            except Exception:
                pass

            # 1. Adapt the proto response to appropriate json format
            node_json = adapter.adapt(response, node_id)

            # 2. Save the json for MainDriver to find
            # Ensure that the parent dirs actually exist before writing to the json file.
            try:
                with open(
                    save_path / f"deploy-tc.zeuz.json", "w", encoding="utf-8"
                ) as f:
                    f.write(json.dumps(node_json))
            except Exception:
                print(Fore.RED + "ERROR failed to save test case json into file")
                print(Fore.YELLOW + "JSON CONTENT:")
                print(node_json)
                import traceback as tb

                tb.print_exc()

            # 3. Call MainDriver
            device_info = All_Device_Info.get_all_connected_device_info()
            MainDriverApi.main(
                device_dict=device_info,
                all_run_id_info=node_json,
            )

        def on_connect_callback(reconnected: bool):
            node_server_state.STATE.state = "idle"
            update_machine_info(node_id, should_print=not reconnected)
            return

        def done_callback() -> bool:
            """
            Returns True if we do not want to connect to the service further.
            """

            if not node_json:
                return False

            print("[deploy] Run complete.")
            if CommonUtil.debug_status:
                notify_complete("Run completed")

            if run_once:
                return True

            return False

        def cancel_callback():
            if not node_json:
                return

            print("[deploy] Run cancelled.")
            if CommonUtil.debug_status:
                notify_complete("Run cancelled")
            CommonUtil.run_cancelled = True

        deploy_handler = long_poll_handler.DeployHandler(
            on_connect_callback=on_connect_callback,
            response_callback=response_callback,
            cancel_callback=cancel_callback,
            done_callback=done_callback,
        )
        deploy_handler.run(deploy_srv_addr())
        return False

    except Exception:
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

    return True


def PreProcess(log_dir=None):
    current_path_file = TMP_INI_FILE
    ConfigModule.clean_config_file(current_path_file)
    ConfigModule.add_section("sectionOne", current_path_file)
    if log_dir is None:
        log_dir = TMP_INI_FILE.parent

    ConfigModule.add_config_value(
        "sectionOne",
        "temp_run_file_path",
        str(log_dir),
        current_path_file,
    )
    print(f"Save temp_run_file_path = '{str(log_dir)}'")
    ConfigModule.add_config_value(
        "sectionOne", "sTestStepExecLogId", "node_cli", TMP_INI_FILE
    )


def update_machine(dependency, should_print=True):
    try:
        console = Console()
        # Get Local Info object
        oLocalInfo = CommonUtil.MachineInfo()

        local_ip = oLocalInfo.getLocalIP()
        testerid = (oLocalInfo.getLocalUser()).lower()

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
            "device": device_dict,
            "allProject": allProject,
        }
        url = RequestFormatter.form_uri("update_automation_machine_api/")
        resp = RequestFormatter.request("post", url, json=update_object)

        if resp.status_code != 200:
            CommonUtil.ExecLog("", "Machine is not registered as online", 4)
            return

        data = resp.json()
        if data["registered"]:
            if should_print:
                rich_print = console.print
                # rich_print(":green_circle: Zeuz Node is online: ", end="")
                rich_print(":green_circle: " + data["name"], style="bold cyan", end="")
                print(" is online\n")
                CommonUtil.ExecLog(
                    "",
                    "Zeuz Node is online: %s" % (data["name"]),
                    4,
                    print_Execlog=False,
                )
        else:
            if data["license"]:
                CommonUtil.ExecLog("", "Machine is not registered as online", 4)
            else:
                if "message" in data:
                    CommonUtil.ExecLog("", data["message"], 4)
                    CommonUtil.ExecLog("", "Machine is not registered as online", 4)
                else:
                    CommonUtil.ExecLog("", "Machine is not registered as online", 4)
        return data
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = f"{str(exc_type).replace('type ', 'Error Type: ')}; Message: {exc_obj}; File: {fname}; Line: {exc_tb.tb_lineno}"
        CommonUtil.ExecLog("", Error_Detail, 4)


def pass_decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc + "========")
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + enc[i] - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


def Local_run(log_dir=None):
    try:
        PreProcess(log_dir=log_dir)
        user_info_object = {}
        user_info_object["project"] = ConfigModule.get_config_value(
            "sectionOne", PROJECT_TAG, TMP_INI_FILE
        )
        user_info_object["team"] = ConfigModule.get_config_value(
            "sectionOne", TEAM_TAG, TMP_INI_FILE
        )
        device_dict = All_Device_Info.get_all_connected_device_info()
        rem_config = {"local_run": True}
        ConfigModule.remote_config = rem_config
        MainDriverApi.main(device_dict)
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


def get_folder_creation_time(folder_path):
    if platform.system() == "Windows":
        creation_time = os.path.getctime(folder_path)
    else:
        stat = os.stat(folder_path)
        if hasattr(stat, "st_birthtime"):
            # Use st_birthtime if available (Mac)
            creation_time = stat.st_birthtime
        else:
            # Use st_mtime (last modification time) as an alternative
            creation_time = stat.st_mtime

    return dt.fromtimestamp(creation_time).date()


def command_line_args() -> Path | None:
    """
    This function handles command line arguments for configuring and running Zeuz Node.

    Returns:
      `log_dir` - Path object for custom log directory if specified, otherwise None

    Example 1 - Basic usage:
    python node_cli.py

    Example 2 - Authentication:
    python node_cli.py -s https://zeuz.zeuz.ai -k YOUR_API_KEY

    Example 3 - Custom node ID:
    python node_cli.py -n custom_node_name

    Example 4 - Run once and exit:
    python node_cli.py -o

    Example 5 - Custom log directory:
    python node_cli.py -d /path/to/logs

    Example 6 - Local run:
    python node_cli.py -r

    Example 7 - Logout:
    python node_cli.py -l

    Example 8 - GitHub integration:
    python node_cli.py -gh YOUR_GITHUB_TOKEN

    Example 9 - Advanced options:
    python node_cli.py -spu -sbl -slg

    Use -h or --help to see full documentation of all available arguments.
    """
    # try:
    parser_object = argparse.ArgumentParser("node_cli parser")
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
        "-m",
        "--max_run_history",
        action="store",
        help="How many latest histories do you want to keep",
        metavar="",
    )
    parser_object.add_argument(
        "-l", "--logout", action="store_true", help="Logout from the server"
    )
    parser_object.add_argument(
        "-r", "--local_run", action="store_true", help="Performs a local run"
    )
    parser_object.add_argument(
        "-o",
        "--once",
        action="store_true",
        help="If specified, this flag tells node to run only one session (test set/deployment) and then quit immediately",
    )
    parser_object.add_argument(
        "-d",
        "--log_dir",
        action="store",
        help="Specify a custom directory for storing Run IDs and logs.",
        metavar="",
    )

    parser_object.add_argument(
        "-gh",
        "--gh_token",
        action="store",
        help="Enter GitHub personal access token (https://github.com/settings/tokens)",
        metavar="",
    )

    parser_object.add_argument(
        "-spu",
        "--stop_pip_auto_update",
        action="store_true",
        help="Auto python modules from auto updating",
    )
    parser_object.add_argument(
        "-sbl",
        "--show_browser_log",
        action="store_true",
        help="Show browserlog in the console",
    )

    parser_object.add_argument(
        "-slg",
        "--stop_live_log",
        action="store_true",
        help="Disables log in live server",
    )

    all_arguments = parser_object.parse_args()

    server = all_arguments.server
    api = all_arguments.api_key
    node_id = all_arguments.node_id
    max_run_history = all_arguments.max_run_history
    logout = all_arguments.logout
    gh_token = all_arguments.gh_token
    stop_pip_auto_update = all_arguments.stop_pip_auto_update
    show_browser_log = all_arguments.show_browser_log
    stop_live_log = all_arguments.stop_live_log

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
        raise Exception(
            f"ERR: Zeuz Node does not have enough permissions to write to the specified log directory: {log_dir}"
        )
    except Exception:
        raise Exception(
            f"ERR: Invalid custom log directory, or failed to create directory: {log_dir}"
        )

    global local_run
    local_run = all_arguments.local_run

    global RUN_ONCE
    RUN_ONCE = all_arguments.once

    settings_conf_path = (
        os.path.dirname(os.path.abspath(__file__)).replace(
            os.sep + "Framework", os.sep + ""
        )
        + os.sep
        + "Framework"
        + os.sep
        + "settings.conf"
    )
    config = ConfigObj(settings_conf_path)
    date_str = config.get("Advanced Options", {}).get("last_module_update_date", "")
    module_update_interval = config.get("Advanced Options", {}).get(
        "module_update_interval", ""
    )
    if date_str:
        # Parse the date from the configuration file
        config_date = date.fromisoformat(date_str)
        current_date = datetime.date.today()
        time_difference = (current_date - config_date).days
        CommonUtil.ai_module_update_flag = stop_pip_auto_update
        CommonUtil.ai_module_update_time_difference = time_difference
        # Check if the time difference is greater than one month
        if (
            not stop_pip_auto_update
            and CommonUtil.ws_ss_log
            and time_difference > int(module_update_interval)
        ):
            update_outdated_modules()
            config_date = date.today()
            config.setdefault("Advanced Options", {})["last_module_update_date"] = str(
                config_date
            )
            config.write()
            # print("module_updater: Module Updated..")
        else:
            # TODO: remove these print statements
            # print("module_updater: All modules are already up to date.")
            pass
    else:
        # Assign the current date
        config_date = date.today()
        config.setdefault("Advanced Options", {})["last_module_update_date"] = str(
            config_date
        )
        # Save the updated configuration file
        config.write()
        if not stop_pip_auto_update and CommonUtil.ws_ss_log:
            update_outdated_modules()
        print("module_updater: Module Updated..")

    # Delete Old Subfolders in Automationlog folder.

    def get_subfolders_created_before_n_days(folder_path, log_delete_interval):
        subfolder_paths = []
        current_time = time.time()
        interval_days_in_sec = int(log_delete_interval) * 24 * 60 * 60

        for dir_name in os.listdir(folder_path):
            dir_path = os.path.join(folder_path, dir_name)
            if os.path.isdir(dir_path):
                created_time = os.path.getctime(dir_path)

                if current_time - created_time > interval_days_in_sec:
                    subfolder_paths.append(dir_path)

        return subfolder_paths

    folder_path = (
        os.path.dirname(os.path.abspath(__file__)).replace(
            os.sep + "Framework", os.sep + ""
        )
        + os.sep
        + "AutomationLog"
    )
    log_delete_interval = ConfigModule.get_config_value(
        "Advanced Options", "log_delete_interval"
    )

    # By default set the automation log delete interval to 7 days
    if not isinstance(log_delete_interval, int):
        log_delete_interval = 7
    else:
        if log_delete_interval <= 0:
            log_delete_interval = 7

    def delete_old_automationlog_folders():
        while True:
            auto_log_subfolders = get_subfolders_created_before_n_days(
                folder_path, int(log_delete_interval)
            )
            auto_log_subfolders = [
                subfolder
                for subfolder in auto_log_subfolders
                if subfolder
                not in [
                    "attachments",
                    "attachments_db",
                    "outdated_modules.json",
                    "temp_config.ini",
                    "failed_reports",
                ]
            ]

            for subfolder in auto_log_subfolders:
                shutil.rmtree(subfolder)
            if auto_log_subfolders:
                print(
                    f"automation_log_cleanup: deleted {len(auto_log_subfolders)} that are older than {log_delete_interval} days"
                )

            # Check every 5 hours for old automation logs
            time.sleep(60 * 60 * 5)

    # Create a background thread for deleting automation log
    thread = threading.Thread(target=delete_old_automationlog_folders, daemon=True)
    thread.start()

    if show_browser_log:
        CommonUtil.show_browser_log = True

    if server and server[-1] == "/":
        server = server[:-1]

    if server or logout or api:
        # destroy_session()
        if api and server:
            set_new_credentials(server=server, api_key=api)
        elif logout:
            ConfigModule.remove_config_value(AUTHENTICATION_TAG, "server_address")
            set_new_credentials(server="", api_key="")
            # zeuz_authentication_prompts_for_cli()
        else:
            CommonUtil.ExecLog(
                "AUTHENTICATION FAILED",
                "Enter the command line arguments in correct format. Type -h for help.",
                3,
            )
            sys.exit()  # exit and let the user try again from command line
    if node_id:
        CommonUtil.MachineInfo().setLocalUser(node_id)
    if max_run_history:
        # TODO: implement max run history feature which will ensure that we do
        # not have more than X number of run IDs.
        pass
    if gh_token:
        os.environ["GH_TOKEN"] = gh_token

    ConfigModule.add_config_value(
        "Advanced Options", "stop_live_log", str(stop_live_log)
    )

    """argparse module automatically shows exceptions of corresponding wrong arguments
     and executes sys.exit(). So we don't need to use try except"""
    # except:
    #     CommonUtil.ExecLog("\ncommand_line_args : node_cli.py","Did not parse anything from given arguments",4)
    #     sys.exit()

    return log_dir


def set_new_credentials(server, api_key):
    """Store new credentials in the settings file."""
    ConfigModule.remove_config_value(AUTHENTICATION_TAG, "api-key")
    ConfigModule.add_config_value(AUTHENTICATION_TAG, "api-key", api_key)
    ConfigModule.remove_config_value(AUTHENTICATION_TAG, "server_address")
    ConfigModule.add_config_value(AUTHENTICATION_TAG, "server_address", server)


def Bypass():
    while True:
        oLocalInfo = CommonUtil.MachineInfo()
        testerid = (oLocalInfo.getLocalUser()).lower()
        print("[Bypass] Zeuz Node is online: %s" % testerid)
        RunProcess(testerid)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    print("Press Ctrl-C or Ctrl-Break to disconnect and quit.")

    console = Console()

    try:
        log_dir = command_line_args()
    except Exception as e:
        from colorama import Fore

        print(Fore.RED + str(e))
        print("Exiting...")
        os._exit(1)

    if local_run:
        Local_run(log_dir=log_dir)
    else:
        # Bypass()

        print_login_information = True
        while True:
            if STATE.reconnect_with_credentials is not None:
                destroy_session()
                server_name = STATE.reconnect_with_credentials.server
                api_key = STATE.reconnect_with_credentials.api_key
                set_new_credentials(server=server_name, api_key=api_key)

                STATE.reconnect_with_credentials = None

            server_name = (
                ConfigModule.get_config_value(AUTHENTICATION_TAG, "server_address")
                .strip('""')
                .strip()
            )
            api = (
                ConfigModule.get_config_value(AUTHENTICATION_TAG, "api-key")
                .strip('"')
                .strip()
            )

            if len(server_name) == 0 and len(api) == 0:
                if print_login_information:
                    console.print(
                        "\n" + ":red_circle: " + "Zeuz Node is disconnected.",
                        style="bold red",
                    )
                    console.print("Please log in to ZeuZ server and connect.")

                    print_login_information = False
                # If server_name and api are not set, then wait for the user to
                # connect via the ZeuZ server.
                time.sleep(1)
                continue

            Login(
                server_name=server_name,
                run_once=RUN_ONCE,
                log_dir=log_dir,
            )

            if RUN_ONCE:
                console.print(
                    ":yellow_circle: "
                    + "Zeuz Node is going offline after running one session, since `--once` or `-o` flag is specified.",
                    style="bold cyan",
                )
                os._exit(0)

            print_login_information = True
            time.sleep(1)
