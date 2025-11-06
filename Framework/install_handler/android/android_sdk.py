import os
import platform
import stat
import shutil
import zipfile
from pathlib import Path
import httpx
from Framework.install_handler.utils import send_response
from settings import ZEUZ_NODE_DOWNLOADS_DIR


async def check_status() -> bool:
   """Check if ANDROID_HOME environment variable is set and valid."""
   print("[installer][android-sdk] Checking status...")
  
   try:
       # Check if ANDROID_HOME is set
       android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')


       print(android_home)
       if not android_home:
           print("[installer][android-sdk] Not installed (ANDROID_HOME not set)")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Android SDK",
                   "status": "not installed",
                   "comment": "Install Android SDK and set ANDROID_HOME environment variable.",
               }
           })
           return False
      
       # Check if the path exists
       if not os.path.exists(android_home):
           print(f"[installer][android-sdk] Not installed (ANDROID_HOME path does not exist: {android_home})")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Android SDK",
                   "status": "not installed",
                   "comment": f"ANDROID_HOME is set but path does not exist: {android_home}",
               }
           })
           return False
      
       print(f"[installer][android-sdk] Already installed")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Android SDK",
               "status": "installed",
               "comment": f"Android SDK is installed at {android_home}",
           }
       })
       return True
   except Exception as e:
       print(f"[installer][android-sdk] Error checking status: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Android SDK",
               "status": "not installed",
               "comment": "Unable to check Android SDK status.",
           }
       })
       return False




def _get_sdk_root() -> Path:
   # Place SDK fully under ZeuZ downloads directory
   sdk_root = ZEUZ_NODE_DOWNLOADS_DIR / "android_sdk" / "sdk"
   sdk_root.mkdir(parents=True, exist_ok=True)
   return sdk_root




def _get_cmdline_tools_url() -> str:
   version = "10406996_latest"
   if platform.system() == "Windows":
       return f"https://dl.google.com/android/repository/commandlinetools-win-{version}.zip"
   elif platform.system() == "Linux":
       return f"https://dl.google.com/android/repository/commandlinetools-linux-{version}.zip"
   elif platform.system() == "Darwin":  # iOS/macOS
       return f"https://dl.google.com/android/repository/commandlinetools-mac-{version}.zip"




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




async def _set_env_vars(sdk_root: Path) -> None:
   print("[installer][android-sdk] Setting environment variables...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "Android SDK",
           "status": "installing",
           "comment": "Setting ANDROID_HOME and PATH...",
       }
   })


   env_paths = [
       str(sdk_root / "platform-tools"),
       str(sdk_root / "emulator"),
       str(sdk_root / "cmdline-tools" / "latest" / "bin"),
   ]


   if platform.system() == "Windows":
       try:
           import winreg
           with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                              r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                              0, winreg.KEY_ALL_ACCESS) as key:
               winreg.SetValueEx(key, "ANDROID_HOME", 0, winreg.REG_EXPAND_SZ, str(sdk_root))
           with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                              r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                              0, winreg.KEY_ALL_ACCESS) as key:
               current_path, _ = winreg.QueryValueEx(key, "Path")
               parts = current_path.split(";")
               updated = False
               for p in env_paths:
                   if p not in parts:
                       parts.append(p)
                       updated = True
               if updated:
                   winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, ";".join(parts))
       except Exception as e:
           print(f"[installer][android-sdk] Windows env update failed (continuing for user session): {e}")
   elif platform.system() == "Linux":
       # Linux - update shell configuration files
       user_home = Path.home()
       shell_configs = [
           user_home / ".bashrc",
           user_home / ".zshrc",
           user_home / ".profile"
       ]
       
       export_lines = [
           f"export ANDROID_HOME={sdk_root}",
           f"export ANDROID_SDK_ROOT={sdk_root}",
           f"export PATH={':'.join(env_paths)}:$PATH"
       ]
       
       updated = False
       for config_file in shell_configs:
           if config_file.exists():
               try:
                   with open(config_file, 'r') as f:
                       content = f.read()
                   needs_update = any(export not in content for export in export_lines)
                   
                   if needs_update:
                       with open(config_file, 'a') as f:
                           f.write("\n# Android SDK environment variables\n" + "\n".join(export_lines) + "\n")
                       print(f"[installer][android-sdk] Updated {config_file} with Android SDK paths")
                       updated = True
               except Exception as e:
                   print(f"[installer][android-sdk] Failed to update {config_file}: {e}")
       
       if updated:
           print("[!] Please restart your terminal or run 'source ~/.bashrc' (or your shell config)")
   elif platform.system() == "Darwin":  # iOS/macOS
       # iOS/macOS - update shell configuration files
       user_home = Path.home()
       shell_configs = [
           user_home / ".bash_profile",
           user_home / ".zshrc",
           user_home / ".profile"
       ]
       
       export_lines = [
           f"export ANDROID_HOME={sdk_root}",
           f"export ANDROID_SDK_ROOT={sdk_root}",
           f"export PATH={':'.join(env_paths)}:$PATH"
       ]
       
       updated = False
       for config_file in shell_configs:
           if config_file.exists():
               try:
                   with open(config_file, 'r') as f:
                       content = f.read()
                   needs_update = any(export not in content for export in export_lines)
                   
                   if needs_update:
                       with open(config_file, 'a') as f:
                           f.write("\n# Android SDK environment variables\n" + "\n".join(export_lines) + "\n")
                       print(f"[installer][android-sdk] Updated {config_file} with Android SDK paths")
                       updated = True
               except Exception as e:
                   print(f"[installer][android-sdk] Failed to update {config_file}: {e}")
       
       if updated:
           print("[!] Please restart your terminal or run 'source ~/.zshrc' (or your shell config)")


   # Always set for current session (works on all platforms)
   os.environ['ANDROID_HOME'] = str(sdk_root)
   os.environ['ANDROID_SDK_ROOT'] = str(sdk_root)
   current_path = os.environ.get('PATH', '')
   
   if platform.system() == "Windows":
       sep = ';'
   elif platform.system() == "Linux":
       sep = ':'
   elif platform.system() == "Darwin":  # iOS/macOS
       sep = ':'
   
   # Prepend to PATH to ensure sdk tools are found first
   for p in reversed(env_paths):
       if p not in current_path:
           current_path = f"{p}{sep}{current_path}" if current_path else p
   os.environ['PATH'] = current_path




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
       
       cmd = [str(sdkmanager), f"--sdk_root={sdk_root}"] + args
       print(f"[installer][android-sdk] Running: {' '.join(cmd)}")
       
       # Use subprocess.run in executor to avoid asyncio subprocess issues
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
       
       if result.returncode != 0:
           print(f"[installer][android-sdk] sdkmanager failed (returncode={result.returncode}): {output[:500]}")
           return False
       
       if output:
           print(f"[installer][android-sdk] sdkmanager output: {output[:200]}")
       
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
           # On Windows, pipe multiple "yes" responses
           # SDK typically asks for ~10+ license acceptances
           yes_input = ("y\n" * 20).encode()
           process = await asyncio.create_subprocess_exec(
               *cmd,
               stdin=asyncio.subprocess.PIPE,
               stdout=asyncio.subprocess.PIPE,
               stderr=asyncio.subprocess.STDOUT
           )
           stdout, _ = await process.communicate(input=yes_input)
           output = stdout.decode('utf-8', errors='ignore') if stdout else ""
           returncode = process.returncode
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


   # If already installed (has sdkmanager), short-circuit
   latest_dir = sdk_root / "cmdline-tools" / "latest"
   if _find_executable(latest_dir / "bin", "sdkmanager"):
       print("[installer][android-sdk] SDK already installed")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Android SDK",
               "status": "installed",
               "comment": f"Android SDK available at {sdk_root}",
           }
       })
       return True


   # Prepare download path under ZeuZ downloads dir
   download_dir = ZEUZ_NODE_DOWNLOADS_DIR / "android_sdk"
   archive_path = download_dir / "commandlinetools.zip"


   ok = await _download_cmdline_tools(archive_path)
   if not ok:
       return False


   ok = await _extract_cmdline_tools(archive_path, sdk_root)
   if not ok:
       return False


   await _set_env_vars(sdk_root)


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
