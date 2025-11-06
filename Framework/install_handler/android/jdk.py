import subprocess
import re
import httpx
import asyncio
import os
import platform
import shutil
import tempfile
import zipfile
import tarfile
import stat
from pathlib import Path
from Framework.install_handler.utils import send_response
from settings import ZEUZ_NODE_DOWNLOADS_DIR


def _is_windows():
   """Check if running on Windows"""
   return platform.system() == 'Windows'


async def _get_jdk_download_url():
   """Get the appropriate JDK 21 LTS download URL based on platform"""
   if _is_windows():
       return "https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.zip"
   else:
       return "https://download.oracle.com/java/21/latest/jdk-21_linux-x64_bin.tar.gz"


async def _download_jdk():
   """Download JDK 21 LTS with progress reporting"""
   print("[installer][android-jdk] Downloading JDK 21 LTS...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "JDK",
           "status": "installing",
           "comment": "Downloading JDK 21...",
       }
   })
  
   jdk_url = await _get_jdk_download_url()
  
   download_dir = ZEUZ_NODE_DOWNLOADS_DIR / "jdk"
   if _is_windows():
       jdk_archive = download_dir / "jdk21.zip"
   else:
       jdk_archive = download_dir / "jdk21.tar.gz"
  
   try:
       jdk_archive.parent.mkdir(parents=True, exist_ok=True)
      
       async with httpx.AsyncClient(timeout=900.0) as client:
           async with client.stream("GET", jdk_url) as response:
               response.raise_for_status()
              
               total_size = int(response.headers.get("content-length", 0))
               chunk_size = 8192
               downloaded = 0
              
               count = []
               with open(jdk_archive, "wb") as f:
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
                          
                           print(f"\r[installer][android-jdk] |{bar}| {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='', flush=True)
                          
                           p = round(mb_downloaded/mb_total, 1)
                           if p not in count:
                               count.append(p)
                               asyncio.create_task(send_response({
                                   "action": "status",
                                   "data": {
                                       "category": "Android",
                                       "name": "JDK",
                                       "status": "installing",
                                       "comment": f"Downloading JDK 21... {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)",
                                   }
                               }))
      
       print()
       print(f"[installer][android-jdk] JDK download complete: {jdk_archive}")
       return jdk_archive
   except Exception as e:
       print(f"\n[installer][android-jdk] JDK download failed: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "JDK",
               "status": "not installed",
               "comment": f"JDK download failed: {str(e)}",
           }
       })
       return None


async def _extract_jdk(jdk_archive):
   """Extract JDK to the appropriate location"""
   if not jdk_archive or not jdk_archive.exists():
       return None
  
   print("[installer][android-jdk] Extracting JDK...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "JDK",
           "status": "installing",
           "comment": "Extracting JDK...",
       }
   })
  
   # Install to user directory by default to avoid permission issues
   if not _is_windows():
       jdk_dir = Path.home() / "jdk-21"
       if jdk_dir.exists():
           shutil.rmtree(jdk_dir)
       jdk_dir.mkdir(parents=True, exist_ok=True)
       print("[installer][android-jdk] Installing JDK to user directory ~/jdk-21")
   else:
       jdk_dir = Path.home() / "jdk-21"
       if jdk_dir.exists():
           shutil.rmtree(jdk_dir)
       jdk_dir.mkdir(parents=True, exist_ok=True)
  
   try:
       if _is_windows():
           with zipfile.ZipFile(jdk_archive, 'r') as zip_ref:
               zip_ref.extractall(jdk_dir)
       else:
           with tarfile.open(jdk_archive, 'r:gz') as tar_ref:
               tar_ref.extractall(jdk_dir)
      
       # Find the actual JDK directory (it might be nested)
       jdk_home = None
       for item in jdk_dir.iterdir():
           if item.is_dir() and "jdk" in item.name.lower():
               jdk_home = item
               break
      
       if not jdk_home:
           print("[installer][android-jdk] Could not find JDK directory after extraction")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "JDK",
                   "status": "not installed",
                   "comment": "Could not find JDK directory after extraction.",
               }
           })
           return None
      
       print(f"[installer][android-jdk] JDK extracted to {jdk_home}")
       return jdk_home
   except Exception as e:
       print(f"[installer][android-jdk] JDK extraction failed: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "JDK",
               "status": "not installed",
               "comment": f"JDK extraction failed: {str(e)}",
           }
       })
       return None


async def _set_java_env_vars(jdk_home):
   """Set JAVA_HOME and add Java to PATH"""
   if not jdk_home or not jdk_home.exists():
       return False
  
   print("[installer][android-jdk] Setting Java environment variables...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "JDK",
           "status": "installing",
           "comment": "Setting Java environment variables...",
       }
   })
  
   if _is_windows():
       try:
           import winreg
           # Set JAVA_HOME
           with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                              r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                              0, winreg.KEY_ALL_ACCESS) as key:
               winreg.SetValueEx(key, "JAVA_HOME", 0, winreg.REG_EXPAND_SZ, str(jdk_home))
               print("[installer][android-jdk] JAVA_HOME set in Windows registry")
          
           # Update PATH
           with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                              r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                              0, winreg.KEY_ALL_ACCESS) as key:
               current_path, _ = winreg.QueryValueEx(key, "Path")
               path_parts = current_path.split(";")
              
               java_bin = str(jdk_home / "bin")
               if java_bin not in path_parts:
                   path_parts.append(java_bin)
                   new_path = ";".join(path_parts)
                   winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                   print("[installer][android-jdk] Java added to PATH in Windows registry")
       except Exception as e:
           print(f"[installer][android-jdk] Failed to update Windows registry: {e}")
           return False
   else:
       # Linux - determine if system-wide or user installation
       is_system_wide = str(jdk_home).startswith('/opt/')
      
       # Use current user's home directory
       user_home = Path.home()
       print("[installer][android-jdk] Setting Java environment variables for current user")
      
       if is_system_wide:
           print("[installer][android-jdk] System-wide Java installation detected")
       else:
           print("[installer][android-jdk] User-specific Java installation detected")
      
       shell_configs = [
           user_home / ".bashrc",
           user_home / ".zshrc",
           user_home / ".profile"
       ]
      
       export_lines = [
           f"export JAVA_HOME={jdk_home}",
           f"export PATH=$JAVA_HOME/bin:$PATH"
       ]
      
       # Set environment variables in current session
       os.environ['JAVA_HOME'] = str(jdk_home)
       current_path = os.environ.get('PATH', '')
       java_bin_path = str(jdk_home / "bin")
       if java_bin_path not in current_path:
           os.environ['PATH'] = f"{java_bin_path}:{current_path}"
      
       updated = False
       for config_file in shell_configs:
           if config_file.exists():
               try:
                   with open(config_file, 'r+') as f:
                       content = f.read()
                       needs_update = any(export not in content for export in export_lines)
                      
                       if needs_update:
                           f.write("\n# Java environment variables\n" + "\n".join(export_lines) + "\n")
                           print(f"[installer][android-jdk] Updated {config_file} with Java paths")
                           updated = True
               except Exception as e:
                   print(f"[installer][android-jdk] Failed to update {config_file}: {e}")
      
       if updated:
           print("[!] Please restart your terminal or run 'source ~/.bashrc' (or your shell config)")
  
   return True


async def _verify_java_installation(jdk_home):
   """Verify that Java is properly installed and working"""
   print("[installer][android-jdk] Verifying Java installation...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "JDK",
           "status": "installing",
           "comment": "Verifying Java installation...",
       }
   })
  
   # Check if java executable exists
   java_exe = jdk_home / "bin" / ("java.exe" if _is_windows() else "java")
   if not java_exe.exists():
       print(f"[installer][android-jdk] Java executable not found at {java_exe}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "JDK",
               "status": "not installed",
               "comment": f"Java executable not found at {java_exe}",
           }
       })
       return False
  
   # Make executable on Linux
   if not _is_windows():
       try:
           java_exe.chmod(java_exe.stat().st_mode | stat.S_IEXEC)
       except Exception as e:
           print(f"[installer][android-jdk] Failed to make Java executable: {e}")
           return False
  
   # Test Java version
   try:
       result = subprocess.run([str(java_exe), "-version"],
                             capture_output=True,
                             text=True)
       if "version \"21" not in result.stderr:
           print("[installer][android-jdk] Java version check failed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "JDK",
                   "status": "not installed",
                   "comment": "Java version check failed.",
               }
           })
           return False
       print("[installer][android-jdk] Java version verified")
      
       # Test Java compiler
       javac_exe = jdk_home / "bin" / ("javac.exe" if _is_windows() else "javac")
       if not javac_exe.exists():
           print(f"[installer][android-jdk] Java compiler not found at {javac_exe}")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "JDK",
                   "status": "not installed",
                   "comment": f"Java compiler not found at {javac_exe}",
               }
           })
           return False
      
       if not _is_windows():
           javac_exe.chmod(javac_exe.stat().st_mode | stat.S_IEXEC)
          
       result = subprocess.run([str(javac_exe), "-version"],
                             capture_output=True,
                             text=True)
       if "javac 21" not in (result.stdout or result.stderr):
           print("[installer][android-jdk] Java compiler version check failed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "JDK",
                   "status": "not installed",
                   "comment": "Java compiler version check failed.",
               }
           })
           return False
       print("[installer][android-jdk] Java compiler verified")
      
       return True
   except Exception as e:
       print(f"[installer][android-jdk] Java verification failed: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "JDK",
               "status": "not installed",
               "comment": f"Java verification failed: {str(e)}",
           }
       })
       return False


async def check_status() -> bool:
   """Check if JDK 21 is installed."""
   print("[installer][android-jdk] Checking status...")
  
   try:
       result = subprocess.run(
           ["javac", "-version"],
           capture_output=True,
           text=True,
           check=False
       )
         
       if result.returncode != 0:
           print("[installer][android-jdk] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "JDK",
                   "status": "not installed",
                   "comment": "Install JDK 21 to use it.",
               }
           })
           return False
      
       # javac -version prints to stderr typically
       version_text = (result.stderr or result.stdout).strip()
       if not version_text:
           print("[installer][android-jdk] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "JDK",
                   "status": "not installed",
                   "comment": "Install JDK 21 to use it.",
               }
           })
           return False
      
       # Extract version number from output like "javac 21.0.1" or "javac 1.8.0_291"
       version_match = re.search(r'javac\s+(\d+)\.(\d+)', version_text)
       if version_match:
           major_version = int(version_match.group(1))
           minor_version = int(version_match.group(2))
          
           # Check if it's JDK 21
           if major_version == 21:
               print(f"[installer][android-jdk] Already installed (version: {major_version}.{minor_version})")
               await send_response({
                   "action": "status",
                   "data": {
                       "category": "Android",
                       "name": "JDK",
                       "status": "installed",
                       "comment": f"JDK is installed (version: {major_version}.{minor_version})",
                   }
               })
               return True
           # Handle old versioning like "1.8.0" where major=1, minor=8
           elif major_version == 1 and minor_version >= 8:
               print(f"[installer][android-jdk] Wrong version installed (found: {major_version}.{minor_version})")
               await send_response({
                   "action": "status",
                   "data": {
                       "category": "Android",
                       "name": "JDK",
                       "status": "not installed",
                       "comment": f"Install JDK 21 to use it (found version: {major_version}.{minor_version}).",
                   }
               })
               return False
      
       print(f"[installer][android-jdk] Not installed (found version: {version_text})")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "JDK",
               "status": "not installed",
               "comment": f"Install JDK 21 to use it (found version: {version_text[:50]}).",
           }
       })
       return False
   except (FileNotFoundError, OSError):
       # javac command not found - JDK is not installed
       print("[installer][android-jdk] Not installed (javac not found)")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "JDK",
               "status": "not installed",
               "comment": "Install JDK 21 to use it.",
           }
       })
       return False
   except Exception as e:
       print(f"[installer][android-jdk] Error checking status: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "JDK",
               "status": "not installed",
               "comment": "Unable to check JDK status.",
           }
       })
       return False




async def install() -> bool:
   """Main function to setup JDK 21 LTS"""
   print("[installer][android-jdk] Installing...")
  
   # Check if Java is already installed
   jdk_home = None
   try:
       result = subprocess.run(["java", "-version"], capture_output=True, text=True)
       if "version \"21" in result.stderr:
           print("[installer][android-jdk] JDK 21 is already installed")
           # Find the JDK installation directory
           if _is_windows():
               jdk_dir = Path.home() / "jdk-21"
               if jdk_dir.exists():
                   # Find the actual JDK directory
                   for item in jdk_dir.iterdir():
                       if item.is_dir() and "jdk" in item.name.lower():
                           jdk_home = item
                           break
           else:
               # Check user location first
               user_jdk = Path.home() / "jdk-21"
               if user_jdk.exists():
                   # Find the actual JDK directory
                   for item in user_jdk.iterdir():
                       if item.is_dir() and "jdk" in item.name.lower():
                           jdk_home = item
                           break
               else:
                   # Check system-wide location as fallback
                   system_jdk = Path("/opt/jdk-21")
                   if system_jdk.exists():
                       # Find the actual JDK directory
                       for item in system_jdk.iterdir():
                           if item.is_dir() and "jdk" in item.name.lower():
                               jdk_home = item
                               break
              
               if not jdk_home:
                   print("[installer][android-jdk] JDK is installed but installation directory not found")
   except:
       pass
  
   # If JDK is not installed, download and install it
   if not jdk_home:
       # Download and extract JDK
       jdk_archive = await _download_jdk()
       if not jdk_archive:
           return False
      
       jdk_home = await _extract_jdk(jdk_archive)
       if not jdk_home:
           return False
      
       # Clean up archive
       try:
           jdk_archive.unlink()
       except:
           pass
  
   # Verify installation
   if not await _verify_java_installation(jdk_home):
       print("[installer][android-jdk] Java installation verification failed")
       return False
  
   # Set environment variables
   if not await _set_java_env_vars(jdk_home):
       return False
  
   print("[installer][android-jdk] JDK 21 LTS setup complete")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "JDK",
           "status": "installed",
           "comment": f"JDK is installed at {jdk_home}",
       }
   })
   return True
