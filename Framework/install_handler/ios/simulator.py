import asyncio
import platform
import os
import shutil
import subprocess
import json
import re
from Framework.install_handler.utils import send_response

async def _send_status(status: str, comment: str):
    """Helper to send status responses."""
    await send_response(
        {
            "action": "status",
            "data": {
                "category": "iOS",
                "name": "Simulator",
                "status": status,
                "comment": comment,
            },
        }
    )

async def _create_default_device() -> bool:
    """
    Attempts to create a default iPhone simulator using the newest available 
    iOS runtime and the newest available iPhone device type.
    """
    await _send_status("installing", "No devices found. Creating a new default simulator...")

    try:
        # 1. Get available Runtimes (JSON is safer to parse)
        # We need to find the installed iOS runtime ID (e.g. com.apple.CoreSimulator.SimRuntime.iOS-18-0)
        runtime_proc = subprocess.run(
            ["xcrun", "simctl", "list", "runtimes", "-j"],
            capture_output=True,
            text=True
        )
        if runtime_proc.returncode != 0:
            raise Exception("Failed to list runtimes.")

        runtimes_data = json.loads(runtime_proc.stdout)
        available_runtimes = runtimes_data.get("runtimes", [])
        
        # Filter for iOS runtimes and sort to find the latest version
        ios_runtimes = [
            r for r in available_runtimes 
            if r.get("platform") == "iOS" or "iOS" in r.get("name", "")
        ]

        if not ios_runtimes:
            raise Exception("No iOS Runtimes found after installation.")

        # Sort by version (assuming name contains version or using buildversion)
        # We'll just pick the first one which is usually the latest in the list, 
        # or we can try to sort by the 'version' key if available.
        target_runtime = ios_runtimes[-1] # Usually the list is ordered, taking the last one is a safe bet for 'newest'
        runtime_id = target_runtime["identifier"]
        runtime_name = target_runtime["name"]

        # 2. Get available Device Types
        type_proc = subprocess.run(
            ["xcrun", "simctl", "list", "devicetypes", "-j"],
            capture_output=True,
            text=True
        )
        types_data = json.loads(type_proc.stdout)
        
        # Find a modern iPhone (e.g., iPhone 16, 15, or just the last "iPhone" in the list)
        device_types = [
            t for t in types_data.get("devicetypes", [])
            if "iPhone" in t.get("name", "")
        ]
        
        if not device_types:
            raise Exception("No iPhone device types found.")

        # Pick the last one (usually the newest model)
        target_device_type = device_types[-1]
        device_type_id = target_device_type["identifier"]
        device_name = target_device_type["name"]

        # 3. Create the device
        new_device_name = f"{device_name} (Default)"
        await _send_status("installing", f"Creating {new_device_name} with {runtime_name}...")

        create_proc = subprocess.run(
            ["xcrun", "simctl", "create", new_device_name, device_type_id, runtime_id],
            capture_output=True,
            text=True
        )

        if create_proc.returncode == 0:
            new_udid = create_proc.stdout.strip()
            await _send_status("installed", f"Created new device: {new_device_name} ({new_udid})")
            return True
        else:
            raise Exception(f"Failed to create device: {create_proc.stderr}")

    except Exception as e:
        await _send_status("error", f"Auto-creation of device failed: {e}")
        return False

async def check_status() -> bool:
    """Check if iOS Simulator is installed and available."""
    print("[simulator] Checking status...")

    if platform.system().lower() != "darwin":
        await _send_status("error", "Unsupported OS. iOS Simulator is only available on macOS.")
        return False

    if not os.path.exists("/Applications/Xcode.app"):
        await _send_status("not installed", "Xcode must be installed before using iOS Simulator.")
        return False

    if not shutil.which("xcrun"):
        await _send_status("not installed", "xcrun not found. Xcode command line tools missing.")
        return False

    try:
        # Check for available devices
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "available", "iOS"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        if result.returncode != 0:
            await _send_status("error", f"simctl error: {result.stderr.strip()}")
            return False

        output = result.stdout
        # Basic check: verify lines with UDIDs exist
        device_lines = [line for line in output.splitlines() if "(" in line and ")" in line]
        
        if len(device_lines) > 0:
            await _send_status("installed", f"iOS Simulator available with {len(device_lines)} devices.")
            return True
        else:
            await _send_status("not installed", "No iOS Simulator devices found.")
            return False

    except Exception as e:
        await _send_status("error", f"Error checking iOS Simulator: {e}")
        return False

async def _install_command_line_tools() -> bool:
    """Install Xcode command line tools if not present."""
    try:
        result = subprocess.run(["xcode-select", "-p"], capture_output=True, text=True)
        if result.returncode == 0:
            return True

        await _send_status("installing", "Installing Xcode command line tools...")
        subprocess.run(["xcode-select", "--install"], capture_output=True, text=True)
        
        # Poll for completion (simplified for brevity)
        for _ in range(60): # wait up to 10 mins
            await asyncio.sleep(10)
            if subprocess.run(["xcode-select", "-p"], capture_output=True).returncode == 0:
                return True
                
        await _send_status("error", "Timed out waiting for command line tools.")
        return False
    except Exception as e:
        await _send_status("error", f"Error installing tools: {e}")
        return False

async def _install_simulator_runtime(user_password: str) -> bool:
    """Install iOS Simulator runtime if missing."""
    try:
        # Ensure xcode-select is pointing to Xcode app
        cmd = ["xcode-select", "--switch", "/Applications/Xcode.app/Contents/Developer"]
        if user_password:
            # Use sudo -S for password piping if provided
            subprocess.run(
                f"echo '{user_password}' | sudo -S {' '.join(cmd)}",
                shell=True, capture_output=True
            )
        else:
            subprocess.run(cmd, capture_output=True)

        # Check existing runtimes
        await _send_status("installing", "Checking iOS Simulator runtimes...")
        
        # Download iOS platform using xcodebuild (Your provided block)
        await _send_status("installing", "Downloading iOS Simulator runtime (this may take a while)...")

        with subprocess.Popen(
            ["xcodebuild", "-downloadPlatform", "iOS"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        ) as process:
            for line in process.stdout:
                await _send_status("installing", line.strip())

        if process.returncode != 0:
            # Only fail if it's a real error. Sometimes it fails if already installed.
            # We proceed to verification regardless.
            pass 
        
        await asyncio.sleep(5)
        
        # Verify installation
        verify_result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "available", "iOS"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        device_count = 0
        if verify_result.returncode == 0:
            device_lines = [line for line in verify_result.stdout.splitlines() if "(" in line and ")" in line]
            device_count = len(device_lines)

        # LOGIC CHANGE: If installed but no devices, create one.
        if device_count > 0:
            await _send_status("installed", f"iOS Simulator runtime ready with {device_count} devices.")
            return True
        else:
            # Runtime might be there, but no devices created yet.
            # Attempt to create a default device.
            return await _create_default_device()

    except Exception as e:
        await _send_status("error", f"Error installing simulator runtime: {e}")
        return False

async def install(user_password: str = "") -> bool:
    """Main install entry point."""
    print("[simulator] Installing...")

    if platform.system().lower() != "darwin":
        await _send_status("error", "iOS Simulator is only available on macOS.")
        return False

    if await check_status():
        return True

    if not os.path.exists("/Applications/Xcode.app"):
        await _send_status("error", "Xcode must be installed first.")
        return False

    await _send_status("installing", "Setting up iOS Simulator...")

    if not await _install_command_line_tools():
        return False

    if not await _install_simulator_runtime(user_password):
        return False

    return await check_status()