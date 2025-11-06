import os
import platform
import subprocess
import asyncio
from pathlib import Path
from settings import ZEUZ_NODE_DOWNLOADS_DIR


def _get_sdk_root() -> Path:
    """Get the Android SDK root path, following the pattern from android_sdk.py"""
    # First try environment variable
    android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if android_home and os.path.exists(android_home):
        return Path(android_home)
    
    # Fallback to ZeuZ downloads directory
    sdk_root = ZEUZ_NODE_DOWNLOADS_DIR / "android_sdk" / "sdk"
    return sdk_root


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
                    "status_function": lambda avd=name: launch_avd(avd)
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
        return True

    except Exception as e:
        print(f"[installer][emulator] Failed to launch AVD {avd_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def android_emulator_install():
    
    print("[installer][emulator] Installing Android Emulator...")