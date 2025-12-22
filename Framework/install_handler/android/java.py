import subprocess
import re
import asyncio
import platform
import os
from Framework.install_handler.utils import send_response
from Framework.install_handler.android.jdk import install as install_jdk
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
    
    print("Updating java path for")
    # Check if java exists
    if not java_path.exists():
        print("Java not found for PATH update.")
        return
    
    # Get JDK home directory (parent of bin directory)
    # java_path is like: ~/.zeuz/zeuz_node_downloads/jdk/jdk-21/jdk-21.0.x/bin/java
    # jdk_home should be: ~/.zeuz/zeuz_node_downloads/jdk/jdk-21/jdk-21.0.x
    jdk_home = java_path.parent.parent
    
    # Set JAVA_HOME for the current process
    os.environ['JAVA_HOME'] = str(jdk_home)
    print(f"JAVA_HOME set for current process: {jdk_home}")
    
    # Add Java bin to PATH for the current process (prepend so it takes precedence)
    java_bin_path = str(java_path.parent)
    current_path = os.environ.get('PATH', '')
    if java_bin_path not in current_path:
        os.environ['PATH'] = f"{java_bin_path}{os.pathsep}{current_path}"
        print(f"Java added to current process PATH: {java_bin_path}")
    else:
        print(f"Java already in PATH: {java_bin_path}")


async def install():
   """Install Java by calling JDK installation function"""
   print("[installer][android-java] Installing...")
   
   # Call JDK installation function
   success = await install_jdk()
   
   if success:
       print("[installer][android-java] Java installation successful")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Java",
               "status": "installed",
               "comment": "Java is installed",
           }
       })
       return True
   else:
       print("[installer][android-java] Java installation failed")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Java",
               "status": "not installed",
               "comment": "Failed to install Java",
           }
       })
       return False