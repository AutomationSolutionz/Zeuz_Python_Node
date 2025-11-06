import subprocess
from Framework.install_handler.utils import send_response


async def check_status() -> bool:
   """Check if Appium is installed."""
   print("[installer][android-appium] Checking status...")
  
   try:
       result = subprocess.run(
           ["appium", "--version"],
           capture_output=True,
           text=True,
           check=False
       )
      
       if result.returncode == 0:
           version_output = (result.stdout or result.stderr).strip()
           print(f"[installer][android-appium] Already installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Appium",
                   "status": "installed",
                   "comment": f"Appium is installed (version: {version_output if version_output else 'unknown'})",
               }
           })
           return True
       else:
           print("[installer][android-appium] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Appium",
                   "status": "not installed",
                   "comment": "Install Appium to use it.",
               }
           })
           return False
   except Exception as e:
       print(f"[installer][android-appium] Error checking status: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Appium",
               "status": "not installed",
               "comment": "Unable to check Appium status.",
           }
       })
       return False




async def install():
   print("[appium] Installing...")
