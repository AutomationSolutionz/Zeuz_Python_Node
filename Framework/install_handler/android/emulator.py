#this file is for mac os emulator installation. there are codes for windows and linux as well but they are not used for now.
#windows and linux codes are in emulator_windows_linux.py

import os
import platform
import subprocess
import asyncio
import re
import random
import traceback
from pathlib import Path
from Framework.install_handler.utils import send_response, debug
from Framework.install_handler.android.android_sdk import _get_sdk_root
from Framework.install_handler.android.emulator_manager import ensure_android_emulator
from Framework.install_handler.install_log_config import get_logger

logger = get_logger()


def _find_executable(base_path: Path, base_name: str) -> Path | None:
    """Find an executable file with platform-specific extensions"""
    system = platform.system()
    if system == "Windows":
        exts = [".exe", ".bat", ".cmd", ""]
    elif system == "Linux":
        exts = ["", ".sh"]
    elif system == "Darwin":  # iOS/macOS
        exts = ["", ".sh"]
    else:
        return None
    
    for ext in exts:
        p = base_path / (base_name + ext)
        if p.is_file():
            return p
    return None


def _find_avdmanager(sdk_root: Path) -> Path | None:
    """Find avdmanager executable"""
    return _find_executable(sdk_root / "cmdline-tools" / "latest" / "bin", "avdmanager")


def _find_sdkmanager(sdk_root: Path) -> Path | None:
    """Find sdkmanager executable"""
    return _find_executable(sdk_root / "cmdline-tools" / "latest" / "bin", "sdkmanager")


def _is_windows():
    """Check if running on Windows"""
    return platform.system() == 'Windows'


def _is_linux():
    """Check if running on Linux"""
    return platform.system() == 'Linux'


def _is_darwin():
    """Check if running on macOS"""
    return platform.system() == 'Darwin'


def _build_android_process_env(sdk_root: Path | None = None) -> dict[str, str]:
    """
    Build subprocess env that always points to ZeuZ-managed Android SDK.
    This keeps sdkmanager/avdmanager/emulator in the same SDK context.
    """
    sdk_root = sdk_root or _get_sdk_root()
    env = os.environ.copy()
    sdk_root_str = str(sdk_root)
    env["ANDROID_HOME"] = sdk_root_str
    env["ANDROID_SDK_ROOT"] = sdk_root_str

    # Prepend SDK paths to make sure ZeuZ binaries are resolved first.
    sdk_paths = [
        str(sdk_root / "platform-tools"),
        str(sdk_root / "emulator"),
        str(sdk_root / "cmdline-tools" / "latest" / "bin"),
    ]
    current_path = env.get("PATH", "")
    env["PATH"] = os.pathsep.join([*sdk_paths, current_path]) if current_path else os.pathsep.join(sdk_paths)
    return env


def _run_avdmanager_capture(
    avdmanager: Path,
    sdk_root: Path,
    args: list[str],
    timeout: int
) -> subprocess.CompletedProcess:
    """
    Run avdmanager with SDK-root first, with a Darwin-only fallback that drops
    --sdk_root but keeps the ZeuZ SDK env vars.
    """
    env = _build_android_process_env(sdk_root)
    cmd_with_sdk_root = [str(avdmanager), f"--sdk_root={sdk_root}", *args]
    result = subprocess.run(
        cmd_with_sdk_root,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env
    )
    if result.returncode == 0 or not _is_darwin():
        return result

    if debug:
        logger.debug("[installer][emulator] avdmanager command failed with --sdk_root, retrying without it on macOS. stderr: %s", result.stderr)

    cmd_without_sdk_root = [str(avdmanager), *args]
    fallback_result = subprocess.run(
        cmd_without_sdk_root,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env
    )
    return fallback_result


def _read_file_tail(path: Path, max_lines: int = 20) -> str:
    """Read tail of a log file for error hints."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        tail = [line.strip() for line in lines[-max_lines:] if line.strip()]
        return " | ".join(tail)
    except Exception:
        return ""


def _get_host_arch() -> str:
    """Normalize host architecture for image selection."""
    arch = platform.machine().lower()
    if arch in {"arm64", "aarch64"}:
        return "arm64"
    if arch in {"x86_64", "amd64", "x64"}:
        return "x86_64"
    return arch


def _get_arch_preference_order() -> list[str]:
    """
    Return preferred system-image ABI order for current host.
    On Apple Silicon, arm64-v8a must be preferred over x86_64.
    """
    host_arch = _get_host_arch()
    if _is_darwin() and host_arch == "arm64":
        return ["arm64-v8a", "arm64", "aarch64", "x86_64", "x86"]
    if host_arch == "x86_64":
        return ["x86_64", "x86", "arm64-v8a", "arm64", "aarch64"]
    return [host_arch, "x86_64", "x86", "arm64-v8a", "arm64", "aarch64"]


def get_emulator_command():
    """
    Returns the correct emulator executable path depending on OS.
    Uses isolated SDK installation from android_sdk.py
    """
    system = platform.system()
    sdk_root = _get_sdk_root()
    
    if debug:
        logger.debug("[installer][emulator] Launch avd: %s", sdk_root)

    if system == "Windows":
        return os.path.join(str(sdk_root), "emulator", "emulator.exe")

    elif system == "Darwin":  # macOS
        return os.path.join(str(sdk_root), "emulator", "emulator")

    elif system == "Linux":
        return os.path.join(str(sdk_root), "emulator", "emulator")

    else:
        raise RuntimeError(f"Unsupported OS: {system}")


async def get_available_avds() -> list[dict]:
    """
    List available Android Virtual Devices (AVDs) by running avdmanager list avd.
    Returns a list of dictionaries with name and comment fields.
    """
    try:
        sdk_root = _get_sdk_root()
        
        # Check if Android SDK is installed
        if sdk_root is None:
            if debug:
                logger.debug("[installer][emulator] Android SDK not found. ANDROID_HOME or ANDROID_SDK_ROOT not set.")
            return []
        
        avdmanager = _find_avdmanager(sdk_root)
        
        if not avdmanager:
            if debug:
                logger.debug("[installer][emulator] avdmanager not found")
            return []
        
        # Run avdmanager list avd command using async executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: _run_avdmanager_capture(avdmanager, sdk_root, ["list", "avd"], 30)
        )
        
        if result.returncode != 0:
            if debug:
                logger.debug("[installer][emulator] avdmanager list avd failed: %s", result.stderr)
            return []
        
        output = result.stdout
        
        # Parse the output preserving original formatting
        avds = []
        current_avd = {}
        comment_lines = []
        lines = output.split('\n')
        
        for line in lines:
            stripped_line = line.strip()
            
            # Skip empty lines and header
            if not stripped_line:
                # Preserve empty lines if we're collecting comments (they're part of formatting)
                if current_avd.get("name") and comment_lines:
                    # Only add empty line if it's not trailing (there are non-empty lines after)
                    pass  # We'll skip empty lines to avoid trailing ones
                continue
            
            if stripped_line.startswith("Available Android Virtual Devices"):
                continue
            
            # Skip separator lines (e.g., "---------")
            if stripped_line.startswith("-") and all(c == "-" for c in stripped_line):
                continue
            
            # Parse Name
            if stripped_line.startswith("Name:"):
                # Save previous AVD if exists
                if current_avd.get("name"):
                    # Join all comment lines preserving original format
                    current_avd["comment"] = "\n".join(comment_lines).rstrip()
                    avds.append(current_avd)
                    comment_lines = []
                
                # Start new AVD
                name = stripped_line.replace("Name:", "").strip()
                
                current_avd = {
                    "name": name,
                    "status": "installed",
                    "comment": "",
                    "install_text": "",
                    "os": ["windows", "linux", "darwin"],
                    "check_text": "Launch",
                    "status_function": lambda avd=name: launch_avd(avd),
                    "user_password": "no",
                }
                continue
            
            # For all other lines (Path, Target, Based on, Tag/ABI, Sdcard)
            # Preserve the original line format (including indentation)
            if current_avd.get("name"):
                comment_lines.append(line)
        
        # Don't forget the last AVD
        if current_avd.get("name"):
            current_avd["comment"] = "\n".join(comment_lines).rstrip()
            avds.append(current_avd)
        
        return avds
    
    except subprocess.TimeoutExpired:
        if debug:
            logger.debug("[installer][emulator] avdmanager list avd timed out")
        return []
    except Exception as e:
        if debug:
            logger.debug("[installer][emulator] Error listing AVDs: %s", e)
        traceback.print_exc()
        return []


async def launch_avd(avd_name: str) -> bool:
    """
    Launch an AVD and wait until it is safe for automation.
    """
    try:
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": avd_name,
                "status": "installing",
                "comment": f"Starting {avd_name} and waiting for Android to become stable...",
            }
        })
        target = await asyncio.to_thread(
            ensure_android_emulator,
            requested_avd=avd_name,
            headless=False,
        )
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": avd_name,
                "status": "installed",
                "comment": f"Emulator {avd_name} is ready on {target.serial}",
            }
        })
        return True
    except Exception as e:
        error_msg = f"Failed to launch AVD {avd_name}: {e}"
        logger.error("[installer][emulator] %s", error_msg)
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": avd_name,
                "status": "not installed",
                "comment": error_msg,
            }
        })
        return False

async def get_filtered_avd_services():
   """
   Get available AVDs and filter them by OS, returning a formatted category dictionary.
   Uses the same filtering logic as generate_services_list in utils.py.
  
   Returns:
       Dictionary with category "AndroidEmulator" and filtered services, or None if no AVDs match
   """
   current_os = platform.system().lower()
  
   try:
       avds = await get_available_avds()
      
       if not avds:
           return None
      
       # Filter AVDs by OS (same logic as generate_services_list)
       filtered_services = []
       for avd in avds:
           # Check if AVD supports current OS
           if "os" in avd and current_os not in avd["os"]:
               continue
          
           # Create filtered service with only the fields needed (matching generate_services_list format)
           filtered_service = {
               "name": avd.get("name", ""),
               "status": avd.get("status", "installed"),
               "comment": avd.get("comment", ""),
               "install_text": avd.get("install_text", ""),
               "check_text": "Launch",
               "os": avd.get("os", []),
               "user_password": avd.get("user_password", "no")
           }
           filtered_services.append(filtered_service)
      
       # Return None if no services match, otherwise return category dict
       if not filtered_services:
           return None
      
       return {
           "category": "AndroidEmulator",
           "services": filtered_services
       }
  
   except Exception as e:
       if debug:
           logger.debug("[installer][emulator] Error getting filtered AVD services: %s", e)
       traceback.print_exc()
       return None

def _run_sdkmanager_list(sdkmanager: Path, sdk_root: Path) -> str:
    """Run sdkmanager --list with shell piping to filter system-images (OS-agnostic, synchronous)"""
    try:
        system = platform.system()
        
        if system == "Windows":
            # Windows: Use PowerShell Select-String
            command = f'& "{sdkmanager}" --sdk_root="{sdk_root}" --list | Select-String "system-images"'
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=60
            )
        elif system in ["Linux", "Darwin"]:
            # Linux/macOS: Use grep
            command = f'"{sdkmanager}" --sdk_root="{sdk_root}" --list | grep "system-images"'
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
        else:
            # Fallback: run without filtering
            result = subprocess.run(
                [str(sdkmanager), f"--sdk_root={sdk_root}", "--list"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                # Filter manually
                lines = result.stdout.split('\n')
                filtered = [line for line in lines if 'system-images' in line]
                return '\n'.join(filtered)
            else:
                if debug:
                    logger.debug("[installer][emulator] sdkmanager --list failed: %s", result.stderr)
                return ""
        
        if result.returncode == 0:
            return result.stdout
        else:
            if debug:
                logger.debug("[installer][emulator] sdkmanager --list failed: %s", result.stderr)
            return ""
    except subprocess.TimeoutExpired:
        if debug:
            logger.debug("[installer][emulator] sdkmanager --list timed out")
        return ""
    except Exception as e:
        if debug:
            logger.debug("[installer][emulator] Error running sdkmanager --list: %s", e)
        return ""


def _parse_system_image_details(output: str) -> list[dict]:
    """
    Parse system image details from sdkmanager --list output.
    Expected format: system-images;android-36.1;google_apis_playstore;x86_64 | 3 | Google Play Intel x86_64 Atom System Image
    Returns list of dicts with package, version, and description.
    """
    system_images = []
    lines = output.split('\n')
    
    for line in lines:
        stripped = line.strip()
        if not stripped or not stripped.startswith('system-images;'):
            continue
        
        # Parse the line: package | version | description
        # Split by | and clean up
        parts = [p.strip() for p in stripped.split('|')]
        
        if len(parts) >= 1:
            package = parts[0].strip()
            
            # Extract additional info if available
            version = parts[1].strip() if len(parts) > 1 else ""
            description = parts[2].strip() if len(parts) > 2 else ""
            
            system_images.append({
                "package": package,
                "version": version,
                "description": description,
                "status" : "not installed",
                "comment" : ""
            })
    
    return system_images


async def get_available_system_images() -> list[dict]:
    """
    Get available system images by running sdkmanager --list and parsing system-images.
    Returns a list of dictionaries with package, version, and description.
    Example: [{"package": "system-images;android-34;google_apis;x86_64", "version": "3", "description": "Google APIs Intel x86_64 Atom System Image"}]
    """
    try:
        sdk_root = _get_sdk_root()
        
        # Check if Android SDK is installed
        if sdk_root is None:
            if debug:
                logger.debug("[installer][emulator] Android SDK not found. ANDROID_HOME or ANDROID_SDK_ROOT not set.")
            await send_response({
                "action": "status",
                "data": {
                    "category": "Android Emulator",
                    "name": "System Images",
                    "status": "not installed",
                    "comment": "No system images found. Please make sure you have installed the ANDROID SDK components.",
                }
            })
            return []
        
        sdkmanager = _find_sdkmanager(sdk_root)
        
        if not sdkmanager:
            if debug:
                logger.debug("[installer][emulator] sdkmanager not found")
            return []
        
        # Check platform support
        if not (_is_windows() or _is_linux() or _is_darwin()):
            if debug:
                logger.debug("[installer][emulator] Unsupported platform: %s", platform.system())
            return []
        
        # Run sdkmanager --list using async executor
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(
            None,
            _run_sdkmanager_list,
            sdkmanager,
            sdk_root
        )
        
        if not output:
            if debug:
                logger.debug("[installer][emulator] sdkmanager --list returned empty output")
            return []
        
        # Parse system image details from output
        system_images = _parse_system_image_details(output)
        
        # Remove duplicates based on package name and sort
        seen = set()
        unique_images = []
        for img in system_images:
            if img["package"] not in seen:
                seen.add(img["package"])
                unique_images.append(img)
        
        # Sort by package name
        system_images = sorted(unique_images, key=lambda x: x["package"])
        
        if debug:
            logger.debug("[installer][emulator] Found %s available system images", len(system_images))
        return system_images
    
    except subprocess.TimeoutExpired:
        if debug:
            logger.debug("[installer][emulator] sdkmanager --list timed out")
        return []
    except Exception as e:
        if debug:
            logger.debug("[installer][emulator] Error getting available system images: %s", e)
        traceback.print_exc()
        return []


def _parse_device_list(output: str) -> list[dict]:
    """
    Parse device list from avdmanager list device output.
    package = device id
    version = device name
    description = OEM 
    As perviously, we were sending avaailable system images list, this is done to 
    keep the response send to the server same as before. Minimal changes required in the server.
    """
    devices = []
    lines = output.split('\n')
    current_device = {}
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines and header
        if not stripped or stripped.startswith("Available devices definitions:"):
            continue
        
        # Skip separator lines
        if stripped.startswith("-") and all(c == "-" for c in stripped):
            # Save previous device if exists
            if current_device.get("package"):
                # Add status and comment fields before appending
                current_device["status"] = "Not installed"
                current_device["comment"] = ""
                devices.append(current_device)
                current_device = {}
            continue
        
        # Parse device ID: id: 0 or "desktop_large"
        if stripped.startswith("id:"):
            # Extract the quoted part (device ID) -> package
            # Format: id: 2 or "desktop_large"
            match = re.search(r'"([^"]+)"', stripped)
            if match:
                current_device["package"] = match.group(1)
            else:
                # Fallback: try to extract numeric ID
                match = re.search(r'id:\s*(\d+)', stripped)
                if match:
                    current_device["package"] = match.group(1)
            continue
        
        # Parse Name: Name: Large Desktop -> version
        if stripped.startswith("Name:"):
            name = stripped.replace("Name:", "").strip()
            current_device["version"] = name
            continue
        
        # Parse OEM: OEM : Google -> description
        if stripped.startswith("OEM"):
            oem = stripped.split(":", 1)[1].strip() if ":" in stripped else ""
            current_device["description"] = oem
            continue
    
    # Don't forget the last device
    if current_device.get("package"):
        # Add status and comment fields before appending
        current_device["status"] = "Not installed"
        current_device["comment"] = ""
        devices.append(current_device)
    
    return devices


async def get_available_devices() -> list[dict]:
    """
    Get available devices by running avdmanager list device.
    Returns a list of dictionaries with package, version, and description (matching system images format).
    """
    try:
        sdk_root = _get_sdk_root()
        
        # Check if Android SDK is installed
        if sdk_root is None:
            if debug:
                logger.debug("[installer][emulator] Android SDK not found. ANDROID_HOME or ANDROID_SDK_ROOT not set.")
            await send_response({
                "action": "status",
                "data": {
                    "category": "Android Emulator",
                    "name": "System Images",
                    "status": "Not Found",
                    "comment": "No devices found. Please make sure you have installed the ANDROID SDK components.",
                }
            })
            return []
        
        avdmanager = _find_avdmanager(sdk_root)
        
        if not avdmanager:
            if debug:
                logger.debug("[installer][emulator] avdmanager not found")
            return []
        
        # Run avdmanager list device using async executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: _run_avdmanager_capture(avdmanager, sdk_root, ["list", "device"], 60)
        )
        
        if result.returncode != 0:
            if debug:
                logger.debug("[installer][emulator] avdmanager list device failed: %s", result.stderr)
            return []
        
        # Parse device details from output
        devices = _parse_device_list(result.stdout)
        
        # Filter out devices that already have AVDs created
        existing_avds = await get_available_avds()
        existing_avd_names = {avd["name"] for avd in existing_avds}
        
        filtered_devices = []
        for device in devices:
            device_name = device.get("version", "")  # version field contains device name
            if device_name:
                # Sanitize device name to match how AVD names are created
                sanitized_name = _sanitize_avd_name(device_name)
                # Check if an AVD with this name already exists
                if sanitized_name not in existing_avd_names:
                    filtered_devices.append(device)
                elif debug:
                    logger.debug("[installer][emulator] Filtering out device '%s' (AVD '%s' already exists)", device_name, sanitized_name)
            else:
                # If no device name, include it (shouldn't happen, but safe fallback)
                filtered_devices.append(device)
        
        if debug:
            logger.debug("[installer][emulator] Found %s available devices, %s not yet installed", len(devices), len(filtered_devices))
        return filtered_devices
    
    except subprocess.TimeoutExpired:
        if debug:
            logger.debug("[installer][emulator] avdmanager list device timed out")
        return []
    except Exception as e:
        logger.exception("[installer][emulator] Error getting available devices: %s", e)
        traceback.print_exc()
        return []

async def check_emulator_list():
    """
    Sends response to server with list of installed emulators for Android.
    """
    avd_list = await get_filtered_avd_services()
    if avd_list:
        await send_response(
            {
                "action": "services_update",
                "data": {
                    'category': 'AndroidEmulator',
                    "services": avd_list['services'],
                },
            }
        )
        return True
    return False

async def android_emulator_install():
    """
    Get available devices when install button is clicked.
    Returns list of available devices for emulator installation.
    """
    if debug:
        logger.debug("[installer][emulator] Getting available devices...")
    
    try:
        # Check if Android SDK is installed first
        sdk_root = _get_sdk_root()
        if sdk_root is None:
            if debug:
                logger.debug("[installer][emulator] Android SDK not found")
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "name": "System Images",
                    "status": "Not Found",
                    "comment": "Download and install Android SDK first",
                    "installables": []
                }
            })
            return False
        
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": "Devices",
                "status": "Fetching",
                "comment": "Fetching available devices...",
                "installables": []
            }
        })
        
        # Get available devices
        devices = await get_available_devices()
        if debug:
            logger.debug("[installer][emulator] Available devices: %s", devices)

        
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                ##"name": "System Images",
                #"status": "Found",
                # "comment": f"Available devices ({len(devices)} total)",
                "installables": devices,  # Send the full list with details
            }
        })
        return True
        
    except Exception as e:
        logger.exception("[installer][emulator] Error getting devices: %s", e)
        traceback.print_exc()
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": "Devices",
                "status": "not installed",
                "comment": f"Error getting devices: {str(e)}",
                "installables": []
            }
        })
        return False


# List of 20 four-letter words for AVD name generation
_AVD_NAME_WORDS = [
    "blue", "fast", "cool", "wave", "star", "moon", "fire", "wind", "rock", "tree",
    "lake", "snow", "rain", "gold", "dark", "light", "bold", "soft", "wild", "calm"
]


def _extract_android_version(system_image_name: str) -> str:
    """
    Extract Android version from system image name.
    Example: system-images;android-36-ext18;google_apis;arm64-v8 -> android-36
    """
    # Split by semicolon and get the second part (android-XX-...)
    parts = system_image_name.split(';')
    if len(parts) < 2:
        raise ValueError(f"Invalid system image name format: {system_image_name}")
    
    android_part = parts[1]  # e.g., "android-36-ext18"
    
    # Extract just the version part (android-XX)
    # Match "android-" followed by digits
    match = re.match(r'android-(\d+)', android_part)
    if not match:
        raise ValueError(f"Could not extract Android version from: {android_part}")
    
    return f"android-{match.group(1)}"


def _get_existing_avd_names() -> list[str]:
    """Get list of existing AVD names"""
    try:
        sdk_root = _get_sdk_root()
        if sdk_root is None:
            return []
        
        avdmanager = _find_avdmanager(sdk_root)
        if not avdmanager:
            return []
        
        result = _run_avdmanager_capture(avdmanager, sdk_root, ["list", "avd"], 30)
        
        if result.returncode != 0:
            return []
        
        # Parse AVD names from output
        avd_names = []
        for line in result.stdout.split('\n'):
            if line.strip().startswith('Name:'):
                name = line.strip().replace('Name:', '').strip()
                if name:
                    avd_names.append(name)
        
        return avd_names
    except Exception:
        return []


def _generate_avd_name(android_version: str, existing_avds: list[str]) -> str:
    """
    Generate a unique AVD name by combining Android version with two random words.
    Format: android-{version}-{word1}-{word2}
    """
    max_attempts = 100  # Prevent infinite loop
    
    for _ in range(max_attempts):
        # Pick two random words
        word1, word2 = random.sample(_AVD_NAME_WORDS, 2)
        avd_name = f"{android_version}-{word1}-{word2}"
        
        # Check if AVD name already exists
        if avd_name not in existing_avds:
            return avd_name
    
    # Fallback: add random number if all combinations are taken
    word1, word2 = random.sample(_AVD_NAME_WORDS, 2)
    random_num = random.randint(1000, 9999)
    return f"{android_version}-{word1}-{word2}-{random_num}"


def _run_sdkmanager_install_windows(sdkmanager: Path, sdk_root: Path, system_image: str, loop=None, device_id: str = None) -> tuple[bool, str]:
    """Install system image on Windows with real-time output"""
    try:
        # Use PowerShell to handle the command properly and auto-accept licenses
        # This approach pipes 'y' responses to automatically accept licenses
        yes_responses = ";".join(["echo y"] * 20)
        quoted_image = f"'{system_image}'"
        shell_cmd = f'powershell -Command "{yes_responses} | &\\"{str(sdkmanager)}\\" --sdk_root={sdk_root} {quoted_image}"'
        
        if debug:
            logger.debug("[installer][emulator] Running: sdkmanager --sdk_root=%s %s", sdk_root, system_image)
            logger.debug("[installer][emulator] This may take 10-30 minutes to download system image...")
        
        process = subprocess.Popen(
            shell_cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        # Close stdin - PowerShell piping will provide input
        process.stdin.close()
        
        # Print output in real-time as it comes, showing progress on single line
        output_lines = []
        last_progress = ""
        progress_count = []
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    stripped = line.strip()
                    output_lines.append(stripped)
                    
                    # Extract progress percentage from lines like "[====] 25% Loading..."
                    progress_match = re.search(r'\[.*?\]\s*(\d+)%\s*(.+)', stripped)
                    if progress_match:
                        percent = int(progress_match.group(1))
                        status = progress_match.group(2).strip()
                        current_progress = f"{percent}% {status}"
                        if current_progress != last_progress:
                            logger.info("[installer][emulator] Download progress: %s", current_progress)
                            last_progress = current_progress
                            
                            if loop and device_id:
                                rounded_percent = round(percent / 10) * 10
                                if rounded_percent not in progress_count:
                                    progress_count.append(rounded_percent)
                                    asyncio.run_coroutine_threadsafe(
                                        send_response({
                                            "action": "status",
                                            "data": {
                                                "category": "AndroidEmulator",
                                                "package": device_id,
                                                "status": "installing",
                                                "comment": f"Downloading system image... {percent}% {status}",
                                            }
                                        }),
                                        loop
                                    )
                    elif stripped and not stripped.startswith('[') and '%' not in stripped:
                        # Print important non-progress messages on new line
                        logger.info("[installer][emulator] %s", stripped)
                    elif stripped.endswith('%'):
                        # Handle lines that end with just percentage
                        percent_match = re.search(r'(\d+)%', stripped)
                        if percent_match:
                            percent = int(percent_match.group(1))
                            logger.info("[installer][emulator] Download progress: %s", stripped)
                            
                            if loop and device_id:
                                rounded_percent = round(percent / 10) * 10
                                if rounded_percent not in progress_count:
                                    progress_count.append(rounded_percent)
                                    asyncio.run_coroutine_threadsafe(
                                        send_response({
                                            "action": "status",
                                            "data": {
                                                "category": "AndroidEmulator",
                                                "package": device_id,
                                                "status": "installing",
                                                "comment": f"Downloading system image... {percent}%",
                                            }
                                        }),
                                        loop
                                    )
        except Exception as e:
            logger.error("[installer][emulator] Output reading error: %s", e)
        finally:
            pass  # New line after progress completes
        
        process.stdout.close()
        returncode = process.wait(timeout=1800)  # 30 minutes for large system image downloads
        
        output = "\n".join(output_lines)
        if returncode == 0:
            return True, output
        else:
            return False, output
    except subprocess.TimeoutExpired:
        return False, "Installation timed out after 30 minutes"
    except Exception as e:
        return False, str(e)


def _run_sdkmanager_install_linux(sdkmanager: Path, sdk_root: Path, system_image: str, loop=None, device_id: str = None) -> tuple[bool, str]:
    """Install system image on Linux with real-time output"""
    try:
        if debug:
            logger.debug("[installer][emulator] Running: sdkmanager --sdk_root=%s %s", sdk_root, system_image)
            logger.debug("[installer][emulator] This may take 10-30 minutes to download system image...")
        
        process = subprocess.Popen(
            [str(sdkmanager), f"--sdk_root={sdk_root}", system_image],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Print output in real-time as it comes, showing progress on single line
        output_lines = []
        last_progress = ""
        progress_count = []
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    stripped = line.strip()
                    output_lines.append(stripped)
                    
                    # Extract progress percentage from lines like "[====] 25% Loading..."
                    progress_match = re.search(r'\[.*?\]\s*(\d+)%\s*(.+)', stripped)
                    if progress_match:
                        percent = int(progress_match.group(1))
                        status = progress_match.group(2).strip()
                        current_progress = f"{percent}% {status}"
                        if current_progress != last_progress:
                            logger.info("[installer][emulator] Download progress: %s", current_progress)
                            last_progress = current_progress
                            
                            if loop and device_id:
                                rounded_percent = round(percent / 10) * 10
                                if rounded_percent not in progress_count:
                                    progress_count.append(rounded_percent)
                                    asyncio.run_coroutine_threadsafe(
                                        send_response({
                                            "action": "status",
                                            "data": {
                                                "category": "AndroidEmulator",
                                                "package": device_id,
                                                "status": "installing",
                                                "comment": f"Downloading system image... {percent}% {status}",
                                            }
                                        }),
                                        loop
                                    )
                    elif stripped and not stripped.startswith('[') and '%' not in stripped:
                        # Print important non-progress messages on new line
                        logger.info("[installer][emulator] %s", stripped)
                    elif stripped.endswith('%'):
                        # Handle lines that end with just percentage
                        percent_match = re.search(r'(\d+)%', stripped)
                        if percent_match:
                            percent = int(percent_match.group(1))
                            logger.info("[installer][emulator] Download progress: %s", stripped)
                            
                            if loop and device_id:
                                rounded_percent = round(percent / 10) * 10
                                if rounded_percent not in progress_count:
                                    progress_count.append(rounded_percent)
                                    asyncio.run_coroutine_threadsafe(
                                        send_response({
                                            "action": "status",
                                            "data": {
                                                "category": "AndroidEmulator",
                                                "package": device_id,
                                                "status": "installing",
                                                "comment": f"Downloading system image... {percent}%",
                                            }
                                        }),
                                        loop
                                    )
        except Exception as e:
            logger.error("[installer][emulator] Output reading error: %s", e)
        finally:
            pass  # New line after progress completes
        
        process.stdout.close()
        returncode = process.wait(timeout=1800)  # 30 minutes for large system image downloads
        
        output = "\n".join(output_lines)
        if returncode == 0:
            return True, output
        else:
            return False, output
    except subprocess.TimeoutExpired:
        return False, "Installation timed out after 30 minutes"
    except Exception as e:
        return False, str(e)


def _run_sdkmanager_install_darwin(sdkmanager: Path, sdk_root: Path, system_image: str, loop=None, device_id: str = None) -> tuple[bool, str]:
    """Install system image on macOS with real-time output"""
    try:
        if debug:
            logger.debug("[installer][emulator] Running: sdkmanager --sdk_root=%s %s", sdk_root, system_image)
            logger.debug("[installer][emulator] This may take 10-30 minutes to download system image...")
        
        process = subprocess.Popen(
            [str(sdkmanager), f"--sdk_root={sdk_root}", system_image],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Print output in real-time as it comes, showing progress on single line
        output_lines = []
        last_progress = ""
        progress_count = []
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    stripped = line.strip()
                    output_lines.append(stripped)
                    
                    # Extract progress percentage from lines like "[====] 25% Loading..."
                    progress_match = re.search(r'\[.*?\]\s*(\d+)%\s*(.+)', stripped)
                    if progress_match:
                        percent = int(progress_match.group(1))
                        status = progress_match.group(2).strip()
                        current_progress = f"{percent}% {status}"
                        if current_progress != last_progress:
                            logger.info("[installer][emulator] Download progress: %s", current_progress)
                            last_progress = current_progress
                            
                            if loop and device_id:
                                rounded_percent = round(percent / 10) * 10
                                if rounded_percent not in progress_count:
                                    progress_count.append(rounded_percent)
                                    asyncio.run_coroutine_threadsafe(
                                        send_response({
                                            "action": "status",
                                            "data": {
                                                "category": "AndroidEmulator",
                                                "package": device_id,
                                                "status": "installing",
                                                "comment": f"Downloading system image... {percent}% {status}",
                                            }
                                        }),
                                        loop
                                    )
                    elif stripped and not stripped.startswith('[') and '%' not in stripped:
                        # Print important non-progress messages on new line
                        logger.info("[installer][emulator] %s", stripped)
                    elif stripped.endswith('%'):
                        # Handle lines that end with just percentage
                        percent_match = re.search(r'(\d+)%', stripped)
                        if percent_match:
                            percent = int(percent_match.group(1))
                            logger.info("[installer][emulator] Download progress: %s", stripped)
                            
                            if loop and device_id:
                                rounded_percent = round(percent / 10) * 10
                                if rounded_percent not in progress_count:
                                    progress_count.append(rounded_percent)
                                    asyncio.run_coroutine_threadsafe(
                                        send_response({
                                            "action": "status",
                                            "data": {
                                                "category": "AndroidEmulator",
                                                "package": device_id,
                                                "status": "installing",
                                                "comment": f"Downloading system image... {percent}%",
                                            }
                                        }),
                                        loop
                                    )
        except Exception as e:
            logger.error("[installer][emulator] Output reading error: %s", e)
        finally:
            pass  # New line after progress completes
        
        process.stdout.close()
        returncode = process.wait(timeout=1800)  # 30 minutes for large system image downloads
        
        output = "\n".join(output_lines)
        if returncode == 0:
            return True, output
        else:
            return False, output
    except subprocess.TimeoutExpired:
        return False, "Installation timed out after 30 minutes"
    except Exception as e:
        return False, str(e)


def _run_avdmanager_create_windows(avdmanager: Path, sdk_root: Path, avd_name: str, system_image: str, device_id: str) -> tuple[bool, str]:
    """Create AVD on Windows with real-time output"""
    try:
        # Create AVD: avdmanager create avd -n {avd_name} -k {system_image} -d {device_id}
        # Answer "no" to custom hardware profile prompt
        env = _build_android_process_env(sdk_root)
        process = subprocess.Popen(
            [str(avdmanager), f"--sdk_root={sdk_root}", "create", "avd", "-n", avd_name, "-k", system_image, "-d", device_id],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
            env=env
        )
        
        # Send "no" to custom hardware profile prompt
        process.stdin.write("no\n")
        process.stdin.close()
        
        # Print output in real-time as it comes, showing progress on single line
        output_lines = []
        last_progress = ""
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    stripped = line.strip()
                    output_lines.append(stripped)
                    
                    # Extract progress percentage from lines like "[====] 25% Loading..."
                    progress_match = re.search(r'\[.*?\]\s*(\d+)%\s*(.+)', stripped)
                    if progress_match:
                        percent = progress_match.group(1)
                        status = progress_match.group(2).strip()
                        current_progress = f"{percent}% {status}"
                        if current_progress != last_progress:
                            logger.info("[installer][emulator] Download progress: %s", current_progress)
                            last_progress = current_progress
                    elif stripped and not stripped.startswith('[') and '%' not in stripped:
                        # Print important non-progress messages on new line
                        logger.info("[installer][emulator] %s", stripped)
                    elif stripped.endswith('%'):
                        # Handle lines that end with just percentage
                        logger.info("[installer][emulator] Download progress: %s", stripped)
        except Exception as e:
            logger.error("[installer][emulator] Output reading error: %s", e)
        finally:
            pass  # New line after progress completes
        
        process.stdout.close()
        returncode = process.wait(timeout=120)
        
        output = "\n".join(output_lines)
        if returncode == 0:
            return True, output
        else:
            return False, output
    except subprocess.TimeoutExpired:
        return False, "AVD creation timed out"
    except Exception as e:
        return False, str(e)


def _run_avdmanager_create_linux(avdmanager: Path, sdk_root: Path, avd_name: str, system_image: str, device_id: str) -> tuple[bool, str]:
    """Create AVD on Linux with real-time output"""
    try:
        # Create AVD: avdmanager create avd -n {avd_name} -k {system_image} -d {device_id}
        # Answer "no" to custom hardware profile prompt
        env = _build_android_process_env(sdk_root)
        process = subprocess.Popen(
            [str(avdmanager), f"--sdk_root={sdk_root}", "create", "avd", "-n", avd_name, "-k", system_image, "-d", device_id],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
            env=env
        )
        
        # Send "no" to custom hardware profile prompt
        process.stdin.write("no\n")
        process.stdin.close()
        
        # Print output in real-time as it comes, showing progress on single line
        output_lines = []
        last_progress = ""
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    stripped = line.strip()
                    output_lines.append(stripped)
                    
                    # Extract progress percentage from lines like "[====] 25% Loading..."
                    progress_match = re.search(r'\[.*?\]\s*(\d+)%\s*(.+)', stripped)
                    if progress_match:
                        percent = progress_match.group(1)
                        status = progress_match.group(2).strip()
                        current_progress = f"{percent}% {status}"
                        if current_progress != last_progress:
                            logger.info("[installer][emulator] Download progress: %s", current_progress)
                            last_progress = current_progress
                    elif stripped and not stripped.startswith('[') and '%' not in stripped:
                        # Print important non-progress messages on new line
                        logger.info("[installer][emulator] %s", stripped)
                    elif stripped.endswith('%'):
                        # Handle lines that end with just percentage
                        logger.info("[installer][emulator] Download progress: %s", stripped)
        except Exception as e:
            logger.error("[installer][emulator] Output reading error: %s", e)
        finally:
            pass  # New line after progress completes
        
        process.stdout.close()
        returncode = process.wait(timeout=120)
        
        output = "\n".join(output_lines)
        if returncode == 0:
            return True, output
        else:
            return False, output
    except subprocess.TimeoutExpired:
        return False, "AVD creation timed out"
    except Exception as e:
        return False, str(e)


def _run_avdmanager_create_darwin(avdmanager: Path, sdk_root: Path, avd_name: str, system_image: str, device_id: str) -> tuple[bool, str]:
    """Create AVD on macOS with real-time output"""
    try:
        env = _build_android_process_env(sdk_root)

        def _run_create_command(cmd: list[str]) -> tuple[bool, str]:
            # Create AVD: avdmanager create avd -n {avd_name} -k {system_image} -d {device_id}
            # Answer "no" to custom hardware profile prompt
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # Line buffered
                env=env
            )

            process.stdin.write("no\n")
            process.stdin.close()

            output_lines = []
            last_progress = ""
            try:
                for line in iter(process.stdout.readline, ''):
                    if line:
                        stripped = line.strip()
                        output_lines.append(stripped)

                        # Extract progress percentage from lines like "[====] 25% Loading..."
                        progress_match = re.search(r'\[.*?\]\s*(\d+)%\s*(.+)', stripped)
                        if progress_match:
                            percent = progress_match.group(1)
                            status = progress_match.group(2).strip()
                            current_progress = f"{percent}% {status}"
                            if current_progress != last_progress:
                                logger.info("[installer][emulator] Download progress: %s", current_progress)
                                last_progress = current_progress
                        elif stripped and not stripped.startswith('[') and '%' not in stripped:
                            # Print important non-progress messages on new line
                            logger.info("[installer][emulator] %s", stripped)
                        elif stripped.endswith('%'):
                            # Handle lines that end with just percentage
                            logger.info("[installer][emulator] Download progress: %s", stripped)
            except Exception as e:
                logger.error("[installer][emulator] Output reading error: %s", e)
            finally:
                pass  # New line after progress completes

            process.stdout.close()
            returncode = process.wait(timeout=120)
            output = "\n".join(output_lines)
            return returncode == 0, output

        primary_cmd = [
            str(avdmanager),
            f"--sdk_root={sdk_root}",
            "create",
            "avd",
            "-n",
            avd_name,
            "-k",
            system_image,
            "-d",
            device_id,
        ]
        success, output = _run_create_command(primary_cmd)
        if success:
            return True, output

        # macOS-only compatibility fallback for avdmanager builds that reject --sdk_root.
        if debug:
            logger.debug("[installer][emulator] Retrying AVD create without --sdk_root on macOS.")
        fallback_cmd = [
            str(avdmanager),
            "create",
            "avd",
            "-n",
            avd_name,
            "-k",
            system_image,
            "-d",
            device_id,
        ]
        fallback_success, fallback_output = _run_create_command(fallback_cmd)
        if fallback_success:
            return True, fallback_output
        return False, fallback_output or output
    except subprocess.TimeoutExpired:
        return False, "AVD creation timed out"
    except Exception as e:
        return False, str(e)


def _sanitize_avd_name(device_name: str) -> str:
    """
    Sanitize device name to create a valid AVD name.
    AVD names can only contain: a-z A-Z 0-9 . _ -
    
    Args:
        device_name: Original device name (e.g., "Pixel 6")
    
    Returns:
        Sanitized AVD name (e.g., "Pixel-6")
    """
    # Replace spaces with hyphens
    sanitized = device_name.replace(" ", "-")
    
    # Remove any characters that are not allowed (a-z A-Z 0-9 . _ -)
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', sanitized)
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "AVD"
    
    return sanitized


def _configure_avd_hardware(avd_name: str) -> bool:
    """
    Configure AVD hardware settings to ensure buttons work properly.
    Sets hw.keyboard=yes in config.ini so hardware buttons are functional.
    
    Args:
        avd_name: Name of the AVD
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Find AVD config directory
        # AVDs are stored in ~/.android/avd/{avd_name}.avd/ on Linux/macOS
        # or %USERPROFILE%\.android\avd\{avd_name}.avd\ on Windows
        system = platform.system()
        
        if system == "Windows":
            avd_home = os.environ.get('ANDROID_AVD_HOME')
            if not avd_home:
                user_profile = os.environ.get('USERPROFILE', os.environ.get('HOME', ''))
                avd_home = os.path.join(user_profile, '.android', 'avd')
            avd_home = os.path.expandvars(avd_home)
        else:
            # Linux/macOS
            avd_home = os.environ.get('ANDROID_AVD_HOME')
            if not avd_home:
                avd_home = os.path.join(os.path.expanduser('~'), '.android', 'avd')
        
        config_path = Path(avd_home) / f"{avd_name}.avd" / "config.ini"
        
        if not config_path.exists():
            logger.warning("[installer][emulator] AVD config file not found: %s", config_path)
            return False
        
        # Read current config
        with open(config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Modify or add hw.keyboard setting
        # hw.keyboard=yes enables hardware input so buttons work
        modified = False
        new_lines = []
        hw_keyboard_found = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('hw.keyboard='):
                # Replace existing setting
                new_lines.append('hw.keyboard=yes\n')
                hw_keyboard_found = True
                if 'no' in stripped.lower():
                    modified = True
            else:
                new_lines.append(line)
        
        # Add setting if not found
        if not hw_keyboard_found:
            # Add after other hw.* settings if any, otherwise at the end
            insert_pos = len(new_lines)
            for i, line in enumerate(new_lines):
                if line.strip().startswith('hw.') and i < len(new_lines) - 1:
                    # Check if next line doesn't start with hw.
                    if i + 1 < len(new_lines) and not new_lines[i + 1].strip().startswith('hw.'):
                        insert_pos = i + 1
                        break
            
            new_lines.insert(insert_pos, 'hw.keyboard=yes\n')
            modified = True
        
        # Write back if modified
        if modified:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            logger.info("[installer][emulator] Configured hardware settings (hw.keyboard=yes) for AVD '%s'", avd_name)
            return True
        else:
            logger.info("[installer][emulator] Hardware settings already configured for AVD '%s'", avd_name)
            return True
        
    except Exception as e:
        logger.exception("[installer][emulator] Failed to configure hardware settings for AVD '%s': %s", avd_name, e)
        traceback.print_exc()
        return False


def _get_highest_api_system_image(system_images: list[dict]) -> str | None:
    """
    Get the system image with the highest API level.
    API level is the primary priority. Uses variant/arch as tiebreaker when API levels are equal.
    
    Args:
        system_images: List of system image dictionaries with package, version, description
    
    Returns:
        System image package name (e.g., "system-images;android-36;google_apis;x86_64") or None
    """
    if not system_images:
        return None
    
    # Extract API levels - API level is the priority.
    arch_preference = _get_arch_preference_order()
    candidates = []
    for img in system_images:
        package = img.get("package", "")
        if not package.startswith("system-images;"):
            continue
        
        # Parse: system-images;android-XX;variant;arch
        parts = package.split(";")
        if len(parts) < 2:
            continue
        
        # Extract API level from android-XX
        android_part = parts[1]
        match = re.match(r'android-(\d+)', android_part)
        if not match:
            continue
        
        api_level = int(match.group(1))
        variant = parts[2] if len(parts) > 2 else ""
        arch = parts[3] if len(parts) > 3 else ""
        
        # Variant preference for tiebreaking (only used when API levels are equal).
        variant_priority = 0
        if variant == "google_apis":
            variant_priority = 3
        elif variant == "google_apis_playstore":
            variant_priority = 2
        elif variant:
            variant_priority = 1

        # Host-compatible architecture preference (important for Apple Silicon).
        if arch in arch_preference:
            arch_priority = len(arch_preference) - arch_preference.index(arch)
        else:
            arch_priority = 0
        
        candidates.append({
            "package": package,
            "api_level": api_level,
            "arch_priority": arch_priority,
            "variant_priority": variant_priority
        })
    
    if not candidates:
        return None
    
    # Sort by API level (descending), then host arch compatibility, then image variant.
    candidates.sort(key=lambda x: (x["api_level"], x["arch_priority"], x["variant_priority"]), reverse=True)
    
    # Return the highest API level (variant priority only matters if API levels are equal)
    return candidates[0]["package"]


async def create_avd_from_system_image(device_param: str) -> bool:
    """
    Create AVD from device ID and device name, using highest API level system image.
    
    Args:
        device_param: Format "install device;device_id;device_name"
                     Example: "install device;desktop_large;Large Desktop"
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Parse device parameter: "install device;device_id;device_name"
        parts = device_param.split(";")
        if len(parts) < 3:
            error_msg = f"Invalid device parameter format. Expected 'install device;device_id;device_name', got: {device_param}"
            logger.error("[installer][emulator] %s", error_msg)
            device_id = parts[1].strip() if len(parts) > 1 else "unknown"
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "package": device_id,
                    "status": "Not Found",
                    "comment": error_msg,
                }
            })
            return False
        
        device_id = parts[1].strip()
        device_name = parts[2].strip()
        
        # Sanitize device name for AVD (AVD names can only contain: a-z A-Z 0-9 . _ -)
        avd_name = _sanitize_avd_name(device_name)
        
        logger.info("[installer][emulator] Creating AVD '%s' (from device name '%s') with device ID '%s'", avd_name, device_name, device_id)
        
        # Check if Android SDK is installed
        sdk_root = _get_sdk_root()
        if sdk_root is None:
            logger.warning("[installer][emulator] Android SDK not found. ANDROID_HOME or ANDROID_SDK_ROOT not set.")
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "package": device_id,
                    "status": "not installed",
                    "comment": "Download and install Android SDK first",
                }
            })
            return False
        
        # Find required tools
        sdkmanager = _find_sdkmanager(sdk_root)
        avdmanager = _find_avdmanager(sdk_root)
        
        if not sdkmanager:
            if debug:
                logger.debug("[installer][emulator] sdkmanager not found")
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "package": device_id,
                    "status": "Not Found",
                    "comment": "sdkmanager not found. Please check Android SDK installation.",
                }
            })
            return False
        
        if not avdmanager:
            if debug:
                logger.debug("[installer][emulator] avdmanager not found")
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "package": device_id,
                    "status": "Not Found",
                    "comment": "avdmanager not found. Please check Android SDK installation.",
                }
            })
            return False
        
        # Step 0: Get available system images and select highest API level
        logger.info("[installer][emulator] Getting available system images with Android Version 16")
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "package": device_id,
                "status": "installing",
                "comment": "Finding the latest compatible Android system image",
            }
        })
        
        system_images = await get_available_system_images()
        if not system_images:
            error_msg = "No system images found. Please install Android SDK components first."
            logger.error("[installer][emulator] %s", error_msg)
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "package": device_id,
                    "status": "not installed",
                    "comment": error_msg,
                }
            })
            return False
        
        # Get highest API level system image with host-architecture-aware tiebreakers.
        system_image_name = _get_highest_api_system_image(system_images)
        if not system_image_name:
            error_msg = "Could not find a suitable system image."
            logger.error("[installer][emulator] %s", error_msg)
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "package": device_id,
                    "status": "not installed",
                    "comment": error_msg,
                }
            })
            return False
        
        logger.info("[installer][emulator] Selected system image: %s", system_image_name)
        logger.info("[installer][emulator] Creating AVD '%s' with device ID '%s' and system image '%s'", device_name, device_id, system_image_name)
        
        # Step 1: Install system image
        logger.info("[installer][emulator] Installing system image: %s", system_image_name)
        
        loop = asyncio.get_event_loop()
        if _is_windows():
            success, output = await loop.run_in_executor(
                None,
                _run_sdkmanager_install_windows,
                sdkmanager,
                sdk_root,
                system_image_name,
                loop,
                device_id
            )
        elif _is_linux():
            success, output = await loop.run_in_executor(
                None,
                _run_sdkmanager_install_linux,
                sdkmanager,
                sdk_root,
                system_image_name,
                loop,
                device_id
            )
        elif _is_darwin():
            success, output = await loop.run_in_executor(
                None,
                _run_sdkmanager_install_darwin,
                sdkmanager,
                sdk_root,
                system_image_name,
                loop,
                device_id
            )
        else:
            # Fallback to Linux for unknown platforms
            success, output = await loop.run_in_executor(
                None,
                _run_sdkmanager_install_linux,
                sdkmanager,
                sdk_root,
                system_image_name,
                loop,
                device_id
            )
        
        if not success:
            error_msg = f"Failed to install Android Version 16: {output}"
            logger.error("[installer][emulator] %s", error_msg)
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "package": device_id,
                    "status": "Not Found",
                    "comment": error_msg,
                }
            })
            return False
        
        logger.info("[installer][emulator] System image installed successfully")
        
        # Step 2: Create AVD with device_id and device_name
        logger.info("[installer][emulator] Creating AVD: %s with device ID: %s", avd_name, device_id)
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "package": device_id,
                "status": "installing",
                "comment": f"Creating AVD '{avd_name}'...",
            }
        })
        
        if _is_windows():
            success, output = await loop.run_in_executor(
                None,
                _run_avdmanager_create_windows,
                avdmanager,
                sdk_root,
                avd_name,
                system_image_name,
                device_id
            )
        elif _is_linux():
            success, output = await loop.run_in_executor(
                None,
                _run_avdmanager_create_linux,
                avdmanager,
                sdk_root,
                avd_name,
                system_image_name,
                device_id
            )
        elif _is_darwin():
            success, output = await loop.run_in_executor(
                None,
                _run_avdmanager_create_darwin,
                avdmanager,
                sdk_root,
                avd_name,
                system_image_name,
                device_id
            )
        else:
            # Fallback to Linux for unknown platforms
            success, output = await loop.run_in_executor(
                None,
                _run_avdmanager_create_linux,
                avdmanager,
                sdk_root,
                avd_name,
                system_image_name,
                device_id
            )
        
        if not success:
            error_msg = f"Failed to create AVD: {output}"
            logger.error("[installer][emulator] %s", error_msg)
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "package": device_id,
                    "status": "not installed",
                    "comment": error_msg,
                }
            })
            return False
        
        logger.info("[installer][emulator] AVD '%s' created successfully", avd_name)
        
        # Configure hardware settings so buttons work properly
        _configure_avd_hardware(avd_name)
        
        # Note: AVD list will be automatically refreshed when services_list is requested
        # in long_poll_handler.py, so no manual refresh is needed here
        
        # Send success response
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "package": device_id,
                "status": "installed",
                "comment": f"Installation of AVD '{avd_name}' completed",
            }
        })
        
        return True
        
    except ValueError as e:
        error_msg = f"Invalid device parameter: {e}"
        logger.error("[installer][emulator] %s", error_msg)
        device_name = device_param.split(";")[2].strip() if len(device_param.split(";")) > 2 else device_param
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "package": device_id,
                "status": "not installed",
                "comment": error_msg,
            }
        })
        return False
    except Exception as e:
        error_msg = f"Error creating AVD: {e}"
        logger.exception("[installer][emulator] %s", error_msg)
        traceback.print_exc()
        device_name = device_param.split(";")[2].strip() if len(device_param.split(";")) > 2 else device_param
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "package": device_id,
                "status": "not installed",
                "comment": error_msg,
            }
        })
        return False


########################################
