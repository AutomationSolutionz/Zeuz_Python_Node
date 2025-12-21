import subprocess
import asyncio
import platform
import os
import httpx
import shutil
import zipfile
import tarfile
import stat
from pathlib import Path
from Framework.install_handler.utils import send_response
from settings import ZEUZ_NODE_DOWNLOADS_DIR


def get_jdk_dir():
    """Get JDK installation directory (in downloads directory, matching jdk.py extraction location)."""
    jdk_dir = ZEUZ_NODE_DOWNLOADS_DIR / "jdk" / "jdk-21"
    jdk_dir.mkdir(parents=True, exist_ok=True)
    return jdk_dir


def get_java_path():
    """Get java binary path (handles JDK subdirectory structure)."""
    jdk_dir = get_jdk_dir()
    system = platform.system()
    
    # JDK is typically extracted to a subdirectory like jdk-21.0.x
    # Check for any jdk-* subdirectory first
    for item in jdk_dir.iterdir():
        if item.is_dir() and "jdk" in item.name.lower():
            if system == "Windows":
                java_exe = item / "bin" / "java.exe"
            else:
                java_exe = item / "bin" / "java"
            if java_exe.exists():
                return java_exe
    
    # Fallback to direct bin path (if JDK was extracted directly)
    if system == "Windows":
        return jdk_dir / "bin" / "java.exe"
    else:
        return jdk_dir / "bin" / "java"


async def check_status() -> bool:
    """Check if Java 21 is installed (following Node.js installer pattern - simple file existence check)."""
    print("[installer][android-java] Checking status...")
    
    # Simple file existence check in isolated directory (like Node.js installer)
    java_path = get_java_path()
    
    if java_path.exists():
        print("[installer][android-java] Already installed")
        await send_response({
            "action": "status",
            "data": {
                "category": "Android",
                "name": "Java",
                "status": "installed",
                "comment": "Java is installed (version : 21)",
            }
        })
        return True
    
    # Not installed
    print("[installer][android-java] Not installed")
    await send_response({
        "action": "status",
        "data": {
            "category": "Android",
            "name": "Java",
            "status": "not installed",
            "comment": "Install Java 21 to use it.",
        }
    })
    return False


def update_java_path():
    """Add Java binaries to PATH and set JAVA_HOME for the current process (following Node.js pattern)."""
    java_path = get_java_path()
    
    # Check if java exists
    if not java_path.exists():
        print("[installer][android-java] Warning: Java not found for PATH update.")
        return
    
    # Get JDK home directory (parent of bin directory)
    # java_path is like: ~/.zeuz/zeuz_node_downloads/jdk/jdk-21/jdk-21.0.x/bin/java
    # jdk_home should be: ~/.zeuz/zeuz_node_downloads/jdk/jdk-21/jdk-21.0.x
    jdk_home = java_path.parent.parent
    
    # Set JAVA_HOME for the current process
    os.environ['JAVA_HOME'] = str(jdk_home)
    print(f"[installer][android-java] JAVA_HOME set for current process: {jdk_home}")
    
    # Add Java bin to PATH for the current process (prepend so it takes precedence)
    java_bin_path = str(java_path.parent)
    current_path = os.environ.get('PATH', '')
    if java_bin_path not in current_path:
        os.environ['PATH'] = f"{java_bin_path}{os.pathsep}{current_path}"
        print(f"[installer][android-java] Java added to current process PATH: {java_bin_path}")
    else:
        print(f"[installer][android-java] Java already in PATH: {java_bin_path}")


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