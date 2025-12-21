import subprocess
import re
import httpx
import asyncio
import platform
import shutil
import zipfile
import tarfile
import stat
from pathlib import Path
from Framework.install_handler.utils import send_response
from settings import ZEUZ_NODE_DOWNLOADS_DIR


async def _get_jdk_download_url():
   """Get the appropriate JDK 21 LTS download URL based on platform"""
   system = platform.system()
   
   if system == "Windows":
       return "https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.zip"
   elif system == "Linux":
       return "https://download.oracle.com/java/21/latest/jdk-21_linux-x64_bin.tar.gz"
   elif system == "Darwin":
       # macOS - use ARM64 for Apple Silicon or x64 for Intel
       import subprocess
       try:
           # Check if running on Apple Silicon
           result = subprocess.run(["uname", "-m"], capture_output=True, text=True)
           arch = result.stdout.strip()
           if arch == "arm64":
               return "https://download.oracle.com/java/21/latest/jdk-21_macos-aarch64_bin.tar.gz"
           else:
               return "https://download.oracle.com/java/21/latest/jdk-21_macos-x64_bin.tar.gz"
       except:
           # Default to x64 if detection fails
           return "https://download.oracle.com/java/21/latest/jdk-21_macos-x64_bin.tar.gz"
   else:
       raise OSError(f"Unsupported platform: {system}")


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
   system = platform.system()
   
   if system == "Windows":
       jdk_archive = download_dir / "jdk21.zip"
   elif system == "Linux":
       jdk_archive = download_dir / "jdk21.tar.gz"
   elif system == "Darwin":
       jdk_archive = download_dir / "jdk21.tar.gz"
   else:
       raise OSError(f"Unsupported platform: {system}")
  
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
  
   system = platform.system()
   
   # Extract to ZEUZ downloads directory
   jdk_dir = ZEUZ_NODE_DOWNLOADS_DIR / "jdk" / "jdk-21"
   if jdk_dir.exists():
       shutil.rmtree(jdk_dir)
   jdk_dir.mkdir(parents=True, exist_ok=True)
   
   if system == "Windows":
       print(f"[installer][android-jdk] Extracting JDK to {jdk_dir}")
   elif system == "Linux":
       print(f"[installer][android-jdk] Extracting JDK to {jdk_dir}")
   elif system == "Darwin":
       print(f"[installer][android-jdk] Extracting JDK to {jdk_dir}")
  
   try:
       if system == "Windows":
           with zipfile.ZipFile(jdk_archive, 'r') as zip_ref:
               zip_ref.extractall(jdk_dir)
       elif system == "Linux":
           with tarfile.open(jdk_archive, 'r:gz') as tar_ref:
               tar_ref.extractall(jdk_dir)
       elif system == "Darwin":
           with tarfile.open(jdk_archive, 'r:gz') as tar_ref:
               tar_ref.extractall(jdk_dir)
       else:
           raise OSError(f"Unsupported platform: {system}")
      
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
  
   system = platform.system()
   
   # Check if java executable exists
   if system == "Windows":
       java_exe = jdk_home / "bin" / "java.exe"
   elif system == "Linux":
       java_exe = jdk_home / "bin" / "java"
   elif system == "Darwin":
       java_exe = jdk_home / "bin" / "java"
   else:
       print(f"[installer][android-jdk] Unsupported platform: {system}")
       return False
       
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
  
   # Make executable on Linux and macOS
   if system == "Linux":
       try:
           java_exe.chmod(java_exe.stat().st_mode | stat.S_IEXEC)
       except Exception as e:
           print(f"[installer][android-jdk] Failed to make Java executable: {e}")
           return False
   elif system == "Darwin":
       try:
           java_exe.chmod(java_exe.stat().st_mode | stat.S_IEXEC)
       except Exception as e:
           print(f"[installer][android-jdk] Failed to make Java executable: {e}")
           return False
  
   # Test Java version (async)
   try:
       loop = asyncio.get_event_loop()
       result = await loop.run_in_executor(
           None,
           lambda: subprocess.run(
               [str(java_exe), "-version"],
               capture_output=True,
               text=True
           )
       )
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
       if system == "Windows":
           javac_exe = jdk_home / "bin" / "javac.exe"
       elif system == "Linux":
           javac_exe = jdk_home / "bin" / "javac"
       elif system == "Darwin":
           javac_exe = jdk_home / "bin" / "javac"
           
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
      
       if system == "Linux":
           javac_exe.chmod(javac_exe.stat().st_mode | stat.S_IEXEC)
       elif system == "Darwin":
           javac_exe.chmod(javac_exe.stat().st_mode | stat.S_IEXEC)
          
       result = await loop.run_in_executor(
           None,
           lambda: subprocess.run(
               [str(javac_exe), "-version"],
               capture_output=True,
               text=True
           )
       )
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
       loop = asyncio.get_event_loop()
       result = await loop.run_in_executor(
           None,
           lambda: subprocess.run(
               ["javac", "-version"],
               capture_output=True,
               text=True,
               check=False
           )
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
  
   # Check if JDK 21 is already installed
   if await check_status():
       print("[installer][android-jdk] JDK 21 is already installed")
       return True
   
   jdk_home = None
  
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