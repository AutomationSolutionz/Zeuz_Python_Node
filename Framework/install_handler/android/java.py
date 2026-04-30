import subprocess
import re
import asyncio
import platform
import os
import shutil
import zipfile
import tarfile
import stat
import httpx
from pathlib import Path
from Framework.install_handler.install_log_config import get_logger
from Framework.install_handler.utils import send_response
from Framework.install_handler.android.jdk import install as install_jdk
from settings import ZEUZ_NODE_DOWNLOADS_DIR

logger = get_logger()


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
            elif system == "Linux":
                java_exe = item / "bin" / "java"
            elif system == "Darwin":
                # macOS: Check for bundle structure first (Contents/Home)
                contents_home = item / "Contents" / "Home"
                if contents_home.exists() and (contents_home / "bin" / "java").exists():
                    java_exe = contents_home / "bin" / "java"
                else:
                    # Fallback: regular directory structure
                    java_exe = item / "bin" / "java"
            else:
                java_exe = item / "bin" / "java"
            
            if java_exe.exists():
                return java_exe
    
    # Fallback to direct bin path (if JDK was extracted directly)
    if system == "Windows":
        return jdk_dir / "bin" / "java.exe"
    elif system == "Linux":
        return jdk_dir / "bin" / "java"
    elif system == "Darwin":
        return jdk_dir / "bin" / "java"
    else:
        return jdk_dir / "bin" / "java"

async def check_status() -> bool:
    """Check if Java 21 is installed (following Node.js installer pattern - simple file existence check)."""
    logger.info("[installer][android-java] Checking status...")
    
    
    # Simple file existence check in isolated directory (like Node.js installer)
    java_path = get_java_path()
    
    if java_path.exists():
        logger.info("[installer][android-java] Already installed")
        
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
    logger.info("[installer][android-java] Not installed")
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
    
    print("Updating java path for the current session")
    # Check if java exists
    if not java_path.exists():
        print("Java not found for PATH update.")
        return
    
    # Get JDK home directory (parent of bin directory)
    # java_path is like:
    #   Linux/Windows: ~/.zeuz/zeuz_node_downloads/jdk/jdk-21/jdk-21.0.x/bin/java
    #   macOS (bundle): ~/.zeuz/zeuz_node_downloads/jdk/jdk-21/jdk-21.0.x/Contents/Home/bin/java
    # jdk_home should be:
    #   Linux/Windows: ~/.zeuz/zeuz_node_downloads/jdk/jdk-21/jdk-21.0.x
    #   macOS (bundle): ~/.zeuz/zeuz_node_downloads/jdk/jdk-21/jdk-21.0.x/Contents/Home
    jdk_home = java_path.parent.parent
    
    # Set JAVA_HOME for the current process
    os.environ['JAVA_HOME'] = str(jdk_home)
    print("JAVA_HOME set for current process: %s", jdk_home)
    
    # Add Java bin to PATH for the current process (always prepend so it takes precedence)
    java_bin_path = str(java_path.parent)
    current_path = os.environ.get('PATH', '')
    # Always prepend to ensure isolated Java takes precedence (even if path already exists)
    os.environ['PATH'] = f"{java_bin_path}{os.pathsep}{current_path}"
    print("Java prepended to current process PATH: %s", java_bin_path)


async def _get_jdk_download_url():
   """Get the appropriate JDK 21 LTS download URL from Eclipse Temurin (Adoptium) based on platform"""
   system = platform.system()
   
   # Map platform to Temurin API format
   if system == "Windows":
       os_name = "windows"
   elif system == "Linux":
       os_name = "linux"
   elif system == "Darwin":
       os_name = "mac"
   else:
       raise OSError(f"Unsupported platform: {system}")
   
   # Detect machine architecture dynamically (Temurin supports: x64, aarch64, ppc64, ppc64le, riscv64, s390x)
   machine = platform.machine().lower()
   
   # Map common architecture names to Temurin format
   if machine in ["x86_64", "amd64", "x64"]:
       arch = "x64"
   elif machine in ["aarch64", "arm64"]:
       arch = "aarch64"
   elif machine in ["ppc64le"]:
       arch = "ppc64le"
   elif machine in ["ppc64"]:
       arch = "ppc64"
   elif machine in ["riscv64"]:
       arch = "riscv64"
   elif machine in ["s390x"]:
       arch = "s390x"
   else:
       # Default to x64 for unknown architectures
       logger.warning("[installer][android-java] Warning: Unknown architecture '%s', defaulting to x64", machine)
       arch = "x64"
   
   # Use Temurin metadata API to get latest JDK 21 download URL
   api_url = f"https://api.adoptium.net/v3/assets/latest/21/hotspot?os={os_name}&architecture={arch}&image_type=jdk&vendor=eclipse"
   
   try:
       async with httpx.AsyncClient(timeout=30.0) as client:
           response = await client.get(api_url)
           response.raise_for_status()
           data = response.json()
           
           # Extract download URL from API response
           if data and len(data) > 0:
               download_url = data[0]["binary"]["package"]["link"]
               logger.info("[installer][android-java] Found Temurin JDK 21 download URL: %s", download_url)
               return download_url
           else:
               raise Exception("No download URL found in API response")
   except Exception as e:
       logger.error("[installer][android-java] Error fetching Temurin download URL: %s", e)
       raise Exception(f"Failed to get JDK download URL from Temurin API: {e}")


async def _download_jdk():
   """Download JDK 21 LTS with progress reporting"""
   logger.info("[installer][android-jdk] Downloading JDK 21 LTS...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "Java",
           "status": "installing",
           "comment": "Downloading Java 21...",
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
      
       async with httpx.AsyncClient(timeout=900.0, follow_redirects=True) as client:
           async with client.stream("GET", jdk_url) as response:
               response.raise_for_status()
              
               total_size = int(response.headers.get("content-length", 0))
               chunk_size = 8192
               downloaded = 0
               last_pct = [-1]
               with open(jdk_archive, "wb") as f:
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
                               logger.info("[installer][android-jdk] |%s| %d%% (%.1f/%.1f MB)", bar, pct, mb_downloaded, mb_total)
                               asyncio.create_task(send_response({
                                   "action": "status",
                                   "data": {
                                       "category": "Android",
                                       "name": "Java",
                                       "status": "installing",
                                       "comment": f"Downloading Java 21... {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)",
                                   }
                               }))
      
       logger.info("[installer][android-jdk] JDK download complete: %s", jdk_archive)
       return jdk_archive
   except Exception as e:
       logger.error("[installer][android-jdk] JDK download failed: %s", e)
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Java",
               "status": "not installed",
               "comment": f"Java download failed: {str(e)}",
           }
       })
       return None


async def _extract_jdk(jdk_archive):
   """Extract JDK to the appropriate location"""
   if not jdk_archive or not jdk_archive.exists():
       return None
  
   logger.info("[installer][android-jdk] Extracting JDK...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "Java",
           "status": "installing",
           "comment": "Extracting Java...",
       }
   })
  
   system = platform.system()
   
   # Extract to ZEUZ downloads directory
   jdk_dir = ZEUZ_NODE_DOWNLOADS_DIR / "jdk" / "jdk-21"
   if jdk_dir.exists():
       shutil.rmtree(jdk_dir)
   jdk_dir.mkdir(parents=True, exist_ok=True)
   
   if system == "Windows":
       logger.info("[installer][android-jdk] Extracting JDK to %s", jdk_dir)
   elif system == "Linux":
       logger.info("[installer][android-jdk] Extracting JDK to %s", jdk_dir)
   elif system == "Darwin":
       logger.info("[installer][android-jdk] Extracting JDK to %s", jdk_dir)
  
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
       
       if system == "Windows":
           # Windows: Find JDK directory directly
           for item in jdk_dir.iterdir():
               if item.is_dir() and "jdk" in item.name.lower():
                   jdk_home = item
                   break
       elif system == "Linux":
           # Linux: Find JDK directory directly
           for item in jdk_dir.iterdir():
               if item.is_dir() and "jdk" in item.name.lower():
                   jdk_home = item
                   break
       elif system == "Darwin":
           # macOS: Handle bundle structure (Contents/Home)
           for item in jdk_dir.iterdir():
               if item.is_dir() and "jdk" in item.name.lower():
                   # Check for macOS bundle structure: jdk_dir/Contents/Home
                   contents_home = item / "Contents" / "Home"
                   if contents_home.exists() and (contents_home / "bin" / "java").exists():
                       jdk_home = contents_home
                       break
                   # Fallback: regular directory structure (like Linux)
                   elif (item / "bin" / "java").exists():
                       jdk_home = item
                       break
       else:
           raise OSError(f"Unsupported platform: {system}")
       
       if not jdk_home:
           logger.error("[installer][android-jdk] Could not find JDK directory after extraction")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Java",
                   "status": "not installed",
                   "comment": "Could not find Java directory after extraction.",
               }
           })
           return None
       
       logger.info("[installer][android-jdk] JDK extracted to %s", jdk_home)
       return jdk_home
   except Exception as e:
       logger.error("[installer][android-jdk] JDK extraction failed: %s", e)
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Java",
               "status": "not installed",
               "comment": f"Java extraction failed: {str(e)}",
           }
       })
       return None


async def _verify_java_installation(jdk_home):
   """Verify that Java is properly installed and working"""
   logger.info("[installer][android-jdk] Verifying Java installation...")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "Java",
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
       logger.warning("[installer][android-jdk] Unsupported platform: %s", system)
       return False
       
   if not java_exe.exists():
       logger.error("[installer][android-jdk] Java executable not found at %s", java_exe)
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Java",
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
           logger.error("[installer][android-jdk] Failed to make Java executable: %s", e)
           return False
   elif system == "Darwin":
       try:
           java_exe.chmod(java_exe.stat().st_mode | stat.S_IEXEC)
       except Exception as e:
           logger.error("[installer][android-jdk] Failed to make Java executable: %s", e)
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
           logger.error("[installer][android-jdk] Java version check failed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Java",
                   "status": "not installed",
                   "comment": "Java version check failed.",
               }
           })
           return False
       logger.info("[installer][android-jdk] Java version verified")
      
       # Test Java compiler
       if system == "Windows":
           javac_exe = jdk_home / "bin" / "javac.exe"
       elif system == "Linux":
           javac_exe = jdk_home / "bin" / "javac"
       elif system == "Darwin":
           javac_exe = jdk_home / "bin" / "javac"
           
       if not javac_exe.exists():
           logger.error("[installer][android-jdk] Java compiler not found at %s", javac_exe)
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Java",
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
           logger.error("[installer][android-jdk] Java compiler version check failed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Java",
                   "status": "not installed",
                   "comment": "Java compiler version check failed.",
               }
           })
           return False
       logger.info("[installer][android-jdk] Java compiler verified")
      
       return True
   except Exception as e:
       logger.error("[installer][android-jdk] Java verification failed: %s", e)
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Java",
               "status": "not installed",
               "comment": f"Java verification failed: {str(e)}",
           }
       })
       return False


async def install() -> bool:
   """Main function to setup JDK 21 LTS"""
   logger.info("[installer][android-java] Installing...")
  
   # Check if JDK 21 is already installed
   if await check_status():
       logger.info("[installer][android-java] JDK 21 is already installed")
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
       except Exception:
           pass
  
   # Verify installation
   if not await _verify_java_installation(jdk_home):
       logger.error("[installer][android-jdk] Java installation verification failed")
       return False
  
   logger.info("[installer][android-jdk] JDK 21 LTS setup complete")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "Java",
           "status": "installed",
           "comment": f"Java is installed at {jdk_home}",
       }
   })

   update_java_path()
   return True