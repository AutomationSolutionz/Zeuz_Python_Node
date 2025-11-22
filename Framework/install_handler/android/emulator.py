import os
import platform
import subprocess
import asyncio
import re
import random
from pathlib import Path
from settings import ZEUZ_NODE_DOWNLOADS_DIR
from Framework.install_handler.utils import send_response


def _get_sdk_root() -> Path | None:
    """Get the Android SDK root path, following the pattern from android_sdk.py"""
    # First try environment variable
    android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if android_home and os.path.exists(android_home):
        return Path(android_home)
    
    # Fallback to ZeuZ downloads directory
    sdk_root = ZEUZ_NODE_DOWNLOADS_DIR / "android_sdk" / "sdk"
    if sdk_root.exists():
        return sdk_root
    
    # If neither exists, return None (SDK not installed)
    return None


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


def get_emulator_command():
    """
    Returns the correct emulator executable path depending on OS.
    Assumes ANDROID_HOME or ANDROID_SDK_ROOT is already set.
    """
    sdk_root = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not sdk_root:
        raise EnvironmentError("ANDROID_HOME or ANDROID_SDK_ROOT is not set.")

    system = platform.system()

    if system == "Windows":
        return os.path.join(sdk_root, "emulator", "emulator.exe")

    elif system == "Darwin":  # macOS
        return os.path.join(sdk_root, "emulator", "emulator")

    elif system == "Linux":
        return os.path.join(sdk_root, "emulator", "emulator")

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
            print("[installer][emulator] Android SDK not found. ANDROID_HOME or ANDROID_SDK_ROOT not set.")
            return []
        
        avdmanager = _find_avdmanager(sdk_root)
        
        if not avdmanager:
            print("[installer][emulator] avdmanager not found")
            return []
        
        # Run avdmanager list avd command using async executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                [str(avdmanager), "list", "avd"],
                capture_output=True,
                text=True,
                timeout=30
            )
        )
        
        if result.returncode != 0:
            print(f"[installer][emulator] avdmanager list avd failed: {result.stderr}")
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
        print("[installer][emulator] avdmanager list avd timed out")
        return []
    except Exception as e:
        print(f"[installer][emulator] Error listing AVDs: {e}")
        import traceback
        traceback.print_exc()
        return []


async def launch_avd(avd_name: str) -> bool:
    """
    Launch AVD using emulator command determined by OS.
    Non-blocking - the emulator starts in the background.
    Sends response to server on success or failure.
    """
    try:
        emulator_path = get_emulator_command()

        # Launch emulator in background using Popen (non-blocking)
        # Popen returns immediately, so we can call it directly without blocking
        process = subprocess.Popen(
            [emulator_path, "-avd", avd_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # Detach from parent process
        )
        
        # Popen returns immediately - the process runs in background
        print(f"[installer][emulator] Launching AVD: {avd_name}... (PID: {process.pid})")
        
        # Send success response to server
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": avd_name,
                "status": "installed",
                "comment": f"Emulator {avd_name} is launching (PID: {process.pid})",
            }
        })
        return True

    except FileNotFoundError:
        error_msg = f"Emulator executable not found"
        print(f"[installer][emulator] {error_msg}")
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": avd_name,
                "status": "not installed",
                "comment": f"Failed to launch {avd_name}: {error_msg}",
            }
        })
        return False
    except Exception as e:
        error_msg = f"Failed to launch AVD {avd_name}: {e}"
        print(f"[installer][emulator] {error_msg}")
        import traceback
        traceback.print_exc()
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
                print(f"[installer][emulator] sdkmanager --list failed: {result.stderr}")
                return ""
        
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"[installer][emulator] sdkmanager --list failed: {result.stderr}")
            return ""
    except subprocess.TimeoutExpired:
        print("[installer][emulator] sdkmanager --list timed out")
        return ""
    except Exception as e:
        print(f"[installer][emulator] Error running sdkmanager --list: {e}")
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
                "description": description
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
            print("[installer][emulator] Android SDK not found. ANDROID_HOME or ANDROID_SDK_ROOT not set.")
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
            print("[installer][emulator] sdkmanager not found")
            return []
        
        # Check platform support
        if not (_is_windows() or _is_linux() or _is_darwin()):
            print(f"[installer][emulator] Unsupported platform: {platform.system()}")
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
            print("[installer][emulator] sdkmanager --list returned empty output")
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
        
        print(f"[installer][emulator] Found {len(system_images)} available system images")
        return system_images
    
    except subprocess.TimeoutExpired:
        print("[installer][emulator] sdkmanager --list timed out")
        return []
    except Exception as e:
        print(f"[installer][emulator] Error getting available system images: {e}")
        import traceback
        traceback.print_exc()
        return []


async def android_emulator_install():
    """
    Get available system images when install button is clicked.
    Returns list of available system images for emulator installation.
    """
    print("[installer][emulator] Getting available system images...")
    
    try:
        # Check if Android SDK is installed first
        sdk_root = _get_sdk_root()
        if sdk_root is None:
            print("[installer][emulator] Android SDK not found")
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "name": "System Images",
                    "status": "not installed",
                    "comment": "Download and install Android SDK first",
                    "system_images": []
                }
            })
            return False
        
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": "System Images",
                "status": "installing",
                "comment": "Fetching available system images...",
            }
        })
        
        # Get available system images
        system_images = await get_available_system_images()
        
        # if not system_images:
        #     print("[installer][emulator] No system images found")
        #     await send_response({
        #         "action": "status",
        #         "data": {
        #             "category": "AndroidEmulator",
        #             "name": "System Images",
        #             "status": "not installed",
        #             "comment": "No system images available. Please make sure you have installed the ANDROID SDK components",
        #             "system_images": [],
        #         }
        #     })
        #     return True
        
        print("here")
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": "System Images",
                "status": "installed",
                "comment": f"Available system images ({len(system_images)} total)",
                "system_images": system_images,  # Send the full list with details
            }
        })
        return True
        
    except Exception as e:
        print(f"[installer][emulator] Error getting system images: {e}")
        import traceback
        traceback.print_exc()
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": "System Images",
                "status": "not installed",
                "comment": f"Error getting system images: {str(e)}",
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
        
        result = subprocess.run(
            [str(avdmanager), "list", "avd"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
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


def _run_sdkmanager_install_windows(sdkmanager: Path, sdk_root: Path, system_image: str) -> tuple[bool, str]:
    """Install system image on Windows with real-time output"""
    try:
        # Use PowerShell to handle the command properly and auto-accept licenses
        # This approach pipes 'y' responses to automatically accept licenses
        yes_responses = ";".join(["echo y"] * 20)
        quoted_image = f"'{system_image}'"
        shell_cmd = f'powershell -Command "{yes_responses} | &\\"{str(sdkmanager)}\\" --sdk_root={sdk_root} {quoted_image}"'
        
        print(f"[installer][emulator] Running: sdkmanager --sdk_root={sdk_root} {system_image}")
        print(f"[installer][emulator] This may take 10-30 minutes to download system image...")
        
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
        
        # Print output in real-time as it comes
        output_lines = []
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.rstrip())  # Print immediately
                    output_lines.append(line.strip())
        except Exception as e:
            print(f"[installer][emulator] Output reading error: {e}")
        
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


def _run_sdkmanager_install_linux(sdkmanager: Path, sdk_root: Path, system_image: str) -> tuple[bool, str]:
    """Install system image on Linux with real-time output"""
    try:
        print(f"[installer][emulator] Running: sdkmanager --sdk_root={sdk_root} {system_image}")
        print(f"[installer][emulator] This may take 10-30 minutes to download system image...")
        
        process = subprocess.Popen(
            [str(sdkmanager), f"--sdk_root={sdk_root}", system_image],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Print output in real-time as it comes
        output_lines = []
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.rstrip())  # Print immediately
                    output_lines.append(line.strip())
        except Exception as e:
            print(f"[installer][emulator] Output reading error: {e}")
        
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


def _run_sdkmanager_install_darwin(sdkmanager: Path, sdk_root: Path, system_image: str) -> tuple[bool, str]:
    """Install system image on macOS with real-time output"""
    try:
        print(f"[installer][emulator] Running: sdkmanager --sdk_root={sdk_root} {system_image}")
        print(f"[installer][emulator] This may take 10-30 minutes to download system image...")
        
        process = subprocess.Popen(
            [str(sdkmanager), f"--sdk_root={sdk_root}", system_image],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Print output in real-time as it comes
        output_lines = []
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.rstrip())  # Print immediately
                    output_lines.append(line.strip())
        except Exception as e:
            print(f"[installer][emulator] Output reading error: {e}")
        
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


def _run_avdmanager_create_windows(avdmanager: Path, sdk_root: Path, avd_name: str, system_image: str) -> tuple[bool, str]:
    """Create AVD on Windows with real-time output"""
    try:
        # Create AVD: avdmanager create avd -n {avd_name} -k {system_image}
        # Answer "no" to custom hardware profile prompt
        process = subprocess.Popen(
            [str(avdmanager), "create", "avd", "-n", avd_name, "-k", system_image],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Send "no" to custom hardware profile prompt
        process.stdin.write("no\n")
        process.stdin.close()
        
        # Print output in real-time as it comes
        output_lines = []
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.rstrip())  # Print immediately
                    output_lines.append(line.strip())
        except Exception as e:
            print(f"[installer][emulator] Output reading error: {e}")
        
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


def _run_avdmanager_create_linux(avdmanager: Path, sdk_root: Path, avd_name: str, system_image: str) -> tuple[bool, str]:
    """Create AVD on Linux with real-time output"""
    try:
        # Create AVD: avdmanager create avd -n {avd_name} -k {system_image}
        # Answer "no" to custom hardware profile prompt
        process = subprocess.Popen(
            [str(avdmanager), "create", "avd", "-n", avd_name, "-k", system_image],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Send "no" to custom hardware profile prompt
        process.stdin.write("no\n")
        process.stdin.close()
        
        # Print output in real-time as it comes
        output_lines = []
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.rstrip())  # Print immediately
                    output_lines.append(line.strip())
        except Exception as e:
            print(f"[installer][emulator] Output reading error: {e}")
        
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


def _run_avdmanager_create_darwin(avdmanager: Path, sdk_root: Path, avd_name: str, system_image: str) -> tuple[bool, str]:
    """Create AVD on macOS with real-time output"""
    try:
        # Create AVD: avdmanager create avd -n {avd_name} -k {system_image}
        # Answer "no" to custom hardware profile prompt
        process = subprocess.Popen(
            [str(avdmanager), "create", "avd", "-n", avd_name, "-k", system_image],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Send "no" to custom hardware profile prompt
        process.stdin.write("no\n")
        process.stdin.close()
        
        # Print output in real-time as it comes
        output_lines = []
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.rstrip())  # Print immediately
                    output_lines.append(line.strip())
        except Exception as e:
            print(f"[installer][emulator] Output reading error: {e}")
        
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


async def create_avd_from_system_image(system_image_name: str) -> bool:
    """
    Download system image and create AVD with dynamic name.
    
    Args:
        system_image_name: System image package name (e.g., "system-images;android-36-ext18;google_apis;arm64-v8")
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if Android SDK is installed
        sdk_root = _get_sdk_root()
        if sdk_root is None:
            print("[installer][emulator] Android SDK not found. ANDROID_HOME or ANDROID_SDK_ROOT not set.")
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "name": system_image_name,
                    "status": "not installed",
                    "comment": "Download and install Android SDK first",
                }
            })
            return False
        
        # Find required tools
        sdkmanager = _find_sdkmanager(sdk_root)
        avdmanager = _find_avdmanager(sdk_root)
        
        if not sdkmanager:
            print("[installer][emulator] sdkmanager not found")
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "name": system_image_name,
                    "status": "not installed",
                    "comment": "sdkmanager not found. Please check Android SDK installation.",
                }
            })
            return False
        
        if not avdmanager:
            print("[installer][emulator] avdmanager not found")
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "name": system_image_name,
                    "status": "not installed",
                    "comment": "avdmanager not found. Please check Android SDK installation.",
                }
            })
            return False
        
        # Extract Android version and generate AVD name
        android_version = _extract_android_version(system_image_name)
        existing_avds = _get_existing_avd_names()
        avd_name = _generate_avd_name(android_version, existing_avds)
        
        print(f"[installer][emulator] Creating AVD '{avd_name}' from system image '{system_image_name}'")
        
        # Step 1: Install system image
        print(f"[installer][emulator] Installing system image: {system_image_name}")
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": system_image_name,
                "status": "installing",
                "comment": "Download started. Check the terminal on which ZeuZ Node is open for updates",
            }
        })
        
        loop = asyncio.get_event_loop()
        if _is_windows():
            success, output = await loop.run_in_executor(
                None,
                _run_sdkmanager_install_windows,
                sdkmanager,
                sdk_root,
                system_image_name
            )
        elif _is_linux():
            success, output = await loop.run_in_executor(
                None,
                _run_sdkmanager_install_linux,
                sdkmanager,
                sdk_root,
                system_image_name
            )
        elif _is_darwin():
            success, output = await loop.run_in_executor(
                None,
                _run_sdkmanager_install_darwin,
                sdkmanager,
                sdk_root,
                system_image_name
            )
        else:
            # Fallback to Linux for unknown platforms
            success, output = await loop.run_in_executor(
                None,
                _run_sdkmanager_install_linux,
                sdkmanager,
                sdk_root,
                system_image_name
            )
        
        if not success:
            error_msg = f"Failed to install system image: {output}"
            print(f"[installer][emulator] {error_msg}")
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "name": system_image_name,
                    "status": "not installed",
                    "comment": error_msg,
                }
            })
            return False
        
        print(f"[installer][emulator] System image installed successfully")
        
        # Step 2: Create AVD
        print(f"[installer][emulator] Creating AVD: {avd_name}")
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": system_image_name,
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
                system_image_name
            )
        elif _is_linux():
            success, output = await loop.run_in_executor(
                None,
                _run_avdmanager_create_linux,
                avdmanager,
                sdk_root,
                avd_name,
                system_image_name
            )
        elif _is_darwin():
            success, output = await loop.run_in_executor(
                None,
                _run_avdmanager_create_darwin,
                avdmanager,
                sdk_root,
                avd_name,
                system_image_name
            )
        else:
            # Fallback to Linux for unknown platforms
            success, output = await loop.run_in_executor(
                None,
                _run_avdmanager_create_linux,
                avdmanager,
                sdk_root,
                avd_name,
                system_image_name
            )
        
        if not success:
            error_msg = f"Failed to create AVD: {output}"
            print(f"[installer][emulator] {error_msg}")
            await send_response({
                "action": "status",
                "data": {
                    "category": "AndroidEmulator",
                    "name": system_image_name,
                    "status": "not installed",
                    "comment": error_msg,
                }
            })
            return False
        
        print(f"[installer][emulator] AVD '{avd_name}' created successfully")
        
        # Refresh the AVD list so the new AVD appears without restarting
        try:
            from Framework.install_handler import route
            await route.refresh_avd_list()
        except Exception as e:
            print(f"[installer][emulator] Warning: Could not refresh AVD list: {e}")
        
        # Send success response
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": system_image_name,
                "status": "installed",
                "comment": f"Installation of {avd_name} completed",
            }
        })
        
        return True
        
    except ValueError as e:
        error_msg = f"Invalid system image name: {e}"
        print(f"[installer][emulator] {error_msg}")
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": system_image_name,
                "status": "not installed",
                "comment": error_msg,
            }
        })
        return False
    except Exception as e:
        error_msg = f"Error creating AVD: {e}"
        print(f"[installer][emulator] {error_msg}")
        import traceback
        traceback.print_exc()
        await send_response({
            "action": "status",
            "data": {
                "category": "AndroidEmulator",
                "name": system_image_name,
                "status": "not installed",
                "comment": error_msg,
            }
        })
        return False