import subprocess
from Framework.install_handler.utils import send_response


async def check_status() -> bool:
   """Check if ADB (Android Debug Bridge) is installed."""
   print("[installer][android-adb] Checking status...")
  
   try:
       result = subprocess.run(
           ["adb", "version"],
           capture_output=True,
           text=True,
           check=False
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
   print("[adb] Installing...")





