import subprocess
import platform
import shutil
import httpx
import asyncio
import os
import json
import tarfile
import re
from pathlib import Path
from Framework.install_handler.install_log_config import get_logger
from Framework.install_handler.utils import send_response
from settings import ZEUZ_NODE_DOWNLOADS_DIR

logger = get_logger()


def _is_windows():
   """Check if running on Windows"""
   return platform.system() == 'Windows'


def _is_linux():
   """Check if running on Linux"""
   return platform.system() == 'Linux'


def _is_darwin():
   """Check if running on macOS"""
   return platform.system() == 'Darwin'


def _get_linux_package_manager():
   """Detect Linux package manager"""
   if shutil.which("apt-get"):
       return "apt"
   elif shutil.which("dnf"):
       return "dnf"
   elif shutil.which("yum"):
       return "yum"
   elif shutil.which("pacman"):
       return "pacman"
   elif shutil.which("zypper"):
       return "zypper"
   elif shutil.which("apk"):
       return "apk"
   elif shutil.which("emerge"):
       return "emerge"
   elif shutil.which("nix"):
       return "nix"
   return None


async def check_status() -> bool:
   """Check if Mozilla Firefox is installed."""
   logger.info("[installer][web-mozilla] Checking status...")
  
   try:
       result = None
       
       if platform.system() == "Windows":
           # Windows: Check registry for Firefox installation
           ps_command = '''
           $firefox = Get-ItemProperty "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*",
                                        "HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*" |
                      Where-Object { $_.DisplayName -like "*Firefox*" } |
                      Select-Object -First 1
           if ($firefox) {
               @{
                   InstallLocation = $firefox.InstallLocation
                   DisplayVersion = $firefox.DisplayVersion
                   DisplayName = $firefox.DisplayName
               } | ConvertTo-Json
           }
           '''
           result = subprocess.run(
               ["powershell", "-Command", ps_command],
               capture_output=True,
               text=True,
               check=False
           )
           
           # If registry check found Firefox, parse JSON and get version
           if result.returncode == 0 and result.stdout.strip():
               try:
                   firefox_info = json.loads(result.stdout.strip())
                   install_location = firefox_info.get('InstallLocation', '')
                   display_version = firefox_info.get('DisplayVersion', '')
                   
                   # Try to get version from firefox.exe if we have install location
                   version_text = None
                   if install_location and install_location != '':
                       firefox_exe = Path(install_location) / "firefox.exe"
                       if firefox_exe.exists():
                           version_result = subprocess.run(
                               [str(firefox_exe), "--version"],
                               capture_output=True,
                               text=True,
                               check=False
                           )
                           if version_result.returncode == 0:
                               version_text = (version_result.stdout or version_result.stderr).strip()
                   
                   # Use DisplayVersion from registry if we couldn't get it from exe
                   if not version_text and display_version:
                       version_text = f"Mozilla Firefox {display_version}"
                   elif not version_text:
                       # Found in registry but couldn't get version
                       version_text = "Mozilla Firefox"
                   
                   if version_text:
                       result.stdout = version_text
                       result.returncode = 0
                   else:
                       result.returncode = 1
               except (json.JSONDecodeError, KeyError, Exception):
                   # If JSON parsing fails, Firefox is still installed (found in registry)
                   result.stdout = "Mozilla Firefox"
                   result.returncode = 0
           else:
               # Not found in registry, set returncode to indicate not installed
               result.returncode = 1
       elif platform.system() == "Linux":
           # Linux: try firefox command
           result = subprocess.run(
               ["firefox", "--version"],
               capture_output=True,
               text=True,
               check=False
           )
           
           # If not found, try using shutil.which
           if result.returncode != 0:
               firefox_path = shutil.which("firefox")
               if firefox_path:
                   result = subprocess.run(
                       [firefox_path, "--version"],
                       capture_output=True,
                       text=True,
                       check=False
                   )
       elif platform.system() == "Darwin":
           # macOS: try firefox command
           result = subprocess.run(
               ["firefox", "--version"],
               capture_output=True,
               text=True,
               check=False
           )
           
           # If not found, try using shutil.which
           if result.returncode != 0:
               firefox_path = shutil.which("firefox")
               if firefox_path:
                   result = subprocess.run(
                       [firefox_path, "--version"],
                       capture_output=True,
                       text=True,
                       check=False
                   )
       else:
           # Default fallback for other platforms
           result = subprocess.run(
               ["firefox", "--version"],
               capture_output=True,
               text=True,
               check=False
           )

       if result.returncode != 0:
           logger.info("[installer][web-mozilla] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Web",
                   "name": "Mozilla",
                   "status": "not installed",
                   "comment": "Install Mozilla Firefox to use it.",
               }
           })
           return False
      
       # Firefox version output is typically in stdout or stderr
       version_text = (result.stdout or result.stderr).strip()
       if not version_text:
           logger.info("[installer][web-mozilla] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Web",
                   "name": "Mozilla",
                   "status": "not installed",
                   "comment": "Install Mozilla Firefox to use it.",
               }
           })
           return False
      
       logger.info("[installer][web-mozilla] Already installed")
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "installed",
               "comment": f"Mozilla Firefox is installed version: {version_text[:50]}",
           }
       })
       return True
   except (FileNotFoundError, OSError):
       # Firefox command not found - Firefox is not installed
       logger.info("[installer][web-mozilla] Not installed (firefox not found)")
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "not installed",
               "comment": "Install Mozilla Firefox to use it.",
           }
       })
       return False
   except Exception as e:
       logger.error("[installer][web-mozilla] Error checking status: %s", e)
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "not installed",
               "comment": "Unable to check Mozilla Firefox status.",
           }
       })
       return False


async def _download_firefox_installer():
   """Download Firefox installer based on platform"""
   logger.info("[installer][web-mozilla] Downloading Mozilla Firefox installer...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Web",
           "name": "Mozilla",
           "status": "installing",
           "comment": "Downloading Mozilla Firefox installer...",
       }
   })
   
   download_dir = ZEUZ_NODE_DOWNLOADS_DIR / "firefox"
   download_dir.mkdir(parents=True, exist_ok=True)
   
   system = platform.system().lower()
   arch = platform.machine().lower()
   
   try:
       if system == "windows":
           # Windows: Download .exe installer
           # Firefox provides direct download links for Windows
           installer_url = "https://download.mozilla.org/?product=firefox-latest&os=win64&lang=en-US"
           # The actual filename will be determined from the download (may include version number)
           # We'll find any .exe file in the download directory after download
           installer_path = download_dir / "FirefoxSetup.exe"
       elif system == "linux":
           # Linux: Download .tar.xz package (Mozilla now uses xz instead of bz2)
           installer_url = "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US"
           installer_path = download_dir / "firefox-latest.tar.xz"
       elif system == "darwin":
           # macOS: Download .dmg installer
           installer_url = "https://download.mozilla.org/?product=firefox-latest&os=osx&lang=en-US"
           installer_path = download_dir / "Firefox.dmg"
       else:
           await send_response({
               "action": "status",
               "data": {
                   "category": "Web",
                   "name": "Mozilla",
                   "status": "not installed",
                   "comment": f"Unsupported platform: {system}",
               }
           })
           return None
       
       async with httpx.AsyncClient(timeout=900.0, follow_redirects=True) as client:
           async with client.stream("GET", installer_url) as response:
               response.raise_for_status()
               
               # Try to get actual filename from Content-Disposition header or URL
               content_disposition = response.headers.get("content-disposition", "")
               actual_filename = None
               if content_disposition and "filename=" in content_disposition:
                   # Extract filename from Content-Disposition header
                   match = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', content_disposition)
                   if match:
                       actual_filename = match.group(1).strip('"\'')
               
               # Use actual filename if found, otherwise use default
               if system == "windows" and actual_filename:
                   installer_path = download_dir / actual_filename
               
               total_size = int(response.headers.get("content-length", 0))
               chunk_size = 8192
               downloaded = 0
               last_pct = [-1]
               with open(installer_path, "wb") as f:
                   async for chunk in response.aiter_bytes(chunk_size):
                       f.write(chunk)
                       downloaded += len(chunk)
                       
                       if total_size > 0:
                           progress = (downloaded / total_size) * 100
                           pct = int(progress)
                           if pct != last_pct[0]:
                               last_pct[0] = pct
                               bar_length = 50
                               filled_length = int(bar_length * downloaded // total_size)
                               bar = '█' * filled_length + '-' * (bar_length - filled_length)
                               mb_downloaded = downloaded / (1024 * 1024)
                               mb_total = total_size / (1024 * 1024)
                               logger.info("[installer][web-mozilla] |%s| %d%% (%.1f/%.1f MB)", bar, pct, mb_downloaded, mb_total)
                               asyncio.create_task(send_response({
                                   "action": "status",
                                   "data": {
                                       "category": "Web",
                                       "name": "Mozilla",
                                       "status": "installing",
                                       "comment": f"Downloading Mozilla Firefox... {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)",
                                   }
                               }))
       
       # For Windows, if we couldn't get filename from header, find any .exe file in download directory
       if system == "windows":
           if not installer_path.exists():
               exe_files = list(download_dir.glob("*.exe"))
               if exe_files:
                   installer_path = exe_files[0]  # Use the first .exe file found
                   logger.info("[installer][web-mozilla] Found installer file: %s", installer_path.name)
       
       logger.info("[installer][web-mozilla] Download complete: %s", installer_path)
       return installer_path
   except Exception as e:
       logger.error("[installer][web-mozilla] Download failed: %s", e)
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "not installed",
               "comment": f"Mozilla Firefox download failed: {str(e)}",
           }
       })
       return None


async def _install_firefox_windows(installer_path, user_password: str = ""):
   """Install Firefox on Windows"""
   logger.info("[installer][web-mozilla] Installing Mozilla Firefox on Windows...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Web",
           "name": "Mozilla",
           "status": "installing",
           "comment": "Installing Mozilla Firefox...",
       }
   })
   
   try:
       download_dir = ZEUZ_NODE_DOWNLOADS_DIR / "firefox"
       
       # Find the installer .exe file (may have versioned name like "Firefox Setup 145.0.2.exe")
       installer_exe = None
       if installer_path and installer_path.exists():
           installer_exe = installer_path
       else:
           # Look for any .exe file in the firefox download directory
           if download_dir.exists():
               exe_files = list(download_dir.glob("*.exe"))
               if exe_files:
                   installer_exe = exe_files[0]
                   logger.info("[installer][web-mozilla] Found installer: %s", installer_exe.name)
       
       if not installer_exe or not installer_exe.exists():
           error_msg = "Firefox installer not found in download directory"
           logger.error("[installer][web-mozilla] %s", error_msg)
           await send_response({
               "action": "status",
               "data": {
                   "category": "Web",
                   "name": "Mozilla",
                   "status": "not installed",
                   "comment": error_msg,
               }
           })
           return False
       
       # Use simple PowerShell Start-Process command with /S flag for silent installation
       # This installs to default location (Program Files) which works better for automation
       installer_path_str = str(installer_exe).replace('/', '\\')
       ps_command = f'Start-Process "{installer_path_str}" -ArgumentList "/S" -Wait'
       
       logger.info("[installer][web-mozilla] Running installer: %s", installer_exe.name)
       logger.info("[installer][web-mozilla] Command: %s", ps_command)
       
       # Run the command (UAC prompt will appear if needed for elevation)
       result = subprocess.run(
           ["powershell", "-Command", ps_command],
           capture_output=True,
           text=True,
           check=False
       )
       
       if result.returncode == 0:
           logger.info("[installer][web-mozilla] Mozilla Firefox installed successfully")
           return True
       else:
           error_msg = f"Installation failed: {result.stderr or result.stdout}"
           logger.error("[installer][web-mozilla] %s", error_msg)
           await send_response({
               "action": "status",
               "data": {
                   "category": "Web",
                   "name": "Mozilla",
                   "status": "not installed",
                   "comment": f"Installation failed. Please check if you have administrator privileges.",
               }
           })
           return False
   except Exception as e:
       logger.exception("[installer][web-mozilla] Windows installation failed: %s", e)
       import traceback
       traceback.print_exc()
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "not installed",
               "comment": f"Mozilla Firefox installation failed: {str(e)}",
           }
       })
       return False


async def _install_firefox_linux(installer_path, user_password: str = ""):
   """Install Firefox on Linux"""
   logger.info("[installer][web-mozilla] Installing Mozilla Firefox on Linux...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Web",
           "name": "Mozilla",
           "status": "installing",
           "comment": "Installing Mozilla Firefox...",
       }
   })
   
   try:
       # Helper function to run sudo commands with password if provided
       def run_sudo(cmd_list):
           if user_password:
               # Use echo to pipe password to sudo -S (read password from stdin)
               cmd = f"echo '{user_password}' | sudo -S {' '.join(cmd_list[1:])}"
               return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
           else:
               return subprocess.run(cmd_list, capture_output=True, text=True, check=False)
       
       # First, try to install from downloaded .tar.xz file (ensures Selenium can find binary)
       # Find any .tar.xz file in the download directory (filename may vary: firefox-145.0.2.tar.xz, firefox-latest.tar.xz, etc.)
       download_dir = ZEUZ_NODE_DOWNLOADS_DIR / "firefox"
       tar_file = None
       
       # If installer_path exists and is a .tar.xz file, use it
       if installer_path and installer_path.exists() and installer_path.suffix == '.xz':
           tar_file = installer_path
       else:
           # Otherwise, find any .tar.xz file in the download directory (there should be only one)
           if download_dir.exists():
               tar_files = list(download_dir.glob("*.tar.xz"))
               if tar_files:
                   tar_file = tar_files[0]  # Use the first .tar.xz file found
                   logger.info("[installer][web-mozilla] Found Firefox installer: %s", tar_file.name)
       
       if tar_file and tar_file.exists():
           logger.info("[installer][web-mozilla] Attempting to install from downloaded .tar.xz file...")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Web",
                   "name": "Mozilla",
                   "status": "installing",
                   "comment": "Extracting Firefox from archive...",
               }
           })
           
           try:
               extract_dir = ZEUZ_NODE_DOWNLOADS_DIR / "firefox"
               extract_dir.mkdir(parents=True, exist_ok=True)
               
               logger.info("[installer][web-mozilla] Extracting Firefox from archive...")
               await send_response({
                   "action": "status",
                   "data": {
                       "category": "Web",
                       "name": "Mozilla",
                       "status": "installing",
                       "comment": "Extracting Firefox from archive...",
                   }
               })
               
               # Extract the tar.xz file directly to download directory (works with any filename)
               with tarfile.open(tar_file, 'r:xz') as tar:
                   tar.extractall(extract_dir)
               
               # Find the firefox directory (usually named firefox/)
               firefox_dir = None
               for item in extract_dir.iterdir():
                   if item.is_dir() and item.name.startswith('firefox'):
                       firefox_dir = item
                       break
               
               if firefox_dir and (firefox_dir / "firefox").exists():
                   # Keep files in download directory - no copying needed
                   # Binary path: ~/.zeuz/zeuz_node_downloads/firefox/firefox/firefox
                   firefox_binary_path = firefox_dir / "firefox"
                   
                   logger.info("[installer][web-mozilla] Creating symlink to Firefox binary...")
                   await send_response({
                       "action": "status",
                       "data": {
                           "category": "Web",
                           "name": "Mozilla",
                           "status": "installing",
                           "comment": "Creating symlink to Firefox...",
                       }
                   })
                   
                   # Create symlink in /usr/local/bin or /usr/bin (prefer /usr/local/bin)
                   symlink_paths = [
                       Path("/usr/local/bin/firefox"),
                       Path("/usr/bin/firefox")
                   ]
                   
                   symlink_created = False
                   for symlink_path in symlink_paths:
                       # Remove existing symlink or file if it exists
                       if symlink_path.exists() or symlink_path.is_symlink():
                           remove_result = run_sudo(["sudo", "rm", "-f", str(symlink_path)])
                           if remove_result.returncode != 0:
                               logger.warning("[installer][web-mozilla] Warning: Failed to remove existing %s: %s", symlink_path, remove_result.stderr)
                       
                       # Create new symlink pointing directly to the binary in download directory
                       symlink_result = run_sudo([
                           "sudo", "ln", "-s", str(firefox_binary_path), str(symlink_path)
                       ])
                       
                       if symlink_result.returncode == 0:
                           logger.info("[installer][web-mozilla] Created symlink: %s -> %s", symlink_path, firefox_binary_path)
                           run_sudo(["sudo", "chmod", "+x", str(symlink_path)])
                           symlink_created = True
                           break
                       else:
                           logger.error("[installer][web-mozilla] Failed to create symlink at %s: %s", symlink_path, symlink_result.stderr)
                   
                   if not symlink_created:
                       logger.error("[installer][web-mozilla] Failed to create symlink in any location")
                   else:
                       # Create .desktop file to appear in application menu
                       desktop_dir = Path.home() / ".local" / "share" / "applications"
                       desktop_dir.mkdir(parents=True, exist_ok=True)
                       desktop_file = desktop_dir / "firefox.desktop"
                       
                       # Find icon path (default128.png or fallback to any icon)
                       icon_path = firefox_dir / "browser" / "chrome" / "icons" / "default" / "default128.png"
                       if not icon_path.exists():
                           # Try to find any icon file
                           icon_dir = firefox_dir / "browser" / "chrome" / "icons" / "default"
                           if icon_dir.exists():
                               icon_files = list(icon_dir.glob("*.png"))
                               if icon_files:
                                   icon_path = icon_files[0]
                       
                       # Create .desktop file content
                       desktop_content = f"""[Desktop Entry]
Version=1.0
Name=Firefox (Custom)
Comment=Mozilla Firefox Web Browser
Exec={firefox_binary_path}
Icon={icon_path if icon_path.exists() else ''}
Terminal=false
Type=Application
Categories=Network;WebBrowser;
StartupNotify=true
"""
                       
                       try:
                           with open(desktop_file, "w") as f:
                               f.write(desktop_content)
                           # Make .desktop file executable
                           os.chmod(desktop_file, 0o755)
                           logger.info("[installer][web-mozilla] Created .desktop file: %s", desktop_file)
                       except Exception as e:
                           logger.warning("[installer][web-mozilla] Warning: Failed to create .desktop file: %s", e)
                       
                       # Verify installation by testing firefox command (uses symlink)
                       test_result = subprocess.run(
                           ["firefox", "--version"],
                           capture_output=True,
                           text=True,
                           check=False
                       )
                       if test_result.returncode == 0:
                           logger.info("[installer][web-mozilla] Firefox successfully installed")
                           logger.info("[installer][web-mozilla] Binary location: %s", firefox_binary_path)
                           logger.info("[installer][web-mozilla] Symlink: %s -> %s", symlink_path, firefox_binary_path)
                           return True
                       else:
                           error_msg = f"Firefox verification failed: {test_result.stderr}"
                           logger.error("[installer][web-mozilla] %s", error_msg)
                           await send_response({
                               "action": "status",
                               "data": {
                                   "category": "Web",
                                   "name": "Mozilla",
                                   "status": "not installed",
                                   "comment": error_msg,
                               }
                           })
                           return False
               else:
                   error_msg = "Could not find Firefox directory or binary after extraction"
                   logger.error("[installer][web-mozilla] %s", error_msg)
                   await send_response({
                       "action": "status",
                       "data": {
                           "category": "Web",
                           "name": "Mozilla",
                           "status": "not installed",
                           "comment": error_msg,
                       }
                   })
                   return False
           except Exception as e:
               error_msg = f"Installation from .tar.xz failed: {str(e)}"
               logger.exception("[installer][web-mozilla] %s", error_msg)
               import traceback
               traceback.print_exc()
               await send_response({
                   "action": "status",
                   "data": {
                       "category": "Web",
                       "name": "Mozilla",
                       "status": "not installed",
                       "comment": error_msg,
                   }
               })
               return False
       
       # If no installer file was downloaded or tar.xz installation not attempted
       error_msg = "Firefox installer file not found or invalid. Cannot proceed with installation."
       logger.error("[installer][web-mozilla] %s", error_msg)
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "not installed",
               "comment": error_msg,
           }
       })
       return False
   except Exception as e:
       logger.exception("[installer][web-mozilla] Linux installation failed: %s", e)
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "not installed",
               "comment": f"Mozilla Firefox installation failed: {str(e)}",
           }
       })
       return False


async def _install_firefox_darwin(installer_path, user_password: str = ""):
   """Install Firefox on macOS"""
   logger.info("[installer][web-mozilla] Installing Mozilla Firefox on macOS...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Web",
           "name": "Mozilla",
           "status": "installing",
           "comment": "Installing Mozilla Firefox...",
       }
   })
   
   try:
       # Try using homebrew first (doesn't need sudo)
       brew_result = subprocess.run(
           ["brew", "install", "--cask", "firefox"],
           capture_output=True,
           text=True,
           check=False
       )
       
       if brew_result.returncode == 0:
           logger.info("[installer][web-mozilla] Mozilla Firefox installed via homebrew")
           return True
       
       # Fallback to .dmg installer
       if installer_path and installer_path.exists():
           # Mount the DMG (doesn't need sudo)
           mount_result = subprocess.run(
               ["hdiutil", "attach", str(installer_path)],
               capture_output=True,
               text=True,
               check=False
           )
           
           if mount_result.returncode == 0:
               try:
                   # Find the mounted volume
                   mount_point = None
                   for line in mount_result.stdout.split('\n'):
                       if '/Volumes/Firefox' in line:
                           parts = line.split('\t')
                           if len(parts) > 2:
                               mount_point = parts[-1].strip()
                               break
                   
                   if mount_point:
                       firefox_app = Path(mount_point) / "Firefox.app"
                       if firefox_app.exists():
                           # Copy to Applications (may need sudo if permissions require it)
                           if user_password:
                               cmd = f"echo '{user_password}' | sudo -S cp -R {str(firefox_app)} /Applications/"
                               copy_result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
                           else:
                               copy_result = subprocess.run(
                                   ["cp", "-R", str(firefox_app), "/Applications/"],
                                   capture_output=True,
                                   text=True,
                                   check=False
                               )
                           
                           if copy_result.returncode == 0:
                               logger.info("[installer][web-mozilla] Mozilla Firefox installed via .dmg")
                               return True
               finally:
                   # Unmount the DMG (doesn't need sudo)
                   subprocess.run(
                       ["hdiutil", "detach", mount_point or "/Volumes/Firefox"],
                       capture_output=True,
                       text=True,
                       check=False
                   )
       
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "not installed",
               "comment": "Mozilla Firefox installation failed. Please install manually.",
           }
       })
       return False
   except Exception as e:
       logger.exception("[installer][web-mozilla] macOS installation failed: %s", e)
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "not installed",
               "comment": f"Mozilla Firefox installation failed: {str(e)}",
           }
       })
       return False


async def _verify_firefox_installation():
   """Verify that Firefox is properly installed"""
   logger.info("[installer][web-mozilla] Verifying Mozilla Firefox installation...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Web",
           "name": "Mozilla",
           "status": "installing",
           "comment": "Verifying Mozilla Firefox installation...",
       }
   })
   
   # Wait a moment for installation to complete
   await asyncio.sleep(2)
   
   # Check if Firefox is installed by running check_status
   return await check_status()


async def install(user_password: str = "") -> bool:
   """Main function to install Mozilla Firefox"""
   logger.info("[installer][web-mozilla] Installing Mozilla Firefox...")
   
   # Check if Firefox is already installed
   if await check_status():
       logger.info("[installer][web-mozilla] Mozilla Firefox is already installed")
       return True
   
   installer_path = None
   system = platform.system().lower()
   
   # Download installer if needed
   if system == "windows" or system == "darwin" or system == "linux":
       installer_path = await _download_firefox_installer()
       if not installer_path:
           return False
   
   # Install based on platform
   if system == "windows":
       success = await _install_firefox_windows(installer_path, user_password)
   elif system == "linux":
       success = await _install_firefox_linux(installer_path, user_password)
   elif system == "darwin":
       success = await _install_firefox_darwin(installer_path, user_password)
   else:
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "not installed",
               "comment": f"Unsupported platform: {system}",
           }
       })
       return False
   
   if not success:
       return False
   
   # Verify installation
   if not await _verify_firefox_installation():
       logger.error("[installer][web-mozilla] Mozilla Firefox installation verification failed")
       return False
   
   # Keep installer file in downloads directory (not cleaning up)
   # The installer is kept for potential reuse
   
   logger.info("[installer][web-mozilla] Mozilla Firefox installation complete")
   await send_response({
       "action": "status",
       "data": {
           "category": "Web",
           "name": "Mozilla",
           "status": "installed",
           "comment": "Mozilla Firefox is installed",
       }
   })
   return True
