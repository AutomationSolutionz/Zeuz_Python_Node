import platform
import os
import shutil
import subprocess
import json
import tempfile
import asyncio
from pathlib import Path
from Framework.install_handler.utils import send_response

async def _send_status(status: str, comment: str):
    """Helper to send status responses."""
    print(f"[{status}] {comment}")
    await send_response(
        {
            "action": "status",
            "data": {
                "category": "iOS",
                "name": "WebDriver",
                "status": status,
                "comment": comment,
            },
        }
    )

def _get_webdriver_path() -> Path:
    home = Path.home()
    return home / ".zeuz" / "WebDriverAgent"

async def _check_xcode_installed() -> bool:
    if not os.path.exists("/Applications/Xcode.app"):
        return False
    return shutil.which("xcodebuild") is not None

async def _get_best_simulator() -> tuple[str, str] | None:
    """Finds the best candidate simulator (preferring iPhones)."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "available", "-j"],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            return None
        
        data = json.loads(result.stdout)
        candidates = []

        for runtime_key, devices in data.get("devices", {}).items():
            if "iOS" not in runtime_key:
                continue
            for device in devices:
                if device.get("isAvailable"):
                    name = device.get("name")
                    uuid = device.get("udid")
                    score = 2 if "iPhone" in name else 1
                    candidates.append((score, name, uuid))

        candidates.sort(key=lambda x: x[0], reverse=True)
        if candidates:
            return candidates[0][1], candidates[0][2]
        return None
    except Exception as e:
        print(f"Error listing simulators: {e}")
        return None

async def _boot_simulator_if_needed(device_uuid: str) -> bool:
    """Boots the simulator ONLY if it is currently shutdown."""
    try:
        # 1. Check current state
        list_res = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "-j"],
            capture_output=True, text=True
        )
        if list_res.returncode == 0:
            data = json.loads(list_res.stdout)
            for runtime, devices in data.get("devices", {}).items():
                for device in devices:
                    if device.get("udid") == device_uuid:
                        if device.get("state") == "Booted":
                            # Already booted
                            return True

        # 2. Boot if needed
        await _send_status("installing", "Booting simulator to perform check/install...")
        subprocess.run(["open", "-a", "Simulator"], capture_output=True)
        
        # Give the app a moment to launch
        await asyncio.sleep(2)
        
        subprocess.run(["xcrun", "simctl", "boot", device_uuid], capture_output=True)
        
        # 3. Wait for 'Booted' status
        res = subprocess.run(
            ["xcrun", "simctl", "bootstatus", device_uuid],
            capture_output=True, timeout=120
        )
        return res.returncode == 0
    except Exception as e:
        print(f"Boot exception: {e}")
        # We return True here to attempt the next step anyway, 
        # as sometimes bootstatus fails even if the device works.
        return True

async def check_status() -> bool:
    """Checks if WebDriverAgent is installed (Ensures Simulator is ON)."""
    print("[webdriver] Checking status...")

    if platform.system().lower() != "darwin":
        await _send_status("error", "Unsupported OS.")
        return False

    if not await _check_xcode_installed():
        await _send_status("not installed", "Xcode missing.")
        return False

    webdriver_path = _get_webdriver_path()
    if not (webdriver_path / "WebDriverAgent.xcodeproj").exists():
        await _send_status("not installed", "Repo not cloned.")
        return False

    sim_info = await _get_best_simulator()
    if not sim_info:
        await _send_status("not installed", "No iOS Simulator devices found.")
        return False
        
    name, uuid = sim_info

    if not await _boot_simulator_if_needed(uuid):
        await _send_status("error", f"Failed to boot {name} for verification.")
        return False

    # Check if app container exists
    cmd = ["xcrun", "simctl", "get_app_container", uuid, "com.facebook.WebDriverAgentRunner.xctrunner"]
    check_res = subprocess.run(cmd, capture_output=True, text=True)
    
    if check_res.returncode == 0 and check_res.stdout.strip():
        await _send_status("installed", f"WebDriverAgent found on {name} ({uuid}).")
        return True
    else:
        await _send_status("not installed", f"WebDriverAgent not found on {name} ({uuid}).")
        return False

async def _build_and_install_webdriver(webdriver_path: Path) -> bool:
    try:
        sim_info = await _get_best_simulator()
        if not sim_info: return False
        name, uuid = sim_info

        # Ensure booted (check_status might have done this, but good to double check)
        if not await _boot_simulator_if_needed(uuid):
            await _send_status("error", "Failed to boot simulator.")
            return False

        await _send_status("installing", f"Building WebDriverAgent for {name}...")

        # Create a temp directory to store build artifacts
        with tempfile.TemporaryDirectory() as derived_data_path:
            cmd = [
                "xcodebuild",
                "-project", "WebDriverAgent.xcodeproj",
                "-scheme", "WebDriverAgentRunner",
                "-destination", f"platform=iOS Simulator,id={uuid}",
                "-derivedDataPath", derived_data_path,
                "-allowProvisioningUpdates",
                "build-for-testing"
            ]
            
            result = subprocess.run(
                cmd, cwd=str(webdriver_path),
                capture_output=True, text=True, timeout=1200
            )

            if result.returncode != 0:
                err = result.stderr[-500:] if result.stderr else "Unknown error"
                await _send_status("error", f"Build failed: {err}")
                return False

            # Explicitly Install the Built App
            await _send_status("installing", "Installing WebDriverAgentRunner-Runner.app...")
            
            app_path = Path(derived_data_path) / "Build" / "Products" / "Debug-iphonesimulator" / "WebDriverAgentRunner-Runner.app"
            
            if not app_path.exists():
                await _send_status("error", f"Could not find built app at {app_path}")
                return False
                
            install_res = subprocess.run(
                ["xcrun", "simctl", "install", uuid, str(app_path)],
                capture_output=True, text=True
            )
            
            if install_res.returncode != 0:
                await _send_status("error", f"Install failed: {install_res.stderr.strip()}")
                return False

            await _send_status("installing", "App installed successfully via simctl.")
            return True

    except Exception as e:
        await _send_status("error", f"Build/Install exception: {e}")
        return False

async def _clone_repository(webdriver_path: Path) -> bool:
    try:
        if webdriver_path.exists():
            shutil.rmtree(webdriver_path)
        webdriver_path.parent.mkdir(parents=True, exist_ok=True)
        
        await _send_status("installing", "Cloning WebDriverAgent...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/appium/WebDriverAgent.git", str(webdriver_path)],
            check=True, capture_output=True
        )
        return True
    except Exception as e:
        await _send_status("error", f"Clone failed: {e}")
        return False

async def _bootstrap_webdriver(webdriver_path: Path):
    script = webdriver_path / "Scripts" / "bootstrap.sh"
    if script.exists():
        try:
            await _send_status("installing", "Running bootstrap...")
            subprocess.run(["bash", str(script)], cwd=str(webdriver_path), capture_output=True)
        except: pass

async def install(user_password: str = "") -> bool:
    print("[webdriver] Starting installation...")
    
    if await check_status():
        return True

    if not await _check_xcode_installed():
        await _send_status("error", "Xcode required.")
        return False

    webdriver_path = _get_webdriver_path()

    if not await _clone_repository(webdriver_path): return False
    await _bootstrap_webdriver(webdriver_path)

    if not await _build_and_install_webdriver(webdriver_path): return False

    if await check_status():
        await _send_status("installed", "WebDriverAgent installed successfully.")
        return True
    else:
        await _send_status("error", "Installation completed but verification failed.")
        return False