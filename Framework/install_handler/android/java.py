import subprocess
import re
import asyncio
import platform
import os
from Framework.install_handler.utils import send_response
from Framework.install_handler.android.jdk import install as install_jdk


async def check_status() -> bool:
   """Check if Java 21 is installed."""
   print("[installer][android-java] Checking status...")
  
   # Dynamically refresh JAVA_HOME and PATH from registry on Windows
   system = platform.system()
   if system == "Windows":
       try:
           import winreg
           with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ) as key:
               try:
                   java_home_reg, _ = winreg.QueryValueEx(key, "JAVA_HOME")
                   if java_home_reg and os.path.exists(java_home_reg):
                       os.environ['JAVA_HOME'] = java_home_reg
                       # Update PATH with Java bin
                       java_bin = os.path.join(java_home_reg, "bin")
                       current_path = os.environ.get('PATH', '')
                       if java_bin not in current_path:
                           os.environ['PATH'] = f"{java_bin};{current_path}"
                       print(f"[installer][android-java] Refreshed JAVA_HOME from registry: {java_home_reg}")
               except FileNotFoundError:
                   pass
       except Exception as e:
           print(f"[installer][android-java] Failed to refresh from registry: {e}")
  
   try:
       loop = asyncio.get_event_loop()
       result = await loop.run_in_executor(
           None,
           lambda: subprocess.run(
               ["java", "-version"],
               capture_output=True,
               text=True,
               check=False
           )
       )
         
       if result.returncode != 0:
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
      
       # java -version prints to stderr typically
       version_text = (result.stderr or result.stdout).strip()
       if not version_text:
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
      
       # Extract version number from output like "openjdk version \"21.0.1\"" or "java version \"1.8.0_291\""
       version_match = re.search(r'version\s+"?(\d+)\.(\d+)', version_text)
       if version_match:
           major_version = int(version_match.group(1))
           minor_version = int(version_match.group(2))
          
           # Check if it's Java 21
           if major_version == 21:
               print(f"[installer][android-java] Already installed (version: {major_version}.{minor_version})")
               await send_response({
                   "action": "status",
                   "data": {
                       "category": "Android",
                       "name": "Java",
                       "status": "installed",
                       "comment": f"Java is installed (version: {major_version}.{minor_version})",
                   }
               })
               return True
           # Handle old versioning like "1.8.0" where major=1, minor=8
           elif major_version == 1 and minor_version >= 8:
               print(f"[installer][android-java] Wrong version installed (found: {major_version}.{minor_version})")
               await send_response({
                   "action": "status",
                   "data": {
                       "category": "Android",
                       "name": "Java",
                       "status": "not installed",
                       "comment": f"Install Java 21 to use it (found version: {major_version}.{minor_version}).",
                   }
               })
               return False
      
       print(f"[installer][android-java] Not installed (found version: {version_text})")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Java",
               "status": "not installed",
               "comment": f"Install Java 21 to use it (found version: {version_text[:50]}).",
           }
       })
       return False
   except Exception as e:
       print(f"[installer][android-java] Error checking status: {e}")
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Java",
               "status": "not installed",
               "comment": "Unable to check Java status.",
           }
       })
       return False




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