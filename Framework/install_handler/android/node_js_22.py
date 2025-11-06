import subprocess
import re
from Framework.install_handler.utils import send_response


async def check_status() -> bool:
   """Check if Node.js 22 is installed."""
   print("[installer][android-nodejs22] Checking status...")
  
   try:
       result = subprocess.run(
           ["node", "--version"],
           capture_output=True,
           text=True,
           check=False
       )
         
       if result.returncode != 0:
           print("[installer][android-nodejs22] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Node js 22",
                   "status": "not installed",
                   "comment": "Install Node.js 22 to use it.",
               }
           })
           return False
      
       # node --version prints to stdout typically
       version_text = (result.stderr or result.stdout).strip()
       if not version_text:
           print("[installer][android-nodejs22] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Node js 22",
                   "status": "not installed",
                   "comment": "Install Node.js 22 to use it.",
               }
           })
           return False
      
       # Extract version number from output like "v22.0.0" or "v18.0.0"
       version_match = re.search(r'v(\d+)\.(\d+)', version_text)
       if version_match:
           major_version = int(version_match.group(1))
          
           # Check if it's Node.js 22
           if major_version == 22:
               print(f"[installer][android-nodejs22] Already installed (version: {version_text})")
               await send_response({
                   "action": "status",
                   "data": {
                       "category": "Android",
                       "name": "Node js 22",
                       "status": "installed",
                       "comment": f"Node.js is installed (version: {version_text})",
                   }
               })
               return True
      
       print(f"[installer][android-nodejs22] Not installed (found version: {version_text})")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Node js 22",
               "status": "not installed",
               "comment": f"Install Node.js 22 to use it (found version: {version_text}).",
           }
       })
       return False
   except Exception as e:
       print(f"[installer][android-nodejs22] Error checking status: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Node js 22",
               "status": "not installed",
               "comment": "Unable to check Node.js status.",
           }
       })
       return False




async def install():
   print("[node_js_22] Installing...")




