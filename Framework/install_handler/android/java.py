import subprocess
import re
from Framework.install_handler.utils import send_response


async def check_status() -> bool:
   """Check if Java 21 is installed."""
   print("[installer][android-java] Checking status...")
  
   try:
       result = subprocess.run(
           ["java", "-version"],
           capture_output=True,
           text=True,
           check=False
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
   print("[java] Installing...")
