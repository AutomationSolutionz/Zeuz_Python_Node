import subprocess
import asyncio
import platform
from Framework.install_handler.install_log_config import get_logger
from Framework.install_handler.utils import send_response
from Framework.nodejs_appium_installer import check_installations, get_appium_path, get_node_dir

logger = get_logger()


async def check_status() -> bool:
   """Check if Appium is installed."""
   logger.info("[installer][android-appium] Checking status...")
  
   try:
       # Use the check function from nodejs_appium_installer
       node_installed, appium_installed, missing_drivers = check_installations()
       
       if appium_installed and not missing_drivers:
           # Get the installation location
           appium_path = get_appium_path()
           node_dir = get_node_dir()
           appium_location = str(appium_path.resolve()) if appium_path.exists() else str(node_dir.resolve())
           
           # Get version for display
           try:
               loop = asyncio.get_event_loop()
               result = await loop.run_in_executor(
                   None,
                   lambda: subprocess.run(
                       [str(appium_path), "--version"],
                       capture_output=True,
                       text=True,
                       check=False
                   )
               )

               version_output = (result.stdout or result.stderr or "").strip()
               version_info = f" (version: {version_output})" if version_output else ""
           except Exception:
               version_info = ""
           
           logger.info("[installer][android-appium] Already installed at %s", appium_location)
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Appium",
                   "status": "installed",
                   "comment": f"Appium is installed at {appium_location}{version_info}",
               }
           })
           return True
       elif appium_installed:
           missing_text = ", ".join(missing_drivers)
           logger.warning(
               "[installer][android-appium] Missing required drivers: %s",
               missing_text,
           )
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Appium",
                   "status": "not installed",
                   "comment": f"Appium is installed, but required drivers are missing: {missing_text}",
               }
           })
           return False
       else:
           logger.info("[installer][android-appium] Not installed")
           await send_response({
               "action": "status",
               "data": {
                   "category": "Android",
                   "name": "Appium",
                   "status": "not installed",
                   "comment": "Run the ZeuZ Node, it will automatically install Appium",
               }
           })
           return False
   except Exception as e:
       logger.error("[installer][android-appium] Error checking status: %s", e)
       await send_response({
           "action": "status",
           "data": {
               "category": "Android",
               "name": "Appium",
               "status": "not installed",
               "comment": f"Unable to verify Appium: {str(e)[:160]}",
           }
       })
       return False




async def install() -> bool:
    """Install Appium globally via npm."""
    logger.info("[installer][android-appium] Installing...")
    
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
            
            logger.info("[installer][android-appium] Running on Windows: %s", " ".join(cmd))
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
            
            logger.info("[installer][android-appium] Running on Linux: %s", " ".join(cmd))
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
            
            logger.info("[installer][android-appium] Running on macOS: %s", " ".join(cmd))
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
            logger.warning("[installer][android-appium] Unsupported platform: %s", system)
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
            logger.error("[installer][android-appium] Installation failed (returncode=%s)", result.returncode)
            logger.error("[installer][android-appium] Output: %s", output[:500])
            
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
        
        logger.info("[installer][android-appium] Installation successful")
        if output:
            logger.info("[installer][android-appium] Output: %s", output[:300])
        
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
        logger.warning("[installer][android-appium] Installation timed out after 10 minutes")
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
        logger.error("[installer][android-appium] Installation error: %s", e)
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
