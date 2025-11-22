import subprocess
import platform
from Framework.install_handler.utils import send_response
from Framework.nodejs_appium_installer import get_node_dir, check_installations


async def check_status() -> bool:
   """Check if Node.js 22 is installed."""
   print("[installer][android-nodejs22] Checking status...")
  
   try:
       # Use the check function from nodejs_appium_installer
       node_installed, appium_installed, missing_drivers = check_installations()
       
       if node_installed:
           # Get the installation location
           node_dir = get_node_dir()
           node_location = str(node_dir.resolve())
           
           # Get version for display
           node_bin = node_dir / ("node.exe" if platform.system() == "Windows" else "bin/node")
           try:
               result = subprocess.run(
                   [str(node_bin), "--version"],
                   capture_output=True,
                   text=True,
                   check=False
               )
               version_text = (result.stdout or result.stderr or "").strip()
               version_info = f" (version: {version_text})" if version_text else ""
           except:
               version_info = ""
           
           print(f"[installer][android-nodejs22] Already installed at {node_location}")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Node js 22",
                   "status": "installed",
                   "comment": f"Node.js is installed at {node_location}{version_info}",
               }
           })
           return True
       else:
           print("[installer][android-nodejs22] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Node js 22",
                   "status": "not installed",
                   "comment": "Run the ZeuZ Node, it will automatically install Node.js",
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
               "comment": "Run the ZeuZ Node, it will automatically install Node.js",
           }
       })
       return False




async def install():
   print("[node_js_22] Installing...")



