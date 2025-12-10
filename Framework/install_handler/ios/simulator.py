import asyncio
import platform
import os
import shutil
import subprocess
import json
import re
import tempfile
from pathlib import Path
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

async def get_available_simulators() -> list[dict]:
    """
    List available iOS Simulators by running xcrun simctl list devices.
    Returns a list of dictionaries with name, udid, and state fields.
    """
    try:
        if platform.system().lower() != "darwin":
            return []
        
        if not shutil.which("xcrun"):
            return []
        
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "available", "-j"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return []
        
        data = json.loads(result.stdout)
        simulators = []
        
        for runtime_key, devices in data.get("devices", {}).items():
            if "iOS" not in runtime_key:
                continue
            
            # Extract iOS version from runtime key (e.g., "com.apple.CoreSimulator.SimRuntime.iOS-18-2" -> "iOS 18.2")
            version_match = re.search(r'iOS-(\d+)-(\d+)', runtime_key)
            runtime_version = f"iOS {version_match.group(1)}.{version_match.group(2)}" if version_match else runtime_key
            
            for device in devices:
                if device.get("isAvailable"):
                    simulators.append({
                        "name": device.get("name"),
                        "udid": device.get("udid"),
                        "state": device.get("state"),
                        "runtime": runtime_version,
                        "comment": f"{device.get('name')} - {runtime_version} ({device.get('state')})"
                    })
        
        return simulators
    
    except Exception as e:
        print(f"[simulator] Error listing simulators: {e}")
        return []


async def get_available_device_types() -> list[dict]:
    """
    Get available iOS device types by running xcrun simctl list devicetypes.
    Returns a list of dictionaries with package (device type ID), version (device name), and description.
    Format matches Android's device list for consistency.
    """
    try:
        if platform.system().lower() != "darwin":
            return []
        
        if not shutil.which("xcrun"):
            return []
        
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devicetypes", "-j"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return []
        
        data = json.loads(result.stdout)
        device_types = []
        
        for device_type in data.get("devicetypes", []):
            name = device_type.get("name", "")
            identifier = device_type.get("identifier", "")
            
            # Filter for iPhone and iPad devices only
            if "iPhone" in name or "iPad" in name:
                device_types.append({
                    "package": identifier,  # device type ID
                    "version": name,         # device name
                    "description": "Apple"   # OEM
                })
        
        return device_types
    
    except Exception as e:
        print(f"[simulator] Error listing device types: {e}")
        return []


async def get_available_runtimes() -> list[dict]:
    """
    Get available iOS runtimes by running xcrun simctl list runtimes.
    Returns a list of dictionaries with runtime ID, version, and availability.
    """
    try:
        if platform.system().lower() != "darwin":
            return []
        
        if not shutil.which("xcrun"):
            return []
        
        result = subprocess.run(
            ["xcrun", "simctl", "list", "runtimes", "-j"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return []
        
        data = json.loads(result.stdout)
        runtimes = []
        
        for runtime in data.get("runtimes", []):
            platform_name = runtime.get("platform", "")
            name = runtime.get("name", "")
            
            # Filter for iOS runtimes only
            if platform_name == "iOS" or "iOS" in name:
                runtimes.append({
                    "identifier": runtime.get("identifier", ""),
                    "name": name,
                    "version": runtime.get("version", ""),
                    "isAvailable": runtime.get("isAvailable", False)
                })
        
        return runtimes
    
    except Exception as e:
        print(f"[simulator] Error listing runtimes: {e}")
        return []


async def ios_simulator_install():
    """
    Get available device types when install button is clicked.
    Returns list of available iOS device types for simulator creation.
    """
    print("[simulator] Getting available device types...")
    
    try:
        # Check if macOS
        if platform.system().lower() != "darwin":
            await send_response({
                "action": "status",
                "data": {
                    "category": "iOSSimulator",
                    "name": "Device Types",
                    "status": "Not Found",
                    "comment": "iOS Simulator is only available on macOS",
                    "installables": []
                }
            })
            return False
        
        # Check if Xcode is installed
        if not os.path.exists("/Applications/Xcode.app"):
            await send_response({
                "action": "status",
                "data": {
                    "category": "iOSSimulator",
                    "name": "Device Types",
                    "status": "Not Found",
                    "comment": "Xcode must be installed first",
                    "installables": []
                }
            })
            return False
        
        await send_response({
            "action": "status",
            "data": {
                "category": "iOSSimulator",
                "name": "Device Types",
                "status": "Fetching",
                "comment": "Fetching available device types...",
                "installables": []
            }
        })
        
        # Get available device types
        device_types = await get_available_device_types()
        print(f"[simulator] Available device types: {device_types}")
        
        await send_response({
            "action": "status",
            "data": {
                "category": "iOSSimulator",
                "installables": device_types,
            }
        })
        return True
        
    except Exception as e:
        print(f"[simulator] Error getting device types: {e}")
        await send_response({
            "action": "status",
            "data": {
                "category": "iOSSimulator",
                "name": "Device Types",
                "status": "error",
                "comment": f"Error: {e}",
                "installables": []
            }
        })
        return False


async def get_filtered_simulator_services():
    """
    Get available iOS simulators and return a formatted category dictionary.
    Similar to Android's get_filtered_avd_services.
    
    Returns:
        Dictionary with category "iOSSimulator" and filtered services, or None if no simulators
    """
    current_os = platform.system().lower()
    
    # iOS simulators only available on macOS
    if current_os != "darwin":
        return None
    
    try:
        simulators = await get_available_simulators()
        
        if not simulators:
            return None
        
        # Format simulators as services
        services_list = []
        for sim in simulators:
            services_list.append({
                "name": sim["udid"],  # Use UDID as the identifier
                "status": "installed",
                "comment": sim["comment"],
                "install_text": "delete",
                "install_function": "delete_simulator",
                "os": ["darwin"],
                "user_password": "no",
            })
        
        return {
            "group": {
                "check_text": "",
                "install_text": "",
            },
            "category": "iOSSimulator",
            "services": services_list,
        }
    
    except Exception as e:
        print(f"[simulator] Error getting filtered simulators: {e}")
        return None


async def delete_simulator(udid: str) -> bool:
    """
    Delete iOS Simulator by UDID using simctl delete.
    Sends response to server on success or failure.
    
    Args:
        udid: The UDID of the simulator to delete
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get simulator info first to show proper name in messages
        simulators = await get_available_simulators()
        simulator_info = next((s for s in simulators if s["udid"] == udid), None)
        
        if not simulator_info:
            error_msg = f"Simulator {udid} not found"
            print(f"[simulator] {error_msg}")
            await send_response({
                "action": "status",
                "data": {
                    "category": "iOSSimulator",
                    "name": udid,
                    "status": "not installed",
                    "comment": error_msg,
                }
            })
            return False
        
        simulator_name = simulator_info["name"]
        print(f"[simulator] Deleting simulator: {simulator_name} ({udid})")
        
        # Send deleting status
        await send_response({
            "action": "status",
            "data": {
                "category": "iOSSimulator",
                "name": udid,
                "status": "uninstalling",
                "comment": f"Deleting simulator {simulator_name}...",
            }
        })
        
        # Delete the simulator
        result = subprocess.run(
            ["xcrun", "simctl", "delete", udid],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            error_msg = f"Failed to delete simulator: {result.stderr.strip()}"
            print(f"[simulator] {error_msg}")
            await send_response({
                "action": "status",
                "data": {
                    "category": "iOSSimulator",
                    "name": udid,
                    "status": "error",
                    "comment": error_msg,
                }
            })
            return False
        
        print(f"[simulator] Simulator deleted successfully: {simulator_name} ({udid})")
        
        # Send success response
        await send_response({
            "action": "status",
            "data": {
                "category": "iOSSimulator",
                "name": udid,
                "status": "not installed",
                "comment": f"Simulator '{simulator_name}' deleted successfully",
            }
        })
        return True
    
    except subprocess.TimeoutExpired:
        error_msg = "Simulator deletion timed out"
        print(f"[simulator] {error_msg}")
        await send_response({
            "action": "status",
            "data": {
                "category": "iOSSimulator",
                "name": udid,
                "status": "error",
                "comment": error_msg,
            }
        })
        return False
    except Exception as e:
        error_msg = f"Error deleting simulator: {e}"
        print(f"[simulator] {error_msg}")
        import traceback
        traceback.print_exc()
        await send_response({
            "action": "status",
            "data": {
                "category": "iOSSimulator",
                "name": udid,
                "status": "error",
                "comment": error_msg,
            }
        })
        return False


async def launch_simulator(udid: str) -> bool:
    """
    Launch iOS Simulator using simctl boot and open Simulator app.
    Checks for WebDriverAgent installation and installs if needed.
    Launches WebDriverAgent app automatically.
    Non-blocking - the simulator starts in the background.
    Sends response to server on success or failure.
    """
    try:
        # Get simulator info first
        simulators = await get_available_simulators()
        simulator_info = next((s for s in simulators if s["udid"] == udid), None)
        
        if not simulator_info:
            error_msg = f"Simulator {udid} not found"
            print(f"[simulator] {error_msg}")
            await send_response({
                "action": "status",
                "data": {
                    "category": "iOSSimulator",
                    "name": udid,
                    "status": "not installed",
                    "comment": error_msg,
                }
            })
            return False
        
        simulator_name = simulator_info['name']
        is_already_booted = simulator_info["state"] == "Booted"
        
        # Boot simulator if not already booted
        if not is_already_booted:
            # Open Simulator app
            subprocess.Popen(
                ["open", "-a", "Simulator"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Small delay to let Simulator app launch
            await asyncio.sleep(1)
            
            # Boot the specific device
            result = subprocess.run(
                ["xcrun", "simctl", "boot", udid],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                error_msg = f"Failed to boot simulator: {result.stderr.strip()}"
                print(f"[simulator] {error_msg}")
                await send_response({
                    "action": "status",
                    "data": {
                        "category": "iOSSimulator",
                        "name": udid,
                        "status": "error",
                        "comment": error_msg,
                    }
                })
                return False
            
            print(f"[simulator] Booting simulator: {simulator_name}...")
            
            # Wait for boot to complete
            await asyncio.sleep(3)
        else:
            print(f"[simulator] Simulator {simulator_name} already running")
        
        # Check if WebDriverAgent is installed on this simulator
        print(f"[simulator] Checking WebDriverAgent installation on {simulator_name}...")
        check_wda = subprocess.run(
            ["xcrun", "simctl", "get_app_container", udid, "com.facebook.WebDriverAgentRunner.xctrunner"],
            capture_output=True,
            text=True
        )
        
        wda_installed = check_wda.returncode == 0 and check_wda.stdout.strip()
        
        if not wda_installed:
            print(f"[simulator] WebDriverAgent not found on {simulator_name}, installing...")
            await send_response({
                "action": "status",
                "data": {
                    "category": "iOSSimulator",
                    "name": udid,
                    "status": "installing",
                    "comment": f"Installing WebDriverAgent on {simulator_name}...",
                }
            })
            
            # Get WebDriverAgent path (same as webdriver.py uses)
            home = Path.home()
            webdriver_path = home / ".zeuz" / "WebDriverAgent"
            
            # Check if WebDriverAgent repo exists
            if not (webdriver_path / "WebDriverAgent.xcodeproj").exists():
                print(f"[simulator] Cloning WebDriverAgent repository...")
                if webdriver_path.exists():
                    shutil.rmtree(webdriver_path)
                webdriver_path.parent.mkdir(parents=True, exist_ok=True)
                
                clone_result = subprocess.run(
                    ["git", "clone", "--depth", "1", "https://github.com/appium/WebDriverAgent.git", str(webdriver_path)],
                    capture_output=True,
                    text=True
                )
                
                if clone_result.returncode != 0:
                    error_msg = f"Failed to clone WebDriverAgent: {clone_result.stderr}"
                    print(f"[simulator] {error_msg}")
                    # Continue with launching simulator even if WDA install fails
            
            # Build and install WebDriverAgent for this simulator
            if (webdriver_path / "WebDriverAgent.xcodeproj").exists():
                # Check if app is already built (in standard location)
                standard_build_path = webdriver_path / "Build" / "Products" / "Debug-iphonesimulator" / "WebDriverAgentRunner-Runner.app"
                app_path_to_install = None
                
                if standard_build_path.exists():
                    print(f"[simulator] Found pre-built WebDriverAgent at {standard_build_path}")
                    app_path_to_install = standard_build_path
                else:
                    # Need to build
                    print(f"[simulator] Building WebDriverAgent for {simulator_name}...")
                    
                    with tempfile.TemporaryDirectory() as derived_data_path:
                        build_cmd = [
                            "xcodebuild",
                            "-project", "WebDriverAgent.xcodeproj",
                            "-scheme", "WebDriverAgentRunner",
                            "-destination", f"platform=iOS Simulator,id={udid}",
                            "-derivedDataPath", derived_data_path,
                            "-allowProvisioningUpdates",
                            "build-for-testing"
                        ]
                        
                        build_result = subprocess.run(
                            build_cmd,
                            cwd=str(webdriver_path),
                            capture_output=True,
                            text=True,
                            timeout=1200
                        )
                        
                        if build_result.returncode == 0:
                            app_path = Path(derived_data_path) / "Build" / "Products" / "Debug-iphonesimulator" / "WebDriverAgentRunner-Runner.app"
                            
                            if app_path.exists():
                                # Copy to standard location before temp directory is deleted
                                standard_build_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copytree(app_path, standard_build_path, dirs_exist_ok=True)
                                print(f"[simulator] Copied built app to {standard_build_path}")
                                app_path_to_install = standard_build_path
                            else:
                                print(f"[simulator] WebDriverAgent app not found at {app_path}")
                        else:
                            print(f"[simulator] WebDriverAgent build failed: {build_result.stderr[-500:]}")
                
                # Install the app if we have it
                if app_path_to_install:
                    print(f"[simulator] Installing WebDriverAgent on {simulator_name}...")
                    install_result = subprocess.run(
                        ["xcrun", "simctl", "install", udid, str(app_path_to_install)],
                        capture_output=True,
                        text=True
                    )
                    
                    if install_result.returncode == 0:
                        print(f"[simulator] WebDriverAgent installed successfully on {simulator_name}")
                        wda_installed = True
                    else:
                        print(f"[simulator] Failed to install WebDriverAgent: {install_result.stderr}")
        else:
            print(f"[simulator] WebDriverAgent already installed on {simulator_name}")
        
        # Launch WebDriverAgent if installed
        if wda_installed:
            print(f"[simulator] Launching WebDriverAgent on {simulator_name}...")
            await send_response({
                "action": "status",
                "data": {
                    "category": "iOSSimulator",
                    "name": udid,
                    "status": "installing",
                    "comment": f"Launching WebDriverAgent on {simulator_name}...",
                }
            })
            
            # Launch WebDriverAgent app
            launch_wda = subprocess.run(
                ["xcrun", "simctl", "launch", udid, "com.facebook.WebDriverAgentRunner.xctrunner"],
                capture_output=True,
                text=True
            )
            
            if launch_wda.returncode == 0:
                print(f"[simulator] WebDriverAgent launched successfully on {simulator_name}")
                await send_response({
                    "action": "status",
                    "data": {
                        "category": "iOSSimulator",
                        "name": udid,
                        "status": "installed",
                        "comment": f"Simulator {simulator_name} running with WebDriverAgent",
                    }
                })
            else:
                print(f"[simulator] Failed to launch WebDriverAgent: {launch_wda.stderr}")
                await send_response({
                    "action": "status",
                    "data": {
                        "category": "iOSSimulator",
                        "name": udid,
                        "status": "installed",
                        "comment": f"Simulator {simulator_name} running (WebDriverAgent launch failed)",
                    }
                })
        else:
            # Simulator is running but WDA not available
            await send_response({
                "action": "status",
                "data": {
                    "category": "iOSSimulator",
                    "name": udid,
                    "status": "installed",
                    "comment": f"Simulator {simulator_name} is running",
                }
            })
        
        return True
    
    except subprocess.TimeoutExpired:
        error_msg = "Operation timed out"
        print(f"[simulator] {error_msg}")
        await send_response({
            "action": "status",
            "data": {
                "category": "iOSSimulator",
                "name": udid,
                "status": "error",
                "comment": error_msg,
            }
        })
        return False
    except Exception as e:
        error_msg = f"Failed to launch simulator: {e}"
        print(f"[simulator] {error_msg}")
        import traceback
        traceback.print_exc()
        await send_response({
            "action": "status",
            "data": {
                "category": "iOSSimulator",
                "name": udid,
                "status": "error",
                "comment": error_msg,
            }
        })
        return False


async def create_simulator_from_device_type(device_param: str) -> bool:
    """
    Create iOS Simulator from device type ID and device name.
    Uses the highest available iOS runtime.
    
    Args:
        device_param: Format "install device;device_type_id;device_name"
                     Example: "install device;com.apple.CoreSimulator.SimDeviceType.iPhone-16;iPhone 16"
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Parse device parameter
        parts = device_param.split(";")
        if len(parts) < 3:
            error_msg = f"Invalid device parameter format. Expected 'install device;device_type_id;device_name', got: {device_param}"
            print(f"[simulator] {error_msg}")
            await send_response({
                "action": "status",
                "data": {
                    "category": "iOSSimulator",
                    "name": "Unknown",
                    "status": "error",
                    "comment": error_msg,
                }
            })
            return False
        
        device_type_id = parts[1].strip()
        device_name = parts[2].strip()
        
        print(f"[simulator] Creating simulator '{device_name}' with device type '{device_type_id}'")
        
        # Get available runtimes
        runtimes = await get_available_runtimes()
        if not runtimes:
            error_msg = "No iOS runtimes found. Please install Xcode and iOS runtime first."
            print(f"[simulator] {error_msg}")
            await send_response({
                "action": "status",
                "data": {
                    "category": "iOSSimulator",
                    "name": device_name,
                    "status": "not installed",
                    "comment": error_msg,
                }
            })
            return False
        
        # Get the latest available runtime
        available_runtimes = [r for r in runtimes if r.get("isAvailable", False)]
        if not available_runtimes:
            error_msg = "No available iOS runtimes found."
            print(f"[simulator] {error_msg}")
            await send_response({
                "action": "status",
                "data": {
                    "category": "iOSSimulator",
                    "name": device_name,
                    "status": "not installed",
                    "comment": error_msg,
                }
            })
            return False
        
        # Use the last runtime (usually the newest)
        runtime = available_runtimes[-1]
        runtime_id = runtime["identifier"]
        runtime_name = runtime["name"]
        
        print(f"[simulator] Using runtime: {runtime_name} ({runtime_id})")
        
        # Generate a unique simulator name
        existing_sims = await get_available_simulators()
        existing_names = [s["name"] for s in existing_sims]
        
        # Create unique name
        simulator_name = device_name
        counter = 1
        while simulator_name in existing_names:
            simulator_name = f"{device_name} ({counter})"
            counter += 1
        
        # Send installing status
        await send_response({
            "action": "status",
            "data": {
                "category": "iOSSimulator",
                "name": device_name,
                "status": "installing",
                "comment": f"Creating {simulator_name} with {runtime_name}...",
            }
        })
        
        # Create the simulator
        result = subprocess.run(
            ["xcrun", "simctl", "create", simulator_name, device_type_id, runtime_id],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            error_msg = f"Failed to create simulator: {result.stderr.strip()}"
            print(f"[simulator] {error_msg}")
            await send_response({
                "action": "status",
                "data": {
                    "category": "iOSSimulator",
                    "name": device_name,
                    "status": "not installed",
                    "comment": error_msg,
                }
            })
            return False
        
        new_udid = result.stdout.strip()
        print(f"[simulator] Simulator created successfully: {simulator_name} ({new_udid})")
        
        # Send success response
        await send_response({
            "action": "status",
            "data": {
                "category": "iOSSimulator",
                "name": device_name,
                "status": "installed",
                "comment": f"Simulator '{simulator_name}' created successfully ({new_udid})",
            }
        })
        
        return True
    
    except subprocess.TimeoutExpired:
        error_msg = "Simulator creation timed out"
        print(f"[simulator] {error_msg}")
        await send_response({
            "action": "status",
            "data": {
                "category": "iOSSimulator",
                "name": device_name if 'device_name' in locals() else "Unknown",
                "status": "error",
                "comment": error_msg,
            }
        })
        return False
    except Exception as e:
        error_msg = f"Error creating simulator: {e}"
        print(f"[simulator] {error_msg}")
        import traceback
        traceback.print_exc()
        await send_response({
            "action": "status",
            "data": {
                "category": "iOSSimulator",
                "name": device_name if 'device_name' in locals() else "Unknown",
                "status": "error",
                "comment": error_msg,
            }
        })
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