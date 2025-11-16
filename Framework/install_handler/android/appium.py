import subprocess
import asyncio
import platform
from Framework.install_handler.utils import send_response


async def check_status() -> bool:
   """Check if Appium is installed."""
   print("[installer][android-appium] Checking status...")
  
   try:
       loop = asyncio.get_event_loop()
       result = await loop.run_in_executor(
           None,
           lambda: subprocess.run(
               ["appium", "--version"],
               capture_output=True,
               text=True,
               check=False
           )
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




async def install() -> bool:
    """Install Appium globally via npm."""
    print("[installer][android-appium] Installing...")
    
    await send_response({
        "action": "status",
        "data": {
            "category": "Android",
            "name": "Appium",
            "status": "installing",
            "comment": "Installing Appium via npm...",
        }
    })
    
    try:
        system = platform.system()
        loop = asyncio.get_event_loop()
        
        # Platform-specific npm command handling
        if system == "Windows":
            # Windows: npm is typically npm.cmd, but npm works too
            npm_cmd = "npm"
            cmd = [npm_cmd, "install", "-g", "appium"]
            
            print(f"[installer][android-appium] Running on Windows: {' '.join(cmd)}")
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    shell=True,  # Windows may need shell=True for npm
                    timeout=600  # 10 minutes timeout
                )
            )
            
        elif system == "Linux":
            # Linux: standard npm command
            npm_cmd = "npm"
            cmd = [npm_cmd, "install", "-g", "appium"]
            
            print(f"[installer][android-appium] Running on Linux: {' '.join(cmd)}")
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minutes timeout
                )
            )
            
        elif system == "Darwin":
            # macOS: standard npm command, may need sudo depending on setup
            npm_cmd = "npm"
            cmd = [npm_cmd, "install", "-g", "appium"]
            
            print(f"[installer][android-appium] Running on macOS: {' '.join(cmd)}")
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minutes timeout
                )
            )
            
        else:
            print(f"[installer][android-appium] Unsupported platform: {system}")
            await send_response({
                "action": "status",
                "data": {
                    "category": "Android",
                    "name": "Appium",
                    "status": "not installed",
                    "comment": f"Installation not supported on platform: {system}",
                }
            })
            return False
        
        # Check installation result
        output = (result.stdout or "") + (result.stderr or "")
        
        if result.returncode != 0:
            print(f"[installer][android-appium] Installation failed (returncode={result.returncode})")
            print(f"[installer][android-appium] Output: {output[:500]}")
            
            await send_response({
                "action": "status",
                "data": {
                    "category": "Android",
                    "name": "Appium",
                    "status": "not installed",
                    "comment": f"Installation failed: {output[:200] if output else 'Unknown error'}",
                }
            })
            return False
        
        print(f"[installer][android-appium] Installation successful")
        if output:
            print(f"[installer][android-appium] Output: {output[:300]}")
        
        # Verify installation by checking status
        if await check_status():
            await send_response({
                "action": "status",
                "data": {
                    "category": "Android",
                    "name": "Appium",
                    "status": "installed",
                    "comment": "Appium installed successfully via npm",
                }
            })
            return True
        else:
            await send_response({
                "action": "status",
                "data": {
                    "category": "Android",
                    "name": "Appium",
                    "status": "not installed",
                    "comment": "Installation completed but Appium is not accessible",
                }
            })
            return False
            
    except subprocess.TimeoutExpired:
        print("[installer][android-appium] Installation timed out after 10 minutes")
        await send_response({
            "action": "status",
            "data": {
                "category": "Android",
                "name": "Appium",
                "status": "not installed",
                "comment": "Installation timed out after 10 minutes",
            }
        })
        return False
        
    except Exception as e:
        print(f"[installer][android-appium] Installation error: {e}")
        await send_response({
            "action": "status",
            "data": {
                "category": "Android",
                "name": "Appium",
                "status": "not installed",
                "comment": f"Installation error: {str(e)[:100]}",
            }
        })
        return False