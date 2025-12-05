import subprocess
import asyncio
import platform
import os
from Framework.install_handler.utils import send_response


async def check_status() -> bool:
   """Check if ADB (Android Debug Bridge) is installed."""
   print("[installer][android-adb] Checking status...")
  
   # Dynamically refresh ANDROID_HOME and PATH from registry on Windows
   system = platform.system()
   if system == "Windows":
       try:
           import winreg
           with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ) as key:
               try:
                   android_home_reg, _ = winreg.QueryValueEx(key, "ANDROID_HOME")
                   if android_home_reg:
                       # Expand environment variables before checking if path exists
                       android_home_expanded = os.path.expandvars(android_home_reg)
                       if os.path.exists(android_home_expanded):
                           os.environ['ANDROID_HOME'] = android_home_expanded
                           # Update PATH with platform-tools (where ADB is located)
                           platform_tools = os.path.join(android_home_expanded, "platform-tools")
                           current_path = os.environ.get('PATH', '')
                           if platform_tools not in current_path:
                               os.environ['PATH'] = f"{platform_tools};{current_path}"
                           print(f"[installer][android-adb] Refreshed ANDROID_HOME from registry: {android_home_expanded}")
               except FileNotFoundError:
                   pass
               
               # Also check ANDROID_SDK_ROOT if ANDROID_HOME not found
               if 'ANDROID_HOME' not in os.environ or not os.path.exists(os.environ.get('ANDROID_HOME', '')):
                   try:
                       android_sdk_root_reg, _ = winreg.QueryValueEx(key, "ANDROID_SDK_ROOT")
                       if android_sdk_root_reg:
                           # Expand environment variables before checking if path exists
                           android_sdk_root_expanded = os.path.expandvars(android_sdk_root_reg)
                           if os.path.exists(android_sdk_root_expanded):
                               os.environ['ANDROID_SDK_ROOT'] = android_sdk_root_expanded
                               # Update PATH with platform-tools (where ADB is located)
                               platform_tools = os.path.join(android_sdk_root_expanded, "platform-tools")
                               current_path = os.environ.get('PATH', '')
                               if platform_tools not in current_path:
                                   os.environ['PATH'] = f"{platform_tools};{current_path}"
                               print(f"[installer][android-adb] Refreshed ANDROID_SDK_ROOT from registry: {android_sdk_root_expanded}")
                   except FileNotFoundError:
                       pass
       except Exception as e:
           print(f"[installer][android-adb] Failed to refresh from registry: {e}")
  
   try:
       loop = asyncio.get_event_loop()
       result = await loop.run_in_executor(
           None,
           lambda: subprocess.run(
               ["adb", "version"],
               capture_output=True,
               text=True,
               check=False
           )
       )
      
       # If command succeeds (returncode = 0), ADB is installed
       if result.returncode == 0:
           version_output = (result.stdout or result.stderr).strip()
           print(f"[installer][android-adb] Already installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "ADB",
                   "status": "installed",
                   "comment": f"ADB is installed (version: {version_output.split()[0] if version_output else 'unknown'})",
               }
           })
           return True
       else:
           print("[installer][android-adb] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "ADB",
                   "status": "not installed",
                   "comment": "Install ADB to use it.",
               }
           })
           return False
   except Exception as e:
       print(f"[installer][android-adb] Error checking status: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "ADB",
               "status": "not installed",
               "comment": "Unable to check ADB status.",
           }
       })
       return False




async def install():
   """Install ADB - checks if already installed, otherwise prompts to install Android SDK."""
   print("[installer][android-adb] Installing...")
   
   # Check if ADB is already installed
   if await check_status():
       print("[installer][android-adb] ADB is already installed")
       return
   
   # ADB is not installed, send response to install Android SDK
   print("[installer][android-adb] ADB is not installed. Install Android SDK to get ADB.")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "ADB",
           "status": "not installed",
           "comment": "Install the Android SDK, it will automatically install ADB.",
       }
   })




