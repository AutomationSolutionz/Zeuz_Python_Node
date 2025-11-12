import asyncio
import subprocess
import sys
import httpx
from subprocess import CalledProcessError
from Framework.Utilities import RequestFormatter, ConfigModule, CommonUtil

debug = False

def read_node_id():
    return CommonUtil.MachineInfo().getLocalUser().lower()


async def send_response(data=None) -> None:
    try:
        api_key = ConfigModule.get_config_value("Authentication", "api-key")
        url = RequestFormatter.form_uri("d/nodes/install/server/push")
        payload = {
            "node_id": read_node_id(),
            "data": data
        }
        if debug: 
            print(f"[installer] Sending response to server: {payload}")
        
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            resp = await client.post(url, json=payload, headers={"X-API-KEY": api_key})
            if debug: 
                print(f"[installer] Response status: {resp.status_code}")
                print(f"[installer] Response content: {resp.content}")
            if not resp.is_success:
                if debug: 
                    print(f"[installer] Failed to send response: {resp.status_code}")
    except Exception as e:
        print(f"[installer] Error sending response: {e}")


async def check_package_available(module_name):
    """
    Check if a module is available for import

    Args:
        module_name (str): The name used to import the package

    Returns:
        bool: True if package is available, False otherwise
    """

    try:
        __import__(module_name)
        return True
    except ImportError:
        return False



async def install_package(package_name) -> bool:
    """
    Install a package using uv

    Args:
        package_name (str): The name of the package to install

    Returns:
        bool: True if installation successful, False otherwise
    """

    # Define the command as a list of arguments
    cmd = [sys.executable, "-m", "uv", "add", package_name]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait for the process to complete and capture output
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise CalledProcessError(
                process.returncode,
                cmd,
                output=stdout,
                stderr=stderr
            )

        print(f"[installer] Successfully installed {package_name} using uv.")
        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        return True

    except CalledProcessError as e:
        print(f"[installer] Failed to install {package_name}: {e}")
        if e.stderr:
            print(f"[stderr]\n{e.stderr.decode()}")
        return False
    except FileNotFoundError:
        print("[installer] Error: 'uv' command not found or Python interpreter path is incorrect.")
        return False
