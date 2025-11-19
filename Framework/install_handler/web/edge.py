import subprocess
import platform
import httpx
import asyncio
import os
import shutil
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
   """Check if Microsoft Edge is installed."""
   print("[installer][web-edge] Checking status...")
  
   try:
       result = None
       
       if _is_windows():
           # Windows: Check registry for Edge installation
           ps_command = '''
           $edge = Get-ItemProperty "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*",
                                     "HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*" |
                     Where-Object { $_.DisplayName -like "*Edge*" } |
                     Select-Object -First 1
           if ($edge) {
               @{
                   InstallLocation = $edge.InstallLocation
                   DisplayVersion = $edge.DisplayVersion
                   DisplayName = $edge.DisplayName
               } | ConvertTo-Json
           }
           '''
           result = subprocess.run(
               ["powershell", "-Command", ps_command],
               capture_output=True,
               text=True,
               check=False
           )
           
           # If registry check found Edge, parse JSON and get version
           if result.returncode == 0 and result.stdout.strip():
               try:
                   edge_info = json.loads(result.stdout.strip())
                   display_version = edge_info.get('DisplayVersion', '')
                   
                   # Use DisplayVersion from registry directly
                   if display_version:
                       version_text = f"Microsoft Edge {display_version}"
                   else:
                       # Found in registry but couldn't get version
                       version_text = "Microsoft Edge"
                   
                   if version_text:
                       result.stdout = version_text
                       result.returncode = 0
                   else:
                       result.returncode = 1
               except (json.JSONDecodeError, KeyError, Exception):
                   # If JSON parsing fails, Edge is still installed (found in registry)
                   result.stdout = "Microsoft Edge"
                   result.returncode = 0
           else:
               # Not found in registry, set returncode to indicate not installed
               result.returncode = 1
       else:
           # Linux: try different possible command names
           commands = ["microsoft-edge", "--version"]
           result = subprocess.run(
               commands,
               capture_output=True,
               text=True,
               check=False
           )
           
           if result.returncode != 0:
               # Try alternative command on Linux
               result = subprocess.run(
                   ["edge", "--version"],
                   capture_output=True,
                   text=True,
                   check=False
               )
         
       if result.returncode != 0:
           print("[installer][web-edge] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Web",
                   "name": "Edge",
                   "status": "not installed",
                   "comment": "Install Microsoft Edge to use it.",
               }
           })
           return False
      
       # Edge version output is typically in stdout or stderr
       version_text = (result.stdout or result.stderr).strip()
       if not version_text:
           print("[installer][web-edge] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Web",
                   "name": "Edge",
                   "status": "not installed",
                   "comment": "Install Microsoft Edge to use it.",
               }
           })
           return False
      
       print("[installer][web-edge] Already installed")
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Edge",
               "status": "installed",
               "comment": f"Microsoft Edge is installed (version: {version_text[:50]})",
           }
       })
       return True
   except (FileNotFoundError, OSError):
       # Edge command not found - Edge is not installed
       print("[installer][web-edge] Not installed (msedge not found)")
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Edge",
               "status": "not installed",
               "comment": "Install Microsoft Edge to use it.",
           }
       })
       return False
   except Exception as e:
       print(f"[installer][web-edge] Error checking status: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Edge",
               "status": "not installed",
               "comment": "Unable to check Microsoft Edge status.",
           }
       })
       return False


async def _download_edge_installer():
   """Download Edge installer based on platform"""
   print("[installer][web-edge] Downloading Microsoft Edge installer...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Web",
           "name": "Edge",
           "status": "installing",
           "comment": "Downloading Microsoft Edge installer...",
       }
   })
   
   download_dir = ZEUZ_NODE_DOWNLOADS_DIR / "edge"
   download_dir.mkdir(parents=True, exist_ok=True)
   
   system = platform.system().lower()
   arch = platform.machine().lower()
   
   try:
       if system == "windows":
           # Windows: Download MSI installer
           installer_url = "https://go.microsoft.com/fwlink/?linkid=2109048&Channel=Stable&language=en"
           installer_path = download_dir / "MicrosoftEdgeSetup.msi"
       elif system == "linux":
           installer_url = "https://go.microsoft.com/fwlink?linkid=2149051&brand=M102"
           installer_path = download_dir / "microsoft-edge-stable.deb"
       elif system == "darwin":
           # macOS: Download .pkg installer from Microsoft Edge website
           installer_url = "https://go.microsoft.com/fwlink/?linkid=2093504"
           installer_path = download_dir / "MicrosoftEdge.pkg"
       else:
           await send_response({
               "action": "status",
               "data": {
                   "category": "Web",
                   "name": "Edge",
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
                           
                           print(f"\r[installer][web-edge] |{bar}| {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='', flush=True)
                           
                           p = round(mb_downloaded/mb_total, 1)
                           if p not in count:
                               count.append(p)
                               asyncio.create_task(send_response({
                                   "action": "status",
                                   "data": {
                                       "category": "Web",
                                       "name": "Edge",
                                       "status": "installing",
                                       "comment": f"Downloading Microsoft Edge... {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)",
                                   }
                               }))
       
       print()
       print(f"[installer][web-edge] Download complete: {installer_path}")
       return installer_path
   except Exception as e:
       print(f"\n[installer][web-edge] Download failed: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Edge",
               "status": "not installed",
               "comment": f"Microsoft Edge download failed: {str(e)}",
           }
       })
       return None


async def _install_edge_windows(installer_path, user_password: str = ""):
   """Install Edge on Windows"""
   print("[installer][web-edge] Installing Microsoft Edge on Windows...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Web",
           "name": "Edge",
           "status": "installing",
           "comment": "Installing Microsoft Edge...",
       }
   })
   
   try:
       # Helper function to run commands with elevation if password provided
       def run_elevated(cmd_list):
           if user_password:
               # Use PowerShell to run with credentials
               # Note: This requires username, so we'll use current user
               import getpass
               username = getpass.getuser()
               # Create secure string and run with credentials
               # Properly escape arguments for PowerShell
               escaped_args = []
               for arg in cmd_list[1:]:
                   escaped_arg = arg.replace('"', '`"').replace('$', '`$')
                   escaped_args.append(f'"{escaped_arg}"')
               args_str = ','.join(escaped_args)
               ps_script = f'''
               $password = ConvertTo-SecureString -String "{user_password}" -AsPlainText -Force
               $credential = New-Object System.Management.Automation.PSCredential("{username}", $password)
               Start-Process -FilePath "{cmd_list[0]}" -ArgumentList {args_str} -Credential $credential -Wait -NoNewWindow
               '''
               return subprocess.run(
                   ["powershell", "-Command", ps_script],
                   capture_output=True,
                   text=True,
                   check=False
               )
           else:
               # Try with RunAs elevation prompt
               # Use Start-Process with -Verb RunAs for elevation
               if cmd_list[0] == "winget":
                   args_str = ' '.join([f'"{arg}"' for arg in cmd_list[1:]])
                   ps_script = f'Start-Process -FilePath "winget" -ArgumentList {args_str} -Verb RunAs -Wait -NoNewWindow'
               elif cmd_list[0] == "msiexec":
                   args_str = ' '.join([f'"{arg}"' for arg in cmd_list[1:]])
                   ps_script = f'Start-Process -FilePath "msiexec" -ArgumentList {args_str} -Verb RunAs -Wait -NoNewWindow'
               else:
                   return subprocess.run(cmd_list, capture_output=True, text=True, check=False)
               
               return subprocess.run(
                   ["powershell", "-Command", ps_script],
                   capture_output=True,
                   text=True,
                   check=False
               )
       
       # Try using winget first (Windows 10/11)
       winget_result = run_elevated(["winget", "install", "--id", "Microsoft.Edge", "--silent", "--accept-package-agreements", "--accept-source-agreements"])
       
       if winget_result.returncode == 0:
           print("[installer][web-edge] Microsoft Edge installed via winget")
           return True
       
       # Fallback to MSI installer
       if installer_path and installer_path.exists():
           msi_result = run_elevated(["msiexec", "/i", str(installer_path), "/quiet", "/norestart"])
           
           if msi_result.returncode == 0:
               print("[installer][web-edge] Microsoft Edge installed via MSI")
               return True
           else:
               print(f"[installer][web-edge] Installation failed. Error: {msi_result.stderr}")
               await send_response({
                   "action": "status",
                   "data": {
                       "category": "Web",
                       "name": "Edge",
                       "status": "not installed",
                       "comment": "Installation failed. Please ensure you have provided the correct password.",
                   }
               })
               return False
       else:
           print("[installer][web-edge] Installer not found, trying direct download")
           # Try direct download URL (this will prompt for elevation if needed)
           if user_password:
               import getpass
               username = getpass.getuser()
               ps_script = f'''
               $password = ConvertTo-SecureString -String "{user_password}" -AsPlainText -Force
               $credential = New-Object System.Management.Automation.PSCredential("{username}", $password)
               Start-Process "https://go.microsoft.com/fwlink/?linkid=2109048" -Credential $credential -Wait
               '''
               download_result = subprocess.run(
                   ["powershell", "-Command", ps_script],
                   capture_output=True,
                   text=True,
                   check=False
               )
           else:
               download_result = subprocess.run(
                   ["powershell", "-Command", "Start-Process", "https://go.microsoft.com/fwlink/?linkid=2109048", "-Wait"],
                   capture_output=True,
                   text=True,
                   check=False
               )
           
           if download_result.returncode == 0:
               return True
           else:
               print(f"[installer][web-edge] Installation failed. Error: {download_result.stderr}")
               await send_response({
                   "action": "status",
                   "data": {
                       "category": "Web",
                       "name": "Edge",
                       "status": "not installed",
                       "comment": "Installation failed. Please ensure you have provided the correct password.",
                   }
               })
               return False
       
       # All installation methods failed
       print(f"[installer][web-edge] Installation failed. Error: {winget_result.stderr}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Edge",
               "status": "not installed",
               "comment": "Installation failed. Please ensure you have provided the correct password.",
           }
       })
       return False
   except Exception as e:
       print(f"[installer][web-edge] Windows installation failed: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Edge",
               "status": "not installed",
               "comment": "Installation failed. Please ensure you have provided the correct password.",
           }
       })
       return False


async def _install_edge_linux(installer_path, user_password: str = ""):
   """Install Edge on Linux"""
   print("[installer][web-edge] Installing Microsoft Edge on Linux...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Web",
           "name": "Edge",
           "status": "installing",
           "comment": "Installing Microsoft Edge...",
       }
   })
   
   try:
       pkg_manager = _get_linux_package_manager()
       
       # Helper function to run sudo commands with password if provided
       def run_sudo(cmd_list):
           if user_password:
               # Use echo to pipe password to sudo -S (read password from stdin)
               cmd = f"echo '{user_password}' | sudo -S {' '.join(cmd_list[1:])}"
               return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
           else:
               return subprocess.run(cmd_list, capture_output=True, text=True, check=False)
       
       if pkg_manager == "apt":
           # Try installing via apt (if repository is configured)
           apt_result = run_sudo(["sudo", "apt-get", "update"])
           
           apt_install_result = run_sudo(["sudo", "apt-get", "install", "-y", "microsoft-edge-stable"])
           
           if apt_install_result.returncode == 0:
               print("[installer][web-edge] Microsoft Edge installed via apt")
               return True
           
           
           # Fallback to .deb package
           if installer_path and installer_path.exists():
               deb_result = run_sudo(["sudo", "dpkg", "-i", str(installer_path)])
               
               if deb_result.returncode != 0:
                   # Install dependencies if needed
                   run_sudo(["sudo", "apt-get", "install", "-f", "-y"])
                   deb_result = run_sudo(["sudo", "dpkg", "-i", str(installer_path)])
               
               if deb_result.returncode == 0:
                   print("[installer][web-edge] Microsoft Edge installed via .deb package")
                   return True
               
               # .deb installation failed
               print(f"[installer][web-edge] Installation failed. Error: {deb_result.stderr}")
               await send_response({
                   "action": "status",
                   "data": {
                       "category": "Web",
                       "name": "Edge",
                       "status": "not installed",
                       "comment": "Installation failed. Please ensure you have provided the correct password.",
                   }
               })
               return False
           else:
               # No .deb package available and apt failed
               print(f"[installer][web-edge] Installation failed. Error: {apt_install_result.stderr}")
               await send_response({
                   "action": "status",
                   "data": {
                       "category": "Web",
                       "name": "Edge",
                       "status": "not installed",
                       "comment": "Installation failed. Please ensure you have provided the correct password.",
                   }
               })
               return False
       
       elif pkg_manager == "yum":
           # Try installing via yum
           yum_result = run_sudo(["sudo", "yum", "install", "-y", "microsoft-edge-stable"])
           
           if yum_result.returncode == 0:
               print("[installer][web-edge] Microsoft Edge installed via yum")
               return True
           
           # Installation failed
           print(f"[installer][web-edge] Installation failed. Error: {yum_result.stderr}")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Web",
                   "name": "Edge",
                   "status": "not installed",
                   "comment": "Installation failed. Please ensure you have provided the correct password.",
               }
           })
           return False
       
       elif pkg_manager == "dnf":
           # Try installing via dnf
           dnf_result = run_sudo(["sudo", "dnf", "install", "-y", "microsoft-edge-stable"])
           
           if dnf_result.returncode == 0:
               print("[installer][web-edge] Microsoft Edge installed via dnf")
               return True
           
           # Installation failed
           print(f"[installer][web-edge] Installation failed. Error: {dnf_result.stderr}")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Web",
                   "name": "Edge",
                   "status": "not installed",
                   "comment": "Installation failed. Please ensure you have provided the correct password.",
               }
           })
           return False
       
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Edge",
               "status": "not installed",
               "comment": "Installation failed. Please ensure you have provided the correct password.",
           }
       })
       return False
   except Exception as e:
       print(f"[installer][web-edge] Linux installation failed: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Edge",
               "status": "not installed",
               "comment": "Installation failed. Please ensure you have provided the correct password.",
           }
       })
       return False


async def _install_edge_darwin(installer_path, user_password: str = ""):
   """Install Edge on macOS"""
   print("[installer][web-edge] Installing Microsoft Edge on macOS...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Web",
           "name": "Edge",
           "status": "installing",
           "comment": "Installing Microsoft Edge...",
       }
   })
   
   try:
       # Try using homebrew first (doesn't need sudo)
       brew_result = subprocess.run(
           ["brew", "install", "--cask", "microsoft-edge"],
           capture_output=True,
           text=True,
           check=False
       )
       
       if brew_result.returncode == 0:
           print("[installer][web-edge] Microsoft Edge installed via homebrew")
           return True
       
       # Fallback to .pkg installer (needs sudo)
       if installer_path and installer_path.exists():
           if user_password:
               # Use echo to pipe password to sudo -S
               cmd = f"echo '{user_password}' | sudo -S installer -pkg {str(installer_path)} -target /"
               pkg_result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
           else:
               pkg_result = subprocess.run(
                   ["sudo", "installer", "-pkg", str(installer_path), "-target", "/"],
                   capture_output=True,
                   text=True,
                   check=False
               )
           
           if pkg_result.returncode == 0:
               print("[installer][web-edge] Microsoft Edge installed via .pkg")
               return True
           else:
               print(f"[installer][web-edge] Installation failed. Error: {pkg_result.stderr}")
               await send_response({
                   "action": "status",
                   "data": {
                       "category": "Web",
                       "name": "Edge",
                       "status": "not installed",
                       "comment": "Installation failed. Please ensure you have provided the correct password.",
                   }
               })
               return False
       
       # All installation methods failed
       if brew_result.returncode != 0:
           print(f"[installer][web-edge] Installation failed. Error: {brew_result.stderr}")
       
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Edge",
               "status": "not installed",
               "comment": "Installation failed. Please ensure you have provided the correct password.",
           }
       })
       return False
   except Exception as e:
       print(f"[installer][web-edge] macOS installation failed: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Edge",
               "status": "not installed",
               "comment": "Installation failed. Please ensure you have provided the correct password.",
           }
       })
       return False


async def _verify_edge_installation():
   """Verify that Edge is properly installed"""
   print("[installer][web-edge] Verifying Microsoft Edge installation...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Web",
           "name": "Edge",
           "status": "installing",
           "comment": "Verifying Microsoft Edge installation...",
       }
   })
   
   # Wait a moment for installation to complete
   await asyncio.sleep(2)
   
   # Check if Edge is installed by running check_status
   return await check_status()


async def install(user_password: str = "") -> bool:
   """Main function to install Microsoft Edge"""
   print("[installer][web-edge] Installing Microsoft Edge...")
   
   # Check if Edge is already installed
   if await check_status():
       print("[installer][web-edge] Microsoft Edge is already installed")
       return True
   
   installer_path = None
   system = platform.system().lower()
   
   # Download installer if needed
   if system == "windows" or system == "darwin" or system == "linux":
       installer_path = await _download_edge_installer()
       if not installer_path:
           return False
   
   # Install based on platform
   if system == "windows":
       success = await _install_edge_windows(installer_path, user_password)
   elif system == "linux":
       success = await _install_edge_linux(installer_path, user_password)
   elif system == "darwin":
       success = await _install_edge_darwin(installer_path, user_password)
   else:
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Edge",
               "status": "not installed",
               "comment": f"Unsupported platform: {system}",
           }
       })
       return False
   
   if not success:
       return False
   
   # Verify installation
   if not await _verify_edge_installation():
       print("[installer][web-edge] Microsoft Edge installation verification failed")
       return False
   
   print("[installer][web-edge] Microsoft Edge installation complete")
   await send_response({
       "action": "status",
       "data": {
           "category": "Web",
           "name": "Edge",
           "status": "installed",
           "comment": "Microsoft Edge is installed",
       }
   })
   return True
