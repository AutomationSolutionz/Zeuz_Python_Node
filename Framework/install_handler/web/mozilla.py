import subprocess
import platform
import shutil
import httpx
import asyncio
import os
import json
from pathlib import Path
from Framework.install_handler.utils import send_response
from settings import ZEUZ_NODE_DOWNLOADS_DIR


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
   print("[installer][web-mozilla] Checking status...")
  
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
           print("[installer][web-mozilla] Not installed")
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
           print("[installer][web-mozilla] Not installed")
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
      
       print("[installer][web-mozilla] Already installed")
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
       print("[installer][web-mozilla] Not installed (firefox not found)")
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
       print(f"[installer][web-mozilla] Error checking status: {e}")
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
   print("[installer][web-mozilla] Downloading Mozilla Firefox installer...")
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
           installer_path = download_dir / "FirefoxSetup.exe"
       elif system == "linux":
           # Linux: Download .tar.bz2 package
           installer_url = "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US"
           installer_path = download_dir / "firefox-latest.tar.bz2"
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
               
               total_size = int(response.headers.get("content-length", 0))
               chunk_size = 8192
               downloaded = 0
               
               count = []
               with open(installer_path, "wb") as f:
                   async for chunk in response.aiter_bytes(chunk_size):
                       f.write(chunk)
                       downloaded += len(chunk)
                       
                       if total_size > 0:
                           progress = (downloaded / total_size) * 100
                           bar_length = 50
                           filled_length = int(bar_length * downloaded // total_size)
                           bar = '█' * filled_length + '-' * (bar_length - filled_length)
                           
                           mb_downloaded = downloaded / (1024 * 1024)
                           mb_total = total_size / (1024 * 1024)
                           
                           print(f"\r[installer][web-mozilla] |{bar}| {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='', flush=True)
                           
                           p = round(mb_downloaded/mb_total, 1)
                           if p not in count:
                               count.append(p)
                               asyncio.create_task(send_response({
                                   "action": "status",
                                   "data": {
                                       "category": "Web",
                                       "name": "Mozilla",
                                       "status": "installing",
                                       "comment": f"Downloading Mozilla Firefox... {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)",
                                   }
                               }))
       
       print()
       print(f"[installer][web-mozilla] Download complete: {installer_path}")
       return installer_path
   except Exception as e:
       print(f"\n[installer][web-mozilla] Download failed: {e}")
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


async def _install_firefox_windows(installer_path):
   """Install Firefox on Windows"""
   print("[installer][web-mozilla] Installing Mozilla Firefox on Windows...")
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
       # Install to custom directory in downloads folder
       install_dir = ZEUZ_NODE_DOWNLOADS_DIR / "firefox" / "installation"
       install_dir.mkdir(parents=True, exist_ok=True)
       
       # Use .exe installer with custom installation directory
       if installer_path and installer_path.exists():
           # Firefox installer supports /D parameter for custom directory
           # /S for silent installation
           # Path needs to be quoted if it contains spaces
           install_dir_str = str(install_dir).replace('/', '\\')
           exe_result = subprocess.run(
               [str(installer_path), "/S", f"/D={install_dir_str}"],
               capture_output=True,
               text=True,
               check=False
           )
           
           if exe_result.returncode == 0:
               print("[installer][web-mozilla] Mozilla Firefox installed via .exe")
               return True
           else:
               print(f"[installer][web-mozilla] .exe installation failed: {exe_result.stderr}")
               return False
       else:
           print("[installer][web-mozilla] Installer not found, trying direct download")
           # Try direct download URL
           download_result = subprocess.run(
               ["powershell", "-Command", "Start-Process", "https://www.mozilla.org/firefox/download/thanks/", "-Wait"],
               capture_output=True,
               text=True,
               check=False
           )
           return download_result.returncode == 0
   except Exception as e:
       print(f"[installer][web-mozilla] Windows installation failed: {e}")
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


async def _install_firefox_linux(installer_path):
   """Install Firefox on Linux"""
   print("[installer][web-mozilla] Installing Mozilla Firefox on Linux...")
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
       pkg_manager = _get_linux_package_manager()
       
       if pkg_manager == "apt":
           # Try installing via apt (if repository is configured)
           apt_result = subprocess.run(
               ["sudo", "apt-get", "update"],
               capture_output=True,
               text=True,
               check=False
           )
           
           apt_install_result = subprocess.run(
               ["sudo", "apt-get", "install", "-y", "firefox"],
               capture_output=True,
               text=True,
               check=False
           )
           
           if apt_install_result.returncode == 0:
               print("[installer][web-mozilla] Mozilla Firefox installed via apt")
               return True
           
           # Fallback to .tar.bz2 package
           if installer_path and installer_path.exists():
               # Extract and install from tar.bz2
               extract_dir = installer_path.parent / "firefox"
               extract_dir.mkdir(exist_ok=True)
               
               tar_result = subprocess.run(
                   ["tar", "-xjf", str(installer_path), "-C", str(extract_dir.parent)],
                   capture_output=True,
                   text=True,
                   check=False
               )
               
               if tar_result.returncode == 0:
                   # Create symlink or move to /opt
                   firefox_bin = extract_dir / "firefox" / "firefox"
                   if firefox_bin.exists():
                       # Try to create symlink in /usr/local/bin
                       symlink_result = subprocess.run(
                           ["sudo", "ln", "-sf", str(firefox_bin), "/usr/local/bin/firefox"],
                           capture_output=True,
                           text=True,
                           check=False
                       )
                       if symlink_result.returncode == 0:
                           print("[installer][web-mozilla] Mozilla Firefox installed via .tar.bz2 package")
                           return True
       
       elif pkg_manager == "yum":
           # Try installing via yum
           yum_result = subprocess.run(
               ["sudo", "yum", "install", "-y", "firefox"],
               capture_output=True,
               text=True,
               check=False
           )
           
           if yum_result.returncode == 0:
               print("[installer][web-mozilla] Mozilla Firefox installed via yum")
               return True
       
       elif pkg_manager == "dnf":
           # Try installing via dnf
           dnf_result = subprocess.run(
               ["sudo", "dnf", "install", "-y", "firefox"],
               capture_output=True,
               text=True,
               check=False
           )
           
           if dnf_result.returncode == 0:
               print("[installer][web-mozilla] Mozilla Firefox installed via dnf")
               return True
       
       elif pkg_manager == "pacman":
           # Try installing via pacman
           pacman_result = subprocess.run(
               ["sudo", "pacman", "-S", "--noconfirm", "firefox"],
               capture_output=True,
               text=True,
               check=False
           )
           
           if pacman_result.returncode == 0:
               print("[installer][web-mozilla] Mozilla Firefox installed via pacman")
               return True
       
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "not installed",
               "comment": "Mozilla Firefox installation failed. Please install manually or configure repository.",
           }
       })
       return False
   except Exception as e:
       print(f"[installer][web-mozilla] Linux installation failed: {e}")
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


async def _install_firefox_darwin(installer_path):
   """Install Firefox on macOS"""
   print("[installer][web-mozilla] Installing Mozilla Firefox on macOS...")
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
       # Try using homebrew first
       brew_result = subprocess.run(
           ["brew", "install", "--cask", "firefox"],
           capture_output=True,
           text=True,
           check=False
       )
       
       if brew_result.returncode == 0:
           print("[installer][web-mozilla] Mozilla Firefox installed via homebrew")
           return True
       
       # Fallback to .dmg installer
       if installer_path and installer_path.exists():
           # Mount the DMG
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
                           # Copy to Applications
                           copy_result = subprocess.run(
                               ["cp", "-R", str(firefox_app), "/Applications/"],
                               capture_output=True,
                               text=True,
                               check=False
                           )
                           
                           if copy_result.returncode == 0:
                               print("[installer][web-mozilla] Mozilla Firefox installed via .dmg")
                               return True
               finally:
                   # Unmount the DMG
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
       print(f"[installer][web-mozilla] macOS installation failed: {e}")
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
   print("[installer][web-mozilla] Verifying Mozilla Firefox installation...")
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


async def install() -> bool:
   """Main function to install Mozilla Firefox"""
   print("[installer][web-mozilla] Installing Mozilla Firefox...")
   
   # Check if Firefox is already installed
   if await check_status():
       print("[installer][web-mozilla] Mozilla Firefox is already installed")
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
       success = await _install_firefox_windows(installer_path)
   elif system == "linux":
       success = await _install_firefox_linux(installer_path)
   elif system == "darwin":
       success = await _install_firefox_darwin(installer_path)
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
       print("[installer][web-mozilla] Mozilla Firefox installation verification failed")
       return False
   
   # Keep installer file in downloads directory (not cleaning up)
   # The installer is kept for potential reuse
   
   print("[installer][web-mozilla] Mozilla Firefox installation complete")
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
