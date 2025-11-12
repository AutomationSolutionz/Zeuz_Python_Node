import asyncio
import subprocess
import sys
import httpx
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


async def check_package_available(package_import_name):
    """
    Check if a package is available for import

    Args:
        package_import_name (str): The name used to import the package

    Returns:
        bool: True if package is available, False otherwise
    """
    try:
        # Run the import check in a separate process to avoid blocking
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-c", f"import {package_import_name}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return process.returncode == 0
    except Exception:
        return False


async def install_package(package_name):
    """
    Install a package using uv add

    Args:
        package_name (str): The name of the package to install

    Returns:
        bool: True if installation successful, False otherwise
    """
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "uv", "add", package_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return process.returncode == 0
    except Exception as e:
        print(f"Error installing {package_name}: {e}")
        return False
