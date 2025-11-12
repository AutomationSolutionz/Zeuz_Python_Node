import subprocess
import platform
import shutil
from Framework.install_handler.utils import send_response


async def check_status() -> bool:
   """Check if Mozilla Firefox is installed."""
   print("[installer][web-mozilla] Checking status...")
  
   try:
       result = None
       
       if platform.system() == "Windows":
           # Windows: try firefox.exe command first
           result = subprocess.run(
               ["firefox.exe", "--version"],
               capture_output=True,
               text=True,
               check=False
           )
           
           # If not in PATH, try common installation paths
           if result.returncode != 0:
               common_paths = [
                   r"C:\Program Files\Mozilla Firefox\firefox.exe",
                   r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
               ]
               for firefox_path in common_paths:
                   try:
                       result = subprocess.run(
                           [firefox_path, "--version"],
                           capture_output=True,
                           text=True,
                           check=False
                       )
                       if result.returncode == 0:
                           break
                   except (FileNotFoundError, OSError):
                       continue
       elif platform.system() == "Linux":
           # Linux: try firefox command
           result = subprocess.run(
               ["firefox", "--version"],
               capture_output=True,
               text=True,
               check=False
           )
           
           # If not found, try using shutil.which
           if result.returncode != 0:
               firefox_path = shutil.which("firefox")
               if firefox_path:
                   result = subprocess.run(
                       [firefox_path, "--version"],
                       capture_output=True,
                       text=True,
                       check=False
                   )
       elif platform.system() == "Darwin":
           # macOS: try firefox command
           result = subprocess.run(
               ["firefox", "--version"],
               capture_output=True,
               text=True,
               check=False
           )
           
           # If not found, try using shutil.which
           if result.returncode != 0:
               firefox_path = shutil.which("firefox")
               if firefox_path:
                   result = subprocess.run(
                       [firefox_path, "--version"],
                       capture_output=True,
                       text=True,
                       check=False
                   )
       else:
           # Default fallback for other platforms
           result = subprocess.run(
               ["firefox", "--version"],
               capture_output=True,
               text=True,
               check=False
           )

       print(f"[installer][web-mozilla] Result: {result}")
         
       if result.returncode != 0:
           print("[installer][web-mozilla] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Web",
                   "name": "Mozilla",
                   "status": "not installed",
                   "comment": "Install Mozilla Firefox to use it.",
               }
           })
           return False
      
       # Firefox version output is typically in stdout or stderr
       version_text = (result.stdout or result.stderr).strip()
       if not version_text:
           print("[installer][web-mozilla] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Web",
                   "name": "Mozilla",
                   "status": "not installed",
                   "comment": "Install Mozilla Firefox to use it.",
               }
           })
           return False
      
      
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "installed",
               "comment": f"Mozilla Firefox is installed version: {version_text[:50]}",
           }
       })
       return True
   except (FileNotFoundError, OSError):
       # Firefox command not found - Firefox is not installed
       print("[installer][web-mozilla] Not installed (firefox not found)")
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "not installed",
               "comment": "Install Mozilla Firefox to use it.",
           }
       })
       return False
   except Exception as e:
       print(f"[installer][web-mozilla] Error checking status: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Web",
               "name": "Mozilla",
               "status": "not installed",
               "comment": "Unable to check Mozilla Firefox status.",
           }
       })
       return False

