#!/usr/bin/env python3
import os
import socket
import sys
import shutil
import subprocess
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
import asyncio

import psutil
import requests
from dotenv import load_dotenv
from colorama import init as colorama_init
from colorama import Fore
from rich.table import Table
from rich.console import Console
from rich import traceback as rich_traceback
import traceback
from urllib3.exceptions import InsecureRequestWarning
import uvicorn
from Framework.Built_In_Automation.Web.Selenium.utils import ChromeExtensionDownloader
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from settings import ZEUZ_NODE_PRIVATE_RSA_KEYS_DIR
from Framework.install_handler.long_poll_handler import InstallHandler
from server.mobile import upload_android_ui_dump


def adjust_python_path():
    """Adjusts the Python path to include the Framework directory."""
    root_dir = Path(__file__).parent
    framework_dir = root_dir / "Framework"

    # Append correct paths so that it can find the configuration files and other modules
    sys.path.append(str(framework_dir))

    # Move to Framework directory and add parent to path for module imports
    os.chdir(framework_dir)


from Framework.module_installer import (  # noqa: E402
    check_min_python_version,
    install_missing_modules,
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


async def start_server():
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) == 0

    try:
        node_server_port = 18100
        tries = 0
        while is_port_in_use(node_server_port) and tries < 99:
            node_server_port += 1
            tries += 1
        ConfigModule.add_config_value("server", "port", str(node_server_port))
        print(f"Launching node-server on port {node_server_port}")

        app = node_server.main()
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=node_server_port,
            log_level="warning",
        )
        server = uvicorn.Server(config)
        await server.serve()

    except Exception as e:
        traceback.print_exc()
        print(f"[WARN] Failed to launch node-server: {str(e)}")


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


def setup_nodejs_appium():
    """Setup Node.js and Appium if not already installed."""
    try:
        import nodejs_appium_installer

        nodejs_appium_installer.setup_nodejs_appium()
    except Exception as e:
        print(f"Warning: Failed to setup Node.js and Appium: {e}")
        print("Continuing without Node.js/Appium setup...")


# Tells node whether it should run a test set/deployment only once and quit.

from Framework.Utilities import (  # noqa: E402
    RequestFormatter,
    CommonUtil,
    All_Device_Info,
)
from Framework import MainDriverApi  # noqa: E402


TMP_INI_FILE = None

"""Constants"""
AUTHENTICATION_TAG = "Authentication"
PROJECT_TAG = "project"
TEAM_TAG = "team"
device_dict: dict[str, Any] = {}


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


async def destroy_session():
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


async def Login(
    server_name: str,
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
            await asyncio.sleep(60)
            return
        else:
            line_color = Fore.RED
            print(line_color + "Incorrect credentials, please try again.")
            # server_name, api = zeuz_authentication_prompts_for_cli()
            # api = api.strip('"')

            # Reset the credentials.
            await set_new_credentials(server="", api_key="")
            return
    except ConnectionError:
        print("Failed to connect to the server, retrying after 30s")
        await asyncio.sleep(30)
        return
    except Exception as e:
        traceback.print_exc()
        return

    node_id = CommonUtil.MachineInfo().getLocalUser().lower()
    from Framework.MainDriverApi import retry_failed_report_upload

    # TODO: this needs to be launched separately - outside of this login
    # function because it is not being killed. So everytime we re-log in it
    # creates a new thread and keeps an infinite while loop - which is dangerous
    # for the server, since it'll be bombarded with requests from multiple
    # threads.

    # Todo: Make it async and not in thread. Fix the while loop inside as well
    # Its returning on first iteration. This should be out of Login function
    # report_thread = threading.Thread(target=retry_failed_report_upload, daemon=True)
    # report_thread.start()

    await RunProcess(node_id, log_dir=log_dir)


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
            # from notifypy import Notify

            # notification = Notify(
            #     default_notification_title=title,
            #     default_notification_icon=icon,
            # )
            # notification.message = message
            # notification.send()
            pass
        elif sys.platform == "win32":
            # Linux and Windows - Use plyer
            from plyer import notification

            notification.notify(
                title=title,
                message=message,
                app_icon=icon,
                timeout=7,
            )
        elif sys.platform == "linux":
            pass
    except Exception:
        print("Failed to send notification")


async def RunProcess(node_id, log_dir=None):
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

        install_handler = InstallHandler()
        install_task = asyncio.create_task(install_handler.run())

        async def response_callback(response: str):
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
                traceback.print_exc()

            # 3. Call MainDriver
            device_info = All_Device_Info.get_all_connected_device_info()
            await install_handler.cancel_run()
            MainDriverApi.main(
                device_dict=device_info,
                all_run_id_info=node_json,
            )

        async def on_connect_callback(reconnected: bool):
            node_server_state.STATE.state = "idle"
            update_machine_info(node_id, should_print=not reconnected)
            return

        async def done_callback() -> bool:
            """
            Returns True if we do not want to connect to the service further.
            """

            if not node_json:
                return False

            print("[deploy] Run complete.")
            notify_complete("Run completed")
            asyncio.create_task(install_handler.run())

            return False

        async def cancel_callback():
            if not node_json:
                return

            print("[deploy] Run cancelled.")
            notify_complete("Run cancelled")
            CommonUtil.run_cancelled = True
            asyncio.create_task(install_handler.run())

        deploy_handler = long_poll_handler.DeployHandler(
            on_connect_callback=on_connect_callback,
            response_callback=response_callback,
            cancel_callback=cancel_callback,
            done_callback=done_callback,
        )

        deploy_task = asyncio.create_task(deploy_handler.run(deploy_srv_addr()))

        await asyncio.gather(install_task, deploy_task, return_exceptions=True)

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


def generate_rsa_key():
    """Generate a new RSA private key and save it to the rsa_private_keys folder."""
    console = Console()

    from Framework.Utilities.RSAKeyUtil import (
        save_private_key as save_key_util,
        get_public_key_pem,
    )

    key_folder = ZEUZ_NODE_PRIVATE_RSA_KEYS_DIR

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
    key_filename = f"private_key_{timestamp}.pem"

    success, _, saved_path = save_key_util(
        private_key=private_key,
        key_folder=key_folder,
        filename=key_filename,
        format_type="pkcs8",
        check_duplicate=False,  # New keys shouldn't have duplicates
    )

    if not success:
        console.print(f"[red]Error:[/red] Failed to save generated private key.")
        return

    # Generate public key
    public_key_pem = get_public_key_pem(private_key)

    console.print(f"\n[green]✓[/green] RSA private key generated successfully!")
    console.print(f"[cyan]Location:[/cyan] {saved_path}")
    console.print(f"\n[cyan]Public Key:[/cyan]")
    console.print(public_key_pem)


def add_existing_rsa_key(key_content: str):
    """Copy an existing RSA private key to the rsa_private_keys folder."""
    console = Console()

    from Framework.Utilities.RSAKeyUtil import (
        load_private_key_from_pem,
        save_private_key as save_key_util,
        get_public_key_pem,
        check_duplicate_key,
    )

    key_folder = ZEUZ_NODE_PRIVATE_RSA_KEYS_DIR

    private_key = load_private_key_from_pem(key_content)
    if private_key is None:
        console.print(f"[red]Error:[/red] Invalid PEM private key.")
        return False

    # Check for duplicates
    duplicate = check_duplicate_key(private_key, key_folder)
    if duplicate:
        console.print(
            f"[yellow]Warning:[/yellow] This private key already exists as {duplicate}. Not adding duplicate."
        )
        return False

    # Copy the key with a timestamp
    timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"imported_key_{timestamp}.pem"

    success, _, saved_path = save_key_util(
        private_key=private_key,
        key_folder=key_folder,
        filename=new_filename,
        format_type="pkcs8",
        check_duplicate=False,  # Already checked above
    )

    if not success:
        console.print(f"[red]Error:[/red] Failed to save private key.")
        return False

    console.print(f"\n[green]✓[/green] Private key imported successfully!")
    console.print(f"[cyan]To:[/cyan] {saved_path}")

    # Show the public key
    public_key_pem = get_public_key_pem(private_key)
    console.print(f"\n[cyan]Public Key:[/cyan]")
    console.print(public_key_pem)

    return True


def show_existing_rsa_keys():
    """List all existing RSA private keys and show their public keys."""
    console = Console()

    from Framework.Utilities.RSAKeyUtil import list_existing_keys

    key_folder = ZEUZ_NODE_PRIVATE_RSA_KEYS_DIR

    keys_info = list_existing_keys(key_folder)

    if not keys_info:
        console.print(f"\n[yellow]No private keys found in:[/yellow] {key_folder}")
        console.print("[cyan]Use -gpk to generate a new key[/cyan]\n")
        return

    console.print(
        f"\n[cyan]Found {len(keys_info)} private key(s) in:[/cyan] {key_folder}\n"
    )

    for idx, key_info in enumerate(keys_info, 1):
        console.print(f"[green]Key #{idx}:[/green] {key_info['filename']}")
        console.print(f"[cyan]Path:[/cyan] {key_info['path']}")
        if "error" in key_info:
            console.print(f"[red]Error:[/red] {key_info['error']}\n")
        else:
            console.print(f"[cyan]Public Key:[/cyan]")
            console.print(key_info["public_key"])


def share_private_keys():
    """Share all RSA private keys by encrypting and uploading to server."""
    console = Console()

    try:
        from Framework.Utilities import ShareKeysUtil
        from Framework.Utilities import RequestFormatter, ConfigModule

        key_folder = ZEUZ_NODE_PRIVATE_RSA_KEYS_DIR

        # Collect all private keys
        keys = ShareKeysUtil.collect_private_keys(key_folder)

        if not keys:
            console.print(f"\n[red]✗[/red] No private keys found in: {key_folder}")
            console.print("[cyan]Use -gpk to generate a new key first[/cyan]\n")
            return False

        console.print(f"\n[cyan]Found {len(keys)} private key(s) to share[/cyan]")

        # Generate share code
        share_code = ShareKeysUtil.generate_share_code()

        # Encrypt all keys
        console.print("[cyan]Encrypting keys...[/cyan]")
        keys_json = json.dumps(keys)
        encrypted_data = ShareKeysUtil.encrypt_data(keys_json, share_code)

        # Send to server
        console.print("[cyan]Uploading to server...[/cyan]")

        payload = {"code": share_code, "encrypted_data": encrypted_data}

        console.print(f"[dim]Endpoint: /zsvc/deploy/v1/share-keys[/dim]")
        response = RequestFormatter.Post("zsvc/deploy/v1/share-keys", payload)

        if response and response.get("success"):
            console.print(f"\n[green]✓[/green] Keys shared successfully!")
            console.print(f"\n[yellow]═══════════════════════════════════[/yellow]")
            console.print(f"[yellow]  Share Code: [bold]{share_code}[/bold][/yellow]")
            console.print(f"[yellow]═══════════════════════════════════[/yellow]")
            console.print(f"\n[cyan]This code will expire in 30 minutes.[/cyan]")
            console.print(
                f"[cyan]Use this code with -fe option to fetch keys on another machine.[/cyan]\n"
            )
            console.print(f"[dim]Example: uv run node_cli.py -fe {share_code}[/dim]\n")
            return True
        else:
            error_msg = (
                response.get("message", "Unknown error")
                if response
                else "No response from server"
            )
            console.print(f"\n[red]✗[/red] Failed to share keys: {error_msg}\n")
            return False

    except Exception as e:
        import traceback as tb

        console.print(f"\n[red]✗[/red] Error sharing keys: {str(e)}\n")
        tb.print_exc()
        return False


def install_linux_inspector_deps():
    """Install Linux inspector dependencies by running setup script."""
    console = Console()

    script_path = Path(__file__).parent / "Installer" / "setup_linux_inspector.sh"

    if not script_path.exists():
        console.print(f"\n[red]✗[/red] Setup script not found at: {script_path}\n")
        return False

    console.print(f"\n[cyan]Installing Linux inspector dependencies...\n[/cyan]")
    console.print(f"[dim]Running: {script_path}[/dim]\n")

    try:
        result = subprocess.run(
            ["bash", str(script_path)], capture_output=False, text=True, check=False
        )

        if result.returncode == 0:
            console.print(
                f"\n[green]✓[/green] Linux inspector dependencies installed successfully!\n"
            )
            return True
        else:
            console.print(
                f"\n[red]✗[/red] Installation failed with exit code: {result.returncode}\n"
            )
            return False

    except Exception as e:
        console.print(f"\n[red]✗[/red] Error running installation script: {str(e)}\n")
        return False


def list_available_apps():
    """List all available applications for UI inspection."""
    console = Console()

    console.print("\n[cyan]Scanning for available applications...[/cyan]\n")

    try:
        # Import the Linux BuiltInFunctions module
        sys.path.insert(
            0,
            str(
                Path(__file__).parent
                / "Framework"
                / "Built_In_Automation"
                / "Desktop"
                / "Linux"
            ),
        )
        try:
            import pyatspi
        except ImportError:
            install_missing_modules(["python3-pyatspi==1.19.0", "pygobject==3.50.1"])
            try:
                import pyatspi
            except ImportError:
                sys.stderr.write(
                    "Error: system dependency is not installed. Install them by running Installer/setup_linux_inspector.sh.\n"
                )
                sys.exit(1)

        desktop = pyatspi.Registry.getDesktop(0)
        apps = []

        for app in desktop:
            if app and app.name:
                apps.append(app.name)

        if apps:
            console.print(f"[green]✓[/green] Found {len(apps)} application(s):\n")
            for idx, app_name in enumerate(apps, 1):
                console.print(f"  {idx}. {app_name}")
            console.print()
            return True
        else:
            console.print("[yellow]No applications found[/yellow]\n")
            return False

    except Exception as e:
        console.print(f"\n[red]✗[/red] Error listing applications: {str(e)}\n")
        import traceback as tb

        tb.print_exc()
        return False


def generate_ui_dump(app_keyword: str):
    """Generate UI dump for a specific application."""
    console = Console()

    console.print(
        f"\n[cyan]Generating UI dump for application: '{app_keyword}'[/cyan]\n"
    )

    try:
        # Import the Linux BuiltInFunctions module
        sys.path.insert(
            0,
            str(
                Path(__file__).parent
                / "Framework"
                / "Built_In_Automation"
                / "Desktop"
                / "Linux"
            ),
        )
        from BuiltInFunctions import get_ui_tree

        ui_tree = get_ui_tree(app_keyword)

        if ui_tree:
            # Save to file
            timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
            output_file = (
                Path(__file__).parent
                / "AutomationLog"
                / f"ui_dump_{app_keyword}_{timestamp}.xml"
            )
            output_file.parent.mkdir(exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(ui_tree)

            console.print(f"[green]✓[/green] UI dump generated successfully!")
            console.print(f"[cyan]Location:[/cyan] {output_file}\n")

            # Also print to console
            console.print("[cyan]UI Tree:[/cyan]")
            print(ui_tree)

            return True
        else:
            console.print(
                f"\n[red]✗[/red] Failed to generate UI dump. Application '{app_keyword}' not found or no UI tree available.\n"
            )
            return False

    except Exception as e:
        console.print(f"\n[red]✗[/red] Error generating UI dump: {str(e)}\n")
        import traceback as tb

        tb.print_exc()
        return False


def fetch_private_keys(share_code: str):
    """Fetch and decrypt shared RSA private keys from server."""
    console = Console()

    from Framework.Utilities import ShareKeysUtil
    from Framework.Utilities import RequestFormatter

    # Validate code format
    if len(share_code) != 9 or share_code[4] != "-":
        console.print(
            f"\n[red]✗[/red] Invalid share code format. Expected format: AkEf-B910 (9 characters with dash)\n"
        )
        return False

    console.print(f"\n[cyan]Fetching keys from server...[/cyan]")

    try:
        # Fetch from server
        response = RequestFormatter.Get(f"zsvc/deploy/v1/fetch-keys/{share_code}")

        if not response or not response.get("success"):
            error_msg = (
                response.get("message", "Keys not found or expired")
                if response
                else "No response from server"
            )
            console.print(f"\n[red]✗[/red] Failed to fetch keys: {error_msg}\n")
            return False

        encrypted_data = response.get("encrypted_data")
        if not encrypted_data:
            console.print(f"\n[red]✗[/red] No encrypted data received from server\n")
            return False

        # Decrypt data
        console.print("[cyan]Decrypting keys...[/cyan]")
        decrypted_json = ShareKeysUtil.decrypt_data(encrypted_data, share_code)

        if not decrypted_json:
            console.print(
                f"\n[red]✗[/red] Failed to decrypt keys. Invalid share code or corrupted data.\n"
            )
            return False

        keys = json.loads(decrypted_json)

        # Save keys
        console.print(f"[cyan]Saving {len(keys)} key(s)...[/cyan]")
        key_folder = ZEUZ_NODE_PRIVATE_RSA_KEYS_DIR
        success_count, skipped_count, failed_count = ShareKeysUtil.save_private_keys(
            keys, key_folder
        )

        console.print(f"\n[green]✓[/green] Keys fetched successfully!")
        console.print(f"[cyan]Saved:[/cyan] {success_count} key(s)")
        if skipped_count > 0:
            console.print(
                f"[yellow]Skipped:[/yellow] {skipped_count} key(s) (duplicates)"
            )
        if failed_count > 0:
            console.print(f"[red]Failed:[/red] {failed_count} key(s)")
        console.print(f"[cyan]Location:[/cyan] {key_folder}\n")

        return True

    except json.JSONDecodeError as e:
        console.print(f"\n[red]✗[/red] Error parsing decrypted data: {str(e)}\n")
        return False
    except Exception as e:
        console.print(f"\n[red]✗[/red] Error fetching keys: {str(e)}\n")
        return False


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


async def delete_old_automationlog_folders():
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
        await asyncio.sleep(60 * 60 * 5)


async def command_line_args() -> Path | None:
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


    Example 7 - Logout:
    python node_cli.py -l

    Example 8 - GitHub integration:
    python node_cli.py -gh YOUR_GITHUB_TOKEN

    Example 9 - Advanced options:
    python node_cli.py -spu -sbl -slg

    Example 10 - Generate RSA private key:
    python node_cli.py -gpk

    Example 11 - Add existing RSA private key:
    python node_cli.py -apk /path/to/private_key.pem

    Example 12 - Show existing RSA keys and their public keys:
    python node_cli.py -spk

    Example 13 - Share all RSA private keys (generates a share code):
    python node_cli.py -sh

    Example 14 - Fetch shared RSA private keys using a share code:
    python node_cli.py -fe AkEf-B910

    Example 15 - Install Linux desktop automation dependencies:
    python node_cli.py -ild

    Example 16 - List all available applications:
    python node_cli.py -lsa

    Example 17 - Generate UI dump for an application:
    python node_cli.py -dui firefox

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

    # modification here to add parsers to change chrome download settings
    parser_object.add_argument(
        "-cf",
        "--chrome-fetch",
        type=int,
        action="store",
        help="Days before fetching new Chrome version (default: 15)",
        metavar="",
    )
    parser_object.add_argument(
        "-cc",
        "--chrome-cleanup",
        type=int,
        action="store",
        help="Days before cleaning up old Chrome versions (default: 50)",
        metavar="",
    )

    # RSA key management arguments
    parser_object.add_argument(
        "-gpk",
        "--generate-private-key",
        action="store_true",
        help="Generate a new RSA private key for encrypting secrets",
    )
    parser_object.add_argument(
        "-apk",
        "--add-private-key",
        action="store",
        help="Add an existing RSA private key (provide content of the .pem file)",
        metavar="",
    )
    parser_object.add_argument(
        "-spk",
        "--show-private-keys",
        action="store_true",
        help="Show all existing RSA private keys and their public keys",
    )

    # Share and fetch keys arguments
    parser_object.add_argument(
        "-sh",
        "--share",
        action="store_true",
        help="Share all RSA private keys - generates a single code for encryption and retrieval",
    )
    parser_object.add_argument(
        "-fe",
        "--fetch",
        action="store",
        help="Fetch shared RSA private keys using the share code (format: AkEf-B910)",
        metavar="",
    )

    # Desktop automation setup and UI inspection arguments
    parser_object.add_argument(
        "-ild",
        "--install-linux-deps",
        action="store_true",
        help="Install Linux desktop automation dependencies (runs Installer/setup_linux_inspector.sh)",
    )
    parser_object.add_argument(
        "-lsa",
        "--list-apps",
        action="store_true",
        help="List all available applications for UI inspection",
    )
    parser_object.add_argument(
        "-dui",
        "--dump-ui",
        action="store",
        help="Generate UI dump for a specific application (provide app name or keyword)",
        metavar="",
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

    # RSA key management options
    generate_key = all_arguments.generate_private_key
    add_key = all_arguments.add_private_key
    show_keys = all_arguments.show_private_keys

    # get the chrome extension download settings
    chrome_fetch = all_arguments.chrome_fetch
    chrome_cleanup = all_arguments.chrome_cleanup

    # Share and fetch keys options
    share_keys = all_arguments.share
    fetch_code = all_arguments.fetch

    # Desktop automation and UI inspection options
    install_linux_deps = all_arguments.install_linux_deps
    list_apps = all_arguments.list_apps
    dump_ui = all_arguments.dump_ui

    # Handle RSA key management commands
    if generate_key:
        generate_rsa_key()
        sys.exit(0)

    if add_key:
        if add_existing_rsa_key(add_key):
            sys.exit(0)
        else:
            sys.exit(1)

    if show_keys:
        show_existing_rsa_keys()
        sys.exit(0)

    # Handle share/fetch commands
    if share_keys:
        share_private_keys()
        sys.exit(0)

    if fetch_code:
        if fetch_private_keys(fetch_code):
            sys.exit(0)
        else:
            sys.exit(1)

    # Handle Linux desktop automation dependency installation
    if install_linux_deps:
        install_linux_inspector_deps()
        sys.exit(0)

    # Handle listing available apps
    if list_apps:
        list_available_apps()
        sys.exit(0)

    # Handle UI dump generation
    if dump_ui:
        generate_ui_dump(dump_ui)
        sys.exit(0)

    # Update chrome extension download settings if specified
    if chrome_fetch is not None:
        os.environ["CHROME_DAYS_BEFORE_FETCH"] = str(chrome_fetch)

        print(f"Set days_before_fetch to {os.environ.get('CHROME_DAYS_BEFORE_FETCH')}")

    if chrome_cleanup is not None:
        os.environ["CHROME_DAYS_BEFORE_CLEANUP"] = str(chrome_cleanup)

        print(
            f"Set days_before_cleanup to {os.environ.get('CHROME_DAYS_BEFORE_CLEANUP')}"
        )

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

    if show_browser_log:
        CommonUtil.show_browser_log = True

    if server and server[-1] == "/":
        server = server[:-1]

    if server or logout or api:
        # destroy_session()
        if api and server:
            await set_new_credentials(server=server, api_key=api)
        elif logout:
            ConfigModule.remove_config_value(AUTHENTICATION_TAG, "server_address")
            await set_new_credentials(server="", api_key="")
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


async def set_new_credentials(server, api_key):
    """Store new credentials in the settings file."""
    ConfigModule.remove_config_value(AUTHENTICATION_TAG, "api-key")
    ConfigModule.add_config_value(AUTHENTICATION_TAG, "api-key", api_key)
    ConfigModule.remove_config_value(AUTHENTICATION_TAG, "server_address")
    ConfigModule.add_config_value(AUTHENTICATION_TAG, "server_address", server)


def print_system_info_version():
    """Prints the system information and version of the Node"""
    print(
        f"Python {platform.python_version()} ({platform.architecture()[0]}) @ {sys.executable}"
    )
    print(f"Current file path: {os.path.abspath(__file__)}")


def create_temp_ini_automation_log():
    global TMP_INI_FILE

    root_dir = Path(__file__).parent
    automation_log_dir = root_dir / "AutomationLog"
    automation_log_dir.mkdir(exist_ok=True)
    print(f"Created AutomationLog directory at {automation_log_dir}")

    TMP_INI_FILE = automation_log_dir / ConfigModule.get_config_value(
        "Advanced Options", "_file"
    )


async def main():
    print_system_info_version()
    load_dotenv()
    adjust_python_path()
    ConfigModule.remove_settings_lock_file()
    ConfigModule.create_settings_config_file()
    create_temp_ini_automation_log()

    extension_downloader = ChromeExtensionDownloader()
    extension_downloader.cleanup_extensions()

    rich_traceback.install(show_locals=True, max_frames=1)

    # Suppress the InsecureRequestWarning since we use verify=False parameter.
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)  # type: ignore

    # Disable WebdriverManager SSL verification.
    os.environ["WDM_SSL_VERIFY"] = "0"

    colorama_init(autoreset=True)

    kill_old_process(Path.cwd().parent / "pid.txt")
    check_min_python_version(min_python_version="3.11", show_warning=True)

    # Setup Node.js and Appium before other operations
    setup_nodejs_appium()

    update_outdated_modules()
    asyncio.create_task(start_server())
    asyncio.create_task(upload_android_ui_dump())
    asyncio.create_task(delete_old_automationlog_folders())
    await destroy_session()

    signal.signal(signal.SIGINT, signal_handler)
    print("Press Ctrl-C or Ctrl-Break to disconnect and quit.")

    console = Console()

    try:
        log_dir = await command_line_args()
    except Exception as e:
        print(Fore.RED + str(e))
        print("Exiting...")
        os._exit(1)

    server_name = (
        ConfigModule.get_config_value(AUTHENTICATION_TAG, "server_address")
        .strip('"')
        .strip()
    )
    api = (
        ConfigModule.get_config_value(AUTHENTICATION_TAG, "api-key").strip('"').strip()
    )

    if len(server_name) == 0 and len(api) == 0:
        console.print(
            "\n" + ":red_circle: " + "Zeuz Node is disconnected.",
            style="bold red",
        )
        console.print("Please log in to ZeuZ server and connect.")
        await asyncio.sleep(1)

    else:
        asyncio.create_task(
            Login(
                server_name=server_name,
                log_dir=log_dir,
            )
        )
    while True:
        if STATE.reconnect_with_credentials is not None:
            await destroy_session()
            server_name = STATE.reconnect_with_credentials.server
            api_key = STATE.reconnect_with_credentials.api_key
            await set_new_credentials(server=server_name, api_key=api_key)

            STATE.reconnect_with_credentials = None
            server_name = (
                ConfigModule.get_config_value(AUTHENTICATION_TAG, "server_address")
                .strip('"')
                .strip()
            )
            api = (
                ConfigModule.get_config_value(AUTHENTICATION_TAG, "api-key")
                .strip('"')
                .strip()
            )

            if len(server_name) == 0 and len(api) == 0:
                console.print(
                    "\n" + ":red_circle: " + "Zeuz Node is disconnected.",
                    style="bold red",
                )
                console.print("Please log in to ZeuZ server and connect.")

            asyncio.create_task(
                Login(
                    server_name=server_name,
                    log_dir=log_dir,
                )
            )
        await asyncio.sleep(1)


def handle_inspection_commands():
    """Handle inspection commands that should not kill existing node processes."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-lsa", "--list-apps", action="store_true")
    parser.add_argument("-dui", "--dump-ui", action="store")

    # Parse only known args to avoid errors from other arguments
    args, _ = parser.parse_known_args()

    if args.list_apps:
        list_available_apps()
        sys.exit(0)

    if args.dump_ui:
        generate_ui_dump(args.dump_ui)
        sys.exit(0)


# Handle inspection commands before starting main process
handle_inspection_commands()

asyncio.run(main())
