import subprocess
import asyncio
import platform
import os
from Framework.install_handler.install_log_config import get_logger
from Framework.install_handler.utils import send_response
from Framework.install_handler.android.android_sdk import update_android_sdk_path

logger = get_logger()


async def check_status() -> bool:
   """Check if ADB (Android Debug Bridge) is installed."""
   logger.info("[installer][android-adb] Checking status...")
  
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
           logger.info("[installer][android-adb] Already installed")
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
           logger.info("[installer][android-adb] Not installed")
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
       logger.error("[installer][android-adb] Error checking status: %s", e)
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
   logger.info("[installer][android-adb] Installing...")
   
   # Check if ADB is already installed
   if await check_status():
       logger.info("[installer][android-adb] ADB is already installed")
       return
   
   # ADB is not installed, send response to install Android SDK
   logger.info("[installer][android-adb] ADB is not installed. Install Android SDK to get ADB.")
   await send_response({
       "action": "status",
       "data": {
           "category": "Android",
           "name": "ADB",
           "status": "not installed",
           "comment": "Install the Android SDK, it will automatically install ADB.",
       }
   })




