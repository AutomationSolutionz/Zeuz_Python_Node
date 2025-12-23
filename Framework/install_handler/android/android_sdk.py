import os
import platform
import stat
import shutil
import zipfile
import subprocess
from pathlib import Path
import httpx
from Framework.install_handler.utils import send_response
from settings import ZEUZ_NODE_DOWNLOADS_DIR


async def check_status() -> bool:
    """Check if Android SDK is installed in isolated directory (following Node.js installer pattern)."""
    print("[installer][android-sdk] Checking status...")
    
    # Simple file existence check in isolated directory (like Node.js installer)
    adb_path = get_adb_path()
    
    if adb_path.exists():
        sdk_root = _get_sdk_root()
        print(f"[installer][android-sdk] Already installed at {sdk_root}")
        await send_response({
            "action": "status",
            "data": {
                "category": "Android",
                "name": "Android SDK",
                "status": "installed",
                "comment": f"Android SDK is installed at {sdk_root}",
            }
        })
        return True
    
    # Not installed
    print("[installer][android-sdk] Not installed")
    await send_response({
        "action": "status",
        "data": {
            "category": "Android",
            "name": "Android SDK",
            "status": "not installed",
            "comment": "Install Android SDK to use it.",
        }
    })
    return False




def _get_sdk_root() -> Path:
   # Place SDK fully under ZeuZ downloads directory
   sdk_root = ZEUZ_NODE_DOWNLOADS_DIR / "android_sdk" / "sdk"
   sdk_root.mkdir(parents=True, exist_ok=True)
   return sdk_root


def get_adb_path():
    """Get adb binary path (following Node.js/Java installer pattern)."""
    sdk_root = _get_sdk_root()
    
    if platform.system() == "Windows":
        return sdk_root / "platform-tools" / "adb.exe"
    else:
        return sdk_root / "platform-tools" / "adb"


def update_android_sdk_path():
    """Add Android SDK paths to PATH and set ANDROID_HOME for the current process (following Node.js pattern)."""
    sdk_root = _get_sdk_root()
    
    # Check if SDK exists
    adb_path = get_adb_path()
    if not adb_path.exists():
        print("[installer][android-sdk] Warning: Android SDK not found for PATH update.")
        return
    
    # Set ANDROID_HOME and ANDROID_SDK_ROOT for current process
    os.environ['ANDROID_HOME'] = str(sdk_root)
    os.environ['ANDROID_SDK_ROOT'] = str(sdk_root)
    print(f"[installer][android-sdk] ANDROID_HOME set for current process: {sdk_root}")
    
    # Add SDK paths to PATH for current process (prepend so they take precedence)
    sdk_paths = [
        str(sdk_root / "platform-tools"),
        str(sdk_root / "emulator"),
        str(sdk_root / "cmdline-tools" / "latest" / "bin"),
    ]
    
    current_path = os.environ.get('PATH', '')
    for sdk_path in sdk_paths:
        if sdk_path not in current_path:
            os.environ['PATH'] = f"{sdk_path}{os.pathsep}{current_path}"
            current_path = os.environ['PATH']
            print(f"[installer][android-sdk] Added to current process PATH: {sdk_path}")
        else:
            print(f"[installer][android-sdk] Already in PATH: {sdk_path}")


def _get_cmdline_tools_url() -> str:
   version = "10406996_latest"
   system = platform.system()
   
   if system == "Windows":
       return f"https://dl.google.com/android/repository/commandlinetools-win-{version}.zip"
   elif system == "Linux":
       return f"https://dl.google.com/android/repository/commandlinetools-linux-{version}.zip"
   elif system == "Darwin":  # macOS
       return f"https://dl.google.com/android/repository/commandlinetools-mac-{version}.zip"
   else:
       raise OSError(f"Unsupported platform: {system}")




async def _download_cmdline_tools(archive_path: Path) -> bool:
   url = _get_cmdline_tools_url()
   archive_path.parent.mkdir(parents=True, exist_ok=True)


   print(f"[installer][android-sdk] Downloading Android Command Line Tools to {archive_path}...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "Android SDK",
           "status": "installing",
           "comment": "Downloading Android Command Line Tools...",
       }
   })


   try:
       async with httpx.AsyncClient(timeout=900.0) as client:
           async with client.stream("GET", url) as response:
               response.raise_for_status()
               total_size = int(response.headers.get("content-length", 0))
               downloaded = 0
               chunk = 8192
               counts = []
               with open(archive_path, "wb") as f:
                   async for data in response.aiter_bytes(chunk):
                       f.write(data)
                       downloaded += len(data)
                       if total_size > 0:
                           progress = (downloaded / total_size) * 100
                           mb_d = downloaded / (1024 * 1024)
                           mb_t = total_size / (1024 * 1024)
                           print(f"\r[installer][android-sdk] Download {progress:.1f}% ({mb_d:.1f}/{mb_t:.1f} MB)", end='', flush=True)
                           p = round(mb_d/mb_t, 1)
                           if p not in counts:
                               counts.append(p)
                               await send_response({
                                   "action": "status",
                                   "data": {
                                       "category": "Android",
                                       "name": "Android SDK",
                                       "status": "installing",
                                       "comment": f"Downloading Android Command Line Tools... {progress:.1f}% ({mb_d:.1f}/{mb_t:.1f} MB)",
                                   }
                               })
       print()
       print(f"[installer][android-sdk] Download complete: {archive_path}")
       return True
   except Exception as e:
       print(f"\n[installer][android-sdk] Download failed: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Android SDK",
               "status": "not installed",
               "comment": f"Android Command Line Tools download failed: {str(e)}",
           }
       })
       return False




def _find_executable(base_path: Path, base_name: str) -> Path | None:
   system = platform.system()
   if system == "Windows":
       exts = [".exe", ".bat", ".cmd", ""]
   elif system == "Linux":
       exts = ["", ".sh"]
   elif system == "Darwin":  # iOS/macOS
       exts = ["", ".sh"]
   
   if system not in ("Windows", "Linux", "Darwin"):
       raise OSError(f"Unsupported platform: {system}")
   
   for ext in exts:
       p = base_path / (base_name + ext)
       if p.is_file():
           return p
   return None




async def _extract_cmdline_tools(archive_path: Path, sdk_root: Path) -> bool:
   latest_dir = sdk_root / "cmdline-tools" / "latest"
   latest_dir.mkdir(parents=True, exist_ok=True)


   # If already extracted, clean stale zip and exit success
   sdkmanager = _find_executable(latest_dir / "bin", "sdkmanager")
   if sdkmanager:
       print("[installer][android-sdk] Command Line Tools already extracted")
       try:
           if archive_path.exists():
               archive_path.unlink()
       except Exception:
           pass
       return True


   print("[installer][android-sdk] Extracting Android Command Line Tools...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "Android SDK",
           "status": "installing",
           "comment": "Extracting Android Command Line Tools...",
       }
   })


   try:
       with zipfile.ZipFile(archive_path, 'r') as zip_ref:
           zip_ref.extractall(latest_dir)


       inner = latest_dir / "cmdline-tools"
       if inner.is_dir():
           for item in inner.iterdir():
               shutil.move(str(item), latest_dir)
           shutil.rmtree(inner, ignore_errors=True)


       # Make binaries executable on Linux and iOS/macOS
       if platform.system() == "Linux":
           bin_dir = latest_dir / "bin"
           for tool in bin_dir.glob("*"):
               if tool.is_file():
                   try:
                       tool.chmod(tool.stat().st_mode | stat.S_IEXEC)
                   except Exception:
                       pass
       elif platform.system() == "Darwin":  # iOS/macOS
           bin_dir = latest_dir / "bin"
           for tool in bin_dir.glob("*"):
               if tool.is_file():
                   try:
                       tool.chmod(tool.stat().st_mode | stat.S_IEXEC)
                   except Exception:
                       pass


       try:
           if archive_path.exists():
               archive_path.unlink()
       except Exception:
           pass


       print("[installer][android-sdk] Extraction complete")
       return True
   except Exception as e:
       print(f"[installer][android-sdk] Extraction failed: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Android SDK",
               "status": "not installed",
               "comment": f"Extraction failed: {str(e)}",
           }
       })
       return False




def _find_sdkmanager(sdk_root: Path) -> Path | None:
   return _find_executable(sdk_root / "cmdline-tools" / "latest" / "bin", "sdkmanager")




async def _run_sdkmanager(sdk_root: Path, args: list[str]) -> bool:
   try:
       sdkmanager = _find_sdkmanager(sdk_root)
       if not sdkmanager:
           print("[installer][android-sdk] sdkmanager not found")
           return False
       
       import asyncio
       import subprocess
       
       system = platform.system()
       output = None  # Initialize for later use
       
       if system == "Windows":
           # Windows - use PowerShell to pipe 'y' responses for auto-accepting licenses
           # Quote each argument individually to prevent PowerShell from interpreting semicolons
           yes_responses = ";".join(["echo y"] * 20)
           # Wrap each arg in single quotes to preserve semicolons in package names like "platforms;android-36"
           quoted_args = " ".join([f"'{arg}'" for arg in args])
           shell_cmd = f'powershell -Command "{yes_responses} | &\\"{str(sdkmanager)}\\" --sdk_root={sdk_root} {quoted_args}"'
           print(f"[installer][android-sdk] Running: sdkmanager {' '.join(args)}")
           print(f"[installer][android-sdk] This may take 5-15 minutes to download ~450MB of components...")
           
           loop = asyncio.get_event_loop()
           
           # Use Popen and print output in real-time
           def run_sdkmanager():
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
                   print(f"[installer][android-sdk] Output reading error: {e}")
               
               process.stdout.close()
               returncode = process.wait(timeout=1800)
               
               # Return last 50 lines for debugging
               return returncode, "\n".join(output_lines[-50:]) if output_lines else ""
           
           returncode, output = await loop.run_in_executor(None, run_sdkmanager)
           
           class Result:
               pass
           result = Result()
           result.returncode = returncode
       elif system == "Linux":
           # Linux can execute directly
           cmd = [str(sdkmanager), f"--sdk_root={sdk_root}"] + args
           print(f"[installer][android-sdk] Running: {' '.join(cmd)}")
           
           loop = asyncio.get_event_loop()
           result = await loop.run_in_executor(
               None,
               lambda: subprocess.run(
                   cmd,
                   capture_output=True,
                   text=True,
                   timeout=1800  # 30 minutes timeout
               )
           )
           output = (result.stdout or "") + (result.stderr or "")
       elif system == "Darwin":
           # macOS can execute directly
           cmd = [str(sdkmanager), f"--sdk_root={sdk_root}"] + args
           print(f"[installer][android-sdk] Running: {' '.join(cmd)}")
           
           loop = asyncio.get_event_loop()
           result = await loop.run_in_executor(
               None,
               lambda: subprocess.run(
                   cmd,
                   capture_output=True,
                   text=True,
                   timeout=1800  # 30 minutes timeout
               )
           )
           output = (result.stdout or "") + (result.stderr or "")
       else:
           print(f"[installer][android-sdk] Unsupported platform: {system}")
           return False
       
       if result.returncode != 0:
           print(f"[installer][android-sdk] sdkmanager failed (returncode={result.returncode})")
           if output:
               print(f"[installer][android-sdk] Last output:\n{output}")
           return False
       
       print(f"[installer][android-sdk] sdkmanager completed successfully")
       if output:
           print(f"[installer][android-sdk] Final output:\n{output[-500:]}")  # Last 500 chars
       return True
   except subprocess.TimeoutExpired:
       print("[installer][android-sdk] sdkmanager timed out after 30 minutes")
       return False
   except Exception as e:
       print(f"[installer][android-sdk] sdkmanager error: {e}")
       import traceback
       traceback.print_exc()
       return False


async def _accept_licenses(sdk_root: Path) -> bool:
   """Accept Android SDK licenses by piping 'yes' responses"""
   try:
       sdkmanager = _find_sdkmanager(sdk_root)
       if not sdkmanager:
           print("[installer][android-sdk] sdkmanager not found")
           return False
       
       import asyncio
       import subprocess
       
       cmd = [str(sdkmanager), f"--sdk_root={sdk_root}", "--licenses"]
       print(f"[installer][android-sdk] Accepting licenses: {' '.join(cmd)}")
       
       if platform.system() == "Windows":
           # On Windows, use PowerShell to pipe 'y' responses
           # Multiple 'y' responses to answer all license prompts
           yes_responses = ";".join(["echo y"] * 20)
           shell_cmd = f'powershell -Command "{yes_responses} | &\\"{str(sdkmanager)}\\" --sdk_root={sdk_root} --licenses"'
           
           loop = asyncio.get_event_loop()
           result = await loop.run_in_executor(
               None,
               lambda: subprocess.run(
                   shell_cmd,
                   shell=True,
                   capture_output=True,
                   text=True
               )
           )
           output = result.stdout + result.stderr
           returncode = result.returncode
       elif platform.system() == "Linux":
           # On Linux, use shell to pipe 'yes' command via subprocess.run in executor
           shell_cmd = f"yes | {str(sdkmanager)} --sdk_root={sdk_root} --licenses"
           loop = asyncio.get_event_loop()
           result = await loop.run_in_executor(
               None,
               lambda: subprocess.run(
                   shell_cmd,
                   shell=True,
                   capture_output=True,
                   text=True
               )
           )
           output = result.stdout + result.stderr
           returncode = result.returncode
       elif platform.system() == "Darwin":  # iOS/macOS
           # On iOS/macOS, use shell to pipe 'yes' command via subprocess.run in executor
           shell_cmd = f"yes | {str(sdkmanager)} --sdk_root={sdk_root} --licenses"
           loop = asyncio.get_event_loop()
           result = await loop.run_in_executor(
               None,
               lambda: subprocess.run(
                   shell_cmd,
                   shell=True,
                   capture_output=True,
                   text=True
               )
           )
           output = result.stdout + result.stderr
           returncode = result.returncode
       
       if returncode != 0:
           print(f"[installer][android-sdk] License acceptance failed: {output}")
           return False
       print("[installer][android-sdk] Licenses accepted successfully")
       return True
   except Exception as e:
       print(f"[installer][android-sdk] License acceptance error: {e}")
       import traceback
       traceback.print_exc()
       return False




async def install() -> bool:
   print("[installer][android-sdk] Installing...")
   
   sdk_root = _get_sdk_root()


   # Prepare download path under ZeuZ downloads dir
   download_dir = ZEUZ_NODE_DOWNLOADS_DIR / "android_sdk"
   archive_path = download_dir / "commandlinetools.zip"


   ok = await _download_cmdline_tools(archive_path)
   if not ok:
       return False


   ok = await _extract_cmdline_tools(archive_path, sdk_root)
   if not ok:
       return False


   # Accept licenses
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "Android SDK",
           "status": "installing",
           "comment": "Accepting Android SDK licenses...",
       }
   })
   if not await _accept_licenses(sdk_root):
       print("[installer][android-sdk] License acceptance failed")
       # Continue; some environments prompt-less acceptance may not be required


   # Install core components
   core_components = [
       "platform-tools",
       "emulator",
       # A recent platform and build-tools; adjust if needed
       "platforms;android-36",
       "build-tools;34.0.0",
   ]
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "Android SDK",
           "status": "installing",
           "comment": "Installing SDK components (platform-tools, emulator, platforms, build-tools)...",
       }
   })
   if not await _run_sdkmanager(sdk_root, core_components):
       print("[installer][android-sdk] Failed installing one or more SDK components")
       return False


   print(f"[installer][android-sdk] Installation successful at {sdk_root}")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "Android SDK",
           "status": "installed",
           "comment": f"Android SDK installed at {sdk_root}",
       }
   })
   return True