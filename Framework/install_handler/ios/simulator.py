import asyncio
import platform
import os
import shutil
import subprocess
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


async def check_status() -> bool:
    """Check if iOS Simulator is installed and available."""
    print("[simulator] Checking status...")

    if platform.system().lower() != "darwin":
        await _send_status(
            "error", "Unsupported OS. iOS Simulator is only available on macOS."
        )
        return False

    # Check if Xcode is installed first (required for simulators)
    if not os.path.exists("/Applications/Xcode.app"):
        await _send_status(
            "not installed", "Xcode must be installed before using iOS Simulator."
        )
        return False

    # Check if simctl is available
    simctl_path = shutil.which("xcrun")
    if not simctl_path:
        await _send_status(
            "not installed", "xcrun not found. Xcode command line tools may not be installed."
        )
        return False

    try:
        # Check if any simulators are available
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "available"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        if result.returncode != 0:
            await _send_status(
                "error", f"simctl error: {result.stderr.strip()}"
            )
            return False

        # Check if there are any iOS simulators available
        output = result.stdout
        if "iOS" in output or "iPhone" in output or "iPad" in output:
            # Count number of available devices
            device_lines = [line for line in output.splitlines() if "(" in line and ")" in line and "Booted" not in line]
            if len(device_lines) > 0:
                await _send_status(
                    "installed", f"iOS Simulator available with {len(device_lines)} devices."
                )
                return True
            else:
                await _send_status(
                    "not installed", "No iOS Simulator devices found. Install Xcode or simulator runtimes."
                )
                return False
        else:
            await _send_status(
                "not installed", "No iOS Simulator devices found. Install Xcode or simulator runtimes."
            )
            return False

    except subprocess.TimeoutExpired:
        await _send_status("error", "simctl command timed out.")
        return False
    except Exception as e:
        await _send_status("error", f"Error checking iOS Simulator: {e}")
        return False


async def _install_command_line_tools(user_password: str) -> bool:
    """Install Xcode command line tools if not present."""
    try:
        # Check if already installed
        result = subprocess.run(
            ["xcode-select", "-p"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        if result.returncode == 0:
            return True

        # Install command line tools
        await _send_status(
            "installing", "Installing Xcode command line tools, please wait..."
        )
        
        install_result = subprocess.run(
            ["xcode-select", "--install"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        # Wait for installation to complete (poll for up to 30 minutes)
        timeout_seconds = 30 * 60
        interval = 10
        elapsed = 0

        while elapsed < timeout_seconds:
            await asyncio.sleep(interval)
            elapsed += interval

            check_result = subprocess.run(
                ["xcode-select", "-p"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if check_result.returncode == 0:
                return True

        await _send_status("error", "Timed out waiting for command line tools installation.")
        return False

    except Exception as e:
        await _send_status("error", f"Error installing command line tools: {e}")
        return False


async def _install_simulator_runtime(user_password: str) -> bool:
    """Install iOS Simulator runtime if missing."""
    try:
        # First, ensure Xcode command line tools are set correctly
        if user_password:
            xcode_select_cmd = f"echo '{user_password}' | sudo -S xcode-select --switch /Applications/Xcode.app/Contents/Developer"
            result = subprocess.run(
                xcode_select_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
        else:
            result = subprocess.run(
                ["xcode-select", "--switch", "/Applications/Xcode.app/Contents/Developer"],
                capture_output=True,
                text=True,
                timeout=30,
            )

        # Check available simulator runtimes
        await _send_status(
            "installing", "Checking for available iOS Simulator runtimes..."
        )
        
        runtime_result = subprocess.run(
            ["xcrun", "simctl", "list", "runtimes"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if runtime_result.returncode != 0:
            await _send_status(
                "error", f"Failed to list runtimes: {runtime_result.stderr.strip()}"
            )
            return False

        # Check if iOS runtimes are present and have devices
        has_ios_runtime = "iOS" in runtime_result.stdout
        
        if has_ios_runtime:
            # Verify that there are actual simulator devices available
            devices_result = subprocess.run(
                ["xcrun", "simctl", "list", "devices", "available", "iOS"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if devices_result.returncode == 0:
                output = devices_result.stdout
                device_lines = [line for line in output.splitlines() if "(" in line and ")" in line]
                
                if len(device_lines) > 0:
                    return True
        
        # No iOS runtimes or devices found, attempt to download and install
        await _send_status(
            "installing", 
            "Downloading iOS Simulator runtime, this may take several minutes..."
        )
        
        # Download iOS platform using xcodebuild
        download_result = subprocess.run(
            ["xcodebuild", "-downloadPlatform", "iOS"],
            capture_output=True,
            text=True,
            timeout=3600,  # 1 hour timeout for download
        )
        
        if download_result.returncode != 0:
            await _send_status(
                "error", 
                f"Failed to download platform. Please install via Xcode > Settings > Platforms. Error: {download_result.stderr.strip()[-200:]}"
            )
            return False
        
        # Wait a moment for installation to complete
        await asyncio.sleep(5)
        
        # Verify installation
        verify_result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "available", "iOS"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        if verify_result.returncode == 0:
            output = verify_result.stdout
            device_lines = [line for line in output.splitlines() if "(" in line and ")" in line]
            
            if len(device_lines) > 0:
                await _send_status(
                    "installed", 
                    f"iOS Simulator runtime installed successfully with {len(device_lines)} devices."
                )
                return True
        
        await _send_status(
            "error", 
            "Runtime installation completed but no devices found. Please verify via Xcode > Settings > Platforms."
        )
        return False

    except Exception as e:
        await _send_status("error", f"Error installing simulator runtime: {e}")
        return False


async def install(user_password: str = "") -> bool:
    """Install iOS Simulator (requires Xcode to be installed first)."""
    print("[simulator] Installing...")

    if platform.system().lower() != "darwin":
        await _send_status(
            "error", "Unsupported OS. iOS Simulator is only available on macOS."
        )
        return False

    # Check if already installed and working
    if await check_status():
        return True

    # Ensure Xcode is installed
    if not os.path.exists("/Applications/Xcode.app"):
        await _send_status(
            "error", "Xcode must be installed first. Please install Xcode from the App Store."
        )
        return False

    await _send_status(
        "installing", "Setting up iOS Simulator..."
    )

    # Install command line tools if needed
    if not await _install_command_line_tools(user_password):
        return False

    # Install/verify simulator runtime
    if not await _install_simulator_runtime(user_password):
        return False

    # Final status check
    if await check_status():
        await _send_status(
            "installed", "iOS Simulator is ready to use."
        )
        return True
    else:
        await _send_status(
            "error", "iOS Simulator setup completed but verification failed."
        )
        return False
